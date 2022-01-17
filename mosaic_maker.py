#! python3

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
# ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

from PIL import Image, ImageOps, ImageFilter
import cv2
import matplotlib.pyplot as plt

import numpy as np
import os, copy
from datetime import datetime
from random import random
from math import floor

from yattag import Doc
from yattag import indent

try:
	from MosaicMaker import wantsomechocolate as wsc
except ImportError:
	import wantsomechocolate as wsc

try:
	from MosaicMaker import comparison_functions as cf
except ImportError:
	import comparison_functions as cf

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
# ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

## Should come from a configuration file at some point. 
PIECE_DEFAULT_SAVE_SIZE = (512,512)
PIECE_ACCEPTED_FILETYPES = ['.png','.jpg']
IMAGE_DEFAULT_COMPARISON_SIZE = (64,64)

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
# ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

## This file defines the following classes all related to creating photo mosaics. 

## Mosaic Image 	- A wrapper for a pillow image object
## Mosaic 			- The structure and methods for creating mosaics
## CompareImages	- Just a holder for the comparison functions used to compare sections and pieces
## PieceList 		- Holds the pieces, has some basic functionality for obtaining a piece list

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
# ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

class MosaicImage:

	def __init__(self, img):
		self.img = img


	## Setting img after init must also update original_img, exif data, mode, etc.
	@property
	def img(self):
		return self._img


	@img.setter
	def img(self,value):
		self._img = self.__process_image_argument(value)
		self.original_image = self._img
		if 'exif' in self.original_image.info:
			self.exif 		= self.original_image.info['exif']
		## Partial opacity is not supported
		if self.original_image.mode == 'RGBA':
			self.__rgba_to_rgb()
		self.__update()


	## To allow for a string instead of an Image object
	def __process_image_argument(self, img):
		if type(img) is type('string'):
			img = Image.open(img)
		return img


	## In case any image manipulation operations, use this function to reset exposed img data. 
	def __update(self):		
		self.rgb_data 			=	np.asarray(self._img)
		self.rgb_data_shape 	= 	self.rgb_data.shape
		self.mode				=	self._img.mode
		self.error 				=	None	
		self.width, self.height = 	self._img.size
		self.size 				= 	self._img.size		


	## For dealing with rgba
	def __rgba_to_rgb(self):
		new_img = Image.new("RGB", self._img.size, (255,255,255))
		new_img.paste(self._img, mask=self._img.split()[3])
		self._img = new_img
		self.__update()


	def img_crop_center(self):
		ow, oh = self._img.size
		if ow == oh:
			pass
		else:
			dw = dh = min(ow, oh)
			left  = floor( (ow/2) - (dw/2) )
			upper = floor( (oh/2) - (dh/2) )
			right = floor( (ow/2) + (dw/2) )
			lower = floor( (oh/2) + (dh/2) )
			self._img = self._img.crop((left,upper,right,lower))
			self.__update()


	## Just a wrapper for resize that knows about the default save size.
	def resize(self,size = PIECE_DEFAULT_SAVE_SIZE):
		if self._img.size == size:
			pass
		else:	
			self._img = self._img.resize(size)
			self.__update()


	def correct_orientation(self):
		self._img = wsc.rotate_based_on_exif(self._img)
		self.__update()


	## my preferred method to create thumbnails
	def to_thumbnail(self,size = PIECE_DEFAULT_SAVE_SIZE):
		self.img_crop_center()
		self.resize(size)
		self.correct_orientation()


## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
# ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

#@wsc.timer
class Mosaic:
	'''Size is a tuple of the form (width, height). Individual sections are accessed with [row][col]. 
	First argument can be a string, PIL Image object, or MosacImage obect.'''
	def __init__( 	self 							, 
					image 							, 
					granularity 		= 1/16 		, 
		
					comparison_function = None 		,
					reduce_function 	= None 		,
					error_function 		= None 		,

					f  					= 2 		, 
					rgb_weighting 		=(1,1,1) 	, 
					random_max 			= 0 		, 
					neighborhood_size 	= 1 		, 
		
					opts 				= dict()	,	):

		## Stuff with setters and getters
		self._granularity	 	= granularity
		self.target 			= image

		self.default_comparison_function = None #rgb_avg_comparison
		self.default_reduce_function = cf.reduce_functions.average
		self.default_error_function = cf.error_functions.sum_abs_error

		## Defining the comparison function
		self._comparison_function = comparison_function 
		self._reduce_function = reduce_function
		self._error_function = error_function
		self.__process_comparison_function()

		## Other variables defined here
		self.f 					= f 				
		self.rgb_weighting		= rgb_weighting		 
		## Maybe random should be allowed to be a tuple of (min,max)? or min,offset?
		self.random_max			= random_max		 
		self.neighborhood_size	= neighborhood_size	 

		## See the update function for other things that get defined on initialization


	## #########################################################################################
	## Granularity and target need getters and setters so that other attributes update when they change
	## #########################################################################################

	@property
	def granularity(self):
		return self._granularity
	@granularity.setter
	def granularity(self,value):
		self._granularity = value
		self.__update()	


	@property
	def target(self):
		return self._target
	@target.setter
	def target(self,value):
		self._target = self.__process_target_argument(value)
		self.__update()


	## Any time the target image is specified, or the number of sections is affected, this method should be called. 
	## Right now the number of sections is only affected by granularity. 
	def __update(self):
		self._target.min_dim = min(self._target.width, self._target.height)
		self.section_width 	= self.section_height = int(self._granularity * self._target.min_dim)
		self.w_sections 	= int( self._target.width  / self.section_width  )
		self.h_sections 	= int( self._target.height / self.section_height )

		## Set up an empty grid of the size you'll need based on the inputs. 
		self.grid = [ [None for i in range(self.w_sections)] for j in range(self.h_sections) ]
		
		## Loop through all the sections and create MosaicImage objects out of them all
		## I also add the coordinates to each section for easier reference when doing post edits. 
		for h_section in range(self.h_sections):
			for w_section in range(self.w_sections):
				section = self._target.img.crop((	self.section_width	*	 w_section 		, 		## left
													self.section_height *	 h_section 		, 		## top
													self.section_width	*	(w_section+1)	,		## right
													self.section_height	*	(h_section+1) 	,	))	## bottom
				
				## the grid is indexed using row,col
				self.grid[h_section][w_section] = MosaicImage(section)
				self.grid[h_section][w_section].coordinates = (h_section,w_section)	
				
				## Still fooling around with this at the moment. Should I be able to give the mosaic object
				## a map on init to automatically set these values for each section?
				## or maybe a defult type like center-out for the priority?
				self.grid[h_section][w_section].pinned = False

				## I'm having trouble figuring out where to put the default of radial
				## I also want to be able to allow users to write custom prioritizing functions?
				self.grid[h_section][w_section].priority = 0

		## I want this to be the default priority methodology. It makes sense to reset this based on granularity
		## It makes less sense to reset the priority of each section when just swapping out the target image,
		## but right now when a new target image is chosen, all the sections are completely remade, so 
		## this is the way it has to be at the moment. 
		self.set_section_priority_radial()


	## For treating the target image argument. 
	def __process_target_argument(self,image):
		if type(image) == type('string'):
			#print("Mosaic object initialized with a string")
			image = MosaicImage( Image.open(image) )
		elif type(image).__name__[-9:] == 'ImageFile':
			#print("Mosaic object initialized with an image object")
			image = MosaicImage( image )
		#self.target 		= image		
		return image


	## #########################################################################################
	## COMPARISON FUNCTIONS
	## #########################################################################################

	def __process_comparison_function(self):
		## If there is a comparison function passed directly, use it
		if self._comparison_function != None:
			pass
			
		## if either of reduce or error is specified, build the cf using the given info and defaults if necessary	
		elif (self._reduce_function != None) or (self._error_function != None):
			self._reduce_function = self.default_reduce_function if self._reduce_function == None else self._reduce_function
			self._error_function = self.default_error_function if self._error_function == None else self._error_function				
			self._comparison_function = cf.build_comparison_function(self._reduce_function, self._error_function)

		## if given nothing, and the object has a default cf defined, use that. 
		elif self.default_comparison_function != None:
			self._comparison_function = self.default_comparison_function

		## If given nothing, and the object does not have a default cf defined, use the default rf and ef.  
		else:		
			self._comparison_function = cf.build_comparison_function(self.default_reduce_function, self.default_error_function)


	## These are all properties so that if you update the mosaic object 
	## after initialization you still always have a valid comparison function to use. 
	@property
	def comparison_function(self):
		return self._comparison_function
	@comparison_function.setter
	def comparison_function(self,value):
		self._comparison_function = value
		self.__process_comparison_function()

	@property
	def reduce_function(self):
		return self._reduce_function
	@reduce_function.setter
	def reduce_function(self,value):
		self._reduce_function = value
		self.__process_comparison_function()

	@property
	def error_function(self):
		return self._error_function
	@error_function.setter
	def error_function(self,value):
		self._error_function = value
		self.__process_comparison_function()


	## #########################################################################################
	## THE MAIN METHODS OF THIS CLASS
	## #########################################################################################

	## Uses attributes set on the mosaic object to create a mosiac. 
	@wsc.timer
	def create( 	self 			, 
					piece_list		, 					
					opts= dict()	, 	):

		''' Create a mosaic '''

		print('Starting to Create!')

		## When creating a new mosaic from an existing master, you need to flush the instance counts from the 
		## piece list, otherwise the piece list will think it already has a bunch of stuff
		## in the mosaic. 
		piece_list.flush_instance_counts()

		## Sort all the sections based on priority order 
		sections_list = [self.grid[h_section][w_section] for h_section in range(self.h_sections) for w_section in range(self.w_sections)]
		sections_list.sort(key=lambda x: (x.priority is None, x.priority), reverse = True)

		## Compare each section to each piece
		progress1 = progress2 = 0  # For progress feedback
		for i in range(len(sections_list)):

			## The goal is to assign a single numerical value to each piece indicating it's similarity to the current section
			for j in range(len(piece_list.pieces)):

				## Reset obj1 and obj2 are useful when you want to save calculations through iterations of the comparison function. 
				## For example, pieces only need to be reduced once, that result can then be used with every section. 
				## Right now, comparison function puts the error on object 2 (the 2nd argument)
				self.comparison_function( 		sections_list[i]								,	#self.grid[h_section][w_section]					,
												piece_list.pieces[j] 							, 
												
												f 					= self.f 					, 
												rgb_weighting 		= self.rgb_weighting		,

												reset_obj1			= j==0 						, ## first iteration of a new section
												reset_obj2 			= i==0 						, ## all iterations of the first section #h_section+w_section==0,
												
												opts 				= opts 						,	)
				
			self.choose_match( sections_list[i].coordinates, piece_list.pieces, self.random_max, self.neighborhood_size, blocklist=[], opts=opts )
			## Could be section_list[i].piece = self.choose.......

			## At this point, a given section has just finished being compared to all pieces and the next section is up. 

			## Progress Bar
			progress2 = round(i*100/len(sections_list),0)
			if progress1!=progress2:
				print('#',end='')
				progress1=progress2

		## Newline after progress bar is done
		print('')


	## CHOOSE MATCH #########################################################################################

	## This function has a big job. It takes a section, piece list, and some other stuff
	## and tries to choose a match while satisfying all constraints and criteria.
	## 		Can't be in the same neighborhood
	## 		Can't be in the blocklist
	## 		Can't exceed max_instances (currently set on the pieces object)

	## Is it better to have this function return the match or assign it directly to the coordinate given?

	## In the future it might be nice to allow users to override this function 
		##   so they are not limited to a single numerical value as selection criteria

	## Saving a list of runner ups at the section level might also be useful - that would be best done here at the moment.

	def choose_match(self, coordinates, pieces, random_max, neighborhood_size, blocklist=[], opts = dict() ):
		'''Choose the closest match that doesn't violate the neighbor constraint'''

		## Sort in the beginning because I think it makes later things faster. 
		## https://stackoverflow.com/a/18411610/1937423
		pieces.sort(key=lambda x: (x.error is None, x.error))

		## Collect all the neighbors to merge with the blocklist.
		## Get_neighbors returns a list of grid sections, so you have to get the pieces from those sections first
		neighbors = self.get_neighbors(coordinates, neighborhood_size) if neighborhood_size != 0 else []
		neighbor_pieces = [neighbor.piece for neighbor in neighbors if hasattr(neighbor,'piece')] 
		master_blacklist = neighbor_pieces+blocklist

		## Right now, when a piece is blocklisted, it's error is just changed to None
		## and None is handled on sort. I don't particularly like this method. 
		for piece in master_blacklist:				
			piece.error = None

		## If a piece has been used it's max times, set error to None
		## If all pieces have been used max times, increase all pieces max instances by adding the original max instances
		## e.g. 2 will become 4, then 6, 8, etc. 
		counter=0
		for piece in pieces:
			if piece.appearances['qty']>=piece.max_instances:
				piece.error = None
				counter+=1
			if counter == len(pieces):
				for piece in pieces:
					piece.max_instances += piece.max_instances0

		## Sort the list again, this time there will probably be some None now. I'm not sure what happens if all are None. 
		pieces.sort(key=lambda x: (x.error is None, x.error))		

		## When you've finally chosen the piece, apply any randomization
		chosen_piece = pieces[ int(random()*random_max) ]

		## Update the appearances information. 
		chosen_piece.appearances['qty']+=1
		chosen_piece.appearances['sections'].append(self.grid[coordinates[0]][coordinates[1]])

		## Directly update the section with the piece (or should I return the piece?)
		self.grid[coordinates[0]][coordinates[1]].piece = chosen_piece




	## #########################################################################################
	## Other helper functions
	## #########################################################################################

	## I tried to research a way of making this better/faster, but apparently slicing is actually
	## just an implementation of nested for loops so it's not that bad
	def get_neighbors(self,coordinates, neighborhood_size = 1):

		neighbors=[]

		n_min_i = max( neighborhood_size * -1 , coordinates[0] * -1 )
		n_max_i = min( neighborhood_size +  1 , self.h_sections - coordinates[0] )

		n_min_j = max( neighborhood_size * -1 , coordinates[1] * -1 )
		n_max_j = min( neighborhood_size +  1 , self.w_sections - coordinates[1] )

		## Loop through all the neighbors that a particular section has.
		for i_offset in range( n_min_i, n_max_i, 1 ): ## row or height
			for j_offset in range( n_min_j, n_max_j, 1 ): ## column or width
				if (i_offset != 0 or j_offset != 0): ## if you're not dealing with urself
					
					## get the neighbor from self
					neighbor = self.grid[coordinates[0]+i_offset][coordinates[1]+j_offset]
					neighbors.append(neighbor)

		return neighbors

 	
	@property
	def unique_piece_filenames(self):

		img_list=[]
		for i in range(self.h_sections):
			for j in range (self.w_sections):
				img_list.append(self.grid[i][j].piece.original_image.filename)
		self._unique_piece_filenames = set(img_list)
		return self._unique_piece_filenames


	@property
	def unique_pieces(self):

		seen = set()
		unique = []
		for row in self.grid:
			for obj in row:
				if obj.piece.original_image.filename not in seen:
					unique.append(obj.piece)
					seen.add(obj)

		self._unique_pieces = unique

		return self._unique_pieces

		
	## SECTION PRIORITY ############################################################################################################################

	## Radial priority is applied to all mosaics by default. 
	## I want to add an option to reverse the priority (highest at the edges and lowest in the center)
	## I want to add a starting point option (from next method below that is grayed out)
	def set_section_priority_radial(self,bwp=None,reverse=False):
		if bwp == None:
			bwp = self.granularity

		w_sections_0 = self.w_sections - 1
		h_sections_0 = self.h_sections - 1
		bw = max(1,int( ( min( w_sections_0, h_sections_0 ) +1 ) *bwp))
		nl = int( min( w_sections_0, h_sections_0 ) / (bw *2) )

		for h_asc in range(self.h_sections):
			h_des = h_sections_0 - h_asc
			for w_asc in range(self.w_sections):
				w_des = w_sections_0 - w_asc
				loop_num = min( min( min( nl, int(h_asc/bw) ), min( nl, int(h_des/bw) ) ), min( min( nl, int(w_asc/bw) ), min( nl, int(w_des/bw) ) ) )
				self.grid[h_asc][w_asc].priority = loop_num


	## Will be redundant with above function once I copy over functionality to specify the starting point
	# def set_section_priority_radial_square(self, starting_section = None, bwp=0.1, reverse=False, aspect = (1,1),  ):
	# 	w_sections_0 = self.w_sections - 1
	# 	h_sections_0 = self.h_sections - 1
	# 	bw = max(1,int( ( min( w_sections_0, h_sections_0 ) +1 ) *bwp))
	# 	center = (int((self.h_sections - 1)/2),int((self.w_sections - 1)/2)) if starting_section == None else starting_section 
	# 	for h_asc in range(self.h_sections):
	# 		for w_asc in range(self.w_sections):
	# 			loop_num = int( max(abs(center[0]-h_asc), abs(center[1]-w_asc)) / bw )+1
	# 			self.grid[h_asc][w_asc].priority = loop_num


	## Sets priority based on edges. Has option to add to or replace current priority
	def set_section_priority_edges(self, radius = 2, kernel = ImageFilter.FIND_EDGES, additive=True, multiplier=1):
		
		self.target.img_bnw = self.target.img.convert('L')
		self.target.img_blur = self.target.img_bnw.filter(ImageFilter.GaussianBlur(radius=radius))
		self.target.img_edges = self.target.img_blur.filter(kernel)

		## Create a new master with the same granularity as original master to break the edge image up into sections
		target_image_edges = MosaicImage( self.target.img_edges )
		edge_master = Mosaic(target_image_edges, granularity=self.granularity)

		## Loop through the sections and get the intensity data
		intensities = [edge_master.grid[i][j].rgb_data for i in range(edge_master.h_sections) for j in range(edge_master.w_sections)]
		whiteness = []

		## Get the average intensity for each section
		for item in intensities:
			whiteness.append(np.mean(item))

		## assign a priority to each section based on it's intensity relative to the rest of the sections by using np.histogram and np.digitize
		hist, bin_edges = np.histogram(whiteness)
		priority = np.digitize(whiteness,bin_edges)

		## Go back through the original master and set the priorities. 
		for i in range(self.h_sections):
			for j in range(self.w_sections):
				if additive:
					self.grid[i][j].priority += priority[j+i*self.w_sections]*multiplier
				else: 
					self.grid[i][j].priority = priority[j+i*self.w_sections]*multiplier


	## Use the coordinates returned by the recognition algorithm to alter the section priority of sections 
	##   that fall partly or completely within the boundary of any deteced objects
	## Has option to add to or replace existing priority
	## Uses cv2 instead of PIL
	def set_section_priority_object_recognition(self, items_to_detect = None, additive=True, keep_default_cascades=False):

		"""Detect objects and update their priority.
			Default is faces and facial features.
			Look for other objects if you have haarcascade xml file.
			Read code for how to structure this argument"""

		items_to_detect_default = [ 	dict( 	cascade = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml',
												scale_factor = 1.1,
												min_neighbors = 3,
												priority = 10,
												rect_color=(0,255,0)								),

										dict( 	cascade = cv2.data.haarcascades + 'haarcascade_features.xml',
												scale_factor = 1.1,
												min_neighbors = 3,
												priority = 20,
												rect_color=(255,0,0)								),	

										dict( 	cascade = cv2.data.haarcascades + 'haarcascade_eye.xml',
												scale_factor = 1.1,
												min_neighbors = 3,
												priority = 5,
												rect_color=(255,255,0)								),	
										]

		## Backup Defaults
		default_scale_factor = 1.1
		default_min_neighbors = 3
		default_priority = 10
		default_rect_color = (0,0,255)

		imagecv = cv2.cvtColor(np.array(self.target.img), cv2.COLOR_RGB2BGR)
		gray = cv2.cvtColor(imagecv, cv2.COLOR_BGR2GRAY)
		detections=[]

		if items_to_detect == None:
			items_to_detect = items_to_detect_default
		else:
			if keep_default_cascades:
				for item in items_to_detect_default:
					items_to_detect.append(item)

		for item_dict in items_to_detect:
			
			## If the item_dict doesn't contain a cascade, then let the user know and skip it
			if 'cascade' not in item_dict.keys():
				print("no cascade was passed for {0}, skipping".format(str(item_dict)))
				continue
			else:
				cascade_xml = item_dict['cascade']

			## Get the basename of the cascade file
			name = os.path.basename(cascade_xml)

			## Set the remaining arguments based on their existence
			scale_factor = item_dict['scale_factor'] if 'scale_factor' in item_dict.keys() else default_scale_factor
			min_neighbors = item_dict['min_neighbors'] if 'min_neighbors' in item_dict.keys() else default_min_neighbors
			rect_color = item_dict['rect_color'] if 'rect_color' in item_dict.keys() else default_rect_color
			priority = item_dict['priority'] if 'priority' in item_dict.keys() else default_priority

			## Identify the objects
			cascade = cv2.CascadeClassifier(cascade_xml)

			## If the haarcascade file is no good then print the error and go to the next one
			try:
				items = cascade.detectMultiScale(gray, scale_factor, min_neighbors)
			except cv2.error as e:
				print("the following error occured attempting to use the provided cascade for {0}".format(name))
				print(e)
				continue

			print("Found {0} items using {1}!".format(len(items),name))
			detections.append(dict(items = items,priority=priority,rect_color=rect_color))

		## Draw a rectangle around the objects being detected
		for detect in detections:
			for (x, y, w, h) in detect['items']:
			    _ = cv2.rectangle(imagecv, (x, y), (x+w, y+h), detect['rect_color'], 2)

		## Save marked up image to self
		self.target.imagecvfeatures = imagecv

		## Loop through each section and adjust the priority 
		for h_asc in range(self.h_sections):
			for w_asc in range(self.w_sections):
				section_top = h_asc*self.section_height
				section_bot = h_asc*self.section_height + self.section_height
				section_left = w_asc*self.section_width
				section_right = w_asc*self.section_width + self.section_width

				for detect in detections:
					for (x,y,w,h) in detect['items']:
						object_top = y
						object_bot = y+h
						object_left = x
						object_right = x+w

						## If it's in the boundary of a detected item
						if (section_bot > object_top and section_top < object_bot) and (section_right > object_left and section_left < object_right):
							if additive:
								self.grid[h_asc][w_asc].priority+=detect['priority']
							else:
								self.grid[h_asc][w_asc].priority=detect['priority']


	def set_section_priority_zero(self):
		## Set all the priorities back to 0 so that the alrgorithm just goes left to right top to bottom, that's what it will do right?
		for h_asc in range(self.h_sections):
			for w_asc in range(self.w_sections):
				self.grid[h_asc][w_asc].priority = 0


	def get_section_priority(self):
		return [[self.grid[j][i].priority for i in range(self.w_sections)] for j in range(self.h_sections)]


	def show_section_priority(self):
		size = (8,8)
		data = self.get_section_priority()
		fig = plt.figure()
		fig.set_size_inches(size)
		ax = plt.Axes(fig, [0., 0., 1., 1.])
		ax.set_axis_off()
		fig.add_axes(ax)
		plt.set_cmap('hot')
		ax.imshow(data, aspect='equal')
		plt.axis("image")
		plt.show()


	def print_section_priority(self):
		for i in range(self.h_sections):
			print('')
			for j in range(self.w_sections):
				print(str(self.grid[i][j].priority).zfill(2),end=' ')
		print('')

	## #########################################################################################
	## TOUCH UP FUNCTIONS
	## #########################################################################################

	## To update specific instances of pieces after mosaic creation. It currently still listens to max_instances and neighborhood constraints.
	## In order to have pieces chosen with different settings, you must first set them on self and then call this function.
	def update_all_instances_of(self,coordinates,piece_list,replace_self = True ,opts = dict()):

		## Example Function Call
		#master.update_all_instances_of(master.grid[1][9].piece,piece_list)
		
		## Get the piece that the section at these coordinates has
		piece = self.grid[coordinates[0]][coordinates[1]].piece

		## get all the sections that have this piece - this uses filename at the moment, though it should use an id.
		sections=[]
		piece_file_name = piece.original_image.filename.split('/')[-1]
		for i in range(self.h_sections):
			for j in range(self.w_sections):
				if self.grid[i][j].piece.original_image.filename.split('/')[-1] == piece_file_name:
					sections.append(self.grid[i][j])

		## Remove the specified instance if specified. 
		if replace_self == False:
			sections = [section for section in sections if section.coordinates != coordinates]	

		## This is like creating the mosaic the first time except you are looping through specific sections
		## instead of all sections. 
		for section_index in range(len(sections)):
			section = sections[section_index]

			for i in range(len(piece_list.pieces)):
				self.comparison_function( 	section									,
											piece_list.pieces[i] 					, 
											f 				= self.f 				, 
											rgb_weighting 	= self.rgb_weighting	,
											reset_obj1		= i==0 					, #first iteration of a new section
											reset_obj2 		= section_index==0		, #all iterations of the first section
											opts 			= opts 					,	)

			self.choose_match(section.coordinates, piece_list.pieces, self.random_max, self.neighborhood_size, blocklist=[section.piece], opts=opts )

		## Update the appearances. If replacing specified instance and all others it will be 0
		## If not replacing the clicked instance, it will be 1 and the section will be the one specified. 
		## I could do something like remove the specific section as you go through each section, but this is faster
		## I don't see anything wrong with it yet unless this function fails in the middle
		## But I think I'll need a way to clean up the appearances functionality later anyway, bottom line, don't
		## trust the appearances thing to always be correct, it's good reference, but it's not ready to rely on yet. 
		if replace_self:
			piece.appearances = dict(qty=0,sections=[])
		else:
			piece.appearances = dict(qty=1,sections=[self.grid[coordinates[0]][coordinates[1]]])
		return sections
	

	#def update_all_instances_of_except_self(self, coordinates, piece_list, replace_self = False, opts = dict()):
	#	return self.update_all_instances_of(coordinates,piece_list,replace_self, opts)


	## This function is supposed to immune sections from having their piece chosen by any function that sets pieces
	##   but it's not in use yet by functions that set pieces.
	def pin(self,coordinates):
		if hasattr(self.grid[coordinates[0]][coordinates[1]],"piece"):
			self.grid[coordinates[0]][coordinates[1]].pinned = True



	## #########################################################################################
	## FUNCTIONS THAT SAVE THINGS 
	## #########################################################################################

	## Would be nice to have a mosaic that saved everything you needed to recreate the mosaic object including
	## 		target image, pieces, parameters, etc.
	#def save_mosaic():
	#	pass

	#@wsc.timer
	def save_sections(self):
		timestamp = str(int(datetime.utcnow().timestamp()))
		save_dir = os.path.splitext(self._target.original_image.filename)[0]+'/sections/sections-'+timestamp+'/'
		os.makedirs(save_dir)
		for i in range(len(self.grid)):
			for j in range(len(self.grid[i])):
				section = self.grid[i][j].img
				section = section.resize( PIECE_DEFAULT_SAVE_SIZE ) ## This is currently the default - 
				section.save(save_dir+str(i)+"-"+str(j)+".png")
		print(save_dir)
		return save_dir


	## Outputs html, css, a copy of target image, and necessary pieces to a child directory of the target image.  
	## Can definitely be improved, but it was originally written to view mosaics more conveniently than using a giant image.
	#@wsc.timer
	def output_html(self,section_dim = 50):

		start = datetime.utcnow()
		timestamp = int(start.timestamp())

		## Would be nice to clean this up a little bit, doesn't seem clean
		target_image_filepath = self._target.original_image.filename
		base_save_directory = os.path.splitext(target_image_filepath)[0]
		html_save_directory = os.path.join( base_save_directory,'html','html-'+str(timestamp) )
		pieces_save_directory = os.path.join( html_save_directory , 'pieces' )
		img_filename = os.path.split(base_save_directory)[-1]

		os.makedirs(html_save_directory) if not os.path.exists(html_save_directory) else None
		os.makedirs(pieces_save_directory) if not os.path.exists(pieces_save_directory) else None

		html_output_filepath = os.path.join( html_save_directory, img_filename+'-'+str(int(datetime.utcnow().timestamp()))+'.html' )	
		css_output_filepath = os.path.join(html_save_directory,'mosaicStyle.css')

		doc, tag, text = Doc().tagtext()
		doc.asis('<!DOCTYPE html>')

		with tag('html', lang = 'en'):
			with tag('head'):
				doc.stag('meta', charset='utf-8')
				with tag('title'):
					text("PhotoMosaic")
				doc.stag('meta', name='description', content='PhotoMosaic Output')
				doc.stag('meta', name='author', content='James McGlynn')
				doc.stag('link', rel='stylesheet', href='mosaicStyle.css')

			with tag('body'):
				with tag('div', id='targetImageContainer'):
					doc.stag('img', src='target.png')
				with tag('div', klass='imageContainer'):
					for i in range(self.h_sections):
						with tag('div', klass='row', id='row-'+str(i)):
							for j in range(self.w_sections):
								with tag('div', klass='col', id='cell-'+str(i)+'-'+str(j)):
									## How to avoid hardcoding the /?
									doc.stag('img', src='pieces/'+os.path.split(self.grid[i][j].piece.original_image.filename)[-1])
					
		with open(html_output_filepath, 'w') as fh:
			output = indent(doc.getvalue())
			fh.write(output)
			#section_size = 50
			image_container_width = self.w_sections * section_dim

		css_text = '''
* {{box-sizing:border-box;}}
body {{background:black;
	color:white;
	padding:0;
	margin:0;
	border:0;}}
#targetImageContainer{{position:absolute;;}}
#targetImageContainer img{{width:{image_container_width}px;}}	
.imageContainer {{overflow:hidden;
	position:absolute;
	border:0;
	margin:0;
	padding:0;
	z-index:10;
	width:{image_container_width}px;}}
.col img {{padding:0px;
	margin:0px;
	opacity:1;
	height:{section_dim}px;
	width:{section_dim}px;}}
.row {{width:100%;
	padding:0;
	margin:0;}}
/* Clear floats after image containers */
.row::after {{clear: both;
	content: "";
	display:block;}}
.col {{float: left;
	padding: 0px;
	margin:0px;
	height:{section_dim}px;}}'''

		css_text = css_text.format(image_container_width = image_container_width, section_dim = section_dim)

		with open(css_output_filepath, 'w') as fh:
			fh.write(css_text)

		## Save the necessary items. Wait I thought the pieces class had a method for this?
		for item in self.unique_pieces:
			item.img.save( os.path.join(pieces_save_directory, os.path.split(item.original_image.filename)[1]) )

		## Save the target in there with everyone!
		self._target.img.save( os.path.join( html_save_directory,'target.png' ) )

		return html_output_filepath


	## These mosaic output images can get massive if the piece save size isn't small enough
	#@wsc.timer
	def output_to_image(self,opts=dict()):

		start = datetime.utcnow()
		
		## This assumes all thumbnails are the same dimensions - ok for now, 
		## but in the future I want to avoid this limitation
		thumbnail_size = self.grid[0][0].piece.img.size
		mosaic_width  = self.w_sections * thumbnail_size[0]
		mosaic_height = self.h_sections * thumbnail_size[1]

		## Build the mosaic from the pieces
		im = Image.new('RGB', (mosaic_width,mosaic_height))
		for i in range(self.h_sections):
			for j in range(self.w_sections):
				im.paste(self.grid[i][j].piece.img,(j*thumbnail_size[0],i*thumbnail_size[1]))

		if ('overlay_alpha' in opts.keys()) and (opts['overlay_alpha'] > 0):
			overlay = self._target.img.resize(im.size)
			overlay.putalpha(opts['overlay_alpha'])
			im.putalpha(255)
			im = Image.alpha_composite(im, overlay)

		## figure out where to put it. 
		target_image_filepath = self._target.original_image.filename
		mosaic_save_directory = os.path.join( os.path.splitext(target_image_filepath)[0],'mosaics' )
		os.makedirs(mosaic_save_directory) if not os.path.exists(mosaic_save_directory) else None		
		# mosaic_save_filepath = mosaic_save_directory+'P'+str(round(100*global_opts_dict['granularity']))+'F'+str(global_opts_dict['f'])+'R'+str(global_opts_dict['random_max'])+'-'+str(int(datetime.utcnow().timestamp()))+'.png'
		
		if 'filename' in opts.keys():
			if os.path.isabs(opts['filename']):
				mosaic_save_filepath = os.path.splitext(opts['filename'])[0]+'-'+str(int(start.timestamp()))+os.path.splitext(opts['filename'])[1]
			else:	
				mosaic_save_filepath = os.path.join(mosaic_save_directory,os.path.splitext(opts['filename'])[0]+'-'+str(int(start.timestamp()))+os.path.splitext(opts['filename'])[1] )
		else:			
			mosaic_save_filepath = os.path.join(mosaic_save_directory,str(int(start.timestamp()))+'.png')

		im.save(mosaic_save_filepath, quality=95)

		return mosaic_save_filepath


	
	## #########################################################################################
	## FUTURE DEV
	## #########################################################################################

	## Not sure about the necessity of this function
	def generate_output_filename(self,include_ts=True): ## Jury's still out on the name of this function
		filename = "F={f} NS={ns} R={r} G={g} CF={cf} NP={np}.png".format( f=f, ns=ns, r=r, g=g, cf=cf, np=np )
		return filename


	## I would like to improve the functions that allow for editing the mosaic post creation. I believe I have one that is in operation
	## 		but even more would be useful. 

	def remove_all_instances_of(self):
		''' remove all instances of a particular piece from a mosaic '''
		pass


	def remove_all_but_this_instance_of(self):
		''' remove all instance of a particular piece from a mosaic EXCEPT the one(s?) given '''
		pass


	def reset_instance_at(self, coordinates , new_img = None, opts=dict()):
		pass


## END MOSAIC CLASS




## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
# ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##


## The main responsibility of this class is to take in images or image locations and create a list of 
## 		pieces usable by the mosaic.create method.

## During developement I mostly used my filesystem, but I would like to be able to use database queries in the future 


## Some executive decisions to make developement easier
## Pieces should:
## 		Always have exif-data removed
## 		Always be saved as .png (if they get saved)
## 		Be rotated if they need to be rotated (based on metadata)


#@wsc.timer
class PieceList:

	def __init__(self,arg=None,max_instances = 5):
		self._default_save_size = PIECE_DEFAULT_SAVE_SIZE
		self._accepted_filetypes = PIECE_ACCEPTED_FILETYPES
		self._max_instances = max_instances
		self._max_instances0 = max_instances
		self._pieces = self.__process_pieces_arg(arg)

		
	def __process_pieces_arg(self,arg):
		arg_type = type(arg)
		if arg_type is type(None):
			pieces = []	
		elif arg_type is type(str()):
			if os.path.isdir(arg):
				self.directory = arg
				pieces = self.__create_piece_list_from_directory(arg)
			else:
				pieces = []
		elif arg_type is type(list()):
			pieces = self.__create_piece_list_from_list_of_objects(arg)
		else:
			warning = '''WARNING: The argument supplied to PieceList was not a path or a list of objects with the img attribute.'''
			print (warning)
			pieces = []
		return pieces


	## Pass in a list of objects and the attribute at which there is an image
	def __create_piece_list_from_list_of_objects(self,list_of_objects,attribute='img'):
		pieces=[]
		for item in list_of_objects:
			piece_pillow_image = Image.open(getattr(item,attribute))
			if hasattr(getattr(item,attribute),'name'):
				piece_pillow_image.filename = os.path.basename(getattr(item,attribute).name)
			piece_mosaic_image = MosaicImage(piece_pillow_image)

			## sometimes thumbnailing breaks because of the following error I believe the warning is related:

				# Warning (from warnings module):
				#   File "C:\Users\JamesM\Projects\Programming\MosaicMakerWeb\env\lib\site-packages\PIL\TiffImagePlugin.py", line 819
				#     warnings.warn(str(msg))
				# UserWarning: Corrupt EXIF data.  Expecting to read 4 bytes but only got 0. 
				# Traceback (most recent call last):
				#   File "<pyshell#81>", line 1, in <module>
				#     piece_list = mm.PieceList(list(pieces))
				#   File "C:\Users\JamesM\Projects\Programming\MosaicMaker\wantsomechocolate.py", line 11, in wrapper_timer
				#     value = func(*args, **kwargs)
				#   File "C:\Users\JamesM\Projects\Programming\MosaicMaker\mosaic_maker.py", line 962, in __init__
				#     self._pieces = self.__process_pieces_arg(arg)
				#   File "C:\Users\JamesM\Projects\Programming\MosaicMaker\mosaic_maker.py", line 982, in __process_pieces_arg
				#     pieces = self.__create_piece_list_from_list_of_objects(arg)
				#   File "C:\Users\JamesM\Projects\Programming\MosaicMaker\mosaic_maker.py", line 1005, in __create_piece_list_from_list_of_objects
				#     piece_mosaic_image.to_thumbnail(size = self._default_save_size)
				#   File "C:\Users\JamesM\Projects\Programming\MosaicMaker\mosaic_maker.py", line 133, in to_thumbnail
				#     self.correct_orientation()
				#   File "C:\Users\JamesM\Projects\Programming\MosaicMaker\mosaic_maker.py", line 126, in correct_orientation
				#     self._img = wsc.rotate_based_on_exif(self._img)
				#   File "C:\Users\JamesM\Projects\Programming\MosaicMaker\wantsomechocolate.py", line 50, in rotate_based_on_exif
				#     exif=dict(image._getexif().items())
				#   File "C:\Users\JamesM\Projects\Programming\MosaicMakerWeb\env\lib\site-packages\PIL\PngImagePlugin.py", line 973, in _getexif
				#     return self.getexif()._get_merged_dict()
				#   File "C:\Users\JamesM\Projects\Programming\MosaicMakerWeb\env\lib\site-packages\PIL\PngImagePlugin.py", line 979, in getexif
				#     return super().getexif()
				#   File "C:\Users\JamesM\Projects\Programming\MosaicMakerWeb\env\lib\site-packages\PIL\Image.py", line 1391, in getexif
				#     self._exif.load(exif_info)
				#   File "C:\Users\JamesM\Projects\Programming\MosaicMakerWeb\env\lib\site-packages\PIL\Image.py", line 3422, in load
				#     self._info = TiffImagePlugin.ImageFileDirectory_v2(self.head)
				#   File "C:\Users\JamesM\Projects\Programming\MosaicMakerWeb\env\lib\site-packages\PIL\TiffImagePlugin.py", line 491, in __init__
				#     raise SyntaxError(f"not a TIFF file (header {repr(ifh)} not valid)")
				# SyntaxError: not a TIFF file (header b'' not valid)

			try:
				piece_mosaic_image.to_thumbnail(size = self._default_save_size)

				piece_mosaic_image.max_instances = self._max_instances
				piece_mosaic_image.max_instances0 = self._max_instances0

				## Add the item as an attribute to the piece in case I need it later, but maybe remove it at some point if it's uncessary.
				piece_mosaic_image.original_object = item

				piece_mosaic_image.appearances = dict(	qty 					= 0 					, 
														sections 				= [] 					, 
														max_instances 			= self._max_instances 	, 
														max_instances0 			= self._max_instances0 	,
														max_instance_multiplier = 1 					,	)

				# I hard coded some stuff dealing with 3 layer images, so lazy!!!!!
				if piece_mosaic_image.rgb_data_shape[2] == 3:
					pieces.append(piece_mosaic_image)

			except SyntaxError:
				pass

		if len(pieces) == 0:
			print("WARNING: No pieces were found in the given list")

		return pieces


	def __create_piece_list_from_directory(self, directory, ext_list = ['.png',',jpg','.jpeg','.tiff']):

		items = []
		for root, dirs, files in os.walk(directory):
			for file in files:
				if os.path.splitext(file)[-1] in ext_list:
					items.append(os.path.join(root,file))		

		pieces = []
		for item in items:	
			extension = os.path.splitext(item)[-1]
			if extension in self._accepted_filetypes:
		
				#piece_pillow_image = Image.open( os.path.join(directory,item) )
				piece_pillow_image = Image.open(item)
				piece_mosaic_image = MosaicImage(piece_pillow_image)

				try:
					piece_mosaic_image.to_thumbnail(size=self._default_save_size)
				except SyntaxError as err:
					print(err)
					print('There was a problem thumbnailing '+piece_pillow_image.filename)
		
				piece_mosaic_image.max_instances = self._max_instances
				piece_mosaic_image.max_instances0 = self._max_instances0
				piece_mosaic_image.appearances = dict(	qty 					= 0 					, 
														sections 				= [] 					, 
														max_instances 			= self._max_instances 	, 
														max_instances0 			= self._max_instances0 	,
														max_instance_multiplier = 1 					,	)

				# I hard coded some stuff dealing with 3 layer images, so lazy!!!!!!!
				if piece_mosaic_image.rgb_data_shape[2] == 3:
					pieces.append(piece_mosaic_image)

		if len(pieces) == 0:
			print("WARNING: No pieces were found in the given directory.")

		return pieces


	@property
	def default_save_size(self):
		return self._default_save_size
	@default_save_size.setter
	def default_save_size(self,size):
		self._default_save_size = size
		for piece in self.pieces:
			piece.to_thumbnail(size = self._default_save_size)


	@property
	def pieces(self):
		return self._pieces
	@pieces.setter
	def pieces(self,arg):
		self._pieces = self.__process_pieces_arg(arg)


	@property
	def qty(self):
		self._qty = len(self.pieces)
		return self._qty


	def flush_instance_counts(self):
		for piece in self.pieces:
			piece.appearances = dict(qty=0,sections=[])


	#@wsc.timer
	def save(self, directory, file_ext = '.png'):
		
		os.makedirs(directory) if not os.path.exists(directory) else None
		
		for piece in self.pieces:
			filename = os.path.splitext(os.path.split(piece.original_image.filename)[-1])[0]+file_ext
			filepath = os.path.join(directory,filename)
			piece.img.save(filepath, quality = 99)




## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
# ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
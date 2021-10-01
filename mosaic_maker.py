#! python3

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
# ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

from PIL import Image, ImageOps, ImageFilter

import numpy as np
import os, copy
from datetime import datetime
from random import random
from math import floor

from yattag import Doc
from yattag import indent

import wantsomechocolate as wsc
#from comparison_functions import error_functions, reduce_functions, rgb_avg_comparison
import comparison_functions as cf

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
# ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

## Should come from a configuration file at some point. 
PIECE_DEFAULT_SAVE_SIZE = (128,128)
PIECE_ACCEPTED_FILETYPES = ['.png','.jpg']
IMAGE_DEFAULT_COMPARISON_SIZE = (64,64)

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
# ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

## This file defines the following classes all related to creating photo mosaics. 
## Mosaic Image 	- A wrapper for a pillow image object
## Mosaic 			- Holds information about the sections
## CompareImages	- Just a holder for the comparison functions used to compare sections and pieces
## PieceList 		- Holds the pieces, has some basic functionality for getting a piece list from a directory

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
		## If people wanted to write custom comparison functions that allowed for this I guess I could make 
		## this a optional thing?
		if self.original_image.mode == 'RGBA':
			self.__rgba_to_rgb()
		self.__update()


	## To allow for a string instead of an Image object
	def __process_image_argument(self, img):
		if type(img) == type('string'):
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


	## for dealing with rgba
	def __rgba_to_rgb(self):
		new_img = Image.new("RGB", self._img.size, (255,255,255))
		new_img.paste(self._img, mask=self._img.split()[3])
		self._img = new_img
		self.__update()


	## I have this as an public function, but the only thing it can do is operate on itself, useful?
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


	## just a wrapper for resize that knows about the default save size.
	def resize(self,size = PIECE_DEFAULT_SAVE_SIZE):
		if self._img.size == size:
			pass
		else:	
			self._img = self._img.resize(size)
			self.__update()

	## I put this orientation stuff in a function kind of outside of the project, but maybe I'll roll it back in. 
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

@wsc.timer
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
		## If there is a comparison function passed directly, do it up!
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

		## If given nothing, and hte object does not have a default df defined, use the default rf and ef.  
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

	## Should allow the user to specify arguments here that set parameters at the mosaic level. 
	## e.g. if I say create with granularity = 1/16, but master has g=1/32, set master g = 1/16.
	@wsc.timer
	def create( 	self 			, 
					piece_list		, 					
					opts= dict()	, 	):

		''' Create a mosaic - you can use custom comparison functions! '''

		print('Starting to Create!')

		## When creating a new mosaic from an existing master, you need to flush the instance counts from the 
		## piece list, otherwise the piece list will think it already has a bunch of stuff
		## in the mosaic. 
		piece_list.flush_instance_counts()


		## WHERE THE MAGIC HAPPENS

		## I used to go through each section in order left to right, top to bottom.

		#for h_section in range(self.h_sections):			
		#	print('')
		#	for w_section in range(self.w_sections):
		#		print('x', end = '')

		## Now instead of that I sort all the sections based on priority order and loop through that. 
		sections_list = [self.grid[h_section][w_section] for h_section in range(self.h_sections) for w_section in range(self.w_sections)]
		sections_list.sort(key=lambda x: (x.priority is None, x.priority), reverse = True)

		## Compare each section to each piece - keeping track of progress here will be useful later. 
		progress1 = progress2 = 0
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
				

			## Should I have choose match return the match instead of assigning directly to the coordinate given?
			## Should I allow users to override cm so they are not limited to a single numerical value as selection criteria?
			## I might want to save error results for all or many pieces at the section level. 
			self.choose_match( sections_list[i].coordinates, piece_list.pieces, self.random_max, self.neighborhood_size, blocklist=[], opts=opts )
			## Could be section_list[i].piece = self.choose.......


			## At this point, a given section has just finished being compared to all pieces. 
			## More efficient might be to have comparison function save error results on obj1 for all obj2
			## A workaround for now might be to just do something here (would require looping through all piece again)
			## What's one more time though when you're already doing it hundreds of time lmao. 

			## For giving some user feedback on mosaics that take a long time to calculate?
			progress2 = round(i*100/len(sections_list),0)
			if progress1!=progress2:
				print('#',end='')
				progress1=progress2

		print('')



	## Choose match has a big job right now. It takes a section, piece list, and some other stuff
	## and tries to choose a match while satisfying all the criteria.
	## 		Can't be in the same neighborhood
	## 		Can't be in the blocklist
	## 		Can't exceed max_instances (currently set on the pieces object)
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

	## I tried to research a way of making this better, but apparently slicing is actually
	## just an implementation of nested for loops?
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



	## I think I would rather this property return a unique object list?
	## A unique list of objects based on a particular attribute though. Which I don't know how to do at the moment. 	
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
					unique.append(obj)
					seen.add(obj.piece.original_image.filename)

		self._unique_pieces = unique

		return self._unique_pieces

		
	## SECTION PRIORITY

	## This is the default, I also want to be able to allow for a reverse arg, but that's not implemented yet. 
	def set_section_priority_radial(self,bwp=0.1,reverse=False):
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


	def set_section_priority_radial_square(self, starting_section = None, bwp=0.1, reverse=False, aspect = (1,1),  ):
		w_sections_0 = self.w_sections - 1
		h_sections_0 = self.h_sections - 1
		bw = max(1,int( ( min( w_sections_0, h_sections_0 ) +1 ) *bwp))

		center = (int((self.h_sections - 1)/2),int((self.w_sections - 1)/2)) if starting_section == None else starting_section 
		for h_asc in range(self.h_sections):

			for w_asc in range(self.w_sections):

				loop_num = int( max(abs(center[0]-h_asc), abs(center[1]-w_asc)) / bw )+1
				self.grid[h_asc][w_asc].priority = loop_num


	def show_section_priority(self):
		for i in range(self.h_sections):
			print('')
			for j in range(self.w_sections):
				print(str(self.grid[i][j].priority).zfill(2),end=' ')


	def set_section_priority_edges(self, radius = 2, kernel = ImageFilter.FIND_EDGES):
		
		#if kernel == None:
		#	kernel = ImageFilter.FIND_EDGES
		self.target.img_bnw = self.target.img.convert('L')
		self.target.img_blur = self.target.img_bnw.filter(ImageFilter.GaussianBlur(radius=radius))
		#self.img_edges = self.img_blur.filter(ImageFilter.FIND_EDGES)
		self.target.img_edges = self.target.img_blur.filter(kernel)
		##img_laplace = img_blur.filter(ImageFilter.Kernel((3, 3), (-1, -1, -1,
		##					      -1,  8, -1,
		##					      -1, -1, -1), 1, 0))

		## This creates an images that has only edges in it (edges are white, rest of image is black)
		## now I have to go through and see which sections have the most edges (most white) and
		## give them the highest priority? 
		## https://cyroforge.wordpress.com/2012/01/21/canny-edge-detection/

		target_image_edges = MosaicImage( self.target.img_edges )
		edge_master = Mosaic(target_image_edges, granularity=self.granularity)
		#from comparison_functions import reduce_functions as rf
		#import numpy as np
		#np.mean(edge_master.grid[2][8].rgb_data)
		intensities = [edge_master.grid[i][j].rgb_data for i in range(edge_master.h_sections) for j in range(edge_master.w_sections)]
		whiteness = []
		for item in intensities:
			whiteness.append(np.mean(item))
		hist, bin_edges = np.histogram(whiteness)
		priority = np.digitize(whiteness,bin_edges)

		for i in range(self.h_sections):
			for j in range(self.w_sections):
				self.grid[i][j].priority = priority[j+i*self.w_sections]


	## #########################################################################################
	## TOUCH UP FUNCTIONS
	## #########################################################################################

	## This function is currently working - still listens to max_instances and neighborhood constraints. All around good time. 
	## But it needs to take a section or coordinates and then get the piece from there because 
	## when there is a front end that's the most important info,
	## this would also allow me to have update_all_instances_except_this_one be the same function with a different argument.
	## If this section doesn't have a piece, then just return None?


	## I was testing this function on a image of just black, like an idiot
	## this function needs to reset obj1 and obj2 intelligently, like when creating a mosaic the first time. 
	## I want to be able to override the settings used to find matches. Not implemented yet

	## This function needs to update the appearances info for all affected pieces! It's not doing that right now
	def update_all_instances_of(self,coordinates,piece_list,replace_self = True ,opts = dict()):

		#master.update_all_instances_of(master.grid[1][9].piece,piece_list)
		
		## get the piece that the section at these coordinates has
		piece = self.grid[coordinates[0]][coordinates[1]].piece

		## get all the sections that have this piece - this uses filename - do something better
		sections=[]
		piece_file_name = piece.original_image.filename.split('/')[-1]
		for i in range(self.h_sections):
			for j in range(self.w_sections):
				if self.grid[i][j].piece.original_image.filename.split('/')[-1] == piece_file_name:
					sections.append(self.grid[i][j])




		## Remove the clicked instance if specified. 
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

		## Update the appearances. If replacing clicked instance and all others it will be 0
		## If not replacing the clicked instance, it will be 1 and the section will be the one clicked. 
		## I could do something like remove the specific section as you go through each section, but this is faster
		## I don't see anything wrong with it yet unless this function fails in the middle
		## But I think I'll need a way to clean up the appearances functionality later anyway, bottom line, don't
		## trust the appearances thing to always be correct, it's good reference, but don't rely on it yet. 
		if replace_self:
			piece.appearances = dict(qty=0,sections=[])
		else:
			piece.appearances = dict(qty=1,sections=[self.grid[coordinates[0]][coordinates[1]]])


		return sections
	

	def update_all_instances_of_except_self(self, coordinates, piece_list, replace_self = False, opts = dict()):
		return self.update_all_instances_of(coordinates,piece_list,replace_self, opts)


	def pin(self,coordinates):
		if hasattr(self.grid[coordinates[0]][coordinates[1]],"piece"):
			self.grid[coordinates[0]][coordinates[1]].pinned = True



	## #########################################################################################
	## FUNCTIONS THAT SAVE THINGS 
	## #########################################################################################

	@wsc.timer
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
	## I think this function should also make a database entry so you can recreate it later!
	## I now have access to all the information that is used to build the mosaic on the mosaic attributes, so use them
	## 1.) when creating the directory name, and 2.) when building the html (put it in the metadata)
	@wsc.timer
	def output_html(self,section_dim = 50):

		start = datetime.utcnow()
		timestamp = int(start.timestamp())

		## da-da-da-definitly need to clean this up. 
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

		## Sve the necessary items. Wait I thought the pieces class had a method for this?
		for item in self.unique_pieces:
			im = Image.open(item.piece.original_image.filename)
			im_name = os.path.split(item.piece.original_image.filename)[-1]
			im.save( os.path.join(pieces_save_directory,im_name))

		## Save the target in there with everyone!
		self._target.img.save( os.path.join( html_save_directory,'target.png' ) )

		return html_output_filepath


	## These mosaic output images can get massive, so I'm not making this a property
	@wsc.timer
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

	## Hmmmmm, how to get the info I want? Is this even a function I actually want?	
	def generate_output_filename(self,include_ts=True): ## Jury's still out on the name of this function
		filename = "F={f} NS={ns} R={r} G={g} CF={cf} NP={np}.png".format( f=f, ns=ns, r=r, g=g, cf=cf, np=np )
		return filename


	## I'm going to use filename for now, probably will regret that, but I don't care at the moment?
	## maybe try using image data instead? both have downsides I think. 
	## Anyway, the main thing it needs is a mosaic image object to be passed to it
	## This object, for now, needs a file name.
	## then it goes through all the sections of the mosaic and if a piece has the same filename as the one
	## you want to remove, than BAM, find a new match for that section.
	## That means this function also needs information on how to find the new matches! 
	## i.d. compare function, random max, weather or not to enforce neighbor constraints?
	## true I could make that a variable!
	def remove_all_instances_of(self):
		''' remove all instances of a particular piece from a mosaic '''
		pass
		'''
		Pass in a a coordinate

		'''

	def remove_all_but_this_instance_of(self):
		''' remove all instance of a particular piece from a mosaic EXCEPT the one(s?) given '''
		pass


	def reset_instance_at(self, coordinates , new_img = None, opts=dict()):
		pass
		'''
		You are given a grid spot and the idea is to replace it with something else
		If you are given the something else than great! wait, if you already have the new piece, 
		you can just update the MosaicImage object with the new image, you don't need a special function for that

		How about when making the grid, MosaicImage objects get a method added to them! called reset piece
		or something like that. If you call that method, it uses the same setting as before and gets a new
		match for that spot and adds the one it was previously to a list so that it doesn't keep picking the same
		or switching back and forth between the same few options?
		This brings me back to my point about storing some close matches to begin with, then this function would be 
		pretty simple, just pick a new match from that list and add the current one to the blacklist. 
		Maybe I could even just update this 'black_list' as I go along making the mosaic to begin with 
		so that the neighborhood logic would be just a sub-implementation of that and would probably be faster?
		hmmm, would be kind of tough actually I think to do it this way, as you looped around from one side
		of the target image to the other, you'd basically have to completely reset the blacklist anyway? maybe you
		could have two blacklists, a neighborhood one and another one? for the neighborhood one you could take from an
		adjacent one and modify it? seems like a lot of work, let's forget about it for now. 

		So for this function, let's assume I want to completely recalculate a piece for a section with all new settings
		and stuff. How do I want to handle the arguments?
		I have my object, I have my piece_list the default is the one on master, but I could override it with a new one
		if I wanted to. In this case I just have to.... for piece in piece_list call the compare function to get all the
		errors, then call choose match, but now choose match has to know about the neighbors (it does), but ALSO the 
		custom blacklist. When it tries to select a new match. 

		I want to think of a new method for choose match
		I want to save the best matches regardless of neighbors and blacklist when you run through everything the first time
		But then I want to pick the best match (with the randomization of course) after accounting for these blacklists
		How many to save? customizable of course, the default should be 20+qty of pictures in the neighborhood, so for a ns 
		of 3 there are 49 (3up 3down 3left 3right is a 7x7 square) + 20. 
		I think maybe a separate 'get_neighbors' function would be pretty useful
		Then when I'm choosing a match for the first time, I save the (in this example) 69 references to various objects in
		pieces (it doesn't actually use that much more memory if I don't deep copy these objects, which I think I can get 
		away doing)


		I call get_neighbors (maybe this is a calculated property?) and then I look at those two lists 
		to choose the match the same way I've been doing? null the error of pieces in neighbors and in the misc_blacklist?
		then get the best match after randomization?

		The downside here is that because I'm hesitant to copy piece list I won't know the relative likeness of the 
		images in the closest matches, neighbors, blacklist, etc because their error values will continue to change as the
		mosaic is being built. if I want to save all the individual errors associated with each peice
		that's thousands of pieces of information even for a small mosaic. 

		The benifit of having that information is that single updates happen more quickly, or the mosaic could be
		'randomized' fairly quickly, but having the closes match list, the mosaic could be much more quickly
		'randomized' anyway, so I think it's fine the way I'm thinking about doing it. 

		So I guess step number one is a method that gets the neighbors of a particular section
		This method should live where? I think it makes sense for it to live on the master
		but I still think it should be calculated and also take an argument for the cooridate in question
		and also the size of the neighborhood! default is 1 (3x3) 9 neighbors. 

		'''

	## I also think that I should be storing more information on the master object and fetching things from there
	## rather than supplying them on creation. Because I'm starting to see a lot of functions that need the 
	## information that is being supplied during this time. 
	## perhaps the mosaic can have default values that can be changed, but they can be overwritten by the create
	## method, but then should the ones used for the create method update the values in master? or should they
	## be treated as only overrides?


## END MOSAIC CLASS




## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
# ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##


## This class is supposed to handle creating and grooming piece lists
## To make things more user friendly, it has a default functionality 
## That allows users to simply specify a directory with image files

## At some point I want the piece list to be determined more elegantly
## likely from the response of a database query, but we'll get there
## when we get there. 

## implement groups so that neighbors can act on groups? 

## right now the only thing is save and qty, besides piece list, qty is calculated, save is fine,
## so resetting piece list is currently ok, I guess, although I'm not sure why you would want to do that. 


## Making the exec decision right now
## pieces should always be exif-data-less
## always be saved as .png if they get saved
## if they need to be rotated, they should be rotated


@wsc.timer
class PieceList:

	def __init__(self,arg=None,max_instances = 5):
		
		self._default_save_size = PIECE_DEFAULT_SAVE_SIZE
		self._accepted_filetypes = PIECE_ACCEPTED_FILETYPES

		self._max_instances = max_instances
		self._max_instances0 = max_instances

		self._pieces = self.__process_pieces_arg(arg)

		


	def __process_pieces_arg(self,arg):
		if arg == None:
			pieces = []
		elif os.path.isdir(arg):
			self.directory = arg
			pieces = self.__create_piece_list_from_directory(arg)
		else:
			print ("WARNING: The argument supplied to PieceList was not an existing directory, assuming a piece_list was given.")
			pieces = arg

		return pieces


	def __create_piece_list_from_directory(self, directory):

		#items = os.listdir(directory)
		items = []
		for root, dirs, files in os.walk(directory):
			for file in files:
				#if os.path.splitext(file)[-1] in ['.png',',jpg']:
					items.append(os.path.join(root,file))		


		pieces = []

		for item in items:	
			extension = os.path.splitext(item)[-1]
			if extension in self._accepted_filetypes:
		
				piece_pillow_image = Image.open( os.path.join(directory,item) )
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

				# I hard coded some stuff dealing with 3 layer images, sorry. 
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




	@wsc.timer
	def save(self, directory, file_ext = '.png'):
		
		os.makedirs(directory) if not os.path.exists(directory) else None
		
		for piece in self.pieces:
			#filename = piece.original_image.filename.split('/')[-1]
			#fileext  = '.png' #os.path.splitext(filename)[-1]
			#filename = filename[0:-1*len(fileext)]+fileext
			
			filename = os.path.splitext(os.path.split(piece.original_image.filename)[-1])[0]+file_ext
			filepath = os.path.join(directory,filename)

			##savepath = os.path.splitext(piece.original_image.filename)[0]+'-tn'+os.path.splitext(piece.original_image.filename)[1]
			#if hasattr(piece, 'exif'):
			#	piece.img.save(filepath, quality = 99, exif = piece.exif)
			#else:
			
			piece.img.save(filepath, quality = 99)




## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
# ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
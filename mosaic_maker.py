#! python3


## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
# ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

from PIL import Image
import numpy as np
import os
from datetime import datetime
from random import random
from math import floor

from yattag import Doc
from yattag import indent

import wantsomechocolate as wsc


## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
# ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

## Should come from a configuration at some point. 
PIECE_DEFAULT_SAVE_SIZE = (128,128)
PIECE_ACCEPTED_FILETYPES = ['.png','.jpg']


## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
# ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

## This file defines the following classes all related to creating photo mosaics. 
## Mosaic Image
## Mosaic
## CompareImages
## PieceList

## MosaicImage
## A wrapper for a pillow image object

## Mosaic
## Holds information about the sections

## CompareImages
## Just a holder for the comparison functions used to compare sections and pieces

## PieceList
## Holds the pieces, has some basic functionality for getting a piece list from a directory




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
		self.rgb_data 		=	np.asarray(self._img)
		self.rgb_data_shape = 	self.rgb_data.shape
		self.mode			=	self._img.mode
		self.error 			=	None	
		self.width, self.height = self._img.size
		self.size 			= 	self._img.size		


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
		if self._img.size == PIECE_DEFAULT_SAVE_SIZE:
			pass
		else:	
			self._img = self._img.resize(size)
			self.__update()


	## my preferred method to create thumbnails
	def to_thumbnail(self,size = PIECE_DEFAULT_SAVE_SIZE):
		self.img_crop_center()
		self.resize(size)









## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
# ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##


## COMPARISON FUNCTIONS
## All comparison functions should take two objects and an optional dictionary of options
## These two objects can be expected to have three attributes
##		img      - the PIL image object
## 		rgb_data - a numpy array with color data
##		error    - the default is None
##
## obj1 is a section of the target image
## obj2 is an image from the set of images used to create the mosaic
##
## The comparison function is expected to compare obj1 and obj2 and 
## update the error attribute of obj2 (that's TWO) with a single numerical value indicative of similarity
## 
## For a given target image section, once all "obj2" have been compared, they are sorted on error
## and a decent match is selected from the list 
## 
## NOTE:
## Operations you perform on obj1 and obj2 can be saved between sections of the target image
## by just adding reusable results as attributes to the objects and checking for the existence 
## of the attribute before calculating, this is apparently related to the idea of memo-ization
## BUT beware that if you add something to objects in piece list and the create method
## of the Mosaic class is called again your reusable results will still be there
## So it would also be useful for your function to look at the 'first' parameter


## i ran into a problem where in order to keep the freedom to name attributes with reusable 
## image data calculations, the error calc function needs to know that the final output thing is called,
## do I just standardize the name of that, or do I include the calculation of the error AND it's 
## setting onto obj2 in with the comparison function?, then the reduce function needs to be given 
## the error calc function to use.
class ImageComparison:

	def rgb_avg_comparison( obj1 							, 
							obj2 							, 
							f 				= 2 			, 
							rgb_weighting 	= (1,1,1)		, 
							first 			= True  		,
							reset_obj1		= True 			,
							reset_obj2 		= True 			,
							opts 			= dict() 		,	):


		obj1_data, obj2_data = ImageComparison.ReduceFuncs.average( 
							obj1 							, 
							obj2 							, 
							f 				= f 			, 
							rgb_weighting 	= rgb_weighting	, 
							first 			= first 		,
							reset_obj1		= reset_obj1	,
							reset_obj2 		= reset_obj2	,
							opts 			= opts 			,	)

		error = ImageComparison.ErrorFuncs.sum_abs_error(
							obj1_data 						, 
							obj2_data 						, 
							rgb_weighting 					,	)

		obj2.error = error

		return error


	class ReduceFuncs:
		def __init__(self):
			self.default = self.average


		def average( 	obj1 							, 
						obj2 							, 
						f 				= 2 			, 
						rgb_weighting 	= (1,1,1)		, 
						first 			= True  		,
						reset_obj1		= True 			,
						reset_obj2 		= True 			,
						opts 			= dict() 		,	):

			if reset_obj1:
				if hasattr(obj1,'rgb_avg'):
					delattr(obj1, 'rgb_avg')
			if reset_obj2:
				if hasattr(obj2,'rgb_avg'):
					delattr(obj2, 'rgb_avg')

			## reset some stuff
			obj2.error = None
			error = 0
			
			## put rgb weighting into numpy array to make it easy to work with if you need it. 
			rgb_error_weight_array = np.array(rgb_weighting)

			## This part of the comparison functions will be the same for many of them, how to factor it?
			if not hasattr(obj1,"rgb_avg"):
				obj1.rgb_avg = []
				for i in range(f):
					for j in range(f):
						obj1.rgb_avg.append( np.mean( obj1.rgb_data[ int(obj1.height/f)*i : int(obj1.height/f)*(i+1) , int(obj1.width/f)*j  : int(obj1.width/f)*(j+1) , : ], axis=(0,1) ) )

			if not hasattr(obj2,"rgb_avg"):
				obj2.rgb_avg = []
				for i in range(f):
					for j in range(f):
						obj2.rgb_avg.append( np.mean( obj2.rgb_data[ int(obj2.height/f)*i : int(obj2.height/f)*(i+1) , int(obj2.width/f)*j  : int(obj2.width/f)*(j+1) , : ], axis=(0,1) ) )

			return obj1.rgb_avg, obj2.rgb_avg

		def dominant():
			pass

	class ErrorFuncs:
		
		def __init__(self):
			self.default = self.rmse
			#self.rgb_error_weight_array = np.array(1,1,1)
		

		def rmse(list_of_array_1,list_of_array_2,rgb_error_weight_array):
			error=0
			for i in range(len( list_of_array_1 )):
				error += np.sqrt( np.mean( np.square( ( list_of_array_1[i] - list_of_array_2[i] ) * rgb_error_weight_array ) ) )
			return error


		def luv_low_cost_approx(list_of_array_1,list_of_array_2,rgb_error_weight_array):
			error=0
			r,g,b = 0,1,2
			for i in range(len( list_of_array_1 )):

				weighted_1=list_of_array_1[i]*rgb_error_weight_array
				weighted_2=list_of_array_2[i]*rgb_error_weight_array

				r_mean = (weighted_1[r]+weighted_2[r])/2
				r_diff = weighted_1[r]-weighted_2[r]
				g_diff = weighted_1[g]-weighted_2[g]
				b_diff = weighted_1[b]-weighted_2[b]

				error += ( (2+(r_mean/256))*r_diff**2 + 4*g_diff**2 + (2+((255-r_mean)/256))*b_diff**2 )**0.5
			return error


		def sum_abs_error(list_of_array_1,list_of_array_2,rgb_error_weight_array):
			
			error=0
			for i in range(len( list_of_array_1 )):
				error += sum( np.absolute(list_of_array_1[i] - list_of_array_2[i]) * rgb_error_weight_array )
			return error













	## Maybe make some functions here that take two lists of distilled rgb data and return the total error value?
	## then call these functions from the compare functions?
	## Do I also want to have one giant compare function that also calls the avg vs dom thing?
	## then with just parameters I can do dom luv, avg rmse, etc, etc?
	## sounds good to me. 


	## Comparison functions that dont loop through subsections,
	## I thought maybe numpy did some really efficient stuff for subtracting image data that
	## I could take advantage of to avoid looping through subsections, but it appears that 
	## it's not going to work out really. 
	## Because this function takes foooooreeeeeeeever, even with just a 10x10 grid. 
	## I might try running it for a whole day or something though to see how the results come out. 
	def subtract_image_data( 	obj1 							, 
								obj2 							, 
								f 				= 1 			, 
								rgb_weighting 	= (1,1,1)		, 
								first 			= True  		,
								reset_obj1		= True 			,
								reset_obj2 		= True 			,
								opts 			= dict() 		,	):

		if reset_obj1:
			if hasattr(obj1,'piece_sized_section_rgb_data'):
				delattr(obj1, 'piece_sized_section_rgb_data')

		obj2.error = None
		error = 0

		if not hasattr(obj1, 'piece_sized_section_rgb_data'):
			if obj1.img.size != obj2.img.size:
				obj1.piece_sized_section_rgb_data = np.asarray(obj1.img.resize(obj2.img.size))
			else:
				obj1.piece_sized_section_rgb_data = obj.rgb_data

		error = np.absolute(obj1.piece_sized_section_rgb_data - obj2.rgb_data).sum()
		obj2.error = error
		return error



	## this should be obsolete soon
	def luv_comparison( 	obj1 							, 
							obj2 							, 
							f 				= 2 			, 
							rgb_weighting 	= (1,1,1)		, 
							first 			= True 			,
							reset_obj1		= True 			,
							reset_obj2 		= True 			,							 
							opts 			= dict() 		,	):
		
		## Using the formula found here:
		## https://www.compuphase.com/cmetric.htm

		if reset_obj1:
			if hasattr(obj1,'rgb_avg'):
				delattr(obj1, 'rgb_avg')
		if reset_obj2:
			if hasattr(obj2,'rgb_avg'):
				delattr(obj2, 'rgb_avg')

		## reset the obj2 error just in case anything crazy happens
		obj2.error = None
		error = 0

		r,g,b = 0,1,2

		if not hasattr(obj1,"rgb_avg"):
			obj1.rgb_avg = []
			for i in range(f):
				for j in range(f):
					obj1.rgb_avg.append( np.mean( obj1.rgb_data[ int(obj1.height/f)*i : int(obj1.height/f)*(i+1) , int(obj1.width/f)*j  : int(obj1.width/f)*(j+1) , : ], axis=(0,1) ) )

		if not hasattr(obj2,"rgb_avg"):
			obj2.rgb_avg = []
			for i in range(f):
				for j in range(f):
					obj2.rgb_avg.append( np.mean( obj2.rgb_data[ int(obj2.height/f)*i : int(obj2.height/f)*(i+1) , int(obj2.width/f)*j  : int(obj2.width/f)*(j+1) , : ], axis=(0,1) ) )


		## Should I check here to make sure the lists are the same length?
		for i in range(len(obj1.rgb_avg)):
		
			r_mean = (obj1.rgb_avg[i][r]+obj2.rgb_avg[i][r])/2
			r_diff = obj1.rgb_avg[i][r]-obj2.rgb_avg[i][r]
			g_diff = obj1.rgb_avg[i][g]-obj2.rgb_avg[i][g]
			b_diff = obj1.rgb_avg[i][b]-obj2.rgb_avg[i][b]

			error += ( (2+(r_mean/256))*r_diff**2 + 4*g_diff**2 + (2+((255-r_mean)/256))*b_diff**2 )**0.5


		obj2.error = error

		return error



## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
# ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

@wsc.timer
class Mosaic:
	'''Size is a tuple of width X height. Individual sections are accessed with [row][col]. 
	First argument can be a string, PIL Image object, or MosacImage obect.'''
	def __init__( 	self 							, 
					image 							, 
					granularity 		= 1/16 		, 
		
					comparison_function = ImageComparison.rgb_avg_comparison,
					f  					= 2 		, 
					rgb_weighting 		=(1,1,1) 	, 
					random_max 			= 0 		, 
					neighborhood_size 	= 1 		, 
		
					opts 				= dict()	,	):

		## Stuff with setters and getters
		self._granularity	 	= granularity
		self.target 			= image

		## Other variables defined here
		self.comparison_function = comparison_function 
		
		self.f 					= f 				
		self.rgb_weighting		= rgb_weighting		 
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


	def __update(self):
		## These things need to update - these should probably be single underscore things?
		self._target.min_dim = min(self._target.width, self._target.height)
		self.section_width 	= self.section_height = int(self._granularity * self._target.min_dim)
		self.w_sections 	= int( self._target.width  / self.section_width  )
		self.h_sections 	= int( self._target.height / self.section_height )

		## Set up an empty grid of the size you'll need based on the inputs. 
		self.grid = [ [None for i in range(self.w_sections)] for j in range(self.h_sections) ]
		## Loop through all the sections and create MosaicImage objects out of them all and put them in the appropriate
		## place in the grid - these are referred to as sections
		for h_section in range(self.h_sections):
			for w_section in range(self.w_sections):
				section = self._target.img.crop((	self.section_width	*	 w_section 		, 		## left
													self.section_height *	 h_section 		, 		## top
													self.section_width	*	(w_section+1)	,		## right
													self.section_height	*	(h_section+1) 	,	))	## bottom
				
				## the grid is indexed using row,col
				self.grid[h_section][w_section] = MosaicImage(section)		


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
	## THE MAIN METHODS OF THIS CLASS
	## #########################################################################################

	'''
	I want to be able to have people write their own comparison functions
	I have found so far that comparison functions can be separated into two parts
	Functions that produce distilled information about images
	Functions that comcpare that distilled information
	But what if someone just wants to create a function takes two objects and slaps an error on obj2?
	I want to allow that as well. 
	'''

	## create the mosaic! - Stil working on what should get it's own arg, what should go in opts dict. etc.
	@wsc.timer
	def create( 	self 			, 
					piece_list		, 					
					opts= dict()	, 	):

		''' Create a mosaic - you can use custom comparison functions! '''

		## If a comparison function is not given, use the default one. 
		#comparison_function = ImageComparison.default if comparison_function is None else comparison_function

		## WHERE THE MAGIC HAPPENS
		## Compare each section to each piece
		## This for loop is very common, how do I refactor it? for blah for blah do something, with arguments. 
		for h_section in range(self.h_sections):
			for w_section in range(self.w_sections):
				for i in range(len(piece_list.pieces)):
					
					## This is getting broken up into two functions now, one to reduce the color data
					## one to compare the result of that function. 
					## the reason is because I want to have different functions for reducing
					## e.g. average rgb, dominant rgb, or others,
					## and different functions for comparing the result
					## e.g. rmse, luv, sum_abs_diff
					## the result will still be the same, all the items in piece_list will wind up with
					## an error attribute that is a single numerical value.

					e = self.comparison_function( 	self.grid[h_section][w_section]					,
													piece_list.pieces[i] 							, 
													
													f 					= self.f 					, 
													rgb_weighting 		= self.rgb_weighting		,

													first 				= h_section+w_section+i==0	, #very first iteration
													reset_obj1			= i==0 						, #first iteration of a new section
													reset_obj2 			= h_section+w_section==0	, #all iterations of the first section
													
													opts 				= opts 						,	)
					

				## Right now piece_list is the same between iterations of this loop and the error is getting
				## reset each time. I feel like trying to save all the error results would be too much information. 
				self.choose_match( (h_section,w_section), piece_list.pieces, self.random_max, self.neighborhood_size, opts )



	## Someday I want to save the state of the pieces list for each section to have a quick ref of good alt matches
	## I would use deep copy or something and depending on resources save the file path/id or the image data.  
	def choose_match(self, coordinates, pieces, random_max, neighborhood_size, opts = dict() ):
		'''Choose the closest match that doesn't violate the neighbor constraint'''
		
		## Sort in the beginning because I think it makes later things faster. 
		#pieces.sort(key=lambda x: (x.error is None, x.error))

		neighbors = self.get_neighbors(coordinates, neighborhood_size) if neighborhood_size != 0 else []

		for neighbor in neighbors:
					
			## does neighbor have a mosaic object chosen for itself yet?
			if hasattr(neighbor,'piece'):
				neighbor_mosaic_image = neighbor.piece

				## Find where the neighbor's piece is in the pieces list. I didn't write this code myself. 
				piece = next((x for x in pieces if x.original_image.filename == neighbor_mosaic_image.original_image.filename), None)

				## Update it's error to be nothing (and properly handle None on sort)
				piece.error = None

		## Sort the list again, this time there will be some None - https://stackoverflow.com/a/18411610/1937423
		pieces.sort(key=lambda x: (x.error is None, x.error))		
		
		self.grid[coordinates[0]][coordinates[1]].piece = pieces[ int(random()*random_max) ]




	## #########################################################################################
	## Other helper functions
	## #########################################################################################

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
	@wsc.timer
	def output_html(self):

		start = datetime.utcnow()
		timestamp = int(start.timestamp())

		target_image_filepath = self._target.original_image.filename
		base_save_directory = os.path.splitext(target_image_filepath)[0]
		html_save_directory = base_save_directory+'/html/html-'+str(timestamp)+'/'
		pieces_save_directory = html_save_directory+'pieces/'
		
		img_filename = base_save_directory.split('/')[-1]

		os.makedirs(html_save_directory) if not os.path.exists(html_save_directory) else None
		os.makedirs(pieces_save_directory) if not os.path.exists(pieces_save_directory) else None

		html_output_filepath = html_save_directory+img_filename+'-'+str(int(datetime.utcnow().timestamp()))+'.html'		
		css_output_filepath = html_save_directory+'mosaicStyle.css'

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
									doc.stag('img', src='pieces/'+self.grid[i][j].piece.original_image.filename.split('/')[-1])
					
		
		with open(html_output_filepath, 'w') as fh:
			output = indent(doc.getvalue())
			fh.write(output)
			image_container_width = self.w_sections * 40

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
	z-index:10
	width:{image_container_width}px;}}
.col img {{padding:0px;
	margin:0px;
	opacity:0.68;
	height:40px;
	width:40px;}}
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
	height:40px;}}'''

		css_text = css_text.format(image_container_width = image_container_width)

		with open(css_output_filepath, 'w') as fh:
			fh.write(css_text)

		## Sve the necessary items. Wait I thought the pieces class had a method for this?
		for item in self.unique_pieces:
			im = Image.open(item.piece.original_image.filename)
			im_name = item.piece.original_image.filename.split('/')[-1]
			im.save(pieces_save_directory+im_name)

		## Save the target in there with everyone!
		self._target.img.save(html_save_directory+'target.png')

		return html_output_filepath


	## These mosaic output images can get massive, so I'm not making this a property
	## Consider adding the ability to add a transparent overlay. Easier in html, but maybe good here, too?
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
		mosaic_save_directory = os.path.join( os.path.splitext(target_image_filepath)[0],'mosaics/' )
		os.makedirs(mosaic_save_directory) if not os.path.exists(mosaic_save_directory) else None		
		# mosaic_save_filepath = mosaic_save_directory+'P'+str(round(100*global_opts_dict['granularity']))+'F'+str(global_opts_dict['f'])+'R'+str(global_opts_dict['random_max'])+'-'+str(int(datetime.utcnow().timestamp()))+'.png'
		
		if 'filename' in opts.keys():
			if os.path.isabs(opts['filename']):
				mosaic_save_filepath = os.path.splitext(opts['filename'])[0]+'-'+str(int(start.timestamp()))+os.path.splitext(opts['filename'])[1]
			else:	
				mosaic_save_filepath = mosaic_save_directory+os.path.splitext(opts['filename'])[0]+'-'+str(int(start.timestamp()))+os.path.splitext(opts['filename'])[1]
		else:			
			mosaic_save_filepath = mosaic_save_directory+str(int(start.timestamp()))+'.png'

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

## implement groups so that neighbors can act on groups. 

## right now the only thing is save and qty, besides piece list, qty is calculated, save is fine,
## so resetting piece list is currently ok, I guess, although I'm not sure why you would want to do that. 

@wsc.timer
class PieceList:

	def __init__(self,arg):
		
		self._default_save_size = PIECE_DEFAULT_SAVE_SIZE
		self._accepted_filetypes = PIECE_ACCEPTED_FILETYPES

		if os.path.isdir(arg):
			self.directory = arg
			self.pieces = self.__create_piece_list_from_directory(arg)
		else:
			self.pieces = []


	def __create_piece_list_from_directory(self, directory):

		items = os.listdir(directory)
		pieces = []

		for item in items:	
			extension = os.path.splitext(item)[-1]
			if extension in self._accepted_filetypes:
		
				piece_pillow_image = Image.open( directory + item )
				piece_mosaic_image = MosaicImage(piece_pillow_image)

				try:
					piece_mosaic_image.to_thumbnail()

					# I hard coded some stuff dealing with 3 layer images, sorry. 
					if piece_mosaic_image.rgb_data_shape[2] == 3:
						pieces.append(piece_mosaic_image)

				except SyntaxError as err:
					print(err)
					print('There was a problem thumbnailing '+piece_pillow_image.filename)
		
		if len(pieces) == 0:
			print("WARNING: No pieces were found in the given directory.")

		return pieces


	@property
	def qty(self):
		self._qty = len(self.pieces)
		return self._qty
	
	@wsc.timer
	def save(self, directory):
		
		os.makedirs(directory) if not os.path.exists(directory) else None
		
		for piece in self.pieces:
			filename = piece.original_image.filename.split('/')[-1]
			fileext  = os.path.splitext(filename)[-1]
			filename = filename[0:-1*len(fileext)]+fileext
			filepath = os.path.join(directory,filename)

			##savepath = os.path.splitext(piece.original_image.filename)[0]+'-tn'+os.path.splitext(piece.original_image.filename)[1]
			if hasattr(piece, 'exif'):
				piece.img.save(filepath, quality = 99, exif = piece.exif)
			else:
				piece.img.save(filepath, quality = 99)




## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
# ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
#! python3

from PIL import Image
import numpy as np
import os
from datetime import datetime
from random import random
from math import floor

from yattag import Doc
from yattag import indent

## Should come from a configuration at some point. 
PIECE_DEFAULT_SAVE_SIZE = (512,512)
PIECE_ACCEPTED_FILETYPES = ['.png','.jpg']

## ###########################################################################################
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


class MosaicImage:

	def __init__(self, img):

		if type(img) == type('string'):
			print("MosacImage object initialized with a string")
			img = Image.open(img)

		self.img 			= img
		self.original_image = img
		if 'exif' in self.original_image.info:
			self.exif 		= self.original_image.info['exif']
		
		if self.original_image.mode == 'RGBA':
			self.__rgba_to_rgb()

		self.__update()



	def __update(self):
		self.rgb_data 		=	np.asarray(self.img)
		self.rgb_data_shape = 	self.rgb_data.shape
		self.mode			=	self.img.mode
		self.error 			=	None	
		self.width, self.height = self.img.size
		self.size 			= 	self.img.size		



	def __rgba_to_rgb(self):
		new_img = Image.new("RGB", self.img.size, (255,255,255))
		new_img.paste(self.img, mask=self.img.split()[3])
		self.img = new_img
		self.__update()		



	def img_crop_center(self):
		ow, oh = self.img.size
		if ow == oh:
			pass
		else:
			dw = dh = min(ow, oh)
			left  = floor( (ow/2) - (dw/2) )
			upper = floor( (oh/2) - (dh/2) )
			right = floor( (ow/2) + (dw/2) )
			lower = floor( (oh/2) + (dh/2) )

			self.img = self.img.crop((left,upper,right,lower))
			self.__update()



	def resize(self,size = PIECE_DEFAULT_SAVE_SIZE):
		if self.img.size == PIECE_DEFAULT_SAVE_SIZE:
			pass
		else:	
			self.img = self.img.resize(size)
			self.__update()



	def to_thumbnail(self,size = PIECE_DEFAULT_SAVE_SIZE):
		self.img_crop_center()
		self.resize(size)




class Mosaic:
	'''Size is a tuple of width X height. Individual sections are accessed with [row][col]. 
	First argument can be a string, PIL image object, or MosacImage obect.'''
	def __init__(self, image, granularity = 1/16, opts=dict()):

		if type(image) == type('string'):
			print("Mosaic object initialized with a string")
			image = MosaicImage( Image.open(image) )
		elif type(image).__name__[-9:] == 'ImageFile':
			print("Mosaic object initialized with an image object")
			image = MosaicImage( image )


		self.target 		= image
		self.target.min_dim 	= min(self.target.width, self.target.height)
		
		## Grid Attributes
		self.granularity 	= granularity

		## self.sectionDim 	= int(self.granularity * self.target.min_dim)
		self.section_width 	= self.section_height = int(self.granularity * self.target.min_dim)

		self.w_sections 	= int( self.target.width  / self.section_width  )
		self.h_sections 	= int( self.target.height / self.section_height )

		## Set up an empty grid of the size you'll need based on the inputs. 
		self.grid = [ [None for i in range(self.w_sections)] for j in range(self.h_sections) ]


		## Loop through all the sections and create MosaicImage objects out of them all and put them in the appropriate
		## place in the grid - these are referred to as sections
		for h_section in range(self.h_sections):
			for w_section in range(self.w_sections):
				section = self.target.img.crop((	self.section_width	*	 w_section 		, 		## left
													self.section_height *	 h_section 		, 		## top
													self.section_width	*	(w_section+1)	,		## right
													self.section_height	*	(h_section+1) 	,	))	## bottom
				
				## the grid is indexed using row,col
				self.grid[h_section][w_section] = MosaicImage(section)


	def save_sections(self):
		
		timestamp = str(int(datetime.utcnow().timestamp()))
		save_dir = os.path.splitext(self.target.original_image.filename)[0]+'/sections/sections-'+timestamp+'/'
		os.makedirs(save_dir)
		for i in range(len(self.grid)):
			for j in range(len(self.grid[i])):
				section = self.grid[i][j].img
				section = section.resize( PIECE_DEFAULT_SAVE_SIZE ) ## This is currently the default - 
				section.save(save_dir+str(i)+"-"+str(j)+".png")
		print(save_dir)
		return save_dir


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
	





	## For creating an html file and subdirectory with css file and necessary images. 
	## I think this function should also make a database entry so you can recreate it later!
	## thie method also needs the ability to save all the images it needs in the images directory
	## There is also no css file currently created with this function. 
	def output_html(self):

		start = datetime.utcnow()
		timestamp = int(start.timestamp())

		target_image_filepath = self.target.original_image.filename
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
				with tag('div', klass='imageContainer'):
					
					for i in range(self.h_sections):

						with tag('div', klass='row', id='row-'+str(i)):
					
							for j in range(self.w_sections):

								with tag('div', klass='col', id='cell-'+str(i)+'-'+str(j)):
									doc.stag('img', src='pieces/'+self.grid[i][j].piece.original_image.filename.split('/')[-1])
					
		
		with open(html_output_filepath, 'w') as fh:
			output = indent(doc.getvalue())
			fh.write(output)


		css_text = '''
						* {box-sizing:border-box;}
					    body {background:black;
					        	color:white; 		}
					    .imageContainer {
					    		overflow:hidden;
					        	border:2p solid black;
					        	margin:0 auto;
					        	padding:15px; 		}
					    img {padding:0px;
					        	margin:0px;
								height:20px;
								width:20px;			}
						.row {width:100%;
								padding:0px;
								margin:0px;			}						
						/* Clear floats after image containers */
						.row::after {clear: both;
								content: "";
								display:block;		}
						.col {float: left;
								padding: 0px;
								margin:0px;
								height:20px; 		}	
					'''

		with open(css_output_filepath, 'w') as fh:
			fh.write(css_text)


		for item in self.unique_pieces:
			im = Image.open(item.piece.original_image.filename)
			im_name = item.piece.original_image.filename.split('/')[-1]
			im.save(pieces_save_directory+im_name)

		return html_output_filepath



	def output_to_image(self,opts=dict()):

		start = datetime.utcnow()
		target_image_filepath = self.target.original_image.filename

		## This assumes all thumbnails are the same dimensions - ok for now, but in the future I want to avoid this limitation
		thumbnail_size = self.grid[0][0].piece.img.size

		mosaic_width  = self.w_sections * thumbnail_size[0]
		mosaic_height = self.h_sections * thumbnail_size[1]

		im = Image.new('RGB', (mosaic_width,mosaic_height))

		for i in range(self.h_sections):
			for j in range(self.w_sections):
				im.paste(self.grid[i][j].piece.img,(j*thumbnail_size[0],i*thumbnail_size[1]))

		mosaic_save_directory = os.path.splitext(target_image_filepath)[0]+'/mosaics/'
		
		os.makedirs(mosaic_save_directory) if not os.path.exists(mosaic_save_directory) else None
		
		# mosaic_save_filepath = mosaic_save_directory+'P'+str(round(100*global_opts_dict['granularity']))+'F'+str(global_opts_dict['f'])+'R'+str(global_opts_dict['random_max'])+'-'+str(int(datetime.utcnow().timestamp()))+'.png'
		mosaic_save_filepath = mosaic_save_directory+str(int(start.timestamp()))+'.png'

		im.save(mosaic_save_filepath, quality=95)

		print ("That took "+ str((datetime.utcnow() - start).total_seconds()) +" seconds")

		return mosaic_save_filepath



	## Someday I want to save the state of the pieces list for each section to have a quick ref of good alt matches
	## I would use deep copy or something and depending on resources save the file path/id or the image data.  
	def choose_match(self, coordinates, pieces, random_max, neighborhood_size, opts = dict() ):
		'''Choose the closest match that doesn't violate the neighbor constraint'''
		
		## Sort in the beginning because I think it makes later things faster. 
		pieces.sort(key=lambda x: x.error)

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




	## create the mosaic! - Stil working on what should get it's own arg, what should go in opts dict. etc.
	def create( 	self 							, 
					piece_list						, 

					# keyword arguments and defaults
					comparison_function = None		,
					f 					= 2 		,
					rgb_weighting		= (1,1,1)	,
					random_max			= 0			,
					neighborhood_size	= 1 		,
					opts 				= dict()	, 	):

		''' Create a mosaic - you can use custom comparison functions! '''

		## How long does it take!
		start = datetime.utcnow()

		## If a default comparison function is not given, use the default one. Is there is an easier way to do this?
		comparison_function = self.compare_default if comparison_function is None else comparison_function

		## Because I'm currently using a single piece_list and just having it chill in memory
		## I need to flush the pre-calculated stuff out of it before starting a new mosaic
		## but the piece_list isn't an attribute of the mosaic object, so this feels dirty. 
		## ACTUALLY this should be taken care of with the comparion function? but how would that work?
		## maybe I need to tell the compare function when a new mosaic is being created? 
		## Because if I'm giving people the ability to write custom functions, really they should be 
		## able to save whatever stuff they want to the pieces. 
		## Maybe I could use some sort of decorator function? I mean I could go through all the attributes
		## and remove ones that aren't in a list?
		for piece in piece_list.pieces:
			if hasattr(piece, 'rgb_avg'):
				delattr(piece, 'rgb_avg')

			if hasattr(piece, 'rgb_dom'):
				delattr(piece, 'rgb_dom')

		## WHERE THE MAGIC HAPPENS
		## Compare each section to each piece
		for h_section in range(self.h_sections):
			for w_section in range(self.w_sections):
		
				for i in range(len(piece_list.pieces)):
					e = comparison_function( 	self.grid[h_section][w_section]			,
												piece_list.pieces[i] 					, 
												f 					= f 				, 
												rgb_weighting 		= rgb_weighting		, 
												first 				= i==0				,
												opts 				= opts 				,	)
					

				## Right now piece_list is the same between iterations of this loop and the error is getting
				## reset each time. I feel like trying to save all the error results would be too much information. 
				self.choose_match( (h_section,w_section), piece_list.pieces, random_max, neighborhood_size, opts )

		print ("That took "+ str((datetime.utcnow() - start).total_seconds()) +" seconds")


	def compare_default( 	self 						,
							obj1 						,
							obj2 						,
							f 				= 2 		,
							rgb_weighting 	= (1,1,1)	,
							first 			= True  	,
							opts 			= dict()	,	):


		return ImageComparison.rgb_avg_comparison(	obj1 							,
													obj2 							, 
													f 				= f 			,
													rgb_weighting 	= rgb_weighting ,
													first 			= first 		,
													opts 			= opts 			,	)
	


	## I'm going to use filename for now, probably will regret that, but I don't care at the moment?
	## maybe try using image data instead? both have downsides I think. 
	## Anyway, the main thing it needs is a mosaic image object to be passed to it
	## This object, for now, needs a file name.
	## then it goes through all the sections of the mosaic and if a piece has the same filename as the one
	## you want to remove, than BAM, find a new match for that section.
	## That means this function also needs information on how to find the new matches! 
	## i.d. compare function, random max, weather or not to enforce neighbor constraints?
	## true I could make that a variable!
	def remove_instance():
		''' remove all instances of a particular piece from a mosaic '''
		pass

## END MOSAIC CLASS









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

## was mm_compare
class ImageComparison:

	def __init__(self):
		return None


	def test( 	obj1 							, 
				obj2 							, 
				f 				= 2 			, 
				rgb_weighting 	= (1,1,1)		, 
				first 			= True  		,
				opts 			= dict() 		,	):


		if first:
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

	## This is the simplest form of comparison I could think of
	## The average rgb value of obj1 and ob2 are calculated (thanks numpy for making that so easy)
	## and the error is calculated as the sum of the absolute values of the difference between the
	## r,g, and b values of those two averages. 
	def rgb_avg_comparison( obj1 							, 
							obj2 							, 
							f 				= 2 			, 
							rgb_weighting 	= (1,1,1)		, 
							first 			= True  		,
							opts 			= dict() 		,	):


		if first:
			if hasattr(obj1,'rgb_avg'):
				delattr(obj1, 'rgb_avg')
			if hasattr(obj2,'rgb_avg'):
				delattr(obj2, 'rgb_avg')

		## reset the obj2 error just in case anything crazy happens
		obj2.error = None
		
		error = 0
		rgb_error_weight_array = np.array([rgb_weighting[0],rgb_weighting[1],rgb_weighting[2]])

		## This part of the comparison functions will be the same for many of them, how to factor it. 
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
			error += sum( np.absolute(obj1.rgb_avg[i] - obj2.rgb_avg[i]) * rgb_error_weight_array )
		
		obj2.error = error

		return error




	def luv_comparison( 	obj1 							, 
							obj2 							, 
							f 				= 2 			, 
							rgb_weighting 	= (1,1,1)		, 
							first 			= True 			, 
							opts 			= dict() 		,	):
		
		## Using the formula found here:
		## https://www.compuphase.com/cmetric.htm

		if first:
			if hasattr(obj1,'rgb_avg'):
				delattr(obj1, 'rgb_avg')
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




## This class is supposed to handle creating and groom piece lists
## To make things more user friendly, it has a default functionality 
## That allows users to simply specify a directory with image files

## At some point I want the piece list to be determined more elegantly
## likely from the response of a database query, but we'll get there
## when we get there. 
class PieceList:
	def __init__(self,arg):
		
		start = datetime.utcnow()

		self.__default_save_size = PIECE_DEFAULT_SAVE_SIZE

		self.__accepted_filetypes = PIECE_ACCEPTED_FILETYPES

		if os.path.isdir(arg):
			self.directory = arg
			self.pieces = self.__create_piece_list_from_directory(arg)
		else:
			self.pieces = []

		print ("That took "+ str((datetime.utcnow() - start).total_seconds()) +" seconds")

	def __create_piece_list_from_directory(self, directory):

		items = os.listdir(directory)

		pieces = []

		for item in items:	
			extension = os.path.splitext(item)[-1]
			if extension in self.__accepted_filetypes:
		
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
	

	def save(self, directory):
		start = datetime.utcnow()
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

		print ("That took "+ str((datetime.utcnow() - start).total_seconds()) +" seconds")




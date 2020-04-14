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
PIECE_DEFAULT_SAVE_SIZE = (128,128)
PIECE_ACCEPTED_FILETYPES = ['.png','.jpg']


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
## Just a holder for the comparison functions used to compare sections and pices

## PieceList
## Holds the pieces, has some basic functionality for getting a piece list from a directory


## Object to automatically add a few things to pillow image objects
## I also added a "has" method, but I don't actually use it. 
class MosaicImage:

	def __init__(self, img):

		if type(img) == type('string'):
			print("MosacImage object initialized with a string")
			img = Image.open(img)

		self.img 			= img
		self.original_image = img
		
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



	def resize_to_piece_default_save_size(self):
		if self.img.size == PIECE_DEFAULT_SAVE_SIZE:
			pass
		else:	
			self.img = self.img.resize(PIECE_DEFAULT_SAVE_SIZE)
			self.__update()




## Master object to hold a mosaic - feels like it's turning into a bohemoth
## I don't have a lot of experience with classes yet and it feels like I might be 
## putting too much logic into the this class.

## size is a tuple of w x h
## individual items are accessed with row,col
class Mosaic:

	## I want to see if I could potentially have this class accept
	##		1. a mosaic image object
	##		2. a pillow image object
	##		3. a string/directory to an image
	def __init__(self, imgObj, granularity = 1/16, opts=dict()):


		if type(imgObj) == type('string'):
			print("Mosaic object initialized with a string")
			imgObj = MosaicImage( Image.open(imgObj) )
		elif type(imgObj).__name__[-9:] == 'ImageFile':
			print("Mosaic object initialized with an image object")
			imgObj = MosaicImage( imgObj )


		## targetImgObject Attributes are the height and the width and the min dim
		self.targetImgObject 			= imgObj
		self.targetImgObject.minDim 	= min(self.targetImgObject.width, self.targetImgObject.height)
		
		## Grid Attributes
		self.granularity 				= granularity

		self.sectionDim 				= int(self.granularity * self.targetImgObject.minDim)
		self.sectionWidth 				= self.sectionHeight = self.sectionDim

		self.w_sections 				= int( self.targetImgObject.width  / self.sectionWidth  )
		self.h_sections 				= int( self.targetImgObject.height / self.sectionHeight )

		## Set up an empty grid of the size you'll need based on the inputs. 
		self.grid = [ [None for i in range(self.w_sections)] for j in range(self.h_sections) ]


		## Loop through all the sections and create imgObjects out of them all and put them in the appropriate
		## place in the grid
		for h_section in range(self.h_sections):
			for w_section in range(self.w_sections):
				targetImgSection = self.targetImgObject.img.crop((	self.sectionWidth	*	 w_section 		, 		## left
																	self.sectionHeight 	*	 h_section 		, 		## top
																	self.sectionWidth	*	(w_section+1)	,		## right
																	self.sectionHeight	*	(h_section+1) 	,	))	## bottom
				
				## the grid is indexed using row,col
				self.grid[h_section][w_section] = MosaicImage(targetImgSection)


	def save_sections(self):

		timestamp = str(int(datetime.utcnow().timestamp()))
		saveDir = os.path.splitext(self.targetImgObject.original_image.filename)[0]+'/sections/sections-'+timestamp+'/'
		os.makedirs(saveDir)
		for i in range(len(self.grid)):
			for j in range(len(self.grid[i])):
				section = self.grid[i][j].img
				section = section.resize( PIECE_DEFAULT_SAVE_SIZE ) ## This is currently the default - 
				section.save(saveDir+str(i)+"-"+str(j)+".png")
		print(saveDir)
		return saveDir


	## I think I would rather this property return a unique object list?
	## A unique list of objects based on a particular attribute though. Which I don't know how to do at the moment. 	
	@property
	def uniqueImageList(self):

		imgList=[]
		for i in range(self.h_sections):
			for j in range (self.w_sections):
				imgList.append(self.grid[i][j].currentMosaicImage.original_image.filename)
		self._uniqueImageList = set(imgList)
		return self._uniqueImageList


	@property
	def uniquePiecesObjList(self):

		seen = set()
		unique = []
		for row in self.grid:
			for obj in row:
				if obj.currentMosaicImage.original_image.filename not in seen:
					unique.append(obj)
					seen.add(obj.currentMosaicImage.original_image.filename)

		self._uniquePiecesObjList = unique

		return self._uniquePiecesObjList
	





	## For creating an html file and subdirectory with css file and necessary images. 
	## I think this function should also make a database entry so you can recreate it later!
	## thie method also needs the ability to save all the images it needs in the images directory
	## There is also no css file currently created with this function. 
	def output_html(self):

		start = datetime.utcnow()
		timestamp = int(start.timestamp())

		baseImageFilepath = self.targetImgObject.original_image.filename
		baseSaveDir = os.path.splitext(baseImageFilepath)[0]
		htmlDir = baseSaveDir+'/html/html-'+str(timestamp)+'/'
		imgName = baseSaveDir.split('/')[-1]
		piecesDir = htmlDir+'pieces/'

		os.makedirs(htmlDir) if not os.path.exists(htmlDir) else None
		os.makedirs(piecesDir) if not os.path.exists(piecesDir) else None

		htmlOutputFilePath = htmlDir+imgName+'-'+str(int(datetime.utcnow().timestamp()))+'.html'		
		cssOutputFilePath = htmlDir+'mosaicStyle.css'

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
									doc.stag('img', src='pieces/'+self.grid[i][j].currentMosaicImage.original_image.filename.split('/')[-1])
					
		
		with open(htmlOutputFilePath, 'w') as fh:
			output = indent(doc.getvalue())
			fh.write(output)


		css_text = '''	* {box-sizing:border-box;}

					    body {
					        background:black;
					        color:white;
					    }

					    .imageContainer {
					        overflow:hidden;
					        border:2p solid black;
					        margin:0 auto;
					        padding:15px;
					    }

					    img {
					        padding:0px;
					        margin:0px;
							height:10px;
							width:10px;
						}

						.row{
							width:100%;
							padding:0px;
							margin:0px;
						}
						
						
						/* Clear floats after image containers */
						.row::after {
							clear: both;
							content: "";
							display:block;
						}
						
						.col {
							float: left;
							padding: 0px;
							margin:0px;
							height:10px;
						}											'''

		with open(cssOutputFilePath, 'w') as fh:
			fh.write(css_text)



		for item in self.uniquePiecesObjList:
			im = Image.open(item.currentMosaicImage.original_image.filename)
			im_name = item.currentMosaicImage.original_image.filename.split('/')[-1]
			im.save(piecesDir+im_name)

		return htmlOutputFilePath



	def output_to_image(master,opts=dict()):

		baseImageFilepath = master.targetImgObject.original_image.filename

		## Because I know the thumbnails are 128x128, I'm going to use that for now
		## This means the mosaic image can have different dimensions from the original image
		## thumbnail_size = (128,128) ## This has the side effect of not being able to use smaller source images as well. 

		## This is much better. just ask the first section of the grid what size the chosen image is. 
		## this only assumes that all source images are the same size. Still maybe not a gnt in the future
		## but better than what I got goin on before
		thumbnail_size = master.grid[0][0].currentMosaicImage.img.size

		outputImgWidth  = master.w_sections * thumbnail_size[0]
		outputImgHeight = master.h_sections * thumbnail_size[1]

		im = Image.new('RGB', (outputImgWidth,outputImgHeight))

		for i in range(master.h_sections):
			for j in range(master.w_sections):
				im.paste(master.grid[i][j].currentMosaicImage.img,(j*thumbnail_size[0],i*thumbnail_size[1]))

		outputImgSaveDir = os.path.splitext(baseImageFilepath)[0]+'/mosaics/'
		
		os.makedirs(outputImgSaveDir) if not os.path.exists(outputImgSaveDir) else None
		
		# outputImgSavePath = outputImgSaveDir+'P'+str(round(100*global_opts_dict['granularity']))+'F'+str(global_opts_dict['f'])+'R'+str(global_opts_dict['random_max'])+'-'+str(int(datetime.utcnow().timestamp()))+'.png'
		outputImgSavePath = outputImgSaveDir+str(int(datetime.utcnow().timestamp()))+'.png'

		im.save(outputImgSavePath)

		return outputImgSavePath



	## ok we're finally here! - try to incorporate logic to prevent sections from choosing
	## the same piece as any adjecent sections (including diagonally adjacent)
	def choose_match(self, coordinates, sourceImgObjList, opts = dict() ):
		
		## Get random max from the opts dict if it is given. 
		random_max = opts['random_max'] if 'random_max' in opts.keys() else 1

		## Sort the sourceImgObjList based on the current state of the error metrics
		## Should choose match be the one responsible for getting the error for each piece?
		## Because in order to choose match for a single section, you also need to be able
		## to calculate the error for a single section. What does that look like?
		## That would be just the third loop of the main part of the program
		## The output of that function would feed this one. 
		sourceImgObjList.sort(key=lambda x: x.error)


		## (for now) take the first one (least error) and add it to the master grid as the best match!		
		#self.grid[coordinates[0]][coordinates[1]].currentMosaicImage = sourceImgObjList[ int(random()*global_opts_dict['random_max']) ]	


		## So what is the logic here.
		## make a list of the files from surrounding items
		neighboring_img=[]
		neighbors = (-1,0,1)
		for i_offset in neighbors:
			for j_offset in neighbors:
				if i_offset+j_offset != 0:
					try:
						neighboring_img.append( self.grid[coordinates[0]+i_offset][coordinates[1]+j_offset].currentMosaicImage.original_image.filename )
					except IndexError as err:
						pass #print(err)
					except AttributeError as err:
						pass #print(err)


		#chosenObj = sourceImgObject[0] 
		## use a while loop to check for in-ness of pieces in the neighbors list. 
		i = 0
		while sourceImgObjList[i].original_image.filename in neighboring_img:
			i+=1

		self.grid[coordinates[0]][coordinates[1]].currentMosaicImage = sourceImgObjList[i]


		## This was all my thoughts during the move of this code from inside the main loop to a method of the main class

		## The combination of the below two lines of code should be in a function call so that
		## custom image selection methods can be implemented.
		## But I'm not 100% sure on how I should structure the function because I want to have the ability
		## to check other objects in the grid, but I want to write a generalized selection function based 
		## on the error attributes of a list of objects. 
		## So I guess the comparison function needs to take
		## The master grid, the row and column of the section in question and the sourceImgObjList (sorted or not?)
		## Perhaps each section can be globally set with the compare function to use, but it can be 
		## locally set as well, so that when the final is produced the use can see for particular sections
		## or instances of a particular object, what other algorthms would have produced. Then this function here
		## that I'm trying to write would be something best suited as a method to the class
		## because then you could actually call the method on a single section at a time in order to change a single
		## section's image. 

		#choose_match(master, (h_section,w_section), sourceImgObjectList, opts = dict() )

		# def choose_match(masterGrid,(row,col),sourceImgObjList):
		## Sort the sourceImgObjList based on the error and... 
		#sourceImgObjList.sort(key=lambda x: x.error)
		## (for now) take the first one (least error) and add it to the master grid as the best match!		
		#master.grid[h_section][w_section].currentMosaicImage = sourceImgObjList[ int(random()*global_opts_dict['random_max']) ]		


	## Ok so the grid class can have a default comparison method, but you can override it with 
	## a different one from the CompareImages class or something. 
	def create( 	self 							, 
					piece_list						, 

					# keyword arguments and defaults
					comparison_function = None		,
					f 					= 2 		,
					rgb_weighting		= (1,1,1)	,
					random_max			= 0			,
					opts 				= dict()	, 	):

		## How long does it take!
		start = datetime.utcnow()

		## If a default comparison function is not given, use the default one. 
		comparison_function = self.compare_default if comparison_function is None else comparison_function

		## Because I'm currently using a single piece_list and just having it chill in memory
		## I need to flush the pre-calculated stuff out of it before starting a new mosaic
		## but the piece_list isn't an attribute of the mosaic object, so this feels dirty. 
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
					e = comparison_function( 	self.grid[h_section][w_section]				,
												piece_list.pieces[i] 								, 
												f 					= f 					, 
												rgb_weighting 		= rgb_weighting			, 
												random_max 			= random_max			, 
												opts 				= opts 					,	)
					

				## Right now sourceImgObjList is the same between iterations of this loop and the error is getting
				## reset each time. I feel like trying to save all the error results would be too much information. 
				self.choose_match( (h_section,w_section), piece_list.pieces, opts )

		print ("That took "+ str((datetime.utcnow() - start).total_seconds()) +" seconds")


	def compare_default( 	self 						,
							obj1 						,
							obj2 						,
							f 				= 2 		,
							rgb_weighting 	= (1,1,1)	,
							random_max 		= 0 		,
							opts 			= dict()	,	):


		return ImageComparison.rgb_avg_comparison(	obj1 							,
												obj2 							, 
												f 				= f 			,
												rgb_weighting 	= rgb_weighting ,
												random_max  	= random_max 	, 
												opts 			= opts 			,	)
	

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

## was mm_compare
class ImageComparison:

	def __init__(self):
		return None

	## This is the simplest form of comparison I could think of
	## The average rgb value of obj1 and ob2 are calculated (thanks numpy for making that so easy)
	## and the error is calculated as the sum of the absolute values of the difference between the
	## r,g, and b values of those two averages. 
	def rgb_avg_comparison( obj1 							, 
							obj2 							, 
 
							f 				= 2 			, 
							rgb_weighting 	= (1,1,1)		, 
							random_max 		= 1 			, 

							opts 			= dict() 		,	):

		## reset the obj2 error just in case anything crazy happens
		obj2.error = None
		error = 0
		#f = opts['f']

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
							random_max 		= 1 			, 

							opts 			= dict() 		,	):
		
		## Use the formula found here:
		## https://www.compuphase.com/cmetric.htm

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
			#error += sum( np.absolute(obj1.rgb_avg[i] - obj2.rgb_avg[i]) * rgb_error_weight_array )
		
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
		
		self.accepted_filetypes = PIECE_ACCEPTED_FILETYPES

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
			if extension in self.accepted_filetypes:
		
				piece_pillow_image = Image.open( directory + item )
				piece_mosaic_image = MosaicImage(piece_pillow_image)
				piece_mosaic_image.img_crop_center()
				piece_mosaic_image.resize_to_piece_default_save_size()

				# I hard coded some stuff dealing with 3 layer images, sorry. 
				if piece_mosaic_image.rgb_data_shape[2] == 3:
					pieces.append(piece_mosaic_image)
		
		if len(pieces) == 0:
			print("WARNING: No pieces were found in the given directory.")

		return pieces

	@property
	def qty(self):
		self._qty = len(self.pieces)
		return self._qty
	

	def save(self, directory):
		os.makedirs(directory) if not os.path.exists(directory) else None
		
		for piece in self.pieces:
			filename = piece.original_image.filename.split('/')[-1]
			filepath = os.path.join(directory,filename)
			piece.img.save(filepath) 






#! python3

from PIL import Image
import os
import mosaic_maker as mm


## I need to figure out why I can't reuse a master to make a new mosaic
## it complains about NoneType not having and error attribute in the choose_match function. 


if True:
	## Some Directories
	# 'C:/Users/wants/Projects/Code/MosaicMakerImages/zztemepdb/'
	# 'C:/Users/wants/Projects/Code/MosaicMakerImages/zzarchivedsearches/People/'
	# 'C:/Users/wants/Projects/Code/MosaicMakerImages/Anqi/Anqi-01/sections/'
	# 'C:/Users/wants/Projects/Code/MosaicMakerImages/JamesGrandfatheredIn/JamesSquare/sections/'

	## Create a piece_list (The result should be a list of MosaicImage objects that have
	## been cropped as squares and resized to the default piece size. )
	print('Making the peice list')
	# piece_list = mm.PieceList( 'C:/Users/wants/Projects/Code/MosaicMakerImages/zztemepdb/' )
	# piece_list = mm.PieceList( 'C:/Users/wants/Projects/Code/MosaicMakerImages/JamesMosaicClimbingProject/James/pieces - best/' )
	# piece_list = mm.PieceList( 'C:/Users/wants/Projects/Code/MosaicMakerImages/JamesMosaicClimbingProject/2101-2400-pieces/' )
	piece_list = mm.PieceList( 'C:/Users/wants/Projects/Code/MosaicMakerImages/Woah/NoClimbing/pieces/' )

	## An image to turn into a mosaic
	#base_image_filepath = 'C:/Users/wants/Projects/Code/MosaicMakerImages/James/JamesAndCrystal/JamesAndCrystal.jpg'
	#base_image_filepath = 'C:/Users/wants/Projects/Code/MosaicMakerImages/James/Hot Air Balloon/Hot Air Balloon.jpg'
	#base_image_filepath = 'C:/Users/wants/Projects/Code/MosaicMakerImages/JamesMosaicClimbingProject/James.png'
	base_image_filepath = 'C:/Users/wants/Projects/Code/MosaicMakerImages/Woah/Smirk/SmirkCloseUp.jpg'

	## A MosaicImage object is just a wrapper for a pillow image object.
	## At some point I want the MosaicImage class to allow for a filepath as well.
	target_image = mm.MosaicImage( Image.open( base_image_filepath ) )

	## Create a mosaic object, specify how many sections you want along the shorter dimension using the granularity.
	## At some point I want the Mosaic class to accept filepath, pillow image object, or mosaic image object as first arg. 
	master = mm.Mosaic(target_image, granularity=1/50, opts=dict())

	## Create a mosaic! - requires a piece list - a list of mosaic image objects to fill in the mosaic. 
	## determine how many subsections of each section you'll look at using f
	## I want to be able to pass piece_list to this, not piece_list.pieces 
	print('Creating the mosaic')
	master.create(piece_list 						, 
					f  					= 4			, 
					comparison_function = mm.ImageComparison.rgb_avg_comparison, 
					random_max 			= 4			,
					neighborhood_size 	= 6		, 
					opts 				= dict() 	, )

	## Save your hard work - will by default save to a subdirectory of the target image.
	## And you, uhhhh, actually can't change that behavior at the moment, lol. 
	print('Saving an html version')
	master.output_html()

	print('Saving the mosaic to disc')
	output_image_filepath = master.output_to_image()




## EXAMPLES!

## Create a mosaic of an image using pieces of itself. 
if False:
	mm.PIECE_DEFAULT_SAVE_SIZE = (128,128)
	target_image = 'C:/Users/wants/Projects/Code/MosaicMakerImages/Woah/SLC/WoahAndAng.jpg'
	master = mm.Mosaic(target_image, granularity=1/16)
	piece_list_directory = master.save_sections()
	piece_list = mm.PieceList( piece_list_directory )

	## I should just be cable to change the granularity and have the object recalculate sections?
	master = mm.Mosaic(target_image, granularity=1/32)
	master.create(piece_list, f=5)
	master.output_to_image()















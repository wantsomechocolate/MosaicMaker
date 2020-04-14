#! python3

from PIL import Image
import os
import mosaic_maker as mm


if False:
	## Some Directories
	# 'C:/Users/wants/Projects/Code/MosaicMakerImages/zztemepdb/'
	# 'C:/Users/wants/Projects/Code/MosaicMakerImages/zzarchivedsearches/People/'
	# 'C:/Users/wants/Projects/Code/MosaicMakerImages/Anqi/Anqi-01/sections/'
	# 'C:/Users/wants/Projects/Code/MosaicMakerImages/JamesGrandfatheredIn/JamesSquare/sections/'

	## Create a piece_list (The result should be a list of MosaicImage objects that have
	## been cropped as squares and resized to the default piece size. )
	piece_list = mm.PieceList( 'C:/Users/wants/Projects/Code/MosaicMakerImages/zztemepdb/' )

	## An image to turn into a mosaic
	base_image_filepath = 'C:/Users/wants/Projects/Code/MosaicMakerImages/James/JamesRx/JamesRx.jpg'

	## A MosaicImage object is just a wrapper for a pillow image object.
	## At some point I want the MosaicImage class to allow for a filepath as well.
	target_image = mm.MosaicImage( Image.open( base_image_filepath ) )

	## Create a mosaic object, specify how many sections you want along the shorter dimension using the granularity.
	## At some point I want the Mosaic class to accept filepath, pillow image object, or mosaic image object as first arg. 
	master = mm.Mosaic(target_image, granularity=1/5, opts=dict())

	## Create a mosaic! - requires a piece list - a list of mosaic image objects to fill in the mosaic. 
	## determine how many subsections of each section you'll look at using f
	## I want to be able to pass piece_list to this, not piece_list.pieces 
	master.create(piece_list, f=1, opts=dict())

	## Save your hard work - will by default save to a subdirectory of the target image.
	## And you, uhhhh, actually can't change that behavior at the moment, lol. 
	output_image_filepath = master.output_to_image()


## EXAMPLES!

## Create a mosaic of an image using pieces of itself. 
if True:
	target_image = 'C:/Users/wants/Projects/Code/MosaicMakerImages/James/JamesRx/JamesRx.jpg'
	master = mm.Mosaic(target_image, granularity=1/16)
	piece_list_directory = master.save_sections()
	piece_list = mm.PieceList( piece_list_directory )
	master = mm.Mosaic(target_image, granularity=1/32)
	master.create(piece_list, f=5)
	master.output_to_image()















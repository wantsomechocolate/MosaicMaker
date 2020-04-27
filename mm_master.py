#! python3

## This is a stop sign
# from PIL import Image

## mah imports
import mosaic_maker as mm
import comparison_functions as cf

if True:

	## PIECE LIST
	## Create a piece_list (The result should be a list of MosaicImage objects that have
	## been cropped as squares and resized to the default piece size. )
	piece_list = mm.PieceList( 'C:/Users/wants/Projects/Code/MosaicMakerImages/image_sources/zztemepdb/' )
	# piece_list = mm.PieceList( 'C:/Users/wants/Projects/Code/MosaicMakerImages/JamesMosaicClimbingProject/James/pieces - best/' )
	# piece_list = mm.PieceList( 'C:/Users/wants/Projects/Code/MosaicMakerImages/Woah/NoClimbing/pieces/' )

	## TARGET IMAGE
	base_image_filepath = 'C:/Users/wants/Projects/Code/MosaicMakerImages/mosaics/Joyce/Joyce/Joyce.png'
	# base_image_filepath = 'C:/Users/wants/Projects/Code/MosaicMakerImages/JamesMosaicClimbingProject/James.png'
	# base_image_filepath = 'C:/Users/wants/Projects/Code/MosaicMakerImages/Woah/Smirk/SmirkCloseUp.jpg'

	## A MosaicImage object is just a wrapper for a pillow image object.
	## At some point I want the MosaicImage class to allow for a filepath as well.
	target_image = mm.MosaicImage( base_image_filepath )

	## MOSAIC OBJECT
	## Create a mosaic object, specify how many sections you want along the shorter dimension using the granularity.
	## At some point I want the Mosaic class to accept filepath, pillow image object, or mosaic image object as first arg. 
	#comparison_function = cf.build_comparison_function(cf.reduce_functions.average, cf.error_functions.rmse)

	master = mm.Mosaic(
		target_image, 
		granularity=1/50, 
		#comparison_function=comparison_function,
		reduce_function=cf.reduce_functions.average,
		error_function=cf.error_functions.sum_abs_error, 
		f=3,
		
		neighborhood_size = 5,
		random_max=0,
		opts=dict() )

	## I still want to give the option to override the comparison function, but how do I want to do it and is it worth it?
	## Because you can just change it on the mosaic? and do I really want to get the 
	## function to use from each section? That would pretty nuts. 
	master.create(piece_list, opts= dict(num_clusters = 15) )

	## Save your hard work - will by default save to a subdirectory of the target image.
	## And you, uhhhh, actually can't change that behavior at the moment, lol. 
	#master.output_html()
	master.output_to_image()

	print("round two")
	master.rgb_weighting=(0.5,1,1)
	master.create(piece_list, opts= dict() )
	master.output_to_image()

## SOME MORE EXAMPLES!

## Loop through setting and note the time that it takes for a bunch of different ones
if False:
	piece_list = mm.PieceList( 'C:/Users/wants/Projects/Code/MosaicMakerImages/zztemepdb/' )
	np = len(piece_list.pieces)
	base_image_filepath = 'C:/Users/wants/Projects/Code/MosaicMakerImages/Anqi/Anqi-01/Anqi-01.png'
	target_image = mm.MosaicImage( Image.open( base_image_filepath ) )
	master = mm.Mosaic(target_image, granularity=1/32, opts=dict())
	
	## Loop through f - ns at 0(min) - g at 1/32
	for i in range(0):
		f, ns, r, g, cf = i+1, 0, 0, "1_32", "RMSE"
		master.create( piece_list, f=f, random_max=r, neighborhood_size=ns )
		master.output_to_image( dict(filename = "F={f} NS={ns} R={r} G={g} CF={cf} NP={np}.png".format( f=f, ns=ns, r=r, g=g, cf=cf, np=np ) ) ) 

	## Loop through ns - f at 1(min) - g at 1/32
	## It seems like increasing f doesn't really have a large effect on the run time - cool.
	for i in range(0):
		f, ns, r, g, cf = 1, i, 0, "1_32", "RMSE"
		master.create( piece_list, f=f, random_max=r, neighborhood_size=ns )
		master.output_to_image( dict(filename = "F={f} NS={ns} R={r} G={g} CF={cf} NP={np}.png".format( f=f, ns=ns, r=r, g=g, cf=cf, np=np ) ) ) 

	## Loop through increasing g - f@min ns@min
	for i in range(5):
		f, ns, r, g, cf = 1, 0, 0, "1_"+str(8*i+16), "RMSE"
		master = mm.Mosaic(target_image, granularity=1/(8*i+16), opts=dict())	
		master.create( piece_list, f=f, random_max=r, neighborhood_size=ns )
		master.output_to_image( dict(filename = "F={f} NS={ns} R={r} G={g} CF={cf} NP={np}.png".format( f=f, ns=ns, r=r, g=g, cf=cf, np=np ) ) ) 

	## Increase all together!
	for i in range(5):
		f, ns, r, g, cf = i+1, i, 0, "1_"+str(8*i+16), "RMSE"	
		master = mm.Mosaic(target_image, granularity=1/(8*i+16), opts=dict())	
		master.create( piece_list, f=f, random_max=r, neighborhood_size=ns )
		master.output_to_image( dict(filename = "F={f} NS={ns} R={r} G={g} CF={cf} NP={np}.png".format( f=f, ns=ns, r=r, g=g, cf=cf, np=np ) ) ) 


## Change the default thumbnail size
if False:
	mm.PIECE_DEFAULT_SAVE_SIZE = (512,512)
	piece_list = mm.PieceList( 'C:/Users/wants/Projects/Code/MosaicMakerImages/JamesMosaicClimbingProject/James/pieces - best/' )
	base_image_filepath = 'C:/Users/wants/Projects/Code/MosaicMakerImages/James/JamesBalloon/JamesBalloon.jpg'
	target_image = mm.MosaicImage( Image.open( base_image_filepath ) )
	master = mm.Mosaic(target_image, granularity=1/50, opts=dict())	
	master.create(piece_list,f= 4,random_max=3,neighborhood_size=3)
	master.output_html()
	master.output_to_image()


## Create a mosaic of an image using pieces of itself. I think this one is fun. 
if False:
	mm.PIECE_DEFAULT_SAVE_SIZE = (128,128)
	target_image = 'C:/Users/wants/Projects/Code/MosaicMakerImages/Joyce/Joyce/Joyce.png'
	master = mm.Mosaic(target_image, granularity=1/4, f=1)
	piece_list_directory = master.save_sections()
	piece_list = mm.PieceList( piece_list_directory )

	## I should just be cable to change the granularity and have the object recalculate sections?
	master.granularity=1/2
	master.create(piece_list)
	master.output_to_image()



if False: # make a mosaic, save the output to an image and then add an overlay of the original image
	piece_list = mm.PieceList( 'C:/Users/wants/Projects/Code/MosaicMakerImages/zztemepdb/' )
	base_image_filepath = 'C:/Users/wants/Projects/Code/MosaicMakerImages/Miho/CloseUp/CloseUp.jpg'
	target_image = mm.MosaicImage( Image.open( base_image_filepath ) )
	master = mm.Mosaic(target_image, granularity=1/10, opts=dict())
	master.create(piece_list,f=1,random_max=0,neighborhood_size=0)
	master.output_to_image(dict(overlay_alpha = 100)) ## 0 to 255

	# base = Image.open('C:/Users/wants/Projects/Code/MosaicMakerImages/Miho/CloseUp/CloseUp/mosaics/1587624603.png')
	# overlay = Image.open('C:/Users/wants/Projects/Code/MosaicMakerImages/Miho/CloseUp/CloseUp.jpg')
	# overlay_resized = overlay.resize(base.size)
	# base.putalpha(255)
	# overlay_resized.putalpha(int(255*0.32))
	# new_img = Image.alpha_composite(base, overlay_resized)
	# new_img.save('asdf.png')











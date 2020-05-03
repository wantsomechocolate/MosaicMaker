#! python3

## An example of how to use the the mosaic_maker module
import mosaic_maker as mm
## This import is only necessary if you want to customize the comparison function
import comparison_functions as cf


if True:

        ## PIECE LIST
        ## Create a piece_list - a list of MosaicImage objects that have been cropped as squares and resized to the default piece size.
        # piece_list = mm.PieceList( 'C:/Users/wants/Projects/Recreational/Programming/Code/MosaicMakerImages/image_sources/zztemepdb/' )
        piece_list = mm.PieceList( 'C:/Users/wants/Projects/Recreational/Programming/Code/MosaicMakerImages/mosaics/Demi/pieces/',max_instances = 30 )
        
        ## TARGET IMAGE
        ## can be a path, a PIL Image object, or a MosaicImage object
        base_image_filepath = 'C:/Users/wants/Projects/Recreational/Programming/Code/MosaicMakerImages/mosaics/Demi/Sun/Demi.jpg'
        target_image = mm.MosaicImage( base_image_filepath )
        
        ## MOSAIC OBJECT
        ## The Mosaic class accepts filepath, pillow image object, or mosaic image object as first arg. 
        master = mm.Mosaic(
            
            ## The only positional argument for initializing the mosaic is the target image
            target_image,
            ## This determines how many sections to cut the target image up into. Its a percentage of the target image's smaller dimension. 
            granularity=1/100,
            
            ## The comparison Functions! You can supply a custom one to comparison_function, or you can override the reduce and error function individually
            comparison_function=None,
            reduce_function=cf.reduce_functions.average,
            error_function=cf.error_functions.luv_low_cost_approx,
            
            ## These things govern how the comparison functions operate, look at the class for more information. 
            f=5,
            rgb_weighting = (1,1,1),
            random_max=0,
            neighborhood_size = 5,
            
            opts=dict() )

        
        ## COMPARISON FUNCTIONS
        ## An example of using the build comparison function to create a sort of custom comparison function. equivalent to just specifying average and rsme separately
        #comparison_function = cf.build_comparison_function(cf.reduce_functions.average, cf.error_functions.rmse)

        ## I still want to give the option to override the comparison function, but how do I want to do it and is it worth it?
        ## Because you can just change it on the mosaic? and do I really want to get the 
        ## function to use from each section? That would pretty nuts. 
        # master.create(piece_list, opts= dict(num_clusters = 15) )

        #hahahahahahahahaha this is good to know, if you go to create another mosaic - all the instance counts in the piece list need to be zeroed out,
        ## another reason to have the piece list be part of the mosaic, I think I might be turning towards the light.
        ## Yeah, something like a directory will do, but a list of mosaic image objects is better? or maybe even just a query or some shit? I'll figure it out
        ## the bottom line is that the more sophisticated you get, the more intertwined piece_list and master become. 

        master.create(piece_list)


        ## OUTPUT
        ## Save your hard work - will by default save to a subdirectory of the target image.
        ## And you, uhhhh, actually can't change that behavior at the moment, lol. 
        master.output_html()
        #master.output_to_image()


## SOME MORE EXAMPLES!
        
## Loop through setting and note the time that it takes for a bunch of different ones
if False:
    from datetime import datetime
    piece_list = mm.PieceList( 'C:/Users/wants/Projects/Recreational/Programming/Code/MosaicMakerImages/JamesMosaicClimbingProject/James/pieces - best/' )
    piece_list.default_save_size = (64,64) ## If you wanted you could use the reduced size to analyze and then the larger size to build?
    np = len(piece_list.pieces)
    target_image = 'C:/Users/wants/Projects/Recreational/Programming/Code/MosaicMakerImages/JamesMosaicClimbingProject/James.png'

    ## Loop through a bunch of different mosaic settings, saving the settings and time elapsed in the file name
    ## I think this is going to save like what, 100 mosaics?
    rf_dict = dict(average = cf.reduce_functions.average, dominant_cluster = cf.reduce_functions.dominant_cluster ) #, dominant_simple = cf.reduce_functions.dominant_simple
    ef_dict = dict(rmse = cf.error_functions.rmse, luv_low_cost_approx = cf.error_functions.luv_low_cost_approx, sum_abs_error = cf.error_functions.sum_abs_error )
    for f in range(2,6):
        for ns in range(1,5):
            for g in range(50,51,1):
                for r in range(0,1):
                    for rf in rf_dict:
                        for ef in ef_dict:
                            master = mm.Mosaic(target_image,
                                               granularity=1/g,
                                               reduce_function = rf_dict[rf],
                                               error_function = ef_dict[ef],
                                               f=f,
                                               random_max = r,
                                               neighborhood_size = ns,
                                               opts=dict())
                            
                            start = datetime.utcnow()
                            master.create( piece_list )
                            end = datetime.utcnow()
                            t = str(int( (end-start).total_seconds() ) )
                            master.output_html(section_dim = 60)

##                            master.output_to_image( dict(filename = "F={f} NS={ns} R={r} G=1_{g} RF={rf} EF={ef} NP={np} T={t}.png".format( f=f,
##                                                                                                                                      ns=ns,
##                                                                                                                                      r=r,
##                                                                                                                                      g=g,
##                                                                                                                                      rf=rf,
##                                                                                                                                      ef=ef,
##                                                                                                                                      np=np,
##                                                                                                                                      t=t,) ) )



## Change the default thumbnail size
if False:
    mm.PIECE_DEFAULT_SAVE_SIZE = (512,512)
    piece_list = mm.PieceList( 'C:/Users/wants/Projects/Recreational/Programming/Code/MosaicMakerImages/JamesMosaicClimbingProject/James/pieces - best/' )
    base_image_filepath = 'C:/Users/wants/Projects/Code/MosaicMakerImages/James/JamesBalloon/JamesBalloon.jpg'
    target_image = mm.MosaicImage( Image.open( base_image_filepath ) )
    master = mm.Mosaic(target_image, granularity=1/50, f=4, random_max=3, neighborhood_size=3, opts=dict())	
    master.create(piece_list)
    master.output_html()
    master.output_to_image()


## Create a mosaic of an image using its own sections as the pieces.
if False:
    mm.PIECE_DEFAULT_SAVE_SIZE = (128,128)
    target_image = 'C:/Users/wants/Projects/Code/Recreational/Programming/MosaicMakerImages/Joyce/Joyce/Joyce.png'
    master = mm.Mosaic(target_image, granularity=1/16)
    piece_list_directory = master.save_sections()
    piece_list = mm.PieceList( piece_list_directory )
    master.granularity=1/32
    master.create(piece_list)
    master.output_to_image()


if False: # Save mosaic with an overlay by supplying a positive value for overlay_alpha to the opts dict
    piece_list = mm.PieceList( 'C:/Users/wants/Projects/Recreational/Programming/Code/MosaicMakerImages/zztemepdb/' )
    base_image_filepath = 'C:/Users/wants/Projects/Recreational/Programming/Code/MosaicMakerImages/Miho/CloseUp/CloseUp.jpg'
    target_image = mm.MosaicImage( Image.open( base_image_filepath ) )
    master = mm.Mosaic(target_image, granularity=1/10, opts=dict())
    master.create(piece_list,f=1,random_max=0,neighborhood_size=0)
    master.output_to_image(dict(overlay_alpha = 100)) ## 0 to 255












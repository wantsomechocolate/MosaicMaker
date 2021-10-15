#! python3

## An example of how to use the the mosaic_maker module
import mosaic_maker as mm
## This import is only necessary if you want to customize the comparison function
import comparison_functions as cf


## ##############################################################################################################################################
## BASIC USAGE
## ##############################################################################################################################################

if False:

        ## PIECE LIST - Create a piece_list - a list of MosaicImage objects that have been cropped as squares and resized to the default piece size.
        #piece_list = mm.PieceList( 'C:/Users/wants/Projects/Recreational/Programming/Code/MosaicMakerImages/image_sources/zztempdb100/',max_instances = 2 )
        piece_list = mm.PieceList( 'C:/Users/wants/Projects/Recreational/Programming/Code/MosaicMakerImages/image_sources/zztemepdb/',max_instances = 10 )
        #piece_list = mm.PieceList( 'C:/Users/wants/Projects/Recreational/Programming/Code/MosaicMakerImages/mosaics/ClimbingProject/James/pieces-groomed/',max_instances = 5 )

        ## TARGET IMAGE - can be a path, a PIL Image object, or a MosaicImage object
        #base_image_filepath = 'C:/Users/wants/Projects/Recreational/Programming/Code/MosaicMakerImages/mosaics/Anqi/Anqi-05/mud_mask.JPG'
        #base_image_filepath = 'C:/Users/wants/Projects/Recreational/Programming/Code/MosaicMakerImages/mosaics/Tests/MaxInstances/AllBlack.PNG'
        #base_image_filepath = r'C:\Users\wants\Projects\Recreational\Programming\Code\MosaicMakerImages\mosaics\Anqi\Anqi-01\Anqi-01.png'
        #base_image_filepath = r'C:/Users/wants/Projects/Recreational/Programming/Code/MosaicMakerImages/mosaics/ClimbingProject/James.png'
        base_image_filepath = r'C:/Users/wants/Projects/Recreational/Programming/Code/MosaicMakerImages/mosaics/Anqi/Anqi-Beach/Anqi-Beach.jpg'
        target_image = mm.MosaicImage( base_image_filepath )
        



        ## COMPARISON FUNCTIONS - comparison function consist of a reducing function and an error function.
        ## Reducing functions take the image data and compress it into less information that can be more quickly compared
        ## Error functions compare the results of the reducing function and produce a single number that indicates similarity (lower is better)
        ## Users can override these functions individually if they don't want to write a completely custom comparison function
        ## Below is an example of using the build comparison function to create a 'custom' comparison function, which in this case is just equivalent to specifying the same
        ## reduce and error functions separately.
        #comparison_function = cf.build_comparison_function(cf.reduce_functions.average, cf.error_functions.rmse)
        

        ## MOSAIC OBJECT - The Mosaic class accepts filepath, pillow image object, or mosaic image object as first arg. 
        master = mm.Mosaic(
            
            ## The only positional argument for initializing the mosaic is the target image
            target_image,
            ## This determines how many sections to cut the target image up into. Its a percentage of the target image's smaller dimension. 
            granularity=1/50,
            ## The comparison Functions! You can supply a custom one to comparison_function, or you can override the reduce and error function individually
            #comparison_function=comparison_function,
            reduce_function=cf.reduce_functions.average,
            error_function=cf.error_functions.sum_abs_error,
            
            ## These things govern how the comparison functions operate, look at the class for more information. I'm considering putting all of these things into opts. 
            f=5,
            rgb_weighting = (1,1.3,1),
            random_max=0,
            neighborhood_size = 5,

            ## Additional parameters. I think this can be used for info needed for custom comparison functions. 
            opts=dict() )


        master.set_section_priority_radial_square(starting_section = (24,18))

        #master.create(piece_list, opts= dict(num_clusters = 15) )
        master.create(piece_list)


        ## OUTPUT
        ## Save your hard work - will by default save to a subdirectory of the target image.
        ## And you, uhhhh, actually can't change that behavior at the moment, lol. 
        master.output_html()
        #master.output_to_image()



## ##############################################################################################################################################
## EXPERIMENTS AND TESTS
## ##############################################################################################################################################

if False: ## go through the different methods of setting section priority
        piece_list = mm.PieceList( 'C:/Users/wants/Projects/Recreational/Programming/Code/MosaicMakerImages/mosaics/ClimbingProject/James/pieces-groomed/',max_instances = 5 )
        base_image_filepath = r'C:/Users/wants/Projects/Recreational/Programming/Code/MosaicMakerImages/mosaics/ClimbingProject/James.png'
        target_image = mm.MosaicImage( base_image_filepath )
        master = mm.Mosaic(target_image, granularity=1/50, f=5, rgb_weighting = (1,1,1), random_max=0, neighborhood_size = 5, opts=dict() )

        ## With default priority (currently right to left top to bottom
        master.create(piece_list)
        master.output_html()

        ## with radial priority
        master.set_section_priority_radial()
        master.create(piece_list)
        master.output_html()

        ## with priority determined using edges.
        master.set_section_priority_edges()
        master.create(piece_list)
        master.output_html()

        ## with priority determined using facial recognition dlib (not ready yet)
        

if False: ## Set section priority and create a mosaic
    target_image = mm.MosaicImage('C:/Users/wants/Projects/Recreational/Programming/Code/MosaicMakerImages/mosaics/Anqi/Anqi-05/mud_mask.JPG')
    master = mm.Mosaic(target_image)
    master.set_section_priority_edges()
    piece_list = mm.PieceList( 'C:/Users/wants/Projects/Recreational/Programming/Code/MosaicMakerImages/image_sources/zztemepdb/',max_instances = 2 )
    master.create(piece_list)
    master.output_html()

    ## Get the edges image from the original master and use it to create an edge master
    ## loop through all the sections and calculate the average amount of white?
    ## bin all the values into n priority bins and then somehow get the priority mapped back onto the original master?
    
    


if False: ## Loop through setting and note the time that it takes for a bunch of different ones
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
                            #master.output_to_image( dict(filename = "F={f} NS={ns} R={r} G=1_{g} RF={rf} EF={ef} NP={np} T={t}.png".format( f=f,
                            #                                                                                                          ns=ns,
                            #                                                                                                          r=r,
                            #                                                                                                          g=g,
                            #                                                                                                          rf=rf,
                            #                                                                                                          ef=ef,
                            #                                                                                                          np=np,
                            #                                                                                                          t=t,) ) )



if False: ## Change the default thumbnail size
    mm.PIECE_DEFAULT_SAVE_SIZE = (512,512)
    piece_list = mm.PieceList( 'C:/Users/wants/Projects/Recreational/Programming/Code/MosaicMakerImages/JamesMosaicClimbingProject/James/pieces - best/' )
    base_image_filepath = 'C:/Users/wants/Projects/Code/MosaicMakerImages/James/JamesBalloon/JamesBalloon.jpg'
    target_image = mm.MosaicImage( Image.open( base_image_filepath ) )
    master = mm.Mosaic(target_image, granularity=1/50, f=4, random_max=3, neighborhood_size=3, opts=dict())	
    master.create(piece_list)
    master.output_html()
    master.output_to_image()


if True: ## Create a mosaic of an image using its own sections as the pieces.
    mm.PIECE_DEFAULT_SAVE_SIZE = (128,128)
    target_image = r'C:\Users\JamesM\Projects\Programming\MosaicMakerImages\Anqi\BWSmile\BWSmile.png'
    master = mm.Mosaic(target_image, granularity=1/16)
    piece_list_directory = master.save_sections()
    piece_list = mm.PieceList( piece_list_directory )
    master.granularity=1/32
    master.f = 3
    master.neighborhood_size = 5
    master.set_section_priority_radial()
    master.create(piece_list)
    master.output_html()    
    #master.output_to_image()


if False: # Save mosaic with an overlay by supplying a positive value for overlay_alpha to the opts dict
    from PIL import Image
    piece_list = mm.PieceList( 'C:/Users/wants/Projects/Recreational/Programming/Code/MosaicMakerImages/image_sources/zztemepdb/', max_instances = 2 )
    base_image_filepath = 'C:/Users/wants/Projects/Recreational/Programming/Code/MosaicMakerImages/mosaics/Miho/CloseUp/CloseUp.jpg'
    target_image = mm.MosaicImage( Image.open( base_image_filepath ) )
    master = mm.Mosaic(target_image, granularity=1/16, opts=dict())
    ## create doesn't take these arguments any more. These things live on the  mosaic object
    ## master.create(piece_list,f=1,random_max=0,neighborhood_size=0)
    master.create(piece_list)
    master.output_to_image(dict(overlay_alpha = 100)) ## 0 to 255


if False: # Test max_instances, replace_all_instances, and blocklist
    piece_list = mm.PieceList( 'C:/Users/wants/Projects/Recreational/Programming/Code/MosaicMakerImages/image_sources/zztempdb100/',max_instances = 2 )
    base_image_filepath = 'C:/Users/wants/Projects/Recreational/Programming/Code/MosaicMakerImages/mosaics/Tests/MaxInstances/AllBlack.PNG'
    #base_image_filepath = 'C:/Users/wants/Projects/Recreational/Programming/Code/MosaicMakerImages/mosaics/Miho/CloseUp/CloseUp.jpg'
    target_image = mm.MosaicImage( base_image_filepath )
    master = mm.Mosaic(target_image,granularity=1/12,comparison_function=None,f=1,rgb_weighting = (1,1,1),random_max=0,neighborhood_size = 1,opts=dict() )
    master.create(piece_list)
    master.output_html()
    updated_instances = master.update_all_instances_of((1,9),piece_list)
    master.output_html()

    ## It is interesting to note here that successive iterations of update_all_instances will continue to blacklist items previously updated.
    ## For example, the tree is completely removed from mosaic 1 to 2, but then in mosaic 3, it is not used to replace other images, despite being a better match.
    ## I'm not sure if this is the desired behavior or not. but I think it's a pretty good default for now. 
    updated_instances_2 = master.update_all_instances_of_except_self((1,9),piece_list)
    master.output_html()

if False: #build a custom comparison function and then use to create a mosaic. 
    piece_list = mm.PieceList( 'C:/Users/wants/Projects/Recreational/Programming/Code/MosaicMakerImages/image_sources/zztempdb100/',max_instances = 2 )
    base_image_filepath = 'C:/Users/wants/Projects/Recreational/Programming/Code/MosaicMakerImages/mosaics/Tests/MaxInstances/AllBlack.PNG'
    comparison_function = cf.build_comparison_function(cf.reduce_functions.average, cf.error_functions.luv_low_cost_approx)
    master = mm.Mosaic(base_image_filepath, comparison_function=comparison_function )
    master.create(piece_list)
    master.output_html()





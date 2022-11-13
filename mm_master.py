#! python3

## An example of how to use the the mosaic_maker module
import mosaic_maker as mm
## This import is only necessary if you want to customize the comparison function
import comparison_functions as cf
from datetime import datetime
import cv2

## ##############################################################################################################################################
## BASIC USAGE
## ##############################################################################################################################################

if True:

        ## PIECE LIST - Create a piece_list - a list of MosaicImage objects that have been cropped as squares and resized to the default piece size.
        piece_list = mm.PieceList( r'demo\library',max_instances = 5 )
        piece_list.default_save_size = (64,64)

        ## TARGET IMAGE - can be a path, a PIL Image object, or a MosaicImage object
        base_image_filepath = r'demo\scarjo.jpg'
        target_image = mm.MosaicImage( base_image_filepath )
        
        ## COMPARISON FUNCTIONS - comparison function consist of a reducing function and an error function
        ## Reducing functions take the image data and compress it into less information that can be more quickly compared
        ## Error functions compare the results of the reducing function and produce a single number that indicates similarity
        ## Users can override these functions individually (both or separately) or override the comparison function
        ## Below is an exmaple of using 'build_comparison_function' to create a comparison function from individual reduce and error functions
        ## Read the code for how to structure these functions so that they work with the rest of the code
        #comparison_function = cf.build_comparison_function(cf.reduce_functions.average, cf.error_functions.rmse)
        
        ## Set the comparison granularity (f), section granularity (g), randomization (r), and neighborhood size (ns)        
        f,g,r,ns = 2,40,0,5

        ## Specify reduce and error functions to override the default ones
        rf=cf.reduce_functions.average
        ef=cf.error_functions.sum_abs_error

        ## MOSAIC OBJECT - The Mosaic class accepts filepath, pillow image object, or mosaic image object as first arg. 
        master = mm.Mosaic(
            
            ## The only positional argument for initializing the mosaic is the target image
            target_image, 
            granularity=1/g,
            
            reduce_function=rf,
            error_function=ef,
            #comparison_function=comparison_function,
            
            f=f,
            rgb_weighting = (1,1.1,1.2), ## Weights the error
            random_max=r,
            neighborhood_size = ns,

            ## Additional parameters. I think this can be used for info needed for custom comparison functions. 
            opts=dict() )

                                                        
        start = datetime.utcnow()
        master.create(piece_list)
        end = datetime.utcnow()
        t = str(int( (end-start).total_seconds() ) )


        ## OUTPUT
        ## Save html, css and target image file and required piece image files for viewing mosaic in a browser
        master.output_html()

        ## Save the image with a specific file name (optional)
        master.output_to_image( dict(filename = "F={f} NS={ns} R={r} G=1_{g} RF={rf} EF={ef} NP={np} T={t}.png".format( f=f,
                                                                                                                  ns=ns,
                                                                                                                  r=r,
                                                                                                                  g=g,
                                                                                                                  rf=rf.__name__,
                                                                                                                  ef=ef.__name__,
                                                                                                                  np=len(piece_list.pieces),
                                                                                                                  t=t,) ) )



## ##############################################################################################################################################
## EXPERIMENTS AND TESTS
## ##############################################################################################################################################

## Different Methods of Setting Section Priority
if False:
        piece_list = mm.PieceList( r'demo/library',max_instances = 5 )
        base_image_filepath = r'demo/scarjo.jpg'
        target_image = mm.MosaicImage( base_image_filepath )
        master = mm.Mosaic(target_image, granularity=1/20, f=1, rgb_weighting = (1,1,1), random_max=0, neighborhood_size = 5, opts=dict() )

        ## No Priority (top to bottom and left to right)
        master.set_section_priority_zero()
        master.show_section_priority()
        master.create(piece_list)
        master.output_html()

        ## with radial priority (the default)
        master.set_section_priority_radial()
        master.show_section_priority()
        master.create(piece_list)
        master.output_html()

        ## with priority determined using edges.
        from PIL import ImageFilter
        master.set_section_priority_edges(radius=0.5,additive=True,multiplier=5, kernel=ImageFilter.FIND_EDGES)
        master.show_section_priority()
        master.create(piece_list)
        master.output_html()

        ## with priority determined using haar cascades (for object recognition)
        master.set_section_priority_radial()

        ## items_to_detect by default looks for eyes, faces, and facial features. But you can pass a list of dictionaries like this to override or add to the default list
        items_to_detect = [ 	dict( 	cascade = cv2.data.haarcascades + 'haarcascade_eye.xml',
                                        scale_factor = 1.2,
					min_neighbors = 15,
					priority = 20,
					rect_color=(10,10,10)							        ),
                                
                                dict( 	cascade = cv2.data.haarcascades + 'haarcascade_features.xml',
					scale_factor = 1.2,
                                        min_neighbors = 5,
					priority = 20,
					rect_color=(50,50,50)								)]
        master.set_section_priority_object_recognition(items_to_detect = items_to_detect, additive=True, keep_default_cascades=False)
        master.show_section_priority()
        master.create(piece_list)
        master.output_html()

        ## You can also loop through the master.grid and set priority yourself in anyway you'd like
    

## Loop through tons of different configuration and change the settings.
if False: 
    piece_list = mm.PieceList( r'demo/library',max_instances = 5 )

    piece_list.default_save_size = (64,64) ##Saves some time and reduces size of saved mosaics.
    np = len(piece_list.pieces)

    target_image = mm.MosaicImage( r'demo/scarjo.jpg' )

    ## Loop through a bunch of different mosaic settings, saving the settings and time elapsed in the file name
    rf_dict = dict(average = cf.reduce_functions.average, dominant_cluster = cf.reduce_functions.dominant_cluster, dominant_simple = cf.reduce_functions.dominant_simple, resize_image = cf.reduce_functions.resize_image)
    ef_dict = dict(sum_abs_error = cf.error_functions.sum_abs_error, rmse = cf.error_functions.rmse, luv_low_cost_approx = cf.error_functions.luv_low_cost_approx)
    for f in range(1,5):
        for ns in range(0,5):
            for g in range(10,50,10):
                for r in range(0,2):
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
                            #print("{}-{}-{}-{}-{}-{}".format())
                            master.output_to_image( dict(filename = "F={f} NS={ns} R={r} G=1_{g} RF={rf} EF={ef} NP={np} T={t}.png".format( f=f,
                                                                                                                                      ns=ns,
                                                                                                                                      r=r,
                                                                                                                                      g=g,
                                                                                                                                      rf=rf,
                                                                                                                                      ef=ef,
                                                                                                                                      np=np,
                                                                                                                                      t=t,) ) )


## Change the default thumbnail size
if False:
    from PIL import Image
    mm.PIECE_DEFAULT_SAVE_SIZE = (512,512)
    piece_list = mm.PieceList( r'demo/library',max_instances = 5 )
    base_image_filepath = r'demo/scarjo.jpg'
    target_image = mm.MosaicImage( Image.open( base_image_filepath ) )
    master = mm.Mosaic(target_image, granularity=1/50, f=4, random_max=3, neighborhood_size=3, opts=dict())	
    master.create(piece_list)
    master.output_html()
    master.output_to_image()


## Create a mosaic of an image using its own sections as the pieces.
if False: 
    mm.PIECE_DEFAULT_SAVE_SIZE = (128,128)
    master = mm.Mosaic(r'demo/scarjo.jpg', granularity=1/16)
    piece_list_directory = master.save_sections()
    piece_list = mm.PieceList( piece_list_directory )
    master.granularity=1/32
    master.f = 3
    master.neighborhood_size = 5
    master.set_section_priority_radial()
    master.create(piece_list)
    master.output_html()    
    master.output_to_image()


# Save mosaic with an overlay by supplying a positive value for overlay_alpha to the opts dict
if True: 
    from PIL import Image
    piece_list = mm.PieceList( r'demo/library',max_instances = 10 )
    piece_list.default_save_size = (64,64)
    base_image_filepath = r'demo/scarjo.jpg'
    target_image = mm.MosaicImage( Image.open( base_image_filepath ) )
    master = mm.Mosaic(target_image, granularity=1/16, opts=dict())
    master.create(piece_list)
    master.output_to_image(dict(overlay_alpha = 100)) ## 0 to 255


## Test out update_all_instances_of()
if False: 
    piece_list = mm.PieceList( r'demo/library',max_instances = 5 )
    piece_list.default_save_size = (64,64)
    base_image_filepath = r'demo/scarjo.jpg'
    target_image = mm.MosaicImage( base_image_filepath )
    master = mm.Mosaic(target_image,granularity=1/12,comparison_function=None,f=1,rgb_weighting = (1,1,1),random_max=0,neighborhood_size = 1,opts=dict() )
    master.create(piece_list)
    master.output_html()
    updated_instances = master.update_all_instances_of((1,9),piece_list)
    master.output_html()

    ## It is interesting to note here that successive iterations of update_all_instances will continue to blacklist items previously updated.
    ## For example, the tree is completely removed from mosaic 1 to 2, but then in mosaic 3, it is not used to replace other images, despite being a better match.
    ## I'm not sure if this is the desired behavior or not. but I think it's a pretty good default for now. 
    updated_instances_2 = master.update_all_instances_of((1,9),piece_list,replace_self=True)
    master.output_html()
    

## Build a custom comparison function and then use to create a mosaic. 
if False: 
    piece_list = mm.PieceList( r'demo/library',max_instances = 5 )
    piece_list.default_save_size = (64,64)
    base_image_filepath = r'demo/scarjo.jpg'
    comparison_function = cf.build_comparison_function(cf.reduce_functions.average, cf.error_functions.luv_low_cost_approx)
    master = mm.Mosaic(base_image_filepath, comparison_function=comparison_function )
    master.create(piece_list)
    master.output_html()


## Update cluster size using dominant cluster reduce function
if False:
    piece_list = mm.PieceList( r'demo/library',max_instances = 5 )
    piece_list.default_save_size = (64,64)
    base_image_filepath = r'demo/scarjo.jpg'
    master = mm.Mosaic(base_image_filepath, reduce_function = cf.reduce_functions.dominant_cluster)
    master.create(piece_list, opts= dict(num_clusters = 15) )
    master.output_html()
    

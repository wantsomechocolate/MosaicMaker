
def average_two_obj( 
                obj1                            , 
                obj2                            , 
                f               = 2             ,  
                first           = True          ,
                reset_obj1      = True          ,
                reset_obj2      = True          ,
                opts            = dict()        ,   ):

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
    #rgb_error_weight_array = np.array(rgb_weighting)

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

def rgb_avg_comparison( 
    obj1                            , 
    obj2                            , 
    f               = 2             , 
    rgb_weighting   = (1,1,1)       , 
    first           = True          ,
    reset_obj1      = True          ,
    reset_obj2      = True          ,
    opts            = dict()        ,   ):


    obj1_data, obj2_data = reduce_functions.average( 
                        obj1                            , 
                        obj2                            , 
                        f               = f             ,  
                        first           = first         ,
                        reset_obj1      = reset_obj1    ,
                        reset_obj2      = reset_obj2    ,
                        opts            = opts          ,   )

    obj2.error = error_functions.sum_abs_error(
                        obj1_data                       , 
                        obj2_data                       , 
                        rgb_weighting                   ,   )


def rgb_avg_comparison_f_eq_1(obj1,obj2,opts=dict()):

	## reset the obj2 error just in case anything crazy happens
	obj2.error = None

	if not hasattr(obj1,"rgb_avg"):
		obj1.rgb_avg = np.mean(obj1.rgb_data, axis=(0, 1))

	if not hasattr(obj2,"rgb_avg"):
		obj2.rgb_avg = np.mean(obj2.rgb_data, axis=(0, 1))

	error = np.absolute(obj1.rgb_avg - obj2.rgb_avg).sum()
	
	obj2.error = error

	return error




## For plotting with matplotlib - only good for large granularity
def output_matplotlib(master):

    import matplotlib.pyplot as plt
    
    print("Starting to plot")

    fig, axes = plt.subplots(master.h_sections, master.w_sections) #, figsize=(master.w_sections, master.h_sections))
    for i in range(master.h_sections):
        for j in range(master.w_sections):
            dummy = axes[i,j].imshow(master.grid[i][j].currentMosaicImage.rgb_data)
            dummy = axes[i,j].axis('off')

    fig.subplots_adjust(wspace=0, hspace=0)
    fig.show()
    return fig

    ## Code for making a plot of the original but the same size as the mosaics because I like it
    if False:
        fig2, axes2 = plt.subplots(1, 1)
        dummy = axes2.imshow(master.targetImgObject.rgb_data)
        dummy = axes2.axis('off')
        fig2.subplots_adjust(wspace=0, hspace=0)
        fig2.show()






## COMPARISON FUNCTIONS
## All comparison functions should take two objects and an optional dictionary of options
## These two objects can be expected to have three attributes
##      img      - the PIL image object
##      rgb_data - a numpy array with color data
##      error    - the default is None
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

    def rgb_avg_comparison( obj1                            , 
                            obj2                            , 
                            f               = 2             , 
                            rgb_weighting   = (1,1,1)       , 
                            first           = True          ,
                            reset_obj1      = True          ,
                            reset_obj2      = True          ,
                            opts            = dict()        ,   ):


        obj1_data, obj2_data = ImageComparison.ReduceFuncs.average( 
                            obj1                            , 
                            obj2                            , 
                            f               = f             , 
                            rgb_weighting   = rgb_weighting , 
                            first           = first         ,
                            reset_obj1      = reset_obj1    ,
                            reset_obj2      = reset_obj2    ,
                            opts            = opts          ,   )

        error = ImageComparison.ErrorFuncs.sum_abs_error(
                            obj1_data                       , 
                            obj2_data                       , 
                            rgb_weighting                   ,   )

        obj2.error = error

        return error


    class ReduceFuncs:
        def __init__(self):
            self.default = self.average


        def average(    obj1                            , 
                        obj2                            , 
                        f               = 2             , 
                        rgb_weighting   = (1,1,1)       , 
                        first           = True          ,
                        reset_obj1      = True          ,
                        reset_obj2      = True          ,
                        opts            = dict()        ,   ):

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
            #return obj1.rgb_dom, obj2.rgb_dom


    class ErrorFuncs:
        
        #def __init__(self):
        #   self.default = self.rmse
        
        def default(list_of_array_1,list_of_array_2,rgb_error_weight_array):
            return rmse(list_of_array_1,list_of_array_2,rgb_error_weight_array)

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


#python3

import comparison_functions.error_functions
import comparison_functions.reduce_functions

## I think that comparison functions should be able to get a size to use for their analysis
## maybe the user wants to analyze a smaller size for speed, but still use a larger thumbnail for the stuff

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
## Comparison function are given information on when an object is being analyzed by it's function for the first time.
## If reusable results are being saved on the object to use in later iterations, they should be reset 
## when the reset variables indicate. 



## Builds comparison functions from reduce and error functions. 
## reduce functions are expected to take image data and produce of a list of distilled image data. 
## the error function expects two equally sized lists and is expected to return a numerical value
def build_comparison_function(reduce_function, error_function, opts=dict() ):
	
	def comparison_function( 	
		obj1 						, 
		obj2 						, 
		f 				= 2 		, 
		rgb_weighting 	= (1,1,1)	, 
		reset_obj1		= True 		,
		reset_obj2 		= True 		,
		opts 			= dict() 	,	):

		obj1_data = reduce_function( 
			obj1 					, 
			f 		= f 			,  
			reset 	= reset_obj1	,
			opts 	= opts 			,	)

		obj2_data = reduce_function( 
			obj2 					, 
			f 		= f 			,  
			reset 	= reset_obj2	,
			opts 	= opts 			,	)

		obj2.error = error_function(
			obj1_data 				, 
			obj2_data 				, 
			rgb_weighting 			,
			opts = opts 			,	)

	return comparison_function


## This is an example of a function that uses the library functions to build a comparison function
## This is useful in the case that someone wants to override one but not the other? I guess?
## This could just write the function and pass it to the class directly instead of doing this, but whatever.   
def comparison_function_library_example( 
	obj1 						, 
	obj2 						, 
	f 				= 2 		, 
	rgb_weighting 	= (1,1,1)	, 
	reset_obj1		= True 		,
	reset_obj2 		= True 		,
	opts 			= dict() 	,	):


	obj1_data = reduce_functions.average( 
		obj1 					, 
		f 		= f 			,  
		reset 	= reset_obj1	,
		opts 	= opts 			,	)

	obj2_data = reduce_functions.average( 
		obj2 					, 
		f 		= f 			,  
		reset 	= reset_obj2	,
		opts 	= opts 			,	)


	obj2.error = error_functions.rmse(
		obj1_data 				, 
		obj2_data 				, 
		rgb_weighting 			,
		opts = opts 			,	)


## This is a very very slow example of a function that doesn't use the reduce and error functions
## and instead directly applies the error to obj2
def comparison_function_custom_example( 	
	obj1 						, 
	obj2 						, 
	f 				= 2 		, 
	rgb_weighting 	= (1,1,1)	, 
	first 			= True  	,
	reset_obj1		= True 		,
	reset_obj2 		= True 		,
	opts 			= dict() 	,	):

	if reset_obj1:
		if hasattr(obj1,'piece_sized_section_rgb_data'):
			delattr(obj1, 'piece_sized_section_rgb_data')

	if not hasattr(obj1, 'piece_sized_section_rgb_data'):
		if obj1.img.size != obj2.img.size:
			obj1.piece_sized_section_rgb_data = np.asarray(obj1.img.resize(obj2.img.size))
		else:
			obj1.piece_sized_section_rgb_data = obj.rgb_data

	obj2.error = np.absolute(obj1.piece_sized_section_rgb_data - obj2.rgb_data).sum()



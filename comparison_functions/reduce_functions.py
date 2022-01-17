#python3

import numpy as np
import scipy as sp
import scipy.cluster
import scipy.stats

def average( 	
	obj 				, 
	f 		= 2 		,  
	reset 	= True 		,
	opts 	= dict() 	,	):

	## If the greater being is telling you to reset, reset.
	if reset:		
		if hasattr(obj,'rgb_avg'):
			delattr(obj, 'rgb_avg')
	
	## Check to see if you've already calculated whatever it is you're trying to calculate for obj. 
	if not hasattr(obj,"rgb_avg"):
		obj.rgb_avg = []
		for i in range(f):
			for j in range(f):
				obj.rgb_avg.append( np.mean( obj.rgb_data[ int(obj.height/f)*i : int(obj.height/f)*(i+1) , 
									int(obj.width/f)*j  : int(obj.width/f)*(j+1) , 
									: ], axis=(0,1) ) )

	return obj.rgb_avg



## I'll write this function some day dammit. I wonder if it will help with the skin color in low light problem?
def dominant_cluster(	
	obj 				, 
	f 		= 2 		,  
	reset 	= True 		,
	opts 	= dict() 	,	):
	

	if reset:
		if hasattr(obj,'rgb_dom'):
			delattr(obj,'rgb_dom')

	if not hasattr(obj,'rgb_dom'):
		obj.rgb_dom=[]
		for i in range(f):
			for j in range(f):

				ar = obj.rgb_data[ int(obj.height/f)*i : int(obj.height/f)*(i+1) , int(obj.width/f)*j  : int(obj.width/f)*(j+1) , : ]
				obj.rgb_dom.append( __dominant_cluster(ar, opts = opts) )

	return obj.rgb_dom


def __dominant_cluster(ar,opts=dict()):

	## https://stackoverflow.com/a/3244061/1937423

	NUM_CLUSTERS = opts['num_clusters'] if 'num_clusters' in opts.keys() else 5
	
	shape = ar.shape
	ar = ar.reshape(np.product(shape[:2]), shape[2]).astype(float)
	codes, dist = sp.cluster.vq.kmeans(ar, NUM_CLUSTERS)

	vecs, dist = sp.cluster.vq.vq(ar, codes)
	counts, bins = np.histogram(vecs, len(codes))

	index_max = np.argmax(counts)
	peak = codes[index_max]

	return peak



# There is definitely something wrong with this method, am I picking the least dominant color or something?
# sometimes this function doesn't work because there is no 'most common' color, in which case, it picks the smaller
# one regarding the rgb values. 
def dominant_simple(

	## https://stackoverflow.com/a/16331189/1937423

	obj 				, 
	f 		= 2 		,  
	reset 	= True 		,
	opts 	= dict() 	,	):
	
	if reset:
		if hasattr(obj,'rgb_dom'):
			delattr(obj,'rgb_dom')

	if not hasattr(obj,'rgb_dom'):
		obj.rgb_dom=[]
		for i in range(f):
			for j in range(f):

				ar = obj.rgb_data[ int(obj.height/f)*i : int(obj.height/f)*(i+1) , int(obj.width/f)*j  : int(obj.width/f)*(j+1) , : ]				
				shape = ar.shape
				ar = ar.reshape((1,shape[0]*shape[1],shape[2]))
				obj.rgb_dom.append( np.unique(ar,axis=1)[0][0] )

	return obj.rgb_dom




#reisze the images to a small thing and just return all the pixel data
def resize_image(
	#docstring="""Uses PIL.Image.resize to reduce rgb data before sending to the error function"""
	obj,
	f = 8,
	reset = True,
	opts = dict(), ):

	if reset:
		if hasattr(obj,'rgb_resized_data'):
			delattr(obj,'rgb_resized_data')

	if not hasattr(obj, 'rgb_resized_data'):
		ar =  np.asarray(obj.img.resize((f,f)))
		shape = ar.shape
		ar = ar.reshape((1,shape[0]*shape[1],shape[2]))
		ar = ar.astype(np.int16)

		obj.rgb_resized_data = ar[0]

	return obj.rgb_resized_data








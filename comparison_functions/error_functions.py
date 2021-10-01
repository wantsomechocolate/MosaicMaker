#python3

import numpy as np

def rmse(
	list_of_array_1 		,
	list_of_array_2 		,
	rgb_error_weight_array 	,
	opts = dict() 			,	):
	
	error=0
	for i in range(len( list_of_array_1 )):
		error += np.sqrt( np.mean( np.square( ( list_of_array_1[i] - list_of_array_2[i] ) * rgb_error_weight_array ) ) )
	return error


def luv_low_cost_approx(
	list_of_array_1 		,
	list_of_array_2 		,
	rgb_error_weight_array 	,
	opts = dict() 			,	):
	
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


def sum_abs_error(
	list_of_array_1 		,
	list_of_array_2 		,
	rgb_error_weight_array 	,
	opts = dict() 			,	):
	
	error=0
	for i in range(len( list_of_array_1 )):
		error += sum( np.absolute(list_of_array_1[i] - list_of_array_2[i]) * rgb_error_weight_array )
	return error
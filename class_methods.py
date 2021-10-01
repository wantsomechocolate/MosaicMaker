from datetime import datetime
from comparison_functions import reduce_functions

class A:

	def __init__(self):
		self.third_func = reduce_functions.test


	def some_func(self,a,b,c,d):
		print(self.third_func(a,b,c,d))

	def some_func_w_arg(self,arg):
		print(arg)
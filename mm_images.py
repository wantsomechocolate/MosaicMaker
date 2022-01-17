
## Some functions useful for generating piece libraries using the google cse
## If I wanted to add functionality for creating piece lists from databases, or db queries, it would make sense to come here first.


## IMPORTS
import os, requests
import sqlite3 as sqlite 
from googleapiclient.discovery import build
from io import BytesIO

from PIL import Image
from PIL import UnidentifiedImageError

from math import floor
from pathlib import Path 

## THINGS THAT SHOULD GO IN A YAML
MAX_ITEMS=100
IMG_SAVE_SIZE = (512,512)
IMG_DEFAULT_EXT = '.png'
DEFAULT_SAVE_PATH = 'C:/Users/JamesM/Projects/Programming/MosaicMakerImages/zzSearchQueries'
DB_LOCATION_GLOBAL = 'C:/Users/JamesM/Projects/Programming/MosaicMakerImages/mosaicmaker_db.sqlite'
# DB_LOCATION = os.environ("MOSAIC_MAKER_DB_LOCATION")


#####################################################################################
## FUNCTION RELATED TO CSE API
#####################################################################################


## This function's only purpose is to make a single image search request. 
def cse_basic_api_call(q, **kwargs):

	MOSAIC_MAKER_CSE_API_KEY = os.environ['MOSAIC_MAKER_CSE_API_KEY'	]
	MOSAIC_MAKER_CSE_ID      = os.environ['MOSAIC_MAKER_CSE_ID'			]

	service = build(			"customsearch", 
								"v1", 
								developerKey=MOSAIC_MAKER_CSE_API_KEY	)

	res = service.cse().list(	q=q, 
								cx=MOSAIC_MAKER_CSE_ID, 
								**kwargs								).execute()

	## some stuff you can declare as kwargs
	## fileType, imgColorType, imgDominantColor, imgSize, 
	## imgType, num, safe, searchType, start
	## see the docs for more info

	return res


## To test the simple request function
#if False:
#	res = cse_basic_api_call(	"sunset" 						,
#								searchType 			=	'image'	,
#								imgDominantColor	=	'red'	,
#								#imgSize 			=	'large'	,
#								start=11						,		)


## Loop over cse_basic_api_call function and make enough calls to get all items less than max items
def cse_iterator(q, **kwargs):
	
	## initialize
	res_list = list()
	start = kwargs['start']
	num = kwargs['num']

	## while the request won't ask for any items over max items
	## even if the start is less than 100, it doesn't adjust num to get the last few items.  
	while start+num-1 <= MAX_ITEMS:
		## call the basic api call
		res = cse_basic_api_call(q,**kwargs)
		## append the results to a list
		res_list.append(res)
		## update the start variable with the next next page info from the response
		start = res['queries']['nextPage'][0]['startIndex']
		## most importantly
		kwargs['start'] = start
		## this is where I would adjust num in case that start+num-1 > max items

	## use start as the start, and max_items as a stop.

	## some ways to get at the data:
	## res_list[i]["items"][j]["link"]
	
	return res_list

## To test the wrapper for the single request function to make API requests to get items below MAX_ITEMS
#if False:
#	res_list = cse_iterator(	"sunset"						,
#								searchType 			=	'image'	,
#								imgDominantColor 	=	'red'	,
#								imgSize 			=	'large'	,
#								start 				= 	1		,
#								num 				= 	10		,	)


#####################################################################################
## FUNCTIONS RELATED TO IMAGES - PROCESSING, FETCHING, SAVING, ETC
#####################################################################################

## takes an image url and opens up an image fh in pillow
## also assigns the image name based on the original image filename.
## But I actually don't want to do that anymore. 
## I want to save the url of course, but the filename will be something else. 

## This is certainly not specific to image manipulation
## More related to this module that deals with getting images using google cse
def img_fh_from_url(url):

	## Uses requests, io, and PIL
	filename = url.split("/")[-1]

	try:
		r = requests.get(url)
	except requests.exceptions.ConnectionError as err:
		print (err)
		return None #, err
	except requests.exceptions.ChunkedEncodingError as err:
		print (err)
		return None
	
	img_bytes = BytesIO(r.content)

	try:
		img = Image.open(img_bytes)
	except UnidentifiedImageError as err:
		print (err)
		return None #, err

	img.filename = filename
 
	return img


## I think it makes sense to move this to the MosaicImage class
## This function has been moved! but it is part of the MosaicImage class, thoughts?
def img_crop_center(img):

	ow, oh = img.size
	dw = dh = min(ow, oh)

	left  = floor( (ow/2) - (dw/2) )
	upper = floor( (oh/2) - (dh/2) )
	right = floor( (ow/2) + (dw/2) )
	lower = floor( (oh/2) + (dh/2) )

	try:
		crop = img.crop((left,upper,right,lower))
	except OSError as err:
		print("There was a problem cropping the image")
		print(err)
		crop = img

	
	if hasattr(img,'filename'):
		crop.filename = img.filename

	return crop


## This function has been moved!
def img_resize_to_def_save_size(img):

	img_resized = img.resize(IMG_SAVE_SIZE)
	img_resized.filename = img.filename

	return img_resized



def img_crop_out_border(img,border_size_percent = 0.1):
	'''takes an image and a number as the percent of the shorter dimention of the image to remove from the border of the image'''
	crop_size = int(min(img.size)*border_size_percent)
	new_img =  img.crop([crop_size,crop_size,img.width - crop_size, img.height - crop_size])

	if hasattr(img,'filename'):
		new_img.filename = img.filename

	return new_img



def img_save(img,path = DEFAULT_SAVE_PATH): #, filepath = None, query = None):

	import base64
	import os
	from datetime import datetime

	#try:
	#new_filename = os.path.splitext(os.path.basename(filepath))[0]+" - "+query+int(datetime.timestamp(datetime.utcnow()))

	#except:
	new_filename = base64.urlsafe_b64encode( Path(img.filename[:50]).stem.encode('utf-8') ).decode('utf-8') + IMG_DEFAULT_EXT
	
	fp = os.path.join(path,new_filename)

	os.mkdir(path) if not os.path.exists(path) else None

	img.filename = new_filename

	try:
		img.save(fp)
	except OSError as err:
		print("There was a problem saving the file")
		print (err)
		return None
	except ValueError as err:
		print("There was a problem saving the file")
		print(err)
		return None

	return img


## Test the above functions - go from url to img saved on disk
#if False:
#	url = 'https://images-na.ssl-images-amazon.com/images/I/51pkwlSX97L._AC_.jpg'
#	img_orig = img_fh_from_url(url)
#	img_crop = img_crop_center(img_orig)
#	img_zoom = img_crop_out_border(img_crop)
#	img_resized = img_resize_to_def_save_size(img_zoom)
#	img_final = img_save(img_resized)



##############################################################################
## THESE ARE FOR DB
##############################################################################

## James made a class? is such a thing even possible?
class Database(object):

	DB_LOCATION = DB_LOCATION_GLOBAL

	def __enter__(self):
		return self	

	def __init__(self):
		self.connection = sqlite.connect(Database.DB_LOCATION)
		self.cursor = self.connection.cursor()

	def create_query_table(self):
		self.cursor.execute(''' CREATE TABLE IF NOT EXISTS query (	id 				INTEGER PRIMARY KEY ,
																	response 		TEXT 				, 
																	created_date 	INTEGER					) ''')

	def create_img_source_table(self):
		self.cursor.execute(''' CREATE TABLE IF NOT EXISTS img_source (id 			INTEGER PRIMARY KEY ,
																	queryRef		INTEGER				,
																	filepath 		TEXT 				,
																	groupDesignation TEXT 				,
																	imgDominantColor TEXT 				,
																	relatedQuery 	NUMERIC 			,
																	url 			TEXT 				,
																	imgMode 		TEXT 				,
																	created_date 	INTEGER 			,
																	modified_date 	INTEGER	 				) ''')

	def execute(self, query_fstring):
		return self.cursor.execute(query_fstring)

	def init(self):
		self.create_query_table()
		self.create_img_source_table()

	def sample_res(self):
		return self.cursor.execute(""" SELECT response FROM query WHERE id == 1 """).fetchone()[0]

	def commit(self):
		self.connection.commit()

	def close(self):
		self.connection.close()

	def __exit__(self, ext_type, exc_value, traceback):
		self.cursor.close()
		if isinstance(exc_value, Exception):
			self.connection.rollback()
		else:
			self.connection.commit()
		self.connection.close()


## must replace instances of ' with '' because otherwise it messes with sqlite insert
## I was thinking about making this a method of the class, but I decided against it
def dict_to_str(dictionary):
	import json
	return json.dumps(dictionary).replace("'","''")

## put the string the way it was before you dumped it and load it back into a dict
def str_to_dict(string):
	import json
	return json.loads(string.replace("''","'"))

def url_to_filepath(url):
	import os
	filename = os.path.splitext(url.split('/')[-1])[0]+IMG_DEFAULT_EXT
	filepath = os.path.join(DEFAULT_SAVE_PATH, filename)
	return filepath


def save_res_to_db(res):

	res_text 		= 	dict_to_str(res)
	query_string 	= 	f''' INSERT INTO query (response) VALUES ('{res_text}'); '''
	row_id 			= 	None

	with Database() as db:

		cursor_object 	= 	db.execute(query_string)
		row_id 			= 	cursor_object.lastrowid

	return row_id

if False:

	row_id_res = save_res_to_db(res)
	res['query_row_id']=row_id_res	


## This needs to be rewritten for django
## There is no need save anything in a db unless it's in django
def save_item_to_db(res,item, path = DEFAULT_SAVE_PATH):
	url 				= item['link']
	filepath 			= url_to_filepath(url)
	groupDesignation 	= res['queries']['request'][0]['searchTerms']
	relatedQuery 		= res['queries']['request'][0]['searchTerms']	
	
	if 'query_row_id' in res:
		queryRef 		= res['query_row_id']
	else:
		queryRef 		= None

	img_orig = img_fh_from_url(url)	
	
	if img_orig != None:

		imgMode = img_orig.mode
		
		if imgMode == 'RGB': 
			
			img_crop = img_crop_center(img_orig)
			img_resized = img_resize_to_def_save_size(img_crop)
			img_final = img_save(img_resized, path) #, filepath = None)

			query_string = f''' INSERT INTO img_source 
								(   filepath  ,  queryRef   ,  url   ,   groupDesignation  ,  relatedQuery   ,  imgMode    ) 
								VALUES 
								( '{filepath}', '{queryRef}', '{url}', '{groupDesignation}', '{relatedQuery}', '{imgMode}' ); '''

			row_id = None

			try:
				with Database() as db:
					cursor_object = db.execute(query_string)
					row_id = cursor_object.lastrowid
				
				return row_id

			except sqlite.OperationalError as err:
				print ("There was a problem saving the image to the db:")
				print(err)

		else: 
			print ("The image mode was not RGB")

	else:
		print ("There was a problem reading the image from the URL")

if False:
	
	row_id_item = save_item_to_db(res,res['items'][0])



if __name__ == "__main__":

	#pass

	## Reached my daily limit, but I have 86-ish images I 
	## can use to start messing around with the image matching algorthm
	
	with Database() as db:
		db.init()

	## Uncomment the below to test function without making an api call everytime.		
		#res = db.sample_res()
		#res = str_to_dict(res)
	#res_list=[res]

	query_list = ["Lijiang"]

	for query in query_list:

		res_list = cse_iterator(	query 					,
								searchType 	= 'image'	,
								#imgDominantColor = 'yellow',
								imgSize = 'XLARGE',
								start 		= 1			,
								num 		= 10		,	)

		for res in res_list:
			row_id_res 			= 	save_res_to_db(res)
			res['query_row_id'] = 	row_id_res
			items 				= 	res['items']

			for item in items:
				save_item_to_db(res,item,os.path.join(DEFAULT_SAVE_PATH,query))

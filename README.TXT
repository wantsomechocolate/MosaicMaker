## Hi there. 
If you download this, just put all the files in the same directory and run MosaicMaker.py
I'll add an .exe later using py2exe.

## Warning
Just to be safe, you should probably not include "mosaicMakerProgData.log", but if you do
nothing bad should happen, unless you already have a "C:/Users/James McGlynn/Documents/Mosaic Maker" 
on your machine - in which case the program will store all the mosaic information there. 
I think that is unlikely, but of course not impossible, so until I implement a less lazy way of 
checking for the program directory, other James McGlynns who want to use this program should delete
the mosaicMakerProgData.log file so the program can remake it with the right information. 

## How the program works
You can either make a mosaic or add a search query to the archives. 
If you choose to add a search query, it uses the google API (You'll probably have to get your own 
cx and api key eventually) because right now I can only get 20 new queries a day (In order to 
retrive all 100 results for each query, I need to make each query 10 times). 

If you choose to make a mosaic then the first thing it does is break down the image into sections and gets
the average rgb data for each section. Then it lets you pick queries from the query log file and and
used the rgb data from the images to compare to the base image and chooses the images with the least error.

Then it generates html and css files so that you can view the mosaic without losing any image quality upon zooming in. 
There is currently no good way to print the mosaics out into a massive file for printing on massive paper that 
I know of. 

Thanks for reading the README. 
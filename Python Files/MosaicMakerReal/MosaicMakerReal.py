## How should refreshing be done? Currently the search is not rerun,
## So the links are tested for connection, but the pool of images
## will shrink over time.

## I really need to revisit the whole google api thing. 


import os
import mosaicModuleFAXP as mosaicModule    ##  My Module

## There is a bug when you try to actually pick a different name for the image you select
##  Preliminary stuff 

defaultFineness=4

mainDir=os.getcwd()                                            ##  Get directory that program is run from.

progDataLog="mosaicMakerProgData.log"                          ##  The name of the file used to store program data

imageQueryLog="savedImageQueriesF"+str(defaultFineness)+".log"

##  Find or create the program directory

progDir=mosaicModule.enterMosaic(mainDir,progDataLog)          ##  Check for log file and program directory stored inside. 
       
## Enter the program loop

mosaicModule.mosaicMakerInterface(progDir,mainDir,imageQueryLog,defaultFineness)     ##  Go to mosaicModule to see what this does. Aka everything. 

##  Exit the program

mosaicModule.exitMosaic()                                      ##  I figured I might want something useful here one day. 


import os
import mosaicModuleF3 as mosaicModule    ##  My Module

##  Preliminary stuff 

progDataLog="mosaicMakerProgData.log"                          ##  The name of the file used to store program data

imageQueryLog="savedImageQueriesF3.log"

#fineness=3

mainDir=os.getcwd()                                            ##  Get directory that program is run from.

##  Find or create the program directory

progDir=mosaicModule.enterMosaic(mainDir,progDataLog)          ##  Check for log file and program directory stored inside. 
       
## Enter the program loop

mosaicModule.mosaicMakerInterface(progDir,mainDir,imageQueryLog)     ##  Go to mosaicModule to see what this does. Aka everything. 

##  Exit the program

mosaicModule.exitMosaic()                                      ##  I figured I might want something useful here one day. 

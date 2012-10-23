import os
import mosaicModule2    ##  My Module

##  Filename

progDataLog="mosaicMakerProgData.log"

##  Preliminary stuff 

mosaicModule2.enterMosaic()                                         ##  Just prints welcome to Mosaic Maker

mainDir=os.getcwd()                                                 ##  Get directory that program is run from.

progDir=mosaicModule2.getProgramDirectory(mainDir,progDataLog)      ##  Check for log file and program directory stored inside. 
       
## Enter the program loop

mosaicModule2.mosaicMakerInterface(progDir,mainDir)                 ##  Go to mosaicModule to see what this does. Aka everything. 

##  Exit the program

mosaicModule2.exitMosaic()                                          ##  I figured I might want something useful here one day. 


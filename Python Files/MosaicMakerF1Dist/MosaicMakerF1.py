import os
import mainMenuModule as mainMenu
import bookEnds as bk

##  Preliminary stuff 

progDataLog="mosaicMakerProgData.log"                          ##  The name of the file used to store program data

imageQueryLog="savedImageQueriesF1.log"

mainDir=os.getcwd()                                            ##  Get directory that program is run from.

##  Find or create the program directory

progDir=bk.enterMosaic(mainDir,progDataLog)          ##  Check for log file and program directory stored inside. 
       
## Enter the program loop

mainMenu.mosaicMakerInterface(progDir,mainDir,imageQueryLog)     ##  Go to mosaicModule to see what this does. Aka everything. 

##  Exit the program

bk.exitMosaic()                                      ##  I figured I might want something useful here one day. 

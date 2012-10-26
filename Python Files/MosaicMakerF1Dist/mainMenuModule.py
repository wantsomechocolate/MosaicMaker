#!/usr/bin/python
# Filename: mainMenuModule.py

import ast
import os, sys
import math as op
import numbers
import urllib2
import json
import urllib, cStringIO
import Tkinter, tkFileDialog
from PIL import Image
from markup_1_8 import markup
import shutil
import time

##  This the program "shell" Everything runs from here. 
def mosaicMakerInterface(progDir, mainDir, imageQueryLog):

    print "---------------------------------------------------------------------"
    print "Choose one of the following:"
    print "[1] Make a mosaic"
    print "[2] Do a new search"
    print "[3] Print Searches"
    print "[4] Refresh"
    print "[5] Quit :("
    print "---------------------------------------------------------------------"
    
    promptString="Please make a selection.[1]"

    choice=getIntegerInput(1, 5, promptString, 1) # This goes (start, end, promptString, default)
    print "---------------------------------------------------------------------"
    
    if choice==1:
        
        print "You picked choice one"

        imageFile=getBaseImage(progDir,mainDir)

        imCopy=openImageReturnCopy(imageFile)      ##  I think this doesn't do what I want - too lazy to fix.
        newFilename=saveImageCopy(imCopy,imageFile,progDir, mainDir)
        
        width=imCopy.size[0]                                    ##  Get width of image
        height=imCopy.size[1]                                   ##  Get height of image
        pix=imCopy.load()                                       ##  Noooow we have pixel data

        percentOfPic=getPercentOfPic()             ##  How small to you want the images that make up the mosaic to be?

        pixelHeight=op.floor(height*percentOfPic)               ##  Height of each section
        pixelWidth=op.floor(width*percentOfPic)                 ##  Width of each section
        aveRgbArray=getAveRgbArray(width, height, pixelWidth, pixelHeight, pix)
        
        
        filename=imageQueryLog
        fileContents=getFileContents(filename)

        print "---------------------------------------------------------------------"
        prompt="Choose queries from list using comma separated integers. [All]"
        userSelectedQueries=getUserSelectedQueries(fileContents,prompt)
        returnedArray=getImgUrl_and_aveRgbArrayWeb_forSelection(userSelectedQueries)

        imageUrlArray=returnedArray[0]
        aveRgbArrayWeb=returnedArray[1]

        print "Entering output URL at: "+str(time.time())
        outputUrlList=getOutputUrlList(aveRgbArray, aveRgbArrayWeb, imageUrlArray)
        print "Exited output URL at: "+str(time.time())
        
        mosaicDisplayWidth=800
        cssFile='mosaicStyle.css' 

        filenameHTML=generateHTML(width,height,pixelWidth,pixelHeight,mosaicDisplayWidth,cssFile,outputUrlList,imageFile, progDir, mainDir)
   
        mosaicMakerInterface(progDir, mainDir, imageQueryLog)
        
    elif choice==2:
        
        print "You picked choice 2"
        
        imageUrlArray=getImageUrlArrayNew()
        
        aveRgbArrayWeb=getAveRgbArrayWebNew(imageUrlArray)
        
        logNewResults(imageUrlArray, aveRgbArrayWeb)
        
        mosaicMakerInterface(progDir, mainDir, imageQueryLog)

    elif choice==3:

        print "You picked choice 3"
        print "---------------------------------------------------------------------"
        filename=imageQueryLog
        fileContents=getFileContents(filename)
        prompt="Please hit enter to continue [Enter]"
        userSelectedQueries=getUserSelectedQueries(fileContents,prompt)
        
        mosaicMakerInterface(progDir, mainDir, imageQueryLog)
    
    elif choice==4:

        print "You picked choice 4"
        print "---------------------------------------------------------------------"
        
        refreshUrlImageLists()

        mosaicMakerInterface(progDir, mainDir, imageQueryLog)

    else: print "Bye!"

#!/usr/bin/python
# Filename: imageManipulation.py

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

def getBaseImage(progDir, mainDir):
    os.chdir(progDir)
    
    print "---------------------------------------------------------------------"
    print "Opening the open file dialog window"
    print "---------------------------------------------------------------------"

    root=Tkinter.Tk()                           ##  Explicitly call the root windows so that you can...
    root.withdraw()                             ##  withdraw it!
    imageFile=tkFileDialog.askopenfilename()    ##  imageFile will store the filename of the image you choose
    root.destroy()                              ##  Some overkill 

    os.chdir(mainDir)

    return imageFile                            ##  Returns a string


def saveImageCopy(imCopy, imageFile, progDir, mainDir):
    os.chdir(progDir)
    imageFilename=imageFile[imageFile.rindex('/')+1:imageFile.rindex('.')]
    imageFileExtension=imageFile[imageFile.rindex('.'):]

    print "---------------------------------------------------------------------"
    newFilename=raw_input([str("Name of copy of image to store with html:["+imageFilename+".png]")])
    print "---------------------------------------------------------------------"
    print "Checking to see if "+imageFilename+" exists."
    if newFilename=="":
        newFilename=imageFilename

    fileDir=progDir+'/'+newFilename
    try:
        os.chdir(fileDir)
    except:
        os.mkdir(fileDir)
        os.chdir(fileDir)
        print fileDir+" was created."

    fileExisted="NO"
    for item in os.listdir(os.getcwd()):
        if item[:item.rindex('.')]==newFilename:
            print "File existed - no Copy made"
            fileExisted="YES"
    if fileExisted=="NO":
        try:
            imCopy.save(newFilename+".png")
            print "Copy of "+newFilename+" was made."
        except:
            print "There was a problem copying the image."
    else: pass

    os.chdir(mainDir)
    return newFilename


def openImageReturnCopy(imageFile):
    print "---------------------------------------------------------------------"
    print "Please wait while the image data is loaded."
    print "---------------------------------------------------------------------"

    im = Image.open(imageFile)                  ##  im only has data about the file - no pixel data
    imCopy=im.copy()                            ##  Make a copy of the image so that you can't fuck anything up

    return imCopy                               ##  Returns a image object


def getAveRgbArray(width, height, pixelWidth, pixelHeight, pix):
    print "---------------------------------------------------------------------"
    print "Please wait, the image is being analyzed"
    print "---------------------------------------------------------------------"
    aveR,aveG,aveB=0,0,0        ##  I'm currently just averaging RBG to get the overall color of each section
    wCount, hCount=0,0          ##  Not really a good way of doing it, I saw dude who did the RMS - maybe I'll try that.
    r,g,b=0,1,2                 ##  The pixel data is accessed with the rgb values of 0,1,2 respectively 
    aveRgbArray=[]              ##  Initializing a list. 

    ##  This goes across the image one row at a time and does it's thing
    ##  I tell it how many times to go across by calculating the floor of the width divided by the subsection width
    
    while hCount<int(op.floor(height/pixelHeight)):         ##  I.E. image is 100px high, percentOfPic is 0.1 -> hCount will reach 10 or something
        wCount=0                                            ##  Re-initilize wCount for new row of sections
        while wCount<int(op.floor(width/pixelWidth)):       ##  Same as outer while loop, but for the width
            
            ##  For a given section this adds up all the pixel's RGB values and then averages them and puts them in a list
            
            for w in range(int(pixelWidth)):                
                for h in range(int(pixelHeight)):
                    aveR+=pix[w+pixelWidth*wCount,h+pixelHeight*hCount][r]
                    aveG+=pix[w+pixelWidth*wCount,h+pixelHeight*hCount][g]
                    aveB+=pix[w+pixelWidth*wCount,h+pixelHeight*hCount][b]
                    
            aveR=int(round(aveR/(pixelWidth*pixelHeight)))
            aveG=int(round(aveG/(pixelWidth*pixelHeight)))
            aveB=int(round(aveB/(pixelWidth*pixelHeight)))

            aveRGB=(aveR,aveG,aveB)
            aveRgbArray.append(aveRGB) 
                    
            wCount=wCount+1
            
        hCount=hCount+1

    return aveRgbArray

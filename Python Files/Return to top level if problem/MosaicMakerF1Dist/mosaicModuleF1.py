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
import mosaicModule as mm

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

def getImgUrl_and_aveRgbArrayWeb_forSelection(selection, imageQueryLog):
    imageUrlArray=[]
    aveRgbArrayWeb=[]

    logFilename=imageQueryLog
    fileContents=mm.getFileContents(logFilename)

    singleQueryImageList=[]
    singleQueryRGBList=[]

    
    for item in selection:
        for i in range(len(fileContents)):
            if fileContents[i][8:-1]==item:
                singleQueryImageList=fileContents[i+2]
                singleQueryImageList=ast.literal_eval(singleQueryImageList[:-1])
                for item in singleQueryImageList:
                    imageUrlArray.append(item)
                singleQueryRGBList=fileContents[i+4]
                singleQueryRGBList=ast.literal_eval(singleQueryRGBList[:-1])
                for item in singleQueryRGBList:
                    aveRgbArrayWeb.append(item)

    returnedArray=[]
    
    returnedArray.append(imageUrlArray)
    returnedArray.append(aveRgbArrayWeb)

    print "---------------------------------------------------------------------"
    print "You are using search queries: ",
    for i in range(len(selection)):
        if i!=len(selection)-1:
            print str(selection[i])+', ',
        else:
            print "and "+str(selection[i])+"."
    print "These searches include "+str(len(imageUrlArray))+" images."
    print "---------------------------------------------------------------------"

    return returnedArray

def getOutputUrlList(aveRgbArray, aveRgbArrayWeb, imageUrlArray):
    errorSum=0
    errorSumArray=[]
    minErrorArray=[]
    minErrorIndexArray=[]
    for section in aveRgbArray:
        errorSumArray=[]
        for imageRGB in aveRgbArrayWeb:
            errorSum=0
            error=[section[i]-imageRGB[i] for i in range(len(section))]
            for j in error:
                errorSum+=abs(j)
            errorSumArray.append(errorSum)

        minError=min(errorSumArray)
        minErrorArray.append(minError)

        minErrorIndex=errorSumArray.index(minError)
        minErrorIndexArray.append(minErrorIndex)

    outputUrlList=[]
    for item in minErrorIndexArray:
        outputUrlList.append(imageUrlArray[item])

    return outputUrlList


def getAveRgbArrayWebNew(imageUrlArray):

    print "---------------------------------------------------------------------"
    print "Please wait while the URLs are tested"
    print "---------------------------------------------------------------------"

    aveR,aveG,aveB=0,0,0                        ##  I'm currently just averaging RBG to get the overall color of each section
    wCount, hCount=0,0                          ##  Not really a good way of doing it.
    r,g,b=0,1,2

    aveRgbArrayWeb=[]  

    for item in imageUrlArray:
        try:
            #print "trying"
            filename=cStringIO.StringIO(urllib.urlopen(item).read())
            img=Image.open(filename)

            if img.mode!="RGB":
                nonRGB=(-501,-501,-501)
                aveRgbArrayWeb.append(nonRGB)
                print "The image was not RGB"

            else:
                webWidth=img.size[0]
                webHeight=img.size[1]    

                pixels=img.load()

                for w in range(int(webWidth)):                
                    for h in range(int(webHeight)):
                        aveR+=pixels[w,h][r]
                        aveG+=pixels[w,h][g]
                        aveB+=pixels[w,h][b]
                        
                aveR=int(round(aveR/(webWidth*webHeight)))
                aveG=int(round(aveG/(webWidth*webHeight)))
                aveB=int(round(aveB/(webWidth*webHeight)))

                aveRGBWeb=(aveR,aveG,aveB)
                aveRgbArrayWeb.append(aveRGBWeb)

                print "File Loaded Successfully"

        ## This is so no image that doesn't load will be chosen as a match. But the index of the image url isn't thrown off. 
        except:
            print "File did not Load Successfully"
            defaultRGB=(-500,-500,-500)
            aveRgbArrayWeb.append(defaultRGB)

    return aveRgbArrayWeb

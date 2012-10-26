#!/usr/bin/python
# Filename: makeHTML.py

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

def generateHTML(width,height,pixelWidth, pixelHeight, mosaicDisplayWidth,cssFile,outputUrlList,imageFile,progDir,mainDir):

    ##  This makes the html for me and I can set inline css with the style attribute

    ##  Eventually the image height and width will be determined other ways
    mosaicDisplayWidth=800
    numberOfPics=width/pixelWidth

    aspectRatio=float(width)/float(height)

    imageWidthWeb=mosaicDisplayWidth/numberOfPics
    imageHeightWeb=int(op.floor(imageWidthWeb/aspectRatio))


    ##  This will also be determined a different way. 
    imagesPerRow=numberOfPics
    imagesPerColumn=numberOfPics

    ##  The plus 30 is for 15px of padding on both sides of the mosaic
    imageContainerWidth=mosaicDisplayWidth+30
    imageContainerHeight=int(op.ceil((imageContainerWidth/aspectRatio)+30))

    ##  I'll get this working later
    searchTerm=""
    altText=searchTerm

    ##  Just some header type stuff
    paras = ( "Here is your mosaic!" )

    ##  Initialize the page
    page = markup.page( )

    page.init( title="Mosaic Maker", 
               css=( cssFile),)

    ##  Make a header
    page.div(Class='header', style='width:'+str(imageContainerWidth))
    page.p( paras )
    page.div.close()

    ##  Make a div with all the images floating inside
    page.div(Class = 'imageContainer', style='width:'+str(imageContainerWidth)+'; height:'+str(imageContainerHeight))
    page.img( src=outputUrlList, height=imageHeightWeb, width=imageWidthWeb, alt=searchTerm )
    page.div.close()

    ##  Print html to an actual file so it can be viewed

    imageFilename=imageFile[imageFile.rindex('/')+1:imageFile.rindex('.')]
    
    print "---------------------------------------------------------------------"
    destFileHTML=raw_input([str("Destination File for HTML Output?["+imageFilename+" Mosaic F1 HTML.html]")])
    print "---------------------------------------------------------------------"

    if destFileHTML=="":
        destFileHTML=imageFilename+" Mosaic F1 HTML.html"


    os.chdir(progDir+'/'+imageFilename)
       
    output=open(destFileHTML,'w')
    output.write(str(page))
    output.close()
    print "---------------------------------------------------------------------"
    print "The page "+destFileHTML+" was created"
    print "---------------------------------------------------------------------"

    cssFilename=createCSS()

    os.chdir(mainDir)

    return destFileHTML

def createCSS():
    cssFilename="mosaicStyle.css"
    mosaicStyle=open(cssFilename,'w')
    mosaicStyle.write(
        
    """* {box-sizing:border-box;}\n
    body {\n
        background:black;\n
        color:white;\n
    }\n
    .header {\n
        border:2p solid black;\n
        background:orange;\n
        width:800px;\n
        margin:0 auto;\n
    }\n
    .imageContainer {\n
        overflor:hidden;\n
        border:2p solid black;\n
        background:orange;\n
        margin:0 auto;\n
        padding:15px;\n
    }\n
    img {\n
        float:left;\n
        padding:0px;\n
        margin:0px;\n
    }\n""")
    
    mosaicStyle.close()
    return cssFilename

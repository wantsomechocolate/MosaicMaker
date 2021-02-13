#!/usr/bin/python
# Filename: mosaicModule.py

## This file contains all the code - I think I might break it into smaller peices

##  All the imports that the file needs. Probably better to put only the ones required inside
##  of each function, right?
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

import mosaicModuleF1 as F1

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
        aveRgbArray=F1.getAveRgbArray(width, height, pixelWidth, pixelHeight, pix)
        
        
        filename=imageQueryLog
        fileContents=getFileContents(filename)

        print "---------------------------------------------------------------------"
        prompt="Choose queries from list using comma separated integers. [All]"
        userSelectedQueries=getUserSelectedQueries(fileContents,prompt)
        returnedArray=F1.getImgUrl_and_aveRgbArrayWeb_forSelection(userSelectedQueries, imageQueryLog)

        imageUrlArray=returnedArray[0]
        aveRgbArrayWeb=returnedArray[1]

        print "Entering output URL"
        entTime=time.time()
        outputUrlList=F1.getOutputUrlList(aveRgbArray, aveRgbArrayWeb, imageUrlArray)
        exiTime=time.time()
        print "Exited output URL"
        diff=exiTime-entTime
        minutes=op.floor(diff/60)
        seconds=diff-minutes*60
        print "That took "+str(minutes)+" minutes and "+str(seconds)+" seconds!"
        
        mosaicDisplayWidth=800
        cssFile='mosaicStyle.css' 

        filenameHTML=generateHTML(width,height,pixelWidth,pixelHeight,mosaicDisplayWidth,cssFile,outputUrlList,imageFile, progDir, mainDir)
   
        mosaicMakerInterface(progDir, mainDir, imageQueryLog)
        
    elif choice==2:
        
        print "You picked choice 2"
        
        imageUrlArray=getImageUrlArrayNew(imageQueryLog)
        
        aveRgbArrayWeb=F1.getAveRgbArrayWebNew(imageUrlArray)
        
        logNewResults(imageUrlArray, aveRgbArrayWeb, imageQueryLog)
        
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
        
        refreshUrlImageLists(imageQueryLog)

        mosaicMakerInterface(progDir, mainDir, imageQueryLog)

    else: print "Bye!"


##  Perhaps this will be useful some day 
def enterMosaic(mainDir, progDataLog):
    print "-------------------------------------------------------------------"
    print "-----------------Welcome to Mosaic Maker---------------------------"
    print "-------------------------------------------------------------------"
    
    progDir=getProgramDirectory(mainDir,progDataLog)

    return progDir

    

#The directory that the program was run from is gathered from the main program and passed to this
#function. It checks to see if it can find mosaicMakerProgData.log and if that the log file contains
#a valid directory that contains the "program directory" or where the user is storing the mosaics
#If it finds a directory in the log file it returns that, if not it asks the user to navigate to a
#directory and then adds "Mosaic Maker" to it and then returns that. 
def getProgramDirectory(mainDir,progDataLog):
    try:
        print "Checking to see if "+progDataLog+" exists."
        progData=open(progDataLog,'r')
        fileContents=[]
        for item in progData:
            fileContents.append(item)
        for i in range(len(fileContents)):
            if fileContents[i][:-1]=="Program Directory":
                progDir=fileContents[i+1]
                print "Retrieved program directory: "+progDir+" from "+progDataLog+"."
                print "Checking to see that directory exists."
                os.chdir(progDir)
                os.chdir(mainDir)
        progData.close()
        print "Program startup was successful."

    except:
        print "You are either running this program for the first time or you did something it didn't like"
        print "Please navigate to the directory you would like Mosaic Maker to save to."
        print "If this directory exists already, just navigate to it's parent directory and press OK."
        
        root=Tkinter.Tk()                           ##  Explicitly call the root window so that you can...
        root.withdraw()                             ##  withdraw it!
        baseDirectory=tkFileDialog.askdirectory()   ##  imageFile will store the filename of the image you choose
        root.destroy()                              ##  Some overkill

        progDir=baseDirectory+'/'+"Mosaic Maker"

        print "Creating/Rewriting "+progDataLog+"."
        progData=open(progDataLog,'w')
        progData.write("Program Directory")
        progData.write("\n")
        progData.write(progDir)
        progData.close()

        print "Creating/Locating "+progDir+"."

        try:
            os.mkdir(progDir)
            os.chdir(progDir)
            readMe=open("README.TXT",'w')
            readMe.write("YOU READ ME!")
            readMe.close()
        except:
            os.chdir(progDir)

        os.chdir(mainDir)
        
        print "Program startup was successful."

    print "-------------------------------------------------------------------"
    return progDir


def getIntegerInput(start, end, promptString, default):

    flag="BAD"
    while flag=="BAD":

        userSelection=raw_input([promptString])

        if userSelection=="":
            userSelection=default

        try:
            userSelection=int(userSelection)
            if userSelection<start:
                print "Option Doesn't Exist."
            elif userSelection>end:
                print "Option Doesn't Exist."
            else:
                flag="GOOD"
            
        except:
            print "Please enter an integer."

    return userSelection

def getFileContents(filename):
    fileHandle=open(filename,'r')
    fileContents=[]
    for item in fileHandle:
        fileContents.append(item)
    fileHandle.close()
    return fileContents


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


def getPercentOfPic():
    start=1
    end=5
    promptString="Percent of original size for mosaic images(1-5): (Percent)[2%]"
    default=2
    print "---------------------------------------------------------------------"
    choice=getIntegerInput(start,end,promptString,default)
    print "---------------------------------------------------------------------"
    percentOfPic=choice/100.0
    return percentOfPic                         ##  Returns a float

def getUserSelectedQueries(fileContents, prompt):
    listOfQueries=[]
    for item in fileContents:
        if item[:7]=="Search:":
            listOfQueries.append(item[8:-1])

    print '0: All Items'
    for i in range(len(listOfQueries)):
        print str(i+1)+": ",
        print listOfQueries[i]

    print "---------------------------------------------------------------------"
    ##  There is no error checking here. 
    querySelection=raw_input([prompt])
    if querySelection=='':
        querySelection='0'
    querySelection=ast.literal_eval(querySelection)

    if querySelection==0:
        querySelection=[]
        for i in range(len(listOfQueries)):
            querySelection.append(i+1)

    userSelectedQueries=[]
    try:
        for item in querySelection:
            userSelectedQueries.append(listOfQueries[item-1])
    except:
        userSelectedQueries.append(listOfQueries[querySelection-1])

    return userSelectedQueries


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


def getImageUrlArrayNew(imageQueryLog):

    ##  Below uses a custom CSE and the google API to retrieve search results
    ##  It is limited to 100 queries a day and 100 results per query 

    MY_API_KEY="AIzaSyD1UeuzDXdKGgcoqH4385D4SF8c2HF8LkY"        ##  This is my personal key for my API
    MY_API_KEY_2="AIzaSyDHprCKraIGVmXnBhuHTPJ8DaWo6hCi9Os"        ## A different one
    SEARCH_ENGINE="010404009348550142839:mz7ovp-utrg"           ##  This is my personal code for my CSE (custom search engine)
    searchType="image"                                          ##  A critera for the urlopen call to limit search to images
    SEARCH_URL="https://www.googleapis.com/customsearch/v1"     ##  I made this a string just to make the code more readable?

    print "---------------------------------------------------------------------"
    searchQuery=raw_input(["What would you like your image query to be?"])
    print "---------------------------------------------------------------------"

    if searchQuery=="":
        searchQuery='mylittlepony'

    logFile=open(imageQueryLog,'a')
    logFile.write('\n')
    logFile.write("Search: "+searchQuery)
    logFile.write('\n')
    logFile.close()

    searchQuery=''.join(searchQuery.strip(' ').split(' '))

##    print "---------------------------------------------------------------------"
##    imgColorType=raw_input(["The default color type is 'color'. Others will become available."])
##    print "---------------------------------------------------------------------"

    imgColorType='color'

    numberOfResults=100


    print "---------------------------------------------------------------------"
    print "Please wait while the images are retrieved."
    print "---------------------------------------------------------------------"

    startIndex=1
    imageUrlArray=[]                    ##  This will hold all the URLs for me

    while startIndex<int(numberOfResults):

        try:
            ##  I got this line straight off the internet - and then made all the strings into variables and put my own stuff in. 
            data = urllib2.urlopen(SEARCH_URL+'?'+'key='+MY_API_KEY+'&'+'cx='+SEARCH_ENGINE+'&'+'q='+searchQuery+'&'+'searchType='+searchType+'&start='+str(startIndex)+'&'+'imgColorType='+imgColorType)

        except:
            data = urllib2.urlopen(SEARCH_URL+'?'+'key='+MY_API_KEY_2+'&'+'cx='+SEARCH_ENGINE+'&'+'q='+searchQuery+'&'+'searchType='+searchType+'&start='+str(startIndex)+'&'+'imgColorType='+imgColorType)

        data = json.load(data)

        ##  Manoj's Code - much better. 20 lines became 3

        for item in data["items"]:
                imageUrlArray.append(item["link"])

        startIndex=startIndex+10

    print "---------------------------------------------------------------------"
    print "The image Urls have been collected"
    print "---------------------------------------------------------------------"

    return imageUrlArray


def logNewResults(imageUrlArray,aveRgbArrayWeb, imageQueryLog):

    savedImageFilename=imageQueryLog
    siv=savedImageFilename
    sivTemp=siv[:siv.index('.')]+'Temp'+siv[siv.rindex('.'):]
    
    shutil.copyfile(siv,sivTemp)
    
    logFile=open(siv,'a')
    
    logFile.write("imageUrlArray:")
    logFile.write("\n")
    logFile.write(str(imageUrlArray))
    logFile.write("\n")

    logFile.write("aveRgbArrayWeb:")
    logFile.write("\n")
    logFile.write(str(aveRgbArrayWeb))
    logFile.write("\n")
    
    logFile.close()

    os.remove(sivTemp)

    print "Your new search has been added to "+savedImageFilename+"."


def refreshUrlImageLists(imageQueryLog):

    savedImageFile=imageQueryLog
    siv=savedImageFile
    sivTemp=siv[:siv.index('.')]+'Test'+siv[siv.rindex('.'):]

    fileContents=getFileContents(siv)

    listOfQueries=[]
    
    tempFile=open(sivTemp,'w')

    tempFile.write(fileContents[0])
    tempFile.write(fileContents[1])
    tempFile.write(fileContents[2])
    tempFile.write(fileContents[3])
    #tempFile.write(fileContents[4])

    aveRgbArrayWebRefresh=[]
    
    for i in range(4,len(fileContents)):
        if fileContents[i-4][:7]=="Search:":
            print "---------------------------------------------------------------------"
            print "Refreshing the image list for "+fileContents[i-4][8:-1]
            aveRgbArrayWebRefresh=F1.getAveRgbArrayWebNew(ast.literal_eval(fileContents[i-2][:-1]))
            tempFile.write(str(aveRgbArrayWebRefresh))
            tempFile.write('\n')
            
        else:
            tempFile.write(fileContents[i])

    tempFile.close()

    shutil.copyfile(sivTemp,siv)
    os.remove(sivTemp)
    
    
def exitMosaic():
    print "---------------------------------------------------------------------"
    print "You have exited the program successfully"
    print "---------------------------------------------------------------------"

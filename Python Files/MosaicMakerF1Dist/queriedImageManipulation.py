#!/usr/bin/python
# Filename: queriedImageManipulation.py

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

def getImgUrl_and_aveRgbArrayWeb_forSelection(selection):
    imageUrlArray=[]
    aveRgbArrayWeb=[]

    logFilename="savedImageQueriesF1.log"
    fileContents=getFileContents(logFilename)

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




def getImageUrlArrayNew():

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

    logFile=open('savedImageQueriesF1.log','a')
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


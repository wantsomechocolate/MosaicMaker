#!/usr/bin/python
# Filename: fileManipulation.py

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

def refreshUrlImageLists():

    savedImageFile='savedImageQueriesF1.log'
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
            aveRgbArrayWebRefresh=getAveRgbArrayWebNew(ast.literal_eval(fileContents[i-2][:-1]))
            tempFile.write(str(aveRgbArrayWebRefresh))
            tempFile.write('\n')
            
        else:
            tempFile.write(fileContents[i])

    tempFile.close()

    shutil.copyfile(sivTemp,siv)
    os.remove(sivTemp)

def logNewResults(imageUrlArray,aveRgbArrayWeb):

    savedImageFilename='savedImageQueriesF1.log'
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

def getFileContents(filename):
    fileHandle=open(filename,'r')
    fileContents=[]
    for item in fileHandle:
        fileContents.append(item)
    fileHandle.close()
    return fileContents

#!/usr/bin/python
# Filename: bookEnds.py

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

def exitMosaic():
    print "---------------------------------------------------------------------"
    print "You have exited the program successfully"
    print "---------------------------------------------------------------------"

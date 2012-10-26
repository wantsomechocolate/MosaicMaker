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



## Packages shipped with python3
import os, sys
import ast, numbers, math
import tkinter
import json, urllib, io, urllib.request
import shutil, time, random

## Using numpy 1.8.0
import numpy as np

## Using Pillow 2.3.0
from PIL import Image

## Using Markup 1.9. It was not installed with pip, just pasted into the site-packages dir in venv
from markup_1_9 import markup   ## ***From http://markup.sourceforge.net/

## This is some code I had as a global site-package on an old machine containing stuff I used often. 
from marbles import glass as chan

#from tkinter.filedialog import askdirectory
#from urllib import request

##  This is the program "shell" Everything runs from here. 
def mosaicMakerInterface(progDir, mainDir, imageQueryLog, fineness):

    # This blob of text should be somewhere else!
    print ("    -----------           MAIN MENU              -------------")
    print ("--------------------------------------------------------------------------------------")
    print ("    -----------   Choose one of the following:   -------------")
    print ("    -----------     [1] Make a mosaic            -------------")
    print ("    -----------     [2] Do a new search          -------------")
    print ("    -----------     [3] Print Searches           -------------")
    print ("    -----------     [4] Refresh                  -------------")
    print ("    -----------     [5] Change Fineness ["+str(fineness)+"]      -------------")
    print ("    -----------     [6] Quit :(                  -------------")
    print ("--------------------------------------------------------------------------------------")
    
    promptString="    ----    Please make a selection[1]    "

    # This goes (start, end, promptString, default)
    choice=getIntegerInput(1, 6, promptString, 1)
    print ("---------------------------------------------------------------------")

    #To make a mosaic
    if choice==1:
        
        print ("You picked choice one")  

        # Use askopenfile dialog to get base image. Changes to the directory where mosaics are
        # stored invokes the dialog, then changes back to directory the program was run from.
        imageFile=getBaseImage(progDir,mainDir)     

        # Opens the image @imageFile, calls .copy() on it and then returns the image object for the copy.
        # Not sure if that creates a legit copy, but it works for now.
        imCopy=openImageReturnCopy(imageFile)       

        # Every new image gets stored in a new directory, checks to see if the directory already exists with the
        # picture inside it and creates the structure and saves a copy of the image if not.
        newFilename=saveImageCopy(imCopy,imageFile,progDir, mainDir)

        # I like png
        newFilenameWithExt=newFilename+'.png'

        ##  Get width of image
        width=imCopy.size[0]

        ##  Get height of image
        height=imCopy.size[1]

        ##  Noooow we have pixel data
        pix=imCopy.load()                                       

        ##  How small do you want the images that make up the mosaic to be?
        ##  If I want squares and the user picks 10%, then it has to be at least 10%, so
        ##  basically accross the shorter dimension determines the size of each square.
        ## This function just lets the user pick a number from 1-5.
        percentOfPic=getPercentOfPic()             

        ## if aspect ratio < 1
        if width<=height:

            ## Calculate dimensions based on width (shorter dimension)
            pixelWidth=math.floor(width*percentOfPic)
            pixelHeight=pixelWidth
        else:
            ## Calc dimensions based on height (shorter dimension)
            pixelHeight=math.floor(width*percentOfPic)
            pixelWidth=pixelHeight

        ## Currently this returns a single dimension list with the results of the rgb analysis
        ## of the base image at each index. I should change this to return a 2 dimension array to
        ## better represent the image. Maybe.
        aveRgbArray=getAveRgbArray(width, height, pixelWidth, pixelHeight, pix, fineness)

        ## imageQueryLog is chosen depending on the fineness (F2 has a different cache of images than F3, etc)
        filename=imageQueryLog

        ## this just goes through imageQueryLog and returns all the link and rgb info for each web-image
        fileContents=getFileContents(filename)

        print ("---------------------------------------------------------------------")
        prompt="Choose queries from list using comma separated integers. [All]"

        ## Present the choices to the user for selection using raw_input
        userSelectedQueries=getUserSelectedQueries(fileContents,prompt)

        ## What a function name! returns a list of two lists, one containing all the image links
        ## and the other the corresponding results of analsysis for each one.
        returnedArray=getImgUrl_and_aveRgbArrayWeb_forSelection(userSelectedQueries, imageQueryLog)

        ## Unpack
        imageUrlArray, aveRgbArrayWeb = returnedArray

        ## Timekeeping
        print ("Entering output URL")
        entTime=time.time()

        ## This takes the results of analyzing the base image, the results of analyzing the web images
        ## and generates a list of URLs to be used in the final product.
        ## This recently got some work done to it to randomize the selection process
        ## It will soon get some more work done to refine that randomization and to save the data
        ## for the 5 closet web-image matches for each spot so that upon mosaic creation,
        ## if certain images aren't loading, there are backups, or if an image is being chosen too many times.
    #----------------------------------------------------------------------------------------------
        outputUrlList=getOutputUrlList(aveRgbArray, aveRgbArrayWeb, imageUrlArray,fineness)
    #----------------------------------------------------------------------------------------------

        print ("Looking through images to find best matches for image section")

        ## Get all the uniques, usually a surprisingly low number (<100, although I have seen >200)
        outputUrlSet = set(outputUrlList)
        
        print ("There are "+str(len(outputUrlSet))+" unique images in this mosaic")
        print ("Filling "+str(int(height/pixelHeight)*int(width/pixelWidth))+" possible spots")

        ## time keeping
        exiTime=time.time()
        print ("Exited output URL")
        diff=exiTime-entTime
        minutes=math.floor(diff/60)
        seconds=int(diff-minutes*60)
        print ("That took "+str(minutes)+" minutes and "+str(seconds)+" seconds!")
        
        mosaicDisplayWidth=800
        cssFile='mosaicStyle.css' 
        jsFile='mosaicScript.js'

        filenameHTML=generateHTML(width,height,pixelWidth,pixelHeight,mosaicDisplayWidth,cssFile,outputUrlList,newFilename, progDir, mainDir,fineness,jsFile)
   
        mosaicMakerInterface(progDir, mainDir, imageQueryLog, fineness)
        
    elif choice==2:  # To do a new search
        
        print ("You picked choice 2")
        
        imageUrlArray=getImageUrlArrayNew(imageQueryLog)
        
        aveRgbArrayWeb=getAveRgbArrayWebNew(imageUrlArray, fineness)
        
        logNewResults(imageUrlArray, aveRgbArrayWeb, imageQueryLog)
        
        mosaicMakerInterface(progDir, mainDir, imageQueryLog, fineness)

    elif choice==3:  #To print the possible searches to select

        print ("You picked choice 3")
        print ("---------------------------------------------------------------------")
        filename=imageQueryLog
        fileContents=getFileContents(filename)
        prompt=("Please hit enter to continue [Enter]")
        userSelectedQueries=getUserSelectedQueries(fileContents,prompt)
        
        mosaicMakerInterface(progDir, mainDir, imageQueryLog, fineness)
    
    elif choice==4:  #To refresh the links and get rid of any bad ones from the possible selection pool

        print ("You picked choice 4")
        print ("---------------------------------------------------------------------")
        
        refreshUrlImageLists(imageQueryLog,fineness)

        mosaicMakerInterface(progDir, mainDir, imageQueryLog, fineness)

    elif choice==5:  # To change the fineness
        print ("You picked choice 5")
        print ("--------------------------------------------------------------------------------------")
        prompt= ("Pick a fineness ["+str(fineness)+"]")
        fineness=getIntegerInput(1,4,prompt,2)
        imageQueryLog=("savedImageQueriesF"+str(fineness)+".log")

        mosaicMakerInterface(progDir, mainDir, imageQueryLog, fineness)

    else: print ("Bye!")  # This is obviously if you pick option 6. It exits this function and goes back to the main script and exits. 


##  Perhaps this will be useful some day 
def enterMosaic(mainDir, progDataLog):
    print ("--------------------------------------------------------------------------------------")
    print ("    ----------------------    WELCOME TO MOSAIC MAKER    -------------------------")
    print ("--------------------------------------------------------------------------------------")
    
    progDir=getProgramDirectory(mainDir,progDataLog)

    return progDir

    

#The directory that the program was run from is gathered from the main program and passed to this
#function. It checks to see if it can find mosaicMakerProgData.log and if that the log file contains
#a valid directory that contains the "program directory" or where the user is storing the mosaics
#If it finds a directory in the log file it returns that, if not it asks the user to navigate to a
#directory and then adds "Mosaic Maker" to it and then returns that. 
def getProgramDirectory(mainDir,progDataLog):
    try:
        print ("    ----    Checking to see if "+progDataLog+" exists    ----")
        print ("  -----------------------------------------------------------------")
        progData=open(progDataLog,'r')
        fileContents=[]
        for item in progData:
            fileContents.append(item)
        for i in range(len(fileContents)):
            if fileContents[i][:-1]=="Program Directory":
                progDir=fileContents[i+1]
                print ("    ----    Retrieved program directory:")
                print ('            "'+progDir+'"')
                print ("            from "+progDataLog+"    ----")
                print ("  ---------------------------------------------------------------")
                print ("    ----    Checking to see that the directory exists    ----")
                print ("  ---------------------------------------------------------------")
                os.chdir(progDir)
                os.chdir(mainDir)
        progData.close()
        print ("    ----    Program startup was successful    ----")

    except:
        print ("You are either running this program for the first time or you did something it didn't like")
        print ("Please navigate to the directory you would like Mosaic Maker to save to.")
        print ("If this directory exists already, just navigate to it's parent directory and press OK.")
        
        root=tkinter.Tk()                           ##  Explicitly call the root window so that you can...
        root.withdraw()                             ##  withdraw it!

        #baseDirectory=tkFileDialog.askdirectory(focus=True)   ##  imageFile will store the filename of the image you choose
        baseDirectory=tkinter.filedialog.askdirectory()#focus=True)   ##  imageFile will store the filename of the image you choose
        root.destroy()                              ##  Some overkill

        progDir=baseDirectory+'/'+"Mosaic Maker"

        print ("Creating/Rewriting "+progDataLog+".")
        progData=open(progDataLog,'w')
        progData.write("Program Directory")
        progData.write("\n")
        progData.write(progDir)
        progData.close()

        print ("Creating/Locating "+progDir+".")

        try:
            os.mkdir(progDir)
            os.chdir(progDir)
            readMe=open("README.TXT",'w')
            readMe.write("YOU READ ME!")
            readMe.close()
        except:
            os.chdir(progDir)

        os.chdir(mainDir)
        
        print ("    ----    Program startup was successful    ----")

    print ("  ---------------------------------------------------------------")
    return progDir


def getIntegerInput(start, end, promptString, default):

    flag="BAD"
    while flag=="BAD":

        userSelection=input(promptString)

        if userSelection=="":
            userSelection=default

        try:
            userSelection=int(userSelection)
            if userSelection<start:
                print ("Option Doesn't Exist.")
            elif userSelection>end:
                print ("Option Doesn't Exist.")
            else:
                flag="GOOD"
            
        except:
            print ("Please enter an integer.")

    return userSelection

def getFileContents(filename):
    fileHandle=open(filename,'r')
    fileContents=[]
    for item in fileHandle:
        fileContents.append(item)
    fileHandle.close()
    return fileContents


def getBaseImage(progDir, mainDir):

    # Operate inside the program directory - the directory where the mosaics are saved.
    os.chdir(progDir)
    
    print ("---------------------------------------------------------------------")
    print ("Opening the open file dialog window")
    print ("---------------------------------------------------------------------")

    ##  Explicitly call the root windows so that you can...
    root=tkinter.Tk()
    ##  withdraw it!
    root.withdraw()
    ##  imageFile will store the filename of the image you choose
    imageFile=tkinter.filedialog.askopenfilename()
    ##  Search and
    root.destroy()                              

    ## Change the directory back to the directory that the program was run from.
    os.chdir(mainDir)
    
    ##  Returns a string
    return imageFile                            

## imCopy is an image object, imageFile is the name of the original, fullpath)
def saveImageCopy(imCopy, imageFile, progDir, mainDir):
    os.chdir(progDir)

    # Get JUST the filename without extension
    imageFilename=os.path.basename(imageFile)
    imageFilename=imageFilename[:imageFilename.rindex('.')]
    #imageFilename=imageFile[imageFile.rindex('/')+1:imageFile.rindex('.')]

    # Get JUST the extension
    imageFileExtension=imageFile[imageFile.rindex('.'):]

    
    print ("---------------------------------------------------------------------")
    newFilename=input([str("Name of copy of image to store with html:["+imageFilename+".png]")])
    print ("---------------------------------------------------------------------")
    
    if newFilename=="":
        newFilename=imageFilename

    print ("Checking to see if "+newFilename+" exists.")

    fileDir=progDir+'/'+newFilename
    try:
        os.chdir(fileDir)
    except:
        os.mkdir(fileDir)
        os.chdir(fileDir)
        print (fileDir+" was created.")

    fileExisted="NO"
    for item in os.listdir(os.getcwd()):
        if item[:item.rindex('.')]==newFilename:
            print ("File existed - no Copy made")
            fileExisted="YES"
    if fileExisted=="NO":
        try:
            imCopy.save(newFilename+".png")
            print ("Copy of "+newFilename+" was made.")
        except:
            print ("There was a problem copying the image.")
    else: pass

    os.chdir(mainDir)
    return newFilename


def openImageReturnCopy(imageFile):
    print ("---------------------------------------------------------------------")
    print ("Please wait while the image data is loaded.")
    print ("---------------------------------------------------------------------")

    ##  im only has data about the file - no pixel data
    im = Image.open(imageFile)

    ##  Make a copy of the image so that you can't mess anything up
    imCopy=im.copy()                            

    ##  Returns an image object
    return imCopy                               


def getAveRgbArray(width, height, pixelWidth, pixelHeight, pix, fineness):
    print ("---------------------------------------------------------------------")
    print ("Please wait, the image is being analyzed")
    print ("---------------------------------------------------------------------")

    ##  I'm currently just averaging RBG to get the overall color of each section
    ##  Not really a good way of doing it, I saw a dude who did the RMS - maybe I'll try that.

    ## Initializing
    aveR,aveG,aveB=0,0,0

    ##  The pixel data is accessed with the rgb values of 0,1,2 respectively 
    r,g,b=0,1,2

    ##  Initializing a list. 
    aveRgbArray=[]              

    ## Fineness is how much do I look at the distribution of color within each sub image. F=1 means that RGB for the whole
    ## square is calculated and the best match is found based on that. For example, a half red/ half green square would match
    ## perfectly well with an image that had half green/ half red (switched places), where as F2,F3,F4 that would not happen.
    ## Color distribution within each sub image is looked at, although it obviously takes longer. Still F1 is the first case I
    ## coded because it is the easiest thing to implement. 
    if fineness==1:

        # These counts represent columns and rows (respectively) of the sub image spaces. 
        wCount, hCount=0,0          

        # height/pixelHeight will give the amount of sub image spaces needed for each column (aka the number of rows)
        while hCount<int(math.floor(height/pixelHeight)):

            ##  Re-initilize wCount for new row of sections
            wCount=0

            # width/pixelWidth will give number of sub image spaces in each row (aka the number of columns)
            while wCount<int(math.floor(width/pixelWidth)):     
                
                ##  For a given section this adds up all the pixel's RGB values and then averages them and puts them in a list

                ## for x coordinate for a pixel in pixelWidth
                for w in range(int(pixelWidth)):
                    ## for y coordinate for a pixel in pixelHeight
                    for h in range(int(pixelHeight)):

                        ## Get the RGB for the exact place on the image. This requires knowing what sub-image space you are
                        ## in and also where in that sub image space you are. 
                        aveR+=pix[w+pixelWidth*wCount,h+pixelHeight*hCount][r]
                        aveG+=pix[w+pixelWidth*wCount,h+pixelHeight*hCount][g]
                        aveB+=pix[w+pixelWidth*wCount,h+pixelHeight*hCount][b]

                ## After going through each pixel in a sub image space, divide the sum of R,G,B by the total pixels
                ## I wrote this when I was using rectangular sub image spaces. (not forcing square AR) 
                aveR=int(round(aveR/(pixelWidth*pixelHeight)))
                aveG=int(round(aveG/(pixelWidth*pixelHeight)))
                aveB=int(round(aveB/(pixelWidth*pixelHeight)))

                ## Average RGB for a given sub image space
                aveRGB=(aveR,aveG,aveB)

                ## Add it to the list that describes the entire image.
                aveRgbArray.append(aveRGB) 

                # new column        
                wCount=wCount+1

            # new row
            hCount=hCount+1



    ## If the fineness is greater than 1, (only other possible values atm are 2,3,4)

    ## I will try to give an example for this one to make it easier to follow:
    ## Let's say that the image is 100px by 200px, the finess is 2 (that looks at a 2x2 grid in
            # each sub image space

    ## Percent of pic was chosen to be 10% (not a possible choice because of image quality issues)

    ## because the width is the shorter dimension we are taking 10% of that to be the size of each sub image space
            # which in this case would be 10 pixels

    else:

        ## initialize
        subAveR,subAveG,subAveB=0,0,0
        subRgbArray=[]

        ## the width and height of each sub image space was already calculated, this is the width and height of each
        ## sub SUB image space! Again this was written when sub image spaces were allowed to be rectangular
        subHeight=int(pixelHeight/fineness)                 ## 10/2=5
        subWidth=int(pixelWidth/fineness)                   ## 10/2=5
        print ("SubHeight="+str(subHeight))                   
        print ("SubWidth="+str(subWidth))

        heightSections=int(height/pixelHeight)              ## 200/10 = 20
        widthSections=int(width/pixelWidth)                 ## 100/10 = 10
        print ("HeightSections="+str(heightSections))
        print ("WidthSections="+str(widthSections))
        
        subHeightSections=fineness                          ## =2  I guess this is more accurately called subHeightRows
        subWidthSections=fineness                           ## =2   and this more accurately called subHeightColumns
        print ("SubHeightSections="+str(subHeightSections))
        print ("SubWidthSections="+str(subWidthSections))

        ##  This goes across the image one row at a time and does it's thing
        ##  I tell it how many times to go across by calculating the floor of the width divided by the subsection width

        ## For this example, the image is being broken into a 10x20 grid with each section being a square. 
        
        for hs in range(heightSections):           ## Calculated to be 20 in example      
            for ws in range(widthSections):         ## Calculated to be 10 in example

                ## Basically, for each section in the 10 by 20 grid. Take the fineness and break up each section into another
                ## grid, in this example, the grid for each section is 2x2.

                ## The 2x2 sections are looped through first for speed reasons I think, in the first iteration it was
                ## probably switched. So sub sub sections are first, the sub sections
                
                for h in range(subHeightSections):          #=2
                    for w in range(subWidthSections):       #=2

                        # For each subsection (2x2) of each section (10x20)
                        # add up and average all the r,g, and b values.
                        # adding up the subsection dimensions in this exapmle gets you 10x10 which matches the
                        # dimensions of the sections themselves, multplying those out to get overall image dimensions
                        # gives 100X200. This example was chosen to work out even, with rounding errors and floor
                        # operations there may be some other behavior going on for other dimensions.

                        # sub height and sub width
                        for sh in range(subHeight):         #=5
                            for sw in range(subWidth):      #=10
                                #print '('+str(sw+(subWidth*w)+(pixelWidth*ws))+',',
                                #print str(sh+(subHeight*h)+(pixelHeight*hs))+')'

                                subAveR+=pix[sw+(subWidth*w)+(pixelWidth*ws),sh+(subHeight*h)+(pixelHeight*hs)][r]
                                subAveG+=pix[sw+(subWidth*w)+(pixelWidth*ws),sh+(subHeight*h)+(pixelHeight*hs)][g]
                                subAveB+=pix[sw+(subWidth*w)+(pixelWidth*ws),sh+(subHeight*h)+(pixelHeight*hs)][b]

                        ## After the r,g, and b vlaues are added, there should be subwidth*subheight values 
                        ## (25 in this ex.) so divide by that number to get the average
            
                        subAveR=int(round(subAveR/(subWidth*subHeight)))
                        subAveG=int(round(subAveG/(subWidth*subHeight)))
                        subAveB=int(round(subAveB/(subWidth*subHeight)))
                         
                        subRGB=(subAveR,subAveG,subAveB)
                        subRgbArray.append(subRGB)

                        subAveR,subAveG,subAveB=0,0,0
                                             
                aveRgbArray.append(subRgbArray)
                subRgbArray=[]

    ## At the end of this there will be a list item for every section (10x20=200), containing a list item for every
    ## subsection (4) for a total of 800 subsections)

    return aveRgbArray



def getAveRgbArraySquare(width, height, pixelWidth, pixelHeight, pix, fineness):
    print ("---------------------------------------------------------------------")
    print ("Please wait, the image is being analyzed")
    print ("---------------------------------------------------------------------")

    ## Initialize the variables that will store rbg data about each section
    aveR,aveG,aveB=0,0,0
    ##  The pixel data is accessed with the rgb values of 0,1,2 respectively 
    r,g,b=0,1,2
    ##  Initializing a list.
    aveRgbArray=[]               

    ## The fineness is something I used to try and look more at the distribution of color in each sub section
    ## without getting too crazy. I think it might just be easier to compare histograms of resized version of each image?
    ## That might make my life super easy and improve quality. That way I could take a peice of the image of an aspect ratio
    ## that would fit in the desired container and then shrink it down to the same size as the peice of image I'm looking at
    ## and then compare color distribution using a histogram. Histograms have the problem of not finding similar looking
    ## images because they only look at color, but I think that would be fine for this.

    ##Anyway, Here the finess is one, so I just get the average RGB of each section, the sections are currently
    ##always the same aspect ratio as the original image, but I'm commenting so I know what to change to fix that.
    if fineness==1:
        
        ## These variables are used to step through the sub sections. Because of the way things are currently done,
        ## they will end up being equal. 10X10, 20x20 etc. But I'm trying to change that
        wCount, hCount=0,0  

        ##  pixelHeight/Width is currently taken to be a percentage of the original image dimensions. So changing
        ##  those values will allow this function to step through a different number of boxes? I think so!
        while hCount<int(math.floor(height/pixelHeight)):         
            wCount=0                                            ##  Re-initilize wCount for new row of sections
            while wCount<int(math.floor(width/pixelWidth)):       ##  Same as outer while loop, but for the width
                
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

    ## Example: 100px by 200 px
    ## Fineness = 2
    ## Pixel width and Pixel height were chosen to be 10% They are calculated like so...
    ##  pixelHeight=math.floor(height*percentOfPic)               ##  Height of each section
    ##  pixelWidth=math.floor(width*percentOfPic)                 ##  Width of each section
    ## Percent of pic is user chosen

    else:
        subAveR,subAveG,subAveB=0,0,0
        subRgbArray=[]

        subHeight=int(pixelHeight/fineness)                 ## .1*100/2=5
        subWidth=int(pixelWidth/fineness)                   ## .1*200/2=10
        print ("SubHeight="+str(subHeight))                  
        print ("SubWidth="+str(subWidth))

        heightSections=int(height/pixelHeight)              ## 100/10 = 10
        widthSections=int(width/pixelWidth)                 ## 200/20 = 10  These should equal the percentage chosen (10%)
        print ("HeightSections="+str(heightSections))
        print ("WidthSections="+str(widthSections))
        
        #subHeightSections=int(pixelHeight/subHeight)     
        #subWidthSections=int(pixelWidth/subWidth)
        subHeightSections=fineness                          ## =2
        subWidthSections=fineness                           ## =2
        print ("SubHeightSections="+str(subHeightSections))
        print ("SubWidthSections="+str(subWidthSections))

        ##  This goes across the image one row at a time and does it's thing
        ##  I tell it how many times to go across by calculating the floor of the width divided by the subsection width

        ## For this example, the image is being broken into a 10x10 grid. (But the sections are not square)
        
        for hs in range(heightSections):           ## Calculated to be 10 in example      
            for ws in range(widthSections):         ## Calculated to be 10 in example

                ## Basically, for each section in the 10 by 10 grid. Take the fineness and break up each section into another
                ## grid, in this example, the grid for each section is 2x2.
                
                for h in range(subHeightSections):          #=2
                    for w in range(subWidthSections):       #=2

                        # For each subsection (2x2) of each section (10x10)
                        # add up and average all the r,g, and b values.
                        # adding up the subsection dimensions in this exapmle gets you 10x20 which matches the
                        # dimensions of the sections themselves, multplying those out to get overall image dimensions
                        # gives 100X200. This example was chosen to work out even, which rounding errors and floor
                        # operations there may be some other behavoir going on for other dimensions.
                        
                        for sh in range(subHeight):         #=5
                            for sw in range(subWidth):      #=10
                                #print '('+str(sw+(subWidth*w)+(pixelWidth*ws))+',',
                                #print str(sh+(subHeight*h)+(pixelHeight*hs))+')'

                                subAveR+=pix[sw+(subWidth*w)+(pixelWidth*ws),sh+(subHeight*h)+(pixelHeight*hs)][r]
                                subAveG+=pix[sw+(subWidth*w)+(pixelWidth*ws),sh+(subHeight*h)+(pixelHeight*hs)][g]
                                subAveB+=pix[sw+(subWidth*w)+(pixelWidth*ws),sh+(subHeight*h)+(pixelHeight*hs)][b]

                        ## After the r,g, and b vlaues are added, there should be subwidth*subheight values 
                        ## (50 in this ex.) so divide by that number to get the average
            
                        subAveR=int(round(subAveR/(subWidth*subHeight)))
                        subAveG=int(round(subAveG/(subWidth*subHeight)))
                        subAveB=int(round(subAveB/(subWidth*subHeight)))
                         
                        subRGB=(subAveR,subAveG,subAveB)
                        subRgbArray.append(subRGB)

                        subAveR,subAveG,subAveB=0,0,0
                                             
                aveRgbArray.append(subRgbArray)
                subRgbArray=[]

    ## At the end of this there will be a list item for every section (100), containing a list item for every
    ## subsection (4) for a total of 400 subsections)

    return aveRgbArray


def getPercentOfPic():
    start=1
    end=5
    promptString="Percent of original size for mosaic images(1-5): (Percent)[2%]"
    default=2
    print ("---------------------------------------------------------------------")
    choice=getIntegerInput(start,end,promptString,default)
    print ("---------------------------------------------------------------------")
    percentOfPic=choice/100.0
    return percentOfPic                         ##  Returns a float

def getUserSelectedQueries(fileContents, prompt):
    listOfQueries=[]
    for item in fileContents:
        if item[:7]=="Search:":
            listOfQueries.append(item[8:-1])

    print ('0: All Items')
    for i in range(len(listOfQueries)):
        print (str(i+1)+": ", end="")
        print (listOfQueries[i])

    print ("---------------------------------------------------------------------")
    ##  There is no error checking here. 
    querySelection=input([prompt])
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

## This function gets the image list and associated rgb analysis for each image in the list
## The links were already retrieved, the analysis already done, this simply gets that info.
def getImgUrl_and_aveRgbArrayWeb_forSelection(selection, imageQueryLog):
    
    imageUrlArray=[]
    aveRgbArrayWeb=[]

    logFilename=imageQueryLog
    fileContents=getFileContents(logFilename)

    singleQueryImageList=[]
    singleQueryRGBList=[]

    ## below is a hack to get info from the text file that has the rgb data for web images.
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

    print ("---------------------------------------------------------------------")
    print ("You are using search queries: ", end="")
    for i in range(len(selection)):
        if i!=len(selection)-1:
            print (str(selection[i])+', ', end="")
        else:
            print ("and "+str(selection[i])+".")
    print ("These searches include "+str(len(imageUrlArray))+" images.")
    print ("---------------------------------------------------------------------")

    return returnedArray

## This is the function I want to work on randomizing the selections a bit. This is what I want to fix.
def getOutputUrlList(aveRgbArray, aveRgbArrayWeb, imageUrlArray, fineness):

    errorSum=0
    errorInter=0
    errorSumArray=[]
    minErrorArray=[]
    minErrorIndexArray=[]

    ##  What up! This shit works!

    if fineness==1:

        for section in aveRgbArray:
            errorSumArray=[]
            
            for imageRGB in aveRgbArrayWeb:
                errorSum=0
                error=[section[i]-imageRGB[i] for i in range(len(section))]
                for j in error:
                    errorSum+=abs(j)
                errorSumArray.append(errorSum)

            #minError=min(errorSumArray)         ## Instead of getting the min error here, get the nth lowest where n is rand int
                                                ## I think that might work?
            
            minError=chan.get_n_min_value_indices(errorSumArray,5)

            rand_int=random.randint(0,len(minError)-1)
            
            minErrorIndex=minError[rand_int]#errorSumArray.index(minError)
            
            minErrorIndexArray.append(minErrorIndex)

    ##Psuedo code:
    ## Take the errorSumArray and instead of getting the lowest value, get the 5 lowest values in a list
    ## Do that by making a copy of errorSumArray
    ## Get the min value, remove it, get new min value, remove it. Do that 5 times. I swear I have this already.

    else:

        for section in aveRgbArray: 
            errorSumArray=[]
 
            for imageRGB in aveRgbArrayWeb:

                for i in range(len(section)):

                    error=[section[i][j]-imageRGB[i][j] for j in range(len(section[i]))]

                    for item in error:
                        errorInter+=abs(item)
                    errorSum+=errorInter
                    errorInter=0

##          This method takes about 10-20 times longer than the above method, Why?
##          It is probably converting to a numpy array every time that takes all the time.
##          I bet if I made the two main arrays numpy arrays right off the bat
##          Theeeen analyzed them, it would go much faster, maybe even faster then the list comp way.        
##                try:   
##                    errorSum=np.sum(np.abs(np.array(section)-np.array(imageRGB)))
##                except:
##                    errorSum=10000

                errorSumArray.append(errorSum)
                errorSum=0

            #minError=min(errorSumArray)
            
            #minErrorArray.append(minError)
            minError=chan.get_n_min_value_indices(errorSumArray,5)

            rand_int=random.randint(0,len(minError)-1)
            
            minErrorIndex=minError[rand_int]#errorSumArray.index(minError)
            
            minErrorIndexArray.append(minErrorIndex)

    outputUrlList=[]
    for item in minErrorIndexArray:
        outputUrlList.append(imageUrlArray[item])

    return outputUrlList


## There are some issues with where this gets the image filename and path from. It is currently not working properly.
def generateHTML(width,height,pixelWidth, pixelHeight, mosaicDisplayWidth,cssFile,outputUrlList,imageFile,progDir,mainDir,fineness,jsFile):

    ##  This makes the html for me and I can set inline css with the style attribute
    ##  I want to have all the css in the html so you don't have to float around that mosaic css thang
    ##  Eventually the image height and width will be determined other ways
    print ("Image file: "+str(imageFile))
    
    mosaicDisplayWidth=800
    numberOfPics=int(width/pixelWidth)
    numberOfRows=int(height/pixelHeight)

    aspectRatio=float(width)/float(height)

    imageWidthWeb=mosaicDisplayWidth/numberOfPics
    #imageHeightWeb=int(math.floor(imageWidthWeb/aspectRatio))
    imageHeightWeb=imageWidthWeb

    

    ##  This will also be determined a different way. 
    #imagesPerRow=numberOfPics
    #imagesPerColumn=numberOfPics

    ##  The plus 30 is for 15px of padding on both sides of the mosaic
    imageContainerWidth=mosaicDisplayWidth+30
    imageContainerHeight=int(math.ceil((imageContainerWidth/aspectRatio)+30))

    ##  I'll get this working later
    searchTerm=""
    altText=searchTerm

    ##  Just some header type stuff
    paras = ( "Here is your mosaic! "+imageFile )

    ##  Initialize the page
    page = markup.page( )

    page.init( title="Mosaic Maker", 
               css=(cssFile),
               script={jsFile:'text/type'},)

    ##  Make a header
    page.div(Class='header', style='width:'+str(imageContainerWidth))
    page.p( paras )
    page.div.close()

    ##  Make a div with all the images floating inside
    page.div(Class = 'imageDivContainer', style='width:'+str(imageContainerWidth)+'; height:'+str(imageContainerHeight))

    for i in range(numberOfRows):

        for j in range(numberOfPics):

            if j==0:
                page.div(Class = 'imageRow')

            page.div(Class = 'imageDiv', style='background-image:url('+str(outputUrlList[i*numberOfPics+j])+')')
            page.div.close()

            if j==numberOfPics-1:
                page.div.close()
                     
    #page.div(Class = 'imageDivs', style='background-image:', 
    #page.img( src=outputUrlList, alt=searchTerm ) #height=imageHeightWeb, width=imageWidthWeb, 
    page.div.close()

    ##  Print html to an actual file so it can be viewed

    #imageFilename=imageFile[imageFile.rindex('/')+1:imageFile.rindex('.')]
    imageFilename=imageFile
    
    print ("---------------------------------------------------------------------")
    destFileHTML=input([str("Destination File for HTML Output?["+imageFilename+" Mosaic F"+str(fineness)+" HTML.html]")])
    print ("---------------------------------------------------------------------")

    if destFileHTML=="":
        destFileHTML=imageFilename+" Mosaic F"+str(fineness)+" HTML.html"

    else:
        destFileHTML+=".html"

    os.chdir(progDir+'/'+imageFilename)
       
    output=open(destFileHTML,'w')
    output.write(str(page))
    output.close()
    print ("---------------------------------------------------------------------")
    print ("The page "+destFileHTML+" was created")
    print ("---------------------------------------------------------------------")

    cssFilename=createCSS(imageHeightWeb, imageWidthWeb)
    jsFilename=createJs()

    os.chdir(mainDir)

    return destFileHTML

def createCSS(img_height, img_width):
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
    
    .imageDivContainer {\n
        overflow:hidden;\n
        border:2px solid black;\n
        background:orange;\n
        margin:0 auto;\n
        padding:15px;\n
    }\n
    
    .imageRow {

	position:relative;\n
        display:inline-block;\n
	width:100%;\n
	background-color:orange;\n
	padding:0px;\n
	margin:0px;\n
        
    }\n
    
    .imageDiv {\n
    
        display:inline-block;\n

        padding:0px;\n

        margin:-2px;\n

        background-size: cover;\n

        background-repeat: no-repeat;\n

        background-position: 50% 50%;\n"""+
    
        "width:"+str(int(img_width))+";\n"+
    
        "height:"+str(int(img_height))+";\n"+
    
    """}\n""")
    
    mosaicStyle.close()
    return cssFilename

def createJs():
    jsFilename="mosaicScript.js"
    mosaicScript=open(jsFilename,'w')
    mosaicScript.write(

    """<script src="http://ajax.googleapis.com/ajax/libs/jquery/1/jquery.min.js"></script>
    <script>
    $(document).ready(function() {	
            $('img').error(function(){ 
                    $(this).attr('src', 'https://www.google.com/logos/2012/election12-hp.jpg');
        });
    });	
    </script>""")

    mosaicScript.close()
    return jsFilename


def getImageUrlArrayNew(imageQueryLog):

    ##  Below uses a custom CSE and the google API to retrieve search results
    ##  It is limited to 100 queries a day and 100 results per query 

    MY_API_KEY="AIzaSyD1UeuzDXdKGgcoqH4385D4SF8c2HF8LkY"        ##  This is my personal key for my API
    MY_API_KEY_2="AIzaSyDHprCKraIGVmXnBhuHTPJ8DaWo6hCi9Os"        ## A different one
    SEARCH_ENGINE="010404009348550142839:mz7ovp-utrg"           ##  This is my personal code for my CSE (custom search engine)
    searchType="image"                                          ##  A critera for the urlopen call to limit search to images
    SEARCH_URL="https://www.googleapis.com/customsearch/v1"     ##  I made this a string just to make the code more readable?

    print ("---------------------------------------------------------------------")
    searchQuery=input(["What would you like your image query to be?"])
    print ("---------------------------------------------------------------------")

    if searchQuery=="":
        searchQuery='mylittlepony'

    #logFile=open('savedImageQueries.log','a')
    logFile=open(imageQueryLog,'a')
    logFile.write('\n')
    logFile.write("Search: "+searchQuery)
    logFile.write('\n')
    logFile.close()

    searchQuery=''.join(searchQuery.strip(' ').split(' '))

##    print "---------------------------------------------------------------------"
##    imgColorType=input(["The default color type is 'color'. Others will become available."])
##    print "---------------------------------------------------------------------"

    imgColorType='color'

    numberOfResults=100


    print ("---------------------------------------------------------------------")
    print ("Please wait while the images are retrieved.")
    print ("---------------------------------------------------------------------")

    startIndex=1
    imageUrlArray=[]                    ##  This will hold all the URLs for me

    while startIndex<int(numberOfResults):

        try:
            ##  I got this line straight off the internet - and then made all the strings into variables and put my own stuff in. 
            data = request.urlopen(SEARCH_URL+'?'+'key='+MY_API_KEY+'&'+'cx='+SEARCH_ENGINE+'&'+'q='+searchQuery+'&'+'searchType='+searchType+'&start='+str(startIndex)+'&'+'imgColorType='+imgColorType)

        except:
            data = request.urlopen(SEARCH_URL+'?'+'key='+MY_API_KEY_2+'&'+'cx='+SEARCH_ENGINE+'&'+'q='+searchQuery+'&'+'searchType='+searchType+'&start='+str(startIndex)+'&'+'imgColorType='+imgColorType)

        #encoding = data.headers.get_content_charset()
        
        #data = json.loads(data.read().decode(encoding))

        #data =json.load(data.decode('utf8'))

        dataread = data.read()
        
        datajson = json.loads(dataread.decode("utf8"))

        ##  Manoj's Code - much better. 20 lines became 3

        for item in datajson["items"]:
                imageUrlArray.append(item["link"])
                #print (item["link"])

        startIndex=startIndex+10

    print ("---------------------------------------------------------------------")
    print ("The image Urls have been collected")
    print ("---------------------------------------------------------------------")

    return imageUrlArray

def getAveRgbArrayWebNew_01_08_14(imageUrlArray, fineness):

    #fineness=2

    print ("---------------------------------------------------------------------")
    print ("Please wait while the URLs are tested")
    print ("---------------------------------------------------------------------")

    aveR,aveG,aveB=0,0,0                        ##  I'm currently just averaging RBG to get the overall color of each section
    wCount, hCount=0,0                          ##  Not really a good way of doing it.
    r,g,b=0,1,2

    aveRgbArrayWeb=[]
    
    nonRgbArray=[]
    defaultRgbArray=[]
    
    subRgbArrayWeb=[]
    
    nonRGB=(-501,-501,-501)
    defaultRGB=(-500,-500,-500)

    for i in range(fineness*fineness):
        nonRgbArray.append(nonRGB)
        defaultRgbArray.append(defaultRGB)

    for item in imageUrlArray:
        try:

            #url = 'http://upload.wikimedia.org/wikipedia/commons/thumb/4/43/Timba%2B1.jpg/220px-Timba%2B1.jpg'
            user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.19 (KHTML, like Gecko) Ubuntu/12.04 Chromium/18.0.1025.168 Chrome/18.0.1025.168 Safari/535.19'

            #u = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': user_agent}))
            #filename = request.urlopen(request.Request(item, headers={'User-Agent': user_agent}))

            #filename = filename.read()
            
            #filename=io.StringIO(request.urlopen(item).read())

            URL = item
            u = urllib.request.urlopen(urllib.request.Request(URL, headers={'User-Agent': user_agent}))
            image_file = io.BytesIO(u.read())
            im = Image.open(image_file)
            #print ("Image format: "+str(im.format))
            #print ("Image mode: "+str(im.mode))
            
            #img=Image.open(filename)

            img = im
            
            if img.mode!="RGB":
                print ("The image was not RGB")
                aveRgbArrayWeb.append(nonRgbArray)
                
            else:
                webWidth=img.size[0]
                webHeight=img.size[1]

                subWebWidth=int(webWidth/fineness)
                subWebHeight=int(webHeight/fineness)
                
                pixels=img.load()

                for ws in range(fineness):
                    for hs in range(fineness):
                        
                        for sw in range(subWebWidth):

                            for sh in range(subWebHeight):

                                aveR+=pixels[sw+subWebWidth*ws,sh+subWebHeight*hs][r]
                                aveG+=pixels[sw+subWebWidth*ws,sh+subWebHeight*hs][g]
                                aveB+=pixels[sw+subWebWidth*ws,sh+subWebHeight*hs][b]

                        aveR=int(round(aveR/(subWebWidth*subWebHeight)))
                        aveG=int(round(aveG/(subWebWidth*subWebHeight)))
                        aveB=int(round(aveB/(subWebWidth*subWebHeight)))

                        subRGBWeb=(aveR,aveG,aveB)

                        subRgbArrayWeb.append(subRGBWeb)
                        #print subRgbArrayWeb
                        aveR,aveG,aveB=0,0,0

                aveRgbArrayWeb.append(subRgbArrayWeb)
                subRgbArrayWeb=[]

                print ("File Loaded Successfully")

        ## This is so no image that doesn't load will be chosen as a match. But the index of the image url isn't thrown off. 
        except:
            print ("File did not Load Successfully")
            aveRgbArrayWeb.append(defaultRgbArray)

    return aveRgbArrayWeb














def getAveRgbArrayWebNew(imageUrlArray, fineness):

    #fineness=2

    print ("---------------------------------------------------------------------")
    print ("Please wait while the URLs are tested")
    print ("---------------------------------------------------------------------")

    aveR,aveG,aveB=0,0,0                        ##  I'm currently just averaging RBG to get the overall color of each section
    wCount, hCount=0,0                          ##  Not really a good way of doing it.
    r,g,b=0,1,2

    aveRgbArrayWeb=[]
    
    nonRgbArray=[]
    defaultRgbArray=[]
    
    subRgbArrayWeb=[]
    
    nonRGB=(-501,-501,-501)
    defaultRGB=(-500,-500,-500)

    for i in range(fineness*fineness):
        nonRgbArray.append(nonRGB)
        defaultRgbArray.append(defaultRGB)

    for URL in imageUrlArray:

        try:
            #print (1)
            user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.19 (KHTML, like Gecko) Ubuntu/12.04 Chromium/18.0.1025.168 Chrome/18.0.1025.168 Safari/535.19'
            #print (2)
            u = urllib.request.urlopen(urllib.request.Request(URL, headers={'User-Agent': user_agent}))
            #print (3)
            image_file = io.BytesIO(u.read())
            #print (4)
            img = Image.open(image_file)
            #print (5)
            if img.mode!="RGB":
                #print ("The image was not RGB")
                aveRgbArrayWeb.append(nonRgbArray)
                #print (6)
            else:
                #print (7)
                ## During the analysis here I would like to find the largest square from each image
                ## at the center of the image and then analyze that image.
                ## Should be easy. 
                
                webWidth, webHeight=img.size
                #print (8)
                newW=webWidth
                #print (9)
                newH=webHeight
                #print (10)

                if newW<=newH:
                    #print (11)
                    newH=newW
                    #print (12)
                    x1=0
                    #print (13)
                    x2=newW
                    #print (14)
                    y1=int((webHeight-newH)/2)
                    #print (15)
                    y2=y1+newH
                    #print (16)
                else:
                    #print (17)
                    newW=newH
                    #print (18)
                    y1=0
                    #print (19)
                    y2=newH
                    #print (20)
                    x1=int((webWidth-newW)/2)
                    #print (21)
                    x2=x1+newW
                    #print (22)

                img=img.crop([x1,y1,x2,y2])
                #print (23)

                

                subWebWidth=int(newW/fineness)
                #print (24)
                subWebHeight=int(newH/fineness)
                #print (25)
                
                pixels=img.load()
                #print (26)

                for ws in range(fineness):
                    for hs in range(fineness):
                        
                        for sw in range(subWebWidth):

                            for sh in range(subWebHeight):

                                aveR+=pixels[sw+subWebWidth*ws,sh+subWebHeight*hs][r]
                                aveG+=pixels[sw+subWebWidth*ws,sh+subWebHeight*hs][g]
                                aveB+=pixels[sw+subWebWidth*ws,sh+subWebHeight*hs][b]

                        aveR=int(round(aveR/(subWebWidth*subWebHeight)))
                        aveG=int(round(aveG/(subWebWidth*subWebHeight)))
                        aveB=int(round(aveB/(subWebWidth*subWebHeight)))

                        subRGBWeb=(aveR,aveG,aveB)

                        subRgbArrayWeb.append(subRGBWeb)
                        #print subRgbArrayWeb
                        aveR,aveG,aveB=0,0,0

                aveRgbArrayWeb.append(subRgbArrayWeb)
                subRgbArrayWeb=[]

                print ("File Loaded Successfully")

        ## This is so no image that doesn't load will be chosen as a match. But the index of the image url isn't thrown off. 
        except:
            print ("File did not Load Successfully")
            aveRgbArrayWeb.append(defaultRgbArray)

    return aveRgbArrayWeb











def logNewResults(imageUrlArray,aveRgbArrayWeb, imageQueryLog):

    #savedImageFilename='savedImageQueries.log'
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

    print ("Your new search has been added to "+savedImageFilename+".")


def refreshUrlImageLists(imageQueryLog, fineness):

    #savedImageFile='savedImageQueries.log'
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
            print ("---------------------------------------------------------------------")
            print ("Refreshing the image list for "+fileContents[i-4][8:-1])
            aveRgbArrayWebRefresh=getAveRgbArrayWebNew(ast.literal_eval(fileContents[i-2][:-1]), fineness)
            tempFile.write(str(aveRgbArrayWebRefresh))
            tempFile.write('\n')
            
        else:
            tempFile.write(fileContents[i])

    tempFile.close()

    shutil.copyfile(sivTemp,siv)
    try:
        os.remove(sivTemp)
    except:
        print ("File "+sivTemp+" could not be removed. Delete it yo damn self")
    
##def printScreen():
##    import win32api, win32con, ImageGrab
##    win32api.keybd_event(win32con.VK_SNAPSHOT, 0) #use 1 for only the active window 0 for whole screen
##    im = ImageGrab.grabclipboard()
##    im.save("screenshot.jpg", "JPEG")

##def openBrowser(dest):
##    import webbrowser
##    new = 2
##    url=dest
##    result=webbrowser.open(url,new=new)
##    return result
    
def exitMosaic():
    print ("---------------------------------------------------------------------")
    print ("You have exited the program successfully")
    print ("---------------------------------------------------------------------")

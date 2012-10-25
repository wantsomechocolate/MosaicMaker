from PIL import Image
import math as op

print "---------------------------------------------------------------------"
print "Please wait while the image data is loaded."
print "---------------------------------------------------------------------"
imageFile="C:\Users\James McGlynn\Documents\Mosaic Maker\ManojWTF\ManojWTF.jpg"

im = Image.open(imageFile)                  ##  im only has data about the file - no pixel data
percentOfPic=.1

width=im.size[0]                                    ##  Get width of image
height=im.size[1]

pixelHeight=op.floor(height*percentOfPic)               ##  Height of each section
pixelWidth=op.floor(width*percentOfPic)                 ##  Width of each section

pix=im.load()

print "---------------------------------------------------------------------"
print "Please wait, the image is being analyzed"
print "---------------------------------------------------------------------"
aveR,aveG,aveB=0,0,0        ##  I'm currently just averaging RBG to get the overall color of each section
subAveR,subAveG,subAveB=0,0,0
#wCount, hCount=0,0          ##  Not really a good way of doing it, I saw dude who did the RMS - maybe I'll try that.
r,g,b=0,1,2
 
aveRgbArray=[]              ##  Initializing a list. 
subRgbArray=[]

fineness=1

subHeight=int(pixelHeight/fineness)      
subWidth=int(pixelWidth/fineness)

heightSections=int(height/pixelHeight)           
widthSections=int(width/pixelWidth)              

subHeightSections=int(pixelHeight/subHeight)     
subWidthSections=int(pixelWidth/subWidth)        

print "Height = "+str(height)
print "Width = "+str(width)
print "Section Height = "+str(pixelHeight)
print "Section Width = "+str(pixelWidth)
print "Section Height/2 = "+str(subHeight)
print "Section Width/2 = "+str(subWidth)


##  This goes across the image one row at a time and does it's thing
##  I tell it how many times to go across by calculating the floor of the width divided by the subsection width

for hs in range(heightSections):
    for ws in range(widthSections):
        
        for h in range(subHeightSections):
            for w in range(subWidthSections):
                
                for sh in range(subHeight):
                    for sw in range(subWidth):
                        #print '('+str(sw+(subWidth*w)+(pixelWidth*ws))+',',
                        #print str(sh+(subHeight*h)+(pixelHeight*hs))+')'

                        subAveR+=pix[sw+(subWidth*w)+(pixelWidth*ws),sh+(subHeight*h)+(pixelHeight*hs)][r]
                        subAveG+=pix[sw+(subWidth*w)+(pixelWidth*ws),sh+(subHeight*h)+(pixelHeight*hs)][g]
                        subAveB+=pix[sw+(subWidth*w)+(pixelWidth*ws),sh+(subHeight*h)+(pixelHeight*hs)][b]

                subAveR=int(round(subAveR/(subWidth*subHeight)))
                subAveG=int(round(subAveG/(subWidth*subHeight)))
                subAveB=int(round(subAveB/(subWidth*subHeight)))
                 
                subRGB=(subAveR,subAveG,subAveB)
                subRgbArray.append(subRGB)

                subAveR,subAveG,subAveB=0,0,0
                                     
        aveRgbArray.append(subRgbArray)
        subRgbArray=[]


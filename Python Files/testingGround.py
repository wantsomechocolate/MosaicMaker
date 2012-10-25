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
wCount, hCount=0,0          ##  Not really a good way of doing it, I saw dude who did the RMS - maybe I'll try that.
r,g,b=0,1,2                 ##  The pixel data is accessed with the rgb values of 0,1,2 respectively 
aveRgbArray=[]              ##  Initializing a list. 
subRgbArray=[]

fineness=2

subHeight=pixelHeight/fineness
subWidth=pixelWidth/fineness

print "Height = "+str(height)
print "Width = "+str(width)
print "Section Height = "+str(pixelHeight)
print "Section Width = "+str(pixelWidth)
print "Section Height/3 = "+str(subHeight)
print "Section Width/3 = "+str(subWidth)


##  This goes across the image one row at a time and does it's thing
##  I tell it how many times to go across by calculating the floor of the width divided by the subsection width

while hCount<int(op.floor(height/pixelHeight)):         ##  I.E. image is 100px high, percentOfPic is 0.1 -> hCount will reach 10 or something
    wCount=0                                            ##  Re-initilize wCount for new row of sections
    while wCount<int(op.floor(width/pixelWidth)):       ##  Same as outer while loop, but for the width
        
        ##  For a given section this adds up all the pixel's RGB values and then averages them and puts them in a list

        for h in range(int(pixelHeight)):

            for w in range(int(pixelWidth)):                

                for sh in range(int(subHeight)):

                    for sw in range(int(subWidth)):
                        print str(sw+subWidth*w)+','+str(sh+subHeight*h)
                        subAveR+=pix[sw+subWidth*w,sh+subHeight*h][r]
                        subAveG+=pix[sw+subWidth*w,sh+subHeight*h][g]
                        subAveB+=pix[sw+subWidth*w,sh+subHeight*h][b]

                subAveR=int(round(subAveR/(subWidth*subHeight)))
                subAveG=int(round(subAveG/(subWidth*subHeight)))
                subAveB=int(round(subAveB/(subWidth*subHeight)))

                subRGB=(subAveR,subAveG,subAveB)
                subRgbArray.append(subRGB)
                        
##                aveR+=pix[w+pixelWidth*wCount,h+pixelHeight*hCount][r]
##                aveG+=pix[w+pixelWidth*wCount,h+pixelHeight*hCount][g]
##                aveB+=pix[w+pixelWidth*wCount,h+pixelHeight*hCount][b]
##                
##        aveR=int(round(aveR/(pixelWidth*pixelHeight)))
##        aveG=int(round(aveG/(pixelWidth*pixelHeight)))
##        aveB=int(round(aveB/(pixelWidth*pixelHeight)))
##
##        aveRGB=(aveR,aveG,aveB)
##        aveRgbArray.append(aveRGB) 
                
        wCount=wCount+1
        
    hCount=hCount+1

##print "-----------------------------------------"
##print "Sample RGB Data"
##for i in range(0,len(aveRgbArray),10):
##    print aveRgbArray[i]
##print "-----------------------------------------"

print "-----------------------------------------"
print "Sample RGB Data"
for i in range(0,len(subRgbArray),10):
    print subRgbArray[i]
print "-----------------------------------------"
    

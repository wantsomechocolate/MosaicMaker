## Functions relating to image analysis
## They won't care about stupid bullshit with directories and crap
## Just take the inputs and produce the outputs.

def getAveRgbArray(width, height, pixelWidth, pixelHeight, pix, fineness):

    ## Initializing
    aveR,aveG,aveB=0,0,0

    r,g,b=0,1,2

    aveRgbArray=[]              

    if fineness==1:
 
        wCount, hCount=0,0          

        while hCount<int(math.floor(height/pixelHeight)):

            wCount=0

            while wCount<int(math.floor(width/pixelWidth)):     

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

    else:

        subAveR,subAveG,subAveB=0,0,0
        
        subRgbArray=[]

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
        
        for hs in range(heightSections):           ## Calculated to be 20 in example      
            for ws in range(widthSections):         ## Calculated to be 10 in example

                for h in range(subHeightSections):          #=2
                    for w in range(subWidthSections):       #=2
                        
                        for sh in range(subHeight):         #=5
                            for sw in range(subWidth):      #=10

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

    return aveRgbArray



def getAveRgbArraySquare(width, height, pixelWidth, pixelHeight, pix, fineness):
    print ("---------------------------------------------------------------------")
    print ("Please wait, the image is being analyzed")
    print ("---------------------------------------------------------------------")

    aveR,aveG,aveB=0,0,0
    
    r,g,b=0,1,2

    aveRgbArray=[]               

    if fineness==1:
        
        wCount, hCount=0,0  

        while hCount<int(math.floor(height/pixelHeight)):
            
            wCount=0                                            ##  Re-initilize wCount for new row of sections
            
            while wCount<int(math.floor(width/pixelWidth)):       ##  Same as outer while loop, but for the width
                
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
        
        subHeightSections=fineness                          ## =2
        subWidthSections=fineness                           ## =2
        print ("SubHeightSections="+str(subHeightSections))
        print ("SubWidthSections="+str(subWidthSections))
        
        for hs in range(heightSections):           ## Calculated to be 10 in example      
            for ws in range(widthSections):         ## Calculated to be 10 in example

                for h in range(subHeightSections):          #=2
                    for w in range(subWidthSections):       #=2
                        
                        for sh in range(subHeight):         #=5
                            for sw in range(subWidth):      #=10

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

    ## At the end of this there will be a list item for every section (100), containing a list item for every
    ## subsection (4) for a total of 400 subsections)

    return aveRgbArray

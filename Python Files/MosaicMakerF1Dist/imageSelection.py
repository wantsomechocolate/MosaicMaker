#!/usr/bin/python
# Filename: imageSelection.py

def getOutputUrlList(aveRgbArray, aveRgbArrayWeb, imageUrlArray):
    errorSum=0
    errorSumArray=[]
    minErrorArray=[]
    minErrorIndexArray=[]
    for section in aveRgbArray:
        errorSumArray=[]
        for imageRGB in aveRgbArrayWeb:
            errorSum=0
            error=[section[i]-imageRGB[i] for i in range(len(section))]
            for j in error:
                errorSum+=abs(j)
            errorSumArray.append(errorSum)

        minError=min(errorSumArray)
        minErrorArray.append(minError)

        minErrorIndex=errorSumArray.index(minError)
        minErrorIndexArray.append(minErrorIndex)

    outputUrlList=[]
    for item in minErrorIndexArray:
        outputUrlList.append(imageUrlArray[item])

    return outputUrlList

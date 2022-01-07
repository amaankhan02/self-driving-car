import os
import numpy as np
import cv2

"""
Test out the classifier by running it on few images
"""

def getBrighestSpot(bgrImg):
    """

    :param bgrImg:
    :return: an ordered pair (x,y) location of brightest spot
    """
    gray = cv2.cvtColor(bgrImg, cv2.COLOR_BGR2GRAY)
    # gray = cv2.GaussianBlur(gray, (3,3), 0) #blur to remove noise

    # the area of the image with largest intensity value
    (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(gray)
    print("gray brightest value: ",gray[maxLoc[1], maxLoc[0]])

    cv2.circle(bgrImg,maxLoc,5,(255,0,0), 2)
    return minLoc, maxLoc

def getColor(bgrImg):
    """returns 'green', 'red', or 'none' """

    hsvImg = cv2.cvtColor(bgrImg, cv2.COLOR_BGR2HSV)
    #get brightest spot
    minLoc, maxLoc = getBrighestSpot(bgrImg)

    #brightest
    h,s,v = hsvImg[maxLoc[1],maxLoc[0],:]
    print("Brightest: ",h, s, v)

    #dimmest
    h,s,v = hsvImg[minLoc[1], minLoc[0],:]
    print("Dimmest: ",h,s,v)



imgPath = \
    r'I:\TFS\AK\MyProjects\Development\SelfDrivingCar\Computer\ObjectDetection\TrafficLightDetection\NegativeImgTesting.png'
cascadePath = \
    r'I:\TFS\AK\MyProjects\Development\SelfDrivingCar\Computer\ObjectDetection\TrafficLightDetection\HaarCascadeClassifier\data\12.26.17\Trial2\trafficLightCascade.xml'
negImgPath = \
    r'I:\TFS\AK\MyProjects\Development\SelfDrivingCar\Computer\ObjectDetection\TrafficLightDetection\HaarCascadeClassifier\neg\negImg_835.png'


cascade = cv2.CascadeClassifier(cascadePath)
img = cv2.imread(imgPath)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

#TODO: what do these parameters do, and what is detectMultiScale2() and detectMultiScale3()
trafficLights = cascade.detectMultiScale(gray, 1.35, 5, maxSize=(50,50))

#if found an object, it returns Rect(x,y,w,h), then draw a box there
# print("Number of Traffic Lights found ",len(trafficLights))
# boxes = []
# greenContents = []
for (x,y,w,h) in trafficLights:
    #find center of boudning box (by splitting it into 9 squares and taking center)
    xmin = x + int(w/3)
    ymin = y + int(h/3)
    xmax = x + int((2*w)/3)
    ymax = y + int((2*w)/3)

    cv2.rectangle(img, (xmin, ymin), (xmax,ymax), (255, 0, 0), 2)
    getColor(img[ymin:ymax, xmin:xmax])


# index = greenContents.index(max(greenContents)) #get index of max green content
# greenBox = boxes[index]
# x,y,w,h = greenBox
#
# cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)



cv2.imshow('gray', img)

cv2.waitKey(0)
cv2.destroyAllWindows()

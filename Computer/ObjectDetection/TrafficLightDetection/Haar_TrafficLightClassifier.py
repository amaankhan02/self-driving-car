from abc import ABC
import cv2
import numpy as np

"""
Classifier for Haar Cascade
"""
class Haar_TrafficLightClassifier(ABC):
    def __init__(self, cascade_path):
        self.cascade = cv2.CascadeClassifier(cascade_path)

    def classify(self,bgrImg,drawBoundingBox=True, search_upper_half=True):
        """

        :param bgrImg:
        :param drawBoundingBox:
        :param search_upper_half: if True, it only searches for traffic light in upper half of image
        :return:
        """
        gray = cv2.cvtColor(bgrImg, cv2.COLOR_BGR2GRAY) #gray is
        if(search_upper_half):
            height = bgrImg.shape[0]
            gray = gray[0:int(height/2)] #only detect on upper half of image
        trafficLights = self.cascade.detectMultiScale(gray, 1.35, 5, maxSize=(80,80))

        for (x,y,w,h) in trafficLights:
            # find center of boudning box (by splitting it into 9 squares and taking center)
            xmin = x + int(w / 3)
            ymin = y + int(h / 3)
            xmax = x + int((2 * w) / 3)
            ymax = y + int((2 * w) / 3)

            #get brightest spot
            (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(gray[ymin:ymax, xmin:xmax])
            maxLoc = (xmin+maxLoc[0],ymin+maxLoc[1])

            #TODO: Apply condition on threshold for brightness value here
            if(gray[maxLoc[1],maxLoc[0]] > 220):

                #get color of bright spot
                hsvImg = cv2.cvtColor(bgrImg, cv2.COLOR_BGR2HSV) # Hue range: 0,179, Saturation and value range: 0,255
                color = self._getColor(hsvImg, maxLoc) #finds color, and also checks if it is bright enough
                if(color is not None):
                    if (drawBoundingBox):
                        cv2.rectangle(bgrImg, (x, y), (x + w, y + h), (255, 0, 0), 2)
                        textYLoc = y + h + 20;
                        if(color == 'red'):
                            textColor = (0,0,255)
                        elif(color == 'green'):
                            textColor = (0,255,0)
                        cv2.putText(bgrImg, color.upper(), (x,textYLoc), cv2.FONT_HERSHEY_SIMPLEX, 0.6, textColor, 2)
                    return color
        return None


    def _getColor(self, hsvImg, point):
        """
        :param hsvImg:
        :param point: ordered par of (x,y) location for color to be evaluated
        :return: "green", "red", or None
        """
        h,s,v = hsvImg[point[1], point[0], :] #get hsv values of the point

        if(h <= 40 and v >= 200): # v makes sure that it is bright enough
            return "red"
        elif(h >=70 and h <= 95 and v >= 200):
            return "green"
        else:
            return None


# #testing
# cascadePath = \
#     r'I:\TFS\AK\MyProjects\Development\SelfDrivingCar\Computer\ObjectDetection\TrafficLightDetection\HaarCascadeClassifier\data\12.26.17\Trial2\trafficLightCascade.xml'
# imgPath = \
#     r'I:\TFS\AK\MyProjects\Development\SelfDrivingCar\Computer\ObjectDetection\TrafficLightDetection\RedLightTesting2.png'
# img = cv2.imread(imgPath)
#
# classifer = Haar_TrafficLightClassifier(cascadePath)
# color = classifer.classify(img)
# print(color)
# cv2.imshow("i",img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

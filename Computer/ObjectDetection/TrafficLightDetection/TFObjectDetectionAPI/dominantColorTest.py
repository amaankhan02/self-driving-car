import os
import cv2
import numpy as np
import tensorflow
from Computer.ObjectDetection.TrafficLightDetection.TrafficLightClassifer import TrafficLightClassifier

"""
testing for finding dominant color in the bounding box prediction of traffic light
"""


def identifyPrimaryColor(bgrImg):
    """
    :param bgrImg:
    :return: 'red', 'green', or 'none' for not red or green as primary
    """
    hsvImg = cv2.cvtColor(bgrImg, cv2.COLOR_BGR2HSV) #FULL indicates hue in range 0 - 255, else it is 0 - 180
    h,s,v = cv2.split(hsvImg)
    # h = hsvImg[:,:,0]
    print("MAX VALUE",np.amax(v))
    #take count
    redCount = 0
    greenCount = 0
    noneCount = 0; #holds count for when not green or red
    lowerRedCount = 0
    for row in hsvImg:
        for pixel in row:
            hue = pixel.item(0)
            value = pixel.item(2)
            if(hue >= 150 and hue <= 180): #red (magenta in HSV scale)
                redCount+=1;
            elif(hue >=0 and hue <= 60 and value >=200):#check if range of [0,60] and value is above 85. Explanation in OneNote
                lowerRedCount +=1;
                redCount +=1;
            elif(hue >=60 and hue <= 120): #green (green and cyan in HSV scale)
                greenCount += 1;
            else:
                noneCount +=1

    print("Red Count: {0}\nGreen count: {1}\nNone Count: {2}\nLower Red Count:{3}".format(redCount, greenCount, noneCount, lowerRedCount))

    maxCount = max(max(redCount, greenCount), noneCount)
    if(redCount == maxCount):
        return 'red'
    elif(greenCount == maxCount):
        return 'green'
    else:
        return 'none'



path_to_ckpt = r"I:\TFS\AK\MyProjects\Development\SelfDrivingCar\Computer\ObjectDetection\TrafficLightDetection\models\ssd_mobiilenet_v1_coco_2017_11_17_model\fine_tuned_model\frozen_inference_graph.pb"
path_to_labels=r"I:\TFS\AK\MyProjects\Development\SelfDrivingCar\Computer\ObjectDetection\TrafficLightDetection\TrafficLightLabeledData\Train_label_map.pbtxt"
# classifier = TrafficLightClassifier(path_to_ckpt, path_to_labels)

greenImgPath = "I:\TFS\AK\MyProjects\Development\SelfDrivingCar\Computer\ObjectDetection\TrafficLightDetection\GreenLightTesting.png"
redImgPath = "I:\TFS\AK\MyProjects\Development\SelfDrivingCar\Computer\ObjectDetection\TrafficLightDetection\RedLightTesting.png"
noLightImgPath = r"I:\TFS\AK\MyProjects\Development\SelfDrivingCar\Computer\ObjectDetection\TrafficLightDetection\NoLightTesting.png"
imgDataPath = "I:\TFS\AK\MyProjects\Development\SelfDrivingCar\Computer\ObjectDetection\TrafficLightDetection\TrafficLightData"

img = cv2.imread(os.path.join(imgDataPath, '1511574863.2.png'))
# img = cv2.imread(noLightImgPath)
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# boxes,scores,classes,num = classifier.get_classification(img_rgb)
# max_index = np.argmax(scores)  # get the index of highest confidence score
# prediction = classifier.category_index[classes[max_index]]['name']
# print(prediction)

# ymin, xmin, ymax, xmax = classifier.getBoundingBoxCoordinates(boxes[max_index], img.shape[0], img.shape[1])

# drawImg = np.array(img, copy=True) #copy img
# lineColor = (0,0,255)
# cv2.line(drawImg,(xmin,ymin), (xmin,ymax), lineColor) #left, top to bottom
# cv2.line(drawImg,(xmin,ymin), (xmax, ymin), lineColor) #top, left to right
# cv2.line(drawImg, (xmin,ymax), (xmax,ymax), lineColor) #bottom, left to right
# cv2.line(drawImg, (xmax,ymin), (xmax,ymax),lineColor) #right, top to bottom

# cropImg = img[ymin:ymax,xmin:xmax]
# color = identifyPrimaryColor(cropImg)
# print("Primary Color: {0}".format(color))

# prediction = classifier.get_classification(img_rgb)
# print(prediction)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
cv2.imshow("I",gray)
cv2.waitKey(0)
cv2.destroyAllWindows()
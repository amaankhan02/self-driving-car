"""
Proof of concept of classifying the traffic lights
Streams video from raspberry pi and it shows it here
"""
import socket
from _thread import *
import threading
import io
import socketserver
import struct
import cv2
import numpy as np
from Computer.Autonomous.KerasDiscreteTurnsModel import KerasDiscreteTurnsModel
import atexit
from tkinter import *
import time
sys.path.append(r'C:\Program Files\tensorflow-models\research\object_detection')
sys.path.append(r'C:\Program Files\tensorflow-models\research\object_detection\slim')
from utils import label_map_util
from utils import visualization_utils as vis_util
import tensorflow as tf
import os
from PIL import Image
from Computer.ObjectDetection.TrafficLightDetection.TrafficLightClassifer import TrafficLightClassifier

def identifyDominantColor(rgbImg):
    """
    :param rgbImg:
    :return: 'red' or 'green' or 'none' -- String values returned
    """
    hsvImg = cv2.cvtColor(rgbImg, cv2.COLOR_RGB2HSV)  # FULL indicates hue in range 0 - 255, else it is 0 - 180
    h, s, v = cv2.split(hsvImg)
    # h = hsvImg[:,:,0]

    # take count
    redCount = 0
    greenCount = 0
    noneCount = 0;  # holds count for when not green or red

    for row in hsvImg:
        for pixel in row:
            hue = pixel.item(0)
            value = pixel.item(2)
            if (hue >= 150 and hue <= 180):  # red (magenta in HSV scale)
                redCount += 1;
            elif (hue >= 0 and hue <= 60 and value >= 200):  # check if range of [0,60] and value is above 85. Explanation in OneNote
                redCount += 1;
            elif (hue >= 60 and hue <= 120):  # green (green and cyan in HSV scale)
                greenCount += 1;
            else:
                noneCount += 1

    maxCount = max(max(redCount, greenCount), noneCount)
    if (redCount == maxCount):
        return 'red'
    elif (greenCount == maxCount):
        return 'green'
    else:
        return 'none'


def getBoundingBoxCoordinates(box, height, width):
    """
    returns coordinates of bounding box in pixels
    :param box: a Tensor returned of tensorflow object detection prediction of 1 set of ymin, xmin, ymax, xmax
    :param height: height of image
    :param width: width of image
    :return: ymin, xmin, ymax, xmax coordinates in image of bounding box
    """
    # coordinates return the percent of height or width
    ymin, xmin, ymax, xmax = tuple(box.tolist())
    # convert to coordinate points
    ymin = int(ymin * height)
    ymax = int(ymax * height)
    xmin = int(xmin * width)
    xmax = int(xmax * width)
    return ymin, xmin, ymax, xmax


def predictTrafficLight(rgbImg, classifier):
    """
    :param rgbImg: RGB img
    :param classifier:
    :return:
    """
    global previousPrediction, isClassifying
    prediction = classifier.get_classification(rgbImg, 0.6)
    if (prediction != previousPrediction):  # if new prediction
        previousPrediction = prediction;
        print(prediction)
        print("Distance: ",distance_to_camera(8,356.5,classifier.getTrafficLightWidth()))
    else: #it is less than
        if(previousPrediction != "none"): #don't print none if already said none
            print("none")
        previousPrediction = "none";
    isClassifying = False;

def distance_to_camera(knownWidth, focalLength, pixelWidth):
    return (knownWidth*focalLength) / pixelWidth;

class VideoStreamHandler(socketserver.StreamRequestHandler):
    def handle(self):
        global isClassifying, classifierPrediction;
        print("inside video stream handler")
        path_to_ckpt = r"I:\TFS\AK\MyProjects\Development\SelfDrivingCar\Computer\ObjectDetection\TrafficLightDetection\models\ssd_mobiilenet_v1_coco_2017_11_17_model\fine_tuned_model\frozen_inference_graph.pb"
        path_to_labels=r"I:\TFS\AK\MyProjects\Development\SelfDrivingCar\Computer\ObjectDetection\TrafficLightDetection\TrafficLightLabeledData\Train_label_map.pbtxt"
        classifier = TrafficLightClassifier(path_to_ckpt, path_to_labels)
        try:
            while True:
                #read length of the image, if len = 0, then quit loop
                image_len = struct.unpack('<L', self.rfile.read(struct.calcsize('<L')))[0]
                if not image_len:
                    break
                #Construct stream to hold image data and read the image
                #data from connection
                image_stream = io.BytesIO()
                image_stream.write(self.rfile.read(image_len))
                # Rewind the stream, open it as an image with PIL and do some
                # processing on it
                image_stream.seek(0)
                #convert to numpy array for cv2 to read
                cv2_image = np.asarray(bytearray(image_stream.read()), dtype=np.uint8)
                cv2_image = cv2.imdecode(cv2_image, cv2.IMREAD_COLOR)
                cv2_image_rgb = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
                if(isClassifying == False):
                    isClassifying = True
                    start_new_thread(predictTrafficLight, (cv2_image_rgb,classifier))


                # ymin, xmin, ymax, xmax = classifier.getBoundingBoxCoordinates(boxes[max_index], cv2_image.shape[0], cv2_image.shape[1])
                # lightHeight = ymax - ymin;
                # lightWidth = xmax - xmin;
                # print("{}x{}".format(lightWidth, lightHeight))
                # max_index = np.argmax(scores)

                # boxed_image = vis_util.visualize_boxes_and_labels_on_image_array(
                #     cv2_image[0:120], #classify on top half of image
                #     boxes,
                #     classes.astype(np.int32),
                #     scores,
                #     classifier.category_index,
                #     use_normalized_coordinates=True,
                #     line_thickness=4,
                #     min_score_thresh = .90)

                # combined_img = np.concatenate((boxed_image, cv2_image[120:240]))
                cv2.imshow('image', cv2_image)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        finally:
            cv2.destroyAllWindows()
            print("Connection Closed on VideoStreamHandler")


def startVideoStreamHandler(host, port):
    print("starting video server")
    server = socketserver.TCPServer((host, port), VideoStreamHandler)
    server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.serve_forever()


isClassifying = False;
classifierPrediction = []
previousPrediction = ""
startVideoStreamHandler("192.168.1.7", 8000)
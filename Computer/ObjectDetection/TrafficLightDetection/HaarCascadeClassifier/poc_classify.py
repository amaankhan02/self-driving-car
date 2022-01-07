"""
get streamed video and classify the light
"""

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
import atexit
from tkinter import *
import time
sys.path.append(r'C:\Program Files\tensorflow-models\research\object_detection')
sys.path.append(r'C:\Program Files\tensorflow-models\research\object_detection\slim')
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


def classify(bgrImg, cascade):
    gray = cv2.cvtColor(bgrImg, cv2.COLOR_BGR2GRAY)
    trafficLights = cascade.detectMultiScale(gray, 1.35, 5, maxSize=(55,55), minSize=(15,15))

    # if found an object, it returns Rect(x,y,w,h), then draw a box there
    for (x, y, w, h) in trafficLights:
        cv2.rectangle(bgrImg, (x, y), (x + w, y + h), (255, 0, 0), 2)


def distance_to_camera(knownWidth, focalLength, pixelWidth):
    return (knownWidth*focalLength) / pixelWidth;

class VideoStreamHandler(socketserver.StreamRequestHandler):
    def handle(self):
        global isClassifying, classifierPrediction;
        print("inside video stream handler")
        cascadePath = \
            r'I:\TFS\AK\MyProjects\Development\SelfDrivingCar\Computer\ObjectDetection\TrafficLightDetection\HaarCascadeClassifier\data\12.26.17\Trial2\trafficLightCascade.xml'
        cascade = cv2.CascadeClassifier(cascadePath)
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
                classify(cv2_image, cascade)

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
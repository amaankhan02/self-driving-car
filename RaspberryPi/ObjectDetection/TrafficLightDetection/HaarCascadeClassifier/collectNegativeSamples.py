"""
Records video and saves frames to disk
"""

import time
from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import glob
import os


camera = PiCamera()
camera.resolution = (320, 240)
camera.framerate = 5
rawCapture = PiRGBArray(camera, size=(320, 240))

directory = '/home/pi/PiRoboticFiles/TrafficLightData/HaarCascadeClassifier/NegativeSamples/'
filenameFormat = directory + "{}.png"

print("started recording")
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # raw NumPy array representing the image
    image = frame.array
    cv2.imshow("i", image)
    rawCapture.truncate(0)
    cv2.imwrite(filenameFormat.format(round(time.time(),1)),image)
    k = cv2.waitKey(33)
    if k == ord("q"):
        break;

cv2.destroyAllWindows()
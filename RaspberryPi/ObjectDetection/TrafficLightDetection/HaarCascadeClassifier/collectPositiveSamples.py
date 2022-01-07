"""
Records video, press space bar to save to disk.
Runs on RPi3, remote desktop onto RPi3 and control this program
"""
import time
from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2

camera = PiCamera()
camera.resolution = (320, 240)
camera.framerate = 30
rawCapture = PiRGBArray(camera, size=(320, 240))



filenameFormat = '/home/pi/PiRoboticFiles/TrafficLightData/HaarCascadeClassifier/Positive Samples/{}.png'

count = 1;
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # raw NumPy array representing the image
    image = frame.array
    cv2.imshow("i", image)

    rawCapture.truncate(0)

    k = cv2.waitKey(33)
    if k == ord("q"):
        break;
    elif k == 32: #space bar click
        cv2.imwrite(filenameFormat.format(round(time.time(),1)),image)
        print("saved")

cv2.destroyAllWindows()
import socket
from _thread import *
import threading
import io
import socketserver
import struct
import cv2
import numpy as np
from Computer.Autonomous.KerasDiscreteTurnsModel import KerasDiscreteTurnsModel
from Computer.Autonomous.KerasSteeringAngleModel import KerasSteeringAngleModel
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
from Computer.NN_Trainer.TrainType import TrainType;
# from Computer.ObjectDetection.TrafficLightDetection.TrafficLightClassifer import TrafficLightClassifier
from Computer.ObjectDetection.TrafficLightDetection.Haar_TrafficLightClassifier import Haar_TrafficLightClassifier

if tf.__version__ != '1.4.0':
  raise ImportError('Please upgrade your tensorflow installation to v1.4.0!')


'''
predictionIndex is based on the index of 1 in one-hot encoded value from
Commands.py Enum.
-1 = Stop_all_motors
    NO_CMD = [0,0,0,0]
    LEFT = [1,0,0,0] #left forward
    RIGHT = [0,1,0,0] #right forward
    FORWARD = [0,0,1,0] #Only forward straight
    BACK = [0,0,0,1]
'''

def sendDiscreteTurnsCommand(serverSocket, data):
    """
    Takes the prediction index and sends appropriate command
    :param serverSocket:
    :param data:
    :return:
    """
    if(data == 0): #LEFT
        serverSocket.send("L;".encode()) #.encode converts to byte
    elif(data == 1): #RIGHT
        serverSocket.send("R;".encode())
    elif(data == 2): #FORWARD
        serverSocket.send("F;".encode())
    elif(data == 3): #BACK
        serverSocket.send("B;".encode())
    else:
        print("-----invalid command to send-----DATA={}".format(data))

def sendSteeringAngleCommand(serverSocket, data):
    #convert int data to string, and send, because the integer with negatives gives bad results sometimes
    if(data > 10):
        data = 10
    elif(data < -10):
        data = -10
    data = str(data) + ";"
    # serverSocket.send(data.to_bytes(2,'little',signed=True))
    serverSocket.send(data.encode())
    print(data)

def sendStop(serverSocket):
    serverSocket.send("*;".encode()) #STOP ALL MOTORS

'''DEPRECATED -- USED FOR CNN TRAFFIC LIGHT DETECTOR'''
'''
def predictTrafficLight(rgbImg, classifier):
    """
   :param rgbImg: RGB img
   :param classifier:
   :return:
   """
    global trafficLightPrediction, isClassifyingTrafficLight, thresholdColorAbundance, \
        differentPreviousTrafficLightPrediction, minTrafficLightDistance, focalLength, knownWidth

    previousTrafficLightPrediction = trafficLightPrediction;
    color = classifier.get_classification(rgbImg, thresholdColorAbundance)

    if((color == 'none' and differentPreviousTrafficLightPrediction== 'red') or (color == 'red')):
        distance = distance_to_camera(knownWidth,focalLength, classifier.getTrafficLightWidth())
        # print("distance = ",round(distance,2))
        if(distance <= minTrafficLightDistance):
            trafficLightPrediction = 'red'
    elif(color == 'green'):
        trafficLightPrediction = 'green'
    else:
        trafficLightPrediction = 'none'
    print(trafficLightPrediction)
    if(trafficLightPrediction != previousTrafficLightPrediction): #only initalize to new one if its a different prediction, don't have same values for both vairables
        differentPreviousTrafficLightPrediction = previousTrafficLightPrediction

    isClassifyingTrafficLight = False

def distance_to_camera(knownWidth, focalLength, pixelWidth):
    return (knownWidth * focalLength) / pixelWidth
'''
class VideoStreamHandler(socketserver.StreamRequestHandler):
    def handle(self):
        global prediction, oldPrediction, commandSocket, lastPredictionTime, networkType, networkDirectory
        print("inside video stream handler")
        # the model MUST be declared in same thread as where the predict function is called, OR, an error occurs - https://github.com/fchollet/keras/issues/2397
        model = None;
        if(networkType.value == TrainType.SteerAngles.value):
            model = KerasSteeringAngleModel(networkDirectory)
            sendCommand = sendSteeringAngleCommand
        elif(networkType.value == TrainType.DiscreteTurns.value):
            model = KerasDiscreteTurnsModel(networkDirectory)
            sendCommand = sendDiscreteTurnsCommand;

        cascadePath = \
            r'I:\TFS\AK\MyProjects\Development\SelfDrivingCar\Computer\ObjectDetection\TrafficLightDetection\HaarCascadeClassifier\data\12.26.17\Trial2\trafficLightCascade.xml'
        trafficLightClassifier = Haar_TrafficLightClassifier(cascadePath)

        isRedLight = False;
        numContinuousRedLights = 0;

        print("inside video stream handler")
        try:
            while True:
                #read length of the image, if len = 0, then quit loop
                image_len = struct.unpack('<L', self.rfile.read(struct.calcsize('<L')))[0]
                if not image_len:
                    break
                #Construct stream to hold image data and read the image data from connection
                image_stream = io.BytesIO()
                image_stream.write(self.rfile.read(image_len))
                # Rewind the stream, open it as an image with PIL and do some processing on it
                image_stream.seek(0)
                #convert to numpy array for cv2 to read
                cv2_image = np.asarray(bytearray(image_stream.read()), dtype=np.uint8)
                cv2_image = cv2.imdecode(cv2_image, cv2.IMREAD_COLOR)

                #predict steering
                prediction = int(round(model.predict(cv2_image)))  # update the prediction index
                #TODO: CHANGE THIS LATER, BUT FOR NOW KEEP IT, (predict_old)
                # prediction = model.predict_old(cv2_image[120:240])

                #look for traffic light in upper half of image
                trafficLightPrediction = trafficLightClassifier.classify(cv2_image,drawBoundingBox=True, search_upper_half=True)

                if(trafficLightPrediction == 'red'):
                    isRedLight = True
                    oldPrediction = "stop";
                elif(trafficLightPrediction == 'green'):
                    isRedLight = False

                if(isRedLight == False):
                    numContinuousRedLights = 0; #reset
                    if oldPrediction != prediction: #send if its a new cmd
                        oldPrediction = prediction
                        sendCommand(commandSocket, prediction)
                else: #RED TRAFFIC LIGHT
                    numContinuousRedLights +=1
                    if(numContinuousRedLights == 1): #if first red, then stop, don't keep sending stop
                        sendStop(commandSocket)


                cv2.imshow('image', cv2_image)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        finally:
            cv2.destroyAllWindows()
            print("Connection Closed on VideoStreamHandler")

# class UltrasonicSensorHandler(socketserver.BaseRequestHandler):
#     def handle(self):
#         global uss_distance
#         print("inside ultraonsic sensor handler")
#         try:
#             while True:
#                 self.data = self.request.recv(1024)
#                 if not self.data:
#                     print("ultrasonic sensor handler closed")
#                     break;
#                 uss_distance = int.from_bytes(self.data, byteorder="little"); #raspbian byteorder is 'little'
#                 print("distance: {}".format(uss_distance))
#         finally:
#                 print("Closed Connection on UltrasonicSensorHandler")

def startVideoStreamHandler(host, port):
    print("starting video server")
    server = socketserver.TCPServer((host, port), VideoStreamHandler)
    server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.serve_forever()
    # t = threading.Thread(target=server.serve_forever)
    # t.setDaemon(True)
    # t.start()

#
# def startUltrasonicSensorHandler(host, port):
#     print("starting uss server")
#     server = socketserver.TCPServer((host, port), UltrasonicSensorHandler)
#     server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#     # server.serve_forever()
#     t = threading.Thread(target=server.serve_forever)
#     t.setDaemon(True)
#     t.start()

def startAutonomous():
    global host, ussPort, videoStreamPort, commandSocket, isRunning
    isRunning = True;
    # initlaize sendCommand client_socket
    commandSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    commandSocket.connect(("192.168.1.13", 8004))
    # Allow socket reuse
    commandSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # startUltrasonicSensorHandler(host, ussPort)
    startVideoStreamHandler(host, videoStreamPort)

def pauseAutonomous():
    global isRunning
    isRunning = False;

def resumeAutonomous():
    global isRunning
    isRunning = True;

def stopAutonomous():
    global commandSocket
    commandSocket.close()

# commandServerPort = 8004
# start_new_thread(startVideoStreamHandler, (host, videoStreamPort))
# start_new_thread(startUltrasonicSensorHandler,(host, ussPort))
#Threading implemenation of socket server - https://stackoverflow.com/a/8020639/7359915

# uss_distance = 0
# uss_distanceThreshold = 25

networkType = None;
wrongInput = True
while(wrongInput):
    tableInput = input(
        "What type of Network model?\n\t-SteeringAngle (s)\n\t-DiscreteTurns (d)\n")
    if(tableInput == 's'):
        networkType = TrainType.SteerAngles
        wrongInput = False;
    elif(tableInput =='d'):
        networkType = TrainType.DiscreteTurns
        wrongInput = False;
    else:
        print("Wrong input, Please type in 's' for SteeringAngleData or 'd' for DiscreteTurnsData")

networkDirectory = input("Path to folder of Network Model: ")

prediction = None;
oldPrediction = None;
lastPredictionTime = 0

#--traffic light--
# isClassifyingTrafficLight = False;
# trafficLightPrediction = ''
# # previousTrafficLightPrediction = ''
# differentPreviousTrafficLightPrediction = '' #holds the previous light prediction, but only updates if its a new prediction
# thresholdColorAbundance = 0.6

#--traffic light distance calculation parameters--- **in OneNote
focalLength = 271.625
knownWidth = 8 #known width of traffic light
minTrafficLightDistance = 60

isRunning = False

host = "192.168.1.7"
videoStreamPort = 8000
ussPort = 8002

top = Tk()
top.geometry("500x500")
startAutonomousButton = Button(top, text="Start Autonomous", command=startAutonomous)
startAutonomousButton.place(x=50,y=50)

stopAutonomousButton = Button(top, text="Stop Autonomous", command=stopAutonomous)
stopAutonomousButton.place(x=50, y=100)

pauseButton = Button(top, text="Pause ", command=pauseAutonomous)
pauseButton.place(x=200,y=50)

resumeButton = Button(top, text="resume ", command=resumeAutonomous)
resumeButton.place(x=200,y=100)

top.mainloop()

atexit.register(commandSocket.close) #close socket before closing

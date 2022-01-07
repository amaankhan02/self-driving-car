"""
Same as Server.py, but instead of discrete values (left, right, forward), that is being
stored, it is steering angles between -15 to +15
"""

from time import gmtime, strftime
import gzip
import sys
import json
sys.path.insert(0,'/home/pi/SDC_Project/RaspberryPi/Hardware')
from _thread import *
import time;
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np
import os
import socket
from TwoMotorDriver import TwoMotorDriver
from Motor import Motor
from GpioMode import GpioMode
from SteerMotor import ServoSteerMotor
from BackMotor import BackMotor
from Commands import Commands
from Framelet import Framelet
import queue
import pickle
import os;
import datetime as dt
import argparse
from enum import Enum

class CollectingDataType(Enum):
    DiscreteTurns = 0,
    SteerAngles = 1

class CollectingTrainingData:
    def __init__(self, steerMotorCenterAngle, backMotor, steerMotor, dataFilepath):
        # self.collectingDataType = collectingDataType.value;

        self.tripQueue = queue.Queue()  #FIFO (first in, first out)
        self.isMovingForward = False

        self.speed = 35; #TODO: Added because not using Driver class

        self.isPaused = False;
        self.pickleSaveCount = 1;
        # self.pickle_filename = "/RoboticFiles/training_directory/data_{}.pickle"
        self.dataFilepath = dataFilepath;
        self.pickle_filename = os.path.join(self.dataFilepath, 'training_data/data_{}')
        # self.pickle_filename = "/home/pi/PiRoboticFiles/SteeringAngleData/training_data/data_{}"
        # self.discardPickle_filename = "/RoboticFiles/discarded_directory/data_{}.pickle"
        self.discardPickle_filename = os.path.join(self.dataFilepath, 'discarded_data/discarded_{}')
        # self.discardPickle_filename = "/home/pi/PiRoboticFiles/SteeringAngleData/discarded_data/discarded_{}"
        self.serverRunning = False;
        self.frameCount = 1
        self.startClicks = 0;

        self.steerMotorCenterAngle = steerMotorCenterAngle #the angle of servo where the steering wheels are centered (usually around 125) (range of 0 - 180)
        # Range of -10 to +10, This is stored in training data, and input param as steerMotor.setDegree()
        self.steerDegree = 0 #holds the current steer degree
        self.backMotor = backMotor
        self.steerMotor = steerMotor
        # self.InitMotors(steerMotorCenterAngle)
        self.InitServer()

    def getTimeStamp(self):
        return dt.datetime.fromtimestamp(time.time()).strftime('%Y.%m.%d %H.%M.%S')


    def InitServer(self):
        self.HOST = ''  # Symbolic name meaning all available interfaces
        self.PORT = 5000  # Arbitrary non-privileged port #TODO: try change port from 5000 to diff. - flask uses port 5000

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Allow socket reuse
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.sock.bind((self.HOST, self.PORT))
        except socket.error as msg:  # TODO: Change to python2.7 version if error - socket.error, msg
            print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
            sys.exit()
        self.sock.listen(10)

    # def InitMotors(self, steerMotorCenterAngle):
    #     #NOTE: These are the old ones, before changing the wires of BM in Motor Driver to the Steer Motor inputs (input 1 and 2)
    #     # BM_ForwardPin = 13
    #     # BM_ReversePin = 15
    #     # BM_pwmPin = 12
    #     BM_ForwardPin = 11
    #     BM_ReversePin = 7
    #     BM_frequency = 60
    #     BM_pwmPin = 16
    #
    #     SM_pwmPin = 3
    #     SM_frequency = 50
    #
    #     self.backMotor = BackMotor(Motor(BM_ForwardPin, BM_ReversePin, BM_pwmPin, BM_frequency))
    #     self.steerMotor = ServoSteerMotor(SM_pwmPin, GpioMode.BOARD, steerMotorCenterAngle, SM_frequency)
    #     self.steerMotor.setDegree(0) #center it

    def StartServer(self):
        self.serverRunning = True;
        try:
            while self.serverRunning:
                # initialize socket server
                self.sock.listen(10)
                print("waiting")
                conn, addr = self.sock.accept()
                print('Connected with ' + addr[0] + ':' + str(addr[1]))

                self.listen(conn,self.tripQueue)
        except KeyboardInterrupt:
            pass
        finally:
            print("exiting")
            try:
                self._stopAllMotors()
                self.backMotor.cleanup()
                self.steerMotor.cleanup()
            except:
                pass
            self.sock.close()
            time.sleep(0.1)  # wait a little for threads to finish
            #TODO: Stop recording and save current data
            #TODO: Add way to wait for thread to finish then close program

    def record(self):
        # initialize the camera and grab a reference to the raw camera capture
        camera = PiCamera()
        camera.resolution = (320, 240)
        camera.framerate = 30
        rawCapture = PiRGBArray(camera, size=(320, 240))

        t0 = time.time()

        try:
            for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
                # raw NumPy array representing the image
                image = frame.array

                if self.isPaused == False: #only add framelet when not paused training
                    if(self.isMovingForward): #only save the data that where car is moving
                        self.tripQueue = self.AssembleWithSteerDegree(self.tripQueue, image, self.steerDegree,self.frameCount)

                    #check if should save data
                    if(self.frameCount % 125 == 0): #300frames is 10 seconds #125 is 1/4 the track
                        print("self.tripQueue size = {}".format(self.tripQueue.qsize()))
                        t1 = time.time()
                        # tempQ = queue.Queue()  #make copy of queue to save
                        # for i in self.tripQueue.queue: #transfer elements to new queue
                        #     tempQ.put(i)
                        tripList = [item for item in self.qdumper(self.tripQueue)]

                        start_new_thread(self.SaveToPickle,(tripList,self.pickle_filename.format(self.getTimeStamp()),));
                        # start_new_thread(self.SaveCompressedToPickle, (tempQ, self.pickle_filename.format(self.getTimeStamp()),));
                        self.pickleSaveCount+=1
                        with self.tripQueue.mutex: #thread safe for clearing
                            self.tripQueue.queue.clear()
                        print("\t{0:.2f} Seconds for 300 Frames".format(t1-t0))

                    # show image on screen
                    # cv2.imshow('i', image)
                    if (self.isMovingForward):
                        self.frameCount += 1

                # clear the stream in preparation for the next frame -- IMPORTANT
                rawCapture.truncate(0)
                # if cv2.waitKey(1) & 0xFF == ord("q"):
                #     break

        # except Exception as e:
        #     print("---EXCEPTION OCCURED-----\n{}".format(e))
        finally:
            cv2.destroyAllWindows()
            camera.close()
            self.sock.close()
            print("closing recording")

    def qdumper(self,q):
        for i in q.queue:
            yield i

    ## DONT COMPRESS --> TO SLOW...
    def SaveCompressedToPickle(self, tripQueue, filename):
        print("-----STARTING TO PICKLE COMPRESSED-----------")
        t0 = time.time()
        file = gzip.GzipFile(filename, 'wb')
        remaining = [item for item in self.qdumper(tripQueue)]  # convert to list, not queue, b/c pickle can't save a queue
        pickle.dump(remaining, file, 4)  # 4 - protocol that is the latest protocol
        file.close()
        t1 = time.time()
        print('---------FINISHED PICKLING COMPRESSED-----------\n{0:.2f}seconds'.format(t1 - t0))

    def SaveToPickle(self, tripList, filename):
        print("-----STARTING TO PICKLE-----------")
        t0 = time.time()
        pickle_out = open(filename + '.pickle', "wb")
        # file = gzip.GzipFile(filename,'wb')

        #framelet_list file to upload = remaining
        # remaining = [item for item in self.qdumper(tripQueue)] #convert to list, not queue, b/c pickle can't save a queue

        print("'remaining' array size: {}".format(len(tripList)))

        pickle.dump(tripList,pickle_out, 4)
        # pickle.dump(remaining,file,-1) #-1 protocol gets the latest protocol

        pickle_out.close()
        #filename + '-frameCount-{}'.format(len(remaining)) +'_ready.pickle'
        newFileName = "{0}-frameCount-{1:03}_ready.pickle".format(filename, len(tripList))   #newFileNameFormat = data_2017.11.16 21.55.25-frameCount-125_ready.pickle
        os.rename(filename + '.pickle',newFileName)
        # file.close()
        t1 = time.time()
        print('---------FINISHED PICKLING-----------\n{0:.2f}seconds'.format(t1-t0))

    '''Throws a ValueError: setting an array elemetn with a sequence'''
    def SaveToNpz(self, tripQueue, directory):
        print("--------saving to npz--------")
        t0 = time.time()
        frameList = []
        cmdList = []
        frameNameList = []
        print("tripQueue.size = {}".format(tripQueue.qsize()))
        for i in tripQueue.queue:
            frameNameList.append(i.frameName)
            frameList.append(i.frame)
            cmdList.append(i.cmd)

        print("frameList length = {}".format(len(frameList)))

        #save data
        file_name = strftime("%m.%d.%Y_%H.%M", gmtime())
        if not os.path.exists(directory):
            os.makedirs(directory)
        try:
            np.savez(directory + '/' + file_name + '.npz', frameName=frameNameList, frame=frameList,
                     cmd=cmdList);
            t1 = time.time()
            print("------Saved data to npz file!------- {0:.2f}ms".format((t1-t0)*1000))

        except IOError as e:
            print(e)

    def _stopAllMotors(self):
        self.backMotor.Stop()
        self.steerDegree = 0
        self.steerMotor.turn(self.steerDegree*10)  # reset to center
        self.steerMotor.offMotor()  # off motor

    def _bytesToString(self, input):
        input = input.decode("utf-8")
        return input

    def AssembleWithCmd(self, tripQueue, image, cmd, frameCount):
        name = "frame_{}".format(frameCount)
        tripQueue.put(Framelet(name, image, cmd))
        return tripQueue
        #TODO: Bug: cmds is a list of cmds sometimes (when the SS is sent fast), so i shoudld be adding all of them, but can only add the last cmd in the list. If want to add the whole thing
            #TODO: then i must make Listen() a totally different thread altogether and should be called once and the UpdateFramelet() should be called from there

    def AssembleWithSteerDegree(self, tripQueue, image, steerDegree, frameCount):
        name = "frame_{}".format(frameCount)
        tripQueue.put(Framelet(name, image, steerDegree=steerDegree))
        return tripQueue

    def ExecuteCommand(self, data, tripQueue):
        '''
        executes the commands from data recieved in socket server, also
        changes boolean values representing the movement of car
        :param data: data recieved from socket server
        '''
        # cmds = []
        if data is None:
            return
        for i in range(len(data) - 1):
            if data[i] == ',':  # STOP ALL MOTORS
                # self.driver.StopAll()
                self._stopAllMotors()
                print("stop all")
                # cmds.append(Commands.STOP_ALL_MOTORS.value)
                self.isMovingForward = False
            elif data[i][0:2] == 'SS':
                self.speed = int(data[i][2:])  # get second half of data with the number for speed
                print("Speed: {}".format(self.speed))
                if (self.isMovingForward):
                    self.backMotor.Forward(self.speed)
                # elif (self.isMovingBackward):
                #     self.twoMotorDriver.Reverse(self.speed)
                # self.driver.Speed(int(speed))
                #todo: add speed command to training data
            elif data[i][0:2] == 'SA': #Steering Angle Change
                self.steerDegree = int(data[i][2:]) #get second half of data with the number for steer angle
                self.steerMotor.turn(self.steerDegree*10)
                # self.steerMotor.offMotor()
                print("Steer Degree: {}".format(self.steerDegree))
            elif data[i] == 'FF':
                print("forward")
                self.backMotor.Forward(self.speed)
                self.isMovingForward = True;
            # elif data[i] == 'BB':
            #     print("Back")
            #     self.backMotor.Reverse(self.speed)
            #     self.isMovingForward = False
            elif data[i] == '@': #PAUSE Training
                self.isPaused = True  #Pauses videorecorder
                # self.driver.StopAll()
                self._stopAllMotors()
                print("------PAUSED---")
            elif data[i] == '#': #UNPAUSE TRAINING
                self.isPaused = False; #unpauses videorecorder
                print("------UNPAUSED---")
            elif data[i] == '*': #SAVE Training - sent after paused
                t0 = time.time()
                print("tripQueue size = {}".format(tripQueue.qsize()))
                # tempQ = queue.Queue()  # make copy of queue to save
                # for i in tripQueue.queue:  # transfer elements to new queue
                #     tempQ.put(i)
                tripList = [item for item in self.qdumper(self.tripQueue)];
                start_new_thread(self.SaveToPickle,(tripList, self.pickle_filename.format(self.getTimeStamp()),));
                self.pickleSaveCount += 1
                with tripQueue.mutex:  # thread safe for clearing
                    tripQueue.queue.clear()
                t1 = time.time()
                print("\t{0:.2f} Seconds for 300 Frames".format(t1 - t0))
            elif data[i] == '&': #DISCARD Training
                t0 = time.time()
                print("--------DISCARDING DATA ----\ntripQueue size = {}".format(tripQueue.qsize()))
                # tempQ = queue.Queue()  # make copy of queue to save
                # for i in tripQueue.queue:  # transfer elements to new queue
                #     tempQ.put(i)
                #start_new_thread(self.SaveToPickle,(tempQ, self.discardPickle_filename.format(self.getTimeStamp()),));
                #DELETE DISCARDED QUEUE
                with tripQueue.mutex:  # thread safe for clearing
                    tripQueue.queue.clear()
                # self.pickleSaveCount += 1

                t1 = time.time()
                print("\t{0:.2f} Seconds for 500 Frames".format(t1 - t0))
            elif data[i] ==':': #START TRAINING
                self.startClicks += 1
                # self.isMovingForward = True; #TODO; should i do this?????
                if(self.startClicks == 1): #if first time pressing start
                    start_new_thread(self.record, ()) #start new recording thread
                else:
                    self.isPaused = False;  # unpauses videorecorder
                    print("------UNPAUSED---FROM START CMD")
            else:
                print("Bad Command")
            # return cmds

    def listen(self, conn, tripQueue):
        while True:
            data = conn.recv(1024)
            if not data:
                print("socket closed")
                break;

            data = self._bytesToString(data)
            #split by delimeter
            data = data.split(';\n')
            self.ExecuteCommand(data, tripQueue)

def saveRecentSteerMotorCenterAngle(steerAngle, file):
    try:
        data = {"RecentSteerServoMotorAngle": steerAngle};
        with open(file, 'w') as f:
            json.dump(data, f, indent=4, separators=(',', ': '));
    except Exception as e:
        print("Error while saving RecentSteerServoMotorAngle to JSON, could not save")

if __name__ == "__main__":
    jsonFilePath = '/home/pi/PiRoboticFiles/CollectingTrainingData/ExtraInfo.json'
    #get most recent steer servo motor angle from JSON file
    with open(jsonFilePath) as json_file:
        data = json.load(json_file)
        recentServoMotorAngle = int(data['RecentSteerServoMotorAngle'])

    BM_ForwardPin = 11
    BM_ReversePin = 7
    BM_pwmPin = 16
    BM_frequency = 60

    SM_pwmPin = 3
    SM_frequency = 50

    backMotor = BackMotor(Motor(BM_ForwardPin, BM_ReversePin, BM_pwmPin, BM_frequency))
    steerMotor = ServoSteerMotor(SM_pwmPin, GpioMode.BOARD, recentServoMotorAngle, SM_frequency)
    # steerMotor.setDegree(0)  # center it

    newSteerMotorCenterAngle = recentServoMotorAngle;
    while True:
        msg = "Test the Steer Angle for Center. Enter a steer Angle: (most recent: {})".format(recentServoMotorAngle)
        inputSteerAngle = int(input(msg))
        steerMotor.setCenterAngle(inputSteerAngle)
        steerMotor.turn(0)
        time.sleep(1.5)
        goodBad = input("Is that good or bad? (Good=g or Bad=b'") #input g or b
        if(goodBad == 'g'):
            newSteerMotorCenterAngle = inputSteerAngle;
            saveRecentSteerMotorCenterAngle(newSteerMotorCenterAngle, jsonFilePath)
            break;
        elif(goodBad !='b'): #not valid input
            print("Bad input, Type 'g' or 'b' for good/bad")

    ctd = CollectingTrainingData(newSteerMotorCenterAngle, backMotor, steerMotor, "/home/pi/PiRoboticFiles/SteeringAngleData/")
    ctd.StartServer()
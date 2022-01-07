'''
Same as server.py, but uses the Driver class instead of TwoMotorDriver class
'''
from time import gmtime, strftime
import gzip
import sys
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
from Driver import Driver
from Commands import Commands
from Framelet import Framelet
import queue
import pickle

class CollectingTrainingData:
    def __init__(self):
        self.tripQueue = queue.Queue()  #FIFO (first in, first out)
        self.isMovingForward = False
        self.isMovingBackward = False
        self.isTurningLeft = False
        self.isTurningRight = False

        self.speed = 35; #TODO: Added because not using Driver class
        self.SM_speed = 85; #How much speed to apply when turning

        self.isPaused = False;
        self.pickleSaveCount = 1;
        self.pickle_filename = "data_{}.pickle"
        self.serverRunning = False;
        self.frameCount = 1
        self.startClicks = 0;

        self.InitMotors()
        self.InitServer()


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

    def InitMotors(self):
        BM_ForwardPin = 13
        BM_ReversePin = 15
        BM_pwmPin = 12

        SM_LeftPin = 7
        SM_RightPin = 11
        SM_pwmPin = 16

        Frequency = 60

        twoMotorDriver = TwoMotorDriver(Motor(BM_ForwardPin, BM_ReversePin, BM_pwmPin, Frequency),
                                        Motor(SM_LeftPin, SM_RightPin, SM_pwmPin, Frequency))
        self.driver = Driver(twoMotorDriver)

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
                self.driver.StopAll()  # STop the arm if we get here in error
                self.driver.cleanup()
                # self.twoMotorDriver.StopAll()
                # self.twoMotorDriver.cleanup()
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
        global cmd;

        try:
            for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
                # raw NumPy array representing the image
                image = frame.array

                if self.isPaused == False: #only add framelet when not paused training
                    if(self.isTurningRight):
                        cmd = Commands.RIGHT.value
                    elif(self.isTurningLeft):
                        cmd = Commands.LEFT.value
                    elif(self.isMovingForward):
                        cmd = Commands.FORWARD.value
                    elif(self.isMovingBackward):
                        cmd = Commands.BACK.value
                    else:
                        cmd = Commands.NO_CMD.value

                    self.tripQueue = self.Assemble(self.tripQueue, image, cmd, self.frameCount)

                    #check if should save data
                    if(self.frameCount % 500 == 0): #300frames is 10 seconds
                        print("self.tripQueue size = {}".format(self.tripQueue.qsize()))
                        t1 = time.time()
                        tempQ = queue.Queue()  #make copy of queue to save
                        for i in self.tripQueue.queue: #transfer elements to new queue
                            tempQ.put(i)
                        start_new_thread(self.SaveToPickle,(tempQ,'training_directory',self.pickle_filename.format(self.pickleSaveCount),));
                        self.pickleSaveCount+=1
                        with self.tripQueue.mutex: #thread safe for clearing
                            self.tripQueue.queue.clear()
                        print("\t{0:.2f} Seconds for 300 Frames".format(t1-t0))

                    # show image on screen
                    # cv2.imshow('i', image)
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

    def SaveToPickle(self, tripQueue, directory, filename):
        print("-----STARTING TO PICKLE-----------")
        t0 = time.time()
        pickle_out = open(filename, "wb")
        # file = gzip.GzipFile(filename,'wb')
        remaining = [item for item in self.qdumper(tripQueue)]

        print("'remaining' array size: {}".format(len(remaining)))

        pickle.dump(remaining,pickle_out, 4)
        # pickle.dump(remaining,file,-1) #-1 protocol gets the latest protocol

        pickle_out.close()
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

    def BytesToString(self, input):
        input = input.decode("utf-8")
        return input

    def Assemble(self, tripQueue, image, cmd, frameCount):
        name = "frame_{}".format(frameCount)
        tripQueue.put(Framelet(name, image, cmd))
        return tripQueue
        #TODO: Bug: cmds is a list of cmds sometimes (when the SS is sent fast), so i shoudld be adding all of them, but can only add the last cmd in the list. If want to add the whole thing
            #TODO: then i must make Listen() a totally different thread altogether and should be called once and the UpdateFramelet() should be called from there

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
            if data[i] == '.':  # STOP BACK MOTOR
                self.driver.StopBM()
                # self.twoMotorDriver.StopBM()
                print("stop bm")
                # cmds.append(Commands.BACK_MOTOR_STOP.value)
                self.isMovingBackward = False
                self.isMovingForward = False
            elif data[i] == '-':  # RESET STEER
                self.driver.ResetSteer()
                # self.twoMotorDriver.ResetSteer()
                print("reset steer")
                # cmds.append(Commands.RESET_STEER.value)
                self.isTurningLeft = False
                self.isTurningRight = False
            elif data[i] == ',':  # STOP ALL MOTORS
                self.driver.StopAll()
                # self.twoMotorDriver.StopAll()
                print("stop all")
                # cmds.append(Commands.STOP_ALL_MOTORS.value)
                self.isMovingBackward = False
                self.isMovingForward = False
                self.isTurningLeft = False
                self.isTurningRight = False
            elif data[i][0:2] == 'SS':
                self.speed = int(data[i][2:])  # get second half of data with the number for speed
                print("Speed: {}".format(self.speed))
                # if (self.isMovingForward):
                #     self.twoMotorDriver.Forward(self.speed)
                # elif (self.isMovingBackward):
                #     self.twoMotorDriver.Reverse(self.speed)
                self.driver.Speed(int(self.speed))
                #todo: add command for speed
            elif data[i] == 'FF':
                self.driver.Forward()
                print("forward")
                # self.twoMotorDriver.Forward(self.speed)
                # cmds.append(Commands.FORWARD.value)
                self.isMovingForward = True;
                self.isMovingBackward = False;
            elif data[i] == 'BB':
                self.driver.Back();
                print("Back")
                # self.twoMotorDriver.Reverse(self.speed)
                # cmds.append(Commands.BACK.value)
                self.isMovingForward = False
                self.isMovingBackward = True;
            elif data[i] == 'LL':
                self.driver.Left()
                print("left")
                # self.twoMotorDriver.TurnLeft(self.SM_speed)
                # cmds.append(Commands.LEFT.value)
                self.isTurningLeft = True
                self.isTurningRight = False
            elif data[i] == 'RR':
                self.driver.Right()
                print("Right")
                # self.twoMotorDriver.TurnRight(self.SM_speed)
                # cmds.append(Commands.RIGHT.value)
                self.isTurningLeft = False
                self.isTurningRight = True
            elif data[i] == '@': #PAUSE Training
                self.isPaused = True  #Pauses videorecorder
                self.driver.StopAll()
                # self.twoMotorDriver.StopAll()
                print("------PAUSED---")
            elif data[i] == '#': #UNPAUSE TRAINING
                self.isPaused = False; #unpauses videorecorder
                print("------UNPAUSED---")
            elif data[i] == '*': #SAVE Training - sent after paused
                t0 = time.time()
                print("tripQueue size = {}".format(tripQueue.qsize()))
                tempQ = queue.Queue()  # make copy of queue to save
                for i in tripQueue.queue:  # transfer elements to new queue
                    tempQ.put(i)
                start_new_thread(self.SaveToPickle,(tempQ, 'training_directory', self.pickle_filename.format(self.pickleSaveCount),));
                self.pickleSaveCount += 1
                with tripQueue.mutex:  # thread safe for clearing
                    tripQueue.queue.clear()
                t1 = time.time()
                print("\t{0:.2f} Seconds for 300 Frames".format(t1 - t0))
            elif data[i] == '&': #DISCARD Training
                t0 = time.time()
                print("--------DISCARDING DATA ----\ntripQueue size = {}".format(tripQueue.qsize()))
                tempQ = queue.Queue()  # make copy of queue to save
                for i in tripQueue.queue:  # transfer elements to new queue
                    tempQ.put(i)
                start_new_thread(self.SaveToPickle,(tempQ, 'discarded_directory', 'discarded_{}.pickle'.format(self.pickleSaveCount),));
                self.pickleSaveCount += 1
                with tripQueue.mutex:  # thread safe for clearing
                    tripQueue.queue.clear()
                t1 = time.time()
                print("\t{0:.2f} Seconds for 500 Frames".format(t1 - t0))
            # elif data[i] == '$': #END TRAINING and clean up
            #     #stop recording

            # elif data[i] == '@':  # STOP current TRAINING SESSION
            #     self.driver.StopAll()
            #     self.currentTS.Pause()  # Just pause it, don't stop it completely
            #     self.TS_inProgress = False;

            # elif data[i] == ':':  # START TRAINING SESSION
            #     self.startBtnClicks += 1;
            #     if (self.startBtnClicks == 1):  # first time start is pressed
            #         self.currentTS = TrainingSession()  # Create NEW TRAINING SESSION object
            #         self.currentTS.Start();  # START the TRAINING SESSION
            #         self.TS_inProgress = True;
            #     else:  # Not the first press
            #         self.currentTS.UnPause()
            #         print("unpaused TS")
            #         self.TS_inProgress = True;
            #
            #         # if(self.TS_inProgress == False):
            #         #     self.currentTS = TrainingSession() # NEW TRAINING SESSION
            #         #     self.currentTS.Start(); #START TRAINING SESSION
            #         #     self.TS_inProgress = True;

            # elif data[i] == '$': #PAUSE TRAINING SESSION
            #     self.driver.StopAll()
            #     self.currentTS.Pause()
            #
            # elif data[i] == '%':
            #     self.currentTS.UnPause()

            # elif data[i] == '*':  # SAVE TRAINING SESSION DATA to QUEUE
            #     self.currentTS.SaveToQueue()
            #     # if(self.TS_inProgress):
            #     #     self.currentTS.Stop()
            #     #     self.TS_inProgress = False;
            #     #     self.currentTS.SaveData('training_data')

            # elif data[i] == '&':  # DISCARD TRAINING SESSION DATA
            #     # self.currentTS.SaveData('discarded_training_data')
            #     self.currentTS.DiscardCurrentData()
            #
            # elif data[i] == '$':  # Save all sessions into npz file
            #     self.currentTS.Stop()
            #     self.driver.StopAll()
            #     self.currentTS.SaveAllSessionsToNpz('training_data')
            elif data[i] ==':': #START TRAINING
                self.startClicks += 1
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

            data = self.BytesToString(data)
            #split by delimeter
            data = data.split(';\n')
            self.ExecuteCommand(data, tripQueue)


if __name__ == "__main__":
    ctd = CollectingTrainingData()
    ctd.StartServer()
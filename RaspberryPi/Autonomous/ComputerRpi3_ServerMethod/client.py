"""
Sends Video Frames and Distance Measurement and recieve cmds for motor
"""
import threading
import io
import socket
import struct
import time
import picamera
import sys
import json
sys.path.insert(0,'/home/pi/SDC_Project/RaspberryPi/Hardware')
from UltrasonicSensor import UltrasonicSensor
from UltrasonicSensorSet import UltrasonicSensorSet
from Motor import Motor
from GpioMode import GpioMode
from _thread import *
import socketserver
from BackMotor import BackMotor
from SteerMotor import ServoSteerMotor, AbstractSteerMotor, MotorDriverSteerMotor
from NetworkType import NetworkType;



#used with VideoStreamHandler to send the frames
class SplitFrames:
    def __init__(self, connection):
        self.connection = connection
        self.stream = io.BytesIO()
        self.count = 0

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # Start of new frame; send the old one's length
            # then the data
            size = self.stream.tell()
            if size > 0:
                # struct.pack(fmt, v1,v2,..) --> returns a bytes objcect containing values v1, v2, .. packed according to the string fmt format
                self.connection.write(struct.pack('<L', size))  # TODO: don't know what connection.write does
                self.connection.flush()  # flush the data, to send right away. Explanation on flush--> https://stackoverflow.com/a/914321/7359915
                # Change the stream position to the given byte offset (the parameter) --> https://docs.python.org/3/library/io.html#io.IOBase.seek
                self.stream.seek(0)  # change stream position to beginning
                # stream.read(size) --> read up to 'size' bytes from the object and return them (if size = -1, then readall() is called)
                # if 0 bytes are return from stream.read(), and size != 0, then it indicates the end of file
                self.connection.write(self.stream.read(size))
                self.count += 1
                self.stream.seek(0)
        self.stream.write(buf)

class ClientSocket:
    def __init__(self):
        """
        :param host: Server Host
        :param videoServerPort: port for VideoStream Server
        :param ussServerPort: port for UltrasonicSensor Server
        :param ultrasonicSensor:
        :param ultrasonicSensorDistanceThreshold:
        """
        #initialize picamera
        self.camera = picamera.PiCamera(resolution='VGA', framerate=20)
        self.camera.resolution = (320,240)
        print("initialized contructor")

    def start(self, host, videoServerPort):
        print("starting videostream and uss connection")
        # initialize videostream client socket
        self.videoStreamClient_socket = socket.socket()
        self.videoStreamClient_socket.connect((host, videoServerPort))
        self.connection = self.videoStreamClient_socket.makefile('wb')
        print("connected to videoStream server")

        # try:
        output = SplitFrames(self.connection)
        time.sleep(1) #wait for 1 second
        self.camera.start_recording(output, format='mjpeg');

    def stop(self):
        self.camera.stop_recording()
        #write terminating 0-length to let server know we are done
        self.connection.write(struct.pack('<L', 0))
        self.camera.close()
        self.connection.close()
        self.videoStreamClient_socket.close()

class CommandServerHandler(socketserver.BaseRequestHandler): #TODO: BaseRequestHandler or StreamRequestHandler
    def handle(self):
        global networkType
        try:
            if networkType.value == NetworkType.DiscreteTurns.value:
                while True:
                    data = self.request.recv(1024)
                    if not data:
                        print("command socket closed")
                        break;
                    data = data.decode("utf-8") #convert bytes to string
                    # split by delimeter
                    data = data.split(';');
                    executeDiscreteTurnCommand(data)
            elif networkType.value == NetworkType.SteerAngles.value:
                while True:
                    data = self.request.recv(1024)
                    if not data:
                        print("command socket closed")
                        break;
                    data = data.decode("utf-8")
                    data = data.split(';');
                    # data = int.from_bytes(data,byteorder='little', signed=True);
                    executeSteerAngleCommand(data)

        finally:
            print("closed connection with CommandServerHandler")

def executeAndroidCommand(data):
    global isRunning, backMotorSpeed, isStopped;
    if data is None:
        return
    for i in range(len(data) - 1):
        if data[i] == '^': #START AUTONOMOUS
            isRunning = True;
        elif data[i] == '%': #STOP AUTONOMOUS
            isRunning == False;
            isStopped = True
        elif data[i][0:2] == 'SS':
            backMotorSpeed = int(data[i][2:])
        else:
            print("Bad Command -- executeAndroidCommand()");

def stopAllMotors():
    global backMotor, steerMotor, isMovingBackward,isMovingForward
    backMotor.Stop()
    # steerMotor.turn(0)  # reset to center
    steerMotor.offMotor()  # off motor

def listenAndroidServer(conn):
    global isRunning, backMotorSpeed;
    while True:
        data = conn.recv(1024)
        if not data:
            print("lost connection with Android server")
            break;

        data = data.decode("utf-8")  # Convert bytes to string
        # split by delimeter
        data = data.split(';\n')
        executeAndroidCommand(data)

def measureDistance(ultrasonicSensorSet):
    """
    :param ultrasonicSensor:
    :param waitSeconds:
    :return:
    """
    global ussDistance, isStopped, ussDistanceThreshold, currentCmd
    while True:
        ussDistance = int(min(ultrasonicSensorSet.getDistances())) #get minimum distance from the sensor set
        if(isStopped == False and ussDistance <= ussDistanceThreshold):
            stopAllMotors()
            isStopped = True
            print("STOP -- TOO CLOSE: Distance {}cm".format(ussDistance))
        elif(isStopped == True and ussDistance > ussDistanceThreshold):
            isStopped = False
            executeMotors(currentCmd)


def executeSteerAngleCommand(data):
    global backMotorSpeed, isRunning, ussDistance, ussDistanceThreshold, isStopped, backMotor, steerMotor, currentCmd
    if data is None:
        return
    if (isRunning == True):
        if (ussDistance > ussDistanceThreshold):  # check if enough distance infront to move
            for i in range(len(data) - 1):
                if(data[i] == "*"): #STOP ALL MOTORS
                    stopAllMotors()
                    print("STOP")
                else:
                    backMotor.Forward(backMotorSpeed)
                    degree = int(data[i])
                    steerMotor.turn(degree * 10)
                    print(degree)
                    currentCmd = degree
            # backMotor.Forward(backMotorSpeed)
            # print(data)
            # steerMotor.setDegree(data)

def executeMotors(cmd):
    print(cmd)
    cmd = cmd.lower()
    if(cmd == "stop"):
        stopAllMotors()
    elif(cmd == "left"):
        steerMotor.turn(-1 * discreteTurnsSteerMotorSpeed)
        backMotor.Forward(backMotorSpeed)
    elif(cmd == "right"):
        steerMotor.turn(discreteTurnsSteerMotorSpeed)
        backMotor.Forward(backMotorSpeed)
    elif(cmd == "forward"):
        backMotor.Forward(backMotorSpeed)
        steerMotor.turn(0)
    elif(cmd == "back"):
        backMotor.Reverse(backMotorSpeed)
        steerMotor.turn(0)

def executeDiscreteTurnCommand(data):
    """
    Executes cmds from computer
    :param data:
    :return:
    """
    global backMotorSpeed, isRunning, ussDistance, ussDistanceThreshold, isStopped, backMotor, steerMotor, currentCmd
    if data is None:
        return
    if(isRunning == True ):
        #TODO: Bring back Ultrasonic Sensor Reading when connected
        if(ussDistance > ussDistanceThreshold): #check if enough distance infront to move
            for i in range(len(data) - 1):
                if data[i] == '*': #STOP_ALL_MOTORS
                    isStopped = True
                    currentCmd = 'STOP';
                elif data[i] == 'L': #LEFT
                    isStopped = False
                    currentCmd = 'Left';
                elif data[i] == 'R': #RIGHT
                    isStopped = False
                    currentCmd = 'Right';
                elif data[i] == 'F': #FORWARD
                    isStopped = False
                    currentCmd = 'Forward';
                elif data[i] == 'B': #BACK -- DEPRECATED #todo: remove backward cmd, never in use
                    isStopped = False
                    currentCmd = 'Back';
                else:
                    currentCmd = None
                    print("bad command recieved")
                executeMotors(currentCmd);


def startCommandServerHandler(host, port):
    print("starting command server")
    server = socketserver.TCPServer((host, port), CommandServerHandler)
    server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    t = threading.Thread(target=server.serve_forever)
    t.setDaemon(True)
    t.start()

def getAndroidServerHandler(host, port):
    print("starting android server")
    # server = socketserver.TCPServer((host, port), AndroidServerHandler)
    # server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # t = threading.Thread(target=server.serve_forever)
    # t.setDaemon(True)
    # t.start()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.connect((host, port))
    return s

def saveRecentSteerMotorCenterAngle(steerAngle, file):
    try:
        data = {"RecentSteerServoMotorAngle": steerAngle};
        with open(file, 'w') as f:
            json.dump(data, f, indent=4, separators=(',', ': '));
    except Exception as e:
        print("Error while saving RecentSteerServoMotorAngle to JSON, could not save")


jsonFilePath = '/home/pi/PiRoboticFiles/CollectingTrainingData/ExtraInfo.json'
#get most recent steer servo motor angle from JSON file
with open(jsonFilePath) as json_file:
    data = json.load(json_file)
    recentServoMotorAngle = int(data['RecentSteerServoMotorAngle'])

backMotorSpeed = 31
isStopped = False; #when motor is stopped

# initialize hardware
uss1 = UltrasonicSensor(29, 31, GpioMode.BOARD)
uss2 = UltrasonicSensor(18, 22, GpioMode.BOARD)
uss3 = UltrasonicSensor(38, 40, GpioMode.BOARD)
frontSensors = UltrasonicSensorSet(uss1,uss2,uss3)
ussDistance = 0
ussDistanceThreshold = 50

BM_ForwardPin = 11
BM_ReversePin = 7
BM_pwmPin = 16
BM_frequency = 60

backMotor = BackMotor(Motor(BM_ForwardPin, BM_ReversePin, BM_pwmPin, BM_frequency))
steerMotor = AbstractSteerMotor() #Initialized below when input NetworkType
discreteTurnsSteerMotorSpeed = 95

currentCmd = ""; #holds the current command received by computer

isRunning = True; #holds value of its predicting

HOST = "192.168.1.7" #Computer
videoStreamPort = 8000
# ussServerPort = 8002
commandServerPort = 8004
commandServerHost = "192.168.1.13" #Pi

clientPi = ClientSocket()
isClientPiRunning = False

networkType = None;
wrongInput = True
while(wrongInput):
    tableInput = input(
        "What type of Network model?\n\t-SteeringAngle (s)\n\t-DiscreteTurns (d)\n")
    if(tableInput == 's'):
        networkType = NetworkType.SteerAngles
        wrongInput = False;
    elif(tableInput =='d'):
        networkType = NetworkType.DiscreteTurns
        wrongInput = False;
    else:
        print("Wrong input, Please type in 's' for SteeringAngleData or 'd' for DiscreteTurnsData")


if(networkType.value == NetworkType.SteerAngles.value):
    SM_pwmPin = 3
    SM_frequency = 50
    steerMotor = ServoSteerMotor(SM_pwmPin, GpioMode.BOARD, recentServoMotorAngle, SM_frequency)

    newSteerMotorCenterAngle = recentServoMotorAngle;
    while True:
        msg = "Test the Steer Angle for Center. Enter a steer Angle: (most recent: {})".format(recentServoMotorAngle)
        inputSteerAngle = int(input(msg))
        steerMotor.setCenterAngle(inputSteerAngle)
        steerMotor.turn(0)
        goodBad = input("Is that good or bad? (Good=g or Bad=b'")  # input g or b
        if (goodBad == 'g'):
            newSteerMotorCenterAngle = inputSteerAngle;
            saveRecentSteerMotorCenterAngle(newSteerMotorCenterAngle, jsonFilePath)
            break;
        elif (goodBad != 'b'):  # not valid input
            print("Bad input, Type 'g' or 'b' for good/bad")
elif(networkType.value == NetworkType.DiscreteTurns.value):
    SM_LeftPin = 13
    SM_RightPin = 15
    SM_pwmPin = 12
    SM_frequency = 60
    steerMotor = MotorDriverSteerMotor(Motor(SM_LeftPin, SM_RightPin, SM_pwmPin, SM_frequency))


try:
    # start_new_thread(smoothSteering, (0.2,))
    startCommandServerHandler(commandServerHost, commandServerPort)
    clientPi.start(HOST, videoStreamPort)
    measureDistance(frontSensors) #loop indefinitely

finally:
    clientPi.stop()
    frontSensors.cleanup()
    stopAllMotors()
    print("Exiting...")
    time.sleep(0.1) #wait a little for threads to finish


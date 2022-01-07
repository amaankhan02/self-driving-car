import sys
sys.path.insert(0,'/home/pi/SDC_Project/RaspberryPi/Hardware')
from _thread import *
import socket
from TwoMotorDriver import TwoMotorDriver
from Motor import Motor
from UltrasonicSensor import UltrasonicSensor
from GpioMode import GpioMode
from Autonomous import Autonomous
from KerasConvNetModel import KerasConvNetModel
import argparse

startClicks = 0

def getModel():
    # ues argparse to get directory of model from cmd line
    # parser = argparse.ArgumentParser()
    # parser.add_argument("directory", help="Pass in the Neural Network Saved Directory")
    # args = parser.parse_args()
    # directory = args.directory;
    directory = '/home/pi/SDC_Project/Computer/NeuralNetworkModels/CNN/11.17.17/Trial1Keras/'
    return KerasConvNetModel(str(directory))

def getTwoMotorDriver():
    BM_ForwardPin = 13
    BM_ReversePin = 15
    BM_pwmPin = 12

    SM_LeftPin = 7
    SM_RightPin = 11
    SM_pwmPin = 16

    Frequency = 60

    return TwoMotorDriver(Motor(BM_ForwardPin, BM_ReversePin, BM_pwmPin, Frequency),
                                    Motor(SM_LeftPin, SM_RightPin, SM_pwmPin, Frequency))

def bytesToString(self, input):
    input = input.decode("utf-8")
    return input

def listen(conn, autonomous):
    global startClicks;

    while True:
        data = conn.recv(1024)
        if not data:
            print("socket closed")
            break;

        data = bytesToString(data)
        # split by delimeter
        data = data.split(';\n')
        if data is None:
            return
        for i in range(len(data) - 1):
            if data[i][0:2] == 'SS':
                speed = int(data[i][2:])  # get second half of data with the number for speed
                autonomous.setSpeed(speed)
                print("Speed: {}".format(speed))
            elif data[i] == '^':  # START AUTONOMOUS
                startClicks += 1
                if (startClicks == 1):  # if first time pressing start
                    start_new_thread(autonomous.start, ())  # start new recording thread
                else:
                    autonomous.resume()
                    print("------UNPAUSED---FROM START CMD")
            elif data[i] == '%': #STOP AUTONOMOUS
                autonomous.pause()
                print("STOPPED AUTONOMOUS")
            else:
                print("Bad Command")

TRIG = 18  # TRIG - PIN 18 (GPIO 24)
ECHO = 22  # ECHO - PIN 22 (GPIO 25)
uss1 = UltrasonicSensor(TRIG, ECHO, GpioMode.BOARD)
model = getModel()
twoMotorDriver = getTwoMotorDriver()

car = Autonomous(model,twoMotorDriver,uss1,15, 35,95)



#----INITIALIZE SOCKET-----
HOST = '' # Symbolic name meaning all available interfaces
PORT = 5000 # Arbitrary non-privileged port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Allow socket reuse
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    s.bind((HOST,PORT))
except socket.error as msg:  #TODO: Change to python2.7 version if error - socket.error, msg
    print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    sys.exit()

s.listen(10)

running = True;
try:
    while running:
        print("Waiting ...")
        # Wait to accept connection from client control app
        conn, addr = s.accept()
        print('Connected with ' + addr[0] + ':' + str(addr[1]))

        # Start listening
        listen(conn, car)
finally:
    print("exiting")
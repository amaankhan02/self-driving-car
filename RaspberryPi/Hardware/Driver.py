#TODO: Combine Driver.py into TwoMotorDriver OR add this code into CAR class

import socket
import time
from _thread import *
from TwoMotorDriver import TwoMotorDriver
from Motor import Motor


# Motor Helper class
class Driver:
    def __init__(self, twoMotorDriver):
        self.motors = twoMotorDriver

        self.BM_speed = 40
        self.SM_speedIncrement = 90  #How much to increase steering angle each call to turn *Max is angle 90
        self.SM_currentAngle = 0
        self.isMovingForward = False;
        self.isMovingBack = False;
        self.isTurningLeft = False
        self.isTurningRight = False

    def StopAll(self):
        print("stopped all motors")
        self.motors.StopAll()
        self.isMovingForward = False;
        self.isMovingBack = False
        self.SM_currentAngle = 0

    def StopBM(self):
        print("Stop back motor")
        self.motors.StopBM()
        self.isMovingForward = False;
        self.isMovingBack = False

    def ResetSteer(self):
        print("reset steer")
        self.motors.ResetSteer();
        self.SM_currentAngle = 0;

    def Forward(self):
        self.isMovingForward = True;
        self.isMovingBack = False;
        self.motors.Forward(self.BM_speed)
        print("Moving forward at speed " + str(self.BM_speed))

    def Back(self):
        self.isMovingForward = False;
        self.isMovingBack = True
        self.motors.Reverse(self.BM_speed)
        print("Moving backward at speed " + str(self.BM_speed))

    def Left(self):
        if (self.SM_currentAngle > -90):
            self.SM_currentAngle -= self.SM_speedIncrement
        else:
            self.SM_currentAngle = -90
        self.motors.Turn(self.SM_currentAngle)

    def Right(self):
        if (self.SM_currentAngle < 90):
            self.SM_currentAngle += self.SM_speedIncrement
        else:
            self.SM_currentAngle = 90
        self.motors.Turn(self.SM_currentAngle)

    def Speed(self, s):
        self.BM_speed = s;
        print("speed: %s" % self.BM_speed)

        # driver.setSpeed(BM_speed)
        if (self.isMovingForward):
            self.motors.Forward(self.BM_speed)
        elif (self.isMovingBack):
            self.motors.Reverse(self.BM_speed)

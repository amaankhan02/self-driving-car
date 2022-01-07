import RPi.GPIO as gpio
import time
from Motor import Motor


"""
For the Steer Motor and back motor, not the servo motor steering that I added
"""
class TwoMotorDriver:
    def __init__(self, backMotor, steerMotor):
        self._BM = backMotor
        self._SM = steerMotor

    def StopAll(self):
        '''self._BM.setSpeed(0)
        self._SM.setSpeed(0)
        self._BM.Stop()
        self._SM.Stop()'''
        self.StopBM()
        self.ResetSteer()

    def StopBM(self):
        self._BM.setSpeed(0)
        self._BM.Stop()

    def ResetSteer(self):
        self._SM.setSpeed(0)
        self._SM.Stop()

    def Forward(self, speed):
        if (speed > 90):
            speed = 90
        elif (speed < 0):
            speed = 0

        self._BM.setSpeed(speed)
        self._BM.TurnClockwise()

    def Reverse(self, speed):
        if (speed > 90):
            speed = 90
        elif (speed < 0):
            speed = 0

        self._BM.setSpeed(speed)
        self._BM.TurnCounterClockwise()

    def TurnLeft(self, anglePercent):
        """
        :param anglePercent: from 0 - 90 for turning
        """
        # TODO: ?? add restriction on speed 0 - 90 for turning
        self._SM.setSpeed(anglePercent)
        self._SM.TurnClockwise()

    def TurnRight(self, anglePercent):
        """
        :param anglePercent: from 0 - 100 for turning
        """
        # TODO: ?? add restriction on speed 0 - 90 for turning
        self._SM.setSpeed(anglePercent)
        self._SM.TurnCounterClockwise()

    def ForwardRight(self, forwardSpeed, steerSpeed):
        self.TurnRight(steerSpeed)
        self.Forward(forwardSpeed)

    def ForwardLeft(self, forwardSpeed, steerSpeed):
        self.TurnLeft(steerSpeed)
        self.Forward(forwardSpeed)

    def Turn(self, angle):
        '''
        Accepts a degree between -90 to 90, if Angle < 0, then turn left, if Angle > 0, then turn right
        :param angle:
        :return:
        '''
        if angle < 0:  # Left Turn
            self.TurnLeft(-angle)  # Make negative angle positive
        elif (angle > 0):  # Right turn
            self.TurnRight(angle)
        elif (angle == 0):  # Stop --> Center steer
            self.ResetSteer()
            print("Steer CENTER")

    def cleanup(self):
        self._BM.cleanup()
        self._SM.cleanup()

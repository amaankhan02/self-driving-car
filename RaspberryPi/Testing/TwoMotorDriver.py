import RPi.GPIO as gpio
import time
from motor import Motor

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
        if(speed > 90):
            speed = 90
        elif (speed < 0):
            speed = 0
        
        self._BM.setSpeed(speed)
        self._BM.TurnClockwise()

    def Reverse(self, speed):
        if(speed > 90):
            speed = 90
        elif (speed < 0):
            speed = 0

        self._BM.setSpeed(speed)
        self._BM.TurnCounterClockwise()

    def TurnLeft(self, anglePercent):
        """
        :param anglePercent: from 0 - 90 for turning
        """
        #TODO: ?? add restriction on speed 0 - 90 for turning
        self._SM.setSpeed(anglePercent)
        self._SM.TurnClockwise()

    def TurnRight(self, anglePercent):
        """
        :param anglePercent: from 0 - 100 for turning
        """
        # TODO: ?? add restriction on speed 0 - 90 for turning
        self._SM.setSpeed(anglePercent)
        self._SM.TurnCounterClockwise()

    def Turn(self, angle):
        if angle < 0:  # Left Turn
            self.TurnLeft(-angle)  #Make negative angle positive
        elif (angle > 0):  # Right turn
            self.TurnRight(angle)
        elif (angle == 0):  # Stop --> Center steer
            self.ResetSteer()
            print("Steer CENTER")

    def cleanup(self):
        self._BM.cleanup()
        self._SM.cleanup()


if __name__ == "__main__":
    BM_ForwardPin = 11
    BM_ReversePin = 7
    BM_pwmPin = 16

    SM_LeftPin = 13
    SM_RightPin = 15
    SM_pwmPin = 12

    Frequency = 60
    driver = TwoMotorDriver(Motor(BM_ForwardPin, BM_ReversePin, BM_pwmPin, Frequency), Motor(SM_LeftPin, SM_RightPin, SM_pwmPin, Frequency))

    try:
        """driver.Forward(30)
        print("Forward")
        time.sleep(1.5)
        driver.Reverse(30)
        print("Backward")
        time.sleep(1.5)
        driver.StopAll()
        print("Stop")"""
        driver.TurnLeft(95)
        print("left")
        time.sleep(1.5)
        driver.TurnRight(95)
        print("Right")
        time.sleep(1.5)
        driver.ResetSteer()
        driver.TurnLeft(95)
        print("left")
        time.sleep(1.5)
        driver.TurnRight(95)
        print("Right")
        time.sleep(1.5)
        driver.ResetSteer()
        driver.cleanup()
        print("Cleanup")
    except KeyboardInterrupt:
        driver.cleanup()
        print("Cleanup")



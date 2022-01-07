import RPi.GPIO as gpio
import time

#NEW VERSION -- W/ back motor connected to previous Steering Motor inputs in L298N Motor Driver
class BackMotor:
    def __init__(self, motor):
        self._backMotor = motor

    def Stop(self):
        self._backMotor.setSpeed(0)
        self._backMotor.Stop()

    def Forward(self, speed):
        if (speed > 90):
            speed = 90
        elif (speed < 0):
            speed = 0

        self._backMotor.setSpeed(speed)
        self._backMotor.TurnClockwise()

    def Reverse(self, speed):
        if (speed > 90):
            speed = 90
        elif (speed < 0):
            speed = 0

        self._backMotor.setSpeed(speed)
        self._backMotor.TurnCounterClockwise()

    def cleanup(self):
        self._backMotor.cleeanup()
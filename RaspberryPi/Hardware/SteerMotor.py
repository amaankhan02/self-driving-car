import RPi.GPIO as gpio
from GpioMode import GpioMode
import time
from abc import ABC

"""
Works ONLY for Servo Motor Steering
"""

class AbstractSteerMotor(ABC):
    def turn(self, degree):
        pass

    def offMotor(self):
        pass

    def cleanup(self):
        pass

class ServoSteerMotor(AbstractSteerMotor):
    def __init__(self, pwmPin, gpioMode, centerAngle, frequency=50):
        """

        :param pwmPin:
        :param frequency:
        :param gpioMode: enum of GpioMode
        """
        self.pwmPin = pwmPin
        self.frequency = frequency
        self.centerAngle = centerAngle
        if(gpioMode == GpioMode.BCM):
            gpio.setmode(gpio.BCM)
        elif(gpioMode == GpioMode.BOARD):
            gpio.setmode(gpio.BOARD)
        gpio.setwarnings(False)
        gpio.setup(pwmPin, gpio.OUT)
        self.pwm = gpio.PWM(self.pwmPin, self.frequency)
        self.pwm.start(0)

    def turn(self, degree):
        """
        :param degree: range of -100 -> +100, 0=center, (+) = Right, (-) = Left
        """
        #NOTE: All explanation in onenote notebook
        degree = -1*degree #turn to negative, b/c + is right, and - is left
        degree = self.centerAngle + degree
        duty = (degree/18)+2 #explanation in onenote code
        gpio.output(self.pwmPin, True)
        self.pwm.ChangeDutyCycle(duty)

    def offMotor(self):
        # gpio.output(self.pwmPin, False)
        # self.pwm.ChangeDutyCycle(0)
        self.turn(0)
        gpio.output(self.pwmPin, False)

    def setCenterAngle(self, centerAngle):
        self.centerAngle = centerAngle

    def cleanup(self):
        self.pwm.stop()
        gpio.cleanup()


class MotorDriverSteerMotor(AbstractSteerMotor):
    def __init__(self, motor):
        self._steerMotor = motor

    def turn(self, degree):
        """
        :param degree: range of -100 to +100, (-) = Left, (+) = Right
        """
        if(degree < 0): #left turn
            self._steerMotor.setSpeed(degree*-1)
            self._steerMotor.TurnClockwise()
        else: #positive -- right
            self._steerMotor.setSpeed(degree)
            self._steerMotor.TurnCounterClockwise()

    def offMotor(self):
        self._steerMotor.setSpeed(0)
        self._steerMotor.Stop()

    def cleanup(self):
        self._steerMotor.cleanup()
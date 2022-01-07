import RPi.GPIO as gpio
import time

"""
Motor that is attached to L298N Motor Driver
"""
class Motor:

    def __init__(self, pin1, pin2, pwmPin, pwmFrequency):
        """

        :param pin1: TurnClockwise Pin
        :param pin2: TurnCounterClockwise Pin
        :param pwmPin:
        :param pwmFrequency:
        """
        # use physical pin numbering
        gpio.setmode(gpio.BOARD)
        gpio.setwarnings(False)

        self._pin1 = pin1
        self._pin2 = pin2
        self._pwmPin = pwmPin
        self._pwmFrequency = pwmFrequency

        #Set up GPIO Pin channels with OUTPUT
        gpio.setup(self._pin1, gpio.OUT)
        gpio.setup(self._pin2, gpio.OUT)

        #Set the GPIO to software PWM at 'Frequency' Hertz
        gpio.setup(self._pwmPin, gpio.OUT)
        self._pwm = gpio.PWM(self._pwmPin, self._pwmFrequency)
        self._pwm.start(0)  #Set PWM with dutycycle of 0 (not moving)

    def TurnClockwise(self):
        gpio.output(self._pin2, gpio.LOW)  # Turn off pin2
        gpio.output(self._pin1, gpio.HIGH) #Turn on Pin1

    def TurnCounterClockwise(self):
        gpio.output(self._pin1, gpio.LOW)  # Turn off pin1
        gpio.output(self._pin2, gpio.HIGH) # Turn on pin2

    def Stop(self):
        gpio.output(self._pin1, gpio.LOW)
        gpio.output(self._pin2, gpio.LOW)

    def setSpeed(self, speed):
        self._pwm.ChangeDutyCycle(speed)

    def cleanup(self):
        gpio.cleanup()
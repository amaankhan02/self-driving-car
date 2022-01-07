import RPi.GPIO as gpio
from enum import Enum
import time
from GpioMode import GpioMode
from UltrasonicSensor import UltrasonicSensor

class UltrasonicSensorSet:
    def __init__(self, *args:UltrasonicSensor):
        """
        :param args: UltrasonicSensor objects
        """
        self.ussSet = args

    def getDistances(self):
        """
        :return: list of distances of all UltrasonicSensors in order of how passed in constructor
        """
        distances = []
        for uss in self.ussSet:
            distances.append(uss.getDistance())

        return distances

    def cleanup(self):
        gpio.cleanup()
        print("GPIO cleaned up")
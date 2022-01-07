import RPi.GPIO as gpio
from enum import Enum
import time
from abc import ABC



class UltrasonicSensor:
    def __init__(self, TRIG_pin, ECHO_pin):
        """
        :param TRIG_pin:
        :param ECHO_pin:
        :param gpioMode: GpioMode.BOARD or GpioMode.BCM.
        """
        self.TRIG = TRIG_pin
        self.ECHO = ECHO_pin
        gpio.setwarnings(False)
        gpio.setmode(gpio.BOARD)
        
        gpio.setup(self.TRIG, gpio.OUT)  # Initialize TRIG - Output
        gpio.setup(self.ECHO, gpio.IN)  # Initialize ECHO - Input
        # Set trigger to LOW
        gpio.output(self.TRIG, gpio.LOW)

    def getDistance(self):
        # Send 10microsecond pulse to trigger
        gpio.output(self.TRIG, gpio.HIGH)
        time.sleep(0.00001)
        gpio.output(self.TRIG, gpio.LOW)

        start = time.time()

        while gpio.input(self.ECHO) == gpio.LOW:
            start = time.time()

        while gpio.input(self.ECHO) == gpio.HIGH:
            stop = time.time()
        elapsed = stop - start

        # Distance pulse travelled in that time is multiplied by speed of sound (cm/s).
        # But half of speed of sound cause there and back
        distance = round((elapsed * 17160), 2)
        return distance

    def getAverageDistance(self, waitTime=0.1):
        """
        Takes 3 distance measurements and gets the average distance,
        Total time for getting distance is 2*waitTime
        Reference: https://www.raspberrypi-spy.co.uk/2013/01/ultrasonic-distance-measurement-using-python-part-2/
        :param waitTime: time to wait in seoconds between each distance reading
        :return:
        """
        distance1 = self.getDistance()
        time.sleep(waitTime)
        distance2 = self.getDistance()
        time.sleep(waitTime)
        distance3 = self.getDistance()
        avg_distance = (distance1 + distance2 + distance3)/3 #take average
        return avg_distance

    def cleanup(self):
        gpio.cleanup()
        print("GPIO Cleaned up")

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


if __name__ == "__main__":
    uss1 = UltrasonicSensor(29,31)
    uss2 = UltrasonicSensor(18,22)
    uss3 = UltrasonicSensor(38,40)
    frontSensors = UltrasonicSensorSet(uss1, uss2, uss3)
    try:
        while True:
            distances = frontSensors.getDistances()
            print(min(distances))
            time.sleep(0.4)
    except KeyboardInterrupt:
        frontSensors.cleanup()
        print("exiting")

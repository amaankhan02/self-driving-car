from enum import Enum
import RPi.GPIO as gpio

class GpioMode(Enum):
    BOARD = gpio.BOARD
    BCM = gpio.BCM
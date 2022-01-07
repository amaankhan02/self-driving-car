import RPi.GPIO as gpio
import time
gpio.setmode(gpio.BOARD)


frequency = 50 #50 hz == 50 cycles per second
pwmPin = 3

gpio.setup(pwmPin, gpio.OUT) #setup as output
pwm = gpio.PWM(pwmPin, frequency)
pwm.start(0)


def setAngle(angle):
    duty = (angle/18) + 2 #explanation in oneNote notebook
    gpio.output(pwmPin, True)
    pwm.ChangeDutyCycle(duty)
    #time.sleep(1)
    #print("1 second up")
    #gpio.output(pwmPin, False)
    #pwm.ChangeDutyCycle(0) #off it


try:
    #angle = 35
    while True:
        angle = int(input("Angle: "))
        setAngle(angle)
        #angle +=
except KeyboardInterrupt:
    print("exiting")
    gpio.output(pwmPin, False)
    pwm.ChangeDutyCycle(0)
    pwm.stop()
    gpio.cleanup()



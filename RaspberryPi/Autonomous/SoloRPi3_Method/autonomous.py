import time
from keras import backend as K
K.set_image_dim_ordering('tf')
import sys
sys.path.insert(0,'/home/pi/SDC_Project/RaspberryPi/Hardware')
from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
from TwoMotorDriver import TwoMotorDriver
from Motor import Motor
from Commands import Commands
from _thread import *

class Autonomous:
    def __init__(self, networkModel, twoMotorDriver, ultrasonicSensor, ultrasonicsSensorThresholdDistance, defaultSpeed, defaultSteerSpeed):
        """
        :param networkModel:
        :param twoMotorDriver:
        :param ultrasonicSensor:
        :param ultrasonicsSensorThresholdDistance: threshold distance to stop in cm
        :param defaultSpeed: default backmotor speed
        :param defaultSteerSpeed:
        """
        self._networkModel = networkModel
        self._twoMotorDriver = twoMotorDriver
        self.ultrasonicSensor = ultrasonicSensor
        self.uss_thresholdDistance = ultrasonicsSensorThresholdDistance

        self._speed = self.setSpeed(defaultSpeed)
        self._steerSpeed = self.setSteerSpeed(defaultSteerSpeed)
        self._isPredicting = False
        # self._isTooClose = False; #True if USS reads distance to be too close
        self.uss_distance = 0; #distance that USS reads

    def setSpeed(self, speed):
        if(speed > 95):
            self._speed = 95
        elif(speed < 0):
            self._speed = 0
        else:
            self._speed = speed

    def setSteerSpeed(self, steerSpeed):
        if(steerSpeed > 100):
            self._steerSpeed = 100
        elif(steerSpeed < 0):
            self._steerSpeed = 0
        else:
            self._steerSpeed = steerSpeed

    def __executePrediction(self, prediction):
        """
        executes motor commands from networkModel prediction
        :param prediction: one-hot encoded array (return value of NetworkModel.predicts)
        """
        if(prediction == Commands.FORWARD.value):
            self._twoMotorDriver.Forward(self._speed)
            print("Forward")
        elif(prediction == Commands.BACK.value):
            self._twoMotorDriver.Reverse(self._speed)
            print("Back")
        elif(prediction == Commands.RIGHT.value):
            # self._twoMotorDriver.TurnRight(self._steerSpeed)
            self._twoMotorDriver.ForwardRight(self._speed, self._steerSpeed)
            print("Forward Right")
        elif (prediction == Commands.LEFT.value):
            # self._twoMotorDriver.TurnLeft(self._steerSpeed)
            self._twoMotorDriver.ForwardLeft(self._speed, self._steerSpeed)
            print("Forward Left")
        else:
            print("ExecutePrediction: Bad Command")

    def start(self):
        """
        Starts Autonomous mode - records video, predicts, and executes motor on prediction
        """
        start_new_thread(self._pollDistance, ())

        # initialize the camera and grab a reference to the raw camera capture
        camera = PiCamera()
        camera.resolution = (320, 240)
        camera.framerate = 30
        rawCapture = PiRGBArray(camera, size=(320, 240))

        try:
            for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
                # raw NumPy array representing the image
                image = frame.array
                if (self._isPredicting and self.uss_distance > self.uss_thresholdDistance): #Only predict if boolean = true and distance > 15 cm
                    prediction = self._networkModel.predict(image[120:240])  # predict on lower half of image only
                    self.__executePrediction(prediction)

                # clear the stream in preparation for the next frame -- IMPORTANT
                rawCapture.truncate(0)
                # if cv2.waitKey(1) & 0xFF == ord("q"):
                #     break

        except Exception as e:
            print("---EXCEPTION OCCURED-----\n{}".format(e))
        finally:
            cv2.destroyAllWindows()
            camera.close()
            print("closing recording")

    def pause(self):
        self._isPredicting = False
        self._twoMotorDriver.StopAll()

    def resume(self):
        self._isPredicting = True

    def _pollDistance(self):
        while True:
            if(self._isPredicting):
                self.uss_distance = self.ultrasonicSensor.getDistance()
                time.sleep(0.4) #wait 0.4 seconds before getting distance again
                if(self.uss_distance <= self.uss_thresholdDistance):
                    print("Distance Too close: {}cm".format(self.uss_distance))





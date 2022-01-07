from keras.models import Sequential, model_from_json, load_model
from keras import backend as K
K.set_image_dim_ordering('tf')
import sys
import json
import numpy as np
import tensorflow as tf
from Computer.NN_Trainer.Util import *
from Computer.Autonomous.KerasNetworkModel import KerasNetworkModel

class KerasSteeringAngleModel(KerasNetworkModel):
    def predict(self, img):
        '''
        :param img: size 240,320,3.
        :return: type = numpy.float32, prediction of steering angle between -10 to +10
        '''

        x = img.reshape((1, img.shape[0], img.shape[1], img.shape[2])) #TODO: make it more dynamic, it should reshape based on the input shape of network
        prediction = self.model.predict(x, batch_size=1, verbose=0)
        return prediction[0][0] #prediction looks something like this --> [[2.424]], so we take the [0][0]
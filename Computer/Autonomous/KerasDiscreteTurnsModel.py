from keras.models import Sequential, model_from_json, load_model
from keras import backend as K
K.set_image_dim_ordering('tf')
import sys
import json
import numpy as np
import tensorflow as tf
from Computer.NN_Trainer.Util import *
from Computer.Autonomous.KerasNetworkModel import KerasNetworkModel

class KerasDiscreteTurnsModel(KerasNetworkModel):
    def __convertIndexToSoftmax(self, index, totalNumOutputs):
        '''
        :param index: index of highest value in softmax
        :param totalNumOutputs: is the length of the softamx output array
        :return:
        '''
        softmax = np.zeros(totalNumOutputs)
        softmax[index] = 1.0
        return softmax

    def predict(self, img):
        '''
        :param img: size 120,320,3. Take regular image and do Image[120;240] to get lower half
        :return: prediction as the index of 1 in one-hot encoded value
        '''
        # x = normalizeData(img,self.normalizationMethod)
        x = img.reshape((1, img.shape[0], img.shape[1], img.shape[2]))
        predictionIndex = self.model.predict_classes(x, batch_size=1, verbose=0)
        # softmaxPrediction = self.__convertIndexToSoftmax(predictionIndex, 4)
        return predictionIndex[0]

    def predict_old(self, img):
        x = np.divide(img, 255) #normalize zero to one
        x = x.reshape((1, 120, 320, 3))
        predictionIndex = self.model.predict_classes(x, batch_size=1, verbose=0)
        # softmaxPrediction = self.__convertIndexToSoftmax(predictionIndex, 4)
        return predictionIndex[0]

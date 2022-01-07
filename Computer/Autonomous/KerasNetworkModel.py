from abc import ABC, abstractmethod, abstractclassmethod, abstractproperty, abstractstaticmethod
from keras.models import Sequential, model_from_json, load_model
from keras import backend as K
K.set_image_dim_ordering('tf')
import sys
import json
import numpy as np
import tensorflow as tf

class KerasNetworkModel(ABC): #an abstact class
    def __init__(self, directory):
        '''
        :param directory: directory where Network model is saved **Must include a slash at end of path
        '''
        self.saveDirectory = directory;
        self.model = self.__getModel(directory)
        self.additionalInfoJson = self.__getAdditionalInfo(directory)
        self.normalizationMethod = self.additionalInfoJson['normalization_method']

    def __getAdditionalInfo(self, directory):
        # open json file
        with open(directory + '\\additional_info.json') as json_file:
            data = json.load(json_file)
            return data

    def __getModel(self, directory):
        # get the model
        json_file = open(directory + '\\single_batch_model.json', 'r')
        model_json = json_file.read()
        json_file.close()
        model = model_from_json(model_json)

        # Load weights into new model
        model.load_weights(directory + "\\single_batch_model_weights.h5")
        print("loaded model and weights")
        return model

    @abstractmethod
    def predict(self, img):
        pass
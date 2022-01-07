from keras.models import Sequential, model_from_json, load_model
from keras import backend as K
K.set_image_dim_ordering('tf')
import sys
sys.path.insert(0,'/home/pi/SDC_Project/RaspberryPi/Hardware')
import json
import numpy as np

'''
If creating more model classes, create a base NetworkModel class, and have each inherit from it
'''

class KerasConvNetModel():
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

    def __normalizeData(self, data):
        if (self.normalizationMethod == 'zero_to_one'):
            return np.divide(data, 255)
        elif (self.normalizationMethod == 'negOne_to_one'):
            return np.subtract(np.divide(data, 127.5), 1)
        elif (self.normalizationMethod == 'none'):
            return data
        else:
            raise ValueError(
                "Unknown normalization method. From Autonomous.py >__normalizeData()\nnormalizationMethod={}".format(
                    self.normalizationMethod))

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
        :return: one-hot encoded prediction
        '''
        x = self.__normalizeData(img)
        x = x.reshape((1, 120, 320, 3))
        predictionIndex = self.model.predict_classes(x, batch_size=1, verbose=0)
        softmaxPrediction = self.__convertIndexToSoftmax(predictionIndex, 4)
        return softmaxPrediction


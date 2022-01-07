import cv2
import numpy as np
np.random.seed(1337)
import pathlib
from Computer.NN_Trainer.NormalizationMethod import NormalizationMethod
import json
from matplotlib import pyplot as plt
import keras
from keras.layers import Dense, Dropout, Flatten, Lambda, ELU, Cropping2D
from keras.layers.convolutional import MaxPooling2D, Conv2D
from keras.regularizers import l2
from keras.preprocessing.image import ImageDataGenerator
from keras.optimizers import Adam, SGD
from keras.constraints import maxnorm
from keras.datasets import cifar10
from keras.models import Sequential, model_from_json, load_model
from keras.backend import tf
from keras import backend as K
K.set_image_dim_ordering('tf') #TODO: Change this to 'tf' - https://stackoverflow.com/questions/39547279/loading-weights-in-th-format-when-keras-is-set-to-tf-format
from keras.callbacks import Callback, ModelCheckpoint
from keras.utils import plot_model, np_utils
# from sklearn.cross_validation import train_test_split #--> sklean.cross_validation is deprecated
from sklearn.model_selection import train_test_split
import time
import os

from PIL import Image
import pickle
from Computer.NN_Trainer.Dataset import Dataset
from Computer.NN_Trainer.DataGenerator import DataGenerator
from keras_tqdm import TQDMNotebookCallback
from Computer.NN_Trainer.Util import *
from TrainType import TrainType
import tensorflow as tf


"""
Tests a model on data, returns the accuracy metrics
"""

def getModel(path):
    json_file = open(os.path.join(path,"model.json"), 'r')
    model_json = json_file.read()
    json_file.close()
    model = model_from_json(model_json)

    #load weights into new model
    model.load_weights(os.path.join(path, "model_weights.h5"))
    return model

def getSingleBatchModel(path):
    json_file = open(os.path.join(path,'single_batch_model.json'), 'r')
    model_json = json_file.read()
    json_file.close()
    model = model_from_json(model_json)
    # Load weights into new model
    model.load_weights(os.path.join(path,'single_batch_model_weights.h5'))
    print("loaded model and weights")
    return model

def showOnlyCmds(imgList, cmdList):
    count_angles = np.zeros(21);
    angles = np.arange(0,21);

    for i in range(len(imgList)):
        x = imgList[i].reshape((1, 240, 320, 3))
        prediction = model.predict(x, batch_size=1, verbose=0)[0][0]
        yTestPrediction = cmdList[i];
        # print(prediction /yTestPrediction)
        print(prediction)
        print(yTestPrediction)
        # if(prediction!= yTestPrediction): #wrong prediciton
        #     print(prediction)
        #     count_angles[yTestPrediction] += 1 #add count

    plt.bar(np.arange(0,21),height=count_angles)
    plt.xticks(angles, angles)
    plt.show()

def showOnlyBadPredictions(imgList, cmdList):
    badCount = 0;
    for i in range(len(imgList)):
        x = imgList[i].reshape((1, 240, 320, 3))
        prediction = model.predict(x, batch_size=1, verbose=0)[0][0]
        yTestPrediction = cmdList[i];

        if(abs(yTestPrediction - prediction) > 3):
            badCount+=1
            # print("Prediction: {0}, Real: {1}".format(prediction, yTestPrediction))
    print("badCount: {0}".format(badCount))
    print("Percent of bad: {0}".format(100*badCount/len(cmdList)))

def runPredictions(x_test, y_test):
    for i in range(len(x_test)):
        x = x_test[i].reshape((1,240,320,3))
        prediction = model.predict(x, batch_size=1, verbose=0)[0][0]
        print("Prediction: {0}, Real: {1}".format(prediction, y_test[i]));
        cv2.putText(x_test[i], str(y_test[i]), (135,25), cv2.FONT_HERSHEY_SIMPLEX,
                    1,(0,0,255), 2)
        cv2.imshow('img', x_test[i])
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

def runEvaluation(x_test, y_test):
    testScores = model.evaluate(x_test, y_test, verbose=0)
    return testScores[1]

model = getModel(r"I:\TFS\AK\MyProjects\Development\SelfDrivingCar\Computer\NeuralNetworkModels\SteeringAngleModel\CNN\12.11.17\Trial3Keras")
# model.compile(loss='mse', optimizer=Adam(lr=1e-4),metrics=['accuracy']) #must compile to evaluate model -- https://stackoverflow.com/questions/46127625/need-to-compile-keras-model-before-model-evaluate


#get data
server = ''
database = ''
username = ''
password = ''
driver = '{ODBC Driver 13 for SQL Server}'

normalizationMethod = NormalizationMethod.none;
table = "trainData.SteeringAngleData"
trainType = TrainType.SteerAngles;

dataset = Dataset(server,database,username,password,driver)
imgList, cmdList = dataset.getData("""SELECT * FROM {0} where Evaluation='Good' and Id between 350 and 370""".format(table), trainType = trainType,
                                     shouldReshape=False,normalizationMethod=normalizationMethod,shouldShuffle=False)
print("Image Count: ",len(imgList))
runPredictions(imgList,cmdList)

# negCount = 0;
# posCount = 0;
# zeroCount = 0;
# greatFive = 0;
# for cmd in cmdList:
#     if(cmd < 0):
#         negCount+=1
#     elif(cmd >=5):
#         greatFive+=1
#     elif(cmd > 0):
#         posCount+=1;
#     else:
#         zeroCount+=1;
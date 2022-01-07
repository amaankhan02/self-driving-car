import numpy as np
from Computer.NN_Trainer.NormalizationMethod import NormalizationMethod
from sklearn.model_selection import train_test_split
from random import random, shuffle

def normalize_zero_to_one(xList):
    return np.divide(xList, 255)

def normalize_negOne_to_one(xList):
    return np.subtract(np.divide(xList, 127.5), 1)


def normalizeData(data, normalizationMethod):
    if(normalizationMethod.value == NormalizationMethod.zero_to_one.value):
        return normalize_zero_to_one(data)
    elif(normalizationMethod.value == NormalizationMethod.negOne_to_one.value):
        return normalize_negOne_to_one(data)
    elif(normalizationMethod.value == NormalizationMethod.none.value):
        return data
    else:
        raise ValueError("Unknown Value for NormalizationMethod, from Dataset.py > __normalizeData(),\n normalizationMethod={}".format(normalizationMethod))

def splitTrainTestVal(x, y, testVal_size):
    '''
    splits data into train, test, and validation data sets
    :param x: input data
    :param y: output data
    :return: (x_train, x_test, x_val, _train, y_test, y_val)
    '''
    x_train, x_testVal, y_train, y_testVal = train_test_split(x, y, test_size=testVal_size, random_state=42)
    x_test, x_val, y_test, y_val = train_test_split(x_testVal, y_testVal, test_size=0.5,random_state=53)  # split the testVal into test and validation sets
    return x_train, x_test, x_val, y_train, y_test, y_val

def splitTrainTest(x, y, test_size):
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=test_size, random_state=42)
    return x_train, x_test, y_train, y_test

def getRandomSample(xList, yList, size):
    '''returns new_xList, new_yList'''
    if (len(xList) != len(yList)):  # must be same size
        raise Exception
    else:
        max_index = random.randint(size, len(
            xList) - 1)  # lower bound of max index is the size, and upperbound is the size of list
        return xList[max_index - size:max_index], yList[max_index - size:max_index]

def convert_index_to_oneHotEncoded(index, length):
    onehot = np.zeros(length)
    onehot[index] = 1;
    return onehot


def unzipXY(inputList):
    '''gets seperate list of images and seperate list of cmds from a list of (img,cmd)'''
    xList = list(zip(*inputList))[0] #unzip and get the first list in ilst (imgs)
    yList = list(zip(*inputList))[1]
    return xList, yList
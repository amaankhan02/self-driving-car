from Computer.NN_Trainer.NormalizationMethod import NormalizationMethod
# from Computer.NN_Trainer.Normalize import normalize_zero_to_one, normalize_negOne_to_one
import numpy as np
import pickle
from RaspberryPi.CollectingTrainingData.Commands import Commands
import pyodbc
from sklearn.model_selection import train_test_split
from random import random, shuffle
import cv2
from queue import LifoQueue, Queue
from Computer.NN_Trainer.TrainType import TrainType
from Computer.NN_Trainer.Util import *

class Dataset:
    def __init__(self, server, database, username, password, driver):
        '''establish sql database connection'''
        cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+ ';UID='+username+';PWD='+ password)
        self.cursor = cnxn.cursor()
        self.trainingDataList = []  # ((img, cmd), (img,cmd), ...)

    def getData(self, query, shouldReshape, normalizationMethod, trainType, shouldShuffle=True,functionOnImg=None,functionOnCmd=None):
        '''

        :param query: sql cmd to get data
        :param shouldReshape:
        :param batchSize: size of data to get, None => get All data
        :param normalizeFunction:
        :param shouldShuffle:
        :return:
        '''
        imgList = []
        cmdList = []
        noCmdCount = 0
        self.cursor.execute(query)
        row = self.cursor.fetchone()  # fetch one row

        framelet_list = []

        # get framelets in a list
        while row is not None:
            framelet_list.extend(pickle.loads(row.ImageByteArray))  # a video clip of framelets
            row = self.cursor.fetchone()

        if(shouldShuffle):
            shuffle(framelet_list)

        # split framelet list on frame and cmd
        if(trainType.value == TrainType.DiscreteTurns.value):
            for framelet in framelet_list:
                if (framelet.cmd[0:4] != Commands.NO_CMD.value[0:4] and framelet.cmd[0:4] != Commands.STOP_ALL_MOTORS.value[0:4]):
                    img = framelet.frame
                    img = normalizeData(img, normalizationMethod)
                    if (shouldReshape):
                        imgList.append(img.reshape(-1))
                    else:
                        imgList.append(img)
                    cmdList.append(framelet.cmd[0:4])
                else:
                    noCmdCount += 1
        elif(trainType.value == TrainType.SteerAngles.value):
            for framelet in framelet_list:
                img = framelet.frame
                img = normalizeData(img, normalizationMethod)
                if (shouldReshape):
                    imgList.append(img.reshape(-1))
                else:
                    imgList.append(img)
                cmdList.append(framelet.steerDegree)
        else:
            msg = "Unknown trainType. trainType is of type TrainType. Your value is : {}".format(trainType)
            raise ValueError(msg)

        print("noCmdCount/StopMotorsCount = {}".format(noCmdCount))

        if functionOnImg != None:
            imgList = functionOnImg(imgList)
        if functionOnCmd != None:
            cmdList = functionOnCmd(cmdList)

        return np.array(imgList), np.array(cmdList)



    # def nextBatch(self, x,y, batchSize):
    #     # start = 0
    #     # end = start + batchSize
    #     num_batches = int(len(x) / batchSize)
    #     i = 0
    #     while True:
    #         start = i * batchSize
    #         end = start + batchSize
    #         yield (x[start:end], y[start:end])
    #         # the -1 makes it so that if the list is of size not evenly divisible by batchsize, then it won't take the left over elements of
    #         # the list. For example, batchsize = 2, x=[1,2,3,4,5]. Then it yields [1,2], then [3,4], then back to [1,2]. It WONT yield [5], cause its not size of the batchsize
    #         if (i >= num_batches - 1):
    #             i = 0
    #         else:
    #             i += 1



    # def nextBatch_fromList(self, x, y, batchSize):


    # def flipVertical(self, imgList):

#-------TESTING-------
# server = ''
# database = ''
# username = ''
# password = ''
# driver = '{ODBC Driver 13 for SQL Server}'
#
# data = Dataset(server, database, username, password, driver)
# aList = [1,2,3,4,5,6,7,8,9]
# bList = [4,2,54,265,2,5,25,6,2]
#
# mygen = data.nextBatch(aList,bList, 3)
#
# for i in range(4):
#     print(next(mygen))
import numpy as np
import pickle
from RaspberryPi.CollectingTrainingData.Commands import Commands
import pyodbc
from sklearn.model_selection import train_test_split
from random import random, shuffle
from Computer.NN_Trainer.NormalizationMethod import NormalizationMethod
# from Computer.NN_Trainer.Normalize import normalize_zero_to_one, normalize_negOne_to_one
import cv2
from queue import LifoQueue, Queue
from Computer.NN_Trainer.TrainType import TrainType
from Computer.NN_Trainer.Util import *
from imgaug import augmenters as iaa

class DataGenerator:
  
    def __init__(self, sqlWhereClause,server, database, username, password,
                 driver, normalizationMethod, trainType, table, shouldReshapeImg=False, updateFrameletSize=1000, shouldAugment=True, shouldHorizontalFlip=True):
        '''

        :param sqlWhereClause: Where clause for SQL Cmd to fetch rows **Include the keyword 'WHERE' in clause**
        :param sqlConnectionCursor:
        :param server: sql server
        :param database: sql database
        :param username: sql server username
        :param password: sql server password
        :param driver:
        :param trainType: The type of data for training. Either a cmd or steerDegree. Of type TrainType
        :param shouldReshapeImg: should FLATTEN the image, to 1-D array
        :param shouldHorizontalFlip: Doubles the data by horizontally flipping the imgs and getting opposite cmd.
        :param numRows: number of rows to fetch, -1 = all rows
        '''
        # if(numRows == -1):
        #     self._numRows = self.getTotalNumRows()
        # else:
        #     self._numRows = numRows;
        self.table = table;
        if('where' not in sqlWhereClause.lower()): #check if 'where' is in the clause
            sqlWhereClause = 'WHERE' + sqlWhereClause
        self.sqlWhereClause = sqlWhereClause
        # self.maxFramelets = maxFramelets #holds max number of framelets to fetch
        #self.batchSize = batchSize

        cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+ ';UID='+username+';PWD='+ password)
        self.cursor = cnxn.cursor()
        self.updateFrameletSize = updateFrameletSize
        self.frameletList = [] # a list of tuples of(img,cmd)
        self.rowIdList = self.__getRowsId() #holds all rows Id
        shuffle(self.rowIdList) #shuffle the list

        self.trainType = trainType
        self.shouldAugment = shouldAugment
        self.shouldHorizontalFlip = shouldHorizontalFlip

        self.rowIdIndex = 0; #holds the last index used from self.rowsIdList
        self.normalizationMethod = normalizationMethod
        self.shouldReshapeImg = shouldReshapeImg
        self.seq = iaa.Sequential([
            # iaa.Sometimes(0.2, iaa.PerspectiveTransform(scale=(0.005, 0.05))), #20% of time do this
            # iaa.Sometimes(1, iaa.GaussianBlur(sigma=(0,9))), #30% of time do this
            iaa.Sometimes(0.20, iaa.OneOf([  # do one of these 2, and do that 20% of time
                iaa.ContrastNormalization((0.75, 1.5)),  # increase/decrease contrast
                iaa.Multiply((0.5, 1.5))  # brightness
            ]))
        ])

        if(self.shouldHorizontalFlip):
            newFrameletList = self.__fetchNewData(int(self.updateFrameletSize/2)) #take half of data cause the other half will be from the flipped version
            newFrameletList.extend(self._flipHorizontal(newFrameletList))
        else:
            newFrameletList = self.__fetchNewData(self.updateFrameletSize)  # get initial self.updateFrameletSize framelets
        if(self.shouldAugment):
            newFrameletList = self._applyAugment(newFrameletList)
        self.frameletList.extend(newFrameletList)

    def _applyAugment(self, frameletList):
        imgList, cmdList = unzipXY(frameletList)
        augImgList = self.seq.augment_images(imgList)  # augment it
        augmentedFrameletList = list(zip(augImgList, cmdList)) #zip them together again
        return augmentedFrameletList

    # def getNumRowsToFetch(self):
    #     return self._numRows

    def getTotalNumRows(self):
        '''gets total num rows in table'''
        query = """SELECT count(Id) as NumRows FROM {0} {1}""".format(self.table, self.sqlWhereClause)
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        numRows = int(row.NumRows);
        return numRows

    def getTotalFrameCount(self):
        """
        gets total framcount from the number of rows to pick from
        :return:
        """
        query = """SELECT sum(FrameCount) as TotalFrameCount FROM {0} {1}""".format(self.table,self.sqlWhereClause)
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        frameCount = int(row.TotalFrameCount)

        # frameCount = 0
        # rowIds = self.__getRowsId();
        # #TODO: CHANGE TO FETCH INDIVIDUAL ROWS IN FOR LOOP SO IT GETS BASED ON WHERE CLAUSE
        # query = """SELECT (FrameCount) as FrameCount from {0} where Id BETWEEN {1} and {2} and Evaluation='Good'""".format(self.table, rowIds[0], rowIds[len(rowIds)-1])
        # self.cursor.execute(query)
        # row = self.cursor.fetchone()
        # while row is not None:
        #     frameCount += int(row.FrameCount);
        #     row = self.cursor.fetchone()

        if(self.shouldHorizontalFlip):
            frameCount *= 2 #double the count cause all data will have an original and a flipped version

        return frameCount

    def getTrainableFrameCount(self):
        '''gets only count of frames that are trainable. so no NO_CMD or STOP_MOTOR_CMD, and the framecounts from rows that are being picked from input in constructor'''
        # startIndex = 0
        # endIndex = startIndex + 49
        # startRowId = self.rowIdList[startIndex]
        # endRowId = self.rowIdList[endIndex]
        query = """SELECT sum(TrainableFrameCount) as TrainableFrameCount FROM {0} {1}""".format(self.table,self.sqlWhereClause)
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        frameCount = int(row.TrainableFrameCount)

        # frameCount = 0
        # rowIds = self.__getRowsId();
        # query = """SELECT (TrainableFrameCount) as FrameCount from {0} where Id BETWEEN {1} and {2} and Evaluation='Good'""".format(self.table, rowIds[0], rowIds[len(rowIds)-1])
        # self.cursor.execute(query)
        # row = self.cursor.fetchone()
        # while row is not None:
        #     frameCount += int(row.FrameCount);
        #     row = self.cursor.fetchone()

        if(self.shouldHorizontalFlip):
            frameCount *=2 #double the count cause all data will have an original and a flipped version
        return frameCount

    def __getRowsId(self):
        query = "SELECT (Id) FROM {0} {1} order by 1 asc".format(self.table,self.sqlWhereClause)
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        rowIdList = []
        while row is not None:
            rowIdList.append(int(row.Id))
            row = self.cursor.fetchone()
        return rowIdList

    def _flipCommand(self,cmd):
        if(cmd == Commands.RIGHT.value):
            return Commands.LEFT.value
        elif(cmd == Commands.LEFT.value):
            return Commands.RIGHT.value;
        elif(cmd==Commands.FORWARD.value or cmd==Commands.BACK.value or cmd==Commands.STOP_ALL_MOTORS.value):
            return cmd
        else:
            return Commands.NO_CMD.value;

    def _flipHorizontal(self, imgCmdFrameletList):
        refactoredList = []
        if(self.trainType.value == TrainType.SteerAngles.value):
            for xyDataSet in imgCmdFrameletList:
                img = cv2.flip(xyDataSet[0], 1)  # 0 is vertical flip, 1 is horizontal flip, xyDataSet[0] is the img
                cmd = xyDataSet[1] * -1 #take opposite, xyDataSet[1] is the cmd/steeringDegreeAngle
                refactoredList.append((img, cmd))
        elif(self.trainType.value == TrainType.DiscreteTurns.value):
            for xyDataSet in imgCmdFrameletList:
                img = cv2.flip(xyDataSet[0], 1)  # 0 is vertical flip, 1 is horizontal flip, xyDataSet[0] is the img
                cmd = self._flipCommand(xyDataSet[1]) #take opposite, xyDataSet[1] is the cmd/steeringDegreeAngle
                refactoredList.append((img,cmd))
        else:
            msg = "Unknown trainType. trainType is of type TrainType. Your value is : {}".format(self.trainType.name)
            raise ValueError(msg)
        return refactoredList

    def __fetchNewData(self, size):
        '''Adds elements to self.framelet_list as the discrete turns cmds'''
        frameCount = 0;
        newImgCmdFrameletList = []
        while frameCount < size:
            self.cursor.execute("""SELECT * FROM {0} WHERE Id=?""".format(self.table), self.rowIdList[self.rowIdIndex])
            row = self.cursor.fetchone()

            framelet_list = pickle.loads(row.ImageByteArray) #get the framelet_list
            shuffle(framelet_list)
            if(self.trainType.value == TrainType.DiscreteTurns.value):
                for framelet in framelet_list:
                    if (framelet.cmd[0:4] != Commands.NO_CMD.value[0:4] and framelet.cmd[0:4] != Commands.STOP_ALL_MOTORS.value[0:4]):
                        img = framelet.frame
                        # img = self.__normalizeData(img)
                        img = normalizeData(img, self.normalizationMethod)
                        if (self.shouldReshapeImg):
                            img = img.reshape(-1)
                        newImgCmdFrameletList.append((img, framelet.cmd[0:4]))
                        frameCount +=1
            elif(self.trainType.value == TrainType.SteerAngles.value): #cmds are steering angles
                for framelet in framelet_list:
                    img = framelet.frame
                    img = normalizeData(img, self.normalizationMethod)
                    if (self.shouldReshapeImg):
                        img = img.reshape(-1)
                    newImgCmdFrameletList.append((img, framelet.steerDegree))
                    frameCount +=1
            else:
                msg = "Unknown trainType. trainType is of type TrainType. Your value is : {}".format(self.trainType.name)
                raise ValueError(msg)
            # frameCount += row.FrameCount
            self.__incrementRowIdIndex()

        return newImgCmdFrameletList


    def __incrementRowIdIndex(self):
        '''increases self.rowIdIndex by 1, but equals to 0 if exceeds the index limit of self.rowIdList'''
        if(self.rowIdIndex >= len(self.rowIdList)-1): #check if rowIdIndex is the last index
            self.rowIdIndex = 0
        else:
            self.rowIdIndex +=1

    def __getBatch(self, batchSize):
        '''gets a batchSize from framelet_list and removes those elements from the list'''
        batchList = self.frameletList[0:batchSize]
        del self.frameletList[0:batchSize]
        return batchList


    def nextBatch(self,batchSize, functionOnImg=None, functionOnCmd=None):
        '''returns next batch of imgs and cmds as a np array
        :param functionOnImg: any function that can be applied on imgList data, 1 parameter which is img'''
        while True:
            if(len(self.frameletList) < batchSize*2): #check to see if get more reocrds in framelet_list
                if (self.shouldHorizontalFlip):
                    newImgCmdFrameletList = self.__fetchNewData(int(self.updateFrameletSize / 2))  # take half of data cause the other half will be from the flipped version
                    newImgCmdFrameletList.extend(self._flipHorizontal(newImgCmdFrameletList))
                else:
                    newImgCmdFrameletList = self.__fetchNewData(self.updateFrameletSize)  # get initial self.updateFrameletSize framelets
                if (self.shouldAugment):
                    newImgCmdFrameletList = self._applyAugment(newImgCmdFrameletList)
                self.frameletList.extend(newImgCmdFrameletList)

            batchList = self.__getBatch(batchSize)

            #unzip batchList into imgList and cmdList
            imgList = list(zip(*batchList))[0]
            cmdList = list(zip(*batchList))[1]

            if functionOnImg != None:
                imgList = functionOnImg(imgList)
            if functionOnCmd != None:
                cmdList = functionOnCmd(cmdList)

            yield np.array(imgList), np.array(cmdList) #return as np array, or else keras throws error

# '''SteeringAngleClassificationDataGenerator'''
# class SACDataGenerator(DataGenerator):
#     def __init__(self, sqlWhereClause,server, database, username, password,
#                  driver, normalizationMethod, trainType, table,shouldReshapeImg=False, updateFrameletSize=1000, shouldAugment=True, shouldHorizontalFlip=True):
#         super().__init__(sqlWhereClause,server,database,username,password,
#                        driver,normalizationMethod,trainType,table,shouldReshapeImg,updateFrameletSize,shouldAugment,shouldHorizontalFlip)
#
#     def nextBatch(self, batchSize, functionOnImg=None):


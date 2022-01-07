import random
import pyodbc
import pickle
import cv2
import time
from RaspberryPi.CollectingTrainingData.Commands import Commands
from imgaug import augmenters as iaa

# server = 'amaanrobotics.database.windows.net'
# database = 'AmaanRoboticsCloudDB'
# username = ''
# password = ''
# driver= '{ODBC Driver 13 for SQL Server}'
# cnxn = pyodbc.connect('DRIVER='+driver+';PORT=1433;SERVER='+server+';PORT=1443;DATABASE='+database+';UID='+username+';PWD='+ password)


def parseCommand(cmd):
    if cmd == Commands.NO_CMD.value:
        return "NO_CMD"
    elif cmd == Commands.LEFT.value:
        return "LEFT"
    elif cmd == Commands.RIGHT.value:
        return 'RIGHT'
    elif cmd == Commands.FORWARD.value:
        return 'FORWARD'
    elif cmd == Commands.BACK.value:
        return 'BACK'
    elif cmd == Commands.STOP_ALL_MOTORS.value:
        return 'STOP ALL MOTORS'
    elif cmd == Commands.BACK_MOTOR_STOP.value:
        return 'BACK_MOTOR_STOP'
    elif cmd == Commands.RESET_STEER.value:
        return 'RESET_STEER'
    else:
        return None

def applyAdaptiveThreshold(imgs):
    threshImgs = []
    for img in imgs:
        thresh = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        thresh = cv2.medianBlur(thresh, 5) #5 - kernel size
        thresh = cv2.adaptiveThreshold(thresh, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
        threshImgs.append(thresh)
    return threshImgs

def applyOtsuThreshold(imgs):
    threshImgs = []
    for img in imgs:
        thresh = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        thresh = cv2.GaussianBlur(thresh, (3,3), 0) #apply guassian blur
        ret3, thresh = cv2.threshold(thresh, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        threshImgs.append(thresh)
    return threshImgs

def getTrainingData(cursor):
    '''
    :param cursor: pyodbc cursor cnxn
    :return: the imgList and cmdList
    '''
    # master_list = [] #contains all framelets
    imgList = []
    cmdList = []
    noCmdCount = 0
    cursor.execute("Select X.* From (SELECT *,Row_Number() over (Order by FileName) as RN from poc.TrainingData) As X where X.Evaluation='Good' and X.Id < 20")
    row = cursor.fetchone() #fetch one row
    while row is not None:
        currentFramelet_list= pickle.loads(row.ImageByteArray) #a video clip of framelets
        for framelet in currentFramelet_list:
            # master_list.append(framelet)
            if(framelet.cmd != Commands.NO_CMD.value):
                imgList.append(framelet.frame[120:240]) #flatten the 3-d array into 1-d --> -1 means 1 dimensional flatten AND take lower half of image
                cmdList.append(framelet.cmd[0:4]) #TODO: THIS IS TEMPERORARY, IT SHOULD ACTUALLY RETURN ME THE WHOLE CMD
            else:
                noCmdCount += 1
        row = cursor.fetchone()
    print("noCmdCount = {}".format(noCmdCount))
    return imgList #TODO: returns list not numpy array, Do we need numpy array instead?

server = ''
database = ''
username = ''
password = ''
driver= '{ODBC Driver 13 for SQL Server}'


cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()

query1 ="Select X.* From (SELECT *,Row_Number() over (Order by FileName) as RN from poc.TrainingData) As X where X.RN BETWEEN 7 and 11 "
query2 = "Select X.* From (SELECT *,Row_Number() over (Order by FileName) as RN from poc.TrainingData) As X where X.Evaluation='Good'"
query3 = "SELECT * FROM [AmaanRoboticsDB].[].[TrainingData] where Id between 5 and 14"

seq = iaa.Sequential([
            # iaa.Sometimes(0.2, iaa.PerspectiveTransform(scale=(0.005, 0.05))), #20% of time do this
            # iaa.Sometimes(1, iaa.GaussianBlur(sigma=(0,9))), #30% of time do this
            iaa.Sometimes(0.20, iaa.OneOf([ #do one of these 2, and do that 30% of time
                iaa.ContrastNormalization((0.75, 1.5)), #increase/decrease contrast
                iaa.Multiply((0.5, 1.5)) #brightness
            ]))
        ])

cursor.execute("SELECT TOP 10 * FROM trainData.SteeringAngleData order by 1 desc")
row = cursor.fetchone() #fetch all rows


while row is not None:
    print(row.Id)
    p = pickle.loads(row.ImageByteArray)
    for framelet in p:
        img = cv2.resize(framelet.frame[112:228],(288,116))
        img = seq.augment_image(img)
        cv2.imshow('i', img)
        # print(parseCommand(framelet.cmd))
        # time.sleep()
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        time.sleep(0.1)
        # time.sleep
    row = cursor.fetchone()

#show shuffled
# cursor.execute("Select X.* From (SELECT *,Row_Number() over (Order by FileName) as RN from poc.TrainingData) As X where X.Evaluation='Good' and Id < 50")

# imgs  = getTrainingData(cursor)
#
#
# for img in imgs:
#     print(img.shape)
#     cv2.imshow('i', img)
#     if cv2.waitKey(1) & 0xFF == ord("q"):
#         break
#     time.sleep(0.01)


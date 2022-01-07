import numpy as np
import cv2
from RaspberryPi.CollectingTrainingData.Commands import Commands
import pyodbc
import pickle
from RaspberryPi.CollectingTrainingData.Framelet import Framelet
import time
import uuid

def flipImageVertically(img): #https://scottontechnology.com/flip-image-opencv-python/
    return cv2.flip(img, 1)  # 0 is horizontal, 1 is vertical, -1 is flip vertical and horizontal

def flipCommand(cmd):
    '''accepts Commands.[cmd].value only and returns opposite'''
    if(cmd == Commands.RIGHT.value):
        return Commands.LEFT.value
    elif(cmd == Commands.LEFT.value):
        return Commands.RIGHT.value;
    elif(cmd==Commands.FORWARD.value or cmd==Commands.BACK.value or cmd==Commands.STOP_ALL_MOTORS.value):
        return cmd
    else:
        return Commands.NO_CMD.value;

def SaveToSql(framelet_list, cursor, originalRowId, guid):
    t0 = time.time()
    bytesList = pickle.dumps(framelet_list)
    filename = 'GeneratedFlip_Id_{}'.format(originalRowId)
    cursor.execute("""INSERT INTO poc.TrainingData(FileName, ImageByteArray, MyGuid, HasGeneratedFlip, Evaluation) SELECT ?, ?, ?, ?, ?""",filename, bytesList, guid, True, 'Good') #insert frameletlist into new row
    t1 = time.time()
    duration = t1-t0
    cursor.execute("""UPDATE poc.TrainingData SET ProcessingTime=? WHERE MyGuid=?""", duration, guid) #update that new row with processing time


server = ''
database = ''
username = ''
password = ''
driver= '{ODBC Driver 13 for SQL Server}'


cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()

# cursor.execute("""Select max(Id) from poc.TrainingData""")
# max = cursor.fetchall()
# print(max)

query = "SELECT * FROM poc.TrainingData where HasGeneratedFlip='FALSE' and Evaluation = 'Good' and Id <400"


cursor.execute(query)
rows = cursor.fetchall() #fetch all rows

#append all new flipped framelets
for row in rows:
    framelet_list = pickle.loads(row.ImageByteArray)
    flippedFrameletList = []
    for framelet in framelet_list: #add flipped imgs to a flippedFrameletList
        flippedImage = flipImageVertically(framelet.frame)
        flippedCmd = flipCommand(framelet.cmd)
        flippedFrameletList.append(Framelet('flipped', flippedImage, flippedCmd))
    if(len(flippedFrameletList) != 0):
        guid = uuid.uuid4()
        SaveToSql(flippedFrameletList, cursor,row.Id, guid)
        cursor.execute("""UPDATE poc.TrainingData SET HasGeneratedFlip='TRUE' WHERE MyGuid=?""", row.MyGuid)
        cursor.commit()
        print("updated row {}".format(row.Id))




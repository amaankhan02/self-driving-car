import numpy as np
import cv2
from RaspberryPi.CollectingTrainingData.Commands import Commands
import pyodbc
import pickle
from RaspberryPi.CollectingTrainingData.Framelet import Framelet
import time
import uuid


def updateFrameCount(frameCount, guid, cursor):
    cursor.execute("""UPDATE poc.TrainingData SET TrainableFrameCount=? WHERE MyGuid=?""", frameCount,guid)


server = ''
database = ''
username = ''
password = ''
driver= '{ODBC Driver 13 for SQL Server}'

cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()


maxRowQuery = "SELECT max(Id) as MaxId FROM poc.TrainingData" #TODO: See if count(*) works or if should be max(Id)
#get max row 
cursor.execute(maxRowQuery)
maxRow = int(cursor.fetchone().MaxId)


#iterate rows 50 at a time and update TrainableFrameCount
currentRowLimit = 50
currentRowStart = 1
while currentRowStart <= maxRow:
    print("Updating rows between {} and {}".format(currentRowStart, currentRowLimit))
    query = "SELECT * FROM poc.TrainingData WHERE TrainableFrameCount is NULL and Id between {0} and {1}" #NOTE: between is inclusive
    cursor.execute(query.format(currentRowStart,currentRowLimit))
    rows = cursor.fetchall() #fetch all rows

    for row in rows:
        framelet_list = pickle.loads(row.ImageByteArray)

        frameCount = 0
        for framelet in framelet_list:
            if (framelet.cmd != Commands.NO_CMD.value and framelet.cmd != Commands.STOP_ALL_MOTORS.value):
                frameCount +=1
        updateFrameCount(frameCount, row.MyGuid, cursor) #TODO: check if column name is MyGuid?
        print("updated row {0} --- TrainableFrameCount={1}".format(row.Id, frameCount))
    currentRowStart = currentRowLimit + 1 #add 1 b/c 'between' cmd is inclusive in sql
    currentRowLimit += 50 #increase by 50
    
    cursor.commit() #commit (save) to database

print("Finished Updating all rows")


    

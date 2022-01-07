'''
CHANGE ALL DATA WITH NO_CMD TO ANOTHER CMD, like Forward
'''

import pyodbc
import pickle
import cv2
import time
from RaspberryPi.CollectingTrainingData.Commands import Commands

def containsNo_Cmd(framelet_list):
    for framelet in framelet_list:
        if(framelet.cmd == Commands.NO_CMD.value):
            return True;
    return False;

def updateFrameletList(framelet_list, cmdToChange, newCmdToApply):
    newList = framelet_list
    for framelet in newList:
        if(framelet.cmd == cmdToChange):
            framelet.cmd = newCmdToApply
    return newList

def previewFrameletList(framelet_list):
    for framelet in framelet_list:
        cv2.imshow('i', framelet.frame)
        print(Commands.parseCommand(framelet.cmd))
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

def updateToTable(cursor, rowGuid, framelet_list):
    framelet_byteArray = pickle.dumps(framelet_list, 4) #protocal 4, the latest
    cursor.execute("UPDATE poc.TrainingData SET ImageByteArray=?, WasUpdated='Yes'WHERE MyGuid=?", framelet_byteArray, rowGuid)

def main():
    server = ''
    database = ''
    username = ''
    password = ''
    driver = '{ODBC Driver 13 for SQL Server}'

    cnxn = pyodbc.connect(
        'DRIVER=' + driver + ';SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
    cursor = cnxn.cursor()


    try:
        cursor.execute("SELECT * FROM poc.TrainingData WHERE Evaluation is NULL and WasUpdated is NULL")
        rows = cursor.fetchall() #fetch one row
        for row in rows:
            print("Row ID = {}".format(row.Id))
            currentFramelet_list= pickle.loads(row.ImageByteArray) #a video clip of framelets
            if(containsNo_Cmd(currentFramelet_list)):
                print('previewing')
                previewFrameletList(currentFramelet_list)
                yesNo = input("Change these No_Cmd to Forward? (y or n)")
                if(yesNo == 'y'):
                    newFrameletList = updateFrameletList(currentFramelet_list,Commands.NO_CMD.value, Commands.FORWARD.value)
                    previewFrameletList(newFrameletList)
                    goodBad = input("should proceed to change? (y or n)")
                    if(goodBad == 'y'):
                        updateToTable(cursor, row.MyGuid, newFrameletList)
                    else:
                        cursor.execute("UPDATE poc.TrainingData SET WasUpdated='Yes' WHERE MyGuid=?", row.MyGuid)
                        print("ok")
                else:
                    cursor.execute("UPDATE poc.TrainingData SET WasUpdated='Yes' WHERE MyGuid=?", row.MyGuid)
                    print("showing next clip")
            cnxn.commit()
    except Exception as e:
        print(e)
    finally:
        cnxn.commit()
        print("commited to database")



main()


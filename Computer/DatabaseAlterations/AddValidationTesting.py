import pyodbc
import pickle
import cv2
from random import shuffle, randint
import time
from RaspberryPi.CollectingTrainingData.Commands import Commands

def getRowsListShuffled(cursor, table):
    '''returns list tuples of rows as (row.Id, row.FrameCount)'''
    query = """SELECT Id, FrameCount FROM {0} WHERE Evaluation='Good' and FileName not like '%GeneratedFlip%' order by 1 asc""".format(table)
    cursor.execute(query)
    rows = cursor.fetchall()
    # rowIdList = []
    # frameCountList = []
    rowsList = []
    frameCount = 0

    for row in rows:
        rowsList.append((row.Id, row.FrameCount))
        # rowIdList.append(int(row.Id))
        # frameCountList.append(int(row.FrameCount))
        frameCount += int(row.FrameCount)

    shuffle(rowsList)
    rowIdList = list(zip(*rowsList))[0]  # unzip and get the first list
    frameCountList = list(zip(*rowsList))[1]
    return list(rowIdList), list(frameCountList), frameCount

#INIT the SQL Table
wrongInput = True
table = "";
while(wrongInput):
    tableInput = input("Which SQL Table will you like to evaluation?\n\t-SteeringAngleData (s)\n\t-DiscreteTurnsData (d)\n")
    if(tableInput == 's'):
        table= 'trainData.SteeringAngleData'
        wrongInput = False;
    elif(tableInput =='d'):
        table='poc.TrainingData'
        wrongInput = False;
    else:
        print("Wrong input, Please type in 's' for SteeringAngleData or 'd' for DiscreteTurnsData")

# INIT Database information
server = ''
database = ''
username = ''
password = ''
driver= '{ODBC Driver 13 for SQL Server}'

cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()

#get rows list of 'good' evaluation
rowIdList, frameCountList, frameCount = getRowsListShuffled(cursor, table)
print(type(rowIdList))
# rowIdList = rowsList[0]
# frameCountList = frameCount

print("Total Frame count: {}".format(frameCount))
print("Number of rows that are 'Good' Evaluation: {}".format(len(rowIdList)))

#Get FrameCount of Total
# cursor.execute("""SELECT sum(FrameCount) as TotalFrameCount FROM {0} WHERE Evaluation='Good' and FileName not like '%GeneratedFlip%'""".format(table))
# row = cursor.fetchone()
# frameCount = int(row.TotalFrameCount)


#Calculate x% of Total Framecount to be validation, testing
validationFrameCountGoal = int(.05 * frameCount)
testingFrameCountGoal = int(.05 * frameCount)

#Change rows to evaluation of -----VALIDATION until
cursor.execute("""SELECT sum(FrameCount) as TotalFrameCount FROM {0} WHERE Evaluation='Validation'""".format(table))
row = cursor.fetchone()
currentValidationFrameCount = row.TotalFrameCount #get already amount of Validation frame count
if(currentValidationFrameCount == None):
    currentValidationFrameCount = 0


print("Changing VALIDATION")
index = 0
while currentValidationFrameCount < validationFrameCountGoal:
    cursor.execute("""UPDATE {0} SET Evaluation='Validation' WHERE Id=?""".format(table),rowIdList[index])
    currentValidationFrameCount += frameCountList[index]
    print("updated row: {}".format(rowIdList[index]))
    rowIdList.pop(index)
    frameCountList.pop(index)
    index +=1
print("Total Validation Frame count: {}".format(currentValidationFrameCount))
print("len(rowIdList) = {}".format(len(rowIdList)))

cursor.commit()


#Change rows to evaluation of ---------TESTING
cursor.execute("""SELECT sum(FrameCount) as TotalFrameCount FROM {0} WHERE Evaluation='Testing'""".format(table))
row = cursor.fetchone()
currentTestingFrameCount = row.TotalFrameCount
if(currentTestingFrameCount == None): #get already amount of Testing frame count
    currentTestingFrameCount = 0


print("Changing Testing")
index = 0
while currentTestingFrameCount < testingFrameCountGoal:
    cursor.execute("""UPDATE {0} SET Evaluation='Testing' WHERE Id=?""".format(table),rowIdList[index])
    print("updated row: {}".format(rowIdList[index]))
    currentTestingFrameCount += frameCountList[index]
    rowIdList.pop(index)
    frameCountList.pop(index)
    index += 1

print("Total Testing Frame count: {}".format(currentTestingFrameCount))

cursor.commit()










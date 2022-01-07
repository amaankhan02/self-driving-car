'''
Allows me to view Framelets from SQL DB and mark as good/bad for my data
'''
import pyodbc
import pickle
import cv2
import time
from RaspberryPi.CollectingTrainingData.Commands import Commands

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
    # elif cmd == Commands.BACK_MOTOR_STOP.value:
    #     return 'BACK_MOTOR_STOP'
    # elif cmd == Commands.RESET_STEER.value:
    #     return 'RESET_STEER'
    else:
        return None

def parseEvaluation(evaluation):
    if evaluation == 'g':
        return "Good"
    elif evaluation == 'b':
        return "Bad"
    elif evaluation == 't':
        return "Testing"
    elif evaluation == 'p':
        return "NULL" #set to null to check over that data again later
    else:
        return -1

def updateEvaluation(cursor, evaluation, guid, table):
    query = """UPDATE {0} SET Evaluation=? WHERE MyGuid=?""".format(table)
    cursor.execute(query,evaluation, guid)


#setup sql connection
server = ''
database = ''
username = ''
password = ''
driver= '{ODBC Driver 13 for SQL Server}'


cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()


wrongInput = True
while(wrongInput):
    tableInput = input(
        "Which SQL Table will you like to evaluation?\n\t-SteeringAngleData (s)\n\t-DiscreteTurnsData (d)\n")
    if(tableInput == 's'):
        table= 'trainData.SteeringAngleData'
        wrongInput = False;
    elif(tableInput =='d'):
        table='poc.TrainingData'
        wrongInput = False;
    else:
        print("Wrong input, Please type in 's' for SteeringAngleData or 'd' for DiscreteTurnsData")


query1 = "SELECT * FROM {} where Evaluation is NULL and Id > 120 ORDER BY FileName ASC".format(table)
query2 = "Select X.* From (SELECT *,Row_Number() over (Order by FileName) as RN from {}) As X where X.Evaluation is NULL".format(table)
query3 = "SELECT TOP 150 * FROM {} where Evaluation is NULL order by 1 asc".format(table)
query4 = "SELECT * FROM {} where Evaluation = 'Good' and Id BETWEEN 40 and 70".format(table)

cursor.execute(query4)
rows = cursor.fetchall()
# row = cursor.fetchone()

for row in rows:
    framelet_list = pickle.loads(row.ImageByteArray)
    guid = row.MyGuid;
    replay = True;
    while replay:
        #play the video clip
        for framelet in framelet_list:
            cv2.imshow('i', framelet.frame[112:228])
            cv2.imshow("full", framelet.frame)
            if(framelet.cmd != None):
                print(parseCommand(framelet.cmd))
            if(table == "trainData.SteeringAngleData"):
                if(framelet.steerDegree != None):
                    print(framelet.steerDegree);
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
            time.sleep(.3)
        print("ROW ID: {}".format(row.Id))
        print("Evaluation is ALREADY: {}".format(row.Evaluation))
        userInput = input("Good (g), Bad (b), Testing (t), Repeat (r), Check later (p), Quit(q)") #"Testing" is for saving as Testing Data
        if(userInput == 'q'): #quit application
            replay=False;
        elif(userInput == 'r'): #repeat
            print("repeating...")
            time.sleep(0.3) #sleep for 0.3 seconds before replaying
        else:
            evaluation = parseEvaluation(userInput)
            if(evaluation == -1): #an invalid input
                print("INVALID INPUT, replaying in 0.5 seconds")
                time.sleep(0.5)
            elif(evaluation == "NULL"): #check data later cmd, leave the current evaluation to be same as before
                replay = False;
                # cursor.execute("UPDATE poc.TrainingData SET Evaluation is NULL WHERE MyGuid=?", guid)
            else: #a good cmd
                print("--------------------------------")
                updateEvaluation(cursor, evaluation, guid, table)
                replay = False;
        cnxn.commit()

# # SHOW ALL IMAGES
# imgs = 0
# rowsCount = 0
# turns = 0
# while row is not None:
#     framelet_list = pickle.loads(row.ImageByteArray)
#     play = True;
#     rowsCount +=1
#     for framelet in framelet_list:
#         imgs+=1
#         if(framelet.cmd == Commands.LEFT.value or framelet.cmd == Commands.RIGHT.value):
#             turns+=1
#         # cv2.imshow('i', framelet.frame)
#         # if cv2.waitKey(1) & 0xFF == ord("q"):
#         #     break
#         # time.sleep(0.01)
#     row = cursor.fetchone()
# print(imgs)
# print(rowsCount)
# print(turns)


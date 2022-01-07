import sys
import pickle
import pyodbc
import os
import glob
import time
import shutil
import uuid
from os.path import isfile, join
from os import listdir
import argparse

'''
-- Runs automatically from a Task Scheduler
'''

# #argparse -- cmd line input
# parser = argparse.ArgumentParser(description="Save Discarded or Training data?")
# parser.add_argument('--num', dest='num', required=True, metavar='N', type=int, nargs='+',
#                     help='an integer from the accumulator')
# args = parser.parse_args()
# print(args.num[0])

def removePath(path):
    '''returns the only the filename without the path'''
    return os.path.basename(path)

def removeExtension(path):
    return os.path.splitext(path)[0]

def SaveToSql(connectionCursor, file, guid, frameCount, table):
    t0 = time.time()
    # guid = uuid.uuid4()

    with open(file, 'rb') as content_file:
        filecontent = content_file.read()
        #get the name without path
        name = keepDataTime(content_file.name)
        insertQuery = """INSERT INTO {0}(FileName,ImageByteArray, MyGuid, FrameCount)
                    SELECT ?, ?, ?, ? """.format(table)
        connectionCursor.execute(insertQuery, name, filecontent, guid, frameCount)
        t1 = time.time()
        duration = t1-t0
        updateQuery = """UPDATE {0} SET ProcessingTime=? WHERE MyGuid=?""".format(table)
        connectionCursor.execute(updateQuery, duration, guid)
        print("Time: {} seconds".format(round(t1-t0,2)))
        #TODO: add file size to table

def doesContainsFiles(path):
    '''https://stackoverflow.com/a/33463354/7359915'''
    return any(isfile(join(path, i)) for i in listdir(path))

def getFrameCount(fileName):
    fileNameSplit = fileName.split('-frameCount-') #create 2 arrays where split on -frameCount-
    count = int(fileNameSplit[1][0:3]) #gets second half with number and gets first 3 elements representing the number
    return count

def keepDataTime(filename):
    '''removes unnecessary parts in filename and returns what is needed'''
    newName = removePath(filename) #remove the path directory
    newName = removeExtension(newName) #remove the extension
    newName = newName.replace('_processing', '')  # removes the statues _processing
    newName = newName.replace('-frameCount-', '') #
    newName = newName[:-3]  # remove last 3 digits (framecount)
    return newName;

def mainProcess(file,table):
    newFileName = ""
    oldestFile = ""
    # movingDirectory = 'I:\SavedPickles\\'
    try:
        oldestFile = min(file, key=os.path.getctime)  # get oldest file
        newFileName = oldestFile.replace('_ready', '_processing')
        os.rename(oldestFile, newFileName)

        print("found pickle file - {}".format(str(oldestFile)))
        guid = uuid.uuid4()
        frameCount = getFrameCount(newFileName)
        SaveToSql(cursor, newFileName, guid, frameCount, table)
        os.remove(newFileName)  # delete file
        # os.remove(newFileName)
        # name = removePath(newFileName)
        # shutil.move(newFileName, movingDirectory + name)
        # os.rename(newFileName, movingDirectory + name)
    except Exception as e:
        os.rename(newFileName, oldestFile)
        print(e)
        # TODO: fix adding the error to database, not working, do i update or insert?
        # cursor.execute("""UPDATE poc.TrainingData SET ErrorMessage=? WHERE MyGuid=?""", e, guid)
    finally:
        print("Updated {}".format(table))
        cnxn.commit()  # commit to the database -- or else it wont save

#connect to SQL Database
server = ''
database = ''
username = ''
password = ''
driver= '{ODBC Driver 13 for SQL Server}'

cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()

discreteTurnsData_pickleFiles = 'Z:\\DiscreteTurnData\\training_data\\*_ready.pickle' # get all pickle files in directory
steerAngleData_pickleFiles = r'Z:\SteeringAngleData\training_data\*_ready.pickle'
if os.path.exists('Z:\\'):
    if(doesContainsFiles(r'Z:\SteeringAngleData\training_data\\')):
        file = glob.glob(steerAngleData_pickleFiles)
        mainProcess(file, "trainData.SteeringAngleData")
    else:
        print("no files in steering angle data directory")

    if(doesContainsFiles('Z:\\DiscreteTurnData\\training_data\\')):
        file = glob.glob(discreteTurnsData_pickleFiles)
        mainProcess(file, "poc.TrainingData")
    else:
        print("no files in discrete turns data directory")
else:
    print("path does not exist")

print("closing")
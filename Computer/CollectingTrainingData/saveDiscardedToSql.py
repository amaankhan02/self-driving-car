
import pickle
import pyodbc
import os
import glob
import time
import shutil
import uuid
from os.path import isfile, join
from os import listdir
'''
Saves the Discarded the Recordings to the Database
-- Runs automatically from a Task Scheduler

*******DEPRECATE THIS, ADD THIS AS AN ARGUMENT INTO SAVETOSQL.PY********************************
'''


#connect to SQL Database
server = ''
database = ''
username = ''
password = ''
driver= '{ODBC Driver 13 for SQL Server}'

cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()

def removePath(path):
    '''returns the only the filename without the path'''
    return os.path.basename(path)

def removeExtension(path):
    return os.path.splitext(path)[0]

def SaveToSql(connectionCursor, file, guid):
    t0 = time.time()

    with open(file, 'rb') as content_file:
        filecontent = content_file.read()
        #get the name without path
        name = removePath(content_file.name)
        name = removeExtension(name)
        connectionCursor.execute("""INSERT INTO poc.TrainingData(FileName,ImageByteArray, MyGuid, Evaluation)
                    SELECT ?, ?, ?, ? """,name,filecontent, guid, 'Discarded')
        t1 = time.time()
        duration = t1-t0
        connectionCursor.execute("""UPDATE poc.TrainingData SET ProcessingTime=? WHERE MyGuid=?""", duration, guid)
        #TODO: add file size to table

def doesContainsFiles(path):
    '''https://stackoverflow.com/a/33463354/7359915'''
    return any(isfile(join(path, i)) for i in listdir(path))

discreteTurnsData_pickleFiles = 'Z:\\discarded_data\\*_ready.pickle' # get all pickle files in directory
if os.path.exists('Z:\\'):
    if(doesContainsFiles('Z:\\discarded_data\\')):
        file = glob.glob(discreteTurnsData_pickleFiles)
        newFileName = ""
        oldestFile = ""
        try:
            oldestFile = min(file, key=os.path.getctime)  # get oldest file
            newFileName = oldestFile.replace('_ready', '_processing') #change name so another program doesn't try saving the same file
            os.rename(oldestFile, newFileName)

            print("found pickle file - {}".format(str(oldestFile)))
            guid = uuid.uuid4()
            SaveToSql(cursor, newFileName, guid)
            # os.remove(newFileName)
            # name = removePath(newFileName)
            # shutil.move(newFileName, movingDirectory + name)
            os.remove(newFileName)  # delete file
            # os.rename(newFileName, movingDirectory + name)
        except Exception as e:
            print(e)
            os.rename(newFileName, oldestFile)
            # TODO: fix adding the error to database, not working, do i update or insert/
            # cursor.execute("""UPDATE poc.TrainingData SET ErrorMessage=? WHERE MyGuid=?""", e, guid)
        finally:
            print("closing")
            cnxn.commit()  # commit to the database -- or else it wont save
    else:
        print("no files in directory")

else:
    print("path does not exist")
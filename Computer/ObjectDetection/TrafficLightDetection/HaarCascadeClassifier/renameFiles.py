"""used to rename imgs from neg directory"""


import os
import glob
from sklearn.model_selection import train_test_split
from random import random, shuffle
import shutil

def renameNegatives():
    count = 855
    directory = r"I:\TFS\AK\MyProjects\Development\SelfDrivingCar\Computer\ObjectDetection\TrafficLightDetection\HaarCascadeClassifier\temp_neg"
    for filename in os.listdir(directory):
        # newFileName = filename.replace('redLight_', "neg_{0:03d}".format(count)) #remove the redLight
        fullPath = os.path.join(directory, filename)
        #
        newName = "negImg_{0:03d}.png".format(count)
        newFullPath = os.path.join(directory,newName)

        os.rename(fullPath,newFullPath)
        print(count)
        count+=1;

renameNegatives()
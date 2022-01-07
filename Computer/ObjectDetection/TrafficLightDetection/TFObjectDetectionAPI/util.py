"""
Quick refactor code for my data
"""

import os
import glob
from sklearn.model_selection import train_test_split
from random import random, shuffle
import shutil

# count = 1
# directory = "I:\TFS\AK\MyProjects\Development\SelfDrivingCar\Computer\ObjectDetection\TrafficLightDetection\\TrafficLightLabeledData\Train"
# for filename in os.listdir(directory):
#     if filename.endswith('.xml') and "redLight" in filename:
#         newFileName = filename.replace('redLight_', '') #remove the redLight
#         fullPath = os.path.join(directory,filename)
#         newFullPath = os.path.join(directory, newFileName)
#         os.rename(fullPath, newFullPath)
#         print("original: {}, new: {}".format(fullPath, newFullPath))

#split train-test

# filesList = os.listdir(directory + "\\TrafficLightLabeledData")
# shuffle(filesList)
# shuffle(filesList)
#
# #10% in test folder
# maxIndex = int(.1*(len(filesList)))
# for i in range(maxIndex):
#     fullPath = os.path.join(directory + "\\TrafficLightLabeledData", filesList[i])
#     newFullPath = os.path.join(directory + "\Test", filesList[i])
#     shutil.move(fullPath, newFullPath)
#     print(filesList[i])
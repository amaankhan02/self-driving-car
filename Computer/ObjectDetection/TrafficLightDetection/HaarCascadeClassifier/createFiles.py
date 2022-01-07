
import os
import csv
"""
used to create contents of bg.txt, trafficLight.info, etc
    ****iF DOESN'T WORK -- Run from CMD Line***
"""

def createBgTxt(negativeSamplesPath):
    """
    :param negativeSampleFolderName: name of folder where negative sample images are located
    """

    folderName = os.path.basename(negativeSamplesPath)

    with open("bg.txt", "w+") as f:  # the '+' in "w" means "create file if doesn't exist", 'w' means "write to file"
        for filename in os.listdir(negativeSamplesPath):
            f.write(folderName + "/" + filename + "\n")

def createPosSampleAnnotations_from_csv(csv_annotation_file, file_to_write, positiveImgSampleDirectory):
    nameFormat = "{0}\{1} 1 {2} {3} {4} {5}" #folder/filename 1 x y width height

    #contents from csv
    filenames = []
    xLocations = []
    yLocations = []
    widths = []
    heights = []

    rowCount = 1;
    #open csv file
    with open(csv_annotation_file) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV:
            if(rowCount != 1): #first row is the column heading, so don't print that
                filenames.append(row[0])
                xLocations.append(row[2])
                yLocations.append(row[3])
                widths.append(row[4])
                heights.append(row[5])
            rowCount+=1;


    with open(file_to_write, "w+") as f:
        for i in range(len(filenames)):
            lineContent = nameFormat.format(positiveImgSampleDirectory,
                                            filenames[i],
                                            xLocations[i],
                                            yLocations[i],
                                            widths[i],
                                            heights[i])
            f.write(lineContent + '\n')


# createBgTxt(r'I:\TFS\AK\MyProjects\Development\SelfDrivingCar\Computer\ObjectDetection\TrafficLightDetection\HaarCascadeClassifier\neg')

parentDirectory = "I:\TFS\AK\MyProjects\Development\SelfDrivingCar\Computer\ObjectDetection\TrafficLightDetection\HaarCascadeClassifier"
# csv_annotation_file = os.path.join(parentDirectory,'annotations.csv')
# file = os.path.join(parentDirectory, 'info.dat')
# createPosSampleAnnotations_from_csv(csv_annotation_file,file,os.path.join(parentDirectory,'pos'))

createBgTxt(r"I:\TFS\AK\MyProjects\Development\SelfDrivingCar\Computer\ObjectDetection\TrafficLightDetection\HaarCascadeClassifier\neg")
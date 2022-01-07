"""
From https://github.com/datitran/raccoon_dataset/blob/master/xml_to_csv.py
"""

import os
import glob
import pandas as pd
import xml.etree.ElementTree as ET


def xml_to_csv(path):
    xml_list = []
    for xml_file in glob.glob(path + '/*.xml'):
        tree = ET.parse(xml_file)
        root = tree.getroot()
        for member in root.findall('object'):
            xmin = int(member[4][0].text)
            ymin = int(member[4][1].text)
            xmax = int(member[4][2].text)
            ymax = int(member[4][3].text)
            width = xmax - xmin
            height = ymax - ymin

            value = (root.find('filename').text,
                     member[0].text,
                     xmin,
                     ymin,
                     width,
                     height
                     )
            xml_list.append(value)
    # column_name = ['filename', 'width', 'height', 'class', 'xmin', 'ymin', 'xmax', 'ymax']
    column_name = ['filename', 'class', 'xmin', 'ymin', 'width', 'height']
    xml_df = pd.DataFrame(xml_list, columns=column_name)
    return xml_df


def main():
    #convert the xml annotations in annotation folder into a csv
    annotations_directory = \
        "I:\TFS\AK\MyProjects\Development\SelfDrivingCar\Computer\ObjectDetection\TrafficLightDetection\HaarCascadeClassifier\pos_annotations"
    # image_path = os.path.join(os.getcwd(), 'TrafficLightLabeledData\{}'.format(directory))
    xml_df = xml_to_csv(annotations_directory)
    xml_df.to_csv('annotations.csv', index=None)
    print('Successfully converted xml to csv.')

main()
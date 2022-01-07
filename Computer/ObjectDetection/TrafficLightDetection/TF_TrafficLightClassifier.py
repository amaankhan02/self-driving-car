import socket
from _thread import *
import threading
import io
import socketserver
import struct
import cv2
import numpy as np
from Computer.Autonomous.KerasDiscreteTurnsModel import KerasDiscreteTurnsModel
import atexit
from tkinter import *
import time
sys.path.append(r'C:\Program Files\tensorflow-models\research\object_detection')
sys.path.append(r'C:\Program Files\tensorflow-models\research\object_detection\slim')
from utils import label_map_util
from utils import visualization_utils as vis_util
import tensorflow as tf
import os
from PIL import Image

class TF_TrafficLightClassifier:
    def __init__(self, path_to_ckpt, path_to_labels):
        """

        :param path_to_ckpt: path to the frozen_inference_graph.pb
        :param path_to_labels:
        """
        num_classes = 2
        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(path_to_ckpt, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')
            self.image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
            self.detection_boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
            self.detection_scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
            self.detection_classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
            self.num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')
        self.sess = tf.Session(graph=self.detection_graph)

        #get category index
        label_map = label_map_util.load_labelmap(path_to_labels)
        categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=num_classes,use_display_name=True)
        self.category_index = label_map_util.create_category_index(categories)
        self._trafficLightWidth = 0
        self._trafficLightHeight = 0

    def get_classification(self, rgbImg, threshold_percentAbundance):
        """
        :param rgbImg:
        :param threshold_percentAbundance: threshold percent of minimum abundance of color in img
        :return: np.squeeze() of all of --> boxes,scores,classes,num
        """
        # Bounding box detection
        with self.detection_graph.as_default():
            #expand dimsions since the model expencts image to have shape [1, None, none, 3]
            img_expanded = np.expand_dims(rgbImg, axis=0)
            (boxes, scores, classes, num) = self.sess.run(
                [self.detection_boxes, self.detection_scores, self.detection_classes, self.num_detections],
                feed_dict={self.image_tensor: img_expanded})

            boxes = np.squeeze(boxes)
            classes = np.squeeze(classes)
            scores = np.squeeze(scores)
            max_index = np.argmax(scores)

            if(scores[max_index] > 0.8):
                ymin, xmin, ymax, xmax = self._getBoundingBoxCoordinates(boxes[max_index], rgbImg.shape[0], rgbImg.shape[1])
                self._trafficLightWidth = xmax - xmin
                self._trafficLightHeight = ymax - ymin
                cropImg = rgbImg[ymin:ymax, xmin:xmax] #crop to just the traffic light
                color = self._identifyColor(cropImg, threshold_percentAbundance)
            else:
                color = 'none'
            return color
            #TODO: Add percent abundance of color to decide in identifyColor()

    def _getBoundingBoxCoordinates(self,box, height, width):
        """
        returns coordinates of bounding box in pixels
        :param box: 1 Tensor returned from tensorflow object detection prediction of 1 set of ymin, xmin, ymax, xmax
        :param height: height of image
        :param width: width of image
        :return: ymin, xmin, ymax, xmax coordinates in image of bounding box
        """
        # coordinates return the percent of height or width
        ymin, xmin, ymax, xmax = tuple(box.tolist())
        # convert to coordinate points
        ymin = int(ymin * height)
        ymax = int(ymax * height)
        xmin = int(xmin * width)
        xmax = int(xmax * width)
        return ymin, xmin, ymax, xmax

    def _identifyColor(self, rgbImg, threshold_percentAbundance):
        """
        gets color of traffic light. if does not seem to be a traffic light color, return none
        :param rgbImg:
        :param threshold_percentAbundance: threshold percent of minimum abundance of color in img
        :return: 'red' or 'green' or 'none' -- String values returned
        """
        hsvImg = cv2.cvtColor(rgbImg, cv2.COLOR_RGB2HSV)  # FULL indicates hue in range 0 - 255, else it is 0 - 180

        # take count
        redCount = 0
        greenCount = 0
        noneCount = 0;  # holds count for when not green or red

        for row in hsvImg:
            for pixel in row:
                hue = pixel.item(0)
                value = pixel.item(2)
                if (hue >= 150 and hue <= 180):  # red (magenta in HSV scale)
                    redCount += 1;
                elif (hue >= 0 and hue <= 60 and value >= 200):  # check if range of [0,60] and value is above 200. Explanation in OneNote
                    redCount += 1;
                elif (hue >= 60 and hue <= 120):  # green (green and cyan in HSV scale)
                    greenCount += 1;
                else:
                    noneCount += 1

        maxCount = max(max(redCount, greenCount), noneCount)
        percentAbundance = maxCount / (rgbImg.shape[0] * rgbImg.shape[1])
        # print("percent abundance: ", maxCount/(rgbImg.shape[0]*rgbImg.shape[1]))
        # print("redCount: {0}\ngreenCount: {1}\nnoneCount: {2}".format(redCount,greenCount,noneCount))
        if(percentAbundance >= threshold_percentAbundance):
            if (redCount == maxCount):
                return 'red'
            elif (greenCount == maxCount):
                return 'green'
            else:
                return 'none'
        else:
            return 'none'

    def getTrafficLightWidth(self):
        return self._trafficLightWidth

    def getTrafficLightHeight(self):
        return self._trafficLightHeight



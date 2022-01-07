import numpy as np
np.random.seed(1337)
import cv2
import pathlib
from Computer.NN_Trainer.NormalizationMethod import NormalizationMethod
import json
from matplotlib import pyplot as plt
import keras
from keras.layers import Dense, Dropout, Flatten, Lambda, ELU, Cropping2D, GlobalAveragePooling2D
from keras.layers.convolutional import MaxPooling2D, Conv2D;
from keras.regularizers import l2
from keras.preprocessing.image import ImageDataGenerator
from keras.optimizers import Adam, SGD
from keras.constraints import maxnorm
from keras.models import Model

from keras.applications.vgg16 import VGG16, preprocess_input
from keras.applications.vgg19 import VGG19, preprocess_input
from keras.applications.xception import Xception, preprocess_input
from keras.applications.resnet50 import ResNet50, preprocess_input
from keras.applications.inception_v3 import InceptionV3, preprocess_input



def add_new_last_layer(base_model, nb_classes, FC_size):
    """Add Last layer to the convnet
    :param base_model: keras model exluding last layer
    :param nb_classes: # of classes for output
    :param FC_size: Fully connected layer size (# of nodes)
    :return: new keras model with last layer
    """
    x = base_model.output;
    x = GlobalAveragePooling2D()(x) #converts the 3D tensor ouput into 1xC where c is # of channels
    x = Dense(FC_size)(x)
    predictions = Dense(nb_classes)(x)
    model = Model(input=base_model.input,outputs=predictions)
    return model;

def setup_to_transfer_learn(model, base_model):
    """Freeze all layers and compile the model"""
    for layer in base_model.layers:
        layer.trainable=False;
    model.compile(optimizer='rmsprop',
                  loss='mse',
                  metrics=['accuracy'])

def setup_to_finetune(model, nb_layers_to_freeze):
    """
    Freeze the bottom NB_IV3_Layers and retrain the remainging top layers
    note: NB_IV3_LAYERS corresponds to the top 2 inception blocks in
     the inceptionv3 architecture
    :param model: keras model
    :return:
    """
    for layer in model.layers[:nb_layers_to_freeze]:
        layer.trainable = False
    for layer in model.layers[nb_layers_to_freeze:]:
        layer.trainable = True;
    model.compile(optimizer=SGD(lr=0.0001, momentum=0.9),
                  loss='mse')

# def getBaseInceptionV3Model():
#     '''
#     Once you get this model, in code, use setup_to_transfer()
#     then train it, then use setup_to_finetune()
#     then train again, then save
#     :param self:
#     :return:
#     '''
#     #include_top=False is to leave out the weights of the last FCL since that is specific to ImageNet
#     #We will add a new last layer
#     base_model = InceptionV3(weights='imagenet', include_top=False)





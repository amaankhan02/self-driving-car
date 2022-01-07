from keras.utils.generic_utils import get_custom_objects
import numpy as np
np.random.seed(1337)
import cv2
import pathlib
from Computer.NN_Trainer.NormalizationMethod import NormalizationMethod
import json
from matplotlib import pyplot as plt
import keras
from keras.layers import Dense, Dropout, Flatten, Lambda, ELU, Cropping2D
from keras.layers.convolutional import MaxPooling2D, Conv2D;
from keras.regularizers import l2
from keras.initializers import glorot_normal
from keras.preprocessing.image import ImageDataGenerator
from keras.optimizers import Adam, SGD
from keras.constraints import maxnorm

from keras.applications.vgg16 import VGG16, preprocess_input
from keras.applications.vgg19 import VGG19, preprocess_input
from keras.applications.xception import Xception, preprocess_input
from keras.applications.resnet50 import ResNet50, preprocess_input
from keras.applications.inception_v3 import InceptionV3, preprocess_input

from keras.models import Sequential
from keras.backend import tf
from keras import backend
backend.set_image_dim_ordering('tf') #TODO: Change this to 'tf' - https://stackoverflow.com/questions/39547279/loading-weights-in-th-format-when-keras-is-set-to-tf-format
from keras.callbacks import Callback, ModelCheckpoint
from keras.utils import plot_model, np_utils
# from sklearn.cross_validation import train_test_split #--> sklean.cross_validation is deprecated
from sklearn.model_selection import train_test_split
import time

from PIL import Image
import pickle
from Dataset import Dataset
from DataGenerator import DataGenerator
from keras_tqdm import TQDMNotebookCallback
from TrainType import TrainType
from ipywidgets import IntProgress
# import tensorflow as tf
from keras import applications

from Computer.NN_Trainer.PretrainedModel import *

## Callback for loss logging per epoch
class LossHistory(Callback):
    def on_train_begin(self, logs={}):
        self.losses = []
        self.val_losses = []


    def on_epoch_end(self, epoch, logs={}):
        self.losses.append(logs.get('loss'))
        self.val_losses.append(logs.get('val_losses'))
        # print("----Epoch: {} --- Validation Loss: {} ---- Training Loss: {}")

class AccuracyCallBack(Callback):
    def on_train_begin(self, logs=None):
        self.val_accuracy = []
        self.train_accuracy = []

    def on_batch_end(self, batch, logs=None):
        self.val_accuracy.append(logs.get('val_acc'))
        self.train_accuracy.append(logs.get('acc'))


#hyperparameters
batchSize = 32
epochs = 8
lrate = 1e-4
L2_REG_SCALE = 0.
normalizationMethod = NormalizationMethod.none;
#pretrained model hyperparameters
FC_SIZE_IV3 = 1024
NB_IV3_LAYERS_TO_FREEZE = 172

def create_model_discreteTurns():
    # Create model
    model = Sequential()

    topCrop = 112; # num of pixels to crop from top
    bottomCrop = 12; # num of pixels to crop from bottom
    resizeWidth = 320;
    resizeHeight = 240 - topCrop - bottomCrop;

    model.add(Cropping2D(cropping=((topCrop, bottomCrop), (0, 0)),
                         dim_ordering='tf',  # default
                         input_shape=(240, 320, 3)))
    model.add(Lambda(lambda x: x / 255.0, input_shape=(resizeHeight, resizeWidth, 3)))
    model.add(Conv2D(32, (3, 3), padding='same', activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(32, (3, 3), padding='same', activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(64, (3, 3), activation='relu', padding='same'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Dropout(0.25))
    model.add(Flatten())
    model.add(Dense(64, activation='relu'))  # Dense() creates a normal NN layer, 1st param is number of units/nodes
    model.add(Dropout(0.5))
    model.add(Dense(4, activation='softmax'))  # 4 is the number of units in Dense Layer

    model.compile(optimizer=Adam(lr=lrate), loss='categorical_crossentropy',
                  metrics=['accuracy'])  # include metrics=['accuracy'] for it to display accuracy
    return model
def create_commasAiModel_discreteTurns():
    """
    	Creates the comma.ai model w/ a little tweaks, and returns a reference to the model
    	The comma.ai model's original source code is available at:
    	https://github.com/commaai/research/blob/master/train_steering_model.py
    	"""
    # ch, row, col = 3, 120, 320  # camera format

    model = Sequential()
    #NORMAL COMMAS AI MODEL
    #Normalize inputs between [-1,1]
    # model.add(Lambda(lambda x: x / 127.5 - 1.,
    #                  input_shape=(row, col, ch),
    #                  output_shape=(row, col, ch)))
    # model.add(Conv2D(16, 8, 8, subsample=(4, 4), border_mode='same', W_regularizer=l2(L2_REG_SCALE))) #
    # model.add(ELU()) #
    # model.add(Conv2D(32, 5, 5, subsample=(2, 2), border_mode='same', W_regularizer=l2(L2_REG_SCALE))) #
    # model.add(ELU()) #
    # model.add(Conv2D(64, 5, 5, subsample=(2, 2), border_mode='same', W_regularizer=l2(L2_REG_SCALE)))#
    # model.add(Flatten()) #
    # model.add(Dropout(.2)) #
    # model.add(ELU()) #
    # model.add(Dense(512, W_regularizer=l2(0.))) #
    # model.add(Dropout(.5))
    # model.add(ELU())
    # model.add(Dense(1, W_regularizer=l2(0.)))

    #TWEAKED VERSION
    model.add(Conv2D(16, (5,5),strides=(2,2) ,input_shape=(120,320,3), padding='same', W_regularizer=l2(L2_REG_SCALE))); '''Changed from (8,8) kernel to (5,5) and stride to 2,2 from 4,4 previously'''
    model.add(ELU())
    model.add(Conv2D(32, (3,3), strides=(1,1), padding='same', W_regularizer=l2(L2_REG_SCALE))); '''Changes: (5,5) to (3,3) kernel, stride 2,2 to 1,1'''
    model.add(ELU())
    model.add(Conv2D(64, (3,3), strides=(1,1), padding='same', W_regularizer=l2(L2_REG_SCALE))); '''Changes: (5,5) to (3,3) kernel, stride 2,2 to 1,1'''

    model.add(Flatten())
    model.add(Dropout(0.2))
    model.add(ELU())
    model.add(Dense(512, W_regularizer=l2(0.)))
    model.add(Dropout(.5))
    model.add(ELU())
    model.add(Dense(4, activation='softmax'))

    model.compile(optimizer=Adam(lr=lrate), loss='categorical_crossentropy',  metrics=['accuracy'])

    return model
#NOTE: NORMALIZE BETWEEN NEG 1 AND 1
'''#NOTE: DO NOT APPLY NORMALIZATION, NORMALIZATION IS IN THE MODEL W/ LAMBDA'''
def commasAiModel_SteeringAnglePrediction():
    # NORMAL COMMAS AI MODEL
    # Normalize inputs between [-1,1]
    # model.add(Lambda(lambda x: x / 127.5 - 1.,
    #                  input_shape=(row, col, ch),
    #                  output_shape=(row, col, ch)))
    #SOURCE: https://github.com/jessicayung/self-driving-car-nd/tree/master/p3-behavioural-cloning
    # sess = tf.Session()
    model = Sequential()
    # model.add(Lambda(lambda x: cv2.cvtColor(x.eval(session=sess),cv2.COLOR_BGR2RGB), input_shape=(240,320,3)))
    model.add(Cropping2D(cropping=((108, 36), (0, 0)),
                         dim_ordering='tf',  # default
                         input_shape=(240, 320, 3)))
    model.add(Lambda(lambda x: x / 255.0 - 0.5,input_shape=(96, 320, 3)))
    # model.add(Conv2D(16, (8, 8), subsample=(4, 4), border_mode='same', W_regularizer=l2(L2_REG_SCALE))) #
    model.add(Conv2D(16, (5, 5), strides=(2, 2), padding='same'))  #
    model.add(ELU()) #
    # model.add(Conv2D(32, (5, 5), subsample=(2, 2), border_mode='same', W_regularizer=l2(L2_REG_SCALE))) #
    model.add(Conv2D(32, (5, 5), strides=(2, 2), padding='same'))  #
    model.add(ELU()) #
    # model.add(Conv2D(64, (5, 5), subsample=(2, 2), border_mode='same', W_regularizer=l2(L2_REG_SCALE)))#
    model.add(Conv2D(64, (3, 3), strides=(2, 2), padding='same'))  #

    model.add(Flatten()) #
    model.add(Dropout(.2)) #
    model.add(ELU()) #

    #fully connected 1
    # model.add(Dense(512, W_regularizer=l2(0.))) #
    model.add(Dense(512, activation='relu'))  #
    model.add(Dropout(.5))
    # model.add(ELU())

    #fully connected 2
    model.add(Dense(50, activation='relu'))
    # model.add(ELU())

    # model.add(Dense(1, W_regularizer=l2(0.)))
    model.add(Dense(1))
    model.compile(optimizer=Adam(lr=lrate), loss='mean_squared_error',metrics=['accuracy'])

    return model
#NOTE: DO NOT APPLY NORMALIZATION, NORMALIZATION IS IN THE MODEL W/ LAMBDA
def nVidiaModel():
    """
    Creates nVidea Autonomous Car Group model
    """
    resizeWidth = 320;
    resizeHeight = 128;
    model = Sequential()
    #crop 108 from top, and 36 from bottom, to get [108:204], or 96 elements, and 0 cropped from width
    model.add(Cropping2D(cropping=((112, 12), (0, 0)),
                         dim_ordering='tf',  # default
                         input_shape=(240, 320, 3)))
    model.add(Lambda(lambda x: x/255.0 - 0.5, input_shape=(resizeHeight, resizeWidth, 3)))
    #TODO: look into cropping layer. Why add it??
    model.add(Conv2D(24,(5,5), subsample=(2,2), activation='elu', padding='same'))
    model.add(Conv2D(36,(5,5), subsample=(2,2), activation='elu', padding='same'))
    model.add(Conv2D(48,(5,5), subsample=(2,2), activation='elu', padding='same'))
    model.add(Conv2D(64,(3,3), activation='elu', padding='same'))
    model.add(Conv2D(64,(3,3), activation='elu', padding='same'))
    model.add(Flatten())
    model.add(Dense(100,activation='elu'))
    model.add(Dense(50,activation='elu'))
    model.add(Dense(10,activation='elu'))
    model.add(Dense(1))
    model.compile(loss='mse', optimizer=Adam(lr=lrate),metrics=['accuracy'])
    return model

def create_mySteeringModel():
    # get_custom_objects().update({'custom_activation': Activation(custom_activation)})

    model = Sequential()
    #preprocessing
    inputWidth = 320;
    inputHeight = 240;
    resizeWidth = 320;
    resizeHeight = 128;
    model.add(Cropping2D(cropping=((112, 12), (0,0)),dim_ordering='tf',
                         input_shape=(240,320,3)))
    # model.add(Lambda(lambda img: backend.resize_images(img,int(resizeHeight/inputHeight),int(resizeWidth/inputWidth), "channels_last")))
    #TODO: must specify input_shape here, or else throws error
    model.add(Lambda(lambda x: x/127.5 - 1, input_shape=(resizeHeight, resizeWidth, 3))) #normalize img into a range

    model.add(Conv2D(8, (7, 7), strides=1, padding='valid', activation='relu', kernel_initializer=glorot_normal(12345)))
    model.add(Conv2D(16, (5, 5), strides=1, padding='valid', activation='relu', kernel_initializer=glorot_normal(12345)))
    model.add(Conv2D(32, (3, 3), strides=2, padding='valid', activation='relu', kernel_initializer=glorot_normal(12345)))
    model.add(MaxPooling2D((2, 2), strides=2))
    model.add(Conv2D(64, (3, 3), strides=2, padding='valid', activation='relu', kernel_initializer=glorot_normal(12345)))

    model.add(Dropout(0.25))
    model.add(Flatten())
    # model.add(Dense(500, activation='relu'))
    model.add(Dense(100))
    model.add(Dropout(0.5))
    model.add(Dense(20))
    model.add(Dense(1))
    model.compile(loss='mse', optimizer=Adam(lr=lrate), metrics=['accuracy'])
    return model

def create_someSteeringModel():
    model = Sequential()

    #preprocessing
    resizeWidth = 320;
    resizeHeight = 128;
    model.add(Cropping2D(cropping=((112, 12), (0,0)),dim_ordering='tf', input_shape=(240,320,3)))
    model.add(Lambda(lambda img: tf.image.resize_images(img,(resizeHeight,resizeWidth))))
    model.add(Lambda(lambda x: x/127.5 - 1, output_shape=(resizeHeight, resizeWidth, 3))) #normalize img into a range

    model.add(Conv2D(16, (3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Conv2D(32, (3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Conv2D(64, (3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Flatten())
    model.add(Dense(500, activation='relu'))
    model.add(Dense(100, activation='relu'))
    model.add(Dense(20, activation='relu'))
    model.add(Dense(1))
    model.compile(loss='mse', optimizer=Adam(lr=lrate), metrics=['accuracy'])
    return model

def create_steeringAngleClassification_model():
    # Create model
    model = Sequential()

    # 1st param=filters, 2nd Param = kernel_size
    # TODO: ADDED THIS NEW PART, MUST CHANGE THIS IN AUTONOMOUS.PY AND CHANGE HAVING IT CROP OFF IMAGE and previously it had [120:240], now the new one i want is [108:204]
    model.add(Cropping2D(cropping=((108, 36), (0, 0)),
                         dim_ordering='tf',  # default
                         input_shape=(240, 320, 3)))
    model.add(Lambda(lambda x: x / 255.0, input_shape=(96, 320, 3)))
    model.add(Conv2D(32, (3, 3), padding='same', activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(32, (3, 3), padding='same', activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(64, (3, 3), padding='same',activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Dropout(0.25))
    model.add(Flatten())
    model.add(Dense(128, activation='relu'))  #TODO: Make more nodes, like 128 maybe
    model.add(Dropout(0.5))
    model.add(Dense(21, activation='softmax'))  # 21 diffrent possible steering angle

    model.compile(optimizer=Adam(lr=lrate), loss='categorical_crossentropy',
                  metrics=['accuracy'])  # include metrics=['accuracy'] for it to display accuracy
    return model
def nvidia_classification():
    model = Sequential()
    # crop 108 from top, and 36 from bottom, to get [108:204], or 96 elements, and 0 cropped from width
    model.add(Cropping2D(cropping=((108, 36), (0, 0)),
                         dim_ordering='tf',  # default
                         input_shape=(240, 320, 3)))
    model.add(Lambda(lambda x: x / 255.0, input_shape=(96, 320, 3), output_shape=(96, 320, 3)))
    # TODO: look into cropping layer. Why add it??
    model.add(Conv2D(24, (5, 5), subsample=(2, 2), activation='elu', padding='same'))
    model.add(Conv2D(36, (5, 5), subsample=(2, 2), activation='elu', padding='same'))
    model.add(Conv2D(48, (5, 5), subsample=(2, 2), activation='elu', padding='same'))
    model.add(Conv2D(64, (3, 3), activation='elu', padding='same'))
    model.add(Conv2D(64, (3, 3), activation='elu', padding='same'))
    model.add(Flatten())
    model.add(Dense(100, activation='elu'))
    model.add(Dense(50, activation='elu'))
    model.add(Dense(10, activation='elu'))
    model.add(Dense(21, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer=Adam(lr=lrate), metrics=['accuracy'])
    return model
def getBaseInceptionModel():
    """returns base_model, new_model (the base_model w/ changed last layer)"""
    base_model = InceptionV3(weights='imagenet', include_top=False)
    # model = add_new_last_layer(base_model, nb_classes=1, FC_size=FC_SIZE_IV3)
    return base_model
def getEditedInceptionModel(base_model):
    model = add_new_last_layer(base_model, nb_classes=1, FC_size=FC_SIZE_IV3)
    return model;
def convertBGR2RGB(imgList):
    newImgList = []
    for i in range(len(imgList)):
        newImgList.append(cv2.cvtColor(imgList[i],cv2.COLOR_BGR2RGB));
    return newImgList;
def IV3_preprocessing(imgList):
    newImgList = []
    rgbImgList = convertBGR2RGB(imgList);
    for img in rgbImgList:
        newImgList.append(img[108:204]) #crop image to size 96,320,3
    return newImgList;
def normalizeSteerAngles(steerAngleList):
    # TODO: When needed: normalize cmds to range -1 to +1 for regressions
    pass
def convertSteeringAngle_to_OneHotEncoded(steeringAngleList):
    """
    converts the steeringAngle numbers of range -10 to +10
    into one-hot-encoded arrays for classification
    :param steeringAngleList: list of steeringAngles
    """
    sa_list = []
    for angle in steeringAngleList:
        index = angle + 10; #add 10 so convert negative angles into positive
        oneHotArray = np.zeros(21) #20 possible outputs, but 21 b/c max degree is 10, so 10 + 10 is 21
        oneHotArray[index] = 1
        sa_list.append(oneHotArray.tolist())
    return sa_list

def train(model, historyCallBack, accuracyCallBack, shouldEarlyStop):
    print(len(x_val), len(y_val))
    ## Callback for early stopping the training
    early_stopping = keras.callbacks.EarlyStopping(monitor='val_acc',
                                                   min_delta=0,# min chnage in val_loss to qualify as "improvement" i.e. change of less than min_delta will be no improvement
                                                   patience=2,# num of epochs w/ no imporovement after which training will stop
                                                   verbose=1,# verbosity mode: 1 for progress bar logging for each batch, 2 for one log line PER epoch
                                                   mode='auto')  # either min,max, or auto. Auto mode --> training will stop in way inferred by the name of monitered quality. (
    t0 = time.time()
    checkpointer = ModelCheckpoint(filepath=saveDirectory.format(r'checkpoints\weights.hdf5'), verbose=1,save_best_only=True)
    if shouldEarlyStop:
        fitted_model = model.fit_generator(
            train_generator,
            steps_per_epoch=train_trainableFrameCount // batchSize,
            epochs=epochs,
            validation_data=(x_val, y_val),
            validation_steps=len(x_val) // batchSize,
            callbacks=[TQDMNotebookCallback(leave_inner=True, leave_outer=True), early_stopping, historyCallBack, checkpointer,accuracyCallBack],
            verbose=1,
            shuffle=True
        )
    else:
        fitted_model = model.fit_generator(
            train_generator,
            steps_per_epoch=train_trainableFrameCount // batchSize,
            epochs=epochs,
            validation_data=(x_val, y_val),
            validation_steps=len(x_val) // batchSize,
            callbacks=[TQDMNotebookCallback(leave_inner=True, leave_outer=True), historyCallBack, checkpointer, accuracyCallBack],
            verbose=1,
            shuffle=True
        )
    duration = time.time() - t0
    # Final evaluation of the model
    try:
        scores = model.evaluate(x_test, y_test, verbose=0)  # Verbose=0 means don't display output, while calculating,
        print("Accuracy: %.2f%%" % (scores[1] * 100))
    except Exception as e:
        print("EXCEPTION at evaluating x_test, Error message: {}".format(e))

    print('Total training time: %.2f sec (%.2f min)' % (duration, duration / 60))

    return fitted_model

def train_pretrainedModel(model, base_model, historyCallBack, accuracyCallBack):

    checkpointer = ModelCheckpoint(filepath=saveDirectory.format(r'checkpoints\weights.hdf5'), verbose=1,save_best_only=True)

    #transfer learn
    setup_to_transfer_learn(model,base_model)

    tl_fitted_model = model.fit_generator(
        train_generator,
        steps_per_epoch=train_trainableFrameCount // batchSize, #TODO: Tutorial has this as the # of train examples, what is the batchSize he used??
        epochs=epochs,
        validation_data=(x_val, y_val),
        validation_steps=len(x_val) // batchSize,
        callbacks=[TQDMNotebookCallback(leave_inner=True, leave_outer=True), historyCallBack,
                   checkpointer, accuracyCallBack],
        verbose=1,
        shuffle=True
    )

    #fine tune
    setup_to_finetune(model,NB_IV3_LAYERS_TO_FREEZE)

    fineTuned_model = model.fit_generator(
        train_generator,
        steps_per_epoch=train_trainableFrameCount // batchSize,# TODO: Tutorial has this as the # of train examples, what is the batchSize he used??
        epochs=epochs,
        validation_data=(x_val, y_val),
        validation_steps=len(x_val) // batchSize,
        callbacks=[TQDMNotebookCallback(leave_inner=True, leave_outer=True), historyCallBack,
                   checkpointer, accuracyCallBack],
        verbose=1,
        shuffle=True
    )
    return fineTuned_model

server = ''
database = ''
username = ''
password = ''
driver = '{ODBC Driver 13 for SQL Server}'

#INIT the SQL Table
wrongInput = True
table = "";
trainType = None;
while(wrongInput):
    tableInput = input("Which SQL Table will you like to pull data from?\n\t-SteeringAngleData (s)\n\t-DiscreteTurnsData (d)\n")
    if(tableInput == 's'):
        table= 'trainData.SteeringAngleData'
        trainType = TrainType.SteerAngles;
        wrongInput = False;
    elif(tableInput =='d'):
        table='poc.TrainingData'
        trainType = TrainType.DiscreteTurns;
        wrongInput = False;
    else:
        print("Wrong input, Please type in 's' for SteeringAngleData or 'd' for DiscreteTurnsData")

saveDirectory = input("Type path to folder you like to save the Model: ")
#create save directory directory, if already exits, it doesn't create (https://stackoverflow.com/a/14364249/7359915)
pathlib.Path(saveDirectory).mkdir(parents=True, exist_ok=True)
pathlib.Path(saveDirectory + '\\checkpoints').mkdir(parents=True, exist_ok=True)
saveDirectory += '\{}' #add this so can use '.format() to add the file names

train_DataGenerator = DataGenerator("""WHERE Evaluation='Good'""",
                                server, database, username, password, driver, normalizationMethod,trainType, table,
                                    shouldReshapeImg=False, updateFrameletSize=1000, shouldHorizontalFlip=True,
                                    shouldAugment=True)
train_generator = train_DataGenerator.nextBatch(batchSize, functionOnCmd=None) #create generator

dataset = Dataset(server,database,username,password,driver)
x_val, y_val = dataset.getData("""SELECT * FROM {0} where Evaluation='Validation'""".format(table), trainType = trainType,
                                     shouldReshape=False,normalizationMethod=normalizationMethod,shouldShuffle=False,
                                    functionOnCmd=None)
x_test, y_test = dataset.getData("""SELECT * FROM {0} where Evaluation='Testing'""".format(table), trainType = trainType,
                                     shouldReshape=False,normalizationMethod=normalizationMethod,shouldShuffle=False,
                                    functionOnCmd=None)
train_totalFrameCount = train_DataGenerator.getTotalFrameCount()
if(trainType.value == TrainType.SteerAngles.value):
    train_trainableFrameCount = train_totalFrameCount; #equal to the total, cause in this table, only the trainable ones are kept
elif(trainType.value == TrainType.DiscreteTurns.value):
    train_trainableFrameCount = train_DataGenerator.getTrainableFrameCount()

print("{} Total Training Data {} Training Data, {} Testing Data, {} Trainable Validation Data".format(train_totalFrameCount,
                                  train_trainableFrameCount, len(x_test), len(x_val)))


#CREATE MODEL
getModel = create_model_discreteTurns
# base_model = getBaseInceptionModel()
# model = getModel(base_model)
model = getModel()

# redefine the model
# single_batch_model = getModel(base_model)
single_batch_model = getModel()

print(model.summary())

history = LossHistory()
accuracy = AccuracyCallBack()
fitted_model = train(model, history, accuracy, shouldEarlyStop=True)

# fitted_model = train_pretrainedModel(model,base_model,history,accuracy)




#----------Save model architecture to model.json, model weights to model.h5----------
#SAVE JSON MODEL
try:
    json_string = model.to_json()
    with open(saveDirectory.format('model.json'), 'w') as f:
        f.write(json_string)
except Exception as e:
    print("Error while saving model to json, Error Message: {}".format(e))
#SAVE MODEL.h5
try:
    model.save(saveDirectory.format('model.h5'))
except Exception as e:
    print("Error while saving model to .h5 file, Error Message: {}".format(e))
#SAVE WEIGHTS.h5
try:
    model.save_weights(saveDirectory.format('model_weights.h5'))
except Exception as e:
    print("Error while saving model weights to .h5 file, Error Message: {}".format(e))

# ------SAVE Single batch model for loading and deploying --> https://machinelearningmastery.com/use-different-batch-sizes-training-predicting-python-keras/

# copy the weights
old_weights = model.get_weights()
single_batch_model.set_weights(old_weights)
#SAVE JSON SINGLE_BATCH_MODEL
try:
    json_string = single_batch_model.to_json()
    with open(saveDirectory.format('single_batch_model.json'), 'w') as f:
        f.write(json_string)
except Exception as e:
    print("Error while saving SINGLE_BATCH_MODEL to json, Error Message: {}".format(e))

#SAVE SINGLE_BATCH_MODEL AS .h5 -
try:
    single_batch_model.save(saveDirectory.format('single_batch_model.h5'))
except Exception as e:
    print("Error while saving SINGLE_BATCH_MODEL to .h5 file, Error Message: {}".format(e))
#SAVE SINGLE_BATCH_MODEL_WEIGHTS.h5
try:
    single_batch_model.save_weights(saveDirectory.format('single_batch_model_weights.h5'))
except Exception as e:
    print("Error while saving SINGLE_BATCH_MODEL_WEIGHTS to .h5 file, Error Message: {}".format(e))

#SAVE Additional Info into JSON
try:
    data = {'normalization_method': normalizationMethod.value}
    with open(saveDirectory.format('additional_info.json'), 'w') as f:
        json.dump(data, f,indent=4, separators=(',', ': ') )
except Exception as e:
    print("Error while saving additional_info.json. Mesage: {}".format(e))

#----------SAVE HISTORY---------------
#THIS ALWAYS GIVES ERROR, SO COMMENTED OUT
# try:
#     # Save training history
#     with open(saveDirectory.format('train_hist.p'), 'wb') as f:
#         pickle.dump(history, f)
# except Exception as e:
#     print("Error while saving TRAINING HISTORY to PICKLE file, Error Message: {}".format(e))

try:
    with open(saveDirectory.format('fitted_model.history.p'), 'wb') as f:
        pickle.dump(fitted_model.history,f)
except Exception as e:
    print("Error while saving FITTED_MODEL HISTORY to PICKLE file, Error Message: {}".format(e))


print('Models and Histroy saved in {}'.format(saveDirectory))

losses, val_losses = history.losses, history.val_losses
try:
    plt.figure(1, figsize=(15, 5))
    plt.plot(fitted_model.history['loss'], 'g', label="train losses")
    plt.plot(fitted_model.history['val_loss'], 'r', label="val losses")
    plt.grid(True)
    plt.title('Training loss vs. Validation loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    plt.savefig(saveDirectory.format('trainValLoss.png'))

    plt.figure(2, figsize=(15, 5))
    plt.plot(fitted_model.history['acc'], 'g', label="accuracy on train set")
    plt.plot(fitted_model.history['val_acc'], 'r', label="accuracy on validation set")
    plt.grid(True)
    plt.title('Training Accuracy vs. Validation Accuracy')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    plt.savefig(saveDirectory.format('trainValAccuracy.png'))
except Exception as e:
    print("Exception while displaying accuracy and loss graphs\n\tError Message: {0}".format(e))
finally:
    plt.show()
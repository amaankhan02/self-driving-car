# Self Driving Car Prototype
This repository contains code for my Self-Driving Car Prototype that was originally hosted on TFS. I exported the 
code files to GitHub now.
This project was developed between **Jan 2017 to Dec 2017** when I was a Freshman to Sophomore in high school.

**Click [here](https://www.youtube.com/watch?v=3dEgJ7sz6XA) or the image below to watch the video demo!**    
[![IMAGE_ALT](https://img.youtube.com/vi/3dEgJ7sz6XA/0.jpg)](https://www.youtube.com/watch?v=3dEgJ7sz6XA)    

## Quick Overview:
* Independently researched and developed a Self-Driving Car prototype on a Raspberry Pi that can drive within lanes, detect traffic lights, and avoid obstacles, all running on a CPU.
* Removed the existing microcontroller from a Remote Control car and replaced with a Raspberry Pi and motor driver, along with adding an ultrasonic distance sensor to avoid obstacles
* Trained a Convolutional Neural Network (CNN) using TensorFlow for end-to-end steering prediction with 91.06% testing accuracy. Model inspired by NVIDIA's paper: End to End Learning for Self-Driving Cars by Bojarski et al.
* Researched and optimized my CNN for steering prediction to be accurate but fast to run on a CPU in real-time, since I did not have access to a GPU
* To run the car autonomously, I offloaded the models and algorithms to my PC by having the Raspberry Pi car send live video frames to my PC through a socket server, in which my PC ran the models/algorithms on the video frame and sent back a command to the car.
* Developed an Android App using Java to control the car wirelessly through a socket server to collect the steering prediction data of 120,000 video frames, which was stored on Microsoft SQL Server
* Setup a Windows Task Scheduler to automatically fetch training data from the Raspberry Pi to a SQL Server database on my PC (during data collection process).
* Implemented various data augmentation techniques to artificially grow the dataset to improve model accuracy and robustness.
* Due to limited computational resources, I trained an LBP Cascade Classifier instead of using a Deep Learning method to detect traffic lights on a custom collected dataset of 570 positive samples 1000 negative samples.
* **Awarded [2nd place at the National Junior Science & Humanities Symposium (JSHS)](https://www.psd202.org/news/1163) in Mathematics and Computer Science and [1st place at the Illinois-Chicago JSHS](https://patch.com/illinois/plainfield/plainfield-south-student-builds-self-driving-car) for this project**


## Directory Structure
* `/Computer` -  Contains code that meant to be ran on my main PC. This directory contains code to...
    * **Run the car autonomously** - where the PC was connected to the Raspberry Pi via a socket server
    * **Collect Training Data** - When collecting training data, I control the car (Raspberry Pi) using an Android app that I wrote. The Raspberry Pi sends the video frames along with the current car steering command
  to a shared network folder. The code in this folder collects that data saved in the network drive and saves it to a
    in Microsoft SQL Server Database. 
    * **Neural Network Training** - Contains code to train various neural network models for the steering prediction.
    * **Traffic Light Detection** - Contains code for training the model to detect Traffic Lights - contains code for both
  the LBP Cascade Classifier and for training using the TensorFlow Object Detection API.
* `/Phone` - Contains code for the Android App that I wrote to control the car, for when the car is running autonomously
and for when the car is collecting training data for training the steering prediction neural network model.
* `/RaspberryPi` - Contains code that is hosted on the Raspberry Pi (which is in the car). This contains code 
that is pertaining to the Autonomous mode, collecting training data mode, and code to control the sensors on the car.

# Self Driving Car Prototype
This repository contains code for my Self-Driving Car Prototype that was originally hosted on TFS. I exported the 
code files to GitHub now.
This project was developed between **Jan 2017 to Dec 2017** when I was a Freshman to Sophomore in high school.

**Click on image below to watch YouTube video demo!**    
[![IMAGE_ALT](https://img.youtube.com/vi/3dEgJ7sz6XA/0.jpg)](https://www.youtube.com/watch?v=3dEgJ7sz6XA)    

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

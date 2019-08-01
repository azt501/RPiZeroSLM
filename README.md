# RPiZeroSLM

Sound Level Meter connected to Raspberry Pi

# Installation

Download this using

        sudo apt-get install git

	git clone https://github.com/azt501/RPiZeroSLM

cd into the folder RPiZeroSLM and type

	bash ./install.sh

#Useful Information

to start server:

	cd mosquitto-1.6.3

	mosquitto -c mosquitto.conf -v

to subscribe to topic & subtopics: 

	mosquitto_sub -h localhost -t sensor1/#

to kill mosquitto (if running as daemon):

	pgrep mosquitto

	kill -9 PID (that you get from above command)

use "python getdBValues.py" to start the microphone code.

	if it doesn't work, "python findAudioDevices.py" and see what index the usb controller is of the lines ending in (hw:*,*) (starting from 0)



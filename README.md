# RPiZeroSLM

Sound Level Meter connected to Raspberry Pi

use "mosquitto -c mosquitto.conf -v" in mosquitto directory to start server.

use "mosquitto_sub -h localhost -t sensor1/#" in mosquitto directory to subscribe to the topic "sensor1" and all subtopics

to kill mosquitto (if running as daemon):

	ps -aux | grep mosquitto

	pgrep mosquitto

	kill -9 PID (that you get from above command)

use "python getdBValues.py" to start the microphone code.

	if it doesn't work, "python findAudioDevices.py" and see what index the usb controller is of the lines ending in (hw:*,*) (starting from 0)



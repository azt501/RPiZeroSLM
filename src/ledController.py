from blinkt import set_pixel, show
import paho.mqtt.client as mqtt
import math
import time

readyToGo = False
olddB = 0

def on_message(client, userdata, message):
    global currentdB, readyToGo
    message = message.payload.decode("utf-8")[12:]
    currentdB = float(message)
 #   print(currentdB)
    readyToGo = True

R = [0,0,65,105,180,255,255,255]
G = [255,230,150,100,50,0,0,0]
B = [0,0,0,0,0,0,0,0]
client = mqtt.Client("P1")
client.connect("172.16.21.105")
client.subscribe("sensor1")
client.on_message = on_message
client.loop_start()

while not readyToGo:
	on_message

def updateLEDs(dB):
	global olddB
	reset_board()
	currentPercent = dB / 1.10
	LEDsToLight = int(math.floor(currentPercent / 12.5))	#checks the number of LEDs to light all the way up
	percentToLight = currentPercent / 12.5 - math.floor(currentPercent / 12.5)	#checks the amount to light the next LED
	if LEDsToLight > 7: 
		LEDsToLight = 7
		percentToLight = 1
	if LEDsToLight == 0:
		LEDsToLight = 1

	for i in range (0,LEDsToLight):
		set_pixel(i, R[i],G[i],B[i])
		set_pixel(LEDsToLight, int(R[LEDsToLight]*percentToLight), int(G[LEDsToLight]*percentToLight), int(B[LEDsToLight]*percentToLight))
	olddB = currentdB

	show()

def reset_board():
	for i in range(0,8):
		set_pixel(i,0,0,0)

while readyToGo:
	reset_board()
	difference = (currentdB-olddB)/20
	try:
		for i in range (int(olddB), int(currentdB), int(difference)):
			updateLEDs(i)
	except ValueError:
		reset_board()

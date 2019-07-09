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
    print(currentdB)
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

while readyToGo:
	for i in range (0,8):
		set_pixel(i,0,0,0)
	if currentdB != olddB:
		currentPercent = currentdB / 1.10
		LEDsToLight = int(math.floor(currentPercent / 12.5))	#checks the number of LEDs to light all the way up
		percentToLight = currentPercent / 12.5 - math.floor(currentPercent / 12.5)	#checks the amount to light the next LED
		if LEDsToLight > 7: 
			LEDsToLight = 7
			percentToLight = 1

		for i in range (0,LEDsToLight):
			set_pixel(i, R[i],G[i],B[i])
			print(R[i], G[i], B[i])

		set_pixel(LEDsToLight, int(R[LEDsToLight]*percentToLight), int(G[LEDsToLight]*percentToLight), int(B[LEDsToLight]*percentToLight))
		print("final rgb: ", int(R[LEDsToLight]*percentToLight), int(G[LEDsToLight]*percentToLight), int(B[LEDsToLight]*percentToLight))
		olddB = currentdB
		show()

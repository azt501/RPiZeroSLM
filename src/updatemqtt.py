import paho.mqtt.client as mqtt
import time

readyToGo = False
def on_message(client, userdata, message):
    global readyToGo
    message = message.payload.decode("utf-8")
    for i in range (0,20):
	client.publish("sensor1",message)
	time.sleep(0.02)
    readyToGo = True

client = mqtt.Client("T1")
client.connect("172.16.21.105")
client.subscribe("sensor1")
client.on_message = on_message
client.loop_start()

while not readyToGo:
	on_message

while readyToGo:
	1+1

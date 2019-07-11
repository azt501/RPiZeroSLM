import random
import time
import paho.mqtt.client as mqtt
import socket

client = mqtt.Client("randomTest")
client.connect("localhost")
directory = "sensor1"
client.subscribe("sensor1")
hostname = socket.gethostname()
print(hostname)
client.loop_start()

while True:
	randnum = random.randint(0,110)
	client.publish(directory, hostname+'&'+str(randnum))
	print(hostname+'@'+str(randnum))
	time.sleep(1)

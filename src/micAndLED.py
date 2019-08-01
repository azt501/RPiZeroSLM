import os, errno
import math
import time
import pyaudio
import spl_lib as spl
from scipy.signal import lfilter
import numpy
import paho.mqtt.client as mqtt
from blinkt import set_pixel, show

'''
setup leds
'''
R = [0,0,65,105,180,255,255,255]
G = [255,230,150,100,50,0,0,0]
olddB = 0

def updateLEDs(dB):
	global olddB
	reset_board()
	LEDsToLight = dB/13.75
	intLEDs = int(math.floor(LEDsToLight))
	percentToLight = LEDsToLight - intLEDs
	if LEDsToLight > 7:
		LEDsToLight, percentToLight = 7,1
	elif LEDsToLight == 0:
		LEDsToLight = 1

	for i in range (0, intLEDs):
		set_pixel(i,R[i],G[i],0)
	set_pixel(intLEDs, int(R[intLEDs]*percentToLight), int(G[intLEDs]*percentToLight),0)
	olddB = dB
	show()

def reset_board():
	for i in range(0,8):
		set_pixel(i,0,0,0)


'''
Setup mqtt
'''
def on_message(client, userdata, message):
	msg = str(message.payload.decode("utf-8"))
	if msg == "calibrate":
		calibrateMic()
	elif msg == "nocalibrate":
		unCalibrateMic()

client = mqtt.Client("MicZTest") #,transport='websockets')
client.connect("172.16.21.105") # ,9001)
directory = "sensor1"
client.on_message = on_message
client.subscribe("sensor1")

'''
Listen to mic
'''

prevdB = 0
dBOffset = 0

def calibrateMic(decibel = 94):
    global dBOffset
    dBOffset = prevdB - decibel

def unCalibrateMic():
    global dBOffset
    dBOffset = 0

def listen(FORMAT = pyaudio.paInt16, CHUNK = 2**13, FS = 48000, CHANNEL = 1):
    succeeded = 1
    A_NUMERATOR, A_DENOMINATOR = spl.A_weighting(FS)
    pa = pyaudio.PyAudio()
    stream = pa.open(format = FORMAT, channels = CHANNEL, rate = FS, input = True, frames_per_buffer = CHUNK)
    global prevdB
    print("Listening")
    counter = 0
    sum2 = 0
    rms = 0
    client.loop_start()
    while True:
        try:
            block = stream.read(CHUNK)
        except IOError as e:
	    succeeded = 0
	    break
        else:
            decoded_block = numpy.fromstring(block, 'Int16') # use numpy to decode the data
            filtered = lfilter(A_NUMERATOR, A_DENOMINATOR, decoded_block) # a-weighted
            for value in filtered:
                sum2 += value*value # sum squared
                counter += 1 # count the number of samples for the average
                if counter >= FS: #FS samples = 1s of data
                    ms = sum2/float(FS) # mean squared
                    rms = numpy.sqrt(ms) # root mean squared
		    prevdB = float("{:.2f}".format( 20*numpy.log10(rms) ))
                    text = float(prevdB) - float(dBOffset)
#		    try:
#		     	    for i in range (int(olddB), int(text), int((text-olddB)/3)):
	            updateLEDs(text)
#		    except:
#			1+1
		    print(text)
                    client.publish(directory,text)
                    counter, sum2 = 0,0

    print("stopping")
    if succeeded:
	    stream.stop_stream()
	    stream.close()
    pa.terminate()



if __name__ == '__main__':
    while True:
        listen()
	time.sleep(.5)


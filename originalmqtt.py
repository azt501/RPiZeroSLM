#!/usr/bin/env python
import os, errno
import pyaudio
import spl_lib as spl
from scipy.signal import lfilter
import numpy
import paho.mqtt.client as mqtt
import socket

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CHUNK = 2**13 #8192
FORMAT = pyaudio.paInt16    # 16 bit
CHANNEL = 1

FS = 48000

# Create the filter coeffs
A_NUMERATOR, A_DENOMINATOR = spl.A_weighting(FS)
C_NUMERATOR, C_DENOMINATOR = spl.C_weighting(FS)

def get_path(base, tail, head=''):
    return os.path.join(base, tail) if head == '' else get_path(head, get_path(base, tail)[1:])
def on_message(client, userdata, message):
	msg = str(message.payload.decode("utf-8"))
	if "rasp" not in msg: print("message received " ,msg)
	if msg == "calibrate":
		calibrateMic()
	elif msg == "nocalibrate":
		unCalibrateMic()

client = mqtt.Client("MicZTest") #,transport='websockets')
client.connect("172.16.21.105") # ,9001)
directory = "sensor1"
client.on_message = on_message
client.subscribe("sensor1")
hostname = socket.gethostname()
print(hostname)

'''
Listen to mic
'''
pa = pyaudio.PyAudio()

stream = pa.open(format = FORMAT,
                channels = CHANNEL,
                rate = FS,
                input = True,
                frames_per_buffer = CHUNK)

prevdB = 0
dBOffset = 0

def calibrateMic(decibel = 94):
    global dBOffset
    dBOffset = prevdB - decibel

def unCalibrateMic():
    global dBOffset
    dBAOffset = 0


def _format_db_string(value, units="dB"):
    return "{:.2f} {:s}".format(value, units)

def write_file(content, filename, dirname):
    path = os.path.join(dirname, filename)
    with open(path, 'w') as f:
        f.write( content )
    return path


def _filter(data, NUMERATOR, DENOMINATOR, unit="dBA"):
    y = lfilter(NUMERATOR, DENOMINATOR, data)
    rms = 20*numpy.log10(spl.rms_flat(y))
    t = _format_db_string(rms, unit)
    return t,rms



def listen(old=0, error_count=0, min_decibel=100, max_decibel=0):
    global prevdB
    print("Listening")
    counter = 0
    sum2 = 0
    rms = 0
    edited = 0
    client.loop_start()
    while True:
        try:
            ## read() returns string. You need to decode it into an array later.
            block = stream.read(CHUNK)
        except IOError as e:
            error_count += 1
            print(" (%d) Error recording: %s" % (error_count, e))
        else:
            decoded_block = numpy.fromstring(block, 'Int16') # use numpy to decode the data
            filtered = lfilter(A_NUMERATOR, A_DENOMINATOR, decoded_block) # a-weighted
            # filtered = lfilter(C_NUMERATOR, C_DENOMINATOR, decoded_block) # c-weighted


            # loop through all the values in filtered
            for value in filtered:
                sum2 += value*value # sum squared
                counter += 1 # count the number of samples for the average
                if counter >= FS: #FS samples = 1s of data
                    ms = sum2/float(FS) # mean squared
                    rms = numpy.sqrt(ms) # root mean squared
                    text = "{:.2f}".format( 20*numpy.log10(rms) )
                    prevdB = float(text)
                    edited = str(float(text)-float(dBOffset))
                    client.publish(directory,hostname+"&"+edited)
                    print("a: " edited )
                    write_file(text, "value.txt", "/var/tmp/" )
                    counter, sum2 = 0,0


    stream.stop_stream()
    stream.close()
    pa.terminate()



if __name__ == '__main__':
    listen()

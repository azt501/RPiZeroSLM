#!/usr/bin/env python
import socket
import os, errno
import paho.mqtt.client as mqtt
import pyaudio
import spl_lib as spl
from scipy.signal import lfilter
import numpy

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def on_message(client, userdata, message):
	msg = str(message.payload.decode("utf-8"))
	if "rasp" not in msg: print("message received " ,msg)
	if msg == "calibrate":
		calibrateMic()
	elif msg == "nocalibrate":
		unCalibrateMic()

CHUNK = 2**13 #8192
FORMAT = pyaudio.paInt16    # 16 bit
CHANNEL = 1
dev_index = 1

FS = 48000

#Setup client mqtt

client = mqtt.Client("MicTest") #,transport='websockets')
client.connect("localhost") # ,9001)
directory = "sensor1"
client.on_message = on_message
client.subscribe("sensor1")
hostname = socket.gethostname()
print(hostname)

# Create the filter coeffs
A_NUMERATOR, A_DENOMINATOR = spl.A_weighting(FS)
C_NUMERATOR, C_DENOMINATOR = spl.C_weighting(FS)

def get_path(base, tail, head=''):
    return os.path.join(base, tail) if head == '' else get_path(head, get_path(base, tail)[1:])


'''
Listen to mic
'''
pa = pyaudio.PyAudio()

stream = pa.open(format = FORMAT,
                rate = FS,
                channels = CHANNEL,
                input_device_index = dev_index,
                input = True,
                frames_per_buffer = CHUNK)

prevdBA = 0
prevdBC = 0
dBAOffset = 0
dBCOffset = 0

def calibrateMic(decibel = 94):
    global dBAOffset, dBCOffset
    dBAOffset = prevdBA - decibel
    dBCOffset = prevdBC - decibel

def unCalibrateMic():
    global dBAOffset, dBCOffset
    dBAOffset, dBCOffset = 0,0


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
    global prevdBA, prevdBC
    print("Listening")
    counterdBTest = 0
    counter = 0
    suma = 0
    sumc = 0
    rmsa = 0
    rmsc = 0
    editeda = 0
    editedc = 0
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
            afiltered = lfilter(A_NUMERATOR, A_DENOMINATOR, decoded_block) # a-weighted
            cfiltered = lfilter(C_NUMERATOR, C_DENOMINATOR, decoded_block) # c-weighted

            for i in range (0, len(afiltered)-1):
                avalue = afiltered[i]
                cvalue = cfiltered[i]
                suma += avalue*avalue # sum squared
                sumc += cvalue*cvalue
                counter += 1 # count the number of samples for the average
                if counter >= FS: #FS samples = 1s of data
                    msa = suma/float(FS) # mean squared
                    msc = sumc/float(FS)
                    rmsa = numpy.sqrt(msa) # root mean squared
                    rmsc = numpy.sqrt(msc)

                    texta = "{:.2f}".format( 20*numpy.log10(rmsa) )
                    textc = "{:.2f}".format( 20*numpy.log10(rmsc) )

		    editeda = str(float(texta)-float(dBAOffset))
		    editedc = str(float(textc)-float(dBCOffset))

		    client.publish(directory,hostname+"&"+editeda)

		    prevdBA = float(texta)
		    prevdBC =float(textc)

                    print("a: " + editeda )
                    print("c: " + editedc )
                    print("c-a: " + str(float(editeda)-float(editedc) ))
                    print("")
                    counter, suma, sumc = 0,0,0
		    counterdBTest += 1
	
#	if counterdBTest == 3:
#		calibrateMic()

    stream.stop_stream()
    stream.close()
    pa.terminate()



if __name__ == '__main__':
    listen()

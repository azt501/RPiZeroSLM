import pyaudio
import time
time.sleep(5)
p = pyaudio.PyAudio()
for ii in range(p.get_device_count()):
	print(p.get_device_info_by_index(ii).get('name'))

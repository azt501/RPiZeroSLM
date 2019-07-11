# Install the Raspbian Minimal Image
sudo apt-get --allow-releaseinfo-change update --fix-missing
sudo apt-get upgrade
sudo apt-get install tmux vim git
sudo apt-get install i2c-tools build-essential
sudo apt-get install mosquitto mosquitto-clients
# python2 libraries
sudo apt-get install python-dev python-pyaudio python-numpy python-scipy python-smbus python-pip python-blinkt libc-ares-dev libwebsockets-dev libssl-dev xsltproc docbook-xsl python-blinkt
sudo pip install paho-mqtt
sudo pip install spl
# install mosquitto
wget https://mosquitto.org/files/source/mosquitto-1.6.3.tar.gz
tar -xzvf mosquitto-1.6.3.tar.gz
rm mosquitto-1.6.3.tar.gz
cd mosquitto-1.6.3
# make
cp mosquitto.conf mosquitto.conf.original
cd ..
mv mosquitto.conf mosquitto-1.6.3/mosquitto.conf 
git clone https://github.com/adafruit/Adafruit_Python_SSD1306
cd Adafruit_Python_SSD1306
sudo python setup.py install
cd ..
read -p "Enable i2c. Press enter to continue"
sudo raspi-config # enable i2c
read -p "Looking for '3c' in i2c"
sudo i2cdetect -y 1

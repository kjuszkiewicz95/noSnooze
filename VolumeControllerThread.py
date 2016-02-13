import RPi.GPIO as GPIO
import os
import logging
import time
import threading
import subprocess

logger = logging.getLogger('root')

# Clock
CLKPIN = 18
# Master In Slave Out
MISOPIN = 23
# Master Out Slave In
MOSIPIN = 24
# Chip Select
CSPIN = 25

GPIO.setmode(GPIO.BCM)

GPIO.setup(CLKPIN, GPIO.OUT)
GPIO.setup(MISOPIN, GPIO.IN)
GPIO.setup(MOSIPIN, GPIO.OUT)
GPIO.setup(CSPIN, GPIO.OUT)

# Volume starts to become very very low around 50, that will be our "zero" instead of 0
ZERO = 50
# Don't want to necessarily go through the trouble of changing system volume for a 1/1024th change of the potentiometer so we set up a tolerance
TOLERANCE = 20

class VolumeControllerThread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self._ended = False
		self._previousADCValue = 0
		
	def getADCValue(self):
		# Bringing CS low HIGH begins the ADC reset process
 		GPIO.output(CSPIN, True)
 		# Setting CLK to low as we're not yet ready to send data
		GPIO.output(CLKPIN, False)
		# Bringing CS LOW completes the ADC reset process, activates the slave (ADC) and makes it listen
		GPIO.output(CSPIN, False)
		# Want to send code 1-1-000 to ADC
		# First bit tells ADC to be ready for voltage measurement
		# Next bit determines if we want to take single or differential measurement
		# Last 3 bits determine which channel to read voltage over, in our case 000 for channel O
		for i in range(2):
			GPIO.output(MOSIPIN, True)
			GPIO.output(CLKPIN, True)
			GPIO.output(CLKPIN, False)
		for i in range(3):
			GPIO.output(MOSIPIN, False)
			GPIO.output(CLKPIN, True)
			GPIO.output(CLKPIN, False)
		# ADC will return 10 bit 0-1023 value from ADC
		# ADC first sends out a single null bit so we want to loop 11 times to get all 10 bits
		ADCValue = 0
		for i in range(12):
			GPIO.output(CLKPIN, True)
			GPIO.output(CLKPIN, False)
			ADCValue <<= 1
			if(GPIO.input(MISOPIN) == True):
				ADCValue |= 0x1
		# Getting rid of null bit at beginning
		ADCValue >>= 1
		# Start ADC reset process otherwise ADC will spit out 10 digits again in LSB order and then start spitting out 0's indefinitely
		GPIO.output(CSPIN, True)
		return ADCValue
		
	def end(self):
		self._ended = True
	
	def run(self):
		try:
			while(self._ended == False):
				currentADCValue = self.getADCValue()
				if (abs(currentADCValue - self._previousADCValue) > TOLERANCE):
					self._previousADCValue = currentADCValue
					volumeValue = currentADCValue / 10.24
					# 50(ZERO) + 50(Max volumeValue) = 100 | HIGHEST SYSTEM VOLUME LEVEL
					# 50(ZERO) + 0(Min volumeValue) = 50 | LOWEST SYSTEM VOLUME LEVEL
					# Therefore must divide volumeValue by 2 if our zero is 50
					volumeValue = volumeValue / 2
					systemVolume = ZERO + volumeValue
					logger.info('Volume = {volume}%' .format(volume = systemVolume))
					setSystemVolumeString = '{volume}%' .format(volume = systemVolume)
					subprocess.call(["amixer", "sset", "\'PCM\'", setSystemVolumeString])
				time.sleep(1)
			
		finally:
			logger.info("Cleaning up and quitting.")
			GPIO.cleanup()

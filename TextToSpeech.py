
import subprocess
import logging

logger = logging.getLogger('root')

class TextToSpeech:
	def __init__(self):
		logger.info('TextToSpeech started')
	
	def speak(self, text):
		subprocess.call(["pico2wave", "-w", "/home/pi/Desktop/tts.wav", text])
		subprocess.call(["aplay", "/home/pi/Desktop/tts.wav"])

	def makeSoundFile(self, text):
		subprocess.call(["pico2wave", "-w", "/home/pi/Desktop/tts.wav", text])
		
	def playSoundFile(self):
		subprocess.call(["aplay", "/home/pi/Desktop/tts.wav"])

	
		

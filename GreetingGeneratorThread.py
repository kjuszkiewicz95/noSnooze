import threading
import logging
from time import sleep

logger = logging.getLogger('root')

class GreetingGeneratorThread(threading.Thread):
	
	def __init__(self, weather, gCalendar, textToSpeech):
		threading.Thread.__init__(self)
		self.weather = weather
		self.gCalendar = gCalendar
		self.textToSpeech = textToSpeech
		self._enabled = False
		self.ended = False
	
	@property
	def enabled(self):
		return self._enabled

	@enabled.setter
	def enabled(self, enabledValue):
		self._enabled = enabledValue
	
	def generateGreetingSoundFile(self):
		alarmString = self.weather.generateAlarmString()
		logger.info('Alarm string generated')
		eventsString = self.gCalendar.generateEventsString()
		logger.info('Events string generated')
		alarmString  = alarmString + eventsString
		self.textToSpeech.makeSoundFile(alarmString)
		logger.info('File made')
		
	def run(self):
		while(self.ended == False):
			if(self._enabled == True):
				self.generateGreetingSoundFile()
				logger.info('Done generating greeting')
				self._enabled = False
			sleep(1)

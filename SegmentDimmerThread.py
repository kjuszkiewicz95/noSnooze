
import threading
import time
import logging

logger = logging.getLogger('root')


# Dims the display throughout the day based on sunrise and sunset times also taking account when I go to sleep, 10PM. 
# The display should be on its least jarring setting, 0, from 10:00PM until sunrise. In the 2 hours following sunrise
# The display will gradually reach a brightness level of 12. It will stay at that level until an hour before sunset, where
# It will begin a gradual descent from 12 -> 0 that will take 22 (10:00PM) - (sunset - 1) hours. 

# There are 3 modes introduced to program this behavior. CONSTANT, INCREASING, DECREASING

CONSTANT_MORNING_START = 22
CONSTANT_MORNING_END = 6
INCREASING_START = 6
INCREASING_END = 8
CONSTANT_AFTERNOON_START = 8
CONSTANT_AFTERNOON_END = 16 	# WILL DEPEND ON WEATHER
DECREASING_START = 16 # WILL DEPEND ON WEATHER
DECREASING_END = 22

INCREASING_INCREMENT = ((INCREASING_END - INCREASING_START) * 60) / 12
DECREASING_INCREMENT = ((DECREASING_END -DECREASING_START) * 60) / 12

class SegmentDimmerThread(threading.Thread):
	
	def __init__(self, clockThread, weather):
		threading.Thread.__init__(self)
		self.ended = False
		self.clockThread = clockThread
		self.weather = weather
		self._brightness = 12
		self._mode = 'none'
	
	def end(self):
		self.ended = True
		
	def updateSunTimes(self):
		weatherData = self.weather.getWeather()
		# Sunrise
		sunriseDT = self.weather.getSunriseDateTime(weatherData)
		self.sunriseHour = sunriseDT.hour
		# Sunset
		sunsetDT = self.weather.getSunsetDateTime(weatherData)
		self.sunsetHour = sunsetDT.hour
		logger.info('Sun times updated')
		
	def updateModeTimes(self):
		CONSTANT_AFTERNOON_END = self.sunsetHour - 1 
		DECREASING_START = self.sunsetHour - 1
		# Update decreasing increment
		DECREASING_INCREMENT = (DECREASING_END -DECREASING_START) / 12
		
	
	def performIncreasing(self, hour, minute):
		if (minute % INCREASING_INCREMENT == 0):
			self._brightness = self._brightness + 1
			self.clockThread.segment.disp.setBrightness(self._brightness)
			logger.info('incremented to {brightness}' .format(brightness = self._brightness))
		
	def performDecreasing(self, hour, minute):
		if (minute % DECREASING_INCREMENT == 0):
			self._brightness = self._brightness - 1
			self.clockThread.segment.disp.setBrightness(self._brightness)
			logger.info('decremented to {brightness}' .format(brightness = self._brightness))

	def run(self):
		self.updateSunTimes()
		self.updateModeTimes()
		while (self.ended != True):
			hour = self.clockThread.hour
			minute = self.clockThread.minute
			if ((hour >= CONSTANT_MORNING_START and hour < 24) or (hour < CONSTANT_MORNING_END)):
				if (self._mode != 'constant_morning'):
					self._mode = 'constant_morning'
					self._brightness = 0
					self.clockThread.segment.disp.setBrightness(self._brightness)
					logger.info(self._mode)
			elif (hour >= INCREASING_START and hour < INCREASING_END):
				if (self._mode != 'increasing'):
					self._mode = 'increasing'
					logger.info(self._mode)
				self.performIncreasing(hour, minute)
			elif (hour >= CONSTANT_AFTERNOON_START and hour < CONSTANT_AFTERNOON_END):
				if (self._mode != 'constant_afternoon'):
					self._mode = 'constant_afternoon'
					self._brightness = 12
					self.clockThread.segment.disp.setBrightness(self._brightness)
					logger.info(self._mode)
			else:
				if (self._mode != 'decreasing'):
					self._mode = 'decreasing'
					logger.info(self._mode)
				self.performDecreasing(hour, minute)
			if (hour == 0 and minute == 30): # Reset sunrise and sunset times at 12:30AM 
				self.updateSunTimes()
				self.updateModeTimes()
			time.sleep(1000)
			
	

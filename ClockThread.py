import logging
import threading
import time
import datetime
from Adafruit_7Segment import SevenSegment

logger = logging.getLogger('root')

class ClockThread (threading.Thread):
	
	def __init__(self):
		threading.Thread.__init__(self)
		self._segment = SevenSegment(address=0x70)
		self._segment.disp.clear()
		self.ended = False
		
	@property
	def segment(self):
		return self._segment
		
	@property
	def hour(self):
		return self._hour
		
	@property
	def minute(self):
		return self._minute
	
	def end(self):
		self._segment.disp.clear()
		self.ended = True
	
	def run(self):
		while(self.ended != True):
			now = datetime.datetime.now()
			hour = now.hour
			minute = now.minute
			second = now.second
			
			self._hour = hour
			self._minute = minute
			
			hourTensPlace = int(hour / 10)
			hourOnesPlace = hour % 10
			minuteTensPlace = int(minute / 10)
			minuteOnesPlace = minute % 10
			
			self._segment.writeDigit(0, hourTensPlace)
			self._segment.writeDigit(1, hourOnesPlace)
			self._segment.writeDigit(3, minuteTensPlace)
			self._segment.writeDigit(4, minuteOnesPlace)
		self._segment.disp.clear()
		logger.info('Clock is powering down')
		
		

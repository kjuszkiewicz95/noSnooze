# THIS IS THE MAIN FILE
import logging
import sys
from time import sleep
import ClockThread
import MusicPlayer
import TextToSpeech
import AlarmThread
import Weather
import SegmentDimmerThread
import InternalCommServer
import GCalendar
import VolumeControllerThread

logger = logging.getLogger('root')
logger.setLevel(logging.DEBUG)

streamHandler = logging.StreamHandler(sys.stdout)
streamHandler.setLevel(logging.DEBUG)

formatter = logging.Formatter('[%(asctime)s] %(levelname)s %(module)s: %(message)s')
streamHandler.setFormatter(formatter)

logger.addHandler(streamHandler)


class Main:
	def __init__(self):
		self.ended = False
	
	def end(self):
		self.ended = True
	
	def start(self):
		clock = ClockThread.ClockThread()
		clock.setDaemon(True)
		clock.start()
		
		musicPlayer = MusicPlayer.MusicPlayer()
		textToSpeech = TextToSpeech.TextToSpeech()
		weather = Weather.Weather()
		
		segmentDimmer = SegmentDimmerThread.SegmentDimmerThread(clock, weather)
		segmentDimmer.setDaemon(True)
		segmentDimmer.start()
		
		gCalendar = GCalendar.GCalendar()
		volumeController = VolumeControllerThread.VolumeControllerThread()
		volumeController.setDaemon(True)
		volumeController.start()
		
		
		sleep(1) # Wait one second so clock's hour and minute values get filled ready for when alarm needs them
		alarm = AlarmThread.AlarmThread(musicPlayer, textToSpeech, weather, clock, gCalendar)
		alarm.setDaemon(True)
		# DEFAULT WAKEUP TIME - 6:00AM
		alarm.setAlarm(6,0)
		alarm.start()
		
		internalCommServer = InternalCommServer.InternalCommServer(alarm, musicPlayer, textToSpeech)
		internalCommServer.setDaemon(True)
		internalCommServer.start()
		
		try:
			while (self.ended == False):
				sleep(1)
		except (KeyboardInterrupt, SystemExit):
			logger.warn("Interrupted")
		logger.warn("Main powering off process beginning")
		clock.end()
		alarm.end()
		segmentDimmer.end()
		volumeController.end()
		internalCommServer.end()
		sleep(2)
		logger.info("Main powering off process finished")
		

main = Main()
main.start()

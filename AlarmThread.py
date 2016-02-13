
import logging
import time
import threading
import GreetingGeneratorThread
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(5, GPIO.OUT)
GPIO.setup(19, GPIO.IN)
GPIO.output(5, True)

logger = logging.getLogger('root')

class AlarmThread(threading.Thread):
	
	def __init__(self, musicPlayer, textToSpeech, weather, clockThread, gCalendar):
		threading.Thread.__init__(self)
		self.ended = False
		self.musicPlayer = musicPlayer
		self.textToSpeech = textToSpeech
		self.weather = weather
		self.clockThread = clockThread
		self.gCalendar = gCalendar
		self.greetingGThread = GreetingGeneratorThread.GreetingGeneratorThread(weather, gCalendar, textToSpeech)
		self.greetingGThread.setDaemon(True)
		self._alarmSong = 'Intro-The XX.mp3'
		# Variable helpful for ensuring the alarm plays for at least 45 seconds in the event that the pressure pad malfunctions 
		self.enteredSleepCheck = False
		self.cheatedAlarm = False
		
	def end(self):
		self.ended = True
		
	@property
	def hour(self):
		return self._hour
		
	@property
	def minute(self):
		return self._minute
		
	@property
	def alarmSong(self):
		return self._alarmSong
		
	@alarmSong.setter
	def alarmSong(self, alarmSong):
		self._alarmSong = alarmSong
	
	def setAlarm(self, hour, minute):
		self._hour = hour
		self._minute = minute
		
	def soundAlarm(self):
		self.musicPlayer.resetPlayer()
		self.musicPlayer.load(self._alarmSong)
		
	def pauseAlarm(self):
		self.musicPlayer.pause()
		
	def resumeAlarm(self):
		self.musicPlayer.resume()
		
	def stopAlarm(self):
		self.musicPlayer.endPlayer()
		
		
	def run(self):
		self.greetingGThread.start()
		try:
			while(self.ended != True):
				# Obtain current time
				currentHour = self.clockThread.hour
				currentMinute = self.clockThread.minute
			
				# Check to see if its time to sound the alarm
				if ((self._hour == currentHour and self._minute == currentMinute) or self.cheatedAlarm == True):
					self.greetingGThread.enabled = True
					self.soundAlarm()
					while(GPIO.input(19)== True): # While I am lying in bed
						self.enteredSleepCheck = True
						time.sleep(1)
					if (self.enteredSleepCheck == True):
						self.stopAlarm()
					else:	# Pressure pad failed, play alarm for at least 45 seconds
						time.sleep(45)
						self.stopAlarm()
					# Wait an extra 30 seconds at most after getting out of bed for tts file to be created (It most likely is already created).
					fileCounter = 0
					while(self.greetingGThread.enabled == True and counter < 30):
						fileCounter = fileCounter + 1
						time.sleep(1)
					# Finished tts file generation and can be played
					if(self.greetingGThread.enabled == False):
						self.textToSpeech.playSoundFile()
					# Reset value
					self.enteredSleepCheck = False
					# Making sure one doesn't get back into bed in the next 3 minutes, alarm will replay again
					# Reset value
					self.cheatedAlarm = False
					logger.info('Beginning cheat counter')
					cheatCounter = 0
					while(cheatCounter < 180):
						if(GPIO.input(19) == True):
							self.cheatedAlarm = True
							logger.info('CHEATED CHEATED CHEATED')
						cheatCounter = cheatCounter + 1	
						time.sleep(1)
					logger.info('Cheat counter end')
			self.stopAlarm()
			logger.info('AlarmThread stopped MusicPlayer')
			logger.info('AlarmThread is ending')
		finally:
			GPIO.cleanup()
			logger.info('GPIO alarmThread cleaned up.')
		

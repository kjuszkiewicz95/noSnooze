

import logging
import time
import pexpect

logger = logging.getLogger('root')

class MusicPlayer:
	
	def __init__(self):
		self.spawnling = pexpect.spawn('mpg321 -R MusicPlayer')
		self._paused = False
		self._playing = False
		self.folderPath = '/home/pi/Desktop/AlarmMusic/'
		logger.info('MUSIC PLAYER SPAWNED')
		
	def spawn(self):
		self.spawnling = pexpect.spawn('mpg321 -R MusicPlayer')
		
		
	@property
	def playing(self):
		return self._playing
		
	@property
	def paused(self):
		return self._paused
		
	@property
	def currentFile(self):
		return self._currentFile
		
	def load(self, fileName):
		self._currentFile = fileName
		musicLoadLine = 'LOAD ' + self.folderPath + fileName
		logger.info(musicLoadLine)
		self.spawnling.sendline(musicLoadLine)
		self._playing = True
		self._paused = False
		
	def pause(self):
		if (self._paused != True):
			self.spawnling.sendline('PAUSE')
			self._paused = True
			self._playing = False
			
	def resume(self):
		if (self._playing != True):
			self.spawnling.sendline('PAUSE')
			self._playing = True
			self._paused = False
			
	def endPlayer(self):
		logger.info('SPAWNLING CLOSED')
		self.spawnling.close()
		self._paused = False
		self._playing = False
		
	def resetPlayer(self):
		self.endPlayer()
		self.spawn()
		logger.info('PLAYER RESET')

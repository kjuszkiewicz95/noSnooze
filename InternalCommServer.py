
import zerorpc
import threading
import json
import glob
import logging

logger = logging.getLogger('root')

class InternalCommServer(threading.Thread):
	def __init__(self, alarmThread, musicPlayer, textToSpeech):
		threading.Thread.__init__(self)
		self.alarmThread = alarmThread
		self.musicPlayer = musicPlayer
		self.textToSpeech = textToSpeech
		self.ended = False
		self._alarmSongIndex = 0
		
	def getAlarm(self):
		hour = self.alarmThread.hour
		minute = self.alarmThread.minute
		data = {}
		data['hour'] = hour
		data['minute'] = minute
		jsonString = json.dumps(data)
		return jsonString
		
	def setAlarm(self, hour, minute):
		self.alarmThread.setAlarm(hour, minute)
		if (hour == self.alarmThread.hour and minute == self.alarmThread.minute):
			if (minute < 10):
				self.textToSpeech.speak('Alarm set for {sHour} O {sMinute}' .format(sHour = hour, sMinute = minute))
			else:
				self.textToSpeech.speak('Alarm set for {sHour}:{sMinute}' .format(sHour = hour, sMinute = minute))
			return 'success'
		else:
			return 'fail'
			
	def getMP3Library(self):
		absolutePaths = glob.glob("/home/pi/Desktop/AlarmMusic/*.mp3")
		mp3LibraryJSONArray = []
		alarmSong = self.alarmThread.alarmSong
		counter = 0
		mp3Files = [] #	Needed for later setting of alarmSong
		
		for path in absolutePaths:
			tempList = path.split("/")
			mp3Name = tempList[-1]
			mp3Files.append(mp3Name)
			if(mp3Name == alarmSong):
				self._alarmSongIndex = counter
			tempList2 = mp3Name.split("-")
			song = tempList2[0]
			artist = tempList2[1]
			# Remove .mp3 extension still attached to artist"
			artist = artist[:-4]
			mp3Info = {}
			mp3Info['song'] = song
			mp3Info['artist'] = artist
			mp3LibraryJSONArray.append(mp3Info.copy())
			counter = counter + 1
		self._mp3Files = mp3Files
		mp3LibraryString = json.dumps(mp3LibraryJSONArray, separators=(',',':'))
		return mp3LibraryString
		
		
	def getAlarmSongIndex(self):
		return self._alarmSongIndex
		
	def setAlarmSongIndex(self, indexString):
		index = int(indexString)
		self._alarmSongIndex = index
		alarmSong = self._mp3Files[index]
		self.setAlarmSong(alarmSong)
		
	def playMP3(self, mp3String):
		fileName = mp3String + '.mp3'
		logger.info(fileName)
		if(self.musicPlayer.paused == True):
			if(self.musicPlayer.currentFile == fileName):
				self.musicPlayer.resume()
			else: # Previous song was paused but now we are trying to play another one
				self.musicPlayer.resetPlayer()
				self.musicPlayer.load(fileName)
		else:
			self.musicPlayer.resetPlayer()
			self.musicPlayer.load(fileName)
			
	def pauseMP3(self):
		self.musicPlayer.pause()
		
	def setAlarmSong(self, mp3File):
		self.alarmThread.alarmSong = mp3File
		logger.info('Alarm song set to: {selectedSong}'.format(selectedSong = mp3File))
		self.textToSpeech.speak('Alarm song set')
		
	
	def end(self):
		self.ended = True
		self.s.stop
		
	def run(self):
		logger.info('Internal Comm run reached: starting zeroRPC server')
		s = zerorpc.Server(self)
		s.bind("tcp://0.0.0.0:4242")
		self.s = s
		s.run()
		

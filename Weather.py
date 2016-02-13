import requests
import json
import datetime

class Weather:
	def __init__(self):
		# Fake API id added here
		self.url = 'http://api.openweathermap.org/data/2.5/weather?q=North+Babylon,us&units=imperial&appid=67fgffddfxce0fgf40'
	
	def getWeather(self):
		response = requests.get(self.url)
		data = response.json()
		return data

	def generateWeatherString(self):
		data = self.getWeather()
		# Temperature
		temp = self.getTemperature(data)
		# Weather Condition
		cond = self.getCondition(data)
		# Sunset
		sunsetDT = self.getSunsetDateTime(data)
		
		temperatureString = 'The temperature is currently {temperature} degrees farenheit. ' .format(temperature = temp)
		conditionString = 'The current weather condition given is, {condition}. '.format(condition = cond)
		if (sunsetDT.minute < 10):
			sunsetString = 'Today the sun will set at {hour} O {minute}PM in the evening. ' .format(hour = sunsetDT.hour, minute = sunsetDT.minute)
		else:
			sunsetString = 'Today the sun will set at {0:%I:%M%p} in the evening. '.format(sunsetDT)
		weatherStringSequence = (temperatureString, conditionString, sunsetString)
		weatherString = "".join(weatherStringSequence)
		return weatherString


	def getTemperature(self, data):
		temp = data['main']['temp']
		temp = round(temp, 0)
		temp = int(temp)
		return temp
		
	def getCondition(self, data):
		cond = data['weather'][0]['description']
		return cond
		
	def getSunsetDateTime(self, data):
		ts = data['sys']['sunset']
		dt = datetime.datetime.fromtimestamp(ts)
		return dt
		
	def getSunriseDateTime(self, data):
		ts = data['sys']['sunrise']
		dt = datetime.datetime.fromtimestamp(ts)
		return dt
	
	def generateDateString(self):
		#A = Weekday | B = Month | d = DayOfMonth
		dt = datetime.datetime.now()
		dateString = 'Today is {0:%A}, {0:%B} {0:%d}. '.format(dt)
		return dateString

	def generateAlarmString(self):
		alarmString = self.generateDateString() + self.generateWeatherString()
		return alarmString

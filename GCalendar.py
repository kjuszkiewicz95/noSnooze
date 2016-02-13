from __future__ import print_function
import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import tools
from oauth2client import client

import datetime
from dateutil.parser import parse

try:
	import argparse
	flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
	flags = None
	
	
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'

credential_directory = '/home/pi/'
credential_filePath = os.path.join(credential_directory, 'calendar-credentials.json')

class GCalendar:
	def __init__(self):
		self.ended = False
		
	def getCredentials(self):
		store = oauth2client.file.Storage(credential_filePath)
		# Check to see if we already have credentials stored
		credentials = store.get()
		if not credentials or credentials.invalid:
			# If not create new flow
			flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
			flow.user_agent = APPLICATION_NAME
			# This will store our credentials for next time if User gives authorization
			credentials = tools.run_flow(flow, store, flags)
		return credentials
		
	def getCalEvents(self):
		credentials = self.getCredentials()
		# Need to authorize httplib2 object with our credentials so that we can build a service object with it and send requests
		http = httplib2.Http()
		http = credentials.authorize(http)
		now = datetime.datetime.utcnow().isoformat() + 'Z'
		service = discovery.build('calendar', 'v3', http=http)
		# Build request calling on the 'events' collection of our service object
		request = service.events().list(calendarId='primary', timeMin=now, maxResults = 5, singleEvents=True, orderBy='startTime')
		# Execute request and get response
		response = request.execute()
		events = response.get('items', [])
		return events
		
	def getTodaysCalEvents(self):
		events = self.getCalEvents()
		todaysEvents = []
		for event in events:
			utcString = event['start'].get("dateTime")
			eventDT = parse(utcString)
			todayDT = datetime.datetime.now()
			if (eventDT.month == todayDT.month and eventDT.day == todayDT.day and eventDT.year == todayDT.year):
				todaysEvents.append(event)
		return todaysEvents
		
	def generateEventsString(self):
		todaysEvents = self.getTodaysCalEvents()
		eventsString = ''
		if not todaysEvents:
			eventsString = 'No calendar events today.'
			return eventsString
		else:
			for event in todaysEvents:
				description = event['summary']
				utcString = event['start'].get("dateTime")
				eventDT = parse(utcString)
				if (eventDT.minute == 0):
					singleEventString = ' Today at {hour} on the dot you have a calendar event titled, {desc}.' .format(hour = eventDT.hour, desc = description)
				elif (eventDT.minute < 10):
					singleEventString = ' Today at {hour} O {minute} you have a calendar event titled, {desc}.' .format(hour = eventDT.hour, minute = eventDT.minute, desc = description)
				else:
					singleEventString = ' Today at {hour}:{minute} you have a calendar event titled, {desc}.' .format(hour = eventDT.hour, minute = eventDT.minute, desc = description)
				eventsString = eventsString + singleEventString
			return eventsString
		
			


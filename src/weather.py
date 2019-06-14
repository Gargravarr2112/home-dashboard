import requests
import json
import datetime

API_KEY = ""
METOFFICE_OXFORD_LOCATION_ID = 310118
FORECAST_URL = "http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/json/"
config = {}

with open('weather.json', 'r') as configFile:
	config = json.load(configFile)

API_KEY = config['APIKey']

def getWeather():
	query = { 'key': API_KEY, 'res': '3hourly' }
	weatherRequest = requests.get(FORECAST_URL + str(METOFFICE_OXFORD_LOCATION_ID), params=query)
	if weatherRequest.status_code != 200:
		print("Error retrieving weather")
		return
	weatherData = weatherRequest.json()
	days = weatherData['SiteRep']['DV']['Location']['Period']
	for day in days:
		date = datetime.datetime.strptime(day['value'], '%Y-%m-%dZ')
		reports = day['Rep']
		for report in reports:
			interval = datetime.timedelta(minutes=int(report['$']))
			reportTime = date + interval
		nextThreeHours = reports[0]
		return nextThreeHours
import requests
import json
import datetime
import logging

logger = logging.getLogger(__name__)

API_KEY = ""
METOFFICE_OXFORD_LOCATION_ID = 310118
FORECAST_URL = "http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/json/"
METOFFICE_WEATHER_KEY = {0: "Clear night", 1: "Sunny day", 2: "Partly cloudy (night)", 3: "Partly cloudy (day)", 5: "Mist", 6: "Fog", 7: "Cloudy", 8: "Overcast", 9: "Light rain shower (night)", 10: "Light rain shower (day)", 11: "Drizzle", 12: "Light rain", 13: "Heavy rain shower (night)", 14: "Heavy rain shower (day)", 15: "Heavy rain", 16: "Sleet shower (night)", 17: "Sleet shower (day)", 18: "Sleet", 19: "Hail shower (night)", 20: "Hail shower (day)", 21: "Hail", 22: "Light snow shower (night)", 23: "Light snow shower (day)", 24: "Light snow", 25: "Heavy snow shower (night)", 26: "Heavy snow shower (day)", 27: "Heavy snow", 28: "Thunder shower (night)", 29: "Thunder shower (day)", 30: "Thunder"}
WEATHER_IMAGE_KEY = {0: "night-clear", 1: "day-clear", 2: "night-cloud", 3: "day-cloud", 5: "fog", 6: "fog", 7: "cloudy", 8: "cloudy", 9: "night-rain", 10: "day-rain", 11: "$t-rain", 12: "$t-rain", 13: "$t-rain", 14: "heavy-rain", 15: "heavy-rain", 16: "snow", 17: "snow", 18: "snow", 19: "snow", 20: "snow", 21: "snow", 22: "snow", 23: "snow", 24: "snow", 25: "snow", 26: "snow", 27: "snow", 28: "thunder", 29: "thunder", 30: "thunder"}
RAIN_THRESHHOLD = 50 #%
config = {}

with open('weather.json', 'r') as configFile:
	logger.debug("Loading config file")
	config = json.load(configFile)
	logger.debug("Loaded config file")

API_KEY = config['APIKey']

def getWeather():
	query = { 'key': API_KEY, 'res': '3hourly' }
	logger.debug("Querying Met Office API for Oxford weather")
	weatherRequest = requests.get(FORECAST_URL + str(METOFFICE_OXFORD_LOCATION_ID), params=query)
	if weatherRequest.status_code != 200:
		logger.error("Error retrieving weather: HTTP %d", weatherRequest.status_code)
		return
	weatherData = weatherRequest.json()
	today = weatherData['SiteRep']['DV']['Location']['Period'][0]
	date = datetime.datetime.strptime(today['value'], '%Y-%m-%dZ')
	reports = today['Rep']
	rain = (datetime.datetime.now(), 0)
	for report in reports:
		interval = datetime.timedelta(minutes=int(report['$'])) #$ in this instance being the time since midnight in minutes
		reportTime = date + interval
		rainProbability = int(report['Pp'])
		if rainProbability > RAIN_THRESHHOLD:
			rain = (reportTime, rainProbability)
	nextThreeHours = reports[0]
	return (nextThreeHours, rain)

def getWeatherType(typeCode):
	weatherName = METOFFICE_WEATHER_KEY[typeCode]
	weatherImage = "img/{0}.png".format(WEATHER_IMAGE_KEY[typeCode].replace('$t', 'night')) #TODO: pass in day or night and select accordingly
	return (weatherName, weatherImage)
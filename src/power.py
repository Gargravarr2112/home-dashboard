try:
	from gpiozero import Energenie
except ImportError:
	print("Debug mode")
	from dummy import Energenie

import requests, json, logging
logger = logging.getLogger(__name__)

ENERGYHIVE_API = "https://www.energyhive.com/mobile_proxy/getEnergy"
ENERGYHIVE_API_TOKEN = ""
PENCE_PER_KWH = 14.626
STANDING_CHARGE = 14.416

FAN_CHANNEL = 1
HEATER_CHANNEL = 2

with open("power.json") as configFile:
	logger.debug("Loading config file")
	config = json.load(configFile)
	logger.debug("Loaded config file")

ENERGYHIVE_API_TOKEN = config["APIKey"]

def getYesterdayPowerUse():
	logger.debug("Querying EnergyHive API for power use data")
	requestParameters = { "token": ENERGYHIVE_API_TOKEN, "period": "day", "offset": "-1" }
	try:
		powerUse = requests.get(ENERGYHIVE_API, requestParameters)
		if powerUse.status_code != 200:
			logger.error("API returned HTTP %d", powerUse.status_code)
			return (0, 0)
		kWh = float(powerUse.json()['sum'])
		costP = (kWh * PENCE_PER_KWH) + STANDING_CHARGE
		return (kWh, costP)
	except Exception as e:
		logger.error("Failed to access EnergyHive API")
		logger.error(e)
		return (0, 0)

fan = Energenie(FAN_CHANNEL)
heater = Energenie(HEATER_CHANNEL)

def toggleFan(event=None):
	logger.debug("Fan toggled")
	if event:
		button = event.GetEventObject()
		if toggleSocket(fan):
			button.SetBackgroundColour('#8AE234')
		else:
			button.SetBackgroundColour('#EF2929')
	else:
		return toggleSocket(fan)

def toggleHeater(event=None):
	logger.debug("Heater toggled")
	if event:
		button = event.GetEventObject()
		if toggleSocket(heater):
			button.SetBackgroundColour('#8AE234')
		else:
			button.SetBackgroundColour('#EF2929')
	else:
		return toggleSocket(heater)

def toggleSocket(socket):
	if socket.value:
		logger.debug("Switching off")
		socket.off()
	else:
		logger.debug("Switching on")
		socket.on()
	return socket.value
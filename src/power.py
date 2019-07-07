try:
	from gpiozero import Energenie
except ImportError:
	print("Debug mode")
	from dummy import Energenie

import requests, json, logging
logger = logging.getLogger(__name__)

ENERGYHIVE_API = "https://www.energyhive.com/mobile_proxy/getEnergy"
ENERGYHIVE_API_TOKEN = ""

FAN_CHANNEL = 1
HEATER_CHANNEL = 2

with open("power.json") as configFile:
	logger.debug("Loading config file")
	config = json.load(configFile)
	logger.debug("Loaded config file")

ENERGYHIVE_API_TOKEN = config["APIKey"]

def getYesterdayPowerUse():
	logger.info("Querying EnergyHive API for power use data")
	requestParameters = { "token": ENERGYHIVE_API_TOKEN, "period": "day", "offset": "-1" }
	powerUse = requests.get(ENERGYHIVE_API, requestParameters)
	if powerUse.status_code != 200:
		logger.error("API returned HTTP %d", powerUse.status_code)
		return 0
	kWh = powerUse.json()['sum']
	return float(kWh)

fan = Energenie(FAN_CHANNEL)
heater = Energenie(HEATER_CHANNEL)

def toggleFan():
	return toggleSocket(fan)

def toggleHeader():
	return toggleSocket(heater)

def toggleSocket(socket):
	if socket.value:
		socket.off()
	else:
		socket.on()
	return socket.value
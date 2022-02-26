#!/usr/bin/env python3
#CO2 code credit: https://charlottemach.com/2020/05/17/co2-sensor-raspi.html

try:
	import Adafruit_DHT, serial
except ImportError:
	print("Debug mode")
	from dummy import Adafruit_DHT, serial
import time, json, MySQLdb, logging

DHT_PIN = 21
logger = logging.getLogger(__name__)

def connectDB():
	try:
		with open('sql.json', 'r') as configFile:
			sqlConfig = json.load(configFile)
		dbConn = MySQLdb.connect(host=sqlConfig['host'], user=sqlConfig['user'], password=sqlConfig['password'], db=sqlConfig['db'])
		dbConn.autocommit(True)
		return dbConn.cursor()
	except Exception as e:
		logger.critical("Unable to connect to MySQL database: {0}".format(e))
		return False

def getTempReadings():
	logger.debug("Getting sensor values from DHT11")
	return Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, DHT_PIN)

class CO2Sensor():
	request = [0xff, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79]

	def __init__(self, port='/dev/ttyAMA0'):
		self.serial = serial.Serial(
				port = port,
				timeout = 1
		)

	def get(self):
		self.serial.write(bytearray(self.request))
		response = self.serial.read(9)
		if len(response) == 9:
			current_time = time.strftime('%H:%M:%S', time.localtime())
			return {"time": current_time, "ppa": (response[2] << 8) | response[3], "temp": response[4]}
		return False

def main():
	sensor = CO2Sensor()
	dbCursor = connectDB()
	if not dbCursor:
		return
	while (True):
		current = sensor.get()
		if current:
			dbCursor.execute("INSERT INTO sensorReading(sensorID, unitID, value, time) VALUES (1, 6, %s, NOW()), (1, 7, %s, NOW())", (current['ppa'], current['temp']))
		else:
			logger.error("Failed to get CO2 sensor readings")
		humidTemp = getTempReadings()
		if humidTemp:
			dbCursor.execute("INSERT INTO sensorReading(sensorID, unitID, value, time) VALUES (1, 2, %s, NOW()), (1, 1, %s, NOW())", humidTemp)
		else:
			logger.error("Failed to get temperature/humidity readings")
		time.sleep(300)
	dbConn.close()

if __name__ == '__main__':
	main()

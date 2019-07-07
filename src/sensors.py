try:
	import Adafruit_DHT
except ImportError:
	print("Debug mode")
	from dummy import Adafruit_DHT
import sqlite3

DHT_PIN = 21
LOG_DB = 'sensors.db'
dbConn = sqlite3.connect(LOG_DB, isolation_level=None)

def getReadings():
	return Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, DHT_PIN)

def createTable():
	dbCursor = dbConn.cursor()
	dbCursor.execute("CREATE TABLE IF NOT EXISTS Readings (time datetime, humidity real, temperature real)")

def logReadings(temperature, humidity):
	dbCursor = dbConn.cursor()
	values = (humidity, temperature)
	dbCursor.execute("INSERT INTO Readings(time, humidity, temperature) VALUES (date('now'), ?, ?)", values)
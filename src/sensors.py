try:
	import Adafruit_DHT
except ImportError:
	print("Debug mode")
	from dummy import Adafruit_DHT
import sqlite3, logging

DHT_PIN = 21
LOG_DB = 'sensors.db'
dbConn = sqlite3.connect(LOG_DB, isolation_level=None)
logger = logging.getLogger(__name__)

def getReadings():
	logger.debug("Getting sensor values from DHT11")
	return Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, DHT_PIN)

def createTable():
	logger.debug("Creating SQLite DB table")
	dbCursor = dbConn.cursor()
	dbCursor.execute("CREATE TABLE IF NOT EXISTS Readings (time datetime, humidity real, temperature real)")
	dbCursor.close()

def logReadings(temperature, humidity):
	logger.debug("Storing sensor values in database: {0}, {1}".format(temperature, humidity))
	dbCursor = dbConn.cursor()
	values = (humidity, temperature)
	dbCursor.execute("INSERT INTO Readings(time, humidity, temperature) VALUES (datetime('now'), ?, ?)", values)
	dbCursor.close()
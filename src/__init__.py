#Python modules
import wx, requests, json, datetime, time, logging
from wx import gizmos
#Custom modules
import weather, news, power, routerstats, sensors

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

PI_SCREEN_RESOLUTION = wx.Size(800, 480)

class DashboardFrame(wx.Frame):
	def __init__(self):
		super().__init__(parent=None, title="Dashboard", size=PI_SCREEN_RESOLUTION)

		layout = wx.BoxSizer(wx.VERTICAL)

		textStyle = wx.Font(pointSize=12, family=wx.FONTFAMILY_SWISS, style=wx.FONTSTYLE_NORMAL, weight=wx.FONTWEIGHT_NORMAL, underline=False, faceName="", encoding=wx.FONTENCODING_SYSTEM)

		self.clock = gizmos.LEDNumberCtrl(self, wx.ID_ANY, wx.DefaultPosition, wx.Size(180, 40), gizmos.LED_ALIGN_CENTER)
		self.clockTick = wx.Timer(self, 1)
		# update clock digits every second (1000ms)
		self.clockTick.Start(1000)
		self.refreshTimer = wx.Timer(self, 2)
		# update the rest once an hour
		self.refreshTimer.Start(3600000)
		self.Bind(wx.EVT_TIMER, self.OnTimer)
		layout.Add(self.clock, 0, 0, 0)

		self.weatherText = wx.StaticText(self)
		self.weatherText.SetFont(textStyle)
		layout.Add(self.weatherText, 0, 0, 0)

		self.weatherGraphic = wx.StaticBitmap(self)
		layout.Add(self.weatherGraphic, 0, 0, 0)

		self.rainText = wx.StaticText(self)
		self.rainText.SetFont(textStyle)
		layout.Add(self.rainText, 0, 0, 0)
		
		self.newsTitle = wx.StaticText(self)
		self.newsTitle.SetFont(textStyle)
		layout.Add(self.newsTitle, 0, 0, 0)
		
		self.newsList = wx.ListBox(self)
		self.newsList.SetFont(textStyle)
		layout.Add(self.newsList, 1, wx.EXPAND | wx.ALL, 0)

		powerButtons = wx.BoxSizer(wx.HORIZONTAL)
		fanButton = wx.Button(self, wx.ID_ANY, "Fan")
		fanButton.Bind(wx.EVT_BUTTON, power.toggleFan)
		powerButtons.Add(fanButton, 0, 0, 0)
		heaterButton = wx.Button(self, wx.ID_ANY, "Heater")
		heaterButton.Bind(wx.EVT_BUTTON, power.toggleHeater)
		powerButtons.Add(heaterButton, 0, 0, 0)
		layout.Add(powerButtons, 0, 0, 0)

		self.powerUsage = wx.StaticText(self)
		self.powerUsage.SetFont(textStyle)
		layout.Add(self.powerUsage, 0, 0, 0)

		self.flatConditions = wx.StaticText(self)
		self.flatConditions.SetFont(textStyle)
		layout.Add(self.flatConditions, 0, 0, 0)

		
		self.trafficInfo = wx.StaticText(self)
		self.trafficInfo.SetFont(textStyle)
		layout.Add(self.trafficInfo, 0, 0, 0)

		self.WANIP = wx.StaticText(self)
		self.WANIP.SetFont(textStyle)
		layout.Add(self.WANIP, 0, 0, 0)

		self.pendingSMS = wx.StaticText(self)
		self.pendingSMS.SetFont(textStyle)
		layout.Add(self.pendingSMS, 0, 0, 0)

		self.signalStrength = wx.StaticText(self)
		self.signalStrength.SetFont(textStyle)
		layout.Add(self.signalStrength, 0, 0, 0)

		refreshButton = wx.Button(self, wx.ID_ANY, "Refresh")
		refreshButton.Bind(wx.EVT_BUTTON, self.refreshButtonClick)
		layout.Add(refreshButton, 0, 0, 0)

		self.refreshTime = wx.StaticText(self)
		layout.Add(self.refreshTime)

		self.refreshedTime = datetime.datetime.min

		self.refreshAll()

		self.SetSizer(layout)
		self.Show()

	def showWeather(self):
		logger.info("Getting weather")
		weatherForecast = weather.getWeather()
		if weatherForecast:
			(weatherData, rainData) = weatherForecast
			weatherCode = int(weatherData['W'])
			weatherType = weather.getWeatherType(weatherCode) #returns tuple of name and image filename
			self.weatherGraphic.SetBitmap(wx.Bitmap(weatherType[1]))
			weatherText = "{0} - {1}℃ (feels like {2}℃) - {3}MPH {4} - {5}%".format(weatherType[0], weatherData['T'], weatherData['F'], weatherData['S'], weatherData['D'], weatherData['H'])
			self.weatherText.SetLabelText(weatherText)
			chanceOfRain = rainData[1]
			if chanceOfRain > 0:
				logger.debug("Rain: {0}% at {1}".format(chanceOfRain, rainData[0]))
				if (rainData[0] - datetime.datetime.now()).days == 1:
					day = "tomorrow"
				else:
					day = "today"
				rainLabel = "{0}% chance of rain predicted {1} at {2}".format(chanceOfRain, day, rainData[0].strftime('%H:%M'))
			else:
				rainLabel = "No rain predicted"
			self.rainText.SetLabelText(rainLabel)
		else:
			logger.error("Unable to display weather")
	
	def showNews(self):
		logger.info("Getting news")
		todaysNews = news.getTop3Articles()
		if todaysNews:
			updatedTime = todaysNews['updateTime']
			headlines = []
			for article in todaysNews['articles']:
				headlines.append(article['title'])
			self.newsTitle.SetLabelText("News as of {0}".format(time.strftime('%H:%M', updatedTime)))
			self.newsList.SetItems(headlines)
		else:
			logger.error("Unable to display news")

	def showPowerUse(self):
		self.powerUsage.SetLabelText("Power usage yesterday: {0} kWh".format(power.getYesterdayPowerUse()))
	
	def showFlatConditions(self):
		(humidity, temperature) = sensors.getReadings()
		self.flatConditions.SetLabelText("Humidity: {0}%, Temperature: {1}℃".format(humidity, temperature))
		sensors.logReadings(humidity, temperature)
	
	def showTrafficStats(self):
		(refreshDate, downloadBytes, uploadBytes) = routerstats.getTrafficStats()
		downloadGB = round(downloadBytes / routerstats.bytesToGB, 2)
		uploadGB = round(uploadBytes / routerstats.bytesToGB, 2)
		totalGB = round(downloadGB + uploadGB, 2)
		self.trafficInfo.SetLabelText("Traffic since {0}: {1} GB down, {2} GB up, total {3} GB".format(refreshDate.strftime('%a %m %b'), downloadGB, uploadGB, totalGB))
	
	def showWANIP(self):
		self.WANIP.SetLabelText("WAN IP: {0}".format(routerstats.getWANIP()))
	
	def showPendingSMS(self):
		self.pendingSMS.SetLabelText("Pending SMS: {0}".format(routerstats.checkForSMS()))
	
	def showSignalStrength(self):
		self.signalStrength.SetLabelText("4G Signal Strength: {0}/5".format(routerstats.getSignalStrength()))
	
	def clearRouterSession(self):
		routerstats.clearSession()
	
	def refreshButtonClick(self, event):
		logger.debug("Refresh button clicked")
		self.refreshAll()

	def refreshAll(self):
		self.showWeather()
		self.showNews()
		self.showPowerUse()
		self.showFlatConditions()
		self.showTrafficStats()
		self.showWANIP()
		self.showPendingSMS()
		self.showSignalStrength()
		self.clearRouterSession()
		self.refreshedTime = datetime.datetime.now()
		self.refreshTime.SetLabelText("Refreshed at {0}".format(self.refreshedTime.strftime("%H:%M")))
	
	def OnTimer(self, event):
		if event.GetTimer().GetId() == 1:
			# get current time from computer
			current = time.localtime(time.time())
			# time string can have characters 0..9, -, period, or space
			ts = time.strftime("%H:%M:%S", current)
			self.clock.SetValue(ts)
		elif event.GetTimer().GetId() == 2:
			logger.debug("Refresh timer triggered")
			self.refreshAll()

if __name__ == '__main__':
	logger.debug("Starting up")
	application = wx.App()
	frame = DashboardFrame()
	application.MainLoop()
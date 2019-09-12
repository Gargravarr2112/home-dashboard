#Python modules
import wx, requests, json, datetime, time, logging
#Custom modules
import weather, news, power, routerstats, sensors

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

PI_SCREEN_RESOLUTION = wx.Size(800, 480)

class DashboardFrame(wx.Frame):
	def __init__(self):
		super().__init__(parent=None, title="Dashboard", size=PI_SCREEN_RESOLUTION)

		layout = wx.BoxSizer(wx.VERTICAL)

		self.weatherGraphic = wx.StaticBitmap(self)
		self.weatherText = wx.StaticText(self)

		layout.Add(self.weatherText, 0, 0, 0)
		layout.Add(self.weatherGraphic, 0, 0, 0)

		self.rainText = wx.StaticText(self)
		layout.Add(self.rainText, 0, 0, 0)
		
		self.newsTitle = wx.StaticText(self)
		layout.Add(self.newsTitle, 0, 0, 0)
		
		self.newsList = wx.ListBox(self)
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
		layout.Add(self.powerUsage, 0, 0, 0)

		self.flatConditions = wx.StaticText(self)
		layout.Add(self.flatConditions, 0, 0, 0)

		
		self.trafficInfo = wx.StaticText(self)
		layout.Add(self.trafficInfo, 0, 0, 0)

		self.WANIP = wx.StaticText(self)
		layout.Add(self.WANIP, 0, 0, 0)

		self.pendingSMS = wx.StaticText(self)
		layout.Add(self.pendingSMS, 0, 0, 0)

		self.signalStrength = wx.StaticText(self)
		layout.Add(self.signalStrength, 0, 0, 0)

		refreshButton=wx.Button(self, wx.ID_ANY, "Refresh")
		refreshButton.Bind(wx.EVT_BUTTON, self.refreshButtonClick)
		layout.Add(refreshButton, 0, 0, 0)

		self.refreshAll()

		self.SetSizer(layout)
		self.Show()

	def showWeather(self):
		todaysWeather = weather.getWeather()
		if todaysWeather:
			logger.info("Adding weather")
			weatherCode = int(todaysWeather[0]['W'])
			weatherType = weather.getWeatherType(weatherCode) #returns tuple of name and image filename
			self.weatherGraphic.SetBitmap(wx.Bitmap(weatherType[1]))
			self.weatherText.SetLabelText(weatherType[0])
			self.rainText.SetLabelText("{0}% chance of rain predicted at {1}".format(todaysWeather[1][1], todaysWeather[1][0]))
	
	def showNews(self):
		todaysNews = news.getTop3Articles()
		if todaysNews:
			logger.info("Addng news")
			updatedTime = todaysNews['updateTime']
			headlines = []
			for article in todaysNews['articles']:
				headlines.append(article['title'])
			self.newsTitle.SetLabelText("News as of {0}".format(time.strftime('%H:%M', updatedTime)))
			self.newsList.SetItems(headlines)

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
		totalGB = round(downloadGB + uploadBytes, 2)
		self.trafficInfo.SetLabelText("Traffic since {0}: {1} GB down, {2} GB up, total {3} GB".format(refreshDate, downloadGB, uploadGB, totalGB))
	
	def showWANIP(self):
		self.WANIP.SetLabelText("WAN IP: {0}".format(routerstats.getWANIP()))
	
	def showPendingSMS(self):
		self.pendingSMS.SetLabelText("Pending SMS: {0}".format(routerstats.checkForSMS()))
	
	def showSignalStrength(self):
		self.signalStrength.SetLabelText("4G Signal Strength: {0}/5".format(routerstats.getSignalStrength()))
	
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

if __name__ == '__main__':
	logger.debug("Starting up")
	application = wx.App()
	frame = DashboardFrame()
	application.MainLoop()
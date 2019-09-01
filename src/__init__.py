#Python modules
import wx, requests, json, datetime, logging
#Custom modules
import weather, news, power, routerstats, sensors

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

PI_SCREEN_RESOLUTION = wx.Size(800, 480)

# class DashboardApplication(wx.App):
# 	def OnInit(self):
# 		super().__init__()

class DashboardFrame(wx.Frame):
	def __init__(self):
		super().__init__(parent=None, title="Dashboard", size=PI_SCREEN_RESOLUTION)

		layout = wx.BoxSizer(wx.VERTICAL)

		todaysWeather = weather.getWeather()
		if todaysWeather:
			logger.info("Adding weather")
			weatherCode = int(todaysWeather[0]['W'])
			weatherType = weather.getWeatherType(weatherCode) #returns tuple of name and image filename
			weatherGraphic = wx.StaticBitmap(self, bitmap=wx.Bitmap(weatherType[1]))
			weatherText = wx.StaticText(self, label=weatherType[0])

			layout.Add(weatherText, 0, 0, 0)
			layout.Add(weatherGraphic, 0, 0, 0)
			if todaysWeather[1]:
				rainText = wx.StaticText(self, label="{0}% chance of rain predicted at {1}".format(todaysWeather[1][1], todaysWeather[1][0]))
				layout.Add(rainText, 0, 0, 0)

		todaysNews = news.getTop3Articles()
		if todaysNews:
			logger.info("Addng news")
			updatedTime = todaysNews['updateTime']
			newsTitle = wx.StaticText(self, label="News as of {0}".format(updatedTime))
			layout.Add(newsTitle, 0, 0, 0)
			headlines = []
			for article in todaysNews['articles']:
				headlines.append(article['title'])
			newsList = wx.ListBox(self, choices=headlines)
			layout.Add(newsList, 0, 0, 0)

		powerButtons = wx.BoxSizer(wx.HORIZONTAL)
		fanButton = wx.Button(self, wx.ID_ANY, "Fan")
		fanButton.Bind(wx.EVT_BUTTON, power.toggleFan)
		powerButtons.Add(fanButton, 0, 0, 0)
		heaterButton = wx.Button(self, wx.ID_ANY, "Heater")
		heaterButton.Bind(wx.EVT_BUTTON, power.toggleHeater)
		powerButtons.Add(heaterButton, 0, 0, 0)
		layout.Add(powerButtons, 0, 0, 0)

		powerUsage = wx.StaticText(self, label="Power usage yesterday: {0} kWh".format(power.getYesterdayPowerUse()))
		layout.Add(powerUsage, 0, 0, 0)

		sensorReadings = sensors.getReadings()
		flatConditions = wx.StaticText(self, label="Humidity: {0}%, Temperature: {1}℃".format(sensorReadings[0], sensorReadings[1]))
		layout.Add(flatConditions, 0, 0, 0)

		traffic = routerstats.getTrafficStats()
		downloadGB = round(traffic[1] / routerstats.bytesToGB, 2)
		uploadGB = round(traffic[2] / routerstats.bytesToGB, 2)
		trafficInfo = wx.StaticText(self, label="Traffic since {0}: {1} GB down, {2} GB up".format(traffic[0], downloadGB, uploadGB))
		layout.Add(trafficInfo, 0, 0, 0)

		WANIP = wx.StaticText(self, label="WAN IP: {0}".format(routerstats.getWANIP()))
		layout.Add(WANIP, 0, 0, 0)

		pendingSMS = wx.StaticText(self, label="Pending SMS: {0}".format(routerstats.checkForSMS()))
		layout.Add(pendingSMS, 0, 0, 0)

		signalStrength = wx.StaticText(self, label="4G Signal Strength: {0}/5".format(routerstats.getSignalStrength()))
		layout.Add(signalStrength, 0, 0, 0)

		self.SetSizer(layout)
		self.Show()

if __name__ == '__main__':
	logger.debug("Starting up")
	application = wx.App()
	frame = DashboardFrame()
	application.MainLoop()
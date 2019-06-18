import wx
import requests
import json
import datetime
import logging
import weather
import news

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

PI_SCREEN_RESOLUTION = wx.Size(800, 480)

# class DashboardApplication(wx.App):
# 	def OnInit(self):
# 		super().__init__()

class DashboardFrame(wx.Frame):
	def __init__(self):
		super().__init__(parent=None, title="Dashboard", size=PI_SCREEN_RESOLUTION)

		panel = wx.Panel(self)

		layout = wx.BoxSizer(wx.VERTICAL)

		todaysWeather = weather.getWeather()
		if todaysWeather:
			logger.info("Adding weather")
			weatherCode = int(todaysWeather[0]['W'])
			weatherType = weather.getWeatherType(weatherCode) #returns tuple of name and image filename
			weatherGraphic = wx.StaticBitmap(panel, bitmap=wx.Bitmap(weatherType[1]))
			weatherText = wx.StaticText(panel, label=weatherType[0])
			layout.Add(weatherText, wx.ID_ANY, wx.EXPAND | wx.ALL, 20)
			layout.Add(weatherGraphic, wx.ID_ANY, wx.EXPAND | wx.ALL, 20)

		todaysNews = news.getTop3Articles()
		if todaysNews:
			logger.info("Addng news")
			updatedTime = todaysNews['updateTime']
			newsTitle = wx.StaticText(panel, label="News as of {0}".format(updatedTime))
			layout.Add(newsTitle, wx.ID_ANY, wx.EXPAND | wx.ALL, 20)
			headlines = []
			for article in todaysNews['articles']:
				headlines.append(article['title'])
			newsList = wx.ListBox(panel, choices=headlines)
			layout.Add(newsList, wx.ID_ANY, wx.EXPAND | wx.ALL, 20)

		self.Show()

if __name__ == '__main__':
	logger.debug("Starting up")
	application = wx.App()
	frame = DashboardFrame()
	application.MainLoop()
import wx
import requests
import json
import datetime
import logging
import weather

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

		layout = wx.BoxSizer(wx.HORIZONTAL)

		todaysWeather = weather.getWeather()
		if todaysWeather:
			weatherType = weather.getWeatherType(int(todaysWeather['W'])) #returns tuple of name and image filename
			weatherGraphic = wx.StaticBitmap(panel, bitmap=wx.Bitmap(weatherType[1]))
		layout.Add(weatherGraphic, wx.ID_ANY, wx.EXPAND | wx.ALL, 20)

		self.Show()

if __name__ == '__main__':
	logger.debug("Starting up")
	application = wx.App()
	frame = DashboardFrame()
	application.MainLoop()
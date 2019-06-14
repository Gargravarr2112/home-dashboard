import wx
import requests
import json
import datetime
import logging
import weather

PI_SCREEN_RESOLUTION = wx.Size(800, 480)

# class DashboardApplication(wx.App):
# 	def OnInit(self):
# 		super().__init__()

class DashboardFrame(wx.Frame):
	def __init__(self):
		super().__init__(parent=None, title="Dashboard", size=PI_SCREEN_RESOLUTION)

		panel = wx.Panel(self)

		self.textbox = wx.TextCtrl(panel, pos=(5,5))
		btn = wx.Button(panel, label="Submit", pos=(5,55))

		self.Show()

if __name__ == '__main__':
	application = wx.App()
	frame = DashboardFrame()
	application.MainLoop()
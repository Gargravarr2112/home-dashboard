"""
  Designed for a Huawei B310 router
"""

import requests, logging
from xml.dom import minidom
from datetime import datetime

logger = logging.getLogger(__name__)

routerIP = '192.168.1.1'
bytesToGB = 1073741824
bytesToMB = 1048576

session = None

#Some portions of the API require a session cookie. Thankfully, Requests supports this neatly
def startSession():
  global session
  logger.debug("Starting session for %s", routerIP)
  session = requests.Session()
  session.get('http://{0}/html/home.html'.format(routerIP))

#Can't get any more than the count without logging in, but it's enough to alert on
def checkForSMS():
  logger.debug("Checking for unread SMS")
  response = requests.get("http://{0}/api/monitoring/check-notifications".format(routerIP))
  if not response.status_code == 200:
    logger.error("Failed to get notifications list from router: HTTP %d", response.status_code)
    return -1
  tree = minidom.parseString(response.text)
  doc = tree.documentElement
  unread = doc.getElementsByTagName('UnreadMessage')[0]
  unreadCount = unread.childNodes[0].data
  return int(unreadCount)

#Gets the current month up/download totals
def getTrafficStats():
  logger.debug("Getting traffic stats")
  if not session:
    startSession()
  stats = session.get("http://{0}/api/monitoring/month_statistics".format(routerIP))
  if not stats.status_code == 200:
    logger.error("Failed to get notifications list from router: HTTP %d", stats.status_code)
    return (-1, -1)
  tree = minidom.parseString(stats.text)
  doc = tree.documentElement
  lastClearDate = doc.getElementsByTagName('MonthLastClearTime')[0].childNodes[0].data
  dateReset = datetime.strptime(lastClearDate, '%Y-%m-%d')
  downloadBytes = int(doc.getElementsByTagName('CurrentMonthDownload')[0].childNodes[0].data)
  uploadBytes = int(doc.getElementsByTagName('CurrentMonthUpload')[0].childNodes[0].data)
  return (dateReset, downloadBytes, uploadBytes)

def getWANIP():
  logger.debug("Getting WAN IP address")
  if not session:
    startSession()
  status = session.get("http://{0}/api/monitoring/status".format(routerIP))
  if not status.status_code == 200:
    logger.error("Failed to get notifications list from router: HTTP %d", status.status_code)
    return False
  tree = minidom.parseString(status.text)
  return tree.documentElement.getElementsByTagName('WanIPAddress')[0].childNodes[0].data

def getSignalStrength():
  logger.debug("Getting 4G signal strength")
  if not session:
    startSession()
  status = session.get("http://{0}/api/monitoring/status".format(routerIP))
  if not status.status_code == 200:
    logger.error("Failed to get notifications list from router: HTTP %d", status.status_code)
    return False
  tree = minidom.parseString(status.text)
  return int(tree.documentElement.getElementsByTagName('SignalIcon')[0].childNodes[0].data)
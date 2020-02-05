"""
  Designed for a Huawei B310 router
"""

import requests, logging
from xml.dom import minidom
from datetime import datetime

logger = logging.getLogger(__name__)

routerIP = '192.168.0.1'
bytesToGB = 1073741824
bytesToMB = 1048576
monthlyLimitBytes = 32212254720 #30GB

session = None

#Some portions of the API require a session cookie. Thankfully, Requests supports this neatly
def startSession():
  global session
  logger.debug("Starting session for %s", routerIP)
  session = requests.Session()
  session.get('http://{0}/html/home.html'.format(routerIP))

#Refactored to move error-checking into a nice function
def queryRouterAPI(endpoint):
  if not session:
    startSession()
  try:
    response = session.get("http://{0}/api/{1}".format(routerIP, endpoint))
    if not response.status_code == 200:
      logger.error("Failed to get notifications list from router: HTTP %d", response.status_code)
      return False
    else:
      tree = minidom.parseString(response.text)
      if tree.documentElement.tagName == 'error':
        raise Exception("Router returned error {}".format(tree.documentElement.childNodes[0].childNodes[0].data))
      else:
        return tree
  except Exception as e:
    logger.error("Failed to query router API")
    logger.error(e)
    return False

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
  stats = queryRouterAPI("monitoring/month_statistics")
  if stats:
    doc = stats.documentElement
    lastClearDate = doc.getElementsByTagName('MonthLastClearTime')[0].childNodes[0].data
    dateReset = datetime.strptime(lastClearDate, '%Y-%m-%d')
    downloadBytes = int(doc.getElementsByTagName('CurrentMonthDownload')[0].childNodes[0].data)
    uploadBytes = int(doc.getElementsByTagName('CurrentMonthUpload')[0].childNodes[0].data)
    return (dateReset, downloadBytes, uploadBytes)
  else:
    return (datetime.now(), 0, 0)

def getWANIP():
  logger.debug("Getting WAN IP address")
  status = queryRouterAPI("monitoring/status")
  if status:
    return status.documentElement.getElementsByTagName('WanIPAddress')[0].childNodes[0].data
  else:
    return "Not available"

def getSignalStrength():
  logger.debug("Getting 4G signal strength")
  status = queryRouterAPI("monitoring/status")
  if status:
    return int(status.documentElement.getElementsByTagName('SignalIcon')[0].childNodes[0].data)
  else:
    return 0

#The B310 strictly enforces sessions for various APIs, but doesn't set an expiry on session cookies, so it's impossible to know the session has expired until 
#the router returns an error. Even nicer, it doesn't return an HTTP error (e.g. 403) but instead an XML object containing the error message.
#Call this after using all necessary methods in this file to clear the session so it starts fresh next time.
def clearSession():
  logger.debug("Closing session")
  session.close()
import feedparser
import logging
logger = logging.getLogger(__name__)

bbcRSSFeed = "http://feeds.bbci.co.uk/news/rss.xml"

#Create a persistent RSS reader in memory rather than creating new ones each time, since feedparser can update itself
feed = feedparser.parse(bbcRSSFeed)

def getTop3Articles():
	logger.debug("Updating BBC News RSS feed")
	try:
		feed.update()
		if feed.status != 200:
			logger.error("RSS feed failed to update!")
			return {}
		updateTime = feed.feed['updated_parsed']
		newsList = { "updateTime": updateTime, "articles": feed.entries[0:3] }
		return newsList
	except Exception as e:
		logger.error("Failed to update BBC News feed")
		logger.error(e)
		return False
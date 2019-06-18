import feedparser
import logging
logger = logging.getLogger(__name__)

bbcRSSFeed = "http://feeds.bbci.co.uk/news/rss.xml"

feed = None

#Create a persistent RSS reader in memory rather than creating new ones each time, since feedparser can update itself
feed = feedparser.parse(bbcRSSFeed)

def getTop3Articles():
	logger.debug("Updating BBC News RSS feed")
	feed.update()
	if feed.status != 200:
		logger.error("RSS feed failed to update!")
		return {}
	updateTime = feed.feed['updated']
	newsList = { "updateTime": updateTime, "articles": feed.entries[0:2] }
	return newsList
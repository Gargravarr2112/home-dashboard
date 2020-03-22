import requests, logging

BBC_API = 'https://www.bbc.co.uk/indepthtoolkit/data-sets/coronavirus_lookup/json'

logger = logging.getLogger(__name__)

#Queries the BBC API to determine how many cases are known in Oxfordshire.
#Returns a tuple containing (cases, population)
def lookupOxfordshire():
  logger.info("Checking how real shit is getting")
  try:
    response = requests.get(BBC_API)
    if not response.status_code == 200:
      logger.error("Failed to get statistics from BBC API: HTTP %d", response.status_code)
      return False
    else:
      jsonResponse = response.json()
      for county in jsonResponse: #Structure: [lookup code, name, cases, population]
        if county[1] == 'Oxfordshire':
          lastUpdated = jsonResponse[len(jsonResponse) - 1] #Last entry /should/ be the last-updated time
          if lastUpdated[0] != 'UpdatedOn':
            logger.error("JSON response has changed, last entry does not start UpdatedOn, is instead {0}".format(lastUpdated[0]))
          return (county[2], county[3], lastUpdated[1])
  except Exception as e:
    logger.error("Failed to query BBC API")
    logger.error(e)
    return False
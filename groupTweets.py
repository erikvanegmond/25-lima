import json
import sys

from functions import *



#assuming every folder has the same files in it to save time looking for files.
directory = 'Fixed/Timelines-201408/20140801'
siteList = getSitesFromFiles(getFiles(directory))
siteList = ['telegraaf.nl']
tweetFileTemplate = 'strippedFeatures/Fixed/Timelines-201408/201408%02d/%s.csv'
httpCheckFileTemplate = "HttpCheck/August 2014/201408%02d/HttpCheck-%s.json"

downtimeTweets = []
uptimeTweets = []

for site in siteList:
    logging.info(site)
    for i in range(1,32):
        downtimeFile = httpCheckFileTemplate % (i, site)
        tweetFile = tweetFileTemplate % (i, site)

        logging.debug("201408%02d - %s" % (i, site))
        try:
            downtimeData = pd.read_json(downtimeFile)
            tweetData = pd.read_json(tweetFile)
        except:
            logging.warn("%s or %s cannot be opened" % (downtimeFile, tweetFile))
            continue

        try:
            if len(tweetData) and len(downtimeData):
                downtimeData['timestamp'] = pd.to_datetime(downtimeData['timestamp'], dayfirst=True)
                tweetData['created_at'] = pd.to_datetime(tweetData['created_at'], dayfirst=True)
                tweetData.index = pd.to_datetime(tweetData.pop('created_at'))
                downtimes = downtimeData[downtimeData["IsDown"].isin([True])]['timestamp']

                downtimeRanges = getDowntimeRanges(downtimes, downtimeData)
                uptimeRanges = getUptimeRanges(downtimeRanges, downtimeData)

                for downtimeRange in downtimeRanges:
                    messageList = tweetDataToMessageList(tweetData[downtimeRange[0]:downtimeRange[1]])
                    for message in messageList:
                        if message not in uptimeTweets:
                            downtimeTweets.append(message)

                for uptimeRange in uptimeRanges:
                    messageList = tweetDataToMessageList(tweetData[uptimeRange[0]:uptimeRange[1]])
                    for message in messageList:
                        if message not in uptimeTweets:
                            uptimeTweets.append(message)

        except IndexError as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logging.error("IndexError on line %d,  %s" % (exc_tb.tb_lineno,e))

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logging.error("Something went wrong at %d: %s, %s. Problematic files: %s or %s" % (exc_tb.tb_lineno,exc_type, e, downtimeFile, tweetFile))


with open("downtimeTweets.json", 'w') as f:
    f.write(json.dumps(downtimeTweets, indent=1))

with open("uptimeTweets.json", 'w') as f:
    f.write(json.dumps(uptimeTweets, indent=1))



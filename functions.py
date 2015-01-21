from logger import *
import os, glob, sys
import numpy as np
import pandas as pd
import re
import json
from collections import Counter

PREOFFSET = 1
POSTOFFSET = 2

def getFiles(directory = ".", fileFilter="*"):
    """ Get the files from a folder.

        Default gets all files from the current folder.

        Arguments:
        directory = the directory to get the files from
        fileFilter = a pattern to match the filenames, see default python glob

        Returns a list of all files in the selected folder
    """
    directory += "/" if directory[-1] is not "/" else ""
    files = []
    os.chdir(directory)
    for file in glob.glob(fileFilter):
        files.append(file)
    levels = len(directory.split("/"))-1
    goBack = "../"*levels
    if goBack:
        os.chdir(goBack)
    return files

def getSitesFromFiles(fileList):
    '''
    Returns all the sites that have a file listed in the fileList
    '''
    siteList = []
    for file in fileList:
        site = re.sub(r'(.csv)|(.json)|(HttpCheck-)|(TwitterNerStatus-)', '', file)
        if site not in siteList:
            siteList.append(site)
    return siteList

def getDowntimeRanges(downtimeList, downtimeData):
    downtimeRanges = []
    for (i, downtimeMoment) in downtimeList.iteritems():
        #make sure we have some downtime data to get, if not just do it with minutes.
        if i > len(downtimeData) - PREOFFSET:
            preDowntimeMoment = pd.to_datetime(downtimeData[downtimeData.index == i-PREOFFSET]['timestamp'].values[0], dayfirst=True)
        else:
            preDowntimeMoment = downtimeMoment - np.timedelta64(5, 'm')
        if i < len(downtimeData) - POSTOFFSET:
            postDowntimeMoment = pd.to_datetime(downtimeData[downtimeData.index == i+POSTOFFSET]['timestamp'].values[0], dayfirst=True)
        else:
            postDowntimeMoment = downtimeMoment + np.timedelta64(10, 'm')
        downtimeRanges.append((preDowntimeMoment,postDowntimeMoment))
    return downtimeRanges

def getUptimeRanges(downtimeRanges, downtimeData):
    timestamp = pd.to_datetime(downtimeData[downtimeData.index == 0]['timestamp'].values[0], dayfirst=True)
    startDay = pd.to_datetime(pd.datetime(timestamp.year, timestamp.month, timestamp.day))
    endDay = pd.to_datetime(pd.datetime(timestamp.year, timestamp.month, timestamp.day, 23,59,59))

    uptimeRanges = []
    if len(downtimeRanges):
        for i,downtimeRange in enumerate(downtimeRanges):
            if i is 0:
                uptimeRanges.append((startDay,downtimeRange[0]))
            else:
                uptimeRanges.append((downtimeRanges[i-1][1],downtimeRange[0]))
        uptimeRanges.append((downtimeRanges[-1][1],endDay))
    else:
        uptimeRanges.append((startDay,endDay))

    return uptimeRanges

def tweetDataToMessageList(tweetData):
    messageList = [{'created_at':str(index), 'text':row['text'].encode('ascii', 'ignore')} for index, row in tweetData.iterrows()]
    return messageList

def getNgramsFromString(n, string):
    '''
    Returns ngrams of string in a list format
    '''
    string = re.sub('[^a-zA-Z\d\s@:!?#]','', string).lower()
    words = string.split()
    ngrams=[]
    position = 0
    for i in range(0,len(words)-n+1):
        ngrams.append(" ".join(words[position:position+n]))
        position+=1
    return ngrams

def getNgramsFromMessageList(n, messageList):
    '''
    Return an Ngram dict if a list of messages is entered in this format:
    [
        {
            text:'message1',
            otherFeature:value,
            anotherFeature:anothervalue
        },
        {
            text:'message2',
            otherFeature:value,
            anotherFeature:anothervalue
        },
        ....
    ]

    creates ngrams of size n
    '''

    ngrams = []
    for message in messageList:
        if message:
            ngrams += getNgramsFromString(n, message["text"])

    return ngrams

def getNgramFrequenciesFromFiles(n, fileList):
    ngrams = []
    for inputFile in fileList:
        text = open(inputFile).read()
        messageList = json.loads(text)
        ngrams += getNgramsFromMessageList(n, messageList)

    countDict = Counter(ngrams)
    totalNr = len(ngrams)
    return (countDict, totalNr)

def groupTweets(writeToFile=False):
    #assuming every folder has the same files in it to save time looking for files.
    directory = 'Fixed/Timelines-201408/20140801'
    siteList = getSitesFromFiles(getFiles(directory))
    # siteList = ['telegraaf.nl']
    tweetFileTemplate = 'strippedFeatures/Fixed/Timelines-201408/201408%02d/%s.csv'
    httpCheckFileTemplate = "HttpCheck/August 2014/201408%02d/HttpCheck-%s.json"

    downtimeTweets = []
    uptimeTweets = []

    for site in siteList:
        logging.info(site)
        for i in range(1,32):
            downtimeData = None
            tweetData = None

            downtimeFile = httpCheckFileTemplate % (i, site)
            tweetFile = tweetFileTemplate % (i, site)

            logging.debug("201408%02d - %s" % (i, site))
            try:
                downtimeData = pd.read_json(downtimeFile)
                tweetData = pd.read_json(tweetFile)
            except:
                # logging.warn("%s or %s cannot be opened" % (downtimeFile, tweetFile))
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

    if writeToFile:
        with open("downtimeTweets.json", 'w') as f:
            f.write(json.dumps(downtimeTweets, indent=1))
            logging.info("Saved downtimeTweets in downtimeTweets.json")

        with open("uptimeTweets.json", 'w') as f:
            f.write(json.dumps(uptimeTweets, indent=1))
            logging.info("Saved uptimeTweets in uptimeTweets.json")

    return (downtimeTweets, uptimeTweets)

def fixFiles(directoryTemplate):
    for i in range(1,32):
        try:
            directory = directoryTemplate % (i)
            files = []
            try:
                os.chdir(directory)
                for file in glob.glob("*.csv"):
                    files.append(file)
                os.chdir('../..')


                for myFile in files:
                    inputFile = directory+'/'+myFile
                    text = open(inputFile).read()
                    text = re.sub("\x00", "", text)

                    outDir = 'Fixed/'+directory
                    if not os.path.exists(outDir):
                        os.makedirs(outDir)
                    with open(outDir+'/'+myFile, 'w') as outfile:
                        outfile.write(text)

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logging.warn("Something went wrong at:%d, %s" %( exc_tb.tb_lineno, str(e)))
                break
        except:
            continue


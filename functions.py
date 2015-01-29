"""
    HAL24K data analysis - project Leren & Beslissen
    Timothy Dingeman, Erik van Egmond, Sebastiaan Hoekstra, Jos Wezenberg
    January, 2015 - University of Amsterdam
"""

# Import libraries
from logger import *
from collections import Counter
from datetime import datetime
import os, glob, sys, json, csv, re
import numpy as np
import pandas as pd
import pprint as pp
from nltk.classify import SklearnClassifier
from sklearn.naive_bayes import BernoulliNB
from sklearn.svm import LinearSVC
from sklearn import neighbors
from nltk.corpus import stopwords
import random
import pickle


# Fields describing period (in test period or minutes) of comparison monitoring data and tweets
PREOFFSETPERIOD = 1
POSTOFFSETPERIOD = 4
PREOFFSETMIN = 5
POSTOFFSETMIN = 10

def getFiles(directory = ".", fileFilter="*"):
    """
        Returns a list of all (default) files in the selected folder
        > directory = the directory to get the files from
        > fileFilter = a pattern to match the file names, see default Python glob
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
        Returns a list of all sites that have a file in the fileList
        > fileList: list of files from the Timelines data set
    '''
    siteList = []
    for file in fileList:
        site = re.sub(r'(.csv)|(.json)|(HttpCheck-)|(TwitterNerStatus-)', '', file)
        if site not in siteList:
            siteList.append(site)
    return siteList

def getDowntimeRanges(downtimeList, downtimeData):
    '''
        Returns a list of ranges using the OFFSET fields around downtime events
        Uses an offset period, or minutes when not available
        > downtimeList: the downtime events from a single site found by "isDown" = True
        > downtimeData: all the events from a single site from HttpCheck
    '''
    downtimeRanges = []
    for (i, downtimeMoment) in downtimeList.iteritems():
        if i > len(downtimeData) - PREOFFSETPERIOD:
            preDowntimeMoment = pd.to_datetime(downtimeData[downtimeData.index == i-PREOFFSETPERIOD]['timestamp'].values[0], dayfirst=True)
        else:
            preDowntimeMoment = downtimeMoment - np.timedelta64(PREOFFSETMIN, 'm')
        if i < len(downtimeData) - POSTOFFSETPERIOD:
            postDowntimeMoment = pd.to_datetime(downtimeData[downtimeData.index == i+POSTOFFSETPERIOD]['timestamp'].values[0], dayfirst=True)
        else:
            postDowntimeMoment = downtimeMoment + np.timedelta64(POSTOFFSETMIN, 'm')
        downtimeRanges.append((preDowntimeMoment,postDowntimeMoment))
    return downtimeRanges

def getUptimeRanges(downtimeRanges, downtimeData):
    '''
        Returns a list of uptime ranges, found by comparing the time between downtime ranges
        > downtimeRanges: a list of ranges using the OFFSET fields around downtime events
        > downtimeData: all the events from a single site from HttpCheck
    '''
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
    '''
        Returns a list of tweets in JSON format using only these four features
        > tweetData: list of tweets
    '''
    messageList = [
                    {'created_at':str(index),
                     'text':row['text'].encode('ascii', 'ignore'),
                     'id':row['id'],
                     'user':row['user']['id']
                    } for index, row in tweetData.iterrows()]
    return messageList

def getNgramsFromString(n, string):
    '''
        Returns n-grams of string in a list format
        > n: the length of the n-gram sequence
        > string: sequence of natural language
    '''
    string = re.sub('(\^[A-Z]{2})|([^a-zA-Z\d\s@:!?#])','', string).lower()
    words = string.split()
    ngrams=[]
    position = 0
    for i in range(0,len(words)-n+1):
        ngrams.append(" ".join(words[position:position+n]))
        position+=1
    return ngrams

def getNgramsFromMessageList(n, messageList):
    '''
        Returns an n-gram dictionary
        > n: length of the n-gram sequence
        > messageList: list of tweets in JSON format
    '''
    ngrams = []
    for message in messageList:
        if message:
            ngrams += getNgramsFromString(n, message["text"])
    return ngrams

def getNgramFrequenciesFromFiles(n, fileList):
    '''
        Returns a dictionary with n-gram frequencies and the total number of n-grams
        > n: length of the n-gram sequence
        > fileList: list of files from the Timelines data set
    '''
    ngrams = []
    for inputFile in fileList:
        text = open(inputFile).read()
        messageList = json.loads(text)
        ngrams += getNgramsFromMessageList(n, messageList)
    countDict = Counter(ngrams)
    totalNr = len(ngrams)
    return (countDict, totalNr)

def groupTweets(writeToFile=False):
    '''
        Returns a list of tweets regarding uptime and a list of tweets regarding downtime
        > writeToFile: save to disk (boolean)
    '''
    directory = 'Fixed/Timelines-201408/20140801'
    siteList = getSitesFromFiles(getFiles(directory))
    tweetFileTemplate = 'strippedFeatures/Fixed/Timelines-201408/201408%02d/%s.csv'
    httpCheckFileTemplate = "HttpCheck/August 2014/201408%02d/HttpCheck-%s.json"
    downtimeTweets = []
    uptimeTweets = []

    for site in siteList:
        logging.info("Grouping tweets in %s" % (site))
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
                if i is not 31:
                    logging.debug("%s or %s cannot be opened, this data is not available" % (downtimeFile, tweetFile))
                continue

            try:
                if len(tweetData) and len(downtimeData):
                    downtimeData['timestamp'] = pd.to_datetime(downtimeData['timestamp'], dayfirst=True)
                    tweetData['created_at'] = pd.to_datetime(tweetData['created_at'], dayfirst=True)
                    tweetData.index = pd.to_datetime(tweetData.pop('created_at'))

                    # Pandas does not always properly handle Timestamp indices
                    if not tweetData.index.is_monotonic:
                        tweetData = tweetData.sort()

                    downtimes = downtimeData[downtimeData["IsDown"].isin([True])]['timestamp']

                    downtimeRanges = getDowntimeRanges(downtimes, downtimeData)
                    uptimeRanges = getUptimeRanges(downtimeRanges, downtimeData)

                    previousDowntimeRange = [pd.to_datetime(0),pd.to_datetime(0)]

                    # Find tweets that are in a period of downtime
                    for j, downtimeRange in enumerate(downtimeRanges):                         
                        # Case of overlapping downtime ranges
                        if previousDowntimeRange[1] > downtimeRange[0]:
                            if previousDowntimeRange[1] > downtimeRange[1]:
                                downtimeRange = [previousDowntimeRange[0],previousDowntimeRange[1]]
                                if j is not len(downtimeRanges)-1:
                                    # Increase range and continue with new range
                                    previousDowntimeRange = downtimeRange
                                    continue
                            else:
                                downtimeRange = [previousDowntimeRange[0],downtimeRange[1]]
                                if j is not len(downtimeRanges)-1:
                                    # Increase range and continue with new range
                                    previousDowntimeRange = downtimeRange
                                    continue                     
                        messageList = tweetDataToMessageList(tweetData[downtimeRange[0]:downtimeRange[1]])
                        for message in messageList:
                            if message not in uptimeTweets:
                                downtimeTweets.append(message)
                        previousDowntimeRange = downtimeRange

                    # Find tweets that are in surrounding period (uptime)
                    for uptimeRange in uptimeRanges:
                        if uptimeRange[0] < uptimeRange[1]:
                            temp = tweetData[uptimeRange[0]:uptimeRange[1]]
                            messageList = tweetDataToMessageList(tweetData[uptimeRange[0]:uptimeRange[1]])
                            for message in messageList:
                                if message not in uptimeTweets:
                                    uptimeTweets.append(message)
                        else:
                            # Skip because of overlap
                            continue

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

def fixFiles(directoryTemplate='Timelines-201408/201408%02d'):
    '''
        Repairs the data corruption, removes null characters
        > directoryTemplate: source on disk (default: 'Timelines-201408/201408%02d')
    '''
    for i in range(1,32):
        try:
            directory = directoryTemplate % (i)
            files = []
            os.chdir(directory)
            logging.info("Fixing files in: %s" %(directory))
            try:
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
            # Ignore error when month has less than 31 days
            continue

def stripFeatures(writeToFile=False):
    """
        Creates a new folder with all tweet messages with only relevant features
        > writeToFile = save to disk (boolean)
    """
    directory = 'Fixed/Timelines-201408/20140801'
    files = getFiles(directory)

    for i in range(1,32):
        try:
            directory = 'Fixed/Timelines-201408/201408%02d' % (i)
            logging.info("Stripping features in files in: %s" %(directory))

            for myFile in files:
                inputFile = directory+'/'+myFile
                text = open(inputFile).read()
                # Assuming the JSON is correct, duplicate features will be joined
                messageList = json.loads(text)
                for i, message in enumerate(messageList):
                    message = extractFeatures(message)
                    messageList[i] = message

                outDir = 'strippedFeatures/'+directory
                if not os.path.exists(outDir):
                    os.makedirs(outDir)
                with open(outDir+'/'+myFile, 'w') as f:
                    f.write(json.dumps(messageList, indent=1))

        except IOError as e:
            logging.warn("Skipped the following file (does not exist): %s" % (inputFile))
            continue
        except ValueError as e:
            logging.warn("Skipped the following file (incorrect format): %s" % (inputFile))
            continue
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logging.error("Type: %s \n Line: %s \n Error: %s" % (exc_type,exc_tb.tb_lineno,str(e)))

def extractFeatures(message):
    """
        Returns a tweet with only relevant features
        > message = a single tweet, with all features from Twitter API
    """
    relevantFeaturesList = ["text",
                            "in_reply_to_status_id",
                            "id",
                            "favorite_count",
                            "coordinates",
                            "entities",
                            "retweet_count",
                            "in_reply_to_user_id",
                            "user",
                            "lang",
                            "created_at"]
    relevantUserFeaturesList = ["id",
                            "verified",
                            "followers_count",
                            "listed_count",
                            "statuses_count",
                            "description",
                            "friends_count",
                            "location",
                            "name",
                            "lang",
                            "favourites_count",
                            "screen_name",
                            "url",
                            "created_at",
                            "default_profile"]
    for feature in message.keys():
        if feature not in relevantFeaturesList:
            message.pop(feature, None)
    for userFeature in message['user'].keys():
        if userFeature not in relevantUserFeaturesList:
            message['user'].pop(userFeature, None)
    return message

def relFreq(uptimeFile, downtimeFile, n=1):
    """
        Display frequency statistics of uptime and downtime tweets
        > uptimeFile: the JSON file with all the uptime tweets
        > downtimeFile: the JSON file with all the downtime tweets
        > n: length of the n-gram sequence
    """

    # [n=1] chosen minimal frequency to occur, when lower not interesting
    minCount = 10

    if not(os.path.exists(uptimeFile) and uptimeFile[-5:] ==".json"):
        logging.error("%s is not a valid json file!" % (uptimeFile))
        return
    if not(os.path.exists(downtimeFile) and downtimeFile[-5:] ==".json"):
        logging.error("%s is not a valid json file!" % (downtimeFile))
        return

    (downtimeCountDict, downtimeTotalNr) = getNgramFrequenciesFromFiles(n, [downtimeFile])
    (uptimeCountDict, uptimeTotalNr) = getNgramFrequenciesFromFiles(n, [uptimeFile])

    relativeList = []
    allWords = set(downtimeCountDict.keys()+uptimeCountDict.keys())

    for word in allWords:
        if downtimeCountDict[word] > minCount:
            wordDict = {}
            if word in uptimeCountDict:
                ufreq = uptimeCountDict[word]/float(uptimeTotalNr)
            else:
                ufreq = 0
            if word in downtimeCountDict:
                dfreq = downtimeCountDict[word]/float(downtimeTotalNr)
            else:
                dfreq = 0

            wordDict['ufreq'] = ufreq
            wordDict['uCount'] = uptimeCountDict[word]
            wordDict['dfreq'] = dfreq
            wordDict['dCount'] = downtimeCountDict[word]
            wordDict['relfreq'] = dfreq/ufreq if ufreq else -1

            relativeList.append((word, wordDict))

    relativeList = sorted(relativeList, key=lambda x: x[1]['relfreq'], reverse=True)
    print "Relative frequency\t| Downtime frequency\t| Uptime frequency \t| Word"
    for word in relativeList[:100]:
        print "%f\t\t| %f\t\t| %f\t\t| %s" % (word[1]['relfreq'], word[1]['dfreq'], word[1]['ufreq'], word[0])


def messageListToCSV(messageList, filename):
    """
        Converts a list of tweets to CSV format and saves to disk
        > messageList: list of tweets in JSON format
        > filename: name of the output file (eg "name.csv")
    """
    features = messageList[0].keys()

    outDir = 'CSV/'
    if not os.path.exists(outDir):
        os.makedirs(outDir)

    with open(outDir+'/'+filename, 'w') as f:
        f.write(",".join(features))
        f.write("\n")
        for message in messageList:
            line = ""
            for feature in features:
                line += "\"%s\"," % (message[feature])
            line = line.strip(",")+"\n"
            f.write(line.encode('ascii', 'ignore'))

def csvToJson(csvFile, jsonFile = 'labeledData.json'):
    """
        Converts a CSV file to JSON, converts the time format, writes to disk and returns list tweets
        > csvFile = comma separated input file with header line of column names
    """
    csvfile = open(csvFile, 'r')
    jsonfile = open(jsonFile, 'w')

    r = csv.reader(csvfile)
    features = tuple(r.next())

    reader = csv.DictReader(csvfile, fieldnames=features ,delimiter=',')
    messageList = [ row for row in reader ]

    try:
        for message in messageList:
            message["created_at"] = datetime.strptime(message["created_at"],
            '%d/%m/%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        logging.error("Expected different time format in %s %s " % (csvFile,str(e)))

    out = json.dumps( messageList , indent=1 )
    jsonfile.write(out)

    return messageList

def createHugeTrainSet(messageList):
    """
        Create very large training set, by filling the smaller subset with duplicates
        > messageList: list of tweets in JSON format
    """
    logging.info( "Creating train set" )
    downtime_set = [message for message in messageList if message['downtime']=='1']
    uptime_set = [message for message in messageList if message['downtime']=='0']
    nDowntime = len(downtime_set)
    nUptime = len(uptime_set)

    multiplier = int(nUptime/nDowntime)
    newDowntime_set = downtime_set * multiplier
    train_set = uptime_set + newDowntime_set
    return train_set

def createRandomTrainSet(messageList):
    """
        Create training set by selecting random tweets, no duplicates
        > messageList: list of tweets in JSON format
    """
    logging.info( "Creating train set" )
    train_set = [message for message in messageList if message['downtime']=='1']
    print len(range(0, len(train_set)))
    nMessages = len(messageList)
    for i in range(0, len(train_set)):
        while True:
            randMessage = messageList[random.randrange(nMessages)]
            if randMessage not in train_set:
                train_set.append(randMessage)
                break
    return train_set

def createTrainData(messageList, featureList):
    """
        Create training set using all tweets
        > messageList: list of tweets in JSON format
        > featureList: list of features (for Bayes: the n-grams)
    """
    train_data = []
    for message in messageList:
        text = message['text']
        features = getFeaturesFromText(featureList, text)
        train_data.append((features, message['downtime']))

    return train_data

def createTestData(messageList, featureList):
    """
        Create test set using all tweets
        > messageList: list of tweets in JSON format
        > featureList: list of features (for Bayes: the n-grams)
    """
    test_data = []
    for message in messageList:
        text = message['text']
        features = getFeaturesFromText(featureList, text)
        test_data.append(features)
    return test_data

def getFeaturesFromText(featureList, text):
    """
        Find features in text
        > featureList: list of features (for Bayes: the n-grams)
        > text: sequence of natural language
    """
    sw = stopwords.words('dutch')
    features = {x:0 for x in featureList if len(x)>3 and x not in sw}
    ngrams = getNgramsFromString(1, text)
    for gram in ngrams:
        if gram in features:
            features[gram] += 1
    return features

def splitDataSet(dataset, ratio):
    """
        Find features in text
        > dataset:
        > ratio:
    """
    downtime_set = [message for message in dataset if message['downtime']=='1']
    uptime_set = [message for message in dataset if message['downtime']=='0']

    nDowntimeTrain = int(len(downtime_set)*ratio)
    nDowntimeTest = len(downtime_set)-nDowntimeTrain

    nUptimeTrain = int(len(uptime_set)*ratio)
    nUptimeTest = len(uptime_set)-nUptimeTrain

    train_set = []
    test_set = []

    for i in range(0,nDowntimeTrain):
        randomIndex = random.randrange(len(downtime_set))
        train_set.append(downtime_set[randomIndex])
        del downtime_set[randomIndex]
    test_set = test_set + downtime_set

    for i in range(0,nUptimeTrain):
        randomIndex = random.randrange(len(uptime_set))
        train_set.append(uptime_set[randomIndex])
        del uptime_set[randomIndex]
    test_set = test_set + uptime_set

    return (train_set, test_set)

def getAccuracy(classifResults, test_data):
    """
        Display classifier results
        > classifResults: the labels determined by classifier
        > test_data: the actual labels
    """
    truepos = 0
    falsepos = 0
    trueneg = 0
    falseneg = 0

    for i, result in enumerate(classifResults):
        if result == '1':
            if result == test_data[i]['downtime']:
                truepos += 1
            else:
                falsepos += 1
        if result == '0':
            if result == test_data[i]['downtime']:
                trueneg += 1
            else:
                falseneg += 1
    print "True positive: %d, False positive: %d, True negative: %d, False negative: %d" %(truepos, falsepos, trueneg, falseneg)
    accuracy = (truepos + trueneg)/float(len(classifResults))
    precision = float(truepos)/float(falsepos+truepos) if float(falsepos+truepos) else -1
    recall = float(truepos)/float(falseneg+truepos) if float(falseneg+truepos) else -1
    print "Accuracy: %f, Precision: %f, Recall: %f" % (accuracy, precision, recall)

def classifier(inputFile, pickleLocation=None, classifier="naiveBayes", ratio=0.7, n=1, datasetMethod=0):
    text = open(inputFile).read()
    messageList = json.loads(text)

    if datasetMethod == 0:
        dataset = messageList
    elif datasetMethod == 1:
        dataset = createHugeTrainSet(messageList)
    elif datasetMethod == 2:
        dataset = createRandomTrainSet(messageList)

    logging.info("splitting the dataset into train and test with a ratio of %.1f..." % (ratio))
    (trainset, testset) = splitDataSet(dataset, ratio)

    logging.info("Getting the features from the data set with n=%d..."%(n))
    featureList = getNgramsFromMessageList(n, messageList)

    logging.info("Creating train data...")
    train_data = createTrainData(trainset, featureList)

    test_data = createTestData(testset, featureList)

    logging.info("Creating a classifier using %s..." % (classifier))
    if classifier == "naiveBayes":
        classif = SklearnClassifier(BernoulliNB()).train(train_data)
    elif classifier == "linearSVC":
        classif = SklearnClassifier(LinearSVC()).train(train_data)
    elif classifier == "neighbors":
        classif = SklearnClassifier(neighbors.KNeighborsClassifier()).train(train_data)
    else:
        logging.error("Unknown classifier %s" %(classifier))
        return

    if pickleLocation is not None:
        output = open(pickleLocation, 'wb')
        pickle.dump(classif, output)
        pickle.dump(featureList, output)
        output.close()

    logging.info("Classifying...")
    classifResults = classif.classify_many(test_data)

    getAccuracy(classifResults, testset)

def demo(classifier):
    pkl_file = open(classifier, 'rb')
    classif = pickle.load(pkl_file)
    featureList = pickle.load(pkl_file)
    print "Classifier loaded!"
    while True:
        tweet = raw_input("\nEnter a tweet:\n")
        print "Downtime" if classif.classify(getFeaturesFromText(featureList, tweet))=="1" else "Uptime"





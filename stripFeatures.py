import json
import os, glob, sys
import pprint as pp

from functions import *

def run():
    #assuming every folder has the same files in it to save time looking for files.
    directory = 'Fixed/Timelines-201408/20140801'
    files = getFiles(directory)

    for i in range(1,32):
        try:
            directory = 'Fixed/Timelines-201408/201408%02d' % (i)
            for myFile in files:
                inputFile = directory+'/'+myFile
                text = open(inputFile).read()
                messageList = json.loads(text)
                for i, message in enumerate(messageList):
                    message = extractFeatures(message)
                    messageList[i] = message

                outDir = 'strippedFeatures/'+directory
                if not os.path.exists(outDir):
                    os.makedirs(outDir)
                with open(outDir+'/'+myFile, 'w') as f:
                    f.write(json.dumps(messageList, indent=1))

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type)
            print inputFile
            print(exc_tb.tb_lineno)
            print str(e)+"!"      

def extractFeatures(message):
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
        if userFeature not in relevantFeaturesList:
            message['user'].pop(userFeature, None)

    return message


run()
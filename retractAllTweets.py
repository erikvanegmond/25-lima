import json
import os, glob, sys

from functions import *

removeMessageFeaturesList = ["in_reply_to_status_id","id","favorite_count","coordinates","entities","retweet_count","in_reply_to_user_id","user","lang","timestamp_ms","retweeted_status","extended_entities"]

#assuming every folder has the same files in it to save time looking for files.
directory = 'Fixed/Timelines-201408/20140801'
files = getFiles(directory)

for i in range(1,32):
    try:
        directory = 'strippedFeatures/Fixed/Timelines-201408/201408%02d' % (i)
        outDir = 'onlyText/'
        if not os.path.exists(outDir):
            os.makedirs(outDir)

        for myFile in files:
            inputFile = directory+'/'+myFile
            text = open(inputFile).read()
            messageList = json.loads(text)
            for j, message in enumerate(messageList):
                for feature in removeMessageFeaturesList:
                    message.pop(feature, None)
                if len(message) > 2:
                    messageList.pop(j)

            if i == 1:
                f = open(outDir+'/'+myFile, 'a')
                f.write("[ ")
            if messageList:
                f = open(outDir+'/'+myFile, 'a')
                f.write(json.dumps(messageList)[1:-1])
                if i!=30:
                    f = open(outDir+'/'+myFile, 'a')
                    f.write(", ")
                else:
                    f = open(outDir+'/'+myFile, 'a')
                    f.write(" ]")

    except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type)
            print inputFile
            print(exc_tb.tb_lineno)
            print str(e)+"!"
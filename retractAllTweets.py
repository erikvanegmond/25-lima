import json
import os, glob

os.getcwd()

removeMessageFeaturesList = ["in_reply_to_status_id","id","favorite_count","coordinates","entities","retweet_count","in_reply_to_user_id","user","lang","timestamp_ms","retweeted_status"]

for i in range(1,32):
    try:
        directory = 'strippedFeatures/Fixed/Timelines-201408/201408%02d' % (i)
        files = []
        os.chdir(directory)
        for file in glob.glob("*.csv"):
            files.append(file)
        os.chdir('../../../..')
        
        outDir = 'onlyText/'
        if not os.path.exists(outDir):
            os.makedirs(outDir)

        for myFile in files:
            inputFile = directory+'/'+myFile
            text = open(inputFile).read()
            messageList = json.loads(text)
            for message in messageList:
                for feature in removeMessageFeaturesList:
                    message.pop(feature, None)

            with open(outDir+'/'+myFile, 'a') as f:
                f.write(json.dumps(messageList))

    except Exception as e:
        print e
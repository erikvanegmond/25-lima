import os, glob, sys, json

from functions import *

def run():
    #assuming every folder has the same files in it to save time looking for files.
    directory = 'Fixed/Timelines-201408/20140801'
    files = getFiles(directory)
    
    number_of_days = len([item for item in os.listdir('Fixed/Timelines-201408') if os.path.isdir(os.path.join('Fixed/Timelines-201408', item))])
    
    for i in range(1,number_of_days+1):
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
                    message = extractFeatures(message)
                    messageList[j] = message  

                if i == 1:
                    f = open(outDir+'/'+myFile, 'a')
                    f.write("[ ")
                if messageList:
                    f = open(outDir+'/'+myFile, 'a')
                    f.write(json.dumps(messageList, indent=1)[1:-1])
                    if i!=number_of_days:
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
                
def extractFeatures(message):
    relevantFeaturesList = ["text",
                            "created_at"]
    for feature in message.keys():
        if feature not in relevantFeaturesList:
            message.pop(feature, None)
        if feature is "text":
            message["text"] = message["text"].encode('ascii', 'ignore')
    

    return message

run()                
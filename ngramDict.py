import os, glob, sys, json
from collections import Counter

from functions import *

def run():
    #assuming every folder has the same files in it to save time looking for files.
    directory = 'onlyText/'
    files = getFiles(directory)
    
    n = 1 #unigrams
    ngrams = []
    
    try:         
        for myFile in files:
            inputFile = directory+'/'+myFile
            text = open(inputFile).read()
            messageList = json.loads(text)
            for message in messageList:
                if message:
                    wordArray = message["text"].split()
                    position = 0    
                    for i in range(0,len(wordArray)-n+1):
                        ngrams.append(" ".join(wordArray[position:position+n]))
                        position+=1
                
        countDict = Counter(ngrams)

        for k in countDict.most_common(5):
            print k[0] + ": " + str(k[1])

    except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type)
            print inputFile
            print(exc_tb.tb_lineno)
            print str(e)+"!"

run()                
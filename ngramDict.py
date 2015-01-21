import os, glob, sys, json
from collections import Counter

from functions import *


def run():
    logging.debug("Start")
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
            ngrams += getNgramsFromMessageList(n, messageList)
            # for message in messageList:
            #     if message:
            #         ngrams += getNgrams(n, message["text"])

        countDict = Counter(ngrams)
        totalNr = len(ngrams)

        print "aantal ngrams: " + str(totalNr)
        print "WOORD - FREQ - REL FREQ"
        for k in countDict.most_common(5):
            print k[0] + " - " + str(k[1]) + " - " + str(k[1]/float(totalNr))

    except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type)
            print inputFile
            print(exc_tb.tb_lineno)
            print str(e)+"!"

run()
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 17 17:14:26 2015

@author: WexY
"""

import json
import re
import glob
import os
from functions import *

userFeaturesList = ["id",
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
                   "default_profile"
                   ]


#assuming every folder has the same files in it to save time looking for files.
directory = 'Fixed/Timelines-201408/20140801'
files = getFiles(directory)
users = [] #Init user list

for i in range(1,32): #For loop iterating through 31 days
    try: #exit upon failure to prevent
        directory = 'Fixed/Timelines-201408/201408%02d' % (i)
        print ("iteration")
        outDir = 'userList/'#folder for output
        if not os.path.exists(outDir):  #if the folder doesn't exist
            os.makedirs(outDir)         #create it

        for myFile in files:
            inputFile = directory+'/'+myFile
            text = open(inputFile).read()
            messageList = json.loads(text)
            for message in messageList:
                for feature not in userFeaturesList:
                    message.pop(feature, None)

            with open(outDir+'/'+myFile, 'w') as f:
                f.write(json.dumps(messageList, indent=None))

    except Exception as e:
        print e
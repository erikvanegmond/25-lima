import os, glob
import re
import numpy as np
import pandas as pd

from logger import *

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


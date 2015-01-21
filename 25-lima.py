from functions import *
import argparse
import pprint as pp

def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-all', "--all", action='store_true', default=False,
                    dest='run_all',
                    help='Runs the entire process, from reading the raw data files until a classifier is produced')
    arg_parser.add_argument('-groupTweets', "--groupTweets", action='store_true', default=False,
                    dest='groupTweets',
                    help='Groups the tweets in two seperate sets, uptime and downtime. Writes to file in root folder. CAN TAKE A LONG TIME!')
    arg_parser.add_argument('-relfreq', "--relfreq", action='store_true', default=False,
                    dest='relfreq',
                    help='Calculates the relative frequencies of the uptime- and downtimeTweets, needs the output from groupTweets in -uptime and -downtime.')
    arg_parser.add_argument("-uptime", "--uptime",
                    help="File containing the uptime tweets")
    arg_parser.add_argument("-downtime", "--downtime",
                    help="File containing the downtime tweets")

    args = arg_parser.parse_args()

    if args.run_all:
        fixFiles('Timelines-201408/201408%02d')
        '''
        TODO:
        add other steps
        '''
    elif args.groupTweets:
        groupTweets(True)

    elif args.relfreq:

        if args.uptime is not None and args.downtime is not None:
            relFreq(args.uptime, args.downtime)
        else:
            print "uptime and/or downtime files are missing!"
            exit()


def relFreq(uptimeFile, downtimeFile):
    n = 1
    minCount = 10

    if not(os.path.exists(uptimeFile) and uptimeFile[-5:] ==".json"):
        print "%s is not a valid json file!" % (uptimeFile)
        exit()
    if not(os.path.exists(downtimeFile) and downtimeFile[-5:] ==".json"):
        print "%s is not a valid json file!" % (downtimeFile)
        exit()

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
    pp.pprint( relativeList[:100])




if __name__ == '__main__':
    main()

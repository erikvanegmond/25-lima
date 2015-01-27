"""
    HAL24K data analysis - project Leren & Beslissen
    Timothy Dingeman, Erik van Egmond, Sebastiaan Hoekstra, Jos Wezenberg
    January, 2015 - University of Amsterdam
"""
25
from functions import *
import argparse

def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-prepare', "--prepare", action='store_true', default=False,
                    dest='prepareData',
                    help='prepares the data for classification, reads raw files, strips the features and groups the tweets')
    arg_parser.add_argument('-fixFiles', "--fixFiles", action='store_true', default=False,
                    dest='fixFiles',
                    help='Fix the files, by replacing null values in ASCII.')
    arg_parser.add_argument('-stripFeatures', "--stripFeatures", action='store_true', default=False,
                    dest='stripFeatures',
                    help='Extracts the relevant features from datasets, writes to file in root folder.')
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
    arg_parser.add_argument("-n", "--n",
                    help="n for the Ngrams")

    args = arg_parser.parse_args()

    if args.fixFiles:
        fixFiles('Timelines-201408/201408%02d')
    elif args.groupTweets:
        groupTweets(True)

    elif args.stripFeatures:
        stripFeatures(True)

    elif args.prepareData:
        #fixFiles('Timelines-201408/201408%02d')
        #stripFeatures(True)
        #groupTweets(True)
   
        (uptimeTweets, downtimeTweets)=groupTweets(True)
        print downtimeTweets[0]
        
        #waar komt csv in logger
        messageListToCSV(uptimeTweets,'uptime.csv')
        messageListToCSV(downtimeTweets,'downtime.csv')

    elif args.relfreq:

        if args.uptime is not None and args.downtime is not None:
            if args.n:
                if args.n.isdigit():
                    relFreq(args.uptime, args.downtime, int(args.n))
                else:
                    print "%s entered for -n is not a number while it should" % (args.n)
                    exit()
            else:
                relFreq(args.uptime, args.downtime)
        else:
            print "uptime and/or downtime files are missing!"
            exit()

if __name__ == '__main__':
    main()

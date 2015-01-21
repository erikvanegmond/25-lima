from functions import *
import argparse

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
        n = 1
        if args.uptime is not None and args.downtime is not None:
            if not(os.path.exists(args.uptime) and args.uptime[-5:] ==".json"):
                print "%s is not a valid json file!" % (args.uptime)
                exit()
            if not(os.path.exists(args.downtime) and args.downtime[-5:] ==".json"):
                print "%s is not a valid json file!" % (args.downtime)
                exit()

            (downtimeCountDict, downtimeTotalNr) = getNgramFrequenciesFromFiles(n, [args.downtime])
            (uptimeCountDict, uptimeTotalNr) = getNgramFrequenciesFromFiles(n, [args.uptime])

            for k in downtimeCountDict.most_common():
                ufreq = uptimeCountDict[k[0]]/float(uptimeTotalNr)
                dfreq = k[1]/float(downtimeTotalNr)

                if dfreq and ufreq and dfreq/ufreq > 1.2:
                    print "Uptime: %f,\tDowntime:%f \t| %f \t|%s" % (ufreq, dfreq, dfreq/ufreq, k[0])


        else:
            print "uptime and/or downtime files are missing!"
            exit()







if __name__ == '__main__':
    main()

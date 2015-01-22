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
    arg_parser.add_argument("-n", "--n",
                    help="n for the Ngrams")

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

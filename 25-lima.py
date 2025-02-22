import argparse
import sys
from functions import *


class Lima(object):

    def __init__(self):
        parser = argparse.ArgumentParser(
            prog="25-lima",
            usage="""25-lima <command> [<args>]

prepare     prepares the data for classification, reads raw files, strips the features and groups the tweets
train       Train a naive bayes classifier on a data file
subModule   Run a subModule from 25-lima:
    --relfreq
    --fixFiles
    --stripFeatures
    --groupTweets
    --csvToJson
            """,
            epilog="""HAL24K data analysis - project Leren & Beslissen
Timothy Dingeman, Erik van Egmond, Sebastiaan Hoekstra, Jos Wezenberg
January, 2015 - University of Amsterdam
""")
        parser.add_argument('command', help='Subcommand to run')
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print 'Unrecognized command'
            parser.print_help()
            exit(1)
        getattr(self, args.command)()

    def prepare(self):
        print "Fixing files in Timelines-201408..."
        fixFiles('Timelines-201408/201408%02d')
        print "Stripping features..."
        stripFeatures(True)
        print "Grouping tweets..."
        (uptimeTweets, downtimeTweets)=groupTweets(True)

        #waar komt csv in logger
        messageListToCSV(uptimeTweets,'uptime.csv')
        messageListToCSV(downtimeTweets,'downtime.csv')

        print "Done!\n\nThe downtime tweets are saved in downtime.csv and the uptime tweets in uptime.csv.\nYou can now use a program like excel to label the tweets.\n\t-Add a column downtime to the data\n\t-Label downtime tweets with 1 and all other tweets with 0\n\t-Save your work as csv\n\nRun the program again to train on the labeled data.\n\t-25-lima.py train [<labeled-data.csv>] [<labeled-data-output.json>]\n\t-For more info: 25-lima.py train --help"

    def train(self):
        parser = argparse.ArgumentParser(
            description='Run the trainer')
        parser.add_argument('input',
                    help='The file that contains the classified data in csv format')
        parser.add_argument('output',
                    help='The file will be created in json format')
        parser.add_argument('--saveClassifier',
                    help='The classifier will be pickled in this file')
        parser.add_argument('--classifier', default='naiveBayes', choices=['naiveBayes', 'linearSVC', 'neighbors'],
                    help='The classifier that will be used, default=naiveBayes')
        parser.add_argument('--ratio', default=0.7, type=float,
                    help='The ratio used for splitting the data set in a train and test set, default=0.7')
        parser.add_argument('--n', default=1, type=int,
                    help='The n used for ngram features, default n=1')

        args = parser.parse_args(sys.argv[2:])

        csvToJson(args.input, args.output)
        if args.saveClassifier:
            classifier(args.output, args.saveClassifier, args.classifier, args.ratio, args.n)
        else:
            save = "%s-%.1f-%d.pkl" % (args.classifier, args.ratio, args.n)
            classifier(args.output, save, args.classifier, args.ratio, args.n)

    def demo(self):
        parser = argparse.ArgumentParser(
            description='Run the demo')
        parser.add_argument('classifier',
                    help='The file that contains the pickled classifier')

        args = parser.parse_args(sys.argv[2:])

        demo(args.classifier)


    def subModule(self):
        parser = argparse.ArgumentParser(
            prog="25-Lima Submodules",
            description='Run a 25-Lima submodule')

        parser.add_argument('-relfreq', "--relfreq", action='store_true', default=False,
                    dest='relfreq',
                    help='Calculates the relative frequencies of the uptime- and downtimeTweets, needs the output from groupTweets in -uptime and -downtime.')
        parser.add_argument('-fixFiles', "--fixFiles", action='store_true', default=False,
                    dest='fixFiles',
                    help='Fix the files, by replacing null values in ASCII.')
        parser.add_argument('-stripFeatures', "--stripFeatures", action='store_true', default=False,
                    dest='stripFeatures',
                    help='Extracts the relevant features from datasets, writes to file in root folder.')
        parser.add_argument('-groupTweets', "--groupTweets", action='store_true', default=False,
                    dest='groupTweets',
                    help='Groups the tweets in two seperate sets, uptime and downtime. Writes to file in root folder. CAN TAKE A LONG TIME!')
        parser.add_argument('-csvToJson', '--csvToJson', help="file to convert to json")



        if "--help" in sys.argv[3:] or "-h" in sys.argv[3:]:
            newArgs = filter(lambda a: a != '-h' and a != '--help', sys.argv[2:])
            args = parser.parse_args(newArgs)
        elif '--relfreq' in sys.argv[2:]:
            args = parser.parse_args(sys.argv[2:3])
        else:
            args = parser.parse_args(sys.argv[2:])


        if args.relfreq:
            relfreq_parser = argparse.ArgumentParser(
                description='Run relative frequencies')
            relfreq_parser.add_argument("uptime",
                        help="File containing the uptime tweets")
            relfreq_parser.add_argument("downtime",
                        help="File containing the downtime tweets")
            relfreq_parser.add_argument("-n", "--n", type=int,
                        help="n for the Ngrams")
            relfreq_args = relfreq_parser.parse_args(sys.argv[3:])
            if relfreq_args.n:
                relFreq(relfreq_args.uptime, relfreq_args.downtime, int(relfreq_args.n))
            else:
                relFreq(relfreq_args.uptime, relfreq_args.downtime)
        elif args.fixFiles:
            fixFiles('Timelines-201408/201408%02d')
        elif args.stripFeatures:
            stripFeatures(True)
        elif args.groupTweets:
            groupTweets(True)
        elif args.csvToJson:
            csvToJson(args.csvToJson)



if __name__ == '__main__':
    Lima()
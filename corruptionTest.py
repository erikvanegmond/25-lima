import json
import glob
import os
#json_data=open('20140801/3fm.nl.csv')

successCounter = 0
failCounter = 0
for i in range(1,32):
    try:
        directory = '201408%02d' % (i)
        files = []
        try:
            os.chdir(directory)
            for file in glob.glob("*.csv"):
                files.append(file)
            os.chdir('..')

        except Exception as e:
            print e

        for myFile in files:
            inputFile = directory+'/'+myFile
            lines = open(inputFile).read().split('\n')

            for line in lines:
                if len(line.strip())>10:
                    try:
                        data = json.loads(line.strip(','))
                        successCounter += 1
                    except Exception as e:
                        failCounter += 1
    except:
        continue

print "%d fails, %d success" % (failCounter, successCounter)
print failCounter/float(successCounter)
import json
import re
import glob
import os

for i in range(1,2):
    try:
        directory = 'HttpCheck/August 2014/201408%02d' % (i)
        files = []
        try:
            os.chdir(directory)
            for file in glob.glob("*.json"):
                files.append(file)
            os.chdir('../../..')


            for myFile in files:
                inputFile = directory+'/'+myFile
                lines = open(inputFile).read().split('\n')
                for line in lines:
                    if len(line.strip())>10:
                        try:
                            data = json.loads(line.strip(','))
                            if data["IsDown"]==True:
                                print data["ServiceEndpointUrl"]
                                break
                        except Exception as e:
                            continue

        except Exception as e:
            print e
            break

    except Exception as e:
        print e
        continue
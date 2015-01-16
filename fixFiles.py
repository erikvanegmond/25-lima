import json
import re
import glob
import os

for i in range(1,32):
    try:
        directory = 'Timelines-201408/201408%02d' % (i)
        files = []
        try:
            os.chdir(directory)
            for file in glob.glob("*.csv"):
                files.append(file)
            os.chdir('../..')


            for myFile in files:
                inputFile = directory+'/'+myFile
                text = open(inputFile).read()
                text = re.sub("\x00", "", text)

                outDir = 'Fixed/'+directory
                if not os.path.exists(outDir):
                    os.makedirs(outDir)
                with open(outDir+'/'+myFile, 'w') as outfile:
                    outfile.write(text)

        except Exception as e:
            print e
            break

    except:
        continue
import json

inputFile = '20140801/3fm.nl.csv'

lines = open(inputFile).read().split('\n')

feature = 'source'

for line in lines:
    if len(line.strip())>10:
        try:
            data = json.loads(line.strip(','))
            print data[feature]
            # for key in data.keys():
            #     try:
            #         print "%s: %s\n" % (key.encode('ascii', 'ignore'), str(data[key]).decode('utf-8').encode('ascii', 'ignore'))
            #     except Exception as e:
            #         print e
        except Exception as e:
            print e
            continue
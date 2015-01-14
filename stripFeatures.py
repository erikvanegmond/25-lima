import json
import os, glob

os.getcwd()
removeMessageFeaturesList = ["contributors","truncated","source","retweeted","in_reply_to_screen_name","id_str","favorited","geo","in_reply_to_user_id_str","possibly_sensitive","filter_level","in_reply_to_status_id_str","place"]
removeUserFeaturesList = ["profile_background_color","profile_background_image_url_https","utc_offset","profile_link_color","profile_image_url","following","geo_enabled","profile_banner_url","profile_background_image_url","profile_background_tile","notifications","contributors_enabled","time_zone","protected","is_translator"]
for i in range(1,32):
    try:
        directory = 'Fixed/Timelines-201408/201408%02d' % (i)
        files = []
        os.chdir(directory)
        for file in glob.glob("*.csv"):
            files.append(file)
        os.chdir('../../..')

        for myFile in files:
            inputFile = directory+'/'+myFile
            text = open(inputFile).read()
            messageList = json.loads(text)
            for message in messageList:
                for feature in removeMessageFeaturesList:
                    message.pop(feature, None)
                for feature in removeUserFeaturesList:
                    message['user'].pop(feature, None)

            outDir = 'strippedFeatures/'+directory
            if not os.path.exists(outDir):
                os.makedirs(outDir)
            with open(outDir+'/'+myFile, 'w') as f:
                f.write(json.dumps(messageList))

    except Exception as e:
        print e
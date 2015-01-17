import json
import os, glob, sys
import pprint as pp

from functions import *



def run():
    #assuming every folder has the same files in it to save time looking for files.
    directory = 'Fixed/Timelines-201408/20140801'
    files = getFiles(directory)

    for i in range(1,31):
        try:
            directory = 'Fixed/Timelines-201408/201408%02d' % (i)
            for myFile in files:
                inputFile = directory+'/'+myFile
                text = open(inputFile).read()
                messageList = json.loads(text)
                for i, message in enumerate(messageList):
                    message = removeFeatures(message)
                    messageList[i] = message

                outDir = 'strippedFeatures/'+directory
                if not os.path.exists(outDir):
                    os.makedirs(outDir)
                with open(outDir+'/'+myFile, 'w') as f:
                    f.write(json.dumps(messageList, indent=None))

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type)
            print inputFile
            print(exc_tb.tb_lineno)
            print str(e)+"!"

def removeFeatures(message):
    removeMessageFeaturesList = ["contributors",
                                 "truncated",
                                 "source",
                                 "retweeted",
                                 "in_reply_to_screen_name",
                                 "id_str",
                                 "favorited",
                                 "geo",
                                 "in_reply_to_user_id_str",
                                 "possibly_sensitive",
                                 "filter_level",
                                 "in_reply_to_status_id_str",
                                 "extended_entities",
                                 "place"]
    removeUserFeaturesList = ["profile_background_color",
                              "profile_background_image_url_https",
                              "default_profile",
                              "default_profile_image",
                              "follow_request_sent",
                              "utc_offset",
                              "profile_link_color",
                              "profile_image_url",
                              "following",
                              "id_str",
                              "geo_enabled",
                              "profile_image_url_https",
                              "profile_sidebar_border_color",
                              "profile_sidebar_fill_color",
                              "profile_text_color",
                              "profile_use_background_image",
                              "profile_banner_url",
                              "profile_background_image_url",
                              "profile_background_tile",
                              "notifications",
                              "contributors_enabled",
                              "time_zone",
                              "protected",
                              "is_translator"]
    for feature in removeMessageFeaturesList:
        if feature in message:
            message.pop(feature, None)
    if 'user' in message:
        for feature in removeUserFeaturesList:
            if feature in message['user']:
                message['user'].pop(feature, None)
    if "retweeted_status" in message:
        message["retweeted_status"] = removeFeatures(message["retweeted_status"])

    return message


run()
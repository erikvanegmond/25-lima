import os, glob
import re

def getFiles(directory = ".", fileFilter="*"):
    """ Get the files from a folder.

        Default gets all files from the current folder.

        Arguments:
        directory = the directory to get the files from
        fileFilter = a pattern to match the filenames, see default python glob

        Returns a list of all files in the selected folder
    """
    directory += "/" if directory[-1] is not "/" else ""
    files = []
    os.chdir(directory)
    for file in glob.glob(fileFilter):
        files.append(file)
    levels = len(directory.split("/"))-1
    goBack = "../"*levels
    if goBack:
        os.chdir(goBack)
    return files


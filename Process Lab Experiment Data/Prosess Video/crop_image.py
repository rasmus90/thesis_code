"""
Title:  Crop Image
Author: RNT
Date:   01.12.17
About:  Crops image in order to reduce computational time.
"""

import PIL.Image
import glob
import os
from IPython import embed

from folder_path import path_

path = path_.path+"Video/"

os.chdir(path)
files = []
for file in glob.glob("00*"):
    files.append(file)
files.sort()


def crop_image(_file):
    embed()
    img = PIL.Image.open(_file)
    # only include path of slider, remove rest of image.
    img2 = img.crop((0, 360, 1090, 410))
    img2.save("crop"+_file)


for _file in files:
    crop_image(_file)

"""
Title:  Crop Image
Author: RNT
Date:   01.12.17
About:  Crops image and makes black and white image

"""
import numpy as np
import PIL.Image
import matplotlib.pyplot as plt
import glob
import os
from IPython import embed

from folder_path import path_

path = "/media/rasmus/SAMSUNG/Velocity (Cam) Data/2018/0102glass01_pmma_tape_psd/120_1/Video/"
path = path_.path+"Video/"

os.chdir(path)
files = []
for file in glob.glob("00*"):
    files.append(file)
files.sort()


def crop_image(_file):
    embed()
    img = PIL.Image.open(_file)
    img2 = img.crop((0, 360, 1090, 410))


    # gray = img2.convert('L')
    # bw = gray.point(lambda x: 0 if x < 150 else 255, '1')
    # ind = np.where(bw)
    # img2 = np.asarray(img2)
    # img2.setflags(write=1)
    # img2[:, :] = 0
    # img2[ind] = 255
    # img2 = PIL.Image.fromarray(img2, 'RGB')
    img2.save("crop"+_file)


for _file in files[100:101]:
    crop_image(_file)

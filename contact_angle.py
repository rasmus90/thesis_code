"""
Title:      Calculate Contact Angle
Date:       23.03
Author:     RNT
"""

import numpy as np
import matplotlib.pyplot as plt
import PIL.Image
import glob
import os
from IPython import embed
from scipy import signal

path = "/home/rasmus/master/Experiment Lab/Drop - Wettability/Images/"

os.chdir(path)
files = []
for file in glob.glob("one*"):
    files.append(file)
files.sort()

scharr = np.array([[- 3 - 3j, 0 - 10j,  + 3 - 3j],
                  [- 10 + 0j, 0 + 0j, +10 + 0j],
                  [- 3 + 3j, 0+10j,  + 3 + 3j]])  # Gx + j*Gy


def crop_image(_file):
    img = PIL.Image.open(_file)
    img_crop = img.crop((2680, 2260, 2870, 2370))
    img_crop.save("crop"+_file)
    black_and_white = img_crop.convert('L')
    imd = np.asarray(black_and_white)
    # compute gradient
    grad = signal.convolve2d(imd, scharr, boundary='symm', mode='same')
    abs_grad = np.absolute(grad)
    #plt.imshow(abs_grad)
    #plt.show()

    abs_grad = abs_grad[:, 10:]
    for column in abs_grad.T:
        if column.max() > 160:
            column[np.where(column > 200)[0][0]] = 2000

    for column in abs_grad[:88]:
        if column[:90].max() > 160:
            column[np.where(column > 160)[0][0]] = 2000

    plt.imshow(abs_grad)
    plt.title("Detect shape of drop.")
    plt.show()
    #embed()

    angle_measurement(abs_grad)


def angle_measurement(img):
    im2 = img[32:, :58]
    #plt.imshow(im2)
    #plt.show()

    y, x = np.where(im2 == 2000)
    y = - y[::-1]
    x = x[::-1]
    z = np.polyfit(x, y, 5)
    f = np.poly1d(z)
    xnew = np.linspace(6, 50, 45)
    ynew = f(xnew)

    plt.plot(xnew, ynew)
    plt.plot(x, y)
    plt.axis([0, 60, -70, 0])
    plt.show()

    embed()


for _file in files:
    crop_image(_file)

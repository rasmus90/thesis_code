"""
Tite:   Load Cell Calibration and Testing in Canal
Author: Rasmus
Date:   30.11
About:  Test load cell with load and use the calibration to check
        values in the canal.


"""

import numpy as np
import matplotlib.pyplot as plt
import glob
import os
from IPython import embed
from processing import select_valid_range as select_range
from processing import process_valid_range as process
from processing import extract_data as extract

# Load Cell Calibration with different loads

_plot = False

calibration = False
psd = False
show = True
save = False

slider_load = 0.535 * 9.81  # normal load
motor_power = 40
counter = 0

# choose path of files
path = "/home/rasmus/master/Experiment Lab/Load Cell Data/2018/Mars/2203_glass_pehd_soap/40/"

# Calibration data (must perform test before each test sequence)
loads = np.array([0.0, 107.3, 157.3, 197.3]) * 9.81 / 1000.
adc_raw = np.array([275.0, 624.7, 785.1, 898.2])

z = np.polyfit(adc_raw, loads,  3)
p = np.poly1d(z)

# make titles for plotting
titles = []
for _ in range(20):
    titles.append("Measured pull. PMMA sliding on a wetted glass plate. Run "+str(_+1)+".")


if _plot:
    x = np.linspace(274, 1000, 1000)
    y = p(x)
    plt.plot(x, y)
    plt.plot(adc_raw, loads, 'ro')
    plt.xlabel('ADC-value')
    plt.ylabel('Load (g)')
    plt.show()

# Declare path and put files in a list, sort them by their name.

os.chdir(path)
files = []
for file in glob.glob("F0*"):
    files.append(file)
files.sort()


def process_file(name, title_, i):

    extraction_new = extract.Extract_Data_New(name, title_, p)
    time, load_val, raw_data = extraction_new.check_file()

    if calibration:
        data = raw_data
    else:
        data = load_val

    if calibration:
        valid_range = select_range.select_valid_range(time, data, calibration)
    else:
        #valid_range = [2000, 12000]
        valid_range = select_range.select_valid_range(time, data, calibration)

    processing = process.Process_Valid_Range(valid_range, time, data, title_)

    if psd:
        f, sxx = processing.welch()
        return f, sxx

    mean_ = processing.get_mean()
    std = processing.get_std()
    if calibration:
        print mean_, std

    if not calibration:
        mu = processing.get_mu(slider_load)
        print "{} & {} &  {} & {} &  {}".format(i+counter, motor_power, mean_, std, mu)
        #processing.plot_valid_range(True, save, name+".png")
        #processing.save_valid_range('v40_', 'l510_', '1')

    processing.measurement_section()
    return 0, 0


f_list = []
sxx_list = []

if psd:
    for i, _file in enumerate(files):
            f, sxx = process_file(_file, titles[i], i+1)
            f_list.append(f)
            sxx_list.append(sxx)


    f_arr = np.asarray(f_list)
    sxx_arr = np.asarray(sxx_list)
    np.save("f_arr.npy", f_arr)
    np.save("sxx_arr.npy", sxx_arr)
else:
    for i, _file in enumerate(files[3:4]):
            process_file(_file, titles[i], i+1)

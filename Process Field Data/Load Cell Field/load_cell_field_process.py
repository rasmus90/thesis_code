"""
Title:  Process Load Cell Data from Field
Author: Rasmus
Date:   01.03.18
"""

import numpy as np
import matplotlib.pyplot as plt
import glob
import os
from IPython import embed
from processing import select_valid_range as select_range
from processing import process_valid_range as process
from processing import extract_data as extract


path = "/home/rasmus/master/Field Experiment/Experiments/Mars/15.03/Load Cell Data/"
#path = "/home/rasmus/master/Field Experiment/Experiments/February/28.02/Load Cell Data/Cold 1200 10"
calibration = False
show = True
save = False
slider_load = 73.75
counter = 0
motor_power = 1300

# Calibration Data
loads = np.array([0.0, 2.5, 7.5, 15.0, 20.0])
voltage = np.array([0.0, 0.672, 1.924, 3.783, 4.99])
adc_value = np.asarray([(1023.0 / 5) * v for v in voltage])

z = np.polyfit(adc_value, loads,  3)
p = np.poly1d(z)

# Declare path and put files in a list, sort them by their name.
os.chdir(path)
files = []
for file in glob.glob("F0*"):
    files.append(file)
files.sort()

# Make titles
titles = []
for _ in range(len(files)):
    titles.append("Measured pull. Run "+str(_ + 1)+".")


def process_file(name, title_, i):
    extraction_new = extract.Extract_Data_New(name, title_, p)

    # extraction = extract.Extract_Data(name, title_, p)
    # time, load_val, raw_data = extraction.check_file()
    time, load_val, raw_data = extraction_new.check_file()

    if calibration:
        data = raw_data
    else:
        data = load_val

    if calibration:
        valid_range = select_range.select_valid_range(time, data, calibration)
    else:
        #valid_range = [29*10**3, 34*10**3]
        #valid_range = [0,25300]
        valid_range = select_range.select_valid_range(time, data, calibration)

    processing = process.Process_Valid_Range(valid_range, time, data, title_)
    mean_ = processing.get_mean()
    std = processing.get_std()
    if calibration:
        print mean_, std

    if not calibration:
        mu = processing.get_mu(slider_load)
        if mu > 0.04:
            print "{}. Non-valid run.".format(i+counter)
        else:
            print "{} & {} & {} & {} &  {} & {}".format(i+counter, motor_power, mean_, std, mu, processing.time[-1]/1000)

        #processing.save_to_np("/home/rasmus/master/Field Experiment/Experiments/April/10.04/Compare Data/Run " + str(i+counter) + "/")
        #processing.measurement_section()
        #processing.plot_valid_range(show, save, name+".png")
        # processing.save_valid_range('v40_', 'l510_', '1')

    #processing.measurement_section()
    #print "Duration (sec): ", processing.time[-1]/1000.
    #processing.error_bar()
    return 0, 0


start = 0
stop = 9
for i, _file in enumerate(files[start:stop]):
    #print _file
    process_file(_file, titles[i], i + start + 1)

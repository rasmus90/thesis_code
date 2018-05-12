"""
Title:  Check thermistors for 1403
Date:   01.03.18
Author: RNT
"""

from processing_thermistors import thermistors_read_file as therm
import glob
import os
import numpy as np
from IPython import embed
import matplotlib.pyplot as plt


path = "/home/rasmus/master/Field Experiment/Experiments/Mars/14.03/Thermistor Data/"

os.chdir(path)
files = []
for file in glob.glob("F0*"):
    files.append(file)
files.sort()


def run_through_files():
    print len(files)
    counter = 4
    stop = 8
    max_temp_array = []
    for i, file_name in enumerate(files[counter:stop]):

        ex = therm.Extract_Data(file_name, "cold", True)
        counter += 1

        print counter, file_name, len(ex.time)/10
        ex.plot_temp("Relative change in temperature. Date: 14.03. \n Velocity = 8 km/h. Run nr. "+str(counter), None)
        #if counter == 8:
        #    ex.save_to_np("/home/rasmus/master/Field Experiment/Experiments/Mars/27.03/Compare Data/Run " + str(counter) + "/")
        # ex.plot_temp("Temperature under left ski. 40 kg. Motor power 1200. 4 runs.", None)
        max_temp_array.append(ex.get_max_delta_t())
    max_temp = np.asarray(max_temp_array)
    m = np.transpose(max_temp)

    counter = 1
    for i in np.transpose(max_temp):
        #print i
        print "T"+str(counter), round(i.mean(), 2), round(np.std(i, ddof=1), 3)
        counter += 1


if __name__ == "__main__":
    # compare_plots()
    # relative_temp_example_plot()
    run_through_files()

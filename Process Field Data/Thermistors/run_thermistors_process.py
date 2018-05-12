"""
Title:  Run Thermistor Post-Processing
Date:   01.03.18
Author: RNT
"""

from processing_thermistors import thermistors_read_file as therm
import glob
import os
import numpy as np
from IPython import embed
import matplotlib.pyplot as plt


path = "/home/rasmus/master/Field Experiment/Experiments/Mars/16.03/Thermistor Data/"

#path = "/home/rasmus/master/Field Experiment/Temperature Data and Equipment/Test Data - 7 thermistors/Zero Degrees Calibration 2/"
#path = "/home/rasmus/master/Field Experiment/Experiments/Mars/27.03/Thermistor Data/Wet"
#path = "/home/rasmus/master/Field Experiment/Experiments/April/10.04/Thermistor Data/"
#path = "/home/rasmus/master/Field Experiment/Temperature Data and Equipment/Test Data 15.03/Outside field/"

os.chdir(path)
files = []
for file in glob.glob("F0*"):
    files.append(file)
files.sort()


def run_through_files():
    print len(files)
    counter = 15
    stop = 17
    max_temp_array = []
    for i, file_name in enumerate(files[counter:stop]):

        ex = therm.Extract_Data(file_name, "cold", True)
        counter += 1

        print counter, file_name, len(ex.time)/10
        #ex.plot_temp("Temperature test of thermistors in field. Date: 16.03. \n Velocity = 8 km/h. Run nr. "+str(counter), None)
        ex.plot_temp("Relative change in temperature. Cold Grind. \n Date: 16.03.", None)
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

def compare_plots():
    temp_array = [therm.Extract_Data(f) for f in files[4:7]]
    titles = ["8 km/h", "2 km/h", "14 km/h"]
    for t, i in zip(temp_array, titles):
        time_array = np.arange(0, (t.time[-1] - t.time[0])/1000. + 0.1, 0.1)
        sg = t.savitzky_golay(t.t2, 101, 5)
        plt.plot(time_array, sg, label=i)

    plt.axis([0, 50, -3, 0])
    plt.legend(loc='upper right', shadow=True, fontsize='large')
    plt.xlabel("Time (seconds)")
    plt.ylabel("Temperature (celsius)")
    plt.title("Temperature profile of runs with differents velocities.")
    plt.show()


def relative_temp_example_plot():
    """
    Make plot showing how Delta T Max is determined
    """
    ex = therm.Extract_Data("F00642", "cold", True)
    t = ex.temp[1]
    t = t[1:]

    time = np.arange(0, len(t)/10., 0.1)
    plt.plot(time, t, 'r')
    plt.xlabel("Time (seconds)")
    plt.ylabel("Temperature ($^o$C)")
    plt.title("Temperture profile under a sliding ski (starting from rest).")
    plt.text(1.8, -5.0, r'$\Delta T_{max}$',
         fontsize=20)
    plt.axhline(y=t.max(), linestyle='--')
    plt.axhline(y=t[:4].min(), linestyle="--")
    plt.annotate('$T_0$', xy=(10, t[:4].min()), xytext=(12, -7),
            arrowprops=dict(arrowstyle='<->'))

    plt.annotate(s='', xy=(1.5,t[:4].min()), xytext=(1.5,t.max()), arrowprops=dict(arrowstyle='->'))
    plt.show()
    #embed()


if __name__ == "__main__":
    # compare_plots()
    # relative_temp_example_plot()
    run_through_files()

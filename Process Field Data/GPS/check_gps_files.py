"""
Title:  Process GPS Files
Date:   01.03.18
Author: Rasmus Nes Tjoerstad
"""

from processing_gps import GPS_Read_Files as gps
import glob
import os
import matplotlib.pyplot as plt
from IPython import embed

path = "/home/rasmus/master/Field Experiment/Experiments/Mars/07.03/GPS Data/"
path = "/home/rasmus/master/Field Experiment/Experiments/April/10.04/GPS Data/"
os.chdir(path)
files = []
for file in glob.glob("G0*"):
    files.append(file)
files.sort()


def process_files():
    run = 0
    counter = 34
    stop = 35
    for i, name in enumerate(files[counter:stop]):
        counter += 1
        process_file = gps.FileHandler(name, counter)
        run = counter
        #print run, name, len(process_file.time), process_file.get_start_time()
        #process_file.track_distance()
        print run, process_file.get_elevatation_stats(), process_file.track_distance()
        process_file.displacement()
        #process_file.plot_both_velocities("Velocity data. Run nr. "+str(i+1))
        #process_file.plot_velocity("Velocity data 16.03. Run number "+str(run)+".")

        #process_file.save_to_np("/home/rasmus/master/Field Experiment/Experiments/April/10.04/Compare Data/Run " + str(run) + "/")
        #process_file.make_html_map("run"+str(i))

        #plt.show()

    #process_file.plot_for_thesis()





if __name__ == "__main__":
    process_files()

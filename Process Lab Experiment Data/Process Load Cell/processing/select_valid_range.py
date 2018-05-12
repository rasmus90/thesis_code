"""
About:  Select valid range for load cell data
Date:   01.12.17
"""
import os
import fnmatch
import numpy as np
import matplotlib.pyplot as plt


# %matplotlib inline

#################################################################################
# all functions ----------------------------------------------------------------


class generateDataOnClick:
    def __init__(self, verbose=0):
        self.position_on_click_accumulator = []
        self.verbose = verbose

    def position_on_click(self, event):
        x, y = event.x, event.y
        if event.button == 1:
            if event.inaxes is not None:
                if self.verbose > 0:
                    print 'data coords:' + str(event.xdata) + " , " + str(event.ydata)
                self.position_on_click_accumulator.append((event.xdata, event.ydata))
                plt.axvline(event.xdata, color='r')
                plt.show()

    def return_positions(self):
        return self.position_on_click_accumulator


def select_valid_range(time, load_val, calibration):

    plt.figure()
    plt.plot(time, load_val, label='Measured pull, $F_P$ (raw data).')
    plt.xlabel('Time (seconds)', fontsize=12)
    if calibration:
        ylabel = 'ADC value'
    else:
        ylabel = 'Pull force $F_P$ (N)'
    plt.ylabel(ylabel, fontsize=15)
    plt.title("Measured pull. PEHD sliding on wetted glass plate.")
    plt.legend(loc=0, fontsize=12)

    generate_data_on_click_object = generateDataOnClick()

    plt.connect('button_press_event', generate_data_on_click_object.position_on_click)
    plt.show()

    selected_positions_pixels = generate_data_on_click_object.return_positions()

    x_position_1 = int(np.floor(selected_positions_pixels[0][0]))
    x_position_2 = int(np.floor(selected_positions_pixels[1][0]))

    data_valid_range = np.array([x_position_1, x_position_2])
    #print data_valid_range
    return data_valid_range

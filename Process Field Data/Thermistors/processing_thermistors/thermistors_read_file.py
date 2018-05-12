"""
Title:      Extract and Process Thermistor Data
Date:       03.01.18
Author:     RNT
"""

import numpy as np
import matplotlib.pyplot as plt
from IPython import embed
import steinhart_hart_equation as shh
from math import factorial


class Extract_Data():
    def __init__(self, name, grind, relative):
        self.name = name
        self.grind = grind
        self.time = None
        self.adc = None
        self.temp = None
        self.resistance = None
        self.Vcc = 4.096
        self.Vref = 2.048
        self.R = 47000.
        self.labels = self.get_labels()
        self.relative = relative
        self.extract_and_calculate()

    def plot_temp(self, title_, mode):
        time_array = np.arange(0, (self.time[-1] - self.time[0])/1000. + 0.1, 0.1)

        for t, label_ in zip(self.temp[:], self.labels[:]):
            if len(time_array) > len(t):
                time_array = time_array[:-1]
            t = t[2:]
            t = t - t[0]
            sg = self.savitzky_golay(t, 9, 1)

            plt.plot(time_array[2:], sg, label=label_)
            #plt.axvspan(1270, 1320, facecolor='0.8', alpha=.8)
            plt.xlabel('Time (seconds)', fontsize=15)
            #plt.ylabel('$\Delta T$ (Celsius)')
            plt.ylabel('Temperature ($^o$C)', fontsize=15)
            plt.legend(loc='upper right', shadow=True, fontsize='large')
        if mode is not None:
            plt.axis([0, time_array[-1], -8, -1])
        if title_ is None:
            plt.title("Temperature under the left ski during a run.")
        else:
            plt.title(title_, fontsize=15)
        plt.show()

    def save_to_np(self, path):
        time_array = np.arange(0, (self.time[-1] - self.time[0])/1000. + 0.1, 0.1)
        np.save(path + "temp_time.npy", time_array)
        np.save(path + "temp_values.npy", self.temp)

    def get_max_delta_t(self):
        max_temp = []
        for t in self.temp:
            t = t[2:]
            t = t - t[0]

            #t = t[:80]
            t = t[~np.isnan(t)]
            if len(t) < 10:
                max_temp.append(-100)
            else:
                #t.sort()
                #tmp = t[::-1]
                t = t[:]
                # tmax = tmp[:10].sum() / 10
                #tmax = tmp[0]
                #max_temp.append(tmax)
                max_temp.append(t.max())
        #print np.around(max_temp, 2)
        return max_temp

    def get_labels(self):
        return ["25 cm", "40 cm", "130 cm", "140 cm", "150 cm", "160 cm", "170 cm"]

    def extract_and_calculate(self):

        text_file = open(self.name, 'r')
        lines = text_file.read().split('\n')
        data = np.asarray([line.split(',') for line in lines[3:-2]])

        # extract data
        self.time = np.asarray([np.float(t) for t in data[:, 0]])
        self.adc = []
        for i in [1, 3, 5, 7, 9, 11, 13]:
        # for i in [3, 5]:
            self.adc.append(np.asarray([np.float(r) for r in data[:, i]]))

        alpha = []
        for adc in self.adc:
            alpha.append(adc * self.Vref / (self.Vcc * 2**24))

        self.resistance = []
        for a in alpha:
            self.resistance.append(self.R * a / (1 - a))

        A, B, C = shh.x

        self.temp = []
        for r in self.resistance:
            self.temp.append(shh.steinhart_hart_temperature(A, B, C, r))

        self.temp = np.asarray(self.temp)
        if self.grind == "cold":
            self.temp[2:] = self.temp[2:][::-1]



    def savitzky_golay(self, y, window_size, order, deriv=0, rate=1):
        try:
            window_size = np.abs(np.int(window_size))
            order = np.abs(np.int(order))
        except ValueError, msg:
            raise ValueError("window_size and order have to be of type int")
        if window_size % 2 != 1 or window_size < 1:
            raise TypeError("window_size size must be a positive odd number")
        if window_size < order + 2:
            raise TypeError("window_size is too small for the polynomials order")
        order_range = range(order+1)
        half_window = (window_size - 1) // 2
        # precompute coefficients
        b = np.mat([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
        m = np.linalg.pinv(b).A[deriv] * rate**deriv * factorial(deriv)
        # pad the signal at the extremes with
        # values taken from the signal itself
        firstvals = y[0] - np.abs(y[1:half_window+1][::-1] - y[0])
        lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
        y = np.concatenate((firstvals, y, lastvals))
        return np.convolve(m[::-1], y, mode='valid')

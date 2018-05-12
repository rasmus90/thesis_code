"""
Title:  Extract Data from Load Cell files
Date:   05.12
"""
import numpy as np
import matplotlib.pyplot as plt
from IPython import embed


class Extract_Data():
    def __init__(self, name, title_, polynom):
        self.name = name
        self.title_ = title_
        self.load_val = None
        self.time = None
        self.p = polynom

    def check_file(self, _plot=False):

        text_file = open(self.name, "r")
        lines = text_file.read().split("\n")
        # remove the first and last readings, in case of invalid data or strings
        raw_adc = np.asarray([np.float(line[8:11]) if len(line) > 11 else
                             (np.float(line[7:10]) if len(line) > 10 else (
                              np.float(line[6:9])) if len(line) > 9 else
                              np.float(line[5:8]))for line in lines[4:-2]])
        self.load_val = self.p(raw_adc)

        self.time = np.asarray([np.float(line[:7]) if len(line) > 11 else
                                (np.float(line[:6]) if len(line) > 10 else (
                                 np.float(line[:5])) if len(line) > 9 else
                                 np.float(line[:4])) for line in lines[4:-2]])
        self.time -= self.time[0]

        if _plot:
            plt.plot(self.time, raw_adc, 'g')
            plt.xlabel("Time (seconds)")
            plt.ylabel("ADC raw (g)")
            plt.title(self.title_)
            plt.show()

        return self.time, self.load_val, raw_adc


class Extract_Data_New():
    def __init__(self, name, title_, polynom):
        self.name = name
        self.title_ = title_
        self.load_val = None
        self.time = None
        self.p = polynom


    def check_file(self, _plot=False):

        text_file = open(self.name, "r")
        lines = text_file.read().split("\n")
        # remove the first and last readings, in case of invalid data or strings
        data = [line.split(',')[:-1] for line in lines[4:-2]]
        tmp_time = []
        tmp_load = []

        for line in data:
            for i, val in enumerate(line):
                if i == 0 or i == (len(line)-1):
                    tmp_time.append(np.float(val))
                else:
                    tmp_load.append(np.float(val))
        self.time = np.asarray(tmp_time)/1000.
        raw_adc = np.asarray(tmp_load)
        self.load_val = self.p(raw_adc)
    

        # just make a new array of time stamps
        self.time = np.arange(0, len(self.load_val), 1)

        self.time -= self.time[0]
        if _plot:
            plt.plot(self.time, raw_adc, 'g')
            plt.xlabel("Time (seconds)")
            plt.ylabel("ADC raw (g)")
            plt.title(self.title_)
            plt.show()

        return self.time, self.load_val, raw_adc

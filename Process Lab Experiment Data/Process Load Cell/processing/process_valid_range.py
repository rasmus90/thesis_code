from __future__ import division
"""
About:  Process the range selected from
        select_valid_range.py
Date:   01.12.17
"""

import numpy as np
import matplotlib.pyplot as plt
from math import factorial
import scipy.signal


class Process_Valid_Range():
    def __init__(self, valid_range, time, load_val, title_):
        self.valid_range = valid_range
        self.time = time
        self.load_val = load_val
        self.ind = np.where(np.logical_and(self.time >= self.valid_range[0],
                                           self.time <= self.valid_range[1]))

        self.v_time = self.time[self.ind]
        self.v_load_val = self.load_val[self.ind]
        self.title_ = title_
        self.path = "/home/rasmus/master/Experiment Lab/Experimental Notes - Part 2/"

    def frequency(self):
        data = np.random.rand(len(self.v_load_val)) - 0.5
        ps = np.abs(np.fft.fft(data))**2

        time_step = 1 / 1000
        freqs = np.fft.fftfreq(data.size, time_step)
        idx = np.argsort(freqs)

        print max(freqs)
        plt.plot(freqs[idx], ps[idx])
        plt.show()

    def welch(self):
        x = self.v_load_val
        fs = 1000
        # Estimate PSD `S_xx_welch` at discrete frequencies `f_welch`
        f_welch, S_xx_welch = scipy.signal.welch(x, fs, nperseg=1024)
        """
        plt.figure()
        plt.plot(f_welch, S_xx_welch)
        plt.xlabel('frequency [Hz]')
        plt.ylabel('PSD')
        plt.show()
        """
        return f_welch, S_xx_welch

    def remove_measurements(self, a, b):
        tmp_ind = np.where(np.logical_and(self.v_time >= a, self.v_time <= b))[0]
        new_value = (self.v_load_val[tmp_ind[0]-1] + self.v_load_val[tmp_ind[-1]+1]) / 2.
        self.v_load_val[tmp_ind] = new_value

    def get_sg_array(self):
        sg = self.savitzky_golay(self.v_load_val, 1001, 5)
        time = self.v_time/1000.
        return [sg, time]

    def plot_valid_range(self, show, save, name):
        sg = self.savitzky_golay(self.v_load_val, 1001, 5)
        plt.figure()
        #plt.plot(self.v_time/1000., self.v_load_val)
        plt.plot(self.v_time/1000., sg, label="Smoothed")
        plt.xlabel("Time (seconds)")
        plt.ylabel("Load (gram")
        plt.title(self.title_)
        if show:
            plt.show()
        if save:
            plt.savefig(self.path+name)

    def save_valid_range(self, vel, load, number):
        path = "/home/rasmus/master/Experiment Lab/Power/1412PEHD/l510_1/"
        load_file_name = 'load_'+vel+load+number+'.npy'
        time_file_name = 'load_time'+vel+load+number+'.npy'
        np.save(path+load_file_name, self.savitzky_golay(self.v_load_val, 101, 5))
        np.save(path+time_file_name, self.v_time/1000.)

    def get_mean(self):
        # print "Mean from selected range: {:4.1f}".format(np.mean(self.v_load_val))
        return round(np.mean(self.v_load_val), 1)

    def get_std(self):
        # print "Std: {:4.3f}".format(np.std(self.v_load_val))
        return round(np.std(self.v_load_val, ddof=1), 1)

    def get_mu(self, normal_load):
        # print "u = {:4.3f}".format(np.mean(self.v_load_val)/normal_load)
        return round(np.mean(self.v_load_val)/normal_load, 3)

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

    def measurement_section(self):
        """
        Plot showing the measurement section
        """
        sg = self.savitzky_golay(self.v_load_val, 1001, 5)
        plt.plot(self.v_time/1000., sg, linewidth=2.0)
        plt.xlabel("Time (seconds)", fontsize=15)
        plt.ylabel("Pull Force $F_P$ (N)", fontsize=15)
        plt.axvspan(4.8, 10.0, facecolor='0.5', alpha=0.4)
        plt.title("Load cell data (smoothed) from channel experiment.")
        plt.text(6, 1.0, r'$F_F=|F_P|$', fontsize=20)
        plt.annotate(r'$\mu_k = \frac{\bar{F_F}}{F_N}$', xy=(8, 0.2), xytext=(6, .6),
            arrowprops=dict(arrowstyle='->'), fontsize=20)
        plt.show()

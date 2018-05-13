"""
Title:      Pick range and process data
Date:       02.01.18
Author:     RNT
"""

from folder_path import path_
import numpy as np
import pickle
import matplotlib.pyplot as plt
from math import factorial
from IPython import embed


def get_valid_range(min_x, max_x, list_position_slider):
    position_slider = np.asarray(list_position_slider)
    uncalibrated_x = np.asarray(position_slider[:, 1], dtype=np.float32)

    # use calibration on x-positions
    p = np.poly1d(polynomial_calibration_horizontal)
    x = p(uncalibrated_x)
    embed()

    # extract indices
    ind = np.where(np.logical_and(x > min_x, x < max_x))
    # np.save(path + "indices", ind)
    print x[-1]
    return x, ind


def load_one_result(result_name):
    with open(path + 'Video' + '/' + result_name + '.pkl', 'r') as crrt_file:
            result_data = pickle.load(crrt_file)
    return result_data


def savitzky_golay(y, window_size, order, deriv=0, rate=1):
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


def plot_results(x, ind, inc):
    """
    inc: increment when calculating velocity
    """
    time = np.arange(0, len(x), 1.0) / float(samp_freq) * 1000
    time = time[ind]/1000.
    x = x[ind]

    horizontal_velocity = (x[inc:] - x[0:-inc]) * samp_freq / inc
    sg_vel = savitzky_golay(horizontal_velocity, 101, 5)

    mean_horizontal_velocity = (x[-1] - x[0]) * samp_freq / len(x)
    print "Time interval: [{:2.2f}, {:2.2f}].".format(time[0], time[-1])
    print "Mean horizontal velocity: {:2.4f} m/s.".format(mean_horizontal_velocity)
    plt.plot(time[inc:], horizontal_velocity, label=r'$\frac{x_{i+5}-x_i}{5 \Delta t}$')
    plt.plot(time[inc:], sg_vel, label=r'Savitzky Golay')
    plt.xlabel('Time (s)')
    plt.ylabel('Velocity (m / s, calibrated)')
    plt.title('Material: '+path_.material+'. Motor power:'+vel+'. Load '+load+' g. Run nr.'+path_.number)
    plt.axis([0, time[-1]+1, 0., 0.5])
    plt.legend(loc='upper left', shadow=True, fontsize='x-large')
    name = path_.material+"_"+"v"+vel+"_"+number+"_l"+load+"_"+path_.id_+".png"

    if path_.savefigure:
        plt.savefig("/home/rasmus/master/Experiment Lab/Experimental Notes - Part 2/"+name)
    plt.show()

    #save_data(horizontal_velocity, sg_vel, time)


def save_data(horizontal_velocity, sg_vel, time):

    np.save(data_path + 'velocity.npy', horizontal_velocity)
    np.save(data_path + 'savgol_vel.npy', sg_vel)
    np.save(data_path + 'time.npy', time)


data_path = path_.data_path
path = path_.path
vel = path_.vel
load = path_.load
number = path_.number
polynomial_calibration_horizontal = np.load(path + 'poly_fit_calibration.npy')
samp_freq = 60

if __name__ == "__main__":
    list_position_slider = load_one_result('list_pos_slider')
    x, ind = get_valid_range(0.0, 2.5, list_position_slider)
    plot_results(x, ind, inc=5)

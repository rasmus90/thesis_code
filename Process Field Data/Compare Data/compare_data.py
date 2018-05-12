import numpy as np
import matplotlib.pyplot as plt
from math import factorial
from IPython import embed


def plot_temp(time, temp, ax1):
    temp[2:] = temp[2:][::-1]
    labels = ["25 cm", "40 cm", "130 cm", "140 cm", "150 cm", "160 cm", "170 cm"]
    labels = ["40 cm", "150 cm"]
    for t, _label in zip(temp, labels):
        t = t[2:]
        t = t - t[0]
        sg = savitzky_golay(t, 31, 5)
        ax1.plot(time[2:], sg, label=_label)
        ax1.legend(loc='upper right', shadow=True, fontsize='large')
    return ax1


def plot_velocity(time, velocity, ax1):
    ax2 = ax1.twinx()
    ax2.plot(time, velocity, 'r-', linewidth=3, label="Velocity")
    ax2.legend(loc='lower right', shadow=True, fontsize='large')
    return ax2


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


def compare_1603_last_run():
    # add 1 from GPS time to get corresponding time stamps
    path = "/home/rasmus/master/Field Experiment/Experiments/Mars/16.03/Compare Data/Last Run"
    fig, ax1 = plt.subplots()
    temp_time = np.load(path + "/temp_time.npy")
    temp_values = np.load(path + "/temp_values.npy")
    velocity_time = np.load(path + "/velocity_time.npy")
    velocity_values = np.load(path + "/velocity_values.npy")
    temp_values = np.asarray((temp_values[1], temp_values[4]))
    ax1 = plot_temp(temp_time, temp_values, ax1)
    ax1.set_ylabel(r'$\Delta T$'+" ($^o$C)", color='b', fontsize=13)
    ax1.set_xlabel("Time (seconds)", fontsize=13)
    ax1.tick_params("y", colors='b')

    ax2 = plot_velocity(velocity_time + 1, velocity_values, ax1)
    ax2.set_ylabel("Velocity (km/h)", color="r", fontsize=13)
    ax2.tick_params('y', colors='r')
    ax2.set_title("Velocity and $\Delta T$. Date: 16.03. Time: 14:30.")
    fig.tight_layout()
    plt.show()


def compare_1603_6_first_runs():
    path = "/home/rasmus/master/Field Experiment/Experiments/Mars/16.03/Compare Data/Run "
    for i in range(1, 7):
        fig, ax1 = plt.subplots()
        temp_time = np.load(path + str(i) + "/temp_time.npy")
        temp_values = np.load(path + str(i) + "/temp_values.npy")
        velocity_time = np.load(path + str(i) + "/velocity_time.npy")
        velocity_values = np.load(path + str(i) + "/velocity_values.npy")
        temp_values = np.asarray((temp_values[1], temp_values[4]))
        ax1 = plot_temp(temp_time, temp_values, ax1)
        ax1.set_ylabel(r'$\Delta T$'+" ($^o$C)", color='b', fontsize=13)
        ax1.set_xlabel("Time (seconds)", fontsize=13)
        ax1.tick_params("y", colors='b')
        ax2 = plot_velocity(velocity_time, velocity_values, ax1)
        ax2.set_ylabel("Velocity (km/h)", color="r", fontsize=13)
        ax2.tick_params('y', colors='r')
        ax2.set_title("Velocity and $\Delta T$. Date: 16.03. Time: 13:10.", fontsize=13)
        fig.tight_layout()
        plt.show()


def compare_1603_runs_9to12():
    path = "/home/rasmus/master/Field Experiment/Experiments/Mars/16.03/Compare Data/Run "
    for i in range(9, 13):
        fig, ax1 = plt.subplots()
        temp_time = np.load(path + str(i) + "/temp_time.npy")
        temp_values = np.load(path + str(i) + "/temp_values.npy")
        velocity_time = np.load(path + str(i) + "/velocity_time.npy")
        velocity_values = np.load(path + str(i) + "/velocity_values.npy")
        ax1 = plot_temp(temp_time, temp_values, ax1)
        ax1.set_ylabel(r'$\Delta T$', color='b')
        ax1.tick_params("y", colors='b')
        ax2 = plot_velocity(velocity_time + 1.5, velocity_values, ax1)
        ax2.set_ylabel("Velocity (km/h)", color="r")
        ax2.tick_params('y', colors='r')
        ax2.set_title("Velocity and temperature. Motor power 1300. Date: 16.03.")
        fig.tight_layout()
        plt.show()


def compare_2703_run8():
    # add 1 from GPS time to get corresponding time stamps
    path = "/home/rasmus/master/Field Experiment/Experiments/Mars/27.03/Compare Data/Run 8"
    fig, ax1 = plt.subplots()
    temp_time = np.load(path + "/temp_time.npy")
    temp_values = np.load(path + "/temp_values.npy")
    velocity_time = np.load(path + "/velocity_time.npy")
    velocity_values = np.load(path + "/velocity_values.npy")
    ax1 = plot_temp(temp_time, temp_values, ax1)
    ax1.set_ylabel(r'$\Delta T$', color='b')
    ax1.tick_params("y", colors='b')

    ax2 = plot_velocity(velocity_time + 0, velocity_values, ax1)
    ax2.set_ylabel("Velocity (km/h)", color="r")
    ax2.tick_params('y', colors='r')
    ax2.set_title("Velocity and temperature. Motor power 1300. Date: 27.03.")
    fig.tight_layout()
    plt.show()


def compare_1004_run35():
    path = "/home/rasmus/master/Field Experiment/Experiments/April/10.04/Compare Data/Run 35/"
    velocity_time = np.load(path + "/velocity_time.npy")
    velocity_values = np.load(path + "/velocity_values.npy")
    load_values = np.load(path + "/load_values.npy")
    load_time = np.load(path + "/load_time.npy")

    grad = np.gradient(velocity_values, 1.)
    plt.plot(velocity_time, grad)
    plt.plot(velocity_time, velocity_values)
    plt.plot(load_time, load_values)
    plt.show()


if __name__ == '__main__':
    #compare_1603_runs_9to12()
    compare_1603_last_run()
    compare_1603_6_first_runs()
    # compare_2703_run8()
    #compare_1004_run35()

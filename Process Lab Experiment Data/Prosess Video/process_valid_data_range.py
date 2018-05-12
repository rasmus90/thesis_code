from scipy import misc
import os
import fnmatch
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage
from scipy import signal
from tqdm import tqdm
import pickle
from IPython import embed
from math import factorial
from folder_path import path_

# all functions for range selection ----------------------------------------------------------------


def plot_raw_results_folder_process(list_pos_seed, polynomial_calibration_horizontal=None, sampling_frequency=60.0, valid_index=(-1, -1), debug=False, f_max=5):

    # generate data to use
    pos_seed = np.asarray(list_pos_seed, dtype=np.float32)

    coord = pos_seed
    use_calibration = False

    time_vector = np.arange(0, len(pos_seed), 1.0) / float(sampling_frequency) * 1000
    ind = np.where(np.logical_and(time_vector >= valid_index[0],
                                  time_vector <= valid_index[1]))

    if valid_index[0] > -1:
        pos_seed = pos_seed[ind[0], :]

    # extract selected time interval

    time_vector = time_vector[ind[0]]/1000.

    if debug:
        print time_vector

    if debug:
        print "f shape:"
        print f.shape
        print "Pxx_tips_1x shape:"
        print Pxx_tips_1x.shape

    if polynomial_calibration_horizontal is not None:
        print "Using horizontal calibration"
        p = np.poly1d(polynomial_calibration_horizontal)
        use_calibration = True

        if debug:
            print pos_seed

        pos_seed[:, 1] = p(pos_seed[:, 1])
        coord[:, 1] = p(coord[:, 1])

        if debug:
            print pos_seed

        trajectory = False
        if trajectory:
            # look at horizontal velocity by time evolution of height
            plt.figure()
            # plt.plot(pos_seed[:,1])
            plt.plot(time_vector, pos_seed[:, 1])
            plt.xlabel('Time (s)')
            plt.ylabel('Position (m, calibrated)')
            plt.show()

        inc = 5



        # look at the horizontal velocity by differenciation
        horizontal_velocity = (pos_seed[inc:, 1] - pos_seed[0:-inc, 1]) * sampling_frequency / inc
        horizontal_velocity_whole_range = (coord[inc:, 1] - coord[0:-inc, 1]) * sampling_frequency / inc
        sg = savitzky_golay(horizontal_velocity_whole_range[ind[0][4]:ind[0][-1]], 101, 5)

        embed()

        plt.figure()
        # plt.plot(horizontal_velocity)
        plt.plot(time_vector[inc:], horizontal_velocity)
        plt.plot(time_vector[inc:], sg, 'r')
        plt.xlabel('Time (s)')
        plt.ylabel('Velocity (m / s, calibrated)')
        plt.title('Material: '+path_.material+'. Velocity input:'+vel+'. Load '+load+' g. Run nr.'+path_.number)
        plt.axis([0, 12, 0., 0.5])
        name = path_.material+"_"+"v"+vel+"_"+number+"_l"+load+".png"

        if path_.savefigure:
            plt.savefig("/home/rasmus/master/Experiment Lab/Experimental Notes/"+name)
        plt.show()

        if path_.savepower:
            save_to_power_folder(time_vector[inc:], sg)

        mean_horizontal_velocity = (pos_seed[-1, 1] - pos_seed[0, 1]) * sampling_frequency / pos_seed.shape[0]
        print
        print " "
        print "Information slider horizontal velocity:"
        print "Slider mean horizontal velocity (m/s): " + str(mean_horizontal_velocity)

    else:
        print "Using no calibration"
        # figure identified points
        plt.figure()
        plt.plot(pos_seed[:, 0], pos_seed[:, 1], marker='o', color='k')
        plt.xlabel("x (pxls)")
        plt.ylabel("y (pxls)")
        plt.show()

        # look at horizontal velocity by time evolution of height
        plt.figure()
        # plt.plot(pos_seed[:,1])
        plt.plot(time_vector, pos_seed[:, 1])
        plt.xlabel('Time (s)')
        plt.ylabel('Position (pxls, not calibrated)')

        # look at the horizontal velocity by differenciation
        horizontal_velocity = (pos_seed[1:, 1] - pos_seed[0:-1, 1]) * sampling_frequency

        plt.figure()
        # plt.plot(horizontal_velocity)
        plt.plot(time_vector[1:], horizontal_velocity)
        plt.xlabel('Time (s)')
        plt.ylabel('Velocity (pxl / s, not calibrated)')

    return (pos_seed, use_calibration, mean_horizontal_velocity)


def save_to_power_folder(time, velocity):
    path = path_.power_path
    time_file = 'vel_time_vel'+vel+'.npy'
    velocity_file = 'vel'+vel+'.npy'
    np.save(path+time_file, time)
    np.save(path+velocity_file, velocity)


def load_one_result(result_name):
    with open(path + list_cases[ind_case] + '/' + result_name + '.pkl', 'r') as crrt_file:
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
    half_window = (window_size -1) // 2
    # precompute coefficients
    b = np.mat([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
    m = np.linalg.pinv(b).A[deriv] * rate**deriv * factorial(deriv)
    # pad the signal at the extremes with
    # values taken from the signal itself
    firstvals = y[0] - np.abs(y[1:half_window+1][::-1] - y[0])
    lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
    y = np.concatenate((firstvals, y, lastvals))
    return np.convolve(m[::-1], y, mode='valid')


def check_position(path_to_images, x):
    import glob
    files = []
    destination = path_to_images+"/Video/"
    os.chdir(destination)
    for file in glob.glob("crop*"):
        files.append(file)
    files.sort()
    n = 319
    img_tmp = files[n:]
    x_tmp = x[n:]
    x_val = x_tmp[:,1]
    y_val = x_tmp[:,0]
    embed()
    for img, x, y in zip(img_tmp, x_val, y_val):
        img = misc.imread(img)
        plt.figure()
        plt.imshow(img)
        plt.plot(x, y, 'ro')
        plt.show()
        s = raw_input("Press k to contiune")
        if s == "k":
            continue
        else:
            break

#################################################################################
#################################################################################
# range selection is done from here
# adapt paths / fnmatch arguments as needed

# analysis of the data


path = path_.path
vel = path_.vel
load = path_.load
number = path_.number

sampling_frequency = 60

# loads the calibration --------------------------------------------------------
poly_fit_calibration = np.load(path + 'poly_fit_calibration.npy')

# load list of all cases -------------------------------------------------------
list_cases = []
for file_name in os.listdir(path):
    if fnmatch.fnmatch(file_name, 'Video*'):
        list_cases.append(file_name)

print "Cases to process:"
for crrt_case in list_cases:
    print crrt_case

print " "
nbr_cases = len(list_cases)
print "Number of cases: " + str(nbr_cases)

dict_all_results = {}

# analyse all cases ------------------------------------------------------------
for ind_case in range(nbr_cases):
    # for ind_case in [5]:

    print ""
    print "------------------------------------------------------------"
    print "Analysing case: " + str(list_cases[ind_case])

    path_to_images = path + list_cases[ind_case] + '/'

    print "Load generated data"

    list_pos_seed = load_one_result('list_pos_seed')
    indices = np.load(path + "indices.npy")
    print "Load valid range data"
    valid_range = np.genfromtxt(path_to_images + "valid_range.csv", delimiter=",")

    min_valid_range = int(valid_range[0])
    max_valid_range = int(valid_range[1])

    (pos_seed, use_calibration, mean_horizontal_velocity) = plot_raw_results_folder_process(
        list_pos_seed, polynomial_calibration_horizontal=poly_fit_calibration,
        sampling_frequency=sampling_frequency, valid_index=(min_valid_range, max_valid_range), debug=False, f_max=5)

    dict_all_results[list_cases[ind_case] + "pos_seed"] = pos_seed
    dict_all_results[list_cases[ind_case] + "use_calibration"] = use_calibration
    dict_all_results[list_cases[ind_case] + "mean_horizontal_velocity"] = mean_horizontal_velocity

# save the dictionary
with open(path + 'dict_all_results.pkl', 'w') as crrt_file:
        pickle.dump(dict_all_results, crrt_file, pickle.HIGHEST_PROTOCOL)

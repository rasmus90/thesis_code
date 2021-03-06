from scipy import misc
import os
import fnmatch
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage
from tqdm import tqdm
import pickle
from folder_path import path_

# %matplotlib inline

# images lading and processing functions ---------------------------------------


def generate_image_list(path_to_images):
    list_images = []

    for file_name in os.listdir(path_to_images):
        if fnmatch.fnmatch(file_name, 'crop*'):
            list_images.append(file_name)

    list_images.sort()

    return list_images


def read_one_image(path_to_images, image, verbose=0):
    name_image_current = path_to_images + image
    image_current = misc.imread(name_image_current)

    if verbose > 1:
        print "Read: " + name_image_current
        print "Native shape: " + str(image_current.shape)

        plt.imshow(image_current)
        plt.show()

    return image_current


def load_all_images(list_images, dict_images, verbose=0):
    for current_image_name in list_images:
        dict_images[current_image_name] = read_one_image(path_to_images, current_image_name)

        if verbose > 1:
            print "Loaded " + current_image_name


def shape_image(image_name, dict_images, verbose=0):
    shape_image = dict_images[image_name].shape

    if verbose > 1:
        print "Shape image: " + str(shape_image)

    return shape_image


def compute_mean_image(list_images, dict_images, shape_image, image_max=-1, verbose=0):
    """
    compute the mean image at each pixel, based on all images in the video
    """

    if image_max > 0:

        numpy_array_all_images = np.zeros((shape_image[0], shape_image[1], shape_image[2], image_max), dtype=np.uint8)

        for ind_image in range(image_max):
            image_name = list_images[ind_image]
            numpy_array_all_images[:, :, :, ind_image] = dict_images[image_name]

    else:

        number_of_images = len(list_images)
        numpy_array_all_images = np.zeros((shape_image[0], shape_image[1], shape_image[2], number_of_images), dtype=np.uint8)

        for ind_image in range(number_of_images):
            image_name = list_images[ind_image]
            numpy_array_all_images[:, :, :, ind_image] = dict_images[image_name]

    mean_image = np.uint8(np.floor(np.mean(numpy_array_all_images, 3)))
    std_image = np.uint8(np.floor(np.std(numpy_array_all_images, 3)))

    dict_images['mean_image'] = mean_image
    dict_images['std_image'] = std_image

    if verbose > 0:
        plt.figure()
        plt.imshow(mean_image)

        plt.figure()
        plt.imshow(std_image)

        plt.show()


def compute_change_image(list_images, dict_images, image_number, plot_L2=False, verbose=0):
    image_name = list_images[image_number]
    image = dict_images[image_name]

    mean_image = dict_images['mean_image']
    std_image = dict_images['std_image']

    image_difference = np.uint8(np.floor(np.abs(np.float16(image) - np.float16(mean_image))))

    if plot_L2:
        float_difference = L2_norm(np.float32(image_difference))

    if verbose > 1:
        plt.figure()
        plt.imshow(image_difference)

        if plot_L2:
            plt.figure()
            plt.pcolor(float_difference)
            plt.colorbar()

        plt.show()

    return(image_difference)


def threshold_image(shape_image, change_image, threshold_change, verbose=0):

    threshold_image = np.zeros((shape_image[0], shape_image[1]), dtype=np.uint8)

    image_0 = np.float32(change_image[:, :, 0]) >= np.float32(threshold_change)
    image_1 = np.float32(change_image[:, :, 1]) >= np.float32(threshold_change)
    image_2 = np.float32(change_image[:, :, 2]) >= np.float32(threshold_change)

    threshold_image = np.uint8(image_0 & image_1 & image_2)

    if verbose > 1:
        plt.figure()
        plt.imshow(threshold_image)

        plt.show()

    return threshold_image


def plot_as_image(image):
    max_image = np.max(np.max(image))

    image_uint8 = np.uint8(np.floor(254.0 * image / max_image))

    plt.figure()
    plt.imshow(image_uint8)

    print "Plot as image max: " + str(np.max(np.max(image)))


def convolve_disk(image_in, kernel_radius=10, verbose=0):
    kernel = np.zeros((kernel_radius * 2, kernel_radius * 2))

    for i in range(kernel_radius * 2):
        for j in range(kernel_radius * 2):

            if (i - kernel_radius + 1)**2 + (j - kernel_radius + 1)**2 < kernel_radius**2:
                kernel[i, j] = 1

    if verbose > 1:
        plt.figure()
        plt.imshow(kernel)

    convolved = ndimage.convolve(np.float32(image_in), kernel)

    if verbose > 1:
        plot_as_image(convolved)

    if verbose > 1:
        plt.show()

    return convolved


def find_pos_slider(shape_image, list_images, dict_images, image_number, identification='lowest', verbose=0, debug=False):
    difference_image = compute_change_image(list_images, dict_images, image_number, plot_L2=False, verbose=verbose)

    threshold_change = 40
    thresholded_image = threshold_image(shape_image, difference_image, threshold_change, verbose=verbose)

    convolved = convolve_disk(thresholded_image, kernel_radius=11, verbose=0)
    convolved = np.uint8(255.0 * convolved / np.max(np.max(convolved)))

    convolved_3_channels = np.zeros((shape_image[0], shape_image[1], shape_image[2]), dtype=np.uint8)
    convolved_3_channels[:, :, 0] = np.uint8(np.floor(convolved))
    convolved_3_channels[:, :, 1] = np.uint8(np.floor(convolved))
    convolved_3_channels[:, :, 2] = np.uint8(np.floor(convolved))

    threshold_change = 100
    thresholded_image = threshold_image(shape_image, convolved_3_channels, threshold_change, verbose=verbose)
    convolved = convolve_disk(thresholded_image, kernel_radius=11, verbose=verbose)
    convolved = np.uint8(255.0 * convolved / np.max(np.max(convolved)))

    # version to identify the lowest point of the sliders light emitting diode
    if identification == 'lowest':
        index_valid = np.where(convolved > 250)
        if index_valid[0].size == 0:
            index_valid = ([0], [0])
        position_1 = np.min(index_valid[1])
        # should check if a position is detected here!
        if position_1 > 0:
            position_0 = int(np.floor(np.mean(np.where(convolved[:, position_1] == np.max(convolved[:, position_1])))))
            position = (position_0, position_1)
        else:
            position_1 = 0
            position_2 = 0
            position = (position_1, position_2)
    # version to identify the center of the sliders light emitting diode
    elif identification == 'highest':
        position = np.unravel_index(convolved.argmax(), convolved.shape)
    else:
        print "Identification method not implemented!"

    if debug:
        print "position:"
        print position

    if not position > 0:
        position = 0

    if verbose > 0:
        print "Found position: " + str(position)

    if verbose > 1:

        image_current = dict_images[list_images[image_number]]

        plt.figure()
        # image_current = ndimage.rotate(image_current, 90)
        plt.imshow(image_current)
        # plt.plot(position[0], position[1], marker='o', color='r')
        plt.plot(position[1], position[0], marker='o', color='r')
        plt.show()

    return(position)


def plot_image_with_identified_points(list_images, dict_images, image_number, pos_slider, half_width_box=150, height_box=80):

    plt.figure()
    plt.imshow(dict_images[list_images[image_number]])
    plt.plot(pos_slider[1], pos_slider[0], marker='o', color='r')
    plt.show()

# Analysis of one folder and processing of raw results functions ----------------------


def process_folder_load(path_to_folder, verbose=0):
    print "Create necessary data structure"
    dict_images = {}

    print "Generate image names"
    list_images = generate_image_list(path_to_images)

    number_of_images = len(list_images)
    print "Number of images found: " + str(number_of_images)

    print "Load all images"
    load_all_images(list_images, dict_images, verbose=verbose)

    print "Determine size images"
    tuple_shape_image = shape_image(list_images[0], dict_images, verbose=verbose)

    print "Compute mean image"
    compute_mean_image(list_images, dict_images, tuple_shape_image, verbose=verbose)

    print "Done!"

    return(dict_images, list_images, number_of_images, tuple_shape_image)


def process_folder_process(path_to_folder, dict_images, list_images, number_of_images, tuple_shape_image, image_start=0, number_of_images_to_analyse=-1, verbose=0, debug=False):

    print "Generate positions and width for each sliderfrom images"
    list_pos_slider = []

    if number_of_images_to_analyse > 0:
        max_range = number_of_images_to_analyse
    else:
        max_range = number_of_images - image_start

    for ind in tqdm(range(max_range)):
        ind += image_start

        if verbose > 1:
            print "Locate slider in image number: " + str(ind)

        position = find_pos_slider(tuple_shape_image, list_images, dict_images, ind, verbose=verbose - 2, debug=debug)
        list_pos_slider.append(position)

        if verbose > 2:
            plot_image_with_identified_points(list_images, dict_images, ind, list_pos_slider[-1])

            if number_of_images_to_analyse == -1:
                continue_processing = raw_input("Continue? yes [y] or no [n]: ")
                if continue_processing == 'n':
                    break

    print "Done!"

    return list_pos_slider

# Calibration and fine analysis of raw results functions ---------------------------------


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
                plt.plot(event.xdata, event.ydata, marker='o', color='r')
                plt.show()

    def return_positions(self):
        return self.position_on_click_accumulator


def generate_data_calibration_click(path_to_images, image, verbose=0):
    if verbose > 0:
        print "Load image to use for calibration"
    image_calibration = read_one_image(path_to_images, image, verbose=verbose)

    if verbose > 0:
        print "Position of the calibration points:"
        for a in position_points:
            print str(a)

    if verbose > 0:
        print "Select all points to use for calibration and then close the figure"

    plt.figure()
    plt.imshow(image_calibration)

    generate_data_click_object = generateDataOnClick(verbose=verbose)
    plt.connect('button_press_event', generate_data_click_object.position_on_click)
    plt.show()

    selected_positions_pixels = generate_data_click_object.return_positions()

    return selected_positions_pixels


def generate_vertical_positions_table(min, max, step, verbose=0):
    vertical_positions_table = []
    for value in np.arange(min, max, float(step)):
        vertical_positions_table.append((0, value))

    if verbose > 0:
        print "Number of points generated: " + str(len(vertical_positions_table))
        print "Points generated:"
        for a in vertical_positions_table:
            print a

    return vertical_positions_table

# position_points contains the list of physical positions (x,y) in mm of the points on which the user will click
# ex: position_points = [(0,0), (0,10), (0,20)]
# NOTE: this function is ok for course use but too simplistic for 'research' use. as it uses only one
# polynomial based only on the y values instead of x = P1(pxlx, pxly) and y = P2(pxlx, pxly)


def perform_fitting_calibration_vertical(selected_positions_pixels, position_points, order=3, verbose=0, debug=False):
    if not len(position_points) == len(selected_positions_pixels):
        print "Problem: not the same number of mm and pxls locations!!"

    y = np.asarray(selected_positions_pixels)
    x = np.asarray(position_points)
    if debug:
        print x
        print y

    x = x[:, 0]
    y = y[:, 1]
    if debug:
        print x
        print y

    z = np.polyfit(x, y, order)

    if verbose > 1:
        print "Test calibration"

        plt.figure()
        plt.plot(x, y, marker='o', color='r')
        values_test = np.arange(0, 1200, 1.0)
        poly_z = np.poly1d(z)
        plt.plot(values_test, poly_z(values_test), label='calibration points')
        plt.xlabel('Pixels')
        plt.ylabel('Coordinates')
        plt.legend(loc=2)
        plt.show()

    return z


def save_one_result(result_data, result_name):
    with open(path + list_cases[ind_case] + '/' + result_name + '.pkl', 'w') as crrt_file:
            pickle.dump(result_data, crrt_file, pickle.HIGHEST_PROTOCOL)

################################################################################
################################################################################
# Here is the code that uses all the previously defined functions to do the
# analysis; update paths, fnmatch arguments etc as needed.


path = path_.path
# perform the calibration ------------------------------------------------------


if 'poly_fit_calibration.npy' not in os.listdir(path):
    position_points = generate_vertical_positions_table(0, 2.5, 0.5, verbose=0)     # do it in mm
    selected_positions_pixels = generate_data_calibration_click(path, 'cropgrid.png', verbose=0)
    poly_fit_calibration = perform_fitting_calibration_vertical(position_points, selected_positions_pixels, order=3, verbose=2, debug=False)
    print "save calibration"
    print poly_fit_calibration
    np.save(path + 'poly_fit_calibration', poly_fit_calibration)

# loads the calibration --------------------------------------------------------
poly_fit_calibration = np.load(path + 'poly_fit_calibration.npy')

# load list of all cases -------------------------------------------------------
list_cases = []
for file_name in os.listdir(path):
    if fnmatch.fnmatch(file_name, 'Video'):
        list_cases.append(file_name)

print "Cases to process:"
for crrt_case in list_cases:
    print crrt_case

print " "
nbr_cases = len(list_cases)
print "Number of cases: " + str(nbr_cases)

# perform analysis of all cases ------------------------------------------------
for ind_case in range(nbr_cases):


    print ""
    print "------------------------------------------------------------"
    print "Analysing case: " + str(list_cases[ind_case])
    print "Case index: " + str(ind_case) + ' out of ' + str(nbr_cases)

    path_to_images = path + list_cases[ind_case] + '/'

    (dict_images, list_images, number_of_images, tuple_shape_image) = process_folder_load(path_to_images, verbose=0)

    list_pos_slider = process_folder_process(path_to_images, dict_images, list_images, number_of_images, tuple_shape_image, image_start=0, number_of_images_to_analyse=-1, verbose=0, debug=False)

    print "Saving generated data"

    save_one_result(list_pos_slider, 'list_pos_slider')

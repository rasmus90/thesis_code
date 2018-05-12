import matplotlib.pyplot as plt
import numpy as np
from scipy import misc
from IPython import embed


def read_one_image(path_to_images, image, verbose=0):
    name_image_current = path_to_images + image
    print name_image_current
    image_current = misc.imread(name_image_current)

    if verbose > 1:
        print "Read: " + name_image_current
        print "Native shape: " + str(image_current.shape)

        plt.imshow(image_current)
        plt.show()

    return image_current


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


def perform_fitting_calibration_horizontal(selected_positions_pixels, position_points, order=3, verbose=0, debug=False):
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


def generate_horizontal_positions_table(min, max, step, verbose=0):
    horizontal_positions_table = []
    for value in np.arange(min, max, float(step)):
        horizontal_positions_table.append((0, value))

    if verbose > 0:
        print "Number of points generated: " + str(len(horizontal_positions_table))
        print "Points generated:"
        for a in horizontal_positions_table:
            print a

    return horizontal_positions_table



path = "/home/rasmus/master/Experiment Lab/Grid/720/"
image = "crop_grid.png"
position_points = generate_horizontal_positions_table(0, 2.5+0.5, 0.5, verbose=0)
selected_positions_pixels = generate_data_calibration_click(path, image, verbose=0)
poly_fit_calibration = perform_fitting_calibration_horizontal(position_points, selected_positions_pixels, order=3, verbose=2, debug=False)

print "save calibration"
np.save(path+'poly_fit_calibration', poly_fit_calibration)
poly_fit_calibration = np.load(path + 'poly_fit_calibration.npy')

embed()

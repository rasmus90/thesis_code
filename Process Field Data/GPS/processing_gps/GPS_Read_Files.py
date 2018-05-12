"""
Title:  Read from file (GPS data)
Author: Rasmus Nes Tjoerstad
Date:   01.03.18
"""

import numpy as np
import matplotlib.pyplot as plt
from IPython import embed
import gmplot
import LatLon  # calculating distance between coordinates
import pynmea2
import scipy.signal


class FileHandler():
    def __init__(self, name, nr):
        self.nr = nr
        self.name = name
        self.lines = []
        self.lat_list = []
        self.long_list = []
        self.altitude_list = []
        # stores velocity: km/h
        self.velocity = []
        self.time = []
        self.check_file()
        self.velocity_time = np.arange(0, len(self.velocity), 1)

    def check_file(self):
        GPS_file = open(self.name, "r")
        self.lines = GPS_file.read().split("\n")
        for line in self.lines:
            if line[1:6] == "GPGGA" and len(line) > 72 and len(line) < 80:
                msg = pynmea2.parse(line)
                self.lat_list.append(msg.latitude)
                self.long_list.append(msg.longitude)
                self.time.append(msg.timestamp)
                self.altitude_list.append(msg.altitude)

            if line[1:6] == "GPVTG" and len(line) > 42 and len(line) < 52:
                msg2 = pynmea2.parse(line)
                # self.velocity.append(float(line[31:36]))
                self.velocity.append(msg2.spd_over_grnd_kmph)

    def get_elevatation_stats(self):
        if len(self.altitude_list) < 1:
            return 0
        h = np.asarray(self.altitude_list)

        return h.min(), h.max()

    def plot_velocity(self, title_):
        sg = scipy.signal.savgol_filter(self.velocity, 11, 5)

        plt.plot(self.velocity_time, sg, label="km/h")
        #plt.plot(self.velocity_time, self.velocity, label="Run nr. " + str(self.nr))
        plt.xlabel("Time (seconds)")
        plt.ylabel("Velocity (km/h)")
        if title_ is not None:
            plt.title(title_)
        else:
            plt.title("Velocity data.")
        #plt.axis([0, 30, 0, 25])
        plt.legend(loc='upper right', shadow=True, fontsize='large')
        plt.show()

    def save_to_np(self, path):
        np.save(path + "velocity_time.npy", self.velocity_time)
        np.save(path + "velocity_values.npy", self.velocity)

    def track_distance(self):
        if len(self.long_list) < 1:
            return 0
        p1 = LatLon.LatLon(self.lat_list[0], self.long_list[0])
        p2 = LatLon.LatLon(self.lat_list[-1], self.long_list[-1])
        d = p2.distance(p1) * 1000
        return "Track distance: {:1.1f} m.".format(d)

    def displacement(self):
        if len(self.long_list) < 1:
            return 0
        else:
            disp = []
            for i in range(len(self.long_list)-1):
                p1 = LatLon.LatLon(self.lat_list[i], self.long_list[i])
                p2 = LatLon.LatLon(self.lat_list[-1], self.long_list[-1])
                d = p2.distance(p1) * 1000
                disp.append(d)
            disp = np.asarray(disp)
            embed()
            return disp[::-1]

    def plot_both_velocities(self, title_):
        dist_list = []
        for i in range(len(self.lat_list)-1):
            p1 = LatLon.LatLon(self.lat_list[i], self.long_list[i])
            p2 = LatLon.LatLon(self.lat_list[i+1], self.long_list[i+1])
            dist = p2.distance(p1)
            dist_list.append(dist)
        velocity_2 = np.asarray(dist_list) * 3600
        time_2 = np.arange(2, len(velocity_2) + 2, 1)
        vel = np.asarray(self.velocity)
        # print vel[26:35].mean()
        plt.plot(time_2, velocity_2, 'r-', label='Position based.')
        plt.plot(self.velocity_time, self.velocity, 'b-', label='GPS')
        plt.xlabel("Time (seconds)")
        plt.ylabel("Velocity (km/h)")
        plt.legend(loc='upper right', shadow=True, fontsize='large')
        if title_ is not None:
            plt.title(title_)
        else:
            plt.title("Velocity data.")
        plt.show()

    def get_start_time(self):
        if len(self.time) == 0:
            return "No valid GPS Data."
        else:
            # remember correct time. +2 : adjusted for spring/summer time after 24.03
            return ("{}:{}").format(self.time[0].hour+2, self.time[0].minute)

    def make_html_map(self, filename):
        gmap = gmplot.GoogleMapPlotter(self.lat_list[0], self.long_list[0], 16)
        gmap.heatmap(self.lat_list, self.long_list)
        gmap.draw(filename+".html")

    def plot_for_thesis(self):
        sg = scipy.signal.savgol_filter(self.velocity, 11, 5)

        plt.plot(self.velocity_time, sg, label="km/h", linewidth=3.0)

        #plt.plot(self.velocity_time, self.velocity, label="Run nr. " + str(self.nr))
        plt.xlabel("Time (seconds)", fontsize=12)
        plt.ylabel("Velocity (km/h)", fontsize=12)
        plt.title("Velocity data. Time: 11:52. Date: 14 March.")
        plt.axvspan(11, 18, facecolor='0.5', alpha=0.4)
        plt.legend(loc='upper right', shadow=True, fontsize='large')
        plt.show()

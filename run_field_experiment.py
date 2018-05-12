"""
Title:      Run Field Experiment
Author:     RNT
About:      This script controls the engine and the logging.
            Connect the USB cabel from the Motor to the
            USB port furthest away from you.
            Connect the USB from the Feather LoRa to the USB port
            closest to you.

            If the script does not yield expected result, try to change
            the port for ser1 and ser2.

Arduino:    Works with the following arduino programs:
            1) Field_Motor_Control.ino
            2) Radio_Transmit_Signal.ino


"""


import serial
import glob
import time
import os
import numpy as np
from IPython import embed


class RunField():

    def __init__(self):
        self.ports = glob.glob('/dev/ttyACM*')  # swap ports if program does not run properly
        self.ser1 = None
        self.ser2 = None
        self.start_throttle = 0  # set to 1000 if reset, 1500 if arming
        self.chosen_velocity = None
        self.zero_speed = 1000
        self.full_speed = 1600
        self.mid_points = 1500
        self.inc = 50
        # self.set_port_singel()
        self.set_ports()

    def set_port_singel(self):
        self.ser1 = serial.Serial(self.ports[0], 9600, timeout=0.5)

    def set_ports(self):
        if "0" in self.ports[0]:
            self.ser1 = serial.Serial(self.ports[0], 9600, timeout=0.5)
            self.ser2 = serial.Serial(self.ports[1], 9600, timeout=0.5)
        else:
            self.ser1 = serial.Serial(self.ports[1], 9600, timeout=0.5)
            self.ser2 = serial.Serial(self.ports[0], 9600, timeout=0.5)
        time.sleep(0.1)

    def set_velocity(self):
        v = raw_input("Set speed to amp up to. Value between 1000 and 2000: ")
        print int(v)
        if int(v) > 2000 or int(v) < 1000:
            print "Non-valid value. Try again."
            return 0
        else:
            return v

    def start_run(self):
        start = raw_input("Send char S to start, other to reboot: ")
        if start == "S":
            return "S"
        else:
            print "Invalid character. Try again."
            return "F"

    def safety_check(self, mode):
        if mode == "acceleration":
            s = raw_input("Continue to amp up? y/n ")
        else:
            s = raw_input("Turn off? y/n ")
        return s

    def amping_down(self, velocity):
        print "Apming down."
        while velocity > self.zero_speed:
            velocity -= self.inc
            print velocity
            time.sleep(0.250)

    def initiate(self):
        throttle = raw_input("Send M for mid-throttle (1500) or Z for zero (1000): ")
        if throttle == 'M' or throttle == 'Z':
            print "Chosen char: {} ".format(throttle)
            return throttle
        else:
            print "Non-valid answer. Try again."
            return 'F'  # Fail.

    def run(self):
        t1 = time.time()
        print "----------------  Starting  --------------------------"
        while True:
            t2 = time.time()
            if t2 - t1 > 7:
                print "Sending M for mid-throttle."
                self.ser1.write('M')
                break
            string = self.ser1.readline()
            print string
            if 'zero' in string:
                while True:
                    self.start_throttle = self.initiate()
                    if self.start_throttle == 'M' or self.start_throttle == 'Z':
                        self.ser1.write(self.start_throttle)
                        self.ser1.flush()
                        break
                    else:
                        self.ser1.readline()
                break
        print "---------------  Set Velocity  -----------------------"
        # set velocity
        while True:
            string = self.ser1.readline()
            if 'speed' in string:
                while True:
                    self.chosen_velocity = self.set_velocity()
                    if self.chosen_velocity != 0:
                        break
                    else:
                        self.ser1.readline()
                self.ser1.write(self.chosen_velocity)
                self.ser1.flush()
                time.sleep(0.1)
                break

        # start running
        print "---------------  Start Running  ----------------------"
        while True:
            string = self.ser1.readline()
            if 'char' in string:
                while True:
                    start = self.start_run()
                    if start == "S":
                        self.ser2.write("S")
                        self.ser2.flush()
                        time.sleep(0.01)
                        self.ser1.write(start)
                        self.ser1.flush()
                        time.sleep(0.1)
                        break
                    else:
                        time.sleep(0.1)
                        self.ser1.readline()
                break

        # acceleration phase
        print "-------------  Acceleration Phase  --------------------"

        # Running at constant speed
        print "------------ Running at Constant Speed  ------------------"
        constant_speed = True
        while constant_speed:
            string = self.ser1.readline()
            if "off" in string:
                while True:
                    s = self.safety_check("constant")
                    if s == "y":
                        print "---------------  Turning off Motor  -----------------------"
                        self.ser1.write(s)
                        self.ser1.flush()
                        constant_speed = False
                        self.amping_down(int(self.chosen_velocity))
                        break
                else:
                    self.ser1.write(s)
                    self.ser1.flush()

        while True:
            string = self.ser1.readline()
            if "after" in string:
                print "Run finish."
                break

        # let the sled slid to rest before turning off logging.
        time.sleep(10.0)
        self.ser2.write("E")
        self.ser2.flush()
        print "---------------  Logging Stopped  -----------------------"


if __name__ == "__main__":
    experiment = RunField()
    experiment.run()

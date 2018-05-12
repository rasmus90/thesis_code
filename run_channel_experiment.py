"""
Title:      Userface for  Lab setup
Author:     RNT
About:      This script controls the engine and the logging.
            Connect the USB cabel from the MegaMoto Engine to the
            USB port furthest away from you.
            Connect the USB from the Feather LoRa to the USB port
            closest to you.

            If the script does not yield expected result, try to change
            the port for ser1 and ser2.

Arduino:    Works with the following arduino programs:
            1) Laboratory_Motor_Control.ino
            2) Radio_Transmit_Signal.ino

Webcamera:  Remember to run "ls -ltrh /dev/video*" in terminal to ensure you have
            the right device for your pipeline.
"""


import serial
import glob
import time
import shlex
from subprocess import Popen, STDOUT
import os


set_camera_parameters = False


def camera_settings():
    pipeline1 = "v4l2-ctl --device=/dev/video1 --list-ctrls"


if set_camera_parameters:
    camera_settings()

# subprocess.DEVNULL does not exist in python 2. Declare it manually.
FNULL = open(os.devnull, 'w')

# Declare pipeline: recording specifics
# run
name = raw_input("Type name of video file: ")
pipeline = "ffmpeg -f v4l2 -framerate 60 -video_size 1280x720 -input_format mjpeg -i /dev/video1 -preset faster -pix_fmt yuv420p "+name+".mkv"


port = glob.glob('/dev/ttyACM*')
# swap ports if program does not run properly
ser1 = serial.Serial(port[1], 9600, timeout=0.5)
ser2 = serial.Serial(port[0], 9600, timeout=0.5)

time.sleep(1)

found = True
while found:
    string = ser1.readline()
    s2 = ser2.readline()
    if 'G' in string:
        v = raw_input("Give string value (0 to 255): ")
        ser1.write(v)
        ser1.flush()
        found = False
        time.sleep(0.5)

found = True
while found:
    string = ser1.readline()
    if 'char' in string:
        v = raw_input("Send char S to start, other to reboot: ")
        # start recording
        p = Popen(shlex.split(pipeline), stdin=FNULL, stdout=FNULL, stderr=STDOUT)
        time.sleep(2.0)
        # start logging
        ser2.write('S')
        time.sleep(0.5)
        ser1.write(v)
        ser1.flush()
        time.sleep(0.5)
        found = False

found = True
while found:
    string = ser1.readline()
    if 'sensor' in string:
        print "Reboot"
        time.sleep(1.0)
        ser2.write('E')
        found = False
        time.sleep(0.01)
        p.terminate()

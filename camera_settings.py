"""
Run this script to set all camera settings.
"""


from subprocess import Popen, STDOUT
import shlex
import os
FNULL = open(os.devnull, 'w')

# initiate correct device

pipeline = "v4l2-ctl --device=/dev/video1 --list-ctrls"

set_exposure = "v4l2-ctl --device=/dev/video1 --set-ctrl=exposure_absolute=90"
focus_auto_0 = "v4l2-ctl --device=/dev/video1 --set-ctrl=focus_auto=0"
focus_abs = "v4l2-ctl --device=/dev/video1 --set-ctrl=focus_absolute"
focus_abs_0 = "v4l2-ctl --device=/dev/video1 --set-ctrl=focus_absolute=0"
set_gain = "v4l2-ctl --device=/dev/video1 --set-ctrl=gain=255"
white_balance = "v4l2-ctl --device=/dev/video1 --set-ctrl=white_balance_temperature_auto=0"
white_balance_val = "v4l2-ctl --device=/dev/video1 --set-ctrl=white_balance_temperature=4000"

commands = [set_exposure, focus_auto_0, focus_abs, focus_abs_0, set_gain, white_balance, white_balance_val]
Popen(shlex.split(pipeline), stdin=FNULL, stdout=FNULL, stderr=STDOUT)
for c in commands:
    print c
    Popen(shlex.split(c), stdin=FNULL, stdout=FNULL, stderr=STDOUT)

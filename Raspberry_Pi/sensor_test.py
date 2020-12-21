#! /usr/bin/python3
"""
TBD.

Classes:
    None

Misc variables:
    TBD
"""

# import math
import time
import logging
import board
import busio
import adafruit_bno055


# Initialize Logging
format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO,
                    datefmt="%Y-%m-%d : %H:%M:%S")

# Initialize i2C Connection to sensor- need check/try?
i2c = busio.I2C(board.SCL, board.SCA)
self._sensor = adafruit_bno055.BNO055_I2C(i2c)
try:
    accel_x, accel_y, accel_z = (
        self._sensor.linear_acceleration)
except RuntimeError:
    return False


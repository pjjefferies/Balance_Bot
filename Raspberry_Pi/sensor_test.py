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
import balance_bot_config as bbc


# Initialize Logging
LOG_FORMAT = '%(asctime)s — %(name)s — %(levelname)s — %(message)s'
logging.basicConfig(format=LOG_FORMAT,
                    level=bbc.LOG_LEVEL,
                    datefmt="%Y-%m-%dT%H:%M:%S")
logger = logging.getLogger(__name__)

# Initialize i2C Connection to sensor- need check/try?
i2c = busio.I2C(board.SCL, board.SCA)
sensor = adafruit_bno055.BNO055_I2C(i2c)

UPDATE_TIME = 1  # Seconds

try:
    accel_x, accel_y, accel_z = sensor.linear_acceleration
except RuntimeError:
    logger.ERROR('No Sensor Acceleration detected')
    raise

    try:
        LASTTIME_CONTROL = 0
        while True:
            if ((time.time() - LASTTIME_CONTROL) >= UPDATE_TIME):
                # exec every UPDATE_TIME seconds
                lasttime_control = time.time()
                accel_x, accel_y, accel_z = sensor.linear_acceleration
                roll, pitch, yaw = sensor.euler
                temperature = sensor.temperature
                magnetic = sensor.magnetic
                gyro = sensor.gyro
                gravity = sensor.gravity

                """
                logger.debug(f'Pos.: {POSITION:.2f}, ' +
                             'Spe.: {SPEED:.2f}, ' +
                             'Acc.: {ACCEL:.2f}, ' +
                             'Jrk.: {JERK: .2f}')
                """
    except KeyboardInterrupt:
        pass
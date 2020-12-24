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
import json
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
# Read Sensor Mode to verify connected
sensor_mode = sensor.mode

# Wait for, read and save calibration information
while sensor.calibration_status()[1] != 0x03:  # Gyro
    logger.INFO('Waiting for gyro calibration')
    time.sleep(2)
logger.INFO('Gyro calibrated')

while sensor.calibration_status()[2] != 0x03:  # Accel
    logger.INFO('Waiting for accel calibration')
    time.sleep(2)
logger.INFO('Accelerometer calibrated')

while sensor.calibration_status()[2] != 0x03:  # Mag
    logger.INFO('Waiting for magnetrometer calibration')
    time.sleep(2)
logger.INFO('Magnetrometer calibrated')

while sensor.calibration_status()[0] != 0x03:  # System
    logger.INFO('Waiting for system calibration')
    time.sleep(2)
logger.INFO('System calibrated')

# Read Calibration Data
sensor_calibration_values = {
    "accel_offset": sensor.offsets_accelerometer,
    "magnet_offset": sensor.offsets_magnetometer,
    "gyro_offset": sensor.offsets_gyroscope,
    "accel_radius": sensor.radius_accelerometer,
    "magnet_radius": sensor.radius_magnetometer}

# Save Calibration Data
with open(bbc.CALIBRATION_FILE, 'w') as fp:
    json.dump(sensor_calibration_values, fp)

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
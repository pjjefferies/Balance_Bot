#! /usr/bin/python3
"""
TBD.

Classes:
    None

Misc variables:
    TBD
"""

# import math
import datetime as dt
import time
import re
import json
import pandas as pd
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
i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_bno055.BNO055_I2C(i2c)

# Read Sensor Mode to verify connected
sensor_mode = sensor.mode

# Wait for, read and save calibration information
while sensor.calibration_status[1] != 0x03:  # Gyro
    logger.info('Waiting for gyro calibration')
    time.sleep(2)
logger.info('Gyro calibrated')

"""
while sensor.calibration_status[2] != 0x03:  # Accel
    logger.info('Waiting for accel calibration')
    time.sleep(2)
logger.info('Accelerometer calibrated')


while sensor.calibration_status[2] != 0x03:  # Mag
    logger.info('Waiting for magnetrometer calibration')
    time.sleep(2)
logger.info('Magnetrometer calibrated')

while sensor.calibration_status[0] != 0x03:  # System
    logger.info('Waiting for system calibration')
    time.sleep(2)
logger.info('System calibrated')
"""

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

update_time_measure = 1  # Seconds
update_time_save = 30

params_hist = pd.DataFrame()
try:
    lasttime_control_measure = 0
    lasttime_control_save = 0
    while True:
        if ((time.time() - lasttime_control_measure) >= update_time_measure):
            # exec every UPDATE_TIME seconds
            lasttime_control_measure = time.time()
            params = pd.Series(dtype='float64')
            print('params1:', params)
            params = params.append(pd.Series(data=sensor.linear_acceleration,
                                             index=['x_accel', 'y_accel', 'z_accel']))
            print('params2:', params)
            params = params.append(pd.Series(data=sensor.euler,
                                             index=['roll(x)', 'pitch(y)', 'yaw(z)']))
            params = params.append(pd.Series(data=sensor.temperature,
                                             index=['temperature']))
            params = params.append(pd.Series(data=sensor.magnetic,
                                             index=['mag_x', 'mag_y', 'mag_z']))
            params = params.append(pd.Series(data=sensor.gyro,
                                             index=['gyro_x', 'gyro_y', 'gyro_z']))
            params = params.append(pd.Series(data=sensor.gravity,
                                             index=['gravity_x', 'gravity_y', 'gravity_z']))

            params = params.rename(str(dt.datetime.now()))
            print('\n\nparams3:', params)
            logger.debug(str(params))

            params_hist.append(params)

        if ((time.time() - lasttime_control_save) >= update_time_save):
            sensor_history_filename = (
                'sensor_history - ' +
                re.sub(':', '', str(dt.datetime.now())) +
                '.json')
            params_hist.to_json(path_or_buf=sensor_history_filename)

except KeyboardInterrupt:
    pass

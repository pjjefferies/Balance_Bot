#! /usr/bin/python3
"""
TBD.

Classes:
    None

Misc variables:
    TBD
"""

import datetime as dt
import time
import re
import json
import logging
import pandas as pd
import board
import busio
import adafruit_bno055
from balance_bot.config import cfg

# Initialize Logging
logger = logging.getLogger(__name__)

# Initialize i2C Connection to sensor- need check/try?
i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_bno055.BNO055_I2C(i2c)

# Read Sensor Mode to verify connected
sensor_mode = sensor.mode

"""
# Wait for, read and save calibration information
while sensor.calibration_status[1] != 0x03:  # Gyro
    logger.info('Waiting for gyro calibration')
    time.sleep(2)
logger.info('Gyro calibrated')

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
"""

update_time_measure = 0  # Seconds
update_time_save = 100000    # Seconds

params_hist = pd.DataFrame()
try:
    lasttime_control_measure = 0
    lasttime_control_save = 0
    while True:
        if ((time.time() - lasttime_control_measure) >= update_time_measure):
            # exec every UPDATE_TIME seconds
            lasttime_control_measure = time.time()
            params = pd.Series(dtype='float64')
            # print('params1:', params)
            params = params.append(pd.Series(data=sensor.linear_acceleration,
                                             index=['y_accel', 'x_accel', 'z_accel']))
            # print('params2:', params)
            params = params.append(pd.Series(data=sensor.euler,
                                             index=['yaw(z)', 'roll(x)', 'pitch(y)']))
            # params = params.append(pd.Series(data=sensor.temperature,
            #                                  index=['temperature']))
            # params = params.append(pd.Series(data=sensor.magnetic,
            #                                  index=['mag_x', 'mag_y', 'mag_z']))
            params = params.append(pd.Series(data=sensor.gyro,
                                             index=['gyro_y', 'gyro_x', 'gyro_z']))
            # params = params.append(pd.Series(data=sensor.gravity,
            #                                  index=['gravity_x', 'gravity_y', 'gravity_z']))

            params = params.rename(str(dt.datetime.now()))
            # logger.debug(str(params))
            # if params['pitch(y)'] is not None:
            #     print(f'Euler Angles: ' +
            #           f'Roll(x): {params["roll(x)"]:4.1f}  ' +
            #           f'Pitch(y): {params["pitch(y)"]:4.1f}  ' +
            #           f'Yaw(z): {params["yaw(z)"]:4.1f}')
            #    logger.debug(str(params['yaw(z)']))

            # print(f'Gyro.: ' +
            #       f'gyro_x: {params["gyro_x"]:4.1f}  ' +
            #       f'gyro_y: {params["gyro_y"]:4.1f}  ' +
            #       f'gyro_z: {params["gyro_z"]:4.1f}')

            if params['x_accel'] is not None:
                print(f'Accel: ' +
                      f'Accel_x: {params["x_accel"]:4.0f}  ' +
                      f'Accel_y: {params["y_accel"]:4.0f}  ' +
                      f'Accel_z: {params["z_accel"]:4.0f}  ')
            else:
                pass
                # print('No Accel data')

            params_hist = params_hist.append(params)

        if ((time.time() - lasttime_control_save) >= update_time_save):
            logger.debug('Saving CSV File')
            lasttime_control_save = time.time()
            sensor_history_filename = (
                'sensor_history-' +
                dt.datetime.now().strftime('%Y-%m-%d_%H%M%S') +
                '.csv')
            params_hist.to_csv(path_or_buf=sensor_history_filename)

except KeyboardInterrupt:
    pass

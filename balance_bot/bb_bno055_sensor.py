#! /usr/bin/python3
"""
Create representation of Adafruit 9-DOF Abs. Orientation IMU BNO055.

This is needed to rotate axes on BNO055 Chip to Robot Axes.

Classes:
    BNO055Sensor

Methods:
	calibrate_sensor
	temperature
	accel
	magnetic
	gyro
	euler_angles
	gravity_dir
	gravity_mag
	quarternion

Misc variables:
    x
"""

import os
import math
import time
import logging
import yaml
from box import Box
import adafruit_bno055
from config import cfg

logger = logging.getLogger(__name__)


class BB_BNO055Sensor:
    """
    A class to represent the Adafruit BNO055 Sensor mounted in Balance Bot

    Attributes:
        X

    Methods:
        X
    """
    _calibration_items = ('accel_offset', 'magnet_offset', 'gyro_offset',
                          'accel_radius', 'magnet_radius')

    def __init__(self, *,
                 i2c,
                 verbose=False):
        """

        Args:
             (TYPE): DESCRIPTION.

        Returns:
            None.

        """
        self._sensor = adafruit_bno055.BNO055_I2C(i2c)

        if cfg.bno055_sensor.restore_calibration_available:
            if os.path.exists(cfg.path.calibration):
                try:
                    with open(cfg.path.log_config, "r") as ymlfile:
                        sensor_calibration_values = (
                            Box(yaml.safe_load(ymlfile)))
                    if not self._validate_calibration_data(
                            sensor_calibration_values):
                        raise ValueError('Missing configurations in ' +
                                         'Senor Cal file')
                    if input('Do you want to use saved ' +
                             'configuration?').lower.beginswith('y'):
                        self._restore_calibration(sensor_calibration_values)
                        return
                except (YAMLError, OSError, ValueError) as e:
                    logger.info('Cannot use config file: ' + e)
        else:
            logger.info('Sensor calibration restoration not available')

        self.calibrate_sensor(verbose=verbose)

    def calibrate_sensor(self, verbose=False):
        """
        Check for sensor calibraiton file and offer to use it, otherwise,
        wait for sensor calibrations and notify of status regularly. If
        calibrating, save calibration data.

        Returns:
            None.

        """

        # Wait for, read and save calibration information
        while self._sensor.calibration_status[1] != 0x03:  # Gyro
            logger.info('Waiting for gyro calibration')
            time.sleep(2)
        logger.info('Gyro calibrated')

        while self._sensor.calibration_status[2] != 0x03:  # Accel
            logger.info('Waiting for accel calibration')
            time.sleep(2)
        logger.info('Accelerometer calibrated')


        while self._sensor.calibration_status[2] != 0x03:  # Mag
            logger.info('Waiting for magnetrometer calibration')
            time.sleep(2)
        logger.info('Magnetrometer calibrated')

        while self._sensor.calibration_status[0] != 0x03:  # System
            logger.info('Waiting for system calibration')
            time.sleep(2)
        logger.info('System calibrated')

        # Read Calibration Data
        sensor_calibration_data = {
            'accel_offset': self._sensor.offsets_accelerometer,
            'magnet_offset': self._sensor.offsets_magnetometer,
            'gyro_offset': self._sensor.offsets_gyroscope,
            'accel_radius': self._sensor.radius_accelerometer,
            'magnet_radius': self._sensor.radius_magnetometer}

        self._save_calibration(sensor_calibration_data)

    def _save_calibration(self, sensor_calibration_data):
        """Saves calibration data from dictionary to yaml file in configs folder"""
        if not self._validate_bno055_sensor_calibration_data(sensor_calibration_data):
            logger.error('Could not save calibration data. Data invalid')
            return
        with open(cfg.path.calibration, 'w') as fp:
            yaml.dump(sensor_calibration_data, stream=fp,
                      default_flow_style=True, sort_keys=True)
        logger.info('Calibration data saved')

    def _restore_calibration(self):
        """
        Saves calibration data from dictionary to bno055 Sensor for use
        When we figure-out how to do that
        """

    def _validate_calibration_data(self, sensor_calibration_data):
        if not all(item in sensor_calibration_data for
                           item in BB_BNO055Sensor._calibration_items):
            return False

    @property
    def temperature(self, units="degrees celsius"):
        """
        Getter for temperature readings

        Returns:
            temperature in specified units.
        """
        if units in ("degrees Fahrenheit", "degrees F", "deg F", "deg. F"):
            return self._sensor.temperature * 9 / 5 + 32
        else:
            return self._sensor.temperature

    @property
    def accel(self):
        """
        Getter for acceleration readings

        Returns:
            3-tuple of X, Y, Z axis accelerrometer values in meters/sec.^2
            data=sensor.linear_acceleration,
                                             index=['y_accel', 'x_accel', 'z_accel']))
        """
        accel_y, accel_x, accel_z = self._sensor.linear_acceleration
        return {'x': accel_x, 'y': accel_y, 'z': accel_z}

    @property
    def magnetic(self):
        """
        Getter for magnetic field strength readings

        Returns:
            3-tuple of X, Y, Z megnetometer values in microteslas
        """
        mag_x, mag_y, mag_z = self._sensor.magnetic  # ORDER NOT VERIFIED
        return {'x': mag_x, 'y': mag_y, 'z': mag_z}

    @property
    def gyro(self):
        """
        Getter for gyroscope readings

        Returns:
            3-tuple of X, Y, Z axis gyroscope values in degrees/sec.
        """
        gyro_y, gyro_x, gyro_z = self._sensor.gyro
        return {'x': gyro_x, 'y': gyro_y, 'z': gyro_z}

    @property
    def euler_angles(self):
        """
        Getter for Euler angle orientation of sensor

        Returns:
            3-tuple of orientation angles
        """
        yaw_z, roll_x, pitch_y = self._sensor.euler
        return {'x': roll_x, 'y': pitch_y, 'z': yaw_z}

    @property
    def gravity_dir(self):
        """
        Getter for gravity direction readings

        Returns:
            2-tuple of XY and XZ angle orientations of gravity vector
        """
        x_grav, y_grav, z_grav = self._sensor.gravity
        xy_grav_angle = math.atan2(y_grav, x_grav)
        xz_grav_angle = math.atan2(z_grav, x_grav)
        return {'xy': xy_grav_angle,
                'xz': xz_grav_angle}  # ORDER NOT VERIVIED

    @property
    def gravity_mag(self):
        """
        Getter for gravity magnitude readings

        Returns:
            magnitude of gravity vector        # ORDER NOT VERIFIED
        """
        return math.sqrt(sum([x**2 for x in self._sensor.gravity]))

    @property
    def quaternion(self):
        """
        Getter for quaternion giving orientation

        Returns:
            4-tuple quaternion
        """
        return self._sensor.quaternion  # ORDER NOT VERIFIED

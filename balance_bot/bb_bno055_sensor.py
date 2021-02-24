#! /usr/bin/python3
"""
Create representation of Adafruit 9-DOF Abs. Orientation IMU BNO055.

X

Classes:
    BNO055Sensor

Misc variables:
    x
"""

import math
import logging
from config import cfg
# import time
# import busio
import adafruit_bno055
from balance_bot.config import cfg

logger = logging.getLogger(__name__)


class BB_BNO055Sensor:
    """
    A class to represent the Adafruit BNO055 Sensor mounted in Balance Bot

    Attributes:
        X

    Methods:
        X
    """
    def __init__(self,
                 i2c):
        """

        Args:
             (TYPE): DESCRIPTION.

        Returns:
            None.

        """
        self._sensor = adafruit_bno055.BNO055_I2C(i2c)

    def _sensor_cal(self):
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

    def
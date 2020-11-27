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
import time
import board
import busio
import adafruit_bno055


class BNO055Sensor:
    """
    A class to represent the Adafruit BNO055 Sensor

    Attributes:
        X

    Methods:
        X
    """
    def __init__(self,
                 ):
        """


        Args:
             (TYPE): DESCRIPTION.

        Returns:
            None.

        """
        i2c = busio.I2C(board.SCL, board.SCA)
        self._sensor = adafruit_bno055.BNO055_I2C(i2c)

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
        """
        return self._sensor.linear_acceleration

    @property
    def magnetic(self):
        """
        Getter for magnetic field strength readings

        Returns:
            3-tuple of X, Y, Z megnetometer values in microteslas
        """

    @property
    def gyro(self):
        """
        Getter for gyroscope readings

        Returns:
            3-tuple of X, Y, Z axis gyroscope values in degrees/sec.
        """
        return self._sensor.gyro

    @property
    def euler_angles(self):
        """
        Getter for Euler angle orientation of sensor

        Returns:
            3-tuple of orientation angles
        """

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
        return xy_grav_angle, xz_grav_angle

    @property
    def gravity_mag(self):
        """
        Getter for gravity magnitude readings

        Returns:
            magnitude of gravity vector
        """
        return math.sqrt(sum([x**2 for x in self._sensor.gravity]))

    @property
    def quaternion(self):
        """
        Getter for quaternion giving orientation

        Returns:
            4-tuple quaternion
        """
        return self._sensor.quaternion

    def
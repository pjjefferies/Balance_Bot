#! /usr/bin/python3
"""
Create representation of Simulated Adafruit 9-DOF Abs. Orientation IMU BNO055.

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
import random
import math
import logging

# from box import Box
# from config import cfg

logger = logging.getLogger(__name__)


class BB9DOFSensorSimulator:
    """
    A class to simulate the Adafruit BNO055 Sensor mounted in Balance Bot

    Attributes:
        X

    Methods:
        X
    """

    def __init__(self) -> None:
        """
        Args:
            None

        Returns:
            None

        """

        # self.calibrate_sensor()

    def calibrate_sensor(self) -> None:
        """
        Check for sensor calibraiton file and offer to use it, otherwise,
        wait for sensor calibrations and notify of status regularly. If
        calibrating, save calibration data.

        Returns:
            None.

        """

        # Not sure if this is necessary
        pass

    def temperature(self, units: str = "degrees celsius") -> int:
        """
        Getter for temperature readings

        Returns:
            temperature in specified units.
        """
        a_temp = int(random.random() * 10 + 65)
        if units in ("degrees Fahrenheit", "degrees F", "deg F", "deg. F", "°F"):
            return int(a_temp * 9 / 5 + 32)
        else:
            return a_temp

    @property
    def accel(self) -> dict[str, float]:
        """
        Getter for acceleration readings

        Returns:
            Dict of X, Y, Z axis accelerrometer values in meters/sec.^2
        """
        accel_x: float = random.random() * 2 - 1  # -1 to 1
        accel_y: float = random.random() * 2 / 10 - 0.1  # -0.1 to 0.1
        accel_z: float = random.random() * 2 / 10 - 0.1  # -0.1 to 0.1
        return {"x": accel_x, "y": accel_y, "z": accel_z}

    @property
    def magnetic_bb(self) -> dict[str, float]:
        """
        Getter for magnetic field strength readings

        Returns:
            Dict of X, Y, Z megnetometer values in microteslas
        """
        mag_x: float = 1.0
        mag_y: float = 0
        mag_z: float = 0
        return {"x": mag_x, "y": mag_y, "z": mag_z}

    @property
    def gyro_bb(self) -> dict[str, float]:
        """
        Getter for gyroscope readings

        Returns:
            Dict of X, Y, Z axis gyroscope values in degrees/sec.
        """
        gyro_x: float = random.random() * 2 / 10 - 0.1  # -0.1 to 0.1
        gyro_y: float = random.random() * 2 / 5 - 0.2  # -0.2 to 0.2
        gyro_z: float = random.random() * 2 / 10 - 0.1  # -0.1 to 0.1
        return {"x": gyro_x, "y": gyro_y, "z": gyro_z}

    @property
    def euler_angles(self) -> dict[str, float]:
        """
        Getter for Euler angle orientation of sensor

        Returns:
            3-tuple of orientation angles
        """
        yaw_z: float = 0.0
        roll_x: float = 0.0
        pitch_y: float = 0.0
        return {"x": roll_x, "y": pitch_y, "z": yaw_z}

    @property
    def gravity_dir(self) -> dict[str, float]:
        """
        Getter for gravity direction readings

        Returns:
            2-tuple of XY and XZ angle orientations of gravity vector
        """
        x_grav: float = 0.0
        y_grav: float = 0.0
        z_grav: float = -1.0
        xy_grav_angle: float = math.atan2(y_grav, x_grav)
        xz_grav_angle: float = math.atan2(z_grav, x_grav)
        return {"xy": xy_grav_angle, "xz": xz_grav_angle}  # ORDER NOT VERIVIED

    @property
    def gravity_mag(self) -> float:
        """
        Getter for gravity magnitude readings

        Returns:
            magnitude of gravity vector        # ORDER NOT VERIFIED
        """
        x_grav: float = 0.0
        y_grav: float = 0.0
        z_grav: float = -1.0
        return math.sqrt(sum([x_grav**2, y_grav**2, z_grav**2]))

    """
    @property
    def quaternion_bb(self) -> tuple[int, ]:

        Getter for quaternion giving orientation

        Returns:
            4-tuple quaternion

        return self._sensor.quaternion  # ORDER NOT VERIFIED
    """

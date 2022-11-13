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
from typing import Protocol
from abc import abstractmethod
import os
import math
import time
import logging
import yaml
from box import Box
from config import cfg

logger = logging.getLogger(__name__)

"""
class PinProt(Protocol):
    def __init__(self, bcm_number: int):
        raise NotImplementedError

    def init(self, mode: int, pull: int) -> None:
        raise NotImplementedError

    def value(self, val: int | None) -> int | None:
        # method to read (if val is None) or write
        raise NotImplementedError


class CommProtocol(Protocol):  # Generic i2c protocol
    @abstractmethod
    def write_then_readinto(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def write(self) -> None:
        raise NotImplementedError
"""


class AbsoluteSensor(Protocol):
    def __init__(self) -> None:
        raise NotImplementedError

    @property
    def calibration_status(self) -> tuple[int, int, int, int]:
        raise NotImplementedError

    @property
    @abstractmethod
    def accel_range(self) -> int:
        raise NotImplementedError

    @accel_range.setter
    @abstractmethod
    def accel_range(self, rng: int) -> None:
        raise NotImplementedError

    @property
    @abstractmethod
    def offsets_accelerometer(self) -> tuple[int, int, int]:
        raise NotImplementedError

    @property
    @abstractmethod
    def offsets_magnetometer(self) -> tuple[int, int, int]:
        raise NotImplementedError

    @property
    @abstractmethod
    def offsets_gyroscope(self) -> tuple[int, int, int]:
        raise NotImplementedError

    @property
    @abstractmethod
    def radius_accelerometer(self) -> int:
        raise NotImplementedError

    @property
    @abstractmethod
    def radius_magnetometer(self) -> int:
        raise NotImplementedError

    @property
    @abstractmethod
    def temperature(self) -> int:
        raise NotImplementedError

    @property
    @abstractmethod
    def linear_acceleration(self) -> tuple[float | None, float | None, float | None]:
        raise NotImplementedError

    @property
    @abstractmethod
    def magnetic(self) -> tuple[int | None, int | None, int | None]:
        raise NotImplementedError

    @property
    @abstractmethod
    def gyro(self) -> tuple[int | None, int | None, int | None]:
        raise NotImplementedError

    @property
    @abstractmethod
    def euler(self) -> tuple[int | None, int | None, int | None]:
        raise NotImplementedError

    @property
    @abstractmethod
    def quaternion(self) -> tuple[int | None, int | None, int | None, int | None]:
        raise NotImplementedError

    @property
    @abstractmethod
    def gravity(self) -> tuple[float | None, float | None, float | None]:
        raise NotImplementedError


class BB_BNO055Sensor:
    """
    A class to represent the Adafruit BNO055 Sensor mounted in Balance Bot

    Attributes:
        X

    Methods:
        X
    """

    _calibration_items = (
        "accel",
        # "accel.offset",
        # "accel.radius",
        # "accel.range",
        "magnet",
        # "magnet.offset",
        # "magnet.radius",
        "gyro",
        # "gyro.offset",
    )

    def __init__(self, *, sensor: AbsoluteSensor) -> None:
        """
        Args:
             (TYPE): DESCRIPTION.

        Returns:
            None.

        """
        # self._sensor: adafruit_bno055.BNO055_I2C = adafruit_bno055.BNO055_I2C(i2c)
        self._sensor = sensor

        # self._sensor.accel_range =
        self.calibrate_sensor()

    def calibrate_sensor(self) -> None:
        """
        Check for sensor calibraiton file and offer to use it, otherwise,
        wait for sensor calibrations and notify of status regularly. If
        calibrating, save calibration data.

        Returns:
            None.

        """

        # Wait for, read and save calibration information
        while self._sensor.calibration_status[1] != 0x03:  # Gyro
            logger.info("Waiting for gyro calibration")
            time.sleep(2)
        logger.info("Gyro calibrated")

        while self._sensor.calibration_status[2] != 0x03:  # Accel
            logger.info("Waiting for accel calibration")
            time.sleep(2)
        logger.info("Accelerometer calibrated")

        while self._sensor.calibration_status[2] != 0x03:  # Mag
            logger.info("Waiting for magnetrometer calibration")
            time.sleep(2)
        logger.info("Magnetrometer calibrated")

        while self._sensor.calibration_status[0] != 0x03:  # System
            logger.info("Waiting for system calibration")
            time.sleep(2)
        logger.info("System calibrated")

        # Read Calibration Data
        acc_offset_x: int
        acc_offset_y: int
        acc_offset_z: int
        acc_offset_x, acc_offset_y, acc_offset_z = self._sensor.offsets_accelerometer
        mag_offset_x: int
        mag_offset_y: int
        mag_offset_z: int
        mag_offset_x, mag_offset_y, mag_offset_z = self._sensor.offsets_magnetometer
        gyr_offset_x: int
        gyr_offset_y: int
        gyr_offset_z: int
        gyr_offset_x, gyr_offset_y, gyr_offset_z = self._sensor.offsets_gyroscope

        sensor_calibration_data: dict[
            str, dict[str, dict[str, int] | int] | dict[str, dict[str, int]]
        ] = {
            "accel": {
                "offset": {"x": acc_offset_x, "y": acc_offset_y, "z": acc_offset_z},
                "radius": self._sensor.radius_accelerometer,
            },
            "magnet": {
                "offset": {"x": mag_offset_x, "y": mag_offset_y, "z": mag_offset_z},
                "radius": self._sensor.radius_magnetometer,
            },
            "gyro": {
                "offset": {"x": gyr_offset_x, "y": gyr_offset_y, "z": gyr_offset_z}
            },
        }

        self._save_calibration(sensor_calibration_data)

    def _save_calibration(
        self,
        sensor_calibration_data: dict[
            str, dict[str, dict[str, int] | int] | dict[str, dict[str, int]]
        ],
    ) -> None:
        """Saves calibration data from dictionary to yaml file in configs folder"""
        if not self._validate_calibration_data(sensor_calibration_data):
            logger.error("Could not save calibration data. Data invalid")
            return
        with open(cfg.path.calibration, "w") as fp:
            yaml.dump(
                sensor_calibration_data,
                stream=fp,
                default_flow_style=True,
                sort_keys=True,
            )
        logger.info(f"Calibration data saved: {sensor_calibration_data}")

    def _restore_calibration(self) -> bool:
        """
        Saves calibration data from dictionary to bno055 Sensor for use
        When we figure-out how to do that
        """
        if cfg.bno055_sensor.restore_calibration_available:
            # Import 9DOF Sensor Configuration if available
            if os.path.exists(cfg.path.ninedof_sensor_calibration):
                try:
                    with open(
                        cfg.path.ninedof_sensor_calibration, "r"
                    ) as ninedof_sensor_cfg_file:
                        ninedof_sensor_config: Box | None = Box(
                            yaml.safe_load(ninedof_sensor_cfg_file)
                        )
                    if not self._validate_calibration_data(ninedof_sensor_config):
                        logger.warning("Nine DOF Calibration Data is not valid")
                        return False
                except (yaml.YAMLError, OSError, ValueError) as e:
                    logger.warning(f"Cannot use config file: {e}")
                    return False
            else:
                logger.warning(
                    f"Path, {cfg.path.ninedof_sensor_calibration} does not exist"
                )
                return False
        else:
            logger.info("Sensor calibration restoration not available")
            return False
        logger.warning(
            "Cannot restore calibration data, haven't found a way to do that yet"
        )
        return False

    def _validate_calibration_data(
        self,
        sensor_calibration_data: dict[
            str, dict[str, dict[str, int] | int] | dict[str, dict[str, int]]
        ],
    ) -> bool:
        return all(
            item in sensor_calibration_data
            for item in BB_BNO055Sensor._calibration_items
        )

    def temperature(self, units: str = "degrees celsius") -> int:
        """
        Getter for temperature readings

        Returns:
            temperature in specified units.
        """
        if units in ("degrees Fahrenheit", "degrees F", "deg F", "deg. F", "°F"):
            return int(self._sensor.temperature * 9 / 5 + 32)
        else:
            return self._sensor.temperature

    @property
    def accel(self) -> dict[str, float]:
        """
        Getter for acceleration readings

        Returns:
            Dict of X, Y, Z axis accelerrometer values in meters/sec.^2
        """
        accel_x: float | None
        accel_y: float | None
        accel_z: float | None
        accel_y, accel_x, accel_z = self._sensor.linear_acceleration
        if accel_x is None or accel_y is None or accel_z is None:
            raise ValueError("Accel not available, check mode")
        return {"x": accel_x, "y": accel_y, "z": accel_z}

    @property
    def magnetic_bb(self) -> dict[str, float]:
        """
        Getter for magnetic field strength readings

        Returns:
            Dict of X, Y, Z megnetometer values in microteslas
        """
        mag_x: float | None
        mag_y: float | None
        mag_z: float | None
        mag_x, mag_y, mag_z = self._sensor.magnetic  # ORDER NOT VERIFIED
        if mag_x is None or mag_y is None or mag_z is None:
            raise ValueError("Magnetic reading not available, check mode")
        return {"x": mag_x, "y": mag_y, "z": mag_z}

    @property
    def gyro_bb(self) -> dict[str, float]:
        """
        Getter for gyroscope readings

        Returns:
            Dict of X, Y, Z axis gyroscope values in degrees/sec.
        """
        gyro_x: float | None
        gyro_y: float | None
        gyro_z: float | None
        gyro_y, gyro_x, gyro_z = self._sensor.gyro
        if gyro_x is None or gyro_y is None or gyro_z is None:
            raise ValueError("Gyro not available, check mode")
        return {"x": gyro_x, "y": gyro_y, "z": gyro_z}

    @property
    def euler_angles(self) -> dict[str, float]:
        """
        Getter for Euler angle orientation of sensor

        Returns:
            3-tuple of orientation angles
        """
        yaw_z: float | None
        roll_x: float | None
        pitch_y: float | None
        yaw_z, roll_x, pitch_y = self._sensor.euler
        if yaw_z is None or roll_x is None or pitch_y is None:
            raise ValueError("Euler angles not available, check mode")
        return {"x": roll_x, "y": pitch_y, "z": yaw_z}

    @property
    def gravity_dir(self) -> dict[str, float]:
        """
        Getter for gravity direction readings

        Returns:
            2-tuple of XY and XZ angle orientations of gravity vector
        """
        x_grav: float | None
        y_grav: float | None
        z_grav: float | None
        x_grav, y_grav, z_grav = self._sensor.gravity
        if x_grav is None or y_grav is None or z_grav is None:
            raise ValueError("Gravity not available, check mode")
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
        x_grav: float | None
        y_grav: float | None
        z_grav: float | None
        x_grav, y_grav, z_grav = self._sensor.gravity
        x_grav = x_grav if x_grav is not None else 0
        y_grav = y_grav if y_grav is not None else 0
        z_grav = z_grav if z_grav is not None else 0
        return math.sqrt(sum([x_grav**2, y_grav**2, z_grav**2]))

    """
    @property
    def quaternion_bb(self) -> tuple[int, ]:

        Getter for quaternion giving orientation

        Returns:
            4-tuple quaternion

        return self._sensor.quaternion  # ORDER NOT VERIFIED
    """

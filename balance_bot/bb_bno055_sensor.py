#!/usr/bin/env python3
"""
Create representation of Adafruit 9-DOF Abs. Orientation IMU BNO055.

This is needed to rotate axes on BNO055 Chip to Robot Axes.
"""

from abc import abstractmethod
from box import Box
import math
import time
from typing import Optional, Protocol

import adafruit_bno055 as bno055
from box import Box
from box.exceptions import BoxError
import busio

from balance_bot.config_main import cfg
from balance_bot.event import EventHandler


class EventHandlerTemplate(Protocol):
    def post(self, *, event_type: str, message: str) -> None:
        raise NotImplementedError


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
    def linear_acceleration(
        self,
    ) -> tuple[Optional[float], Optional[float], Optional[float]]:
        raise NotImplementedError

    @property
    @abstractmethod
    def magnetic(self) -> tuple[Optional[float], Optional[float], Optional[float]]:
        raise NotImplementedError

    @property
    @abstractmethod
    def gyro(self) -> tuple[Optional[float], Optional[float], Optional[float]]:
        raise NotImplementedError

    @property
    @abstractmethod
    def euler(self) -> tuple[Optional[float], Optional[float], Optional[float]]:
        raise NotImplementedError

    @property
    @abstractmethod
    def quaternion(
        self,
    ) -> tuple[Optional[float], Optional[float], Optional[float], Optional[float]]:
        raise NotImplementedError

    @property
    @abstractmethod
    def gravity(
        self,
    ) -> tuple[Optional[float], Optional[float], Optional[float]]:
        raise NotImplementedError


class BB_BNO055Sensor_I2C(bno055.BNO055_I2C):
    """
    A class to represent the Adafruit BNO055 Sensor mounted in Balance Bot
    """

    _calibration_items = (
        "accel",
        "accel.offset",
        "accel.radius",
        "accel.range",
        "magnet",
        "magnet.offset",
        "magnet.radius",
        "gyro",
        "gyro.offset",
    )

    def __init__(
        self, *, i2c: busio.I2C, eh: EventHandler
    ) -> None:  # sensor: AbsoluteSensor, V3.10

        # self._sensor: bno055.BNO055_I2C = bno055.BNO055_I2C(i2c)
        super().__init__(i2c=i2c)
        self._sensor_calibration_data: Box = Box(
            {
                "accel": {
                    "offset": {"x": 0, "y": 0, "z": 0},
                    "radius": 0,
                },
                "magnet": {
                    "offset": {"x": 0, "y": 0, "z": 0},
                    "radius": 0,
                },
                "gyro": {"offset": {"x": 0, "y": 0, "z": 0}},
            }
        )
        self._eh = eh

    def calibrate_sensor(self) -> None:
        """
        Wait for sensor calibrations and notify of status regularly.
        """

        # Wait for and read calibration information
        while self.calibration_status[2] != 0x03:  # Accel
            self._eh.post(
                event_type="9DOF sensor",
                message="Waiting for accel calibration. Rotate robot slowly to 6 stable positions for a few seconds.",
            )
            time.sleep(1)
        self._eh.post(
            event_type="9DOF sensor", message="Accelerometer calibrated"
        )

        while self.calibration_status[1] != 0x03:  # Gyro
            self._eh.post(
                event_type="9DOF sensor",
                message="Waiting for gyro calibration. Place robot in a stable position.",
            )
            time.sleep(1)
        self._eh.post(event_type="9DOF sensor", message="Gyro calibrated")

        while self.calibration_status[3] != 0x03:  # Mag
            self._eh.post(
                event_type="9DOF sensor",
                message="Waiting for magnetrometer calibration. Rotate robot in random directions.",
            )
            time.sleep(2)
        self._eh.post(
            event_type="9DOF sensor", message="Magnetrometer calibrated"
        )

        while self.calibration_status[0] != 0x03:  # System
            self._eh.post(
                event_type="9DOF sensor", message="Waiting for system calibration"
            )
            time.sleep(2)
        self._eh.post(event_type="9DOF sensor", message="System calibrated")

    def read_calibration_data_from_sensor(self) -> Box:
        # if self.calibration_status[0] != 0x03:
        #     raise ValueError("Sensor not calibrated, calibration values not available")

        acc_offset_x: int
        acc_offset_y: int
        acc_offset_z: int
        acc_offset_x, acc_offset_y, acc_offset_z = self.offsets_accelerometer
        mag_offset_x: int
        mag_offset_y: int
        mag_offset_z: int
        mag_offset_x, mag_offset_y, mag_offset_z = self.offsets_magnetometer
        gyr_offset_x: int
        gyr_offset_y: int
        gyr_offset_z: int
        gyr_offset_x, gyr_offset_y, gyr_offset_z = self.offsets_gyroscope
        acc_radius: int | tuple[int, int, int] = self.radius_accelerometer
        mag_radius: int | tuple[int, int, int] = self.radius_magnetometer

        self._sensor_calibration_data: Box = Box(
            {
                "accel": {
                    "offset": {"x": acc_offset_x, "y": acc_offset_y, "z": acc_offset_z},
                    "radius": acc_radius,
                },
                "magnet": {
                    "offset": {"x": mag_offset_x, "y": mag_offset_y, "z": mag_offset_z},
                    "radius": mag_radius,
                },
                "gyro": {
                    "offset": {"x": gyr_offset_x, "y": gyr_offset_y, "z": gyr_offset_z}
                },
            }
        )
        self._eh.post(
            event_type="9DOF sensor",
            message=f"Calibration Values:\n{self._sensor_calibration_data}",
        )
        return self._sensor_calibration_data

    def write_calibration_data_to_sensor(
        self, sensor_calibration_data: Optional[Box]
    ) -> None:
        if sensor_calibration_data is None:
            sensor_calibration_data = self._sensor_calibration_data
        if not self._validate_calibration_data(sensor_calibration_data):
            self._eh.post(
                event_type="log",
                message="ERROR: Could not save calibration data. Data invalid",
            )
            raise ValueError("Could not save calibration data")
        self.offsets_accelerometer = (
            sensor_calibration_data.accel.offset.x,
            sensor_calibration_data.accel.offset.y,
            sensor_calibration_data.accel.offset.z,
        )
        self.offsets_magnetometer = (
            sensor_calibration_data.magnet.offset.x,
            sensor_calibration_data.magnet.offset.y,
            sensor_calibration_data.magnet.offset.z,
        )
        self.offsets_gyroscope = (
            sensor_calibration_data.gyro.offset.x,
            sensor_calibration_data.gyro.offset.y,
            sensor_calibration_data.gyro.offset.z,
        )
        self.radius_accelerometer = sensor_calibration_data.accel.radius
        self.radius_magnetometer = sensor_calibration_data.magnet.radius

    def read_calibration_data_from_file(self) -> Box:
        """Loads calibration data from configuration file, saves it in object and returns it"""
        try:
            self._sensor_calibration_data = Box.from_yaml(
                filename=cfg.path.ninedof_sensor_calibration
            )
            if not self._validate_calibration_data(self._sensor_calibration_data):
                print(f"Cal. Data:{self._sensor_calibration_data}")
                raise ValueError("Calibration data from file is invalid")
        except BoxError as e:
            raise ValueError(e)
        except ValueError as e:
            raise ValueError(e)

        self._eh.post(
            event_type="9DOF sensor",
            message=f"Calibration values read from {cfg.path.calibration}:\n{self._sensor_calibration_data}",
        )

        return self._sensor_calibration_data

    def write_calibration_data_to_file(
        self, sensor_calibration_data: Optional[Box]
    ) -> None:
        """Saves calibration data from Box to yaml file in configs folder"""
        if sensor_calibration_data is None:
            sensor_calibration_data = self._sensor_calibration_data
        if not self._validate_calibration_data(sensor_calibration_data):
            raise ValueError("Could not save calibration data")

        sensor_calibration_data.to_yaml(
            filename=cfg.path.ninedof_sensor_calibration
        )

        self._eh.post(
            event_type="9DOF sensor",
            message=f"Calibration data saved to {cfg.path.ninedof_sensor_calibration}:\n{sensor_calibration_data}",
        )

    @classmethod
    def _validate_calibration_data(cls, sensor_calibration_data: Box) -> bool:
        """Validate passed calibration data"""
        try:
            float(sensor_calibration_data.accel.offset.x)
            float(sensor_calibration_data.accel.offset.y)
            float(sensor_calibration_data.accel.offset.z)
            float(sensor_calibration_data.magnet.offset.x)
            float(sensor_calibration_data.magnet.offset.y)
            float(sensor_calibration_data.magnet.offset.z)
            float(sensor_calibration_data.gyro.offset.x)
            float(sensor_calibration_data.gyro.offset.y)
            float(sensor_calibration_data.gyro.offset.z)
            float(sensor_calibration_data.accel.radius)
            float(sensor_calibration_data.magnet.radius)
            return True
        except (ValueError, AttributeError, BoxError):
            return False

    def bb_temperature(self, units: str = "degrees celsius") -> int:
        """Getter for temperature readings"""
        temperature: int
        if units in ("degrees Fahrenheit", "degrees F", "deg F", "deg. F", "°F"):
            temperature = int(self.temperature * 9 / 5 + 32)
        else:
            temperature = self.temperature

        self._eh.post(
            event_type="9DOF sensor",
            message=f"Temperature: {temperature} {units}",
        )
        return temperature

    @property
    def accel(self) -> Box:
        accel_x: Optional[float]
        accel_y: Optional[float]
        accel_z: Optional[float]
        accel_y, accel_x, accel_z = self.linear_acceleration
        if accel_x is None or accel_y is None or accel_z is None:
            raise ValueError("Accel not available, check mode")
        self._eh.post(
            event_type="9DOF sensor",
            message=f"Accel: x: {accel_x}, y: {accel_y}, z: {accel_z}",
        )
        return Box({"x": accel_x, "y": accel_y, "z": accel_z})

    @property
    def bb_magnetic(self) -> Box:
        mag_x: Optional[float]
        mag_y: Optional[float]
        mag_z: Optional[float]
        mag_x, mag_y, mag_z = self.magnetic  # ORDER NOT VERIFIED
        if mag_x is None or mag_y is None or mag_z is None:
            raise ValueError("Magnetic reading not available, check mode")
        self._eh.post(
            event_type="9DOF sensor",
            message=f"Magnetic Field: x: {mag_x}, y: {mag_y}, z: {mag_z}",
        )
        return Box({"x": mag_x, "y": mag_y, "z": mag_z})

    @property
    def bb_gyro(self) -> Box:
        gyro_x: Optional[float]
        gyro_y: Optional[float]
        gyro_z: Optional[float]
        gyro_y, gyro_x, gyro_z = self.gyro  # Ordered for BB Axes ?
        if gyro_x is None or gyro_y is None or gyro_z is None:
            raise ValueError("Gyro not available, check mode")
        self._eh.post(
            event_type="9DOF sensor",
            message=f"Gyro: x: {gyro_x:.2f}, y: {gyro_y:.2f}, z: {gyro_z:.2f}",
        )
        return Box({"x": gyro_x, "y": gyro_y, "z": gyro_z})

    @property
    def euler_angles(self) -> Box:
        """Getter for Euler angle orientation of sensor"""
        yaw_z: Optional[float]
        roll_x: Optional[float]
        pitch_y: Optional[float]
        yaw_z, roll_x, pitch_y = self.euler
        if yaw_z is None or roll_x is None or pitch_y is None:
            # raise ValueError("Euler angles not available, check mode")
            print("Euler angles not available, please try again")
            return Box({"x": 0, "y": 0, "z": 0})
        self._eh.post(
            event_type="9DOF sensor",
            message=f"roll: x: {roll_x:.2f}, pitch y: {pitch_y:.2f}, yaw z: {yaw_z:.2f}",
        )
        return Box({"x": roll_x, "y": pitch_y, "z": yaw_z})

    @property
    def gravity_dir(self) -> Box:
        """
        Getter for gravity direction readings

        Returns:
            2-tuple of XY and XZ angle orientations of gravity vector
        """
        x_grav: Optional[float]
        y_grav: Optional[float]
        z_grav: Optional[float]
        x_grav, y_grav, z_grav = self.gravity
        if x_grav is None or y_grav is None or z_grav is None:
            raise ValueError("Gravity not available, check mode")
        xy_grav_angle: float = math.atan2(y_grav, x_grav)
        xz_grav_angle: float = math.atan2(z_grav, x_grav)
        self._eh.post(
            event_type="9DOF sensor",
            message=f"Gravity Dir: xy_angle: {xy_grav_angle}, xz_angle: {xz_grav_angle}",
        )
        return Box({"xy": xy_grav_angle, "xz": xz_grav_angle})  # ORDER NOT VERIVIED

    @property
    def gravity_mag(self) -> float:
        """Getter for gravity magnitude readings"""
        x_grav: Optional[float]
        y_grav: Optional[float]
        z_grav: Optional[float]
        x_grav, y_grav, z_grav = self.gravity  # ORDER NOT VERIFIED
        x_grav = x_grav if x_grav is not None else 0
        y_grav = y_grav if y_grav is not None else 0
        z_grav = z_grav if z_grav is not None else 0
        grav_mag: float = math.sqrt(sum([x_grav**2, y_grav**2, z_grav**2]))
        self._eh.post(
            event_type="9DOF sensor",
            message=f"Gravity Magnitude: {grav_mag}",
        )
        return grav_mag

    @property
    def quaternion(self) -> tuple[float, float, float, float]:
        """
        Getter for quaternion giving orientation

        Returns:
            4-tuple quaternion
        """
        quaternion: tuple[
            Optional[float], Optional[float], Optional[float], Optional[float]
        ] = self.quaternion  # ORDER NOT VERIFIED
        if None in quaternion:
            raise ValueError("Quaternion is not available")
        return quaternion

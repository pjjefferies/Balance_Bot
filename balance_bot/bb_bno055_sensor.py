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
from typing import Dict, Union  # Protocol

# from abc import abstractmethod
import os
import math
import time
import yaml
from box import Box
from config import cfg
from event import EventHandler
import adafruit_bno055
import busio

"""
Not needed until Python V3.10 can be implemented on Raspberry Pi. As of Dec. 2022, dbus package does
not work with 32-bit Linux (e.g. Raspberry Pi).


class EventHandlerTemplate(Protocol):
    def post(self, *, event_type: str, message: str) -> None:
        raise NotImplementedError


class AbsoluteSensor(Protocol):
    def __init__(self) -> None:
        raise NotImplementedError

    @property
    def calibration_status(self) -> Tuple[int, int, int, int]:
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
    def offsets_accelerometer(self) -> Tuple[int, int, int]:
        raise NotImplementedError

    @property
    @abstractmethod
    def offsets_magnetometer(self) -> Tuple[int, int, int]:
        raise NotImplementedError

    @property
    @abstractmethod
    def offsets_gyroscope(self) -> Tuple[int, int, int]:
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
    ) -> Tuple[Union[float, None], Union[float, None], Union[float, None]]:
        raise NotImplementedError

    @property
    @abstractmethod
    def magnetic(self) -> Tuple[Union[int, None], Union[int, None], Union[int, None]]:
        raise NotImplementedError

    @property
    @abstractmethod
    def gyro(self) -> Tuple[Union[int, None], Union[int, None], Union[int, None]]:
        raise NotImplementedError

    @property
    @abstractmethod
    def euler(self) -> Tuple[Union[int, None], Union[int, None], Union[int, None]]:
        raise NotImplementedError

    @property
    @abstractmethod
    def quaternion(
        self,
    ) -> Tuple[Union[int, None], Union[int, None], Union[int, None], Union[int, None]]:
        raise NotImplementedError

    @property
    @abstractmethod
    def gravity(
        self,
    ) -> Tuple[Union[float, None], Union[float, None], Union[float, None]]:
        raise NotImplementedError
"""


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

    def __init__(
        self, *, i2c: busio.I2C, eh: EventHandler
    ) -> None:  # sensor: AbsoluteSensor, V3.10
        """
        Args:
             (TYPE): DESCRIPTION.

        Returns:
            None.

        """
        # self._sensor: adafruit_bno055.BNO055_I2C = adafruit_bno055.BNO055_I2C(i2c)
        self._sensor = adafruit_bno055.sensorBNO055_I2C(i2c)
        self._eh = eh

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
            self._eh.post(
                event_type="robot 9DOF sensor", message="Waiting for gyro calibration"
            )
            time.sleep(2)
        self._eh.post(event_type="robot 9DOF sensor", message="Gyro calibrated")

        while self._sensor.calibration_status[2] != 0x03:  # Accel
            self._eh.post(
                event_type="robot 9DOF sensor", message="Waiting for accel calibration"
            )
            time.sleep(2)
        self._eh.post(
            event_type="robot 9DOF sensor", message="Accelerometer calibrated"
        )

        while self._sensor.calibration_status[2] != 0x03:  # Mag
            self._eh.post(
                event_type="robot 9DOF sensor",
                message="Waiting for magnetrometer calibration",
            )
            time.sleep(2)
        self._eh.post(
            event_type="robot 9DOF sensor", message="Magnetrometer calibrated"
        )

        while self._sensor.calibration_status[0] != 0x03:  # System
            self._eh.post(
                event_type="robot 9DOF sensor", message="Waiting for system calibration"
            )
            time.sleep(2)
        self._eh.post(event_type="robot 9DOF sensor", message="System calibrated")

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

        sensor_calibration_data: Dict[
            str, Union[Dict[str, Union[Dict[str, int], int]], Dict[str, Dict[str, int]]]
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
        sensor_calibration_data: Dict[
            str, Union[Dict[str, Union[Dict[str, int], int]], Dict[str, Dict[str, int]]]
        ],
    ) -> None:
        """Saves calibration data from dictionary to yaml file in configs folder"""
        if not self._validate_calibration_data(sensor_calibration_data):
            self._eh.post(
                event_type="log",
                message="ERROR: Could not save calibration data. Data invalid",
            )
            return
        with open(cfg.path.calibration, "w") as fp:
            yaml.dump(
                sensor_calibration_data,
                stream=fp,
                default_flow_style=True,
                sort_keys=True,
            )
        self._eh.post(
            event_type="robot 9DOF sensor",
            message=f"Calibration data saved: {sensor_calibration_data}",
        )

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
                        ninedof_sensor_config: Union[Box, None] = Box(
                            yaml.safe_load(ninedof_sensor_cfg_file)
                        )
                    if not self._validate_calibration_data(ninedof_sensor_config):
                        self._eh.post(
                            event_type="robot 9DOF sensor",
                            message="ERROR: Nine DOF Calibration Data is not valid",
                        )
                        return False
                except (yaml.YAMLError, OSError, ValueError) as e:
                    self._eh.post(
                        event_type="robot 9DOF sensor",
                        message=f"ERROR: Cannot use config file: {e}",
                    )
                    return False
            else:
                self._eh.post(
                    event_type="robot 9DOF sensor",
                    message=f"ERROR: Path, {cfg.path.ninedof_sensor_calibration} does not exist",
                )
                return False
        else:
            self._eh.post(
                event_type="robot 9DOF sensor",
                message="ERROR: Sensor calibration restoration not available",
            )
            return False
        self._eh.post(
            event_type="robot 9DOF sensor",
            message="ERROR: Cannot restore calibration data, haven't found a way to do that yet",
        )
        return False

    def _validate_calibration_data(
        self,
        sensor_calibration_data: Dict[
            str, Union[Dict[str, Union[Dict[str, int], int]], Dict[str, Dict[str, int]]]
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
            temperature: int = int(self._sensor.temperature * 9 / 5 + 32)
        else:
            temperature: int = self._sensor.temperature

        self._eh.post(
            event_type="robot 9DOF sensor", message=f"Temperature: {temperature}"
        )
        return temperature

    @property
    def accel(self) -> Dict[str, float]:
        """
        Getter for acceleration readings

        Returns:
            Dict of X, Y, Z axis accelerrometer values in meters/sec.^2
        """
        accel_x: Union[float, None]
        accel_y: Union[float, None]
        accel_z: Union[float, None]
        accel_y, accel_x, accel_z = self._sensor.linear_acceleration
        if accel_x is None or accel_y is None or accel_z is None:
            raise ValueError("Accel not available, check mode")
        self._eh.post(
            event_type="robot 9DOF sensor",
            message=f"Accel: x: {accel_x}, y: {accel_y}, z: {accel_z}",
        )
        return {"x": accel_x, "y": accel_y, "z": accel_z}

    @property
    def magnetic_bb(self) -> Dict[str, float]:
        """
        Getter for magnetic field strength readings

        Returns:
            Dict of X, Y, Z megnetometer values in microteslas
        """
        mag_x: Union[float, None]
        mag_y: Union[float, None]
        mag_z: Union[float, None]
        mag_x, mag_y, mag_z = self._sensor.magnetic  # ORDER NOT VERIFIED
        if mag_x is None or mag_y is None or mag_z is None:
            raise ValueError("Magnetic reading not available, check mode")
        self._eh.post(
            event_type="robot 9DOF sensor",
            message=f"Magnetic Field: x: {mag_x}, y: {mag_y}, z: {mag_z}",
        )
        return {"x": mag_x, "y": mag_y, "z": mag_z}

    @property
    def gyro_bb(self) -> Dict[str, float]:
        """
        Getter for gyroscope readings

        Returns:
            Dict of X, Y, Z axis gyroscope values in degrees/sec.
        """
        gyro_x: Union[float, None]
        gyro_y: Union[float, None]
        gyro_z: Union[float, None]
        gyro_y, gyro_x, gyro_z = self._sensor.gyro
        if gyro_x is None or gyro_y is None or gyro_z is None:
            raise ValueError("Gyro not available, check mode")
        self._eh.post(
            event_type="robot 9DOF sensor",
            message=f"Gyro: x: {gyro_x}, y: {gyro_y}, z: {gyro_z}",
        )
        return {"x": gyro_x, "y": gyro_y, "z": gyro_z}

    @property
    def euler_angles(self) -> Dict[str, float]:
        """
        Getter for Euler angle orientation of sensor

        Returns:
            3-tuple of orientation angles
        """
        yaw_z: Union[float, None]
        roll_x: Union[float, None]
        pitch_y: Union[float, None]
        yaw_z, roll_x, pitch_y = self._sensor.euler
        if yaw_z is None or roll_x is None or pitch_y is None:
            raise ValueError("Euler angles not available, check mode")
        self._eh.post(
            event_type="robot 9DOF sensor",
            message=f"roll: x: {roll_x}, pitch y: {pitch_y}, yaw z: {yaw_z}",
        )
        return {"x": roll_x, "y": pitch_y, "z": yaw_z}

    @property
    def gravity_dir(self) -> Dict[str, float]:
        """
        Getter for gravity direction readings

        Returns:
            2-tuple of XY and XZ angle orientations of gravity vector
        """
        x_grav: Union[float, None]
        y_grav: Union[float, None]
        z_grav: Union[float, None]
        x_grav, y_grav, z_grav = self._sensor.gravity
        if x_grav is None or y_grav is None or z_grav is None:
            raise ValueError("Gravity not available, check mode")
        xy_grav_angle: float = math.atan2(y_grav, x_grav)
        xz_grav_angle: float = math.atan2(z_grav, x_grav)
        self._eh.post(
            event_type="robot 9DOF sensor",
            message=f"Gravity Dir: xy_angle: {xy_grav_angle}, xz_angle: {xz_grav_angle}",
        )
        return {"xy": xy_grav_angle, "xz": xz_grav_angle}  # ORDER NOT VERIVIED

    @property
    def gravity_mag(self) -> float:
        """
        Getter for gravity magnitude readings

        Returns:
            magnitude of gravity vector        # ORDER NOT VERIFIED
        """
        x_grav: Union[float, None]
        y_grav: Union[float, None]
        z_grav: Union[float, None]
        x_grav, y_grav, z_grav = self._sensor.gravity
        x_grav = x_grav if x_grav is not None else 0
        y_grav = y_grav if y_grav is not None else 0
        z_grav = z_grav if z_grav is not None else 0
        grav_mag: float = math.sqrt(sum([x_grav**2, y_grav**2, z_grav**2]))
        self._eh.post(
            event_type="robot 9DOF sensor",
            message=f"Gravity Magnitude: {grav_mag}",
        )
        return grav_mag

    """
    @property
    def quaternion_bb(self) -> Tuple[int, ]:

        Getter for quaternion giving orientation

        Returns:
            4-tuple quaternion

        return self._sensor.quaternion  # ORDER NOT VERIFIED
    """

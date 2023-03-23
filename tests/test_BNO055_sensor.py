#!/usr/bin/env python3

from abc import abstractmethod
import time
from typing import Callable, Protocol

import board
from box import Box
import busio


from src import bb_bno055_sensor as bno055
from src.event import EventHandler
from src import robot_listener


class BBAbsoluteSensorGeneral(Protocol):
    def __init__(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def calibrate_sensor(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def temperature(self, units: str) -> float:
        raise NotImplementedError

    @property
    @abstractmethod
    def accel(self) -> dict[str, float]:
        raise NotImplementedError

    @property
    @abstractmethod
    def magnetic_bb(self) -> dict[str, float]:
        raise NotImplementedError

    @property
    @abstractmethod
    def gyro_bb(self) -> dict[str, float]:
        raise NotImplementedError

    @property
    @abstractmethod
    def euler_angles(self) -> dict[str, float]:
        raise NotImplementedError

    @property
    @abstractmethod
    def gravity_dir(self) -> dict[str, float]:
        raise NotImplementedError

    @property
    @abstractmethod
    def gravity_mag(self) -> float:
        raise NotImplementedError


TIME_MS: Callable[[], int] = lambda: int(time.time() * 1000)
TIME_S: Callable[[], int] = lambda: int(time.time())


def test_bno055_sensor():
    """Test BNO055 Sensor"""
    eh = EventHandler()

    robot_listener.setup_robot_9DOF_sensor_handler(eh=eh)
    robot_listener.setup_general_logging_handler(eh=eh)

    # Initialize i2C Connection to sensor
    # TODO: need check/try?
    i2c = busio.I2C(board.SCL, board.SDA)
    sensor: bno055.BB_BNO055Sensor_I2C = bno055.BB_BNO055Sensor_I2C(i2c=i2c, eh=eh)

    # Read Sensor Mode to verify connected
    sensor.mode

    # Calibrate Sensor
    # sensor.calibrate_sensor()
    # Read saved sensor calibration values
    sensor_calibration_data: Box = sensor.read_calibration_data_from_file()
    sensor.write_calibration_data_to_sensor(
        sensor_calibration_data=sensor_calibration_data
    )

    while True:
        try:
            sensor.euler_angles
            time.sleep(1)
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    test_bno055_sensor()

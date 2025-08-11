#!/usr/bin/env python3

import time
from typing import Callable, Protocol

import board  # type: ignore
import busio  # type: ignore
from box import Box

from src.robot_logging.logging_setup import bb_logger as logger
from src.sensor import bb_bno055_sensor as bno055


class BBAbsoluteSensorGeneral(Protocol):
    def __init__(self) -> None:
        ...

    def calibrate_sensor(self) -> None:
        ...

    def temperature(self, units: str) -> float:
        ...

    @property
    def accel(self) -> dict[str, float]:
        ...

    @property
    def magnetic_bb(self) -> dict[str, float]:
        ...

    @property
    def gyro_bb(self) -> dict[str, float]:
        ...

    @property
    def euler_angles(self) -> dict[str, float]:
        ...

    @property
    def gravity_dir(self) -> dict[str, float]:
        ...

    @property
    def gravity_mag(self) -> float:
        ...


TIME_MS: Callable[[], int] = lambda: int(time.time() * 1000)
TIME_S: Callable[[], int] = lambda: int(time.time())


def test_bno055_sensor() -> None:
    """Test BNO055 Sensor"""

    # Initialize i2C Connection to sensor
    i2c = busio.I2C(board.SCL, board.SDA)  # type: ignore
    sensor: bno055.BB_BNO055Sensor_I2C = bno055.BB_BNO055Sensor_I2C(
        i2c=i2c, logger=logger
    )

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
            print("Stopping at your request")
            break


if __name__ == "__main__":
    test_bno055_sensor()

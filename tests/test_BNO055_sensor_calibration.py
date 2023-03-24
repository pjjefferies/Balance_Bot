#!/usr/bin/env python3
""" Tester for BNO055 9-Degree of Freedom Sensor Calibration, Saving and Restoring """

from typing import Protocol, Optional, Any

import board
from box import Box
import busio

from src.sensor import bb_bno055_sensor as bno055
from src import robot_listener
from src.event import EventHandler


class EventHandlerTemplate(Protocol):
    def post(
        self, *, event_type: str, message: str | Any, level: Optional[str]
    ) -> None:
        raise NotImplementedError


def test_BNO055_sensor_calibrate():

    eh: EventHandlerTemplate = EventHandler()

    robot_listener.setup_robot_9DOF_sensor_handler(eh=eh)

    # Initialize i2C Connection to sensor
    # TODO: need check/try?
    i2c = busio.I2C(board.SCL, board.SDA)
    sensor = bno055.BB_BNO055Sensor_I2C(i2c=i2c, eh=eh)

    # Read Sensor Mode to verify connected
    sensor.mode

    # Read and Post "Pre" Calibration Data
    initial_sensor_calibration_data: Box = sensor.read_calibration_data_from_sensor()
    eh.post(
        event_type="9DOF sensor",
        message=f"Initial Sensor Calibration Values:\n{initial_sensor_calibration_data}",
    )

    # Read calibration data saved in configuration file
    initial_config_file_calibration_data: Box = sensor.read_calibration_data_from_file()
    eh.post(
        event_type="9DOF sensor",
        message=f"Initial Sensor Calibration File Values:\n{initial_config_file_calibration_data}",
    )

    # Calibrate Sensor and read calibration values
    sensor.calibrate_sensor()
    post_calibration_sensor_calibration_data: Box = (
        sensor.read_calibration_data_from_sensor()
    )
    eh.post(
        event_type="9DOF sensor",
        message=f"Sensor Calibration Values after calibration:\n{post_calibration_sensor_calibration_data}",
    )

    # Save New Calibration Data to Configuration File
    sensor.write_calibration_data_to_file(post_calibration_sensor_calibration_data)


if __name__ == "__main__":
    test_BNO055_sensor_calibrate()

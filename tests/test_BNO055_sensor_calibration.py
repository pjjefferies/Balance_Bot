#!/usr/bin/env python3
""" Tester for BNO055 9-Degree of Freedom Sensor Calibration, Saving and Restoring """


import board  # type: ignore
from box import Box
import busio  # type: ignore

from src.robot_logging.logging_setup import bb_logger as logger
from src.sensor import bb_bno055_sensor as bno055


def test_BNO055_sensor_calibrate() -> None:
    # Initialize i2C Connection to sensor
    # TODO: need check/try?
    i2c = busio.I2C(board.SCL, board.SDA)  # type: ignore
    sensor = bno055.BB_BNO055Sensor_I2C(i2c=i2c, logger=logger)

    # Read Sensor Mode to verify connected
    sensor.mode

    # Read and Post "Pre" Calibration Data
    initial_sensor_calibration_data: Box = sensor.read_calibration_data_from_sensor()
    logger.info(
        msg=f"9DOF sensor: Initial Sensor Calibration Values:\n{initial_sensor_calibration_data}",
    )

    # Read calibration data saved in configuration file
    initial_config_file_calibration_data: Box = sensor.read_calibration_data_from_file()
    logger.info(
        msg=f"9DOF sensor: Initial Sensor Calibration File Values:\n{initial_config_file_calibration_data}",
    )

    # Calibrate Sensor and read calibration values
    sensor.calibrate_sensor()
    post_calibration_sensor_calibration_data: Box = (
        sensor.read_calibration_data_from_sensor()
    )
    logger.info(
        msg=f"9DOF sensor: Sensor Calibration Values after calibration:\n{post_calibration_sensor_calibration_data}",
    )

    # Save New Calibration Data to Configuration File
    sensor.write_calibration_data_to_file(post_calibration_sensor_calibration_data)


if __name__ == "__main__":
    test_BNO055_sensor_calibrate()

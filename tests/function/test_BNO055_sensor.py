#!/usr/bin/env python3
"""
Tester for BNO055 9-Degree of Freedom Sensor
"""

import datetime as dt
import os
import time
from typing import Protocol, Optional, Any, Callable

import adafruit_bno055
import board
import busio
import numpy as np
import pandas as pd

from balance_bot import robot_listener
from balance_bot.config import cfg
from balance_bot.event import EventHandler

TIME_MS: Callable[[], float] = lambda: time.time() * 1000
TIME_S: Callable[[], float] = lambda: time.time()
UPDATE_TIME: float = 0.1  # Update readings every 0.1 second
LOG_UPDATE_TIME: float = 2  # Time between log post with current readings
DATA_SAVE_TIME: float = 10  # Time between savings history


class EventHandlerTemplate(Protocol):
    def post(
        self, *, event_type: str, message: str | Any, level: Optional[str]
    ) -> None:
        raise NotImplementedError


def test_BNO055_sensor():

    eh: EventHandlerTemplate = EventHandler()

    robot_listener.setup_robot_9DOF_sensor_handler_logfile(eh=eh)
    robot_listener.setup_robot_9DOF_sensor_handler_stdout(eh=eh)

    if os.name == "posix" and os.uname()[1] == "raspberrypi":
        # We're running on Raspberry Pi. OK to start robot.
        eh.post(event_type="9DOF sensor", message="Starting Test BNO055 Sensor Test")
    elif os.name == "nt":
        # Running on Windows, please drive through.
        eh.post(
            event_type="9DOF sensor",
            message="Test BNO055 Sensor not designed to run on Windows at this time",
        )
        return
    else:
        eh.post(
            event_type="9DOF sensor",
            message="Test BNO055 Sensor - OS not identified. Please try on Raspberry Pi",
        )
        return

    # Initialize i2C Connection to sensor
    # TODO: need check/try?
    i2c = busio.I2C(board.SCL, board.SDA)
    sensor = adafruit_bno055.BNO055_I2C(i2c=i2c)

    # Read Sensor Mode to verify connected
    sensor.mode

    # Read and Post "Pre" Calibration Data
    sensor_calibration_values = {
        "accel_offset": sensor.offsets_accelerometer,
        "magnet_offset": sensor.offsets_magnetometer,
        "gyro_offset": sensor.offsets_gyroscope,
        "accel_radius": sensor.radius_accelerometer,
        "magnet_radius": sensor.radius_magnetometer,
    }
    eh.post(event_type="9DOF sensor", message=f"{sensor_calibration_values}")

    # Wait for, read and save calibration information
    start_time = TIME_S()
    while sensor.calibration_status[1] != 0x03:  # Gyro
        eh.post(event_type="9DOF sensor", message=f"Waiting for gyro calibration")
        time.sleep(1)
    elapsed_time = TIME_S() - start_time
    eh.post(
        event_type="9DOF sensor",
        message=f"Gyro calibrated in {elapsed_time:.1f} seconds",
    )

    start_time = TIME_S()
    while sensor.calibration_status[2] != 0x03:  # Accel
        eh.post(event_type="9DOF sensor", message=f"Waiting for accel calibration")
        time.sleep(1)
    elapsed_time = TIME_S() - start_time
    eh.post(
        event_type="9DOF sensor",
        message=f"Accel calibrated in {elapsed_time:.1f} seconds",
    )

    start_time = TIME_S()
    while sensor.calibration_status[2] != 0x03:  # Mag
        eh.post(
            event_type="9DOF sensor", message=f"Waiting for magnetrometer calibration"
        )
        time.sleep(1)
    elapsed_time = TIME_S() - start_time
    eh.post(
        event_type="9DOF sensor",
        message=f"Megnetrometer calibrated in {elapsed_time:.1f} seconds",
    )

    start_time = TIME_S()
    while sensor.calibration_status[0] != 0x03:  # System
        eh.post(event_type="9DOF sensor", message=f"Waiting for system calibration")
        time.sleep(1)
    elapsed_time = TIME_S() - start_time
    eh.post(
        event_type="9DOF sensor",
        message=f"System calibrated in {elapsed_time:.1f} seconds",
    )

    # Read and Post "Post" Calibration Data
    sensor_calibration_values = {
        "accel_offset": sensor.offsets_accelerometer,
        "magnet_offset": sensor.offsets_magnetometer,
        "gyro_offset": sensor.offsets_gyroscope,
        "accel_radius": sensor.radius_accelerometer,
        "magnet_radius": sensor.radius_magnetometer,
    }
    eh.post(event_type="9DOF sensor", message=f"{sensor_calibration_values}")

    # Save Calibration Data
    with open(cfg.path.ninedof_sensor_calibration, "w") as fp:
        json.dump(sensor_calibration_values, fp)

    params_hist: pd.DataFrame = pd.DataFrame()
    lasttime_control_measure: float = TIME_S()
    last_log_time = TIME_S()
    last_data_save_time = TIME_S()
    try:
        while True:
            if (TIME_S() - lasttime_control_measure) >= UPDATE_TIME:
                # exec every UPDATE_TIME seconds
                lasttime_control_measure = TIME_S()
                params: pd.Series[float] = pd.Series(dtype="float64")

                params = params.append(
                    pd.Series(
                        data=sensor.linear_acceleration,
                        index=["y_accel", "x_accel", "z_accel"],
                    )
                )

                params = params.append(
                    pd.Series(
                        data=sensor.euler, index=["yaw(z)", "roll(x)", "pitch(y)"]
                    )
                )

                params = params.append(
                    pd.Series(data=sensor.temperature, index=["temperature"])
                )
                params = params.append(
                    pd.Series(data=sensor.magnetic, index=["mag_x", "mag_y", "mag_z"])
                )
                params = params.append(
                    pd.Series(data=sensor.gyro, index=["gyro_y", "gyro_x", "gyro_z"])
                )
                params = params.append(
                    pd.Series(
                        data=sensor.gravity,
                        index=["gravity_x", "gravity_y", "gravity_z"],
                    )
                )

                params = params.rename(str(dt.datetime.now()))

                if (TIME_S() - last_log_time) > LOG_UPDATE_TIME:
                    eh.post(
                        event_type="9DOF sensor",
                        message="\n".join(str(params).split("\n")[:-1]),
                    )
                    last_log_time = TIME_S()

                params_hist = params_hist.append(params)

                if (TIME_S() - last_data_save_time) >= DATA_SAVE_TIME:
                    eh.post(event_type="9DOF sensor", message="Saving CSV File")
                    last_data_save_time = TIME_S()
                    sensor_history_filename = (
                        "sensor_history-"
                        + dt.datetime.now().strftime("%Y-%m-%d_%H%M%S")
                        + ".csv"
                    )
                    params_hist.to_csv(path_or_buf=sensor_history_filename)

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    test_BNO055_sensor()

#!/usr/bin/env python3

"""
Create representation of distance tracking, digital encoder.

Receives on-off pulses. Counts pulses and keeps track of distance (in
revolutions) over the specified duration.

Classes:
    RotationEncoder

Misc variables:
    FORWARD = True, for use in setting self.direction
    REARWARD = False, for use in setting self.direction
"""

import csv
import pandas as pd
import time

from gpiozero import Motor

from config import cfg
import encoder_sensor as es


def main():
    import os

    if os.name == "posix" and os.uname()[1] == "raspberrypi":
        # We're running on Raspberry Pi. OK to start robot.
        logger.info("Starting Test Encoder Sensor with Motor")
    elif os.name == "nt":
        # Running on Windows, please drive through.
        logger.warning(
            "Test Encoder Sensor with Motor not designed to run on Windows at this time"
        )
        return
    else:
        logger.warning(
            "Test Encoder Sensor with Motor  - OS not identified. Please try on Raspberry Pi"
        )
        return

    FORWARD = True
    REARWARD = False

    logger = logging.getLogger(__name__)

    rh_wheel_motor = Motor(
        forward=cfg.wheel.right.motor.fwd, rearward=cfg.wheel.right.motor.rwd, pwm=True
    )
    rh_wheel_sensor = es.RotationEncoder(
        signal_pin=cfg.wheel.right.encoder, history_len=3600
    )

    with open(cfg.motor_encoder_test_sequence, "r") as fp:
        # Reading a sequence of rows with Speed [-1, 1], Duration in seconds
        csv_reader = csv.reader(fp)
        test_sequence = list(csv_reader)

        # Get initial position of encoder sensor position (should be zero) to initize
        # DataFrame of history data
        test_cond = pd.Series(
            {
                "end_time": time.time(),
                "motor_input": 0,
                "duration": 0,
                "position": rh_wheel_sensor.position,
                "speed_avg": rh_wheel_sensor.speed,
                "accel_avg": rh_wheel_sensor.accel,
                "jerk_avg": rh_wheel_sensor.jerk,
            }
        )
        test_results = pd.DataFrame().append(test_cond)

    for speed, duration in test_sequence:
        speed = max(min(speed, 1), -1)  # limit speed to motor full scale
        duration = max(min(duration, 60), 0)  # limit steps to 0 to 60 seconds
        rh_wheel_motor.average_duration = duration
        start_time = time.time()
        rh_wheel_motor.value = speed
        end_time = start_time + duration
        while time.time() < end_time:
            pass
        test_cond = pd.Series(
            {
                "end_time": time.time(),
                "motor_input": speed,
                "duration": duration,
                "position": rh_wheel_sensor.position,
                "speed_avg": rh_wheel_sensor.speed,
                "accel_avg": rh_wheel_sensor.accel,
                "jerk_avg": rh_wheel_sensor.jerk,
            }
        )
        test_results = test_results.append(test_cond)

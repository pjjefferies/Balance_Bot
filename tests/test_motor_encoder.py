#!/usr/bin/env python3

import csv
import sys
import time
from typing import Callable

from src.encoder.encoder_sensor_digital import EncoderDigital
from src.motor.motor_battery_relay import MotorBatteryRelay
from src.motor.rpi_motor import RPI_Motor
from src.robot_logging.logging_setup import bb_logger as logger

TIME_S: Callable[[], int] = lambda: int(time.time())


def main(argv: list[str]):
    tests: list[dict[str, int | float]] = []
    motor_tests: list[list[str]]
    # [Motor Relay Pin, Motor Fwd. Pin, Motor Rwd. Pin, Encoder Pin, Velocity, Duration (seconds)]

    for filename in argv:
        # Import program to run motor and data to collect
        try:
            with open(file=filename, newline="") as f:
                reader = csv.reader(
                    filter(lambda row: row[0] != "#", f)
                )  # filter comments out
                motor_tests = [list(row) for row in reader]
            for test_no, test in enumerate(motor_tests):
                if len(test) != 6:
                    logger.warning(
                        msg=f"WARNING:In csv file, '{filename}', line {test_no+1} does not have 6 values. Skipping line."
                    )
                    continue
                try:
                    test_detail = {
                        "motor_power_pin": int(test[0]),
                        "motor_pin_fwd": int(test[1]),
                        "motor_pin_rwd": int(test[2]),
                        "encoder_pin": int(test[3]),
                        "velocity": min(max(float(test[4]), -1), 1),
                        "duration": float(test[5]),
                    }
                    if (
                        test_detail["motor_power_pin"] < 1
                        or test_detail["motor_power_pin"] > 27
                    ):
                        logger.warning(
                            msg=f"WARNING:In csv file, '{filename}', line {test_no+1}, motor_power_pin is invalid GPIO number, {test_detail['motor_power_pin']}.",
                        )
                        raise ValueError()
                    if (
                        test_detail["motor_pin_fwd"] < 1
                        or test_detail["motor_pin_fwd"] > 27
                        or test_detail["motor_pin_fwd"]
                        == test_detail["motor_power_pin"]
                    ):
                        logger.warning(
                            msg=f"WARNING:In csv file, '{filename}, line {test_no+1}, motor_pin_fwd is invalid GPIO number, {test_detail['motor_pin_fwd']}.",
                        )
                        raise ValueError()
                    if (
                        test_detail["motor_pin_rwd"] < 0
                        or test_detail["motor_pin_rwd"] > 27
                        or test_detail["motor_pin_rwd"] == test_detail["motor_pin_fwd"]
                        or test_detail["motor_pin_rwd"]
                        == test_detail["motor_power_pin"]
                    ):
                        logger.warning(
                            msg=f"WARNING:In csv file, '{filename}, line {test_no+1}, motor_pin_rwd is invalid GPIO number, {test_detail['motor_pin_rwd']}.",
                        )
                        raise ValueError()
                    if (
                        test_detail["encoder_pin"] < 1
                        or test_detail["encoder_pin"] > 27
                        or test_detail["encoder_pin"] == test_detail["motor_pin_fwd"]
                        or test_detail["encoder_pin"] == test_detail["motor_pin_rwd"]
                        or test_detail["encoder_pin"] == test_detail["motor_power_pin"]
                    ):
                        logger.warning(
                            msg=f"WARNING:In csv file, '{filename}', line {test_no+1}, encoder_pin is invalid GPIO number, {test_detail['encoder_pin']}.",
                        )
                        raise ValueError()
                except ValueError:
                    logger.warning(
                        msg=f"WARNING:In csv file, '{filename}', line {test_no+1}, could not convert values to (int, int, int, int, float, float).",
                    )
                    continue
                tests.append(test_detail)
        except FileNotFoundError:
            logger.warning(msg=f"ERROR:File: {filename} not found. Skipped.")
        except csv.Error:
            logger.warning(
                msg=f"ERROR:File: {filename} is not valid csv file. Skipped."
            )

    if not tests:
        logger.warning(msg=f"WARNING:No tests found in file: {argv}.")
        return

    logger.info(msg=f"Found {len(tests)} tests")

    test_dic: dict[str, int | float]

    for test_no, test_dic in enumerate(tests):
        logger.info(msg=f"INFO:Starting Test No.: {test_no+1}")
        if (
            test_dic["motor_power_pin"] != 0
            and test_dic["motor_pin_fwd"] != 0
            and test_dic["motor_pin_rwd"] != 0
        ):
            motor_power_relay = MotorBatteryRelay(
                gpio_pin_no=int(test_dic["motor_power_pin"]), logger=logger
            )
            motor_power_relay.on()
            motor = RPI_Motor(
                forward=int(test_dic["motor_pin_fwd"]),
                backward=int(test_dic["motor_pin_rwd"]),
                pwm=True,
                logger=logger,
            )
            if test_dic["encoder_pin"] != 0:
                encoder = EncoderDigital(
                    signal_pin=int(test_dic["encoder_pin"]), motor=motor, logger=logger
                )
                encoder.start()
                is_encoder = True
            else:
                is_encoder = False
                continue
            motor.value = test_dic["velocity"]
            time.sleep(test_dic["duration"])
            motor.value = 0
            motor.close()
            motor_power_relay.off()
            motor_power_relay.close()
            if is_encoder:
                encoder.stop()
                _ = encoder.distance  # posts to log distance
                _ = encoder.jerk  # posts to log average speed, accel and jerk
                encoder.close()
        else:
            logger.info(
                msg=f"INFO:Wait step for {test_dic['duration']} seconds",
            )
            time.sleep(test_dic["duration"])


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print(f"Please supply at least one motor test sequence file name.")
    main(sys.argv[1:])

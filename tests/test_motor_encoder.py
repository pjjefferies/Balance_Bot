#!/usr/bin/env python3

import csv
import sys
import time
from typing import Callable

from src import robot_listener
from src.encoder_sensor_digital import EncoderDigital
from src.event import EventHandler
from src.motor_battery_relay import MotorBatteryRelay
from src.rpi_motor import RPI_Motor

TIME_S: Callable[[], int] = lambda: int(time.time())


def main(argv: list[str]):
    eh = EventHandler()
    robot_listener.setup_robot_movement_handler(eh=eh)
    robot_listener.setup_robot_encoder_sensor_handler(eh=eh)
    #  robot_listener.setup_robot_9DOF_sensor_handler(eh=eh)
    robot_listener.setup_general_logging_handler(eh=eh)
    # robot_listener.setup_bluedot_handler(eh=eh)
    robot_listener.setup_power_handler(eh=eh)
    robot_listener.setup_position_history_logging_handler(eh=eh)

    import os

    if os.name == "posix" and os.uname()[1] == "raspberrypi":
        # We're running on Raspberry Pi. OK to start Test Pi Motor.
        eh.post(
            event_type="log",
            message=f"INFO: Starting Test Pi Motor",
        )
    elif os.name == "nt":
        # Running on Windows, please drive through.
        eh.post(
            event_type="log",
            message=f"WARNING: Test Pi Motor not designed to run on Windows at this time",
        )
        # return
    else:
        eh.post(
            event_type="log",
            message=f"WARNING: Test Pi Motor - OS not identified. Please try on Raspberry Pi",
        )
        return

    tests: list[dict[str, int | float]] = []
    # [(Motor Fwd. Pin, Motor Rwd. Pin, Encoder Pin, Velocity, Duration (seconds))]

    for filename in argv:
        # Import program to run motor and data to collect
        try:
            with open(file=filename, newline="") as f:
                reader = csv.reader(
                    filter(lambda row: row[0] != "#", f)
                )  # filter comments out
                motor_tests = [tuple(row) for row in reader]
            for test_no, test in enumerate(motor_tests):
                if len(test) != 6:
                    eh.post(
                        event_type="log",
                        message=f"WARNING:In csv file, '{filename}', line {test_no+1} does not have 6 values. Skipping line.",
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
                        eh.post(
                            event_type="log",
                            message=f"WARNING:In csv file, '{filename}', line {test_no+1}, motor_power_pin is invalid GPIO number, {test_detail['motor_power_pin']}.",
                        )
                        test_detail["motor_power_pin"] = 0
                    if (
                        test_detail["motor_pin_fwd"] < 1
                        or test_detail["motor_pin_fwd"] > 27
                        or test_detail["motor_pin_fwd"]
                        == test_detail["motor_power_pin"]
                    ):
                        eh.post(
                            event_type="log",
                            message=f"WARNING:In csv file, '{filename}, line {test_no+1}, motor_pin_fwd is invalid GPIO number, {test_detail['motor_pin_fwd']}.",
                        )
                        test_detail["motor_pin_fwd"] = 0
                    if (
                        test_detail["motor_pin_rwd"] < 0
                        or test_detail["motor_pin_rwd"] > 27
                        or test_detail["motor_pin_rwd"] == test_detail["motor_pin_fwd"]
                        or test_detail["motor_pin_rwd"]
                        == test_detail["motor_power_pin"]
                    ):
                        eh.post(
                            event_type="log",
                            message=f"WARNING:In csv file, '{filename}, line {test_no+1}, motor_pin_rwd is invalid GPIO number, {test_detail['motor_pin_rwd']}.",
                        )
                        test_detail["motor_pin_rwd"] = 0
                    if (
                        test_detail["encoder_pin"] < 1
                        or test_detail["encoder_pin"] > 27
                        or test_detail["encoder_pin"] == test_detail["motor_pin_fwd"]
                        or test_detail["encoder_pin"] == test_detail["motor_pin_rwd"]
                        or test_detail["encoder_pin"] == test_detail["motor_power_pin"]
                    ):
                        eh.post(
                            event_type="log",
                            message=f"WARNING:In csv file, '{filename}', line {test_no+1}, encoder_pin is invalid GPIO number, {test_detail['encoder_pin']}.",
                        )
                        test_detail["encoder_pin"] = 0
                except ValueError:
                    eh.post(
                        event_type="log",
                        message=f"ERROR:In csv file, '{filename}', line {test_no+1}, could not convert values to (int, int, int, int, float, float).",
                    )
                    continue
                tests.append(test_detail)  # type: ignore
        except FileNotFoundError:
            print(f"File: {filename} not found. Skipped.")
            eh.post(
                event_type="log", message=f"ERROR:File: {filename} not found. Skipped."
            )
        except csv.Error:
            print(f"File: {filename} is not a valid csv file. Skipped.")
            eh.post(
                event_type="log",
                message=f"ERROR:File: {filename} is not valid csv file. Skipped.",
            )

    if not tests:
        print(f"No tests found. Exiting.")
        eh.post(
            event_type="log", message=f"WARNING:No tests found in file: {filename}."
        )
        return

    print(f"Found {len(tests)} tests", flush=True)
    eh.post(event_type="log", message=f"Found {len(tests)} tests")

    for test_no, test in enumerate(tests):
        print(f"Starting test no.: {test_no+1}. (see log for details)", flush=True)
        eh.post(event_type="log", message=f"INFO:Starting Test No.: {test_no+1}")
        if (
            test["motor_power_pin"] != 0
            and test["motor_pin_fwd"] != 0
            and test["motor_pin_rwd"] != 0
        ):
            motor_power_relay = MotorBatteryRelay(
                gpio_pin_no=int(test["motor_power_pin"]), eh=eh
            )
            motor_power_relay.on()
            motor = RPI_Motor(
                forward=int(test["motor_pin_fwd"]),
                backward=int(test["motor_pin_rwd"]),
                pwm=True,
                eh=eh,
            )
            if test["encoder_pin"] != 0:
                encoder = EncoderDigital(
                    signal_pin=int(test["encoder_pin"]), motor=motor, eh=eh
                )
                encoder.start()
                is_encoder = True
            else:
                is_encoder = False
                continue
            motor.value = test["velocity"]
            time.sleep(test["duration"])
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
            eh.post(
                event_type="log",
                message=f"INFO:Wait step for {test['duration']} seconds",
            )
            time.sleep(test["duration"])


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print(f"Please supply at least one motor test sequence file name.")
    main(sys.argv[1:])

#! /usr/bin/python3


import csv
import sys
import time
from typing import Dict, List, Union, Callable

from gpiozero import Motor

from ...balance_bot import robot_listener
from ...balance_bot.encoder_sensor_digital import EncoderDigital
from ...balance_bot.event import EventHandler
from ...balance_bot.motor_battery_relay import MotorBatteryRelay

TIME_S: Callable[[], int] = lambda: int(time.time())


def main(argv: List[str]):
    eh = EventHandler()
    robot_listener.setup_robot_movement_handler()
    robot_listener.setup_robot_encoder_sensor_handler()
    robot_listener.setup_robot_9DOF_sensor_handler()
    robot_listener.setup_general_logging_handler()
    robot_listener.setup_bluedot_handler()
    robot_listener.setup_power_handler()

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

    tests: List[Dict[str, Union[int, float]]] = []
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
                    print(
                        f"In csv file, '{filename}', line {test_no} does not have 6 values. Skipping line."
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
                        test_detail["motor_power_pin"] < 0
                        or test_detail["motor_power_pin"] > 27
                    ):
                        print(
                            f"In csv file, '{filename}, line {test_no}, motor_power_pin is invalid GPIO number."
                        )
                        continue
                    if (
                        test_detail["motor_pin_fwd"] < 0
                        or test_detail["motor_pin_fwd"] > 27
                        or test_detail["motor_pin_fwd"]
                        == test_detail["motor_power_pin"]
                    ):
                        print(
                            f"In csv file, '{filename}, line {test_no}, motor_pin_fwd is invalid GPIO number."
                        )
                        continue
                    if (
                        test_detail["motor_pin_rwd"] < 0
                        or test_detail["motor_pin_rwd"] > 27
                        or test_detail["motor_pin_rwd"] == test_detail["motor_pin_fwd"]
                        or test_detail["motor_pin_rwd"]
                        == test_detail["motor_power_pin"]
                    ):
                        print(
                            f"In csv file, '{filename}, line {test_no}, motor_pin_rwd is invalid GPIO number."
                        )
                        continue
                    if (
                        test_detail["encoder_pin"] < 0
                        or test_detail["encoder_pin"] > 27
                        or test_detail["encoder_pin"] == test_detail["motor_pin_fwd"]
                        or test_detail["encoder_pin"] == test_detail["motor_pin_rwd"]
                        or test_detail["encoder_pin"] == test_detail["motor_power_pin"]
                    ):
                        print(
                            f"In csv file, '{filename}, line {test_no}, encoder_pin is invalid GPIO number."
                        )
                        continue
                except ValueError:
                    print(
                        f"In csv file, '{filename}', line {test_no}, could not convert values to (int, int, int, int, float, float)."
                    )
                    continue
            tests.append(test_detail)  # type: ignore
        except FileNotFoundError:
            print(f"File: {filename} not found. Skipped.")
        except csv.Error:
            print(f"File: {filename} is not a valid csv file. Skipped.")

    if not tests:
        print(f"No tests found. Exiting.")
        return

    for test in tests:
        if (
            test["motor_power_pin"] != 0
            and test["motor_pin_fwd"] != 0
            and test["motor_pin_rwd"] != 0
        ):
            motor_power_relay = MotorBatteryRelay(
                gpio_pin_no=int(test["motor_power_pin"]), eh=eh
            )
            motor_power_relay.on()
            motor = Motor(
                forward=int(test["motor_pin_fwd"]),
                backward=int(test["motor_pin_rwd"]),
                pwm=True,
            )
            motor.value = test["velocity"]
            if test["encoder_pin"] != 0:
                encoder = EncoderDigital(
                    signal_pin=int(test["encoder_pin"]), motor=motor, eh=eh
                )
                encoder.start()
                is_encoder = True
            else:
                is_encoder = False
                time.sleep(test["duration"])
                continue
            time.sleep(test["duration"])
            motor.value = 0
            if is_encoder:
                encoder.stop()
                _ = encoder.distance  # posts to log distance
                _ = encoder.jerk  # posts to log average speed, accel and jerk
        else:
            time.sleep(test["duration"])


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print(f"Please supply at least one motor test sequence file name.")
    main(sys.argv[1:])

#! /usr/bin/python3

# Based on Observer Pattern Tutorial by ArjanCodes o YouTube
# https://www.youtube.com/watch?v=oNalXg67XEE&t=0s

import datetime as dt
from .event import subscribe

# Robot Moved Event Handler
def robot_movement(message: str) -> None:
    print(f"Robot Move: {message}")


def setup_robot_movement_handler() -> None:
    subscribe(event_type="robot moved", fn=robot_movement)


# Robot Encoder Sensor Event Handler
def robot_encoder_sensor(message: str) -> None:
    print(f"Encoder Sensor: {message}")


def setup_robot_encoder_sensor_handler() -> None:
    subscribe(event_type="robot encoder sensor", fn=robot_encoder_sensor)


# Robot 9DOF Sensor Event Handler
def robot_9DOF_sensor(message: str) -> None:
    print(f"9DOF Sensor: {message}")


def setup_robot_9DOF_sensor_handler() -> None:
    subscribe(event_type="robot 9DOF sensor", fn=robot_9DOF_sensor)


# General Logging Event Handlers
def general_logging_handler(message: str) -> None:
    log_type: str
    match message[:4]:
        case ["ERROR", "WARNING", "INFO", "DEBUG"]:
            log_type = message[:4]
        case _:
            log_type = "INVALID_LOG_TYPE"
    print(
        f"Log ({log_type})({dt.datetime.now().strftime('%Y-%m-%d|%H:%M:%S')}): {message}"
    )


def setup_general_logging_handler() -> None:
    subscribe(event_type="log_event", fn=general_logging_handler)

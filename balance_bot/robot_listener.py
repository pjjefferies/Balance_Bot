#! /usr/bin/python3

# Based on Observer Pattern Tutorial by ArjanCodes o YouTube
# https://www.youtube.com/watch?v=oNalXg67XEE&t=0s

import datetime as dt
from event import EventHandler

eh = EventHandler()

# Robot Moved Event Handler
def robot_movement_eh(message: str) -> None:
    print(f"Robot Move: {message}")


def setup_robot_movement_handler() -> None:
    eh.subscribe(event_type="robot moved", fn=robot_movement_eh)


# Robot Encoder Sensor Event Handler
def robot_encoder_sensor_eh(message: str) -> None:
    print(f"Encoder Sensor: {message}")


def setup_robot_encoder_sensor_handler() -> None:
    eh.subscribe(event_type="robot encoder sensor", fn=robot_encoder_sensor_eh)


# Robot 9DOF Sensor Event Handler
def robot_9DOF_sensor_eh(message: str) -> None:
    print(f"9DOF Sensor: {message}")


def setup_robot_9DOF_sensor_handler() -> None:
    eh.subscribe(event_type="robot 9DOF sensor", fn=robot_9DOF_sensor_eh)


# BlueDot Event Handler
def bluedot_eh(message: str) -> None:
    print(f"BlueDot: {message}")


def setup_bluedot_handler() -> None:
    eh.subscribe(event_type="bluedot", fn=bluedot_eh)

# Power Event Handler
def power_eh(message: str) -> None:
    print(f"Power: {message}")


def setup_power_handler() -> None:
    eh.subscribe(event_type="power", fn=power_eh)

# General Logging Event Handlers
def general_logging_handler(message: str) -> None:
    log_type: str
    message_body: str

    log_type, message_body = [txt.strip() for txt in message.split(":")]

    if log_type not in ["ERROR", "WARNING", "INFO", "DEBUG"]:
        log_type = "INVALID_LOG_TYPE"
        message_body = message
    print(
        f"Log ({log_type}):({dt.datetime.now().strftime('%Y-%m-%d|%H:%M:%S')}):{message_body}"
    )


def setup_general_logging_handler() -> None:
    eh.subscribe(event_type="log", fn=general_logging_handler)

#! /usr/bin/python3

# Based on Observer Pattern Tutorial by ArjanCodes o YouTube
# https://www.youtube.com/watch?v=oNalXg67XEE&t=0s

import datetime as dt
import sys
from typing import Optional

from balance_bot.config import log_cfg
from balance_bot.event import EventHandler

eh = EventHandler()

# General Event Handler
def general_eh(event_type: str, message: str, level: Optional[str] = None) -> None:
    now = dt.datetime.now()
    level_text = ": " + level if level is not None else ""
    log_file = log_cfg.handler.log_file
    if log_file == "sys.stdout":
        print(log_cfg.format.simple, file=sys.stdout)
    else:
        with open(log_file, "w") as f:
            print(log_cfg.format.simple, file=f)


def setup_robot_movement_handler() -> None:
    eh.subscribe(event_type="robot moved", fn=general_eh)


# Robot Encoder Sensor Event Handler
def robot_encoder_sensor_eh(message: str) -> None:
    print(f"Encoder Sensor: {message}")


def setup_robot_encoder_sensor_handler() -> None:
    eh.subscribe(event_type="robot encoder sensor", fn=general_eh)


# Robot 9DOF Sensor Event Handler
def robot_9DOF_sensor_eh(message: str) -> None:
    print(f"9DOF Sensor: {message}")


def setup_robot_9DOF_sensor_handler() -> None:
    eh.subscribe(event_type="robot 9DOF sensor", fn=general_eh)


# BlueDot Event Handler
def bluedot_eh(message: str) -> None:
    print(f"BlueDot: {message}")


def setup_bluedot_handler() -> None:
    eh.subscribe(event_type="bluedot", fn=general_eh)


# Power Event Handler
def power_eh(message: str) -> None:
    print(f"Power: {message}")


def setup_power_handler() -> None:
    eh.subscribe(event_type="power", fn=general_eh)


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
    eh.subscribe(event_type="log", fn=general_eh)

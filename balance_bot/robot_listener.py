#! /usr/bin/python3

# Based on Observer Pattern Tutorial by ArjanCodes o YouTube
# https://www.youtube.com/watch?v=oNalXg67XEE&t=0s

import datetime as dt
import numpy as np
import numpy.typing as npt
import sys
from typing import Optional

from balance_bot.config import log_cfg
from balance_bot.event import EventHandler

eh: EventHandler

# General Event Handler
def general_eh(event_type: str, message: str, level: Optional[str] = None) -> None:
    # general_eh_handler = "console"
    general_eh_handler = "log_file"

    now = dt.datetime.now()
    level_text = ": " + level if level is not None else ""
    log_folder = log_cfg.handler[general_eh_handler].folder
    log_filename_base = log_cfg.handler[general_eh_handler].filename
    if log_filename_base == "sys.stdout":
        print(log_cfg.format.simple.format(now=now, event_type=event_type,
                                           level_text=level_text, message=message), file=sys.stdout)
    else:
        log_filename_path = log_folder + "/" + f"{now:%Y-%m-%d_%H_%M}_" + log_filename_base
        # print(f"Trying to cature a general event to a file: {log_filename_path}")
        with open(log_filename_path, "a") as f:
            print(log_cfg.format[log_cfg.handler[general_eh_handler].formatter].format(now=now, event_type=event_type,
                                 level_text=level_text, message=message), file=f)


def setup_robot_movement_handler(eh: EventHandler) -> None:
    eh.subscribe(event_type="robot moved", fn=general_eh)


# Robot Encoder Sensor Event Handler
def robot_encoder_sensor_eh(message: str) -> None:
    print(f"Encoder Sensor: {message}")


def setup_robot_encoder_sensor_handler(eh: EventHandler) -> None:
    eh.subscribe(event_type="encoder sensor", fn=general_eh)


# Robot 9DOF Sensor Event Handler
def robot_9DOF_sensor_eh(message: str) -> None:
    print(f"9DOF Sensor: {message}")


def setup_robot_9DOF_sensor_handler(eh: EventHandler) -> None:
    eh.subscribe(event_type="robot 9DOF sensor", fn=general_eh)


# BlueDot Event Handler
def bluedot_eh(message: str) -> None:
    print(f"BlueDot: {message}")


def setup_bluedot_handler(eh: EventHandler) -> None:
    eh.subscribe(event_type="bluedot", fn=general_eh)


# Power Event Handler
def power_eh(message: str) -> None:
    print(f"Power: {message}")


def setup_power_handler(eh: EventHandler) -> None:
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


def setup_general_logging_handler(eh: EventHandler) -> None:
    eh.subscribe(event_type="log", fn=general_eh)


# Position History Event Handler
def position_history_eh(event_type: str, message: npt.ArrayLike) -> None:
    now = dt.datetime.now()
    log_folder = log_cfg.handler["position_history_file"].folder
    log_filename_base = log_cfg.handler["position_history_file"].filename
    log_filename_path = log_folder + "/" + f"{now:%Y-%m-%d_%H_%M}_" + log_filename_base
    message.savetxt(fname=log_filename_path, fmt="%.5e", delimiter=",")


def setup_position_history_logging_handler(eh: EventHandler) -> None:
    eh.subscribe(event_type="position_history", fn=position_history_eh)

#!/usr/bin/env python3

# Based on Observer Pattern Tutorial by ArjanCodes o YouTube
# https://www.youtube.com/watch?v=oNalXg67XEE&t=0s

import datetime as dt
import numpy as np
import os
import sys
from typing import Optional, Any

from balance_bot.config_logging import log_cfg
from balance_bot.event import EventHandler

# General Log File Event Handler
def general_logfile_eh(
    event_type: str,
    message: str,
    level: Optional[str] = None,
    dt_string: Optional[str] = None,
) -> None:
    general_eh_handler = "log_file"
    now: str = f"{dt.datetime.now():%Y-%m-%d_%H_%M_%S}"
    if dt_string is None:
        dt_string = now
    level_text = ": " + level if level is not None else ""
    log_folder = log_cfg.handler[general_eh_handler].folder
    log_filename_base = log_cfg.handler[general_eh_handler].filename
    log_filename = f"{dt_string}_{log_filename_base}"
    log_filename_path = os.path.join(log_folder, log_filename)

    with open(log_filename_path, "a") as f:
        print(
            log_cfg.format[log_cfg.handler[general_eh_handler].formatter].format(
                now=now,
                event_type=event_type,
                level_text=level_text,
                message=message,
            ),
            file=f,
        )


# General Stdout Event Handler
def general_stdout_eh(
    event_type: str,
    message: str,
    level: Optional[str] = None,
) -> None:
    level_text = ": " + level if level is not None else ""
    print(
        log_cfg.format.simple.format(
            now=f"{dt.datetime.now():%Y-%m-%d_%H_%M_%S}",
            event_type=event_type,
            level_text=level_text,
            message=message,
        ),
        file=sys.stdout,
    )


def setup_robot_movement_handler(eh: EventHandler) -> None:
    subscribe_time = f"{dt.datetime.now():%Y-%m-%d_%H_%M_%S}"
    eh.subscribe(
        event_type="robot moved", fn=general_logfile_eh, dt_string=subscribe_time
    )
    eh.subscribe(event_type="robot moved", fn=general_stdout_eh)


# Robot Encoder Sensor Event Handler
def robot_encoder_sensor_eh(message: str) -> None:
    print(f"Encoder Sensor: {message}")


def setup_robot_encoder_sensor_handler(eh: EventHandler) -> None:
    subscribe_time = f"{dt.datetime.now():%Y-%m-%d_%H_%M_%S}"
    eh.subscribe(
        event_type="encoder sensor", fn=general_logfile_eh, dt_string=subscribe_time
    )


# Robot 9DOF Sensor Event Handler
def robot_9DOF_sensor_eh(message: str) -> None:
    print(f"9DOF Sensor: {message}")


def setup_robot_9DOF_sensor_handler(eh: EventHandler) -> None:
    subscribe_time = f"{dt.datetime.now():%Y-%m-%d_%H_%M_%S}"
    eh.subscribe(
        event_type="9DOF sensor", fn=general_logfile_eh, dt_string=subscribe_time
    )
    eh.subscribe(
        event_type="9DOF sensor", fn=general_stdout_eh, dt_string=subscribe_time
    )


# BlueDot Event Handler
def bluedot_eh(message: str) -> None:
    print(f"BlueDot: {message}")


def setup_bluedot_handler(eh: EventHandler) -> None:
    subscribe_time = f"{dt.datetime.now():%Y-%m-%d_%H_%M_%S}"
    eh.subscribe(event_type="bluedot", fn=general_logfile_eh, dt_string=subscribe_time)


# Power Event Handler
def power_eh(message: str) -> None:
    print(f"Power: {message}")


def setup_power_handler(eh: EventHandler) -> None:
    subscribe_time = f"{dt.datetime.now():%Y-%m-%d_%H_%M_%S}"
    eh.subscribe(event_type="power", fn=general_logfile_eh, dt_string=subscribe_time)
    eh.subscribe(event_type="power", fn=general_stdout_eh, dt_string=subscribe_time)


# General Logging Event Handlers
def general_logging_handler(message: str) -> None:
    log_type: str
    message_body: str

    log_type, message_body = [txt.strip() for txt in message.split(":")]

    if log_type not in ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]:
        log_type = "INFO"
    print(
        f"Log ({log_type}):({dt.datetime.now().strftime('%Y-%m-%d|%H:%M:%S')}):{message_body}"
    )


def setup_general_logging_handler(eh: EventHandler) -> None:
    subscribe_time = f"{dt.datetime.now():%Y-%m-%d_%H_%M_%S}"
    eh.subscribe(event_type="log", fn=general_logfile_eh, dt_string=subscribe_time)


# Position History Event Handler
def position_history_eh(
    event_type: str, message: Any, level: Optional[str] = None
) -> None:
    now = dt.datetime.now()
    log_folder = log_cfg.handler["position_history_file"].folder
    log_filename = (
        f"{now:%Y-%m-%d_%H_%M_%S}_{log_cfg.handler['position_history_file'].filename}"
    )
    log_filename_path = os.path.join(log_folder, log_filename)
    np.savetxt(fname=log_filename_path, X=message, fmt="%.7f", delimiter=",")  # type: ignore


def setup_position_history_logging_handler(eh: EventHandler) -> None:
    subscribe_time = f"{dt.datetime.now():%Y-%m-%d_%H_%M_%S}"
    eh.subscribe(
        event_type="position_history", fn=position_history_eh, dt_string=subscribe_time
    )

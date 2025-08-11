#!/usr/bin/env python3

import time

from src.bluedot.bluedot_direction_control import BlueDotRobotController
from src.robot_logging.logging_setup import bb_logger as logger

prev_position: tuple[float, float] = (
    101.0,
    101.0,
)  # start with impossible position for comp.

bluedot_controller = BlueDotRobotController(logger=logger, timeout=30)
position: tuple[float, float]

while True:
    position = bluedot_controller.bd_drive
    if position != prev_position:
        print(rf"x:{position[1]}, y:{position[0]}")
    prev_position = position
    time.sleep(0.2)

#!/usr/bin/env python3

import time
from typing import Tuple

from src.bluedot_direction_control import BlueDotRobotController

prev_position = [101, 101]  # start with impossible position for comp.

while True:
    position: Tuple[float, float] = BlueDotRobotController.bd_drive
    if position != prev_position:
        print(rf"x:{position[1]}, y:{position[0]}")
    prev_position = position
    time.sleep(0.2)

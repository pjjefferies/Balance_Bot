#! /usr/bin/python3

import logging
from simple_robot import Simple_Robot

logger = logging.getLogger(__name__)


ROBOT_RUN_DURATION = 300  # Seconds
CONTROL_STEPS = 100  # milliseconds

two_wheel_robot = Simple_Robot()

two_wheel_robot.drive_two_wheel_robot_by_bd(interval=CONTROL_STEPS,
                                            duration=ROBOT_RUN_DURATION)

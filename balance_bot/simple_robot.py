#! /usr/bin/python3

import time
import logging
import pandas as pd
from config import cfg
from gpiozero import Motor
import bluedot_direction_control
# from encoder_sensor import RotationEncoder
import balance_bot_config as bbc

logger = logging.getLogger(__name__)
logger.debug(f'Loading data from {cfg.path.data}')
df = pd.read_csv(cfg.path.data)

class Simple_Robot():
    """
    Basic Robot Manual control for 2-Motor Simple Robot
    """
    def __init__(self):
        """
        Initialize Simple Robot using values in balance_bot_config

        Args:
            None

        Returns:
            None.

        """
        # Set-up Motor Control Pins
        self._motor_wheel_left = Motor(forward=bbc.WHEEL_L_FWD,
                                       backward=bbc.WHEEL_L_RWD,
                                       pwm=True)
        self._motor_wheel_right = Motor(forward=bbc.WHEEL_R_FWD,
                                        backward=bbc.WHEEL_R_RWD,
                                        pwm=True)

        # Set-up Motor Encoders
        """
        self._enc_wheel_left = RotationEncoder(signal_pin=bbc.WHEEL_L_ENC)
        self._enc_wheel_right = RotationEncoder(signal_pin=bbc.WHEEL_R_ENC)
        self._enc_arm_left = RotationEncoder(signal_pin=bbc.ARM_L_ENC)
        self._enc_arm_right = RotationEncoder(signal_pin=bbc.ARM_R_ENC)
        """

        self.bd_ctl = bluedot_direction_control.bd_drive

    def drive_two_wheel_robot_by_bd(self, interval=500, duration=60):  # ms, s
        start_time = time.time()

        lasttime = 0

        while time.time() - start_time < duration:
            if (time.time()*1000 - lasttime) >= interval:
                lasttime = time.time() * 1000
                direction = self.bd_ctl()  # [y, x] eached scaled [-1, 1]
                print(f'Direction: {direction[0]}, {direction[1]}')
                if direction == [0, 0]:
                    self._motor_wheel_left.value = 0
                    self._motor_wheel_right.value = 0
                else:
                    fwd_vel = direction[0]
                    right_turn = direction[1]
                    if abs(right_turn) < 0.2:
                        right_turn = 0
                    self._motor_wheel_left.value = max(min(fwd_vel + right_turn, 1), -1) 
                    self._motor_wheel_right.value = max(min(fwd_vel - right_turn, 1 ), -1)


if __name__ == "__main__":

    ROBOT_RUN_DURATION = 300  # Seconds
    CONTROL_STEPS = 100  # milliseconds

    two_wheel_robot = Simple_Robot()

    two_wheel_robot.drive_two_wheel_robot_by_bd(interval=CONTROL_STEPS,
                                                duration=ROBOT_RUN_DURATION)

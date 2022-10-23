#! /usr/bin/python3

import time
import logging
from gpiozero import Motor
from encoder_sensor import RotationEncoder
from config import cfg

logger = logging.getLogger(__name__)


class Simple_Robot:
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
        self._motor_wheel_left = Motor(forward=cfg.wheel.left.motor.fwd,
                                       backward=cfg.wheel.left.motor.rwd,
        # self._motor_wheel_left = Motor(forward=bbc.WHEEL_L_FWD,
        #                                backward=bbc.WHEEL_L_RWD,
                                       pwm=True)
        self._motor_wheel_right = Motor(forward=cfg.wheel.right.motor.fwd,
                                        backward=cfg.wheel.right.motor.rwd,
        # self._motor_wheel_right = Motor(forward=bbc.WHEEL_R_FWD,
        #                                backward=bbc.WHEEL_R_RWD,
                                        pwm=True)

        # Set-up Motor Encoders
        self._enc_wheel_left = RotationEncoder(signal_pin=cfg.wheel.left.encoder)
        # signal_pin=bbc.WHEEL_L_ENC)
        self._enc_wheel_right = RotationEncoder(signal_pin=cfg.wheel.right.encoder)
        # bbc.WHEEL_R_ENC)
        self._enc_arm_left = RotationEncoder(signal_pin=cfg.arm.left.encoder)
        # bbc.ARM_L_ENC)
        self._enc_arm_right = RotationEncoder(signal_pin=cfg.arm.right.encoder)
        # bbc.ARM_R_ENC)

        # self.bd_ctl = bluedot_direction_control.bd_drive

    def drive_two_wheel_robot_auto(self, control_list):  # [[move_1_LH, move_1_RH, time (s)],[...]]
        # start_time = time.time()

        lasttime = 0

        for x_move, y_move, duration in control_list:
            self._motor_wheel_left.value = x_move
            self._motor_wheel_right.value = y_move

            print(f'Left: {x_move}, Right: {y_move}, Duration: {duration}')
            time.sleep(duration)
        """
    while time.time() - start_time < duration:
            if (time.time()*1000 - lasttime) >= interval:
                lasttime = time.time() * 1000
                direction = self.bd_drive()  # [x, y] eached scaled [-1, 1]
                if direction == [0, 0]:
                    self._motor_wheel_left.value = 0
                    self._motor_wheel_right.value = 0
                else:
                    fwd_vel = direction[0]
                    right_turn = direction[1]
                    self._motor_wheel_left.value = fwd_vel + right_turn
                    self._motor_wheel_right.value = fwd_vel - right_turn
        """

def main():
    import os
    if os.name == 'posix' and os.uname()[1] == 'raspberrypi':
        # We're running on Raspberry Pi. OK to start Test Pi Motor.
        logger.info('Starting Test Pi Motor')
    elif os.name == 'nt':
        # Running on Windows, please drive through.
        logger.warning('Test Pi Motor not designed to run on Windows at this time')
        return
    else:
        logger.warning('Test Pi Motor - OS not identified. Please try on Raspberry Pi')
        return

    ROBOT_RUN_DURATION = 60  # Seconds
    CONTROL_STEPS = 500  # milliseconds
    MAX_SPEED = 1

    two_wheel_robot = Simple_Robot()

    # for speed in range(20):
    two_wheel_robot.drive_two_wheel_robot_auto([
                                                # [MAX_SPEED, MAX_SPEED, 1],
                                                # [-MAX_SPEED, -MAX_SPEED, 1],
                                                [MAX_SPEED, -MAX_SPEED, 1],
                                                [-MAX_SPEED, MAX_SPEED, 1],
                                                # [-0.25, 0, 0.5],
                                                # [0, -0.25, 0.5]
                                                # [speed/20, 0.0, 0.25],
                                                #   ])
                                                # [0.0, 0.25, 0.5]])
                                                ])
if __name__ == "__main__":
    main()

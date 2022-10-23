#! /usr/bin/python3
"""
Balance Bot Main Routine.

Classes:
    BalanceBot

Misc variables:
    TBD
"""

# import math
import time
import yaml
from box import Box
import logging
from importlib import reload
import threading
from gpiozero import Motor
import bluedot_direction_control
import board
import busio
from  bb_bno055_sensor import BB_BNO055Sensor
from encoder_sensor import RotationEncoder
from balance_bot.config import cfg

logger = logging.getLogger(__name__)

TIMER = lambda: time.time() * 1000
ENCODERS = False

with open('balance_bot_config.yml', 'r') as ymlfile:
    bb_cfg = Box(yaml.safe_load(ymlfile))

class BalanceBot:
    """
    A class to represent the Balance Bot Robot

    Attributes:
        X

    Methods:
        X
    """
    def __init__(self,
                 start_prog: tuple[tuple[float, float, float]] | None=None,
                 repeat_prog=None):
        """
        Create Balance Bat Robot Object, initiating all start-up functions

        Args:
            start_prog (list): Sequence of steps to run once.
            repeat_prog (list): Sequence of steps to run repeatedly
        Returns:
            Result: True if successful, False if not
        """

        # Initialize i2C Connection to sensor- need check/try?
        i2c = busio.I2C(board.SCL, board.SCA)
        self._sensor = BB_BNO055Sensor(i2c)

        self._sensor_cal()

        # Set-up Motor Control Pins
        self._motor_wheel_left = Motor(forward=bbc.WHEEL_L_FWD,
                                       backward=bbc.WHEEL_L_RWD,
                                       pwm=True)
        self._motor_wheel_right = Motor(forward=bbc.WHEEL_R_FWD,
                                        backward=bbc.WHEEL_R_RWD,
                                        pwm=True)
        self._motor_arm_left = Motor(forward=bbc.ARM_L_FWD,
                                     backward=bbc.ARM_L_RWD,
                                     pwm=True)
        self._motor_arm_right = Motor(forward=bbc.ARM_R_FWD,
                                      backward=bbc.ARM_R_RWD,
                                      pwm=True)

        # Set-up Motor Encoders
        if ENCODERS:
            self._enc_wheel_left = RotationEncoder(signal_pin=bbc.WHEEL_L_ENC)
            self._enc_wheel_right = RotationEncoder(signal_pin=bbc.WHEEL_R_ENC)
            self._enc_arm_left = RotationEncoder(signal_pin=bbc.ARM_L_ENC)
            self._enc_arm_right = RotationEncoder(signal_pin=bbc.ARM_R_ENC)

        # Get Initial Values for PID Filter Initialization
        self._roll_last, self._pitch_last, self._yaw_last = self._sensor.euler

        # Set initial instructions to stand still
        self.pitch_setpoint_angle = 0
        self.yaw_setpoint_angle = 0
        self.previous_fore_aft_motor_input = 0

        # Set initial integral sum for PID control to zero
        self._integral_term = 0

        # Start Balance Loop in its own thread
        main_loop_thread = threading.Thread(target=self.movement_loop,
                                            args=())
        main_loop_thread.start()

        # Start start_prog if we have one
        if start_prog is not None and isinstance(start_prog, list):
            for a_command in start_prog:
                if (not isinstance(a_command, list)) or (len(a_command) != 3):
                    logging.info('Invalid start_prog step, skipping')
                    next
                duration, fwd_rwd, right_left = a_command
                if ((duration < 0 or duration > bbc.MAX_STEP_TIME) or
                    (fwd_rwd < -1 or fwd_rwd > 1) or
                        (right_left < -1 or right_left > 1)):
                    logging.info('Invalid start_prog step, skipping')
                    next
                self.pitch_setpoint_angle = fwd_rwd
                self.yaw_setpoint_angle = right_left
                self.sleep(duration)

        # Start repeat_prog if we have one
        if repeat_prog is not None and isinstance(repeat_prog, list):
            while True:
                for a_command in repeat_prog:
                    if not isinstance(a_command, list) or len(a_command) != 3:
                        logging.info('Invalid repeat_prog step, skipping')
                        next
                    duration, fwd_rwd, right_left = a_command
                    if ((duration < 0 or duration > bbc.MAX_STEP_TIME) or
                        (fwd_rwd < -1 or fwd_rwd > 1) or
                            (right_left < -1 or right_left > 1)):
                        logging.info('Invalid repeat_prog step, skipping')
                        next
                    self.pitch_setpoint_angle = fwd_rwd
                    self.yaw_setpoint_angle = right_left
                    self.sleep(duration)

        # Set-up BlueDot Remote Control
        self.bd_ctl = bluedot_direction_control.bd_drive


    def movement_loop(self):
        lasttime_control = 0
        lasttime_params_updated = 0
        while True:
            if ((time.time()*1000 - lasttime_control) >=
                    bbc.CONTROL_UPDATE_INTERVAL):
                # exec every CONTROL_UPDATE_INTERVAL msec.
                lasttime_control = time.time() * 1000
                self._roll, self._pitch, self._yaw = self._sensor.euler
                fore_aft_error = self.pitch_setpoint_angle - self._pitch
                self._integral_term += bbc.K_INTEGRAL * fore_aft_error
                self._integral_term = max(self._intergral_term, bbc.MOTOR_MIN)
                self._integral_term = min(self._intergral_term, bbc.MOTOR_MAX)
                derivative_term = bbc.K_DERIVATIVE * (
                    self._pitch - self._pitch_last)
                proportional_term = bbc.K_PROPORTIONAL * fore_aft_error
                motor_output = (proportional_term +
                                self._integral_term +
                                derivative_term)
                motor_output = max(motor_output, bbc.MOTOR_MIN)
                motor_output = min(motor_output, bbc.MOTOR_MAX)

                self._motor_wheel_left.move(motor_output)
                self._motor_wheel_right.move(motor_output)

                self._roll_last, self._pitch_last, self._yaw_last = (
                    self._roll, self._pitch, self._yaw)

            if ((time.time() - lasttime_params_updated) >=
                    bbc.PARAMS_UPDATE_INTERVAL):
                # exec every PARAMS_UPDATE_INTERVAL msec.
                lasttime_params_updated = time.time()
                reload(bbc)


def main():
	import os
	if os.name == 'posix' and os.uname()[1] == 'raspberrypi':
		# We're running on Raspberry Pi. OK to start robot.
		logger.info('Starting Balance Bot Robt')
	    robot = BalanceBot()
	elif os.name == 'nt':
		# Running on Windows, please drive through.
		logger.warning('Balance Bot not designed to run on Windows at this time')
	else:
		logger.warning('Balance Bot - OS not identified. Please try on Raspberry Pi')

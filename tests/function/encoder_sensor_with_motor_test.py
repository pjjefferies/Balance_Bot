#! /usr/bin/python3
"""
Create representation of distance tracking, digital encoder.

Receives on-off pulses. Counts pulses and keeps track of distance (in
revolutions) over the specified duration.

Classes:
    RotationEncoder

Misc variables:
    FORWARD = True, for use in setting self.direction
    REARWARD = False, for use in setting self.direction
"""

import time
import csv
import Pandas as pd
from gpiozero import Motor
import encoder_sensor as es
import logging
from balance_bot.config import cfg

FORWARD = True
REARWARD = False

logger = logging.getLogger(__name__)

rh_wheel_motor = Motor(forward=bbc.WHEEL_R_FWD,
                       rearward=bbc.WHEEL_R_RWD,
                       pwm=True)
rh_wheel_sensor = es.RotationEncoder(signal_pin=bbc.WHEEL_R_ENC,
                                     history_len=3600)

with open(bbc.MOTOR_ENCODER_TEST_SEQUENCE, 'r') as fp:
    # Reading a sequence of rows with Speed [-1, 1], Duration in seconds
    csv_reader = csv.reader(fp)
    test_sequence = list(csv_reader)


# Get initial position of encoder sensor position (should be zero) to initize
# DataFrame of history data
    test_cond = pd.Series({'end_time': time.time(),
                           'motor_input': 0,
                           'duration': 0,
                           'position': rh_wheel_sensor.position,
                           'speed_avg': rh_wheel_sensor.speed,
                           'accel_avg': rh_wheel_sensor.accel,
                           'jerk_avg': rh_wheel_sensor.jerk})
    test_results = pd.DataFrame().append(test_cond)

for speed, duration in test_sequence:
    speed = max(min(speed, 1), -1)  # limit speed to motor full scale
    duration = max(min(duration, 60), 0)  # limit steps to 0 to 60 seconds
    rh_wheel_motor.average_duration = duration
    start_time = time.time()
    rh_wheel_motor.value = speed
    end_time = start_time + duration
    while time.time() < end_time:
        pass
    test_cond = pd.Series({'end_time': time.time(),
                           'motor_input': speed,
                           'duration': duration,
                           'position': rh_wheel_sensor.position,
                           'speed_avg': rh_wheel_sensor.speed,
                           'accel_avg': rh_wheel_sensor.accel,
                           'jerk_avg': rh_wheel_sensor.jerk})
    test_results = test_results.append(test_cond)

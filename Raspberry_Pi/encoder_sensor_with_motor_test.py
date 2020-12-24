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
# from gpiozero import LineSensor
from gpiozero import Motor
import encoder_sensor as es
import logging
import balance_bot_config as bbc

FORWARD = True
REARWARD = False

LOGFILENAME = 'sensor__motor_test_log_' + str(int(time.time())) + '.log'
LOG_FORMAT = '%(asctime)s — %(name)s — %(levelname)s — %(message)s'
logger = logging.getLogger(__name__)
logger.basicConfig(filename=LOGFILENAME,
                   level=logging.DEBUG,
                   format=LOG_FORMAT)

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
    start_cond = pd.Series({'end_time': time.time(),
                            'position': rh_wheel_sensor.position,
                            'speed_avg': rh_wheel_sensor.speed(),
                            'accel_avg': })


for speed, duration in test_sequence:
    speed = max(min(speed, 1), -1)  # limit speed to motor full scale
    duration = max(min(duration, 60), 0)  # limit steps to 0 to 60 seconds
    start_time = time.time()
    rh_wheel_motor.value = speed
    end_time = start_time + duration
    while time.time() < end_time:
        pass



try:
    LASTTIME_CONTROL = 0
    while True:
        if ((time.time() - LASTTIME_CONTROL) >= UPDATE_TIME):
            # exec every UPDATE_TIME seconds
            lasttime_control = time.time()
            POSITION = ABS_SENSOR.position
            SPEED = ABS_SENSOR.speed(UPDATE_TIME)
            ACCEL = ABS_SENSOR.accel(UPDATE_TIME)
            JERK = ABS_SENSOR.jerk(UPDATE_TIME)

            logger.debug(f'Pos.: {POSITION:.2f}, ' +
                         'Spe.: {SPEED:.2f}, ' +
                         'Acc.: {ACCEL:.2f}, ' +
                         'Jrk.: {JERK: .2f}')
except KeyboardInterrupt:
    for a_position in ABS_SENSOR._position_history:
        logger.info(a_position)

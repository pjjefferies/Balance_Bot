#! /usr/bin/python3
"""
Balance Bot Configuration Data.

"""

import logging


WHEEL_L_FWD = "GPIO4"     # Physical Pin  7 (1, 4)
WHEEL_L_RWD = "GPIO17"    # Physical Pin 11 (1, 6)

WHEEL_R_FWD = "GPIO27"    # Physical Pin 13 (1, 7)
WHEEL_R_RWD = "GPIO22"    # Physical Pin 15 (1, 8)

ARM_L_FR_LIFT = "GPIO5"   # Physical Pin 29 (1, 15)
ARM_L_FR_DROP = "GPIO6"   # Physical Pin 31 (1, 16)

ARM_R_FR_LIFT = "GPIO13"  # Physical Pin 33 (1, 17)
ARM_R_FR_DROP = "GPIO19"  # Physical Pin 35 (1, 18)

WHEEL_L_ENC = "GPIO26"    # Physical Pin 37 (1, 19)
WHEEL_R_ENC = "GPIO21"    # Physical Pin 40 (2, 20)

ARM_L_ENC = "GPIO20"      # Physical Pin 38 (2, 19)
ARM_R_ENC = "GPIO16"      # Physical Pin 36 (2, 18)

SENSOR_PIN = "GPIO12"     # Physical Pin 32 (2, 16)

CONTROL_UPDATE_INTERVAL = 10  # milliseconds

PARAMS_UPDATE_INTERVAL = 60  # seconds

MAX_STEP_TIME = 60  # seconds

K_PROPORTIONAL = 100  # Proportional Constant
K_INTEGRAL = 2        # Helf catch-up
K_DERIVATIVE = 0      # Damping Adjustment. Should be negative

MOTOR_MAX = 1
MOTOR_MIN = -1

LOG_LEVEL = logging.DEBUG
LOG_FORMAT = '%(asctime)s — %(name)s — %(levelname)s — %(message)s'
CALIBRATION_FILE = 'bno055_calibration_data.json'
MOTOR_ENCODER_TEST_SEQUENCE = 'motor_encoder_test_sequence.csv'
LOGGING_FILE = 'bb_logfile.txt'

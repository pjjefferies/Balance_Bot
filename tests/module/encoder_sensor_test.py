#! /usr/bin/python3
"""
Test representation of distance tracking, digital encoder.

"""

import encoder_sensor
import logging
from balance_bot.config import cfg

logger = logging.getLogger(__name__)

ABS_SENSOR = RotationEncoder(signal_pin=cfg.wheel.encoder.right,
                             history_len=cfg.duration.sensor_history)
UPDATE_TIME = cfg.duration.encoder_sensor_update  # Seconds
LOGFILENAME = 'sensor_log_' + str(int(time.time())) + '.log'
LOG_FORMAT = '%(asctime)s — %(name)s — %(levelname)s — %(message)s'
logger = logging.getLogger(__name__)
logger.basicConfig(filename=LOGFILENAME,
                   level=logging.DEBUG,
                   format=LOG_FORMAT)

try:
    LASTTIME_CONTROL = 0
    while True:
        if ((time.time() - LASTTIME_CONTROL) >= UPDATE_TIME):
            # exec every UPDATE_TIME seconds
            lasttime_control = time.time()
            POSITION = ABS_SENSOR.position
            SPEED = ABS_SENSOR.speed
            ACCEL = ABS_SENSOR.accel
            JERK = ABS_SENSOR.jerk

            logger.debug(f'Pos.: {POSITION:.2f}, ' +
                         'Spe.: {SPEED:.2f}, ' +
                         'Acc.: {ACCEL:.2f}, ' +
                         'Jrk.: {JERK: .2f}')
except KeyboardInterrupt:
    for a_position in ABS_SENSOR._position_history:
        logger.info(a_position)

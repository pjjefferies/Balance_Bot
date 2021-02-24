#! /usr/bin/python3

import logging
import pandas as pd
from config import cfg
from gpiozero import Motor
from signal import pause

logger = logging.getLogger(__name__)
logger.debug(f'Loading data from {cfg.path.data}')
df = pd.read_csv(cfg.path.data)

motor = Motor(forward=5, backward=6, pwm=True)
motor.value = 0
print('motor.value =', motor.value)

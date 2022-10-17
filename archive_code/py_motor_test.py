#! /usr/bin/python3

import logging
from gpiozero import Motor
from signal import pause
from balance_bot.config import cfg

logger = logging.getLogger(__name__)

motor = Motor(forward=5, backward=6, pwm=True)
motor.value = 0
print('motor.value =', motor.value)

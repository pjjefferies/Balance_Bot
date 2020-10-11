#! /usr/bin/python3

from gpiozero import Motor
from signal import pause

motor = Motor(forward=5, backward=6, pwm=True)
motor.value = 0
print('motor.value =', motor.value)

#! /usr/bin/python3

# import RPi.GPIO as GPIO  # Import GPIO library
from gpiozero import Motor


class RPI_Motor:
    """
    Object for indivisual Motor control - direction, speed
    """
    def __init__(self, forward_line, rearward_line):
        self._motor = Motor(forward=5, backward=6, pwm=True)
        self._motor.value = 0

    def move(self, *, velocity=0.1):
        """
        Method to move motor
        velocity:  1 = Forward at full speed
        velocity:  0 = Stop
        velocity: -1 = Rearward at full speed
        """
        velocity = min(max(velocity, -1), 1)
        self._motor.value = velocity

    def stop(self):
        self._motor.value = 0

    def max_speed(self):
        self._motor.value = 1

    def current_speed(self):
        return self._motor.value

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
import logging
from gpiozero import LineSensor
from balance_bot.config import cfg

logger = logging.getLogger(__name__)

FORWARD = True
REARWARD = False


class RotationEncoder:
    """
    A class to represent a two-state digital, rotary encoder.

    Attributes:
        position (float): number and fractions of rotations
        direction (bool): Dir. of travel: FORWARD (True) or REARWARD (False)

    Methods:
        speed (float): Returns average speed over a give time duration
        accel (float): Returns average acceleration over a give time duration
        jerk (float): Returns average jerk over a give time duration
        clear_history (None): Clears position history and calls current
                              position zero.
    """
    def __init__(self, *,
                 signal_pin,
                 sample_freq=200,  # per second
                 slots_per_rev=20,
                 history_len=60,  # seconds
                 average_duration=1, # seconds
                 ):
        """
        Constructs all the necessary attributes for the Rotation_Encoder
        object using LineSensor class from gpiozero.

        Args:
            signal_pin: RaspberriPi Logical Pin connected to Sensor output Pin
            sample_freq: Frequency to sample Sensor (Hz)
            slots_per_rev: Number of slots per revolutoin
            history_len: Length of distance history to maintain in seconds

        Returns:
            None, other than object itself

        Raises:
            None.
        """
        self._sample_freq = sample_freq
        self._history_len = history_len
        self.average_duration = average_duration
        # time speed, accel and jerk are averaged over

        self._sensor = LineSensor(pin=signal_pin,
                                  pull_up=True,
                                  queue_len=5,
                                  sample_rate=sample_freq,
                                  partial=True,
                                  )
        self._rev_per_half_slot = (lambda: 1/slots_per_rev/2 if self.direction
                                   else -1/slots_per_rev/2)
        self.position = 0
        self._position_history = [[time.time(), 0]]
        self.direction = FORWARD

        self._sensor.when_line = lambda: self._move_a_half_slot
        self._sensor.when_no_line = lambda: self._move_a_half_slot

    def _move_a_half_slot(self):
        """
        Increments the distance traveled when triggered. Stores distance
        traveled at time in _posiiton_history.

        Returns:
            None.
        """
        move_time = time.time()
        self.position += self._rev_per_half_slot()
        self._position_history.append([move_time, self.position])
        self._position_history = (  # Truncate position history
            self._position_history[-self._sample_freq * self._history_len])

    @property
    def speed(self):
        """
        Getter for speed Encoder has observed, averaged by time over the
        duration specified.

        Args:
            duration: int, optional. duration of time, in seconds, to average
            speed over. The default is 1 second.

        Returns:
            Average speed as a float
        """
        end_time, end_position = self._position_history[-1]
        for pos_meas in range(len(self._position_history)-2, 0, -1):
            if ((end_time - self._position_history[pos_meas][0]) >
                    self.average_duration):
                break
        actual_duration = (end_time -
                           self._position_history[pos_meas][0])
        dist_traveled = (end_position -
                         self._position_history[pos_meas][1])
        return dist_traveled / actual_duration

    @property
    def accel(self):
        """
        Getter for acceleration Encoder has observed, averaged by time over
        the duration specified.

        Args:
            duration: int, optional duration of time, in seconds, to average
            acceleration over. The default is 1 second.

        Returns:
            Average acceleration as float
        """
        end_time, end_position = self._position_history[-1]
        for pos_meas in range(len(self._position_history)-2, 0, -1):
            if ((end_time - self._position_history[pos_meas][0]) >
                    self.average_duration):
                break
        actual_duration = (end_time -
                           self._position_history[pos_meas][0])
        dist_traveled = (end_position -
                         self._position_history[pos_meas][1])
        return 2 * dist_traveled / (actual_duration**2)

    @property
    def jerk(self):
        """
        Getter for jerk Encoder has observed, averaged by time over
        the duration specified.

        Args:
            duration: int, optional, duration of time, in seconds, to average
            jerk over. The default is 1 second.

        Returns:
            Average jerk as float
        """
        end_time, end_position = self._position_history[-1]
        for pos_meas in range(len(self._position_history)-2, 0, -1):
            if ((end_time - self._position_history[pos_meas][0]) >
                    self.average_duration):
                break
        actual_duration = (end_time -
                           self._position_history[pos_meas][0])
        dist_traveled = (end_position -
                         self._position_history[pos_meas][1])
        return 6 * dist_traveled / (actual_duration**3)

    def clear_history(self):
        """
        Clear history of position, setting current position as zero.

        Args:
            None

        Returns:
            None

        """
        self.position = 0
        self._position_history = [[time.time(), 0]]

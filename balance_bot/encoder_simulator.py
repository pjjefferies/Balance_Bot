#! /usr/bin/python3

import time
import asyncio
from typing import Protocol
from config import cfg_sim
import logging
from encoder_sensor_general import EncoderGeneral

# from config import cfg

logger = logging.getLogger(__name__)


class MotorGeneral(Protocol):
    def __init__(
        self,
    ):
        raise NotImplementedError

    @property
    def value(self) -> float:
        raise NotImplementedError


class EncoderSim(EncoderGeneral):
    """
    A class to represent a simulated distance encoder.

    Attributes:
        position: float: number and fractions of rotations
        moving_forward: bool: True if moving forward, False if moving backwards

    Methods:
        speed: float: Returns average speed over a give time duration
        accel: float: Returns average acceleration over a give time duration
        jerk: float: Returns average jerk over a give time duration
        reset_history: None: Clears position history and calls current
                              position zero.
    """

    def __init__(
        self,
        *,
        sample_freq: float = 100,  # per second
        max_no_position_points: int = 10_000,
        average_duration: int = 1,  # seconds
        motor: MotorGeneral,
    ) -> None:
        """
        Constructs all the necessary attributes for the EncoderSim object
        Args:
            sample_freq: Frequency to sample Sensor (Hz)
            slots_per_rev: Number of slots per revolutoin
            history_len: Length of distance history to maintain in seconds
            average_duration: Length to average speed, accel, jerk over
        Returns:
            None, other than object itself
        Raises:
            None.
        """
        super().__init__(
            max_no_position_points=max_no_position_points,
            average_duration=average_duration,
            motor=motor,
        )
        self._position_change_to_motor_value_ratio: float = (
            cfg_sim.encoder.position_change_to_motor_value_ratio
        )
        self._position_change_rate = (  # distance / time (s)
            self._motor.value * self._position_change_to_motor_value_ratio
        )
        self._sample_freq: float = sample_freq

        # Initialize these now to save time each encoding loop
        self._new_time: float
        self._old_time: float
        self._time_delta: float
        self._old_position: float
        self._new_position: float

        self.reset_history()

        self.start()

    async def _encoding_loop(self):
        while True:
            self._new_time = time.time()
            self._old_time = self._position_history[self._current_history_len - 1, 0]
            self._time_delta: float = self._new_time - self._old_time

            self._old_position = self._position_history[
                self._current_history_len - 1, 2
            ]
            self._new_position = (
                self._old_position + self._position_change_rate * self._time_delta
            )

            self.add_position(a_time=self._new_time, position=self._new_position)

            await asyncio.sleep(1 / self._sample_freq)
            if not self._running:
                break

    def start(self) -> None:
        self._running = True
        self.reset_history()
        loop = asyncio.get_event_loop()
        tasks = [loop.create_task(self._encoding_loop())]
        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()

    def stop(self) -> None:
        self._running = False

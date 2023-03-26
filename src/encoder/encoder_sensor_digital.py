#!/usr/bin/env python3


import time
from logging import Logger
from typing import Any, Callable, Protocol

import numpy as np
from gpiozero import LineSensor

from src.encoder.encoder_sensor_general import EncoderGeneral
from src.save_position_history import save_position_history


class MotorGeneral(Protocol):
    def __init__(
        self,
        *,
        forward: int | str,
        backward: int | str,
        logger: Logger,
    ):
        raise NotImplementedError

    @property
    def value(self) -> float:
        raise NotImplementedError


class EncoderDigital(EncoderGeneral):
    """
    A class to represent a two-state digital, encoder.

    Attributes:
        position: float: number and fractions of distance
        moving_forward: bool: True if moving forward, False if moving backwards

    Methods:
        speed: float: Returns average speed over a give time duration
        accel: float: Returns average acceleration over a give time duration
        jerk: float: Returns average jerk over a give time duration
        clear_history: None: Clears position history and calls current
                              position zero.
        motor: Motor_General: Motor object to detect direction of movement
    """

    def __init__(
        self,
        *,
        signal_pin: int | str,  # RaspberriPi Logical Pin connected to Sensor output Pin
        slots_per_rev: int = 20,
        max_no_position_points: int = 10_000,
        average_duration: float = 1,  # seconds, duration to take averages over
        motor: MotorGeneral,
        logger: Logger,
    ):
        """
        Constructs all the necessary attributes for the Rotation_Encoder
        object using LineSensor class from gpiozero.
        """
        super().__init__(
            max_no_position_points=max_no_position_points,
            average_duration=average_duration,
            motor=motor,
            logger=logger,
        )

        self._sensor: LineSensor = LineSensor(
            pin=signal_pin,
            pull_up=True,
            queue_len=5,
            # sample_rate=self._sample_freq,
            partial=True,
        )
        self._revs_per_half_slot: Callable[[], float] = (
            lambda: 1 / slots_per_rev / 2
            if self.moving_forward
            else -1 / slots_per_rev / 2
        )
        self._revs_per_slot: Callable[[], float] = (
            lambda: 1 / slots_per_rev if self.moving_forward else -1 / slots_per_rev
        )
        self.position: float
        self._position_history: Any

        self._signal_pin = signal_pin
        self._logger.info(f"encoder sensor: Created Digital Sensor on pin {signal_pin}")

    def _move_a_half_slot(self) -> None:
        """
        Increments the distance traveled when triggered. Stores distance
        traveled at time in _posiiton_history.
        """
        if not self._running:
            return
        move_time = time.time()  # seconds
        self.position = (
            self._position_history[self._current_history_len - 1, 2]
            + self._revs_per_half_slot()
        )
        self.add_position(a_time=move_time, position=self.position)

    def _move_a_full_slot(self) -> None:
        """
        Increments the distance traveled when triggered. Stores distance
        traveled at time in _posiiton_history.
        """
        if not self._running:
            return
        move_time = time.time()  # seconds
        self.position = (
            self._position_history[self._current_history_len - 1, 2]
            + self._revs_per_slot()
        )
        self.add_position(a_time=move_time, position=self.position)

    def start(self):
        super().start()
        self._sensor.when_line = (
            self._move_a_half_slot
        )  # sets function to be run when line is detected
        self._sensor.when_no_line = (
            self._move_a_half_slot
        )  # sets function to be run when no line is detected

        self._running = True
        self._logger.info(f"encoder sensor: Started Digital Sensor {self._signal_pin}")
        self.reset_history()

    def stop(self):
        self._sensor.when_line = None
        self._sensor.when_no_line = None
        self._running = False
        self._logger.info(
            f"encoder sensor: Stopped Digital Sensor on pin {self._signal_pin}"
        )

    def close(self):  # releases pins from use by encoder sensor
        self._logger.info(
            f"encoder sensor: Digital Sensor Destroyed on pin {self._signal_pin}"
        )

        # Strip history of all empty rows
        temp_history = self._position_history[
            ~np.all(self._position_history == 0, axis=1)
        ]
        save_position_history(pos_history=temp_history)
        self._sensor.close()

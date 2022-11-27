#! /usr/bin/python3

import time
from typing import Callable, Protocol, Any
from encoder_sensor_general import EncoderGeneral
from gpiozero import LineSensor  # type: ignore


class EventHandlerTemplate(Protocol):
    def post(self, *, event_type: str, message: str) -> None:
        raise NotImplementedError


class MotorGeneral(Protocol):
    def __init__(
        self,
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
        signal_pin: int | str,
        slots_per_rev: int = 20,
        max_no_position_points: int = 10_000,
        average_duration: float = 1,  # seconds
        motor: MotorGeneral,
        eh: EventHandlerTemplate,
    ):
        """
        Constructs all the necessary attributes for the Rotation_Encoder
        object using LineSensor class from gpiozero.

        Args:
            signal_pin: RaspberriPi Logical Pin connected to Sensor output Pin
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
            eh=eh,
        )

        self._sensor: LineSensor = LineSensor(
            pin=signal_pin,
            pull_up=True,
            queue_len=5,
            # sample_rate=self._sample_freq,
            partial=True,
        )
        self._dist_per_half_slot: Callable[[], float] = (
            lambda: 1 / slots_per_rev / 2
            if self.moving_forward
            else -1 / slots_per_rev / 2
        )
        self.position: float
        self._position_history: Any

        self.start()
        self._eh.post(event_type="Encoder Sensor", message="Created Digital Sensor")

    def _move_a_half_slot(self) -> None:
        """
        Increments the distance traveled when triggered. Stores distance
        traveled at time in _posiiton_history.

        Returns:
            None.
        """
        if not self._running:
            return
        move_time = time.time()  # seconds
        self.position = (
            self._position_history[self._current_history_len - 1, 2]
            + self._dist_per_half_slot()
        )
        self.add_position(a_time=move_time, position=self.position)

    def start(self):
        self._sensor.when_line = (
            self._move_a_half_slot
        )  # sets function to be run when line is detected
        self._sensor.when_no_line = (  # type: ignore
            self._move_a_half_slot
        )  # sets function to be run when no line is detected
        self._running = True
        self.reset_history()
        self._eh.post(event_type="Encoder Sensor", message="Started Digital Sensor")

    def stop(self):
        self._sensor.when_line = None
        self._sensor.when_no_line = None
        self._running = False
        self._eh.post(event_type="Encoder Sensor", message="Stopped Digital Sensor")

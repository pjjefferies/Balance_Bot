#! /usr/bin/python3

import numpy as np
from typing import Protocol, Any

# from config import cfg


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


class EncoderGeneral:
    """
    A class to represent a general encoder for tracking changes in position

    Attributes:
        position: float: number and fractions of rotations
        moving_forward: bool: True if moving forward, False if moving backwards

    Methods:
        speed: float: Returns average speed over a give time duration
        accel: float: Returns average acceleration over a give time duration
        jerk: float: Returns average jerk over a give time duration
        reset_history: None: Clears position history and calls current
                              position zero.
        motor: Motor_General: Motor object to detect direction of movement
    """

    def __init__(
        self,
        *,
        max_no_position_points: int = 10_000,
        average_duration: float = 1,  # seconds - for calc. speed, accel, etc.
        motor: MotorGeneral,  # Motor object to detect direction of movement
        eh: EventHandlerTemplate,
    ):
        """
        Constructs all the necessary attributes for the EncoderGeneral

        Raises:
            None.
        """
        # self._sample_freq: float = sample_freq
        self._max_no_position_points: int = max_no_position_points
        self._average_duration: float = (
            average_duration  # time in seconds speed, accel and jerk are averaged over
        )
        self._history_lines_to_use: int
        self._motor: MotorGeneral = motor
        self._eh: EventHandlerTemplate = eh
        self._running = False
        self.reset_history()

    def start(self) -> None:
        raise NotImplementedError

    def stop(self) -> None:
        raise NotImplementedError

    @property
    def moving_forward(self):
        return self._motor.value >= 0

    def reset_history(self) -> None:
        """
        Clear history of position, setting current position as zero.
          Args: None
          Returns: None
          self._position_history format, e.g. at 2 Hz. (p=t^3) after 3 seconds,
          self_current_history_len = 7,
          self._max_history_len = 10
            index time  step_duration  postion  speed  acceleration  jerk
              0     0        0            0        0         0         0
              1     0.5      0.5          0.125    0.25      0         0
              2     1.0      0.5          1.0      1.75      3         0
              3     1.5      0.5          3.375    4.75      6         6
              4     2.0      0.5          8.0      9.25      9         6
              5     2.5      0.5         15.625   15.25     12         6
              6     3.0      0.5         27.0     22.75     15         6
              7     0        0            0        0         0         0
              8     0        0            0        0         0         0
              9     0        0            0        0         0         0
        """

        self._eh.post(event_type="Encoder Sensor", message="Resetting Sensor History")

        # self._position_history = [(time.time(), 0)]
        self._position_history: Any = np.zeros(  # type: ignore
            shape=(self._max_no_position_points, 6), dtype=float
        )  # (time, step duration, position, speed, acceleration, jerk)
        self._current_history_len: int = 1
        self._eh.post(
            event_type="Encoder Sensor",
            message="Encoder Sensor history reset",
        )

    def add_position(self, a_time: float, position: float) -> None:
        self._current_history_len += 1
        if self._current_history_len > self._max_no_position_points:
            self._current_history_len = self._max_no_position_points
            self._position_history[:, 0] = np.roll(self._position_history[:, 0], -1)  # type: ignore
            self._position_history[:, 2] = np.roll(self._position_history[:, 2], -1)  # type: ignore
        self._position_history[self._current_history_len - 1, 0] = a_time
        self._position_history[self._current_history_len - 1, 2] = position
        self._eh.post(
            event_type="Encoder Sensor",
            message="Adding position: time: {a_time}, pos.: {position}",
        )

    @property
    def distance(self) -> float:
        """
        Getter for Distance Encoder has observed

        Args:
            None

        Returns:
            Distance as a float
        """

        distance: float = self._position_history[self._history_lines_to_use - 1, 2]

        self._eh.post(
            event_type="robot encoder sensor", message=f"Distance: {distance:.2f}"
        )

        return distance

    @property
    def speed(self) -> float:
        """
        Getter for speed Encoder has observed, averaged by time over the
        duration specified.

        Args:
            None

        Returns:
            Average speed as a float
        """
        if self._current_history_len < 2:
            return 0

        self._history_lines_to_use = np.argmax(  # type: ignore
            self._position_history[:, 0] >= self._average_duration
        )
        if self._history_lines_to_use == 0:
            self._history_lines_to_use = self._current_history_len
            # Don't have enough for average duration so use all we have

        # Calculate Step Duration in column 1
        self._position_history[0:1, 4] = np.zeros(1)  # type: ignore

        self._position_history[1 : self._history_lines_to_use - 1, 1] = (
            self._position_history[1 : self._history_lines_to_use - 1, 0]
            - self._position_history[: self._history_lines_to_use - 2, 0]
        )

        # Calculate Speed in column 3
        self._position_history[0, 3] = 0
        self._position_history[1 : self._history_lines_to_use - 1, 3] = (
            self._position_history[1 : self._history_lines_to_use - 1, 2]
            - self._position_history[0 : self._history_lines_to_use - 2, 2]
        ) / self._position_history[1 : self._history_lines_to_use - 1, 1]

        avg_speed: float = float(
            np.average(self._position_history[1 : self._history_lines_to_use - 1, 3])
        )

        self._eh.post(event_type="Encoder Sensor", message=f"Speed: {avg_speed}")

        return avg_speed

    @property
    def accel(self) -> float:
        """
        Getter for acceleration Encoder has observed, averaged by time over
        the duration specified.

        Args:
            None

        Returns:
            Average acceleration as float
        """
        if self._current_history_len < 3:
            return 0

        self.speed

        # Calculate Acceleration in column 4
        self._position_history[0:2, 4] = np.zeros(2)  # type: ignore

        self._position_history[2 : self._history_lines_to_use - 1, 4] = (
            self._position_history[2 : self._history_lines_to_use - 1, 3]
            - self._position_history[1 : self._history_lines_to_use - 2, 3]
        ) / self._position_history[2 : self._history_lines_to_use - 1, 1]

        avg_accel: float = float(
            np.average(self._position_history[2 : self._history_lines_to_use - 1, 4])
        )
        self._eh.post(event_type="Encoder Sensor", message=f"Accel: {avg_accel}")

        return avg_accel

    @property
    def jerk(self) -> float:
        """
        Getter for jerk Encoder has observed, averaged by time over
        the duration specifieda.

        Args:
            None

        Returns:
            Average jerk as float
        """
        if self._current_history_len < 4:
            return 0

        self.accel

        # Calculate Jerk in column 5
        self._position_history[0:3, 5] = np.zeros(3)  # type: ignore

        self._position_history[3 : self._history_lines_to_use - 1, 5] = (
            self._position_history[3 : self._history_lines_to_use - 1, 4]
            - self._position_history[2 : self._history_lines_to_use - 2, 4]
        ) / self._position_history[3 : self._history_lines_to_use - 1, 1]

        avg_jerk: float = float(
            np.average(self._position_history[3 : self._history_lines_to_use - 1, 5])
        )

        self._eh.post(event_type="Encoder Sensor", message=f"Jerk: {avg_jerk}")

        return avg_jerk

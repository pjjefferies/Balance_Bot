import numpy as np
import time
from typing import Any, Union, Protocol

from gpiozero import Motor

from balance_bot.motor_simulator import MotorSim
from balance_bot.event import EventHandler
from balance_bot.find_mode import find_gamma_mode
from cumulative_average import cumulative_average


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
        eh: EventHandler,
    ):
        """
        Constructs all the necessary attributes for the EncoderGeneral

        Raises:
            None.
        """
        self._T_COL: int = 0  # Time Column
        self._T_SINCE_START_COL: int = 1
        self._S_D_COL: int = 2  # Step Distance Column
        self._S_D_MODE_COL: int = 3
        self._S_D_MODE_AVG_COL: int = 4
        self._DIST_COL: int = 5
        self._SPEED_COL: int = 6
        self._ACCEL_COL: int = 7
        self._JERK_COL: int = 8
        self._TOT_NUM_COLS: int = 9

        self._max_no_position_points: int = max_no_position_points

        # time in seconds speed, accel and jerk are averaged over
        self._average_duration: float = average_duration
        self._motor: MotorGeneral = motor
        self._eh: EventHandler = eh
        self._running = False

    def start(self) -> None:
        self.reset_history()
        self._position_history[0, self._T_COL] = time.time()

    def stop(self) -> None:
        raise NotImplementedError

    @property
    def moving_forward(self) -> bool:
        return self._motor.value >= 0

    def reset_history(self) -> None:
        """
        Clear history of position, setting current position as zero.
          Args: None
          Returns: None
          sd_mode: Step Duration Mode (most likely value of continuous distribution)
          sd_mode_run_avg: Continuous, whole history running average
          self._position_history format, e.g. at 2 Hz. (p=t^3) after 3 seconds,
          self._current_history_len = 7,
          self._max_history_len = 10
            col_ind     0                1            2            3             4              5       6         7            8
                      T_COL      T_SINCE_START_COL S_D_COL       S_D_MODE_COL S_D_MODE_AVG_COL POS_COL SPEED_COL ACCEL_COL    JERK_COL
            index      time       time_since_start step_duration sd_mode      sd_mode_run_avg  postion speed     acceleration jerk
              0   1673844977.7530        0            0            0             0             0        0         0           0
              1   1673844978.2530      0.5            0.125        0.0625        0.03125       0        0         0           0
              2   1673844978.7530      0.5            1.0          0.5           0.3           3        0         0           0
              3   1673844979.2530      1.5            0.5          0.5           0.4           3.375    4.75      6           6
              4   1673844979.7530      2.0            0.5          0.5           0.45          8.0      9.25      9           6
              5   1673844980.2530      2.5            0.5          0.5           0.48         15.625   15.25     12           6
              6   1673844980.7530      3.0            0.5          0.5           0.49         27.0     22.75     15           6
              7            0           0              0            0             0             0        0         0           0
              8            0           0              0            0             0             0        0         0           0
              9            0           0              0            0             0             0        0         0           0
        """

        self._position_history: Any = np.zeros(  # type: ignore
            shape=(self._max_no_position_points, self._TOT_NUM_COLS), dtype=float
        )  # (time, time_since_start, step_duration, sd_mode, sd_mode_run_avg, position, speed, acceleration, jerk)
        self._current_history_len: int = 1
        self._eh.post(
            event_type="encoder sensor",
            message="Encoder Sensor history reset",
        )

    def add_position(self, a_time: float, position: float) -> None:
        self._current_history_len += 1

        # Check if max history length exceeded. Roll if so
        if self._current_history_len > self._max_no_position_points:
            self._current_history_len = self._max_no_position_points
            self._position_history = np.roll(self._position_history, -1)
            # first position point will roll to last but be overwritten with new data

            # Calculate time_since_start column since we have new baseline
            # zero time at beginning of remaining history
            self._position_history[0:, self._T_SINCE_START_COL] = (
                self._position_history[0:, self._T_COL]
                - self._position_history[0, self._T_COL]
            )

        # Add New data to the position history

        # Add current time for new position point (Column T_COL)
        self._position_history[self._current_history_len - 1, self._T_COL] = a_time

        # Calculate time_since_start for new position point (Column T_SINCE_START_COL)
        self._position_history[
            self._current_history_len - 1, self._T_SINCE_START_COL
        ] = (
            self._position_history[self._current_history_len - 1, self._T_COL]
            - self._position_history[0, self._T_COL]
        )

        # Calculate step duration for new position point (Column S_D_COL)
        self._position_history[self._current_history_len - 1, self._S_D_COL] = (
            self._position_history[
                self._current_history_len - 1, self._T_SINCE_START_COL
            ]
            - self._position_history[
                self._current_history_len - 2, self._T_SINCE_START_COL
            ]
        )

        # Calculate mode of step duration up to latest history point (Column S_D_MODE_COL)
        self._position_history[
            self._current_history_len - 1, self._S_D_MODE_COL
        ] = find_gamma_mode(
            data=self._position_history[: self._current_history_len, self._S_D_COL]
        )

        # Calculate step duration mode cumulative average for new position point (Column S_D_MODE_AVG_COL)
        self._position_history[
            self._current_history_len - 1, self._S_D_MODE_AVG_COL
        ] = cumulative_average(
            prev_cumulative_average=self._position_history[
                self._current_history_len - 2, self._S_D_MODE_AVG_COL
            ],
            new_value=self._position_history[
                self._current_history_len - 1, self._S_D_MODE_COL
            ],
            number_of_history_points=self._current_history_len,
        )

        # Add position for new position point (Column POS_COL)
        self._position_history[self._current_history_len - 1, self._DIST_COL] = position

        # Add speed for new position point (Column SPEED_COL)
        self._position_history[self._current_history_len - 1, self._SPEED_COL] = (
            self._position_history[self._current_history_len - 1, self._DIST_COL]
            - self._position_history[self._current_history_len - 2, self._DIST_COL]
        ) / self._position_history[self._current_history_len - 1, self._S_D_COL]

        # Add acceleration for new position point (Column ACCEL_COL)
        if self._current_history_len >= 3:
            self._position_history[self._current_history_len - 1, self._ACCEL_COL] = (
                self._position_history[self._current_history_len - 1, self._SPEED_COL]
                - self._position_history[self._current_history_len - 2, self._SPEED_COL]
            ) / self._position_history[self._current_history_len - 1, self._S_D_COL]
        else:
            self._position_history[self._current_history_len - 1, self._ACCEL_COL] = 0

        # Add jerk for new position point (Column JERK_COL)
        if self._current_history_len >= 4:
            self._position_history[self._current_history_len - 1, self._JERK_COL] = (
                self._position_history[self._current_history_len - 1, self._ACCEL_COL]
                - self._position_history[self._current_history_len - 2, self._ACCEL_COL]
            ) / self._position_history[self._current_history_len - 1, self._S_D_COL]
        else:
            self._position_history[self._current_history_len - 1, self._JERK_COL] = 0

        self._eh.post(
            event_type="encoder sensor",
            message=f"Added position: time: {a_time}, pos.: {position}",
        )

    @property
    def distance(self) -> float:
        """
        Getter for Distance Encoder has observed
        """
        distance: float = self._position_history[
            self._current_history_len - 1, self._DIST_COL
        ]
        self._eh.post(event_type="encoder sensor", message=f"Distance: {distance:.2f}")
        return distance

    @property
    def speed(self) -> float:
        """
        Getter for speed Encoder has observed, averaged by time over the
        duration specified.
        """
        if self._current_history_len < 3:
            return 0

        # find the row number of the first data point with cumulative time > _average_duration
        self._history_lines_to_use = self._row_with_cumulative_time_greater_than_target(
            self._average_duration
        )

        speeds_list: npt.ArrayLike = self._position_history[
            self._current_history_len
            - self._history_lines_to_use : self._current_history_len,
            self._SPEED_COL,
        ]

        avg_speed: float = float(np.average(speeds_list))
        self._eh.post(event_type="encoder sensor", message=f"Speed: {avg_speed:.2f}")
        return avg_speed

    @property
    def accel(self) -> float:
        """
        Getter for acceleration Encoder has observed, averaged by time over
        the duration specified.
        """
        if self._current_history_len < 3:
            return 0

        # find the row number of the first data point with cumulative time > _average_duration
        self._history_lines_to_use = self._row_with_cumulative_time_greater_than_target(
            self._average_duration
        )

        accels_list: npt.ArrayLike = self._position_history[
            self._current_history_len
            - self._history_lines_to_use : self._current_history_len,
            self._ACCEL_COL,
        ]

        avg_accel: float = float(np.average(accels_list))
        self._eh.post(event_type="encoder sensor", message=f"Accel: {avg_accel:.2f}")
        return avg_accel

    @property
    def jerk(self) -> float:
        """
        Getter for jerk Encoder has observed, averaged by time over
        the duration specifieda.
        """
        if self._current_history_len < 4:
            return 0

        # find the row number of the first data point with cumulative time > _average_duration
        self._history_lines_to_use = self._row_with_cumulative_time_greater_than_target(
            self._average_duration
        )

        jerks_list: npt.ArrayLike = self._position_history[
            self._current_history_len
            - self._history_lines_to_use : self._current_history_len,
            self._JERK_COL,
        ]

        avg_jerk: float = float(
            np.average(jerks_list)
        self._eh.post(event_type="encoder sensor", message=f"Jerk: {avg_jerk:.2f}")
        return avg_jerk

    def _row_with_cumulative_time_greater_than_target(self, target: float):
        # find the row number of the first data point with cumulative time > _average_duration
        self._history_lines_to_use = np.argmax(self._position_history[:, 0] >= target)

        # If we don't have enough for average duration, use all we have
        if self._history_lines_to_use == 0:
            self._history_lines_to_use = self._current_history_len

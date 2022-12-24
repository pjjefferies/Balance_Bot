#! /usr/bin/python

from typing import Tuple, Union

from gpiozero import Motor

from event import EventHandler

AVAIL_GPIO_PINS: Tuple[Union[int, str]] = tuple(range(2, 28)) + tuple(
    ["GPIO" + str(a_no) for a_no in range(2, 28)]
)


class RPI_Motor:
    """
    Object for indivisual Motor control - direction, speed
    """

    def __init__(
        self, forward: Union[int, str], rearward: Union[int, str], eh: EventHandler
    ):
        if forward not in RPI_GPIO_PINS or rearward not in RPI_GPIO_PINS:
            raise ValueError(
                f"forward and rearward must be one of the following: {AVAIL_GPIO_PINS}"
            )
        self._motor = Motor(forward=forward, backward=backward, pwm=True)
        self._motor.value = 0
        self._eh = eh
        self._eh.post(
            event_type="robot moved",
            message="RPI_Motor created with pins {fowrard} and {rearward}",
        )

    @property
    def value(self) -> float:
        self._eh.post(
            event_type="robot moved",
            message="RPI_Motor, on Pins {fowrard} and {rearward}, moving at velocity: {self._motor.value}",
        )
        return self._motor.value

    @value.setter
    def value(self, value: float) -> None:
        """
        Method to move motor
        velocity:  1 = Forward at full speed
        velocity:  0 = Stop
        velocity: -1 = Rearward at full speed
        """
        velocity = min(max(value, -1), 1)
        self._motor.value = velocity
        self._eh.post(
            event_type="robot moved",
            message="RPI_Motor, on Pins {fowrard} and {rearward}, moving at velocity: {self._motor.value}",
        )

    def stop(self) -> None:
        self._motor.value = 0
        self._eh.post(
            event_type="robot moved",
            message="RPI_Motor, on Pins {fowrard} and {rearward}, stopped",
        )

    def close(self):
        self._motor.close()
        self._eh.post(
            event_type="robot moved",
            message="RPI_Motor, on Pins {fowrard} and {rearward}, destroyed",
        )

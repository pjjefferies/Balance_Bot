#!/usr/bin/env python3

from gpiozero import Motor

from balance_bot.event import EventHandler

RPI_GPIO_PINS: tuple[int | str] = tuple(range(2, 28)) + tuple(
    ["GPIO" + str(a_no) for a_no in range(2, 28)]
)


class RPI_Motor:
    """
    Object for indivisual Motor control - direction, speed
    """

    def __init__(
        self,
        *,
        forward: int | str,
        backward: int | str,
        pwm: bool = True,
        eh: EventHandler,
    ):
        if forward not in RPI_GPIO_PINS or backward not in RPI_GPIO_PINS:
            raise ValueError(
                f"forward and rearward must be one of the following: {RPI_GPIO_PINS}"
            )
        self._motor = Motor(forward=forward, backward=backward, pwm=pwm)
        self._motor.value = 0
        self._forward_pin = forward
        self._backward_pin = backward
        self._eh = eh
        self._eh.post(
            event_type="robot moved",
            message=f"RPI_Motor created with pins {forward} and {backward}",
        )

    @property
    def value(self) -> float:
        self._eh.post(
            event_type="robot moved",
            message=f"RPI_Motor, on Pins {self._forward_pin} and {self._backward_pin}, moving at velocity: {self._motor.value}",
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
            message=f"RPI_Motor, on Pins {self._forward_pin} and {self._backward_pin}, moving at velocity: {self._motor.value}",
        )

    def stop(self) -> None:
        self._motor.value = 0
        self._eh.post(
            event_type="robot moved",
            message=f"RPI_Motor, on Pins {self._forward_pin} and {self._backward_pin}, stopped",
        )

    def close(self):
        self._motor.close()
        self._eh.post(
            event_type="robot moved",
            message=f"RPI_Motor, on Pins {self._forward_pin} and {self._backward_pin}, destroyed",
        )

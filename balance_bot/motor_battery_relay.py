#! /usr/bin/python3


from typing import Tuple, Union

from gpiozero import OutputDevice

from .event import EventHandler

AVAIL_GPIO_PINS: Tuple[Union[int, str]] = tuple(range(2, 28)) + tuple(
    ["GPIO" + str(a_no) for a_no in range(2, 28)]
)


class MotorBatteryRelay:
    """
    Representation of relay used to turn power on to Motor Controller.
    This is used to optionally turn on power with RPi to avoid having
    to use manual switch. Relay input is grounded to activate.
    """

    def __init__(self, gpio_pin_no: Union[int, str], eh: EventHandler):
        if gpio_pin_no not in (AVAIL_GPIO_PINS):
            raise ValueError(
                f"gpio_pin_no must be one of the following: {AVAIL_GPIO_PINS}"
            )

        self._relay = OutputDevice(gpio_pin_no, active_high=False, initial_value=False)
        self._gpio_pin_no = gpio_pin_no
        self._eh = eh

        eh.post(
            event_type="power", message=f"Output Device Created on pin: {gpio_pin_no}"
        )

    def on(self) -> None:
        self._eh.post(
            event_type="power",
            message=f"Output Device on pin {self._gpio_pin_no} turned: on",
        )
        self._relay.on()

    def off(self) -> None:
        self._eh.post(
            event_type="power",
            message=f"Output Device on pin {self._gpio_pin_no} turned: on",
        )
        self._relay.off()

    @property
    def active(self) -> bool:
        return bool(self._relay.value)

    def close(self):
        self._relay.close()

#!/usr/bin/env python3

from logging import Logger

from gpiozero import OutputDevice

AVAIL_GPIO_PINS: list[int | str] = list(range(2, 28)) + [
    "GPIO" + str(a_no) for a_no in range(2, 28)
]


class MotorBatteryRelay:
    """
    Representation of relay used to turn power on to Motor Controller.
    This is used to optionally turn on power with RPi to avoid having
    to use manual switch. Relay input is grounded to activate.
    """

    def __init__(self, *, gpio_pin_no: int | str, logger: Logger):
        if gpio_pin_no not in AVAIL_GPIO_PINS:
            raise ValueError(
                f"gpio_pin_no must be one of the following: {AVAIL_GPIO_PINS}"
            )
        self._relay = OutputDevice(gpio_pin_no, active_high=False, initial_value=False)
        self._gpio_pin_no = gpio_pin_no
        self._logger = logger
        self._logger.info(f"power: Motor Battery Relay Created on pin: {gpio_pin_no}")

    def on(self) -> None:
        self._logger.info(
            f"power: Motor Battery Relay on pin {self._gpio_pin_no} turned: on"
        )
        self._relay.on()

    def off(self) -> None:
        self._logger.info(
            f"power: Motor Battery Relay on pin {self._gpio_pin_no} turned: off"
        )
        self._relay.off()

    @property
    def active(self) -> bool:
        return bool(self._relay.value)

    def close(self):
        self._logger.info(
            f"power: Motor Battery Relay on pin {self._gpio_pin_no} destroyed"
        )
        self._relay.close()

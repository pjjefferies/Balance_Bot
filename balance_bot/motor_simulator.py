#! /usr/bin/python3

import logging


logger = logging.getLogger(__name__)


class MotorSim:
    def __init__(self):
        logger.info("We have a simululated motor")
        self._value = 0

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, value: float) -> None:
        self._value = min(max(value, -1), 1)
        if self._value > 0:
            logger.info(f"Vroom! Moving Forward at speed: {self._value}")
        elif self._value < 0:
            logger.info(f"Vroom! Moving rearward at speed: {self._value}")
        else:
            logger.info(f"Stopped")

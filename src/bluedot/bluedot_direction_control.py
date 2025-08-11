"""Bluedot Phone App Interface"""

from logging import Logger
from typing import Protocol

import bluedot  # type:ignore


class BlueDotRobotController:
    def __init__(self, logger: Logger, timeout: int = 60) -> None:
        self._logger = logger
        self._logger.info(msg=f"bluedot: Starting BlueDot receiver")
        self._bd: bluedot.BlueDot = bluedot.BlueDot()

        logger.info(msg=f"bluedot: Receiver started. Establishing connection...")

        if not self._bd.wait_for_connection(timeout=timeout):  # type:ignore
            raise ConnectionError("Could not connect to BlueDot controller")

        logger.info(msg=f"bluedot: Connection established.")
        self._running: bool = True

    @property
    def bd_drive(self) -> tuple[float, float]:
        """
        BlueDot wrapper to send y (fwd/rwd), x (right/left) when bluedot is touched
        or 0, 0 if it's not pressed.
        """
        if not self._running:
            return 0, 0

        if self._bd.is_pressed:
            return -self._bd.position.x, -self._bd.position.y  # type:ignore
        else:
            return 0, 0

    def start(self) -> None:
        self._logger.info(msg=f"bluedot: BlueDot sending directions")
        self._running = True

    def stop(self) -> None:
        self._logger.info(msg=f"bluedot: BlueDot not sending directions")
        self._running = False

#! /usr/bin/python3

from typing import Tuple  # Protocol
import bluedot
from event import EventHandler

# from config import cfg

"""
Not needed until Python V3.10 can be implemented on Raspberry Pi. As of Dec. 2022, dbus package does
not work with 32-bit Linux (e.g. Raspberry Pi).

class EventHandlerTemplate(Protocol):
    def post(self, *, event_type: str, message: str) -> None:
        raise NotImplementedError
"""


class BlueDotRobotController:
    def __init__(self, eh: EventHandler, timeout: int = 60) -> None:
        self._eh = eh
        eh.post(event_type="bluedot", message="Starting BlueDot receiver")
        self._bd: bluedot.BlueDot = bluedot.BlueDot()

        eh.post(
            event_type="bluedot", message="Receiver started. Establishing connection..."
        )

        if not self._bd.wait_for_connection(timeout=timeout):
            raise ConnectionError("Could not connect to BlueDot controller")

        eh.post(event_type="bluedot", message="Connection established.")
        self._running: bool = True

    def bd_drive(self) -> Tuple[float, float]:
        """
        BlueDot wrapper to send y (fwd/rwd), x (right/left) when bluedot is touched
        or 0, 0 if it's not pressed.
        """
        if not self._running:
            return 0, 0

        if self._bd.is_pressed:
            return -self._bd.position.x, -self._bd.position.y
        else:
            return 0, 0

    def start(self) -> None:
        self._eh.post(event_type="bluedot", message="BlueDot sending directions")
        self._running = True

    def stop(self) -> None:
        self._eh.post(event_type="bluedot", message="BlueDot not sending directions")
        self._running = False

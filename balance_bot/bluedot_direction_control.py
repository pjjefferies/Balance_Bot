#! /usr/bin/python3

from typing import Protocol
import bluedot

# from config import cfg


class EventHandlerTemplate(Protocol):
    def post(self, *, event_type: str, message: str) -> None:
        raise NotImplementedError


class BlueDotRobotController:
    def __init__(self, eh: EventHandlerTemplate) -> None:
        self._eh = eh
        eh.post(event_type="bluedot", message="Starting BlueDot receiver")
        self._bd: bluedot.BlueDot = bluedot.BlueDot()

        eh.post(
            event_type="bluedot", message="Receiver started. Establishing connection..."
        )

        self._bd.wait_for_connection()

        eh.post(event_type="bluedot", message="Connection established.")
        self._running: bool = True

    def bd_drive(self) -> tuple[float, float]:
        """
        BlueDot wrapper to send y (fwd/rwd), x (right/left) when bluedot is touched
        or 0, 0 if it's not pressed.
        """
        if not self._running:
            return 0, 0

        if self._bd.is_pressed:
            return -bd.position.x, -bd.position.y
        else:
            return 0, 0

    def start(self) -> None:
        self._eh.post(event_type="bluedot", message="BlueDot sending directions")
        self._running = True

    def stop(self) -> None:
        self._eh.post(event_type="bluedot", message="BlueDot not sending directions")
        self._running = False

#! /usr/bin/python3

"""
Not needed until Python V3.10 can be implemented on Raspberry Pi. As of Dec. 2022, dbus package does
not work with 32-bit Linux (e.g. Raspberry Pi).

class EventHandlerTemplate:
    def post(self, *, event_type: str, message: str) -> None:
        raise NotImplementedError
"""
from event import EventHandler


class MotorSim:
    def __init__(self, eh: EventHandler) -> None:
        self._eh.post(event_type="robot moved", message=f"We have a simululated motor")
        self._value: float = 0
        self._eh: EventHandler = eh

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, value: float) -> None:
        self._value = min(max(value, -1), 1)
        if self._value > 0:
            self._eh.post(
                event_type="robot moved",
                message=f"Vroom! Moving Forward at speed: {self._value}",
            )
        elif self._value < 0:
            self._eh.post(
                event_type="robot moved",
                message=f"Vroom! Moving Rearward at speed: {self._value}",
            )
        else:
            self._eh.post(event_type="robot moved", message=f"Stopped")

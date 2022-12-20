#! /usr/bin/python3

# Based on Observer Pattern Tutorial by ArjanCodes on YouTube
# https://www.youtube.com/watch?v=oNalXg67XEE&t=0s

from typing import Callable, Optional


class EventHandler:
    def __init__(self) -> None:
        self._subscribers: dict[
            str, list[Callable[[str, Optional[str], str], None]]
        ] = dict()

    def subscribe(
        self, *, event_type: str, fn: Callable[[str, Optional[str], str], None]
    ) -> None:
        if not event_type in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(fn)

    def post(
        self, *, event_type: str, level: Optional[str] = None, message: str
    ) -> None:
        if not event_type in self._subscribers:
            return
        for fn in self._subscribers[event_type]:
            fn(event_type=event_type, level=level, message=message)

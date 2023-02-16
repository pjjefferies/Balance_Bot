#!/usr/bin/env python3

# Based on Observer Pattern Tutorial by ArjanCodes on YouTube
# https://www.youtube.com/watch?v=oNalXg67XEE&t=0s

from typing import Callable, Optional, Any


class EventHandler:
    def __init__(self) -> None:
        self._subscribers: dict[
            str,
            list[
                Callable[
                    [
                        str,
                        str,
                        Optional[str],
                    ],
                    None,
                ]
            ],
        ] = dict()

    def subscribe(
        self,
        *,
        event_type: str,
        fn: Callable[[str, str | Any, Optional[str]], None],
    ) -> None:
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(fn)

    def post(
        self,
        *,
        event_type: str,
        message: str | Any,
        level: Optional[str] = None,
    ) -> None:
        if event_type not in self._subscribers:
            raise ValueError(f"event_type: '{event_type}' not found")
        for fn in self._subscribers[event_type]:
            fn(event_type, message, level)

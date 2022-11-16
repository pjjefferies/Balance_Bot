#! /usr/bin/python3

# Based on Observer Pattern Tutorial by ArjanCodes o YouTube
# https://www.youtube.com/watch?v=oNalXg67XEE&t=0s

from typing import Callable

subscribers: dict[str, list[Callable[[str], None]]] = dict()


def subscribe(*, event_type: str, fn: Callable[[str], None]) -> None:
    if not event_type in subscribers:
        subscribers[event_type] = []
    subscribers[event_type].append(fn)


def post_event(*, event_type: str, message: str) -> None:
    if not event_type in subscribers:
        return
    for fn in subscribers[event_type]:
        fn(message=message)

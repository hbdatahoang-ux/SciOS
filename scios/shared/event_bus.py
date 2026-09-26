"""
SciOS Shared Event Bus
======================

Thread-safe publish/subscribe event bus shared across
Kernel, Runtime, Cognitive Core, and Agents.
"""

from __future__ import annotations

from collections import defaultdict
from threading import RLock
from typing import Any, Callable

EventHandler = Callable[..., None]


class EventBus:
    """
    Thread-safe publish/subscribe event bus.
    """

    def __init__(self) -> None:
        self._subscribers: dict[str, list[EventHandler]] = defaultdict(list)
        self._lock = RLock()

    def subscribe(
        self,
        event: str,
        handler: EventHandler,
    ) -> None:
        """
        Subscribe a handler to an event.
        """
        with self._lock:
            if handler not in self._subscribers[event]:
                self._subscribers[event].append(handler)

    def unsubscribe(
        self,
        event: str,
        handler: EventHandler,
    ) -> None:
        """
        Unsubscribe a handler.
        """
        with self._lock:
            if handler in self._subscribers[event]:
                self._subscribers[event].remove(handler)

    def publish(
        self,
        event: str,
        **payload: Any,
    ) -> None:
        """
        Publish an event.
        """
        with self._lock:
            handlers = tuple(self._subscribers[event])

        for handler in handlers:
            handler(**payload)

    def subscribers(
        self,
        event: str,
    ) -> tuple[EventHandler, ...]:
        """
        Return subscribers of an event.
        """
        with self._lock:
            return tuple(self._subscribers[event])

    def clear(self) -> None:
        """
        Remove all subscriptions.
        """
        with self._lock:
            self._subscribers.clear()

    def __len__(self) -> int:
        with self._lock:
            return sum(len(v) for v in self._subscribers.values())

    def __repr__(self) -> str:
        return (
            f"EventBus(events={len(self._subscribers)}, "
            f"subscribers={len(self)})"
        )
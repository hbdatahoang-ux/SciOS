"""
SciOS Kernel Event Bus
======================

Thread-safe publish/subscribe event bus used throughout the SciOS Kernel.

Responsibilities
----------------
- Publish events
- Subscribe handlers
- Unsubscribe handlers
- Middleware execution
- Event filtering
- Exception isolation

Design Goals
------------
- Thread-safe
- Lightweight
- Fast
- Extensible
- Runtime independent
"""

from __future__ import annotations

from collections import defaultdict
from threading import RLock
from typing import Any
from typing import Callable

from .event import Event


EventHandler = Callable[[Event], None]


class EventBus:
    """
    Central event bus for SciOS.

    Supports topic-based publish/subscribe.

    Example
    -------
    >>> bus = EventBus()
    >>> bus.subscribe("task.completed", handler)
    >>> bus.publish("task.completed", result=42)
    """

    def __init__(self) -> None:

        self._subscribers: dict[
            str,
            list[EventHandler],
        ] = defaultdict(list)

        self._middleware: list[Callable[[Event], Event]] = []

        self._filters: list[Callable[[Event], bool]] = []

        self._lock = RLock()

        self._published = 0

    # ==========================================================
    # Subscription
    # ==========================================================

    def subscribe(
        self,
        topic: str,
        handler: EventHandler,
    ) -> None:
        """
        Subscribe a handler to a topic.
        """

        with self._lock:

            if handler not in self._subscribers[topic]:
                self._subscribers[topic].append(handler)

    def unsubscribe(
        self,
        topic: str,
        handler: EventHandler,
    ) -> None:
        """
        Remove a subscription.
        """

        with self._lock:

            if handler in self._subscribers[topic]:
                self._subscribers[topic].remove(handler)

    def clear_subscribers(self) -> None:
        """
        Remove all subscribers.
        """

        with self._lock:
            self._subscribers.clear()

    # ==========================================================
    # Middleware
    # ==========================================================

    def add_middleware(
        self,
        middleware: Callable[[Event], Event],
    ) -> None:
        """
        Register middleware.
        """

        self._middleware.append(middleware)

    # ==========================================================
    # Filters
    # ==========================================================

    def add_filter(
        self,
        predicate: Callable[[Event], bool],
    ) -> None:
        """
        Register an event filter.
        """

        self._filters.append(predicate)

    # ==========================================================
    # Publish
    # ==========================================================

    def publish(
        self,
        topic: str,
        **payload: Any,
    ) -> Event:
        """
        Publish an event.

        Returns
        -------
        Event
            Published event instance.
        """

        event = Event(
            topic=topic,
            payload=payload,
        )

        # Apply middleware

        for middleware in self._middleware:
            event = middleware(event)

        # Apply filters

        for predicate in self._filters:

            if not predicate(event):
                return event

        # Snapshot subscribers

        with self._lock:

            subscribers = list(
                self._subscribers.get(topic, [])
            )

            wildcard = list(
                self._subscribers.get("*", [])
            )

            self._published += 1

        # Notify subscribers

        for handler in subscribers + wildcard:

            try:
                handler(event)

            except Exception:
                # Never allow one subscriber
                # to break the event system.
                continue

        return event

    # ==========================================================
    # Query
    # ==========================================================

    def topics(self) -> list[str]:
        """
        Registered topics.
        """

        with self._lock:
            return sorted(self._subscribers.keys())

    def subscribers(
        self,
        topic: str,
    ) -> list[EventHandler]:
        """
        Handlers subscribed to topic.
        """

        with self._lock:
            return list(
                self._subscribers.get(topic, [])
            )

    def subscriber_count(
        self,
        topic: str | None = None,
    ) -> int:
        """
        Count subscribers.

        If topic is None count all.
        """

        with self._lock:

            if topic is None:

                return sum(
                    len(v)
                    for v in self._subscribers.values()
                )

            return len(
                self._subscribers.get(topic, [])
            )

    @property
    def events_published(self) -> int:
        return self._published

    # ==========================================================
    # Maintenance
    # ==========================================================

    def reset(self) -> None:
        """
        Reset the event bus.
        """

        with self._lock:

            self._subscribers.clear()

            self._middleware.clear()

            self._filters.clear()

            self._published = 0

    def status(self) -> dict[str, Any]:
        """
        EventBus status.
        """

        return {
            "topics": len(self._subscribers),
            "subscribers": self.subscriber_count(),
            "middleware": len(self._middleware),
            "filters": len(self._filters),
            "events_published": self._published,
        }

    # ==========================================================
    # Magic Methods
    # ==========================================================

    def __contains__(
        self,
        topic: object,
    ) -> bool:

        return (
            isinstance(topic, str)
            and topic in self._subscribers
        )

    def __len__(self) -> int:
        return len(self._subscribers)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"topics={len(self)}, "
            f"subscribers={self.subscriber_count()}, "
            f"published={self._published})"
        )
"""
SciOS Event Subscriber
======================

Subscriber API for the SciOS EventBus.

Responsibilities
----------------
- Subscribe to topics
- Unsubscribe from topics
- Register callbacks
- Pause / Resume subscriptions
- Batch subscription management

Design Goals
------------
- Lightweight
- Thread-safe
- Easy to extend
- Runtime independent
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .bus import EventBus
from .event import Event

__all__ = [
    "Subscriber",
]

EventHandler = Callable[[Event], None]


class Subscriber:
    """
    High-level EventBus subscriber.

    Example
    -------
    >>> bus = EventBus()

    >>> def on_completed(event):
    ...     print(event.payload)

    >>> subscriber = Subscriber(bus)

    >>> subscriber.subscribe(
    ...     "task.completed",
    ...     on_completed,
    ... )

    >>> subscriber.unsubscribe(
    ...     "task.completed",
    ...     on_completed,
    ... )
    """

    def __init__(
        self,
        bus: EventBus,
        *,
        name: str | None = None,
    ) -> None:
        self._bus = bus
        self._name = name or self.__class__.__name__
        self._enabled = True

        self._subscriptions: dict[
            str,
            list[EventHandler],
        ] = {}

    # ======================================================
    # Subscription
    # ======================================================

    def subscribe(
        self,
        topic: str,
        handler: EventHandler,
    ) -> None:
        """
        Subscribe to a topic.
        """

        self._bus.subscribe(topic, handler)

        self._subscriptions.setdefault(
            topic,
            [],
        ).append(handler)

    def unsubscribe(
        self,
        topic: str,
        handler: EventHandler,
    ) -> None:
        """
        Remove a subscription.
        """

        self._bus.unsubscribe(topic, handler)

        handlers = self._subscriptions.get(topic)

        if handlers and handler in handlers:
            handlers.remove(handler)

            if not handlers:
                del self._subscriptions[topic]

    def unsubscribe_all(self) -> None:
        """
        Remove all subscriptions.
        """

        for topic, handlers in list(
            self._subscriptions.items()
        ):
            for handler in list(handlers):
                self._bus.unsubscribe(
                    topic,
                    handler,
                )

        self._subscriptions.clear()

    # ======================================================
    # Lifecycle
    # ======================================================

    def enable(self) -> None:
        """
        Enable subscriber.
        """
        self._enabled = True

    def disable(self) -> None:
        """
        Disable subscriber.
        """
        self._enabled = False

    @property
    def enabled(self) -> bool:
        """
        Whether subscriber is enabled.
        """
        return self._enabled

    # ======================================================
    # Query
    # ======================================================

    @property
    def bus(self) -> EventBus:
        return self._bus

    @property
    def name(self) -> str:
        return self._name

    def topics(self) -> list[str]:
        """
        Return subscribed topics.
        """
        return sorted(
            self._subscriptions.keys()
        )

    def handlers(
        self,
        topic: str,
    ) -> list[EventHandler]:
        """
        Handlers for a topic.
        """

        return list(
            self._subscriptions.get(
                topic,
                [],
            )
        )

    def subscription_count(self) -> int:
        """
        Total subscriptions.
        """

        return sum(
            len(v)
            for v in self._subscriptions.values()
        )

    def status(self) -> dict[str, Any]:
        """
        Subscriber status.
        """

        return {
            "name": self._name,
            "enabled": self._enabled,
            "topics": len(self._subscriptions),
            "subscriptions": self.subscription_count(),
        }

    # ======================================================
    # Context Manager
    # ======================================================

    def __enter__(self) -> "Subscriber":
        return self

    def __exit__(
        self,
        exc_type,
        exc,
        tb,
    ) -> None:
        self.unsubscribe_all()

    # ======================================================
    # Representation
    # ======================================================

    def __len__(self) -> int:
        return self.subscription_count()

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name={self._name!r}, "
            f"topics={len(self._subscriptions)}, "
            f"subscriptions={self.subscription_count()}, "
            f"enabled={self._enabled})"
        )
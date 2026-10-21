"""
SciOS Event Publisher
=====================

Publisher interface for the SciOS EventBus.

Responsibilities
----------------
- Publish events
- Publish Event objects
- Convenience APIs
- Batch publishing

Design Goals
------------
- Lightweight
- EventBus independent
- Type-safe
- Easy to extend
"""

from __future__ import annotations

from typing import Any
from collections.abc import Iterable

from .bus import EventBus
from .event import Event

__all__ = [
    "Publisher",
]


class Publisher:
    """
    High-level publisher API.

    Examples
    --------
    >>> bus = EventBus()
    >>> publisher = Publisher(bus)

    >>> publisher.publish(
    ...     "task.started",
    ...     task="hello"
    ... )

    >>> event = Event(
    ...     topic="runtime.completed",
    ...     payload={"result": 42},
    ... )
    >>> publisher.publish_event(event)
    """

    def __init__(
        self,
        bus: EventBus,
        *,
        source: str | None = None,
    ) -> None:
        self._bus = bus
        self._source = source

    # ======================================================
    # Basic Publishing
    # ======================================================

    def publish(
        self,
        topic: str,
        **payload: Any,
    ) -> Event:
        """
        Publish an event by topic.
        """

        if self._source is not None:
            payload.setdefault("source", self._source)

        return self._bus.publish(
            topic,
            **payload,
        )

    def publish_event(
        self,
        event: Event,
    ) -> Event:
        """
        Publish an Event instance.
        """

        return self._bus.publish(
            event.topic,
            **event.payload,
        )

    # ======================================================
    # Batch Publishing
    # ======================================================

    def publish_many(
        self,
        events: Iterable[Event],
    ) -> list[Event]:
        """
        Publish multiple events.
        """

        published: list[Event] = []

        for event in events:
            published.append(
                self.publish_event(event)
            )

        return published

    # ======================================================
    # Convenience APIs
    # ======================================================

    def info(
        self,
        message: str,
        **payload: Any,
    ) -> Event:
        """
        Publish informational event.
        """

        payload["message"] = message

        return self.publish(
            "system.info",
            **payload,
        )

    def warning(
        self,
        message: str,
        **payload: Any,
    ) -> Event:
        """
        Publish warning event.
        """

        payload["message"] = message

        return self.publish(
            "system.warning",
            **payload,
        )

    def error(
        self,
        message: str,
        **payload: Any,
    ) -> Event:
        """
        Publish error event.
        """

        payload["message"] = message

        return self.publish(
            "system.error",
            **payload,
        )

    # ======================================================
    # Properties
    # ======================================================

    @property
    def bus(self) -> EventBus:
        """
        Underlying EventBus.
        """
        return self._bus

    @property
    def source(self) -> str | None:
        """
        Publisher source identifier.
        """
        return self._source

    # ======================================================
    # Status
    # ======================================================

    def status(self) -> dict[str, Any]:
        """
        Publisher status.
        """

        return {
            "source": self._source,
            "events_published": self._bus.events_published,
        }

    # ======================================================
    # Representation
    # ======================================================

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"source={self._source!r})"
        )
"""
SciOS Event Bus
===============

Lightweight publish/subscribe event bus for the SciOS Kernel.

Responsibilities
----------------
- Publish kernel events
- Subscribe event handlers
- Decouple kernel components
- Maintain event statistics
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable

__all__ = [
    "Event",
    "EventBus",
]


# ==========================================================
# Event
# ==========================================================

@dataclass(slots=True)
class Event:
    """
    Kernel event.
    """

    name: str

    payload: dict[str, Any] = field(default_factory=dict)

    timestamp: str = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        ).isoformat()
    )


# ==========================================================
# Event Bus
# ==========================================================

class EventBus:
    """
    Publish/Subscribe event bus.

    Used internally by the SciOS Kernel.
    """

    def __init__(self) -> None:

        self._subscribers: dict[
            str,
            list[Callable[[Event], None]]
        ] = defaultdict(list)

        self._published = 0

    # =====================================================
    # Subscription
    # =====================================================

    def subscribe(
        self,
        event: str,
        handler: Callable[[Event], None],
    ) -> None:
        """
        Subscribe a handler to an event.
        """

        if handler not in self._subscribers[event]:
            self._subscribers[event].append(handler)

    def unsubscribe(
        self,
        event: str,
        handler: Callable[[Event], None],
    ) -> None:
        """
        Remove a subscription.
        """

        if event not in self._subscribers:
            return

        if handler in self._subscribers[event]:
            self._subscribers[event].remove(handler)

    # =====================================================
    # Publishing
    # =====================================================

    def publish(
        self,
        event: str,
        **payload: Any,
    ) -> Event:
        """
        Publish an event.
        """

        evt = Event(
            name=event,
            payload=payload,
        )

        self._published += 1

        for handler in list(
            self._subscribers.get(event, [])
        ):
            handler(evt)

        return evt

    # =====================================================
    # Queries
    # =====================================================

    def listeners(
        self,
        event: str,
    ) -> int:

        return len(
            self._subscribers.get(event, [])
        )

    def clear(self) -> None:

        self._subscribers.clear()

    # =====================================================
    # Status
    # =====================================================

    def status(self) -> dict[str, Any]:

        return {

            "events": len(self._subscribers),

            "published": self._published,

            "subscribers": {
                name: len(handlers)
                for name, handlers
                in self._subscribers.items()
            },
        }

    # =====================================================
    # Python Protocols
    # =====================================================

    def __contains__(
        self,
        event: str,
    ) -> bool:

        return event in self._subscribers

    def __len__(self) -> int:

        return len(self._subscribers)

    def __repr__(self) -> str:

        return (
            "EventBus("
            f"events={len(self)}, "
            f"published={self._published})"
        )
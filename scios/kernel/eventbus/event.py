"""
SciOS Kernel Events
===================

Canonical event models used throughout the SciOS Kernel.

Responsibilities
----------------
- Immutable event object
- Event metadata
- Event identifiers
- Timestamping
- Serialization
- Factory methods

Design Goals
------------
- Lightweight
- Immutable
- Thread-safe
- Serializable
- Runtime independent
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from datetime import datetime
from datetime import timezone

from typing import Any
import uuid


__all__ = [
    "Event",
]


# ==========================================================
# Event
# ==========================================================


@dataclass(slots=True, frozen=True)
class Event:
    """
    Immutable event object.

    Parameters
    ----------
    topic:
        Event topic.

    payload:
        Event payload.

    source:
        Event producer.

    correlation_id:
        Distributed tracing identifier.

    event_id:
        Unique event identifier.

    timestamp:
        UTC timestamp.
    """

    topic: str

    payload: dict[str, Any] = field(default_factory=dict)

    source: str | None = None

    correlation_id: str | None = None

    event_id: str = field(
        default_factory=lambda: uuid.uuid4().hex
    )

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )

    # ======================================================
    # Serialization
    # ======================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Convert event into dictionary.
        """

        return {
            "event_id": self.event_id,
            "topic": self.topic,
            "payload": self.payload,
            "source": self.source,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "Event":
        """
        Construct Event from dictionary.
        """

        timestamp = data.get("timestamp")

        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)

        return cls(
            topic=data["topic"],
            payload=data.get("payload", {}),
            source=data.get("source"),
            correlation_id=data.get("correlation_id"),
            event_id=data.get(
                "event_id",
                uuid.uuid4().hex,
            ),
            timestamp=timestamp
            or datetime.now(timezone.utc),
        )

    # ======================================================
    # Convenience
    # ======================================================

    @property
    def name(self) -> str:
        """
        Alias of topic.
        """
        return self.topic

    @property
    def age_seconds(self) -> float:
        """
        Event age.
        """

        return (
            datetime.now(timezone.utc)
            - self.timestamp
        ).total_seconds()

    def copy(
        self,
        **updates: Any,
    ) -> "Event":
        """
        Create a modified copy.

        Example
        -------
        event2 = event.copy(
            topic="runtime.completed"
        )
        """

        data = self.to_dict()

        data.update(updates)

        return Event.from_dict(data)

    # ======================================================
    # Representation
    # ======================================================

    def __str__(self) -> str:

        return (
            f"[{self.topic}] "
            f"{self.event_id[:8]}"
        )

    def __repr__(self) -> str:

        return (
            "Event("
            f"topic={self.topic!r}, "
            f"event_id={self.event_id!r}, "
            f"source={self.source!r})"
        )
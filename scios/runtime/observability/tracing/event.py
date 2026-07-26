"""
SciOS Observability - Trace Event
=================================

Atomic timeline event used by Trace and Span.

Responsibilities
----------------
- Represent a single runtime event.
- Store timestamps and metadata.
- Provide serialization helpers.
- Support OpenTelemetry-style event attributes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from .status import ExecutionPhase

__all__ = [
    "Event",
]


def utcnow() -> datetime:
    """
    Return current UTC time with timezone information.
    """
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class Event:
    """
    Atomic runtime event.

    Examples
    --------
    submitted
    started
    before_execute
    after_execute
    completed
    failed
    """

    event_id: str = field(default_factory=lambda: str(uuid4()))

    name: str = ""

    phase: ExecutionPhase = ExecutionPhase.CREATED

    timestamp: datetime = field(default_factory=utcnow)

    severity: str = "INFO"

    attributes: dict[str, Any] = field(default_factory=dict)

    metadata: dict[str, Any] = field(default_factory=dict)

    # =====================================================
    # Helpers
    # =====================================================

    def add_attribute(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Add or update an event attribute.
        """

        self.attributes[key] = value

    def add_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Add metadata.
        """

        self.metadata[key] = value

    # =====================================================
    # Serialization
    # =====================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Convert to dictionary.
        """

        return {
            "event_id": self.event_id,
            "name": self.name,
            "phase": self.phase.value,
            "timestamp": self.timestamp.isoformat(),
            "severity": self.severity,
            "attributes": dict(self.attributes),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "Event":
        """
        Restore Event from dictionary.
        """

        return cls(
            event_id=data["event_id"],
            name=data.get("name", ""),
            phase=ExecutionPhase(
                data.get("phase", ExecutionPhase.CREATED.value)
            ),
            timestamp=datetime.fromisoformat(
                data["timestamp"]
            ),
            severity=data.get("severity", "INFO"),
            attributes=dict(
                data.get("attributes", {})
            ),
            metadata=dict(
                data.get("metadata", {})
            ),
        )

    # =====================================================
    # Representation
    # =====================================================

    def __str__(self) -> str:
        return (
            f"[{self.timestamp.isoformat()}] "
            f"{self.phase.value}: {self.name}"
        )

    def __repr__(self) -> str:
        return (
            f"Event("
            f"name={self.name!r}, "
            f"phase={self.phase.value!r})"
        )
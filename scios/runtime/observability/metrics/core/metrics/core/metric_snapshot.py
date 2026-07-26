"""
SciOS-NG Metrics Core - Metric Snapshot
=======================================

Immutable snapshot of a MetricState.

Design goals
------------
- Immutable
- Hashable
- Serializable
- Thread-safe
- Snapshot-friendly
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import time
import uuid

__all__ = [
    "MetricSnapshot",
]


@dataclass(slots=True, frozen=True)
class MetricSnapshot:
    """
    Immutable snapshot of a MetricState.
    """

    uuid: uuid.UUID

    value: Any = None

    previous_value: Any = None

    update_count: int = 0

    enabled: bool = True

    frozen: bool = False

    closed: bool = False

    timestamp: float = field(default_factory=time.time)

    # ---------------------------------------------------------
    # Serialization
    # ---------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """
        Export snapshot as a serializable dictionary.
        """

        return {
            "uuid": str(self.uuid),
            "value": self.value,
            "previous_value": self.previous_value,
            "update_count": self.update_count,
            "enabled": self.enabled,
            "frozen": self.frozen,
            "closed": self.closed,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "MetricSnapshot":
        """
        Create a snapshot from a dictionary.
        """

        return cls(
            uuid=uuid.UUID(data["uuid"]),
            value=data.get("value"),
            previous_value=data.get("previous_value"),
            update_count=data.get("update_count", 0),
            enabled=data.get("enabled", True),
            frozen=data.get("frozen", False),
            closed=data.get("closed", False),
            timestamp=data.get("timestamp", time.time()),
        )

    # ---------------------------------------------------------
    # Copy
    # ---------------------------------------------------------

    def copy(
        self,
        **updates: Any,
    ) -> "MetricSnapshot":
        """
        Return a modified copy of this snapshot.
        """

        data = self.to_dict()

        # Restore UUID object before reconstruction
        data["uuid"] = self.uuid

        data.update(updates)

        return MetricSnapshot(**data)

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    @property
    def is_active(self) -> bool:
        """
        True if the snapshot represents an active metric.
        """

        return (
            self.enabled
            and not self.frozen
            and not self.closed
        )

    @property
    def age(self) -> float:
        """
        Seconds since the snapshot was created.
        """

        return max(0.0, time.time() - self.timestamp)

    # ---------------------------------------------------------
    # Rich API
    # ---------------------------------------------------------

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"uuid={self.uuid}, "
            f"value={self.value!r}, "
            f"updates={self.update_count})"
        )
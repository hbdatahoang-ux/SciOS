# ==============================================================================
# Part 1. Imports
# ==============================================================================

from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, TypeAlias


# ==============================================================================
# Part 2. Constants
# ==============================================================================

SNAPSHOT_VERSION = "0.1.0"

DEFAULT_TIMESTAMP_FACTORY = (
    lambda: datetime.now(timezone.utc)
)


# ==============================================================================
# Part 3. Exceptions
# ==============================================================================


class MetricSnapshotError(Exception):
    """Base exception for metric snapshots."""


class SnapshotValidationError(
    MetricSnapshotError,
    ValueError,
):
    """Raised when snapshot content is invalid."""


# ==============================================================================
# Part 4. Type Aliases
# ==============================================================================

SnapshotPayload: TypeAlias = dict[str, Any]


# ==============================================================================
# Part 5. Dataclass
# ==============================================================================


@dataclass(slots=True)
class MetricSnapshot:
    """
    Immutable-like snapshot of metric state.
    """

    snapshot: SnapshotPayload = field(
        default_factory=dict,
    )

    created_at: datetime = field(
        default_factory=DEFAULT_TIMESTAMP_FACTORY,
    )

    version: str = SNAPSHOT_VERSION


# ==============================================================================
# Part 6. Constructor Validation
# ==============================================================================

    def __post_init__(self) -> None:
        """
        Validate constructor arguments.
        """

        if not isinstance(self.snapshot, dict):
            raise TypeError(
                "snapshot must be a dictionary."
            )

        if not isinstance(
            self.created_at,
            datetime,
        ):
            raise TypeError(
                "created_at must be a datetime."
            )

        if not isinstance(
            self.version,
            str,
        ):
            raise TypeError(
                "version must be a string."
            )

        self.snapshot = copy.deepcopy(
            self.snapshot,
        )

# ==============================================================================
# Part 7. Properties
# ==============================================================================

    @property
    def timestamp(self) -> datetime:
        """
        Snapshot creation timestamp.
        """
        return self.created_at

    @property
    def payload(self) -> SnapshotPayload:
        """
        Snapshot payload.
        """
        return copy.deepcopy(self.snapshot)


# ==============================================================================
# Part 8. Snapshot Utilities
# ==============================================================================

    @classmethod
    def capture(
        cls,
        payload: SnapshotPayload,
    ) -> "MetricSnapshot":
        """
        Create a snapshot from payload.
        """
        return cls(snapshot=payload)

    def merge(
        self,
        other: "MetricSnapshot",
    ) -> "MetricSnapshot":
        """
        Merge two snapshots.
        """

        if not isinstance(
            other,
            MetricSnapshot,
        ):
            raise TypeError(
                "other must be MetricSnapshot."
            )

        merged = copy.deepcopy(self.snapshot)
        merged.update(other.snapshot)

        return MetricSnapshot(
            snapshot=merged,
        )

    def diff(
        self,
        other: "MetricSnapshot",
    ) -> dict[str, tuple[Any, Any]]:
        """
        Compute differences.
        """

        if not isinstance(
            other,
            MetricSnapshot,
        ):
            raise TypeError(
                "other must be MetricSnapshot."
            )

        result: dict[str, tuple[Any, Any]] = {}

        keys = (
            set(self.snapshot)
            | set(other.snapshot)
        )

        for key in keys:

            left = self.snapshot.get(key)
            right = other.snapshot.get(key)

            if left != right:
                result[key] = (
                    left,
                    right,
                )

        return result

    def clear(self) -> None:
        """
        Remove snapshot payload.
        """
        self.snapshot.clear()

    def is_empty(self) -> bool:
        """
        Return True if payload is empty.
        """
        return len(self.snapshot) == 0

    def checksum(self) -> str:
        """
        Stable checksum.
        """
        payload = json.dumps(
            self.snapshot,
            sort_keys=True,
            default=str,
        )

        return hashlib.sha256(
            payload.encode("utf-8"),
        ).hexdigest()

    def age(self) -> float:
        """
        Snapshot age in seconds.
        """
        return (
            datetime.now(timezone.utc)
            - self.created_at
        ).total_seconds()


# ==============================================================================
# Part 9. Validation
# ==============================================================================

    def validate(self) -> bool:
        """
        Validate snapshot.
        """

        if not isinstance(
            self.snapshot,
            dict,
        ):
            return False

        if not isinstance(
            self.created_at,
            datetime,
        ):
            return False

        if not isinstance(
            self.version,
            str,
        ):
            return False

        return True


# ==============================================================================
# Part 10. Serialization
# ==============================================================================

    def to_dict(self) -> dict[str, Any]:
        return {
            "snapshot": copy.deepcopy(
                self.snapshot,
            ),
            "created_at": self.created_at.isoformat(),
            "version": self.version,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "MetricSnapshot":
        return cls(
            snapshot=copy.deepcopy(
                data.get(
                    "snapshot",
                    {},
                )
            ),
            created_at=datetime.fromisoformat(
                data["created_at"],
            )
            if "created_at" in data
            else DEFAULT_TIMESTAMP_FACTORY(),
            version=data.get(
                "version",
                SNAPSHOT_VERSION,
            ),
        )

    def to_json(self) -> str:
        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            sort_keys=True,
        )

    @classmethod
    def from_json(
        cls,
        payload: str,
    ) -> "MetricSnapshot":
        return cls.from_dict(
            json.loads(payload),
        )


# ==============================================================================
# Part 11. Copy
# ==============================================================================

    def copy(self) -> "MetricSnapshot":
        return MetricSnapshot.from_dict(
            self.to_dict(),
        )

    def clone(self) -> "MetricSnapshot":
        return self.copy()


# ==============================================================================
# Part 12. Equality
# ==============================================================================

    def __eq__(
        self,
        other: object,
    ) -> bool:

        if not isinstance(
            other,
            MetricSnapshot,
        ):
            return NotImplemented

        return (
            self.snapshot == other.snapshot
            and self.created_at == other.created_at
            and self.version == other.version
        )

    def __hash__(self) -> int:
        return hash(
            (
                json.dumps(
                    self.snapshot,
                    sort_keys=True,
                    default=str,
                ),
                self.created_at,
                self.version,
            )
        )


# ==============================================================================
# Part 13. Representation
# ==============================================================================

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(snapshot={self.snapshot!r})"
        )

    def __str__(self) -> str:
        return (
            f"MetricSnapshot"
            f"(size={len(self.snapshot)})"
        )


# ==============================================================================
# Part 14. Public API
# ==============================================================================

__all__ = [
    "SNAPSHOT_VERSION",
    "SnapshotPayload",
    "MetricSnapshotError",
    "SnapshotValidationError",
    "MetricSnapshot",
]        
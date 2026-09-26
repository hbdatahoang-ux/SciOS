"""
SciOS Observability
===================

Metric Snapshot
---------------

Immutable runtime snapshot used by the SciOS Observability
Metrics subsystem.

Responsibilities
----------------
- Capture metric runtime state
- Support snapshot / restore
- Safe serialization
- Copy / clone support
- Change tracking
- Runtime inspection

Design Goals
------------
- Immutable by default
- Thread-safe
- Serialization friendly
- Deep-copy safe
- Production ready
"""

from __future__ import annotations

# ==========================================================
# Imports
# ==========================================================

import json

from copy import deepcopy

from dataclasses import dataclass
from dataclasses import field

from datetime import datetime
from datetime import timezone

from enum import Enum
from enum import auto

from typing import Any
from typing import Final
from typing import Mapping
from typing import TypeAlias

from uuid import UUID

from ..attributes import MetricAttributes
from ..descriptor import MetricDescriptor
from ..labels import MetricLabels
from ..metadata import MetricMetadata

# ==========================================================
# Internal Sentinel
# ==========================================================

_MISSING: Final = object()

# ==========================================================
# Part 4 — Version
# ==========================================================

SNAPSHOT_VERSION: Final[str] = "1.0.0"

SNAPSHOT_API_VERSION: Final[str] = "1"

# ==========================================================
# Part 4 — Constants
# ==========================================================

DEFAULT_SNAPSHOT_NAME: Final[str] = "snapshot"

DEFAULT_SNAPSHOT_NAMESPACE: Final[str] = "metrics"

DEFAULT_SNAPSHOT_REVISION: Final[int] = 0

DEFAULT_SCHEMA_VERSION: Final[int] = 1

DEFAULT_RUNTIME_VERSION: Final[int] = 1

DEFAULT_ENABLED: Final[bool] = True

DEFAULT_FROZEN: Final[bool] = False

DEFAULT_CLOSED: Final[bool] = False

EMPTY_STATISTICS: Final[dict[str, Any]] = {}

EMPTY_METADATA: Final[dict[str, Any]] = {}

EMPTY_LABELS: Final[dict[str, str]] = {}

EMPTY_ATTRIBUTES: Final[dict[str, Any]] = {}

# ==========================================================
# Part 4 — Type Aliases
# ==========================================================

SnapshotID: TypeAlias = UUID

SnapshotValue: TypeAlias = Any

SnapshotRevision: TypeAlias = int

SnapshotTimestamp: TypeAlias = datetime

SnapshotStatistics: TypeAlias = dict[str, Any]

SnapshotMapping: TypeAlias = Mapping[str, Any]

SnapshotDict: TypeAlias = dict[str, Any]


# ==========================================================
# Part 5 — SnapshotState
# ==========================================================

class SnapshotState(Enum):
    """
    Runtime lifecycle state of a metric snapshot.
    """

    CREATED = auto()

    ACTIVE = auto()

    FROZEN = auto()

    RESTORED = auto()

    ARCHIVED = auto()

    INVALID = auto()

# ==========================================================
# Part 6 — MetricSnapshot
# ==========================================================

@dataclass(slots=True)
class MetricSnapshot:
    """
    Immutable runtime snapshot of a metric.
    """

    # ------------------------------------------------------
    # Identity
    # ------------------------------------------------------

    id: SnapshotID

    revision: SnapshotRevision = DEFAULT_SNAPSHOT_REVISION

    schema_version: int = DEFAULT_SCHEMA_VERSION

    runtime_version: int = DEFAULT_RUNTIME_VERSION

    # ------------------------------------------------------
    # Descriptor
    # ------------------------------------------------------

    descriptor: MetricDescriptor | None = None

    # ------------------------------------------------------
    # Metadata
    # ------------------------------------------------------

    metadata: MetricMetadata = field(
        default_factory=MetricMetadata,
    )

    # ------------------------------------------------------
    # Labels
    # ------------------------------------------------------

    labels: MetricLabels = field(
        default_factory=MetricLabels,
    )

    # ------------------------------------------------------
    # Attributes
    # ------------------------------------------------------

    attributes: MetricAttributes = field(
        default_factory=MetricAttributes,
    )

    # ------------------------------------------------------
    # Value
    # ------------------------------------------------------

    value: SnapshotValue = None

    # ------------------------------------------------------
    # Timestamps
    # ------------------------------------------------------

    created_at: SnapshotTimestamp = field(
        default_factory=lambda: datetime.now(
            timezone.utc,
        ),
    )

    updated_at: SnapshotTimestamp = field(
        default_factory=lambda: datetime.now(
            timezone.utc,
        ),
    )

    # ------------------------------------------------------
    # Runtime State
    # ------------------------------------------------------

    state: SnapshotState = SnapshotState.CREATED

    enabled: bool = DEFAULT_ENABLED

    frozen: bool = DEFAULT_FROZEN

    closed: bool = DEFAULT_CLOSED

    # ------------------------------------------------------
    # Statistics
    # ------------------------------------------------------

    statistics: SnapshotStatistics = field(
        default_factory=dict,
    )


# ==========================================================
# Part 7 — Constructor Helpers
# ==========================================================

    @classmethod
    def create(
        cls,
        *,
        id: SnapshotID,
        descriptor: MetricDescriptor | None = None,
        metadata: MetricMetadata | None = None,
        labels: MetricLabels | None = None,
        attributes: MetricAttributes | None = None,
        value: SnapshotValue = None,
    ) -> "MetricSnapshot":
        """
        Create a new runtime snapshot.
        """

        now = datetime.now(timezone.utc)

        return cls(
            id=id,
            descriptor=descriptor,
            metadata=(
                metadata.copy()
                if metadata is not None
                else MetricMetadata()
            ),
            labels=(
                labels.copy()
                if labels is not None
                else MetricLabels()
            ),
            attributes=(
                attributes.copy()
                if attributes is not None
                else MetricAttributes()
            ),
            value=deepcopy(value),
            created_at=now,
            updated_at=now,
        )

    @classmethod
    def from_metric(
        cls,
        metric: Any,
    ) -> "MetricSnapshot":
        """
        Build a snapshot from a Metric instance.
        """

        return cls(
            id=metric.id,
            revision=metric.revision,
            descriptor=metric.descriptor,
            metadata=metric.metadata.copy(),
            labels=metric.labels.copy(),
            attributes=metric.attributes.copy(),
            value=deepcopy(metric.value),
            created_at=metric.created_at,
            updated_at=datetime.now(timezone.utc),
            state=metric.state,
            enabled=metric.enabled,
            frozen=metric.frozen,
            closed=metric.closed,
        )

# ==========================================================
# Part 8 — Snapshot API
# ==========================================================

    def copy(self) -> "MetricSnapshot":
        """
        Return a shallow-safe copy.
        """
        return deepcopy(self)

    def clone(self) -> "MetricSnapshot":
        """
        Return a deep runtime clone.
        """
        return deepcopy(self)

    def freeze(self) -> "MetricSnapshot":
        """
        Freeze this snapshot.
        """
        self.frozen = True
        self.state = SnapshotState.FROZEN
        self.updated_at = datetime.now(timezone.utc)
        return self

    def thaw(self) -> "MetricSnapshot":
        """
        Restore a frozen snapshot.
        """
        self.frozen = False

        if self.state is SnapshotState.FROZEN:
            self.state = SnapshotState.ACTIVE

        self.updated_at = datetime.now(timezone.utc)
        return self

    def replace(
        self,
        *,
        value: SnapshotValue = _MISSING,
        metadata: MetricMetadata | None = None,
        labels: MetricLabels | None = None,
        attributes: MetricAttributes | None = None,
        statistics: SnapshotStatistics | None = None,
    ) -> "MetricSnapshot":
        """
        Replace snapshot content.
        """

        if value is not _MISSING:
            self.value = deepcopy(value)

        if metadata is not None:
            self.metadata = metadata.copy()

        if labels is not None:
            self.labels = labels.copy()

        if attributes is not None:
            self.attributes = attributes.copy()

        if statistics is not None:
            self.statistics = deepcopy(statistics)

        self.revision += 1
        self.updated_at = datetime.now(timezone.utc)

        return self

    def merge(
        self,
        other: "MetricSnapshot",
    ) -> "MetricSnapshot":
        """
        Merge another snapshot into this snapshot.
        """

        self.metadata.update(other.metadata)
        self.labels.update(other.labels)
        self.attributes.update(other.attributes)

        self.statistics.update(
            deepcopy(other.statistics)
        )

        self.value = deepcopy(other.value)

        self.revision = max(
            self.revision,
            other.revision,
        ) + 1

        self.updated_at = datetime.now(timezone.utc)

        return self

    def update(
        self,
        **kwargs: Any,
    ) -> "MetricSnapshot":
        """
        Generic runtime update.
        """

        for key, value in kwargs.items():

            if hasattr(self, key):
                setattr(
                    self,
                    key,
                    deepcopy(value),
                )

        self.revision += 1
        self.updated_at = datetime.now(timezone.utc)

        return self


# ==========================================================
# Part 9 — Serialization
# ==========================================================

    def to_dict(self) -> SnapshotDict:
        """
        Serialize snapshot into a dictionary.
        """

        return {
            "id": str(self.id),
            "revision": self.revision,
            "schema_version": self.schema_version,
            "runtime_version": self.runtime_version,
            "descriptor": (
                self.descriptor.to_dict()
                if self.descriptor is not None
                and hasattr(self.descriptor, "to_dict")
                else None
            ),
            "metadata": self.metadata.to_dict(),
            "labels": self.labels.to_dict(),
            "attributes": self.attributes.to_dict(),
            "value": deepcopy(self.value),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "state": self.state.name,
            "enabled": self.enabled,
            "frozen": self.frozen,
            "closed": self.closed,
            "statistics": deepcopy(self.statistics),
        }

    @classmethod
    def from_dict(
        cls,
        data: SnapshotMapping,
    ) -> "MetricSnapshot":
        """
        Construct a snapshot from a dictionary.
        """

        return cls(
            id=UUID(data["id"]),
            revision=data.get(
                "revision",
                DEFAULT_SNAPSHOT_REVISION,
            ),
            schema_version=data.get(
                "schema_version",
                DEFAULT_SCHEMA_VERSION,
            ),
            runtime_version=data.get(
                "runtime_version",
                DEFAULT_RUNTIME_VERSION,
            ),
            descriptor=None,
            metadata=MetricMetadata.from_dict(
                data.get("metadata", {}),
            ),
            labels=MetricLabels.from_dict(
                data.get("labels", {}),
            ),
            attributes=MetricAttributes.from_dict(
                data.get("attributes", {}),
            ),
            value=deepcopy(
                data.get("value"),
            ),
            created_at=datetime.fromisoformat(
                data["created_at"],
            ),
            updated_at=datetime.fromisoformat(
                data["updated_at"],
            ),
            state=SnapshotState[
                data.get(
                    "state",
                    SnapshotState.CREATED.name,
                )
            ],
            enabled=data.get(
                "enabled",
                DEFAULT_ENABLED,
            ),
            frozen=data.get(
                "frozen",
                DEFAULT_FROZEN,
            ),
            closed=data.get(
                "closed",
                DEFAULT_CLOSED,
            ),
            statistics=deepcopy(
                data.get("statistics", {}),
            ),
        )

    def to_json(
        self,
        *,
        indent: int | None = 2,
    ) -> str:
        """
        Serialize snapshot into JSON.
        """

        return json.dumps(
            self.to_dict(),
            indent=indent,
            ensure_ascii=False,
        )

    @classmethod
    def from_json(
        cls,
        payload: str,
    ) -> "MetricSnapshot":
        """
        Deserialize snapshot from JSON.
        """

        return cls.from_dict(
            json.loads(payload),
        )

# ==========================================================
# Part 10 — Validation
# ==========================================================

    def validate(self) -> None:
        """
        Validate snapshot consistency.

        Raises
        ------
        ValueError
            If any required field is invalid.
        """

        if self.id is None:
            raise ValueError("Snapshot id cannot be None.")

        if not isinstance(self.state, SnapshotState):
            raise ValueError("Invalid snapshot state.")

        if self.revision < 0:
            raise ValueError("Revision must be non-negative.")

        if self.created_at > self.updated_at:
            raise ValueError(
                "created_at cannot be later than updated_at."
            )

        if self.descriptor is not None:
            if hasattr(self.descriptor, "validate"):
                self.descriptor.validate()

        if hasattr(self.metadata, "validate"):
            self.metadata.validate()

        if hasattr(self.labels, "validate"):
            self.labels.validate()

        if hasattr(self.attributes, "validate"):
            self.attributes.validate()

    def is_valid(self) -> bool:
        """
        Return True if snapshot passes validation.
        """

        try:
            self.validate()
            return True
        except Exception:
            return False


# ==========================================================
# Part 11 — Comparison
# ==========================================================

    def equals(
        self,
        other: object,
    ) -> bool:
        """
        Strict equality comparison.
        """

        if not isinstance(other, MetricSnapshot):
            return False

        return self.to_dict() == other.to_dict()

    def compatible_with(
        self,
        other: "MetricSnapshot",
    ) -> bool:
        """
        Runtime compatibility check.

        Compatibility requires:

        - same descriptor
        - same schema version
        """

        if not isinstance(other, MetricSnapshot):
            return False

        return (
            self.schema_version == other.schema_version
            and self.descriptor == other.descriptor
        )

    def diff(
        self,
        other: "MetricSnapshot",
    ) -> dict[str, tuple[Any, Any]]:
        """
        Compute field-level differences.

        Returns
        -------
        dict
            {
                field_name: (self_value, other_value)
            }
        """

        if not isinstance(other, MetricSnapshot):
            raise TypeError(
                "other must be MetricSnapshot."
            )

        left = self.to_dict()
        right = other.to_dict()

        differences: dict[str, tuple[Any, Any]] = {}

        for key in sorted(set(left) | set(right)):
            if left.get(key) != right.get(key):
                differences[key] = (
                    left.get(key),
                    right.get(key),
                )

        return differences

# ==========================================================
# Part 12 — Statistics
# ==========================================================

    def age(self) -> float:
        """
        Return snapshot age in seconds.
        """

        return (
            datetime.now(timezone.utc) - self.created_at
        ).total_seconds()

    def size(self) -> int:
        """
        Approximate serialized size (bytes).
        """

        return len(
            self.to_json(
                indent=None,
            ).encode("utf-8")
        )

    def summary(self) -> dict[str, Any]:
        """
        Return compact runtime summary.
        """

        return {
            "id": str(self.id),
            "state": self.state.name,
            "revision": self.revision,
            "schema_version": self.schema_version,
            "runtime_version": self.runtime_version,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "age_seconds": self.age(),
            "enabled": self.enabled,
            "frozen": self.frozen,
            "closed": self.closed,
            "size_bytes": self.size(),
        }


# ==========================================================
# Part 13 — Python Protocols
# ==========================================================

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"id={self.id!s}, "
            f"state={self.state.name}, "
            f"revision={self.revision})"
        )

    def __str__(self) -> str:
        return (
            f"MetricSnapshot("
            f"{self.state.name}, "
            f"revision={self.revision})"
        )

    def __bool__(self) -> bool:
        return (
            self.enabled
            and not self.closed
        )

    def __copy__(self) -> "MetricSnapshot":
        return self.copy()

    def __deepcopy__(
        self,
        memo: dict[int, Any],
    ) -> "MetricSnapshot":
        return self.clone()

    def __eq__(
        self,
        other: object,
    ) -> bool:

        if not isinstance(
            other,
            MetricSnapshot,
        ):
            return NotImplemented

        return self.equals(other)

    def __hash__(self) -> int:
        return hash(
            (
                self.id,
                self.revision,
                self.created_at,
            )
        )


# ==========================================================
# Part 14 — Final cleanup
# ==========================================================

__all__ = [
    "SnapshotState",
    "MetricSnapshot",
]        
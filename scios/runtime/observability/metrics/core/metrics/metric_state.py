"""
SciOS Observability Metrics
===========================

Metric Runtime State
--------------------

Foundation definitions for runtime metric state.

This module contains:

- Version information
- Global constants
- Common type aliases

Higher-level runtime logic is implemented in the
subsequent parts of this file.
"""

from __future__ import annotations


# ==========================================================
# Part 2 — Imports
# ==========================================================

from __future__ import annotations

import time

from dataclasses import dataclass
from dataclasses import field

from datetime import datetime
from datetime import timezone

from enum import Enum
from enum import auto

from typing import Any
from typing import Final
from typing import TypeAlias

from uuid import UUID

# ==========================================================
# Part 3 — Public API
# ==========================================================

__all__ = [
    "METRIC_STATE_VERSION",
    "METRIC_STATE_API_VERSION",
    "DEFAULT_STATE_NAME",
    "DEFAULT_REVISION",
    "DEFAULT_ERROR_COUNT",
    "DEFAULT_WARNING_COUNT",
    "DEFAULT_UPDATE_COUNT",
    "DEFAULT_IS_ENABLED",
    "DEFAULT_IS_FROZEN",
    "DEFAULT_IS_CLOSED",
    "MetricID",
    "Revision",
    "Timestamp",
    "Counter",
]


# ==========================================================
# Part 4 — Version
# ==========================================================

METRIC_STATE_VERSION: Final[str] = "1.0.0"

METRIC_STATE_API_VERSION: Final[str] = "1.0"


# ==========================================================
# Part 4 — Constants
# ==========================================================

DEFAULT_STATE_NAME: Final[str] = "created"

DEFAULT_REVISION: Final[int] = 0

DEFAULT_ERROR_COUNT: Final[int] = 0

DEFAULT_WARNING_COUNT: Final[int] = 0

DEFAULT_UPDATE_COUNT: Final[int] = 0

DEFAULT_IS_ENABLED: Final[bool] = True

DEFAULT_IS_FROZEN: Final[bool] = False

DEFAULT_IS_CLOSED: Final[bool] = False


# ==========================================================
# Part 4 — Type Aliases
# ==========================================================

MetricID: TypeAlias = UUID

Revision: TypeAlias = int

Timestamp: TypeAlias = datetime



Counter: TypeAlias = int

# ==========================================================
# Part 5 — Runtime Enums
# ==========================================================

from dataclasses import dataclass
from dataclasses import field

from datetime import timezone

from enum import Enum
from enum import auto

from typing import Any


class MetricStatus(Enum):
    """
    Runtime lifecycle status.
    """

    CREATED = auto()
    ACTIVE = auto()
    IDLE = auto()
    PAUSED = auto()
    FROZEN = auto()
    DISABLED = auto()
    CLOSED = auto()
    DELETED = auto()


class MetricHealth(Enum):
    """
    Runtime health state.
    """

    UNKNOWN = auto()
    HEALTHY = auto()
    WARNING = auto()
    DEGRADED = auto()
    ERROR = auto()
    FAILED = auto()


class MetricMode(Enum):
    """
    Runtime operating mode.
    """

    READ_ONLY = auto()
    READ_WRITE = auto()
    MAINTENANCE = auto()
    RECOVERY = auto()


# ==========================================================
# Part 6 — MetricState
# ==========================================================

@dataclass(slots=True)
class MetricState:
    """
    Runtime state of a metric.

    This object stores only mutable runtime information.
    """

    # ------------------------------------------------------
    # Identity
    # ------------------------------------------------------

    metric_id: MetricID | None = None

    name: str = DEFAULT_STATE_NAME

    # ------------------------------------------------------
    # Runtime Value
    # ------------------------------------------------------

    value: Any = None

    previous_value: Any = None

    default_value: Any = None

    # ------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------

    status: MetricStatus = MetricStatus.CREATED

    health: MetricHealth = MetricHealth.UNKNOWN

    mode: MetricMode = MetricMode.READ_WRITE

    # ------------------------------------------------------
    # Runtime Flags
    # ------------------------------------------------------

    enabled: bool = DEFAULT_IS_ENABLED

    frozen: bool = DEFAULT_IS_FROZEN

    closed: bool = DEFAULT_IS_CLOSED

    # ------------------------------------------------------
    # Revision
    # ------------------------------------------------------

    revision: Revision = DEFAULT_REVISION

    # ------------------------------------------------------
    # Timestamps
    # ------------------------------------------------------

    created_at: Timestamp = field(default_factory=time.time)

    updated_at: Timestamp = field(default_factory=time.time)

    timestamp: Timestamp = field(default_factory=time.time)

    last_value_at: Timestamp | None = None

    # ------------------------------------------------------
    # Statistics
    # ------------------------------------------------------

    update_count: Counter = DEFAULT_UPDATE_COUNT

    warning_count: Counter = DEFAULT_WARNING_COUNT

    error_count: Counter = DEFAULT_ERROR_COUNT

    # ------------------------------------------------------
    # UUID
    # ------------------------------------------------------

    @property
    def uuid(self) -> MetricID | None:
        """
        Runtime UUID.

        Delegated to MetricState.
        """
        return self._state.metric_id


    @uuid.setter
    def uuid(self, value: MetricID | None) -> None:
        """
        Runtime UUID.

        Delegated to MetricState.
        """
        self._state.metric_id = value

# ==========================================================
# Part 7 — Constructor Helpers
# ==========================================================

    @classmethod
    def create(
        cls,
        *,
        metric_id: MetricID | None = None,
        name: str = DEFAULT_STATE_NAME,
    ) -> "MetricState":
        """
        Create a default runtime state.
        """

        return cls(
            metric_id=metric_id,
            name=name,
        )

    @classmethod
    def from_metric(
        cls,
        metric: Any,
    ) -> "MetricState":
        """
        Build runtime state from a Metric object.
        """

        return cls(
            metric_id=getattr(metric, "id", None),
            name=getattr(metric, "name", DEFAULT_STATE_NAME),
            status=MetricStatus.ACTIVE,
            enabled=getattr(metric, "enabled", True),
            frozen=getattr(metric, "frozen", False),
            closed=getattr(metric, "closed", False),
            revision=getattr(metric, "revision", DEFAULT_REVISION),
            created_at=getattr(
                metric,
                "created_at",
                datetime.now(timezone.utc),
            ),
        )

    @classmethod
    def from_snapshot(
        cls,
        snapshot: Any,
    ) -> "MetricState":
        """
        Build runtime state from MetricSnapshot.
        """

        return cls(
            metric_id=getattr(snapshot, "metric_id", None),
            name=getattr(snapshot, "name", DEFAULT_STATE_NAME),
            status=getattr(
                snapshot,
                "status",
                MetricStatus.CREATED,
            ),
            enabled=getattr(snapshot, "enabled", True),
            frozen=getattr(snapshot, "frozen", False),
            closed=getattr(snapshot, "closed", False),
            revision=getattr(
                snapshot,
                "revision",
                DEFAULT_REVISION,
            ),
            created_at=getattr(
                snapshot,
                "created_at",
                datetime.now(timezone.utc),
            ),
            updated_at=getattr(
                snapshot,
                "updated_at",
                datetime.now(timezone.utc),
            ),
        )

# ==========================================================
# Part 8 — Lifecycle API
# ==========================================================

    def activate(self) -> "MetricState":
        """Activate metric."""
        self.status = MetricStatus.ACTIVE
        self.enabled = True
        self.closed = False
        self.touch()
        return self

    def deactivate(self) -> "MetricState":
        """Deactivate metric."""
        self.status = MetricStatus.IDLE
        self.enabled = False
        self.touch()
        return self

    def freeze(self) -> "MetricState":
        """Freeze metric updates."""
        self.status = MetricStatus.FROZEN
        self.frozen = True
        self.touch()
        return self

    def unfreeze(self) -> "MetricState":
        """Resume metric updates."""
        self.frozen = False
        self.status = MetricStatus.ACTIVE
        self.touch()
        return self

    def close(self) -> "MetricState":
        """Close metric permanently."""
        self.closed = True
        self.enabled = False
        self.status = MetricStatus.CLOSED
        self.touch()
        return self

    def reopen(self) -> "MetricState":
        """Reopen closed metric."""
        self.closed = False
        self.enabled = True
        self.status = MetricStatus.ACTIVE
        self.touch()
        return self

    def reset(self) -> "MetricState":
        """Reset runtime state."""
        self.status = MetricStatus.CREATED
        self.health = MetricHealth.UNKNOWN
        self.mode = MetricMode.READ_WRITE

        self.enabled = DEFAULT_IS_ENABLED
        self.frozen = DEFAULT_IS_FROZEN
        self.closed = DEFAULT_IS_CLOSED

        self.revision = DEFAULT_REVISION

        self.update_count = DEFAULT_UPDATE_COUNT
        self.warning_count = DEFAULT_WARNING_COUNT
        self.error_count = DEFAULT_ERROR_COUNT

        now = datetime.now(timezone.utc)
        self.created_at = now
        self.updated_at = now
        self.last_value_at = None

        return self


# ==========================================================
# Part 9 — Runtime API
# ==========================================================

    def touch(self) -> "MetricState":
        """
        Update modification timestamp.
        """
        self.updated_at = datetime.now(timezone.utc)
        return self

    def increment_revision(
        self,
        step: int = 1,
    ) -> Revision:
        """
        Increase revision number.
        """
        self.revision += max(step, 1)
        self.touch()
        return self.revision

    def enable(self) -> "MetricState":
        """
        Enable runtime state.
        """
        self.enabled = True
        self.touch()
        return self

    def disable(self) -> "MetricState":
        """
        Disable runtime state.
        """
        self.enabled = False
        self.touch()
        return self

    def set_health(
        self,
        health: MetricHealth,
    ) -> "MetricState":
        """
        Update health state.
        """
        self.health = health
        self.touch()
        return self

    def update(
        self,
        *,
        status: MetricStatus | None = None,
        health: MetricHealth | None = None,
        mode: MetricMode | None = None,
        enabled: bool | None = None,
        frozen: bool | None = None,
        closed: bool | None = None,
    ) -> "MetricState":
        """
        Generic runtime update.
        """

        if status is not None:
            self.status = status

        if health is not None:
            self.health = health

        if mode is not None:
            self.mode = mode

        if enabled is not None:
            self.enabled = enabled

        if frozen is not None:
            self.frozen = frozen

        if closed is not None:
            self.closed = closed

        self.increment_revision()

        return self


# ==========================================================
# Part 10 — Serialization
# ==========================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Convert runtime state to dictionary.
        """
        return {
            "metric_id": (
                str(self.metric_id)
                if self.metric_id is not None
                else None
            ),
            "name": self.name,
            "status": self.status.name,
            "health": self.health.name,
            "mode": self.mode.name,
            "enabled": self.enabled,
            "frozen": self.frozen,
            "closed": self.closed,
            "revision": self.revision,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_value_at": (
                self.last_value_at.isoformat()
                if self.last_value_at is not None
                else None
            ),
            "update_count": self.update_count,
            "warning_count": self.warning_count,
            "error_count": self.error_count,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "MetricState":
        """
        Construct state from dictionary.
        """
        return cls(
            metric_id=UUID(data["metric_id"])
            if data.get("metric_id")
            else None,
            name=data.get("name", DEFAULT_STATE_NAME),
            status=MetricStatus[
                data.get("status", "CREATED")
            ],
            health=MetricHealth[
                data.get("health", "UNKNOWN")
            ],
            mode=MetricMode[
                data.get("mode", "READ_WRITE")
            ],
            enabled=data.get("enabled", True),
            frozen=data.get("frozen", False),
            closed=data.get("closed", False),
            revision=data.get(
                "revision",
                DEFAULT_REVISION,
            ),
            created_at=datetime.fromisoformat(
                data["created_at"]
            ),
            updated_at=datetime.fromisoformat(
                data["updated_at"]
            ),
            last_value_at=(
                datetime.fromisoformat(
                    data["last_value_at"]
                )
                if data.get("last_value_at")
                else None
            ),
            update_count=data.get(
                "update_count",
                DEFAULT_UPDATE_COUNT,
            ),
            warning_count=data.get(
                "warning_count",
                DEFAULT_WARNING_COUNT,
            ),
            error_count=data.get(
                "error_count",
                DEFAULT_ERROR_COUNT,
            ),
        )

    def to_json(self) -> str:
        """
        Serialize runtime state to JSON.
        """
        import json

        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            sort_keys=True,
        )

    @classmethod
    def from_json(
        cls,
        text: str,
    ) -> "MetricState":
        """
        Deserialize runtime state from JSON.
        """
        import json

        return cls.from_dict(
            json.loads(text)
        )

# ==========================================================
# Part 11 — Validation
# ==========================================================

    def validate(self) -> None:
        """
        Validate runtime state.

        Raises
        ------
        ValueError
            If the runtime state is inconsistent.
        """

        if self.revision < 0:
            raise ValueError("revision must be >= 0.")

        if self.update_count < 0:
            raise ValueError("update_count must be >= 0.")

        if self.warning_count < 0:
            raise ValueError("warning_count must be >= 0.")

        if self.error_count < 0:
            raise ValueError("error_count must be >= 0.")

        if self.closed and self.enabled:
            raise ValueError(
                "closed metric cannot be enabled."
            )

        if self.created_at > self.updated_at:
            raise ValueError(
                "created_at must not exceed updated_at."
            )

        if (
            self.last_value_at is not None
            and
            self.last_value_at < self.created_at
        ):
            raise ValueError(
                "last_value_at is invalid."
            )

    def is_valid(self) -> bool:
        """
        Return True if runtime state is valid.
        """

        try:
            self.validate()
            return True
        except Exception:
            return False


# ==========================================================
# Part 12 — Comparison
# ==========================================================

    def equals(
        self,
        other: object,
    ) -> bool:
        """
        Deep runtime equality.
        """

        if not isinstance(other, MetricState):
            return False

        return self.to_dict() == other.to_dict()

    def compatible_with(
        self,
        other: object,
    ) -> bool:
        """
        Runtime compatibility check.
        """

        if not isinstance(other, MetricState):
            return False

        return (
            self.metric_id == other.metric_id
            and
            self.name == other.name
        )

    def diff(
        self,
        other: "MetricState",
    ) -> dict[str, tuple[Any, Any]]:
        """
        Compute runtime differences.
        """

        differences: dict[str, tuple[Any, Any]] = {}

        left = self.to_dict()
        right = other.to_dict()

        for key in sorted(set(left) | set(right)):
            if left.get(key) != right.get(key):
                differences[key] = (
                    left.get(key),
                    right.get(key),
                )

        return differences


# ==========================================================
# Part 13 — Statistics
# ==========================================================

    def age(self) -> float:
        """
        Seconds since creation.
        """

        return (
            datetime.now(timezone.utc)
            - self.created_at
        ).total_seconds()

    def uptime(self) -> float:
        """
        Seconds since last runtime update.
        """

        return (
            datetime.now(timezone.utc)
            - self.updated_at
        ).total_seconds()

    def summary(self) -> dict[str, Any]:
        """
        Compact runtime summary.
        """

        return {
            "metric_id": (
                str(self.metric_id)
                if self.metric_id is not None
                else None
            ),
            "name": self.name,
            "status": self.status.name,
            "health": self.health.name,
            "mode": self.mode.name,
            "enabled": self.enabled,
            "frozen": self.frozen,
            "closed": self.closed,
            "revision": self.revision,
            "updates": self.update_count,
            "warnings": self.warning_count,
            "errors": self.error_count,
            "age_seconds": round(self.age(), 6),
            "uptime_seconds": round(self.uptime(), 6),
        }

# ==========================================================
# Part 14 — Python Protocols
# ==========================================================

    def __repr__(self) -> str:
        """
        Developer representation.
        """
        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"status={self.status.name}, "
            f"health={self.health.name}, "
            f"revision={self.revision})"
        )

    def __str__(self) -> str:
        """
        Human-readable representation.
        """
        return (
            f"{self.name}"
            f"[{self.status.name}]"
        )

    def __bool__(self) -> bool:
        """
        Runtime truth value.

        A state evaluates True only when
        it is enabled and not closed.
        """
        return (
            self.enabled
            and
            not self.closed
        )

    def __copy__(self) -> "MetricState":
        """
        Shallow copy.
        """
        return self.from_dict(
            self.to_dict()
        )

    def __deepcopy__(
        self,
        memo: dict[int, Any],
    ) -> "MetricState":
        """
        Deep copy.
        """
        import copy

        state = self.from_dict(
            copy.deepcopy(
                self.to_dict(),
                memo,
            )
        )

        memo[id(self)] = state

        return state

    def __eq__(
        self,
        other: object,
    ) -> bool:
        """
        Equality comparison.
        """
        if not isinstance(
            other,
            MetricState,
        ):
            return NotImplemented

        return self.equals(other)

    def __hash__(self) -> int:
        """
        Stable hash.

        MetricState is logically identified by
        metric id + revision.
        """
        return hash(
            (
                self.metric_id,
                self.revision,
            )
        )


# ==========================================================
# Part 15 — Final Cleanup
# ==========================================================

__all__.extend(
    [
        "MetricStatus",
        "MetricHealth",
        "MetricMode",
        "MetricState",
    ]
)                
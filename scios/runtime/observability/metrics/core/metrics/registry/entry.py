"""
Metric Registry Entry
=====================

Registry entry binding a MetricKey to a metric instance.
"""

from __future__ import annotations

import time

from dataclasses import dataclass
from dataclasses import field

from typing import Any
from typing import TypeAlias

from .key import MetricKey

__all__ = [
    "DEFAULT_VALUE",
    "DEFAULT_STATE",
    "MetricValue",
    "MetricSnapshot",
    "MetricEntry",
]

# ==============================================================================
# Part 1. Imports & Constants
# ==============================================================================

DEFAULT_VALUE: Any = None

DEFAULT_STATE: dict[str, Any] = {}

MetricValue: TypeAlias = Any

MetricSnapshot: TypeAlias = dict[str, Any]


# ==============================================================================
# Part 2. MetricEntry
# ==============================================================================


@dataclass(slots=True)
class MetricEntry:
    """
    Registry entry binding a MetricKey to a metric instance.
    """

    key: MetricKey = field(default_factory=MetricKey)

    metric: MetricValue = None

    value: MetricValue = DEFAULT_VALUE

    timestamp: float = field(default_factory=time.time)

    state: MetricSnapshot = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------

    def __post_init__(self) -> None:

        self._normalize()

        self._refresh_state()

        self._validate()

    # ------------------------------------------------------------------
    # Normalization
    # ------------------------------------------------------------------

    def _normalize(self) -> None:

        self.key.normalize()

        if isinstance(self.metric, str):
            self.metric = self.metric.strip().lower()

        try:
            self.timestamp = float(self.timestamp)
        except (TypeError, ValueError):
            pass

        if not isinstance(self.state, dict):
            self.state = {}

    # ------------------------------------------------------------------
    # State Synchronization
    # ------------------------------------------------------------------

    def _refresh_state(self) -> None:
        """
        Synchronize runtime state with current entry.
        """

        self.state.clear()

        self.state.update(
            {
                "key": self.key,
                "metric": self.metric,
                "value": self.value,
                "timestamp": self.timestamp,
            }
        )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate(self) -> None:

        if not isinstance(self.key, MetricKey):
            raise TypeError("key must be a MetricKey.")

        if self.metric is not None and not isinstance(self.metric, str):
            raise TypeError("metric must be a string or None.")

        if not isinstance(self.timestamp, (int, float)):
            raise TypeError("timestamp must be numeric.")

        if not isinstance(self.state, dict):
            raise TypeError("state must be a mapping.")


# ==============================================================================
# Part 3. Properties
# ==============================================================================

    @property
    def has_metric(self) -> bool:
        """
        Whether a metric object is attached.
        """
        return self.metric is not None

    @property
    def has_value(self) -> bool:
        """
        Whether a value is available.
        """
        return self.value is not None

    @property
    def is_active(self) -> bool:
        """
        Whether the entry is active.
        """
        return self.state.get("status", "active") == "active"

    @property
    def fullname(self) -> str:
        """
        Fully-qualified metric name.
        """
        return self.key.fullname

    @property
    def age(self) -> float:
        """
        Age in seconds.
        """
        return max(0.0, time.time() - self.timestamp)


# ==============================================================================
# Part 4. Operations
# ==============================================================================

    def update(
        self,
        *,
        metric: Any = ...,
        value: MetricValue = ...,
        state: MetricSnapshot | None = None,
    ) -> "MetricEntry":
        """
        Update entry in-place.
        """

        if metric is not ...:
            self.metric = metric

        if value is not ...:
            self.value = value

        if state is not None:
            self.state = dict(state)

        self.touch()
        self.normalize()
        self._refresh_state()
        self.validate()

        return self

    def replace(
        self,
        other: "MetricEntry",
    ) -> "MetricEntry":
        """
        Replace contents from another entry.
        """

        self.key = other.key.clone()
        self.metric = other.metric
        self.value = other.value
        self.timestamp = other.timestamp
        self.state = dict(other.state)

        self.normalize()
        self._refresh_state()
        self.validate()

        return self

    def reset(self) -> "MetricEntry":
        """
        Reset entry to defaults.
        """

        self.metric = None
        self.value = DEFAULT_VALUE
        self.touch()

        self.state.clear()

        self._refresh_state()

        self.validate()

        return self

    def touch(self) -> "MetricEntry":
        """
        Refresh timestamp.
        """

        self.timestamp = time.time()

        self._refresh_state()

        return self

# ==============================================================================
# Part 5. Serialization
# ==============================================================================

    def to_dict(self) -> MetricSnapshot:
        """
        Serialize to dictionary.
        """

        return {
            "key": self.key.to_dict(),
            "metric": self.metric,
            "value": self.value,
            "timestamp": self.timestamp,
            "state": dict(self.state),
        }

    @classmethod
    def from_dict(
        cls,
        data: MetricSnapshot,
    ) -> "MetricEntry":
        """
        Deserialize from dictionary.
        """

        return cls(
            key=MetricKey.from_dict(data.get("key", {})),
            metric=data.get("metric"),
            value=data.get("value"),
            timestamp=float(data.get("timestamp", time.time())),
            state=dict(data.get("state", {})),
        )

    def to_tuple(self) -> tuple:
        """
        Serialize to tuple.
        """

        return (
            self.key.to_tuple(),
            self.metric,
            self.value,
            self.timestamp,
            dict(self.state),
        )

    @classmethod
    def from_tuple(
        cls,
        value: tuple,
    ) -> "MetricEntry":
        """
        Deserialize from tuple.
        """

        key, metric, metric_value, timestamp, state = value

        return cls(
            key=MetricKey.from_tuple(key),
            metric=metric,
            value=metric_value,
            timestamp=float(timestamp),
            state=dict(state),
        )

    def snapshot(self) -> MetricSnapshot:
        """
        Snapshot entry.
        """

        return self.to_dict()

    def restore(
        self,
        snapshot: MetricSnapshot,
    ) -> "MetricEntry":
        """
        Restore in-place.
        """

        restored = self.from_dict(snapshot)

        self.replace(restored)

        return self

# ==============================================================================
# Part 6. Validation
# ==============================================================================

    @staticmethod
    def validate_key(key: Any) -> bool:
        """
        Validate registry key.
        """
        return isinstance(key, MetricKey)

    @staticmethod
    def validate_metric(metric: Any) -> bool:
        """
        Validate metric type.
        """
        return metric is None or isinstance(metric, str)

    @staticmethod
    def validate_value(value: Any) -> bool:
        """
        Validate metric value.
        """
        return True

    @classmethod
    def validate_entry(cls, entry: Any) -> bool:
        """
        Validate MetricEntry instance.
        """
        return (
            isinstance(entry, cls)
            and cls.validate_key(entry.key)
            and cls.validate_metric(entry.metric)
            and cls.validate_value(entry.value)
        )

    def validate(self) -> bool:
        """
        Validate current instance.
        """
        self._validate()
        return True


# ==============================================================================
# Part 7. Utilities
# ==============================================================================

    def clone(self) -> "MetricEntry":
        """
        Deep clone.
        """
        return MetricEntry(
            key=self.key.clone(),
            metric=self.metric,
            value=self.value,
            timestamp=float(self.timestamp),
            state=dict(self.state),
        )

    copy = clone

    def merge(
        self,
        *,
        key: MetricKey | None = None,
        metric: Any = ...,
        value: Any = ...,
        timestamp: float | None = None,
        state: MetricSnapshot | None = None,
    ) -> "MetricEntry":
        """
        Return merged copy.
        """
        merged_state = dict(self.state)

        if state is not None:
            merged_state.update(state)

        return MetricEntry(
            key=key.clone() if key is not None else self.key.clone(),
            metric=self.metric if metric is ... else metric,
            value=self.value if value is ... else value,
            timestamp=self.timestamp if timestamp is None else float(timestamp),
            state=merged_state,
        )

    def clear(self) -> "MetricEntry":
        """
        Reset to defaults.
        """
        self.key = MetricKey()
        self.metric = None
        self.value = DEFAULT_VALUE
        self.state.clear()
        self.touch()
        return self

    def normalize(self) -> "MetricEntry":
        """
        Normalize entry.
        """
        self._normalize()
        return self


# ==============================================================================
# Part 8. Protocols
# ==============================================================================

    def ordering(self) -> tuple:
        """
        Ordering key.
        """
        return (
            self.key.ordering(),
            self.timestamp,
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.key,
                self.metric,
                self.value,
            )
        )

    def __eq__(self, other: object) -> bool:

        if not isinstance(other, MetricEntry):
            return NotImplemented

        return (
            self.key == other.key
            and self.metric == other.metric
            and self.value == other.value
            and self.state == other.state
        )

    def __lt__(self, other: object) -> bool:

        if not isinstance(other, MetricEntry):
            return NotImplemented

        return self.ordering() < other.ordering()

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"key={self.key!r}, "
            f"metric={self.metric!r}, "
            f"value={self.value!r}, "
            f"state={self.state!r})"
        )

    def __str__(self) -> str:

        return self.key.fullname

    def __bool__(self) -> bool:

        return bool(self.key)


# ==============================================================================
# Part 9. Diagnostics
# ==============================================================================

    def summary(self) -> MetricSnapshot:
        """
        Summary information.
        """
        return {
            "fullname": self.key.fullname,
            "metric": self.metric,
            "value": self.value,
            "timestamp": self.timestamp,
            "state": dict(self.state),
        }

    def diagnostics(self) -> MetricSnapshot:
        """
        Diagnostic information.
        """
        return {
            "valid": self.validate(),
            "age": self.age,
            **self.summary(),
        }

    def entry_report(self) -> MetricSnapshot:
        """
        Complete report.
        """
        return {
            "summary": self.summary(),
            "diagnostics": self.diagnostics(),
        }

    def overall_status(self) -> bool:
        """
        Overall health.
        """
        return self.validate()


# ==============================================================================
# Part 10. Public API
# ==============================================================================

__all__ = [
    "DEFAULT_VALUE",
    "DEFAULT_STATE",
    "MetricValue",
    "MetricSnapshot",
    "MetricEntry",
]        
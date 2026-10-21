from __future__ import annotations

# ==========================================================
# Part 1. Imports & Constants
# ==========================================================

from collections.abc import Mapping
from datetime import UTC, datetime
from enum import Enum
from threading import RLock
from typing import Any, TypeAlias

__all__ = [
    "DEFAULT_LOW",
    "DEFAULT_HIGH",
    "DEFAULT_NAME",
    "DEFAULT_UNIT",
    "DEFAULT_VERSION",
    "DEFAULT_METADATA",
    "DEFAULT_ENABLED",
    "ThresholdMode",
    "ThresholdCompareResult",
    "ThresholdValue",
    "NumericValue",
    "MetadataType",
    "MetricThreshold",
]


DEFAULT_LOW: float = 0.0
DEFAULT_HIGH: float = 100.0

DEFAULT_NAME: str = ""
DEFAULT_UNIT: str = ""

DEFAULT_VERSION: str = "1.0.0"

DEFAULT_METADATA: dict[str, Any] = {}

DEFAULT_ENABLED: bool = True


# ==========================================================
# Part 2. Enums & Type Aliases
# ==========================================================


NumericValue: TypeAlias = int | float

ThresholdValue: TypeAlias = NumericValue | str

MetadataType: TypeAlias = dict[str, Any]


class ThresholdMode(str, Enum):
    RANGE = "range"
    ABOVE = "above"
    BELOW = "below"


class ThresholdCompareResult(str, Enum):
    BELOW = "below"
    WITHIN = "within"
    ABOVE = "above"


# ==========================================================
# Part 3. Constructor
# ==========================================================


class MetricThreshold:
    """
    Threshold definition for metric monitoring.
    """

    __slots__ = (
        "_low",
        "_high",
        "_name",
        "_unit",
        "_timestamp",
        "_version",
        "_metadata",
        "_enabled",
        "_lock",
    )

    _low: float
    _high: float

    _name: str
    _unit: str

    _timestamp: datetime
    _version: str

    _metadata: MetadataType

    _enabled: bool

    _lock: RLock

    def __init__(
        self,
        *,
        low: NumericValue = DEFAULT_LOW,
        high: NumericValue = DEFAULT_HIGH,
        name: str = DEFAULT_NAME,
        unit: str = DEFAULT_UNIT,
        timestamp: datetime | None = None,
        version: str = DEFAULT_VERSION,
        metadata: Mapping[str, Any] | None = None,
        enabled: bool = DEFAULT_ENABLED,
    ) -> None:

        self._low = float(low)
        self._high = float(high)

        self._name = str(name)
        self._unit = str(unit)

        self._timestamp = timestamp or datetime.now(UTC)
        self._version = str(version)

        self._metadata = dict(metadata or {})

        self._enabled = bool(enabled)

        self._lock = RLock()


# ==========================================================
# Part 4. Properties
# ==========================================================

    @property
    def low(self) -> float:
        return self._low

    @property
    def high(self) -> float:
        return self._high

    @property
    def name(self) -> str:
        return self._name

    @property
    def unit(self) -> str:
        return self._unit

    @property
    def timestamp(self) -> datetime:
        return self._timestamp

    @property
    def version(self) -> str:
        return self._version

    @property
    def metadata(self) -> MetadataType:
        return self._metadata

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def lock(self) -> RLock:
        return self._lock

# ==========================================================
# Part 5. Threshold API
# ==========================================================

    def set(
        self,
        *,
        low: NumericValue,
        high: NumericValue,
    ) -> None:

        with self._lock:
            self._low = float(low)
            self._high = float(high)
            self._timestamp = datetime.now(UTC)

    def clear(self) -> None:

        with self._lock:
            self._low = DEFAULT_LOW
            self._high = DEFAULT_HIGH
            self._timestamp = datetime.now(UTC)

    def reset(self) -> None:

        with self._lock:
            self._low = DEFAULT_LOW
            self._high = DEFAULT_HIGH
            self._name = DEFAULT_NAME
            self._unit = DEFAULT_UNIT
            self._version = DEFAULT_VERSION
            self._metadata.clear()
            self._enabled = DEFAULT_ENABLED
            self._timestamp = datetime.now(UTC)

    def update(
        self,
        *,
        low: NumericValue | None = None,
        high: NumericValue | None = None,
    ) -> None:

        with self._lock:

            if low is not None:
                self._low = float(low)

            if high is not None:
                self._high = float(high)

            self._timestamp = datetime.now(UTC)

    def enable(self) -> None:

        with self._lock:
            self._enabled = True
            self._timestamp = datetime.now(UTC)

    def disable(self) -> None:

        with self._lock:
            self._enabled = False
            self._timestamp = datetime.now(UTC)

    def toggle(self) -> None:

        with self._lock:
            self._enabled = not self._enabled
            self._timestamp = datetime.now(UTC)


# ==========================================================
# Part 6. Comparison API
# ==========================================================

    def exceeded(
        self,
        value: NumericValue,
    ) -> bool:

        return float(value) > self._high

    def below(
        self,
        value: NumericValue,
    ) -> bool:

        return float(value) < self._low

    def within(
        self,
        value: NumericValue,
    ) -> bool:

        value = float(value)

        return self._low <= value <= self._high

    def compare(
        self,
        value: NumericValue,
    ) -> ThresholdCompareResult:

        if self.below(value):
            return ThresholdCompareResult.BELOW

        if self.exceeded(value):
            return ThresholdCompareResult.ABOVE

        return ThresholdCompareResult.WITHIN

    def evaluate(
        self,
        value: NumericValue,
    ) -> ThresholdCompareResult:

        return self.compare(value)


# ==========================================================
# Part 7. Metadata API
# ==========================================================

    def set_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:

        with self._lock:
            self._metadata[str(key)] = value

    def update_metadata(
        self,
        values: Mapping[str, Any],
    ) -> None:

        with self._lock:
            self._metadata.update(values)

    def clear_metadata(self) -> None:

        with self._lock:
            self._metadata.clear()


# ==========================================================
# Part 8. Serialization
# ==========================================================

    def to_dict(self) -> dict[str, Any]:

        return {
            "low": self._low,
            "high": self._high,
            "name": self._name,
            "unit": self._unit,
            "timestamp": self._timestamp.isoformat(),
            "version": self._version,
            "metadata": dict(self._metadata),
            "enabled": self._enabled,
        }

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "MetricThreshold":

        timestamp = data.get("timestamp")

        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)

        return cls(
            low=float(data.get("low", DEFAULT_LOW)),
            high=float(data.get("high", DEFAULT_HIGH)),
            name=str(data.get("name", DEFAULT_NAME)),
            unit=str(data.get("unit", DEFAULT_UNIT)),
            timestamp=timestamp,
            version=str(data.get("version", DEFAULT_VERSION)),
            metadata=dict(data.get("metadata", {})),
            enabled=bool(data.get("enabled", DEFAULT_ENABLED)),
        )

    def to_json(self) -> str:

        import json

        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            separators=(",", ":"),
        )

    @classmethod
    def from_json(
        cls,
        text: str,
    ) -> "MetricThreshold":

        import json

        return cls.from_dict(json.loads(text))

# ==========================================================
# Part 9. Validation
# ==========================================================

    def validate(self) -> bool:

        if not isinstance(self._low, (int, float)):
            return False

        if not isinstance(self._high, (int, float)):
            return False

        if self._low > self._high:
            return False

        if not isinstance(self._name, str):
            return False

        if not isinstance(self._unit, str):
            return False

        if not isinstance(self._metadata, dict):
            return False

        if not isinstance(self._enabled, bool):
            return False

        return True

    def is_valid(self) -> bool:

        return self.validate()


# ==========================================================
# Part 10. Snapshot API
# ==========================================================

    def copy(self) -> "MetricThreshold":

        return type(self).from_dict(self.to_dict())

    def deepcopy(self) -> "MetricThreshold":

        return self.copy()

    def clone(self) -> "MetricThreshold":

        return self.copy()


# ==========================================================
# Part 11. Python Protocols
# ==========================================================

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}"
            f"(low={self._low!r}, "
            f"high={self._high!r}, "
            f"enabled={self._enabled!r})"
        )

    def __str__(self) -> str:

        return f"[{self._low}, {self._high}]"

    def __bool__(self) -> bool:

        return self._enabled

    def __len__(self) -> int:

        return len(self._metadata)

    def __eq__(
        self,
        other: object,
    ) -> bool:

        if not isinstance(other, MetricThreshold):
            return False

        return self.to_dict() == other.to_dict()

    def __hash__(self) -> int:

        return hash(
            (
                self._low,
                self._high,
                self._name,
                self._unit,
                self._version,
                self._enabled,
            )
        )

    def __getstate__(self) -> dict[str, Any]:

        return self.to_dict()

    def __setstate__(
        self,
        state: dict[str, Any],
    ) -> None:

        obj = type(self).from_dict(state)

        self._low = obj._low
        self._high = obj._high

        self._name = obj._name
        self._unit = obj._unit

        self._timestamp = obj._timestamp
        self._version = obj._version

        self._metadata = dict(obj._metadata)

        self._enabled = obj._enabled

        self._lock = RLock()


# ==========================================================
# Part 12. Diagnostics
# ==========================================================

    def summary(self) -> str:

        return (
            f"MetricThreshold("
            f"low={self._low}, "
            f"high={self._high}, "
            f"enabled={self._enabled})"
        )

    def diagnostics(self) -> dict[str, Any]:

        return {
            "valid": self.validate(),
            "enabled": self._enabled,
            "low": self._low,
            "high": self._high,
            "metadata_size": len(self._metadata),
            "timestamp": self._timestamp.isoformat(),
        }

    def threshold_report(self) -> dict[str, Any]:

        return {
            "threshold": self.to_dict(),
            "diagnostics": self.diagnostics(),
        }

    def overall_status(self) -> str:

        if not self.validate():
            return "invalid"

        return "enabled" if self._enabled else "disabled"


# ==========================================================
# Part 13. Public API
# ==========================================================

__all__ = [
    "DEFAULT_LOW",
    "DEFAULT_HIGH",
    "DEFAULT_NAME",
    "DEFAULT_UNIT",
    "DEFAULT_VERSION",
    "DEFAULT_METADATA",
    "DEFAULT_ENABLED",
    "ThresholdMode",
    "ThresholdCompareResult",
    "ThresholdValue",
    "NumericValue",
    "MetadataType",
    "MetricThreshold",
]                
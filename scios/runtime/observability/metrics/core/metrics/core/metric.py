# ==========================================================
# Part 1. Imports
# ==========================================================

from __future__ import annotations

import copy as _copy
import json
import time
from dataclasses import dataclass, field, replace as _replace
from typing import Any


# ==========================================================
# Part 2. Constants & Type Aliases
# ==========================================================

DEFAULT_NAME: str = ""
DEFAULT_VALUE: float = 0.0
DEFAULT_UNIT: str = ""
DEFAULT_VERSION: str = "1.0"

LabelMap: type = dict[str, str]


# ==========================================================
# Part 3. Dataclass / Core Container
# ==========================================================

@dataclass(slots=True)
class Metric:
    """
    Represents a single metric sample.
    """

    name: str = DEFAULT_NAME

    value: Any = DEFAULT_VALUE

    unit: str = DEFAULT_UNIT

    labels: LabelMap = field(
        default_factory=dict,
    )

    timestamp: float = field(
        default_factory=time.time,
    )

    version: str = DEFAULT_VERSION

# ==========================================================
# Part 4. Validation
# ==========================================================

    def __post_init__(self) -> None:
        if isinstance(self.labels, dict):
            self.labels = dict(self.labels)

    def validate(self) -> None:
        """
        Validate metric fields.
        """

        if not isinstance(self.name, str):
            raise TypeError("name must be str")

        if self.name == "":
            raise ValueError("name cannot be empty")

        if not isinstance(self.value, (int, float)):
            raise TypeError("value must be numeric")

        if not isinstance(self.unit, str):
            raise TypeError("unit must be str")

        if not isinstance(self.labels, dict):
            raise TypeError("labels must be dict")

        if not isinstance(self.timestamp, (int, float)):
            raise TypeError("timestamp must be numeric")

        if not isinstance(self.version, str):
            raise TypeError("version must be str")

        for k, v in self.labels.items():
            if not isinstance(k, str):
                raise TypeError("label keys must be str")
            if not isinstance(v, str):
                raise TypeError("label values must be str")

    def is_valid(self) -> bool:
        """
        Return True if metric is valid.
        """

        try:
            self.validate()
            return True
        except Exception:
            return False


# ==========================================================
# Part 5. Mutation API
# ==========================================================

    def set_value(
        self,
        value: int | float,
    ) -> None:
        """
        Update metric value.
        """

        self.value = value

    def update_labels(
        self,
        labels: LabelMap,
    ) -> None:
        """
        Merge labels.
        """

        self.labels.update(labels)

    def clear_labels(self) -> None:
        """
        Remove all labels.
        """

        self.labels.clear()

    def touch(self) -> None:
        """
        Refresh timestamp.
        """

        self.timestamp = time.time()


# ==========================================================
# Part 6. Serialization
# ==========================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize metric.
        """

        return {
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "labels": _copy.deepcopy(self.labels),
            "timestamp": self.timestamp,
            "version": self.version,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "Metric":
        """
        Construct metric from dict.
        """

        return cls(
            name=data.get("name", DEFAULT_NAME),
            value=data.get("value", DEFAULT_VALUE),
            unit=data.get("unit", DEFAULT_UNIT),
            labels=_copy.deepcopy(data.get("labels", {})),
            timestamp=float(data.get("timestamp", time.time())),
            version=data.get("version", DEFAULT_VERSION),
        )

    def to_json(self) -> str:
        """
        Serialize metric to JSON.
        """

        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            sort_keys=True,
        )

    @classmethod
    def from_json(
        cls,
        payload: str,
    ) -> "Metric":
        """
        Construct metric from JSON.
        """

        return cls.from_dict(
            json.loads(payload),
        )

# ==========================================================
# Part 7. Copy API
# ==========================================================

    def copy(self) -> "Metric":
        """
        Shallow copy.
        """

        return Metric(
            name=self.name,
            value=self.value,
            unit=self.unit,
            labels=dict(self.labels),
            timestamp=self.timestamp,
            version=self.version,
        )

    def clone(self) -> "Metric":
        """
        Alias of copy().
        """

        return self.copy()

    def deepcopy(self) -> "Metric":
        """
        Deep copy.
        """

        return Metric(
            name=self.name,
            value=_copy.deepcopy(self.value),
            unit=self.unit,
            labels=_copy.deepcopy(self.labels),
            timestamp=self.timestamp,
            version=self.version,
        )

    def replace(
        self,
        **changes: Any,
    ) -> "Metric":
        """
        Dataclass replace.
        """

        return _replace(self, **changes)


# ==========================================================
# Part 8. Comparison
# ==========================================================

    def __eq__(
        self,
        other: object,
    ) -> bool:
        if not isinstance(other, Metric):
            return False

        return (
            self.name == other.name
            and self.value == other.value
            and self.unit == other.unit
            and self.labels == other.labels
            and self.timestamp == other.timestamp
            and self.version == other.version
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.name,
                self.value,
                self.unit,
                frozenset(self.labels.items()),
                self.timestamp,
                self.version,
            )
        )


# ==========================================================
# Part 9. Python Protocols
# ==========================================================

    def items(self):
        return self.labels.items()

    def keys(self):
        return self.labels.keys()

    def values(self):
        return self.labels.values()

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        return self.labels.get(key, default)

    def __repr__(self) -> str:
        return (
            f"Metric("
            f"name={self.name!r}, "
            f"value={self.value!r}, "
            f"unit={self.unit!r})"
        )

    def __str__(self) -> str:
        return f"{self.name}={self.value} {self.unit}".strip()

    def __bool__(self) -> bool:
        return bool(self.name)

    def __len__(self) -> int:
        return len(self.labels)

    def __iter__(self):
        return iter(self.labels)

    def __contains__(
        self,
        key: object,
    ) -> bool:
        return key in self.labels

    def __getitem__(
        self,
        key: str,
    ) -> str:
        return self.labels[key]

    def __setitem__(
        self,
        key: str,
        value: str,
    ) -> None:
        self.labels[key] = value

    def __delitem__(
        self,
        key: str,
    ) -> None:
        del self.labels[key]

# ==========================================================
# Part 10. Pickle Support
# ==========================================================

    def __getstate__(self) -> dict[str, Any]:
        """
        Return pickle state.
        """

        return {
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "labels": self.labels,
            "timestamp": self.timestamp,
            "version": self.version,
        }

    def __setstate__(
        self,
        state: dict[str, Any],
    ) -> None:
        """
        Restore pickle state.
        """

        object.__setattr__(self, "name", state["name"])
        object.__setattr__(self, "value", state["value"])
        object.__setattr__(self, "unit", state["unit"])
        object.__setattr__(self, "labels", dict(state["labels"]))
        object.__setattr__(self, "timestamp", state["timestamp"])
        object.__setattr__(self, "version", state["version"])


# ==========================================================
# Part 11. Public API
# ==========================================================

__all__ = [
    "DEFAULT_NAME",
    "DEFAULT_VALUE",
    "DEFAULT_UNIT",
    "DEFAULT_VERSION",
    "LabelMap",
    "Metric",
]                    
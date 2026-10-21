# ==========================================================
# Part 1. Imports
# ==========================================================

from __future__ import annotations

import copy as _copy
import json
import time

from dataclasses import dataclass, field
from typing import Any, TypeAlias


# ==========================================================
# Part 2. Constants & Type Aliases
# ==========================================================

MetricValue: TypeAlias = Any
MetricMap: TypeAlias = dict[str, MetricValue]
MetadataMap: TypeAlias = dict[str, Any]

DEFAULT_VERSION: str = "1.0"


# ==========================================================
# Part 3. Dataclass / Core Container
# ==========================================================

@dataclass(slots=True)
class MetricSnapshot:
    """
    Immutable-like snapshot of a metrics collection.
    """

    timestamp: float = field(
        default_factory=time.time
    )

    metrics: MetricMap = field(
        default_factory=dict
    )

    metadata: MetadataMap = field(
        default_factory=dict
    )

    version: str = DEFAULT_VERSION
# ==========================================================
# Part 4. Validation
# ==========================================================

    def __post_init__(self) -> None:
        """
        Dataclass initialization hook.

        Construction never raises validation errors.
        Validation is performed explicitly by validate().
        """
        pass

    def validate(self) -> None:
        """
        Validate snapshot fields.
        """

        if not isinstance(self.timestamp, (int, float)):
            raise TypeError("timestamp must be numeric")

        if not isinstance(self.metrics, dict):
            raise TypeError("metrics must be a dict")

        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dict")

        if not isinstance(self.version, str):
            raise TypeError("version must be a str")

        for key in self.metrics:
            if not isinstance(key, str):
                raise TypeError("metric keys must be str")

        for key in self.metadata:
            if not isinstance(key, str):
                raise TypeError("metadata keys must be str")

    def is_valid(self) -> bool:
        """
        Return True if snapshot is valid.
        """

        try:
            self.validate()
            return True
        except Exception:
            return False


# ==========================================================
# Part 5. Serialization
# ==========================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize snapshot to dict.
        """

        return {
            "timestamp": self.timestamp,
            "metrics": _copy.deepcopy(self.metrics),
            "metadata": _copy.deepcopy(self.metadata),
            "version": self.version,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "MetricSnapshot":
        """
        Construct snapshot from dict.
        """

        return cls(
            timestamp=float(data["timestamp"]),
            metrics=_copy.deepcopy(data.get("metrics", {})),
            metadata=_copy.deepcopy(data.get("metadata", {})),
            version=data.get("version", DEFAULT_VERSION),
        )

    def to_json(self) -> str:
        """
        Serialize snapshot to JSON.
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
    ) -> "MetricSnapshot":
        """
        Construct snapshot from JSON.
        """

        return cls.from_dict(json.loads(payload))


# ==========================================================
# Part 6. Copy API
# ==========================================================

    def copy(self) -> "MetricSnapshot":
        """
        Shallow copy.
        """

        return _copy.copy(self)

    def clone(self) -> "MetricSnapshot":
        """
        Deep clone.
        """

        return _copy.deepcopy(self)

    def deepcopy(self) -> "MetricSnapshot":
        """
        Explicit deep copy.
        """

        return _copy.deepcopy(self)

    def replace(
        self,
        **changes: Any,
    ) -> "MetricSnapshot":
        """
        Return a copied snapshot with updated fields.
        """

        data = self.to_dict()

        if "timestamp" in changes:
            data["timestamp"] = float(changes.pop("timestamp"))

        data.update(changes)

        return self.from_dict(data)

# ==========================================================
# Part 7. Comparison
# ==========================================================

    def __eq__(
        self,
        other: object,
    ) -> bool:

        if not isinstance(other, MetricSnapshot):
            return NotImplemented

        return (
            self.timestamp == other.timestamp
            and self.metrics == other.metrics
            and self.metadata == other.metadata
            and self.version == other.version
        )

    def __hash__(self) -> int:

        return hash(
            (
                self.timestamp,
                frozenset(self.metrics.items()),
                frozenset(self.metadata.items()),
                self.version,
            )
        )


# ==========================================================
# Part 8. Python Protocols
# ==========================================================

    def items(self):

        return self.metrics.items()

    def keys(self):

        return self.metrics.keys()

    def values(self):

        return self.metrics.values()

    def get(
        self,
        key: str,
        default: Any = None,
    ):

        return self.metrics.get(
            key,
            default,
        )

    def update_metadata(
        self,
        metadata: Mapping[str, Any],
    ) -> None:

        if not isinstance(metadata, Mapping):
            raise TypeError("metadata must be a mapping")

        self.metadata.update(dict(metadata))

    def add_metric(
        self,
        key: str,
        value: Any,
    ) -> None:

        self.metrics[str(key)] = value

    def remove_metric(
        self,
        key: str,
    ) -> None:

        self.metrics.pop(
            key,
            None,
        )

    def clear(self) -> None:

        self.metrics.clear()
        self.metadata.clear()

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"timestamp={self.timestamp!r}, "
            f"metrics={self.metrics!r}, "
            f"metadata={self.metadata!r}, "
            f"version={self.version!r})"
        )

    def __str__(self) -> str:

        return str(self.metrics)

    def __bool__(self) -> bool:

        return bool(self.metrics)

    def __len__(self) -> int:

        return len(self.metrics)

    def __iter__(self):

        return iter(self.metrics)

    def __contains__(
        self,
        key: object,
    ) -> bool:

        return key in self.metrics

    def __getitem__(
        self,
        key: str,
    ) -> Any:

        return self.metrics[key]

    def __setitem__(
        self,
        key: str,
        value: Any,
    ) -> None:

        self.metrics[str(key)] = value

    def __delitem__(
        self,
        key: str,
    ) -> None:

        del self.metrics[key]


# ==========================================================
# Part 9. Public API
# ==========================================================

__all__ = [
    "MetricSnapshot",
    "MetricValue",
    "MetricMap",
    "MetadataMap",
    "DEFAULT_VERSION",
]            
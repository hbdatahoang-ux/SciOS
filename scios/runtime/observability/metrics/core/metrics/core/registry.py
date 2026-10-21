# ==========================================================
# Part 1. Imports
# ==========================================================

from __future__ import annotations

import copy as _copy
import json
import time

from dataclasses import dataclass, field, replace as _replace
from typing import Any, TypeAlias

from .metric import Metric


# ==========================================================
# Part 2. Constants & Type Aliases
# ==========================================================

DEFAULT_VERSION: str = "1.0"

MetricMap: TypeAlias = dict[str, Metric]
MetricItems: TypeAlias = list[tuple[str, Metric]]
MetricValues: TypeAlias = list[Metric]
MetricNames: TypeAlias = list[str]


# ==========================================================
# Part 3. Dataclass / Core Container
# ==========================================================

@dataclass(slots=True)
class MetricRegistry:
    """
    Registry of Metric objects.
    """

    metrics: MetricMap = field(default_factory=dict)
    version: str = DEFAULT_VERSION
    created_at: float = field(default_factory=time.time)

    @property
    def size(self) -> int:
        """
        Number of registered metrics.
        """
        return len(self.metrics)

# ==========================================================
# Part 4. Validation
# ==========================================================

    def __post_init__(self) -> None:
        if not isinstance(self.metrics, dict):
            try:
                self.metrics = dict(self.metrics)
            except Exception:
                self.metrics = {}

    def validate(self) -> None:
        """
        Validate registry.
        """
        if not isinstance(self.metrics, dict):
            raise TypeError("metrics must be a dict[str, Metric]")

        for name, metric in self.metrics.items():
            if not isinstance(name, str):
                raise TypeError("metric name must be str")

            if not isinstance(metric, Metric):
                raise TypeError("metric must be Metric")

            metric.validate()

        if not isinstance(self.version, str):
            raise TypeError("version must be str")

    def is_valid(self) -> bool:
        """
        Return True if registry is valid.
        """
        try:
            self.validate()
            return True
        except Exception:
            return False


# ==========================================================
# Part 5. Registration API
# ==========================================================

    def register(
        self,
        metric: Metric,
    ) -> None:
        """
        Register metric.
        """
        if not isinstance(metric, Metric):
            raise TypeError("metric must be Metric")

        self.metrics[metric.name] = metric

    def unregister(
        self,
        name: str,
    ) -> Metric | None:
        """
        Remove metric.
        """
        return self.metrics.pop(name, None)

    def clear(self) -> None:
        """
        Remove all metrics.
        """
        self.metrics.clear()

    def replace(
        self,
        **changes: Any,
    ) -> "MetricRegistry":
        """
        Dataclass replace.
        """
        return _replace(self, **changes)


# ==========================================================
# Part 6. Lookup API
# ==========================================================

    def get(
        self,
        name: str,
        default: Metric | None = None,
    ) -> Metric | None:
        """
        Get metric by name.
        """
        return self.metrics.get(name, default)

    def items(self) -> MetricItems:
        """
        Registry items.
        """
        return list(self.metrics.items())

    def keys(self) -> MetricNames:
        """
        Registry keys.
        """
        return list(self.metrics.keys())

    def values(self) -> MetricValues:
        """
        Registry values.
        """
        return list(self.metrics.values())

    def names(self) -> MetricNames:
        """
        Metric names.
        """
        return list(self.metrics.keys())

# ==========================================================
# Part 7. Serialization
# ==========================================================

    def to_dict(self) -> dict[str, Any]:
        return {
            "metrics": {
                name: metric.to_dict()
                for name, metric in self.metrics.items()
            },
            "version": self.version,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "MetricRegistry":
        metrics = {
            name: Metric.from_dict(metric_data)
            for name, metric_data in data.get("metrics", {}).items()
        }

        return cls(
            metrics=metrics,
            version=data.get("version", DEFAULT_VERSION),
            created_at=data.get("created_at", time.time()),
        )

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(
        cls,
        data: str,
    ) -> "MetricRegistry":
        return cls.from_dict(json.loads(data))


# ==========================================================
# Part 8. Copy API
# ==========================================================

    def copy(self) -> "MetricRegistry":
        return MetricRegistry(
            metrics=dict(self.metrics),
            version=self.version,
            created_at=self.created_at,
        )

    def clone(self) -> "MetricRegistry":
        return self.copy()

    def deepcopy(self) -> "MetricRegistry":
        return MetricRegistry(
            metrics={
                k: _copy.deepcopy(v)
                for k, v in self.metrics.items()
            },
            version=self.version,
            created_at=self.created_at,
        )

    def replace(
        self,
        **changes: Any,
    ) -> "MetricRegistry":
        return _replace(self, **changes)


# ==========================================================
# Part 9. Comparison
# ==========================================================

    def __eq__(
        self,
        other: object,
    ) -> bool:
        if not isinstance(other, MetricRegistry):
            return False

        return (
            self.metrics == other.metrics
            and self.version == other.version
        )

    def __hash__(self) -> int:
        return hash(
            (
                frozenset(self.metrics.items()),
                self.version,
            )
        )

# ==========================================================
# Part 10. Python Protocols
# ==========================================================

    def __repr__(self) -> str:
        return (
            f"MetricRegistry(size={len(self.metrics)}, "
            f"version={self.version!r})"
        )

    def __str__(self) -> str:
        return self.__repr__()

    def __bool__(self) -> bool:
        return bool(self.metrics)

    def __len__(self) -> int:
        return len(self.metrics)

    def __iter__(self):
        """
        Iterate over metric names.
        """
        return iter(self.metrics)

    def __contains__(
        self,
        key: object,
    ) -> bool:
        return key in self.metrics

    def __getitem__(
        self,
        key: str,
    ) -> Metric:
        return self.metrics[key]

    def __setitem__(
        self,
        key: str,
        value: Metric,
    ) -> None:
        if not isinstance(value, Metric):
            raise TypeError("value must be Metric")

        self.metrics[key] = value

    def __delitem__(
        self,
        key: str,
    ) -> None:
        del self.metrics[key]


# ==========================================================
# Part 11. Pickle Support
# ==========================================================

    def __getstate__(self) -> dict[str, Any]:
        return self.to_dict()

    def __setstate__(
        self,
        state: dict[str, Any],
    ) -> None:
        restored = MetricRegistry.from_dict(state)

        self.metrics = restored.metrics
        self.version = restored.version
        self.created_at = restored.created_at


# ==========================================================
# Part 12. Public API
# ==========================================================

__all__ = [
    "DEFAULT_VERSION",
    "MetricMap",
    "MetricItems",
    "MetricValues",
    "MetricNames",
    "MetricRegistry",
]                        
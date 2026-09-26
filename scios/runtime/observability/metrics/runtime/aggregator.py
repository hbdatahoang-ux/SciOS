"""
Runtime Aggregator
==================

Runtime metric aggregation engine.

Python 3.11+
"""

# ==============================================================================
# Part 1. Header
# ==============================================================================

from __future__ import annotations

import copy
import json
import math
import time

from typing import Any
from typing import TypeAlias

from .collector import RuntimeCollector


# ==============================================================================
# Part 2. Constants
# ==============================================================================

DEFAULT_NAME = "aggregator"

DEFAULT_ENABLED = True

DEFAULT_WINDOW_SIZE = 1024

DEFAULT_PRECISION = 6

DEFAULT_AGGREGATED: dict[str, Any] = {}

DEFAULT_COUNT = 0

DEFAULT_IGNORE_NONE = True

DEFAULT_NUMERIC_ONLY = True


__all__ = [
    "DEFAULT_NAME",
    "DEFAULT_ENABLED",
    "DEFAULT_WINDOW_SIZE",
    "DEFAULT_PRECISION",
    "DEFAULT_AGGREGATED",
    "DEFAULT_COUNT",
    "DEFAULT_IGNORE_NONE",
    "DEFAULT_NUMERIC_ONLY",
    "RuntimeAggregator",
]


# ==============================================================================
# Part 3. Type Aliases
# ==============================================================================

AggregateValue: TypeAlias = int | float | bool | str | None

AggregateDict: TypeAlias = dict[str, AggregateValue]

SampleList: TypeAlias = list[dict[str, Any]]

NumericDict: TypeAlias = dict[str, float]

AggregatorState: TypeAlias = dict[str, Any]

AggregatorStats: TypeAlias = dict[str, Any]


# ==============================================================================
# Part 4. RuntimeAggregator
# ==============================================================================


class RuntimeAggregator:

    __slots__ = (
        "_name",
        "_enabled",
        "_collector",
        "_aggregated",
        "_count",
        "_created_at",
        "_last_aggregate",
        "_total_sum",
        "_minimum",
        "_maximum",
        "_window_size",
        "_precision",
    )

    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------

    def __init__(
        self,
        *,
        name: str = DEFAULT_NAME,
        collector: RuntimeCollector | None = None,
        enabled: bool = DEFAULT_ENABLED,
        window_size: int = DEFAULT_WINDOW_SIZE,
        precision: int = DEFAULT_PRECISION,
    ) -> None:

        self._name = str(name)

        self._enabled = bool(enabled)

        self._collector = (
            collector
            if collector is not None
            else RuntimeCollector()
        )

        self._aggregated: AggregateDict = {}

        self._count = DEFAULT_COUNT

        self._created_at = time.time()

        self._last_aggregate: float | None = None

        self._total_sum: NumericDict = {}

        self._minimum: NumericDict = {}

        self._maximum: NumericDict = {}

        self._window_size = int(window_size)

        self._precision = int(precision)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:
        return self._name

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def collector(self) -> RuntimeCollector:
        return self._collector

    @property
    def aggregated(self) -> AggregateDict:
        return self._aggregated

    @property
    def count(self) -> int:
        return self._count

    @property
    def size(self) -> int:
        return len(self._aggregated)

    @property
    def created_at(self) -> float:
        return self._created_at

    @property
    def last_aggregate(self) -> float | None:
        return self._last_aggregate

    @property
    def window_size(self) -> int:
        return self._window_size

    @property
    def precision(self) -> int:
        return self._precision


# ==============================================================================
# Part 5. Lifecycle
# ==============================================================================

    def enable(self):

        self._enabled = True

        return self

    def disable(self):

        self._enabled = False

        return self

    def clear(self):

        self._aggregated.clear()

        self._count = DEFAULT_COUNT

        self._total_sum.clear()

        self._minimum.clear()

        self._maximum.clear()

        self._last_aggregate = None

        return self

    def reset(self):

        self._enabled = DEFAULT_ENABLED

        return self.clear()

    def aggregate(self):

        if not self._enabled:
            return False

        self._last_aggregate = time.time()

        return self.recompute()


# ==============================================================================
# Part 6. Aggregation API
# ==============================================================================

    def aggregate_sample(
        self,
        sample: dict[str, Any],
    ):

        if not self._enabled:
            return False

        self._count += 1

        for key, value in sample.items():

            self._aggregated[key] = value

        return True

    def aggregate_samples(
        self,
        samples: SampleList,
    ):

        success = True

        for sample in samples:

            if not self.aggregate_sample(sample):
                success = False

        return success

    def recompute(self):

        self.clear()

        samples = self.collector.samples

        if not samples:
            return False

        return self.aggregate_samples(samples)

    def get(
        self,
        key: str,
        default: Any = None,
    ):

        return self._aggregated.get(key, default)

    def keys(self):

        return self._aggregated.keys()

    def values(self):

        return self._aggregated.values()

    def items(self):

        return self._aggregated.items()

    def exists(
        self,
        key: str,
    ) -> bool:

        return key in self._aggregated

    def has_key(
        self,
        key: str,
    ) -> bool:

        return self.exists(key)

# ==============================================================================
# Part 7. Statistics
# ==============================================================================

    def sum(
        self,
        key: str | None = None,
    ):

        if key is not None:
            value = self._aggregated.get(key, 0)

            if isinstance(value, (int, float)) and not isinstance(value, bool):
                return round(float(value), self._precision)

            return 0.0

        total = 0.0

        for value in self._aggregated.values():

            if isinstance(value, (int, float)) and not isinstance(value, bool):
                total += float(value)

        return round(total, self._precision)

    def average(
        self,
        key: str | None = None,
    ):

        if key is not None:

            if self._count == 0:
                return 0.0

            return round(self.sum(key) / self._count, self._precision)

        numeric = [
            float(v)
            for v in self._aggregated.values()
            if isinstance(v, (int, float)) and not isinstance(v, bool)
        ]

        if not numeric:
            return 0.0

        return round(sum(numeric) / len(numeric), self._precision)

    def minimum(
        self,
        key: str | None = None,
    ):

        if key is not None:
            return self._minimum.get(key)

        return dict(self._minimum)

    def maximum(
        self,
        key: str | None = None,
    ):

        if key is not None:
            return self._maximum.get(key)

        return dict(self._maximum)

    def statistics(self) -> AggregatorStats:

        return {
            "count": self._count,
            "size": self.size,
            "sum": self.sum(),
            "average": self.average(),
            "minimum": self.minimum(),
            "maximum": self.maximum(),
        }

    def reset_statistics(self):

        self._count = DEFAULT_COUNT

        self._total_sum.clear()

        self._minimum.clear()

        self._maximum.clear()

        return self


# ==============================================================================
# Part 8. Operations
# ==============================================================================

    def clone(self):

        return copy.deepcopy(self)

    def copy(self):

        return self.clone()

    def merge(
        self,
        other: "RuntimeAggregator",
    ):

        if not isinstance(other, RuntimeAggregator):
            return self

        self._aggregated.update(other.aggregated)

        self._count += other.count

        return self

    def update(
        self,
        other: "RuntimeAggregator",
    ):

        return self.merge(other)

    def snapshot(self) -> AggregatorState:

        return self.to_dict()

    def restore(
        self,
        state: AggregatorState,
    ):

        restored = self.from_dict(state)

        self._name = restored.name
        self._enabled = restored.enabled
        self._collector = restored.collector
        self._aggregated = restored.aggregated
        self._count = restored.count
        self._created_at = restored.created_at
        self._last_aggregate = restored.last_aggregate
        self._total_sum = restored._total_sum
        self._minimum = restored._minimum
        self._maximum = restored._maximum
        self._window_size = restored.window_size
        self._precision = restored.precision

        return self


# ==============================================================================
# Part 9. Validation
# ==============================================================================

    def validate(self) -> bool:

        if not isinstance(self._name, str):
            return False

        if self._window_size <= 0:
            return False

        if self._precision < 0:
            return False

        if not isinstance(self._aggregated, dict):
            return False

        return True

    def normalize(
        self,
        value: Any,
    ):

        if isinstance(value, float):

            if math.isnan(value):
                return 0.0

            if math.isinf(value):
                return 0.0

            return round(value, self._precision)

        return value


# ==============================================================================
# Part 10. Serialization
# ==============================================================================

    def to_dict(self) -> AggregatorState:

        return {
            "name": self._name,
            "enabled": self._enabled,
            "aggregated": copy.deepcopy(self._aggregated),
            "count": self._count,
            "created_at": self._created_at,
            "last_aggregate": self._last_aggregate,
            "window_size": self._window_size,
            "precision": self._precision,
        }

    @classmethod
    def from_dict(
        cls,
        data: AggregatorState,
    ):

        obj = cls(
            name=data.get("name", DEFAULT_NAME),
            enabled=data.get("enabled", DEFAULT_ENABLED),
            window_size=data.get("window_size", DEFAULT_WINDOW_SIZE),
            precision=data.get("precision", DEFAULT_PRECISION),
        )

        obj._aggregated = copy.deepcopy(
            data.get("aggregated", {})
        )

        obj._count = data.get("count", DEFAULT_COUNT)

        obj._created_at = data.get(
            "created_at",
            time.time(),
        )

        obj._last_aggregate = data.get(
            "last_aggregate",
        )

        return obj

    def to_tuple(self):

        return (
            self._name,
            self._enabled,
            copy.deepcopy(self._aggregated),
            self._count,
            self._created_at,
            self._last_aggregate,
            self._window_size,
            self._precision,
        )

    @classmethod
    def from_tuple(
        cls,
        data: tuple,
    ):

        return cls.from_dict(
            {
                "name": data[0],
                "enabled": data[1],
                "aggregated": data[2],
                "count": data[3],
                "created_at": data[4],
                "last_aggregate": data[5],
                "window_size": data[6],
                "precision": data[7],
            }
        )

    def to_json(self) -> str:

        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
        )

    @classmethod
    def from_json(
        cls,
        text: str,
    ):

        return cls.from_dict(
            json.loads(text)
        )


# ==============================================================================
# Part 11. Diagnostics
# ==============================================================================

    def summary(self):

        return {
            "name": self._name,
            "count": self._count,
            "size": self.size,
        }

    def diagnostics(self):

        return {
            "valid": self.validate(),
            "enabled": self._enabled,
            "statistics": self.statistics(),
        }

    def report(self):

        return {
            **self.summary(),
            **self.diagnostics(),
        }

    def status(self):

        if not self._enabled:
            return "disabled"

        if self.size == 0:
            return "idle"

        return "active"


# ==============================================================================
# Part 12. Protocols
# ==============================================================================

    def __len__(self):

        return self.size

    def __contains__(
        self,
        item,
    ):

        return item in self._aggregated

    def __iter__(self):

        return iter(self._aggregated.items())

    def __hash__(self):

        return hash(
            (
                self._name,
                self._count,
            )
        )

    def __eq__(
        self,
        other,
    ):

        if not isinstance(other, RuntimeAggregator):
            return False

        return self.to_dict() == other.to_dict()

    def __repr__(self):

        return (
            f"RuntimeAggregator("
            f"name={self._name!r}, "
            f"size={self.size}, "
            f"enabled={self._enabled})"
        )

    def __str__(self):

        return self.__repr__()

    def __bool__(self):

        return self._enabled        
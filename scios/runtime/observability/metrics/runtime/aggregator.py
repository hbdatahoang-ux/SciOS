"""
SciOS-NG Runtime Metrics Aggregation Engine

File:
    scios/runtime/observability/metrics/runtime/aggregator.py

Description
-----------
Runtime Metrics Aggregation Engine responsible for collecting,
aggregating, managing, and exposing runtime metrics.

This module provides the foundation for the Runtime Observability
subsystem. Aggregation logic, lifecycle management, serialization,
statistics, and event dispatching are implemented progressively in
subsequent parts.

SciOS-NG v0.2
"""

from __future__ import annotations

from datetime import datetime
from threading import RLock
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4


class MetricAggregator:
    """
    Runtime Metrics Aggregation Engine.

    The MetricAggregator is the central coordinator responsible for:

    - Metric registration
    - Runtime aggregation
    - Aggregation strategy management
    - Runtime statistics
    - Event & Hook dispatching
    - Snapshot management
    - Serialization

    Notes
    -----
    Part 1 implements only the runtime foundation.
    Runtime behavior is added incrementally in later parts.
    """

    VERSION = "0.2.0"

    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------

    def __init__(
        self,
        name: str = "MetricAggregator",
        description: str = "",
    ) -> None:
        """
        Initialize Runtime Metrics Aggregation Engine.
        """

        # --------------------------------------------------------------
        # Identity
        # --------------------------------------------------------------

        self._id: str = str(uuid4())
        self._name: str = name
        self._description: str = description

        # --------------------------------------------------------------
        # Registries
        # --------------------------------------------------------------

        # Registered runtime metrics
        self._registry: Dict[str, Any] = {}

        # Cached aggregation results
        self._aggregation_registry: Dict[str, Any] = {}

        # Aggregation strategies
        self._strategy_registry: Dict[str, Callable[..., Any]] = {}

        # --------------------------------------------------------------
        # Runtime State
        # --------------------------------------------------------------

        self._enabled: bool = True
        self._frozen: bool = False
        self._closed: bool = False

        # --------------------------------------------------------------
        # Synchronization
        # --------------------------------------------------------------

        self._lock = RLock()

        # --------------------------------------------------------------
        # Metadata
        # --------------------------------------------------------------

        now = datetime.utcnow()

        self._created_at: datetime = now
        self._updated_at: datetime = now
        self._version: str = self.VERSION

        # --------------------------------------------------------------
        # Internal Components
        # --------------------------------------------------------------

        # Runtime statistics
        self._statistics: Dict[str, Any] = {}

        # Registered runtime hooks
        self._hooks: Dict[str, List[Callable[..., Any]]] = {}

        # Runtime event queue / dispatcher storage
        self._events: List[Any] = []

        # Runtime snapshot cache
        self._snapshot: Optional[Dict[str, Any]] = None

    # ------------------------------------------------------------------
    # Internal Utilities
    # ------------------------------------------------------------------

    def _touch(self) -> None:
        """
        Update modification timestamp.
        """
        self._updated_at = datetime.utcnow()
    # ==================================================================
    # Part 2. Aggregation API
    # ==================================================================

    def aggregate(
        self,
        name: str,
        value: Any,
        strategy: str | None = None,
    ) -> Any:
        """
        Aggregate a single metric.

        Parameters
        ----------
        name:
            Metric name.

        value:
            Metric value.

        strategy:
            Aggregation strategy name.

        Returns
        -------
        Aggregated result.
        """
        self.record(name, value)

        if strategy is None:
            return value

        fn = self._strategy_registry.get(strategy)

        if fn is None:
            raise KeyError(f"Unknown aggregation strategy: {strategy}")

        result = fn(self._registry[name])

        self._aggregation_registry[name] = result

        self._touch()

        return result

    def aggregate_many(
        self,
        metrics: dict[str, Any],
        strategy: str |None = None,
    ) -> dict[str, Any]:
        """
        Aggregate multiple metrics.
        """
        results = {}

        for name, value in metrics.items():
            results[name] = self.aggregate(
                name,
                value,
                strategy=strategy,
            )

        return results

    def aggregate_all(
        self,
        strategy: str | None = None,
    ) -> dict[str, Any]:
        """
        Aggregate every registered metric.
        """
        results = {}

        for name, value in self._registry.items():

            if strategy is None:
                results[name] = value
                continue

            fn = self._strategy_registry.get(strategy)

            if fn is None:
                raise KeyError(strategy)

            results[name] = fn(value)

        self._aggregation_registry = dict(results)

        self._touch()

        return results

    def aggregate_batch(
        self,
        metrics: list[tuple[str, Any]],
        strategy: str | None = None,
    ) -> dict[str, Any]:
        """
        Aggregate a batch of metrics.
        """
        return self.aggregate_many(
            dict(metrics),
            strategy=strategy,
        )

    def aggregate_selected(
        self,
        names: list[str],
        strategy: str | None = None,
    ) -> dict[str, Any]:
        """
        Aggregate selected metrics.
        """
        results = {}

        for name in names:

            if name not in self._registry:
                continue

            value = self._registry[name]

            if strategy is None:
                results[name] = value
                continue

            fn = self._strategy_registry.get(strategy)

            if fn is None:
                raise KeyError(strategy)

            results[name] = fn(value)

        return results

    # ------------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------------

    def record(
        self,
        name: str,
        value: Any,
    ) -> None:
        """
        Record a runtime metric.
        """
        self._registry[name] = value
        self._touch()

    def record_many(
        self,
        metrics: dict[str, Any],
    ) -> None:
        """
        Record multiple runtime metrics.
        """
        self._registry.update(metrics)
        self._touch()

    # ------------------------------------------------------------------
    # Composition
    # ------------------------------------------------------------------

    def merge(
        self,
        other: "MetricAggregator",
    ) -> "MetricAggregator":
        """
        Merge another aggregator into this instance.
        """
        self._registry.update(other._registry)
        self._aggregation_registry.update(
            other._aggregation_registry
        )
        self._touch()
        return self

    def combine(
        self,
        other: "MetricAggregator",
    ) -> "MetricAggregator":
        """
        Combine two aggregators.

        Alias of merge().
        """
        return self.merge(other)

    def reduce(
        self,
        strategy: str,
    ) -> dict[str, Any]:
        """
        Reduce all metrics using one strategy.
        """
        return self.aggregate_all(strategy)

    def accumulate(
        self,
        name: str,
        value: Any,
    ) -> None:
        """
        Accumulate values into one metric.
        """
        current = self._registry.get(name)

        if current is None:
            self._registry[name] = [value]

        elif isinstance(current, list):
            current.append(value)

        else:
            self._registry[name] = [current, value]

        self._touch()

    # ------------------------------------------------------------------
    # Runtime Updates
    # ------------------------------------------------------------------

    def update(
        self,
        name: str,
        value: Any,
    ) -> None:
        """
        Update a metric.
        """
        self._registry[name] = value
        self._touch()

    def flush(self) -> dict[str, Any]:
        """
        Flush aggregated results.
        """
        data = dict(self._aggregation_registry)

        self._aggregation_registry.clear()

        self._touch()

        return data

    def reset(self) -> None:
        """
        Reset aggregation engine.
        """
        self._registry.clear()
        self._aggregation_registry.clear()
        self._touch()
# ==================================================================
# Part 3. Metric Registry API
# ==================================================================

# ------------------------------------------------------------------
# Registration
# ------------------------------------------------------------------

def register(
    self,
    name: str,
    metric: Any,
) -> Any:
    """
    Register a runtime metric.
    """
    with self._lock:
        if self._closed:
            raise RuntimeError("Aggregator is closed.")

        if self._frozen:
            raise RuntimeError("Aggregator is frozen.")

        self._registry[name] = metric
        self._touch()

        return metric


def unregister(
    self,
    name: str,
) -> Any:
    """
    Unregister a runtime metric.
    """
    with self._lock:
        metric = self._registry.pop(name, None)
        self._touch()
        return metric


# ------------------------------------------------------------------
# Lookup
# ------------------------------------------------------------------

def contains(
    self,
    name: str,
) -> bool:
    """
    Check whether a metric exists.
    """
    return name in self._registry


def exists(
    self,
    name: str,
) -> bool:
    """
    Alias of contains().
    """
    return self.contains(name)


def get(
    self,
    name: str,
    default: Any = None,
) -> Any:
    """
    Get a metric.
    """
    return self._registry.get(name, default)


def find(
    self,
    predicate: Callable[[str, Any], bool],
) -> dict[str, Any]:
    """
    Find metrics matching a predicate.

    Example
    -------
    >>> aggregator.find(
    ...     lambda name, metric: name.startswith("cpu")
    ... )
    """
    return {
        name: metric
        for name, metric in self._registry.items()
        if predicate(name, metric)
    }


# ------------------------------------------------------------------
# Enumeration
# ------------------------------------------------------------------

def keys(self):
    """
    Return metric names.
    """
    return self._registry.keys()


def values(self):
    """
    Return metric values.
    """
    return self._registry.values()


def items(self):
    """
    Return metric items.
    """
    return self._registry.items()


def metrics(self) -> dict[str, Any]:
    """
    Return a shallow copy of the metric registry.
    """
    return dict(self._registry)


# ------------------------------------------------------------------
# Information
# ------------------------------------------------------------------

def count(self) -> int:
    """
    Number of registered metrics.
    """
    return len(self._registry)


def metric_names(self) -> list[str]:
    """
    Return all metric names.
    """
    return list(self._registry.keys())


# ------------------------------------------------------------------
# Maintenance
# ------------------------------------------------------------------

def clear_registry(self) -> None:
    """
    Remove every registered metric.
    """
    with self._lock:
        self._registry.clear()
        self._touch()
# ==================================================================
# Part 4. Aggregation Strategy API
# ==================================================================

import math
from statistics import median
from typing import Callable, Iterable, Any


# ------------------------------------------------------------------
# Internal Helper
# ------------------------------------------------------------------

def _values(
    self,
    name: str | None = None,
) -> list[float]:
    """
    Return numeric values for aggregation.

    If name is None, aggregate over all registered metrics.
    """

    if name is None:
        values = list(self._registry.values())
    else:
        values = self._registry.get(name, [])

    if not isinstance(values, (list, tuple)):
        values = [values]

    return [
        float(v)
        for v in values
        if isinstance(v, (int, float))
    ]


# ------------------------------------------------------------------
# Built-in Strategies
# ------------------------------------------------------------------

def sum(self, name: str | None = None) -> float:
    values = self._values(name)
    return float(math.fsum(values))


def average(self, name: str | None = None) -> float:
    values = self._values(name)

    if not values:
        return 0.0

    return math.fsum(values) / len(values)


def minimum(self, name: str | None = None):
    values = self._values(name)

    if not values:
        return None

    return min(values)


def maximum(self, name: str | None = None):
    values = self._values(name)

    if not values:
        return None

    return max(values)


def count(self, name: str | None = None) -> int:
    return len(self._values(name))


def median(self, name: str | None = None):
    values = self._values(name)

    if not values:
        return None

    return median(values)


def percentile(
    self,
    p: float,
    name: str | None = None,
):
    values = sorted(self._values(name))

    if not values:
        return None

    if p <= 0:
        return values[0]

    if p >= 100:
        return values[-1]

    k = (len(values) - 1) * p / 100.0

    f = math.floor(k)
    c = math.ceil(k)

    if f == c:
        return values[int(k)]

    return (
        values[f]
        + (values[c] - values[f]) * (k - f)
    )


def variance(self, name: str | None = None):
    values = self._values(name)

    n = len(values)

    if n < 2:
        return 0.0

    mean = self.average(name)

    return sum(
        (v - mean) ** 2
        for v in values
    ) / (n - 1)


def std(self, name: str | None = None):
    return math.sqrt(self.variance(name))


def histogram(
    self,
    bins: int = 10,
    name: str | None = None,
):
    values = self._values(name)

    if not values:
        return []

    low = min(values)
    high = max(values)

    if low == high:
        return [len(values)]

    step = (high - low) / bins

    hist = [0] * bins

    for v in values:

        idx = min(
            int((v - low) / step),
            bins - 1,
        )

        hist[idx] += 1

    return hist


# ------------------------------------------------------------------
# Advanced Strategies
# ------------------------------------------------------------------

def moving_average(
    self,
    window_size: int,
    name: str,
):
    values = self._values(name)

    if len(values) < window_size:
        return []

    return [
        sum(values[i:i + window_size]) / window_size
        for i in range(len(values) - window_size + 1)
    ]


def weighted_average(
    self,
    weights: Iterable[float],
    name: str,
):
    values = self._values(name)

    weights = list(weights)

    if len(values) != len(weights):
        raise ValueError("weights mismatch")

    total = sum(weights)

    if total == 0:
        return 0.0

    return sum(
        v * w
        for v, w in zip(values, weights)
    ) / total


def ema(
    self,
    alpha: float,
    name: str,
):
    values = self._values(name)

    if not values:
        return None

    result = values[0]

    for v in values[1:]:
        result = alpha * v + (1 - alpha) * result

    return result


def window(
    self,
    size: int,
    name: str,
):
    values = self._values(name)

    return [
        values[i:i + size]
        for i in range(len(values) - size + 1)
    ]


def bucket(
    self,
    size: int,
    name: str,
):
    values = self._values(name)

    return [
        values[i:i + size]
        for i in range(0, len(values), size)
    ]


def rate(
    self,
    name: str,
):
    values = self._values(name)

    if len(values) < 2:
        return 0.0

    return values[-1] - values[-2]


def delta(
    self,
    name: str,
):
    values = self._values(name)

    if len(values) < 2:
        return 0.0

    return values[-1] - values[0]


# ------------------------------------------------------------------
# Strategy Management
# ------------------------------------------------------------------

def custom(
    self,
    strategy: str,
    name: str,
):
    fn = self.strategy(strategy)

    return fn(self._values(name))


def register_strategy(
    self,
    name: str,
    strategy: Callable[..., Any],
):
    self._strategy_registry[name] = strategy
    self._touch()


def remove_strategy(
    self,
    name: str,
):
    self._strategy_registry.pop(name, None)
    self._touch()


def strategy(
    self,
    name: str,
):
    if name not in self._strategy_registry:
        raise KeyError(
            f"Unknown strategy: {name}"
        )

    return self._strategy_registry[name]
# ==================================================================
# Part 5. Lifecycle Management
# ==================================================================

# ------------------------------------------------------------------
# Lifecycle
# ------------------------------------------------------------------

def enable(self) -> "MetricAggregator":
    """
    Enable the aggregator.
    """
    with self._lock:
        if self._closed:
            raise RuntimeError("Aggregator is closed.")

        self._enabled = True
        self._touch()

    return self


def disable(self) -> "MetricAggregator":
    """
    Disable the aggregator.
    """
    with self._lock:
        if self._closed:
            raise RuntimeError("Aggregator is closed.")

        self._enabled = False
        self._touch()

    return self


def freeze(self) -> "MetricAggregator":
    """
    Freeze the aggregator.

    While frozen, write operations should be rejected.
    """
    with self._lock:
        if self._closed:
            raise RuntimeError("Aggregator is closed.")

        self._frozen = True
        self._touch()

    return self


def unfreeze(self) -> "MetricAggregator":
    """
    Unfreeze the aggregator.
    """
    with self._lock:
        if self._closed:
            raise RuntimeError("Aggregator is closed.")

        self._frozen = False
        self._touch()

    return self


def close(self) -> "MetricAggregator":
    """
    Close the aggregator.

    A closed aggregator can no longer be modified until reopened.
    """
    with self._lock:
        self._enabled = False
        self._frozen = False
        self._closed = True
        self._touch()

    return self


def reopen(self) -> "MetricAggregator":
    """
    Reopen a previously closed aggregator.
    """
    with self._lock:
        self._closed = False
        self._enabled = True
        self._frozen = False
        self._touch()

    return self


# ------------------------------------------------------------------
# Runtime Properties
# ------------------------------------------------------------------

@property
def enabled(self) -> bool:
    """
    Whether the aggregator is enabled.
    """
    return self._enabled


@property
def disabled(self) -> bool:
    """
    Whether the aggregator is disabled.
    """
    return not self._enabled


@property
def frozen(self) -> bool:
    """
    Whether the aggregator is frozen.
    """
    return self._frozen


@property
def closed(self) -> bool:
    """
    Whether the aggregator is closed.
    """
    return self._closed


@property
def active(self) -> bool:
    """
    Whether the aggregator is active.

    An active aggregator is enabled, not frozen,
    and not closed.
    """
    return (
        self._enabled
        and not self._frozen
        and not self._closed
    )
# ==================================================================
# Part 6. Runtime Operations
# ==================================================================

from copy import copy as _copy
from copy import deepcopy


# ------------------------------------------------------------------
# Snapshot
# ------------------------------------------------------------------

def snapshot(self) -> dict[str, Any]:
    """
    Create a runtime snapshot.
    """
    with self._lock:

        self._snapshot = {
            "registry": deepcopy(self._registry),
            "aggregation_registry": deepcopy(
                self._aggregation_registry
            ),
            "strategy_registry": deepcopy(
                self._strategy_registry
            ),
            "enabled": self._enabled,
            "frozen": self._frozen,
            "closed": self._closed,
            "created_at": self._created_at,
            "updated_at": self._updated_at,
            "version": self._version,
        }

        return deepcopy(self._snapshot)


def restore(
    self,
    snapshot: dict[str, Any] | None = None,
) -> "MetricAggregator":
    """
    Restore from a snapshot.
    """
    with self._lock:

        data = snapshot or self._snapshot

        if data is None:
            raise RuntimeError("No snapshot available.")

        self._registry = deepcopy(
            data["registry"]
        )

        self._aggregation_registry = deepcopy(
            data["aggregation_registry"]
        )

        self._strategy_registry = deepcopy(
            data["strategy_registry"]
        )

        self._enabled = data["enabled"]
        self._frozen = data["frozen"]
        self._closed = data["closed"]

        self._created_at = data["created_at"]
        self._updated_at = data["updated_at"]
        self._version = data["version"]

        self._touch()

        return self


# ------------------------------------------------------------------
# Object Management
# ------------------------------------------------------------------

def clone(self) -> "MetricAggregator":
    """
    Create a deep clone.
    """
    return deepcopy(self)


def copy(self) -> "MetricAggregator":
    """
    Create a shallow copy.
    """
    return _copy(self)


# ------------------------------------------------------------------
# Cleanup
# ------------------------------------------------------------------

def clear(self) -> "MetricAggregator":
    """
    Clear runtime state.
    """
    with self._lock:

        self.clear_metrics()
        self.clear_aggregations()

        self._touch()

        return self


def clear_metrics(self) -> "MetricAggregator":
    """
    Clear metric registry.
    """
    with self._lock:

        self._registry.clear()

        self._touch()

        return self


def clear_aggregations(self) -> "MetricAggregator":
    """
    Clear aggregation cache.
    """
    with self._lock:

        self._aggregation_registry.clear()

        self._touch()

        return self


# ------------------------------------------------------------------
# Optimization
# ------------------------------------------------------------------

def compact(self) -> "MetricAggregator":
    """
    Compact runtime storage.

    Removes empty metric containers.
    """
    with self._lock:

        self._registry = {
            k: v
            for k, v in self._registry.items()
            if v not in (None, [], {}, ())
        }

        self._touch()

        return self


def optimize(self) -> "MetricAggregator":
    """
    Optimize runtime storage.
    """
    with self._lock:

        self.compact()

        self._touch()

        return self


def cleanup(self) -> "MetricAggregator":
    """
    Perform runtime cleanup.

    Removes temporary runtime data.
    """
    with self._lock:

        self._events.clear()

        self._touch()

        return self
# ==================================================================
# Part 7. Statistics & Diagnostics API
# ==================================================================

from datetime import datetime


# ------------------------------------------------------------------
# Runtime Metric Properties
# ------------------------------------------------------------------

@property
def metric_count(self) -> int:
    """
    Number of registered metrics.
    """
    return len(self._registry)


@property
def aggregation_count(self) -> int:
    """
    Number of cached aggregations.
    """
    return len(self._aggregation_registry)


@property
def last_update(self):
    """
    Last modification timestamp.
    """
    return self._updated_at


@property
def uptime(self):
    """
    Runtime uptime.
    """
    return datetime.utcnow() - self._created_at


@property
def events(self) -> int:
    """
    Number of runtime events.
    """
    return len(self._events)


@property
def errors(self) -> int:
    """
    Number of recorded runtime errors.
    """
    return self._statistics.get("errors", 0)


# ------------------------------------------------------------------
# Statistics
# ------------------------------------------------------------------

def summary(self) -> dict[str, object]:
    """
    Return a runtime summary.
    """
    return {
        "id": self._id,
        "name": self._name,
        "metric_count": self.metric_count,
        "aggregation_count": self.aggregation_count,
        "enabled": self._enabled,
        "frozen": self._frozen,
        "closed": self._closed,
        "uptime": self.uptime,
    }


def statistics(self) -> dict[str, object]:
    """
    Return runtime statistics.
    """
    data = self.summary()

    data.update(self._statistics)

    return data


def report(self) -> dict[str, object]:
    """
    Generate a runtime report.
    """
    return {
        "summary": self.summary(),
        "statistics": self.statistics(),
        "health": self.health(),
    }


def describe(self) -> dict[str, object]:
    """
    Describe the runtime state.
    """
    return {
        "identity": {
            "id": self._id,
            "name": self._name,
            "description": self._description,
        },
        "metadata": {
            "version": self._version,
            "created_at": self._created_at,
            "updated_at": self._updated_at,
        },
        "state": self.status(),
    }


# ------------------------------------------------------------------
# Diagnostics
# ------------------------------------------------------------------

def health(self) -> str:
    """
    Return runtime health.
    """
    if self._closed:
        return "closed"

    if self._frozen:
        return "frozen"

    if not self._enabled:
        return "disabled"

    return "healthy"


def status(self) -> dict[str, bool]:
    """
    Runtime status.
    """
    return {
        "enabled": self._enabled,
        "frozen": self._frozen,
        "closed": self._closed,
        "active": self.active,
    }


def info(self) -> dict[str, object]:
    """
    Return runtime information.
    """
    return {
        "id": self._id,
        "name": self._name,
        "description": self._description,
        "version": self._version,
    }


def diagnostics(self) -> dict[str, object]:
    """
    Return runtime diagnostics.
    """
    return {
        "health": self.health(),
        "status": self.status(),
        "events": self.events,
        "errors": self.errors,
        "last_update": self.last_update,
    }


def performance(self) -> dict[str, object]:
    """
    Return runtime performance metrics.
    """
    return {
        "metric_count": self.metric_count,
        "aggregation_count": self.aggregation_count,
        "uptime_seconds": self.uptime.total_seconds(),
    }


def throughput(self) -> dict[str, object]:
    """
    Return throughput information.
    """
    uptime = self.uptime.total_seconds()

    if uptime <= 0:
        rate = 0.0
    else:
        rate = self.metric_count / uptime

    return {
        "metrics_per_second": rate,
        "uptime_seconds": uptime,
    }
# ==================================================================
# Part 8. Serialization API
# ==================================================================

import json
import pickle
from copy import deepcopy

try:
    import yaml
except ImportError:
    yaml = None

try:
    import msgpack
except ImportError:
    msgpack = None


# ------------------------------------------------------------------
# Object Serialization
# ------------------------------------------------------------------

def to_dict(self) -> dict[str, Any]:
    """
    Serialize the aggregator into a Python dictionary.
    """

    return {
        "id": self._id,
        "name": self._name,
        "description": self._description,
        "registry": deepcopy(self._registry),
        "aggregation_registry": deepcopy(
            self._aggregation_registry
        ),
        "enabled": self._enabled,
        "frozen": self._frozen,
        "closed": self._closed,
        "statistics": deepcopy(self._statistics),
        "created_at": self._created_at.isoformat(),
        "updated_at": self._updated_at.isoformat(),
        "version": self._version,
    }


@classmethod
def from_dict(
    cls,
    data: dict[str, Any],
) -> "MetricAggregator":
    """
    Construct an aggregator from a dictionary.
    """

    obj = cls(
        name=data.get("name", "MetricAggregator"),
        description=data.get("description", ""),
    )

    obj._id = data["id"]

    obj._registry = deepcopy(
        data.get("registry", {})
    )

    obj._aggregation_registry = deepcopy(
        data.get("aggregation_registry", {})
    )

    obj._enabled = data.get("enabled", True)
    obj._frozen = data.get("frozen", False)
    obj._closed = data.get("closed", False)

    obj._statistics = deepcopy(
        data.get("statistics", {})
    )

    obj._created_at = datetime.fromisoformat(
        data["created_at"]
    )

    obj._updated_at = datetime.fromisoformat(
        data["updated_at"]
    )

    obj._version = data.get(
        "version",
        cls.VERSION,
    )

    return obj


# ------------------------------------------------------------------
# JSON
# ------------------------------------------------------------------

def to_json(
    self,
    **kwargs,
) -> str:
    """
    Serialize to JSON.
    """
    return json.dumps(
        self.to_dict(),
        **kwargs,
    )


@classmethod
def from_json(
    cls,
    data: str,
) -> "MetricAggregator":
    """
    Deserialize from JSON.
    """
    return cls.from_dict(
        json.loads(data)
    )


# ------------------------------------------------------------------
# Generic Serialization
# ------------------------------------------------------------------

def serialize(
    self,
    fmt: str = "json",
):
    """
    Serialize using the requested format.

    Supported:
        json
        yaml
        pickle
        msgpack
    """

    fmt = fmt.lower()

    if fmt == "json":
        return self.to_json(indent=2)

    if fmt == "yaml":

        if yaml is None:
            raise RuntimeError(
                "PyYAML is not installed."
            )

        return yaml.safe_dump(
            self.to_dict(),
            sort_keys=False,
        )

    if fmt == "pickle":
        return pickle.dumps(
            self.to_dict()
        )

    if fmt == "msgpack":

        if msgpack is None:
            raise RuntimeError(
                "msgpack is not installed."
            )

        return msgpack.packb(
            self.to_dict(),
            use_bin_type=True,
        )

    raise ValueError(
        f"Unsupported format: {fmt}"
    )


@classmethod
def deserialize(
    cls,
    data,
    fmt: str = "json",
):
    """
    Deserialize from any supported format.
    """

    fmt = fmt.lower()

    if fmt == "json":
        return cls.from_json(data)

    if fmt == "yaml":

        if yaml is None:
            raise RuntimeError(
                "PyYAML is not installed."
            )

        return cls.from_dict(
            yaml.safe_load(data)
        )

    if fmt == "pickle":
        return cls.from_dict(
            pickle.loads(data)
        )

    if fmt == "msgpack":

        if msgpack is None:
            raise RuntimeError(
                "msgpack is not installed."
            )

        return cls.from_dict(
            msgpack.unpackb(
                data,
                raw=False,
            )
        )

    raise ValueError(
        f"Unsupported format: {fmt}"
    )


# ------------------------------------------------------------------
# Import / Export
# ------------------------------------------------------------------

def export(
    self,
    path: str,
    fmt: str = "json",
):
    """
    Export the aggregator to a file.
    """

    data = self.serialize(fmt)

    mode = "wb" if isinstance(data, bytes) else "w"

    with open(path, mode) as f:
        f.write(data)


@classmethod
def import_data(
    cls,
    path: str,
    fmt: str = "json",
):
    """
    Import an aggregator from a file.
    """

    mode = "rb" if fmt in (
        "pickle",
        "msgpack",
    ) else "r"

    with open(path, mode) as f:
        data = f.read()

    return cls.deserialize(
        data,
        fmt=fmt,
    )
# ==================================================================
# Part 9. Events & Hooks
# ==================================================================

from collections import defaultdict
from typing import Any, Callable


# ------------------------------------------------------------------
# Runtime Events
# ------------------------------------------------------------------

def before_aggregate(self, *args, **kwargs) -> None:
    """Emit before aggregate event."""
    self.emit("before_aggregate", *args, **kwargs)


def after_aggregate(self, result=None, *args, **kwargs) -> None:
    """Emit after aggregate event."""
    self.emit(
        "after_aggregate",
        result=result,
        *args,
        **kwargs,
    )


def before_merge(self, *args, **kwargs) -> None:
    """Emit before merge event."""
    self.emit("before_merge", *args, **kwargs)


def after_merge(self, *args, **kwargs) -> None:
    """Emit after merge event."""
    self.emit("after_merge", *args, **kwargs)


def before_flush(self, *args, **kwargs) -> None:
    """Emit before flush event."""
    self.emit("before_flush", *args, **kwargs)


def after_flush(self, result=None, *args, **kwargs) -> None:
    """Emit after flush event."""
    self.emit(
        "after_flush",
        result=result,
        *args,
        **kwargs,
    )


def before_reset(self, *args, **kwargs) -> None:
    """Emit before reset event."""
    self.emit("before_reset", *args, **kwargs)


def after_reset(self, *args, **kwargs) -> None:
    """Emit after reset event."""
    self.emit("after_reset", *args, **kwargs)


def before_close(self, *args, **kwargs) -> None:
    """Emit before close event."""
    self.emit("before_close", *args, **kwargs)


def after_close(self, *args, **kwargs) -> None:
    """Emit after close event."""
    self.emit("after_close", *args, **kwargs)


# ------------------------------------------------------------------
# Hook Management
# ------------------------------------------------------------------

def add_hook(
    self,
    event: str,
    callback: Callable[..., Any],
) -> None:
    """
    Register a hook callback.
    """
    self._hooks.setdefault(event, []).append(callback)


def remove_hook(
    self,
    event: str,
    callback: Callable[..., Any],
) -> None:
    """
    Remove a hook callback.
    """
    callbacks = self._hooks.get(event)

    if callbacks and callback in callbacks:
        callbacks.remove(callback)


def clear_hooks(
    self,
    event: str | None = None,
) -> None:
    """
    Clear hook callbacks.
    """
    if event is None:
        self._hooks.clear()
    else:
        self._hooks.pop(event, None)


# ------------------------------------------------------------------
# Event Dispatcher
# ------------------------------------------------------------------

def emit(
    self,
    event: str,
    *args,
    **kwargs,
) -> None:
    """
    Emit an event.
    """

    payload = {
        "event": event,
        "args": args,
        "kwargs": kwargs,
    }

    self._events.append(payload)

    self.notify(event, *args, **kwargs)


def notify(
    self,
    event: str,
    *args,
    **kwargs,
) -> None:
    """
    Notify local hooks.
    """

    for callback in self._hooks.get(event, []):

        callback(*args, **kwargs)


def subscribe(
    self,
    event: str,
    callback: Callable[..., Any],
) -> None:
    """
    Subscribe to an event.

    Alias of add_hook().
    """
    self.add_hook(event, callback)


def unsubscribe(
    self,
    event: str,
    callback: Callable[..., Any],
) -> None:
    """
    Unsubscribe from an event.

    Alias of remove_hook().
    """
    self.remove_hook(event, callback)
# ==================================================================
# Part 10. Python Protocols
# ==================================================================

from copy import deepcopy


# ------------------------------------------------------------------
# Representation
# ------------------------------------------------------------------

def __repr__(self) -> str:
    return (
        f"{self.__class__.__name__}("
        f"id={self._id!r}, "
        f"name={self._name!r}, "
        f"metrics={self.metric_count}, "
        f"active={self.active})"
    )


def __str__(self) -> str:
    return (
        f"{self._name} "
        f"({self.metric_count} metrics)"
    )


# ------------------------------------------------------------------
# Container Protocol
# ------------------------------------------------------------------

def __len__(self) -> int:
    return self.count()


def __iter__(self):
    self._iterator = iter(self._registry.items())
    return self


def __next__(self):
    return next(self._iterator)


def __contains__(self, key: str) -> bool:
    return self.contains(key)


# ------------------------------------------------------------------
# Mapping Protocol
# ------------------------------------------------------------------

def __getitem__(self, key: str):
    return self.get(key)


def __setitem__(self, key: str, value):
    self.register(key, value)


def __delitem__(self, key: str):
    self.unregister(key)


# keys(), values(), items()
# đã được cài đặt trong Part 3.


# ------------------------------------------------------------------
# Object Protocol
# ------------------------------------------------------------------

def __bool__(self) -> bool:
    return self.active


def __eq__(self, other) -> bool:

    if not isinstance(other, MetricAggregator):
        return False

    return (
        self._id == other._id
        and self._registry == other._registry
    )


def __hash__(self) -> int:
    return hash(self._id)


# ------------------------------------------------------------------
# Copy Protocol
# ------------------------------------------------------------------

def __copy__(self):
    return self.copy()


def __deepcopy__(self, memo):
    return self.clone()


# ------------------------------------------------------------------
# Context Manager
# ------------------------------------------------------------------

def __enter__(self):
    self.enable()
    return self


def __exit__(
    self,
    exc_type,
    exc,
    tb,
):
    self.close()
    return False


# ------------------------------------------------------------------
# Callable
# ------------------------------------------------------------------

def __call__(
    self,
    name: str,
    value=None,
):
    """
    Shortcut API.

    aggregator("cpu")
        -> get()

    aggregator("cpu", 10)
        -> record()
    """

    if value is None:
        return self.get(name)

    self.record(name, value)

    return value


# ------------------------------------------------------------------
# Arithmetic
# ------------------------------------------------------------------

def __add__(
    self,
    other,
):
    clone = self.clone()
    clone.merge(other)
    return clone


def __iadd__(
    self,
    other,
):
    self.merge(other)
    return self


def __or__(
    self,
    other,
):
    clone = self.clone()
    clone.combine(other)
    return clone


def __ior__(
    self,
    other,
):
    self.combine(other)
    return self


# ------------------------------------------------------------------
# Comparison
# ------------------------------------------------------------------

def __lt__(
    self,
    other,
):
    return self.metric_count < other.metric_count


def __le__(
    self,
    other,
):
    return self.metric_count <= other.metric_count


def __gt__(
    self,
    other,
):
    return self.metric_count > other.metric_count


def __ge__(
    self,
    other,
):
    return self.metric_count >= other.metric_count                                                    
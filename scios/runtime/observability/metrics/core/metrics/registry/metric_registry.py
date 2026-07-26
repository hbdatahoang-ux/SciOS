"""
SciOS-NG Metrics - Metric Registry
=================================

Thread-safe registry for Metric objects.

Responsibilities
----------------
- Register metrics
- Remove metrics
- Lookup metrics
- Enumerate metrics

The registry DOES NOT:

- collect
- export
- monitor
- serialize
"""

from __future__ import annotations

from threading import RLock
from typing import Final

from ..core.metric import Metric
from ..core.exceptions import RegistryError

__all__ = [
    "MetricRegistry",
]


class MetricRegistry:
    """
    Thread-safe Metric registry.

    Metric key format:

        namespace.name
    """

    DEFAULT_NAMESPACE: Final[str] = "default"

    # ==========================================================
    # Foundation
    # ==========================================================

    def __init__(
        self,
        *,
        name: str = "default",
    ) -> None:

        self._name = name

        #
        # Registry Storage
        #
        # key -> Metric
        #
        self._metrics: dict[str, Metric] = {}

        #
        # Thread safety
        #
        self._lock = RLock()

    # ==========================================================
    # Internal Helpers
    # ==========================================================

    @staticmethod
    def make_key(metric: Metric) -> str:
        """
        Build the registry key.

        Example
        -------
        runtime.cpu_usage
        """

        namespace = (
            metric.namespace
            or MetricRegistry.DEFAULT_NAMESPACE
        )

        return f"{namespace}.{metric.name}"

    @staticmethod
    def build_key(
        namespace: str,
        name: str,
    ) -> str:
        """
        Build a registry key from namespace and name.
        """

        namespace = namespace or MetricRegistry.DEFAULT_NAMESPACE

        return f"{namespace}.{name}"

    # ==========================================================
    # Basic Properties
    # ==========================================================

    @property
    def name(self) -> str:
        """
        Registry name.
        """

        return self._name

    @property
    def lock(self) -> RLock:
        """
        Registry lock.
        """

        return self._lock
# ==========================================================
# Part 2. Registration API
# ==========================================================


from typing import Iterable

from ..core.metric import Metric
from ..core.exceptions import RegistryError


# ----------------------------------------------------------
# Register
# ----------------------------------------------------------

def register(
    self,
    metric: Metric,
    *,
    replace: bool = False,
) -> Metric:
    """
    Register a Metric.

    Parameters
    ----------
    metric:
        Metric instance.

    replace:
        Replace an existing metric if True.

    Returns
    -------
    Metric
        The registered metric.

    Raises
    ------
    RegistryError
        If the metric already exists and replace=False.
    """

    key = self.make_key(metric)

    with self._lock:

        if key in self._metrics and not replace:
            raise RegistryError(
                f"Metric '{key}' already registered."
            )

        self._metrics[key] = metric

    return metric


# ----------------------------------------------------------
# Register Many
# ----------------------------------------------------------

def register_many(
    self,
    metrics: Iterable[Metric],
    *,
    replace: bool = False,
) -> None:
    """
    Register multiple metrics.
    """

    for metric in metrics:
        self.register(
            metric,
            replace=replace,
        )


# ----------------------------------------------------------
# Unregister
# ----------------------------------------------------------

def unregister(
    self,
    metric: Metric,
) -> Metric:
    """
    Remove a metric from the registry.
    """

    return self.remove(
        self.make_key(metric)
    )


# ----------------------------------------------------------
# Remove
# ----------------------------------------------------------

def remove(
    self,
    key: str,
) -> Metric:
    """
    Remove a metric by registry key.

    Raises
    ------
    RegistryError
        If the key does not exist.
    """

    with self._lock:

        try:
            return self._metrics.pop(key)

        except KeyError as exc:
            raise RegistryError(
                f"Metric '{key}' not found."
            ) from exc


# ----------------------------------------------------------
# Clear
# ----------------------------------------------------------

def clear(self) -> None:
    """
    Remove all registered metrics.
    """

    with self._lock:
        self._metrics.clear()


# ----------------------------------------------------------
# Contains
# ----------------------------------------------------------

def contains(
    self,
    key: str,
) -> bool:
    """
    Return True if a metric exists.
    """

    return key in self._metrics


# ----------------------------------------------------------
# Contains Metric
# ----------------------------------------------------------

def contains_metric(
    self,
    metric: Metric,
) -> bool:
    """
    Return True if the Metric is registered.
    """

    return self.contains(
        self.make_key(metric)
    )   
# ==========================================================
# Part 3. Lookup API
# ==========================================================

# ----------------------------------------------------------
# Get
# ----------------------------------------------------------

def get(
    self,
    key: str,
    default: Metric | None = None,
) -> Metric | None:
    """
    Return a metric by registry key.

    Parameters
    ----------
    key:
        Registry key (namespace.name).

    default:
        Value returned if the metric is not found.
    """

    return self._metrics.get(key, default)


# ----------------------------------------------------------
# Require
# ----------------------------------------------------------

def require(
    self,
    key: str,
) -> Metric:
    """
    Return a metric or raise RegistryError.
    """

    metric = self.get(key)

    if metric is None:
        raise RegistryError(
            f"Metric '{key}' not found."
        )

    return metric


# ----------------------------------------------------------
# Find
# ----------------------------------------------------------

def find(
    self,
    name: str,
) -> list[Metric]:
    """
    Find metrics by metric name.

    Example
    -------
    cpu_usage

    Returns
    -------
    List[Metric]
    """

    return [
        metric
        for metric in self._metrics.values()
        if metric.name == name
    ]


# ----------------------------------------------------------
# Keys
# ----------------------------------------------------------

def keys(self) -> tuple[str, ...]:
    """
    Return all registry keys.
    """

    return tuple(self._metrics.keys())


# ----------------------------------------------------------
# Values
# ----------------------------------------------------------

def values(self) -> tuple[Metric, ...]:
    """
    Return all registered metrics.
    """

    return tuple(self._metrics.values())


# ----------------------------------------------------------
# Items
# ----------------------------------------------------------

def items(
    self,
) -> tuple[tuple[str, Metric], ...]:
    """
    Return registry items.
    """

    return tuple(self._metrics.items())


# ----------------------------------------------------------
# First
# ----------------------------------------------------------

def first(self) -> Metric | None:
    """
    Return the first registered metric.
    """

    return next(
        iter(self._metrics.values()),
        None,
    )


# ----------------------------------------------------------
# Last
# ----------------------------------------------------------

def last(self) -> Metric | None:
    """
    Return the last registered metric.
    """

    if not self._metrics:
        return None

    return next(
        reversed(self._metrics.values())
    )
# ==========================================================
# Part 4. Query API
# ==========================================================

# ----------------------------------------------------------
# By Namespace
# ----------------------------------------------------------

def by_namespace(
    self,
    namespace: str,
) -> tuple[Metric, ...]:
    """
    Return all metrics in a namespace.
    """

    return tuple(
        metric
        for metric in self._metrics.values()
        if metric.namespace == namespace
    )


# ----------------------------------------------------------
# By Type
# ----------------------------------------------------------

def by_type(
    self,
    metric_type: str,
) -> tuple[Metric, ...]:
    """
    Return all metrics of a given type.

    Example
    -------
    gauge
    counter
    histogram
    """

    return tuple(
        metric
        for metric in self._metrics.values()
        if metric.metric_type == metric_type
    )


# ----------------------------------------------------------
# By Unit
# ----------------------------------------------------------

def by_unit(
    self,
    unit: str,
) -> tuple[Metric, ...]:
    """
    Return all metrics using the given unit.
    """

    return tuple(
        metric
        for metric in self._metrics.values()
        if metric.unit == unit
    )


# ----------------------------------------------------------
# By Label
# ----------------------------------------------------------

def by_label(
    self,
    key: str,
    value: str | None = None,
) -> tuple[Metric, ...]:
    """
    Query metrics by label.

    If value is None, only the existence
    of the label is checked.
    """

    result: list[Metric] = []

    for metric in self._metrics.values():

        if not metric.has_label(key):
            continue

        if value is None:
            result.append(metric)
            continue

        if metric.get_label(key) == value:
            result.append(metric)

    return tuple(result)


# ----------------------------------------------------------
# By Attribute
# ----------------------------------------------------------

def by_attribute(
    self,
    key: str,
    value: object | None = None,
) -> tuple[Metric, ...]:
    """
    Query metrics by attribute.
    """

    result: list[Metric] = []

    for metric in self._metrics.values():

        if not metric.has_attribute(key):
            continue

        if value is None:
            result.append(metric)
            continue

        if metric.get_attribute(key) == value:
            result.append(metric)

    return tuple(result)


# ----------------------------------------------------------
# Filter
# ----------------------------------------------------------

def filter(
    self,
    predicate,
) -> tuple[Metric, ...]:
    """
    Generic query using a predicate.

    Example
    -------
    registry.filter(
        lambda m: m.value > 90
    )
    """

    return tuple(
        metric
        for metric in self._metrics.values()
        if predicate(metric)
    )


# ----------------------------------------------------------
# Search
# ----------------------------------------------------------

def search(
    self,
    keyword: str,
) -> tuple[Metric, ...]:
    """
    Search metrics by name or namespace.
    """

    keyword = keyword.lower()

    return tuple(
        metric
        for metric in self._metrics.values()
        if keyword in metric.name.lower()
        or keyword in metric.namespace.lower()
    )
# ==========================================================
# Part 5. Bulk Operations
# ==========================================================

# ----------------------------------------------------------
# Reset All
# ----------------------------------------------------------

def reset_all(self) -> None:
    """
    Reset all registered metrics.
    """

    with self._lock:
        for metric in self._metrics.values():
            metric.reset()


# ----------------------------------------------------------
# Clear All
# ----------------------------------------------------------

def clear_all(self) -> None:
    """
    Clear all metric values.
    """

    with self._lock:
        for metric in self._metrics.values():
            metric.clear()


# ----------------------------------------------------------
# Enable All
# ----------------------------------------------------------

def enable_all(self) -> None:
    """
    Enable all metrics.
    """

    with self._lock:
        for metric in self._metrics.values():
            metric.state.enable()


# ----------------------------------------------------------
# Disable All
# ----------------------------------------------------------

def disable_all(self) -> None:
    """
    Disable all metrics.
    """

    with self._lock:
        for metric in self._metrics.values():
            metric.state.disable()


# ----------------------------------------------------------
# Freeze All
# ----------------------------------------------------------

def freeze_all(self) -> None:
    """
    Freeze all metrics.
    """

    with self._lock:
        for metric in self._metrics.values():
            metric.state.freeze()


# ----------------------------------------------------------
# Unfreeze All
# ----------------------------------------------------------

def unfreeze_all(self) -> None:
    """
    Unfreeze all metrics.
    """

    with self._lock:
        for metric in self._metrics.values():
            metric.state.unfreeze()


# ----------------------------------------------------------
# Close All
# ----------------------------------------------------------

def close_all(self) -> None:
    """
    Close all metrics.
    """

    with self._lock:
        for metric in self._metrics.values():
            metric.state.close()


# ----------------------------------------------------------
# Reopen All
# ----------------------------------------------------------

def reopen_all(self) -> None:
    """
    Reopen all metrics.
    """

    with self._lock:
        for metric in self._metrics.values():
            metric.state.reopen()


# ----------------------------------------------------------
# Update All
# ----------------------------------------------------------

def update_all(
    self,
    value,
) -> None:
    """
    Update every metric with the same value.

    Useful for testing and synchronization.
    """

    with self._lock:
        for metric in self._metrics.values():
            metric.update(value)
# ==========================================================
# Part 6. Snapshot API
# ==========================================================

# ----------------------------------------------------------
# Snapshot
# ----------------------------------------------------------

def snapshot(self) -> dict[str, object]:
    """
    Create a snapshot of the entire registry.

    Returns
    -------
    dict
        Mapping of registry keys to MetricSnapshot objects.
    """

    with self._lock:
        return {
            key: metric.snapshot()
            for key, metric in self._metrics.items()
        }


# ----------------------------------------------------------
# Restore
# ----------------------------------------------------------

def restore(
    self,
    snapshots: dict[str, object],
) -> None:
    """
    Restore registry metrics from snapshots.

    Missing keys are ignored.
    """

    with self._lock:

        for key, snapshot in snapshots.items():

            metric = self._metrics.get(key)

            if metric is None:
                continue

            metric.restore(snapshot)


# ----------------------------------------------------------
# Clone
# ----------------------------------------------------------

def clone(self) -> "MetricRegistry":
    """
    Deep clone the registry.
    """

    registry = self.__class__(
        name=self.name,
    )

    with self._lock:

        for metric in self._metrics.values():
            registry.register(
                metric.clone()
            )

    return registry


# ----------------------------------------------------------
# Copy
# ----------------------------------------------------------

def copy(self) -> "MetricRegistry":
    """
    Alias of clone().
    """

    return self.clone()
# ==========================================================
# Part 7. Serialization API
# ==========================================================

# ----------------------------------------------------------
# To Dict
# ----------------------------------------------------------

def to_dict(self) -> dict:
    """
    Serialize this registry into a dictionary.
    """

    from ..serialization.metric_registry_serializer import (
        MetricRegistrySerializer,
    )

    return MetricRegistrySerializer.to_dict(self)


# ----------------------------------------------------------
# From Dict
# ----------------------------------------------------------

@classmethod
def from_dict(
    cls,
    data: dict,
) -> "MetricRegistry":
    """
    Construct a registry from a dictionary.
    """

    from ..serialization.metric_registry_serializer import (
        MetricRegistrySerializer,
    )

    return MetricRegistrySerializer.from_dict(data)


# ----------------------------------------------------------
# To JSON
# ----------------------------------------------------------

def to_json(
    self,
    *,
    indent: int | None = 2,
) -> str:
    """
    Serialize this registry into JSON.
    """

    from ..serialization.metric_registry_serializer import (
        MetricRegistrySerializer,
    )

    return MetricRegistrySerializer.to_json(
        self,
        indent=indent,
    )


# ----------------------------------------------------------
# From JSON
# ----------------------------------------------------------

@classmethod
def from_json(
    cls,
    text: str,
) -> "MetricRegistry":
    """
    Construct registry from JSON.
    """

    from ..serialization.metric_registry_serializer import (
        MetricRegistrySerializer,
    )

    return MetricRegistrySerializer.from_json(text)


# ----------------------------------------------------------
# Save
# ----------------------------------------------------------

def save(
    self,
    path: str,
) -> None:
    """
    Save registry to disk.
    """

    from ..serialization.metric_registry_serializer import (
        MetricRegistrySerializer,
    )

    MetricRegistrySerializer.save(
        self,
        path,
    )


# ----------------------------------------------------------
# Load
# ----------------------------------------------------------

@classmethod
def load(
    cls,
    path: str,
) -> "MetricRegistry":
    """
    Load registry from disk.
    """

    from ..serialization.metric_registry_serializer import (
        MetricRegistrySerializer,
    )

    return MetricRegistrySerializer.load(path)
# ==========================================================
# Part 8. Rich API
# ==========================================================

# ----------------------------------------------------------
# repr()
# ----------------------------------------------------------

def __repr__(self) -> str:
    """
    Developer representation.
    """

    return (
        f"{self.__class__.__name__}("
        f"name={self._name!r}, "
        f"size={len(self)}, "
        f"healthy={self.health!r})"
    )


# ----------------------------------------------------------
# str()
# ----------------------------------------------------------

def __str__(self) -> str:
    """
    Human-readable representation.
    """

    return (
        f"{self.__class__.__name__}"
        f"({len(self)} metrics)"
    )


# ----------------------------------------------------------
# Equality
# ----------------------------------------------------------

def __eq__(
    self,
    other: object,
) -> bool:

    if not isinstance(other, MetricRegistry):
        return NotImplemented

    return self._metrics == other._metrics


# ----------------------------------------------------------
# Hash
# ----------------------------------------------------------

def __hash__(self) -> int:
    """
    Hash by registry name.

    Registry is mutable, therefore we hash
    only its logical identity.
    """

    return hash(self._name)


# ----------------------------------------------------------
# Bool
# ----------------------------------------------------------

def __bool__(self) -> bool:
    """
    True if registry contains metrics.
    """

    return bool(self._metrics)


# ----------------------------------------------------------
# Iterator
# ----------------------------------------------------------

def __iter__(self):
    """
    Iterate over Metric objects.
    """

    return iter(self._metrics.values())


# ----------------------------------------------------------
# Reversed
# ----------------------------------------------------------

def __reversed__(self):
    """
    Iterate in reverse registration order.
    """

    return reversed(tuple(self._metrics.values()))


# ----------------------------------------------------------
# Length
# ----------------------------------------------------------

def __len__(self) -> int:
    """
    Number of registered metrics.
    """

    return len(self._metrics)


# ----------------------------------------------------------
# Contains
# ----------------------------------------------------------

def __contains__(
    self,
    item,
) -> bool:
    """
    Support:

        metric in registry

        "runtime.cpu" in registry
    """

    if isinstance(item, Metric):
        return self.contains_metric(item)

    if isinstance(item, str):
        return self.contains(item)

    return False


# ----------------------------------------------------------
# Get Item
# ----------------------------------------------------------

def __getitem__(
    self,
    key: str,
) -> Metric:
    """
    registry["runtime.cpu"]
    """

    return self.require(key)


# ----------------------------------------------------------
# Set Item
# ----------------------------------------------------------

def __setitem__(
    self,
    key: str,
    metric: Metric,
) -> None:
    """
    registry["runtime.cpu"] = metric
    """

    self.register(
        metric,
        replace=True,
    )


# ----------------------------------------------------------
# Delete Item
# ----------------------------------------------------------

def __delitem__(
    self,
    key: str,
) -> None:
    """
    del registry["runtime.cpu"]
    """

    self.remove(key)
# ==========================================================
# Part 9. Debug Helpers
# ==========================================================

# ----------------------------------------------------------
# Size
# ----------------------------------------------------------

@property
def size(self) -> int:
    """
    Number of registered metrics.
    """

    return len(self._metrics)


# ----------------------------------------------------------
# Is Empty
# ----------------------------------------------------------

@property
def is_empty(self) -> bool:
    """
    True if registry contains no metrics.
    """

    return not self._metrics


# ----------------------------------------------------------
# Metric Names
# ----------------------------------------------------------

@property
def metric_names(self) -> tuple[str, ...]:
    """
    Return all registered metric names.
    """

    return tuple(
        metric.name
        for metric in self._metrics.values()
    )


# ----------------------------------------------------------
# Namespaces
# ----------------------------------------------------------

@property
def namespaces(self) -> tuple[str, ...]:
    """
    Return all unique namespaces.
    """

    return tuple(
        sorted(
            {
                metric.namespace
                for metric in self._metrics.values()
            }
        )
    )


# ----------------------------------------------------------
# State
# ----------------------------------------------------------

@property
def state(self) -> dict[str, object]:
    """
    Registry runtime state.
    """

    return {
        "name": self._name,
        "size": self.size,
        "empty": self.is_empty,
    }


# ----------------------------------------------------------
# Statistics
# ----------------------------------------------------------

@property
def statistics(self) -> dict[str, object]:
    """
    Registry statistics.
    """

    by_type: dict[str, int] = {}

    for metric in self._metrics.values():

        metric_type = metric.metric_type

        by_type[metric_type] = (
            by_type.get(metric_type, 0) + 1
        )

    return {
        "metrics": self.size,
        "namespaces": len(self.namespaces),
        "types": by_type,
    }


# ----------------------------------------------------------
# Health
# ----------------------------------------------------------

@property
def health(self) -> str:
    """
    Overall registry health.
    """

    if self.is_empty:
        return "empty"

    unhealthy = sum(
        metric.health != "healthy"
        for metric in self._metrics.values()
    )

    if unhealthy == 0:
        return "healthy"

    if unhealthy == self.size:
        return "critical"

    return "degraded"


# ----------------------------------------------------------
# Summary
# ----------------------------------------------------------

@property
def summary(self) -> dict[str, object]:
    """
    Human-readable registry summary.
    """

    return {
        "name": self._name,
        "metrics": self.size,
        "namespaces": self.namespaces,
        "health": self.health,
    }


# ----------------------------------------------------------
# Dump
# ----------------------------------------------------------

def dump(self) -> dict[str, object]:
    """
    Complete diagnostic dump.
    """

    return {
        "state": self.state,
        "statistics": self.statistics,
        "summary": self.summary,
        "metrics": {
            key: metric.summary
            for key, metric in self._metrics.items()
        },
    }
# ==========================================================
# Part 10. Thread Safety
# ==========================================================

# ----------------------------------------------------------
# Lock
# ----------------------------------------------------------

@property
def lock(self) -> RLock:
    """
    Return the registry lock.
    """

    return self._lock


# ----------------------------------------------------------
# Acquire
# ----------------------------------------------------------

def acquire(
    self,
    blocking: bool = True,
    timeout: float = -1,
) -> bool:
    """
    Acquire the registry lock.

    Parameters
    ----------
    blocking:
        Whether to block until the lock is acquired.

    timeout:
        Maximum time to wait. Ignored if blocking=False.
    """

    return self._lock.acquire(
        blocking=blocking,
        timeout=timeout,
    )


# ----------------------------------------------------------
# Release
# ----------------------------------------------------------

def release(self) -> None:
    """
    Release the registry lock.
    """

    self._lock.release()


# ----------------------------------------------------------
# Locked
# ----------------------------------------------------------

@property
def locked(self) -> bool:
    """
    Best-effort indication whether the registry lock
    is currently held.

    Note
    ----
    The standard threading.RLock does not expose a
    public 'locked()' method on all Python versions.
    """

    return getattr(self._lock, "_is_owned", lambda: False)()


# ----------------------------------------------------------
# Context Manager
# ----------------------------------------------------------

def __enter__(self) -> "MetricRegistry":
    """
    Acquire the registry lock and return self.
    """

    self.acquire()

    return self


def __exit__(
    self,
    exc_type,
    exc,
    tb,
) -> bool:
    """
    Release the registry lock.
    """

    self.release()

    return False


# ----------------------------------------------------------
# Synchronized
# ----------------------------------------------------------

def synchronized(self, func, *args, **kwargs):
    """
    Execute a callable while holding the registry lock.
    """

    with self:
        return func(*args, **kwargs)                                             
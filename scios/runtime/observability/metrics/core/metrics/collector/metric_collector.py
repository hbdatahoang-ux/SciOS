# ==========================================================
# Part 1. Foundation
# ==========================================================

from __future__ import annotations

from threading import RLock
from time import time
from typing import Final

from ..registry.metric_registry import MetricRegistry

__all__ = [
    "MetricCollector",
]


class MetricCollector:
    """
    Thread-safe Metric collector.

    The collector gathers runtime values from a MetricRegistry.
    It does not own metrics and does not export them.
    """

    DEFAULT_NAME: Final[str] = "collector"

    # ----------------------------------------------------------
    # Constructor
    # ----------------------------------------------------------

    def __init__(
        self,
        registry: MetricRegistry,
        *,
        name: str = DEFAULT_NAME,
    ) -> None:

        self._name = name

        #
        # Registry reference
        #
        self._registry = registry

        #
        # Collection state
        #
        self._enabled = True
        self._timestamp = 0.0
        self._collection_count = 0
        self._last_duration = 0.0

        #
        # Thread safety
        #
        self._lock = RLock()

    # ----------------------------------------------------------
    # Basic Properties
    # ----------------------------------------------------------

    @property
    def name(self) -> str:
        """Collector name."""
        return self._name

    @property
    def registry(self) -> MetricRegistry:
        """Associated MetricRegistry."""
        return self._registry

    @property
    def enabled(self) -> bool:
        """Whether the collector is enabled."""
        return self._enabled

    @property
    def timestamp(self) -> float:
        """Timestamp of the last collection."""
        return self._timestamp

    @property
    def collection_count(self) -> int:
        """Number of completed collections."""
        return self._collection_count

    @property
    def last_duration(self) -> float:
        """Duration (seconds) of the last collection."""
        return self._last_duration

    @property
    def lock(self) -> RLock:
        """Collector lock."""
        return self._lock

    # ----------------------------------------------------------
    # Internal Helper
    # ----------------------------------------------------------

    def _begin_collection(self) -> float:
        """
        Record the start time of a collection cycle.
        """
        return time()

    def _end_collection(
        self,
        started_at: float,
    ) -> None:
        """
        Finalize collection statistics.
        """
        self._timestamp = time()
        self._last_duration = self._timestamp - started_at
        self._collection_count += 1
# ==========================================================
# Part 2. Collection API
# ==========================================================

# ----------------------------------------------------------
# Collect One
# ----------------------------------------------------------

def collect_one(
    self,
    key: str,
) -> dict[str, object] | None:
    """
    Collect a single metric by registry key.
    """

    with self._lock:

        if not self._enabled:
            return None

        metric = self._registry.get(key)

        if metric is None:
            return None

        started_at = self._begin_collection()

        sample = {
            "key": key,
            "timestamp": metric.state.timestamp,
            "value": metric.get(),
            "unit": metric.unit,
            "type": metric.metric_type,
            "labels": metric.labels.to_dict(),
            "attributes": metric.attributes.to_dict(),
        }

        self._end_collection(started_at)

        return sample


# ----------------------------------------------------------
# Collect
# ----------------------------------------------------------

def collect(self) -> tuple[dict[str, object], ...]:
    """
    Collect all registered metrics.
    """

    with self._lock:

        if not self._enabled:
            return ()

        started_at = self._begin_collection()

        samples = tuple(
            self.collect_one(key)
            for key in self._registry.keys()
        )

        self._end_collection(started_at)

        return tuple(
            sample
            for sample in samples
            if sample is not None
        )


# ----------------------------------------------------------
# Collect Many
# ----------------------------------------------------------

def collect_many(
    self,
    keys: list[str] | tuple[str, ...],
) -> tuple[dict[str, object], ...]:
    """
    Collect multiple metrics.
    """

    with self._lock:

        if not self._enabled:
            return ()

        started_at = self._begin_collection()

        samples = tuple(
            self.collect_one(key)
            for key in keys
        )

        self._end_collection(started_at)

        return tuple(
            sample
            for sample in samples
            if sample is not None
        )


# ----------------------------------------------------------
# Collect Namespace
# ----------------------------------------------------------

def collect_namespace(
    self,
    namespace: str,
) -> tuple[dict[str, object], ...]:
    """
    Collect metrics from one namespace.
    """

    with self._lock:

        if not self._enabled:
            return ()

        started_at = self._begin_collection()

        samples = []

        for metric in self._registry.by_namespace(namespace):

            samples.append(
                {
                    "key": self._registry.make_key(metric),
                    "timestamp": metric.state.timestamp,
                    "value": metric.get(),
                    "unit": metric.unit,
                    "type": metric.metric_type,
                    "labels": metric.labels.to_dict(),
                    "attributes": metric.attributes.to_dict(),
                }
            )

        self._end_collection(started_at)

        return tuple(samples)


# ----------------------------------------------------------
# Collect Type
# ----------------------------------------------------------

def collect_type(
    self,
    metric_type: str,
) -> tuple[dict[str, object], ...]:
    """
    Collect metrics by metric type.
    """

    with self._lock:

        if not self._enabled:
            return ()

        started_at = self._begin_collection()

        samples = []

        for metric in self._registry.by_type(metric_type):

            samples.append(
                {
                    "key": self._registry.make_key(metric),
                    "timestamp": metric.state.timestamp,
                    "value": metric.get(),
                    "unit": metric.unit,
                    "type": metric.metric_type,
                    "labels": metric.labels.to_dict(),
                    "attributes": metric.attributes.to_dict(),
                }
            )

        self._end_collection(started_at)

        return tuple(samples)
# ==========================================================
# Part 3. Query Collection
# ==========================================================

# ----------------------------------------------------------
# Collect By Label
# ----------------------------------------------------------

def by_label(
    self,
    key: str,
    value: str | None = None,
) -> tuple[dict[str, object], ...]:
    """
    Collect metrics matching a label.
    """

    with self._lock:

        if not self._enabled:
            return ()

        started_at = self._begin_collection()

        samples = tuple(
            self._collect_metric(
                self._registry.make_key(metric),
                metric,
            )
            for metric in self._registry.by_label(key, value)
        )

        self._end_collection(started_at)

        return samples


# ----------------------------------------------------------
# Collect By Attribute
# ----------------------------------------------------------

def by_attribute(
    self,
    key: str,
    value: object | None = None,
) -> tuple[dict[str, object], ...]:
    """
    Collect metrics matching an attribute.
    """

    with self._lock:

        if not self._enabled:
            return ()

        started_at = self._begin_collection()

        samples = tuple(
            self._collect_metric(
                self._registry.make_key(metric),
                metric,
            )
            for metric in self._registry.by_attribute(key, value)
        )

        self._end_collection(started_at)

        return samples


# ----------------------------------------------------------
# Collect By Predicate
# ----------------------------------------------------------

def filter(
    self,
    predicate,
) -> tuple[dict[str, object], ...]:
    """
    Collect metrics matching a predicate.
    """

    with self._lock:

        if not self._enabled:
            return ()

        started_at = self._begin_collection()

        samples = tuple(
            self._collect_metric(
                self._registry.make_key(metric),
                metric,
            )
            for metric in self._registry.filter(predicate)
        )

        self._end_collection(started_at)

        return samples


# ----------------------------------------------------------
# Search
# ----------------------------------------------------------

def search(
    self,
    keyword: str,
) -> tuple[dict[str, object], ...]:
    """
    Collect metrics matching a keyword.
    """

    with self._lock:

        if not self._enabled:
            return ()

        started_at = self._begin_collection()

        samples = tuple(
            self._collect_metric(
                self._registry.make_key(metric),
                metric,
            )
            for metric in self._registry.search(keyword)
        )

        self._end_collection(started_at)

        return samples
# ==========================================================
# Part 4. Batch Collection
# ==========================================================

# ----------------------------------------------------------
# Collect All
# ----------------------------------------------------------

def collect_all(
    self,
) -> tuple[dict[str, object], ...]:
    """
    Collect all registered metrics.
    """

    return self.collect()


# ----------------------------------------------------------
# Collect Enabled
# ----------------------------------------------------------

def collect_enabled(
    self,
) -> tuple[dict[str, object], ...]:
    """
    Collect all enabled metrics.
    """

    with self._lock:

        if not self._enabled:
            return ()

        started_at = self._begin_collection()

        samples = self._collect_metrics(
            metric
            for metric in self._registry.values()
            if metric.state.enabled
        )

        self._end_collection(started_at)

        return samples


# ----------------------------------------------------------
# Collect Disabled
# ----------------------------------------------------------

def collect_disabled(
    self,
) -> tuple[dict[str, object], ...]:
    """
    Collect all disabled metrics.
    """

    with self._lock:

        if not self._enabled:
            return ()

        started_at = self._begin_collection()

        samples = self._collect_metrics(
            metric
            for metric in self._registry.values()
            if not metric.state.enabled
        )

        self._end_collection(started_at)

        return samples


# ----------------------------------------------------------
# Collect Changed
# ----------------------------------------------------------

def collect_changed(
    self,
) -> tuple[dict[str, object], ...]:
    """
    Collect metrics whose values have changed.
    """

    with self._lock:

        if not self._enabled:
            return ()

        started_at = self._begin_collection()

        samples = self._collect_metrics(
            metric
            for metric in self._registry.values()
            if metric.state.changed()
        )

        self._end_collection(started_at)

        return samples


# ----------------------------------------------------------
# Collect Healthy
# ----------------------------------------------------------

def collect_healthy(
    self,
) -> tuple[dict[str, object], ...]:
    """
    Collect healthy metrics.
    """

    with self._lock:

        if not self._enabled:
            return ()

        started_at = self._begin_collection()

        samples = self._collect_metrics(
            metric
            for metric in self._registry.values()
            if metric.health == "healthy"
        )

        self._end_collection(started_at)

        return samples


# ----------------------------------------------------------
# Collect Unhealthy
# ----------------------------------------------------------

def collect_unhealthy(
    self,
) -> tuple[dict[str, object], ...]:
    """
    Collect unhealthy metrics.
    """

    with self._lock:

        if not self._enabled:
            return ()

        started_at = self._begin_collection()

        samples = self._collect_metrics(
            metric
            for metric in self._registry.values()
            if metric.health != "healthy"
        )

        self._end_collection(started_at)

        return samples
# ==========================================================
# Part 5. Snapshot API
# ==========================================================

# ----------------------------------------------------------
# Snapshot
# ----------------------------------------------------------

def snapshot(self) -> dict[str, object]:
    """
    Create a snapshot of the collector state.
    """

    with self._lock:

        return {
            "name": self._name,
            "enabled": self._enabled,
            "timestamp": self._timestamp,
            "collection_count": self._collection_count,
            "last_duration": self._last_duration,
        }


# ----------------------------------------------------------
# Restore
# ----------------------------------------------------------

def restore(
    self,
    snapshot: dict[str, object],
) -> None:
    """
    Restore collector state.
    """

    with self._lock:

        self._name = snapshot.get(
            "name",
            self._name,
        )

        self._enabled = snapshot.get(
            "enabled",
            self._enabled,
        )

        self._timestamp = snapshot.get(
            "timestamp",
            self._timestamp,
        )

        self._collection_count = snapshot.get(
            "collection_count",
            self._collection_count,
        )

        self._last_duration = snapshot.get(
            "last_duration",
            self._last_duration,
        )


# ----------------------------------------------------------
# Clone
# ----------------------------------------------------------

def clone(self) -> "MetricCollector":
    """
    Create a clone of this collector.

    The cloned collector shares the same registry.
    """

    with self._lock:

        collector = self.__class__(
            registry=self._registry,
            name=self._name,
        )

        collector.restore(
            self.snapshot()
        )

        return collector


# ----------------------------------------------------------
# Copy
# ----------------------------------------------------------

def copy(self) -> "MetricCollector":
    """
    Alias of clone().
    """

    return self.clone()
# ==========================================================
# Part 6. Hook API
# ==========================================================

# ----------------------------------------------------------
# Register Hook
# ----------------------------------------------------------

def register_hook(
    self,
    event: str,
    callback,
) -> None:
    """
    Register a callback for a collector event.
    """

    with self._lock:

        if not hasattr(self, "_hooks"):
            self._hooks: dict[str, list] = {}

        self._hooks.setdefault(
            event,
            []
        ).append(callback)


# ----------------------------------------------------------
# Unregister Hook
# ----------------------------------------------------------

def unregister_hook(
    self,
    event: str,
    callback,
) -> None:
    """
    Remove a callback.
    """

    with self._lock:

        callbacks = self._hooks.get(event)

        if callbacks is None:
            return

        if callback in callbacks:
            callbacks.remove(callback)


# ----------------------------------------------------------
# Clear Hooks
# ----------------------------------------------------------

def clear_hooks(self) -> None:
    """
    Remove every registered hook.
    """

    with self._lock:

        self._hooks.clear()


# ----------------------------------------------------------
# Dispatch Hook
# ----------------------------------------------------------

def dispatch_hook(
    self,
    event: str,
    *args,
    **kwargs,
) -> None:
    """
    Dispatch an event.
    """

    callbacks = self._hooks.get(
        event,
        (),
    )

    for callback in callbacks:
        callback(*args, **kwargs)


# ----------------------------------------------------------
# Before Collection
# ----------------------------------------------------------

def _before_collection(self) -> None:
    """
    Internal hook.
    """

    self.dispatch_hook(
        "before_collection",
        self,
    )


# ----------------------------------------------------------
# After Collection
# ----------------------------------------------------------

def _after_collection(
    self,
    samples,
) -> None:
    """
    Internal hook.
    """

    self.dispatch_hook(
        "after_collection",
        self,
        samples,
    )


# ----------------------------------------------------------
# Collection Error
# ----------------------------------------------------------

def _on_collection_error(
    self,
    exception: Exception,
) -> None:
    """
    Internal hook.
    """

    self.dispatch_hook(
        "collection_error",
        self,
        exception,
    )
# ==========================================================
# Part 7. Serialization API
# ==========================================================

# ----------------------------------------------------------
# To Dict
# ----------------------------------------------------------

def to_dict(self) -> dict:
    """
    Serialize this collector into a dictionary.
    """

    from ..serialization.metric_collector_serializer import (
        MetricCollectorSerializer,
    )

    return MetricCollectorSerializer.to_dict(self)


# ----------------------------------------------------------
# From Dict
# ----------------------------------------------------------

@classmethod
def from_dict(
    cls,
    data: dict,
    registry,
) -> "MetricCollector":
    """
    Construct a collector from a dictionary.
    """

    from ..serialization.metric_collector_serializer import (
        MetricCollectorSerializer,
    )

    return MetricCollectorSerializer.from_dict(
        data,
        registry,
    )


# ----------------------------------------------------------
# To JSON
# ----------------------------------------------------------

def to_json(
    self,
    *,
    indent: int | None = 2,
) -> str:
    """
    Serialize this collector into JSON.
    """

    from ..serialization.metric_collector_serializer import (
        MetricCollectorSerializer,
    )

    return MetricCollectorSerializer.to_json(
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
    registry,
) -> "MetricCollector":
    """
    Construct a collector from JSON.
    """

    from ..serialization.metric_collector_serializer import (
        MetricCollectorSerializer,
    )

    return MetricCollectorSerializer.from_json(
        text,
        registry,
    )


# ----------------------------------------------------------
# Save
# ----------------------------------------------------------

def save(
    self,
    path: str,
) -> None:
    """
    Save collector to disk.
    """

    from ..serialization.metric_collector_serializer import (
        MetricCollectorSerializer,
    )

    MetricCollectorSerializer.save(
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
    registry,
) -> "MetricCollector":
    """
    Load collector from disk.
    """

    from ..serialization.metric_collector_serializer import (
        MetricCollectorSerializer,
    )

    return MetricCollectorSerializer.load(
        path,
        registry,
    )
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
        f"enabled={self._enabled}, "
        f"metrics={len(self)}, "
        f"collections={self._collection_count})"
    )


# ----------------------------------------------------------
# str()
# ----------------------------------------------------------

def __str__(self) -> str:
    """
    Human-readable representation.
    """

    status = "enabled" if self._enabled else "disabled"

    return (
        f"{self.__class__.__name__}"
        f"({status}, {len(self)} metrics)"
    )


# ----------------------------------------------------------
# Equality
# ----------------------------------------------------------

def __eq__(
    self,
    other: object,
) -> bool:
    """
    Compare collectors.
    """

    if not isinstance(other, MetricCollector):
        return NotImplemented

    return (
        self._name == other._name
        and self._registry is other._registry
    )


# ----------------------------------------------------------
# Hash
# ----------------------------------------------------------

def __hash__(self) -> int:
    """
    Hash by collector identity.
    """

    return hash(
        (
            self._name,
            id(self._registry),
        )
    )


# ----------------------------------------------------------
# Bool
# ----------------------------------------------------------

def __bool__(self) -> bool:
    """
    True if collector is enabled.
    """

    return self._enabled


# ----------------------------------------------------------
# Iterator
# ----------------------------------------------------------

def __iter__(self):
    """
    Iterate over registered metrics.
    """

    return iter(self._registry)


# ----------------------------------------------------------
# Reversed
# ----------------------------------------------------------

def __reversed__(self):
    """
    Reverse iterator over registered metrics.
    """

    return reversed(tuple(self._registry))


# ----------------------------------------------------------
# Length
# ----------------------------------------------------------

def __len__(self) -> int:
    """
    Number of metrics in the registry.
    """

    return len(self._registry)


# ----------------------------------------------------------
# Contains
# ----------------------------------------------------------

def __contains__(
    self,
    item,
) -> bool:
    """
    Membership test.

    Supports Metric instances and registry keys.
    """

    return item in self._registry


# ----------------------------------------------------------
# Get Item
# ----------------------------------------------------------

def __getitem__(
    self,
    key: str,
):
    """
    Return a metric by registry key.
    """

    return self._registry[key]
# ==========================================================
# Part 9. Debug Helpers
# ==========================================================

# ----------------------------------------------------------
# State
# ----------------------------------------------------------

@property
def state(self) -> dict[str, object]:
    """
    Return current collector runtime state.
    """

    return {
        "name": self._name,
        "enabled": self._enabled,
        "timestamp": self._timestamp,
        "collection_count": self._collection_count,
        "last_duration": self._last_duration,
    }


# ----------------------------------------------------------
# Age
# ----------------------------------------------------------

@property
def age(self) -> float | None:
    """
    Return seconds since last collection.

    Returns
    -------
    float | None

    None means collector has never collected.
    """

    if self._timestamp == 0:
        return None

    return time() - self._timestamp


# ----------------------------------------------------------
# Is Empty
# ----------------------------------------------------------

@property
def is_empty(self) -> bool:
    """
    True if collector has no metrics available.
    """

    return len(self._registry) == 0


# ----------------------------------------------------------
# Statistics
# ----------------------------------------------------------

@property
def statistics(self) -> dict[str, object]:
    """
    Collection statistics.
    """

    return {
        "collections": self._collection_count,
        "last_duration": self._last_duration,
        "last_timestamp": self._timestamp,
        "metric_count": len(self._registry),
    }


# ----------------------------------------------------------
# Health
# ----------------------------------------------------------

@property
def health(self) -> str:
    """
    Collector health status.
    """

    if not self._enabled:
        return "disabled"

    if self.is_empty:
        return "empty"

    if self._timestamp == 0:
        return "idle"

    #
    # Collector has collected successfully
    #
    return "healthy"


# ----------------------------------------------------------
# Summary
# ----------------------------------------------------------

@property
def summary(self) -> dict[str, object]:
    """
    Human readable summary.
    """

    return {
        "name": self._name,
        "health": self.health,
        "metrics": len(self),
        "collections": self._collection_count,
    }


# ----------------------------------------------------------
# Dump
# ----------------------------------------------------------

def dump(self) -> dict[str, object]:
    """
    Full diagnostic dump.
    """

    return {
        "state": self.state,
        "statistics": self.statistics,
        "summary": self.summary,
        "registry": self._registry.state,
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
    Return collector lock.
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
    Acquire collector lock.
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
    Release collector lock.
    """

    self._lock.release()


# ----------------------------------------------------------
# Locked
# ----------------------------------------------------------

@property
def locked(self) -> bool:
    """
    Best-effort lock status.

    Used for debugging only.
    """

    checker = getattr(
        self._lock,
        "_is_owned",
        None,
    )

    if checker is None:
        return False

    return checker()


# ----------------------------------------------------------
# Context Manager
# ----------------------------------------------------------

def __enter__(self) -> "MetricCollector":
    """
    Acquire collector lock.
    """

    self.acquire()

    return self


def __exit__(
    self,
    exc_type,
    exc,
    traceback,
) -> bool:
    """
    Release collector lock.
    """

    self.release()

    return False


# ----------------------------------------------------------
# Execute Locked
# ----------------------------------------------------------

def synchronized(
    self,
    func,
    *args,
    **kwargs,
):
    """
    Execute a function under collector lock.
    """

    with self:
        return func(
            *args,
            **kwargs,
        )


# ----------------------------------------------------------
# Enable Thread Safe
# ----------------------------------------------------------

def enable(self) -> None:
    """
    Enable collector safely.
    """

    with self._lock:
        self._enabled = True


# ----------------------------------------------------------
# Disable Thread Safe
# ----------------------------------------------------------

def disable(self) -> None:
    """
    Disable collector safely.
    """

    with self._lock:
        self._enabled = False


# ----------------------------------------------------------
# Is Enabled
# ----------------------------------------------------------

def is_enabled(self) -> bool:
    """
    Thread-safe enabled check.
    """

    with self._lock:
        return self._enabled                                                    
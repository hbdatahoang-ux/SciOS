"""
SciOS-NG Metrics Collector
==========================

Runtime metric collection and metric-container layer.

Responsibilities
-----------------
- Register and manage runtime metrics.
- Collect metric observations.
- Manage metric sources.
- Snapshot and restore metric state.
- Reset and clear metrics.
- Merge collectors.
- Provide thread-safe container semantics.

Python 3.11+
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from time import perf_counter
from typing import Any, Callable, Iterator

from .registry import MetricRegistry


__all__ = [
    "MetricCollector",
]


# ==========================================================
# Collector State
# ==========================================================


@dataclass
class CollectorState:
    """Runtime state of the collector."""

    started_at: float = field(
        default_factory=perf_counter
    )

    collections: int = 0

    active: bool = False


# ==========================================================
# Metric Collector
# ==========================================================


class MetricCollector:
    """
    Runtime metric collector.

    The collector acts as a façade over :class:`MetricRegistry`
    while also providing runtime collection APIs.
    """

    def __init__(
        self,
        registry: MetricRegistry | None = None,
    ) -> None:

        self.registry = (
            registry
            if registry is not None
            else MetricRegistry()
        )

        self.state = CollectorState()

        self._sources: list[
            Callable[[], dict[str, Any]]
        ] = []

    # ==========================================================
    # Lifecycle
    # ==========================================================

    def start(self) -> None:
        """Start the collector."""
        self.state.active = True

    def stop(self) -> None:
        """Stop the collector."""
        self.state.active = False

    @property
    def running(self) -> bool:
        """Whether the collector is running."""
        return self.state.active

    # ==========================================================
    # Registration
    # ==========================================================

    def register(self, metric: Any) -> Any:
        """Register a metric."""
        return self.registry.register(metric)

    def replace(self, metric: Any) -> Any:
        """Replace an existing metric."""
        return self.registry.replace(metric)

    def remove(self, name: str) -> Any | bool:
        """Remove a metric by name."""
        return self.registry.remove(name)

    def unregister(self, name: str) -> Any | bool:
        """Alias for :meth:`remove`."""
        return self.remove(name)

    # ==========================================================
    # Lookup
    # ==========================================================

    def get(
        self,
        name: str,
        default: Any = None,
    ) -> Any:
        """Return a metric by name."""
        return self.registry.get(name, default)

    def exists(self, name: str) -> bool:
        """Return whether a metric exists."""
        return self.registry.exists(name)

    @property
    def empty(self) -> bool:
        """Whether no metrics are registered."""
        return len(self) == 0

    # ==========================================================
    # Source Management
    # ==========================================================

    def register_source(
        self,
        source: Callable[[], dict[str, Any]],
    ) -> None:
        """Register a runtime metric source."""

        if not callable(source):
            raise TypeError(
                "source must be callable"
            )

        self._sources.append(source)

    def unregister_source(
        self,
        source: Callable[[], dict[str, Any]],
    ) -> None:
        """Remove a registered metric source."""

        if source in self._sources:
            self._sources.remove(source)

    # ==========================================================
    # Collection API
    # ==========================================================

    def collect(
        self,
        name: str,
        value: Any,
        metric_type: str = "gauge",
        **labels: Any,
    ) -> Any:
        """
        Record an observation.

        If the metric already exists, its value is updated using
        the metric's native API where available.

        Otherwise a compatible metric is created through the
        registry when possible.
        """

        metric = self.get(name)

        if metric is None:
            from .counter import Counter
            from .gauge import Gauge
            from .histogram import Histogram

            metric_type_normalized = (
                metric_type.lower()
            )

            if metric_type_normalized == "counter":
                metric = Counter(
                    name,
                    **labels,
                )

            elif metric_type_normalized == "histogram":
                metric = Histogram(
                    name,
                    **labels,
                )

            else:
                metric = Gauge(
                    name,
                    **labels,
                )

            self.register(metric)

        if metric_type.lower() == "counter":
            updater = getattr(metric, "inc", None)

            if callable(updater):
                updater(value)

        elif metric_type.lower() == "histogram":
            updater = getattr(metric, "observe", None)

            if callable(updater):
                updater(value)

        else:
            updater = getattr(metric, "set", None)

            if callable(updater):
                updater(value)

        self.state.collections += 1

        return metric

    def collect_many(
        self,
        metrics: list[dict[str, Any]],
    ) -> list[Any]:
        """Collect multiple observations."""

        if not isinstance(metrics, list):
            raise TypeError(
                "metrics must be a list"
            )

        return [
            self.collect(**item)
            for item in metrics
        ]

    def collect_sources(self) -> list[Any]:
        """Collect metrics from all registered sources."""

        results: list[Any] = []

        for source in tuple(self._sources):
            data = source()

            if not data:
                continue

            if not isinstance(data, dict):
                raise TypeError(
                    "metric source must return a dictionary"
                )

            for name, value in data.items():
                results.append(
                    self.collect(
                        name,
                        value,
                    )
                )

        return results

    # ==========================================================
    # Snapshot
    # ==========================================================

    def snapshot(self) -> dict[str, Any]:
        """
        Return a metric snapshot.

        Runtime lifecycle state intentionally does not appear
        in this API. This keeps snapshot semantics compatible
        with the metric-container contract.
        """

        return self.registry.snapshot()

    # ==========================================================
    # Restore
    # ==========================================================

    def restore(
        self,
        snapshot: dict[str, Any],
    ) -> None:
        """
        Restore metric state from a snapshot.
        """

        self.registry.restore(snapshot)

    # ==========================================================
    # Reset
    # ==========================================================

    def reset(self) -> None:
        """
        Reset all metrics and collector runtime count.
        """

        self.registry.reset()

        self.state.collections = 0

    # ==========================================================
    # Clear
    # ==========================================================

    def clear(self) -> None:
        """Remove all registered metrics."""

        self.registry.clear()

        self.state.collections = 0

    # ==========================================================
    # Merge
    # ==========================================================

    def merge(
        self,
        other: "MetricCollector",
    ) -> "MetricCollector":
        """
        Merge another collector into this collector.

        Existing metrics are left untouched. Missing metrics are
        copied into this collector.
        """

        if not isinstance(
            other,
            MetricCollector,
        ):
            raise TypeError(
                "other must be a MetricCollector"
            )

        for name, metric in other.registry.items():

            if name in self.registry:
                continue

            if hasattr(metric, "copy"):
                merged_metric = metric.copy()
            else:
                merged_metric = deepcopy(metric)

            self.register(merged_metric)

        return self

    # ==========================================================
    # Report
    # ==========================================================

    def report(self) -> dict[str, Any]:
        """
        Return a metric report.

        This intentionally aliases snapshot() so metric state
        remains the canonical exported representation.
        """

        return self.snapshot()

    # ==========================================================
    # Container Protocols
    # ==========================================================

    def __len__(self) -> int:
        """
        Number of registered metrics.
        """

        return len(self.registry)

    def __bool__(self) -> bool:
        """Collector is truthy when it contains metrics."""
        return not self.empty

    def __iter__(self) -> Iterator[Any]:
        """
        Iterate over metric instances.
        """

        return iter(
            tuple(self.registry.values())
        )

    def __contains__(self, key: object) -> bool:
        """Return whether a metric name is registered."""
        return key in self.registry

    def __getitem__(self, key: str) -> Any:
        """Get metric by name."""
        return self.registry[key]

    def __setitem__(
        self,
        key: str,
        value: Any,
    ) -> None:
        """Register or replace metric under key."""

        if value is None:
            raise TypeError(
                "value cannot be None"
            )

        metric_name = getattr(
            value,
            "name",
            None,
        )

        if metric_name != key:
            raise ValueError(
                f"metric name {metric_name!r} "
                f"does not match key {key!r}"
            )

        if key in self.registry:
            self.registry.replace(value)
        else:
            self.registry.register(value)

    def __delitem__(self, key: str) -> None:
        """Remove metric by name."""

        result = self.registry.remove(key)

        if result is False:
            raise KeyError(key)

    # ==========================================================
    # Mapping Helpers
    # ==========================================================

    def keys(self) -> list[str]:
        """Return metric names."""
        return self.registry.names()

    def values(self) -> list[Any]:
        """Return metric instances."""
        return self.registry.values()

    def items(self) -> list[tuple[str, Any]]:
        """Return metric items."""
        return self.registry.items()

    def metrics(self) -> list[Any]:
        """Return metrics as a list."""
        return self.registry.values()

    # ==========================================================
    # Representation
    # ==========================================================

    def __repr__(self) -> str:
        names = self.keys()

        return (
            "MetricCollector("
            f"metrics={len(self)}, "
            f"names={names!r}, "
            f"collections={self.state.collections}, "
            f"sources={len(self._sources)}"
            ")"
        )
"""
SciOS-NG Metrics Aggregator
===========================

Metric registry and aggregation engine.

Responsibilities
-----------------
- Register runtime metrics.
- Reject duplicate metric registration.
- Remove metrics.
- Iterate over registered metrics.
- Lookup metrics by name.
- Reset registered metrics.
- Create and restore snapshots.
- Calculate total metric value.
- Export metric state.
- Provide thread-safe runtime access.

Python 3.11+
"""

from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from typing import Any, Iterator

from .metric import Metric


__all__ = [
    "AggregationState",
    "MetricAggregator",
    "Aggregator",
]


# ==========================================================
# Aggregation State
# ==========================================================


@dataclass
class AggregationState:
    """
    Runtime state of the metric aggregator.
    """

    samples: int = 0
    metrics: int = 0


# ==========================================================
# Metric Aggregator
# ==========================================================


class MetricAggregator:
    """
    Thread-safe runtime metric registry.

    The aggregator owns registered Metric objects rather than
    storing detached raw values.

    Example
    -------

        aggregator = MetricAggregator()

        counter = Counter("requests")

        aggregator.add(counter)

        counter.inc(5)

        aggregator.total()
    """

    # ======================================================
    # Initialization
    # ======================================================

    def __init__(self) -> None:

        self.state = AggregationState()

        self._metrics: dict[str, Metric] = {}

        self._lock = RLock()

    # ======================================================
    # Registration
    # ======================================================

    def add(
        self,
        metric: Metric,
    ) -> None:
        """
        Register a metric.

        Duplicate metric names are rejected.

        Parameters
        ----------
        metric:
            Metric instance to register.
        """

        if not isinstance(metric, Metric):
            raise TypeError(
                "metric must be an instance of Metric"
            )

        with self._lock:

            if metric.name in self._metrics:
                raise ValueError(
                    f"metric already registered: {metric.name!r}"
                )

            self._metrics[metric.name] = metric

            self.state.metrics = len(
                self._metrics
            )

            self.state.samples += 1

    # ======================================================
    # Removal
    # ======================================================

    def remove(
        self,
        metric: Metric,
    ) -> None:
        """
        Remove a registered metric.

        Unknown metrics are ignored.
        """

        if not isinstance(metric, Metric):
            return

        with self._lock:

            current = self._metrics.get(
                metric.name
            )

            if current is metric:

                del self._metrics[
                    metric.name
                ]

            self.state.metrics = len(
                self._metrics
            )

    # ======================================================
    # Clear
    # ======================================================

    def clear(
        self,
    ) -> None:
        """
        Remove all registered metrics.

        Unlike ``reset()``, this does not modify the
        metric objects themselves.
        """

        with self._lock:

            self._metrics.clear()

            self.state = AggregationState()

    # ======================================================
    # Lookup
    # ======================================================

    def get(
        self,
        name: str,
    ) -> Metric | None:
        """
        Return a registered metric by name.
        """

        with self._lock:

            return self._metrics.get(
                name
            )

    def __getitem__(
        self,
        name: str,
    ) -> Metric:
        """
        Lookup a metric by name.

        Raises
        ------
        KeyError
            If the metric is not registered.
        """

        with self._lock:

            return self._metrics[name]

    # ======================================================
    # Iteration
    # ======================================================

    def __iter__(
        self,
    ) -> Iterator[Metric]:
        """
        Iterate over registered metrics.

        A snapshot of the registry is used so iteration is
        safe against concurrent registry mutation.
        """

        with self._lock:

            metrics = tuple(
                self._metrics.values()
            )

        return iter(metrics)

    # ======================================================
    # Membership
    # ======================================================

    def __contains__(
        self,
        item: object,
    ) -> bool:
        """
        Check whether a metric or metric name is registered.
        """

        with self._lock:

            if isinstance(item, Metric):

                return (
                    self._metrics.get(
                        item.name
                    )
                    is item
                )

            if isinstance(item, str):

                return item in self._metrics

            return False

    # ======================================================
    # Names
    # ======================================================

    def names(
        self,
    ) -> list[str]:
        """
        Return registered metric names.
        """

        with self._lock:

            return list(
                self._metrics.keys()
            )

    # ======================================================
    # Value Extraction
    # ======================================================

    @staticmethod
    def _value(
        metric: Metric,
    ) -> float:
        """
        Extract the numeric value from a metric.

        Supports both the current property-based API and
        legacy callable ``value()`` implementations.
        """

        value = getattr(
            metric,
            "value",
            0.0,
        )

        if callable(value):
            value = value()

        return float(value)

    # ======================================================
    # Total
    # ======================================================

    def total(
        self,
    ) -> float:
        """
        Return the sum of all registered metric values.
        """

        with self._lock:

            return sum(
                self._value(metric)
                for metric in self._metrics.values()
            )

    # ======================================================
    # Snapshot
    # ======================================================

    def snapshot(
        self,
    ) -> dict[str, Any]:
        """
        Create a registry snapshot.

        Snapshot format:

            {
                "requests": {
                    ...
                },
                "cpu": {
                    ...
                }
            }
        """

        with self._lock:

            snapshot: dict[str, Any] = {}

            for name, metric in self._metrics.items():

                if hasattr(metric, "snapshot"):

                    data = metric.snapshot()

                elif hasattr(metric, "to_dict"):

                    data = metric.to_dict()

                else:

                    data = {
                        "name": name,
                        "value": self._value(metric),
                    }

                if hasattr(data, "to_dict"):

                    data = data.to_dict()

                elif not isinstance(data, dict):

                    data = {
                        "name": name,
                        "value": data,
                    }

                snapshot[name] = dict(data)

            return snapshot

    # ======================================================
    # Restore
    # ======================================================

    def restore(
        self,
        snapshot: dict[str, Any],
    ) -> None:
        """
        Restore registered metrics from a snapshot.

        Only metrics already registered with the aggregator
        are restored. Unknown snapshot entries are ignored.
        """

        if not isinstance(snapshot, dict):
            raise TypeError(
                "snapshot must be a dictionary"
            )

        with self._lock:

            for name, data in snapshot.items():

                metric = self._metrics.get(
                    name
                )

                if metric is None:
                    continue

                if isinstance(data, dict):

                    value = data.get(
                        "value"
                    )

                else:

                    value = data

                if value is None:
                    continue

                value = float(value)

                if hasattr(metric, "set"):

                    metric.set(value)

                elif hasattr(metric, "update"):

                    metric.update(value)

                elif hasattr(metric, "_value"):

                    metric._value = value

    # ======================================================
    # Reset
    # ======================================================

    def reset(
        self,
    ) -> None:
        """
        Reset all registered metrics.

        The registry itself remains intact.
        """

        with self._lock:

            for metric in self._metrics.values():

                reset = getattr(
                    metric,
                    "reset",
                    None,
                )

                if callable(reset):

                    reset()

                elif hasattr(metric, "_value"):

                    metric._value = 0.0

            self.state.samples = 0

    # ======================================================
    # Export
    # ======================================================

    def export(
        self,
    ) -> dict[str, Any]:
        """
        Export all registered metrics.

        Returns an empty dictionary when no metrics exist.
        """

        with self._lock:

            if not self._metrics:
                return {}

            data: dict[str, Any] = {}

            for name, metric in self._metrics.items():

                if hasattr(metric, "to_dict"):

                    value = metric.to_dict()

                elif hasattr(metric, "snapshot"):

                    value = metric.snapshot()

                else:

                    value = {
                        "name": name,
                        "value": self._value(metric),
                    }

                if hasattr(value, "to_dict"):

                    value = value.to_dict()

                data[name] = dict(value)

            return data

    # ======================================================
    # Report
    # ======================================================

    def report(
        self,
    ) -> dict[str, Any]:
        """
        Alias for ``snapshot()``.
        """

        return self.snapshot()

    # ======================================================
    # Length
    # ======================================================

    def __len__(
        self,
    ) -> int:
        """
        Return number of registered metrics.
        """

        with self._lock:

            return len(
                self._metrics
            )

    # ======================================================
    # Boolean
    # ======================================================

    def __bool__(
        self,
    ) -> bool:
        """
        Return True when at least one metric is registered.
        """

        return len(self) > 0

    # ======================================================
    # Representation
    # ======================================================

    def __repr__(
        self,
    ) -> str:

        return (
            "MetricAggregator("
            f"metrics={len(self._metrics)}, "
            f"samples={self.state.samples}"
            ")"
        )


# ==========================================================
# Backward-Compatible Public API
# ==========================================================

Aggregator = MetricAggregator
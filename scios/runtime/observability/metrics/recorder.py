"""
SciOS Runtime Metrics Recorder
==============================

Recorder coordinates metric instances with the central metric registry.

Responsibilities
-----------------
- Register metric instances.
- Record existing Counter, Gauge, and Histogram metrics.
- Support batch recording.
- Support labels through metric instances.
- Provide snapshot / restore.
- Support reset.
- Provide thread-safe recording and snapshot operations.

Python 3.11+
"""

from __future__ import annotations

from dataclasses import dataclass, field
from threading import RLock
from time import perf_counter
from typing import Any, Iterable

from .metric import Metric
from .registry import MetricRegistry


__all__ = [
    "Recorder",
    "MetricRecorder",
    "RecorderState",
]


# ==========================================================
# Recorder State
# ==========================================================


@dataclass
class RecorderState:
    """
    Internal recorder state.

    ``elapsed`` stores the accumulated elapsed time represented
    by the current recorder checkpoint.

    ``started_at`` is the monotonic reference point used while
    the recorder is running normally.
    """

    total_records: int = 0

    started_at: float = field(
        default_factory=perf_counter
    )

    elapsed: float = 0.0


# ==========================================================
# Metric Recorder
# ==========================================================


class Recorder:
    """
    Runtime metric recorder.

    The recorder works primarily with metric instances rather than
    replacing them with implicit values.

    Examples
    --------

    >>> registry = MetricRegistry()
    >>> recorder = Recorder(registry)

    >>> counter = Counter("requests")
    >>> counter.inc()
    >>> recorder.record(counter)

    >>> recorder.record_all([counter])
    """

    # ======================================================
    # Initialization
    # ======================================================

    def __init__(
        self,
        registry: MetricRegistry | None = None,
    ) -> None:
        """
        Create a recorder.

        Parameters
        ----------
        registry:
            Optional metric registry.
        """

        self.registry = (
            registry
            if registry is not None
            else MetricRegistry()
        )

        self.state = RecorderState()

        self._lock = RLock()

        # After restore(), elapsed becomes a checkpoint value.
        # New recording operations establish a new running baseline.
        self._restored = False

    # ======================================================
    # Internal Elapsed Handling
    # ======================================================

    def _current_elapsed(self) -> float:
        """
        Return current elapsed time.

        Caller must hold ``_lock``.
        """

        if self._restored:
            return float(
                self.state.elapsed
            )

        return (
            float(self.state.elapsed)
            +
            (
                perf_counter()
                -
                self.state.started_at
            )
        )

    # ======================================================
    # Record
    # ======================================================

    def record(
        self,
        metric: Metric,
    ) -> Metric:
        """
        Register an existing metric instance.

        Parameters
        ----------
        metric:
            Metric instance to record.

        Returns
        -------
        Metric
            The same metric instance.

        Raises
        ------
        TypeError
            If ``metric`` is not a ``Metric`` instance.
        """

        if not isinstance(
            metric,
            Metric,
        ):
            raise TypeError(
                "Recorder.record() expects a Metric instance"
            )

        with self._lock:

            self.registry.register(
                metric
            )

            self._record()

            return metric

    # ======================================================
    # Batch Recording
    # ======================================================

    def record_all(
        self,
        metrics: Iterable[Metric],
    ) -> list[Metric]:
        """
        Register multiple metric instances.
        """

        results: list[Metric] = []

        with self._lock:

            for metric in metrics:

                results.append(
                    self.record(
                        metric
                    )
                )

        return results

    # ======================================================
    # Counter API
    # ======================================================

    def increment(
        self,
        name: str,
        value: int | float = 1,
        **labels: Any,
    ) -> float:
        """
        Increment a counter metric.

        Creates the counter when necessary.
        """

        with self._lock:

            metric = self.registry.get(
                name
            )

            if metric is None:

                from .counter import Counter

                metric = Counter(
                    name,
                    labels=dict(labels),
                )

                self.registry.register(
                    metric
                )

            elif labels:

                metric.labels.update(
                    labels
                )

            metric.inc(
                value
            )

            self._record()

            return float(
                metric.value
            )

    # ======================================================
    # Gauge API
    # ======================================================

    def set(
        self,
        name: str,
        value: int | float,
        **labels: Any,
    ) -> float:
        """
        Set a gauge metric.

        Creates the gauge when necessary.
        """

        with self._lock:

            metric = self.registry.get(
                name
            )

            if metric is None:

                from .gauge import Gauge

                metric = Gauge(
                    name,
                    value=value,
                    labels=dict(labels),
                )

                self.registry.register(
                    metric
                )

                self._record()

                return float(
                    metric.value
                )

            if labels:

                metric.labels.update(
                    labels
                )

            result = metric.set(
                value
            )

            self._record()

            return float(
                result
            )

    # ======================================================
    # Histogram API
    # ======================================================

    def observe(
        self,
        name: str,
        value: int | float,
        **labels: Any,
    ) -> Any:
        """
        Record a histogram observation.

        Creates the histogram when necessary.
        """

        with self._lock:

            metric = self.registry.get(
                name
            )

            if metric is None:

                from .histogram import Histogram

                metric = Histogram(
                    name,
                    labels=dict(labels),
                )

                self.registry.register(
                    metric
                )

            elif labels:

                metric.labels.update(
                    labels
                )

            result = metric.observe(
                value
            )

            self._record()

            return result

    # ======================================================
    # Timing API
    # ======================================================

    def timing(
        self,
        name: str,
        duration: float,
        **labels: Any,
    ) -> Any:
        """
        Record a duration observation.
        """

        return self.observe(
            name,
            duration,
            **labels,
        )

    # ======================================================
    # Generic Convenience API
    # ======================================================

    def record_value(
        self,
        name: str,
        value: int | float,
        metric_type: str = "gauge",
        **labels: Any,
    ) -> Any:
        """
        Record a scalar value.

        ``record()`` remains reserved for actual Metric instances.
        """

        metric_type = str(
            metric_type
        ).lower()

        if metric_type == "counter":

            return self.increment(
                name,
                value,
                **labels,
            )

        if metric_type == "histogram":

            return self.observe(
                name,
                value,
                **labels,
            )

        if metric_type == "gauge":

            return self.set(
                name,
                value,
                **labels,
            )

        raise ValueError(
            f"Unsupported metric type: {metric_type!r}"
        )

    # ======================================================
    # Internal State
    # ======================================================

    def _record(
        self,
    ) -> None:
        """
        Increment recorder operation count.

        Caller must hold ``_lock``.
        """

        # A restored recorder starts a fresh running interval
        # when the first new operation occurs.
        if self._restored:

            self.state.started_at = perf_counter()

            self._restored = False

        self.state.total_records += 1

    # ======================================================
    # Snapshot
    # ======================================================

    def snapshot(
        self,
    ) -> dict[str, Any]:
        """
        Export recorder state.

        The returned object contains:

        - total record operations
        - accumulated elapsed time
        - registry metric snapshots
        """

        with self._lock:

            elapsed = self._current_elapsed()

            return {
                "total_records":
                    self.state.total_records,

                "elapsed":
                    elapsed,

                "registry":
                    self.registry.snapshot(),
            }

    # ======================================================
    # Restore
    # ======================================================

    def restore(
        self,
        snapshot: dict[str, Any],
    ) -> None:
        """
        Restore recorder state from a snapshot.

        Restore is deterministic:

            snap = recorder.snapshot()
            recorder.restore(snap)
            recorder.snapshot() == snap

        immediately after restore.

        Metric instances contained in the snapshot are also
        reconstructed into the registry.
        """

        if not isinstance(
            snapshot,
            dict,
        ):
            raise TypeError(
                "snapshot must be a dictionary"
            )

        with self._lock:

            total_records = int(
                snapshot.get(
                    "total_records",
                    0,
                )
            )

            elapsed = float(
                snapshot.get(
                    "elapsed",
                    0.0,
                )
            )

            self.state = RecorderState(
                total_records=total_records,
                elapsed=elapsed,
                started_at=perf_counter(),
            )

            self._restored = True

            # --------------------------------------------------
            # Restore registry
            # --------------------------------------------------

            registry_data = snapshot.get(
                "registry",
                {},
            )

            if not isinstance(
                registry_data,
                dict,
            ):
                registry_data = {}

            self.registry.clear()

            for data in registry_data.values():

                if not isinstance(
                    data,
                    dict,
                ):
                    continue

                metric = (
                    self._create_metric_from_snapshot(
                        data
                    )
                )

                if metric is not None:

                    self.registry.register(
                        metric
                    )

    # ======================================================
    # Metric Restore
    # ======================================================

    @staticmethod
    def _restore_metric(
        metric: Metric,
        data: dict[str, Any],
    ) -> None:
        """
        Restore a metric instance in place.
        """

        if not isinstance(
            data,
            dict,
        ):
            return

        # --------------------------------------------------
        # Counter / Gauge style metrics
        # --------------------------------------------------

        if "value" in data:

            value = data["value"]

            if hasattr(
                metric,
                "set",
            ):

                metric.set(
                    value
                )

                return

            if hasattr(
                metric,
                "_value",
            ):

                metric._value = float(
                    value
                )

                return

        # --------------------------------------------------
        # Histogram
        # --------------------------------------------------

        if "values" in data:

            if hasattr(
                metric,
                "reset",
            ):

                metric.reset()

            values = data.get(
                "values",
                [],
            )

            if not isinstance(
                values,
                list,
            ):
                return

            if hasattr(
                metric,
                "observe",
            ):

                for value in values:

                    metric.observe(
                        value
                    )

    # ======================================================
    # Metric Construction From Snapshot
    # ======================================================

    @staticmethod
    def _create_metric_from_snapshot(
        data: dict[str, Any],
    ) -> Metric | None:
        """
        Reconstruct a supported metric from serialized data.
        """

        if not isinstance(
            data,
            dict,
        ):
            return None

        metric_type = str(
            data.get(
                "type",
                data.get(
                    "metric_type",
                    "",
                ),
            )
        ).lower()

        name = data.get(
            "name"
        )

        if not isinstance(
            name,
            str,
        ):
            return None

        labels = data.get(
            "labels",
            {},
        )

        if not isinstance(
            labels,
            dict,
        ):
            labels = {}

        # --------------------------------------------------
        # Counter
        # --------------------------------------------------

        if metric_type == "counter":

            from .counter import Counter

            metric = Counter(
                name,
                labels=dict(labels),
            )

            if "value" in data:

                metric._value = float(
                    data["value"]
                )

            return metric

        # --------------------------------------------------
        # Gauge
        # --------------------------------------------------

        if metric_type == "gauge":

            from .gauge import Gauge

            return Gauge(
                name,
                value=float(
                    data.get(
                        "value",
                        0.0,
                    )
                ),
                labels=dict(labels),
            )

        # --------------------------------------------------
        # Histogram
        # --------------------------------------------------

        if metric_type == "histogram":

            from .histogram import Histogram

            metric = Histogram(
                name,
                labels=dict(labels),
            )

            values = data.get(
                "values",
                [],
            )

            if not isinstance(
                values,
                list,
            ):
                values = []

            for value in values:

                metric.observe(
                    value
                )

            return metric

        return None

    # ======================================================
    # Reset
    # ======================================================

    def reset(
        self,
    ) -> None:
        """
        Reset recorder state and all registered metrics.
        """

        with self._lock:

            self.registry.reset()

            self.state = RecorderState()

            self._restored = False

    # ======================================================
    # Clear
    # ======================================================

    def clear(
        self,
    ) -> None:
        """
        Remove all metrics and reset recorder state.
        """

        with self._lock:

            self.registry.clear()

            self.state = RecorderState()

            self._restored = False

    # ======================================================
    # Collection
    # ======================================================

    def get(
        self,
        name: str,
        default: Any = None,
    ) -> Any:
        """
        Get a metric from the registry.
        """

        with self._lock:

            return self.registry.get(
                name,
                default,
            )

    # ======================================================
    # Length
    # ======================================================

    def __len__(
        self,
    ) -> int:
        """
        Return number of recorded operations.
        """

        with self._lock:

            return self.state.total_records

    # ======================================================
    # Boolean
    # ======================================================

    def __bool__(
        self,
    ) -> bool:
        """
        Return whether at least one record operation occurred.
        """

        return len(self) > 0

    # ======================================================
    # Representation
    # ======================================================

    def __repr__(
        self,
    ) -> str:

        with self._lock:

            return (
                "Recorder("
                f"records={self.state.total_records}, "
                f"metrics={len(self.registry)}"
                ")"
            )

    def __str__(
        self,
    ) -> str:

        return repr(self)


# ==========================================================
# Backward Compatibility
# ==========================================================

MetricRecorder = Recorder
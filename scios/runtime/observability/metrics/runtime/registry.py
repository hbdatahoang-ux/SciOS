"""
SciOS-NG Observability
======================

Runtime Metric Registry

Part 1
------

Foundation

The MetricRegistry is the central runtime repository for all
metrics managed by the SciOS observability subsystem.

Responsibilities
----------------

- Register runtime metrics
- Lookup metrics
- Manage metric lifecycle
- Provide thread-safe access
- Support snapshots/exporters
"""

from __future__ import annotations

from collections.abc import Iterator
from threading import RLock
from typing import Any

from ..core.metric import Metric

__all__ = [
    "MetricRegistry",
]


# ==========================================================
# Metric Registry
# ==========================================================


class MetricRegistry:
    """
    Thread-safe runtime metric registry.

    The registry owns every runtime metric and provides
    fast lookup by metric name.

    Notes
    -----
    - Thread-safe
    - Ordered insertion
    - Runtime lifecycle aware
    """

    # ------------------------------------------------------
    # Constructor
    # ------------------------------------------------------

    def __init__(
        self,
    ) -> None:
        """
        Initialize an empty registry.
        """

        # --------------------------------------------------
        # Internal Storage
        # --------------------------------------------------

        self._metrics: dict[str, Metric] = {}

        # --------------------------------------------------
        # Runtime State
        # --------------------------------------------------

        self._enabled: bool = True

        self._frozen: bool = False

        self._closed: bool = False

        self._revision: int = 0

        # --------------------------------------------------
        # Thread Lock
        # --------------------------------------------------

        self._lock = RLock()

    # ------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------

    @property
    def lock(
        self,
    ) -> RLock:
        """
        Registry synchronization lock.
        """

        return self._lock

    @property
    def enabled(
        self,
    ) -> bool:
        """
        Registry enabled state.
        """

        return self._enabled

    @property
    def frozen(
        self,
    ) -> bool:
        """
        Registry frozen state.
        """

        return self._frozen

    @property
    def closed(
        self,
    ) -> bool:
        """
        Registry closed state.
        """

        return self._closed

    @property
    def revision(
        self,
    ) -> int:
        """
        Registry revision number.
        """

        return self._revision

    @property
    def storage(
        self,
    ) -> dict[str, Metric]:
        """
        Internal metric storage.

        Returns
        -------
        dict[str, Metric]
        """

        return self._metrics

    def _touch(
        self,
    ) -> None:
        """
        Advance runtime revision.
        """

        self._revision += 1

    def _ensure_open(
        self,
    ) -> None:
        """
        Ensure registry is open.
        """

        if self._closed:

            raise RuntimeError(
                "MetricRegistry is closed."
            )

    def _ensure_mutable(
        self,
    ) -> None:
        """
        Ensure registry is mutable.
        """

        self._ensure_open()

        if self._frozen:

            raise RuntimeError(
                "MetricRegistry is frozen."
            )
# ==========================================================
# Part 2. Registration
# ==========================================================

    def register(
        self,
        metric: Metric,
    ) -> Metric:
        """
        Register a metric.

        Parameters
        ----------
        metric
            Metric instance.

        Returns
        -------
        Metric
            Registered metric.

        Raises
        ------
        KeyError
            If a metric with the same name already exists.
        """

        self._ensure_mutable()

        self.validate_metric(metric)

        name = metric.name

        with self._lock:

            if name in self._metrics:

                raise KeyError(
                    f"Metric '{name}' is already registered."
                )

            self._metrics[name] = metric

            self._touch()

        return metric


    def unregister(
        self,
        name: str,
    ) -> Metric:
        """
        Remove a metric from the registry.

        Parameters
        ----------
        name
            Metric name.

        Returns
        -------
        Metric
            Removed metric.

        Raises
        ------
        KeyError
            If the metric does not exist.
        """

        self._ensure_mutable()

        self.validate_name(name)

        with self._lock:

            metric = self._metrics.pop(name)

            self._touch()

            return metric


    def replace(
        self,
        metric: Metric,
    ) -> Metric:
        """
        Replace an existing metric.

        If the metric does not exist, it is added.

        Parameters
        ----------
        metric
            Metric instance.

        Returns
        -------
        Metric
        """

        self._ensure_mutable()

        self.validate_metric(metric)

        with self._lock:

            self._metrics[metric.name] = metric

            self._touch()

        return metric


    def clear(
        self,
    ) -> None:
        """
        Remove every registered metric.
        """

        self._ensure_mutable()

        with self._lock:

            self._metrics.clear()

            self._touch()


    def exists(
        self,
        name: str,
    ) -> bool:
        """
        Check whether a metric exists.

        Parameters
        ----------
        name
            Metric name.

        Returns
        -------
        bool
        """

        self.validate_name(name)

        with self._lock:

            return name in self._metrics


    def register_many(
        self,
        metrics: list[Metric] | tuple[Metric, ...],
    ) -> None:
        """
        Register multiple metrics.

        Parameters
        ----------
        metrics
            Iterable of Metric objects.

        Raises
        ------
        KeyError
            If any metric name already exists.
        """

        self._ensure_mutable()

        with self._lock:

            for metric in metrics:

                self.validate_metric(metric)

                if metric.name in self._metrics:

                    raise KeyError(
                        f"Metric '{metric.name}' is already registered."
                    )

            for metric in metrics:

                self._metrics[metric.name] = metric

            self._touch()
# ==========================================================
# Part 3. Lookup
# ==========================================================

    def get(
        self,
        name: str,
        default: Metric | None = None,
    ) -> Metric | None:
        """
        Retrieve a metric by name.

        Parameters
        ----------
        name
            Metric name.

        default
            Value returned if the metric is not found.

        Returns
        -------
        Metric | None
        """

        self.validate_name(name)

        with self._lock:

            return self._metrics.get(
                name,
                default,
            )


    def get_or_create(
        self,
        name: str,
        factory: callable,
        *args,
        **kwargs,
    ) -> Metric:
        """
        Retrieve an existing metric or create one.

        Parameters
        ----------
        name
            Metric name.

        factory
            Callable returning a Metric instance.

        Returns
        -------
        Metric
        """

        self.validate_name(name)

        with self._lock:

            metric = self._metrics.get(name)

            if metric is not None:

                return metric

            metric = factory(
                *args,
                **kwargs,
            )

            self.validate_metric(metric)

            self._metrics[name] = metric

            self._touch()

            return metric


    def names(
        self,
    ) -> list[str]:
        """
        Return all metric names.

        Returns
        -------
        list[str]
        """

        with self._lock:

            return list(
                self._metrics.keys()
            )


    def metrics(
        self,
    ) -> list[Metric]:
        """
        Return all registered metrics.

        Returns
        -------
        list[Metric]
        """

        with self._lock:

            return list(
                self._metrics.values()
            )


    def items(
        self,
    ) -> list[tuple[str, Metric]]:
        """
        Return registry items.

        Returns
        -------
        list[tuple[str, Metric]]
        """

        with self._lock:

            return list(
                self._metrics.items()
            )


    def values(
        self,
    ) -> tuple[Metric, ...]:
        """
        Return all metrics as an immutable tuple.

        Returns
        -------
        tuple[Metric, ...]
        """

        with self._lock:

            return tuple(
                self._metrics.values()
            )


    def count(
        self,
    ) -> int:
        """
        Number of registered metrics.

        Returns
        -------
        int
        """

        with self._lock:

            return len(
                self._metrics
            )
# ==========================================================
# Part 4. Runtime Operations
# ==========================================================

    def snapshot(
        self,
    ) -> dict[str, Any]:
        """
        Create a registry snapshot.

        Returns
        -------
        dict[str, Any]
        """

        with self._lock:

            return {

                "revision": self._revision,

                "enabled": self._enabled,

                "frozen": self._frozen,

                "closed": self._closed,

                "metrics": {

                    name: metric.snapshot().to_dict()

                    for name, metric in self._metrics.items()

                },

            }


    def restore(
        self,
        snapshot: dict[str, Any],
    ) -> None:
        """
        Restore registry state from a snapshot.

        Parameters
        ----------
        snapshot
            Registry snapshot.
        """

        self._ensure_mutable()

        if not isinstance(snapshot, dict):

            raise TypeError(
                "Snapshot must be a dictionary."
            )

        with self._lock:

            metrics = snapshot.get(
                "metrics",
                {},
            )

            for name, metric in self._metrics.items():

                metric_snapshot = metrics.get(name)

                if metric_snapshot is None:

                    continue

                metric.restore(
                    metric.snapshot().__class__.from_dict(
                        metric_snapshot
                    )
                )

            self._revision = int(
                snapshot.get(
                    "revision",
                    self._revision,
                )
            )

            self._enabled = bool(
                snapshot.get(
                    "enabled",
                    self._enabled,
                )
            )

            self._frozen = bool(
                snapshot.get(
                    "frozen",
                    self._frozen,
                )
            )

            self._closed = bool(
                snapshot.get(
                    "closed",
                    self._closed,
                )
            )

            self._touch()


    def clone(
        self,
    ) -> "MetricRegistry":
        """
        Deep clone the registry.

        Returns
        -------
        MetricRegistry
        """

        registry = self.__class__()

        with self._lock:

            registry._enabled = self._enabled

            registry._frozen = self._frozen

            registry._closed = self._closed

            registry._revision = self._revision

            registry._metrics = {

                name: metric.clone()

                for name, metric in self._metrics.items()

            }

        return registry


    def copy(
        self,
    ) -> "MetricRegistry":
        """
        Alias of clone().

        Returns
        -------
        MetricRegistry
        """

        return self.clone()


    def reset(
        self,
    ) -> None:
        """
        Reset every registered metric.

        Metrics supporting reset() will be reset.

        Returns
        -------
        None
        """

        self._ensure_mutable()

        with self._lock:

            for metric in self._metrics.values():

                reset = getattr(
                    metric,
                    "reset",
                    None,
                )

                if callable(reset):

                    reset()

            self._touch()
# ==========================================================
# Part 5. Lifecycle
# ==========================================================

    def enable(
        self,
    ) -> None:
        """
        Enable the registry and all registered metrics.
        """

        self._ensure_open()

        with self._lock:

            self._enabled = True

            for metric in self._metrics.values():

                enable = getattr(
                    metric,
                    "enable",
                    None,
                )

                if callable(enable):

                    enable()

            self._touch()


    def disable(
        self,
    ) -> None:
        """
        Disable the registry and all registered metrics.
        """

        self._ensure_open()

        with self._lock:

            self._enabled = False

            for metric in self._metrics.values():

                disable = getattr(
                    metric,
                    "disable",
                    None,
                )

                if callable(disable):

                    disable()

            self._touch()


    def freeze(
        self,
    ) -> None:
        """
        Freeze the registry and every registered metric.
        """

        self._ensure_open()

        with self._lock:

            self._frozen = True

            for metric in self._metrics.values():

                freeze = getattr(
                    metric,
                    "freeze",
                    None,
                )

                if callable(freeze):

                    freeze()

            self._touch()


    def unfreeze(
        self,
    ) -> None:
        """
        Unfreeze the registry and every registered metric.
        """

        self._ensure_open()

        with self._lock:

            self._frozen = False

            for metric in self._metrics.values():

                unfreeze = getattr(
                    metric,
                    "unfreeze",
                    None,
                )

                if callable(unfreeze):

                    unfreeze()

            self._touch()


    def close(
        self,
    ) -> None:
        """
        Close the registry.

        All registered metrics are closed.
        """

        with self._lock:

            if self._closed:

                return

            for metric in self._metrics.values():

                close = getattr(
                    metric,
                    "close",
                    None,
                )

                if callable(close):

                    close()

            self._enabled = False

            self._closed = True

            self._touch()


    def reopen(
        self,
    ) -> None:
        """
        Reopen the registry.

        All registered metrics are reopened.
        """

        with self._lock:

            self._closed = False

            self._enabled = True

            self._frozen = False

            for metric in self._metrics.values():

                reopen = getattr(
                    metric,
                    "reopen",
                    None,
                )

                if callable(reopen):

                    reopen()

            self._touch()
# ==========================================================
# Part 6. Validation
# ==========================================================

    def validate(
        self,
    ) -> None:
        """
        Validate the registry.

        Raises
        ------
        ValueError
            If the registry contains invalid data.

        RuntimeError
            If the registry is internally inconsistent.
        """

        self.validate_registry()

        with self._lock:

            for name, metric in self._metrics.items():

                self.validate_name(name)

                self.validate_metric(metric)

                validate = getattr(
                    metric,
                    "validate",
                    None,
                )

                if callable(validate):

                    validate()


    def validate_name(
        self,
        name: str,
    ) -> None:
        """
        Validate a metric name.

        Parameters
        ----------
        name
            Metric name.

        Raises
        ------
        TypeError
            If the name is not a string.

        ValueError
            If the name is empty.
        """

        if not isinstance(name, str):

            raise TypeError(
                "Metric name must be a string."
            )

        if not name.strip():

            raise ValueError(
                "Metric name cannot be empty."
            )


    def validate_metric(
        self,
        metric: Metric,
    ) -> None:
        """
        Validate a Metric object.

        Parameters
        ----------
        metric
            Metric instance.

        Raises
        ------
        TypeError
            If the object is not a Metric.
        """

        if not isinstance(metric, Metric):

            raise TypeError(
                "Expected a Metric instance."
            )

        self.validate_name(
            metric.name,
        )


    def validate_registry(
        self,
    ) -> None:
        """
        Validate the internal registry state.

        Raises
        ------
        RuntimeError
            If the registry state is inconsistent.
        """

        if not isinstance(
            self._metrics,
            dict,
        ):

            raise RuntimeError(
                "Registry storage must be a dictionary."
            )

        if self._revision < 0:

            raise RuntimeError(
                "Registry revision cannot be negative."
            )

        if self._closed and self._enabled:

            raise RuntimeError(
                "A closed registry cannot be enabled."
            )

        names: set[str] = set()

        for name, metric in self._metrics.items():

            if name in names:

                raise RuntimeError(
                    f"Duplicate metric name: '{name}'."
                )

            names.add(name)

            if metric.name != name:

                raise RuntimeError(
                    f"Registry key '{name}' "
                    f"does not match metric name "
                    f"'{metric.name}'."
                )
# ==========================================================
# Part 7. Diagnostics
# ==========================================================

    def statistics(
        self,
    ) -> dict[str, Any]:
        """
        Return registry statistics.

        Returns
        -------
        dict[str, Any]
        """

        with self._lock:

            metric_types: dict[str, int] = {}

            for metric in self._metrics.values():

                metric_type = getattr(
                    metric,
                    "metric_type",
                    metric.__class__.__name__.lower(),
                )

                metric_types[metric_type] = (

                    metric_types.get(metric_type, 0) + 1

                )

            return {

                "count": len(self._metrics),

                "revision": self._revision,

                "enabled": self._enabled,

                "frozen": self._frozen,

                "closed": self._closed,

                "metric_types": metric_types,

                "names": list(self._metrics.keys()),

            }


    def health(
        self,
    ) -> dict[str, Any]:
        """
        Return registry health information.

        Returns
        -------
        dict[str, Any]
        """

        try:

            self.validate()

            status = "healthy"

            valid = True

            error = None

        except Exception as exc:

            status = "unhealthy"

            valid = False

            error = str(exc)

        return {

            "status": status,

            "valid": valid,

            "error": error,

            "enabled": self._enabled,

            "frozen": self._frozen,

            "closed": self._closed,

            "revision": self._revision,

            "metric_count": len(self._metrics),

        }


    def dump(
        self,
    ) -> dict[str, Any]:
        """
        Dump the complete registry state.

        Returns
        -------
        dict[str, Any]
        """

        with self._lock:

            return {

                "statistics": self.statistics(),

                "health": self.health(),

                "metrics": {

                    name: metric.to_dict()

                    for name, metric in self._metrics.items()

                },

            }


    def inspect(
        self,
    ) -> dict[str, Any]:
        """
        Inspect the registry.

        Returns
        -------
        dict[str, Any]
        """

        with self._lock:

            return {

                "type": self.__class__.__name__,

                "state": {

                    "enabled": self._enabled,

                    "frozen": self._frozen,

                    "closed": self._closed,

                    "revision": self._revision,

                },

                "statistics": self.statistics(),

                "health": self.health(),

                "registered_metrics": [

                    {

                        "name": name,

                        "type": getattr(

                            metric,

                            "metric_type",

                            metric.__class__.__name__,

                        ),

                    }

                    for name, metric

                    in self._metrics.items()

                ],

            }
# ==========================================================
# Part 8. Serialization
# ==========================================================

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Serialize the registry.

        Returns
        -------
        dict[str, Any]
        """

        with self._lock:

            return {

                "revision": self._revision,

                "enabled": self._enabled,

                "frozen": self._frozen,

                "closed": self._closed,

                "metrics": {

                    name: metric.to_dict()

                    for name, metric

                    in self._metrics.items()

                },

            }


    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "MetricRegistry":
        """
        Deserialize a registry.

        Parameters
        ----------
        data
            Serialized registry.

        Returns
        -------
        MetricRegistry
        """

        if not isinstance(data, dict):

            raise TypeError(
                "Expected a dictionary."
            )

        registry = cls()

        registry._revision = int(
            data.get(
                "revision",
                0,
            )
        )

        registry._enabled = bool(
            data.get(
                "enabled",
                True,
            )
        )

        registry._frozen = bool(
            data.get(
                "frozen",
                False,
            )
        )

        registry._closed = bool(
            data.get(
                "closed",
                False,
            )
        )

        metrics = data.get(
            "metrics",
            {},
        )

        for payload in metrics.values():

            metric_type = payload.get(
                "metric_type",
                "",
            ).lower()

            if metric_type == "counter":

                from ..core.counter import Counter

                metric = Counter.from_dict(payload)

            elif metric_type == "gauge":

                from ..core.gauge import Gauge

                metric = Gauge.from_dict(payload)

            elif metric_type == "histogram":

                from ..core.histogram import Histogram

                metric = Histogram.from_dict(payload)

            elif metric_type == "summary":

                from ..core.summary import Summary

                metric = Summary.from_dict(payload)

            elif metric_type == "timer":

                from ..core.timer import Timer

                metric = Timer.from_dict(payload)

            else:

                continue

            registry._metrics[
                metric.name
            ] = metric

        return registry


    def to_json(
        self,
        *,
        indent: int | None = 2,
    ) -> str:
        """
        Serialize the registry to JSON.

        Parameters
        ----------
        indent
            JSON indentation.

        Returns
        -------
        str
        """

        import json

        return json.dumps(

            self.to_dict(),

            indent=indent,

            ensure_ascii=False,

            default=str,

        )


    @classmethod
    def from_json(
        cls,
        payload: str,
    ) -> "MetricRegistry":
        """
        Deserialize a registry from JSON.

        Parameters
        ----------
        payload
            JSON string.

        Returns
        -------
        MetricRegistry
        """

        import json

        return cls.from_dict(

            json.loads(payload)

        )
# ==========================================================
# Part 9. Export
# ==========================================================

    def prometheus(
        self,
    ) -> str:
        """
        Export all registered metrics in Prometheus format.

        Returns
        -------
        str
        """

        with self._lock:

            lines: list[str] = []

            for metric in self._metrics.values():

                exporter = getattr(
                    metric,
                    "prometheus",
                    None,
                )

                if callable(exporter):

                    lines.append(
                        exporter()
                    )

            return "\n".join(lines)


    def otel(
        self,
    ) -> list[dict[str, Any]]:
        """
        Export all registered metrics in an
        OpenTelemetry-friendly format.

        Returns
        -------
        list[dict[str, Any]]
        """

        with self._lock:

            exports: list[dict[str, Any]] = []

            for metric in self._metrics.values():

                exporter = getattr(
                    metric,
                    "otel",
                    None,
                )

                if callable(exporter):

                    exports.append(
                        exporter()
                    )

            return exports


    def csv(
        self,
        *,
        include_header: bool = True,
    ) -> str:
        """
        Export all metrics as CSV.

        Parameters
        ----------
        include_header
            Include CSV header.

        Returns
        -------
        str
        """

        with self._lock:

            rows: list[str] = []

            if include_header:

                rows.append(
                    "name,type,value"
                )

            for metric in self._metrics.values():

                exporter = getattr(
                    metric,
                    "csv",
                    None,
                )

                if callable(exporter):

                    rows.append(
                        exporter()
                    )

            return "\n".join(rows)


    def snapshots(
        self,
    ) -> dict[str, Any]:
        """
        Export snapshots of every registered metric.

        Returns
        -------
        dict[str, Any]
        """

        with self._lock:

            return {

                name: metric.snapshot()

                for name, metric

                in self._metrics.items()

            }
# ==========================================================
# Part 10. Python Protocols
# ==========================================================

    def __getitem__(
        self,
        name: str,
    ) -> Metric:
        """
        Retrieve a metric by name.

        Parameters
        ----------
        name
            Metric name.

        Returns
        -------
        Metric

        Raises
        ------
        KeyError
            If the metric does not exist.
        """

        with self._lock:

            return self._metrics[name]


    def __contains__(
        self,
        name: object,
    ) -> bool:
        """
        Check whether a metric exists.

        Returns
        -------
        bool
        """

        if not isinstance(name, str):

            return False

        with self._lock:

            return name in self._metrics


    def __iter__(
        self,
    ) -> Iterator[Metric]:
        """
        Iterate over registered metrics.

        Returns
        -------
        Iterator[Metric]
        """

        with self._lock:

            return iter(
                tuple(
                    self._metrics.values()
                )
            )


    def __len__(
        self,
    ) -> int:
        """
        Number of registered metrics.

        Returns
        -------
        int
        """

        with self._lock:

            return len(
                self._metrics
            )


    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.

        Returns
        -------
        str
        """

        return (

            f"{self.__class__.__name__}("

            f"count={len(self)}, "

            f"revision={self._revision}, "

            f"enabled={self._enabled}, "

            f"frozen={self._frozen}, "

            f"closed={self._closed})"

        )


    def __str__(
        self,
    ) -> str:
        """
        Human-readable representation.

        Returns
        -------
        str
        """

        return (

            f"MetricRegistry("

            f"{len(self)} metrics)"

        )


    # ======================================================
    # Compatibility
    # ======================================================

    @property
    def size(
        self,
    ) -> int:
        """
        Compatibility alias for count().

        Returns
        -------
        int
        """

        return self.count()


    @property
    def empty(
        self,
    ) -> bool:
        """
        Whether the registry is empty.

        Returns
        -------
        bool
        """

        return len(self) == 0


    def keys(
        self,
    ) -> list[str]:
        """
        Compatibility alias for names().

        Returns
        -------
        list[str]
        """

        return self.names()


    def export(
        self,
        format: str = "dict",
    ) -> Any:
        """
        Generic export interface.

        Parameters
        ----------
        format
            Supported formats:

            - dict
            - json
            - prometheus
            - otel
            - csv

        Returns
        -------
        Any
        """

        format = format.lower()

        exporters = {

            "dict": self.to_dict,

            "json": self.to_json,

            "prometheus": self.prometheus,

            "otel": self.otel,

            "csv": self.csv,

        }

        try:

            return exporters[format]()

        except KeyError:

            raise ValueError(

                f"Unsupported export format: "

                f"{format!r}"

            ) from None                                                                                                            
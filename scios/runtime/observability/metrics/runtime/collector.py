"""
SciOS-NG Observability
======================

Runtime Metric Collector

Part 1
------

Foundation

MetricCollector is responsible for collecting runtime
metric states from MetricRegistry.

Responsibilities
----------------

- Read metric states
- Produce runtime snapshots
- Coordinate collection lifecycle
- Provide thread-safe access
"""

from __future__ import annotations

from threading import RLock
from typing import Any

from .registry import MetricRegistry

__all__ = [
    "MetricCollector",
]


# ==========================================================
# Metric Collector
# ==========================================================


class MetricCollector:
    """
    Thread-safe runtime metric collector.

    The collector reads metrics from a MetricRegistry and
    produces observability data.
    """

    # ------------------------------------------------------
    # Constructor
    # ------------------------------------------------------

    def __init__(
        self,
        registry: MetricRegistry,
    ) -> None:
        """
        Initialize MetricCollector.

        Parameters
        ----------
        registry
            Runtime metric registry.
        """

        if not isinstance(
            registry,
            MetricRegistry,
        ):

            raise TypeError(
                "registry must be a MetricRegistry."
            )

        # --------------------------------------------------
        # Registry
        # --------------------------------------------------

        self._registry = registry

        # --------------------------------------------------
        # Runtime State
        # --------------------------------------------------

        self._enabled: bool = True

        self._frozen: bool = False

        self._closed: bool = False

        self._running: bool = False

        self._revision: int = 0

        self._collections: int = 0

        # --------------------------------------------------
        # Thread Lock
        # --------------------------------------------------

        self._lock = RLock()


    # ------------------------------------------------------
    # Properties
    # ------------------------------------------------------

    @property
    def registry(
        self,
    ) -> MetricRegistry:
        """
        Attached metric registry.
        """

        return self._registry


    @property
    def enabled(
        self,
    ) -> bool:
        """
        Collector enabled state.
        """

        return self._enabled


    @property
    def frozen(
        self,
    ) -> bool:
        """
        Collector frozen state.
        """

        return self._frozen


    @property
    def closed(
        self,
    ) -> bool:
        """
        Collector closed state.
        """

        return self._closed


    @property
    def running(
        self,
    ) -> bool:
        """
        Collector running state.
        """

        return self._running


    @property
    def revision(
        self,
    ) -> int:
        """
        Collector revision.
        """

        return self._revision


    @property
    def collections(
        self,
    ) -> int:
        """
        Number of collection cycles.
        """

        return self._collections


    @property
    def lock(
        self,
    ) -> RLock:
        """
        Runtime synchronization lock.
        """

        return self._lock


    # ------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------

    def _touch(
        self,
    ) -> None:
        """
        Increase collector revision.
        """

        self._revision += 1


    def _record_collection(
        self,
    ) -> None:
        """
        Record successful collection.
        """

        self._collections += 1

        self._touch()


    def _ensure_open(
        self,
    ) -> None:
        """
        Ensure collector is open.
        """

        if self._closed:

            raise RuntimeError(
                "MetricCollector is closed."
            )


    def _ensure_collectable(
        self,
    ) -> None:
        """
        Ensure collector can collect data.
        """

        self._ensure_open()

        if not self._enabled:

            raise RuntimeError(
                "MetricCollector is disabled."
            )

        if self._frozen:

            raise RuntimeError(
                "MetricCollector is frozen."
            )
# ==========================================================
# Part 2. Collection API
# ==========================================================

    def collect(
        self,
        name: str,
    ) -> dict[str, Any]:
        """
        Collect a single metric.

        Parameters
        ----------
        name
            Metric name.

        Returns
        -------
        dict[str, Any]
        """

        self._ensure_collectable()

        with self._lock:

            metric = self._registry.get(name)

            if metric is None:

                raise KeyError(
                    f"Unknown metric: '{name}'."
                )

            result = self.collect_metric(
                metric
            )

            self._record_collection()

            return result


    def collect_metric(
        self,
        metric: Any,
    ) -> dict[str, Any]:
        """
        Collect data from one metric instance.

        Parameters
        ----------
        metric
            Metric object.

        Returns
        -------
        dict[str, Any]
        """

        if metric is None:

            raise ValueError(
                "Metric cannot be None."
            )

        with self._lock:

            snapshot = getattr(
                metric,
                "snapshot",
                None,
            )

            if callable(snapshot):

                value = snapshot()

            else:

                value = getattr(
                    metric,
                    "value",
                    None,
                )

            data = {

                "name": getattr(
                    metric,
                    "name",
                    metric.__class__.__name__,
                ),

                "type": metric.__class__.__name__,

                "value": value,

            }

            statistics = getattr(
                metric,
                "statistics",
                None,
            )

            if callable(statistics):

                data["statistics"] = statistics()

            return data


    def collect_all(
        self,
    ) -> dict[str, dict[str, Any]]:
        """
        Collect all registered metrics.

        Returns
        -------
        dict[str, dict[str, Any]]
        """

        self._ensure_collectable()

        with self._lock:

            result = {}

            for name, metric in self._registry.items():

                result[name] = self.collect_metric(
                    metric
                )

            self._record_collection()

            return result


    def collect_runtime(
        self,
    ) -> dict[str, Any]:
        """
        Collect collector runtime information.

        Returns
        -------
        dict[str, Any]
        """

        self._ensure_open()

        with self._lock:

            return {

                "collector": self.__class__.__name__,

                "enabled": self._enabled,

                "frozen": self._frozen,

                "closed": self._closed,

                "running": self._running,

                "revision": self._revision,

                "collections": self._collections,

                "metrics": self._registry.count(),

            }


    def snapshot(
        self,
    ) -> dict[str, Any]:
        """
        Create a collector snapshot.

        Returns
        -------
        dict[str, Any]
        """

        self._ensure_open()

        with self._lock:

            return {

                "runtime": self.collect_runtime(),

                "metrics": self.collect_all(),

            }


    def batch(
        self,
        names: list[str] | None = None,
    ) -> dict[str, dict[str, Any]]:
        """
        Collect a batch of metrics.

        Parameters
        ----------
        names
            Optional metric names.

        Returns
        -------
        dict[str, dict[str, Any]]
        """

        self._ensure_collectable()

        with self._lock:

            if names is None:

                return self.collect_all()

            result = {}

            for name in names:

                result[name] = self.collect(
                    name
                )

            return result


    def reset(
        self,
    ) -> None:
        """
        Reset collector counters.

        Does not remove metrics.

        Returns
        -------
        None
        """

        self._ensure_open()

        with self._lock:

            self._collections = 0

            self._touch()
# ==========================================================
# Part 3. Lookup
# ==========================================================

    def get_metric(
        self,
        name: str,
    ) -> Any:
        """
        Retrieve a metric from registry.

        Parameters
        ----------
        name
            Metric name.

        Returns
        -------
        Metric
        """

        self._ensure_open()

        with self._lock:

            metric = self._registry.get(
                name
            )

            if metric is None:

                raise KeyError(
                    f"Unknown metric: '{name}'."
                )

            return metric


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

        self._ensure_open()

        with self._lock:

            return self._registry.exists(
                name
            )


    def names(
        self,
    ) -> list[str]:
        """
        Return registered metric names.

        Returns
        -------
        list[str]
        """

        self._ensure_open()

        with self._lock:

            return self._registry.names()


    def metrics(
        self,
    ) -> list[Any]:
        """
        Return all registered metrics.

        Returns
        -------
        list[Any]
        """

        self._ensure_open()

        with self._lock:

            return self._registry.metrics()


    def count(
        self,
    ) -> int:
        """
        Return number of registered metrics.

        Returns
        -------
        int
        """

        self._ensure_open()

        with self._lock:

            return self._registry.count()
# ==========================================================
# Part 4. Runtime Operations
# ==========================================================

    def start(
        self,
    ) -> None:
        """
        Start the collector.

        Enables active collection mode.

        Returns
        -------
        None
        """

        self._ensure_open()

        with self._lock:

            if self._running:

                return

            self._running = True

            self._touch()


    def stop(
        self,
    ) -> None:
        """
        Stop the collector.

        Disables active collection mode.

        Returns
        -------
        None
        """

        self._ensure_open()

        with self._lock:

            if not self._running:

                return

            self._running = False

            self._touch()


    def pause(
        self,
    ) -> None:
        """
        Pause collection temporarily.

        The collector remains initialized,
        but collection operations are blocked.

        Returns
        -------
        None
        """

        self._ensure_open()

        with self._lock:

            self._frozen = True

            self._running = False

            self._touch()


    def resume(
        self,
    ) -> None:
        """
        Resume collection after pause.

        Returns
        -------
        None
        """

        self._ensure_open()

        with self._lock:

            self._frozen = False

            self._running = True

            self._touch()


    def clone(
        self,
    ) -> "MetricCollector":
        """
        Create a cloned collector.

        The registry is cloned so the new collector
        owns an independent runtime state.

        Returns
        -------
        MetricCollector
        """

        with self._lock:

            collector = self.__class__(

                registry=self._registry.clone(),

            )

            collector._enabled = self._enabled

            collector._frozen = self._frozen

            collector._closed = self._closed

            collector._running = self._running

            collector._revision = self._revision

            collector._collections = self._collections

            return collector


    def copy(
        self,
    ) -> "MetricCollector":
        """
        Copy collector.

        Alias for clone().

        Returns
        -------
        MetricCollector
        """

        return self.clone()
# ==========================================================
# Part 5. Lifecycle
# ==========================================================

    def enable(
        self,
    ) -> None:
        """
        Enable collector.

        Allows collection operations.

        Returns
        -------
        None
        """

        self._ensure_open()

        with self._lock:

            self._enabled = True

            self._touch()


    def disable(
        self,
    ) -> None:
        """
        Disable collector.

        Collection operations are blocked.

        Returns
        -------
        None
        """

        self._ensure_open()

        with self._lock:

            self._enabled = False

            self._touch()


    def freeze(
        self,
    ) -> None:
        """
        Freeze collector.

        Frozen collector keeps state but refuses
        collection changes.

        Returns
        -------
        None
        """

        self._ensure_open()

        with self._lock:

            self._frozen = True

            self._running = False

            self._touch()


    def unfreeze(
        self,
    ) -> None:
        """
        Unfreeze collector.

        Returns
        -------
        None
        """

        self._ensure_open()

        with self._lock:

            self._frozen = False

            self._touch()


    def close(
        self,
    ) -> None:
        """
        Close collector permanently.

        A closed collector cannot collect data
        until reopened.

        Returns
        -------
        None
        """

        with self._lock:

            if self._closed:

                return

            self._enabled = False

            self._running = False

            self._closed = True

            self._touch()


    def reopen(
        self,
    ) -> None:
        """
        Reopen collector.

        Restores collector into active state.

        Returns
        -------
        None
        """

        with self._lock:

            self._closed = False

            self._enabled = True

            self._frozen = False

            self._running = False

            self._touch()
# ==========================================================
# Part 6. Validation
# ==========================================================

    def validate(
        self,
    ) -> None:
        """
        Validate collector state.

        Raises
        ------
        RuntimeError
            If collector state is inconsistent.
        """

        self.validate_state()

        self._registry.validate()

        for metric in self._registry.metrics():

            self.validate_metric(
                metric
            )


    def validate_metric(
        self,
        metric: Any,
    ) -> None:
        """
        Validate a metric object.

        Parameters
        ----------
        metric
            Metric instance.

        Raises
        ------
        TypeError
            If metric is invalid.
        """

        if metric is None:

            raise TypeError(
                "Metric cannot be None."
            )

        if not hasattr(
            metric,
            "name",
        ):

            raise TypeError(
                "Metric must have a name."
            )

        validate = getattr(
            metric,
            "validate",
            None,
        )

        if callable(validate):

            validate()


    def validate_collection(
        self,
        collection: Any,
    ) -> None:
        """
        Validate collected data.

        Parameters
        ----------
        collection
            Collection result.

        Raises
        ------
        TypeError
            If collection format is invalid.
        """

        if collection is None:

            raise TypeError(
                "Collection result cannot be None."
            )

        if not isinstance(
            collection,
            dict,
        ):

            raise TypeError(
                "Collection result must be a dictionary."
            )

        for name, data in collection.items():

            if not isinstance(
                name,
                str,
            ):

                raise TypeError(
                    "Metric name must be a string."
                )

            if data is None:

                raise ValueError(
                    f"Invalid collection data for '{name}'."
                )


    def validate_state(
        self,
    ) -> None:
        """
        Validate collector runtime state.

        Raises
        ------
        RuntimeError
            If state is inconsistent.
        """

        if self._revision < 0:

            raise RuntimeError(
                "Revision cannot be negative."
            )


        if self._collections < 0:

            raise RuntimeError(
                "Collection count cannot be negative."
            )


        if self._closed:

            if self._enabled:

                raise RuntimeError(
                    "Closed collector cannot be enabled."
                )

            if self._running:

                raise RuntimeError(
                    "Closed collector cannot be running."
                )


        if self._frozen and self._running:

            raise RuntimeError(
                "Frozen collector cannot be running."
            )
# ==========================================================
# Part 7. Diagnostics
# ==========================================================

    def statistics(
        self,
    ) -> dict[str, Any]:
        """
        Return collector statistics.

        Returns
        -------
        dict[str, Any]
        """

        with self._lock:

            registry_stats = (
                self._registry.statistics()
            )

            return {

                "collections": self._collections,

                "revision": self._revision,

                "enabled": self._enabled,

                "running": self._running,

                "frozen": self._frozen,

                "closed": self._closed,

                "metric_count": (
                    self._registry.count()
                ),

                "registry": registry_stats,

            }


    def health(
        self,
    ) -> dict[str, Any]:
        """
        Return collector health.

        Returns
        -------
        dict[str, Any]
        """

        try:

            self.validate()

            status = "healthy"

            healthy = True

            error = None

        except Exception as exc:

            status = "unhealthy"

            healthy = False

            error = str(exc)

        return {

            "status": status,

            "healthy": healthy,

            "error": error,

            "enabled": self._enabled,

            "running": self._running,

            "frozen": self._frozen,

            "closed": self._closed,

            "collections": self._collections,

            "revision": self._revision,

        }


    def dump(
        self,
    ) -> dict[str, Any]:
        """
        Dump collector state.

        Returns
        -------
        dict[str, Any]
        """

        with self._lock:

            return {

                "collector": {

                    "enabled": self._enabled,

                    "running": self._running,

                    "frozen": self._frozen,

                    "closed": self._closed,

                    "revision": self._revision,

                    "collections": self._collections,

                },

                "registry": (

                    self._registry.to_dict()

                ),

                "statistics": (

                    self.statistics()

                ),

                "health": (

                    self.health()

                ),

            }


    def inspect(
        self,
    ) -> dict[str, Any]:
        """
        Inspect collector internals.

        Returns
        -------
        dict[str, Any]
        """

        with self._lock:

            return {

                "type": (

                    self.__class__.__name__

                ),

                "runtime": {

                    "enabled": self._enabled,

                    "running": self._running,

                    "frozen": self._frozen,

                    "closed": self._closed,

                    "revision": self._revision,

                    "collections": self._collections,

                },

                "registry": {

                    "metrics": (

                        self._registry.count()

                    ),

                    "names": (

                        self._registry.names()

                    ),

                    "revision": (

                        self._registry.revision

                    ),

                },

                "statistics": (

                    self.statistics()

                ),

                "health": (

                    self.health()

                ),

            }
# ==========================================================
# Part 8. Serialization
# ==========================================================

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Serialize collector.

        Returns
        -------
        dict[str, Any]
        """

        with self._lock:

            return {

                "enabled": self._enabled,

                "running": self._running,

                "frozen": self._frozen,

                "closed": self._closed,

                "revision": self._revision,

                "collections": self._collections,

                "registry": (

                    self._registry.to_dict()

                ),

            }


    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "MetricCollector":
        """
        Deserialize collector.

        Parameters
        ----------
        data
            Serialized collector.

        Returns
        -------
        MetricCollector
        """

        if not isinstance(
            data,
            dict,
        ):

            raise TypeError(
                "Expected a dictionary."
            )

        registry = MetricRegistry.from_dict(

            data.get(
                "registry",
                {},
            )

        )

        collector = cls(

            registry=registry,

        )

        collector._enabled = bool(

            data.get(
                "enabled",
                True,
            )

        )

        collector._running = bool(

            data.get(
                "running",
                False,
            )

        )

        collector._frozen = bool(

            data.get(
                "frozen",
                False,
            )

        )

        collector._closed = bool(

            data.get(
                "closed",
                False,
            )

        )

        collector._revision = int(

            data.get(
                "revision",
                0,
            )

        )

        collector._collections = int(

            data.get(
                "collections",
                0,
            )

        )

        return collector


    def to_json(
        self,
        *,
        indent: int | None = 2,
    ) -> str:
        """
        Serialize collector to JSON.

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
    ) -> "MetricCollector":
        """
        Deserialize collector from JSON.

        Parameters
        ----------
        payload
            JSON string.

        Returns
        -------
        MetricCollector
        """

        import json

        if not isinstance(
            payload,
            str,
        ):

            raise TypeError(
                "Expected a JSON string."
            )

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
            Prometheus exposition text.
        """

        self._ensure_open()

        with self._lock:

            return self._registry.prometheus()


    def otel(
        self,
    ) -> list[dict[str, Any]]:
        """
        Export all registered metrics in
        OpenTelemetry format.

        Returns
        -------
        list[dict[str, Any]]
        """

        self._ensure_open()

        with self._lock:

            return self._registry.otel()


    def csv(
        self,
        *,
        include_header: bool = True,
    ) -> str:
        """
        Export all registered metrics as CSV.

        Parameters
        ----------
        include_header
            Include CSV header.

        Returns
        -------
        str
        """

        self._ensure_open()

        with self._lock:

            return self._registry.csv(
                include_header=include_header,
            )


    def snapshots(
        self,
    ) -> dict[str, Any]:
        """
        Export snapshots of all registered metrics.

        Returns
        -------
        dict[str, Any]
        """

        self._ensure_open()

        with self._lock:

            snapshots: dict[str, Any] = {}

            for name, metric in self._registry.items():

                snapshot = getattr(
                    metric,
                    "snapshot",
                    None,
                )

                if callable(snapshot):

                    snapshots[name] = snapshot()

                else:

                    snapshots[name] = {

                        "value": getattr(
                            metric,
                            "value",
                            None,
                        )

                    }

            return snapshots
# ==========================================================
# Part 10. Python Protocols
# ==========================================================

    def __len__(
        self,
    ) -> int:
        """
        Return the number of registered metrics.

        Returns
        -------
        int
        """

        with self._lock:

            return self._registry.count()


    def __iter__(
        self,
    ):
        """
        Iterate over registered metrics.

        Returns
        -------
        Iterator[Any]
        """

        with self._lock:

            return iter(
                tuple(
                    self._registry.metrics()
                )
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

            f"metrics={len(self)}, "

            f"collections={self._collections}, "

            f"revision={self._revision}, "

            f"running={self._running}, "

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

        state = (

            "running"

            if self._running

            else "stopped"

        )

        return (

            f"MetricCollector("

            f"{len(self)} metrics, "

            f"{self._collections} collections, "

            f"{state})"

        )


    # ======================================================
    # Compatibility
    # ======================================================

    @property
    def metric_count(
        self,
    ) -> int:
        """
        Compatibility alias for len(self).

        Returns
        -------
        int
        """

        return len(self)


    @property
    def collection_count(
        self,
    ) -> int:
        """
        Compatibility alias for collections.

        Returns
        -------
        int
        """

        return self._collections


    @property
    def is_running(
        self,
    ) -> bool:
        """
        Compatibility alias for running.

        Returns
        -------
        bool
        """

        return self._running


    @property
    def is_enabled(
        self,
    ) -> bool:
        """
        Compatibility alias for enabled.

        Returns
        -------
        bool
        """

        return self._enabled


    @property
    def is_frozen(
        self,
    ) -> bool:
        """
        Compatibility alias for frozen.

        Returns
        -------
        bool
        """

        return self._frozen


    @property
    def is_closed(
        self,
    ) -> bool:
        """
        Compatibility alias for closed.

        Returns
        -------
        bool
        """

        return self._closed


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
            - snapshots

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

            "snapshots": self.snapshots,

        }

        try:

            return exporters[format]()

        except KeyError:

            raise ValueError(

                f"Unsupported export format: "

                f"{format!r}"

            ) from None                                                                                                    
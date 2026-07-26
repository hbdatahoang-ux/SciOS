"""
SciOS-NG Observability
======================

Runtime Metric Recorder

Part 1
------

Foundation

MetricRecorder provides a thread-safe façade for recording
runtime metric values through a MetricRegistry.

Responsibilities
----------------

- Record metric values
- Dispatch operations to metrics
- Maintain runtime state
- Coordinate with MetricRegistry
"""

from __future__ import annotations

from threading import RLock
from typing import Any

from .registry import MetricRegistry

__all__ = [
    "MetricRecorder",
]


# ==========================================================
# Metric Recorder
# ==========================================================


class MetricRecorder:
    """
    Thread-safe runtime metric recorder.

    The recorder delegates operations to metrics stored in a
    MetricRegistry.
    """

    # ------------------------------------------------------
    # Constructor
    # ------------------------------------------------------

    def __init__(
        self,
        registry: MetricRegistry,
    ) -> None:
        """
        Initialize a MetricRecorder.

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

        self._revision: int = 0

        self._operations: int = 0

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
        Attached MetricRegistry.
        """

        return self._registry


    @property
    def enabled(
        self,
    ) -> bool:
        """
        Recorder enabled state.
        """

        return self._enabled


    @property
    def frozen(
        self,
    ) -> bool:
        """
        Recorder frozen state.
        """

        return self._frozen


    @property
    def closed(
        self,
    ) -> bool:
        """
        Recorder closed state.
        """

        return self._closed


    @property
    def revision(
        self,
    ) -> int:
        """
        Recorder revision number.
        """

        return self._revision


    @property
    def operations(
        self,
    ) -> int:
        """
        Total successful recording operations.
        """

        return self._operations


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
        Advance runtime revision.
        """

        self._revision += 1


    def _record_operation(
        self,
    ) -> None:
        """
        Record a successful operation.
        """

        self._operations += 1

        self._touch()


    def _ensure_open(
        self,
    ) -> None:
        """
        Ensure the recorder is open.
        """

        if self._closed:

            raise RuntimeError(
                "MetricRecorder is closed."
            )


    def _ensure_mutable(
        self,
    ) -> None:
        """
        Ensure the recorder accepts writes.
        """

        self._ensure_open()

        if self._frozen:

            raise RuntimeError(
                "MetricRecorder is frozen."
            )

        if not self._enabled:

            raise RuntimeError(
                "MetricRecorder is disabled."
            )
# ==========================================================
# Part 2. Recording API
# ==========================================================

    def record(
        self,
        name: str,
        value: Any,
    ) -> None:
        """
        Record a value to a metric.

        Parameters
        ----------
        name
            Metric name.

        value
            Recorded value.
        """

        self._ensure_mutable()

        with self._lock:

            metric = self._registry.get(name)

            if metric is None:

                raise KeyError(
                    f"Unknown metric: '{name}'."
                )

            operation = getattr(
                metric,
                "record",
                None,
            )

            if not callable(operation):

                raise AttributeError(
                    f"{metric.__class__.__name__} "
                    "does not support record()."
                )

            operation(value)

            self._record_operation()


    def update(
        self,
        name: str,
        value: Any,
    ) -> None:
        """
        Update a metric.

        Parameters
        ----------
        name
            Metric name.

        value
            New value.
        """

        self._ensure_mutable()

        with self._lock:

            metric = self._registry.get(name)

            if metric is None:

                raise KeyError(
                    f"Unknown metric: '{name}'."
                )

            operation = getattr(
                metric,
                "update",
                None,
            )

            if not callable(operation):

                raise AttributeError(
                    f"{metric.__class__.__name__} "
                    "does not support update()."
                )

            operation(value)

            self._record_operation()


    def observe(
        self,
        name: str,
        value: float,
    ) -> None:
        """
        Observe a value.

        Used by Histogram, Summary and Timer.
        """

        self.record(
            name,
            value,
        )


    def increment(
        self,
        name: str,
        amount: float = 1,
    ) -> None:
        """
        Increment a Counter.

        Parameters
        ----------
        name
            Metric name.

        amount
            Increment amount.
        """

        self._ensure_mutable()

        with self._lock:

            metric = self._registry[name]

            operation = getattr(
                metric,
                "add",
                None,
            )

            if operation is None:

                operation = getattr(
                    metric,
                    "inc",
                    None,
                )

            if not callable(operation):

                raise AttributeError(
                    f"{metric.__class__.__name__} "
                    "does not support increment."
                )

            operation(amount)

            self._record_operation()


    def decrement(
        self,
        name: str,
        amount: float = 1,
    ) -> None:
        """
        Decrement a Gauge.

        Parameters
        ----------
        name
            Metric name.

        amount
            Decrement amount.
        """

        self._ensure_mutable()

        with self._lock:

            metric = self._registry[name]

            operation = getattr(
                metric,
                "dec",
                None,
            )

            if not callable(operation):

                raise AttributeError(
                    f"{metric.__class__.__name__} "
                    "does not support decrement."
                )

            operation(amount)

            self._record_operation()


    def set(
        self,
        name: str,
        value: Any,
    ) -> None:
        """
        Set a metric value.

        Used primarily by Gauge.
        """

        self._ensure_mutable()

        with self._lock:

            metric = self._registry[name]

            operation = getattr(
                metric,
                "set",
                None,
            )

            if not callable(operation):

                raise AttributeError(
                    f"{metric.__class__.__name__} "
                    "does not support set()."
                )

            operation(value)

            self._record_operation()


    def batch(
        self,
        operations: list[
            tuple[str, str, Any]
        ],
    ) -> None:
        """
        Execute multiple recording operations.

        Parameters
        ----------
        operations

            List of

            (metric_name,
             operation_name,
             value)
        """

        self._ensure_mutable()

        with self._lock:

            for (

                name,

                operation,

                value,

            ) in operations:

                getattr(
                    self,
                    operation,
                )(
                    name,
                    value,
                )


    def reset(
        self,
    ) -> None:
        """
        Reset every registered metric.
        """

        self._ensure_mutable()

        with self._lock:

            for metric in self._registry:

                operation = getattr(
                    metric,
                    "reset",
                    None,
                )

                if callable(operation):

                    operation()

            self._record_operation()
# ==========================================================
# Part 3. Lookup
# ==========================================================

    def get_metric(
        self,
        name: str,
    ) -> Metric:
        """
        Retrieve a metric from the registry.

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

        self._ensure_open()

        with self._lock:

            metric = self._registry.get(name)

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
        Return all registered metric names.

        Returns
        -------
        list[str]
        """

        self._ensure_open()

        with self._lock:

            return self._registry.names()


    def metrics(
        self,
    ) -> list[Metric]:
        """
        Return all registered metrics.

        Returns
        -------
        list[Metric]
        """

        self._ensure_open()

        with self._lock:

            return self._registry.metrics()


    def count(
        self,
    ) -> int:
        """
        Return the number of registered metrics.

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

    def snapshot(
        self,
    ) -> dict[str, Any]:
        """
        Create a runtime snapshot of the recorder.

        Returns
        -------
        dict[str, Any]
        """

        with self._lock:

            return {

                "enabled": self._enabled,

                "frozen": self._frozen,

                "closed": self._closed,

                "revision": self._revision,

                "operations": self._operations,

                "registry": self._registry.snapshot(),

            }


    def restore(
        self,
        snapshot: dict[str, Any],
    ) -> None:
        """
        Restore recorder state.

        Parameters
        ----------
        snapshot
            Recorder snapshot.
        """

        self._ensure_mutable()

        if not isinstance(
            snapshot,
            dict,
        ):

            raise TypeError(
                "Snapshot must be a dictionary."
            )

        with self._lock:

            self._enabled = bool(

                snapshot.get(
                    "enabled",
                    True,
                )

            )

            self._frozen = bool(

                snapshot.get(
                    "frozen",
                    False,
                )

            )

            self._closed = bool(

                snapshot.get(
                    "closed",
                    False,
                )

            )

            self._revision = int(

                snapshot.get(
                    "revision",
                    0,
                )

            )

            self._operations = int(

                snapshot.get(
                    "operations",
                    0,
                )

            )

            registry_snapshot = snapshot.get(
                "registry"
            )

            if registry_snapshot is not None:

                self._registry.restore(
                    registry_snapshot
                )

            self._touch()


    def clone(
        self,
    ) -> "MetricRecorder":
        """
        Create a deep clone of the recorder.

        Returns
        -------
        MetricRecorder
        """

        with self._lock:

            recorder = self.__class__(

                registry=self._registry.clone(),

            )

            recorder._enabled = self._enabled

            recorder._frozen = self._frozen

            recorder._closed = self._closed

            recorder._revision = self._revision

            recorder._operations = self._operations

            return recorder


    def copy(
        self,
    ) -> "MetricRecorder":
        """
        Alias of clone().

        Returns
        -------
        MetricRecorder
        """

        return self.clone()


    def clear(
        self,
    ) -> None:
        """
        Reset every registered metric.

        The registry remains intact.

        Returns
        -------
        None
        """

        self._ensure_mutable()

        with self._lock:

            for metric in self._registry:

                reset = getattr(
                    metric,
                    "reset",
                    None,
                )

                if callable(reset):

                    reset()

            self._operations = 0

            self._touch()
# ==========================================================
# Part 5. Lifecycle
# ==========================================================

    def enable(
        self,
    ) -> None:
        """
        Enable the recorder.

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
        Disable the recorder.

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
        Freeze the recorder.

        Recording operations are blocked until
        unfreeze() is called.

        Returns
        -------
        None
        """

        self._ensure_open()

        with self._lock:

            self._frozen = True

            self._touch()


    def unfreeze(
        self,
    ) -> None:
        """
        Unfreeze the recorder.

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
        Close the recorder.

        A closed recorder cannot accept new
        recording operations.

        Returns
        -------
        None
        """

        with self._lock:

            if self._closed:

                return

            self._enabled = False

            self._closed = True

            self._touch()


    def reopen(
        self,
    ) -> None:
        """
        Reopen the recorder.

        Returns
        -------
        None
        """

        with self._lock:

            self._closed = False

            self._enabled = True

            self._frozen = False

            self._touch()
# ==========================================================
# Part 6. Validation
# ==========================================================

    def validate(
        self,
    ) -> None:
        """
        Validate the recorder.

        Raises
        ------
        RuntimeError
            If the recorder is internally inconsistent.

        ValueError
            If an invalid metric is found.
        """

        if self._revision < 0:

            raise RuntimeError(
                "Recorder revision cannot be negative."
            )

        if self._operations < 0:

            raise RuntimeError(
                "Operation count cannot be negative."
            )

        if self._closed and self._enabled:

            raise RuntimeError(
                "A closed recorder cannot be enabled."
            )

        self._registry.validate()


    def validate_metric(
        self,
        metric: Metric,
    ) -> None:
        """
        Validate a Metric instance.

        Parameters
        ----------
        metric
            Metric object.

        Raises
        ------
        TypeError
            If the object is not a Metric.
        """

        if not isinstance(
            metric,
            Metric,
        ):

            raise TypeError(
                "Expected a Metric instance."
            )

        validate = getattr(
            metric,
            "validate",
            None,
        )

        if callable(validate):

            validate()


    def validate_value(
        self,
        value: Any,
    ) -> None:
        """
        Validate a recording value.

        Parameters
        ----------
        value
            Recording value.

        Raises
        ------
        ValueError
            If the value is invalid.
        """

        if value is None:

            raise ValueError(
                "Metric value cannot be None."
            )

        if isinstance(
            value,
            bool,
        ):

            raise TypeError(
                "Boolean values are not valid metric values."
            )


    def validate_operation(
        self,
        operation: str,
    ) -> None:
        """
        Validate a recorder operation.

        Parameters
        ----------
        operation
            Operation name.

        Raises
        ------
        ValueError
            If the operation is unsupported.
        """

        supported = {

            "record",

            "update",

            "observe",

            "increment",

            "decrement",

            "set",

            "batch",

            "reset",

        }

        if operation not in supported:

            raise ValueError(

                f"Unsupported operation: "

                f"{operation!r}"

            )
# ==========================================================
# Part 7. Diagnostics
# ==========================================================

    def statistics(
        self,
    ) -> dict[str, Any]:
        """
        Return recorder statistics.

        Returns
        -------
        dict[str, Any]
        """

        with self._lock:

            registry = self._registry.statistics()

            return {

                "operations": self._operations,

                "revision": self._revision,

                "enabled": self._enabled,

                "frozen": self._frozen,

                "closed": self._closed,

                "metric_count": registry["count"],

                "registry_revision": registry["revision"],

            }


    def health(
        self,
    ) -> dict[str, Any]:
        """
        Return recorder health information.

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

            "operations": self._operations,

            "revision": self._revision,

        }


    def dump(
        self,
    ) -> dict[str, Any]:
        """
        Dump the complete recorder state.

        Returns
        -------
        dict[str, Any]
        """

        with self._lock:

            return {

                "statistics": self.statistics(),

                "health": self.health(),

                "registry": self._registry.to_dict(),

            }


    def inspect(
        self,
    ) -> dict[str, Any]:
        """
        Inspect the recorder.

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

                    "operations": self._operations,

                },

                "registry": {

                    "metrics": self._registry.count(),

                    "revision": self._registry.revision,

                },

                "statistics": self.statistics(),

                "health": self.health(),

            }
# ==========================================================
# Part 8. Serialization
# ==========================================================

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Serialize the recorder.

        Returns
        -------
        dict[str, Any]
        """

        with self._lock:

            return {

                "enabled": self._enabled,

                "frozen": self._frozen,

                "closed": self._closed,

                "revision": self._revision,

                "operations": self._operations,

                "registry": self._registry.to_dict(),

            }


    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "MetricRecorder":
        """
        Deserialize a recorder.

        Parameters
        ----------
        data
            Serialized recorder.

        Returns
        -------
        MetricRecorder
        """

        if not isinstance(data, dict):

            raise TypeError(
                "Expected a dictionary."
            )

        registry_data = data.get(
            "registry",
            {},
        )

        registry = MetricRegistry.from_dict(
            registry_data,
        )

        recorder = cls(
            registry=registry,
        )

        recorder._enabled = bool(
            data.get(
                "enabled",
                True,
            )
        )

        recorder._frozen = bool(
            data.get(
                "frozen",
                False,
            )
        )

        recorder._closed = bool(
            data.get(
                "closed",
                False,
            )
        )

        recorder._revision = int(
            data.get(
                "revision",
                0,
            )
        )

        recorder._operations = int(
            data.get(
                "operations",
                0,
            )
        )

        return recorder


    def to_json(
        self,
        *,
        indent: int | None = 2,
    ) -> str:
        """
        Serialize the recorder to JSON.

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
    ) -> "MetricRecorder":
        """
        Deserialize a recorder from JSON.

        Parameters
        ----------
        payload
            JSON string.

        Returns
        -------
        MetricRecorder
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
            Whether to include the CSV header.

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
        Export snapshots of every registered metric.

        Returns
        -------
        dict[str, Any]
        """

        self._ensure_open()

        with self._lock:

            return self._registry.snapshots()  
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

            f"operations={self._operations}, "

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

            f"MetricRecorder("

            f"{len(self)} metrics, "

            f"{self._operations} operations)"

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
    def operation_count(
        self,
    ) -> int:
        """
        Compatibility alias for operations.

        Returns
        -------
        int
        """

        return self._operations


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
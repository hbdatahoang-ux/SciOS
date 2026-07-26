"""
SciOS Observability
===================

Timer Metric

Part 1
------

Foundation layer.

A Timer measures execution duration and timing statistics.

Responsibilities
----------------

- Runtime timer metric
- High-resolution clock
- Duration accumulation
- Timing statistics
- Snapshot support
- Lifecycle integration

Concrete APIs are implemented in later parts.
"""

from __future__ import annotations

# ======================================================
# Imports
# ======================================================

import time

from typing import Any

from .metric import Metric
from .descriptor import MetricDescriptor
from .metadata import MetricMetadata
from .labels import MetricLabels
from .attributes import MetricAttributes


__all__ = [
    "Timer",
]


# ======================================================
# Timer
# ======================================================


class Timer(Metric):
    """
    Runtime timer metric.

    Timer measures elapsed durations using a
    monotonic high-resolution clock.

    Runtime statistics include:

    - total duration
    - observation count
    - minimum duration
    - maximum duration
    - average duration
    """

    # ==================================================
    # Constructor
    # ==================================================

    def __init__(
        self,
        *,
        descriptor: MetricDescriptor,
        metadata: MetricMetadata | None = None,
        labels: MetricLabels | None = None,
        attributes: MetricAttributes | None = None,
    ) -> None:
        """
        Initialize a Timer metric.
        """

        super().__init__(

            descriptor=descriptor,

            metadata=metadata,

            labels=labels,

            attributes=attributes,

        )

        # ----------------------------------------------
        # High Resolution Clock
        # ----------------------------------------------

        self._clock = time.perf_counter

        # ----------------------------------------------
        # Runtime Timing State
        # ----------------------------------------------

        self._running: bool = False

        self._started_at: float | None = None

        self._last_duration: float = 0.0

        # ----------------------------------------------
        # Statistics
        # ----------------------------------------------

        self._count: int = 0

        self._total: float = 0.0

        self._min: float | None = None

        self._max: float | None = None

        # ----------------------------------------------
        # Default Metric Value
        # ----------------------------------------------

        self._value = 0.0

        self._previous_value = 0.0

        # ----------------------------------------------
        # Runtime Validation
        # ----------------------------------------------

        self.validate()

    # ==================================================
    # Clock
    # ==================================================

    @property
    def clock(
        self,
    ):
        """
        High-resolution runtime clock.

        Returns
        -------
        Callable
        """

        return self._clock

    # ==================================================
    # Internal Runtime Validation
    # ==================================================

    def _validate_runtime(
        self,
    ) -> None:
        """
        Validate internal runtime state.

        Raises
        ------
        RuntimeError
            If internal timer state is inconsistent.
        """

        if self._count < 0:

            raise RuntimeError(
                "Negative observation count."
            )

        if self._total < 0.0:

            raise RuntimeError(
                "Negative accumulated duration."
            )

        if (

            self._min is not None

            and self._max is not None

            and self._min > self._max

        ):

            raise RuntimeError(
                "Minimum duration exceeds maximum duration."
            )
# ======================================================
# Part 2. Timer API
# ======================================================

    def start(
        self,
    ) -> None:
        """
        Start timing.

        Raises
        ------
        RuntimeError
            If the timer is already running.
        """

        with self.lock:

            self._ensure_mutable()

            if self._running:

                raise RuntimeError(
                    "Timer is already running."
                )

            self._started_at = self._clock()

            self._running = True

            self._touch()


    def stop(
        self,
    ) -> float:
        """
        Stop timing and record the elapsed duration.

        Returns
        -------
        float
            Measured duration in seconds.
        """

        with self.lock:

            self._ensure_mutable()

            if not self._running:

                raise RuntimeError(
                    "Timer is not running."
                )

            duration = (

                self._clock()

                - self._started_at

            )

            self._running = False

            self._started_at = None

            self.observe(duration)

            return duration


    def observe(
        self,
        duration: float,
    ) -> float:
        """
        Record a duration.

        Parameters
        ----------
        duration
            Duration in seconds.

        Returns
        -------
        float
            Recorded duration.
        """

        with self.lock:

            self._ensure_mutable()

            self.validate_duration(duration)

            self._previous_value = self._value

            self._value = float(duration)

            self._last_duration = float(duration)

            self._count += 1

            self._total += duration

            if (

                self._min is None

                or duration < self._min

            ):

                self._min = duration

            if (

                self._max is None

                or duration > self._max

            ):

                self._max = duration

            self._update_count += 1

            self._revision += 1

            self._dirty = True

            self._touch()

            return duration


    def record(
        self,
        duration: float,
    ) -> float:
        """
        Alias of observe().
        """

        return self.observe(duration)


    def update(
        self,
        duration: float,
    ) -> float:
        """
        Alias of observe().
        """

        return self.observe(duration)


    def elapsed(
        self,
    ) -> float:
        """
        Return current elapsed time.

        Returns
        -------
        float
        """

        if not self._running:

            return self._last_duration

        return (

            self._clock()

            - self._started_at

        )


    def reset(
        self,
    ) -> None:
        """
        Reset the timer.

        Clears all observations and statistics.
        """

        with self.lock:

            self._ensure_mutable()

            self._running = False

            self._started_at = None

            self._last_duration = 0.0

            self._value = 0.0

            self._previous_value = 0.0

            self._count = 0

            self._total = 0.0

            self._min = None

            self._max = None

            self._update_count = 0

            self._revision += 1

            self._dirty = True

            self._touch()
# ======================================================
# Part 3. Properties
# ======================================================

    @property
    def value(
        self,
    ) -> float:
        """
        Last recorded duration.

        Returns
        -------
        float
        """

        return float(self._value)


    @property
    def count(
        self,
    ) -> int:
        """
        Number of recorded durations.

        Returns
        -------
        int
        """

        return self._count


    @property
    def total(
        self,
    ) -> float:
        """
        Total accumulated duration.

        Returns
        -------
        float
        """

        return self._total


    @property
    def min(
        self,
    ) -> float | None:
        """
        Minimum recorded duration.

        Returns
        -------
        float | None
        """

        return self._min


    @property
    def max(
        self,
    ) -> float | None:
        """
        Maximum recorded duration.

        Returns
        -------
        float | None
        """

        return self._max


    @property
    def mean(
        self,
    ) -> float:
        """
        Mean duration.

        Returns
        -------
        float
        """

        if self._count == 0:

            return 0.0

        return self._total / self._count


    @property
    def running(
        self,
    ) -> bool:
        """
        Whether the timer is currently running.

        Returns
        -------
        bool
        """

        return self._running


    @property
    def started_at(
        self,
    ) -> float | None:
        """
        Internal high-resolution start timestamp.

        Returns
        -------
        float | None
        """

        return self._started_at


    @property
    def created_at(
        self,
    ):
        """
        Metric creation timestamp.
        """

        return self._created_at


    @property
    def updated_at(
        self,
    ):
        """
        Last update timestamp.
        """

        return self._updated_at


    @property
    def revision(
        self,
    ) -> int:
        """
        Runtime revision number.

        Returns
        -------
        int
        """

        return self._revision


    @property
    def dirty(
        self,
    ) -> bool:
        """
        Dirty state.

        Indicates whether runtime state has
        changed since the previous checkpoint.

        Returns
        -------
        bool
        """

        return self._dirty
# ======================================================
# Part 4. Snapshot
# ======================================================

    def snapshot(
        self,
    ) -> MetricSnapshot:
        """
        Create an immutable snapshot of the timer.

        Returns
        -------
        MetricSnapshot
        """

        return MetricSnapshot.create(

            name=self.name,

            value={

                "last": self._value,

                "count": self._count,

                "total": self._total,

                "min": self._min,

                "max": self._max,

                "mean": self.mean,

                "running": self._running,

            },

            metric_type="timer",

            labels=self.labels.to_dict(),

            attributes=self.attributes.to_dict(),

            metadata=self.metadata.to_dict(),

        )


    def restore(
        self,
        snapshot: MetricSnapshot,
    ) -> None:
        """
        Restore timer state from a snapshot.

        Parameters
        ----------
        snapshot
            Snapshot to restore from.
        """

        self._ensure_mutable()

        if snapshot.metric_type != "timer":

            raise TypeError(
                "Snapshot is not a Timer snapshot."
            )

        value = snapshot.value

        self._previous_value = self._value

        self._value = float(
            value.get("last", 0.0)
        )

        self._count = int(
            value.get("count", 0)
        )

        self._total = float(
            value.get("total", 0.0)
        )

        self._min = value.get("min")

        self._max = value.get("max")

        self._running = bool(
            value.get("running", False)
        )

        self._started_at = None

        self._revision += 1

        self._dirty = True

        self._touch()


    def clone(
        self,
    ) -> "Timer":
        """
        Clone the timer.

        Returns
        -------
        Timer
        """

        cloned = self.__class__(

            descriptor=self.descriptor,

            metadata=self.metadata.copy(),

            labels=self.labels.copy(),

            attributes=self.attributes.copy(),

        )

        cloned.restore(
            self.snapshot()
        )

        return cloned


    def copy(
        self,
    ) -> "Timer":
        """
        Alias of clone().

        Returns
        -------
        Timer
        """

        return self.clone()
# ======================================================
# Part 5. Lifecycle
# ======================================================

    def freeze(
        self,
    ) -> None:
        """
        Freeze the timer.

        Frozen timers cannot be modified.
        """

        if self._closed:

            raise RuntimeError(
                "Cannot freeze a closed Timer."
            )

        self._frozen = True

        self._touch()


    def unfreeze(
        self,
    ) -> None:
        """
        Unfreeze the timer.
        """

        if self._closed:

            raise RuntimeError(
                "Cannot unfreeze a closed Timer."
            )

        self._frozen = False

        self._touch()


    def enable(
        self,
    ) -> None:
        """
        Enable the timer.
        """

        if self._closed:

            raise RuntimeError(
                "Cannot enable a closed Timer."
            )

        self._enabled = True

        self._touch()


    def disable(
        self,
    ) -> None:
        """
        Disable the timer.

        A disabled timer ignores updates.
        """

        if self._closed:

            raise RuntimeError(
                "Cannot disable a closed Timer."
            )

        self._enabled = False

        self._touch()


    def close(
        self,
    ) -> None:
        """
        Permanently close the timer.

        Running timers are stopped.
        """

        if self._running:

            self._running = False

            self._started_at = None

        self._closed = True

        self._enabled = False

        self._touch()


    def reopen(
        self,
    ) -> None:
        """
        Reopen a previously closed timer.
        """

        self._closed = False

        self._enabled = True

        self._running = False

        self._started_at = None

        self._touch()
# ======================================================
# Part 6. Validation
# ======================================================

    def validate(
        self,
    ) -> None:
        """
        Validate the complete Timer state.

        Raises
        ------
        ValueError
            If the runtime state is invalid.
        """

        self.validate_state()

        self.validate_numeric(self._value)

        self.validate_numeric(self._total)

        if self._min is not None:

            self.validate_duration(self._min)

        if self._max is not None:

            self.validate_duration(self._max)


    def validate_duration(
        self,
        duration: float,
    ) -> None:
        """
        Validate a duration.

        Parameters
        ----------
        duration
            Duration in seconds.

        Raises
        ------
        ValueError
            If duration is negative.
        """

        self.validate_numeric(duration)

        if duration < 0.0:

            raise ValueError(
                "Duration must be >= 0."
            )


    def validate_numeric(
        self,
        value: Any,
    ) -> None:
        """
        Validate a numeric value.

        Parameters
        ----------
        value
            Numeric value.

        Raises
        ------
        TypeError
            If value is not numeric.

        ValueError
            If value is NaN or infinite.
        """

        if not isinstance(
            value,
            (int, float),
        ):

            raise TypeError(
                "Value must be numeric."
            )

        value = float(value)

        if value != value:

            raise ValueError(
                "NaN is not allowed."
            )

        if value in (

            float("inf"),

            float("-inf"),

        ):

            raise ValueError(
                "Infinite values are not allowed."
            )


    def validate_state(
        self,
    ) -> None:
        """
        Validate internal Timer runtime state.

        Raises
        ------
        RuntimeError
            If the Timer state is inconsistent.
        """

        if self._count < 0:

            raise RuntimeError(
                "Negative observation count."
            )

        if self._total < 0.0:

            raise RuntimeError(
                "Negative accumulated duration."
            )

        if (

            self._min is not None

            and self._max is not None

            and self._min > self._max

        ):

            raise RuntimeError(
                "Minimum duration exceeds maximum duration."
            )

        if self._running and self._started_at is None:

            raise RuntimeError(
                "Running timer has no start time."
            )

        if (

            not self._running

            and self._started_at is not None

        ):

            raise RuntimeError(
                "Stopped timer still has a start time."
            )
# ======================================================
# Part 7. Diagnostics
# ======================================================

    def statistics(
        self,
    ) -> dict[str, Any]:
        """
        Return runtime statistics.

        Returns
        -------
        dict[str, Any]
        """

        return {

            "name": self.name,

            "metric_type": "timer",

            "value": self._value,

            "count": self._count,

            "total": self._total,

            "min": self._min,

            "max": self._max,

            "mean": self.mean,

            "running": self._running,

            "revision": self._revision,

            "dirty": self._dirty,

            "enabled": self._enabled,

            "frozen": self._frozen,

            "closed": self._closed,

            "created_at": self._created_at,

            "updated_at": self._updated_at,

        }


    def health(
        self,
    ) -> dict[str, Any]:
        """
        Return runtime health information.

        Returns
        -------
        dict[str, Any]
        """

        try:

            self.validate()

            status = "healthy"

            valid = True

        except Exception as exc:

            status = "unhealthy"

            valid = False

            error = str(exc)

        result = {

            "status": status,

            "valid": valid,

            "running": self._running,

            "enabled": self._enabled,

            "frozen": self._frozen,

            "closed": self._closed,

            "dirty": self._dirty,

            "revision": self._revision,

        }

        if not valid:

            result["error"] = error

        return result


    def dump(
        self,
    ) -> dict[str, Any]:
        """
        Dump the complete runtime state.

        Returns
        -------
        dict[str, Any]
        """

        return {

            "statistics": self.statistics(),

            "labels": self.labels.to_dict(),

            "attributes": self.attributes.to_dict(),

            "metadata": self.metadata.to_dict(),

            "snapshot": self.snapshot().to_dict(),

        }


    def inspect(
        self,
    ) -> dict[str, Any]:
        """
        Return a production inspection report.

        Returns
        -------
        dict[str, Any]
        """

        return {

            "type": self.__class__.__name__,

            "descriptor": self.descriptor.name,

            "state": {

                "running": self._running,

                "enabled": self._enabled,

                "frozen": self._frozen,

                "closed": self._closed,

                "dirty": self._dirty,

            },

            "statistics": self.statistics(),

            "health": self.health(),

            "snapshot_version": self.snapshot().version,

        }
# ======================================================
# Part 8. Serialization
# ======================================================

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Serialize the timer to a dictionary.

        Returns
        -------
        dict[str, Any]
        """

        return {

            "name": self.name,

            "metric_type": "timer",

            "value": self._value,

            "count": self._count,

            "total": self._total,

            "min": self._min,

            "max": self._max,

            "mean": self.mean,

            "running": self._running,

            "started_at": self._started_at,

            "created_at": self._created_at,

            "updated_at": self._updated_at,

            "revision": self._revision,

            "dirty": self._dirty,

            "enabled": self._enabled,

            "frozen": self._frozen,

            "closed": self._closed,

            "labels": self.labels.to_dict(),

            "attributes": self.attributes.to_dict(),

            "metadata": self.metadata.to_dict(),

        }


    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "Timer":
        """
        Construct a Timer from a serialized dictionary.

        Parameters
        ----------
        data
            Serialized timer.

        Returns
        -------
        Timer
        """

        timer = cls(

            descriptor=MetricDescriptor(

                name=data["name"],

                metric_type="timer",

            ),

            metadata=MetricMetadata.from_dict(

                data.get("metadata", {})

            ),

            labels=MetricLabels.from_dict(

                data.get("labels", {})

            ),

            attributes=MetricAttributes.from_dict(

                data.get("attributes", {})

            ),

        )

        timer._value = float(
            data.get("value", 0.0)
        )

        timer._previous_value = timer._value

        timer._count = int(
            data.get("count", 0)
        )

        timer._total = float(
            data.get("total", 0.0)
        )

        timer._min = data.get("min")

        timer._max = data.get("max")

        timer._running = bool(
            data.get("running", False)
        )

        timer._started_at = data.get(
            "started_at"
        )

        timer._revision = int(
            data.get("revision", 0)
        )

        timer._dirty = bool(
            data.get("dirty", False)
        )

        timer._enabled = bool(
            data.get("enabled", True)
        )

        timer._frozen = bool(
            data.get("frozen", False)
        )

        timer._closed = bool(
            data.get("closed", False)
        )

        return timer


    def to_json(
        self,
        *,
        indent: int | None = 2,
    ) -> str:
        """
        Serialize the timer to JSON.

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

            default=str,

            ensure_ascii=False,

        )


    @classmethod
    def from_json(
        cls,
        payload: str,
    ) -> "Timer":
        """
        Construct a Timer from JSON.

        Parameters
        ----------
        payload
            JSON string.

        Returns
        -------
        Timer
        """

        import json

        return cls.from_dict(

            json.loads(payload)

        )
# ======================================================
# Part 9. Export
# ======================================================

    def prometheus(
        self,
    ) -> str:
        """
        Export the Timer in Prometheus exposition format.

        Timer is exported as a Summary-compatible metric:

            <name>_count
            <name>_sum

        Returns
        -------
        str
        """

        labels = ""

        if len(self.labels):

            labels = "{" + ",".join(

                f'{k}="{v}"'

                for k, v in sorted(
                    self.labels.items()
                )

            ) + "}"

        return "\n".join(

            [

                f"{self.name}_count{labels} {self._count}",

                f"{self.name}_sum{labels} {self._total}",

            ]

        )


    def otel(
        self,
    ) -> dict[str, Any]:
        """
        Export the Timer in an OpenTelemetry-friendly format.

        Returns
        -------
        dict[str, Any]
        """

        return {

            "name": self.name,

            "type": "timer",

            "value": self._value,

            "count": self._count,

            "sum": self._total,

            "min": self._min,

            "max": self._max,

            "mean": self.mean,

            "running": self._running,

            "attributes": self.attributes.to_dict(),

            "labels": self.labels.to_dict(),

            "metadata": self.metadata.to_dict(),

            "timestamp": self.updated_at.isoformat(),

        }


    def csv(
        self,
    ) -> str:
        """
        Export the Timer as a CSV row.

        Returns
        -------
        str
        """

        return ",".join(

            [

                self.name,

                "timer",

                str(self._value),

                str(self._count),

                str(self._total),

                str(self._min),

                str(self._max),

                str(self.mean),

                str(self._running),

                self.updated_at.isoformat(),

            ]

        )
# ======================================================
# Part 10. Final Polish
# ======================================================

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

            f"name={self.name!r}, "

            f"value={self._value:.6f}, "

            f"count={self._count}, "

            f"total={self._total:.6f}, "

            f"running={self._running}, "

            f"revision={self._revision})"

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

            f"{self.name}"

            f"(last={self._value:.6f}s, "

            f"count={self._count}, "

            f"mean={self.mean:.6f}s)"

        )


    def __float__(
        self,
    ) -> float:
        """
        Convert the Timer to float.

        Returns
        -------
        float
            Last recorded duration.
        """

        return float(self._value)


    def __bool__(
        self,
    ) -> bool:
        """
        Truthiness.

        Returns
        -------
        bool
            True if at least one observation has
            been recorded.
        """

        return self._count > 0


    # ==================================================
    # Compatibility
    # ==================================================

    @property
    def last(
        self,
    ) -> float:
        """
        Compatibility alias for value.

        Returns
        -------
        float
        """

        return self._value


    @property
    def average(
        self,
    ) -> float:
        """
        Compatibility alias for mean.

        Returns
        -------
        float
        """

        return self.mean


    @property
    def duration(
        self,
    ) -> float:
        """
        Compatibility alias for the last duration.

        Returns
        -------
        float
        """

        return self._value


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

                f"Unsupported export format: {format}"

            ) from None                                                                                    
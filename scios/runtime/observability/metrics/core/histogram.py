"""
SciOS Observability
===================

Histogram Metric

Part 1
------

Foundation

Responsibilities
----------------

- Histogram metric implementation
- Bucket management
- Runtime validation
- Default initialization

Histogram stores observations inside configurable buckets.

Aggregation/export logic is implemented by the Metric base class.
"""

from __future__ import annotations

from bisect import bisect_right
from typing import Any
from typing import Iterable

from .metric import Metric
from .descriptor import MetricDescriptor
from .metadata import MetricMetadata
from .labels import MetricLabels
from .attributes import MetricAttributes

__all__ = [
    "Histogram",
]


# ==========================================================
# Histogram
# ==========================================================


class Histogram(Metric):
    """
    Histogram metric.

    A Histogram records observations into ordered buckets.

    Example
    -------
    buckets = (
        0.1,
        0.5,
        1.0,
        2.5,
        5.0,
        10.0,
    )
    """

    DEFAULT_BUCKETS = (
        0.005,
        0.01,
        0.025,
        0.05,
        0.10,
        0.25,
        0.50,
        1.0,
        2.5,
        5.0,
        10.0,
        float("inf"),
    )

    # ======================================================
    # Constructor
    # ======================================================

    def __init__(
        self,
        *,
        descriptor: MetricDescriptor,
        metadata: MetricMetadata | None = None,
        labels: MetricLabels | None = None,
        attributes: MetricAttributes | None = None,
        buckets: Iterable[float] | None = None,
    ) -> None:
        """
        Initialize Histogram.

        Parameters
        ----------
        descriptor
            Metric descriptor.

        metadata
            Metric metadata.

        labels
            Metric labels.

        attributes
            Runtime attributes.

        buckets
            Ordered histogram bucket boundaries.
        """

        super().__init__(
            descriptor=descriptor,
            metadata=metadata,
            labels=labels,
            attributes=attributes,
        )

        # --------------------------------------------------
        # Buckets
        # --------------------------------------------------

        bucket_values = tuple(
            buckets or self.DEFAULT_BUCKETS
        )

        self._validate_buckets(
            bucket_values
        )

        self._buckets: tuple[float, ...] = (
            bucket_values
        )

        self._bucket_counts: list[int] = [
            0
            for _ in self._buckets
        ]

        # --------------------------------------------------
        # Runtime Statistics
        # --------------------------------------------------

        self._count: int = 0

        self._sum: float = 0.0

        self._min: float | None = None

        self._max: float | None = None

        # --------------------------------------------------
        # Default Runtime Value
        # --------------------------------------------------

        self._value = self._default_value()

        # --------------------------------------------------
        # Runtime Validation
        # --------------------------------------------------

        self.validate()

    # ======================================================
    # Buckets
    # ======================================================

    @property
    def buckets(
        self,
    ) -> tuple[float, ...]:
        """
        Histogram bucket boundaries.
        """

        return self._buckets

    @property
    def bucket_counts(
        self,
    ) -> tuple[int, ...]:
        """
        Current bucket counts.
        """

        return tuple(
            self._bucket_counts
        )

    # ======================================================
    # Default Value
    # ======================================================

    def _default_value(
        self,
    ) -> list[int]:
        """
        Default histogram value.
        """

        return [
            0
            for _ in self._buckets
        ]

    # ======================================================
    # Runtime Validation
    # ======================================================

    def validate(
        self,
    ) -> None:
        """
        Validate histogram runtime state.
        """

        self._validate_buckets(
            self._buckets
        )

        if len(
            self._bucket_counts
        ) != len(
            self._buckets
        ):
            raise ValueError(
                "Bucket count mismatch."
            )

        if self._count < 0:
            raise ValueError(
                "Count cannot be negative."
            )

        if self._sum < 0:
            raise ValueError(
                "Sum cannot be negative."
            )

    def _validate_buckets(
        self,
        buckets: Iterable[float],
    ) -> None:
        """
        Validate bucket configuration.
        """

        bucket_list = list(
            buckets
        )

        if not bucket_list:
            raise ValueError(
                "Histogram requires at least one bucket."
            )

        previous = float("-inf")

        for bucket in bucket_list:

            if not isinstance(
                bucket,
                (int, float),
            ):
                raise TypeError(
                    "Bucket values must be numeric."
                )

            if bucket <= previous:
                raise ValueError(
                    "Buckets must be strictly increasing."
                )

            previous = float(
                bucket
            )
    # ======================================================
    # Part 2. Histogram API
    # ======================================================

    def observe(
        self,
        value: float,
    ) -> None:
        """
        Record a single observation.

        Parameters
        ----------
        value
            Numeric value to record.
        """

        self.validate_numeric(value)
        self._ensure_mutable()

        with self.lock:

            self._access()

            self._previous_value = self._value

            index = bisect_right(
                self._buckets,
                float(value),
            )

            if index >= len(self._bucket_counts):
                index = len(self._bucket_counts) - 1

            self._bucket_counts[index] += 1

            self._count += 1

            self._sum += float(value)

            if (
                self._min is None
                or value < self._min
            ):
                self._min = float(value)

            if (
                self._max is None
                or value > self._max
            ):
                self._max = float(value)

            self._value = tuple(
                self._bucket_counts
            )

            self._update_count += 1

            self._touch()


    def record(
        self,
        value: float,
    ) -> None:
        """
        Alias of observe().
        """

        self.observe(value)


    def update(
        self,
        value: Any,
    ) -> None:
        """
        Update histogram.

        Accepts either

        - scalar numeric value
        - iterable of numeric values
        """

        if isinstance(
            value,
            (list, tuple, set),
        ):

            for item in value:
                self.observe(item)

            return

        self.observe(value)


    def count(
        self,
    ) -> int:
        """
        Total number of observations.
        """

        return self._count


    def sum(
        self,
    ) -> float:
        """
        Sum of all observations.
        """

        return self._sum


    def bucket_counts(
        self,
    ) -> tuple[int, ...]:
        """
        Return immutable bucket counts.
        """

        return tuple(
            self._bucket_counts
        )


    def reset(
        self,
    ) -> None:
        """
        Reset histogram runtime state.
        """

        self._ensure_mutable()

        with self.lock:

            self._bucket_counts = [

                0

                for _ in self._buckets

            ]

            self._count = 0

            self._sum = 0.0

            self._min = None

            self._max = None

            self._previous_value = self._value

            self._value = tuple(
                self._bucket_counts
            )

            self._update_count += 1

            self._touch()
    # ======================================================
    # Part 3. Properties
    # ======================================================

    @property
    def value(
        self,
    ) -> tuple[int, ...]:
        """
        Current bucket counts.

        Returns
        -------
        tuple[int, ...]
            Immutable histogram bucket counts.
        """
        return tuple(self._bucket_counts)


    @property
    def buckets(
        self,
    ) -> tuple[float, ...]:
        """
        Histogram bucket boundaries.
        """
        return tuple(self._buckets)


    @property
    def count(
        self,
    ) -> int:
        """
        Total number of observations.
        """
        return self._count


    @property
    def sum(
        self,
    ) -> float:
        """
        Sum of all observed values.
        """
        return self._sum


    @property
    def min(
        self,
    ) -> float | None:
        """
        Minimum observed value.
        """
        return self._min


    @property
    def max(
        self,
    ) -> float | None:
        """
        Maximum observed value.
        """
        return self._max


    @property
    def mean(
        self,
    ) -> float:
        """
        Mean of all observations.
        """
        if self._count == 0:
            return 0.0

        return self._sum / self._count


    @property
    def created_at(
        self,
    ):
        """
        Histogram creation timestamp.
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
        """
        return self._revision


    @property
    def dirty(
        self,
    ) -> bool:
        """
        Whether the histogram has been modified
        since the last checkpoint.
        """
        return self._dirty
    # ======================================================
    # Part 4. Snapshot
    # ======================================================

    def snapshot(
        self,
    ) -> MetricSnapshot:
        """
        Create an immutable snapshot of this histogram.

        Returns
        -------
        MetricSnapshot
        """

        with self.lock:

            return MetricSnapshot.create(

                name=self.name,

                value={
                    "buckets": tuple(self._bucket_counts),
                    "count": self._count,
                    "sum": self._sum,
                    "min": self._min,
                    "max": self._max,
                    "mean": self.mean,
                },

                metric_type="histogram",

                labels=self.labels.to_dict(),

                attributes=self.attributes.to_dict(),

                metadata=self.metadata.to_dict(),
            )


    def restore(
        self,
        snapshot: MetricSnapshot,
    ) -> None:
        """
        Restore histogram state from a snapshot.

        Parameters
        ----------
        snapshot
            Histogram snapshot.
        """

        self._ensure_mutable()

        if snapshot.metric_type != "histogram":
            raise TypeError(
                "Snapshot is not a histogram."
            )

        value = snapshot.value

        with self.lock:

            self._bucket_counts = list(
                value.get(
                    "buckets",
                    (),
                )
            )

            self._count = int(
                value.get(
                    "count",
                    0,
                )
            )

            self._sum = float(
                value.get(
                    "sum",
                    0.0,
                )
            )

            self._min = value.get(
                "min"
            )

            self._max = value.get(
                "max"
            )

            self._value = tuple(
                self._bucket_counts
            )

            self._update_count += 1

            self._touch()


    def clone(
        self,
    ) -> "Histogram":
        """
        Deep clone this histogram.

        Returns
        -------
        Histogram
        """

        clone = self.__class__(

            descriptor=self.descriptor.copy(),

            metadata=self.metadata.copy(),

            labels=self.labels.copy(),

            attributes=self.attributes.copy(),

            buckets=self.buckets,
        )

        clone.restore(
            self.snapshot()
        )

        return clone


    def copy(
        self,
    ) -> "Histogram":
        """
        Alias of clone().

        Returns
        -------
        Histogram
        """

        return self.clone()
    # ======================================================
    # Part 5. Lifecycle
    # ======================================================

    def freeze(
        self,
    ) -> None:
        """
        Freeze the histogram.

        A frozen histogram cannot be modified until
        unfreeze() is called.
        """

        with self.lock:

            if self._closed:
                raise RuntimeError(
                    "Cannot freeze a closed histogram."
                )

            if self._frozen:
                return

            self._frozen = True

            self._touch()


    def unfreeze(
        self,
    ) -> None:
        """
        Unfreeze the histogram.
        """

        with self.lock:

            if self._closed:
                raise RuntimeError(
                    "Cannot unfreeze a closed histogram."
                )

            if not self._frozen:
                return

            self._frozen = False

            self._touch()


    def enable(
        self,
    ) -> None:
        """
        Enable the histogram.

        Enabled histograms accept new observations.
        """

        with self.lock:

            if self._closed:
                raise RuntimeError(
                    "Cannot enable a closed histogram."
                )

            if self._enabled:
                return

            self._enabled = True

            self._touch()


    def disable(
        self,
    ) -> None:
        """
        Disable the histogram.

        Disabled histograms reject new observations
        but preserve their current state.
        """

        with self.lock:

            if self._closed:
                raise RuntimeError(
                    "Cannot disable a closed histogram."
                )

            if not self._enabled:
                return

            self._enabled = False

            self._touch()


    def close(
        self,
    ) -> None:
        """
        Permanently close the histogram.

        A closed histogram becomes read-only.
        """

        with self.lock:

            if self._closed:
                return

            self._closed = True

            self._enabled = False

            self._frozen = True

            self._touch()


    def reopen(
        self,
    ) -> None:
        """
        Reopen a previously closed histogram.
        """

        with self.lock:

            if not self._closed:
                return

            self._closed = False

            self._enabled = True

            self._frozen = False

            self._touch()
    # ======================================================
    # Part 6. Validation
    # ======================================================

    def validate(
        self,
    ) -> None:
        """
        Validate the complete histogram state.

        Raises
        ------
        ValueError
            If the histogram configuration is invalid.
        """

        self.validate_bucket()

        if self._count < 0:
            raise ValueError(
                "Histogram count cannot be negative."
            )

        if self._sum < 0:
            raise ValueError(
                "Histogram sum cannot be negative."
            )

        if (
            self._min is not None
            and self._max is not None
            and self._min > self._max
        ):
            raise ValueError(
                "Histogram minimum cannot exceed maximum."
            )

        if len(self._bucket_counts) != len(self._buckets):
            raise ValueError(
                "Bucket count size does not match bucket definition."
            )


    def validate_bucket(
        self,
    ) -> None:
        """
        Validate histogram bucket configuration.

        Buckets must be strictly increasing.
        """

        if not self._buckets:
            raise ValueError(
                "Histogram must contain at least one bucket."
            )

        previous = None

        for bucket in self._buckets:

            self.validate_numeric(bucket)

            if (
                previous is not None
                and bucket <= previous
            ):
                raise ValueError(
                    "Histogram buckets must be strictly increasing."
                )

            previous = bucket


    def validate_value(
        self,
        value: Any,
    ) -> None:
        """
        Validate an observed value.
        """

        self.validate_numeric(value)


    def validate_numeric(
        self,
        value: Any,
    ) -> None:
        """
        Validate a numeric value.

        Raises
        ------
        TypeError
            If value is not numeric.
        """

        if not isinstance(
            value,
            (int, float),
        ):
            raise TypeError(
                "Histogram values must be numeric."
            )

        if isinstance(
            value,
            bool,
        ):
            raise TypeError(
                "Boolean values are not valid histogram observations."
            )

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
    # ======================================================
    # Part 7. Diagnostics
    # ======================================================

    def statistics(
        self,
    ) -> dict[str, Any]:
        """
        Return runtime statistics for this histogram.

        Returns
        -------
        dict[str, Any]
            Runtime statistics.
        """

        return {
            "metric": self.name,
            "type": "histogram",
            "count": self._count,
            "sum": self._sum,
            "min": self._min,
            "max": self._max,
            "mean": self.mean,
            "bucket_count": len(self._buckets),
            "observations": len(self._values),
            "revision": self._revision,
            "dirty": self._dirty,
            "enabled": self._enabled,
            "frozen": self._frozen,
            "closed": self._closed,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


    def health(
        self,
    ) -> dict[str, Any]:
        """
        Return runtime health information.
        """

        issues: list[str] = []

        if self._closed:
            issues.append("closed")

        if not self._enabled:
            issues.append("disabled")

        if self._frozen:
            issues.append("frozen")

        try:
            self.validate()
        except Exception as exc:
            issues.append(str(exc))

        return {
            "healthy": len(issues) == 0,
            "status": (
                "healthy"
                if not issues
                else "degraded"
            ),
            "issues": issues,
            "revision": self._revision,
            "dirty": self._dirty,
        }


    def dump(
        self,
    ) -> dict[str, Any]:
        """
        Dump complete histogram state.

        Returns
        -------
        dict[str, Any]
        """

        return {
            "name": self.name,
            "metric_type": "histogram",
            "value": self.value,
            "count": self._count,
            "sum": self._sum,
            "min": self._min,
            "max": self._max,
            "mean": self.mean,
            "buckets": list(self._buckets),
            "bucket_counts": self.bucket_counts(),
            "labels": self.labels.to_dict(),
            "attributes": self.attributes.to_dict(),
            "metadata": self.metadata.to_dict(),
            "revision": self._revision,
            "dirty": self._dirty,
            "enabled": self._enabled,
            "frozen": self._frozen,
            "closed": self._closed,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


    def inspect(
        self,
    ) -> dict[str, Any]:
        """
        Developer inspection helper.

        Returns
        -------
        dict[str, Any]
        """

        return {
            "class": self.__class__.__name__,
            "id": str(self.id),
            "descriptor": self.descriptor.qualified_name,
            "statistics": self.statistics(),
            "health": self.health(),
        }
    # ======================================================
    # Part 8. Serialization
    # ======================================================

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Serialize this histogram to a dictionary.

        Returns
        -------
        dict[str, Any]
        """

        return {
            "name": self.name,
            "metric_type": "histogram",
            "buckets": list(self._buckets),
            "bucket_counts": list(self._bucket_counts),
            "values": list(self._values),
            "count": self._count,
            "sum": self._sum,
            "min": self._min,
            "max": self._max,
            "revision": self._revision,
            "dirty": self._dirty,
            "enabled": self._enabled,
            "frozen": self._frozen,
            "closed": self._closed,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "labels": self.labels.to_dict(),
            "attributes": self.attributes.to_dict(),
            "metadata": self.metadata.to_dict(),
        }


    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "Histogram":
        """
        Restore a Histogram from a dictionary.

        Parameters
        ----------
        data
            Serialized histogram.

        Returns
        -------
        Histogram
        """

        from .attributes import MetricAttributes
        from .descriptor import MetricDescriptor
        from .labels import MetricLabels
        from .metadata import MetricMetadata

        descriptor = MetricDescriptor(
            name=data["name"],
            metric_type="histogram",
            metadata=MetricMetadata.from_dict(
                data.get("metadata", {})
            ),
        )

        histogram = cls(
            descriptor=descriptor,
            buckets=data.get("buckets"),
            labels=MetricLabels.from_dict(
                data.get("labels", {})
            ),
            attributes=MetricAttributes.from_dict(
                data.get("attributes", {})
            ),
        )

        histogram._bucket_counts = list(
            data.get("bucket_counts", [])
        )

        histogram._values = list(
            data.get("values", [])
        )

        histogram._count = int(
            data.get("count", 0)
        )

        histogram._sum = float(
            data.get("sum", 0.0)
        )

        histogram._min = data.get("min")

        histogram._max = data.get("max")

        histogram._revision = int(
            data.get("revision", 0)
        )

        histogram._dirty = bool(
            data.get("dirty", False)
        )

        histogram._enabled = bool(
            data.get("enabled", True)
        )

        histogram._frozen = bool(
            data.get("frozen", False)
        )

        histogram._closed = bool(
            data.get("closed", False)
        )

        return histogram


    def to_json(
        self,
        *,
        indent: int | None = 2,
    ) -> str:
        """
        Serialize this histogram to JSON.

        Returns
        -------
        str
        """

        import json

        return json.dumps(
            self.to_dict(),
            indent=indent,
            ensure_ascii=False,
            sort_keys=True,
        )


    @classmethod
    def from_json(
        cls,
        payload: str,
    ) -> "Histogram":
        """
        Restore a Histogram from JSON.

        Parameters
        ----------
        payload
            JSON string.

        Returns
        -------
        Histogram
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
        Export histogram in Prometheus exposition format.

        Returns
        -------
        str
        """

        lines: list[str] = []

        metric_name = self.name

        label_items = self.labels.to_dict()

        # Bucket series
        cumulative = 0

        for bound, count in zip(
            self._buckets,
            self._bucket_counts,
        ):
            cumulative += count

            labels = dict(label_items)
            labels["le"] = str(bound)

            label_str = ",".join(
                f'{k}="{v}"'
                for k, v in sorted(labels.items())
            )

            lines.append(
                f'{metric_name}_bucket{{{label_str}}} {cumulative}'
            )

        # +Inf bucket
        labels = dict(label_items)
        labels["le"] = "+Inf"

        label_str = ",".join(
            f'{k}="{v}"'
            for k, v in sorted(labels.items())
        )

        lines.append(
            f'{metric_name}_bucket{{{label_str}}} {self._count}'
        )

        lines.append(
            f"{metric_name}_sum {self._sum}"
        )

        lines.append(
            f"{metric_name}_count {self._count}"
        )

        return "\n".join(lines)


    def otel(
        self,
    ) -> dict[str, Any]:
        """
        Export histogram in an OpenTelemetry-friendly format.

        Returns
        -------
        dict[str, Any]
        """

        return {
            "name": self.name,
            "type": "histogram",
            "count": self._count,
            "sum": self._sum,
            "min": self._min,
            "max": self._max,
            "boundaries": list(self._buckets),
            "bucket_counts": list(self._bucket_counts),
            "attributes": self.attributes.to_dict(),
            "labels": self.labels.to_dict(),
            "metadata": self.metadata.to_dict(),
            "timestamp": self.updated_at.isoformat(),
        }


    def csv(
        self,
    ) -> list[Any]:
        """
        Export histogram as a CSV row.

        Returns
        -------
        list[Any]
        """

        return [
            self.name,
            "histogram",
            self._count,
            self._sum,
            self._min,
            self._max,
            self.mean,
            ";".join(
                map(str, self._buckets)
            ),
            ";".join(
                map(str, self._bucket_counts)
            ),
            self.updated_at.isoformat(),
        ]
    # ======================================================
    # Part 10. Final Polish
    # ======================================================

    def __repr__(
        self,
    ) -> str:
        """
        Developer-friendly representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"count={self._count}, "
            f"sum={self._sum}, "
            f"min={self._min}, "
            f"max={self._max}, "
            f"buckets={len(self._buckets)}, "
            f"enabled={self._enabled}, "
            f"frozen={self._frozen}, "
            f"closed={self._closed})"
        )


    def __str__(
        self,
    ) -> str:
        """
        Human-readable summary.
        """

        return (
            f"{self.name}: "
            f"count={self._count}, "
            f"sum={self._sum}, "
            f"mean={self.mean}"
        )


    def __len__(
        self,
    ) -> int:
        """
        Number of recorded observations.
        """

        return self._count


    def __bool__(
        self,
    ) -> bool:
        """
        Histogram is truthy if it contains observations.
        """

        return self._count > 0


    # ======================================================
    # Compatibility
    # ======================================================

    @property
    def total(
        self,
    ) -> float:
        """
        Compatibility alias for sum().
        """

        return self._sum


    @property
    def observations(
        self,
    ) -> int:
        """
        Compatibility alias for count().
        """

        return self._count


    @property
    def sample_count(
        self,
    ) -> int:
        """
        Compatibility alias for count().
        """

        return self._count


    @property
    def bucket_total(
        self,
    ) -> list[int]:
        """
        Compatibility alias for bucket_counts().
        """

        return list(self._bucket_counts)


    @property
    def values(
        self,
    ) -> list[float]:
        """
        Return a copy of all recorded values.
        """

        return list(self._values)                                                                                        
"""
SciOS-NG Histogram Metric
=========================

Histogram collects a distribution of observed numeric values.

Responsibilities
-----------------
- Record observations.
- Calculate distribution statistics.
- Support configurable buckets.
- Provide snapshots.
- Restore snapshots.
- Support reset lifecycle.
- Provide thread-safe observation.
- Integrate with Metric base model.

Python 3.11+
"""

from __future__ import annotations

from copy import deepcopy
from threading import RLock
from typing import Any, Iterable

from .metric import Metric


__all__ = [
    "Histogram",
]


# ==============================================================================
# Histogram Metric
# ==============================================================================


class Histogram(Metric):
    """
    Histogram metric.

    A histogram records a sequence of numeric observations and exposes
    distribution statistics together with optional bucket information.

    Parameters
    ----------
    name:
        Histogram metric name.

    value:
        Optional initial observation. ``0`` is treated as "no initial
        observation" for backward compatibility with the previous API.

    buckets:
        Optional bucket upper bounds. Values are assigned to the first
        bucket whose upper bound is greater than or equal to the value.

        Example::

            Histogram(
                "latency",
                buckets=[0.1, 0.5, 1.0],
            )

        produces the conceptual buckets::

            <= 0.1
            <= 0.5
            <= 1.0
            +Inf

    Notes
    -----
    Histogram observations are protected by an ``RLock`` so recording
    from multiple threads is safe.
    """

    # ==========================================================================
    # Initialization
    # ==========================================================================

    def __init__(
        self,
        name: str,
        value: int | float = 0,
        *,
        buckets: Iterable[int | float] | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Create a histogram metric.
        """

        super().__init__(
            name=name,
            **kwargs,
        )

        self._lock = RLock()

        self._values: list[float] = []

        self._buckets: tuple[float, ...] = self._normalize_buckets(
            buckets
        )

        self._bucket_counts: list[int] = [
            0
            for _ in self._buckets
        ]

        # +Inf bucket.
        self._overflow_count = 0

        # Preserve historical constructor semantics:
        # value=0 means an empty histogram.
        if value != 0:
            self.observe(value)

    # ==========================================================================
    # Bucket normalization
    # ==========================================================================

    @staticmethod
    def _normalize_buckets(
        buckets: Iterable[int | float] | None,
    ) -> tuple[float, ...]:
        """
        Normalize and validate bucket boundaries.
        """

        if buckets is None:
            return ()

        normalized = tuple(
            float(boundary)
            for boundary in buckets
        )

        if any(
            normalized[index] >= normalized[index + 1]
            for index in range(len(normalized) - 1)
        ):
            raise ValueError(
                "Histogram buckets must be strictly increasing."
            )

        return normalized

    # ==========================================================================
    # Observation API
    # ==========================================================================

    def observe(
        self,
        value: int | float,
    ) -> float:
        """
        Record one histogram observation.

        Parameters
        ----------
        value:
            Numeric observation.

        Returns
        -------
        float
            Normalized observation value.
        """

        normalized = float(value)

        with self._lock:
            self._values.append(
                normalized
            )

            self._record_bucket(
                normalized
            )

            self.touch()

        return normalized

    add = observe

    # ==========================================================================
    # Bucket API
    # ==========================================================================

    @property
    def buckets(
        self,
    ) -> tuple[float, ...]:
        """
        Return configured bucket boundaries.
        """

        with self._lock:
            return tuple(
                self._buckets
            )

    @property
    def bucket_counts(
        self,
    ) -> tuple[int, ...]:
        """
        Return counts for configured finite buckets.

        The returned tuple corresponds one-to-one with ``buckets``.
        """

        with self._lock:
            return tuple(
                self._bucket_counts
            )

    def bucket_count(
        self,
        boundary: int | float,
    ) -> int:
        """
        Return the number of observations assigned to a bucket.

        Parameters
        ----------
        boundary:
            The configured bucket upper bound.

        Returns
        -------
        int
            Number of observations whose value is less than or equal
            to the specified bucket boundary.

        Raises
        ------
        ValueError
            If ``boundary`` is not one of the configured buckets.

        Examples
        --------
        >>> histogram = Histogram(
        ...     "request_duration",
        ...     buckets=[10, 50, 100],
        ... )
        >>> histogram.observe(7)
        7.0
        >>> histogram.observe(25)
        25.0
        >>> histogram.observe(80)
        80.0
        >>> histogram.bucket_count(10)
        1
        >>> histogram.bucket_count(50)
        2
        >>> histogram.bucket_count(100)
        3
        """

        normalized = float(
            boundary
        )

        with self._lock:
            try:
                index = self._buckets.index(
                    normalized
                )
            except ValueError as exc:
                raise ValueError(
                    f"Unknown histogram bucket boundary: {boundary!r}"
                ) from exc

            return self._bucket_counts[index]

    @property
    def overflow_count(
        self,
    ) -> int:
        """
        Return the number of observations above the final bucket.
        """

        with self._lock:
            return self._overflow_count


    @property
    def buckets(
        self,
    ) -> tuple[float, ...]:
        """
        Return configured bucket boundaries.
        """

        with self._lock:
            return tuple(
                self._buckets
            )

    @property
    def bucket_counts(
        self,
    ) -> tuple[int, ...]:
        """
        Return counts for configured finite buckets.

        The returned tuple corresponds one-to-one with ``buckets``.
        """

        with self._lock:
            return tuple(
                self._bucket_counts
            )

    @property
    def overflow_count(
        self,
    ) -> int:
        """
        Return the number of observations above the final bucket.
        """

        with self._lock:
            return self._overflow_count

    def _record_bucket(
        self,
        value: float,
    ) -> None:
        """
        Assign one observation to a bucket.

        The caller must hold ``self._lock``.
        """

        for index, boundary in enumerate(self._buckets):
            if value <= boundary:
                self._bucket_counts[index] += 1
                return

        self._overflow_count += 1

    def _calculate_bucket_counts(
        self,
        values: Iterable[float],
    ) -> tuple[list[int], int]:
        """
        Calculate bucket counts for an arbitrary value sequence.
        """

        counts = [
            0
            for _ in self._buckets
        ]

        overflow = 0

        for value in values:
            assigned = False

            for index, boundary in enumerate(self._buckets):
                if value <= boundary:
                    counts[index] += 1
                    assigned = True
                    break

            if not assigned:
                overflow += 1

        return counts, overflow

    # ==========================================================================
    # Count
    # ==========================================================================

    @property
    def count(
        self,
    ) -> int:
        """
        Return the number of observations.
        """

        with self._lock:
            return len(
                self._values
            )

    # ==========================================================================
    # Sum
    # ==========================================================================

    @property
    def total(
        self,
    ) -> float:
        """
        Return the sum of all observations.
        """

        with self._lock:
            return float(
                sum(
                    self._values
                )
            )

    @property
    def sum(
        self,
    ) -> float:
        """
        Return the sum of all observations.

        ``sum`` is intentionally a property because the public metrics
        API treats aggregate values as attributes.
        """

        return self.total

    # ==========================================================================
    # Average
    # ==========================================================================

    @property
    def average(
        self,
    ) -> float:
        """
        Return the arithmetic mean.

        Returns
        -------
        float
            Mean value, or ``0.0`` for an empty histogram.
        """

        with self._lock:
            if not self._values:
                return 0.0

            return (
                float(sum(self._values))
                /
                len(self._values)
            )

    @property
    def mean(
        self,
    ) -> float:
        """
        Alias for ``average``.
        """

        return self.average

    # ==========================================================================
    # Minimum
    # ==========================================================================

    @property
    def minimum(
        self,
    ) -> float | None:
        """
        Return the minimum observation.
        """

        with self._lock:
            if not self._values:
                return None

            return min(
                self._values
            )

    @property
    def min(
        self,
    ) -> float | None:
        """
        Alias for ``minimum``.
        """

        return self.minimum

    # ==========================================================================
    # Maximum
    # ==========================================================================

    @property
    def maximum(
        self,
    ) -> float | None:
        """
        Return the maximum observation.
        """

        with self._lock:
            if not self._values:
                return None

            return max(
                self._values
            )

    @property
    def max(
        self,
    ) -> float | None:
        """
        Alias for ``maximum``.
        """

        return self.maximum

    # ==========================================================================
    # Values API
    # ==========================================================================

    @property
    def values(
        self,
    ) -> list[float]:
        """
        Return a detached copy of all observations.
        """

        with self._lock:
            return list(
                self._values
            )

    # ==========================================================================
    # Lifecycle
    # ==========================================================================

    def reset(
        self,
    ) -> None:
        """
        Clear all observations and bucket counts.
        """

        with self._lock:
            self._values.clear()

            for index in range(
                len(self._bucket_counts)
            ):
                self._bucket_counts[index] = 0

            self._overflow_count = 0

            self.touch()

    # ==========================================================================
    # Snapshot
    # ==========================================================================

    def snapshot(
        self,
    ) -> dict[str, Any]:
        """
        Export histogram state.

        The returned dictionary is fully detached from internal state.
        """

        with self._lock:
            values = list(
                self._values
            )

            bucket_counts = list(
                self._bucket_counts
            )

            buckets = list(
                self._buckets
            )

            overflow_count = self._overflow_count

        count = len(
            values
        )

        total = float(
            sum(values)
        )

        average = (
            total / count
            if count
            else 0.0
        )

        minimum = (
            min(values)
            if values
            else None
        )

        maximum = (
            max(values)
            if values
            else None
        )

        return {
            "name": self.name,
            "type": "histogram",
            "values": values,
            "count": count,
            "sum": total,
            "average": average,
            "min": minimum,
            "max": maximum,
            "buckets": buckets,
            "bucket_counts": bucket_counts,
            "overflow_count": overflow_count,
            "labels": dict(
                self.labels
            ),
        }

    # ==========================================================================
    # Restore
    # ==========================================================================

    def restore(
        self,
        snapshot: dict[str, Any],
    ) -> "Histogram":
        """
        Restore histogram state from a snapshot.

        Existing observations are replaced rather than appended.
        """

        if not isinstance(
            snapshot,
            dict,
        ):
            raise TypeError(
                "Histogram snapshot must be a dictionary."
            )

        values = snapshot.get(
            "values",
            [],
        )

        if values is None:
            values = []

        if not isinstance(
            values,
            (list, tuple),
        ):
            raise TypeError(
                "Histogram snapshot 'values' must be a list or tuple."
            )

        normalized_values = [
            float(value)
            for value in values
        ]

        snapshot_buckets = snapshot.get(
            "buckets",
            None,
        )

        with self._lock:
            if snapshot_buckets is not None:
                self._buckets = self._normalize_buckets(
                    snapshot_buckets
                )

            self._values = normalized_values

            (
                self._bucket_counts,
                self._overflow_count,
            ) = self._calculate_bucket_counts(
                self._values
            )

            # Restore labels when present.
            if "labels" in snapshot:
                labels = snapshot["labels"]

                try:
                    self._labels = dict(
                        labels
                    )
                except (TypeError, ValueError) as exc:
                    raise TypeError(
                        "Histogram snapshot 'labels' must be mapping-like."
                    ) from exc

            self.touch()

        return self

    # ==========================================================================
    # Serialization
    # ==========================================================================

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Serialize histogram state.
        """

        return self.snapshot()

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "Histogram":
        """
        Construct a histogram from serialized state.
        """

        if not isinstance(
            data,
            dict,
        ):
            raise TypeError(
                "Histogram data must be a dictionary."
            )

        histogram = cls(
            name=str(
                data.get(
                    "name",
                    "",
                )
            ),
            buckets=data.get(
                "buckets",
                None,
            ),
        )

        histogram.restore(
            data
        )

        return histogram

    # ==========================================================================
    # Copy
    # ==========================================================================

    def copy(
        self,
    ) -> "Histogram":
        """
        Create an independent histogram copy.
        """

        with self._lock:
            snapshot = self.snapshot()

        return type(self).from_dict(
            snapshot
        )

    # ==========================================================================
    # Numeric Protocol
    # ==========================================================================

    def __float__(
        self,
    ) -> float:
        """
        Return the histogram total as a float.
        """

        return self.total

    # ==========================================================================
    # Representation
    # ==========================================================================

    def __repr__(
        self,
    ) -> str:
        """
        Return a concise histogram representation.
        """

        return (
            "Histogram("
            f"name={self.name!r}, "
            f"count={self.count}, "
            f"sum={self.sum}, "
            f"labels={self.labels!r}"
            ")"
        )

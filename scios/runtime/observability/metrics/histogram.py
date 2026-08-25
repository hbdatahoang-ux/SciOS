"""
SciOS-NG Histogram Metric
=========================

Histogram collects a distribution of observed values.

Responsibilities
-----------------
- Record observations.
- Calculate distribution statistics.
- Provide snapshots.
- Support reset lifecycle.
- Integrate with Metric base model.

Python 3.11+
"""

from __future__ import annotations


from copy import deepcopy
from typing import Any


from .metric import Metric


__all__ = [
    "Histogram",
]


# ==========================================================
# Histogram Metric
# ==========================================================


class Histogram(Metric):
    """
    Histogram metric.

    A histogram records a sequence of numeric observations and
    exposes basic distribution statistics.

    Examples
    --------

    hist = Histogram(
        name="request_latency_ms",
    )

    hist.observe(12.5)
    hist.observe(18.1)

    print(hist.count)
    print(hist.average())
    """

    # ======================================================
    # Initialization
    # ======================================================

    def __init__(
        self,
        name: str,
        value: int | float = 0,
        **kwargs: Any,
    ):
        """
        Create histogram metric.

        Parameters
        ----------
        name:
            Histogram metric name.

        value:
            Optional initial observation.

        kwargs:
            Extra metric metadata accepted by ``Metric``.
        """

        super().__init__(
            name=name,
            **kwargs,
        )

        self._values: list[float] = []

        if value != 0:
            self.observe(value)

    # ======================================================
    # Observation API
    # ======================================================

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

        value = float(value)

        self._values.append(
            value
        )

        self.touch()

        return value

    add = observe

    # ======================================================
    # Count
    # ======================================================

    @property
    def count(
        self,
    ) -> int:
        """
        Return the number of observations.
        """

        return len(
            self._values
        )

    # ======================================================
    # Sum
    # ======================================================

    @property
    def total(
        self,
    ) -> float:
        """
        Return the sum of all observations.
        """

        return float(
            sum(
                self._values
            )
        )

    # ======================================================
    # Compatibility Sum API
    # ======================================================

    def sum(
        self,
    ) -> float:
        """
        Return the sum of observations.

        Kept as a method for compatibility with existing
        histogram callers.
        """

        return self.total

    # ======================================================
    # Average
    # ======================================================

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

        if not self._values:
            return 0.0

        return (
            self.total
            /
            self.count
        )

    mean = average

    # ======================================================
    # Minimum
    # ======================================================

    def minimum(
        self,
    ) -> float | None:
        """
        Return the minimum observation.
        """

        if not self._values:
            return None

        return min(
            self._values
        )

    min = minimum

    # ======================================================
    # Maximum
    # ======================================================

    def maximum(
        self,
    ) -> float | None:
        """
        Return the maximum observation.
        """

        if not self._values:
            return None

        return max(
            self._values
        )

    max = maximum

    # ======================================================
    # Values API
    # ======================================================

    @property
    def values(
        self,
    ) -> list[float]:
        """
        Return a copy of all observations.
        """

        return list(
            self._values
        )

    # ======================================================
    # Lifecycle
    # ======================================================

    def reset(
        self,
    ) -> None:
        """
        Clear all histogram observations.
        """

        self._values.clear()

        self.touch()

    # ======================================================
    # Snapshot
    # ======================================================

    def snapshot(
        self,
    ) -> dict[str, Any]:
        """
        Export histogram state.

        The returned dictionary is detached from the internal
        observation list.
        """

        return {
            "name": self.name,
            "type": "histogram",
            "values": self.values,
            "count": self.count,
            "sum": self.total,
            "average": self.average(),
            "min": self.minimum(),
            "max": self.maximum(),
            "labels": dict(
                self.labels
            ),
        }

    # ======================================================
    # Serialization
    # ======================================================

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Serialize histogram state.
        """

        return self.snapshot()

    # ======================================================
    # Copy
    # ======================================================

    def copy(
        self,
    ) -> "Histogram":
        """
        Create an independent histogram copy.
        """

        return deepcopy(
            self
        )

    # ======================================================
    # Numeric Protocol
    # ======================================================

    def __float__(
        self,
    ) -> float:
        """
        Return the histogram total as a float.
        """

        return self.total

    # ======================================================
    # Representation
    # ======================================================

    def __repr__(
        self,
    ) -> str:
        return (
            "Histogram("
            f"name={self.name!r}, "
            f"count={self.count}, "
            f"sum={self.total}, "
            f"labels={self.labels!r}"
            ")"
        )

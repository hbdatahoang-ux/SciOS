"""
SciOS Runtime Metrics Counter
=============================

Counter metric implementation.

Responsibilities
-----------------
- Count monotonically increasing events.
- Provide increment API.
- Support labels and metadata through Metric.
- Support snapshots.
- Support serialization.
- Integrate with the Metric base model.

Python 3.11+
"""

from __future__ import annotations

from typing import Any

from .metric import Metric


__all__ = [
    "Counter",
]


# ==========================================================
# Counter Metric
# ==========================================================


class Counter(Metric):
    """
    Monotonic counter metric.

    A Counter represents a cumulative numeric value that may
    increase during its lifetime.

    Examples
    --------
    Count executed tasks::

        counter = Counter("tasks_total")
        counter.inc()

    Increment by a specific amount::

        counter.inc(3)

    Read the current value::

        value = counter.value

    Notes
    -----
    A Counter does not support negative increments.

    ``reset()`` is intentionally provided for runtime restart,
    testing, and snapshot restoration. It is not considered a
    normal counter operation.
    """

    # ======================================================
    # Initialization
    # ======================================================

    def __init__(
        self,
        name: str,
        value: int | float = 0.0,
        **kwargs: Any,
    ) -> None:
        """
        Create a counter metric.

        Parameters
        ----------
        name:
            Metric name.

        value:
            Initial counter value. Must be non-negative.

        kwargs:
            Additional arguments forwarded to ``Metric``.
        """

        if value < 0:
            raise ValueError(
                "Counter value cannot be negative"
            )

        super().__init__(
            name=name,
            **kwargs,
        )

        self._value: float = float(value)

    # ======================================================
    # Value
    # ======================================================

    @property
    def value(
        self,
    ) -> float:
        """
        Return the current counter value.

        ``value`` is intentionally a property so callers use::

            counter.value

        rather than::

            counter.value()
        """

        return self._value

    # ======================================================
    # Increment
    # ======================================================

    def inc(
        self,
        amount: int | float = 1.0,
    ) -> float:
        """
        Increase the counter.

        Parameters
        ----------
        amount:
            Non-negative increment amount.

        Returns
        -------
        float
            The new counter value.

        Raises
        ------
        ValueError
            If ``amount`` is negative.
        """

        amount = float(amount)

        if amount < 0:
            raise ValueError(
                "Counter cannot decrease"
            )

        self._value += amount

        self.touch()

        return self._value

    # ======================================================
    # Alias
    # ======================================================

    increment = inc

    # ======================================================
    # Reset
    # ======================================================

    def reset(
        self,
    ) -> float:
        """
        Reset the counter to zero.

        Returns
        -------
        float
            The new counter value.
        """

        self._value = 0.0

        self.touch()

        return self._value

    # ======================================================
    # Snapshot
    # ======================================================

    def snapshot(
        self,
    ) -> dict[str, Any]:
        """
        Create a serializable snapshot of the counter.

        The snapshot is detached from the live metric state.
        """

        return {
            "name": self.name,
            "value": self._value,
            "labels": dict(self.labels),
            "metric_type": "counter",
        }

    # ======================================================
    # Serialization
    # ======================================================

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Serialize the counter.

        The returned dictionary is independent from the
        internal metric state.
        """

        return {
            "name": self.name,
            "type": "counter",
            "value": self._value,
            "labels": dict(self.labels),
        }

    # ======================================================
    # Numeric Protocols
    # ======================================================

    def __float__(
        self,
    ) -> float:
        """
        Convert the counter to ``float``.
        """

        return self._value

    def __int__(
        self,
    ) -> int:
        """
        Convert the counter to ``int``.
        """

        return int(self._value)

    # ======================================================
    # Representation
    # ======================================================

    def __repr__(
        self,
    ) -> str:
        """
        Return a concise debug representation.
        """

        return (
            "Counter("
            f"name={self.name!r}, "
            f"value={self._value!r}, "
            f"labels={self.labels!r}"
            ")"
        )
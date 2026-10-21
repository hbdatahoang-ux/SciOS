"""
SciOS Runtime Gauge Metric
==========================

Gauge metric implementation.

A Gauge represents a value that can:

- increase
- decrease
- be set directly
- be reset

Examples
--------

    gauge = Gauge(
        name="cpu_usage",
        value=25.0,
    )

    gauge.set(42.5)

    gauge.increment(5)

    gauge.decrement(2)

Python 3.11+
"""

from __future__ import annotations

from typing import Any

from .labels import MetricLabels
from .metric import Metric


__all__ = [
    "Gauge",
]


# ==========================================================
# Gauge Metric
# ==========================================================


class Gauge(Metric):
    """
    Mutable numeric metric.

    Unlike Counter:

    - Counter only increases.
    - Gauge can move up and down.
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
        Create gauge metric.

        Parameters
        ----------
        name:
            Metric name.

        value:
            Initial gauge value.

        kwargs:
            Extra metadata accepted by ``Metric``.
        """

        super().__init__(
            name=name,
            **kwargs,
        )

        self._value: float = float(value)

    # ======================================================
    # Value
    # ======================================================

    @property
    def value(self) -> float:
        """
        Return the current gauge value.
        """

        return self._value

    # ======================================================
    # Set API
    # ======================================================

    def set(
        self,
        value: int | float,
    ) -> float:
        """
        Set the gauge to an absolute value.

        Parameters
        ----------
        value:
            New gauge value.

        Returns
        -------
        float
            Updated gauge value.
        """

        self._value = float(value)

        self.touch()

        return self._value

    # ======================================================
    # Increment API
    # ======================================================

    def increment(
        self,
        amount: int | float = 1,
    ) -> float:
        """
        Increase the gauge value.

        Parameters
        ----------
        amount:
            Amount to add.

        Returns
        -------
        float
            Updated gauge value.
        """

        self._value += float(amount)

        self.touch()

        return self._value

    # Short alias.
    inc = increment

    # ======================================================
    # Decrement API
    # ======================================================

    def decrement(
        self,
        amount: int | float = 1,
    ) -> float:
        """
        Decrease the gauge value.

        Parameters
        ----------
        amount:
            Amount to subtract.

        Returns
        -------
        float
            Updated gauge value.
        """

        self._value -= float(amount)

        self.touch()

        return self._value

    # Short alias.
    dec = decrement

    # ======================================================
    # Add / Subtract
    # ======================================================

    def add(
        self,
        amount: int | float,
    ) -> float:
        """
        Add a value to the gauge.

        This is an alias for ``increment()``.
        """

        return self.increment(
            amount
        )

    def subtract(
        self,
        amount: int | float,
    ) -> float:
        """
        Subtract a value from the gauge.

        This is an alias for ``decrement()``.
        """

        return self.decrement(
            amount
        )

    # Short alias.
    sub = subtract

    # ======================================================
    # Reset API
    # ======================================================

    def reset(
        self,
    ) -> float:
        """
        Reset the gauge value to zero.

        Returns
        -------
        float
            The new gauge value.
        """

        self._value = 0.0

        self.touch()

        return self._value

    # ======================================================
    # Snapshot API
    # ======================================================

    def snapshot(
        self,
    ) -> dict[str, Any]:
        """
        Create a serializable gauge snapshot.
        """

        snapshot = super().snapshot()

        snapshot.update(
            {
                "type": "gauge",
                "value": self._value,
            }
        )

        return snapshot
    # ======================================================
    # Restore API
    # ======================================================

    def restore(
        self,
        snapshot: dict[str, Any],
    ) -> "Gauge":
        """
        Restore gauge state from a snapshot.
        """

        if not isinstance(snapshot, dict):
            raise TypeError(
                "Gauge snapshot must be a dictionary"
            )

        if snapshot.get("type") not in (None, "gauge"):
            raise ValueError(
                "Invalid snapshot type for Gauge"
            )

        value = snapshot.get("value")

        if value is None:
            raise ValueError(
                "Gauge snapshot is missing 'value'"
            )

        self._value = float(value)

        if "labels" in snapshot:
            self.labels = MetricLabels(
                **dict(snapshot["labels"])
            )

        if "metadata" in snapshot:
            self.metadata = dict(
                snapshot["metadata"]
            )

        if "enabled" in snapshot:
            self.enabled = bool(
                snapshot["enabled"]
            )

        if "unit" in snapshot:
            self.unit = str(
                snapshot["unit"]
            )

        self.touch()

        return self


    # ======================================================
    # Serialization
    # ======================================================

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Serialize the gauge to a dictionary.
        """

        return self.snapshot()

    # ======================================================
    # Numeric Protocols
    # ======================================================

    def __float__(
        self,
    ) -> float:
        """
        Convert gauge value to float.
        """

        return float(
            self._value
        )

    def __int__(
        self,
    ) -> int:
        """
        Convert gauge value to int.
        """

        return int(
            self._value
        )

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
            "Gauge("
            f"name={self.name!r}, "
            f"value={self._value!r}, "
            f"labels={self.labels!r}"
            ")"
        )
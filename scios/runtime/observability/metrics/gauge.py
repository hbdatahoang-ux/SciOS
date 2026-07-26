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
            Initial value.

        kwargs:
            Extra metric metadata.
        """


        super().__init__(
            name=name,
            value=float(value),
            **kwargs,
        )



    # ======================================================
    # Set API
    # ======================================================


    def set(
        self,
        value: int | float,
    ) -> float:
        """
        Set absolute gauge value.
        """

        self.update(
            float(value)
        )


        return self.value



    # ======================================================
    # Increment API
    # ======================================================


    def increment(
        self,
        amount: int | float = 1,
    ) -> float:
        """
        Increase gauge value.
        """

        self.update(
            self.value + float(amount)
        )


        return self.value



    inc = increment



    # ======================================================
    # Decrement API
    # ======================================================


    def decrement(
        self,
        amount: int | float = 1,
    ) -> float:
        """
        Decrease gauge value.
        """

        self.update(
            self.value - float(amount)
        )


        return self.value



    dec = decrement



    # ======================================================
    # Add / Subtract
    # ======================================================


    def add(
        self,
        amount: int | float,
    ) -> float:
        """
        Add value.
        """

        return self.increment(
            amount
        )



    def subtract(
        self,
        amount: int | float,
    ) -> float:
        """
        Subtract value.
        """

        return self.decrement(
            amount
        )



    sub = subtract



    # ======================================================
    # Reset API
    # ======================================================


    def reset(
        self,
    ) -> float:
        """
        Reset gauge value to zero.
        """

        self.update(
            0.0
        )


        return self.value



    # ======================================================
    # Snapshot API
    # ======================================================


    def snapshot(
        self,
    ) -> dict[str, Any]:
        """
        Export gauge snapshot.
        """

        data = super().to_dict()


        data["type"] = "gauge"


        return data



    # ======================================================
    # Serialization
    # ======================================================


    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Serialize gauge.
        """

        data = super().to_dict()


        data["type"] = "gauge"


        return data



    # ======================================================
    # Representation
    # ======================================================


    def __repr__(
        self,
    ) -> str:

        return (
            "Gauge("
            f"name={self.name!r}, "
            f"value={self.value}"
            ")"
        )
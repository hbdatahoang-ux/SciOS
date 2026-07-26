"""
SciOS Runtime Metrics Counter
=============================

Counter metric implementation.

Responsibilities
-----------------
- Count monotonically increasing events.
- Provide increment/decrement API.
- Support labels.
- Support snapshots.
- Integrate with Metric base model.

Python 3.11+
"""

from __future__ import annotations


from dataclasses import dataclass, field
from typing import Any


from .metric import Metric
from .snapshot import MetricSnapshot



__all__ = [
    "Counter",
]



# ==========================================================
# Counter Metric
# ==========================================================


@dataclass
class Counter(Metric):
    """
    Monotonic counter metric.

    Examples
    --------

    Count executed tasks:

        counter.inc()

    Count failures:

        counter.inc(3)

    """


    # ======================================================
    # Value
    # ======================================================


    _value: float = 0.0



    # ======================================================
    # Configuration
    # ======================================================


    labels: dict[str, str] = field(
        default_factory=dict
    )



    # ======================================================
    # Increment
    # ======================================================


    def inc(
        self,
        amount: float = 1.0,
    ) -> None:
        """
        Increase counter value.

        Parameters
        ----------
        amount:
            Increment amount.

        """

        if amount < 0:

            raise ValueError(
                "Counter cannot decrease"
            )


        self._value += float(
            amount
        )



    # ======================================================
    # Read
    # ======================================================


    def value(
        self,
    ) -> float:
        """
        Current counter value.
        """

        return self._value



    # ======================================================
    # Reset
    # ======================================================


    def reset(
        self,
    ) -> None:
        """
        Reset counter.

        Used by:
        - tests
        - runtime restart
        - snapshot restore

        """

        self._value = 0.0



    # ======================================================
    # Snapshot
    # ======================================================


    def snapshot(
        self,
    ) -> MetricSnapshot:
        """
        Create immutable metric snapshot.
        """

        return MetricSnapshot(

            name=self.name,

            value=self._value,

            labels=dict(
                self.labels
            ),

            metric_type="counter",
        )



    # ======================================================
    # Serialization
    # ======================================================


    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Convert to dictionary.
        """

        return {

            "name":
                self.name,

            "type":
                "counter",

            "value":
                self._value,

            "labels":
                dict(
                    self.labels
                ),
        }



    # ======================================================
    # Protocols
    # ======================================================


    def __float__(
        self,
    ) -> float:

        return float(
            self._value
        )



    def __int__(
        self,
    ) -> int:

        return int(
            self._value
        )



    def __repr__(
        self,
    ) -> str:

        return (

            "Counter("
            f"name={self.name!r}, "
            f"value={self._value}, "
            f"labels={self.labels}"
            ")"

        )
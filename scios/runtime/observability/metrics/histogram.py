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

    Example
    -------

        hist = Histogram(
            name="request_latency_ms"
        )

        hist.observe(12.5)

        hist.observe(18.1)

        print(hist.average())
    """


    def __init__(
        self,
        name: str,
        value: int | float = 0,
        **kwargs: Any,
    ):

        super().__init__(
            name=name,
            value=value,
            **kwargs,
        )


        self._values: list[
            int | float
        ] = []



    # ======================================================
    # Observation API
    # ======================================================


    def observe(
        self,
        value: int | float,
    ) -> int | float:
        """
        Record observation.
        """

        value = float(value)


        self._values.append(
            value
        )


        self.update(
            value
        )


        return value



    add = observe



    # ======================================================
    # Statistics API
    # ======================================================


    def count(
        self,
    ) -> int:
        """
        Number of samples.
        """

        return len(
            self._values
        )



    def sum(
        self,
    ) -> float:
        """
        Sum of observations.
        """

        return float(
            sum(
                self._values
            )
        )



    def average(
        self,
    ) -> float:
        """
        Average value.
        """

        if not self._values:

            return 0.0


        return (
            self.sum()
            /
            self.count()
        )



    mean = average



    def minimum(
        self,
    ) -> float | None:
        """
        Minimum value.
        """

        if not self._values:

            return None


        return min(
            self._values
        )



    min = minimum



    def maximum(
        self,
    ) -> float | None:
        """
        Maximum value.
        """

        if not self._values:

            return None


        return max(
            self._values
        )



    max = maximum



    # ======================================================
    # Value API
    # ======================================================


    @property
    def values(
        self,
    ) -> list[float]:
        """
        Return observations copy.
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
        Clear histogram.
        """

        self._values.clear()


        self.update(
            0
        )



    # ======================================================
    # Snapshot
    # ======================================================


    def snapshot(
        self,
    ) -> dict[str, Any]:
        """
        Export histogram state.
        """

        data = super().snapshot()


        data.update(
            {

                "values":
                    self.values,


                "count":
                    self.count(),


                "sum":
                    self.sum(),


                "average":
                    self.average(),


                "min":
                    self.minimum(),


                "max":
                    self.maximum(),

            }
        )


        return data



    # ======================================================
    # Serialization
    # ======================================================


    def to_dict(
        self,
    ) -> dict[str, Any]:

        data = self.snapshot()


        data["type"] = "histogram"


        return data



    # ======================================================
    # Copy
    # ======================================================


    def copy(
        self,
    ) -> "Histogram":

        return deepcopy(
            self
        )

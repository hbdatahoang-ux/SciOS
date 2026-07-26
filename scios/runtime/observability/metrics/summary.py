"""
SciOS-NG Summary Metric
=======================

Summary metric tracks statistical summaries
of observed values.

Responsibilities
-----------------
- Record observations.
- Track count.
- Track total sum.
- Calculate average.
- Track min/max.
- Provide snapshots.

Python 3.11+
"""

from __future__ import annotations


from copy import deepcopy
from typing import Any


from .metric import Metric



__all__ = [
    "Summary",
]



# ==========================================================
# Summary Metric
# ==========================================================


class Summary(Metric):
    """
    Summary metric.

    Example
    -------

        latency = Summary(
            name="request_latency"
        )

        latency.observe(10)

        latency.observe(20)

        print(
            latency.average()
        )

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


        self._count: int = 0

        self._sum: float = 0.0

        self._min: float | None = None

        self._max: float | None = None



    # ======================================================
    # Observation API
    # ======================================================


    def observe(
        self,
        value: int | float,
    ) -> float:
        """
        Add observation.
        """

        value = float(
            value
        )


        self._count += 1


        self._sum += value


        if self._min is None:

            self._min = value

        else:

            self._min = min(
                self._min,
                value,
            )



        if self._max is None:

            self._max = value

        else:

            self._max = max(
                self._max,
                value,
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
        Number of observations.
        """

        return self._count



    def sum(
        self,
    ) -> float:
        """
        Total accumulated value.
        """

        return self._sum



    def average(
        self,
    ) -> float:
        """
        Average value.
        """

        if self._count == 0:

            return 0.0


        return (
            self._sum
            /
            self._count
        )



    mean = average



    def minimum(
        self,
    ) -> float | None:
        """
        Minimum observed value.
        """

        return self._min



    min = minimum



    def maximum(
        self,
    ) -> float | None:
        """
        Maximum observed value.
        """

        return self._max



    max = maximum



    # ======================================================
    # Properties
    # ======================================================


    @property
    def total(
        self,
    ) -> float:

        return self._sum



    @property
    def samples(
        self,
    ) -> int:

        return self._count



    # ======================================================
    # Lifecycle
    # ======================================================


    def reset(
        self,
    ) -> None:
        """
        Reset summary state.
        """

        self._count = 0

        self._sum = 0.0

        self._min = None

        self._max = None


        self.update(
            0
        )



    # ======================================================
    # Snapshot API
    # ======================================================


    def snapshot(
        self,
    ) -> dict[str, Any]:
        """
        Export summary state.
        """

        data = super().snapshot()


        data.update(
            {

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


        data["type"] = "summary"


        return data



    # ======================================================
    # Copy
    # ======================================================


    def copy(
        self,
    ) -> "Summary":

        return deepcopy(
            self
        )


"""
SciOS-NG Metrics Aggregator
===========================

Metric aggregation engine.

Responsibilities
-----------------
- Combine metric samples.
- Aggregate counters.
- Aggregate gauges.
- Aggregate histograms.
- Produce aggregated snapshots.
- Support runtime observability.

Design
------
Aggregator does NOT know about:

- ExecutionEngine
- Plugins
- Exporters

It only transforms metric data.

Python 3.11+
"""

from __future__ import annotations


from dataclasses import dataclass, field
from typing import Any


from .metric import Metric
from .snapshot import MetricSnapshot



__all__ = [
    "MetricAggregator",
]



# ==========================================================
# Aggregation State
# ==========================================================


@dataclass
class AggregationState:
    """
    Aggregation runtime state.
    """


    samples: int = 0


    metrics: int = 0



# ==========================================================
# Metric Aggregator
# ==========================================================


class MetricAggregator:
    """
    Aggregate runtime metrics.

    Example
    -------

        aggregator = MetricAggregator()

        aggregator.add(
            metric
        )

        snapshot = aggregator.snapshot()

    """



    def __init__(self):

        self.state = AggregationState()


        self._metrics: dict[
            str,
            list[Any]
        ] = {}



    # ======================================================
    # Add Metrics
    # ======================================================


    def add(
        self,
        metric: Metric,
    ) -> None:
        """
        Add metric observation.
        """

        name = metric.name


        if name not in self._metrics:

            self._metrics[name] = []


            self.state.metrics += 1



        self._metrics[name].append(
            metric.value
        )


        self.state.samples += 1



    def add_value(
        self,
        name: str,
        value: Any,
    ) -> None:
        """
        Add raw metric value.
        """

        if name not in self._metrics:

            self._metrics[name] = []

            self.state.metrics += 1



        self._metrics[name].append(
            value
        )


        self.state.samples += 1



    # ======================================================
    # Aggregation
    # ======================================================


    def count(
        self,
        name: str,
    ) -> int:

        return len(
            self._metrics.get(
                name,
                [],
            )
        )



    def sum(
        self,
        name: str,
    ) -> float:

        values = self._metrics.get(
            name,
            [],
        )


        return sum(
            values
        )



    def average(
        self,
        name: str,
    ) -> float:

        values = self._metrics.get(
            name,
            [],
        )


        if not values:

            return 0.0


        return (
            sum(values)
            /
            len(values)
        )



    def minimum(
        self,
        name: str,
    ):

        values = self._metrics.get(
            name,
            [],
        )


        if not values:

            return None


        return min(
            values
        )



    def maximum(
        self,
        name: str,
    ):

        values = self._metrics.get(
            name,
            [],
        )


        if not values:

            return None


        return max(
            values
        )



    # ======================================================
    # Snapshot
    # ======================================================


    def snapshot(
        self,
    ) -> dict[str, Any]:
        """
        Create aggregated snapshot.
        """


        metrics = {}


        for name in self._metrics:

            metrics[name] = {

                "count":
                    self.count(
                        name
                    ),


                "sum":
                    self.sum(
                        name
                    ),


                "average":
                    self.average(
                        name
                    ),


                "min":
                    self.minimum(
                        name
                    ),


                "max":
                    self.maximum(
                        name
                    ),
            }



        return {

            "metrics":
                metrics,


            "samples":
                self.state.samples,


            "metric_count":
                self.state.metrics,
        }



    def report(
        self,
    ) -> dict[str, Any]:
        """
        Alias for snapshot.
        """

        return self.snapshot()



    # ======================================================
    # Query
    # ======================================================


    def get(
        self,
        name: str,
    ) -> list[Any]:
        """
        Return raw samples.
        """

        return list(
            self._metrics.get(
                name,
                [],
            )
        )



    def names(
        self,
    ) -> list[str]:

        return list(
            self._metrics.keys()
        )



    # ======================================================
    # Lifecycle
    # ======================================================


    def reset(
        self,
    ) -> None:
        """
        Clear aggregation data.
        """

        self._metrics.clear()


        self.state = AggregationState()



    # ======================================================
    # Protocols
    # ======================================================


    def __len__(
        self,
    ) -> int:

        return self.state.samples



    def __contains__(
        self,
        name: str,
    ) -> bool:

        return name in self._metrics



    def __repr__(
        self,
    ) -> str:

        return (
            "MetricAggregator("
            f"metrics={self.state.metrics}, "
            f"samples={self.state.samples}"
            ")"
        )
"""
SciOS-NG Metrics Recorder
=========================

Recorder collects metric observations
from runtime components.

Responsibilities
-----------------
- Record metric samples.
- Record execution measurements.
- Forward data to metric registry.
- Provide batch recording.
- Support snapshot export.

Python 3.11+
"""

from __future__ import annotations


from dataclasses import dataclass, field
from time import perf_counter
from typing import Any


from .registry import MetricRegistry



__all__ = [
    "MetricRecorder",
]



# ==========================================================
# Recorder State
# ==========================================================


@dataclass
class RecorderState:
    """
    Internal recorder state.
    """


    total_records: int = 0


    started_at: float = field(
        default_factory=perf_counter
    )



# ==========================================================
# Metric Recorder
# ==========================================================


class MetricRecorder:
    """
    Runtime metric recorder.

    Example
    -------

        recorder = MetricRecorder(
            registry
        )

        recorder.increment(
            "tasks_total"
        )

        recorder.observe(
            "latency",
            0.25
        )

    """



    def __init__(
        self,
        registry: MetricRegistry | None = None,
    ):

        self.registry = (
            registry
            or MetricRegistry()
        )


        self.state = RecorderState()



    # ======================================================
    # Counter Recording
    # ======================================================


    def increment(
        self,
        name: str,
        value: int = 1,
        **labels: Any,
    ):

        """
        Increment counter metric.
        """

        metric = self.registry.get_or_create_counter(
            name,
            **labels,
        )


        result = metric.increment(
            value
        )


        self._record()


        return result



    # ======================================================
    # Gauge Recording
    # ======================================================


    def set(
        self,
        name: str,
        value: int | float,
        **labels: Any,
    ):

        """
        Set gauge value.
        """

        metric = self.registry.get_or_create_gauge(
            name,
            **labels,
        )


        result = metric.set(
            value
        )


        self._record()


        return result



    # ======================================================
    # Histogram Recording
    # ======================================================


    def observe(
        self,
        name: str,
        value: int | float,
        **labels: Any,
    ):

        """
        Record histogram observation.
        """

        metric = self.registry.get_or_create_histogram(
            name,
            **labels,
        )


        result = metric.observe(
            value
        )


        self._record()


        return result



    # ======================================================
    # Timer Recording
    # ======================================================


    def timing(
        self,
        name: str,
        duration: float,
        **labels: Any,
    ):

        """
        Record duration sample.
        """

        return self.observe(
            name,
            duration,
            **labels,
        )



    # ======================================================
    # Batch API
    # ======================================================


    def record(
        self,
        name: str,
        value: Any,
        metric_type: str = "gauge",
        **labels: Any,
    ):

        """
        Generic metric recording API.
        """

        if metric_type == "counter":

            return self.increment(
                name,
                value,
                **labels,
            )


        if metric_type == "histogram":

            return self.observe(
                name,
                value,
                **labels,
            )


        return self.set(
            name,
            value,
            **labels,
        )



    def record_many(
        self,
        samples: list[dict[str, Any]],
    ):

        """
        Batch record metrics.

        Example:

            recorder.record_many(
                [
                    {
                        "name": "cpu",
                        "value": 50
                    }
                ]
            )

        """

        results = []


        for sample in samples:

            results.append(
                self.record(
                    **sample
                )
            )


        return results



    # ======================================================
    # Runtime Helpers
    # ======================================================


    def _record(
        self,
    ):

        self.state.total_records += 1



    # ======================================================
    # Snapshot
    # ======================================================


    def snapshot(
        self,
    ) -> dict[str, Any]:
        """
        Export recorder state.
        """

        elapsed = (
            perf_counter()
            -
            self.state.started_at
        )


        return {

            "total_records":
                self.state.total_records,


            "elapsed":
                elapsed,


            "registry":
                self.registry.snapshot(),
        }



    def reset(
        self,
    ) -> None:
        """
        Reset recorder.
        """

        self.state = RecorderState()


        self.registry.reset()



    # ======================================================
    # Protocols
    # ======================================================


    def __len__(
        self,
    ) -> int:

        return self.state.total_records



    def __bool__(
        self,
    ) -> bool:

        return (
            self.state.total_records > 0
        )



    def __repr__(
        self,
    ) -> str:

        return (
            "MetricRecorder("
            f"records={self.state.total_records}"
            ")"
        )
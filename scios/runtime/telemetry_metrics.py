"""
SciOS Runtime Telemetry Metrics
================================

Core metrics model for SciOS Runtime observability.

Responsibilities
-----------------
- Track execution counters.
- Track running tasks.
- Track latency measurements.
- Calculate throughput.
- Provide exporter-ready snapshots.
- Preserve backward compatibility.

Python 3.11+
"""

from __future__ import annotations


from copy import deepcopy
from dataclasses import dataclass, field
from statistics import mean
from time import monotonic
from typing import Any


__all__ = [
    "TelemetryMetrics",
]



# ==========================================================
# Helpers
# ==========================================================


def now() -> float:
    """
    Monotonic runtime clock.
    """

    return monotonic()



# ==========================================================
# Metrics
# ==========================================================


@dataclass
class TelemetryMetrics:
    """
    Runtime telemetry metrics container.

    Independent from:

    - Engine
    - Worker
    - Hooks
    - Exporters
    """



    # ======================================================
    # Counters
    # ======================================================


    total_tasks: int = 0


    running_tasks: int = 0


    completed_tasks: int = 0


    failed_tasks: int = 0



    # ======================================================
    # Latency
    # ======================================================


    latencies: list[float] = field(
        default_factory=list
    )



    # ======================================================
    # Runtime
    # ======================================================


    started_at: float = field(
        default_factory=now
    )



    # ======================================================
    # Lifecycle
    # ======================================================


    def start_task(self) -> None:
        """
        Called by before_execute.
        """

        self.total_tasks += 1

        self.running_tasks += 1



    def complete_task(
        self,
        latency: float,
    ) -> None:
        """
        Called by execution_completed.
        """

        self.running_tasks = max(
            0,
            self.running_tasks - 1,
        )


        self.completed_tasks += 1


        self._record_latency(
            latency
        )



    def fail_task(
        self,
        latency: float,
    ) -> None:
        """
        Called by execution_failed.
        """

        self.running_tasks = max(
            0,
            self.running_tasks - 1,
        )


        self.failed_tasks += 1


        self._record_latency(
            latency
        )



    # ======================================================
    # Latency
    # ======================================================


    def _record_latency(
        self,
        latency: float,
    ) -> None:


        self.latencies.append(
            max(
                0.0,
                float(latency),
            )
        )



    @property
    def latency_count(self) -> int:

        return len(
            self.latencies
        )



    def average_latency(self) -> float:

        if not self.latencies:

            return 0.0


        return mean(
            self.latencies
        )



    def min_latency(self) -> float:

        if not self.latencies:

            return 0.0


        return min(
            self.latencies
        )



    def max_latency(self) -> float:

        if not self.latencies:

            return 0.0


        return max(
            self.latencies
        )



    # ======================================================
    # Throughput
    # ======================================================


    def elapsed(self) -> float:


        return max(
            monotonic() - self.started_at,
            1e-9,
        )



    def throughput(self) -> float:


        return (
            self.completed_tasks
            /
            self.elapsed()
        )



    # ======================================================
    # Rates
    # ======================================================


    @property
    def success_rate(self) -> float:


        if self.total_tasks == 0:

            return 0.0


        return (
            self.completed_tasks
            /
            self.total_tasks
        )



    @property
    def failure_rate(self) -> float:


        if self.total_tasks == 0:

            return 0.0


        return (
            self.failed_tasks
            /
            self.total_tasks
        )



    # ======================================================
    # Snapshot
    # ======================================================


    def snapshot(
        self,
    ) -> dict[str, Any]:
        """
        Exporter compatible snapshot.

        Includes:

        - New observability schema
        - Legacy compatibility schema
        """

        avg = self.average_latency()

        minimum = self.min_latency()

        maximum = self.max_latency()



        return {


            # ------------------------------
            # Counters
            # ------------------------------

            "total_tasks":
                self.total_tasks,


            "running_tasks":
                self.running_tasks,


            "completed_tasks":
                self.completed_tasks,


            "failed_tasks":
                self.failed_tasks,



            # ------------------------------
            # Rates
            # ------------------------------

            "success_rate":
                self.success_rate,


            "failure_rate":
                self.failure_rate,



            # ------------------------------
            # Legacy latency API
            # ------------------------------

            "average_latency":
                avg,


            "min_latency":
                minimum,


            "max_latency":
                maximum,



            # ------------------------------
            # New latency API
            # ------------------------------

            "latency":
            {

                "count":
                    self.latency_count,


                "avg":
                    avg,


                "min":
                    minimum,


                "max":
                    maximum,
            },



            # ------------------------------
            # Throughput
            # ------------------------------

            "throughput":
                self.throughput(),


            "elapsed":
                self.elapsed(),

        }



    def report(self) -> dict[str, Any]:
        """
        Public reporting API.
        """

        return self.snapshot()



    # ======================================================
    # Reset
    # ======================================================


    def reset(self) -> None:


        self.total_tasks = 0

        self.running_tasks = 0

        self.completed_tasks = 0

        self.failed_tasks = 0


        self.latencies.clear()


        self.started_at = now()



    # ======================================================
    # Copy
    # ======================================================


    def copy(self):

        return deepcopy(
            self
        )



    # ======================================================
    # Status
    # ======================================================


    def status(self):

        return {

            "active": True,


            "total_tasks":
                self.total_tasks,


            "completed_tasks":
                self.completed_tasks,


            "failed_tasks":
                self.failed_tasks,


            "running_tasks":
                self.running_tasks,


        }



    # ======================================================
    # Protocols
    # ======================================================


    def __len__(self):

        return self.total_tasks



    def __bool__(self):

        return self.total_tasks > 0



    def __repr__(self):

        return (
            "TelemetryMetrics("
            f"total={self.total_tasks}, "
            f"running={self.running_tasks}, "
            f"completed={self.completed_tasks}, "
            f"failed={self.failed_tasks}"
            ")"
        )
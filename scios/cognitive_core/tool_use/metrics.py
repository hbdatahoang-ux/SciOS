"""
SciOS Tool Metrics
==================

Production-ready metrics collector for Tool Use.

Features
--------
- Thread safe
- High resolution timing
- Per-tool metrics
- Aggregate metrics
- Snapshot export
- Reset lifecycle
- Backward compatible API

Python 3.11+
"""

from __future__ import annotations


from dataclasses import (
    dataclass,
    asdict,
    field,
)

from threading import Lock

from time import (
    perf_counter,
    time,
)

from typing import Any


__all__ = [
    "ToolMetrics",
    "MetricRecord",
    "Metrics",
]



# ============================================================================
# Per Tool Record
# ============================================================================


@dataclass
class MetricRecord:
    """
    Metrics for a single tool.
    """

    calls: int = 0

    success: int = 0

    failure: int = 0

    total_time: float = 0.0



    @property
    def avg_time(
        self,
    ) -> float:

        if self.calls == 0:
            return 0.0

        return self.total_time / self.calls



    @property
    def success_rate(
        self,
    ) -> float:

        if self.calls == 0:
            return 0.0

        return self.success / self.calls



    @property
    def failure_rate(
        self,
    ) -> float:

        if self.calls == 0:
            return 0.0

        return self.failure / self.calls



    def to_dict(
        self,
    ) -> dict[str, Any]:

        data = asdict(self)

        data.update(
            {
                "avg_time": self.avg_time,
                "success_rate": self.success_rate,
                "failure_rate": self.failure_rate,
            }
        )

        return data




# ============================================================================
# Main Metrics Engine
# ============================================================================


@dataclass
class ToolMetrics:
    """
    Global metrics engine.
    """

    total_calls: int = 0

    successful_calls: int = 0

    failed_calls: int = 0


    latencies: list[float] = field(
        default_factory=list
    )


    _records: dict[str, MetricRecord] = field(
        default_factory=dict,
        init=False,
        repr=False,
    )


    _lock: Lock = field(
        default_factory=Lock,
        init=False,
        repr=False,
    )



    def record(
        self,
        tool: str,
        start_time: float,
        success: bool,
    ) -> None:

        duration = perf_counter() - start_time


        if duration < 0 or duration > 86400:

            duration = max(
                0.0,
                time() - start_time,
            )


        with self._lock:

            record = self._records.setdefault(
                tool,
                MetricRecord(),
            )


            record.calls += 1

            record.total_time += duration


            self.total_calls += 1

            self.latencies.append(
                duration
            )


            if success:

                record.success += 1

                self.successful_calls += 1

            else:

                record.failure += 1

                self.failed_calls += 1



    def get_metrics(
        self,
        tool: str,
    ) -> dict[str, Any]:

        record = self._records.get(
            tool
        )

        if record is None:

            return MetricRecord().to_dict()


        return record.to_dict()



    @property
    def success_rate(
        self,
    ) -> float:

        if self.total_calls == 0:
            return 0.0

        return (
            self.successful_calls
            /
            self.total_calls
        )



    @property
    def failure_rate(
        self,
    ) -> float:

        if self.total_calls == 0:
            return 0.0

        return (
            self.failed_calls
            /
            self.total_calls
        )



    @property
    def average_latency(
        self,
    ) -> float:

        if not self.latencies:
            return 0.0

        return (
            sum(self.latencies)
            /
            len(self.latencies)
        )



    def snapshot(
        self,
    ) -> dict[str, Any]:

        return {

            "total_calls":
                self.total_calls,

            "successful_calls":
                self.successful_calls,

            "failed_calls":
                self.failed_calls,

            "success_rate":
                self.success_rate,

            "failure_rate":
                self.failure_rate,

            "average_latency":
                self.average_latency,

            "records":
            {
                name:
                    record.to_dict()

                for name, record
                in self._records.items()
            },

        }



    report = snapshot



    def reset(
        self,
    ) -> None:

        self.total_calls = 0

        self.successful_calls = 0

        self.failed_calls = 0

        self.latencies.clear()

        self._records.clear()




# ============================================================================
# Backward Compatible API
# ============================================================================


class Metrics:
    """
    Compatibility metrics facade.

    Supports:

    metrics.record_success()
    metrics.record_error()

    while keeping ToolMetrics engine.
    """



    def __init__(
        self,
    ) -> None:

        self.metrics = ToolMetrics()

        self.count_success = 0

        self.count_error = 0

        self.total_time = 0.0



    # ------------------------------------------------------
    # Legacy Recording API
    # ------------------------------------------------------

    def record_success(
        self,
        *,
        duration: float = 0.0,
    ) -> None:

        self.count_success += 1

        self.total_time += float(
            duration
        )



    def record_error(
        self,
        *,
        duration: float = 0.0,
    ) -> None:

        self.count_error += 1

        self.total_time += float(
            duration
        )



    def average_time(
        self,
    ) -> float:

        total = (
            self.count_success
            +
            self.count_error
        )

        if total == 0:

            return 0.0


        return (
            self.total_time
            /
            total
        )



    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {

            "success":
                self.count_success,

            "error":
                self.count_error,

            "avg_time":
                self.average_time(),

        }



    # ------------------------------------------------------
    # Modern API
    # ------------------------------------------------------

    def start(
        self,
    ) -> float:

        return perf_counter()



    def record(
        self,
        tool: str,
        start_time: float,
        success: bool,
    ) -> None:

        self.metrics.record(
            tool,
            start_time,
            success,
        )



    def get(
        self,
        tool: str,
    ) -> dict[str, Any]:

        return self.metrics.get_metrics(
            tool
        )



    def status(
        self,
    ) -> dict[str, Any]:

        return self.metrics.snapshot()



    def reset_all(
        self,
    ) -> None:
        """
        Reset all metrics.
        """

        self.metrics.reset()

        self.count_success = 0

        self.count_error = 0

        self.total_time = 0.0



    def reset(
        self,
    ) -> None:
        """
        Backward compatible reset API.
        """

        self.reset_all()



    def __repr__(
        self,
    ) -> str:

        return (
            f"Metrics("
            f"success={self.count_success}, "
            f"error={self.count_error}, "
            f"avg={self.average_time():.4f})"
        )
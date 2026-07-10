"""
SciOS Tool Metrics
==================

Production-ready metrics collector for Tool Use.

Features
--------
- Thread-safe
- High resolution timing
- Per-tool metrics
- Aggregate metrics
- Reset support
- Exportable status
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from threading import Lock
from time import perf_counter
from typing import Dict, Any


@dataclass
class MetricRecord:
    """Statistics for a single tool."""

    calls: int = 0
    success: int = 0
    failure: int = 0
    total_time: float = 0.0

    @property
    def avg_time(self) -> float:
        return self.total_time / self.calls if self.calls else 0.0

    @property
    def success_rate(self) -> float:
        return self.success / self.calls if self.calls else 0.0

    @property
    def failure_rate(self) -> float:
        return self.failure / self.calls if self.calls else 0.0

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["avg_time"] = self.avg_time
        data["success_rate"] = self.success_rate
        data["failure_rate"] = self.failure_rate
        return data


class Metrics:
    """
    SciOS Tool Metrics Collector.

    Example
    -------
    >>> metrics = Metrics()
    >>> start = metrics.start()
    >>> ...
    >>> metrics.record("calculator", start, True)
    """

    def __init__(self) -> None:
        self._records: Dict[str, MetricRecord] = {}
        self._lock = Lock()

    # ------------------------------------------------------------------
    # Timing
    # ------------------------------------------------------------------

    @staticmethod
    def start() -> float:
        """Return a high-resolution timestamp."""
        return perf_counter()

    # ------------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------------

    def record(
        self,
        tool: str,
        start_time: float,
        success: bool,
    ) -> None:
        """
        Record one tool invocation.
        """

        duration = perf_counter() - start_time

        with self._lock:

            record = self._records.setdefault(tool, MetricRecord())

            record.calls += 1
            record.total_time += duration

            if success:
                record.success += 1
            else:
                record.failure += 1

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get(self, tool: str) -> Dict[str, Any]:
        """
        Return metrics for one tool.
        """

        record = self._records.get(tool)

        if record is None:
            return MetricRecord().to_dict()

        return record.to_dict()

    def status(self) -> Dict[str, Any]:
        """
        Export all metrics.
        """

        with self._lock:

            return {
                "tools": len(self._records),
                "records": {
                    name: record.to_dict()
                    for name, record in self._records.items()
                },
            }

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------

    def reset(self, tool: str) -> None:
        """Reset one tool."""

        with self._lock:
            self._records.pop(tool, None)

    def reset_all(self) -> None:
        """Reset every metric."""

        with self._lock:
            self._records.clear()

    # ------------------------------------------------------------------
    # Magic methods
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self._records)

    def __contains__(self, tool: str) -> bool:
        return tool in self._records

    def __repr__(self) -> str:
        return (
            f"<Metrics "
            f"tools={len(self)} "
            f"records={sum(r.calls for r in self._records.values())}>"
        )

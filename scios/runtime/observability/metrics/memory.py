"""
SciOS-NG Metrics Memory Store
=============================

In-memory storage backend for metrics.

Responsibilities
-----------------
- Store metric samples.
- Keep metric history.
- Provide retrieval APIs.
- Support reset lifecycle.
- Serve runtime collectors.

Python 3.11+
"""

from __future__ import annotations


from copy import deepcopy
from dataclasses import dataclass, field
from time import time
from typing import Any


__all__ = [
    "MemoryMetricStore",
]



# ==========================================================
# Memory Metric Store
# ==========================================================


@dataclass
class MemoryMetricStore:
    """
    In-memory metrics storage.

    Used by:

    - MetricsRecorder
    - MetricsCollector
    - Dashboard
    - Exporters


    Example
    -------

        store = MemoryMetricStore()

        store.write(
            "cpu_usage",
            20.5
        )

        store.read(
            "cpu_usage"
        )

    """


    # ======================================================
    # Storage
    # ======================================================


    metrics: dict[str, list[dict[str, Any]]] = field(
        default_factory=dict
    )



    # ======================================================
    # Write API
    # ======================================================


    def write(
        self,
        name: str,
        value: int | float,
        *,
        timestamp: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Store metric sample.
        """


        if timestamp is None:

            timestamp = time()



        sample = {

            "value":
                value,

            "timestamp":
                timestamp,

            "metadata":
                dict(
                    metadata or {}
                ),
        }


        self.metrics.setdefault(
            name,
            [],
        ).append(
            sample
        )



    # ======================================================
    # Read API
    # ======================================================


    def read(
        self,
        name: str,
    ) -> list[dict[str, Any]]:
        """
        Read metric history.
        """


        return deepcopy(
            self.metrics.get(
                name,
                [],
            )
        )



    def latest(
        self,
        name: str,
    ) -> dict[str, Any] | None:
        """
        Return latest metric sample.
        """


        values = self.metrics.get(
            name,
            [],
        )


        if not values:

            return None


        return deepcopy(
            values[-1]
        )



    # ======================================================
    # Query API
    # ======================================================


    def names(
        self,
    ) -> list[str]:
        """
        Return metric names.
        """


        return list(
            self.metrics.keys()
        )



    def count(
        self,
        name: str | None = None,
    ) -> int:
        """
        Count samples.

        If name is None:
            count all samples.
        """


        if name is None:

            return sum(
                len(values)
                for values in self.metrics.values()
            )


        return len(
            self.metrics.get(
                name,
                [],
            )
        )



    # ======================================================
    # Snapshot
    # ======================================================


    def snapshot(
        self,
    ) -> dict[str, Any]:
        """
        Export storage snapshot.
        """


        return deepcopy(
            self.metrics
        )



    # ======================================================
    # Reset
    # ======================================================


    def reset(
        self,
    ) -> None:
        """
        Clear all metrics.
        """


        self.metrics.clear()



    # ======================================================
    # Copy
    # ======================================================


    def copy(
        self,
    ) -> "MemoryMetricStore":
        """
        Create independent copy.
        """


        return MemoryMetricStore(
            metrics=deepcopy(
                self.metrics
            )
        )



    # ======================================================
    # Protocols
    # ======================================================


    def __len__(
        self,
    ) -> int:
        """
        Number of metric groups.
        """


        return len(
            self.metrics
        )



    def __contains__(
        self,
        name: str,
    ) -> bool:

        return name in self.metrics



    def __repr__(
        self,
    ) -> str:

        return (
            "MemoryMetricStore("
            f"metrics={len(self.metrics)}"
            ")"
        )
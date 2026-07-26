"""
SciOS-NG Metrics Collector
==========================

Runtime metric collection layer.

Responsibilities
-----------------
- Collect metrics from runtime sources.
- Aggregate recorded observations.
- Provide collector lifecycle.
- Export collected snapshots.
- Work independently from exporters.

Design
------
Collector does NOT know about:

- ExecutionEngine
- TelemetryPlugin
- Prometheus
- OpenTelemetry

It only collects and exposes metrics.

Python 3.11+
"""

from __future__ import annotations


from dataclasses import dataclass, field
from time import perf_counter
from typing import Any, Callable


from .registry import MetricRegistry



__all__ = [
    "MetricCollector",
]



# ==========================================================
# Collector State
# ==========================================================


@dataclass
class CollectorState:
    """
    Collector runtime state.
    """


    started_at: float = field(
        default_factory=perf_counter
    )


    collections: int = 0


    active: bool = False



# ==========================================================
# Metric Collector
# ==========================================================


class MetricCollector:
    """
    Metrics collection manager.

    Example
    -------

        collector = MetricCollector()

        collector.collect(
            "cpu_usage",
            25
        )

        data = collector.snapshot()

    """



    def __init__(
        self,
        registry: MetricRegistry | None = None,
    ):

        self.registry = (
            registry
            or MetricRegistry()
        )


        self.state = CollectorState()


        self._sources: list[
            Callable[[], dict[str, Any]]
        ] = []



    # ======================================================
    # Lifecycle
    # ======================================================


    def start(
        self,
    ) -> None:
        """
        Start collector.
        """

        self.state.active = True



    def stop(
        self,
    ) -> None:
        """
        Stop collector.
        """

        self.state.active = False



    @property
    def running(
        self,
    ) -> bool:

        return self.state.active



    # ======================================================
    # Source Management
    # ======================================================


    def register_source(
        self,
        source: Callable[
            [],
            dict[str, Any]
        ],
    ) -> None:
        """
        Register metric source.
        """

        self._sources.append(
            source
        )



    def unregister_source(
        self,
        source,
    ) -> None:
        """
        Remove metric source.
        """

        if source in self._sources:

            self._sources.remove(
                source
            )



    # ======================================================
    # Collection API
    # ======================================================


    def collect(
        self,
        name: str,
        value: Any,
        metric_type: str = "gauge",
        **labels: Any,
    ):
        """
        Collect single metric.
        """

        metric = (
            self.registry.record(
                name=name,
                value=value,
                metric_type=metric_type,
                **labels,
            )
        )


        self.state.collections += 1


        return metric



    def collect_many(
        self,
        metrics: list[dict[str, Any]],
    ):
        """
        Collect multiple metrics.
        """

        results = []


        for item in metrics:

            results.append(
                self.collect(
                    **item
                )
            )


        return results



    def collect_sources(
        self,
    ):
        """
        Collect metrics from registered sources.
        """

        results = []


        for source in self._sources:

            data = source()


            if not data:

                continue


            for name, value in data.items():

                results.append(
                    self.collect(
                        name,
                        value,
                    )
                )


        return results



    # ======================================================
    # Snapshot
    # ======================================================


    def snapshot(
        self,
    ) -> dict[str, Any]:
        """
        Create collector snapshot.
        """

        elapsed = (
            perf_counter()
            -
            self.state.started_at
        )


        return {

            "active":
                self.state.active,


            "collections":
                self.state.collections,


            "sources":
                len(
                    self._sources
                ),


            "elapsed":
                elapsed,


            "metrics":
                self.registry.snapshot(),
        }



    def report(
        self,
    ) -> dict[str, Any]:
        """
        Human readable report.
        """

        return self.snapshot()



    # ======================================================
    # Reset
    # ======================================================


    def reset(
        self,
    ) -> None:
        """
        Reset collector state.
        """

        self.state = CollectorState()


        self.registry.reset()



    # ======================================================
    # Protocols
    # ======================================================


    def __len__(
        self,
    ) -> int:

        return self.state.collections



    def __bool__(
        self,
    ) -> bool:

        return (
            self.state.collections > 0
        )



    def __repr__(
        self,
    ) -> str:

        return (
            "MetricCollector("
            f"collections={self.state.collections}, "
            f"sources={len(self._sources)}"
            ")"
        )
"""
SciOS Observability Metrics Plugin
=================================

Runtime Metrics Integration Layer.

Responsibilities
-----------------
- Bridge Runtime lifecycle to MetricRecorder.
- Attach runtime metadata.
- Coordinate collectors.
- Coordinate exporters.
- Provide metrics snapshot.
- Flush metrics.
- Shutdown metrics subsystem.

This class contains NO metric calculation logic.

Python 3.11+
"""

from __future__ import annotations


import platform
import socket
import threading


from datetime import datetime, timezone

from typing import Any


from .collector import MetricCollector
from .exporter import MetricExporter
from .recorder import MetricRecorder
from .registry import MetricRegistry



__all__ = [
    "MetricsPlugin",
]



# ==========================================================
# Metrics Plugin
# ==========================================================


class MetricsPlugin:
    """
    Runtime Metrics Plugin.
    """



    def __init__(
        self,
        *,
        recorder: MetricRecorder | None = None,
        registry: MetricRegistry | None = None,
        collectors: list[MetricCollector] | None = None,
        exporters: list[MetricExporter] | None = None,
        enabled: bool = True,
    ) -> None:


        self.enabled = enabled


        self.registry = (
            registry
            if registry is not None
            else MetricRegistry()
        )


        self.recorder = (
            recorder
            if recorder is not None
            else MetricRecorder(
                registry=self.registry
            )
        )


        self.collectors = list(
            collectors or []
        )


        self.exporters = list(
            exporters or []
        )


        self.installed = False


        self._runtime_start: datetime | None = None


        self._lock = threading.RLock()



    # ======================================================
    # Lifecycle
    # ======================================================


    def install(
        self,
    ) -> None:

        with self._lock:

            self.installed = True



            for collector in self.collectors:

                if hasattr(
                    collector,
                    "start",
                ):

                    collector.start()



    def uninstall(
        self,
    ) -> None:

        with self._lock:

            self.shutdown()

            self.installed = False



    # ======================================================
    # Runtime Hooks
    # ======================================================


    def before_runtime(
        self,
        runtime: Any,
    ) -> None:


        if not self.enabled:

            return


        self._runtime_start = datetime.now(
            timezone.utc
        )


        self.recorder.record_runtime_start()


        self.recorder.record_metadata(

            {

                "platform":
                    platform.platform(),


                "hostname":
                    socket.gethostname(),


                "python_version":
                    platform.python_version(),


            }

        )



    def after_runtime(
        self,
        runtime: Any,
        *,
        success: bool = True,
    ) -> None:


        if not self.enabled:

            return


        self.recorder.record_runtime_finish(

            success=success

        )


        self.flush()



    # ======================================================
    # Stage Lifecycle
    # ======================================================


    def before_stage(
        self,
        stage: Any,
    ) -> None:


        if self.enabled:

            self.recorder.record_stage_start(
                stage
            )



    def after_stage(
        self,
        stage: Any,
        *,
        success: bool = True,
    ) -> None:


        if self.enabled:

            self.recorder.record_stage_finish(

                stage,

                success=success,

            )



    # ======================================================
    # Task Lifecycle
    # ======================================================


    def before_task(
        self,
        task: Any,
    ) -> None:


        if self.enabled:

            self.recorder.record_task_start(
                task
            )



    def after_task(
        self,
        task: Any,
        *,
        success: bool = True,
    ) -> None:


        if self.enabled:

            self.recorder.record_task_finish(

                task,

                success=success,

            )



    # ======================================================
    # Registry API
    # ======================================================


    def snapshot(
        self,
    ) -> dict[str, Any]:

        return self.registry.snapshot()



    def report(
        self,
    ) -> dict[str, Any]:

        return self.snapshot()



    # ======================================================
    # Exporter Management
    # ======================================================


    def add_exporter(
        self,
        exporter: MetricExporter,
    ) -> None:


        with self._lock:

            if exporter not in self.exporters:

                self.exporters.append(
                    exporter
                )



    def remove_exporter(
        self,
        exporter: MetricExporter,
    ) -> None:


        with self._lock:

            if exporter in self.exporters:

                self.exporters.remove(
                    exporter
                )



    # ======================================================
    # Collector Management
    # ======================================================


    def add_collector(
        self,
        collector: MetricCollector,
    ) -> None:


        with self._lock:

            if collector not in self.collectors:

                self.collectors.append(
                    collector
                )



    def remove_collector(
        self,
        collector: MetricCollector,
    ) -> None:


        with self._lock:

            if collector in self.collectors:

                self.collectors.remove(
                    collector
                )



    # ======================================================
    # Export
    # ======================================================


    def export(
        self,
    ) -> list[Any]:

        snapshot = self.snapshot()


        results = []


        for exporter in self.exporters:

            if hasattr(
                exporter,
                "export",
            ):

                results.append(

                    exporter.export(
                        snapshot
                    )

                )


        return results



    def flush(
        self,
    ) -> None:


        with self._lock:

            self.export()



    # ======================================================
    # Reset
    # ======================================================


    def reset(
        self,
    ) -> None:


        with self._lock:

            self.registry.clear()


            self.recorder.reset()


            for collector in self.collectors:

                if hasattr(
                    collector,
                    "reset",
                ):

                    collector.reset()



    # ======================================================
    # Shutdown
    # ======================================================


    def shutdown(
        self,
    ) -> None:


        with self._lock:

            self.flush()


            for exporter in self.exporters:

                if hasattr(
                    exporter,
                    "shutdown",
                ):

                    exporter.shutdown()



            for collector in self.collectors:

                if hasattr(
                    collector,
                    "shutdown",
                ):

                    collector.shutdown()



            self.reset()



    # ======================================================
    # State
    # ======================================================


    def enable(
        self,
    ) -> None:

        self.enabled = True



    def disable(
        self,
    ) -> None:

        self.enabled = False



    def status(
        self,
    ) -> dict[str, Any]:

        return {

            "enabled":
                self.enabled,


            "installed":
                self.installed,


            "collectors":
                len(
                    self.collectors
                ),


            "exporters":
                len(
                    self.exporters
                ),

        }



    # ======================================================
    # Debug
    # ======================================================


    def __repr__(
        self,
    ) -> str:

        return (

            "MetricsPlugin("

            f"enabled={self.enabled}, "

            f"installed={self.installed}, "

            f"collectors={len(self.collectors)}, "

            f"exporters={len(self.exporters)}"

            ")"

        )
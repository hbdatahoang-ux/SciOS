"""
SciOS Runtime Telemetry
=======================

Runtime observability plugin layer.

Responsibilities
-----------------
- Listen to Runtime lifecycle hooks.
- Collect execution telemetry.
- Measure execution latency.
- Update TelemetryMetrics.
- Provide snapshots for exporters.

Architecture
------------

ExecutionEngine
        |
        |
        v
   Runtime Hooks
        |
        |
        v
 TelemetryPlugin
        |
        |
        v
 TelemetryMetrics
        |
        +------------+
        |            |
       JSON     Prometheus
                    |
             OpenTelemetry


Python 3.11+
"""

from __future__ import annotations


import time

from typing import Any, Callable


from .telemetry_metrics import TelemetryMetrics



__all__ = [
    "TelemetryPlugin",
]



# ==========================================================
# Telemetry Plugin
# ==========================================================


class TelemetryPlugin:
    """
    Runtime telemetry hook plugin.

    The plugin is intentionally lightweight.

    It does NOT calculate metrics itself.
    All metric storage and aggregation belongs to:

        TelemetryMetrics
    """



    # ======================================================
    # Construction
    # ======================================================


    def __init__(
        self,
        engine: Any,
    ) -> None:


        self.engine = engine


        self.metrics = TelemetryMetrics()


        self.installed = False


        self.handles: list[Any] = []


        self._starts: dict[int, float] = {}



    # ======================================================
    # Install
    # ======================================================


    def install(self) -> None:
        """
        Attach telemetry hooks.
        """


        if self.installed:

            return



        self.handles = [

            self._register(
                "execution_started",
                self._execution_started,
            ),


            self._register(
                "before_execute",
                self._before_execute,
            ),


            self._register(
                "execution_completed",
                self._execution_completed,
            ),


            self._register(
                "execution_failed",
                self._execution_failed,
            ),


            self._register(
                "execution_finished",
                self._execution_finished,
            ),
        ]



        self.installed = True





    def uninstall(self) -> None:
        """
        Remove telemetry hooks.
        """


        if not self.installed:

            return



        for handle in self.handles:

            try:

                if hasattr(
                    handle,
                    "disable",
                ):

                    handle.disable()


                elif callable(handle):

                    handle()


            except Exception:

                pass



        self.handles.clear()


        self._starts.clear()


        self.installed = False




    # ======================================================
    # Hook Registration
    # ======================================================


    def _register(
        self,
        name: str,
        callback: Callable,
    ):


        return self.engine.register_hook(
            name,
            callback,
        )



    # ======================================================
    # Lifecycle Hooks
    # ======================================================


    def _execution_started(
        self,
        context,
        *args,
        **kwargs,
    ):
        """
        Mark execution start timestamp.
        """


        self._starts[
            id(context)
        ] = time.perf_counter()





    def _before_execute(
        self,
        context,
        *args,
        **kwargs,
    ):
        """
        Count execution.
        """


        self.metrics.start_task()




    def _execution_completed(
        self,
        context,
        result,
        *args,
        **kwargs,
    ):
        """
        Successful execution.
        """


        latency = self._latency(
            context
        )


        self.metrics.complete_task(
            latency
        )





    def _execution_failed(
        self,
        context,
        error,
        *args,
        **kwargs,
    ):
        """
        Failed execution.
        """


        latency = self._latency(
            context
        )


        self.metrics.fail_task(
            latency
        )





    def _execution_finished(
        self,
        context,
        *args,
        **kwargs,
    ):
        """
        Cleanup execution state.
        """


        self._starts.pop(
            id(context),
            None,
        )



    # ======================================================
    # Helpers
    # ======================================================


    def _latency(
        self,
        context,
    ) -> float:
        """
        Calculate execution latency.
        """


        start = self._starts.get(
            id(context)
        )


        if start is None:

            return 0.0



        return (
            time.perf_counter()
            -
            start
        )



    # ======================================================
    # Public API
    # ======================================================


    def report(
        self,
    ):
        """
        Human readable metrics report.
        """


        return self.metrics.report()




    def snapshot(
        self,
    ):
        """
        Exporter-ready snapshot.
        """


        return self.metrics.snapshot()




    def reset(
        self,
    ):
        """
        Reset telemetry state.
        """


        self.metrics.reset()


        self._starts.clear()



    # ======================================================
    # Protocols
    # ======================================================


    def __repr__(self) -> str:


        return (
            "TelemetryPlugin("
            f"installed={self.installed}, "
            f"metrics={self.metrics!r}"
            ")"
        )
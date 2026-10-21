"""
SciOS-NG Runtime Metrics Profiling Integration

Integration layer between Runtime Metrics and Profiling subsystem.

SciOS-NG v0.2
"""

from __future__ import annotations

from contextlib import nullcontext
from datetime import datetime
from typing import Any, Callable


# ==============================================================
# MetricProfilingIntegration
# ==============================================================


class MetricProfilingIntegration:
    """
    Integration layer for connecting Metrics with Profiling.

    Responsibilities
    ----------------
    - Execute metric operations under a profiler
    - Support generic profiling providers
    - Record profiling metadata when supported
    - Preserve profiling subsystem isolation
    - Track integration statistics
    """

    def __init__(
        self,
        profiler: Any = None,
        name: str = "MetricProfilingIntegration",
        description: str = "",
    ) -> None:

        self._name = name
        self._description = description

        self._profiler = profiler

        self._executions = 0
        self._success = 0
        self._failures = 0

        self._last_result: Any = None
        self._last_error: Exception | None = None

        self._created_at = datetime.utcnow()
        self._updated_at = self._created_at

    # ==========================================================
    # Properties
    # ==========================================================

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def profiler(self) -> Any:
        return self._profiler

    @property
    def configured(self) -> bool:
        return self._profiler is not None

    @property
    def last_result(self) -> Any:
        return self._last_result

    @property
    def last_error(self) -> Exception | None:
        return self._last_error

    # ==========================================================
    # Profiler Management
    # ==========================================================

    def set_profiler(
        self,
        profiler: Any,
    ) -> "MetricProfilingIntegration":
        """
        Set the profiling provider.
        """

        self._profiler = profiler
        self._updated_at = datetime.utcnow()

        return self

    def clear_profiler(
        self,
    ) -> "MetricProfilingIntegration":
        """
        Remove the current profiling provider.
        """

        self._profiler = None
        self._updated_at = datetime.utcnow()

        return self

    # ==========================================================
    # Profiling Lifecycle
    # ==========================================================

    def start(
        self,
        name: str | None = None,
        **kwargs: Any,
    ) -> Any:
        """
        Start profiling when the provider exposes start().
        """

        if self._profiler is None:
            return None

        starter = getattr(
            self._profiler,
            "start",
            None,
        )

        if callable(starter):
            return starter(
                name or self._name,
                **kwargs,
            )

        return None

    def stop(
        self,
        **kwargs: Any,
    ) -> Any:
        """
        Stop profiling when the provider exposes stop().
        """

        if self._profiler is None:
            return None

        stopper = getattr(
            self._profiler,
            "stop",
            None,
        )

        if callable(stopper):
            return stopper(
                **kwargs,
            )

        return None

    # ==========================================================
    # Context
    # ==========================================================

    def profile(
        self,
        name: str | None = None,
        **kwargs: Any,
    ):
        """
        Return a profiling context manager when supported.
        """

        if self._profiler is None:
            return nullcontext()

        profiler = self._profiler

        context_factory = getattr(
            profiler,
            "profile",
            None,
        )

        if callable(context_factory):
            return context_factory(
                name or self._name,
                **kwargs,
            )

        context_factory = getattr(
            profiler,
            "context",
            None,
        )

        if callable(context_factory):
            return context_factory(
                name or self._name,
                **kwargs,
            )

        return nullcontext()

    # ==========================================================
    # Execution
    # ==========================================================

    def execute(
        self,
        metric: Any,
        handler: Callable | None = None,
        profile_name: str | None = None,
        **kwargs: Any,
    ) -> Any:
        """
        Execute a metric operation under profiling.
        """

        try:

            with self.profile(
                profile_name or self._name,
                **kwargs,
            ):

                if handler is None:
                    result = metric
                else:
                    result = handler(metric)

            self._executions += 1
            self._success += 1

            self._last_result = result
            self._last_error = None

            return result

        except Exception as exc:

            self._executions += 1
            self._failures += 1

            self._last_result = None
            self._last_error = exc

            raise

        finally:

            self._updated_at = datetime.utcnow()

    def profile_metric(
        self,
        metric: Any,
        handler: Callable | None = None,
        profile_name: str | None = None,
        **kwargs: Any,
    ) -> Any:
        """
        Execute a metric operation under profiling.

        Alias for execute().
        """

        return self.execute(
            metric,
            handler=handler,
            profile_name=profile_name,
            **kwargs,
        )

    def run(
        self,
        metric: Any,
        handler: Callable | None = None,
        profile_name: str | None = None,
        **kwargs: Any,
    ) -> Any:
        """
        Alias for execute().
        """

        return self.execute(
            metric,
            handler=handler,
            profile_name=profile_name,
            **kwargs,
        )

    # ==========================================================
    # Metadata
    # ==========================================================

    def record(
        self,
        key: str,
        value: Any,
    ) -> "MetricProfilingIntegration":
        """
        Record profiling metadata when supported.
        """

        if self._profiler is None:
            return self

        recorder = getattr(
            self._profiler,
            "record",
            None,
        )

        if callable(recorder):
            recorder(
                key,
                value,
            )

        self._updated_at = datetime.utcnow()

        return self

    # ==========================================================
    # Diagnostics
    # ==========================================================

    def statistics(self) -> dict[str, Any]:
        """
        Return profiling integration statistics.
        """

        return {
            "name": self._name,
            "configured": self.configured,
            "executions": self._executions,
            "success": self._success,
            "failures": self._failures,
        }

    def status(self) -> dict[str, Any]:
        """
        Return profiling integration status.
        """

        return {
            "configured": self.configured,
            "active": self.configured,
        }

    def reset(self) -> "MetricProfilingIntegration":
        """
        Reset runtime statistics.
        """

        self._executions = 0
        self._success = 0
        self._failures = 0

        self._last_result = None
        self._last_error = None

        self._updated_at = datetime.utcnow()

        return self

    # ==========================================================
    # Python Protocols
    # ==========================================================

    def __call__(
        self,
        metric: Any,
        **kwargs: Any,
    ) -> Any:

        return self.execute(
            metric,
            **kwargs,
        )

    def __repr__(self) -> str:

        return (
            f"MetricProfilingIntegration("
            f"name={self._name!r}, "
            f"configured={self.configured}, "
            f"executions={self._executions}, "
            f"success={self._success}, "
            f"failures={self._failures}"
            f")"
        )

    def __str__(self) -> str:
        return self._name
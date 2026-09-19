"""
SciOS-NG Runtime Metrics Runtime Integration

Integration layer for coordinating the Metrics Runtime subsystem.

SciOS-NG v0.2
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable


# ==============================================================
# MetricRuntimeIntegration
# ==============================================================


class MetricRuntimeIntegration:
    """
    Integration layer for the Metrics Runtime subsystem.

    Responsibilities
    ----------------
    - Coordinate a runtime execution engine
    - Execute metrics through the runtime
    - Support middleware/pipeline integration
    - Execute batches of metrics
    - Manage runtime lifecycle
    - Track integration statistics
    - Provide runtime diagnostics
    """

    def __init__(
        self,
        runtime: Any | None = None,
        middleware: Any | None = None,
        pipeline: Any | None = None,
        name: str = "MetricRuntimeIntegration",
        description: str = "",
    ) -> None:

        self._name = name
        self._description = description

        self._runtime = runtime
        self._middleware = middleware
        self._pipeline = pipeline

        self._enabled = True
        self._closed = False
        self._running = False

        self._created_at = datetime.utcnow()
        self._updated_at = self._created_at

        self._executions = 0
        self._success = 0
        self._failures = 0

        self._last_result: Any = None
        self._last_error: Exception | None = None

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
    def runtime(self) -> Any | None:
        return self._runtime

    @property
    def middleware(self) -> Any | None:
        return self._middleware

    @property
    def pipeline(self) -> Any | None:
        return self._pipeline

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def closed(self) -> bool:
        return self._closed

    @property
    def running(self) -> bool:
        return self._running

    @property
    def active(self) -> bool:
        return self._enabled and not self._closed

    @property
    def last_result(self) -> Any:
        return self._last_result

    @property
    def last_error(self) -> Exception | None:
        return self._last_error

    # ==========================================================
    # Runtime Configuration
    # ==========================================================

    def set_runtime(
        self,
        runtime: Any | None,
    ) -> "MetricRuntimeIntegration":

        self._runtime = runtime
        self._updated_at = datetime.utcnow()

        return self

    def set_middleware(
        self,
        middleware: Any | None,
    ) -> "MetricRuntimeIntegration":

        self._middleware = middleware
        self._updated_at = datetime.utcnow()

        return self

    def set_pipeline(
        self,
        pipeline: Any | None,
    ) -> "MetricRuntimeIntegration":

        self._pipeline = pipeline
        self._updated_at = datetime.utcnow()

        return self

    # ==========================================================
    # Execution
    # ==========================================================

    def execute(
        self,
        metric: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute a metric through the configured runtime stack.

        Execution order
        ---------------
        1. runtime
        2. middleware
        3. pipeline

        Components that are not configured are skipped.
        """

        self._ensure_active()

        self._running = True
        self._updated_at = datetime.utcnow()

        result = metric

        try:
            if self._runtime is not None:
                result = self._execute_component(
                    self._runtime,
                    result,
                    **kwargs,
                )

            if self._middleware is not None:
                result = self._execute_component(
                    self._middleware,
                    result,
                    **kwargs,
                )

            if self._pipeline is not None:
                result = self._execute_component(
                    self._pipeline,
                    result,
                    **kwargs,
                )

            self._executions += 1
            self._success += 1

            self._last_result = result
            self._last_error = None

            return result

        except Exception as exc:
            self._executions += 1
            self._failures += 1

            self._last_error = exc
            self._last_result = None

            raise

        finally:
            self._running = False
            self._updated_at = datetime.utcnow()

    def process(
        self,
        metric: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Alias for execute().
        """

        return self.execute(
            metric,
            **kwargs,
        )

    def run(
        self,
        metric: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Alias for execute().
        """

        return self.execute(
            metric,
            **kwargs,
        )

    # ==========================================================
    # Batch Execution
    # ==========================================================

    def execute_many(
        self,
        metrics: Iterable[Any],
        **kwargs: Any,
    ) -> list[Any]:
        """
        Execute multiple metrics sequentially.
        """

        return [
            self.execute(
                metric,
                **kwargs,
            )
            for metric in metrics
        ]

    def process_many(
        self,
        metrics: Iterable[Any],
        **kwargs: Any,
    ) -> list[Any]:
        """
        Alias for execute_many().
        """

        return self.execute_many(
            metrics,
            **kwargs,
        )

    # ==========================================================
    # Component Execution
    # ==========================================================

    @staticmethod
    def _execute_component(
        component: Any,
        metric: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute one integration component.

        Preference order:
            execute()
            process()
            run()
            callable
        """

        if hasattr(component, "execute"):
            return component.execute(
                metric,
                **kwargs,
            )

        if hasattr(component, "process"):
            return component.process(
                metric,
                **kwargs,
            )

        if hasattr(component, "run"):
            return component.run(
                metric,
                **kwargs,
            )

        if callable(component):
            return component(
                metric,
                **kwargs,
            )

        raise TypeError(
            "Integration component must expose "
            "execute(), process(), run(), or be callable"
        )

    # ==========================================================
    # Lifecycle
    # ==========================================================

    def enable(self) -> "MetricRuntimeIntegration":
        """
        Enable integration.
        """

        self._enabled = True
        self._updated_at = datetime.utcnow()

        return self

    def disable(self) -> "MetricRuntimeIntegration":
        """
        Disable integration.
        """

        self._enabled = False
        self._updated_at = datetime.utcnow()

        return self

    def close(self) -> "MetricRuntimeIntegration":
        """
        Close integration and propagate close to components
        when supported.
        """

        self._closed = True

        for component in self._components():
            close = getattr(
                component,
                "close",
                None,
            )

            if callable(close):
                close()

        self._updated_at = datetime.utcnow()

        return self

    def reopen(self) -> "MetricRuntimeIntegration":
        """
        Reopen integration and propagate reopen when supported.
        """

        self._closed = False

        for component in self._components():
            reopen = getattr(
                component,
                "reopen",
                None,
            )

            if callable(reopen):
                reopen()

        self._updated_at = datetime.utcnow()

        return self

    # ==========================================================
    # Reset
    # ==========================================================

    def reset(self) -> "MetricRuntimeIntegration":
        """
        Reset integration statistics while preserving configuration.
        """

        self._executions = 0
        self._success = 0
        self._failures = 0

        self._last_result = None
        self._last_error = None

        self._running = False

        self._updated_at = datetime.utcnow()

        return self

    # ==========================================================
    # Validation
    # ==========================================================

    def validate(self) -> bool:
        """
        Validate all configured components.
        """

        for component in self._components():

            if not (
                callable(component)
                or hasattr(component, "execute")
                or hasattr(component, "process")
                or hasattr(component, "run")
            ):
                return False

        return True

    # ==========================================================
    # Components
    # ==========================================================

    def _components(self) -> list[Any]:
        """
        Return configured integration components.
        """

        return [
            component
            for component in (
                self._runtime,
                self._middleware,
                self._pipeline,
            )
            if component is not None
        ]

    def components(self) -> list[Any]:
        """
        Return configured components.
        """

        return list(
            self._components()
        )

    def component_count(self) -> int:
        """
        Return number of configured components.
        """

        return len(
            self._components()
        )

    # ==========================================================
    # Diagnostics
    # ==========================================================

    def statistics(self) -> dict[str, Any]:
        """
        Return integration execution statistics.
        """

        return {
            "name": self._name,
            "components": self.component_count(),
            "executions": self._executions,
            "success": self._success,
            "failures": self._failures,
        }

    def status(self) -> dict[str, Any]:
        """
        Return integration runtime status.
        """

        return {
            "enabled": self._enabled,
            "running": self._running,
            "closed": self._closed,
            "active": self.active,
            "components": self.component_count(),
            "valid": self.validate(),
        }

    # ==========================================================
    # Internal
    # ==========================================================

    def _ensure_active(self) -> None:
        """
        Ensure integration is executable.
        """

        if not self._enabled:
            raise RuntimeError(
                f"Runtime integration {self._name} disabled"
            )

        if self._closed:
            raise RuntimeError(
                f"Runtime integration {self._name} closed"
            )

    # ==========================================================
    # Python Protocols
    # ==========================================================

    def __len__(self) -> int:
        return self.component_count()

    def __iter__(self):
        return iter(
            self._components()
        )

    def __contains__(self, component: Any) -> bool:
        return component in self._components()

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
            f"MetricRuntimeIntegration("
            f"name={self._name!r}, "
            f"components={self.component_count()}, "
            f"executions={self._executions}, "
            f"success={self._success}, "
            f"failures={self._failures}"
            f")"
        )

    def __str__(self) -> str:
        return self._name
"""
SciOS-NG Runtime Metrics Integration

Top-level orchestration runtime for the Metrics subsystem.

SciOS-NG v0.2
"""

from __future__ import annotations

from datetime import datetime
from typing import Any


# ==============================================================
# MetricRuntimeIntegration
# ==============================================================


class MetricRuntimeIntegration:
    """
    Top-level runtime integration for the Metrics subsystem.

    Responsibilities
    ----------------
    - Orchestrate processor, middleware, pipeline, and exporter
    - Execute components in deterministic order
    - Provide a unified runtime API
    - Track execution statistics
    - Provide runtime diagnostics
    - Manage runtime lifecycle
    """

    def __init__(
        self,
        processor: Any | None = None,
        middleware: Any | None = None,
        pipeline: Any | None = None,
        exporter: Any | None = None,
        name: str = "MetricRuntimeIntegration",
        description: str = "",
    ) -> None:

        self._name = name
        self._description = description

        self._processor = processor
        self._middleware = middleware
        self._pipeline = pipeline
        self._exporter = exporter

        self._enabled = True
        self._running = False
        self._closed = False

        self._executions = 0
        self._success = 0
        self._failures = 0

        self._last_result: Any = None
        self._last_error: Exception | None = None

        self._created_at = datetime.utcnow()
        self._updated_at = self._created_at

        self._validate_components()

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
    def processor(self) -> Any | None:
        return self._processor

    @property
    def middleware(self) -> Any | None:
        return self._middleware

    @property
    def pipeline(self) -> Any | None:
        return self._pipeline

    @property
    def exporter(self) -> Any | None:
        return self._exporter

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def running(self) -> bool:
        return self._running

    @property
    def closed(self) -> bool:
        return self._closed

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
    # Component Management
    # ==========================================================

    def set_processor(
        self,
        processor: Any | None,
    ) -> "MetricRuntimeIntegration":

        self._processor = processor
        self._updated_at = datetime.utcnow()

        self._validate_component(
            processor,
            "processor",
        )

        return self

    def set_middleware(
        self,
        middleware: Any | None,
    ) -> "MetricRuntimeIntegration":

        self._middleware = middleware
        self._updated_at = datetime.utcnow()

        self._validate_component(
            middleware,
            "middleware",
        )

        return self

    def set_pipeline(
        self,
        pipeline: Any | None,
    ) -> "MetricRuntimeIntegration":

        self._pipeline = pipeline
        self._updated_at = datetime.utcnow()

        self._validate_component(
            pipeline,
            "pipeline",
        )

        return self

    def set_exporter(
        self,
        exporter: Any | None,
    ) -> "MetricRuntimeIntegration":

        self._exporter = exporter
        self._updated_at = datetime.utcnow()

        self._validate_component(
            exporter,
            "exporter",
        )

        return self

    def clear_components(
        self,
    ) -> "MetricRuntimeIntegration":

        self._processor = None
        self._middleware = None
        self._pipeline = None
        self._exporter = None

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
        Execute the configured Metrics runtime chain.

        Execution order
        ---------------
        1. processor
        2. middleware
        3. pipeline
        4. exporter

        Components that are not configured are skipped.
        """

        self._ensure_active()

        self._running = True
        self._updated_at = datetime.utcnow()

        result = metric

        try:

            if self._processor is not None:
                result = self._execute_component(
                    self._processor,
                    result,
                    "processor",
                    **kwargs,
                )

            if self._middleware is not None:
                result = self._execute_component(
                    self._middleware,
                    result,
                    "middleware",
                    **kwargs,
                )

            if self._pipeline is not None:
                result = self._execute_component(
                    self._pipeline,
                    result,
                    "pipeline",
                    **kwargs,
                )

            if self._exporter is not None:
                result = self._execute_component(
                    self._exporter,
                    result,
                    "exporter",
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

    # ==========================================================
    # Batch Execution
    # ==========================================================

    def execute_many(
        self,
        metrics: list[Any] | tuple[Any, ...],
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

    def run_many(
        self,
        metrics: list[Any] | tuple[Any, ...],
        **kwargs: Any,
    ) -> list[Any]:
        """
        Alias for execute_many().
        """

        return self.execute_many(
            metrics,
            **kwargs,
        )

    def process_many(
        self,
        metrics: list[Any] | tuple[Any, ...],
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
        component_name: str,
        **kwargs: Any,
    ) -> Any:
        """
        Execute one runtime component.

        Preference order
        ----------------
        processor:
            process() -> execute() -> callable

        middleware:
            execute() -> process() -> run() -> callable

        pipeline:
            execute() -> process() -> run() -> callable

        exporter:
            export() -> process() -> execute() -> callable
        """

        if component_name == "processor":

            process = getattr(
                component,
                "process",
                None,
            )

            if callable(process):
                return process(
                    metric,
                    **kwargs,
                )

        if component_name == "exporter":

            export = getattr(
                component,
                "export",
                None,
            )

            if callable(export):
                return export(
                    metric,
                    **kwargs,
                )

        execute = getattr(
            component,
            "execute",
            None,
        )

        if callable(execute):
            return execute(
                metric,
                **kwargs,
            )

        process = getattr(
            component,
            "process",
            None,
        )

        if callable(process):
            return process(
                metric,
                **kwargs,
            )

        run = getattr(
            component,
            "run",
            None,
        )

        if callable(run):
            return run(
                metric,
                **kwargs,
            )

        if callable(component):
            return component(
                metric,
                **kwargs,
            )

        raise TypeError(
            f"{component_name} does not expose "
            "a supported execution API"
        )

    # ==========================================================
    # Validation
    # ==========================================================

    def validate(self) -> bool:
        """
        Validate all configured runtime components.
        """

        components = (
            ("processor", self._processor),
            ("middleware", self._middleware),
            ("pipeline", self._pipeline),
            ("exporter", self._exporter),
        )

        for name, component in components:

            if component is None:
                continue

            if not self._component_supported(
                component,
                name,
            ):
                return False

        return True

    @classmethod
    def _component_supported(
        cls,
        component: Any,
        component_name: str,
    ) -> bool:

        if callable(component):
            return True

        if component_name == "processor":
            return any(
                callable(
                    getattr(
                        component,
                        method,
                        None,
                    )
                )
                for method in (
                    "process",
                    "execute",
                    "run",
                )
            )

        if component_name == "exporter":
            return any(
                callable(
                    getattr(
                        component,
                        method,
                        None,
                    )
                )
                for method in (
                    "export",
                    "process",
                    "execute",
                    "run",
                )
            )

        return any(
            callable(
                getattr(
                    component,
                    method,
                    None,
                )
            )
            for method in (
                "execute",
                "process",
                "run",
            )
        )

    def _validate_component(
        self,
        component: Any | None,
        component_name: str,
    ) -> None:

        if component is None:
            return

        if not self._component_supported(
            component,
            component_name,
        ):
            raise TypeError(
                f"{component_name} does not expose "
                "a supported execution API"
            )

    def _validate_components(self) -> None:

        components = (
            ("processor", self._processor),
            ("middleware", self._middleware),
            ("pipeline", self._pipeline),
            ("exporter", self._exporter),
        )

        for name, component in components:
            self._validate_component(
                component,
                name,
            )

    # ==========================================================
    # Lifecycle
    # ==========================================================

    def enable(self) -> "MetricRuntimeIntegration":

        self._enabled = True
        self._updated_at = datetime.utcnow()

        return self

    def disable(self) -> "MetricRuntimeIntegration":

        self._enabled = False
        self._updated_at = datetime.utcnow()

        return self

    def close(self) -> "MetricRuntimeIntegration":

        self._closed = True
        self._updated_at = datetime.utcnow()

        return self

    def reopen(self) -> "MetricRuntimeIntegration":

        self._closed = False
        self._updated_at = datetime.utcnow()

        return self

    # ==========================================================
    # Diagnostics
    # ==========================================================

    def statistics(self) -> dict[str, Any]:

        return {
            "name": self._name,
            "executions": self._executions,
            "success": self._success,
            "failures": self._failures,
        }

    def status(self) -> dict[str, Any]:

        return {
            "enabled": self._enabled,
            "running": self._running,
            "closed": self._closed,
            "active": self.active,
            "valid": self.validate(),
            "processor": self._processor is not None,
            "middleware": self._middleware is not None,
            "pipeline": self._pipeline is not None,
            "exporter": self._exporter is not None,
        }

    def reset(self) -> "MetricRuntimeIntegration":

        self._executions = 0
        self._success = 0
        self._failures = 0

        self._last_result = None
        self._last_error = None

        self._updated_at = datetime.utcnow()

        return self

    # ==========================================================
    # Internal
    # ==========================================================

    def _ensure_active(self) -> None:

        if not self._enabled:
            raise RuntimeError(
                f"Runtime {self._name} disabled"
            )

        if self._closed:
            raise RuntimeError(
                f"Runtime {self._name} closed"
            )

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

    def __len__(self) -> int:

        return sum(
            component is not None
            for component in (
                self._processor,
                self._middleware,
                self._pipeline,
                self._exporter,
            )
        )

    def __repr__(self) -> str:

        return (
            f"MetricRuntimeIntegration("
            f"name={self._name!r}, "
            f"components={len(self)}, "
            f"executions={self._executions}, "
            f"success={self._success}, "
            f"failures={self._failures}"
            f")"
        )

    def __str__(self) -> str:
        return self._name
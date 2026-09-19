"""
SciOS-NG Runtime Metrics Middleware Pipeline

Ordered middleware execution pipeline.

SciOS-NG v0.2
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
import threading
import uuid

from .stage import MetricMiddlewareStage


# ==============================================================
# MetricMiddlewarePipeline
# ==============================================================


class MetricMiddlewarePipeline:
    """
    Runtime Metric Middleware Pipeline.

    Responsibilities
    ----------------
    - Compose ordered middleware stages
    - Execute a metric through the stage chain
    - Manage stage lifecycle
    - Maintain execution statistics
    - Provide runtime diagnostics
    """

    # ==========================================================
    # Constructor
    # ==========================================================

    def __init__(
        self,
        name: str = "MetricMiddlewarePipeline",
        description: str = "",
    ) -> None:

        # ------------------------------------------------------
        # Identity
        # ------------------------------------------------------

        self._id = str(uuid.uuid4())
        self._name = name
        self._description = description

        # ------------------------------------------------------
        # Stage Registry
        # ------------------------------------------------------

        self._stages: list[MetricMiddlewareStage] = []
        self._stage_registry: dict[str, MetricMiddlewareStage] = {}

        # ------------------------------------------------------
        # Runtime State
        # ------------------------------------------------------

        self._enabled = True
        self._running = False
        self._closed = False

        # ------------------------------------------------------
        # Context
        # ------------------------------------------------------

        self._context: dict[str, Any] = {}

        # ------------------------------------------------------
        # Synchronization
        # ------------------------------------------------------

        self._lock = threading.RLock()

        # ------------------------------------------------------
        # Metadata
        # ------------------------------------------------------

        self._created_at = datetime.utcnow()
        self._updated_at = self._created_at

        # ------------------------------------------------------
        # Statistics
        # ------------------------------------------------------

        self._executions = 0
        self._success = 0
        self._failures = 0

        self._last_result: Any = None
        self._last_error: Exception | None = None

    # ==========================================================
    # Properties
    # ==========================================================

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

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
    # Stage Management
    # ==========================================================

    def add_stage(
        self,
        stage: MetricMiddlewareStage,
    ) -> "MetricMiddlewarePipeline":
        """
        Add a stage to the end of the pipeline.
        """

        if not isinstance(stage, MetricMiddlewareStage):
            raise TypeError(
                "stage must be a MetricMiddlewareStage"
            )

        with self._lock:
            if stage.name in self._stage_registry:
                raise ValueError(
                    f"Stage already exists: {stage.name}"
                )

            self._stages.append(stage)
            self._stage_registry[stage.name] = stage
            self._updated_at = datetime.utcnow()

        return self

    def remove_stage(
        self,
        name: str,
    ) -> "MetricMiddlewarePipeline":
        """
        Remove a stage by name.

        Missing stages are ignored.
        """

        with self._lock:
            stage = self._stage_registry.pop(name, None)

            if stage is not None:
                self._stages.remove(stage)

            self._updated_at = datetime.utcnow()

        return self

    def get_stage(
        self,
        name: str,
    ) -> MetricMiddlewareStage | None:
        """
        Return a stage by name.
        """

        return self._stage_registry.get(name)

    def stages(
        self,
    ) -> list[MetricMiddlewareStage]:
        """
        Return a copy of the ordered stage list.
        """

        with self._lock:
            return list(self._stages)

    def clear_stages(
        self,
    ) -> "MetricMiddlewarePipeline":
        """
        Remove all stages.
        """

        with self._lock:
            self._stages.clear()
            self._stage_registry.clear()
            self._updated_at = datetime.utcnow()

        return self

    def add(
        self,
        stage: MetricMiddlewareStage,
    ) -> "MetricMiddlewarePipeline":
        """
        Alias for add_stage().
        """

        return self.add_stage(stage)

    def remove(
        self,
        name: str,
    ) -> "MetricMiddlewarePipeline":
        """
        Alias for remove_stage().
        """

        return self.remove_stage(name)

    # ==========================================================
    # Execution
    # ==========================================================

    def execute(
        self,
        metric: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute a metric through all enabled stages in order.
        """

        self._ensure_active()

        self._running = True
        self._updated_at = datetime.utcnow()

        result = metric

        try:
            for stage in self._stages:
                result = stage.execute(
                    result,
                    **kwargs,
                )

            self._last_result = result
            self._last_error = None

            self._executions += 1
            self._success += 1

            return result

        except Exception as exc:
            self._last_error = exc
            self._last_result = None

            self._executions += 1
            self._failures += 1

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
    # Stage Execution Control
    # ==========================================================

    def execute_stage(
        self,
        name: str,
        metric: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute one named stage independently.
        """

        self._ensure_active()

        stage = self.get_stage(name)

        if stage is None:
            raise KeyError(
                f"Unknown stage: {name}"
            )

        return stage.execute(
            metric,
            **kwargs,
        )

    def enable_stage(
        self,
        name: str,
    ) -> "MetricMiddlewarePipeline":
        """
        Enable a named stage.
        """

        stage = self.get_stage(name)

        if stage is None:
            raise KeyError(
                f"Unknown stage: {name}"
            )

        stage.enable()
        return self

    def disable_stage(
        self,
        name: str,
    ) -> "MetricMiddlewarePipeline":
        """
        Disable a named stage.

        A disabled stage will raise when reached because stage
        lifecycle is enforced by MetricMiddlewareStage.
        """

        stage = self.get_stage(name)

        if stage is None:
            raise KeyError(
                f"Unknown stage: {name}"
            )

        stage.disable()
        return self

    def skip_stage(
        self,
        name: str,
    ) -> "MetricMiddlewarePipeline":
        """
        Alias for disable_stage().
        """

        return self.disable_stage(name)

    # ==========================================================
    # Context
    # ==========================================================

    def set_context(
        self,
        key: str,
        value: Any,
    ) -> "MetricMiddlewarePipeline":
        """
        Set pipeline context value.
        """

        self._context[key] = value
        self._updated_at = datetime.utcnow()

        return self

    def context(
        self,
    ) -> dict[str, Any]:
        """
        Return a copy of pipeline context.
        """

        return dict(self._context)

    def clear_context(
        self,
    ) -> "MetricMiddlewarePipeline":
        """
        Clear pipeline context.
        """

        self._context.clear()
        self._updated_at = datetime.utcnow()

        return self

    # ==========================================================
    # Lifecycle
    # ==========================================================

    def enable(self) -> "MetricMiddlewarePipeline":
        """
        Enable pipeline.
        """

        self._enabled = True
        self._updated_at = datetime.utcnow()

        return self

    def disable(self) -> "MetricMiddlewarePipeline":
        """
        Disable pipeline.
        """

        self._enabled = False
        self._updated_at = datetime.utcnow()

        return self

    def close(self) -> "MetricMiddlewarePipeline":
        """
        Close pipeline.
        """

        self._closed = True
        self._updated_at = datetime.utcnow()

        return self

    def reopen(self) -> "MetricMiddlewarePipeline":
        """
        Reopen pipeline.
        """

        self._closed = False
        self._updated_at = datetime.utcnow()

        return self

    # ==========================================================
    # Statistics
    # ==========================================================

    def statistics(self) -> dict[str, Any]:
        """
        Return pipeline execution statistics.
        """

        return {
            "name": self._name,
            "executions": self._executions,
            "success": self._success,
            "failures": self._failures,
            "stage_count": len(self._stages),
            "enabled": self._enabled,
            "closed": self._closed,
        }

    def reset(self) -> "MetricMiddlewarePipeline":
        """
        Reset runtime statistics and diagnostics.

        Pipeline configuration survives reset.
        """

        self._executions = 0
        self._success = 0
        self._failures = 0

        self._last_result = None
        self._last_error = None

        self._updated_at = datetime.utcnow()

        return self

    # ==========================================================
    # Diagnostics
    # ==========================================================

    def status(self) -> dict[str, bool]:
        """
        Return pipeline runtime status.
        """

        return {
            "enabled": self._enabled,
            "running": self._running,
            "closed": self._closed,
            "active": self.active,
        }

    # ==========================================================
    # Internal
    # ==========================================================

    def _ensure_active(self) -> None:
        """
        Ensure pipeline can execute.
        """

        if not self._enabled:
            raise RuntimeError(
                f"Middleware pipeline {self._name} disabled"
            )

        if self._closed:
            raise RuntimeError(
                f"Middleware pipeline {self._name} closed"
            )

    # ==========================================================
    # Python Protocols
    # ==========================================================

    def __len__(self) -> int:
        return len(self._stages)

    def __iter__(self):
        return iter(self._stages)

    def __contains__(self, name: str) -> bool:
        return name in self._stage_registry

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
            f"MetricMiddlewarePipeline("
            f"name={self._name!r}, "
            f"stages={len(self._stages)}, "
            f"executions={self._executions}, "
            f"success={self._success}, "
            f"failures={self._failures}"
            f")"
        )

    def __str__(self) -> str:
        return self._name
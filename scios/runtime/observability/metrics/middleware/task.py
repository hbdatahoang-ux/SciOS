"""
SciOS-NG Runtime Metrics Middleware Task.

Executable unit for metric middleware processing.

SciOS-NG v0.2
"""

from __future__ import annotations

import uuid

from datetime import datetime
from typing import Any, Callable


# ============================================================================
# MetricMiddlewareTask
# ============================================================================


class MetricMiddlewareTask:
    """
    Runtime Metric Middleware Task.

    Responsibilities
    ----------------
    - Represent an executable metric task
    - Manage task lifecycle
    - Execute task handler
    - Track task state and result
    - Track execution statistics
    """

    # =========================================================================
    # Constructor
    # =========================================================================

    def __init__(
        self,
        name: str,
        handler: Callable | None = None,
        priority: int = 0,
        description: str = "",
    ) -> None:

        if not isinstance(name, str) or not name.strip():
            raise ValueError(
                "Task name must be a non-empty string"
            )

        if handler is not None and not callable(handler):
            raise TypeError(
                "Task handler must be callable"
            )

        if not isinstance(priority, int):
            raise TypeError(
                "Task priority must be an integer"
            )

        # ---------------------------------------------------------------------
        # Identity
        # ---------------------------------------------------------------------

        self._id = str(uuid.uuid4())
        self._name = name
        self._description = description

        # ---------------------------------------------------------------------
        # Handler
        # ---------------------------------------------------------------------

        self._handler = handler

        # ---------------------------------------------------------------------
        # Scheduling
        # ---------------------------------------------------------------------

        self._priority = priority

        # ---------------------------------------------------------------------
        # Runtime State
        # ---------------------------------------------------------------------

        self._enabled = True
        self._running = False
        self._completed = False
        self._failed = False
        self._cancelled = False

        # ---------------------------------------------------------------------
        # Result / Error
        # ---------------------------------------------------------------------

        self._result: Any = None
        self._error: Exception | None = None

        # ---------------------------------------------------------------------
        # Metadata
        # ---------------------------------------------------------------------

        self._created_at = datetime.utcnow()
        self._updated_at = self._created_at

        # ---------------------------------------------------------------------
        # Statistics
        # ---------------------------------------------------------------------

        self._executions = 0
        self._success = 0
        self._failures = 0

    # =========================================================================
    # Properties
    # =========================================================================

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
    def priority(self) -> int:
        return self._priority

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def running(self) -> bool:
        return self._running

    @property
    def completed(self) -> bool:
        return self._completed

    @property
    def failed(self) -> bool:
        return self._failed

    @property
    def cancelled(self) -> bool:
        return self._cancelled

    @property
    def result(self) -> Any:
        return self._result

    @property
    def error(self) -> Exception | None:
        return self._error

    @property
    def active(self) -> bool:
        return self._enabled and not self._cancelled

    # =========================================================================
    # Execution
    # =========================================================================

    def execute(
        self,
        metric: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute the task.

        A task without a handler passes the metric through unchanged.
        """

        self._ensure_active()

        self._running = True
        self._updated_at = datetime.utcnow()

        try:

            if self._handler is None:
                result = metric
            else:
                result = self._handler(
                    metric,
                    **kwargs,
                )

            self._result = result
            self._error = None

            self._completed = True
            self._failed = False

            self._success += 1
            self._executions += 1

            return result

        except Exception as exc:

            self._error = exc
            self._failed = True
            self._completed = False

            self._failures += 1
            self._executions += 1

            raise

        finally:

            self._running = False
            self._updated_at = datetime.utcnow()

    def run(
        self,
        metric: Any,
        **kwargs: Any,
    ) -> Any:
        """Alias for execute()."""

        return self.execute(
            metric,
            **kwargs,
        )

    def process(
        self,
        metric: Any,
        **kwargs: Any,
    ) -> Any:
        """Alias for execute()."""

        return self.execute(
            metric,
            **kwargs,
        )

    # =========================================================================
    # Handler Management
    # =========================================================================

    def set_handler(
        self,
        handler: Callable,
    ) -> "MetricMiddlewareTask":
        """Set or replace the task handler."""

        if not callable(handler):
            raise TypeError(
                "Task handler must be callable"
            )

        self._handler = handler
        self._updated_at = datetime.utcnow()

        return self

    def clear_handler(
        self,
    ) -> "MetricMiddlewareTask":
        """Remove the current handler."""

        self._handler = None
        self._updated_at = datetime.utcnow()

        return self

    def handler(
        self,
    ) -> Callable | None:
        """Return the current task handler."""

        return self._handler

    # =========================================================================
    # Task Control
    # =========================================================================

    def cancel(
        self,
    ) -> "MetricMiddlewareTask":
        """
        Cancel the task.

        Cancellation prevents future execution but does not alter
        historical execution statistics.
        """

        self._cancelled = True
        self._running = False
        self._updated_at = datetime.utcnow()

        return self

    def reset(
        self,
    ) -> "MetricMiddlewareTask":
        """
        Reset task execution state.

        Configuration and historical statistics are preserved.
        """

        self._running = False
        self._completed = False
        self._failed = False
        self._cancelled = False

        self._result = None
        self._error = None

        self._updated_at = datetime.utcnow()

        return self

    # =========================================================================
    # Lifecycle
    # =========================================================================

    def enable(
        self,
    ) -> "MetricMiddlewareTask":
        """Enable the task."""

        self._enabled = True
        self._updated_at = datetime.utcnow()

        return self

    def disable(
        self,
    ) -> "MetricMiddlewareTask":
        """Disable the task."""

        self._enabled = False
        self._updated_at = datetime.utcnow()

        return self

    # =========================================================================
    # Diagnostics
    # =========================================================================

    def statistics(
        self,
    ) -> dict[str, Any]:
        """Return task execution statistics."""

        return {
            "executions": self._executions,
            "success": self._success,
            "failures": self._failures,
            "priority": self._priority,
        }

    def status(
        self,
    ) -> dict[str, bool]:
        """Return current task state."""

        return {
            "enabled": self._enabled,
            "running": self._running,
            "completed": self._completed,
            "failed": self._failed,
            "cancelled": self._cancelled,
            "active": self.active,
        }

    # =========================================================================
    # Internal
    # =========================================================================

    def _ensure_active(
        self,
    ) -> None:
        """Ensure the task can execute."""

        if not self._enabled:
            raise RuntimeError(
                f"Task {self._name} disabled"
            )

        if self._cancelled:
            raise RuntimeError(
                f"Task {self._name} cancelled"
            )

    # =========================================================================
    # Python Protocols
    # =========================================================================

    def __call__(
        self,
        metric: Any,
        **kwargs: Any,
    ) -> Any:
        """Execute the task as a callable."""

        return self.execute(
            metric,
            **kwargs,
        )

    def __repr__(
        self,
    ) -> str:

        return (
            f"MetricMiddlewareTask("
            f"name={self._name!r}, "
            f"priority={self._priority}, "
            f"executions={self._executions}"
            f")"
        )

    def __str__(
        self,
    ) -> str:

        return self._name
"""
SciOS-NG Runtime Metrics Middleware Stage.

Represents a single executable middleware stage.

SciOS-NG v0.2
"""

from __future__ import annotations

import uuid

from datetime import datetime
from typing import Any, Callable


# ============================================================================
# MetricMiddlewareStage
# ============================================================================


class MetricMiddlewareStage:
    """
    Runtime Metric Middleware Stage.

    Responsibilities
    ----------------
    - Represent a single middleware stage
    - Execute an optional handler
    - Manage stage lifecycle
    - Track execution statistics
    - Expose runtime diagnostics
    """

    # =========================================================================
    # Constructor
    # =========================================================================

    def __init__(
        self,
        name: str,
        handler: Callable | None = None,
        description: str = "",
    ) -> None:

        if not isinstance(name, str) or not name.strip():
            raise ValueError(
                "Stage name must be a non-empty string"
            )

        if handler is not None and not callable(handler):
            raise TypeError(
                "Stage handler must be callable"
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
        # Runtime State
        # ---------------------------------------------------------------------

        self._enabled = True
        self._running = False
        self._closed = False

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

        self._last_result: Any = None
        self._last_error: Exception | None = None

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

    # =========================================================================
    # Execution
    # =========================================================================

    def execute(
        self,
        metric: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute the stage handler.

        If no handler is configured, the metric passes through unchanged.

        Statistics are updated only after an execution attempt has actually
        started.
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

            self._last_result = result
            self._last_error = None

            self._success += 1
            self._executions += 1

            return result

        except Exception as exc:

            self._last_error = exc

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
    ) -> "MetricMiddlewareStage":
        """Replace the stage handler."""

        if not callable(handler):
            raise TypeError(
                "Stage handler must be callable"
            )

        self._handler = handler
        self._updated_at = datetime.utcnow()

        return self

    def clear_handler(
        self,
    ) -> "MetricMiddlewareStage":
        """Remove the stage handler."""

        self._handler = None
        self._updated_at = datetime.utcnow()

        return self

    def handler(
        self,
    ) -> Callable | None:
        """Return the current handler."""

        return self._handler

    # =========================================================================
    # Lifecycle
    # =========================================================================

    def enable(
        self,
    ) -> "MetricMiddlewareStage":
        """Enable the stage."""

        self._enabled = True
        self._updated_at = datetime.utcnow()

        return self

    def disable(
        self,
    ) -> "MetricMiddlewareStage":
        """Disable the stage."""

        self._enabled = False
        self._updated_at = datetime.utcnow()

        return self

    def close(
        self,
    ) -> "MetricMiddlewareStage":
        """Close the stage."""

        self._closed = True
        self._updated_at = datetime.utcnow()

        return self

    def reopen(
        self,
    ) -> "MetricMiddlewareStage":
        """Reopen the stage."""

        self._closed = False
        self._updated_at = datetime.utcnow()

        return self

    def reset(
        self,
    ) -> "MetricMiddlewareStage":
        """
        Reset runtime statistics and execution state.

        Configuration such as name, description, handler and lifecycle state
        is preserved.
        """

        self._running = False

        self._executions = 0
        self._success = 0
        self._failures = 0

        self._last_result = None
        self._last_error = None

        self._updated_at = datetime.utcnow()

        return self

    # =========================================================================
    # Diagnostics
    # =========================================================================

    def statistics(
        self,
    ) -> dict[str, Any]:
        """Return execution statistics."""

        return {
            "name": self._name,
            "executions": self._executions,
            "success": self._success,
            "failures": self._failures,
            "last_result": self._last_result,
            "last_error": self._last_error,
        }

    def status(
        self,
    ) -> dict[str, bool]:
        """Return current runtime state."""

        return {
            "enabled": self._enabled,
            "running": self._running,
            "closed": self._closed,
            "active": self.active,
        }

    # =========================================================================
    # Internal
    # =========================================================================

    def _ensure_active(
        self,
    ) -> None:
        """Ensure the stage can execute."""

        if not self._enabled:
            raise RuntimeError(
                f"Stage {self._name} disabled"
            )

        if self._closed:
            raise RuntimeError(
                f"Stage {self._name} closed"
            )

    # =========================================================================
    # Python Protocols
    # =========================================================================

    def __call__(
        self,
        metric: Any,
        **kwargs: Any,
    ) -> Any:
        """Execute the stage as a callable."""

        return self.execute(
            metric,
            **kwargs,
        )

    def __repr__(
        self,
    ) -> str:

        return (
            f"MetricMiddlewareStage("
            f"name={self._name!r}, "
            f"executions={self._executions}"
            f")"
        )

    def __str__(
        self,
    ) -> str:

        return self._name
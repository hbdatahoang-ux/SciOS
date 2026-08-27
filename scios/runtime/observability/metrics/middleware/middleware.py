"""
SciOS-NG Runtime Metrics Middleware
===================================

Core middleware execution unit.

SciOS-NG v0.2
Python 3.11+
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Callable


# ==============================================================
# MetricMiddleware
# ==============================================================


class MetricMiddleware:
    """
    Runtime Metric Middleware.

    A lightweight execution unit responsible for applying a
    callable handler to a metric and tracking runtime state.

    Responsibilities
    ----------------
    - Represent a single middleware component
    - Execute a middleware handler
    - Manage middleware lifecycle
    - Track execution statistics
    - Preserve the last successful result
    - Preserve the last execution error
    - Provide runtime diagnostics

    Notes
    -----
    ``last_result`` and ``last_error`` are read-only properties.
    Configuration methods return ``self`` to support fluent usage.
    """

    # ==========================================================
    # Constructor
    # ==========================================================

    def __init__(
        self,
        name: str = "MetricMiddleware",
        handler: Callable[..., Any] | None = None,
        description: str = "",
    ) -> None:
        """
        Create a metric middleware instance.

        Parameters
        ----------
        name:
            Human-readable middleware name.

        handler:
            Optional callable receiving ``metric`` and ``**kwargs``.

        description:
            Optional middleware description.
        """

        if not isinstance(name, str):
            raise TypeError("name must be a string")

        if not name.strip():
            raise ValueError("name must not be empty")

        if handler is not None and not callable(handler):
            raise TypeError(
                "handler must be callable or None"
            )

        # ------------------------------------------------------
        # Identity
        # ------------------------------------------------------

        self._id = str(uuid.uuid4())
        self._name = name
        self._description = description

        # ------------------------------------------------------
        # Handler
        # ------------------------------------------------------

        self._handler = handler

        # ------------------------------------------------------
        # Runtime State
        # ------------------------------------------------------

        self._enabled = True
        self._running = False
        self._closed = False

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
        """
        Return the unique middleware identifier.
        """

        return self._id

    @property
    def name(self) -> str:
        """
        Return middleware name.
        """

        return self._name

    @property
    def description(self) -> str:
        """
        Return middleware description.
        """

        return self._description

    @property
    def enabled(self) -> bool:
        """
        Return whether middleware is enabled.
        """

        return self._enabled

    @property
    def running(self) -> bool:
        """
        Return whether middleware is currently executing.
        """

        return self._running

    @property
    def closed(self) -> bool:
        """
        Return whether middleware is closed.
        """

        return self._closed

    @property
    def active(self) -> bool:
        """
        Return whether middleware is available for execution.
        """

        return (
            self._enabled
            and not self._closed
        )

    @property
    def last_result(self) -> Any:
        """
        Return the last successful execution result.

        Returns
        -------
        Any
            Last successful result, or ``None`` if there has not
            been a successful execution.
        """

        return self._last_result

    @property
    def last_error(self) -> Exception | None:
        """
        Return the last execution error.

        Returns
        -------
        Exception | None
            The last exception raised by the handler, or ``None``
            when the last execution was successful.
        """

        return self._last_error

    # ==========================================================
    # Execution
    # ==========================================================

    def execute(
        self,
        metric: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute middleware against a metric.

        The handler is invoked when configured. Without a handler,
        the input metric passes through unchanged.

        Successful executions update ``last_result`` and clear
        ``last_error``.

        Failed executions update ``last_error`` and clear
        ``last_result`` while re-raising the original exception.
        """

        self._ensure_active()

        self._running = True
        self._updated_at = datetime.utcnow()

        try:
            if self._handler is not None:
                result = self._handler(
                    metric,
                    **kwargs,
                )
            else:
                result = metric

            # --------------------------------------------------
            # Successful execution state
            # --------------------------------------------------

            self._last_result = result
            self._last_error = None

            self._executions += 1
            self._success += 1

            return result

        except Exception as exc:
            # --------------------------------------------------
            # Failed execution state
            # --------------------------------------------------

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
        Execute middleware.

        Alias for :meth:`execute`.
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
        Process a metric through this middleware.

        Alias for :meth:`execute`.
        """

        return self.execute(
            metric,
            **kwargs,
        )

    # ==========================================================
    # Handler Management
    # ==========================================================

    def set_handler(
        self,
        handler: Callable[..., Any] | None,
    ) -> "MetricMiddleware":
        """
        Set or replace the middleware handler.

        Parameters
        ----------
        handler:
            Callable handler or ``None`` to remove the handler.

        Returns
        -------
        MetricMiddleware
            ``self`` for fluent usage.
        """

        if handler is not None and not callable(handler):
            raise TypeError(
                "handler must be callable or None"
            )

        self._handler = handler
        self._updated_at = datetime.utcnow()

        return self

    def handler(self) -> Callable[..., Any] | None:
        """
        Return the current middleware handler.
        """

        return self._handler

    def clear_handler(self) -> "MetricMiddleware":
        """
        Remove the current middleware handler.

        Returns
        -------
        MetricMiddleware
            ``self`` for fluent usage.
        """

        self._handler = None
        self._updated_at = datetime.utcnow()

        return self

    # ==========================================================
    # Lifecycle
    # ==========================================================

    def enable(self) -> "MetricMiddleware":
        """
        Enable middleware.
        """

        self._enabled = True
        self._updated_at = datetime.utcnow()

        return self

    def disable(self) -> "MetricMiddleware":
        """
        Disable middleware.

        Disabled middleware cannot execute.
        """

        self._enabled = False
        self._updated_at = datetime.utcnow()

        return self

    def close(self) -> "MetricMiddleware":
        """
        Close middleware.

        Closed middleware cannot execute.
        """

        self._closed = True
        self._updated_at = datetime.utcnow()

        return self

    def reopen(self) -> "MetricMiddleware":
        """
        Reopen middleware.

        Reopening does not automatically enable a middleware
        that was explicitly disabled.
        """

        self._closed = False
        self._updated_at = datetime.utcnow()

        return self

    # ==========================================================
    # Statistics
    # ==========================================================

    def statistics(self) -> dict[str, Any]:
        """
        Return middleware execution statistics.

        The returned dictionary is a snapshot and does not expose
        internal mutable state.
        """

        return {
            "name": self._name,
            "executions": self._executions,
            "success": self._success,
            "failures": self._failures,
            "enabled": self._enabled,
            "closed": self._closed,
            "active": self.active,
        }

    def reset(self) -> "MetricMiddleware":
        """
        Reset runtime statistics and execution diagnostics.

        Configuration such as name, description, handler, enabled
        state, and closed state is preserved.
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
    # Diagnostics
    # ==========================================================

    def status(self) -> dict[str, bool]:
        """
        Return middleware runtime status.
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
        Ensure middleware is available for execution.
        """

        if not self._enabled:
            raise RuntimeError(
                f"Middleware {self._name} disabled"
            )

        if self._closed:
            raise RuntimeError(
                f"Middleware {self._name} closed"
            )

    # ==========================================================
    # Python Protocols
    # ==========================================================

    def __call__(
        self,
        metric: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute middleware as a callable.
        """

        return self.execute(
            metric,
            **kwargs,
        )

    def __repr__(self) -> str:
        """
        Return a diagnostic representation.
        """

        return (
            f"MetricMiddleware("
            f"name={self._name!r}, "
            f"executions={self._executions}, "
            f"success={self._success}, "
            f"failures={self._failures}"
            f")"
        )

    def __str__(self) -> str:
        """
        Return middleware name.
        """

        return self._name
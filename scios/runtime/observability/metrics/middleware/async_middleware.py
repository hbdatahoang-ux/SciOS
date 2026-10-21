"""
SciOS-NG Runtime Metrics Async Middleware

Asynchronous middleware execution unit.

SciOS-NG v0.2
"""

from __future__ import annotations

import inspect
import uuid

from datetime import datetime
from typing import Any, Awaitable, Callable


# ==============================================================
# MetricAsyncMiddleware
# ==============================================================


class MetricAsyncMiddleware:
    """
    Runtime asynchronous Metric Middleware.

    Responsibilities
    ----------------
    - Represent a single asynchronous middleware component
    - Execute sync or async middleware handlers
    - Manage middleware lifecycle
    - Track execution statistics
    - Provide runtime diagnostics
    """

    # ==========================================================
    # Constructor
    # ==========================================================

    def __init__(
        self,
        name: str = "MetricAsyncMiddleware",
        handler: Callable | None = None,
        description: str = "",
    ) -> None:

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

    # ==========================================================
    # Execution
    # ==========================================================

    async def execute(
        self,
        metric: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute middleware asynchronously.

        Both synchronous and asynchronous handlers are supported.
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

                if inspect.isawaitable(result):
                    result = await result

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

    async def run(
        self,
        metric: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Alias for execute().
        """

        return await self.execute(
            metric,
            **kwargs,
        )

    async def process(
        self,
        metric: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Alias for execute().
        """

        return await self.execute(
            metric,
            **kwargs,
        )

    # ==========================================================
    # Handler Management
    # ==========================================================

    def set_handler(
        self,
        handler: Callable | None,
    ) -> "MetricAsyncMiddleware":
        """
        Set middleware handler.
        """

        if handler is not None and not callable(handler):
            raise TypeError(
                "handler must be callable or None"
            )

        self._handler = handler
        self._updated_at = datetime.utcnow()

        return self

    def handler(self) -> Callable | None:
        """
        Return current middleware handler.
        """

        return self._handler

    def clear_handler(self) -> "MetricAsyncMiddleware":
        """
        Remove current middleware handler.
        """

        self._handler = None
        self._updated_at = datetime.utcnow()

        return self

    # ==========================================================
    # Lifecycle
    # ==========================================================

    def enable(self) -> "MetricAsyncMiddleware":
        """
        Enable middleware.
        """

        self._enabled = True
        self._updated_at = datetime.utcnow()

        return self

    def disable(self) -> "MetricAsyncMiddleware":
        """
        Disable middleware.
        """

        self._enabled = False
        self._updated_at = datetime.utcnow()

        return self

    def close(self) -> "MetricAsyncMiddleware":
        """
        Close middleware.
        """

        self._closed = True
        self._updated_at = datetime.utcnow()

        return self

    def reopen(self) -> "MetricAsyncMiddleware":
        """
        Reopen middleware.
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
        """

        return {
            "name": self._name,
            "executions": self._executions,
            "success": self._success,
            "failures": self._failures,
            "enabled": self._enabled,
            "closed": self._closed,
        }

    def reset(self) -> "MetricAsyncMiddleware":
        """
        Reset execution statistics and diagnostics.

        Configuration and lifecycle state are preserved.
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
        Return middleware runtime status.
        """

        return {
            "enabled": self._enabled,
            "running": self._running,
            "closed": self._closed,
            "active": self.active,
        }

    @property
    def last_result(self) -> Any:
        """
        Return last successful result.
        """

        return self._last_result

    @property
    def last_error(self) -> Exception | None:
        """
        Return last execution error.
        """

        return self._last_error

    # ==========================================================
    # Internal
    # ==========================================================

    def _ensure_active(self) -> None:
        """
        Ensure middleware can execute.
        """

        if not self._enabled:
            raise RuntimeError(
                f"Async middleware {self._name} disabled"
            )

        if self._closed:
            raise RuntimeError(
                f"Async middleware {self._name} closed"
            )

    # ==========================================================
    # Python Protocols
    # ==========================================================

    def __len__(self) -> int:
        return self._executions

    def __call__(
        self,
        metric: Any,
        **kwargs: Any,
    ) -> Awaitable[Any]:
        return self.execute(
            metric,
            **kwargs,
        )

    def __repr__(self) -> str:
        return (
            f"MetricAsyncMiddleware("
            f"name={self._name!r}, "
            f"executions={self._executions}, "
            f"success={self._success}, "
            f"failures={self._failures}"
            f")"
        )

    def __str__(self) -> str:
        return self._name
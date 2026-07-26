"""
SciOS Observability - Tracing Middleware
========================================

Runtime middleware for automatic tracing instrumentation.

Responsibilities
----------------
- Create execution traces
- Create root spans
- Record lifecycle events
- Capture exceptions
- Export completed traces

The middleware is framework-agnostic and can be attached
to the SciOS Runtime, Planner, Executor, or Agent system.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .context import TraceContext
from .event import Event
from .manager import TraceManager
from .status import TraceStatus

__all__ = [
    "TracingMiddleware",
]


class TracingMiddleware:
    """
    Automatic runtime tracing middleware.
    """

    def __init__(
        self,
        manager: TraceManager,
    ) -> None:

        self.manager = manager

    # ======================================================
    # Lifecycle
    # ======================================================

    def before_execution(
        self,
        operation: str,
        **attributes: Any,
    ) -> TraceContext:
        """
        Create trace and root span.
        """

        context = self.manager.start_trace(
            operation,
            attributes=attributes,
        )

        span = context.current_span

        if span is not None:
            span.add_event(
                Event(
                    name="started",
                )
            )

        return context

    def after_execution(
        self,
        context: TraceContext,
        result: Any = None,
    ) -> None:
        """
        Complete trace.
        """

        span = context.current_span

        if span is not None:

            span.attributes["result_type"] = (
                type(result).__name__
                if result is not None
                else "None"
            )

            span.add_event(
                Event(
                    name="completed",
                )
            )

        self.manager.end_trace(
            context,
            status=TraceStatus.OK,
        )

    def on_exception(
        self,
        context: TraceContext,
        exc: Exception,
    ) -> None:
        """
        Record execution failure.
        """

        span = context.current_span

        if span is not None:

            span.attributes["exception.type"] = (
                type(exc).__name__
            )

            span.attributes["exception.message"] = (
                str(exc)
            )

            span.add_event(
                Event(
                    name="exception",
                    attributes={
                        "type": type(exc).__name__,
                        "message": str(exc),
                    },
                )
            )

        self.manager.end_trace(
            context,
            status=TraceStatus.ERROR,
        )

    # ======================================================
    # Wrapper
    # ======================================================

    def wrap(
        self,
        operation: str,
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute a callable with automatic tracing.
        """

        context = self.before_execution(
            operation,
        )

        try:

            result = func(
                *args,
                **kwargs,
            )

            self.after_execution(
                context,
                result,
            )

            return result

        except Exception as exc:

            self.on_exception(
                context,
                exc,
            )

            raise

    # ======================================================
    # Utilities
    # ======================================================

    def __call__(
        self,
        operation: str,
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Allow middleware to be used as a callable.
        """

        return self.wrap(
            operation,
            func,
            *args,
            **kwargs,
        )

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"active_traces={len(self.manager.active_traces)})"
        )
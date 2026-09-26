"""
SciOS-NG Runtime Metrics Tracing Integration

Integration layer between Runtime Metrics and Tracing subsystem.

SciOS-NG v0.2
"""

from __future__ import annotations

from contextlib import nullcontext
from datetime import datetime
from typing import Any, Callable


# ==============================================================
# MetricTracingIntegration
# ==============================================================


class MetricTracingIntegration:
    """
    Integration layer for connecting Metrics with Tracing.

    Responsibilities
    ----------------
    - Attach metrics to the active tracing context
    - Create tracing spans when supported
    - Execute metric operations inside a trace/span
    - Support generic tracing providers
    - Preserve tracing subsystem isolation
    - Track integration statistics
    """

    def __init__(
        self,
        tracer: Any = None,
        name: str = "MetricTracingIntegration",
        description: str = "",
    ) -> None:

        self._name = name
        self._description = description

        self._tracer = tracer

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
    def tracer(self) -> Any:
        return self._tracer

    @property
    def configured(self) -> bool:
        return self._tracer is not None

    @property
    def last_result(self) -> Any:
        return self._last_result

    @property
    def last_error(self) -> Exception | None:
        return self._last_error

    # ==========================================================
    # Tracer Management
    # ==========================================================

    def set_tracer(
        self,
        tracer: Any,
    ) -> "MetricTracingIntegration":
        """
        Set the tracing provider.
        """

        self._tracer = tracer
        self._updated_at = datetime.utcnow()

        return self

    def clear_tracer(
        self,
    ) -> "MetricTracingIntegration":
        """
        Remove the current tracing provider.
        """

        self._tracer = None
        self._updated_at = datetime.utcnow()

        return self

    # ==========================================================
    # Trace Context
    # ==========================================================

    def current_span(self) -> Any:
        """
        Return the current active span when supported.
        """

        if self._tracer is None:
            return None

        current = getattr(
            self._tracer,
            "current_span",
            None,
        )

        if callable(current):
            return current()

        current = getattr(
            self._tracer,
            "active_span",
            None,
        )

        if callable(current):
            return current()

        return None

    def current_trace(self) -> Any:
        """
        Return the current active trace when supported.
        """

        if self._tracer is None:
            return None

        current = getattr(
            self._tracer,
            "current_trace",
            None,
        )

        if callable(current):
            return current()

        current = getattr(
            self._tracer,
            "active_trace",
            None,
        )

        if callable(current):
            return current()

        return None

    # ==========================================================
    # Attribute / Event Attachment
    # ==========================================================

    def set_attribute(
        self,
        key: str,
        value: Any,
    ) -> "MetricTracingIntegration":
        """
        Set an attribute on the current span when supported.
        """

        span = self.current_span()

        if span is None:
            return self

        setter = getattr(
            span,
            "set_attribute",
            None,
        )

        if callable(setter):
            setter(key, value)

        else:
            setter = getattr(
                span,
                "set_tag",
                None,
            )

            if callable(setter):
                setter(key, value)

        self._updated_at = datetime.utcnow()

        return self

    def add_event(
        self,
        name: str,
        attributes: dict[str, Any] | None = None,
    ) -> "MetricTracingIntegration":
        """
        Add an event to the current span when supported.
        """

        span = self.current_span()

        if span is None:
            return self

        event = getattr(
            span,
            "add_event",
            None,
        )

        if callable(event):
            if attributes is None:
                event(name)
            else:
                event(
                    name,
                    attributes=attributes,
                )

        self._updated_at = datetime.utcnow()

        return self

    # ==========================================================
    # Span Creation
    # ==========================================================

    def start_span(
        self,
        name: str,
        **kwargs: Any,
    ) -> Any:
        """
        Start a span using the configured tracer.

        Returns None when tracing is not configured.
        """

        if self._tracer is None:
            return None

        start_span = getattr(
            self._tracer,
            "start_span",
            None,
        )

        if callable(start_span):
            return start_span(
                name,
                **kwargs,
            )

        start_as_current = getattr(
            self._tracer,
            "start_as_current_span",
            None,
        )

        if callable(start_as_current):
            return start_as_current(
                name,
                **kwargs,
            )

        return None

    # ==========================================================
    # Execution
    # ==========================================================

    def execute(
        self,
        metric: Any,
        handler: Callable | None = None,
        span_name: str | None = None,
        **kwargs: Any,
    ) -> Any:
        """
        Execute a metric operation inside a tracing span when
        tracing is available.
        """

        try:
            context = self._span_context(
                span_name or self._name,
                **kwargs,
            )

            with context as span:
                if span is not None:
                    self._attach_metric(
                        span,
                        metric,
                    )

                if handler is None:
                    result = metric
                else:
                    result = handler(metric)

                if span is not None:
                    self._attach_result(
                        span,
                        result,
                    )

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

    def trace(
        self,
        metric: Any,
        handler: Callable | None = None,
        span_name: str | None = None,
        **kwargs: Any,
    ) -> Any:
        """
        Alias for execute().
        """

        return self.execute(
            metric,
            handler=handler,
            span_name=span_name,
            **kwargs,
        )

    def run(
        self,
        metric: Any,
        handler: Callable | None = None,
        span_name: str | None = None,
        **kwargs: Any,
    ) -> Any:
        """
        Alias for execute().
        """

        return self.execute(
            metric,
            handler=handler,
            span_name=span_name,
            **kwargs,
        )

    # ==========================================================
    # Internal Span Context
    # ==========================================================

    def _span_context(
        self,
        name: str,
        **kwargs: Any,
    ):
        """
        Resolve a context manager for span execution.
        """

        if self._tracer is None:
            return nullcontext(None)

        start = getattr(
            self._tracer,
            "start_as_current_span",
            None,
        )

        if callable(start):
            return start(
                name,
                **kwargs,
            )

        start = getattr(
            self._tracer,
            "start_span",
            None,
        )

        if callable(start):
            span = start(
                name,
                **kwargs,
            )

            if hasattr(span, "__enter__") and hasattr(
                span,
                "__exit__",
            ):
                return span

            return nullcontext(span)

        return nullcontext(None)

    @staticmethod
    def _attach_metric(
        span: Any,
        metric: Any,
    ) -> None:
        """
        Attach basic metric information to a span.
        """

        setter = getattr(
            span,
            "set_attribute",
            None,
        )

        if not callable(setter):
            return

        if isinstance(metric, dict):
            setter(
                "metrics.type",
                "mapping",
            )

            setter(
                "metrics.keys",
                len(metric),
            )

        else:
            setter(
                "metrics.type",
                type(metric).__name__,
            )

    @staticmethod
    def _attach_result(
        span: Any,
        result: Any,
    ) -> None:
        """
        Attach result metadata to a span.
        """

        setter = getattr(
            span,
            "set_attribute",
            None,
        )

        if callable(setter):
            setter(
                "metrics.result_type",
                type(result).__name__,
            )

    # ==========================================================
    # Diagnostics
    # ==========================================================

    def statistics(self) -> dict[str, Any]:
        """
        Return integration statistics.
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
        Return integration status.
        """

        return {
            "configured": self.configured,
            "active": self.current_span() is not None,
        }

    def reset(self) -> "MetricTracingIntegration":
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
            f"MetricTracingIntegration("
            f"name={self._name!r}, "
            f"configured={self.configured}, "
            f"executions={self._executions}, "
            f"success={self._success}, "
            f"failures={self._failures}"
            f")"
        )

    def __str__(self) -> str:

        return self._name
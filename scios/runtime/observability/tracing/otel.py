"""
SciOS Observability - OpenTelemetry Exporter
============================================

Adapter between SciOS tracing models and OpenTelemetry.

Responsibilities
----------------
- Convert SciOS Trace -> OTel Span data
- Convert SciOS Span -> OTel Span
- Optional integration with OpenTelemetry SDK
- Graceful fallback if SDK is unavailable
"""

from __future__ import annotations

from typing import Any

from .exporter import TraceExporter
from .trace import Trace
from .span import Span

__all__ = [
    "OpenTelemetryExporter",
]


class OpenTelemetryExporter(TraceExporter):
    """
    Adapter exporting SciOS traces to OpenTelemetry.

    This exporter intentionally treats the OpenTelemetry SDK
    as an optional dependency. If the SDK is not installed,
    export() becomes a no-op rather than raising ImportError.
    """

    def __init__(self) -> None:
        self._enabled = False
        self._provider = None

        try:
            from opentelemetry import trace as otel_trace  # type: ignore

            self._provider = otel_trace
            self._enabled = True

        except ImportError:
            self._enabled = False

    @property
    def enabled(self) -> bool:
        """
        Whether the OpenTelemetry SDK is available.
        """
        return self._enabled

    def export_trace(self, trace: Trace) -> bool:
        """
        Export a complete trace.

        Returns
        -------
        bool
            True if export succeeded, False if disabled.
        """
        if not self._enabled:
            return False

        for span in trace.spans:
            self.export_span(span)

        return True

    def export_span(self, span: Span) -> bool:
        """
        Export a single span.

        Current implementation is a compatibility stub.
        A future version will create real OTel spans.
        """
        if not self._enabled:
            return False

        # Placeholder for OTel SDK mapping.
        return True

    def export(self, trace: Trace) -> bool:
        """
        Alias for export_trace().
        """
        return self.export_trace(trace)

    def shutdown(self) -> None:
        """
        Flush exporter if the SDK supports it.
        """
        if not self._enabled:
            return

        provider = getattr(self._provider, "get_tracer_provider", None)

        if callable(provider):
            tracer_provider = provider()

            shutdown = getattr(tracer_provider, "shutdown", None)

            if callable(shutdown):
                shutdown()

    def __repr__(self) -> str:
        state = "enabled" if self._enabled else "disabled"
        return f"{self.__class__.__name__}({state})"
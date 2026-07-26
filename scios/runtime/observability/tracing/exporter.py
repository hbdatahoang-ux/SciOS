"""
SciOS Observability - Base Trace Exporter
=========================================

Abstract base class for all tracing exporters.

Responsibilities
----------------
- Export traces
- Export spans
- Export events
- Lifecycle management
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .event import Event
from .span import Span
from .trace import Trace

__all__ = [
    "TraceExporter",
]


class TraceExporter(ABC):
    """
    Abstract tracing exporter.

    Every exporter (Memory, JSON, OpenTelemetry,
    Jaeger, Zipkin...) should inherit from this class.
    """

    def __init__(self) -> None:
        self._started = False

    # =====================================================
    # Lifecycle
    # =====================================================

    def start(self) -> None:
        """
        Initialize exporter resources.
        """
        self._started = True

    def shutdown(self) -> None:
        """
        Release exporter resources.
        """
        self._started = False

    @property
    def started(self) -> bool:
        return self._started

    # =====================================================
    # Export Interface
    # =====================================================

    @abstractmethod
    def export_trace(
        self,
        trace: Trace,
    ) -> None:
        """
        Export a completed trace.
        """
        raise NotImplementedError

    @abstractmethod
    def export_span(
        self,
        span: Span,
    ) -> None:
        """
        Export a completed span.
        """
        raise NotImplementedError

    def export_event(
        self,
        event: Event,
    ) -> None:
        """
        Export an event.

        Optional override.
        """
        return None

    # =====================================================
    # Batch Export
    # =====================================================

    def export_traces(
        self,
        traces: list[Trace],
    ) -> None:
        """
        Export multiple traces.
        """
        for trace in traces:
            self.export_trace(trace)

    def export_spans(
        self,
        spans: list[Span],
    ) -> None:
        """
        Export multiple spans.
        """
        for span in spans:
            self.export_span(span)

    def export_events(
        self,
        events: list[Event],
    ) -> None:
        """
        Export multiple events.
        """
        for event in events:
            self.export_event(event)

    # =====================================================
    # Flush
    # =====================================================

    def flush(self) -> None:
        """
        Flush buffered data.

        Optional for subclasses.
        """
        return None

    # =====================================================
    # Context Manager
    # =====================================================

    def __enter__(self) -> "TraceExporter":
        self.start()
        return self

    def __exit__(
        self,
        exc_type,
        exc,
        tb,
    ) -> None:
        self.flush()
        self.shutdown()

    # =====================================================
    # Representation
    # =====================================================

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(started={self.started})"
        )
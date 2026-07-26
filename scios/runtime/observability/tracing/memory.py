"""
SciOS Observability - Memory Trace Exporter
==========================================

In-memory exporter for traces, spans and events.

Useful for:

- Unit testing
- Runtime debugging
- CLI inspection
- Development
"""

from __future__ import annotations

from .event import Event
from .exporter import TraceExporter
from .span import Span
from .trace import Trace


__all__ = [
    "MemoryExporter",
]


class MemoryExporter(TraceExporter):
    """
    In-memory tracing exporter.
    """

    def __init__(self) -> None:
        super().__init__()

        self.traces: list[Trace] = []

        self.spans: list[Span] = []

        self.events: list[Event] = []

    # =====================================================
    # Export
    # =====================================================

    def export_trace(
        self,
        trace: Trace,
    ) -> None:

        self.traces.append(trace)

    def export_span(
        self,
        span: Span,
    ) -> None:

        self.spans.append(span)

    def export_event(
        self,
        event: Event,
    ) -> None:

        self.events.append(event)

    # =====================================================
    # Query
    # =====================================================

    def get_trace(
        self,
        trace_id: str,
    ) -> Trace | None:

        for trace in self.traces:
            if trace.trace_id == trace_id:
                return trace

        return None

    def get_span(
        self,
        span_id: str,
    ) -> Span | None:

        for span in self.spans:
            if span.span_id == span_id:
                return span

        return None

    def get_spans_by_trace(
        self,
        trace_id: str,
    ) -> list[Span]:

        return [
            span
            for span in self.spans
            if span.trace_id == trace_id
        ]

    def get_events_by_span(
        self,
        span_id: str,
    ) -> list[Event]:

        return [
            event
            for event in self.events
            if getattr(event, "span_id", None) == span_id
        ]

    # =====================================================
    # Statistics
    # =====================================================

    @property
    def trace_count(self) -> int:
        return len(self.traces)

    @property
    def span_count(self) -> int:
        return len(self.spans)

    @property
    def event_count(self) -> int:
        return len(self.events)

    # =====================================================
    # Maintenance
    # =====================================================

    def clear(self) -> None:

        self.traces.clear()

        self.spans.clear()

        self.events.clear()

    def flush(self) -> None:
        """
        Nothing to flush for memory exporter.
        """
        return

    # =====================================================
    # Serialization
    # =====================================================

    def to_dict(self) -> dict:

        return {
            "trace_count": self.trace_count,
            "span_count": self.span_count,
            "event_count": self.event_count,
            "traces": [
                trace.to_dict()
                for trace in self.traces
            ],
            "spans": [
                span.to_dict()
                for span in self.spans
            ],
            "events": [
                event.to_dict()
                for event in self.events
            ],
        }

    # =====================================================
    # Representation
    # =====================================================

    def __len__(self) -> int:

        return self.trace_count

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"traces={self.trace_count}, "
            f"spans={self.span_count}, "
            f"events={self.event_count})"
        )
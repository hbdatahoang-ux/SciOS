"""
SciOS Observability - Trace Serialization
=========================================

Serialization utilities for Trace, Span and Event.

Responsibilities
----------------
- Serialize tracing objects
- Deserialize tracing objects
- Produce JSON-compatible structures
- Versioned serialization
"""

from __future__ import annotations

from typing import Any

from .event import Event
from .span import Span
from .trace import Trace

__all__ = [
    "TraceSerializer",
]


class TraceSerializer:
    """
    Serialization helper for tracing objects.
    """

    SCHEMA_VERSION = "1.0"

    # =====================================================
    # Event
    # =====================================================

    @staticmethod
    def serialize_event(
        event: Event,
    ) -> dict[str, Any]:

        return {
            "name": event.name,
            "phase": event.phase.value,
            "timestamp": event.timestamp.isoformat(),
            "attributes": event.attributes.to_dict(),
        }

    # =====================================================
    # Span
    # =====================================================

    @classmethod
    def serialize_span(
        cls,
        span: Span,
    ) -> dict[str, Any]:

        return {
            "span_id": span.span_id,
            "parent_span_id": span.parent_span_id,
            "trace_id": span.trace_id,

            "name": span.name,
            "status": span.status.value,

            "started_at": (
                span.started_at.isoformat()
                if span.started_at
                else None
            ),

            "finished_at": (
                span.finished_at.isoformat()
                if span.finished_at
                else None
            ),

            "duration": span.duration,

            "attributes": span.attributes.to_dict(),

            "baggage": span.baggage.to_dict(),

            "events": [
                cls.serialize_event(event)
                for event in span.events
            ],
        }

    # =====================================================
    # Trace
    # =====================================================

    @classmethod
    def serialize_trace(
        cls,
        trace: Trace,
    ) -> dict[str, Any]:

        return {

            "schema_version": cls.SCHEMA_VERSION,

            "trace_id": trace.trace_id,

            "name": trace.name,

            "status": trace.status.value,

            "started_at": (
                trace.started_at.isoformat()
                if trace.started_at
                else None
            ),

            "finished_at": (
                trace.finished_at.isoformat()
                if trace.finished_at
                else None
            ),

            "duration": trace.duration,

            "attributes": trace.attributes.to_dict(),

            "baggage": trace.baggage.to_dict(),

            "spans": [
                cls.serialize_span(span)
                for span in trace.spans
            ],
        }

    # =====================================================
    # Generic
    # =====================================================

    @classmethod
    def serialize(
        cls,
        obj: Any,
    ) -> dict[str, Any]:

        if isinstance(obj, Trace):
            return cls.serialize_trace(obj)

        if isinstance(obj, Span):
            return cls.serialize_span(obj)

        if isinstance(obj, Event):
            return cls.serialize_event(obj)

        raise TypeError(
            f"Unsupported object type: {type(obj)}"
        )
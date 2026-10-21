"""
SciOS-NG Observability Schemas

Unified schema definitions for:
    - Trace
    - Span
    - Metric
    - Log
    - Event

These schemas provide stable contracts between:

    Runtime Engine
        |
        Observability Pipeline
        |
        Exporters / Dashboard / CLI
"""


from __future__ import annotations


# ============================================================
# Package Metadata
# ============================================================

__title__ = "SciOS-NG Observability Schemas"

__version__ = "0.3.0"

__author__ = "SciOS-NG"

__description__ = (
    "Unified observability schema contracts "
    "for SciOS runtime."
)



# ============================================================
# Trace Schema
# ============================================================

from .trace_schema import (
    TraceSchema,
)



# ============================================================
# Span Schema
# ============================================================

from .span_schema import (
    SpanSchema,
)



# ============================================================
# Metric Schema
# ============================================================

from .metric_schema import (
    MetricSchema,
)



# ============================================================
# Log Schema
# ============================================================

from .log_schema import (
    LogSchema,
)



# ============================================================
# Event Schema
# ============================================================

from .event_schema import (
    EventSchema,
    EventContext,
    EventMetadata,
    EventType,
    EventLevel,
    EventStatus,
    EventSource,
)



# ============================================================
# Public API
# ============================================================

__all__ = [

    # Trace
    "TraceSchema",


    # Span
    "SpanSchema",


    # Metric
    "MetricSchema",


    # Log
    "LogSchema",


    # Event
    "EventSchema",
    "EventContext",
    "EventMetadata",

    "EventType",
    "EventLevel",
    "EventStatus",
    "EventSource",
]
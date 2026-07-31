"""
SciOS Runtime Observability
Shared tracing enums.
"""

from __future__ import annotations

from enum import Enum


class ExecutionPhase(str, Enum):
    """
    Runtime execution lifecycle phase.
    """

    CREATED = "created"
    SUBMITTED = "submitted"
    STARTED = "started"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SpanKind(str, Enum):
    """
    Span operation type.
    """

    INTERNAL = "internal"
    SERVER = "server"
    CLIENT = "client"
    PRODUCER = "producer"
    CONSUMER = "consumer"


class TraceState(str, Enum):
    """
    Trace lifecycle state.
    """

    ACTIVE = "active"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"


class SamplingDecision(str, Enum):
    """
    Trace sampling decision.
    """

    DROP = "drop"
    RECORD = "record"
    RECORD_AND_SAMPLE = "record_and_sample"


class Severity(str, Enum):
    """
    Event/log severity.
    """

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


__all__ = [
    "ExecutionPhase",
    "SpanKind",
    "TraceState",
    "SamplingDecision",
    "Severity",
]

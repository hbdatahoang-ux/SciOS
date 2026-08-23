"""
SciOS Runtime Observability
Shared tracing enums.

Python 3.11+
"""

from __future__ import annotations

from enum import Enum


# ==============================================================================
# Execution Phase
# ==============================================================================


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


# ==============================================================================
# Span Kind
# ==============================================================================


class SpanKind(str, Enum):
    """
    Span operation type.
    """

    INTERNAL = "internal"
    SERVER = "server"
    CLIENT = "client"
    PRODUCER = "producer"
    CONSUMER = "consumer"


# ==============================================================================
# Trace State
# ==============================================================================


class TraceState(str, Enum):
    """
    Trace lifecycle state.
    """

    ACTIVE = "active"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"


# ==============================================================================
# Sampling Decision
# ==============================================================================


class SamplingDecision(str, Enum):
    """
    Trace sampling decision.
    """

    DROP = "drop"
    RECORD = "record"
    RECORD_AND_SAMPLE = "record_and_sample"


# ==============================================================================
# Severity
# ==============================================================================


class Severity(str, Enum):
    """
    Event/log severity.
    """

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# ==============================================================================
# Public API
# ==============================================================================


__all__ = [
    "ExecutionPhase",
    "SpanKind",
    "TraceState",
    "SamplingDecision",
    "Severity",
]

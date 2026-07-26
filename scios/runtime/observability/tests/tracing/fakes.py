"""
SciOS Observability Tests
=========================

Tracing Fake Core Types

Shared type definitions used by the tracing test harness.

These objects intentionally mirror a subset of the real tracing API
while remaining lightweight and deterministic for unit testing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, TypeAlias
from copy import deepcopy

# =============================================================================
# Type aliases
# =============================================================================

Attributes: TypeAlias = dict[str, Any]
"""
Generic attribute mapping attached to traces, spans, and events.
"""

Metadata: TypeAlias = dict[str, Any]
"""
Metadata describing runtime, provenance, execution context, etc.
"""

# =============================================================================
# Fake status
# =============================================================================


class FakeStatus(str, Enum):
    """
    Simplified execution status used by fake tracing objects.

    Mirrors the lifecycle states commonly used by tracing systems.
    """

    CREATED = "CREATED"

    RUNNING = "RUNNING"

    SUCCESS = "SUCCESS"

    FAILURE = "FAILURE"

    CANCELLED = "CANCELLED"


# =============================================================================
# Fake Event
# =============================================================================


@dataclass(slots=True)
class FakeEvent:
    """
    Lightweight tracing event.

    Parameters
    ----------
    name:
        Event name.

    attributes:
        Structured event attributes.
    """

    name: str

    attributes: Attributes = field(default_factory=dict)

    timestamp: float | None = None

    def set_attribute(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Set or replace an attribute.
        """

        self.attributes[key] = value

    def update(
        self,
        **attributes: Any,
    ) -> None:
        """
        Update multiple attributes.
        """

        self.attributes.update(attributes)

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize event.
        """

        return {
            "name": self.name,
            "timestamp": self.timestamp,
            "attributes": dict(self.attributes),
        }


# =============================================================================
# Manager call history
# =============================================================================


@dataclass(slots=True)
class CallRecord:
    """
    Records one API invocation.

    Useful for asserting lifecycle order.
    """

    method: str

    args: tuple[Any, ...] = field(default_factory=tuple)

    kwargs: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:

        return {
            "method": self.method,
            "args": self.args,
            "kwargs": self.kwargs,
        }


# =============================================================================
# Processor callback history
# =============================================================================


@dataclass(slots=True)
class ProcessorCall:
    """
    Records a processor callback.

    Used to verify callback ordering and parameters.
    """

    method: str

    target: Any

    success: bool | None = None

    error: Exception | None = None

    metadata: Metadata = field(default_factory=dict)

    def failed(self) -> bool:
        """
        True if callback contains an exception.
        """

        return self.error is not None

    def to_dict(self) -> dict[str, Any]:

        return {
            "method": self.method,
            "target": repr(self.target),
            "success": self.success,
            "error": (
                None
                if self.error is None
                else repr(self.error)
            ),
            "metadata": dict(self.metadata),
        }


# =============================================================================
# Public exports
# =============================================================================

__all__ = [
    "Attributes",
    "Metadata",
    "FakeStatus",
    "FakeEvent",
    "CallRecord",
    "ProcessorCall",
]
"""
SciOS Observability Tests
=========================

FakeTrace - Core

Core fake implementation used by tracing unit tests.

Responsibilities
----------------
- Deterministic lifecycle
- Timing
- Status management
- Reset support

This object intentionally mirrors the public contract of the real
Trace implementation while remaining lightweight.
"""


from dataclasses import dataclass, field



@dataclass(slots=True)
class FakeTrace:
    """
    Fake Trace used by unit tests.

    Only lifecycle behaviour is implemented here.

    Attributes, events, serialization and exception recording
    are implemented in later sections of FakeTrace.
    """

    # ==========================================================
    # Identity
    # ==========================================================

    name: str

    trace_id: str | None = None

    parent_id: str | None = None

    # ==========================================================
    # Lifecycle
    # ==========================================================

    status: FakeStatus = FakeStatus.CREATED

    finished: bool = False

    # ==========================================================
    # Timing
    # ==========================================================

    started_at: float | None = None

    ended_at: float | None = None

    # ==========================================================
    # Internal
    # ==========================================================

    _running: bool = field(
        default=False,
        init=False,
        repr=False,
    )

    # ==========================================================
    # Lifecycle
    # ==========================================================

    def start(
        self,
        timestamp: float = 0.0,
    ) -> "FakeTrace":
        """
        Start the trace.

        Calling start() more than once has no effect.
        """

        if self._running:
            return self

        self.started_at = timestamp
        self.ended_at = None

        self.finished = False

        self.status = FakeStatus.RUNNING

        self._running = True

        return self

    def finish(
        self,
        status: FakeStatus = FakeStatus.SUCCESS,
        timestamp: float | None = None,
    ) -> "FakeTrace":
        """
        Finish the trace.

        Safe to call multiple times.
        """

        if not self._running:
            return self

        self.ended_at = (
            self.started_at
            if timestamp is None
            else timestamp
        )

        self.finished = True

        self.status = status

        self._running = False

        return self

    def reset(self) -> "FakeTrace":
        """
        Restore initial state.
        """

        self.status = FakeStatus.CREATED

        self.finished = False

        self.started_at = None

        self.ended_at = None

        self._running = False

        return self

    # ==========================================================
    # Timing
    # ==========================================================

    @property
    def is_running(self) -> bool:
        """
        True while trace is active.
        """

        return self._running

    @property
    def is_finished(self) -> bool:
        """
        True after finish().
        """

        return self.finished

    @property
    def duration(self) -> float | None:
        """
        Execution duration.

        Returns
        -------
        float | None
            None until the trace has both a start
            and finish timestamp.
        """

        if (
            self.started_at is None
            or self.ended_at is None
        ):
            return None

        return self.ended_at - self.started_at

    # ==========================================================
    # Helpers
    # ==========================================================

    def succeeded(self) -> bool:
        """
        True if finished successfully.
        """

        return self.status is FakeStatus.SUCCESS

    def failed(self) -> bool:
        """
        True if failed.
        """

        return self.status is FakeStatus.FAILURE

    def cancelled(self) -> bool:
        """
        True if cancelled.
        """

        return self.status is FakeStatus.CANCELLED
# ==========================================================
# Trace Data
# ==========================================================

attributes: Attributes = field(
    default_factory=dict,
)
"""
User-defined trace attributes.

Examples
--------
{
    "runtime": "SciOS",
    "kernel": "SciKernel",
    "stage": "planner",
}
"""

metadata: Metadata = field(
    default_factory=dict,
)
"""
System-generated metadata.

Typically contains provenance information,
runtime information, host information,
workflow identifiers, etc.
"""

events: list[FakeEvent] = field(
    default_factory=list,
)
"""
Ordered event history.

Events preserve insertion order.
"""

exceptions: list[Exception] = field(
    default_factory=list,
)
"""
Exceptions recorded during execution.

The trace may finish successfully even if
exceptions were captured and handled.
"""
# ==========================================================
# Attributes
# ==========================================================

def set_attribute(
    self,
    key: str,
    value: Any,
) -> "FakeTrace":
    """
    Set or replace a trace attribute.

    Parameters
    ----------
    key:
        Attribute name.

    value:
        Attribute value.

    Returns
    -------
    FakeTrace
        Enables fluent API.
    """

    self.attributes[key] = value
    return self


def get_attribute(
    self,
    key: str,
    default: Any = None,
) -> Any:
    """
    Return an attribute.

    Parameters
    ----------
    key:
        Attribute name.

    default:
        Value returned when the attribute
        does not exist.
    """

    return self.attributes.get(key, default)


# ==========================================================
# Metadata
# ==========================================================

def set_metadata(
    self,
    key: str,
    value: Any,
) -> "FakeTrace":
    """
    Set runtime metadata.
    """

    self.metadata[key] = value
    return self


def get_metadata(
    self,
    key: str,
    default: Any = None,
) -> Any:
    """
    Return metadata value.
    """

    return self.metadata.get(key, default)


# ==========================================================
# Events
# ==========================================================

def add_event(
    self,
    name: str,
    *,
    timestamp: float | None = None,
    attributes: Attributes | None = None,
) -> FakeEvent:
    """
    Create and append an event.

    Returns
    -------
    FakeEvent
        Newly created event.
    """

    event = FakeEvent(
        name=name,
        timestamp=timestamp,
        attributes=dict(attributes or {}),
    )

    self.events.append(event)

    return event


def clear_events(self) -> "FakeTrace":
    """
    Remove every recorded event.
    """

    self.events.clear()

    return self


# ==========================================================
# Exceptions
# ==========================================================

def record_exception(
    self,
    error: Exception,
) -> "FakeTrace":
    """
    Record an exception raised while
    executing the trace.

    Notes
    -----
    Recording an exception does not
    automatically fail the trace.

    Tests may explicitly call finish()
    with FAILURE if desired.
    """

    self.exceptions.append(error)

    return self


@property
def has_exceptions(self) -> bool:
    """
    True if one or more exceptions
    were recorded.
    """

    return bool(self.exceptions)
# ==========================================================
# Serialization
# ==========================================================

def to_dict(self) -> dict[str, Any]:
    """
    Serialize the trace into a plain dictionary.

    Returns
    -------
    dict[str, Any]
        JSON-friendly representation of the trace.
    """

    return {
        "name": self.name,
        "trace_id": self.trace_id,
        "parent_id": self.parent_id,
        "status": self.status.value,
        "finished": self.finished,
        "started_at": self.started_at,
        "ended_at": self.ended_at,
        "duration": self.duration,
        "attributes": dict(self.attributes),
        "metadata": dict(self.metadata),
        "events": [
            event.to_dict()
            for event in self.events
        ],
        "exceptions": [
            {
                "type": type(exc).__name__,
                "message": str(exc),
            }
            for exc in self.exceptions
        ],
    }


@classmethod
def from_dict(
    cls,
    data: dict[str, Any],
) -> "FakeTrace":
    """
    Reconstruct a FakeTrace from a serialized dictionary.

    Notes
    -----
    Exceptions are restored as RuntimeError objects
    containing the original message because arbitrary
    exception reconstruction is not generally possible.
    """

    trace = cls(
        name=data["name"],
        trace_id=data.get("trace_id"),
        parent_id=data.get("parent_id"),
    )

    trace.status = FakeStatus(
        data.get(
            "status",
            FakeStatus.CREATED.value,
        )
    )

    trace.finished = data.get(
        "finished",
        False,
    )

    trace.started_at = data.get(
        "started_at",
    )

    trace.ended_at = data.get(
        "ended_at",
    )

    trace.attributes.update(
        data.get(
            "attributes",
            {},
        )
    )

    trace.metadata.update(
        data.get(
            "metadata",
            {},
        )
    )

    for event_data in data.get(
        "events",
        [],
    ):
        trace.events.append(
            FakeEvent(
                name=event_data["name"],
                timestamp=event_data.get("timestamp"),
                attributes=dict(
                    event_data.get(
                        "attributes",
                        {},
                    )
                ),
            )
        )

    for exc in data.get(
        "exceptions",
        [],
    ):
        trace.exceptions.append(
            RuntimeError(
                exc.get(
                    "message",
                    "",
                )
            )
        )

    return trace


# ==========================================================
# Copy
# ==========================================================

def copy(self) -> "FakeTrace":
    """
    Return a deep copy of the trace.
    """

    return self.from_dict(
        self.to_dict()
    )


# ==========================================================
# Representation
# ==========================================================

def __repr__(self) -> str:
    """
    Developer-friendly representation.
    """

    return (
        f"{self.__class__.__name__}("
        f"name={self.name!r}, "
        f"status={self.status.value!r}, "
        f"finished={self.finished}, "
        f"events={len(self.events)}, "
        f"exceptions={len(self.exceptions)})"
    )
# ==========================================================
# Serialization
# ==========================================================

def to_dict(self) -> dict[str, Any]:
    """
    Serialize this trace into a JSON-friendly dictionary.

    Returns
    -------
    dict[str, Any]
        Plain Python representation suitable for testing,
        snapshot assertions, or JSON export.
    """

    return {
        # Identity
        "name": self.name,
        "trace_id": self.trace_id,
        "parent_id": self.parent_id,

        # Lifecycle
        "status": self.status.value,
        "finished": self.finished,

        # Timing
        "started_at": self.started_at,
        "ended_at": self.ended_at,
        "duration": self.duration,

        # User data
        "attributes": dict(self.attributes),

        # Runtime metadata
        "metadata": dict(self.metadata),

        # Events
        "events": [
            event.to_dict()
            for event in self.events
        ],

        # Exceptions
        "exceptions": [
            {
                "type": type(exc).__name__,
                "message": str(exc),
            }
            for exc in self.exceptions
        ],
    }


# ==========================================================
# Cloning
# ==========================================================

def copy(self) -> "FakeTrace":
    """
    Return a deep copy of this trace.

    The clone is completely independent of
    the original object.
    """

    return deepcopy(self)


# ==========================================================
# Query Helpers
# ==========================================================

@property
def event_count(self) -> int:
    """Number of recorded events."""
    return len(self.events)


@property
def attribute_count(self) -> int:
    """Number of trace attributes."""
    return len(self.attributes)


@property
def metadata_count(self) -> int:
    """Number of metadata entries."""
    return len(self.metadata)


@property
def exception_count(self) -> int:
    """Number of recorded exceptions."""
    return len(self.exceptions)


@property
def has_events(self) -> bool:
    """True if at least one event exists."""
    return bool(self.events)


@property
def has_attributes(self) -> bool:
    """True if at least one attribute exists."""
    return bool(self.attributes)


@property
def has_metadata(self) -> bool:
    """True if metadata exists."""
    return bool(self.metadata)


@property
def has_exceptions(self) -> bool:
    """True if one or more exceptions were recorded."""
    return bool(self.exceptions)


@property
def is_success(self) -> bool:
    """True if trace completed successfully."""
    return self.status is FakeStatus.SUCCESS


@property
def is_failure(self) -> bool:
    """True if trace failed."""
    return self.status is FakeStatus.FAILURE


@property
def is_cancelled(self) -> bool:
    """True if trace was cancelled."""
    return self.status is FakeStatus.CANCELLED


# ==========================================================
# Reset Helpers
# ==========================================================

def clear_attributes(self) -> "FakeTrace":
    """
    Remove all user attributes.
    """

    self.attributes.clear()
    return self


def clear_metadata(self) -> "FakeTrace":
    """
    Remove all runtime metadata.
    """

    self.metadata.clear()
    return self


def clear_exceptions(self) -> "FakeTrace":
    """
    Remove all recorded exceptions.
    """

    self.exceptions.clear()
    return self


# ==========================================================
# Representation
# ==========================================================

def __repr__(self) -> str:
    """
    Developer-friendly representation used by failing tests,
    debugging sessions, and assertion output.
    """

    return (
        f"{self.__class__.__name__}("
        f"name={self.name!r}, "
        f"status={self.status.value}, "
        f"running={self.is_running}, "
        f"finished={self.finished}, "
        f"duration={self.duration}, "
        f"events={self.event_count}, "
        f"attributes={self.attribute_count}, "
        f"exceptions={self.exception_count})"
    ) 
# ==========================================================
# FakeSpan - Core
# ==========================================================

@dataclass(slots=True)
class FakeSpan:
    """
    Fake Span used throughout the observability test suite.

    This implementation mirrors the public contract of the real
    Span while remaining deterministic and lightweight.

    Hierarchy management, attributes, events and serialization
    are implemented in later sections.
    """

    # ==========================================================
    # Identity
    # ==========================================================

    name: str

    span_id: str | None = None

    trace_id: str | None = None

    parent_span_id: str | None = None

    # ==========================================================
    # Hierarchy
    # ==========================================================

    parent: "FakeSpan | None" = None

    # ==========================================================
    # Lifecycle
    # ==========================================================

    status: FakeStatus = FakeStatus.CREATED

    finished: bool = False

    # ==========================================================
    # Timing
    # ==========================================================

    started_at: float | None = None

    ended_at: float | None = None

    # ==========================================================
    # Internal
    # ==========================================================

    _running: bool = field(
        default=False,
        init=False,
        repr=False,
    )

    # ==========================================================
    # Lifecycle
    # ==========================================================

    def start(
        self,
        timestamp: float = 0.0,
    ) -> "FakeSpan":
        """
        Start the span.

        Calling start() multiple times is safe.
        """

        if self._running:
            return self

        self.started_at = timestamp
        self.ended_at = None

        self.finished = False

        self.status = FakeStatus.RUNNING

        self._running = True

        return self

    def finish(
        self,
        status: FakeStatus = FakeStatus.SUCCESS,
        timestamp: float | None = None,
    ) -> "FakeSpan":
        """
        Finish the span.

        Safe to call multiple times.
        """

        if not self._running:
            return self

        self.ended_at = (
            self.started_at
            if timestamp is None
            else timestamp
        )

        self.finished = True

        self.status = status

        self._running = False

        return self

    def reset(self) -> "FakeSpan":
        """
        Restore the initial lifecycle state.

        Data such as attributes/events is intentionally
        preserved until the Data section adds optional
        clear helpers.
        """

        self.status = FakeStatus.CREATED

        self.finished = False

        self.started_at = None

        self.ended_at = None

        self._running = False

        return self

    # ==========================================================
    # Timing
    # ==========================================================

    @property
    def is_running(self) -> bool:
        """
        True while the span is active.
        """

        return self._running

    @property
    def is_finished(self) -> bool:
        """
        True once finish() has completed.
        """

        return self.finished

    @property
    def duration(self) -> float | None:
        """
        Span execution duration.

        Returns
        -------
        float | None
            None until both timestamps exist.
        """

        if (
            self.started_at is None
            or self.ended_at is None
        ):
            return None

        return self.ended_at - self.started_at

    # ==========================================================
    # Status Helpers
    # ==========================================================

    @property
    def is_success(self) -> bool:
        """
        True if the span completed successfully.
        """

        return self.status is FakeStatus.SUCCESS

    @property
    def is_failure(self) -> bool:
        """
        True if the span completed with failure.
        """

        return self.status is FakeStatus.FAILURE

    @property
    def is_cancelled(self) -> bool:
        """
        True if the span was cancelled.
        """

        return self.status is FakeStatus.CANCELLED   
# ==========================================================
# Hierarchy
# ==========================================================

children: list["FakeSpan"] = field(
    default_factory=list,
)
"""
Direct child spans.

Children preserve insertion order.
"""


# ==========================================================
# Child Management
# ==========================================================

def add_child(
    self,
    child: "FakeSpan",
) -> "FakeSpan":
    """
    Attach a child span.

    If the child already exists, this
    operation has no effect.
    """

    if child not in self.children:
        child.parent = self
        child.parent_span_id = self.span_id
        self.children.append(child)

    return child


def remove_child(
    self,
    child: "FakeSpan",
) -> bool:
    """
    Remove a child span.

    Returns
    -------
    bool
        True if removed.
    """

    if child not in self.children:
        return False

    self.children.remove(child)

    child.parent = None
    child.parent_span_id = None

    return True


def clear_children(self) -> "FakeSpan":
    """
    Remove every child span.
    """

    for child in self.children:
        child.parent = None
        child.parent_span_id = None

    self.children.clear()

    return self


# ==========================================================
# Hierarchy Helpers
# ==========================================================

@property
def is_root(self) -> bool:
    """
    True if this span has no parent.
    """

    return self.parent is None


@property
def child_count(self) -> int:
    """
    Number of direct children.
    """

    return len(self.children)


@property
def depth(self) -> int:
    """
    Depth within the span tree.

    Root span depth == 0.
    """

    depth = 0

    current = self.parent

    while current is not None:
        depth += 1
        current = current.parent

    return depth


# ==========================================================
# Traversal
# ==========================================================

def iter_children(self):
    """
    Iterate over direct children.
    """

    yield from self.children


def walk(self):
    """
    Depth-first traversal.

    Yields
    ------
    FakeSpan
        Self followed by descendants.
    """

    yield self

    for child in self.children:
        yield from child.walk() 
# ==========================================================
# Data
# ==========================================================

attributes: Attributes = field(
    default_factory=dict,
)
"""
User-defined span attributes.
"""

events: list[FakeEvent] = field(
    default_factory=list,
)
"""
Recorded span events.
"""

exceptions: list[BaseException] = field(
    default_factory=list,
)
"""
Recorded exceptions.
"""


# ==========================================================
# Attributes
# ==========================================================

def set_attribute(
    self,
    key: str,
    value: Any,
) -> "FakeSpan":
    """
    Set or replace a span attribute.
    """

    self.attributes[key] = value
    return self


def get_attribute(
    self,
    key: str,
    default: Any = None,
) -> Any:
    """
    Retrieve a span attribute.
    """

    return self.attributes.get(key, default)


# ==========================================================
# Events
# ==========================================================

def add_event(
    self,
    name: str,
    *,
    timestamp: float | None = None,
    attributes: Attributes | None = None,
) -> FakeEvent:
    """
    Record an event on this span.
    """

    event = FakeEvent(
        name=name,
        timestamp=timestamp,
        attributes=dict(attributes or {}),
    )

    self.events.append(event)

    return event


def clear_events(self) -> "FakeSpan":
    """
    Remove all recorded events.
    """

    self.events.clear()

    return self


# ==========================================================
# Exceptions
# ==========================================================

def record_exception(
    self,
    exception: BaseException,
    *,
    record_event: bool = True,
) -> BaseException:
    """
    Record an exception.

    Optionally creates a matching span event.
    """

    self.exceptions.append(exception)

    if record_event:
        self.add_event(
            "exception",
            attributes={
                "exception.type": type(exception).__name__,
                "exception.message": str(exception),
            },
        )

    return exception


# ==========================================================
# Query Helpers
# ==========================================================

@property
def attribute_count(self) -> int:
    """
    Number of span attributes.
    """

    return len(self.attributes)


@property
def event_count(self) -> int:
    """
    Number of recorded events.
    """

    return len(self.events)


@property
def exception_count(self) -> int:
    """
    Number of recorded exceptions.
    """

    return len(self.exceptions)


@property
def has_attributes(self) -> bool:
    return bool(self.attributes)


@property
def has_events(self) -> bool:
    return bool(self.events)


@property
def has_exceptions(self) -> bool:
    return bool(self.exceptions)


def clear_attributes(self) -> "FakeSpan":
    """
    Remove all attributes.
    """

    self.attributes.clear()

    return self


def clear_exceptions(self) -> "FakeSpan":
    """
    Remove all recorded exceptions.
    """

    self.exceptions.clear()

    return self
# ==========================================================
# Utilities
# ==========================================================

def to_dict(self) -> dict[str, Any]:
    """
    Serialize this span into a JSON-friendly dictionary.

    Returns
    -------
    dict[str, Any]
        Dictionary representation suitable for snapshot
        testing, assertions and JSON export.
    """

    return {
        # Identity
        "name": self.name,
        "span_id": self.span_id,
        "trace_id": self.trace_id,
        "parent_span_id": self.parent_span_id,

        # Hierarchy
        "depth": self.depth,
        "child_count": self.child_count,

        # Lifecycle
        "status": self.status.value,
        "finished": self.finished,

        # Timing
        "started_at": self.started_at,
        "ended_at": self.ended_at,
        "duration": self.duration,

        # User data
        "attributes": dict(self.attributes),

        # Events
        "events": [
            event.to_dict()
            for event in self.events
        ],

        # Exceptions
        "exceptions": [
            {
                "type": type(exc).__name__,
                "message": str(exc),
            }
            for exc in self.exceptions
        ],
    }


# ==========================================================
# Cloning
# ==========================================================

def copy(self) -> "FakeSpan":
    """
    Return a deep copy of this span.

    The cloned span is completely independent of the
    original, including children, events and attributes.
    """

    return deepcopy(self)


# ==========================================================
# Query Helpers
# ==========================================================

@property
def event_count(self) -> int:
    """
    Number of recorded events.
    """

    return len(self.events)


@property
def attribute_count(self) -> int:
    """
    Number of span attributes.
    """

    return len(self.attributes)


@property
def exception_count(self) -> int:
    """
    Number of recorded exceptions.
    """

    return len(self.exceptions)


# ==========================================================
# Representation
# ==========================================================

def __repr__(self) -> str:
    """
    Developer-friendly representation.

    Used heavily by pytest assertion output.
    """

    return (
        f"{self.__class__.__name__}("
        f"name={self.name!r}, "
        f"span_id={self.span_id!r}, "
        f"status={self.status.value}, "
        f"depth={self.depth}, "
        f"children={self.child_count}, "
        f"running={self.is_running}, "
        f"finished={self.finished}, "
        f"duration={self.duration}, "
        f"events={self.event_count}, "
        f"attributes={self.attribute_count}, "
        f"exceptions={self.exception_count})"
    )
# ==========================================================
# FakeTraceManager
# Part 1 — Core
# ==========================================================

class FakeTraceManager:
    """
    Production-quality fake implementation of a TraceManager.

    The fake manager records state changes deterministically and
    exposes helper APIs for assertions without depending on the
    real tracing implementation.

    Lifecycle methods (start_trace, finish_trace, start_span,
    finish_span, etc.) are implemented in later sections.
    """

    def __init__(self) -> None:
        # ======================================================
        # Internal collections
        # ======================================================

        # All traces created during this manager lifetime.
        self._traces: list[FakeTrace] = []

        # All spans created during this manager lifetime.
        self._spans: list[FakeSpan] = []

        # Generic call history used by tests.
        self._calls: list[CallRecord] = []

        # ======================================================
        # Current execution state
        # ======================================================

        # Currently active trace.
        self._current_trace: FakeTrace | None = None

        # Currently active span.
        self._current_span: FakeSpan | None = None

        # ======================================================
        # Span stack
        # ======================================================

        # Maintains nested span hierarchy.
        self._span_stack: list[FakeSpan] = []

    # ==========================================================
    # Current State
    # ==========================================================

    @property
    def current_trace(self) -> FakeTrace | None:
        """
        Currently active trace.
        """
        return self._current_trace

    @property
    def current_span(self) -> FakeSpan | None:
        """
        Currently active span.
        """
        return self._current_span

    @property
    def span_stack(self) -> list[FakeSpan]:
        """
        Read-only access to the current span stack.

        A shallow copy is returned to avoid accidental mutation
        by test code.
        """
        return list(self._span_stack)

    # ==========================================================
    # Collection Views
    # ==========================================================

    @property
    def traces(self) -> list[FakeTrace]:
        """
        All traces managed by this instance.
        """
        return list(self._traces)

    @property
    def spans(self) -> list[FakeSpan]:
        """
        All spans managed by this instance.
        """
        return list(self._spans)

    @property
    def calls(self) -> list[CallRecord]:
        """
        Recorded API calls.
        """
        return list(self._calls)

    # ==========================================================
    # Reset
    # ==========================================================

    def reset(self) -> "FakeTraceManager":
        """
        Restore the manager to its initial state.

        Removes all traces, spans, call history and execution
        context so the same instance can be reused across tests.
        """

        self._traces.clear()
        self._spans.clear()
        self._calls.clear()

        self._current_trace = None
        self._current_span = None

        self._span_stack.clear()

        return self
# ==========================================================
# Trace Lifecycle
# ==========================================================

def start_trace(
    self,
    name: str,
    *,
    metadata: Metadata | None = None,
    attributes: Attributes | None = None,
) -> FakeTrace:
    """
    Create and activate a new trace.

    The created trace becomes the current active trace.
    Any previously active trace is replaced.

    Parameters
    ----------
    name:
        Trace name.

    metadata:
        Optional provenance metadata.

    attributes:
        Optional trace attributes.
    """

    trace = FakeTrace(name=name)

    if metadata:
        trace.metadata.update(metadata)

    if attributes:
        trace.attributes.update(attributes)

    trace.start()

    self._traces.append(trace)

    self._current_trace = trace

    self._calls.append(
        CallRecord(
            method="start_trace",
            args=(name,),
            kwargs={
                "metadata": metadata,
                "attributes": attributes,
            },
        )
    )

    return trace


# ----------------------------------------------------------


def finish_trace(
    self,
    trace: FakeTrace | None = None,
    *,
    status: FakeStatus = FakeStatus.SUCCESS,
) -> FakeTrace | None:
    """
    Finish a trace.

    If *trace* is omitted, the currently active trace
    will be finished.
    """

    trace = trace or self._current_trace

    if trace is None:
        return None

    trace.finish(status=status)

    self._calls.append(
        CallRecord(
            method="finish_trace",
            args=(trace,),
            kwargs={
                "status": status,
            },
        )
    )

    if trace is self._current_trace:
        self._current_trace = None

    return trace


# ==========================================================
# Active Trace Helpers
# ==========================================================

@property
def active_trace(self) -> FakeTrace | None:
    """
    Alias for current_trace.

    Mirrors APIs commonly found in tracing frameworks.
    """

    return self._current_trace


@property
def has_active_trace(self) -> bool:
    """
    True if a trace is currently active.
    """

    return self._current_trace is not None


@property
def trace_count(self) -> int:
    """
    Total number of created traces.
    """

    return len(self._traces)


@property
def last_trace(self) -> FakeTrace | None:
    """
    Most recently created trace.
    """

    if not self._traces:
        return None

    return self._traces[-1]


# ==========================================================
# Trace Queries
# ==========================================================

def get_trace(
    self,
    name: str,
) -> FakeTrace | None:
    """
    Find the first trace having the given name.
    """

    for trace in self._traces:
        if trace.name == name:
            return trace

    return None


def iter_traces(self):
    """
    Iterate over all traces.
    """

    yield from self._traces
# ==========================================================
# Span Lifecycle
# ==========================================================

def start_span(
    self,
    name: str,
    *,
    trace: FakeTrace | None = None,
    parent: FakeSpan | None = None,
    attributes: Attributes | None = None,
) -> FakeSpan:
    """
    Create and activate a new span.

    Parent resolution order:

        explicit parent
            ↓
        current active span
            ↓
        root span
    """

    trace = trace or self._current_trace

    if trace is None:
        raise RuntimeError(
            "Cannot start a span without an active trace."
        )

    # ------------------------------------------------------
    # Resolve parent
    # ------------------------------------------------------

    if parent is None:
        parent = self._current_span

    span = FakeSpan(
        name=name,
        trace_id=trace.trace_id,
        parent=parent,
        parent_span_id=(
            parent.span_id
            if parent is not None
            else None
        ),
    )

    if attributes:
        span.attributes.update(attributes)

    span.start()

    # ------------------------------------------------------
    # Attach hierarchy
    # ------------------------------------------------------

    if parent is not None:
        parent.add_child(span)

    # ------------------------------------------------------
    # Register
    # ------------------------------------------------------

    self._spans.append(span)

    self._current_span = span

    self._span_stack.append(span)

    self._calls.append(
        CallRecord(
            method="start_span",
            args=(name,),
            kwargs={
                "trace": trace,
                "parent": parent,
                "attributes": attributes,
            },
        )
    )

    return span


# ----------------------------------------------------------


def finish_span(
    self,
    span: FakeSpan | None = None,
    *,
    status: FakeStatus = FakeStatus.SUCCESS,
) -> FakeSpan | None:
    """
    Finish a span.

    If span is omitted, the current active span
    will be finished.
    """

    span = span or self._current_span

    if span is None:
        return None

    span.finish(status=status)

    self._calls.append(
        CallRecord(
            method="finish_span",
            args=(span,),
            kwargs={
                "status": status,
            },
        )
    )

    # ------------------------------------------------------
    # Stack update
    # ------------------------------------------------------

    if self._span_stack:

        if self._span_stack[-1] is span:

            self._span_stack.pop()

        else:
            try:
                self._span_stack.remove(span)
            except ValueError:
                pass

    self._current_span = (
        self._span_stack[-1]
        if self._span_stack
        else None
    )

    return span


# ==========================================================
# Active Span Helpers
# ==========================================================

@property
def active_span(self) -> FakeSpan | None:
    """
    Alias for current_span.
    """

    return self._current_span


@property
def has_active_span(self) -> bool:
    """
    True if a span is currently active.
    """

    return self._current_span is not None


@property
def span_count(self) -> int:
    """
    Total number of spans.
    """

    return len(self._spans)


@property
def last_span(self) -> FakeSpan | None:
    """
    Most recently created span.
    """

    if not self._spans:
        return None

    return self._spans[-1]


# ==========================================================
# Span Queries
# ==========================================================

def get_span(
    self,
    span_id: str,
) -> FakeSpan | None:
    """
    Lookup a span by span_id.
    """

    for span in self._spans:
        if span.span_id == span_id:
            return span

    return None


def iter_spans(self):
    """
    Iterate over all spans.
    """

    yield from self._spans
# ==========================================================
# Stack Management
# ==========================================================

def push_span(self, span: FakeSpan) -> FakeSpan:
    """
    Push a span onto the active span stack.

    This method makes the supplied span the current active span.
    It does not create or start the span.
    """

    if span not in self._spans:
        self._spans.append(span)

    self._span_stack.append(span)
    self._current_span = span

    self._calls.append(
        CallRecord(
            method="push_span",
            args=(span,),
            kwargs={},
        )
    )

    return span


# ----------------------------------------------------------


def pop_span(self) -> FakeSpan | None:
    """
    Pop the current active span from the stack.

    Returns
    -------
    FakeSpan | None
        Removed span or None if stack is empty.
    """

    if not self._span_stack:
        return None

    span = self._span_stack.pop()

    self._current_span = (
        self._span_stack[-1]
        if self._span_stack
        else None
    )

    self._calls.append(
        CallRecord(
            method="pop_span",
            args=(span,),
            kwargs={},
        )
    )

    return span


# ----------------------------------------------------------


def peek_span(self) -> FakeSpan | None:
    """
    Return the current top span without removing it.
    """

    if not self._span_stack:
        return None

    return self._span_stack[-1]


# ----------------------------------------------------------


@property
def stack_depth(self) -> int:
    """
    Current nesting depth of the span stack.
    """

    return len(self._span_stack)


# ----------------------------------------------------------


def clear_stack(self) -> None:
    """
    Remove every span from the active stack.

    This does not delete spans from the manager registry.
    Only execution context is cleared.
    """

    self._span_stack.clear()
    self._current_span = None

    self._calls.append(
        CallRecord(
            method="clear_stack",
            args=(),
            kwargs={},
        )
    )


# ==========================================================
# Convenience Helpers
# ==========================================================

@property
def is_stack_empty(self) -> bool:
    """
    True if no active spans exist.
    """

    return not self._span_stack


@property
def stack(self) -> tuple[FakeSpan, ...]:
    """
    Immutable snapshot of the current stack.
    """

    return tuple(self._span_stack)


def iter_stack(self):
    """
    Iterate from root span to current span.
    """

    yield from self._span_stack 
# ==========================================================
# Query API
# ==========================================================

@property
def trace_count(self) -> int:
    """
    Total number of registered traces.
    """
    return len(self._traces)


@property
def span_count(self) -> int:
    """
    Total number of registered spans.
    """
    return len(self._spans)


@property
def last_trace(self) -> FakeTrace | None:
    """
    Return the most recently created trace.
    """
    if not self._traces:
        return None

    return self._traces[-1]


@property
def last_span(self) -> FakeSpan | None:
    """
    Return the most recently created span.
    """
    if not self._spans:
        return None

    return self._spans[-1]


# ==========================================================
# Trace Queries
# ==========================================================

def get_trace(
    self,
    *,
    trace_id: str | None = None,
    name: str | None = None,
) -> FakeTrace | None:
    """
    Find a trace by identifier or name.

    Parameters
    ----------
    trace_id:
        Trace identifier.

    name:
        Trace name.

    Notes
    -----
    If both arguments are supplied, trace_id has priority.
    """

    if trace_id is not None:
        for trace in self._traces:
            if trace.trace_id == trace_id:
                return trace

        return None

    if name is not None:
        for trace in self._traces:
            if trace.name == name:
                return trace

    return None


def has_trace(
    self,
    trace_id: str,
) -> bool:
    """
    True if the specified trace exists.
    """

    return self.get_trace(trace_id=trace_id) is not None


def iter_traces(self):
    """
    Iterate over traces in creation order.
    """

    yield from self._traces


# ==========================================================
# Span Queries
# ==========================================================

def get_span(
    self,
    *,
    span_id: str | None = None,
    name: str | None = None,
) -> FakeSpan | None:
    """
    Find a span by identifier or name.
    """

    if span_id is not None:
        for span in self._spans:
            if span.span_id == span_id:
                return span

        return None

    if name is not None:
        for span in self._spans:
            if span.name == name:
                return span

    return None


def has_span(
    self,
    span_id: str,
) -> bool:
    """
    True if the specified span exists.
    """

    return self.get_span(span_id=span_id) is not None


def iter_spans(self):
    """
    Iterate over spans in creation order.
    """

    yield from self._spans


# ==========================================================
# Collection Helpers
# ==========================================================

def find_traces(
    self,
    predicate,
):
    """
    Return every trace satisfying the predicate.
    """

    return [
        trace
        for trace in self._traces
        if predicate(trace)
    ]


def find_spans(
    self,
    predicate,
):
    """
    Return every span satisfying the predicate.
    """

    return [
        span
        for span in self._spans
        if predicate(span)
    ]


def traces_by_status(
    self,
    status: FakeStatus,
):
    """
    Return traces having the specified status.
    """

    return [
        trace
        for trace in self._traces
        if trace.status == status
    ]


def spans_by_status(
    self,
    status: FakeStatus,
):
    """
    Return spans having the specified status.
    """

    return [
        span
        for span in self._spans
        if span.status == status
    ]   


from contextlib import contextmanager
from typing import Iterator


# ==========================================================
# Context Managers
# ==========================================================

@contextmanager
def trace_scope(
    self,
    name: str,
    *,
    metadata: Metadata | None = None,
    attributes: Attributes | None = None,
) -> Iterator[FakeTrace]:
    """
    Context manager for an entire trace.

    Example
    -------
    >>> with manager.trace_scope("Runtime") as trace:
    ...     ...

    The trace is always finished, even if an exception occurs.
    """

    trace = self.start_trace(
        name,
        metadata=metadata,
        attributes=attributes,
    )

    try:
        yield trace

    except Exception as exc:

        trace.record_exception(exc)

        self.finish_trace(
            trace,
            status=FakeStatus.ERROR,
        )

        raise

    else:

        self.finish_trace(
            trace,
            status=FakeStatus.SUCCESS,
        )


# ----------------------------------------------------------


@contextmanager
def span_scope(
    self,
    name: str,
    *,
    trace: FakeTrace | None = None,
    parent: FakeSpan | None = None,
    attributes: Attributes | None = None,
) -> Iterator[FakeSpan]:
    """
    Context manager for a span.

    Parent resolution follows the same rules as
    start_span().
    """

    span = self.start_span(
        name,
        trace=trace,
        parent=parent,
        attributes=attributes,
    )

    try:
        yield span

    except Exception as exc:

        span.record_exception(exc)

        self.finish_span(
            span,
            status=FakeStatus.ERROR,
        )

        raise

    else:

        self.finish_span(
            span,
            status=FakeStatus.SUCCESS,
        )


# ==========================================================
# Convenience Helpers
# ==========================================================

def run_in_trace(
    self,
    name: str,
    func,
    *args,
    **kwargs,
):
    """
    Execute a callable inside a trace.
    """

    with self.trace_scope(name):
        return func(*args, **kwargs)


def run_in_span(
    self,
    name: str,
    func,
    *args,
    **kwargs,
):
    """
    Execute a callable inside a span.
    """

    with self.span_scope(name):
        return func(*args, **kwargs)
# ==========================================================
# Utilities
# ==========================================================

from copy import deepcopy


def to_dict(self) -> dict[str, object]:
    """
    Serialize the manager into a dictionary suitable for
    debugging, snapshot testing, and assertions.

    Returns
    -------
    dict
        Serializable representation of the manager.
    """

    return {
        "trace_count": self.trace_count,
        "span_count": self.span_count,
        "current_trace": (
            self._current_trace.trace_id
            if self._current_trace
            else None
        ),
        "current_span": (
            self._current_span.span_id
            if self._current_span
            else None
        ),
        "stack_depth": self.stack_depth,
        "traces": [
            trace.to_dict()
            for trace in self._traces
        ],
        "spans": [
            span.to_dict()
            for span in self._spans
        ],
        "calls": [
            {
                "method": call.method,
                "args": call.args,
                "kwargs": call.kwargs,
            }
            for call in self._calls
        ],
    }


# ----------------------------------------------------------


def snapshot(self) -> dict[str, object]:
    """
    Alias for to_dict().

    Intended for snapshot-based unit tests.
    """

    return self.to_dict()


# ----------------------------------------------------------


def copy(self) -> "FakeTraceManager":
    """
    Return a deep copy of the manager.

    Useful when comparing state before/after an operation.
    """

    return deepcopy(self)


# ----------------------------------------------------------


def state_summary(self) -> dict[str, object]:
    """
    Lightweight summary of runtime state.

    Suitable for assertions and debugging.
    """

    return {
        "trace_count": self.trace_count,
        "span_count": self.span_count,
        "active_trace": self.has_active_trace,
        "active_span": self.has_active_span,
        "stack_depth": self.stack_depth,
    }


# ----------------------------------------------------------


def __repr__(self) -> str:
    """
    Human-readable representation for debugging.
    """

    return (
        f"{self.__class__.__name__}("
        f"traces={self.trace_count}, "
        f"spans={self.span_count}, "
        f"active_trace={self.has_active_trace}, "
        f"active_span={self.has_active_span}, "
        f"stack_depth={self.stack_depth}"
        f")"
    )
# ============================================================================
# FakeProcessor
# ============================================================================


from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ProcessorCall:
    """
    Recorded processor callback.
    """

    method: str
    target: Any
    success: bool | None = None
    error: Exception | None = None
    kwargs: dict[str, Any] = field(default_factory=dict)


class FakeProcessor:
    """
    Records every processor callback for assertions.

    The fake intentionally performs no processing.
    It only records callback history.
    """

    def __init__(self) -> None:
        self.calls: list[ProcessorCall] = []

    # ------------------------------------------------------------------
    # Runtime lifecycle
    # ------------------------------------------------------------------

    def before_runtime(self, trace) -> None:
        self.calls.append(
            ProcessorCall("before_runtime", trace)
        )

    def after_runtime(
        self,
        trace,
        success: bool,
        error: Exception | None = None,
    ) -> None:
        self.calls.append(
            ProcessorCall(
                "after_runtime",
                trace,
                success,
                error,
            )
        )

    # ------------------------------------------------------------------
    # Stage lifecycle
    # ------------------------------------------------------------------

    def before_stage(self, span) -> None:
        self.calls.append(
            ProcessorCall("before_stage", span)
        )

    def after_stage(
        self,
        span,
        success: bool,
        error: Exception | None = None,
    ) -> None:
        self.calls.append(
            ProcessorCall(
                "after_stage",
                span,
                success,
                error,
            )
        )

    # ------------------------------------------------------------------
    # Task lifecycle
    # ------------------------------------------------------------------

    def before_task(self, span) -> None:
        self.calls.append(
            ProcessorCall("before_task", span)
        )

    def after_task(
        self,
        span,
        success: bool,
        error: Exception | None = None,
    ) -> None:
        self.calls.append(
            ProcessorCall(
                "after_task",
                span,
                success,
                error,
            )
        )

    # ------------------------------------------------------------------
    # Generic callbacks
    # ------------------------------------------------------------------

    def on_start(self, obj) -> None:
        self.calls.append(
            ProcessorCall("on_start", obj)
        )

    def on_end(self, obj) -> None:
        self.calls.append(
            ProcessorCall("on_end", obj)
        )

    def on_event(self, obj, event) -> None:
        self.calls.append(
            ProcessorCall(
                "on_event",
                obj,
                kwargs={"event": event},
            )
        )

    def on_exception(self, obj, exc: Exception) -> None:
        self.calls.append(
            ProcessorCall(
                "on_exception",
                obj,
                error=exc,
            )
        )

    def on_export(self, obj) -> None:
        self.calls.append(
            ProcessorCall("on_export", obj)
        )

    def flush(self) -> None:
        self.calls.append(
            ProcessorCall("flush", None)
        )

    def shutdown(self) -> None:
        self.calls.append(
            ProcessorCall("shutdown", None)
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @property
    def call_count(self) -> int:
        return len(self.calls)

    @property
    def last_call(self) -> ProcessorCall | None:
        return self.calls[-1] if self.calls else None

    def was_called(self, method: str) -> bool:
        return any(c.method == method for c in self.calls)

    def calls_for(self, method: str) -> list[ProcessorCall]:
        return [
            c
            for c in self.calls
            if c.method == method
        ]

    def call_order(self) -> list[str]:
        return [c.method for c in self.calls]

    def clear(self) -> None:
        self.calls.clear()

    reset = clear


# ============================================================================
# FakeExporter
# ============================================================================


class FakeExporter:
    """
    Fake exporter recording export ordering.
    """

    def __init__(self) -> None:

        self.exports: list[tuple[str, Any]] = []

        self.exported_traces = []
        self.exported_spans = []
        self.exported_metrics = []
        self.exported_logs = []

        self.flushed = False
        self.closed = False
        self.shutdown_called = False

        self.flush_count = 0
        self.shutdown_count = 0

    # ------------------------------------------------------------------

    def export_trace(self, trace) -> None:

        self.exported_traces.append(trace)
        self.exports.append(("trace", trace))

    def export_span(self, span) -> None:

        self.exported_spans.append(span)
        self.exports.append(("span", span))

    def export_metric(self, metric) -> None:

        self.exported_metrics.append(metric)
        self.exports.append(("metric", metric))

    def export_log(self, record) -> None:

        self.exported_logs.append(record)
        self.exports.append(("log", record))

    # ------------------------------------------------------------------

    def flush(self) -> None:

        self.flushed = True
        self.flush_count += 1

    def shutdown(self) -> None:

        self.shutdown_called = True
        self.closed = True
        self.shutdown_count += 1

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @property
    def export_count(self) -> int:
        return len(self.exports)

    @property
    def last_export(self):

        if not self.exports:
            return None

        return self.exports[-1]

    @property
    def has_exports(self) -> bool:
        return bool(self.exports)

    def clear(self) -> None:

        self.exports.clear()

        self.exported_traces.clear()
        self.exported_spans.clear()
        self.exported_metrics.clear()
        self.exported_logs.clear()

        self.flushed = False
        self.closed = False
        self.shutdown_called = False

        self.flush_count = 0
        self.shutdown_count = 0

    reset = clear


# ============================================================================
# FakeClock
# ============================================================================


class FakeClock:
    """
    Deterministic clock for repeatable unit tests.
    """

    def __init__(self) -> None:

        self._time = 0.0

        self._frozen = False

        self.history: list[float] = []

        self.tick_count = 0

    # ------------------------------------------------------------------

    def now(self) -> float:
        return self._time

    # ------------------------------------------------------------------

    def advance(
        self,
        seconds: float = 1.0,
    ) -> float:

        if not self._frozen:

            self._time += seconds

        self.tick_count += 1
        self.history.append(self._time)

        return self._time

    def advance_ms(
        self,
        milliseconds: float,
    ) -> float:

        return self.advance(milliseconds / 1000.0)

    def advance_ns(
        self,
        nanoseconds: int,
    ) -> float:

        return self.advance(nanoseconds / 1_000_000_000)

    # ------------------------------------------------------------------

    def freeze(self) -> None:
        self._frozen = True

    def resume(self) -> None:
        self._frozen = False

    # ------------------------------------------------------------------

    @property
    def last_tick(self) -> float | None:

        if not self.history:
            return None

        return self.history[-1]

    # ------------------------------------------------------------------

    def reset(self) -> None:

        self._time = 0.0
        self._frozen = False

        self.history.clear()
        self.tick_count = 0

    # ------------------------------------------------------------------

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"time={self._time:.6f}, "
            f"ticks={self.tick_count}, "
            f"frozen={self._frozen})"
        )                                                                       
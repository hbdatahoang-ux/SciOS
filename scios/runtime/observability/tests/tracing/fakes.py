"""
SciOS Tracing Test Fakes
========================

Deterministic fake implementations used by the tracing test-suite.

This module intentionally contains no production tracing logic.

Python 3.11+
"""

from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
from time import monotonic
from typing import Any, Callable, Iterator


# ============================================================================
# Type aliases
# ============================================================================

Attributes = dict[str, Any]
Metadata = dict[str, Any]


# ============================================================================
# FakeStatus
# ============================================================================


class FakeStatus(str, Enum):
    """
    Minimal status model shared by fake traces and spans.
    """

    UNSET = "unset"
    SUCCESS = "success"
    ERROR = "error"

    # Compatibility aliases commonly used by tracing tests.
    OK = "success"


# ============================================================================
# CallRecord
# ============================================================================


@dataclass(slots=True)
class CallRecord:
    """
    Record of a FakeTraceManager method invocation.

    Both ``args``/``kwargs`` and the legacy ``arguments`` view are supported.
    """

    method: str
    args: tuple[Any, ...] = ()
    kwargs: dict[str, Any] = field(default_factory=dict)

    @property
    def arguments(self) -> dict[str, Any]:
        """
        Compatibility view used by older tests.
        """
        return self.kwargs


# ============================================================================
# FakeTrace
# ============================================================================


class FakeTrace:
    """
    Deterministic fake trace.

    The object intentionally exposes a small, stable API suitable for
    assertions in tracing tests.
    """

    _counter = 0

    def __init__(
        self,
        name: str = "trace",
        *,
        trace_id: str | None = None,
        metadata: Metadata | None = None,
        attributes: Attributes | None = None,
        **extra_attributes: Any,
    ) -> None:
        type(self)._counter += 1

        self.trace_id = (
            trace_id
            or f"fake-trace-{type(self)._counter}"
        )

        self.id = self.trace_id
        self.name = name

        self.metadata: Metadata = dict(
            metadata or {}
        )

        self.attributes: Attributes = dict(
            attributes or {}
        )
        self.attributes.update(
            extra_attributes
        )

        self.spans: list[FakeSpan] = []
        self.events: list[FakeEvent] = []

        self.status = FakeStatus.UNSET

        self.started = False
        self.finished = False

        self.start_time: float | None = None
        self.end_time: float | None = None

        self.exception: Exception | None = None
        self.exceptions: list[Exception] = []

    @property
    def success(self) -> bool | None:
        """
        Runtime completion outcome.

        Returns
        -------
        True
            Trace finished successfully.

        False
            Trace finished with an error.

        None
            Trace has not been finished yet.
        """
        if self.status == FakeStatus.SUCCESS:
            return True

        if self.status == FakeStatus.ERROR:
            return False

        return None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> "FakeTrace":
        self.started = True

        if self.start_time is None:
            self.start_time = monotonic()

        return self

    def finish(
        self,
        *,
        status: FakeStatus = FakeStatus.SUCCESS,
    ) -> "FakeTrace":
        self.finished = True
        self.status = status

        if self.end_time is None:
            self.end_time = monotonic()

        return self

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def set_status(
        self,
        status: FakeStatus | str,
    ) -> "FakeSpan":
        if isinstance(status, str):
            normalized = status.strip().lower()

            if normalized in {"success", "ok"}:
                status = FakeStatus.SUCCESS
            elif normalized in {"error", "failed", "failure"}:
                status = FakeStatus.ERROR
            elif normalized == "unset":
                status = FakeStatus.UNSET
            else:
                raise ValueError(
                    f"Unsupported span status: {status!r}"
                )

        self.status = status
        return self

    def set_ok(self) -> "FakeSpan":
        return self.set_status(FakeStatus.SUCCESS)

    def set_error(self) -> "FakeSpan":
        return self.set_status(FakeStatus.ERROR)

    # ------------------------------------------------------------------
    # Attributes / metadata
    # ------------------------------------------------------------------

    def set_attribute(
        self,
        key: str,
        value: Any,
    ) -> "FakeTrace":
        self.attributes[key] = value
        return self

    def set_attributes(
        self,
        values: Attributes,
    ) -> "FakeTrace":
        self.attributes.update(values)
        return self

    def set_metadata(
        self,
        key: str,
        value: Any,
    ) -> "FakeTrace":
        self.metadata[key] = value
        return self

    # ------------------------------------------------------------------
    # Exceptions
    # ------------------------------------------------------------------

    def attach_exception(
        self,
        exc: BaseException,
    ) -> FakeEvent:
        return self.record_exception(exc)

    def attach_exception(
        self,
        exc: Exception,
    ) -> "FakeTrace":
        return self.record_exception(exc)

    # ------------------------------------------------------------------
    # Span hierarchy
    # ------------------------------------------------------------------

    def add_span(
        self,
        span: "FakeSpan",
    ) -> "FakeSpan":
        if span not in self.spans:
            self.spans.append(span)

        return span

    @property
    def span_count(self) -> int:
        return len(self.spans)

    # ------------------------------------------------------------------
    # State
    # ------------------------------------------------------------------

    @property
    def is_finished(self) -> bool:
        return self.finished

    @property
    def is_active(self) -> bool:
        return self.started and not self.finished

    @property
    def duration(self) -> float | None:
        if (
            self.start_time is None
            or self.end_time is None
        ):
            return None

        return (
            self.end_time
            - self.start_time
        )

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "name": self.name,
            "metadata": dict(self.metadata),
            "attributes": dict(self.attributes),
            "spans": [
                span.to_dict()
                for span in self.spans
            ],
            "status": (
                self.status.value
                if isinstance(
                    self.status,
                    FakeStatus,
                )
                else str(self.status)
            ),
            "started": self.started,
            "finished": self.finished,
            "exception": (
                repr(self.exception)
                if self.exception is not None
                else None
            ),
        }

    def snapshot(self) -> dict[str, Any]:
        return self.to_dict()

    def copy(self) -> "FakeTrace":
        return deepcopy(self)

    def __repr__(self) -> str:
        status = (
            self.status.value
            if isinstance(
                self.status,
                FakeStatus,
            )
            else str(self.status)
        )

        return (
            f"FakeTrace("
            f"name={self.name!r}, "
            f"trace_id={self.trace_id!r}, "
            f"status={status!r}, "
            f"finished={self.finished}"
            f")"
        )

# ============================================================================
# FakeSpan
# ============================================================================

@dataclass
class FakeEvent:
    name: str
    phase: str = "runtime"
    attributes: Attributes = field(default_factory=dict)

    def __init__(
        self,
        name: str,
        phase: str = "runtime",
        attributes: Attributes | None = None,
        **extra_attributes: Any,
    ) -> None:
        self.name = name
        self.phase = phase
        self.attributes = dict(attributes or {})
        self.attributes.update(extra_attributes)

    def set_attribute(
        self,
        key: str,
        value: Any,
    ) -> "FakeEvent":
        self.attributes[key] = value
        return self

    def set_attributes(
        self,
        values: Attributes,
    ) -> "FakeEvent":
        self.attributes.update(values)
        return self

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "phase": self.phase,
            "attributes": dict(self.attributes),
        }

    def snapshot(self) -> dict[str, Any]:
        return self.to_dict()

    def copy(self) -> "FakeEvent":
        return deepcopy(self)

class FakeSpan:
    """
    Deterministic fake span with parent/child hierarchy.
    """

    _counter = 0

    def __init__(
        self,
        name: str,
        phase: str | None = None,
        *,
        trace_id: str | None = None,
        span_id: str | None = None,
        parent: "FakeSpan | None" = None,
        parent_span_id: str | None = None,
        attributes: Attributes | None = None,
        timestamp: float | None = None,
        **extra_attributes: Any,
    ) -> None:
        type(self)._counter += 1

        # Identity
        self.span_id = (
            span_id
            or f"fake-span-{type(self)._counter}"
        )
        self.id = self.span_id

        self.trace_id = trace_id or (
            parent.trace_id
            if parent is not None
            else ""
        )

        # Basic metadata
        self.name = name
        self.phase = phase

        self.attributes: Attributes = dict(
            attributes or {}
        )
        self.attributes.update(extra_attributes)

        self.timestamp = (
            timestamp
            if timestamp is not None
            else monotonic()
        )

        # Hierarchy
        self.parent = parent

        self.parent_span_id = (
            parent_span_id
            if parent_span_id is not None
            else (
                parent.span_id
                if parent is not None
                else None
            )
        )

        self.children: list[FakeSpan] = []

        # Events
        self.events: list[FakeEvent] = []

        # Status
        self.status = FakeStatus.UNSET

        # Lifecycle
        self.started = False
        self.finished = False
        self.start_time: float | None = None
        self.end_time: float | None = None

        # Exceptions
        self.exception: Exception | None = None
        self.exceptions: list[Exception] = []

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> "FakeSpan":
        self.started = True

        if self.start_time is None:
            self.start_time = monotonic()

        return self

    def finish(
        self,
        *,
        status: FakeStatus = FakeStatus.SUCCESS,
    ) -> "FakeSpan":
        self.finished = True
        self.status = (
            status
            if isinstance(status, FakeStatus)
            else FakeStatus(status)
        )

        if self.end_time is None:
            self.end_time = monotonic()

        return self

    # Compatibility alias.
    end = finish

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def set_status(self, status: FakeStatus) -> "FakeSpan":
        self.status = (
            status.name
            if isinstance(status, FakeStatus)
            else str(status)
        )

    def set_ok(self) -> "FakeSpan":
        return self.set_status(FakeStatus.SUCCESS)

    def set_error(self) -> "FakeSpan":
        return self.set_status(FakeStatus.ERROR)

    # ------------------------------------------------------------------
    # Hierarchy
    # ------------------------------------------------------------------

    def add_child(self, span: "FakeSpan") -> "FakeSpan":
        if span not in self.children:
            self.children.append(span)

        span.parent = self
        span.parent_span_id = self.span_id

        return span

    @property
    def child_count(self) -> int:
        return len(self.children)

    # ------------------------------------------------------------------
    # Attributes
    # ------------------------------------------------------------------

    def set_attribute(self, key: str, value: Any) -> "FakeSpan":
        self.attributes[key] = value
        return self

    def set_attributes(self, values: Attributes) -> "FakeSpan":
        self.attributes.update(values)
        return self

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def add_event(
        self,
        name: str,
        *,
        attributes: Attributes | None = None,
        phase: str = "runtime",
    ) -> "FakeSpan":
        event = FakeEvent(
            name=name,
            phase=phase,
            attributes=attributes,
        )

        self.events.append(event)

        return self

    # ------------------------------------------------------------------
    # Exceptions
    # ------------------------------------------------------------------

    def record_exception(
        self,
        exc: BaseException,
    ) -> FakeEvent:
        """
        Record an exception directly on this span.

        The span itself owns exception state. Scope resolution belongs to
        FakeTraceManager, not FakeSpan.
        """

        if not isinstance(
            exc,
            BaseException,
        ):
            raise TypeError(
                "exc must be a BaseException."
            )

        self.exception = exc
        self.exceptions.append(
            exc,
        )

        event = FakeEvent(
            name="exception",
            phase="exception",
            attributes={
                "exception.type": type(exc).__name__,
                "exception.message": str(exc),
            },
        )

        self.events.append(
            event,
        )

        self.status = FakeStatus.ERROR

        return event



    def attach_exception(self, exc: Exception) -> "FakeSpan":
        return self.record_exception(exc)

    # ------------------------------------------------------------------
    # State
    # ------------------------------------------------------------------

    @property
    def is_finished(self) -> bool:
        return self.finished

    @property
    def is_active(self) -> bool:
        return self.started and not self.finished

    @property
    def duration(self) -> float | None:
        if self.start_time is None or self.end_time is None:
            return None

        return self.end_time - self.start_time

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        return {
            "span_id": self.span_id,
            "trace_id": self.trace_id,
            "name": self.name,
            "parent_span_id": self.parent_span_id,
            "attributes": dict(self.attributes),
            "events": [
                event.to_dict()
                for event in self.events
            ],
            "status": self.status.value,
            "started": self.started,
            "finished": self.finished,
            "exception": (
                repr(self.exception)
                if self.exception is not None
                else None
            ),
            "child_count": len(self.children),
        }

    def snapshot(self) -> dict[str, Any]:
        return self.to_dict()

    def copy(self) -> "FakeSpan":
        return deepcopy(self)

    def __repr__(self) -> str:
        return (
            f"FakeSpan("
            f"name={self.name!r}, "
            f"span_id={self.span_id!r}, "
            f"trace_id={self.trace_id!r}, "
            f"status={self.status.value!r}, "
            f"finished={self.finished}"
            f")"
        )


# ============================================================================
# FakeTraceManager
# ============================================================================


class FakeTraceManager:
    """
    Production-quality fake implementation of a TraceManager.

    The fake maintains:

    - trace registry
    - span registry
    - active trace
    - active span
    - span stack
    - call history
    - parent/child relationships
    """

    def __init__(self) -> None:
        self._traces: list[FakeTrace] = []
        self._spans: list[FakeSpan] = []
        self._calls: list[CallRecord] = []

        self._current_trace: FakeTrace | None = None
        self._current_span: FakeSpan | None = None

        self._span_stack: list[FakeSpan] = []

        self._processor: FakeProcessor | None = None

        # --------------------------------------------------------------
        # Lifecycle observability
        # --------------------------------------------------------------

        self.start_trace_called = 0
        self.finish_trace_called = 0
        self.last_started_trace: FakeTrace | None = None
        self.last_finished_trace: FakeTrace | None = None

        self._completed_traces: dict[str, FakeTrace] = {}

    # ------------------------------------------------------------------
    # Observability properties
    # ------------------------------------------------------------------

    @property
    def active_trace_count(self) -> int:
        """Return the number of currently active traces."""
        return 1 if self._current_trace is not None else 0

    @property
    def completed_trace_count(self) -> int:
        """Return the number of completed traces."""
        return len(self._completed_traces)

    def set_processor(
        self,
        processor: "FakeProcessor | None",
    ) -> "FakeTraceManager":
        """
        Set the processor used for manager-level event callbacks.
        """

        self._processor = processor

        return self

    # ==================================================================
    # Current state
    # ==================================================================

    @property
    def current_trace(self) -> FakeTrace | None:
        return self._current_trace

    @property
    def active_trace(self) -> FakeTrace | None:
        return self._current_trace

    @property
    def active_trace_count(self) -> int:
        """Return the number of currently active traces."""
        return 1 if self._current_trace is not None else 0

    @property
    def has_active_trace(self) -> bool:
        return self._current_trace is not None

    @property
    def current_span(self) -> FakeSpan | None:
        return self._current_span

    @property
    def active_span(self) -> FakeSpan | None:
        return self._current_span

    @property
    def has_active_span(self) -> bool:
        return self._current_span is not None

    # ==================================================================
    # Collections
    # ==================================================================

    @property
    def traces(self) -> list[FakeTrace]:
        return list(self._traces)

    @property
    def spans(self) -> list[FakeSpan]:
        return list(self._spans)

    @property
    def calls(self) -> list[CallRecord]:
        return list(self._calls)

    @property
    def span_stack(self) -> list[FakeSpan]:
        return list(self._span_stack)

    @property
    def stack(self) -> tuple[FakeSpan, ...]:
        return tuple(self._span_stack)

    @property
    def completed_traces(self) -> dict[str, FakeTrace]:
        """
        Completed traces indexed by trace_id.
        """
        return dict(self._completed_traces)

    @property
    def completed_trace_count(self) -> int:
        """
        Number of completed traces.
        """
        return len(self._completed_traces)

    # ==================================================================
    # Counts
    # ==================================================================

    @property
    def trace_count(self) -> int:
        return len(self._traces)

    @property
    def span_count(self) -> int:
        return len(self._spans)

    @property
    def stack_depth(self) -> int:
        return len(self._span_stack)

    @property
    def span_depth(self) -> int:
        return len(self._span_stack)

    @property
    def is_stack_empty(self) -> bool:
        return not self._span_stack

    # ==================================================================
    # Last objects
    # ==================================================================

    @property
    def last_trace(self) -> FakeTrace | None:
        return self._traces[-1] if self._traces else None

    @property
    def last_span(self) -> FakeSpan | None:
        return self._spans[-1] if self._spans else None

    def root_span(self) -> FakeSpan | None:
        if not self._spans:
            return None
        return self._spans[0]

    # ==================================================================
    # Call recording
    # ==================================================================

    def _record_call(
        self,
        method: str,
        *args: Any,
        **kwargs: Any,
    ) -> CallRecord:
        record = CallRecord(
            method=method,
            args=args,
            kwargs=dict(kwargs),
        )

        self._calls.append(record)
        return record

    # ==================================================================
    # Reset
    # ==================================================================

    def reset(self) -> "FakeTraceManager":
        """
        Reset the fake trace manager to a clean runtime state.

        Clears active tracing state, recorded objects, callback history,
        completed-trace registry, and lifecycle observability fields.
        """

        # --------------------------------------------------------------
        # Recorded objects / call history
        # --------------------------------------------------------------

        self._traces.clear()
        self._spans.clear()
        self._calls.clear()

        # --------------------------------------------------------------
        # Active runtime state
        # --------------------------------------------------------------

        self._current_trace = None
        self._current_span = None
        self._span_stack.clear()

        # --------------------------------------------------------------
        # Completed trace registry
        # --------------------------------------------------------------

        self._completed_traces.clear()

        # --------------------------------------------------------------
        # Lifecycle observability
        # --------------------------------------------------------------

        self.start_trace_called = 0
        self.finish_trace_called = 0

        self.last_started_trace = None
        self.last_finished_trace = None

        return self


    # ==================================================================
    # Trace lifecycle
    # ==================================================================

    def start_trace(
        self,
        name: str | None = None,
        *,
        metadata: Metadata | None = None,
        attributes: Attributes | None = None,
        **extra_attributes: Any,
    ) -> FakeTrace:

        self.start_trace_called += 1

        trace_attributes = dict(attributes or {})
        trace_attributes.update(extra_attributes)

        trace = FakeTrace(
            name=name or "trace",
            metadata=metadata,
            attributes=trace_attributes,
        )

        trace.start()

        self._traces.append(trace)
        self._current_trace = trace

        self.last_started_trace = trace

        self._current_span = None
        self._span_stack.clear()

        self._record_call(
            "start_trace",
            name,
            metadata=metadata,
            attributes=trace_attributes,
        )

        return trace

    def set_status(
        self,
        status: FakeStatus | str,
    ) -> "FakeTraceManager":
        """
        Set the status of the currently active trace.

        Parameters
        ----------
        status:
            A FakeStatus value or a supported string representation.

        Returns
        -------
        FakeTraceManager
            Self, for fluent usage.

        Raises
        ------
        ValueError
            If the string status is not supported.
        """

        trace = self._current_trace

        # No active trace: lifecycle operation is a safe no-op.
        if trace is None:
            return self

        # --------------------------------------------------------------
        # Normalize string status
        # --------------------------------------------------------------

        if isinstance(status, str):
            normalized = status.strip().lower()

            if normalized == "success":
                status = FakeStatus.SUCCESS

            elif normalized in {
                "error",
                "failed",
                "failure",
            }:
                status = FakeStatus.ERROR

            else:
                raise ValueError(
                    f"Unsupported trace status: {status!r}"
                )

        # --------------------------------------------------------------
        # Apply status
        # --------------------------------------------------------------

        trace.status = status

        # --------------------------------------------------------------
        # Record lifecycle operation
        # --------------------------------------------------------------

        self._record_call(
            "set_status",
            status,
        )

        return self

    def finish_trace(
        self,
        trace: FakeTrace | None = None,
        *,
        status: FakeStatus | str | None = None,
        **kwargs: Any,
    ) -> FakeTrace | None:
        self.finish_trace_called += 1

        trace = trace or self._current_trace

        if trace is None:
            return None

        # --------------------------------------------------------------
        # Resolve status.
        # --------------------------------------------------------------

        if status is None:
            status = trace.status

        if isinstance(status, str):
            normalized = status.strip().lower()

            if normalized == "success":
                status = FakeStatus.SUCCESS

            elif normalized in {
                "error",
                "failed",
                "failure",
            }:
                status = FakeStatus.ERROR

            elif normalized in {
                "unset",
                "",
            }:
                status = FakeStatus.SUCCESS

            else:
                raise ValueError(
                    f"Unsupported trace status: {status!r}"
                )

        elif status is FakeStatus.UNSET:
            # A trace that reaches normal completion without an
            # explicit status is considered successful.
            status = FakeStatus.SUCCESS

        elif status not in {
            FakeStatus.SUCCESS,
            FakeStatus.ERROR,
        }:
            raise ValueError(
                f"Unsupported trace status: {status!r}"
            )

        # --------------------------------------------------------------
        # Record lifecycle call.
        # --------------------------------------------------------------

        self._record_call(
            "finish_trace",
            trace,
            status=status,
            **kwargs,
        )

        self.last_finished_trace = trace

        # --------------------------------------------------------------
        # Finalize trace.
        # --------------------------------------------------------------

        trace.finish(status=status)

        self._completed_traces[trace.trace_id] = trace

        if trace is self._current_trace:
            self._current_trace = None
            self._current_span = None
            self._span_stack.clear()

        return trace


    # ==================================================================
    # Span lifecycle
    # ==================================================================

    def start_span(
        self,
        name: str,
        *,
        trace: FakeTrace | None = None,
        parent: FakeSpan | None = None,
        attributes: Attributes | None = None,
        **extra_attributes: Any,
    ) -> FakeSpan:
        """
        Parent resolution:

            explicit parent
                â†“
            current active span
                â†“
            root span
        """

        trace = trace or self._current_trace

        if trace is None:
            raise RuntimeError(
                "Cannot start a span without an active trace."
            )

        if parent is None:
            parent = self._current_span

        span_attributes = dict(attributes or {})
        span_attributes.update(extra_attributes)

        span = FakeSpan(
            name=name,
            trace_id=trace.trace_id,
            parent=parent,
            parent_span_id=(
                parent.span_id
                if parent is not None
                else None
            ),
            attributes=span_attributes,
        )

        span.start()

        if parent is not None:
            parent.add_child(span)

        trace.add_span(span)

        self._spans.append(span)
        self._span_stack.append(span)
        self._current_span = span

        self._record_call(
            "start_span",
            name,
            trace=trace,
            parent=parent,
            attributes=span_attributes,
        )

        return span

    def finish_span(
        self,
        span: FakeSpan | None = None,
        *,
        status: FakeStatus = FakeStatus.SUCCESS,
        **kwargs: Any,
    ) -> FakeSpan | None:
        span = span or self._current_span

        self._record_call(
            "finish_span",
            span,
            status=status,
            **kwargs,
        )

        if span is None:
            return None

        if not span.finished:
            span.finish(status=status)

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

    # ==================================================================
    # Stack management
    # ==================================================================

    def push_span(self, span: FakeSpan) -> FakeSpan:
        if span not in self._spans:
            self._spans.append(span)

        if span not in self._span_stack:
            self._span_stack.append(span)

        self._current_span = span

        self._record_call("push_span", span)

        return span

    def pop_span(self) -> FakeSpan | None:
        if not self._span_stack:
            return None

        span = self._span_stack.pop()

        self._current_span = (
            self._span_stack[-1]
            if self._span_stack
            else None
        )

        self._record_call("pop_span", span)

        return span

    def peek_span(self) -> FakeSpan | None:
        return self._span_stack[-1] if self._span_stack else None

    # ==================================================================
    # Events
    # ==================================================================

    def emit(
        self,
        name: str,
        *,
        phase: str = "runtime",
        **attributes: Any,
    ) -> FakeEvent:
        """
        Emit a tracing event through the manager's processor path.

        Events require an active span.
        """

        target = self._current_span

        if target is None:
            raise RuntimeError(
                "Cannot emit an event without an active span."
            )

        event = FakeEvent(
            name=name,
            phase=phase,
            attributes=attributes,
        )

        events = getattr(target, "events", None)

        if events is not None:
            events.append(event)

        processor = self._processor

        if processor is not None:
            processor.on_event(
                target,
                event,
            )

        self._record_call(
            "emit",
            name,
            phase=phase,
            attributes=dict(attributes),
        )

        return event

    def add_event(
        self,
        event: FakeEvent,
    ) -> FakeEvent:
        span = self._current_span

        if span is None:
            raise RuntimeError(
                "Cannot add an event without an active span."
            )

        if not isinstance(event, FakeEvent):
            raise TypeError(
                "event must be a FakeEvent instance."
            )

        span.events.append(event)

        self._record_call(
            "add_event",
            event,
        )

        return event

    def clear_stack(self) -> None:
        self._span_stack.clear()
        self._current_span = None

        self._record_call("clear_stack")

    def iter_stack(self) -> Iterator[FakeSpan]:
        yield from self._span_stack

    def record_exception(
        self,
        exc: BaseException,
    ) -> FakeEvent:
        span = self._current_span

        if span is None:
            raise RuntimeError(
                "Cannot record an exception without an active span."
            )

        event = FakeEvent(
            name="exception",
            phase="exception",
            attributes={
                "exception.type": type(exc).__name__,
                "exception.message": str(exc),
            },
        )

        span.events.append(event)

        span.record_exception(exc)

        self._record_call(
            "record_exception",
            exc,
        )

        return event

    def validate_span_stack(self) -> bool:
        if not self._span_stack:
            return True

        return (
            self.current_span is self._span_stack[-1]
            and all(
                self._span_stack[i].parent_span_id
                == self._span_stack[i - 1].span_id
                for i in range(1, len(self._span_stack))
            )
        )

    # ==================================================================
    # Trace queries
    # ==================================================================

    def get_trace(
        self,
        name: str | None = None,
        *,
        trace_id: str | None = None,
    ) -> FakeTrace | None:
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

    def has_trace(self, trace_id: str) -> bool:
        return self.get_trace(trace_id=trace_id) is not None

    def iter_traces(self) -> Iterator[FakeTrace]:
        yield from self._traces

    # ==================================================================
    # Span queries
    # ==================================================================

    def get_span(
        self,
        name: str | None = None,
        *,
        span_id: str | None = None,
    ) -> FakeSpan | None:
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

    def has_span(self, span_id: str) -> bool:
        return self.get_span(span_id=span_id) is not None

    def iter_spans(self) -> Iterator[FakeSpan]:
        yield from self._spans

    # ==================================================================
    # Collection queries
    # ==================================================================

    def find_traces(
        self,
        predicate: Callable[[FakeTrace], bool],
    ) -> list[FakeTrace]:
        return [
            trace
            for trace in self._traces
            if predicate(trace)
        ]

    def find_spans(
        self,
        predicate: Callable[[FakeSpan], bool],
    ) -> list[FakeSpan]:
        return [
            span
            for span in self._spans
            if predicate(span)
        ]

    def traces_by_status(
        self,
        status: FakeStatus,
    ) -> list[FakeTrace]:
        return [
            trace
            for trace in self._traces
            if trace.status == status
        ]

    def spans_by_status(
        self,
        status: FakeStatus,
    ) -> list[FakeSpan]:
        return [
            span
            for span in self._spans
            if span.status == status
        ]

    # ==================================================================
    # Context managers
    # ==================================================================

    @contextmanager
    def trace_scope(
        self,
        name: str,
        *,
        metadata: Metadata | None = None,
        attributes: Attributes | None = None,
    ) -> Iterator[FakeTrace]:
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

    @contextmanager
    def span_scope(
        self,
        name: str,
        *,
        trace: FakeTrace | None = None,
        parent: FakeSpan | None = None,
        attributes: Attributes | None = None,
    ) -> Iterator[FakeSpan]:
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

    # ==================================================================
    # Execution helpers
    # ==================================================================

    def run_in_trace(
        self,
        name: str,
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        with self.trace_scope(name):
            return func(*args, **kwargs)

    def run_in_span(
        self,
        name: str,
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        with self.span_scope(name):
            return func(*args, **kwargs)

    # ==================================================================
    # Serialization / snapshots
    # ==================================================================

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_count": self.trace_count,
            "span_count": self.span_count,
            "current_trace": (
                self._current_trace.trace_id
                if self._current_trace is not None
                else None
            ),
            "current_span": (
                self._current_span.span_id
                if self._current_span is not None
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

    def snapshot(self) -> dict[str, Any]:
        return self.to_dict()

    def copy(self) -> "FakeTraceManager":
        return deepcopy(self)

    def state_summary(self) -> dict[str, Any]:
        return {
            "trace_count": self.trace_count,
            "span_count": self.span_count,
            "active_trace": self.has_active_trace,
            "active_span": self.has_active_span,
            "stack_depth": self.stack_depth,
        }

    def __repr__(self) -> str:
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


@dataclass(slots=True)
class ProcessorCall:
    """
    Recorded processor callback.
    """

    method: str
    target: Any = None
    success: bool | None = None
    error: Exception | None = None
    kwargs: dict[str, Any] = field(default_factory=dict)


# ============================================================================
# FakeProcessor
# ============================================================================

class FakeProcessor:
    """
    Test double for the tracing processor.

    Records every processor callback without transforming tracing objects.
    """

    def __init__(self) -> None:
        self.calls: list[ProcessorCall] = []

        # Legacy/helper counters
        self._started_spans = 0
        self._finished_spans = 0
        self._events: list[str] = []

        # Processing state
        self.processed = False
        self.processed_spans: list[Any] = []

        # Runtime state
        self._enabled = True
        self._manager = None
        self._trace = None
        self._current_span = None
        self._context = None
        self._span_stack: list[Any] = []

        # Lifecycle counters
        self.trace_started = 0
        self.trace_finished = 0

        self.span_started = 0
        self.span_finished = 0

        self.event_processed = 0
        self.attribute_processed = 0
        self.status_processed = 0
        self.exception_processed = 0

        # Last callback payloads
        self.last_trace = None
        self.last_span = None
        self.last_event = None

    # ------------------------------------------------------------------
    # Processing
    # ------------------------------------------------------------------

    def process(self, span) -> Any:
        self.processed = True
        self.processed_spans.append(span)

        self.calls.append(
            ProcessorCall(
                method="process",
                target=span,
            )
        )

        return span

    # ------------------------------------------------------------------
    # Trace lifecycle
    # ------------------------------------------------------------------

    def on_trace_start(self, trace) -> None:
        self.trace_started += 1
        self.last_trace = trace
        self._trace = trace
        self._events.append("trace_start")

        self.calls.append(
            ProcessorCall(
                method="on_trace_start",
                target=trace,
            )
        )

    def on_trace_finish(
        self,
        trace,
        *,
        success: bool = True,
    ) -> None:
        self.trace_finished += 1
        self.last_trace = trace
        self._trace = trace
        self._events.append("trace_finish")

        self.calls.append(
            ProcessorCall(
                method="on_trace_finish",
                target=trace,
                success=success,
            )
        )

    # ------------------------------------------------------------------
    # Span lifecycle
    # ------------------------------------------------------------------

    def on_span_start(self, span) -> None:
        self.span_started += 1
        self._started_spans += 1
        self.last_span = span

        self.calls.append(
            ProcessorCall(
                method="on_span_start",
                target=span,
            )
        )

    def on_span_finish(self, span) -> None:
        self.span_finished += 1
        self._finished_spans += 1
        self.last_span = span

        self.calls.append(
            ProcessorCall(
                method="on_span_finish",
                target=span,
            )
        )

    # ------------------------------------------------------------------
    # Event / attribute / status / exception
    # ------------------------------------------------------------------

    def on_event(self, obj, event) -> None:
        self._events.append("event")
        self.event_processed += 1
        self.last_event = event

        self.calls.append(
            ProcessorCall(
                method="on_event",
                target=obj,
                kwargs={"event": event},
            )
        )

    def on_attribute(
        self,
        obj,
        key,
        value,
    ) -> None:
        self.attribute_processed += 1

        self.calls.append(
            ProcessorCall(
                method="on_attribute",
                target=obj,
                kwargs={
                    "key": key,
                    "value": value,
                },
            )
        )

    def on_status(
        self,
        obj,
        status,
    ) -> None:
        self.status_processed += 1

        self.calls.append(
            ProcessorCall(
                method="on_status",
                target=obj,
                kwargs={
                    "status": status,
                },
            )
        )

    def on_exception(
        self,
        obj,
        exc: Exception,
    ) -> None:
        self.exception_processed += 1

        self.calls.append(
            ProcessorCall(
                method="on_exception",
                target=obj,
                error=exc,
            )
        )

    # ------------------------------------------------------------------
    # Runtime lifecycle
    # ------------------------------------------------------------------

    def before_runtime(self, trace) -> None:
        """
        Compatibility callback for runtime lifecycle.

        Runtime tests should normally use on_trace_start/on_trace_finish.
        """

        self.trace_started += 1
        self.last_trace = trace
        self._trace = trace
        self._events.append("trace_start")

        self.calls.append(
            ProcessorCall(
                method="before_runtime",
                target=trace,
            )
        )

    def after_runtime(
        self,
        trace,
        success: bool = True,
        error: Exception | None = None,
    ) -> None:
        """
        Compatibility callback for runtime lifecycle.
        """

        self.trace_finished += 1
        self.last_trace = trace
        self._trace = trace
        self._events.append("trace_finish")

        self.calls.append(
            ProcessorCall(
                method="after_runtime",
                target=trace,
                success=success,
                error=error,
            )
        )

    # ------------------------------------------------------------------
    # Stage
    # ------------------------------------------------------------------

    def before_stage(self, span) -> None:
        self._current_span = span

        self.calls.append(
            ProcessorCall(
                method="before_stage",
                target=span,
            )
        )

    def after_stage(
        self,
        span,
        success: bool,
        error: Exception | None = None,
    ) -> None:
        self.calls.append(
            ProcessorCall(
                method="after_stage",
                target=span,
                success=success,
                error=error,
            )
        )

    # ------------------------------------------------------------------
    # Task
    # ------------------------------------------------------------------

    def before_task(self, span) -> None:
        self._started_spans += 1
        self.span_started += 1
        self.last_span = span

        self.calls.append(
            ProcessorCall(
                method="before_task",
                target=span,
            )
        )

    def after_task(
        self,
        span,
        success: bool,
        error: Exception | None = None,
    ) -> None:
        self._finished_spans += 1
        self.span_finished += 1
        self.last_span = span

        self.calls.append(
            ProcessorCall(
                method="after_task",
                target=span,
                success=success,
                error=error,
            )
        )

    # ------------------------------------------------------------------
    # Generic lifecycle
    # ------------------------------------------------------------------

    def on_start(self, obj) -> None:
        self.calls.append(
            ProcessorCall(
                method="on_start",
                target=obj,
            )
        )

    def on_end(self, obj) -> None:
        self.calls.append(
            ProcessorCall(
                method="on_end",
                target=obj,
            )
        )

    def on_export(self, obj) -> None:
        self.calls.append(
            ProcessorCall(
                method="on_export",
                target=obj,
            )
        )

    def flush(self) -> None:
        self.calls.append(
            ProcessorCall(method="flush")
        )

    def shutdown(self) -> None:
        self.calls.append(
            ProcessorCall(method="shutdown")
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def events(self) -> list[str]:
        return list(self._events)

    @property
    def started_spans(self) -> int:
        return self._started_spans

    @property
    def finished_spans(self) -> int:
        return self._finished_spans

    @property
    def call_count(self) -> int:
        return len(self.calls)

    @property
    def last_call(self) -> ProcessorCall | None:
        return self.calls[-1] if self.calls else None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def was_called(self, method: str) -> bool:
        return any(
            call.method == method
            for call in self.calls
        )

    def calls_for(
        self,
        method: str,
    ) -> list[ProcessorCall]:
        return [
            call
            for call in self.calls
            if call.method == method
        ]

    def call_order(self) -> list[str]:
        return [
            call.method
            for call in self.calls
        ]

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------

    def clear(self) -> None:
        self.calls.clear()

        self._started_spans = 0
        self._finished_spans = 0
        self._events.clear()

        self.processed = False
        self.processed_spans.clear()

        self.trace_started = 0
        self.trace_finished = 0

        self.span_started = 0
        self.span_finished = 0

        self.event_processed = 0
        self.attribute_processed = 0
        self.status_processed = 0
        self.exception_processed = 0

        self.last_trace = None
        self.last_span = None
        self.last_event = None

        self._trace = None
        self._current_span = None
        self._context = None
        self._span_stack.clear()

    reset = clear


# ============================================================================
# FakeExporter
# ============================================================================


class FakeExporter:
    """
    Lightweight exporter fake for tracing tests.

    Records trace exports explicitly so runtime plugin tests can assert:

    - number of trace exports
    - exported trace payload
    - exporter ordering
    - exactly-once semantics
    - lifecycle calls
    """

    def __init__(self) -> None:
        self.exports: list[tuple[str, Any]] = []

        # --------------------------------------------------------------
        # Exported payloads
        # --------------------------------------------------------------

        self.exported_traces: list[Any] = []
        self.exported_spans: list[Any] = []
        self.exported_metrics: list[Any] = []
        self.exported_logs: list[Any] = []

        # --------------------------------------------------------------
        # General state
        # --------------------------------------------------------------

        self.exported = False

        # --------------------------------------------------------------
        # Lifecycle state
        # --------------------------------------------------------------

        self.flushed = False
        self.closed = False
        self.shutdown_called = False

        # Lifecycle counters
        self.flush_count = 0
        self.shutdown_count = 0

    # ------------------------------------------------------------------
    # Trace export
    # ------------------------------------------------------------------

    def export_trace(self, trace: Any) -> None:
        self.exported = True
        self.exported_traces.append(trace)

        self.exports.append(
            ("trace", trace)
        )

    # ------------------------------------------------------------------
    # Generic export
    # ------------------------------------------------------------------

    def export(self, item: Any) -> None:
        self.exported = True

        self.exports.append(
            ("generic", item)
        )

        # Runtime TracePlugin currently calls export(trace).
        self.exported_traces.append(item)

    # ------------------------------------------------------------------
    # Other export types
    # ------------------------------------------------------------------

    def export_span(self, span: Any) -> None:
        self.exported = True
        self.exported_spans.append(span)

        self.exports.append(
            ("span", span)
        )

    def export_metric(self, metric: Any) -> None:
        self.exported = True
        self.exported_metrics.append(metric)

        self.exports.append(
            ("metric", metric)
        )

    def export_log(self, record: Any) -> None:
        self.exported = True
        self.exported_logs.append(record)

        self.exports.append(
            ("log", record)
        )

    # ------------------------------------------------------------------
    # Runtime-test compatibility
    # ------------------------------------------------------------------

    @property
    def trace_exports(self) -> int:
        return len(self.exported_traces)

    @property
    def last_trace(self) -> Any:
        return (
            self.exported_traces[-1]
            if self.exported_traces
            else None
        )

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def flush(self) -> None:
        self.flushed = True
        self.flush_count += 1

    def shutdown(self) -> None:
        self.shutdown_called = True
        self.closed = True
        self.shutdown_count += 1

    # ------------------------------------------------------------------
    # Compatibility aliases
    # ------------------------------------------------------------------

    @property
    def flush_called(self) -> bool:
        """
        Backward-compatible alias.

        ``flushed`` is the canonical lifecycle state.
        """
        return self.flushed

    @property
    def shutdown_called_flag(self) -> bool:
        """
        Compatibility alias for explicit lifecycle assertions.
        """
        return self.shutdown_called

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @property
    def export_count(self) -> int:
        return len(self.exports)

    @property
    def last_export(self) -> tuple[str, Any] | None:
        return self.exports[-1] if self.exports else None

    @property
    def has_exports(self) -> bool:
        return bool(self.exports)

    def clear(self) -> None:
        self.exports.clear()

        self.exported_traces.clear()
        self.exported_spans.clear()
        self.exported_metrics.clear()
        self.exported_logs.clear()

        self.exported = False

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
    Deterministic clock for repeatable tests.
    """

    def __init__(self) -> None:
        self._time = 0.0
        self._frozen = False

        self.history: list[float] = []
        self.tick_count = 0

    # ------------------------------------------------------------------
    # Time
    # ------------------------------------------------------------------

    def now(self) -> float:
        return self._time

    def time(self) -> float:
        return self._time

    def advance(self, seconds: float = 1.0) -> float:
        if seconds < 0:
            raise ValueError("seconds must be non-negative")

        if not self._frozen:
            self._time += seconds

        self.tick_count += 1
        self.history.append(self._time)

        return self._time

    def advance_ms(self, milliseconds: float) -> float:
        return self.advance(milliseconds / 1_000.0)

    def advance_ns(self, nanoseconds: int) -> float:
        return self.advance(
            nanoseconds / 1_000_000_000
        )

    # ------------------------------------------------------------------
    # Freeze
    # ------------------------------------------------------------------

    def freeze(self) -> None:
        """
        Freeze the clock at its current time.

        While frozen, calls to ``advance()`` do not change the current
        time, although the call is still recorded in ``history`` and
        ``tick_count``.
        """
        self._frozen = True

    def resume(self) -> None:
        """
        Resume normal clock advancement.
        """
        self._frozen = False

    @property
    def trace_exports(self) -> int:
        return len(self.exported_traces)


    @property
    def last_trace(self) -> Any | None:
        return (
            self.exported_traces[-1]
            if self.exported_traces
            else None
        )

    @property
    def frozen(self) -> bool:
        """
        Return whether the clock is currently frozen.
        """
        return self._frozen

    @contextmanager
    def frozen_scope(self) -> Iterator["FakeClock"]:
        """
        Temporarily freeze the clock within a context.

        The previous frozen state is restored when leaving the context,
        including when an exception is raised.

        Examples
        --------
        >>> clock = FakeClock()
        >>> clock.advance(5.0)
        5.0
        >>> with clock.frozen_scope():
        ...     clock.advance(10.0)
        5.0
        >>> clock.advance(2.0)
        7.0
        """
        previous = self._frozen
        self._frozen = True

        try:
            yield self
        finally:
            self._frozen = previous

    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------

    @property
    def last_tick(self) -> float | None:
        return self.history[-1] if self.history else None

    def reset(self) -> "FakeClock":
        self._time = 0.0
        self._frozen = False
        self.history.clear()
        self.tick_count = 0

        return self


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "Attributes",
    "Metadata",
    "FakeStatus",
    "CallRecord",
    "FakeTrace",
    "FakeSpan",
    "FakeTraceManager",
    "ProcessorCall",
    "FakeProcessor",
    "FakeExporter",
    "FakeClock",
]

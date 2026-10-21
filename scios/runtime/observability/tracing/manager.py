"""
SciOS Runtime Tracing Manager
=============================

Part 1. Constructor + Internal State + Lifecycle + Registry

Python 3.11+
"""

from __future__ import annotations

import copy
import time
import uuid

from collections.abc import Iterable, Mapping
from typing import Any, Optional

from .context import TraceContext
from .exporter import TraceExporter
from .processor import TraceProcessor
from .sampler import TraceSampler
from .span import Span
from .trace import Trace
from .event import Event
from .enums import ExecutionPhase, Severity


class TraceManager:
    """
    Central runtime tracing manager.

    Part A responsibilities
    -----------------------
    - constructor
    - internal state
    - lifecycle
    - active/completed trace registry
    - global manager registry
    - basic statistics

    Python 3.11+
    """

    # ==================================================================
    # Global registry
    # ==================================================================

    _global: Optional["TraceManager"] = None

    # ==================================================================
    # Constructor
    # ==================================================================

    def __init__(
        self,
        name: str = "tracer",
        service_name: str = "scios",
        enabled: bool = True,
        *,
        sampler: Optional[TraceSampler] = None,
        processor: Optional[TraceProcessor] = None,
        processors: Optional[Iterable[Any]] = None,
        exporters: Optional[Iterable[TraceExporter]] = None,
        context: Optional[TraceContext] = None,
        metadata: Optional[Mapping[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        # --------------------------------------------------------------
        # Validate configuration
        # --------------------------------------------------------------

        if not isinstance(name, str):
            raise TypeError("name must be a string")

        name = name.strip()

        if not name:
            raise ValueError("name cannot be empty")

        if not isinstance(service_name, str):
            raise TypeError("service_name must be a string")

        service_name = service_name.strip()

        if not service_name:
            raise ValueError("service_name cannot be empty")

        if not isinstance(enabled, bool):
            raise TypeError("enabled must be a bool")

        # --------------------------------------------------------------
        # Identity / configuration
        # --------------------------------------------------------------

        self._manager_id: str = str(uuid.uuid4())
        self._name: str = name
        self._service_name: str = service_name
        self._enabled: bool = enabled

        self._sampler: Optional[TraceSampler] = sampler

        # --------------------------------------------------------------
        # Tracer registry
        #
        # Tracers are runtime dependencies. They are intentionally
        # excluded from serialized snapshots.
        # --------------------------------------------------------------

        self._tracers: dict[str, Any] = {}
        self._default_tracer: Optional[Any] = None

        # --------------------------------------------------------------
        # Processor pipeline
        #
        # `processor` is retained for backward compatibility.
        # `processors` is the preferred multi-processor API.
        # --------------------------------------------------------------

        self._processors: list[Any] = []

        if processors is not None:
            self._processors.extend(
                p
                for p in processors
                if p is not None
            )

        if processor is not None and processor not in self._processors:
            self._processors.insert(0, processor)

        self._processor: Optional[Any] = (
            self._processors[0]
            if self._processors
            else None
        )

        # --------------------------------------------------------------
        # Export pipeline
        # --------------------------------------------------------------

        self._exporters: list[TraceExporter] = list(
            exporters or ()
        )

        # --------------------------------------------------------------
        # Runtime context
        # --------------------------------------------------------------

        self._context: Optional[TraceContext] = context

        # --------------------------------------------------------------
        # Current trace state
        #
        # `_trace` is the canonical current-trace reference.
        # `_traces` contains the traces created by this manager.
        # --------------------------------------------------------------

        self._trace: Optional[Trace] = None
        self._traces: list[Trace] = []

        # --------------------------------------------------------------
        # Current span state
        #
        # `_current_span` is the canonical current-span reference.
        # `_span_stack` preserves nested span scope.
        # --------------------------------------------------------------

        self._spans: list[Span] = []
        self._span_stack: list[Span] = []
        self._current_span: Optional[Span] = None

        # --------------------------------------------------------------
        # Trace registries
        #
        # These dictionaries are the authoritative runtime registries.
        # Do NOT maintain a separate active-trace counter.
        # --------------------------------------------------------------

        self._active_traces: dict[str, Trace] = {}
        self._completed_traces: dict[str, Trace] = {}

        # --------------------------------------------------------------
        # Lifecycle state
        # --------------------------------------------------------------

        self._initialized: bool = True
        self._active: bool = False
        self._closed: bool = False
        self._frozen: bool = False
        self._resetting: bool = False

        self._created_at: float = time.time()
        self._started_at: Optional[float] = None
        self._stopped_at: Optional[float] = None

        # --------------------------------------------------------------
        # Metadata / tags / options
        # --------------------------------------------------------------

        self._metadata: dict[str, Any] = dict(metadata or {})
        self._tags: list[str] = []
        self._baggage: dict[str, Any] = {}
        self._options: dict[str, Any] = dict(kwargs)

        # --------------------------------------------------------------
        # Statistics
        #
        # Registry-backed state:
        #   active traces     -> len(self._active_traces)
        #   completed traces  -> len(self._completed_traces)
        #
        # Explicit counters below represent cumulative lifecycle events.
        # --------------------------------------------------------------

        self._trace_count: int = 0
        self._completed_trace_count: int = 0
        self._cancelled_trace_count: int = 0

        self._span_count: int = 0
        self._completed_span_count: int = 0
        self._cancelled_span_count: int = 0
        self._active_span_count: int = 0

        self._exported_count: int = 0
        self._processed_count: int = 0
        self._error_count: int = 0

        # --------------------------------------------------------------
        # Diagnostics
        # --------------------------------------------------------------

        self._events: list[Any] = []

    # ==================================================================
    # Identity / configuration
    # ==================================================================

    @property
    def id(self) -> str:
        """Return the manager identifier."""
        return self._manager_id

    @property
    def name(self) -> str:
        """Return the manager name."""
        return self._name

    @property
    def service_name(self) -> str:
        """Return the service name."""
        return self._service_name

    @property
    def enabled(self) -> bool:
        """Return whether tracing is enabled."""
        return self._enabled

    @property
    def exporters(self) -> list[TraceExporter]:
        """
        Return a detached snapshot of registered exporters.
        """
        return list(self._exporters)

    def add_exporter(
        self,
        exporter: TraceExporter,
    ) -> "TraceManager":
        """
        Register an exporter.

        Duplicate exporter instances are ignored.
        """
        if exporter is None:
            raise TypeError(
                "exporter must not be None"
            )

        if exporter not in self._exporters:
            self._exporters.append(exporter)

        return self

    def remove_exporter(
        self,
        exporter: TraceExporter,
    ) -> "TraceManager":
        """
        Remove an exporter if registered.
        """
        if exporter in self._exporters:
            self._exporters.remove(exporter)

        return self

    def clear_exporters(
        self,
    ) -> "TraceManager":
        """
        Remove all registered exporters.
        """
        self._exporters.clear()

        return self

    # ==================================================================
    # Lifecycle state
    # ==================================================================

    @property
    def initialized(self) -> bool:
        """Return whether the manager is initialized."""
        return self._initialized

    @property
    def active(self) -> bool:
        """Return whether the manager is active."""
        return self._active

    @property
    def closed(self) -> bool:
        """Return whether the manager is closed."""
        return self._closed

    @property
    def frozen(self) -> bool:
        """Return whether the manager is frozen."""
        return self._frozen

    @property
    def state(self) -> str:
        """
        Return the current lifecycle state of the manager.

        State is derived from the authoritative lifecycle flags.
        No separate mutable `_state` is maintained.
        """
        if self._closed:
            return "closed"

        if self._frozen:
            return "frozen"

        if self._active:
            return "running"

        if self._initialized:
            return "initialized"

        return "created"

    # ==================================================================
    # Current tracing state
    # ==================================================================

    @property
    def current_trace(self) -> Optional[Trace]:
        """Return the currently active trace.

        Returns:
            The active :class:`Trace`, or ``None`` when no trace
            is currently active.
        """
        return self._trace

    @property
    def trace(self) -> Optional[Trace]:
        """Alias for :attr:`current_trace`."""
        return self._trace

    @property
    def current_span(self) -> Optional[Span]:
        """Return the currently active span.

        Returns:
            The active :class:`Span`, or ``None`` when no span
            is currently active.
        """
        return self._current_span

    @property
    def active_span(self) -> Optional[Span]:
        """Alias for :attr:`current_span`."""
        return self._current_span

    @property
    def active_trace_count(self) -> int:
        """Return the number of currently active traces.

        The value represents traces that have been started but have
        not yet been finished.
        """
        return self._active_trace_count

    def root_span(self) -> Optional[Span]:
        """Return the root span of the current trace.

        Returns:
            The first span in the current trace, or ``None`` when
            there is no active trace or the trace contains no spans.
        """
        trace = self.current_trace

        if trace is None:
            return None

        spans = getattr(trace, "spans", None)

        if not spans:
            return None

        return spans[0]

    def current_context(self) -> Optional[TraceContext]:
        """Return the current tracing context.

        Returns:
            The current :class:`TraceContext`, or ``None`` when
            no tracing context has been established.
        """
        return self._context

    def active_span_stack(self) -> list[Span]:
        """Return a snapshot of the active span stack.

        Returns:
            A shallow copy of the current active span stack.
        """
        return list(self._span_stack)

    @property
    def span_stack(self) -> list[Span]:
        """Return a snapshot of the active span stack.

        Alias for :meth:`active_span_stack`.
        """
        return list(self._span_stack)

    @property
    def stack_depth(self) -> int:
        """Return the current span stack depth."""
        return len(self._span_stack)

    @property
    def span_depth(self) -> int:
        """Alias for :attr:`stack_depth`."""
        return len(self._span_stack)


    # ==================================================================
    # Metadata
    # ==================================================================

    @property
    def metadata(self) -> dict[str, Any]:
        """Return a copy of manager metadata."""
        return dict(self._metadata)

    # ==================================================================
    # Baggage
    # ==================================================================

    @property
    def baggage(self) -> dict[str, Any]:
        """
        Return a detached snapshot of manager baggage.

        The returned dictionary is independent from the manager's
        internal baggage state.
        """
        return copy.deepcopy(
            self._baggage,
        )


    def _require_active_trace_for_baggage(self) -> None:
        """Require an active trace for baggage operations."""

        if self._trace is None:
            raise RuntimeError(
                "baggage requires an active trace",
            )


    def add_baggage(
        self,
        key: str,
        value: Any,
    ) -> "TraceManager":
        """
        Add or replace one baggage value.

        Baggage is scoped to the current active trace.
        """

        self._require_active_trace_for_baggage()

        if not isinstance(key, str):
            raise TypeError(
                "baggage key must be a string",
            )

        key = key.strip()

        if not key:
            raise ValueError(
                "baggage key cannot be empty",
            )

        self._baggage[key] = copy.deepcopy(
            value,
        )

        return self


    def get_baggage(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Return one baggage value.

        ``default`` is returned when the key does not exist.
        """

        self._require_active_trace_for_baggage()

        if not isinstance(key, str):
            raise TypeError(
                "baggage key must be a string",
            )

        return self._baggage.get(
            key,
            default,
        )


    def has_baggage(
        self,
        key: str,
    ) -> bool:
        """Return whether a baggage key exists."""

        self._require_active_trace_for_baggage()

        if not isinstance(key, str):
            raise TypeError(
                "baggage key must be a string",
            )

        return key in self._baggage


    def remove_baggage(
        self,
        key: str,
    ) -> bool:
        """
        Remove one baggage value.

        Returns ``True`` when an item was removed and ``False`` when
        the key did not exist.
        """

        self._require_active_trace_for_baggage()

        if not isinstance(key, str):
            raise TypeError(
                "baggage key must be a string",
            )

        if key not in self._baggage:
            return False

        del self._baggage[key]

        return True


    def clear_baggage(
        self,
    ) -> int:
        """
        Clear all baggage.

        Returns the number of removed entries.
        """

        self._require_active_trace_for_baggage()

        count = len(
            self._baggage,
        )

        self._baggage.clear()

        return count


    # ==================================================================
    # Trace registry
    # ==================================================================

    @property
    def active_traces(self) -> dict[str, Trace]:
        """
        Return the active trace registry.

        The returned dictionary is the manager's live registry.
        """
        return self._active_traces

    @property
    def completed_traces(self) -> dict[str, Trace]:
        """
        Return the completed trace registry.

        The returned dictionary is the manager's live registry.
        """
        return self._completed_traces

    @property
    def active_trace_count(self) -> int:
        """
        Number of currently active traces.

        The active-trace registry is the single source of truth.
        """
        return len(self._active_traces)

    @property
    def completed_trace_count(self) -> "_CallableCount":
        """
        Total number of completed traces.

        Supports both:
            manager.completed_trace_count
            manager.completed_trace_count()
        """
        return self._CallableCount(
            self._completed_trace_count
        )

    def has_active_trace(self) -> bool:
        """
        Return True when at least one trace is active.
        """
        return self._trace is not None

    def has_active_span(self) -> bool:
        """
        Return True when a current active span exists.
        """
        return self._current_span is not None

    # ==================================================================
    # Trace statistics
    # ==================================================================

    @property
    def trace_count(self) -> int:
        """Return the total number of traces created."""
        return self._trace_count

    @property
    def total_trace_count(self) -> int:
        """Return the total number of traces created."""
        return self._trace_count

    @property
    def cancelled_trace_count(self) -> int:
        """Return the number of cancelled traces."""
        return self._cancelled_trace_count

    # ==================================================================
    # Span statistics
    # ==================================================================

    @property
    def span_count(self) -> int:
        """Return the total number of spans created."""
        return self._span_count

    @property
    def completed_span_count(self) -> int:
        """Return the number of completed spans."""
        return self._completed_span_count

    @property
    def cancelled_span_count(self) -> int:
        """Return the number of cancelled spans."""
        return self._cancelled_span_count

    @property
    def active_span_count(self) -> int:
        """Return the number of active spans."""
        return self._active_span_count

    # ==================================================================
    # Processing / exporting statistics
    # ==================================================================

    @property
    def exported_count(self) -> int:
        """Return the number of successfully exported traces."""
        return self._exported_count

    @property
    def processed_count(self) -> int:
        """Return the number of processed traces."""
        return self._processed_count

    @property
    def error_count(self) -> int:
        """Return the number of processing/export errors."""
        return self._error_count

    # ==================================================================
    # Global registry
    # ==================================================================

    @classmethod
    def get_global(cls) -> "TraceManager":
        """
        Return the process-wide global TraceManager.
        """
        if cls._global is None:
            cls._global = cls()

        return cls._global

    @classmethod
    def set_global(
        cls,
        manager: Optional["TraceManager"],
    ) -> Optional["TraceManager"]:
        """
        Set the process-wide global TraceManager.

        Returns the previously registered manager.
        """
        if manager is not None and not isinstance(manager, cls):
            raise TypeError(
                f"manager must be an instance of {cls.__name__}"
            )

        previous = cls._global
        cls._global = manager

        return previous

    # ==================================================================
    # Lifecycle
    # ==================================================================

    def initialize(self) -> "TraceManager":
        """
        Initialize or reinitialize the manager.
        """
        self._initialized = True
        self._closed = False
        self._frozen = False

        return self

    def start(self) -> "TraceManager":
        """
        Start the tracing manager.
        """
        if self._closed:
            raise RuntimeError(
                "Cannot start a closed TraceManager."
            )

        if not self._initialized:
            self.initialize()

        self._active = True
        self._started_at = time.time()

        return self

    def stop(self) -> "TraceManager":
        """
        Stop the manager without clearing completed traces.
        """
        self._active = False
        self._stopped_at = time.time()

        return self

    def freeze(self) -> "TraceManager":
        """Freeze manager mutations."""
        self._frozen = True
        return self

    def unfreeze(self) -> "TraceManager":
        """Allow manager mutations again."""
        self._frozen = False
        return self

    def clear(self) -> "TraceManager":
        """
        Clear current tracing runtime state.

        Configuration, processors, exporters, metadata, and manager identity
        are preserved. Active/completed trace registries and current span
        state are cleared.

        The manager remains initialized and open.
        """
        self._trace = None
        self._traces.clear()

        self._spans.clear()
        self._span_stack.clear()
        self._current_span = None
        self._active_span_count = 0

        self._active_traces.clear()
        self._completed_traces.clear()

        self._context = None

        self._trace_count = 0
        self._completed_trace_count = 0
        self._cancelled_trace_count = 0

        self._span_count = 0
        self._completed_span_count = 0
        self._cancelled_span_count = 0

        self._exported_count = 0
        self._processed_count = 0
        self._error_count = 0

        self._events.clear()

        self._active = False
        self._started_at = None
        self._stopped_at = None

        self._closed = False
        self._frozen = False
        self._resetting = False

        return self

    def reset(self) -> "TraceManager":
        """
        Reset runtime and tracing state while preserving configuration.
        """

        if self._closed:
            self._closed = False

        self._trace = None
        self._traces.clear()
        self._baggage.clear()

        self._spans.clear()
        self._span_stack.clear()
        self._current_span = None

        self._active_traces.clear()
        self._completed_traces.clear()

        self._context = None

        self._trace_count = 0
        self._completed_trace_count = 0
        self._cancelled_trace_count = 0

        self._span_count = 0
        self._completed_span_count = 0
        self._cancelled_span_count = 0
        self._active_span_count = 0

        self._exported_count = 0
        self._processed_count = 0
        self._error_count = 0

        self._events.clear()

        self._active = False
        self._frozen = False
        self._resetting = False

        self._started_at = None
        self._stopped_at = None

        return self

    def close(self) -> "TraceManager":
        """
        Close the manager.

        Completed traces remain queryable.
        """
        if self._trace is not None:
            self.finish_trace()

        self._spans.clear()
        self._span_stack.clear()
        self._traces.clear()

        self._trace = None
        self._current_span = None
        self._active_span_count = 0

        self._active = False
        self._closed = True
        self._stopped_at = time.time()

        return self

    def shutdown(self) -> "TraceManager":
        """
        Shutdown the manager.

        Active traces are finished before shutdown.
        Exporters are flushed and then shut down.
        Completed runtime state is cleared.
        """

        if self._closed:
            return self

        if self._trace is not None:
            self.finish_trace()

        # --------------------------------------------------------------
        # Flush exporters before shutdown
        # --------------------------------------------------------------

        self.flush()

        # --------------------------------------------------------------
        # Shutdown exporters
        # --------------------------------------------------------------

        for exporter in self._exporters:
            method = getattr(
                exporter,
                "shutdown",
                None,
            )

            if callable(method):
                method()

        # --------------------------------------------------------------
        # Clear runtime state
        # --------------------------------------------------------------

        self._active_traces.clear()
        self._completed_traces.clear()

        self._completed_trace_count = 0

        self._trace = None
        self._span_stack.clear()
        self._current_span = None
        self._active_span_count = 0

        self._context = None
        self._metadata.clear()

        self._active = False
        self._closed = True
        self._stopped_at = time.time()

        return self
    # ==================================================================
    # Trace identity
    # ==================================================================

    @staticmethod
    def _trace_id(trace: Trace) -> str:
        """
        Resolve the canonical trace identifier.
        """
        trace_id = getattr(trace, "trace_id", None)

        if trace_id is None:
            trace_id = getattr(trace, "id", None)

        if trace_id is None:
            raise ValueError(
                "Trace must provide trace_id or id."
            )

        return str(trace_id)

    def _notify_processors(
        self,
        callback_name: str,
        *args: Any,
    ) -> None:
        """
        Notify all registered processors.

        Processor callbacks are capability-based. A processor may implement
        only the callbacks it needs.

        Processor failures are intentionally propagated. This keeps processor
        failures visible to the runtime while preserving deterministic ordering.
        """

        for processor in tuple(self._processors):

            callback = getattr(
                processor,
                callback_name,
                None,
            )

            if not callable(callback):
                continue

            try:
                callback(*args)
                self._processed_count += 1

            except Exception:
                self._error_count += 1
                raise

    # ==================================================================
    # Tracer Registry
    # ==================================================================

    def register_tracer(
        self,
        name: str,
        tracer: Any,
    ) -> "TraceManager":
        """
        Register a runtime tracer under a symbolic name.

        Tracers are runtime dependencies and are intentionally kept
        outside serialized trace state.
        """

        if not isinstance(name, str):
            raise TypeError(
                "tracer name must be a string"
            )

        name = name.strip()

        if not name:
            raise ValueError(
                "tracer name cannot be empty"
            )

        if tracer is None:
            raise TypeError(
                "tracer cannot be None"
            )

        self._tracers[name] = tracer

        if self._default_tracer is None:
            self._default_tracer = tracer

        return self


    def get_tracer(
        self,
        name: str = "default",
    ) -> Any:
        """Return a registered tracer."""

        if not isinstance(name, str):
            raise TypeError(
                "tracer name must be a string"
            )

        name = name.strip()

        if not name:
            raise ValueError(
                "tracer name cannot be empty"
            )

        if name == "default":
            return self._default_tracer

        return self._tracers.get(name)

    # ==================================================================
    # Trace registry helpers
    # ==================================================================

    def register_trace(self, trace: Trace) -> Trace:
        """
        Register a trace as active.
        """
        if trace is None:
            raise TypeError("trace cannot be None")

        trace_id = self._trace_id(trace)

        # --------------------------------------------------------------
        # Already active
        # --------------------------------------------------------------

        if trace_id in self._active_traces:
            return self._active_traces[trace_id]

        # --------------------------------------------------------------
        # A completed trace with the same ID must not silently coexist.
        # --------------------------------------------------------------

        if trace_id in self._completed_traces:
            raise ValueError(
                f"Trace {trace_id!r} is already completed."
            )

        self._active_traces[trace_id] = trace

        self._trace_count += 1

        if trace not in self._traces:
            self._traces.append(trace)

        return trace

    def unregister_trace(
        self,
        trace: Trace,
    ) -> Optional[Trace]:
        """
        Move an active trace to the completed registry.

        This method performs the single registry transition:

            _active_traces
                ↓
            _completed_traces

        Trace lifecycle finalization belongs to finish_trace().
        """
        trace_id = self._trace_id(trace)

        active = self._active_traces.pop(
            trace_id,
            None,
        )

        if active is None:
            return None

        self._completed_traces[trace_id] = active

        self._completed_trace_count = len(
            self._completed_traces
        )

        self._active = bool(
            self._active_traces
        )

        return active

    def get_trace(
        self,
        trace_id: str,
    ) -> Optional[Trace]:
        """
        Return a trace from either active or completed registry.
        """
        key = str(trace_id)

        trace = self._active_traces.get(key)

        if trace is not None:
            return trace

        return self._completed_traces.get(key)

    def has_trace(
        self,
        trace_id: str,
    ) -> bool:
        """Return whether a trace exists."""
        return self.get_trace(trace_id) is not None

    # ==================================================================
    # Trace lifecycle
    # ==================================================================


    def _finish_span_for_trace(
        self,
        span: Span,
    ) -> None:
        """
        Finish a span during trace finalization.

        This helper is deliberately tolerant of different Span
        lifecycle implementations.
        """
        finish = getattr(span, "finish", None)

        if callable(finish):
            finish()

        try:
            self._span_stack.remove(span)
        except ValueError:
            pass

        self._current_span = (
            self._span_stack[-1]
            if self._span_stack
            else None
        )

        self._active_span_count = len(
            self._span_stack
        )

        self._completed_span_count += 1

    # ==================================================================
    # Representation
    # ==================================================================

    def __repr__(self) -> str:
        return (
            "TraceManager("
            f"name={self._name!r}, "
            f"service={self._service_name!r}, "
            f"enabled={self._enabled!r}, "
            f"active={self._active!r}, "
            f"active_traces={self.active_trace_count}, "
            f"completed={self.completed_trace_count}, "
            f"spans={self._span_count}"
            ")"
        )


    # ============================================================================
    # Part 4. Core Properties
    # ============================================================================

    @property
    def current_trace(self) -> Optional[Trace]:
        """Return the currently active trace."""
        return self._trace

    @property
    def _current_trace(self) -> Optional[Trace]:
        """
        Backward-compatible alias for the internal current trace state.

        ``_trace`` remains the canonical storage location.
        """
        return self._trace

    @property
    def trace(self) -> Optional[Trace]:
        """Alias for current_trace."""
        return self._trace


    @property
    def current_span(self) -> Optional[Span]:
        """
        Return the currently active span.

        The span stack is the single source of truth.
        """
        if not self._span_stack:
            return None

        return self._span_stack[-1]


    @property
    def active_span(self) -> Optional[Span]:
        """Alias for current_span."""
        return self.current_span


    @property
    def span_stack(self) -> list[Span]:
        """
        Return a snapshot of the active span stack.

        The returned list is independent from the internal stack.
        """
        return list(self._span_stack)


    def active_span_stack(self) -> list[Span]:
        """
        Return a snapshot of the active span stack.

        Alias-compatible method form.
        """
        return list(self._span_stack)


    @property
    def span_depth(self) -> int:
        """Return the current span nesting depth."""
        return len(self._span_stack)


    @property
    def stack_depth(self) -> int:
        """Alias for span_depth."""
        return len(self._span_stack)


    @property
    def active_trace_count(self) -> int:
        """
        Return the number of currently active traces.

        `_active_traces` is the authoritative runtime registry.
        """
        return len(self._active_traces)


    def current_context(self) -> Optional[TraceContext]:
        """
        Return the current tracing context.
        """
        return self._context


    @property
    def metadata(self) -> dict[str, Any]:
        """
        Return a shallow copy of manager metadata.
        """
        return dict(self._metadata)

    # ============================================================================
    # Part 5. Trace Lifecycle
    # ============================================================================

    def start_trace(
        self,
        name: str | None = None,
        *,
        metadata: Optional[Mapping[str, Any]] = None,
        attributes: Optional[Mapping[str, Any]] = None,
        **extra_attributes: Any,
    ) -> Optional[Trace]:
        """
        Create and start a new trace.

        Starting a new trace always establishes a new trace identity and
        resets the current span state.
        """

        if not self._enabled:
            return None

        if self._closed:
            raise RuntimeError(
                "Cannot start a trace on a closed TraceManager."
            )

        if self._frozen:
            raise RuntimeError(
                "Cannot start a trace on a frozen TraceManager."
            )

        trace_name = self._name if name is None else name

        if not isinstance(trace_name, str):
            raise TypeError("trace name must be a string")

        trace_name = trace_name.strip()

        if not trace_name:
            raise ValueError("trace name cannot be empty")


        # ------------------------------------------------------------------
        # Reset span runtime state.
        #
        # The span stack is the single source of truth.
        # ------------------------------------------------------------------

        self._span_stack.clear()
        self._current_span = None
        self._active_span_count = 0

        # ------------------------------------------------------------------
        # Build trace attributes.
        # ------------------------------------------------------------------

        trace_attributes: dict[str, Any] = dict(
            attributes or {}
        )
        trace_attributes.update(extra_attributes)

        # ------------------------------------------------------------------
        # Sampling decision
        # ------------------------------------------------------------------

        if not self.should_sample():
            raise RuntimeError(
                "Trace rejected by sampler."
            )

        # ------------------------------------------------------------------
        # Construct trace.
        # ------------------------------------------------------------------

        trace_kwargs: dict[str, Any] = {
            "name": trace_name,
        }

        # --------------------------------------------------------------
        # Merge metadata into trace attributes.
        #
        # Trace currently exposes a single public attribute namespace.
        # Therefore metadata must not be passed as a separate constructor
        # argument.
        # --------------------------------------------------------------

        if metadata is not None:
            trace_attributes.update(dict(metadata))

        if trace_attributes:
            trace_kwargs["attributes"] = trace_attributes

        trace = Trace(**trace_kwargs)

        # ------------------------------------------------------------------
        # Start lifecycle.
        # ------------------------------------------------------------------

        start = getattr(trace, "start", None)

        if callable(start):
            start()

        # ------------------------------------------------------------------
        # Register trace.
        # ------------------------------------------------------------------

        self.register_trace(trace)

        self._trace = trace
        self._active = True

        # ------------------------------------------------------------------
        # Establish current context.
        # ------------------------------------------------------------------

        trace_id = self._trace_id(trace)

        self._context = TraceContext(
            trace_id=trace_id,
            span_id=None,
            parent_span_id=None,
        )

        self._notify_processors(
            "on_trace_start",
            trace,
        )

        # ------------------------------------------------------------------
        # Manager lifecycle timestamp.
        # ------------------------------------------------------------------

        if self._started_at is None:
            self._started_at = time.time()

        return trace


    def finish_trace(
        self,
        trace: Optional[Trace] = None,
        *,
        status: Any = None,
        **kwargs: Any,
    ) -> Optional[Trace]:
        """
        Finish an active trace.

        Lifecycle:

            _active_traces
                ↓
            finish active spans
                ↓
            trace.finish()
                ↓
            unregister_trace()
                ↓
            _completed_traces

        Invariants
        ----------
        * A trace must leave _active_traces before becoming completed.
        * unregister_trace() is the single registry transition authority.
        * _completed_trace_count always equals
        len(_completed_traces).
        * The current trace is cleared after successful completion.
        """

        # ------------------------------------------------------------------
        # 1. Manager lifecycle guard
        # ------------------------------------------------------------------

        if self._frozen:
            raise RuntimeError(
                "Cannot finish a trace on a frozen TraceManager."
            )

        # ------------------------------------------------------------------
        # 2. Resolve target
        # ------------------------------------------------------------------

        target = (
            trace
            if trace is not None
            else self._trace
        )

        if target is None:
            return None

        # ------------------------------------------------------------------
        # 3. Resolve trace identity
        # ------------------------------------------------------------------

        trace_id = self._trace_id(target)

        # ------------------------------------------------------------------
        # 4. Target must be active
        # ------------------------------------------------------------------

        active = self._active_traces.get(
            trace_id
        )

        if active is None:

            # --------------------------------------------------------------
            # Idempotent behavior for an already completed trace.
            # --------------------------------------------------------------

            completed = self._completed_traces.get(
                trace_id
            )

            if completed is not None:

                if self._trace is target:
                    self._trace = None

                return completed

            raise ValueError(
                f"Trace {trace_id!r} is not registered as active."
            )

        # Always operate on the registry-owned object.
        target = active

        # ------------------------------------------------------------------
        # 5. Finish active spans belonging to this trace
        # ------------------------------------------------------------------

        spans_to_finish = [
            span
            for span in reversed(self._span_stack)
            if (
                getattr(span, "trace_id", None)
                == trace_id
            )
            or (
                getattr(span, "trace", None)
                is target
            )
        ]

        for span in spans_to_finish:
            self._finish_span_for_trace(
                span
            )

        # ------------------------------------------------------------------
        # 6. Defensive span-state cleanup
        # ------------------------------------------------------------------

        if self._trace is target:

            self._current_span = None

            self._span_stack.clear()

            self._active_span_count = 0

        # ------------------------------------------------------------------
        # 7. Finish Trace lifecycle
        # ------------------------------------------------------------------

        finish = getattr(
            target,
            "finish",
            None,
        )

        if callable(finish):

            if status is None:
                finish(**kwargs)

            else:
                finish(
                    status=status,
                    **kwargs,
                )

        else:

            # Compatibility fallback.
            if hasattr(target, "state"):

                try:
                    target.state = "finished"

                except (
                    AttributeError,
                    TypeError,
                ):
                    pass

        # ------------------------------------------------------------------
        # 8. ACTIVE -> COMPLETED
        #
        # unregister_trace() is the ONLY registry transition.
        # ------------------------------------------------------------------

        completed = self.unregister_trace(
            target
        )

        if completed is None:
            raise RuntimeError(
                f"Failed to complete trace {trace_id!r}."
            )

        target = completed

        # ------------------------------------------------------------------
        # 9. Processor notification
        # ------------------------------------------------------------------

        self._notify_processors(
            "on_trace_end",
            target,
        )

        # ------------------------------------------------------------------
        # 10. Export
        # ------------------------------------------------------------------

        for exporter in self._exporters:

            callback = getattr(
                exporter,
                "export_trace",
                None,
            )

            if not callable(callback):
                continue

            try:

                callback(target)

                self._exported_count += 1

            except Exception:

                self._error_count += 1

                raise

        # ------------------------------------------------------------------
        # 11. Clear current trace
        # ------------------------------------------------------------------

        if self._trace is target:
            self._trace = None

        self._current_span = None

        self._span_stack.clear()

        self._active_span_count = 0

        self._context = None

        self._active = bool(
            self._active_traces
        )

        self._stopped_at = time.time()

        # ------------------------------------------------------------------
        # 12. Re-establish derived counter invariant
        # ------------------------------------------------------------------

        self._completed_trace_count = len(
            self._completed_traces
        )

        return target

    def cancel_trace(self) -> Optional[Trace]:
        """
        Cancel the current active trace.

        Active spans are cancelled from child to parent before
        cancelling the trace itself.

        The cancelled trace is moved from the active registry to
        the completed registry. The manager remains reusable.
        """

        trace = self._trace

        if trace is None:
            return None

        try:
            # ----------------------------------------------------------
            # Cancel active spans child -> parent
            # ----------------------------------------------------------

            while self._span_stack:
                self.cancel_span()

            # ----------------------------------------------------------
            # Cancel trace
            # ----------------------------------------------------------

            cancel = getattr(trace, "cancel", None)

            if callable(cancel):
                cancel()

            self._cancelled_trace_count += 1

            # ----------------------------------------------------------
            # Move active trace -> completed registry.
            #
            # unregister_trace() is the single registry transition
            # authority:
            #
            #     _active_traces
            #           ↓
            #     unregister_trace()
            #           ↓
            #     _completed_traces
            #
            # It also maintains:
            #
            #     _completed_trace_count
            #         == len(_completed_traces)
            # ----------------------------------------------------------

            completed = self.unregister_trace(trace)

            if completed is None:
                raise RuntimeError(
                    f"Failed to cancel trace "
                    f"{self._trace_id(trace)!r}."
                )

            return completed

        finally:
            # ----------------------------------------------------------
            # Clear current runtime state
            # ----------------------------------------------------------

            self._trace = None
            self._current_span = None
            self._span_stack.clear()

            self._active_span_count = 0

            # ----------------------------------------------------------
            # Trace context is no longer active
            # ----------------------------------------------------------

            self._context = None

            # ----------------------------------------------------------
            # Manager remains reusable
            # ----------------------------------------------------------

            self._active = False



    # ==================================================================
    # Part 6. Span Lifecycle
    # ==================================================================

    def start_span(
        self,
        name: str = "Span",
        *,
        parent: Optional[Span] = None,
        trace: Optional[Trace] = None,
        component: str | None = None,
        task_id: str | None = None,
        kind: str = "internal",
        status: str = "unset",
        attributes: Mapping[str, Any] | None = None,
        metadata: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> Span | None:
        """
        Create and start a span on an active trace.

        The span stack is the canonical source of active-span state.
        Current span, active-span count, and trace context are derived
        through ``_sync_current_span()``.
        """

        # --------------------------------------------------------------
        # Manager state
        # --------------------------------------------------------------

        if not self._enabled:
            return None

        if not isinstance(name, str):
            raise TypeError("span name must be a string")

        name = name.strip()

        if not name:
            raise ValueError("span name cannot be empty")

        # --------------------------------------------------------------
        # Resolve trace
        #
        # Explicit trace takes precedence. Otherwise use the manager's
        # currently active trace.
        # --------------------------------------------------------------

        target_trace = trace if trace is not None else self._trace

        if target_trace is None:
            raise RuntimeError(
                "cannot start span without an active trace"
            )

        # --------------------------------------------------------------
        # Resolve parent
        #
        # Explicit parent takes precedence. Otherwise the current span
        # becomes the parent for nested spans.
        # --------------------------------------------------------------

        target_parent = (
            parent
            if parent is not None
            else self.current_span
        )

        # --------------------------------------------------------------
        # Resolve identifiers
        # --------------------------------------------------------------

        trace_id = getattr(
            target_trace,
            "trace_id",
            getattr(target_trace, "id", None),
        )

        parent_span_id = None

        if target_parent is not None:
            parent_span_id = getattr(
                target_parent,
                "span_id",
                getattr(target_parent, "id", None),
            )

        # --------------------------------------------------------------
        # Merge attributes
        #
        # Explicit ``attributes`` and ``metadata`` are kept separate
        # semantically, but metadata is folded into the span attributes
        # because Span currently receives one attributes mapping.
        # --------------------------------------------------------------

        span_attributes: dict[str, Any] = {}

        if attributes is not None:
            span_attributes.update(attributes)

        if metadata is not None:
            span_attributes.update(metadata)

        if kwargs:
            span_attributes.update(kwargs)

        # --------------------------------------------------------------
        # Construct span
        # --------------------------------------------------------------

        span_kwargs: dict[str, Any] = {
            "name": name,
            "component": component,
            "task_id": task_id,
            "kind": kind,
            "status": status,
            "attributes": span_attributes or None,
        }

        if parent_span_id is not None:
            span_kwargs["parent_id"] = parent_span_id

        if trace_id is not None:
            span_kwargs["trace_id"] = trace_id

        span = Span(**span_kwargs)

        # --------------------------------------------------------------
        # Start lifecycle
        # --------------------------------------------------------------

        if not bool(getattr(span, "running", False)):
            start = getattr(span, "start", None)

            if callable(start):
                start()

        # --------------------------------------------------------------
        # Register with owning trace
        # --------------------------------------------------------------

        add_span = getattr(
            target_trace,
            "add_span",
            None,
        )

        if not callable(add_span):
            raise RuntimeError(
                "active trace does not support span registration"
            )

        add_span(span)

        # --------------------------------------------------------------
        # Register with manager
        #
        # _span_stack is the canonical active-span state.
        # --------------------------------------------------------------

        self._spans.append(span)
        self._span_stack.append(span)

        self._span_count += 1

        # --------------------------------------------------------------
        # Rebuild derived state
        # --------------------------------------------------------------

        self._sync_current_span()

        # --------------------------------------------------------------
        # Notify processors
        # --------------------------------------------------------------

        self._notify_processors(
            "on_span_start",
            span,
        )

        return span


    def finish_span(self) -> Optional[Span]:
        """
        Finish the current span, export it, and restore its parent.

        The span remains in ``_spans`` as historical state but is removed
        from ``_span_stack`` because it is no longer active.
        """

        span = self.current_span

        if span is None:
            return None

        finished_now = False

        try:
            # ----------------------------------------------------------
            # Determine lifecycle state
            # ----------------------------------------------------------

            already_finished = bool(
                getattr(
                    span,
                    "finished",
                    False,
                )
            )

            if not already_finished:
                is_finished = getattr(
                    span,
                    "is_finished",
                    None,
                )

                if callable(is_finished):
                    already_finished = bool(
                        is_finished()
                    )

            # ----------------------------------------------------------
            # Finish lifecycle
            # ----------------------------------------------------------

            if not already_finished:
                finish = getattr(
                    span,
                    "finish",
                    None,
                )

                if callable(finish):
                    finish()

                finished_now = True

            # ----------------------------------------------------------
            # Completed-span accounting
            #
            # Do not increment repeatedly if finish_span() is called
            # against an already-finished span.
            # ----------------------------------------------------------

            if finished_now:
                self._completed_span_count += 1

                # ------------------------------------------------------
                # Export completed span
                # ------------------------------------------------------

                self.export_span(span)

                # ------------------------------------------------------
                # Notify processors
                # ------------------------------------------------------

                self._notify_processors(
                    "on_span_end",
                    span,
                )

            return span

        finally:
            # ----------------------------------------------------------
            # Remove from active span stack
            # ----------------------------------------------------------

            if (
                self._span_stack
                and self._span_stack[-1] is span
            ):
                self._span_stack.pop()

            else:
                try:
                    self._span_stack.remove(span)
                except ValueError:
                    pass

            # ----------------------------------------------------------
            # Rebuild current span, active count and context
            # ----------------------------------------------------------

            self._sync_current_span()


    def cancel_span(
        self,
        span: Optional[Span] = None,
    ) -> "TraceManager":
        """
        Cancel an active span.

        The cancelled span is removed from the active span stack but
        remains in ``_spans`` as historical state.
        """

        # --------------------------------------------------------------
        # Resolve target
        # --------------------------------------------------------------

        if span is None:
            if not self._span_stack:
                return self

            span = self._span_stack[-1]

        # --------------------------------------------------------------
        # Cancel lifecycle
        # --------------------------------------------------------------

        try:
            cancel = getattr(
                span,
                "cancel",
                None,
            )

            if callable(cancel):
                cancel()

            else:
                # ------------------------------------------------------
                # Fallback: finish lifecycle if Span has no cancel()
                # ------------------------------------------------------

                finish = getattr(
                    span,
                    "finish",
                    None,
                )

                if callable(finish):
                    finish()

                else:
                    # --------------------------------------------------
                    # Last-resort state mutation
                    # --------------------------------------------------

                    try:
                        span.status = "cancelled"
                    except Exception:
                        pass

                    try:
                        span.finished = True
                    except Exception:
                        pass

        finally:
            # ----------------------------------------------------------
            # Remove cancelled span from active stack
            # ----------------------------------------------------------

            if self._span_stack:
                if self._span_stack[-1] is span:
                    self._span_stack.pop()

                else:
                    try:
                        self._span_stack.remove(span)
                    except ValueError:
                        pass

            # ----------------------------------------------------------
            # Rebuild all derived state
            # ----------------------------------------------------------

            self._sync_current_span()

        return self


    def enter_span(
        self,
        name: str,
        *,
        parent: Optional[Span] = None,
        trace: Optional[Trace] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Optional[Span]:
        """Enter and activate a span."""

        if trace is not None:
            previous_trace = self._trace
            self._trace = trace
        else:
            previous_trace = None

        try:
            span = self.start_span(
                name,
                attributes=metadata,
            )

            if span is not None and parent is not None:
                # ``start_span`` normally derives the parent from
                # ``current_span``. Explicit parent overrides that
                # relationship when requested.
                try:
                    span.parent_id = getattr(
                        parent,
                        "span_id",
                        getattr(parent, "id", None),
                    )
                except Exception:
                    pass

            return span

        finally:
            if trace is not None and previous_trace is not None:
                self._trace = previous_trace


    def exit_span(
        self,
        *,
        cancel: bool = False,
    ) -> Optional[Span]:
        """
        Exit the current span.

        ``cancel=True`` cancels the current span; otherwise the span
        is normally finished.
        """

        if cancel:
            span = (
                self.current_span
                if self.current_span is not None
                else None
            )

            if span is None:
                return None

            self.cancel_span(span)
            return span

        return self.finish_span()


    # ==================================================================
    # Part 7. Span Management
    # ==================================================================

    def clear_current(self) -> "TraceManager":
        """
        Clear the current runtime trace/span context.

        This operation detaches the manager from the currently active
        execution context without deleting trace or span history.

        Persistent registries such as ``_spans`` remain unchanged.
        """

        self._trace = None
        self._span_stack.clear()

        # Rebuild all derived span/context state from the now-empty stack.
        self._sync_current_span()

        self._active = False

        return self

    def push_span(
        self,
        span: Span,
    ) -> Span:
        """
        Push an existing span onto the active span stack.

        The span is not added to ``_spans`` automatically if it is
        already registered. Registration and activation are separate
        responsibilities.
        """

        if span is None:
            raise TypeError("span cannot be None")

        if not isinstance(span, Span):
            raise TypeError(
                "span must be a Span instance"
            )

        # Register the span in history if necessary.
        if span not in self._spans:
            self._spans.append(span)

        # Prevent duplicate activation of the same span.
        if span in self._span_stack:
            raise ValueError(
                "span is already active"
            )

        self._span_stack.append(span)

        # Rebuild all derived state.
        self._sync_current_span()

        self._active = True

        return span

    def pop_span(self) -> Optional[Span]:
        """
        Pop and return the current active span.

        The span remains in ``_spans`` history.
        """

        if not self._span_stack:
            self._sync_current_span()
            return None

        span = self._span_stack.pop()

        # Restore parent/current span and context.
        self._sync_current_span()

        return span

    def _sync_current_span(self) -> None:
        """
        Synchronize all derived span runtime state.

        ``_span_stack`` is the single source of truth for active spans.

        Derived state maintained here:

        - ``_current_span``
        - ``_active_span_count``
        - ``_context``

        This method must be used whenever the active span stack changes.
        """

        # --------------------------------------------------------------
        # Current span
        # --------------------------------------------------------------

        self._current_span = (
            self._span_stack[-1]
            if self._span_stack
            else None
        )

        # --------------------------------------------------------------
        # Active span count
        # --------------------------------------------------------------

        self._active_span_count = len(
            self._span_stack
        )

        # --------------------------------------------------------------
        # No active span
        # --------------------------------------------------------------

        if self._current_span is None:
            self._context = None
            return

        # --------------------------------------------------------------
        # Resolve trace id
        # --------------------------------------------------------------

        trace_id = None

        if self._trace is not None:
            trace_id = getattr(
                self._trace,
                "trace_id",
                getattr(
                    self._trace,
                    "id",
                    None,
                ),
            )

        # --------------------------------------------------------------
        # Resolve current span id
        # --------------------------------------------------------------

        span_id = getattr(
            self._current_span,
            "span_id",
            getattr(
                self._current_span,
                "id",
                None,
            ),
        )

        # --------------------------------------------------------------
        # Resolve parent span id
        # --------------------------------------------------------------

        parent_span_id = getattr(
            self._current_span,
            "parent_span_id",
            getattr(
                self._current_span,
                "parent_id",
                None,
            ),
        )

        # --------------------------------------------------------------
        # Rebuild trace context
        # --------------------------------------------------------------

        self._context = TraceContext(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
        )

    def get_span(
        self,
        span_id: Optional[str] = None,
    ) -> Optional[Span]:
        """
        Get a span by id.

        If ``span_id`` is omitted, return the current active span.
        """

        if span_id is None:
            return self._current_span

        key = str(span_id)

        # Search newest spans first.
        for span in reversed(self._spans):
            current_id = getattr(
                span,
                "span_id",
                getattr(
                    span,
                    "id",
                    None,
                ),
            )

            if current_id is not None and str(current_id) == key:
                return span

        return None

    def find_span(
        self,
        span_id: Optional[str] = None,
        *,
        name: Optional[str] = None,
    ) -> Optional[Span]:
        """
        Find a span by id or name.

        Span id takes precedence when both arguments are supplied.
        """

        if span_id is not None:
            return self.get_span(span_id)

        if name is not None:
            for span in reversed(self._spans):
                if getattr(span, "name", None) == name:
                    return span

        return None

    def add_span(
        self,
        span: Span,
    ) -> Span:
        """
        Register an existing span in manager history.

        Registration does not activate the span. Use ``push_span()``
        when the span should become part of the active span stack.
        """

        if span is None:
            raise TypeError("span cannot be None")

        if not isinstance(span, Span):
            raise TypeError(
                "span must be a Span instance"
            )

        if span not in self._spans:
            self._spans.append(span)

        return span

    def remove_span(
        self,
        span: Span | str,
    ) -> Optional[Span]:
        """
        Remove a span from manager state.

        The span is removed from both:

        - persistent span registry
        - active span stack

        The underlying ``Trace`` object is not modified here.
        """

        # --------------------------------------------------------------
        # Resolve target
        # --------------------------------------------------------------

        if isinstance(span, str):
            target = self.get_span(span)
        else:
            target = span

        if target is None:
            return None

        # --------------------------------------------------------------
        # Remove from active stack
        # --------------------------------------------------------------

        self._span_stack = [
            active_span
            for active_span in self._span_stack
            if active_span is not target
        ]

        # --------------------------------------------------------------
        # Remove from registry
        # --------------------------------------------------------------

        self._spans = [
            registered_span
            for registered_span in self._spans
            if registered_span is not target
        ]

        # --------------------------------------------------------------
        # Rebuild derived runtime state
        # --------------------------------------------------------------

        self._sync_current_span()

        # --------------------------------------------------------------
        # Runtime active state
        # --------------------------------------------------------------

        if self._trace is None and not self._span_stack:
            self._active = False

        return target


    # ==================================================================
    # Part 8. Context Management
    # ==================================================================

    def context(self) -> Optional[TraceContext]:
        """Return the current trace context."""
        return self._context

    def current_context(self) -> Optional[TraceContext]:
        """Return the current trace context.

        This is the explicit accessor used by runtime/plugin integrations.
        """
        return self._context

    def set_context(
        self,
        context: Optional[TraceContext],
    ) -> "TraceManager":
        """
        Replace the current trace context.

        Parameters
        ----------
        context:
            A TraceContext instance or None.

        Returns
        -------
        TraceManager
            This manager instance.
        """

        if context is not None and not isinstance(
            context,
            TraceContext,
        ):
            raise TypeError(
                "context must be a TraceContext or None"
            )

        self._context = context

        return self

    def update_context(
        self,
        **updates: Any,
    ) -> "TraceManager":
        """
        Update the current tracing context.

        Context updates are applied to the existing context whenever
        possible. If no context exists but an active trace exists, a new
        context is created from the current trace/span identity.

        Unknown keys are stored as context attributes.
        """

        # --------------------------------------------------------------
        # No active trace
        # --------------------------------------------------------------

        if self._trace is None:
            return self

        # --------------------------------------------------------------
        # Resolve trace identity
        # --------------------------------------------------------------

        trace_id = getattr(
            self._trace,
            "trace_id",
            getattr(
                self._trace,
                "id",
                None,
            ),
        )

        # --------------------------------------------------------------
        # Resolve span identity
        # --------------------------------------------------------------

        span_id = None

        if self._current_span is not None:
            span_id = getattr(
                self._current_span,
                "span_id",
                getattr(
                    self._current_span,
                    "id",
                    None,
                ),
            )

        # --------------------------------------------------------------
        # Create context if necessary
        # --------------------------------------------------------------

        current = self._context

        if current is None:
            current = TraceContext(
                trace_id=trace_id,
                span_id=span_id,
            )

        # --------------------------------------------------------------
        # Apply updates
        # --------------------------------------------------------------

        for key, value in updates.items():

            if not isinstance(key, str):
                raise TypeError(
                    "context update keys must be strings"
                )

            # ----------------------------------------------------------
            # Writable property
            # ----------------------------------------------------------

            descriptor = getattr(
                type(current),
                key,
                None,
            )

            if isinstance(
                descriptor,
                property,
            ):
                if descriptor.fset is not None:
                    descriptor.fset(
                        current,
                        value,
                    )
                else:
                    setter = getattr(
                        current,
                        "set_attribute",
                        None,
                    )

                    if callable(setter):
                        setter(
                            key,
                            value,
                        )
                    else:
                        raise AttributeError(
                            f"TraceContext attribute {key!r} "
                            "is read-only"
                        )

            # ----------------------------------------------------------
            # Normal attribute
            # ----------------------------------------------------------

            elif hasattr(current, key):
                setattr(
                    current,
                    key,
                    value,
                )

            # ----------------------------------------------------------
            # Arbitrary context attribute
            # ----------------------------------------------------------

            else:
                setter = getattr(
                    current,
                    "set_attribute",
                    None,
                )

                if callable(setter):
                    setter(
                        key,
                        value,
                    )
                else:
                    raise AttributeError(
                        f"TraceContext does not support "
                        f"attribute {key!r}"
                    )

            # ----------------------------------------------------------
            # Processor notification
            #
            # IMPORTANT:
            # Notify only after the mutation succeeds.
            # ----------------------------------------------------------

            self._notify_processors(
                "on_attribute",
                current,
                key,
                value,
            )

        self._context = current

        return self

    def clear_context(self) -> "TraceManager":
        """Clear the current trace context."""

        self._context = None

        return self

    # ==================================================================
    # Span Status / Exception
    # ==================================================================

    def set_status(
        self,
        status: str,
        description: str | None = None,
    ) -> "TraceManager":
        """
        Set status on the current span and notify processors.
        """

        span = self.current_span

        if span is None:
            raise RuntimeError(
                "cannot set status without an active span"
            )

        if not isinstance(status, str):
            raise TypeError(
                "status must be a string"
            )

        status = status.strip()

        if not status:
            raise ValueError(
                "status cannot be empty"
            )

        span.set_status(
            status,
            description,
        )

        self._notify_processors(
            "on_status_change",
            span,
            status,
            description,
        )

        return self


    def record_exception(
        self,
        exc: BaseException,
        *,
        escaped: bool = False,
    ) -> Event:
        """
        Record an exception as a first-class tracing Event on the
        currently active span.

        Exception recording is strictly span-scoped:

        1. An active span is required.
        2. The exception is recorded on that active span.
        3. If no active span exists, recording fails immediately.

        The exception is always represented as a canonical ``Event`` with
        ``Severity.ERROR``. Native ``record_exception()`` support is preserved
        when available.

        Parameters
        ----------
        exc:
            Exception instance to record.

        escaped:
            Whether the exception escaped the traced operation.

        Returns
        -------
        Event
            The generated exception event.

        Raises
        ------
        TypeError
            If ``exc`` is not a ``BaseException``.

        RuntimeError
            If there is no active span.

        AttributeError
            If the active span does not support event attachment.
        """

        # ------------------------------------------------------------------
        # Validate exception
        # ------------------------------------------------------------------

        if not isinstance(
            exc,
            BaseException,
        ):
            raise TypeError(
                "exc must be a BaseException"
            )

        # ------------------------------------------------------------------
        # Resolve active span
        #
        # Exception events are strictly span-scoped.
        #
        # Do NOT fall back to current_trace here. A trace may exist without
        # an active span, but an exception cannot be attached at trace scope.
        # ------------------------------------------------------------------

        span = self.current_span

        if span is None:
            raise RuntimeError(
                "cannot record exception without "
                "an active span"
            )

        target = span

        # ------------------------------------------------------------------
        # Preserve native exception recording
        #
        # Native span implementations may provide their own exception
        # recorder. Invoke it when available.
        #
        # Recorder failures are intentionally not swallowed: recording an
        # exception is part of the tracing contract.
        # ------------------------------------------------------------------

        recorder = getattr(
            target,
            "record_exception",
            None,
        )

        if callable(recorder):
            recorder(exc)

        # ------------------------------------------------------------------
        # Create canonical exception event
        # ------------------------------------------------------------------

        event = Event(
            name="exception",
            phase="exception",
            severity=Severity.ERROR,
            attributes={
                "exception.type": (
                    exc.__class__.__name__
                ),
                "exception.message": (
                    str(exc)
                ),
                "exception.escaped": (
                    bool(escaped)
                ),
                "exception.scope": "span",
            },
        )

        # ------------------------------------------------------------------
        # Attach event
        #
        # Prefer the public add_event() API. If it is not available, fall
        # back to an events collection when the span exposes one.
        # ------------------------------------------------------------------

        add_event = getattr(
            target,
            "add_event",
            None,
        )

        if callable(add_event):
            add_event(event)

        else:
            events = getattr(
                target,
                "events",
                None,
            )

            if events is None or not hasattr(
                events,
                "append",
            ):
                raise AttributeError(
                    "active span does not support "
                    "add_event() or an events collection"
                )

            events.append(event)

        # ------------------------------------------------------------------
        # Notify processors: canonical event
        # ------------------------------------------------------------------

        self._notify_processors(
            "on_event",
            target,
            event,
        )

        # ------------------------------------------------------------------
        # Notify processors: exception
        # ------------------------------------------------------------------

        self._notify_processors(
            "on_exception",
            target,
            exc,
        )

        return event



    # ==================================================================
    # Processor Management
    # ==================================================================

    def add_processor(
        self,
        processor: Any,
    ) -> "TraceManager":
        """
        Add a processor to the processor pipeline.

        Duplicate processor instances are ignored.
        """

        if processor is None:
            raise TypeError(
                "processor cannot be None"
            )

        if processor not in self._processors:
            self._processors.append(
                processor
            )

        self._processor = (
            self._processors[0]
            if self._processors
            else None
        )

        return self

    def remove_processor(
        self,
        processor: Any,
    ) -> "TraceManager":
        """
        Remove a processor from the processor pipeline.

        Removing a processor that is not registered is idempotent.
        """

        try:
            self._processors.remove(
                processor
            )
        except ValueError:
            return self

        self._processor = (
            self._processors[0]
            if self._processors
            else None
        )

        return self

    def clear_processors(self) -> "TraceManager":
        """Remove all registered processors."""

        self._processors.clear()

        self._processor = None

        return self

    @property
    def processors(self) -> list[Any]:
        """
        Return a snapshot of the registered processors.
        """

        return list(
            self._processors
        )


    # ==================================================================
    # Part 9. Metadata & Attributes
    # ==================================================================

    @property
    def tags(self) -> list[str]:
        """
        Return manager-level tags.

        The collection is intentionally mutable so callers may append
        or remove tags directly.
        """
        return self._tags

    def set_metadata(
        self,
        key: str,
        value: Any,
    ) -> "TraceManager":
        """
        Set one manager-level metadata value.
        """

        if not isinstance(key, str):
            raise TypeError(
                "metadata key must be a string",
            )

        key = key.strip()

        if not key:
            raise ValueError(
                "metadata key cannot be empty",
            )

        self._metadata[key] = value

        return self

    def update_metadata(
        self,
        values: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> "TraceManager":
        """
        Update manager-level metadata.

        ``values`` and keyword arguments are merged into the existing
        metadata dictionary.
        """

        if values is not None:
            if not isinstance(values, dict):
                raise TypeError(
                    "values must be a dictionary",
                )

            for key, value in values.items():
                self.set_metadata(
                    key,
                    value,
                )

        for key, value in kwargs.items():
            self.set_metadata(
                key,
                value,
            )

        return self

    def get_metadata(
        self,
        key: Optional[str] = None,
        default: Any = None,
    ) -> Any:
        """
        Return manager-level metadata.

        When ``key`` is omitted, return a detached copy of all metadata.
        """

        if key is None:
            return copy.deepcopy(
                self._metadata,
            )

        return self._metadata.get(
            key,
            default,
        )

    def update(
        self,
        *,
        metadata: Optional[Mapping[str, Any]] = None,
        **kwargs: Any,
    ) -> "TraceManager":
        """
        Update manager metadata and runtime options.

        ``metadata`` is handled through ``update_metadata()`` so that
        metadata validation remains centralized.

        Other keyword arguments are stored as runtime options.
        """

        if metadata is not None:
            if not isinstance(metadata, Mapping):
                raise TypeError(
                    "metadata must be a mapping",
                )

            self.update_metadata(
                dict(metadata),
            )

        if kwargs:
            self._options.update(
                copy.deepcopy(kwargs),
            )

        return self

    def set_attribute(
        self,
        key: str,
        value: Any,
    ) -> "TraceManager":
        """
        Set an attribute on the current span.

        If no current span exists, the operation is a no-op while
        preserving the fluent manager API.
        """

        if not isinstance(key, str):
            raise TypeError(
                "attribute key must be a string",
            )

        key = key.strip()

        if not key:
            raise ValueError(
                "attribute key cannot be empty",
            )

        span = self.current_span

        if span is None:
            return self

        setter = getattr(
            span,
            "set_attribute",
            None,
        )

        if callable(setter):
            setter(
                key,
                value,
            )
        else:
            attributes = getattr(
                span,
                "attributes",
                None,
            )

            if attributes is None:
                try:
                    span.attributes = {}
                    attributes = span.attributes
                except AttributeError:
                    attributes = None

            if isinstance(attributes, dict):
                attributes[key] = value

        self._notify_processors(
            "on_attribute",
            span,
            key,
            value,
        )

        return self


    def emit(
        self,
        name: str,
        phase: str | ExecutionPhase = ExecutionPhase.RUNNING,
        *,
        severity: Severity = Severity.INFO,
        attributes: Optional[dict[str, Any]] = None,
        metadata: Optional[dict[str, Any]] = None,
        payload: Optional[dict[str, Any]] = None,
        tags: Optional[dict[str, Any]] = None,
        timestamp: Optional[float] = None,
        **kwargs: Any,
    ) -> Event:
        """
        Create and emit an Event on the current span.

        Parameters
        ----------
        name:
            Event name.

        phase:
            Canonical ``ExecutionPhase`` or an extensible string phase.

        severity:
            Event severity.

        attributes:
            Event attributes.

        metadata:
            Event metadata.

        payload:
            Event payload.

        tags:
            Event tags.

        timestamp:
            Optional POSIX timestamp.

        **kwargs:
            Additional attributes.

        Returns
        -------
        Event
            The emitted event.

        Raises
        ------
        RuntimeError
            If there is no active span.
        """

        span = self.current_span

        if span is None:
            raise RuntimeError(
                "cannot emit event without an active span"
            )

        event_attributes = dict(
            attributes or {},
        )

        if kwargs:
            event_attributes.update(
                kwargs,
            )

        event = Event(
            name=name,
            phase=phase,
            severity=severity,
            attributes=event_attributes,
            metadata=dict(
                metadata or {},
            ),
            payload=dict(
                payload or {},
            ),
            tags=dict(
                tags or {},
            ),
        )

        if timestamp is not None:
            event.timestamp = datetime.fromtimestamp(
                timestamp,
                tz=timezone.utc,
            )

        return self.add_event(event)



    def add_event(
        self,
        event: str | Event,
        *,
        attributes: Optional[dict[str, Any]] = None,
        timestamp: Optional[float] = None,
    ) -> Event:
        """
        Add an event to the current span.

        Returns
        -------
        Event
            The exact Event instance attached to the current span.

        Raises
        ------
        RuntimeError
            If there is no active span.
        TypeError
            If ``event`` is neither an Event nor a string.
        ValueError
            If an event name is empty.
        """

        span = self.current_span

        if span is None:
            raise RuntimeError(
                "cannot add event without an active span"
            )

        # ------------------------------------------------------------------
        # Normalize event
        # ------------------------------------------------------------------

        if isinstance(event, Event):
            event_obj = event

            if attributes:
                event_attributes = getattr(
                    event_obj,
                    "attributes",
                    None,
                )

                if isinstance(
                    event_attributes,
                    dict,
                ):
                    event_attributes.update(
                        attributes,
                    )

        elif isinstance(event, str):
            name = event.strip()

            if not name:
                raise ValueError(
                    "event name cannot be empty"
                )

            event_obj = Event(
                name=name,
                attributes=dict(
                    attributes or {},
                ),
            )

            if timestamp is not None:
                event_obj.timestamp = datetime.fromtimestamp(
                    timestamp,
                    tz=timezone.utc,
                )

        else:
            raise TypeError(
                "event must be an Event or string"
            )

        # ------------------------------------------------------------------
        # Attach to span
        # ------------------------------------------------------------------

        add_event_method = getattr(
            span,
            "add_event",
            None,
        )

        if not callable(add_event_method):
            raise AttributeError(
                "current span does not support add_event()"
            )

        add_event_method(event_obj)

        # ------------------------------------------------------------------
        # Notify processors
        # ------------------------------------------------------------------

        self._notify_processors(
            "on_event",
            span,
            event_obj,
        )

        return event_obj



    # ==================================================================
    # Part 10. Processing
    # ==================================================================

    def process_span(
        self,
        span: Optional[Span] = None,
    ) -> Optional[Span]:
        """Process a span through the configured processor."""

        target = span or self._current_span

        if target is None:
            return None

        processor = self._processor

        if processor is None:
            return target

        method = getattr(
            processor,
            "process_span",
            None,
        )

        if callable(method):
            result = method(target)

            self._processed_count += 1

            return target if result is None else result

        method = getattr(
            processor,
            "process",
            None,
        )

        if callable(method):
            result = method(target)

            self._processed_count += 1

            return target if result is None else result

        return target

    def process_trace(
        self,
        trace: Optional[Trace] = None,
    ) -> Optional[Trace]:
        """Process a trace through the configured processor."""

        target = trace or self._trace

        if target is None:
            return None

        processor = self._processor

        if processor is None:
            return target

        method = getattr(
            processor,
            "process_trace",
            None,
        )

        if callable(method):
            result = method(target)

            self._processed_count += 1

            return target if result is None else result

        method = getattr(
            processor,
            "process",
            None,
        )

        if callable(method):
            result = method(target)

            self._processed_count += 1

            return target if result is None else result

        return target

    def process(
        self,
        item: Any = None,
    ) -> Any:
        """
        Generic processing entry point.

        Dispatch Trace and Span to specialized processor APIs.
        """

        if item is None:
            if self._current_span is not None:
                item = self._current_span
            else:
                item = self._trace

        if item is None:
            return None

        if isinstance(item, Span):
            return self.process_span(item)

        if isinstance(item, Trace):
            return self.process_trace(item)

        processor = self._processor

        if processor is None:
            return item

        method = getattr(
            processor,
            "process",
            None,
        )

        if callable(method):
            result = method(item)

            self._processed_count += 1

            return item if result is None else result

        return item

# ============================================================================
# Part 11. Sampling
# ============================================================================

    def should_sample(
        self,
        trace: Optional[Trace] = None,
        *,
        span: Optional[Span] = None,
    ) -> bool:
        """
        Determine whether the current operation should be sampled.
        """
        sampler = self._sampler

        if sampler is None:
            return True

        decision = self.sampling_decision(
            trace=trace,
            span=span,
        )

        if isinstance(decision, bool):
            return decision

        value = getattr(
            decision,
            "sampled",
            None,
        )

        if value is not None:
            return bool(value)

        value = getattr(
            decision,
            "decision",
            None,
        )

        if isinstance(value, bool):
            return value

        return bool(decision)

    def sampling_decision(
        self,
        trace: Optional[Trace] = None,
        *,
        span: Optional[Span] = None,
    ) -> Any:
        """
        Return the sampler's native sampling decision.
        """
        sampler = self._sampler

        if sampler is None:
            return True

        target = trace or self._trace

        method = getattr(
            sampler,
            "should_sample",
            None,
        )

        if callable(method):
            try:
                return method(
                    target,
                    span=span,
                )
            except TypeError:
                try:
                    return method(target)
                except TypeError:
                    return method()

        method = getattr(
            sampler,
            "sample",
            None,
        )

        if callable(method):
            try:
                return method(
                    target,
                    span=span,
                )
            except TypeError:
                try:
                    return method(target)
                except TypeError:
                    return method()

        method = getattr(
            sampler,
            "decide",
            None,
        )

        if callable(method):
            try:
                return method(
                    target,
                    span=span,
                )
            except TypeError:
                try:
                    return method(target)
                except TypeError:
                    return method()

        return True

# ============================================================================
# Part 12. Export
# ============================================================================

    def export_span(
        self,
        span: Optional[Span] = None,
    ) -> list[Any]:
        """
        Export a span through all configured exporters.
        """

        target = span or self.current_span

        if target is None:
            return []

        if not self._exporters:
            return []

        results: list[Any] = []

        for exporter in self._exporters:
            method = getattr(
                exporter,
                "export_span",
                None,
            )

            if callable(method):
                results.append(
                    method(target),
                )
                self._exported_count += 1

        return results

    def set_processor(
        self,
        processor: Optional[TraceProcessor],
    ) -> "TraceManager":
        """
        Set or clear the span processor.

        Processors are accepted by capability rather than requiring
        strict inheritance from TraceProcessor.
        """

        if processor is not None:
            if not callable(getattr(processor, "process", None)):
                raise TypeError(
                    "processor must provide a callable process() method",
                )

        self._processor = processor

        return self

    def export(
        self,
        item: Any = None,
    ) -> Any:
        """
        Generic export entry point.
        """

        if not self._exporters:
            return None

        if item is None:
            item = (
                self.current_span
                if self.current_span is not None
                else self._trace
            )

        if item is None:
            return None

        if isinstance(item, Span):
            return self.export_span(item)

        if isinstance(item, Trace):
            return self.export_trace(item)

        results: list[Any] = []

        for exporter in self._exporters:
            method = getattr(
                exporter,
                "export",
                None,
            )

            if callable(method):
                results.append(
                    method(item),
                )
                self._exported_count += 1

        return results

    def export_trace(
        self,
        trace: Optional[Trace] = None,
    ) -> list[Any]:
        """
        Export a trace through all configured exporters.
        """

        target = trace or self._trace

        if target is None:
            return []

        if not self._exporters:
            return []

        results: list[Any] = []

        for exporter in self._exporters:
            method = getattr(
                exporter,
                "export_trace",
                None,
            )

            if callable(method):
                results.append(
                    method(target),
                )
                self._exported_count += 1

        return results

    def flush(self) -> "TraceManager":
        """
        Flush every configured exporter.
        """

        for exporter in self._exporters:
            method = getattr(
                exporter,
                "flush",
                None,
            )

            if callable(method):
                method()

        return self

    def validate_span_stack(self) -> bool:
        """
        Validate internal span-stack invariants.
        """

        if not self._span_stack:
            return self._current_span is None

        current = self._span_stack[-1]

        return self._current_span is current

# ============================================================================
# Part 13. Snapshot
# ============================================================================

    def snapshot(self) -> dict[str, Any]:
        """
        Snapshot current manager runtime state.

        The returned snapshot is fully detached from the live manager
        state and can therefore be safely restored or inspected without
        mutating the manager.
        """

        return {
            # ------------------------------------------------------------------
            # Identity
            # ------------------------------------------------------------------

            "identity": {
                "manager_id": self._manager_id,
                "name": self._name,
                "service_name": self._service_name,
            },

            # ------------------------------------------------------------------
            # Backward-compatible top-level configuration
            # ------------------------------------------------------------------

            "name": self._name,
            "service_name": self._service_name,
            "enabled": self._enabled,

            # ------------------------------------------------------------------
            # Configuration
            # ------------------------------------------------------------------

            "configuration": {
                "enabled": self._enabled,
                "sampler": copy.deepcopy(
                    self._sampler,
                ),
                "processors": copy.deepcopy(
                    self._processors,
                ),
                "exporters": copy.deepcopy(
                    self._exporters,
                ),
            },

            # ------------------------------------------------------------------
            # Lifecycle
            # ------------------------------------------------------------------

            "lifecycle": {
                "initialized": self._initialized,
                "active": self._active,
                "closed": self._closed,
                "frozen": self._frozen,
            },

            "runtime": {
                "active": self._active,
                "initialized": self._initialized,
                "closed": self._closed,
                "frozen": self._frozen,
                "trace": copy.deepcopy(
                    self._trace,
                ),
                "current_span": copy.deepcopy(
                    self._current_span,
                ),
                "span_depth": len(
                    self._span_stack
                ),
            },

            # Backward-compatible lifecycle fields.
            "initialized": self._initialized,
            "active": self._active,
            "closed": self._closed,
            "frozen": self._frozen,

            # ------------------------------------------------------------------
            # Trace state
            # ------------------------------------------------------------------

            "trace": copy.deepcopy(
                self._trace,
            ),

            "traces": copy.deepcopy(
                self._traces,
            ),

            # ------------------------------------------------------------------
            # Trace registries
            # ------------------------------------------------------------------

            "active_traces": copy.deepcopy(
                self._active_traces,
            ),

            "completed_traces": copy.deepcopy(
                self._completed_traces,
            ),

            # ------------------------------------------------------------------
            # Span state
            # ------------------------------------------------------------------

            "current_span": copy.deepcopy(
                self._current_span,
            ),

            "spans": copy.deepcopy(
                self._spans,
            ),

            "span_stack": copy.deepcopy(
                self._span_stack,
            ),

            # ------------------------------------------------------------------
            # Runtime context
            # ------------------------------------------------------------------

            "context": copy.deepcopy(
                self._context,
            ),

            # ------------------------------------------------------------------
            # Metadata / options
            # ------------------------------------------------------------------

            "metadata": copy.deepcopy(
                self._metadata,
            ),

            "options": copy.deepcopy(
                self._options,
            ),

            # ------------------------------------------------------------------
            # Lifecycle timestamps
            # ------------------------------------------------------------------

            "timestamps": {
                "created_at": self._created_at,
                "started_at": self._started_at,
                "stopped_at": self._stopped_at,
            },

            # Backward-compatible timestamp fields.
            "created_at": self._created_at,
            "started_at": self._started_at,
            "stopped_at": self._stopped_at,

            # ------------------------------------------------------------------
            # Statistics
            # ------------------------------------------------------------------

            "statistics": {
                "trace_count": self._trace_count,
                "completed_trace_count": (
                    self._completed_trace_count
                ),
                "cancelled_trace_count": (
                    self._cancelled_trace_count
                ),
                "span_count": self._span_count,
                "completed_span_count": (
                    self._completed_span_count
                ),
                "cancelled_span_count": (
                    self._cancelled_span_count
                ),
                "active_span_count": (
                    len(self._span_stack)
                ),
                "exported_count": self._exported_count,
                "processed_count": self._processed_count,
                "error_count": self._error_count,
            },

            # ------------------------------------------------------------------
            # Diagnostics / events
            # ------------------------------------------------------------------

            "events": copy.deepcopy(
                self._events,
            ),
        }

    def _validate_snapshot(
        self,
        snapshot: Mapping[str, Any],
    ) -> None:
        """
        Validate snapshot structure before restoration.

        Validation is performed before any live manager state is mutated.
        """

        identity = snapshot.get("identity")

        if identity is None:
            return

        if not isinstance(identity, Mapping):
            raise TypeError(
                "snapshot['identity'] must be a mapping",
            )

        for key in ("manager_id", "uuid"):
            value = identity.get(key)

            if value is None:
                continue

            try:
                uuid.UUID(str(value))
            except (
                ValueError,
                AttributeError,
                TypeError,
            ) as exc:
                raise ValueError(
                    f"snapshot identity contains invalid {key}",
                ) from exc


    def restore(
        self,
        snapshot: Mapping[str, Any],
    ) -> "TraceManager":
        """
        Restore manager runtime state from a snapshot.

        The snapshot is validated completely before any live manager
        state is mutated.
        """

        if not isinstance(snapshot, Mapping):
            raise TypeError(
                "snapshot must be a mapping",
            )

        # --------------------------------------------------------------
        # Validate first — never partially restore a corrupted snapshot.
        # --------------------------------------------------------------

        self._validate_snapshot(snapshot)

        # --------------------------------------------------------------
        # Runtime state
        # --------------------------------------------------------------

        self._trace = copy.deepcopy(
            snapshot.get("trace"),
        )

        self._traces = copy.deepcopy(
            snapshot.get("traces", []),
        )

        # --------------------------------------------------------------
        # Span state
        # --------------------------------------------------------------

        self._spans = copy.deepcopy(
            snapshot.get("spans", []),
        )

        self._span_stack = copy.deepcopy(
            snapshot.get("span_stack", []),
        )

        # --------------------------------------------------------------
        # Context
        # --------------------------------------------------------------

        self._context = copy.deepcopy(
            snapshot.get("context"),
        )

        # --------------------------------------------------------------
        # Metadata / tags
        # --------------------------------------------------------------

        self._metadata = copy.deepcopy(
            snapshot.get("metadata", {}),
        )

        self._tags = copy.deepcopy(
            snapshot.get("tags", []),
        )

        # --------------------------------------------------------------
        # Lifecycle
        # --------------------------------------------------------------

        self._active = bool(
            snapshot.get("active", False),
        )

        self._closed = bool(
            snapshot.get("closed", False),
        )

        # --------------------------------------------------------------
        # Statistics
        # --------------------------------------------------------------

        statistics = snapshot.get(
            "statistics",
            {},
        )

        if not isinstance(statistics, Mapping):
            raise TypeError(
                "snapshot['statistics'] must be a mapping",
            )

        self._trace_count = int(
            statistics.get("trace_count", 0),
        )

        self._completed_trace_count = int(
            statistics.get("completed_trace_count", 0),
        )

        self._cancelled_trace_count = int(
            statistics.get("cancelled_trace_count", 0),
        )

        self._span_count = int(
            statistics.get("span_count", 0),
        )

        self._completed_span_count = int(
            statistics.get("completed_span_count", 0),
        )

        self._cancelled_span_count = int(
            statistics.get("cancelled_span_count", 0),
        )

        self._active_span_count = int(
            statistics.get("active_span_count", 0),
        )

        self._exported_count = int(
            statistics.get("exported_count", 0),
        )

        self._processed_count = int(
            statistics.get("processed_count", 0),
        )

        self._error_count = int(
            statistics.get("error_count", 0),
        )

        # --------------------------------------------------------------
        # Diagnostics / events
        # --------------------------------------------------------------

        self._events = copy.deepcopy(
            snapshot.get("events", []),
        )

        # --------------------------------------------------------------
        # Re-establish derived runtime state.
        # --------------------------------------------------------------

        self._sync_current_span()

        return self

    def copy(self) -> "TraceManager":
        """
        Return an independent copy of the manager.
        """
        return copy.deepcopy(self)

    def clone(self) -> "TraceManager":
        """
        Return an independent clone of the manager.

        clone() is intentionally equivalent to copy() at this layer.
        """
        return self.copy()

# ============================================================================
# Part 14. Validation
# ============================================================================

    def validate(self) -> bool:
        if self._trace is None:
            return (
                not self._active
                and self._current_span is None
                and not self._span_stack
                and self._context is None
            )

        if not self._active:
            return False

        return self.validate_span_stack()

    def validate_trace(
        self,
        trace: Optional[Trace] = None,
    ) -> bool:
        target = trace if trace is not None else self._trace

        if target is None:
            return False

        if self._trace is not target:
            return False

        if not self._active:
            return False

        return True

    def validate_span(
        self,
        span: Optional[Span] = None,
    ) -> bool:
        target = span if span is not None else self.current_span

        if target is None:
            return False

        if target not in self._spans:
            return False

        if target not in self._span_stack:
            return False

        return True

    def validate_state(self) -> bool:
        """
        Validate cross-component runtime invariants.
        """
        if self._trace is None:
            if self._span_stack:
                return False

            if self._context is not None:
                return False

            return True

        if not self.validate_span():
            return False

        if self.span_depth != len(self._span_stack):
            return False

        return True

# ============================================================================
# Part 15. Statistics
# ============================================================================

    class _CallableCount(int):
        """
        Integer count compatible with both:

            manager.trace_count
            manager.trace_count()

        This preserves the existing property-style API while remaining
        backward-compatible with the callable statistics API.
        """

        def __call__(self) -> int:
            return int(self)

    @property
    def trace_count(self) -> int:
        """
        Total number of traces created by this manager.
        """
        return self._CallableCount(self._trace_count)

    @property
    def completed_trace_count(self) -> int:
        """
        Total number of completed traces.
        """
        return self._CallableCount(
            self._completed_trace_count,
        )

    @property
    def cancelled_trace_count(self) -> int:
        """
        Total number of cancelled traces.
        """
        return self._CallableCount(
            self._cancelled_trace_count,
        )

    @property
    def span_count(self) -> int:
        """
        Total number of spans created by this manager.
        """
        return self._CallableCount(self._span_count)

    @property
    def completed_span_count(self) -> int:
        """
        Total number of completed spans.
        """
        return self._CallableCount(
            self._completed_span_count,
        )

    @property
    def cancelled_span_count(self) -> int:
        """
        Total number of cancelled spans.
        """
        return self._CallableCount(
            self._cancelled_span_count,
        )

    @property
    def active_span_count(self) -> int:
        """
        Number of spans currently present on the active span stack.
        """
        return self._CallableCount(
            len(self._span_stack),
        )

    @property
    def exported_count(self) -> int:
        """
        Number of successfully exported tracing objects.
        """
        return self._CallableCount(self._exported_count)

    @property
    def processed_count(self) -> int:
        """
        Number of processed tracing objects.
        """
        return self._CallableCount(self._processed_count)

    @property
    def error_count(self) -> int:
        """
        Number of errors observed by the manager.
        """
        return self._CallableCount(self._error_count)

    @property
    def processors(self) -> list[Any]:
        """Return a copy of registered processors."""

        return list(self._processors)
# ============================================================================
# Part 16. Diagnostics
# ============================================================================

    def health(self) -> dict[str, Any]:
        """
        Return a compact health report.
        """
        valid = self.validate()

        return {
            "healthy": valid,
            "valid": valid,
            "enabled": self._enabled,
            "active": self._active,
            "trace_count": self._trace_count,
            "span_count": self._span_count,
            "active_span_count": self._active_span_count,
            "exported_count": self._exported_count,
            "error_count": self._error_count,
        }

    def diagnostics(self) -> dict[str, Any]:
        """
        Return detailed runtime diagnostics.
        """
        return {
            "name": self._name,
            "service_name": self._service_name,
            "enabled": self._enabled,
            "active": self._active,
            "closed": self._closed,
            "statistics": {
                "trace_count": self._trace_count,
                "completed_trace_count": self._completed_trace_count,
                "cancelled_trace_count": self._cancelled_trace_count,
                "span_count": self._span_count,
                "completed_span_count": self._completed_span_count,
                "cancelled_span_count": self._cancelled_span_count,
                "active_span_count": self._active_span_count,
                "exported_count": self._exported_count,
                "processed_count": self._processed_count,
                "error_count": self._error_count,
            },
            "runtime": {
                "span_depth": len(self._span_stack),
                "has_trace": self._trace is not None,
                "has_context": self._context is not None,
            },
            "metadata": dict(self._metadata),
            "events": list(self._events),
        }

    def summary(self) -> dict[str, Any]:
        """
        Return a stable, serialization-friendly summary.
        """
        return {
            "name": self._name,
            "service_name": self._service_name,
            "enabled": self._enabled,
            "active": self._active,
            "trace_count": self._trace_count,
            "span_count": self._span_count,
            "active_span_count": self._active_span_count,
            "exported_count": self._exported_count,
            "error_count": self._error_count,
        }

# ============================================================================
# Part 17. Representation
# ============================================================================

    def _sync_current_span(self) -> None:
        """
        Synchronize current span with the active span stack.

        The span stack is the single source of truth.
        """
        self._current_span = (
            self._span_stack[-1]
            if self._span_stack
            else None
        )

        self._active_span_count = len(
            self._span_stack
        )

    def __repr__(self) -> str:
        return (
            "TraceManager("
            f"name={self._name!r}, "
            f"service_name={self._service_name!r}, "
            f"enabled={self._enabled!r}, "
            f"active={self._active!r}, "
            f"active_traces={self.active_trace_count!r}, "
            f"completed={self.completed_trace_count!r}"
            ")"
        )

    def __str__(self) -> str:
        return (
            "TraceManager("
            f"name={self._name!r}, "
            f"service={self._service_name!r}, "
            f"active={self._active!r}, "
            f"active_traces={self.active_trace_count!r}, "
            f"completed={self.completed_trace_count!r}"
            ")"
        )

# ============================================================================
# Part 18. End
# ============================================================================


__all__ = [
    "TraceManager",
]                
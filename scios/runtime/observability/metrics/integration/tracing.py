"""
SciOS-NG Metrics Tracing Integration

scios/runtime/observability/metrics/integration/tracing.py
"""

from __future__ import annotations

import copy
import time
import uuid

from datetime import datetime
from threading import RLock
from typing import Any, Optional


class MetricTracingIntegration:
    """
    Distributed tracing integration for SciOS-NG.

    Responsible for:

    - Trace lifecycle
    - Span lifecycle
    - Runtime correlation
    - Distributed tracing
    - Timeline construction
    - Observability integration
    """

    # =====================================================
    # Part 1. Foundation
    # =====================================================

    def __init__(
        self,
        name: str = "MetricTracingIntegration",
        config: Optional[dict[str, Any]] = None,
    ):

        self._lock = RLock()

        # -------------------------------------------------
        # Identity
        # -------------------------------------------------

        self._id = str(uuid.uuid4())

        self._name = name

        self._version = "0.1.0"

        # -------------------------------------------------
        # Runtime State
        # -------------------------------------------------

        self._enabled = True

        self._running = False

        self._frozen = False

        self._closed = False

        # -------------------------------------------------
        # Trace Configuration
        # -------------------------------------------------

        self._config = config or {

            "enabled": True,

            "max_traces": 10000,

            "max_spans": 100000,

            "auto_finish": True,

            "record_attributes": True,

            "record_events": True,

            "record_exceptions": True,

        }

        # -------------------------------------------------
        # Span Registry
        # -------------------------------------------------

        self._trace_registry: dict[str, dict] = {}

        self._span_registry: dict[str, dict] = {}

        self._active_traces: dict[str, dict] = {}

        self._active_spans: dict[str, dict] = {}

        # -------------------------------------------------
        # Metadata
        # -------------------------------------------------

        self._created_at = datetime.utcnow()

        self._updated_at = self._created_at

        self._metadata = {

            "component":
                "metrics.integration.tracing",

            "engine":
                "SciOS-NG",

            "version":
                self._version,

        }

        # -------------------------------------------------
        # Statistics
        # -------------------------------------------------

        self._trace_count = 0

        self._span_count = 0

        self._event_count = 0

        self._error_count = 0

        self._last_latency = 0.0

        self._start_time = time.time()

        # -------------------------------------------------
        # Runtime Containers
        # -------------------------------------------------

        self._snapshot = None

        self._events: list[dict] = []

        self._hooks: dict[str, list] = {}

        self._handlers: dict[str, dict] = {}
    # =====================================================
    # Part 2. Tracing API
    # =====================================================

    def start_trace(
        self,
        name: str,
        **attributes,
    ) -> dict:
        """
        Start a new trace.
        """

        start = time.perf_counter()

        trace_id = str(uuid.uuid4())

        trace = {

            "trace_id": trace_id,

            "name": name,

            "attributes": dict(attributes),

            "status": "running",

            "start_time": datetime.utcnow(),

            "end_time": None,

            "duration": None,

            "spans": [],

        }

        with self._lock:

            self._trace_registry[trace_id] = trace

            self._active_traces[trace_id] = trace

            self._trace_count += 1

            self._updated_at = datetime.utcnow()

        self._last_latency = (
            time.perf_counter() - start
        )

        return trace



    def end_trace(
        self,
        trace_id: str,
    ) -> dict | None:
        """
        Finish an existing trace.
        """

        start = time.perf_counter()

        with self._lock:

            trace = self._trace_registry.get(
                trace_id
            )

            if trace is None:

                return None

            if trace["end_time"] is None:

                trace["end_time"] = datetime.utcnow()

                trace["duration"] = (

                    trace["end_time"]

                    -

                    trace["start_time"]

                ).total_seconds()

                trace["status"] = "finished"

            self._active_traces.pop(
                trace_id,
                None,
            )

            self._updated_at = datetime.utcnow()

        self._last_latency = (
            time.perf_counter() - start
        )

        return trace



    def start_span(
        self,
        trace_id: str,
        name: str,
        parent_span: str | None = None,
        **attributes,
    ) -> dict:
        """
        Start a span belonging to a trace.
        """

        start = time.perf_counter()

        if trace_id not in self._trace_registry:

            raise KeyError(
                f"Unknown trace: {trace_id}"
            )

        span_id = str(uuid.uuid4())

        span = {

            "span_id": span_id,

            "trace_id": trace_id,

            "parent_span": parent_span,

            "name": name,

            "attributes": dict(attributes),

            "status": "running",

            "start_time": datetime.utcnow(),

            "end_time": None,

            "duration": None,

        }

        with self._lock:

            self._span_registry[span_id] = span

            self._active_spans[span_id] = span

            self._trace_registry[trace_id][
                "spans"
            ].append(span_id)

            self._span_count += 1

            self._updated_at = datetime.utcnow()

        self._last_latency = (
            time.perf_counter() - start
        )

        return span



    def end_span(
        self,
        span_id: str,
    ) -> dict | None:
        """
        Finish an active span.
        """

        start = time.perf_counter()

        with self._lock:

            span = self._span_registry.get(
                span_id
            )

            if span is None:

                return None

            if span["end_time"] is None:

                span["end_time"] = datetime.utcnow()

                span["duration"] = (

                    span["end_time"]

                    -

                    span["start_time"]

                ).total_seconds()

                span["status"] = "finished"

            self._active_spans.pop(
                span_id,
                None,
            )

            self._updated_at = datetime.utcnow()

        self._last_latency = (
            time.perf_counter() - start
        )

        return span



    def current_trace(
        self,
    ) -> dict | None:
        """
        Return the latest active trace.
        """

        if not self._active_traces:

            return None

        return next(

            reversed(

                list(
                    self._active_traces.values()
                )

            )

        )



    def current_span(
        self,
    ) -> dict | None:
        """
        Return the latest active span.
        """

        if not self._active_spans:

            return None

        return next(

            reversed(

                list(
                    self._active_spans.values()
                )

            )

        )



    def trace(
        self,
        trace_id: str,
        default=None,
    ):
        """
        Lookup a trace.
        """

        return self._trace_registry.get(
            trace_id,
            default,
        )



    def span(
        self,
        span_id: str,
        default=None,
    ):
        """
        Lookup a span.
        """

        return self._span_registry.get(
            span_id,
            default,
        )
    # =====================================================
    # Part 3. Span Handlers
    # =====================================================

    def add_handler(
        self,
        name: str,
        handler,
        *,
        enabled: bool = True,
        metadata: dict | None = None,
    ):
        """
        Register span handler.

        Examples
        --------
        - ConsoleHandler
        - OpenTelemetryHandler
        - JaegerHandler
        - ZipkinHandler
        - RuntimeHandler
        """

        if not callable(handler):

            raise TypeError(
                "Handler must be callable."
            )

        with self._lock:

            self._handlers[name] = {

                "name":
                    name,

                "handler":
                    handler,

                "enabled":
                    enabled,

                "metadata":
                    metadata or {},

                "created_at":
                    datetime.utcnow(),

            }

            self._updated_at = datetime.utcnow()

        return self



    def remove_handler(
        self,
        name: str,
    ):
        """
        Remove span handler.
        """

        with self._lock:

            self._handlers.pop(
                name,
                None,
            )

            self._updated_at = datetime.utcnow()

        return self



    def handler(
        self,
        name: str,
        default=None,
    ):
        """
        Return handler object.
        """

        entry = self._handlers.get(
            name
        )

        if entry is None:

            return default

        return entry["handler"]



    def handlers(
        self,
    ):
        """
        Return all registered handlers.
        """

        return dict(
            self._handlers
        )



    def emit_handler(
        self,
        name: str,
        payload: dict,
    ):
        """
        Execute one span handler.
        """

        entry = self._handlers.get(
            name
        )

        if entry is None:

            raise KeyError(
                f"Unknown handler: {name}"
            )

        if not entry["enabled"]:

            return None

        return entry["handler"](
            payload
        )



    def enable_handler(
        self,
        name: str,
    ):
        """
        Enable handler.
        """

        if name in self._handlers:

            self._handlers[name][
                "enabled"
            ] = True

            self._updated_at = datetime.utcnow()

        return self



    def disable_handler(
        self,
        name: str,
    ):
        """
        Disable handler.
        """

        if name in self._handlers:

            self._handlers[name][
                "enabled"
            ] = False

            self._updated_at = datetime.utcnow()

        return self



    def builtin_handlers(
        self,
    ):
        """
        Register builtin tracing handlers.
        """

        # ----------------------------------------------
        # Console Trace Handler
        # ----------------------------------------------

        def console_handler(
            payload: dict,
        ):

            print(

                "[TRACE]",

                payload.get(
                    "name"
                ),

            )


        self.add_handler(

            "console",

            console_handler,

            metadata={

                "type":
                    "stdout",

                "engine":
                    "SciOS-NG",

            },

        )


        # ----------------------------------------------
        # Internal Metrics Handler
        # ----------------------------------------------

        def metrics_handler(
            payload: dict,
        ):

            return {

                "trace":

                    payload.get(
                        "trace_id"
                    ),

                "span":

                    payload.get(
                        "span_id"
                    ),

            }


        self.add_handler(

            "metrics",

            metrics_handler,

            metadata={

                "type":
                    "internal",

                "engine":
                    "Metrics",

            },

        )


        return self
    # =====================================================
    # Part 4. Trace Registry API
    # =====================================================

    def register_trace(
        self,
        name: str,
        trace,
        *,
        enabled: bool = True,
        metadata: dict | None = None,
    ):
        """
        Register a trace backend/object.
        """

        with self._lock:

            if not hasattr(
                self,
                "_registered_traces",
            ):

                self._registered_traces = {}

            self._registered_traces[name] = {

                "name":
                    name,

                "trace":
                    trace,

                "enabled":
                    enabled,

                "metadata":
                    metadata or {},

                "created_at":
                    datetime.utcnow(),

            }

            self._updated_at = datetime.utcnow()

        return self



    def remove_trace(
        self,
        name: str,
    ):
        """
        Remove registered trace.
        """

        with self._lock:

            getattr(
                self,
                "_registered_traces",
                {},
            ).pop(
                name,
                None,
            )

            self._updated_at = datetime.utcnow()

        return self



    def trace_object(
        self,
        name: str,
        default=None,
    ):
        """
        Return registered trace object.
        """

        registry = getattr(
            self,
            "_registered_traces",
            {},
        )

        entry = registry.get(name)

        if entry is None:

            return default

        return entry["trace"]



    def traces(
        self,
    ):
        """
        Return all registered traces.
        """

        return dict(

            getattr(
                self,
                "_registered_traces",
                {},
            )

        )



    def contains_trace(
        self,
        name: str,
    ) -> bool:
        """
        Check whether a trace exists.
        """

        return name in getattr(

            self,

            "_registered_traces",

            {},

        )



    def exists_trace(
        self,
        name: str,
    ) -> bool:
        """
        Alias of contains_trace().
        """

        return self.contains_trace(
            name
        )



    def enable_trace(
        self,
        name: str,
    ):
        """
        Enable registered trace.
        """

        registry = getattr(

            self,

            "_registered_traces",

            {},

        )

        if name in registry:

            registry[name]["enabled"] = True

            self._updated_at = datetime.utcnow()

        return self



    def disable_trace(
        self,
        name: str,
    ):
        """
        Disable registered trace.
        """

        registry = getattr(

            self,

            "_registered_traces",

            {},

        )

        if name in registry:

            registry[name]["enabled"] = False

            self._updated_at = datetime.utcnow()

        return self



    def trace_names(
        self,
    ) -> list[str]:
        """
        Return registered trace names.
        """

        return list(

            getattr(

                self,

                "_registered_traces",

                {},

            ).keys()

        )



    def trace_count(
        self,
    ) -> int:
        """
        Return number of registered traces.
        """

        return len(

            getattr(

                self,

                "_registered_traces",

                {},

            )

        )



    def clear_traces(
        self,
    ):
        """
        Remove all registered traces.
        """

        with self._lock:

            if hasattr(
                self,
                "_registered_traces",
            ):

                self._registered_traces.clear()

            self._updated_at = datetime.utcnow()

        return self



    def execute_trace(
        self,
        name: str,
        *args,
        **kwargs,
    ):
        """
        Execute a registered trace object.

        Supports:
        - callable(...)
        - trace.execute(...)
        - trace.run(...)
        """

        registry = getattr(

            self,

            "_registered_traces",

            {},

        )

        entry = registry.get(name)

        if entry is None:

            raise KeyError(

                f"Unknown trace: {name}"

            )

        if not entry["enabled"]:

            return None

        trace = entry["trace"]


        if callable(trace):

            return trace(
                *args,
                **kwargs,
            )


        execute = getattr(
            trace,
            "execute",
            None,
        )

        if callable(execute):

            return execute(
                *args,
                **kwargs,
            )


        run = getattr(
            trace,
            "run",
            None,
        )

        if callable(run):

            return run(
                *args,
                **kwargs,
            )


        raise TypeError(

            f"Registered trace '{name}' is not executable."

        )
    # =====================================================
    # Part 5. Lifecycle
    # =====================================================

    def enable(
        self,
    ):
        """
        Enable tracing integration.
        """

        with self._lock:

            self._enabled = True

            self._running = True

            self._updated_at = datetime.utcnow()

        return self



    def disable(
        self,
    ):
        """
        Disable tracing integration.

        New traces/spans will not be accepted.
        """

        with self._lock:

            self._enabled = False

            self._running = False

            self._updated_at = datetime.utcnow()

        return self



    def freeze(
        self,
    ):
        """
        Freeze tracing runtime.

        Existing registries remain intact,
        but tracing operations are suspended.
        """

        with self._lock:

            self._frozen = True

            self._running = False

            self._updated_at = datetime.utcnow()

        return self



    def unfreeze(
        self,
    ):
        """
        Resume tracing runtime.
        """

        with self._lock:

            self._frozen = False

            self._running = self._enabled

            self._updated_at = datetime.utcnow()

        return self



    def close(
        self,
    ):
        """
        Close tracing integration.
        """

        with self._lock:

            self._closed = True

            self._enabled = False

            self._running = False

            self._updated_at = datetime.utcnow()

        return self



    def reopen(
        self,
    ):
        """
        Reopen tracing integration.
        """

        with self._lock:

            self._closed = False

            self._enabled = True

            self._running = True

            self._updated_at = datetime.utcnow()

        return self



    @property
    def active(
        self,
    ) -> bool:
        """
        Whether tracing integration
        is currently active.
        """

        return (

            self._enabled

            and

            self._running

            and

            not self._frozen

            and

            not self._closed

        )
    # =====================================================
    # Part 6. Runtime Operations
    # =====================================================

    def reset(
        self,
    ):
        """
        Reset runtime statistics while
        preserving configuration,
        handlers and registered traces.
        """

        with self._lock:

            self._trace_registry.clear()

            self._span_registry.clear()

            self._active_traces.clear()

            self._active_spans.clear()

            self._events.clear()

            self._trace_count = 0

            self._span_count = 0

            self._event_count = 0

            self._error_count = 0

            self._last_latency = 0.0

            self._updated_at = datetime.utcnow()

        return self



    def clear(
        self,
    ):
        """
        Clear collected traces and spans.

        Configuration, handlers and
        registered trace backends are preserved.
        """

        with self._lock:

            self._trace_registry.clear()

            self._span_registry.clear()

            self._active_traces.clear()

            self._active_spans.clear()

            self._updated_at = datetime.utcnow()

        return self



    def snapshot(
        self,
    ) -> dict:
        """
        Create runtime snapshot.
        """

        with self._lock:

            snapshot = {

                "runtime": {

                    "enabled":
                        self._enabled,

                    "running":
                        self._running,

                    "frozen":
                        self._frozen,

                    "closed":
                        self._closed,

                },

                "configuration":

                    copy.deepcopy(
                        self._config
                    ),

                "statistics": {

                    "trace_count":
                        self._trace_count,

                    "span_count":
                        self._span_count,

                    "event_count":
                        self._event_count,

                    "error_count":
                        self._error_count,

                    "latency":
                        self._last_latency,

                },

                "trace_registry":

                    copy.deepcopy(
                        self._trace_registry
                    ),

                "span_registry":

                    copy.deepcopy(
                        self._span_registry
                    ),

                "registered_traces":

                    copy.deepcopy(
                        self._registered_traces
                    ),

                "metadata":

                    copy.deepcopy(
                        self._metadata
                    ),

            }

            self._snapshot = snapshot

            return copy.deepcopy(snapshot)



    def restore(
        self,
        snapshot: dict | None = None,
    ):
        """
        Restore runtime snapshot.
        """

        if snapshot is None:

            snapshot = self._snapshot

        if snapshot is None:

            return self

        with self._lock:

            runtime = snapshot.get(
                "runtime",
                {},
            )

            self._enabled = runtime.get(
                "enabled",
                True,
            )

            self._running = runtime.get(
                "running",
                False,
            )

            self._frozen = runtime.get(
                "frozen",
                False,
            )

            self._closed = runtime.get(
                "closed",
                False,
            )

            self._config = copy.deepcopy(

                snapshot.get(
                    "configuration",
                    {},
                )

            )

            stats = snapshot.get(
                "statistics",
                {},
            )

            self._trace_count = stats.get(
                "trace_count",
                0,
            )

            self._span_count = stats.get(
                "span_count",
                0,
            )

            self._event_count = stats.get(
                "event_count",
                0,
            )

            self._error_count = stats.get(
                "error_count",
                0,
            )

            self._last_latency = stats.get(
                "latency",
                0.0,
            )

            self._trace_registry = copy.deepcopy(

                snapshot.get(
                    "trace_registry",
                    {},
                )

            )

            self._span_registry = copy.deepcopy(

                snapshot.get(
                    "span_registry",
                    {},
                )

            )

            self._registered_traces = copy.deepcopy(

                snapshot.get(
                    "registered_traces",
                    {},
                )

            )

            self._metadata = copy.deepcopy(

                snapshot.get(
                    "metadata",
                    {},
                )

            )

            self._active_traces = {}

            self._active_spans = {}

            self._updated_at = datetime.utcnow()

        return self



    def clone(
        self,
    ):
        """
        Create independent clone.
        """

        cloned = self.__class__(

            name=self._name,

            config=copy.deepcopy(
                self._config
            ),

        )

        cloned._handlers = copy.deepcopy(
            self._handlers
        )

        cloned.restore(
            self.snapshot()
        )

        return cloned



    def copy(
        self,
    ):
        """
        Alias of clone().
        """

        return self.clone()
    # =====================================================
    # Part 7. Statistics & Diagnostics
    # =====================================================

    def summary(
        self,
    ) -> dict:
        """
        Return compact runtime summary.
        """

        return {

            "id":
                self._id,

            "name":
                self._name,

            "enabled":
                self._enabled,

            "running":
                self._running,

            "frozen":
                self._frozen,

            "closed":
                self._closed,

            "trace_count":
                self._trace_count,

            "span_count":
                self._span_count,

            "error_count":
                self._error_count,

            "event_count":
                self._event_count,

            "registered_traces":
                len(self._registered_traces),

            "handlers":
                len(self._handlers),

            "uptime":
                self.uptime,

            "latency":
                self.latency,

        }



    def report(
        self,
    ) -> dict:
        """
        Return detailed diagnostic report.
        """

        return {

            "identity": {

                "id":
                    self._id,

                "name":
                    self._name,

                "version":
                    self._version,

            },

            "runtime": {

                "enabled":
                    self._enabled,

                "running":
                    self._running,

                "frozen":
                    self._frozen,

                "closed":
                    self._closed,

                "active":
                    self.active,

            },

            "configuration":

                copy.deepcopy(
                    self._config
                ),

            "statistics": {

                "trace_count":
                    self._trace_count,

                "span_count":
                    self._span_count,

                "event_count":
                    self._event_count,

                "error_count":
                    self._error_count,

                "uptime":
                    self.uptime,

                "latency":
                    self.latency,

            },

            "registries": {

                "trace_registry":
                    len(self._trace_registry),

                "span_registry":
                    len(self._span_registry),

                "registered_traces":
                    len(self._registered_traces),

                "handlers":
                    len(self._handlers),

            },

            "metadata":

                copy.deepcopy(
                    self._metadata
                ),

        }



    def health(
        self,
    ) -> dict:
        """
        Evaluate tracing health.
        """

        healthy = (

            self.active

            and

            self._error_count == 0

        )

        return {

            "healthy":
                healthy,

            "status":

                "healthy"

                if healthy

                else

                "degraded",

            "trace_count":
                self._trace_count,

            "span_count":
                self._span_count,

            "errors":
                self._error_count,

            "latency":
                self.latency,

        }



    def status(
        self,
    ) -> str:
        """
        Return runtime status.
        """

        if self._closed:

            return "closed"

        if self._frozen:

            return "frozen"

        if not self._enabled:

            return "disabled"

        if self._running:

            return "running"

        return "ready"



    # =====================================================
    # Statistics Properties
    # =====================================================

    @property
    def trace_count(
        self,
    ) -> int:
        """
        Number of completed traces.
        """

        return self._trace_count



    @property
    def span_count(
        self,
    ) -> int:
        """
        Number of completed spans.
        """

        return self._span_count



    @property
    def error_count(
        self,
    ) -> int:
        """
        Number of runtime errors.
        """

        return self._error_count



    @property
    def uptime(
        self,
    ) -> float:
        """
        Runtime uptime (seconds).
        """

        return (

            time.time()

            -

            self._start_time

        )



    @property
    def latency(
        self,
    ) -> float:
        """
        Last tracing latency.
        """

        return self._last_latency
    # =====================================================
    # Part 8. Serialization
    # =====================================================

    def to_dict(
        self,
    ) -> dict:
        """
        Serialize tracing integration into dictionary.
        """

        return {

            "identity": {

                "id":
                    self._id,

                "name":
                    self._name,

                "version":
                    self._version,

            },

            "runtime": {

                "enabled":
                    self._enabled,

                "running":
                    self._running,

                "frozen":
                    self._frozen,

                "closed":
                    self._closed,

            },

            "configuration":

                copy.deepcopy(
                    self._config
                ),

            "statistics": {

                "trace_count":
                    self._trace_count,

                "span_count":
                    self._span_count,

                "event_count":
                    self._event_count,

                "error_count":
                    self._error_count,

                "latency":
                    self._last_latency,

            },

            "trace_registry":

                copy.deepcopy(
                    self._trace_registry
                ),

            "span_registry":

                copy.deepcopy(
                    self._span_registry
                ),

            "registered_traces":

                copy.deepcopy(
                    self._registered_traces
                ),

            "handlers":

                list(
                    self._handlers.keys()
                ),

            "metadata":

                copy.deepcopy(
                    self._metadata
                ),

            "created_at":

                self._created_at.isoformat(),

            "updated_at":

                self._updated_at.isoformat(),

        }



    @classmethod
    def from_dict(
        cls,
        data: dict,
    ):
        """
        Restore MetricTracingIntegration
        from dictionary.
        """

        obj = cls(

            name=data.get(
                "identity",
                {},
            ).get(
                "name",
                "MetricTracingIntegration",
            ),

            config=copy.deepcopy(

                data.get(
                    "configuration",
                    {},
                )

            ),

        )

        runtime = data.get(
            "runtime",
            {},
        )

        obj._enabled = runtime.get(
            "enabled",
            True,
        )

        obj._running = runtime.get(
            "running",
            False,
        )

        obj._frozen = runtime.get(
            "frozen",
            False,
        )

        obj._closed = runtime.get(
            "closed",
            False,
        )

        stats = data.get(
            "statistics",
            {},
        )

        obj._trace_count = stats.get(
            "trace_count",
            0,
        )

        obj._span_count = stats.get(
            "span_count",
            0,
        )

        obj._event_count = stats.get(
            "event_count",
            0,
        )

        obj._error_count = stats.get(
            "error_count",
            0,
        )

        obj._last_latency = stats.get(
            "latency",
            0.0,
        )

        obj._trace_registry = copy.deepcopy(

            data.get(
                "trace_registry",
                {},
            )

        )

        obj._span_registry = copy.deepcopy(

            data.get(
                "span_registry",
                {},
            )

        )

        obj._registered_traces = copy.deepcopy(

            data.get(
                "registered_traces",
                {},
            )

        )

        obj._metadata = copy.deepcopy(

            data.get(
                "metadata",
                {},
            )

        )

        return obj



    def to_json(
        self,
        *,
        indent: int = 2,
    ) -> str:
        """
        Serialize into JSON.
        """

        import json

        return json.dumps(

            self.to_dict(),

            indent=indent,

            default=str,

        )



    @classmethod
    def from_json(
        cls,
        payload: str,
    ):
        """
        Restore from JSON.
        """

        import json

        return cls.from_dict(

            json.loads(
                payload
            )

        )



    def serialize(
        self,
    ):
        """
        Generic serialization API.

        Alias of to_dict().
        """

        return self.to_dict()



    @classmethod
    def deserialize(
        cls,
        payload,
    ):
        """
        Generic deserialization API.
        """

        if isinstance(
            payload,
            dict,
        ):

            return cls.from_dict(
                payload
            )

        if isinstance(
            payload,
            str,
        ):

            return cls.from_json(
                payload
            )

        raise TypeError(
            "Unsupported serialization payload."
        )
    # =====================================================
    # Part 9. Events & Hooks
    # =====================================================

    def before_trace(
        self,
        trace_name: str,
        **context,
    ):
        """
        Called before a trace starts.
        """

        self.emit(

            "before_trace",

            trace_name=trace_name,

            context=context,

        )

        return self



    def after_trace(
        self,
        trace: dict,
    ):
        """
        Called after a trace finishes.
        """

        self.emit(

            "after_trace",

            trace=trace,

        )

        return self



    def before_span(
        self,
        span_name: str,
        trace_id: str,
        **context,
    ):
        """
        Called before a span starts.
        """

        self.emit(

            "before_span",

            span_name=span_name,

            trace_id=trace_id,

            context=context,

        )

        return self



    def after_span(
        self,
        span: dict,
    ):
        """
        Called after a span finishes.
        """

        self.emit(

            "after_span",

            span=span,

        )

        return self



    def add_hook(
        self,
        event: str,
        callback,
    ):
        """
        Register event hook.
        """

        if not callable(callback):

            raise TypeError(
                "Hook must be callable."
            )

        with self._lock:

            self._hooks.setdefault(
                event,
                [],
            ).append(
                callback,
            )

        return self



    def remove_hook(
        self,
        event: str,
        callback=None,
    ):
        """
        Remove event hook.
        """

        with self._lock:

            if event not in self._hooks:

                return self

            if callback is None:

                self._hooks.pop(
                    event,
                    None,
                )

                return self

            try:

                self._hooks[event].remove(
                    callback,
                )

            except ValueError:

                pass

            if not self._hooks[event]:

                self._hooks.pop(
                    event,
                    None,
                )

        return self



    def emit(
        self,
        event: str,
        **payload,
    ):
        """
        Emit tracing event.
        """

        record = {

            "event":
                event,

            "payload":
                payload,

            "timestamp":
                datetime.utcnow(),

        }

        self._events.append(
            record,
        )

        self._event_count += 1

        callbacks = self._hooks.get(
            event,
            [],
        )

        for callback in callbacks:

            try:

                callback(
                    self,
                    **payload,
                )

            except Exception:

                self._error_count += 1

        return record



    def subscribe(
        self,
        event: str,
        callback,
    ):
        """
        Alias of add_hook().
        """

        return self.add_hook(
            event,
            callback,
        )
    # =====================================================
    # Part 10. Python Protocols
    # =====================================================

    def __repr__(
        self,
    ) -> str:
        """
        Developer-friendly representation.
        """

        return (

            f"{self.__class__.__name__}("

            f"name={self._name!r}, "

            f"traces={self._trace_count}, "

            f"spans={self._span_count}, "

            f"handlers={len(self._handlers)}, "

            f"registered={len(self._registered_traces)}, "

            f"status={self.status()}"

            f")"

        )



    def __str__(
        self,
    ) -> str:
        """
        Human-readable representation.
        """

        return (

            f"{self._name} "

            f"[status={self.status()}, "

            f"traces={self._trace_count}, "

            f"spans={self._span_count}, "

            f"handlers={len(self._handlers)}]"

        )



    def __len__(
        self,
    ) -> int:
        """
        Number of stored traces.
        """

        return len(

            self._trace_registry

        )



    def __iter__(
        self,
    ):
        """
        Iterate over registered traces.
        """

        return iter(

            self._trace_registry.values()

        )



    def __contains__(
        self,
        trace_id: str,
    ) -> bool:
        """
        Membership test.

        Checks whether a trace ID exists.
        """

        return (

            trace_id

            in

            self._trace_registry

        )



    def __call__(
        self,
        name: str,
        **attributes,
    ):
        """
        Callable interface.

        Equivalent to start_trace().
        """

        return self.start_trace(

            name,

            **attributes,

        )



    def __copy__(
        self,
    ):
        """
        Shallow copy protocol.
        """

        return self.clone()



    def __deepcopy__(
        self,
        memo,
    ):
        """
        Deep copy protocol.
        """

        cloned = self.clone()

        memo[id(self)] = cloned

        return cloned                                                                        
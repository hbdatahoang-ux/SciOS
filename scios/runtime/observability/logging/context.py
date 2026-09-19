# =============================================================================
# scios/runtime/observability/logging/context.py
#
# Part 1. Foundation
# =============================================================================

from __future__ import annotations

# =============================================================================
# Imports
# =============================================================================

import copy
import time
import uuid

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Mapping,
    MutableMapping,
    Optional,
    TypeAlias,
    Union,
)

# =============================================================================
# Constants
# =============================================================================

DEFAULT_CONTEXT_NAME = "logging_context"

DEFAULT_ENABLED = True

DEFAULT_TRACE_KEY = "trace_id"

DEFAULT_SPAN_KEY = "span_id"

DEFAULT_PARENT_SPAN_KEY = "parent_span_id"

DEFAULT_CORRELATION_KEY = "correlation_id"

DEFAULT_USER_KEY = "user"

DEFAULT_REQUEST_KEY = "request"

DEFAULT_RUNTIME_KEY = "runtime"

# =============================================================================
# Type Aliases
# =============================================================================

ContextDict: TypeAlias = Dict[str, Any]

Metadata: TypeAlias = Dict[str, Any]

Statistics: TypeAlias = Dict[str, Union[int, float]]

Hook: TypeAlias = Callable[..., None]

Snapshot: TypeAlias = Dict[str, Any]

# =============================================================================
# ContextRecord
# =============================================================================


@dataclass(slots=True)
class ContextRecord:
    """
    Represents one immutable logging context snapshot.
    """

    trace_id: str

    span_id: str

    correlation_id: str

    context: ContextDict = field(
        default_factory=dict
    )

    metadata: Metadata = field(
        default_factory=dict
    )

    created_at: datetime = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )

    def to_dict(
        self,
    ) -> ContextDict:
        """
        Convert record into a serializable dictionary.
        """

        return {

            "trace_id": self.trace_id,

            "span_id": self.span_id,

            "correlation_id": self.correlation_id,

            "context": copy.deepcopy(
                self.context
            ),

            "metadata": copy.deepcopy(
                self.metadata
            ),

            "created_at": self.created_at.isoformat(),

        }


# =============================================================================
# LoggingContext
# =============================================================================


class LoggingContext:
    """
    Shared runtime logging context.

    Used by

    • StructuredLogger
    • JSONLogger
    • ConsoleHandler
    • FileHandler
    • Metrics
    • Tracing
    • Telemetry

    Supports distributed tracing,
    context propagation and runtime snapshots.
    """

    # =========================================================================
    # __init__
    # =========================================================================

    def __init__(
        self,
        *,
        name: str = DEFAULT_CONTEXT_NAME,
        enabled: bool = DEFAULT_ENABLED,
        metadata: Optional[
            Metadata
        ] = None,
        context: Optional[
            ContextDict
        ] = None,
    ) -> None:

        # ---------------------------------------------------------------------
        # Identity
        # ---------------------------------------------------------------------

        self._id = str(
            uuid.uuid4()
        )

        self._name = name

        # ---------------------------------------------------------------------
        # Runtime State
        # ---------------------------------------------------------------------

        self._enabled = enabled

        self._frozen = False

        self._closed = False

        self.created_at = datetime.now(
            timezone.utc
        )

        self.updated_at = self.created_at

        self._history: List[
            ContextRecord
        ] = []

        self._hooks: Dict[
            str,
            List[Hook],
        ] = {}

        # ---------------------------------------------------------------------
        # Context Configuration
        # ---------------------------------------------------------------------

        self._context: ContextDict = (
            copy.deepcopy(context)
            if context
            else {}
        )

        self._context.setdefault(
            DEFAULT_TRACE_KEY,
            str(uuid.uuid4()),
        )

        self._context.setdefault(
            DEFAULT_SPAN_KEY,
            str(uuid.uuid4()),
        )

        self._context.setdefault(
            DEFAULT_PARENT_SPAN_KEY,
            None,
        )

        self._context.setdefault(
            DEFAULT_CORRELATION_KEY,
            str(uuid.uuid4()),
        )

        self._context.setdefault(
            DEFAULT_USER_KEY,
            None,
        )

        self._context.setdefault(
            DEFAULT_REQUEST_KEY,
            None,
        )

        self._context.setdefault(
            DEFAULT_RUNTIME_KEY,
            {},
        )

        # ---------------------------------------------------------------------
        # Metadata
        # ---------------------------------------------------------------------

        self._metadata: Metadata = (
            copy.deepcopy(metadata)
            if metadata
            else {}
        )

        # ---------------------------------------------------------------------
        # Statistics
        # ---------------------------------------------------------------------

        self._statistics: Statistics = {

            "contexts": 1,

            "traces": 1,

            "spans": 1,

            "updates": 0,

            "latency": 0.0,

        }

    # =========================================================================
    # Internal Helpers
    # =========================================================================

    def _touch(
        self,
    ) -> None:
        """
        Update modification timestamp.
        """

        self.updated_at = datetime.now(
            timezone.utc
        )

    def _record_latency(
        self,
        started: float,
    ) -> None:
        """
        Update accumulated latency.
        """

        self._statistics["latency"] += (

            time.perf_counter()

            -

            started

        )

    def _snapshot_record(
        self,
    ) -> ContextRecord:
        """
        Create a ContextRecord from the current state.
        """

        return ContextRecord(

            trace_id=self._context[
                DEFAULT_TRACE_KEY
            ],

            span_id=self._context[
                DEFAULT_SPAN_KEY
            ],

            correlation_id=self._context[
                DEFAULT_CORRELATION_KEY
            ],

            context=copy.deepcopy(
                self._context
            ),

            metadata=copy.deepcopy(
                self._metadata
            ),

        )
# =============================================================================
# Part 2. Properties
# =============================================================================

    # -------------------------------------------------------------------------
    # id
    # -------------------------------------------------------------------------

    @property
    def id(
        self,
    ) -> str:
        """
        Unique context identifier.
        """

        return self._id


    # -------------------------------------------------------------------------
    # name
    # -------------------------------------------------------------------------

    @property
    def name(
        self,
    ) -> str:
        """
        Context name.
        """

        return self._name


    @name.setter
    def name(
        self,
        value: str,
    ) -> None:

        self._name = str(value)

        self._touch()


    # -------------------------------------------------------------------------
    # enabled
    # -------------------------------------------------------------------------

    @property
    def enabled(
        self,
    ) -> bool:
        """
        Whether the context is enabled.
        """

        return self._enabled


    # -------------------------------------------------------------------------
    # trace_id
    # -------------------------------------------------------------------------

    @property
    def trace_id(
        self,
    ) -> str:
        """
        Current trace identifier.
        """

        return self._context[
            DEFAULT_TRACE_KEY
        ]


    # -------------------------------------------------------------------------
    # span_id
    # -------------------------------------------------------------------------

    @property
    def span_id(
        self,
    ) -> str:
        """
        Current span identifier.
        """

        return self._context[
            DEFAULT_SPAN_KEY
        ]


    # -------------------------------------------------------------------------
    # correlation_id
    # -------------------------------------------------------------------------

    @property
    def correlation_id(
        self,
    ) -> str:
        """
        Current correlation identifier.
        """

        return self._context[
            DEFAULT_CORRELATION_KEY
        ]


    # -------------------------------------------------------------------------
    # context
    # -------------------------------------------------------------------------

    @property
    def context(
        self,
    ) -> ContextDict:
        """
        Runtime context.

        Returned as a defensive copy.
        """

        return copy.deepcopy(
            self._context
        )


    # -------------------------------------------------------------------------
    # metadata
    # -------------------------------------------------------------------------

    @property
    def metadata(
        self,
    ) -> Metadata:
        """
        Metadata dictionary.

        Returned as a defensive copy.
        """

        return copy.deepcopy(
            self._metadata
        )


    # -------------------------------------------------------------------------
    # statistics
    # -------------------------------------------------------------------------

    @property
    def statistics(
        self,
    ) -> Statistics:
        """
        Runtime statistics.

        Returned as a defensive copy.
        """

        return copy.deepcopy(
            self._statistics
        )


    # -------------------------------------------------------------------------
    # age
    # -------------------------------------------------------------------------

    @property
    def age(
        self,
    ) -> float:
        """
        Context lifetime in seconds.
        """

        return (

            datetime.now(
                timezone.utc
            )

            -

            self.created_at

        ).total_seconds()


    # -------------------------------------------------------------------------
    # context_size
    # -------------------------------------------------------------------------

    @property
    def context_size(
        self,
    ) -> int:
        """
        Number of entries in the active context.
        """

        return len(
            self._context
        )
# =============================================================================
# Part 3. Context API
# =============================================================================

    # -------------------------------------------------------------------------
    # Get
    # -------------------------------------------------------------------------

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve a context value.
        """

        return self._context.get(
            key,
            default,
        )


    # -------------------------------------------------------------------------
    # Set
    # -------------------------------------------------------------------------

    def set(
        self,
        key: str,
        value: Any,
    ) -> "LoggingContext":
        """
        Set a context value.
        """

        if self._closed:

            raise RuntimeError(
                "Context is closed."
            )

        if self._frozen:

            raise RuntimeError(
                "Context is frozen."
            )

        started = time.perf_counter()

        self._context[key] = value

        self._statistics["updates"] += 1

        self._record_latency(
            started
        )

        self._touch()

        return self


    # -------------------------------------------------------------------------
    # Update
    # -------------------------------------------------------------------------

    def update(
        self,
        values: Mapping[
            str,
            Any,
        ],
    ) -> "LoggingContext":
        """
        Update multiple context entries.
        """

        if self._closed:

            raise RuntimeError(
                "Context is closed."
            )

        if self._frozen:

            raise RuntimeError(
                "Context is frozen."
            )

        started = time.perf_counter()

        self._context.update(

            copy.deepcopy(

                dict(values)

            )

        )

        self._statistics["updates"] += len(
            values
        )

        self._record_latency(
            started
        )

        self._touch()

        return self


    # -------------------------------------------------------------------------
    # Remove
    # -------------------------------------------------------------------------

    def remove(
        self,
        key: str,
    ) -> bool:
        """
        Remove a context entry.

        Reserved tracing keys cannot be removed.
        """

        if key in (

            DEFAULT_TRACE_KEY,

            DEFAULT_SPAN_KEY,

            DEFAULT_PARENT_SPAN_KEY,

            DEFAULT_CORRELATION_KEY,

        ):

            return False

        removed = (

            self._context.pop(

                key,

                None,

            )

            is not None

        )

        if removed:

            self._statistics["updates"] += 1

            self._touch()

        return removed


    # -------------------------------------------------------------------------
    # Clear
    # -------------------------------------------------------------------------

    def clear(
        self,
        preserve_trace: bool = True,
    ) -> "LoggingContext":
        """
        Clear the runtime context.

        Parameters
        ----------
        preserve_trace
            Preserve distributed tracing identifiers.
        """

        if preserve_trace:

            trace = self.trace_id

            span = self.span_id

            parent = self._context.get(
                DEFAULT_PARENT_SPAN_KEY
            )

            correlation = self.correlation_id

            runtime = copy.deepcopy(

                self._context.get(

                    DEFAULT_RUNTIME_KEY,

                    {},

                )

            )

            self._context.clear()

            self._context.update({

                DEFAULT_TRACE_KEY:
                    trace,

                DEFAULT_SPAN_KEY:
                    span,

                DEFAULT_PARENT_SPAN_KEY:
                    parent,

                DEFAULT_CORRELATION_KEY:
                    correlation,

                DEFAULT_RUNTIME_KEY:
                    runtime,

            })

        else:

            self._context.clear()

        self._statistics["updates"] += 1

        self._touch()

        return self


    # -------------------------------------------------------------------------
    # Copy Context
    # -------------------------------------------------------------------------

    def copy_context(
        self,
    ) -> ContextDict:
        """
        Return a deep copy of the context.
        """

        return copy.deepcopy(
            self._context
        )


    # -------------------------------------------------------------------------
    # Export
    # -------------------------------------------------------------------------

    def export(
        self,
    ) -> Snapshot:
        """
        Export context as a serializable snapshot.
        """

        return {

            "trace_id":
                self.trace_id,

            "span_id":
                self.span_id,

            "parent_span_id":

                self._context.get(

                    DEFAULT_PARENT_SPAN_KEY

                ),

            "correlation_id":
                self.correlation_id,

            "context":
                copy.deepcopy(
                    self._context
                ),

            "metadata":
                copy.deepcopy(
                    self._metadata
                ),

            "statistics":
                copy.deepcopy(
                    self._statistics
                ),

            "created_at":
                self.created_at.isoformat(),

            "updated_at":
                self.updated_at.isoformat(),

        }


    # -------------------------------------------------------------------------
    # Import Context
    # -------------------------------------------------------------------------

    def import_context(
        self,
        snapshot: Mapping[
            str,
            Any,
        ],
    ) -> "LoggingContext":
        """
        Restore context from an exported snapshot.
        """

        if not isinstance(
            snapshot,
            Mapping,
        ):

            raise TypeError(
                "Snapshot must be a mapping."
            )

        self._context = copy.deepcopy(

            snapshot.get(

                "context",

                {},

            )

        )

        self._metadata = copy.deepcopy(

            snapshot.get(

                "metadata",

                {},

            )

        )

        self._statistics = copy.deepcopy(

            snapshot.get(

                "statistics",

                {},

            )

        )

        self._touch()

        return self
# =============================================================================
# Part 4. Trace API
# =============================================================================

    # -------------------------------------------------------------------------
    # New Trace
    # -------------------------------------------------------------------------

    def new_trace(
        self,
        correlation_id: Optional[str] = None,
    ) -> str:
        """
        Start a new distributed trace.

        Parameters
        ----------
        correlation_id:
            Optional correlation identifier.

        Returns
        -------
        str
            Newly generated trace identifier.
        """

        started = time.perf_counter()

        trace_id = str(uuid.uuid4())

        span_id = str(uuid.uuid4())

        self._context[DEFAULT_TRACE_KEY] = trace_id

        self._context[DEFAULT_SPAN_KEY] = span_id

        self._context[DEFAULT_PARENT_SPAN_KEY] = None

        self._context[
            DEFAULT_CORRELATION_KEY
        ] = (

            correlation_id

            if correlation_id is not None

            else str(uuid.uuid4())

        )

        self._statistics["traces"] += 1

        self._statistics["spans"] += 1

        self._statistics["updates"] += 1

        self._history.append(

            self._snapshot_record()

        )

        self._record_latency(started)

        self._touch()

        return trace_id


    # -------------------------------------------------------------------------
    # New Span
    # -------------------------------------------------------------------------

    def new_span(
        self,
    ) -> str:
        """
        Create a child span under the current trace.
        """

        started = time.perf_counter()

        parent = self.span_id

        span = str(uuid.uuid4())

        self._context[
            DEFAULT_PARENT_SPAN_KEY
        ] = parent

        self._context[
            DEFAULT_SPAN_KEY
        ] = span

        self._statistics["spans"] += 1

        self._statistics["updates"] += 1

        self._history.append(

            self._snapshot_record()

        )

        self._record_latency(started)

        self._touch()

        return span


    # -------------------------------------------------------------------------
    # Trace
    # -------------------------------------------------------------------------

    def trace(
        self,
    ) -> str:
        """
        Return the active trace identifier.
        """

        return self.trace_id


    # -------------------------------------------------------------------------
    # Span
    # -------------------------------------------------------------------------

    def span(
        self,
    ) -> str:
        """
        Return the active span identifier.
        """

        return self.span_id


    # -------------------------------------------------------------------------
    # Parent Span
    # -------------------------------------------------------------------------

    def parent_span(
        self,
    ) -> Optional[str]:
        """
        Return the parent span identifier.
        """

        return self._context.get(

            DEFAULT_PARENT_SPAN_KEY

        )


    # -------------------------------------------------------------------------
    # End Span
    # -------------------------------------------------------------------------

    def end_span(
        self,
    ) -> Optional[str]:
        """
        Finish the current span.

        Returns
        -------
        Optional[str]
            Parent span restored as current span.
        """

        parent = self.parent_span()

        if parent is not None:

            self._context[
                DEFAULT_SPAN_KEY
            ] = parent

        self._context[
            DEFAULT_PARENT_SPAN_KEY
        ] = None

        self._statistics["updates"] += 1

        self._touch()

        return parent


    # -------------------------------------------------------------------------
    # End Trace
    # -------------------------------------------------------------------------

    def end_trace(
        self,
    ) -> None:
        """
        Finish the active trace.

        A fresh trace is automatically created so
        the context always remains valid.
        """

        self.new_trace()


    # -------------------------------------------------------------------------
    # Current Trace
    # -------------------------------------------------------------------------

    def current_trace(
        self,
    ) -> ContextRecord:
        """
        Return the current trace snapshot.
        """

        return self._snapshot_record()
# =============================================================================
# Part 5. Context Propagation API
# =============================================================================

    # -------------------------------------------------------------------------
    # Attach
    # -------------------------------------------------------------------------

    def attach(
        self,
        context: Mapping[str, Any],
    ) -> "LoggingContext":
        """
        Attach an external context.

        Existing keys are overwritten.
        """

        if not isinstance(context, Mapping):

            raise TypeError(
                "Context must be a mapping."
            )

        started = time.perf_counter()

        self._context.update(
            copy.deepcopy(dict(context))
        )

        self._statistics["updates"] += 1

        self._record_latency(started)

        self._touch()

        return self


    # -------------------------------------------------------------------------
    # Detach
    # -------------------------------------------------------------------------

    def detach(
        self,
    ) -> ContextDict:
        """
        Detach and return the current context.

        The runtime context is reset afterwards.
        """

        detached = copy.deepcopy(
            self._context
        )

        self.reset()

        return detached


    # -------------------------------------------------------------------------
    # Push
    # -------------------------------------------------------------------------

    def push(
        self,
    ) -> "LoggingContext":
        """
        Push the current context onto the history stack.
        """

        self._history.append(
            self._snapshot_record()
        )

        self._statistics["updates"] += 1

        self._touch()

        return self


    # -------------------------------------------------------------------------
    # Pop
    # -------------------------------------------------------------------------

    def pop(
        self,
    ) -> Optional[ContextRecord]:
        """
        Restore the most recently pushed context.
        """

        if not self._history:

            return None

        record = self._history.pop()

        self._context = copy.deepcopy(
            record.context
        )

        self._metadata = copy.deepcopy(
            record.metadata
        )

        self._statistics["updates"] += 1

        self._touch()

        return record


    # -------------------------------------------------------------------------
    # Inherit
    # -------------------------------------------------------------------------

    def inherit(
        self,
        parent: "LoggingContext",
    ) -> "LoggingContext":
        """
        Inherit context from another LoggingContext.
        """

        if not isinstance(
            parent,
            LoggingContext,
        ):

            raise TypeError(
                "Expected LoggingContext."
            )

        self._context = parent.copy_context()

        self._metadata = copy.deepcopy(
            parent.metadata
        )

        self._statistics["updates"] += 1

        self._touch()

        return self


    # -------------------------------------------------------------------------
    # Merge
    # -------------------------------------------------------------------------

    def merge(
        self,
        other: Mapping[str, Any],
    ) -> "LoggingContext":
        """
        Merge another context into the current one.

        Existing values are preserved.
        """

        if not isinstance(other, Mapping):

            raise TypeError(
                "Context must be a mapping."
            )

        started = time.perf_counter()

        for key, value in other.items():

            self._context.setdefault(

                key,

                copy.deepcopy(value),

            )

        self._statistics["updates"] += 1

        self._record_latency(started)

        self._touch()

        return self


    # -------------------------------------------------------------------------
    # Clone
    # -------------------------------------------------------------------------

    def clone(
        self,
    ) -> "LoggingContext":
        """
        Create a fully independent context clone.
        """

        cloned = self.__class__(

            name=self.name,

            enabled=self.enabled,

            metadata=self.metadata,

            context=self.context,

        )

        cloned._statistics = copy.deepcopy(
            self._statistics
        )

        cloned._history = copy.deepcopy(
            self._history
        )

        cloned.created_at = self.created_at

        cloned.updated_at = self.updated_at

        return cloned


    # -------------------------------------------------------------------------
    # Reset
    # -------------------------------------------------------------------------

    def reset(
        self,
    ) -> "LoggingContext":
        """
        Reset the runtime context.

        Generates fresh trace/span/correlation identifiers.
        """

        self._context.clear()

        self._context.update({

            DEFAULT_TRACE_KEY:
                str(uuid.uuid4()),

            DEFAULT_SPAN_KEY:
                str(uuid.uuid4()),

            DEFAULT_PARENT_SPAN_KEY:
                None,

            DEFAULT_CORRELATION_KEY:
                str(uuid.uuid4()),

            DEFAULT_USER_KEY:
                None,

            DEFAULT_REQUEST_KEY:
                None,

            DEFAULT_RUNTIME_KEY:
                {},

        })

        self._statistics["updates"] += 1

        self._touch()

        return self
# =============================================================================
# Part 6. Runtime Operations
# =============================================================================

    # -------------------------------------------------------------------------
    # Snapshot
    # -------------------------------------------------------------------------

    def snapshot(
        self,
    ) -> Snapshot:
        """
        Create a complete runtime snapshot.

        Returns
        -------
        Snapshot
            Serializable runtime state.
        """

        return {

            "id": self._id,

            "name": self._name,

            "enabled": self._enabled,

            "frozen": self._frozen,

            "closed": self._closed,

            "context": copy.deepcopy(
                self._context
            ),

            "metadata": copy.deepcopy(
                self._metadata
            ),

            "statistics": copy.deepcopy(
                self._statistics
            ),

            "history": copy.deepcopy(
                self._history
            ),

            "created_at": self.created_at,

            "updated_at": self.updated_at,

        }


    # -------------------------------------------------------------------------
    # Restore
    # -------------------------------------------------------------------------

    def restore(
        self,
        snapshot: Snapshot,
    ) -> "LoggingContext":
        """
        Restore runtime from a snapshot.
        """

        if not isinstance(snapshot, Mapping):

            raise TypeError(
                "snapshot must be a mapping."
            )

        self._id = snapshot["id"]

        self._name = snapshot["name"]

        self._enabled = snapshot["enabled"]

        self._frozen = snapshot["frozen"]

        self._closed = snapshot["closed"]

        self._context = copy.deepcopy(

            snapshot["context"]

        )

        self._metadata = copy.deepcopy(

            snapshot["metadata"]

        )

        self._statistics = copy.deepcopy(

            snapshot["statistics"]

        )

        self._history = copy.deepcopy(

            snapshot["history"]

        )

        self.created_at = snapshot["created_at"]

        self.updated_at = snapshot["updated_at"]

        return self


    # -------------------------------------------------------------------------
    # Clone
    # -------------------------------------------------------------------------

    def clone(
        self,
    ) -> "LoggingContext":
        """
        Create a deep runtime clone.
        """

        cloned = self.__class__(

            name=self._name,

            enabled=self._enabled,

            metadata=self._metadata,

            context=self._context,

        )

        cloned.restore(

            self.snapshot()

        )

        cloned._id = str(
            uuid.uuid4()
        )

        return cloned


    # -------------------------------------------------------------------------
    # Copy
    # -------------------------------------------------------------------------

    def copy(
        self,
    ) -> "LoggingContext":
        """
        Alias for clone().
        """

        return self.clone()


    # -------------------------------------------------------------------------
    # Optimize
    # -------------------------------------------------------------------------

    def optimize(
        self,
    ) -> "LoggingContext":
        """
        Optimize runtime structures.
        """

        #
        # Remove duplicated history entries.
        #

        unique = []

        seen = set()

        for record in self._history:

            key = (

                record.trace_id,

                record.span_id,

                record.correlation_id,

            )

            if key in seen:

                continue

            seen.add(key)

            unique.append(record)

        self._history = unique

        self._touch()

        return self


    # -------------------------------------------------------------------------
    # Cleanup
    # -------------------------------------------------------------------------

    def cleanup(
        self,
    ) -> "LoggingContext":
        """
        Cleanup transient runtime data.
        """

        self._hooks.clear()

        self._touch()

        return self


    # -------------------------------------------------------------------------
    # Compact
    # -------------------------------------------------------------------------

    def compact(
        self,
    ) -> "LoggingContext":
        """
        Compact runtime memory.

        Removes obsolete history while
        preserving the latest snapshot.
        """

        if len(self._history) > 1:

            self._history = [

                self._history[-1]

            ]

        self.optimize()

        self._touch()

        return self
# =============================================================================
# Part 7. Statistics & Diagnostics
# =============================================================================

    # -------------------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------------------

    def summary(
        self,
    ) -> Dict[str, Any]:
        """
        Return a concise runtime summary.
        """

        return {

            "id": self.id,

            "name": self.name,

            "enabled": self.enabled,

            "trace_id": self.trace_id,

            "span_id": self.span_id,

            "context_size": self.context_size,

            "trace_count": self.trace_count,

            "uptime": self.uptime,

            "latency": self.latency,

        }


    # -------------------------------------------------------------------------
    # Report
    # -------------------------------------------------------------------------

    def report(
        self,
    ) -> Dict[str, Any]:
        """
        Return a complete runtime report.
        """

        return {

            "identity": {

                "id": self.id,

                "name": self.name,

            },

            "runtime": {

                "enabled": self.enabled,

                "frozen": self._frozen,

                "closed": self._closed,

                "uptime": self.uptime,

            },

            "trace": {

                "trace_id": self.trace_id,

                "span_id": self.span_id,

                "correlation_id":

                    self.correlation_id,

            },

            "statistics":

                copy.deepcopy(

                    self._statistics

                ),

            "metadata":

                copy.deepcopy(

                    self._metadata

                ),

            "context_size":

                self.context_size,

        }


    # -------------------------------------------------------------------------
    # Health
    # -------------------------------------------------------------------------

    def health(
        self,
    ) -> Dict[str, Any]:
        """
        Runtime health information.
        """

        healthy = (

            self._enabled

            and

            not self._closed

        )

        return {

            "healthy": healthy,

            "enabled": self._enabled,

            "frozen": self._frozen,

            "closed": self._closed,

            "history_size": len(
                self._history
            ),

            "context_size":
                self.context_size,

        }


    # -------------------------------------------------------------------------
    # Status
    # -------------------------------------------------------------------------

    def status(
        self,
    ) -> str:
        """
        Human-readable runtime status.
        """

        if self._closed:

            return "closed"

        if self._frozen:

            return "frozen"

        if self._enabled:

            return "running"

        return "disabled"


    # -------------------------------------------------------------------------
    # Context Size
    # -------------------------------------------------------------------------

    @property
    def context_size(
        self,
    ) -> int:
        """
        Number of context entries.
        """

        return len(
            self._context
        )


    # -------------------------------------------------------------------------
    # Trace Count
    # -------------------------------------------------------------------------

    @property
    def trace_count(
        self,
    ) -> int:
        """
        Number of traces created.
        """

        return int(

            self._statistics.get(

                "traces",

                0,

            )

        )


    # -------------------------------------------------------------------------
    # Uptime
    # -------------------------------------------------------------------------

    @property
    def uptime(
        self,
    ) -> float:
        """
        Runtime uptime in seconds.
        """

        return (

            datetime.now(

                timezone.utc

            )

            -

            self.created_at

        ).total_seconds()


    # -------------------------------------------------------------------------
    # Latency
    # -------------------------------------------------------------------------

    @property
    def latency(
        self,
    ) -> float:
        """
        Accumulated runtime latency.
        """

        return float(

            self._statistics.get(

                "latency",

                0.0,

            )

        )
# =============================================================================
# Part 8. Validation
# =============================================================================

    # -------------------------------------------------------------------------
    # Validate
    # -------------------------------------------------------------------------

    def validate(
        self,
    ) -> bool:
        """
        Validate the complete LoggingContext.

        Returns
        -------
        bool
            True if every validation succeeds.
        """

        return (

            self.validate_context()

            and

            self.validate_trace()

            and

            self.check_configuration()

            and

            self.check_integrity()

        )


    # -------------------------------------------------------------------------
    # Validate Context
    # -------------------------------------------------------------------------

    def validate_context(
        self,
    ) -> bool:
        """
        Validate runtime context structure.
        """

        if not isinstance(

            self._context,

            MutableMapping,

        ):

            return False

        required = (

            DEFAULT_TRACE_KEY,

            DEFAULT_SPAN_KEY,

            DEFAULT_PARENT_SPAN_KEY,

            DEFAULT_CORRELATION_KEY,

            DEFAULT_RUNTIME_KEY,

        )

        for key in required:

            if key not in self._context:

                return False

        return True


    # -------------------------------------------------------------------------
    # Validate Trace
    # -------------------------------------------------------------------------

    def validate_trace(
        self,
    ) -> bool:
        """
        Validate trace identifiers.
        """

        identifiers = (

            self.trace_id,

            self.span_id,

            self.correlation_id,

        )

        for identifier in identifiers:

            if not isinstance(

                identifier,

                str,

            ):

                return False

            if not identifier.strip():

                return False

            try:

                uuid.UUID(identifier)

            except (

                ValueError,

                TypeError,

                AttributeError,

            ):

                return False

        parent = self.parent_span()

        if parent is not None:

            try:

                uuid.UUID(parent)

            except (

                ValueError,

                TypeError,

                AttributeError,

            ):

                return False

        return True


    # -------------------------------------------------------------------------
    # Check Configuration
    # -------------------------------------------------------------------------

    def check_configuration(
        self,
    ) -> bool:
        """
        Validate runtime configuration.
        """

        if not isinstance(

            self._enabled,

            bool,

        ):

            return False

        if not isinstance(

            self._metadata,

            MutableMapping,

        ):

            return False

        if not isinstance(

            self._statistics,

            MutableMapping,

        ):

            return False

        if not isinstance(

            self._history,

            list,

        ):

            return False

        return True


    # -------------------------------------------------------------------------
    # Check Integrity
    # -------------------------------------------------------------------------

    def check_integrity(
        self,
    ) -> bool:
        """
        Verify internal runtime integrity.
        """

        if self.context_size < 0:

            return False

        if self.trace_count < 0:

            return False

        if self.latency < 0.0:

            return False

        if self.created_at > self.updated_at:

            return False

        for record in self._history:

            if not isinstance(

                record,

                ContextRecord,

            ):

                return False

        return True
# =============================================================================
# Part 9. Events & Hooks
# =============================================================================

    # -------------------------------------------------------------------------
    # Before Attach
    # -------------------------------------------------------------------------

    def before_attach(
        self,
        context: Mapping[str, Any],
    ) -> None:
        """
        Invoked before attaching an external context.
        """

        self.emit_event(

            "before_attach",

            context=context,

        )


    # -------------------------------------------------------------------------
    # After Attach
    # -------------------------------------------------------------------------

    def after_attach(
        self,
        context: Mapping[str, Any],
    ) -> None:
        """
        Invoked after attaching an external context.
        """

        self.emit_event(

            "after_attach",

            context=context,

        )


    # -------------------------------------------------------------------------
    # Before Detach
    # -------------------------------------------------------------------------

    def before_detach(
        self,
    ) -> None:
        """
        Invoked before detaching the runtime context.
        """

        self.emit_event(

            "before_detach",

            context=self.copy_context(),

        )


    # -------------------------------------------------------------------------
    # After Detach
    # -------------------------------------------------------------------------

    def after_detach(
        self,
        context: ContextDict,
    ) -> None:
        """
        Invoked after detaching the runtime context.
        """

        self.emit_event(

            "after_detach",

            context=context,

        )


    # -------------------------------------------------------------------------
    # Add Hook
    # -------------------------------------------------------------------------

    def add_hook(
        self,
        event: str,
        callback: Hook,
    ) -> "LoggingContext":
        """
        Register a callback for an event.
        """

        if not callable(callback):

            raise TypeError(
                "Hook must be callable."
            )

        self._hooks.setdefault(

            event,

            [],

        ).append(

            callback

        )

        return self


    # -------------------------------------------------------------------------
    # Remove Hook
    # -------------------------------------------------------------------------

    def remove_hook(
        self,
        event: str,
        callback: Hook,
    ) -> bool:
        """
        Remove a previously registered callback.
        """

        callbacks = self._hooks.get(
            event
        )

        if callbacks is None:

            return False

        try:

            callbacks.remove(
                callback
            )

            if not callbacks:

                self._hooks.pop(
                    event,
                    None,
                )

            return True

        except ValueError:

            return False


    # -------------------------------------------------------------------------
    # Emit Event
    # -------------------------------------------------------------------------

    def emit_event(
        self,
        event: str,
        **payload: Any,
    ) -> None:
        """
        Dispatch an event to registered hooks.

        Hook failures are isolated and counted.
        """

        callbacks = self._hooks.get(

            event,

            (),

        )

        for callback in tuple(callbacks):

            try:

                callback(

                    event=event,

                    context=self,

                    **payload,

                )

            except Exception:

                self._statistics["errors"] = (

                    self._statistics.get(

                        "errors",

                        0,

                    )

                    + 1

                )


    # -------------------------------------------------------------------------
    # Subscribe
    # -------------------------------------------------------------------------

    def subscribe(
        self,
        event: str,
        callback: Hook,
    ) -> "LoggingContext":
        """
        Alias for add_hook().
        """

        return self.add_hook(

            event,

            callback,

        )
# =============================================================================
# Part 10. Python Protocols
# =============================================================================

    # -------------------------------------------------------------------------
    # __repr__
    # -------------------------------------------------------------------------

    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """

        return (

            f"{self.__class__.__name__}("

            f"id={self.id!r}, "

            f"name={self.name!r}, "

            f"trace_id={self.trace_id!r}, "

            f"span_id={self.span_id!r}, "

            f"context_size={self.context_size}, "

            f"enabled={self.enabled}"

            f")"

        )


    # -------------------------------------------------------------------------
    # __str__
    # -------------------------------------------------------------------------

    def __str__(
        self,
    ) -> str:
        """
        Human-readable representation.
        """

        return (

            f"{self.name} "

            f"[{self.status()}] "

            f"trace={self.trace_id} "

            f"context={self.context_size}"

        )


    # -------------------------------------------------------------------------
    # __len__
    # -------------------------------------------------------------------------

    def __len__(
        self,
    ) -> int:
        """
        Number of context entries.
        """

        return self.context_size


    # -------------------------------------------------------------------------
    # __iter__
    # -------------------------------------------------------------------------

    def __iter__(
        self,
    ):
        """
        Iterate over context items.
        """

        return iter(
            self._context.items()
        )


    # -------------------------------------------------------------------------
    # __contains__
    # -------------------------------------------------------------------------

    def __contains__(
        self,
        key: str,
    ) -> bool:
        """
        Membership test.

        Example
        -------
        if "trace_id" in ctx:
            ...
        """

        return key in self._context


    # -------------------------------------------------------------------------
    # __getitem__
    # -------------------------------------------------------------------------

    def __getitem__(
        self,
        key: str,
    ) -> Any:
        """
        Dictionary-style lookup.

        Example
        -------
        trace = ctx["trace_id"]
        """

        return self._context[key]


    # -------------------------------------------------------------------------
    # __call__
    # -------------------------------------------------------------------------

    def __call__(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Callable access.

        Equivalent to get().
        """

        return self.get(

            key,

            default,

        )


    # -------------------------------------------------------------------------
    # __copy__
    # -------------------------------------------------------------------------

    def __copy__(
        self,
    ) -> "LoggingContext":
        """
        Shallow runtime copy.
        """

        copied = self.__class__(

            name=self.name,

            enabled=self.enabled,

            metadata=self.metadata,

            context=self.context,

        )

        copied._statistics = (

            self.statistics.copy()

        )

        copied._history = list(

            self._history

        )

        copied.created_at = self.created_at

        copied.updated_at = self.updated_at

        return copied


    # -------------------------------------------------------------------------
    # __deepcopy__
    # -------------------------------------------------------------------------

    def __deepcopy__(
        self,
        memo: Dict[int, Any],
    ) -> "LoggingContext":
        """
        Deep runtime clone.
        """

        if id(self) in memo:

            return memo[id(self)]

        cloned = self.clone()

        memo[id(self)] = cloned

        return cloned                                                                        
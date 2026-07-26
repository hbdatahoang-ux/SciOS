# =============================================================================
# scios/runtime/observability/logging/middleware.py
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
    Sequence,
    TypeAlias,
)

# =============================================================================
# Constants
# =============================================================================

DEFAULT_MIDDLEWARE_NAME = "logging_middleware"

DEFAULT_ENABLED = True

DEFAULT_PRIORITY = 100

DEFAULT_BATCH_SIZE = 1

DEFAULT_ASYNC = False

# =============================================================================
# Type Aliases
# =============================================================================

LogRecord: TypeAlias = Dict[str, Any]

Metadata: TypeAlias = Dict[str, Any]

Statistics: TypeAlias = Dict[str, Any]

Snapshot: TypeAlias = Dict[str, Any]

Hook: TypeAlias = Callable[..., None]

Handler: TypeAlias = Callable[[LogRecord], Any]

Filter: TypeAlias = Callable[[LogRecord], bool]

Transformer: TypeAlias = Callable[[LogRecord], LogRecord]

# =============================================================================
# MiddlewareRecord
# =============================================================================


@dataclass(slots=True)
class MiddlewareRecord:
    """
    Snapshot of a processed middleware record.
    """

    id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )

    record: LogRecord = field(
        default_factory=dict
    )

    metadata: Metadata = field(
        default_factory=dict
    )

    dispatched: bool = False

    dropped: bool = False

    duration: float = 0.0

    def to_dict(
        self,
    ) -> Dict[str, Any]:

        return {

            "id": self.id,

            "timestamp": self.timestamp.isoformat(),

            "record": copy.deepcopy(
                self.record
            ),

            "metadata": copy.deepcopy(
                self.metadata
            ),

            "dispatched": self.dispatched,

            "dropped": self.dropped,

            "duration": self.duration,

        }


# =============================================================================
# LoggingMiddleware
# =============================================================================


class LoggingMiddleware:
    """
    Runtime logging middleware.

    Pipeline

        Logger
            │
            ▼
        Middleware
            │
        Filters
            │
        Transformers
            │
        Handlers
            │
        Observability
    """

    # =========================================================================
    # __init__
    # =========================================================================

    def __init__(
        self,
        *,
        name: str = DEFAULT_MIDDLEWARE_NAME,
        enabled: bool = DEFAULT_ENABLED,
        priority: int = DEFAULT_PRIORITY,
        metadata: Optional[
            Metadata
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
            MiddlewareRecord
        ] = []

        self._hooks: Dict[
            str,
            List[Hook],
        ] = {}

        # ---------------------------------------------------------------------
        # Middleware Configuration
        # ---------------------------------------------------------------------

        self._priority = priority

        self._batch_size = DEFAULT_BATCH_SIZE

        self._async = DEFAULT_ASYNC

        self._handlers: List[
            Handler
        ] = []

        self._filters: List[
            Filter
        ] = []

        self._transformers: List[
            Transformer
        ] = []

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

            "processed": 0,

            "forwarded": 0,

            "dropped": 0,

            "errors": 0,

            "handlers": 0,

            "filters": 0,

            "transformers": 0,

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
        Record processing latency.
        """

        self._statistics["latency"] += (

            time.perf_counter()

            -

            started

        )

    def _new_record(
        self,
        record: LogRecord,
    ) -> MiddlewareRecord:
        """
        Create a MiddlewareRecord snapshot.
        """

        return MiddlewareRecord(

            record=copy.deepcopy(
                record
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
    def id(self) -> str:
        """
        Unique middleware identifier.
        """
        return self._id

    # -------------------------------------------------------------------------
    # name
    # -------------------------------------------------------------------------

    @property
    def name(self) -> str:
        """
        Middleware name.
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
    def enabled(self) -> bool:
        """
        Whether the middleware is enabled.
        """
        return self._enabled

    # -------------------------------------------------------------------------
    # priority
    # -------------------------------------------------------------------------

    @property
    def priority(self) -> int:
        """
        Middleware execution priority.
        """
        return self._priority

    @priority.setter
    def priority(
        self,
        value: int,
    ) -> None:

        self._priority = int(value)

        self._touch()

    # -------------------------------------------------------------------------
    # handlers
    # -------------------------------------------------------------------------

    @property
    def handlers(
        self,
    ) -> Sequence[Handler]:
        """
        Registered handlers.
        """
        return tuple(self._handlers)

    # -------------------------------------------------------------------------
    # filters
    # -------------------------------------------------------------------------

    @property
    def filters(
        self,
    ) -> Sequence[Filter]:
        """
        Registered filters.
        """
        return tuple(self._filters)

    # -------------------------------------------------------------------------
    # transformers
    # -------------------------------------------------------------------------

    @property
    def transformers(
        self,
    ) -> Sequence[Transformer]:
        """
        Registered transformers.
        """
        return tuple(self._transformers)

    # -------------------------------------------------------------------------
    # metadata
    # -------------------------------------------------------------------------

    @property
    def metadata(
        self,
    ) -> Metadata:
        """
        Middleware metadata.
        """
        return copy.deepcopy(
            self._metadata
        )

    @metadata.setter
    def metadata(
        self,
        value: Mapping[str, Any],
    ) -> None:

        self._metadata = dict(

            copy.deepcopy(value)

        )

        self._touch()

    # -------------------------------------------------------------------------
    # statistics
    # -------------------------------------------------------------------------

    @property
    def statistics(
        self,
    ) -> Statistics:
        """
        Runtime statistics.
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
        Middleware lifetime in seconds.
        """

        return (

            datetime.now(

                timezone.utc

            )

            -

            self.created_at

        ).total_seconds()

    # -------------------------------------------------------------------------
    # middleware_count
    # -------------------------------------------------------------------------

    @property
    def middleware_count(
        self,
    ) -> int:
        """
        Number of processed middleware records.
        """

        return len(
            self._history
        )
# =============================================================================
# Part 3. Middleware API
# =============================================================================

    # -------------------------------------------------------------------------
    # Process
    # -------------------------------------------------------------------------

    def process(
        self,
        record: LogRecord,
    ) -> LogRecord:
        """
        Process a log record through the middleware pipeline.
        """

        if not self._enabled:

            return record

        if self._closed:

            raise RuntimeError(
                "Middleware is closed."
            )

        if self._frozen:

            return record

        started = time.perf_counter()

        self.before_process(record)

        record = self.intercept(record)

        record = self.transform(record)

        self.dispatch(record)

        self.finalize(record)

        self.after_process(record)

        self._statistics["processed"] += 1

        self._record_latency(started)

        self._touch()

        return record


    # -------------------------------------------------------------------------
    # Dispatch
    # -------------------------------------------------------------------------

    def dispatch(
        self,
        record: LogRecord,
    ) -> None:
        """
        Dispatch a record to all handlers.
        """

        self.before_dispatch(record)

        for handler in tuple(
            self._handlers
        ):

            self.forward(

                handler,

                record,

            )

        self.after_dispatch(record)


    # -------------------------------------------------------------------------
    # Forward
    # -------------------------------------------------------------------------

    def forward(
        self,
        handler: Handler,
        record: LogRecord,
    ) -> None:
        """
        Forward a record to a handler.
        """

        try:

            handler(record)

            self._statistics[
                "forwarded"
            ] += 1

        except Exception:

            self._statistics[
                "errors"
            ] += 1


    # -------------------------------------------------------------------------
    # Handle
    # -------------------------------------------------------------------------

    def handle(
        self,
        record: LogRecord,
    ) -> LogRecord:
        """
        Alias of process().
        """

        return self.process(
            record
        )


    # -------------------------------------------------------------------------
    # Route
    # -------------------------------------------------------------------------

    def route(
        self,
        record: LogRecord,
    ) -> bool:
        """
        Evaluate all registered filters.

        Returns
        -------
        bool
            True if the record is accepted.
        """

        for filter_fn in tuple(
            self._filters
        ):

            try:

                if not filter_fn(
                    record
                ):

                    self._statistics[
                        "dropped"
                    ] += 1

                    return False

            except Exception:

                self._statistics[
                    "errors"
                ] += 1

                return False

        return True


    # -------------------------------------------------------------------------
    # Intercept
    # -------------------------------------------------------------------------

    def intercept(
        self,
        record: LogRecord,
    ) -> LogRecord:
        """
        Intercept an incoming record.

        Filters are evaluated before
        dispatching.
        """

        accepted = self.route(
            record
        )

        if not accepted:

            raise RuntimeError(
                "Log record rejected "
                "by middleware filter."
            )

        return record


    # -------------------------------------------------------------------------
    # Transform
    # -------------------------------------------------------------------------

    def transform(
        self,
        record: LogRecord,
    ) -> LogRecord:
        """
        Apply all registered transformers.
        """

        transformed = record

        for transformer in tuple(
            self._transformers
        ):

            try:

                transformed = transformer(
                    transformed
                )

            except Exception:

                self._statistics[
                    "errors"
                ] += 1

        return transformed


    # -------------------------------------------------------------------------
    # Finalize
    # -------------------------------------------------------------------------

    def finalize(
        self,
        record: LogRecord,
    ) -> MiddlewareRecord:
        """
        Finalize middleware execution.

        Stores a middleware snapshot.
        """

        snapshot = self._new_record(
            record
        )

        snapshot.dispatched = True

        self._history.append(
            snapshot
        )

        return snapshot
# =============================================================================
# Part 4. Pipeline API
# =============================================================================

    # -------------------------------------------------------------------------
    # Add Handler
    # -------------------------------------------------------------------------

    def add_handler(
        self,
        handler: Handler,
    ) -> "LoggingMiddleware":
        """
        Register a log handler.
        """

        if not callable(handler):

            raise TypeError(
                "Handler must be callable."
            )

        if handler not in self._handlers:

            self._handlers.append(
                handler
            )

            self._statistics["handlers"] = len(
                self._handlers
            )

            self._touch()

        return self


    # -------------------------------------------------------------------------
    # Remove Handler
    # -------------------------------------------------------------------------

    def remove_handler(
        self,
        handler: Handler,
    ) -> bool:
        """
        Remove a registered handler.
        """

        try:

            self._handlers.remove(
                handler
            )

            self._statistics["handlers"] = len(
                self._handlers
            )

            self._touch()

            return True

        except ValueError:

            return False


    # -------------------------------------------------------------------------
    # Add Filter
    # -------------------------------------------------------------------------

    def add_filter(
        self,
        filter_fn: Filter,
    ) -> "LoggingMiddleware":
        """
        Register a record filter.
        """

        if not callable(filter_fn):

            raise TypeError(
                "Filter must be callable."
            )

        if filter_fn not in self._filters:

            self._filters.append(
                filter_fn
            )

            self._statistics["filters"] = len(
                self._filters
            )

            self._touch()

        return self


    # -------------------------------------------------------------------------
    # Remove Filter
    # -------------------------------------------------------------------------

    def remove_filter(
        self,
        filter_fn: Filter,
    ) -> bool:
        """
        Remove a registered filter.
        """

        try:

            self._filters.remove(
                filter_fn
            )

            self._statistics["filters"] = len(
                self._filters
            )

            self._touch()

            return True

        except ValueError:

            return False


    # -------------------------------------------------------------------------
    # Add Transformer
    # -------------------------------------------------------------------------

    def add_transformer(
        self,
        transformer: Transformer,
    ) -> "LoggingMiddleware":
        """
        Register a log transformer.
        """

        if not callable(transformer):

            raise TypeError(
                "Transformer must be callable."
            )

        if transformer not in self._transformers:

            self._transformers.append(
                transformer
            )

            self._statistics["transformers"] = len(
                self._transformers
            )

            self._touch()

        return self


    # -------------------------------------------------------------------------
    # Remove Transformer
    # -------------------------------------------------------------------------

    def remove_transformer(
        self,
        transformer: Transformer,
    ) -> bool:
        """
        Remove a registered transformer.
        """

        try:

            self._transformers.remove(
                transformer
            )

            self._statistics["transformers"] = len(
                self._transformers
            )

            self._touch()

            return True

        except ValueError:

            return False


    # -------------------------------------------------------------------------
    # Pipeline
    # -------------------------------------------------------------------------

    def pipeline(
        self,
    ) -> Dict[str, Any]:
        """
        Return pipeline information.
        """

        return {

            "priority": self.priority,

            "enabled": self.enabled,

            "handlers": len(
                self._handlers
            ),

            "filters": len(
                self._filters
            ),

            "transformers": len(
                self._transformers
            ),

            "handler_objects": tuple(
                self._handlers
            ),

            "filter_objects": tuple(
                self._filters
            ),

            "transformer_objects": tuple(
                self._transformers
            ),

        }


    # -------------------------------------------------------------------------
    # Clear Pipeline
    # -------------------------------------------------------------------------

    def clear_pipeline(
        self,
    ) -> "LoggingMiddleware":
        """
        Remove all pipeline components.
        """

        self._handlers.clear()

        self._filters.clear()

        self._transformers.clear()

        self._statistics["handlers"] = 0

        self._statistics["filters"] = 0

        self._statistics["transformers"] = 0

        self._touch()

        return self
# =============================================================================
# Part 5. Lifecycle API
# =============================================================================

    # -------------------------------------------------------------------------
    # Enable
    # -------------------------------------------------------------------------

    def enable(
        self,
    ) -> "LoggingMiddleware":
        """
        Enable the middleware.

        Returns
        -------
        LoggingMiddleware
            Current middleware instance.
        """

        self._enabled = True

        self._touch()

        return self


    # -------------------------------------------------------------------------
    # Disable
    # -------------------------------------------------------------------------

    def disable(
        self,
    ) -> "LoggingMiddleware":
        """
        Disable the middleware.

        Disabled middleware bypasses all processing.
        """

        self._enabled = False

        self._touch()

        return self


    # -------------------------------------------------------------------------
    # Freeze
    # -------------------------------------------------------------------------

    def freeze(
        self,
    ) -> "LoggingMiddleware":
        """
        Freeze the middleware.

        Frozen middleware preserves its state but
        temporarily suspends record processing.
        """

        self._frozen = True

        self._touch()

        return self


    # -------------------------------------------------------------------------
    # Unfreeze
    # -------------------------------------------------------------------------

    def unfreeze(
        self,
    ) -> "LoggingMiddleware":
        """
        Resume middleware execution.
        """

        self._frozen = False

        self._touch()

        return self


    # -------------------------------------------------------------------------
    # Close
    # -------------------------------------------------------------------------

    def close(
        self,
    ) -> "LoggingMiddleware":
        """
        Close the middleware.

        All runtime processing is permanently
        suspended until reopen() is called.
        """

        self._closed = True

        self._enabled = False

        self._touch()

        return self


    # -------------------------------------------------------------------------
    # Reopen
    # -------------------------------------------------------------------------

    def reopen(
        self,
    ) -> "LoggingMiddleware":
        """
        Reopen a previously closed middleware.
        """

        self._closed = False

        self._enabled = True

        self._frozen = False

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
        Capture the complete runtime state.
        """

        return {

            "id": self._id,

            "name": self._name,

            "enabled": self._enabled,

            "frozen": self._frozen,

            "closed": self._closed,

            "priority": self._priority,

            "batch_size": self._batch_size,

            "async": self._async,

            "metadata": copy.deepcopy(
                self._metadata
            ),

            "statistics": copy.deepcopy(
                self._statistics
            ),

            "history": copy.deepcopy(
                self._history
            ),

            #
            # Configuration only.
            #

            "handlers": list(
                self._handlers
            ),

            "filters": list(
                self._filters
            ),

            "transformers": list(
                self._transformers
            ),

            "created_at": self.created_at,

            "updated_at": self.updated_at,

        )


    # -------------------------------------------------------------------------
    # Restore
    # -------------------------------------------------------------------------

    def restore(
        self,
        snapshot: Snapshot,
    ) -> "LoggingMiddleware":
        """
        Restore middleware state.
        """

        if not isinstance(
            snapshot,
            Mapping,
        ):

            raise TypeError(
                "snapshot must be a mapping."
            )

        self._id = snapshot["id"]

        self._name = snapshot["name"]

        self._enabled = snapshot["enabled"]

        self._frozen = snapshot["frozen"]

        self._closed = snapshot["closed"]

        self._priority = snapshot["priority"]

        self._batch_size = snapshot["batch_size"]

        self._async = snapshot["async"]

        self._metadata = copy.deepcopy(
            snapshot["metadata"]
        )

        self._statistics = copy.deepcopy(
            snapshot["statistics"]
        )

        self._history = copy.deepcopy(
            snapshot["history"]
        )

        self._handlers = list(
            snapshot["handlers"]
        )

        self._filters = list(
            snapshot["filters"]
        )

        self._transformers = list(
            snapshot["transformers"]
        )

        self.created_at = snapshot[
            "created_at"
        ]

        self.updated_at = snapshot[
            "updated_at"
        ]

        return self


    # -------------------------------------------------------------------------
    # Clone
    # -------------------------------------------------------------------------

    def clone(
        self,
    ) -> "LoggingMiddleware":
        """
        Create a deep middleware clone.

        A new middleware receives a new identity
        while preserving the runtime state.
        """

        cloned = self.__class__(

            name=self.name,

            enabled=self.enabled,

            priority=self.priority,

            metadata=self.metadata,

        )

        cloned.restore(

            self.snapshot()

        )

        cloned._id = str(
            uuid.uuid4()
        )

        cloned.created_at = datetime.now(
            timezone.utc
        )

        cloned.updated_at = cloned.created_at

        return cloned


    # -------------------------------------------------------------------------
    # Copy
    # -------------------------------------------------------------------------

    def copy(
        self,
    ) -> "LoggingMiddleware":
        """
        Alias for clone().
        """

        return self.clone()


    # -------------------------------------------------------------------------
    # Optimize
    # -------------------------------------------------------------------------

    def optimize(
        self,
    ) -> "LoggingMiddleware":
        """
        Optimize runtime resources.
        """

        #
        # Remove duplicate history entries.
        #

        unique = []

        seen = set()

        for record in self._history:

            key = record.id

            if key in seen:

                continue

            seen.add(key)

            unique.append(record)

        self._history = unique

        #
        # Synchronize statistics.
        #

        self._statistics["handlers"] = len(
            self._handlers
        )

        self._statistics["filters"] = len(
            self._filters
        )

        self._statistics["transformers"] = len(
            self._transformers
        )

        self._touch()

        return self


    # -------------------------------------------------------------------------
    # Cleanup
    # -------------------------------------------------------------------------

    def cleanup(
        self,
    ) -> "LoggingMiddleware":
        """
        Cleanup transient runtime resources.
        """

        self._hooks.clear()

        self._history.clear()

        self._touch()

        return self


    # -------------------------------------------------------------------------
    # Compact
    # -------------------------------------------------------------------------

    def compact(
        self,
    ) -> "LoggingMiddleware":
        """
        Compact middleware memory.

        Keeps only the newest middleware record.
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
        Return a concise middleware summary.
        """

        return {

            "id": self.id,

            "name": self.name,

            "enabled": self.enabled,

            "priority": self.priority,

            "processed_count": self.processed_count,

            "dropped_count": self.dropped_count,

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
        Return a complete middleware report.
        """

        return {

            "identity": {

                "id": self.id,

                "name": self.name,

            },

            "runtime": {

                "enabled": self._enabled,

                "frozen": self._frozen,

                "closed": self._closed,

                "priority": self._priority,

                "uptime": self.uptime,

            },

            "pipeline": {

                "handlers": len(
                    self._handlers
                ),

                "filters": len(
                    self._filters
                ),

                "transformers": len(
                    self._transformers
                ),

            },

            "statistics": copy.deepcopy(
                self._statistics
            ),

            "metadata": copy.deepcopy(
                self._metadata
            ),

        }


    # -------------------------------------------------------------------------
    # Health
    # -------------------------------------------------------------------------

    def health(
        self,
    ) -> Dict[str, Any]:
        """
        Return middleware health information.
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

            "handlers": len(
                self._handlers
            ),

            "filters": len(
                self._filters
            ),

            "transformers": len(
                self._transformers
            ),

            "history_size": len(
                self._history
            ),

        }


    # -------------------------------------------------------------------------
    # Status
    # -------------------------------------------------------------------------

    def status(
        self,
    ) -> str:
        """
        Return current middleware status.
        """

        if self._closed:

            return "closed"

        if self._frozen:

            return "frozen"

        if self._enabled:

            return "running"

        return "disabled"


    # -------------------------------------------------------------------------
    # Processed Count
    # -------------------------------------------------------------------------

    @property
    def processed_count(
        self,
    ) -> int:
        """
        Total processed log records.
        """

        return int(

            self._statistics.get(

                "processed",

                0,

            )

        )


    # -------------------------------------------------------------------------
    # Dropped Count
    # -------------------------------------------------------------------------

    @property
    def dropped_count(
        self,
    ) -> int:
        """
        Total dropped log records.
        """

        return int(

            self._statistics.get(

                "dropped",

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
        Middleware uptime in seconds.
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
        Total accumulated middleware latency.
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
        Validate the complete middleware state.

        Returns
        -------
        bool
            True when middleware is valid.
        """

        return (

            self.validate_pipeline()

            and

            self.validate_handler()

            and

            self.check_configuration()

            and

            self.check_integrity()

        )


    # -------------------------------------------------------------------------
    # Validate Pipeline
    # -------------------------------------------------------------------------

    def validate_pipeline(
        self,
    ) -> bool:
        """
        Validate pipeline components.
        """

        #
        # Handlers
        #

        for handler in self._handlers:

            if not callable(handler):

                return False


        #
        # Filters
        #

        for filter_fn in self._filters:

            if not callable(filter_fn):

                return False


        #
        # Transformers
        #

        for transformer in self._transformers:

            if not callable(transformer):

                return False


        return True


    # -------------------------------------------------------------------------
    # Validate Handler
    # -------------------------------------------------------------------------

    def validate_handler(
        self,
    ) -> bool:
        """
        Validate handler execution contract.
        """

        for handler in self._handlers:

            if not callable(handler):

                return False


        return True


    # -------------------------------------------------------------------------
    # Check Configuration
    # -------------------------------------------------------------------------

    def check_configuration(
        self,
    ) -> bool:
        """
        Validate middleware configuration.
        """

        #
        # Identity
        #

        if not isinstance(
            self._name,
            str,
        ):

            return False


        if not self._name.strip():

            return False


        #
        # Priority
        #

        if not isinstance(
            self._priority,
            int,
        ):

            return False


        #
        # Runtime flags
        #

        if not isinstance(
            self._enabled,
            bool,
        ):

            return False


        if not isinstance(
            self._frozen,
            bool,
        ):

            return False


        if not isinstance(
            self._closed,
            bool,
        ):

            return False


        #
        # Metadata
        #

        if not isinstance(
            self._metadata,
            MutableMapping,
        ):

            return False


        #
        # Statistics
        #

        if not isinstance(
            self._statistics,
            MutableMapping,
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
        Validate internal runtime consistency.
        """

        #
        # Timestamp integrity
        #

        if self.created_at > self.updated_at:

            return False


        #
        # History integrity
        #

        for record in self._history:

            if not isinstance(
                record,
                MiddlewareRecord,
            ):

                return False


        #
        # Statistics integrity
        #

        counters = (

            "processed",

            "forwarded",

            "dropped",

            "errors",

        )

        for counter in counters:

            value = self._statistics.get(
                counter,
                0,
            )

            if not isinstance(
                value,
                int,
            ):

                return False


            if value < 0:

                return False


        #
        # Pipeline statistics consistency
        #

        if self._statistics.get(
            "handlers",
            0,
        ) != len(
            self._handlers
        ):

            return False


        if self._statistics.get(
            "filters",
            0,
        ) != len(
            self._filters
        ):

            return False


        if self._statistics.get(
            "transformers",
            0,
        ) != len(
            self._transformers
        ):

            return False


        return True
# =============================================================================
# Part 9. Events & Hooks
# =============================================================================

    # -------------------------------------------------------------------------
    # Before Process
    # -------------------------------------------------------------------------

    def before_process(
        self,
        record: LogRecord,
    ) -> None:
        """
        Called before processing a log record.
        """

        self.emit_event(
            "before_process",
            record=record,
        )


    # -------------------------------------------------------------------------
    # After Process
    # -------------------------------------------------------------------------

    def after_process(
        self,
        record: LogRecord,
    ) -> None:
        """
        Called after processing a log record.
        """

        self.emit_event(
            "after_process",
            record=record,
        )


    # -------------------------------------------------------------------------
    # Before Dispatch
    # -------------------------------------------------------------------------

    def before_dispatch(
        self,
        record: LogRecord,
    ) -> None:
        """
        Called before dispatching a record
        to handlers.
        """

        self.emit_event(
            "before_dispatch",
            record=record,
        )


    # -------------------------------------------------------------------------
    # After Dispatch
    # -------------------------------------------------------------------------

    def after_dispatch(
        self,
        record: LogRecord,
    ) -> None:
        """
        Called after dispatching a record.
        """

        self.emit_event(
            "after_dispatch",
            record=record,
        )


    # -------------------------------------------------------------------------
    # Add Hook
    # -------------------------------------------------------------------------

    def add_hook(
        self,
        event: str,
        callback: Hook,
    ) -> "LoggingMiddleware":
        """
        Register a callback hook.
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
        Remove a registered hook.
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
        Emit event to all subscribed hooks.

        Hook errors are isolated from
        the logging pipeline.
        """

        callbacks = tuple(

            self._hooks.get(
                event,
                [],
            )

        )


        for callback in callbacks:

            try:

                callback(
                    event=event,
                    middleware=self,
                    **payload,
                )


            except Exception:

                self._statistics[
                    "errors"
                ] += 1


    # -------------------------------------------------------------------------
    # Subscribe
    # -------------------------------------------------------------------------

    def subscribe(
        self,
        event: str,
        callback: Hook,
    ) -> "LoggingMiddleware":
        """
        Subscribe to middleware events.

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

            f"enabled={self.enabled!r}, "

            f"priority={self.priority!r}, "

            f"handlers={len(self._handlers)}, "

            f"filters={len(self._filters)}, "

            f"transformers={len(self._transformers)}"

            f")"

        )


    # -------------------------------------------------------------------------
    # __str__
    # -------------------------------------------------------------------------

    def __str__(
        self,
    ) -> str:
        """
        Human-readable middleware status.
        """

        return (

            f"{self.name} "

            f"[{self.status()}] "

            f"processed={self.processed_count} "

            f"dropped={self.dropped_count}"

        )


    # -------------------------------------------------------------------------
    # __len__
    # -------------------------------------------------------------------------

    def __len__(
        self,
    ) -> int:
        """
        Return number of pipeline components.

        Includes:
        - handlers
        - filters
        - transformers
        """

        return (

            len(self._handlers)

            +

            len(self._filters)

            +

            len(self._transformers)

        )


    # -------------------------------------------------------------------------
    # __iter__
    # -------------------------------------------------------------------------

    def __iter__(
        self,
    ):
        """
        Iterate over pipeline components.

        Order:

        handlers
        filters
        transformers
        """

        return iter(

            [

                *self._handlers,

                *self._filters,

                *self._transformers,

            ]

        )


    # -------------------------------------------------------------------------
    # __contains__
    # -------------------------------------------------------------------------

    def __contains__(
        self,
        component: Any,
    ) -> bool:
        """
        Check whether a component exists
        in the pipeline.
        """

        return (

            component in self._handlers

            or

            component in self._filters

            or

            component in self._transformers

        )


    # -------------------------------------------------------------------------
    # __call__
    # -------------------------------------------------------------------------

    def __call__(
        self,
        record: LogRecord,
    ) -> LogRecord:
        """
        Callable middleware execution.

        Example
        -------
        middleware(record)
        """

        return self.process(
            record
        )


    # -------------------------------------------------------------------------
    # __copy__
    # -------------------------------------------------------------------------

    def __copy__(
        self,
    ) -> "LoggingMiddleware":
        """
        Create shallow middleware copy.
        """

        copied = self.__class__(

            name=self.name,

            enabled=self.enabled,

            priority=self.priority,

            metadata=self.metadata,

        )


        copied._handlers = list(
            self._handlers
        )

        copied._filters = list(
            self._filters
        )

        copied._transformers = list(
            self._transformers
        )


        copied._statistics = copy.deepcopy(

            self._statistics

        )


        copied._history = list(

            self._history

        )


        return copied


    # -------------------------------------------------------------------------
    # __deepcopy__
    # -------------------------------------------------------------------------

    def __deepcopy__(
        self,
        memo: Dict[int, Any],
    ) -> "LoggingMiddleware":
        """
        Create independent middleware clone.
        """

        if id(self) in memo:

            return memo[id(self)]


        cloned = self.clone()


        memo[id(self)] = cloned


        return cloned                                                                        
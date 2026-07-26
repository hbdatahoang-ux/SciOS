# =============================================================================
# scios/runtime/observability/logging/structured.py
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

DEFAULT_LOGGER_NAME = "structured_logger"

DEFAULT_LEVEL = "INFO"

DEFAULT_ENABLED = True

DEFAULT_SCHEMA = "scios.runtime.log.v1"

DEFAULT_TRACE_KEY = "trace_id"

DEFAULT_SPAN_KEY = "span_id"

DEFAULT_CORRELATION_KEY = "correlation_id"

SUPPORTED_LEVELS = (
    "TRACE",
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
)

# =============================================================================
# Type Aliases
# =============================================================================

Metadata: TypeAlias = Dict[str, Any]

Context: TypeAlias = Dict[str, Any]

Statistics: TypeAlias = Dict[str, Union[int, float]]

Hook: TypeAlias = Callable[..., None]

StructuredDict: TypeAlias = Dict[str, Any]

# =============================================================================
# StructuredRecord
# =============================================================================


@dataclass(slots=True)
class StructuredRecord:
    """
    Structured log record.

    This object represents a semantic runtime event.
    """

    timestamp: datetime

    level: str

    logger: str

    message: str

    context: Context = field(
        default_factory=dict
    )

    metadata: Metadata = field(
        default_factory=dict
    )

    extra: Metadata = field(
        default_factory=dict
    )

    def to_dict(
        self,
    ) -> StructuredDict:
        """
        Convert record into a serializable dictionary.
        """

        return {

            "timestamp": self.timestamp.isoformat(),

            "level": self.level,

            "logger": self.logger,

            "message": self.message,

            "context": self.context,

            "metadata": self.metadata,

            "extra": self.extra,

        }


# =============================================================================
# StructuredLogger
# =============================================================================


class StructuredLogger:
    """
    High-level structured logger.

    Features
    --------
    • Semantic logging
    • Context propagation
    • Trace / Span IDs
    • Correlation IDs
    • Distributed observability
    """

    # =========================================================================
    # __init__
    # =========================================================================

    def __init__(
        self,
        name: str = DEFAULT_LOGGER_NAME,
        *,
        level: str = DEFAULT_LEVEL,
        schema: str = DEFAULT_SCHEMA,
        enabled: bool = DEFAULT_ENABLED,
        metadata: Optional[Metadata] = None,
        context: Optional[Context] = None,
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

        self._last_record: Optional[
            StructuredRecord
        ] = None

        # ---------------------------------------------------------------------
        # Logging Configuration
        # ---------------------------------------------------------------------

        self._level = level.upper()

        self._schema = schema

        # ---------------------------------------------------------------------
        # Context Configuration
        # ---------------------------------------------------------------------

        self._context: Context = (
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
            DEFAULT_CORRELATION_KEY,
            str(uuid.uuid4()),
        )

        # ---------------------------------------------------------------------
        # Metadata
        # ---------------------------------------------------------------------

        self._metadata: Metadata = (
            copy.deepcopy(metadata)
            if metadata
            else {}
        )

        self._hooks: Dict[
            str,
            List[Hook],
        ] = {}

        # ---------------------------------------------------------------------
        # Statistics
        # ---------------------------------------------------------------------

        self._statistics: Statistics = {

            "records": 0,

            "errors": 0,

            "latency": 0.0,

            "contexts": 0,

        }

    # =========================================================================
    # Identity
    # =========================================================================

    @property
    def id(self) -> str:
        """Unique logger identifier."""
        return self._id

    @property
    def name(self) -> str:
        """Logger name."""
        return self._name

    # =========================================================================
    # Runtime State
    # =========================================================================

    @property
    def enabled(self) -> bool:
        """Whether the logger is enabled."""
        return self._enabled

    @property
    def frozen(self) -> bool:
        """Whether the logger is frozen."""
        return self._frozen

    @property
    def closed(self) -> bool:
        """Whether the logger is closed."""
        return self._closed

    # =========================================================================
    # Logging Configuration
    # =========================================================================

    @property
    def level(self) -> str:
        """Current logging level."""
        return self._level

    @property
    def schema(self) -> str:
        """Structured logging schema."""
        return self._schema

    # =========================================================================
    # Context Configuration
    # =========================================================================

    @property
    def context(self) -> Context:
        """Current runtime context."""
        return self._context

    @property
    def trace_id(self) -> str:
        """Current trace identifier."""
        return self._context[
            DEFAULT_TRACE_KEY
        ]

    @property
    def span_id(self) -> str:
        """Current span identifier."""
        return self._context[
            DEFAULT_SPAN_KEY
        ]

    @property
    def correlation_id(self) -> str:
        """Current correlation identifier."""
        return self._context[
            DEFAULT_CORRELATION_KEY
        ]

    # =========================================================================
    # Metadata
    # =========================================================================

    @property
    def metadata(self) -> Metadata:
        """Logger metadata."""
        return self._metadata

    # =========================================================================
    # Statistics
    # =========================================================================

    @property
    def statistics(self) -> Statistics:
        """Runtime statistics."""
        return self._statistics

    @property
    def age(self) -> float:
        """Logger lifetime in seconds."""
        return (
            datetime.now(timezone.utc)
            - self.created_at
        ).total_seconds()

    @property
    def record_count(self) -> int:
        """Number of generated structured records."""
        return int(
            self._statistics.get(
                "records",
                0,
            )
        )

    # =========================================================================
    # Internal Helpers
    # =========================================================================

    def _touch(
        self,
    ) -> None:
        """Update modification timestamp."""

        self.updated_at = datetime.now(
            timezone.utc
        )

    def _record_latency(
        self,
        started: float,
    ) -> None:
        """Accumulate processing latency."""

        self._statistics["latency"] += (
            time.perf_counter()
            - started
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
        Globally unique logger identifier.
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
        Logger name.
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
        Whether the logger accepts new records.
        """

        return self._enabled


    # -------------------------------------------------------------------------
    # level
    # -------------------------------------------------------------------------

    @property
    def level(
        self,
    ) -> str:
        """
        Active logging level.
        """

        return self._level


    @level.setter
    def level(
        self,
        value: str,
    ) -> None:

        value = value.upper()

        if value not in SUPPORTED_LEVELS:

            raise ValueError(
                f"Unsupported level: {value}"
            )

        self._level = value

        self._touch()


    # -------------------------------------------------------------------------
    # schema
    # -------------------------------------------------------------------------

    @property
    def schema(
        self,
    ) -> str:
        """
        Structured logging schema.
        """

        return self._schema


    @schema.setter
    def schema(
        self,
        value: str,
    ) -> None:

        self._schema = str(value)

        self._touch()


    # -------------------------------------------------------------------------
    # context
    # -------------------------------------------------------------------------

    @property
    def context(
        self,
    ) -> Context:
        """
        Runtime logging context.
        """

        return self._context


    @context.setter
    def context(
        self,
        value: Context,
    ) -> None:

        self._context = copy.deepcopy(
            value
        )

        self._touch()


    # -------------------------------------------------------------------------
    # metadata
    # -------------------------------------------------------------------------

    @property
    def metadata(
        self,
    ) -> Metadata:
        """
        Logger metadata.
        """

        return self._metadata


    @metadata.setter
    def metadata(
        self,
        value: Metadata,
    ) -> None:

        self._metadata = copy.deepcopy(
            value
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

        return self._statistics


    # -------------------------------------------------------------------------
    # age
    # -------------------------------------------------------------------------

    @property
    def age(
        self,
    ) -> float:
        """
        Logger lifetime in seconds.
        """

        return (

            datetime.now(
                timezone.utc
            )

            -

            self.created_at

        ).total_seconds()


    # -------------------------------------------------------------------------
    # record_count
    # -------------------------------------------------------------------------

    @property
    def record_count(
        self,
    ) -> int:
        """
        Total structured log records.
        """

        return int(

            self._statistics.get(

                "records",

                0,

            )

        )
# =============================================================================
# Part 3. Structured Logging API
# =============================================================================

    # -------------------------------------------------------------------------
    # Log
    # -------------------------------------------------------------------------

    def log(
        self,
        message: str,
        *,
        level: Optional[str] = None,
        **extra: Any,
    ) -> StructuredRecord:
        """
        Create a structured log record.
        """

        if self._closed:

            raise RuntimeError(
                "Logger is closed."
            )

        if not self._enabled:

            raise RuntimeError(
                "Logger is disabled."
            )

        if self._frozen:

            raise RuntimeError(
                "Logger is frozen."
            )

        started = time.perf_counter()

        level = (
            level or self.level
        ).upper()

        if level not in SUPPORTED_LEVELS:

            raise ValueError(
                f"Unsupported level: {level}"
            )

        record = StructuredRecord(

            timestamp=datetime.now(
                timezone.utc
            ),

            level=level,

            logger=self.name,

            message=str(message),

            context=copy.deepcopy(
                self.context
            ),

            metadata=copy.deepcopy(
                self.metadata
            ),

            extra=copy.deepcopy(
                extra
            ),

        )

        self._last_record = record

        self._statistics["records"] += 1

        self._record_latency(
            started
        )

        self._touch()

        return record


    # -------------------------------------------------------------------------
    # Debug
    # -------------------------------------------------------------------------

    def debug(
        self,
        message: str,
        **extra: Any,
    ) -> StructuredRecord:

        return self.log(

            message,

            level="DEBUG",

            **extra,

        )


    # -------------------------------------------------------------------------
    # Info
    # -------------------------------------------------------------------------

    def info(
        self,
        message: str,
        **extra: Any,
    ) -> StructuredRecord:

        return self.log(

            message,

            level="INFO",

            **extra,

        )


    # -------------------------------------------------------------------------
    # Warning
    # -------------------------------------------------------------------------

    def warning(
        self,
        message: str,
        **extra: Any,
    ) -> StructuredRecord:

        return self.log(

            message,

            level="WARNING",

            **extra,

        )


    # -------------------------------------------------------------------------
    # Error
    # -------------------------------------------------------------------------

    def error(
        self,
        message: str,
        **extra: Any,
    ) -> StructuredRecord:

        return self.log(

            message,

            level="ERROR",

            **extra,

        )


    # -------------------------------------------------------------------------
    # Critical
    # -------------------------------------------------------------------------

    def critical(
        self,
        message: str,
        **extra: Any,
    ) -> StructuredRecord:

        return self.log(

            message,

            level="CRITICAL",

            **extra,

        )


    # -------------------------------------------------------------------------
    # Bind
    # -------------------------------------------------------------------------

    def bind(
        self,
        **values: Any,
    ) -> "StructuredLogger":
        """
        Bind values into the logging context.
        """

        self._context.update(
            values
        )

        self._statistics[
            "contexts"
        ] += len(values)

        self._touch()

        return self


    # -------------------------------------------------------------------------
    # Unbind
    # -------------------------------------------------------------------------

    def unbind(
        self,
        *keys: str,
    ) -> "StructuredLogger":
        """
        Remove context keys.
        """

        for key in keys:

            self._context.pop(
                key,
                None,
            )

        self._touch()

        return self


    # -------------------------------------------------------------------------
    # Context
    # -------------------------------------------------------------------------

    def context(
        self,
    ) -> Context:
        """
        Return a copy of the active context.
        """

        return copy.deepcopy(
            self._context
        )


    # -------------------------------------------------------------------------
    # Clear Context
    # -------------------------------------------------------------------------

    def clear_context(
        self,
        preserve_trace: bool = True,
    ) -> "StructuredLogger":
        """
        Clear runtime context.

        Parameters
        ----------
        preserve_trace:
            Keep trace_id, span_id and
            correlation_id if True.
        """

        if preserve_trace:

            trace = self.trace_id

            span = self.span_id

            correlation = self.correlation_id

            self._context.clear()

            self._context.update({

                DEFAULT_TRACE_KEY: trace,

                DEFAULT_SPAN_KEY: span,

                DEFAULT_CORRELATION_KEY: correlation,

            })

        else:

            self._context.clear()

        self._touch()

        return self
# =============================================================================
# Part 4. Context API
# =============================================================================

    # -------------------------------------------------------------------------
    # Set Context
    # -------------------------------------------------------------------------

    def set_context(
        self,
        key: str,
        value: Any,
    ) -> "StructuredLogger":
        """
        Set a context value.
        """

        self._context[key] = value

        self._statistics["contexts"] += 1

        self._touch()

        return self


    # -------------------------------------------------------------------------
    # Get Context
    # -------------------------------------------------------------------------

    def get_context(
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
    # Remove Context
    # -------------------------------------------------------------------------

    def remove_context(
        self,
        key: str,
    ) -> bool:
        """
        Remove a context value.

        Reserved tracing keys cannot be removed.
        """

        if key in (

            DEFAULT_TRACE_KEY,

            DEFAULT_SPAN_KEY,

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

            self._touch()

        return removed


    # -------------------------------------------------------------------------
    # Merge Context
    # -------------------------------------------------------------------------

    def merge_context(
        self,
        context: Mapping[str, Any],
    ) -> "StructuredLogger":
        """
        Merge another context mapping.
        """

        self._context.update(

            copy.deepcopy(

                dict(context)

            )

        )

        self._statistics["contexts"] += len(
            context
        )

        self._touch()

        return self


    # -------------------------------------------------------------------------
    # Trace ID
    # -------------------------------------------------------------------------

    def trace_id(
        self,
    ) -> str:
        """
        Return the active trace identifier.
        """

        return self._context.setdefault(

            DEFAULT_TRACE_KEY,

            str(uuid.uuid4()),

        )


    # -------------------------------------------------------------------------
    # Span ID
    # -------------------------------------------------------------------------

    def span_id(
        self,
    ) -> str:
        """
        Return the active span identifier.
        """

        return self._context.setdefault(

            DEFAULT_SPAN_KEY,

            str(uuid.uuid4()),

        )


    # -------------------------------------------------------------------------
    # Correlation ID
    # -------------------------------------------------------------------------

    def correlation_id(
        self,
    ) -> str:
        """
        Return the active correlation identifier.
        """

        return self._context.setdefault(

            DEFAULT_CORRELATION_KEY,

            str(uuid.uuid4()),

        )


    # -------------------------------------------------------------------------
    # New Trace
    # -------------------------------------------------------------------------

    def new_trace(
        self,
    ) -> Context:
        """
        Start a completely new trace.

        Generates new trace, span and
        correlation identifiers.
        """

        self._context[

            DEFAULT_TRACE_KEY

        ] = str(

            uuid.uuid4()

        )

        self._context[

            DEFAULT_SPAN_KEY

        ] = str(

            uuid.uuid4()

        )

        self._context[

            DEFAULT_CORRELATION_KEY

        ] = str(

            uuid.uuid4()

        )

        self._touch()

        return copy.deepcopy(
            self._context
        )
# =============================================================================
# Part 5. Lifecycle API
# =============================================================================

    # -------------------------------------------------------------------------
    # Enable
    # -------------------------------------------------------------------------

    def enable(
        self,
    ) -> "StructuredLogger":
        """
        Enable the structured logger.
        """

        if self._closed:

            raise RuntimeError(
                "Cannot enable a closed logger."
            )

        self._enabled = True

        self._touch()

        return self


    # -------------------------------------------------------------------------
    # Disable
    # -------------------------------------------------------------------------

    def disable(
        self,
    ) -> "StructuredLogger":
        """
        Disable the structured logger.

        New log records will not be accepted until
        enable() is called.
        """

        if self._closed:

            raise RuntimeError(
                "Cannot disable a closed logger."
            )

        self._enabled = False

        self._touch()

        return self


    # -------------------------------------------------------------------------
    # Freeze
    # -------------------------------------------------------------------------

    def freeze(
        self,
    ) -> "StructuredLogger":
        """
        Freeze the logger.

        Logging configuration and context become
        read-only while frozen.
        """

        if self._closed:

            raise RuntimeError(
                "Cannot freeze a closed logger."
            )

        self._frozen = True

        self._touch()

        return self


    # -------------------------------------------------------------------------
    # Unfreeze
    # -------------------------------------------------------------------------

    def unfreeze(
        self,
    ) -> "StructuredLogger":
        """
        Resume normal logger operation.
        """

        if self._closed:

            raise RuntimeError(
                "Cannot unfreeze a closed logger."
            )

        self._frozen = False

        self._touch()

        return self


    # -------------------------------------------------------------------------
    # Close
    # -------------------------------------------------------------------------

    def close(
        self,
    ) -> "StructuredLogger":
        """
        Close the logger permanently.

        Releases runtime state and prevents any
        further logging until reopened.
        """

        if self._closed:

            return self

        self._enabled = False

        self._frozen = False

        self._closed = True

        self._last_record = None

        self._touch()

        return self


    # -------------------------------------------------------------------------
    # Reopen
    # -------------------------------------------------------------------------

    def reopen(
        self,
    ) -> "StructuredLogger":
        """
        Reopen a previously closed logger.
        """

        if not self._closed:

            return self

        self._closed = False

        self._enabled = True

        self._frozen = False

        #
        # Ensure tracing context exists.
        #

        self._context.setdefault(

            DEFAULT_TRACE_KEY,

            str(uuid.uuid4()),

        )

        self._context.setdefault(

            DEFAULT_SPAN_KEY,

            str(uuid.uuid4()),

        )

        self._context.setdefault(

            DEFAULT_CORRELATION_KEY,

            str(uuid.uuid4()),

        )

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
    ) -> Dict[str, Any]:
        """
        Capture the current runtime state.
        """

        return {

            "id": self.id,

            "name": self.name,

            "enabled": self.enabled,

            "frozen": self.frozen,

            "closed": self.closed,

            "level": self.level,

            "schema": self.schema,

            "context": copy.deepcopy(
                self.context
            ),

            "metadata": copy.deepcopy(
                self.metadata
            ),

            "statistics": copy.deepcopy(
                self.statistics
            ),

            "created_at": self.created_at,

            "updated_at": self.updated_at,

        }


    # -------------------------------------------------------------------------
    # Restore
    # -------------------------------------------------------------------------

    def restore(
        self,
        snapshot: Mapping[str, Any],
    ) -> "StructuredLogger":
        """
        Restore runtime state from a snapshot.
        """

        if not isinstance(
            snapshot,
            Mapping,
        ):

            raise TypeError(
                "Snapshot must be a mapping."
            )

        self._name = snapshot.get(
            "name",
            self._name,
        )

        self._enabled = snapshot.get(
            "enabled",
            self._enabled,
        )

        self._frozen = snapshot.get(
            "frozen",
            self._frozen,
        )

        self._closed = snapshot.get(
            "closed",
            self._closed,
        )

        self._level = snapshot.get(
            "level",
            self._level,
        )

        self._schema = snapshot.get(
            "schema",
            self._schema,
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

        self.created_at = snapshot.get(
            "created_at",
            self.created_at,
        )

        self.updated_at = datetime.now(
            timezone.utc
        )

        return self


    # -------------------------------------------------------------------------
    # Clone
    # -------------------------------------------------------------------------

    def clone(
        self,
    ) -> "StructuredLogger":
        """
        Create a fully independent logger clone.
        """

        cloned = self.__class__(

            name=self.name,

            level=self.level,

            schema=self.schema,

            enabled=self.enabled,

            metadata=copy.deepcopy(
                self.metadata
            ),

            context=copy.deepcopy(
                self.context
            ),

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
    ) -> "StructuredLogger":
        """
        Alias of clone().
        """

        return self.clone()


    # -------------------------------------------------------------------------
    # Optimize
    # -------------------------------------------------------------------------

    def optimize(
        self,
    ) -> Dict[str, Any]:
        """
        Optimize runtime state.
        """

        removed = self.cleanup()

        return {

            "optimized": True,

            "removed": removed,

            "record_count": self.record_count,

            "context_size": len(
                self.context
            ),

        }


    # -------------------------------------------------------------------------
    # Cleanup
    # -------------------------------------------------------------------------

    def cleanup(
        self,
    ) -> int:
        """
        Remove transient runtime state.

        Returns
        -------
        int
            Number of runtime objects removed.
        """

        removed = 0

        if self._last_record is not None:

            self._last_record = None

            removed += 1

        self._touch()

        return removed


    # -------------------------------------------------------------------------
    # Compact
    # -------------------------------------------------------------------------

    def compact(
        self,
    ) -> Dict[str, Any]:
        """
        Compact metadata and context.

        Removes entries with None values.
        """

        metadata_before = len(
            self._metadata
        )

        context_before = len(
            self._context
        )

        self._metadata = {

            k: v

            for k, v in self._metadata.items()

            if v is not None

        }

        self._context = {

            k: v

            for k, v in self._context.items()

            if v is not None

        }

        removed = self.cleanup()

        self._touch()

        return {

            "optimized": True,

            "metadata_before": metadata_before,

            "metadata_after": len(
                self._metadata
            ),

            "context_before": context_before,

            "context_after": len(
                self._context
            ),

            "runtime_removed": removed,

        }
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

            "level": self.level,

            "schema": self.schema,

            "enabled": self.enabled,

            "record_count": self.record_count,

            "error_count": self.error_count,

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
        Return a complete diagnostic report.
        """

        return {

            "identity": {

                "id": self.id,

                "name": self.name,

            },

            "runtime": {

                "enabled": self.enabled,

                "frozen": self.frozen,

                "closed": self.closed,

                "level": self.level,

                "schema": self.schema,

            },

            "context": copy.deepcopy(

                self.context

            ),

            "metadata": copy.deepcopy(

                self.metadata

            ),

            "statistics": copy.deepcopy(

                self.statistics

            ),

            "diagnostics": {

                "record_count": self.record_count,

                "error_count": self.error_count,

                "uptime": self.uptime,

                "latency": self.latency,

                "health": self.health(),

            },

        }


    # -------------------------------------------------------------------------
    # Health
    # -------------------------------------------------------------------------

    def health(
        self,
    ) -> str:
        """
        Return runtime health.

        Returns
        -------
        HEALTHY
        WARNING
        DISABLED
        CLOSED
        """

        if self.closed:

            return "CLOSED"

        if not self.enabled:

            return "DISABLED"

        if self.error_count > 0:

            return "WARNING"

        return "HEALTHY"


    # -------------------------------------------------------------------------
    # Status
    # -------------------------------------------------------------------------

    def status(
        self,
    ) -> str:
        """
        Return runtime status.
        """

        if self.closed:

            return "closed"

        if self.frozen:

            return "frozen"

        if not self.enabled:

            return "disabled"

        return "running"


    # -------------------------------------------------------------------------
    # Record Count
    # -------------------------------------------------------------------------

    @property
    def record_count(
        self,
    ) -> int:
        """
        Number of structured records.
        """

        return int(

            self._statistics.get(

                "records",

                0,

            )

        )


    # -------------------------------------------------------------------------
    # Error Count
    # -------------------------------------------------------------------------

    @property
    def error_count(
        self,
    ) -> int:
        """
        Number of runtime errors.
        """

        return int(

            self._statistics.get(

                "errors",

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
        Logger uptime in seconds.
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
        Accumulated processing latency.
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
        Validate the entire StructuredLogger runtime.

        Returns
        -------
        bool
            True if every validation stage succeeds.
        """

        return (

            self.check_configuration()

            and

            self.validate_context()

            and

            self.check_integrity()

        )


    # -------------------------------------------------------------------------
    # Validate Record
    # -------------------------------------------------------------------------

    def validate_record(
        self,
        record: StructuredRecord,
    ) -> bool:
        """
        Validate a StructuredRecord.
        """

        if not isinstance(
            record,
            StructuredRecord,
        ):

            return False

        if not record.message:

            return False

        if record.level not in SUPPORTED_LEVELS:

            return False

        if not isinstance(
            record.context,
            dict,
        ):

            return False

        if not isinstance(
            record.metadata,
            dict,
        ):

            return False

        if not isinstance(
            record.extra,
            dict,
        ):

            return False

        return True


    # -------------------------------------------------------------------------
    # Validate Context
    # -------------------------------------------------------------------------

    def validate_context(
        self,
    ) -> bool:
        """
        Validate runtime context.
        """

        if not isinstance(
            self._context,
            dict,
        ):

            return False

        required = (

            DEFAULT_TRACE_KEY,

            DEFAULT_SPAN_KEY,

            DEFAULT_CORRELATION_KEY,

        )

        for key in required:

            value = self._context.get(
                key
            )

            if not isinstance(
                value,
                str,
            ):

                return False

            if not value.strip():

                return False

        return True


    # -------------------------------------------------------------------------
    # Check Configuration
    # -------------------------------------------------------------------------

    def check_configuration(
        self,
    ) -> bool:
        """
        Validate logger configuration.
        """

        if not self.name:

            return False

        if self.level not in SUPPORTED_LEVELS:

            return False

        if not isinstance(
            self.schema,
            str,
        ):

            return False

        if not self.schema.strip():

            return False

        if not isinstance(
            self.metadata,
            dict,
        ):

            return False

        if not isinstance(
            self.statistics,
            dict,
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
        # Closed logger must never remain enabled.
        #

        if self.closed and self.enabled:

            return False

        #
        # Frozen logger cannot be closed and enabled simultaneously.
        #

        if (

            self.closed

            and

            self.frozen

        ):

            return False

        #
        # Runtime counters.
        #

        if self.record_count < 0:

            return False

        if self.error_count < 0:

            return False

        if self.latency < 0.0:

            return False

        #
        # Metadata.
        #

        if not isinstance(
            self._metadata,
            dict,
        ):

            return False

        #
        # Hooks registry.
        #

        if not isinstance(
            self._hooks,
            dict,
        ):

            return False

        #
        # Last record consistency.
        #

        if (

            self._last_record is not None

            and

            not self.validate_record(
                self._last_record
            )

        ):

            return False

        return True
# =============================================================================
# Part 9. Events & Hooks
# =============================================================================

    # -------------------------------------------------------------------------
    # Before Log
    # -------------------------------------------------------------------------

    def before_log(
        self,
        message: str,
        level: str,
        **extra: Any,
    ) -> None:
        """
        Hook executed before a log record is created.
        """

        self.emit_event(

            "before_log",

            message=message,

            level=level,

            extra=extra,

        )


    # -------------------------------------------------------------------------
    # After Log
    # -------------------------------------------------------------------------

    def after_log(
        self,
        record: StructuredRecord,
    ) -> None:
        """
        Hook executed after a log record is created.
        """

        self.emit_event(

            "after_log",

            record=record,

        )


    # -------------------------------------------------------------------------
    # Before Context
    # -------------------------------------------------------------------------

    def before_context(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Fired before context modification.
        """

        self.emit_event(

            "before_context",

            key=key,

            value=value,

        )


    # -------------------------------------------------------------------------
    # After Context
    # -------------------------------------------------------------------------

    def after_context(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Fired after context modification.
        """

        self.emit_event(

            "after_context",

            key=key,

            value=value,

        )


    # -------------------------------------------------------------------------
    # Add Hook
    # -------------------------------------------------------------------------

    def add_hook(
        self,
        event: str,
        callback: Hook,
    ) -> "StructuredLogger":
        """
        Register an event hook.

        Parameters
        ----------
        event
            Event name.

        callback
            Callable executed when the event occurs.
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

        if not callbacks:

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
        Dispatch an event to all registered hooks.

        Hook failures are isolated and counted
        without interrupting logging.
        """

        callbacks = self._hooks.get(

            event,

            (),

        )

        for callback in tuple(callbacks):

            try:

                callback(

                    event=event,

                    logger=self,

                    **payload,

                )

            except Exception:

                self._statistics["errors"] += 1


    # -------------------------------------------------------------------------
    # Subscribe
    # -------------------------------------------------------------------------

    def subscribe(
        self,
        event: str,
        callback: Hook,
    ) -> "StructuredLogger":
        """
        Alias for add_hook().

        Example
        -------
        logger.subscribe(
            "after_log",
            handler,
        )
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
        Developer-friendly representation.
        """

        return (

            f"{self.__class__.__name__}("

            f"id={self.id!r}, "

            f"name={self.name!r}, "

            f"level={self.level!r}, "

            f"schema={self.schema!r}, "

            f"enabled={self.enabled}, "

            f"records={self.record_count}"

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

            f"[{self.level}] "

            f"{self.status()} "

            f"records={self.record_count}"

        )


    # -------------------------------------------------------------------------
    # __len__
    # -------------------------------------------------------------------------

    def __len__(
        self,
    ) -> int:
        """
        Number of structured records.
        """

        return self.record_count


    # -------------------------------------------------------------------------
    # __iter__
    # -------------------------------------------------------------------------

    def __iter__(
        self,
    ):
        """
        Iterate over runtime context.

        Example
        -------
        for key, value in logger:
            ...
        """

        return iter(
            self.context.items()
        )


    # -------------------------------------------------------------------------
    # __contains__
    # -------------------------------------------------------------------------

    def __contains__(
        self,
        key: str,
    ) -> bool:
        """
        Membership test for context keys.

        Example
        -------
        if "trace_id" in logger:
            ...
        """

        return key in self.context


    # -------------------------------------------------------------------------
    # __call__
    # -------------------------------------------------------------------------

    def __call__(
        self,
        message: str,
        *,
        level: Optional[str] = None,
        **extra: Any,
    ) -> StructuredRecord:
        """
        Callable logger.

        Equivalent to log().
        """

        return self.log(

            message,

            level=level,

            **extra,

        )


    # -------------------------------------------------------------------------
    # __copy__
    # -------------------------------------------------------------------------

    def __copy__(
        self,
    ) -> "StructuredLogger":
        """
        Create a shallow runtime copy.
        """

        copied = self.__class__(

            name=self.name,

            level=self.level,

            schema=self.schema,

            enabled=self.enabled,

            metadata=self.metadata.copy(),

            context=self.context.copy(),

        )

        copied._statistics = (

            self.statistics.copy()

        )

        copied._frozen = self.frozen

        copied._closed = self.closed

        copied.created_at = self.created_at

        copied.updated_at = self.updated_at

        return copied


    # -------------------------------------------------------------------------
    # __deepcopy__
    # -------------------------------------------------------------------------

    def __deepcopy__(
        self,
        memo: Dict[int, Any],
    ) -> "StructuredLogger":
        """
        Create a fully independent clone.
        """

        if id(self) in memo:

            return memo[id(self)]

        cloned = self.clone()

        memo[id(self)] = cloned

        return cloned
                                                                                
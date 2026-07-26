"""
SciOS-NG Logging Handlers

Foundation for all logging handlers.
"""

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
    Optional,
    TypeAlias,
)

from .record import LogRecord

# =============================================================================
# Constants
# =============================================================================

DEFAULT_HANDLER_NAME = "handler"

DEFAULT_LEVEL = "INFO"

DEFAULT_ENABLED = True

DEFAULT_FROZEN = False

DEFAULT_CLOSED = False

# =============================================================================
# Type Aliases
# =============================================================================

Metadata: TypeAlias = Dict[str, Any]

Statistics: TypeAlias = Dict[str, Any]

Hook: TypeAlias = Callable[..., Any]

FormatterType: TypeAlias = Any

# =============================================================================
# Handler Result
# =============================================================================


@dataclass(slots=True)
class HandlerResult:
    """
    Result returned by a handler operation.
    """

    success: bool

    record: Optional[LogRecord] = None

    output: Any = None

    message: str = ""

    elapsed: float = 0.0

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# =============================================================================
# Log Handler
# =============================================================================


class LogHandler:
    """
    Base class of every SciOS-NG log handler.

    Examples
    --------
    - ConsoleHandler
    - FileHandler
    - MemoryHandler
    - HTTPHandler
    - KafkaHandler
    - OTLPHandler
    """

    # -------------------------------------------------------------------------
    # Constructor
    # -------------------------------------------------------------------------

    def __init__(
        self,
        name: str = DEFAULT_HANDLER_NAME,
        *,
        level: str = DEFAULT_LEVEL,
        formatter: Optional[FormatterType] = None,
        enabled: bool = DEFAULT_ENABLED,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> None:

        # -----------------------------------------------------------------
        # Identity
        # -----------------------------------------------------------------

        self._id = str(
            uuid.uuid4()
        )

        self._name = name

        self.created_at = datetime.now(
            timezone.utc
        )

        self.updated_at = self.created_at

        # -----------------------------------------------------------------
        # Runtime State
        # -----------------------------------------------------------------

        self._enabled = enabled

        self._frozen = DEFAULT_FROZEN

        self._closed = DEFAULT_CLOSED

        # -----------------------------------------------------------------
        # Handler Configuration
        # -----------------------------------------------------------------

        self._level = str(level).upper()

        self._formatter = formatter

        self._stream = None

        self._buffer: List[Any] = []

        self._hooks: Dict[str, List[Hook]] = {}

        # -----------------------------------------------------------------
        # Metadata
        # -----------------------------------------------------------------

        self._metadata: Metadata = dict(
            metadata or {}
        )

        # -----------------------------------------------------------------
        # Statistics
        # -----------------------------------------------------------------

        self._statistics: Statistics = {

            "emit": 0,

            "write": 0,

            "flush": 0,

            "errors": 0,

            "latency": 0.0,

        }

    # -------------------------------------------------------------------------
    # Foundation Helpers
    # -------------------------------------------------------------------------

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
        Record elapsed runtime.
        """

        self._statistics["latency"] += (

            time.perf_counter()

            -

            started

        )
# =============================================================================
# Part 2. Properties
# =============================================================================

    # -------------------------------------------------------------------------
    # ID
    # -------------------------------------------------------------------------

    @property
    def id(
        self,
    ) -> str:
        """
        Unique handler identifier.
        """

        return self._id

    # -------------------------------------------------------------------------
    # Name
    # -------------------------------------------------------------------------

    @property
    def name(
        self,
    ) -> str:
        """
        Handler name.
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
    # Enabled
    # -------------------------------------------------------------------------

    @property
    def enabled(
        self,
    ) -> bool:
        """
        Whether this handler is enabled.
        """

        return self._enabled

    # -------------------------------------------------------------------------
    # Level
    # -------------------------------------------------------------------------

    @property
    def level(
        self,
    ) -> str:
        """
        Minimum logging level accepted by this handler.
        """

        return self._level

    @level.setter
    def level(
        self,
        value: str,
    ) -> None:

        self._level = str(value).upper()

        self._touch()

    # -------------------------------------------------------------------------
    # Formatter
    # -------------------------------------------------------------------------

    @property
    def formatter(
        self,
    ) -> Optional[FormatterType]:
        """
        Associated formatter.
        """

        return self._formatter

    @formatter.setter
    def formatter(
        self,
        value: Optional[FormatterType],
    ) -> None:

        self._formatter = value

        self._touch()

    # -------------------------------------------------------------------------
    # Metadata
    # -------------------------------------------------------------------------

    @property
    def metadata(
        self,
    ) -> Metadata:
        """
        Handler metadata.
        """

        return self._metadata

    # -------------------------------------------------------------------------
    # Statistics
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
    # Age
    # -------------------------------------------------------------------------

    @property
    def age(
        self,
    ) -> float:
        """
        Handler lifetime in seconds.
        """

        return (

            datetime.now(
                timezone.utc
            )

            -

            self.created_at

        ).total_seconds()

    # -------------------------------------------------------------------------
    # Emit Count
    # -------------------------------------------------------------------------

    @property
    def emit_count(
        self,
    ) -> int:
        """
        Total number of emitted log records.
        """

        return self._statistics.get(
            "emit",
            0,
        )
# =============================================================================
# Part 3. Handler API
# =============================================================================

    # -------------------------------------------------------------------------
    # Emit
    # -------------------------------------------------------------------------

    def emit(
        self,
        record: LogRecord,
    ) -> HandlerResult:
        """
        Emit a log record.

        Entry point used by Logger.
        """

        if not self._enabled:
            return HandlerResult(
                success=False,
                record=record,
                message="Handler is disabled.",
            )

        if self._closed:
            return HandlerResult(
                success=False,
                record=record,
                message="Handler is closed.",
            )

        started = time.perf_counter()

        try:

            self.before_emit(record)

            result = self.handle(record)

            self._statistics["emit"] += 1

            self.after_emit(record)

            return result

        except Exception as exc:

            self._statistics["errors"] += 1

            return HandlerResult(
                success=False,
                record=record,
                message=str(exc),
            )

        finally:

            self._record_latency(started)

    # -------------------------------------------------------------------------
    # Handle
    # -------------------------------------------------------------------------

    def handle(
        self,
        record: LogRecord,
    ) -> HandlerResult:
        """
        Handle a log record.

        Default implementation delegates to process().
        """

        return self.process(record)

    # -------------------------------------------------------------------------
    # Process
    # -------------------------------------------------------------------------

    def process(
        self,
        record: LogRecord,
    ) -> HandlerResult:
        """
        Format and write a log record.
        """

        output = record

        if self._formatter is not None:

            if hasattr(
                self._formatter,
                "format_record",
            ):

                output = self._formatter.format_record(
                    record
                )

            elif hasattr(
                self._formatter,
                "format",
            ):

                output = self._formatter.format(
                    record
                )

        return self.write(output)

    # -------------------------------------------------------------------------
    # Write
    # -------------------------------------------------------------------------

    def write(
        self,
        output: Any,
    ) -> HandlerResult:
        """
        Write formatted output.

        Base implementation buffers the output.

        Concrete handlers should override this method.
        """

        self.before_write(output)

        self._buffer.append(output)

        self._statistics["write"] += 1

        self.after_write(output)

        return HandlerResult(
            success=True,
            output=output,
            message="Record written.",
        )

    # -------------------------------------------------------------------------
    # Flush
    # -------------------------------------------------------------------------

    def flush(
        self,
    ) -> HandlerResult:
        """
        Flush buffered records.
        """

        count = len(self._buffer)

        self._buffer.clear()

        self._statistics["flush"] += 1

        return HandlerResult(
            success=True,
            output=count,
            message=f"Flushed {count} record(s).",
        )

    # -------------------------------------------------------------------------
    # Close Stream
    # -------------------------------------------------------------------------

    def close_stream(
        self,
    ) -> None:
        """
        Close the underlying stream if present.
        """

        stream = self._stream

        if stream is None:

            return

        if hasattr(
            stream,
            "close",
        ):

            stream.close()

        self._stream = None

    # -------------------------------------------------------------------------
    # Reset
    # -------------------------------------------------------------------------

    def reset(
        self,
    ) -> "LogHandler":
        """
        Reset runtime statistics.
        """

        self._statistics = {

            "emit": 0,

            "write": 0,

            "flush": 0,

            "errors": 0,

            "latency": 0.0,

        }

        self._touch()

        return self

    # -------------------------------------------------------------------------
    # Clear
    # -------------------------------------------------------------------------

    def clear(
        self,
    ) -> "LogHandler":
        """
        Clear internal buffers.
        """

        self._buffer.clear()

        self._touch()

        return self
# =============================================================================
# Part 4. Formatter API
# =============================================================================

    # -------------------------------------------------------------------------
    # Set Formatter
    # -------------------------------------------------------------------------

    def set_formatter(
        self,
        formatter: FormatterType,
    ) -> "LogHandler":
        """
        Attach a formatter to this handler.
        """

        if self._closed:
            raise RuntimeError(
                "Handler is closed."
            )

        if self._frozen:
            raise RuntimeError(
                "Handler is frozen."
            )

        self._formatter = formatter

        self._touch()

        return self

    # -------------------------------------------------------------------------
    # Formatter
    # -------------------------------------------------------------------------

    def formatter(
        self,
    ) -> Optional[FormatterType]:
        """
        Return the current formatter.
        """

        return self._formatter

    # -------------------------------------------------------------------------
    # Has Formatter
    # -------------------------------------------------------------------------

    def has_formatter(
        self,
    ) -> bool:
        """
        Return True if a formatter is attached.
        """

        return self._formatter is not None

    # -------------------------------------------------------------------------
    # Remove Formatter
    # -------------------------------------------------------------------------

    def remove_formatter(
        self,
    ) -> Optional[FormatterType]:
        """
        Remove and return the current formatter.
        """

        if self._closed:
            raise RuntimeError(
                "Handler is closed."
            )

        if self._frozen:
            raise RuntimeError(
                "Handler is frozen."
            )

        formatter = self._formatter

        self._formatter = None

        self._touch()

        return formatter

    # -------------------------------------------------------------------------
    # Format
    # -------------------------------------------------------------------------

    def format(
        self,
        record: LogRecord,
    ) -> Any:
        """
        Format a log record.

        If no formatter is attached, the original
        record is returned.
        """

        if self._formatter is None:

            return record

        if hasattr(
            self._formatter,
            "format",
        ):

            return self._formatter.format(
                record
            )

        raise TypeError(
            "Formatter does not implement "
            "'format()'."
        )

    # -------------------------------------------------------------------------
    # Format Record
    # -------------------------------------------------------------------------

    def format_record(
        self,
        record: LogRecord,
    ) -> Any:
        """
        Format a LogRecord.

        Prefer format_record() when available,
        otherwise fall back to format().
        """

        if self._formatter is None:

            return record

        if hasattr(
            self._formatter,
            "format_record",
        ):

            return self._formatter.format_record(
                record
            )

        return self.format(
            record
        )
# =============================================================================
# Part 5. Lifecycle API
# =============================================================================

    # -------------------------------------------------------------------------
    # Enable
    # -------------------------------------------------------------------------

    def enable(
        self,
    ) -> "LogHandler":
        """
        Enable this handler.
        """

        if self._closed:
            raise RuntimeError(
                "Cannot enable a closed handler."
            )

        self._enabled = True

        self._touch()

        return self

    # -------------------------------------------------------------------------
    # Disable
    # -------------------------------------------------------------------------

    def disable(
        self,
    ) -> "LogHandler":
        """
        Disable this handler.
        """

        self._enabled = False

        self._touch()

        return self

    # -------------------------------------------------------------------------
    # Freeze
    # -------------------------------------------------------------------------

    def freeze(
        self,
    ) -> "LogHandler":
        """
        Freeze handler configuration.

        A frozen handler continues processing log records but its
        configuration cannot be modified until unfrozen.
        """

        if self._closed:
            raise RuntimeError(
                "Handler is closed."
            )

        self._frozen = True

        self._touch()

        return self

    # -------------------------------------------------------------------------
    # Unfreeze
    # -------------------------------------------------------------------------

    def unfreeze(
        self,
    ) -> "LogHandler":
        """
        Unfreeze handler configuration.
        """

        if self._closed:
            raise RuntimeError(
                "Handler is closed."
            )

        self._frozen = False

        self._touch()

        return self

    # -------------------------------------------------------------------------
    # Close
    # -------------------------------------------------------------------------

    def close(
        self,
    ) -> "LogHandler":
        """
        Close this handler and release runtime resources.
        """

        if self._closed:
            return self

        try:

            self.flush()

        finally:

            self.close_stream()

            self._enabled = False

            self._closed = True

            self._touch()

        return self

    # -------------------------------------------------------------------------
    # Reopen
    # -------------------------------------------------------------------------

    def reopen(
        self,
    ) -> "LogHandler":
        """
        Reopen a previously closed handler.
        """

        self._closed = False

        self._enabled = True

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
        Create a snapshot of the current runtime state.
        """

        return {

            "id": self._id,

            "name": self._name,

            "enabled": self._enabled,

            "frozen": self._frozen,

            "closed": self._closed,

            "level": self._level,

            "formatter": self._formatter,

            "metadata": copy.deepcopy(
                self._metadata
            ),

            "statistics": copy.deepcopy(
                self._statistics
            ),

            "buffer": copy.deepcopy(
                self._buffer
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
    ) -> "LogHandler":
        """
        Restore the handler from a runtime snapshot.
        """

        self._id = snapshot.get(
            "id",
            self._id,
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

        self._formatter = snapshot.get(
            "formatter",
            self._formatter,
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

        self._buffer = copy.deepcopy(
            snapshot.get(
                "buffer",
                [],
            )
        )

        self.created_at = snapshot.get(
            "created_at",
            self.created_at,
        )

        self.updated_at = snapshot.get(
            "updated_at",
            self.updated_at,
        )

        self._touch()

        return self

    # -------------------------------------------------------------------------
    # Clone
    # -------------------------------------------------------------------------

    def clone(
        self,
    ) -> "LogHandler":
        """
        Create a deep clone of this handler.
        """

        cloned = self.__class__(

            name=self._name,

            level=self._level,

            formatter=self._formatter,

            enabled=self._enabled,

            metadata=copy.deepcopy(
                self._metadata
            ),

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
    ) -> "LogHandler":
        """
        Alias of clone().
        """

        return self.clone()

    # -------------------------------------------------------------------------
    # Optimize
    # -------------------------------------------------------------------------

    def optimize(
        self,
    ) -> "LogHandler":
        """
        Optimize internal runtime structures.
        """

        self._buffer = [

            item

            for item in self._buffer

            if item is not None

        ]

        self._touch()

        return self

    # -------------------------------------------------------------------------
    # Cleanup
    # -------------------------------------------------------------------------

    def cleanup(
        self,
    ) -> "LogHandler":
        """
        Cleanup temporary runtime data.
        """

        self._statistics["latency"] = 0.0

        self._touch()

        return self

    # -------------------------------------------------------------------------
    # Compact
    # -------------------------------------------------------------------------

    def compact(
        self,
    ) -> "LogHandler":
        """
        Compact the internal buffer.

        Removes duplicated consecutive entries while
        preserving order.
        """

        compacted = []

        previous = object()

        for item in self._buffer:

            if item != previous:

                compacted.append(item)

                previous = item

        self._buffer = compacted

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
        Return a concise summary of this handler.
        """

        return {

            "id": self.id,

            "name": self.name,

            "enabled": self.enabled,

            "level": self.level,

            "emit_count": self.emit_count,

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
        Return a detailed runtime report.
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

                "level": self._level,

            },

            "formatter": {

                "attached": self.has_formatter(),

                "type": (
                    type(self._formatter).__name__
                    if self._formatter is not None
                    else None
                ),

            },

            "buffer_size": len(
                self._buffer
            ),

            "statistics": copy.deepcopy(
                self._statistics
            ),

            "metadata": copy.deepcopy(
                self._metadata
            ),

            "health": self.health(),

        }

    # -------------------------------------------------------------------------
    # Health
    # -------------------------------------------------------------------------

    def health(
        self,
    ) -> Dict[str, Any]:
        """
        Return handler health information.
        """

        healthy = (

            self._enabled

            and

            not self._closed

            and

            self.error_count == 0

        )

        return {

            "healthy": healthy,

            "status": self.status(),

            "emit_count": self.emit_count,

            "error_count": self.error_count,

            "uptime": self.uptime,

            "latency": self.latency,

        }

    # -------------------------------------------------------------------------
    # Status
    # -------------------------------------------------------------------------

    def status(
        self,
    ) -> str:
        """
        Return current handler status.
        """

        if self._closed:

            return "closed"

        if self._frozen:

            return "frozen"

        if not self._enabled:

            return "disabled"

        return "active"

    # -------------------------------------------------------------------------
    # Emit Count
    # -------------------------------------------------------------------------

    @property
    def emit_count(
        self,
    ) -> int:
        """
        Total emitted records.
        """

        return self._statistics.get(
            "emit",
            0,
        )

    # -------------------------------------------------------------------------
    # Error Count
    # -------------------------------------------------------------------------

    @property
    def error_count(
        self,
    ) -> int:
        """
        Total runtime errors.
        """

        return self._statistics.get(
            "errors",
            0,
        )

    # -------------------------------------------------------------------------
    # Uptime
    # -------------------------------------------------------------------------

    @property
    def uptime(
        self,
    ) -> float:
        """
        Handler uptime in seconds.
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
        Average emit latency in seconds.
        """

        operations = max(
            self.emit_count,
            1,
        )

        return (

            self._statistics.get(
                "latency",
                0.0,
            )

            /

            operations

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
        Validate the entire handler.

        Returns
        -------
        bool
            True if both configuration and runtime integrity are valid.
        """

        return (

            self.check_configuration()

            and

            self.check_integrity()

        )

    # -------------------------------------------------------------------------
    # Validate Record
    # -------------------------------------------------------------------------

    def validate_record(
        self,
        record: LogRecord,
    ) -> bool:
        """
        Validate an incoming log record.
        """

        if not isinstance(
            record,
            LogRecord,
        ):

            return False

        if not getattr(
            record,
            "message",
            None,
        ):

            return False

        if not getattr(
            record,
            "level",
            None,
        ):

            return False

        return True

    # -------------------------------------------------------------------------
    # Validate Formatter
    # -------------------------------------------------------------------------

    def validate_formatter(
        self,
        formatter: Optional[FormatterType],
    ) -> bool:
        """
        Validate a formatter instance.
        """

        if formatter is None:

            return True

        if hasattr(
            formatter,
            "format_record",
        ):

            return True

        if hasattr(
            formatter,
            "format",
        ):

            return True

        return False

    # -------------------------------------------------------------------------
    # Check Configuration
    # -------------------------------------------------------------------------

    def check_configuration(
        self,
    ) -> bool:
        """
        Validate handler configuration.
        """

        if not isinstance(
            self._name,
            str,
        ):

            return False

        if not isinstance(
            self._level,
            str,
        ):

            return False

        if not isinstance(
            self._enabled,
            bool,
        ):

            return False

        if not self.validate_formatter(
            self._formatter,
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
        Validate internal runtime integrity.
        """

        required_statistics = {

            "emit",

            "write",

            "flush",

            "errors",

            "latency",

        }

        if not isinstance(
            self._metadata,
            dict,
        ):

            return False

        if not isinstance(
            self._statistics,
            dict,
        ):

            return False

        if not required_statistics.issubset(
            self._statistics.keys()
        ):

            return False

        if not isinstance(
            self._buffer,
            list,
        ):

            return False

        if not isinstance(
            self._hooks,
            dict,
        ):

            return False

        if self.created_at is None:

            return False

        if self.updated_at is None:

            return False

        return True
# =============================================================================
# Part 9. Events & Hooks
# =============================================================================

    # -------------------------------------------------------------------------
    # Before Emit
    # -------------------------------------------------------------------------

    def before_emit(
        self,
        record: LogRecord,
    ) -> None:
        """
        Emit hook before processing a log record.
        """

        self.emit_event(
            "before_emit",
            handler=self,
            record=record,
        )

    # -------------------------------------------------------------------------
    # After Emit
    # -------------------------------------------------------------------------

    def after_emit(
        self,
        record: LogRecord,
    ) -> None:
        """
        Emit hook after processing a log record.
        """

        self.emit_event(
            "after_emit",
            handler=self,
            record=record,
        )

    # -------------------------------------------------------------------------
    # Before Write
    # -------------------------------------------------------------------------

    def before_write(
        self,
        output: Any,
    ) -> None:
        """
        Emit hook before writing formatted output.
        """

        self.emit_event(
            "before_write",
            handler=self,
            output=output,
        )

    # -------------------------------------------------------------------------
    # After Write
    # -------------------------------------------------------------------------

    def after_write(
        self,
        output: Any,
    ) -> None:
        """
        Emit hook after writing formatted output.
        """

        self.emit_event(
            "after_write",
            handler=self,
            output=output,
        )

    # -------------------------------------------------------------------------
    # Add Hook
    # -------------------------------------------------------------------------

    def add_hook(
        self,
        event: str,
        callback: Hook,
    ) -> "LogHandler":
        """
        Register an event hook.
        """

        self._hooks.setdefault(
            event,
            [],
        ).append(callback)

        self._touch()

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
            event,
        )

        if callbacks is None:

            return False

        try:

            callbacks.remove(
                callback,
            )

            if not callbacks:

                self._hooks.pop(
                    event,
                    None,
                )

            self._touch()

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
        Dispatch an event to all subscribed hooks.
        """

        callbacks = self._hooks.get(
            event,
            [],
        )

        for callback in tuple(callbacks):

            try:

                callback(
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
    ) -> "LogHandler":
        """
        Alias of add_hook().
        """

        return self.add_hook(
            event,
            callback,
        )
# =============================================================================
# Part 10. Python Protocols
# =============================================================================

    # -------------------------------------------------------------------------
    # Representation
    # -------------------------------------------------------------------------

    def __repr__(
        self,
    ) -> str:
        """
        Return developer representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"id={self.id!r}, "
            f"name={self.name!r}, "
            f"level={self.level!r}, "
            f"enabled={self.enabled}, "
            f"formatter={type(self._formatter).__name__ if self._formatter else None!r})"
        )

    # -------------------------------------------------------------------------
    # String
    # -------------------------------------------------------------------------

    def __str__(
        self,
    ) -> str:
        """
        Return human-readable representation.
        """

        state = self.status()

        return (
            f"{self.name}"
            f" [{self.level}] "
            f"({state})"
        )

    # -------------------------------------------------------------------------
    # Length
    # -------------------------------------------------------------------------

    def __len__(
        self,
    ) -> int:
        """
        Return buffered record count.
        """

        return len(
            self._buffer
        )

    # -------------------------------------------------------------------------
    # Iterator
    # -------------------------------------------------------------------------

    def __iter__(
        self,
    ):
        """
        Iterate over buffered records.
        """

        return iter(
            self._buffer
        )

    # -------------------------------------------------------------------------
    # Contains
    # -------------------------------------------------------------------------

    def __contains__(
        self,
        item: Any,
    ) -> bool:
        """
        Support 'in' operator for buffered records.
        """

        return item in self._buffer

    # -------------------------------------------------------------------------
    # Callable
    # -------------------------------------------------------------------------

    def __call__(
        self,
        record: LogRecord,
    ) -> HandlerResult:
        """
        Allow handler(record) syntax.
        """

        return self.emit(
            record
        )

    # -------------------------------------------------------------------------
    # Copy
    # -------------------------------------------------------------------------

    def __copy__(
        self,
    ) -> "LogHandler":
        """
        Return a shallow copy.
        """

        copied = self.__class__(
            name=self._name,
            level=self._level,
            formatter=self._formatter,
            enabled=self._enabled,
            metadata=copy.copy(
                self._metadata
            ),
        )

        copied.restore(
            self.snapshot()
        )

        return copied

    # -------------------------------------------------------------------------
    # Deep Copy
    # -------------------------------------------------------------------------

    def __deepcopy__(
        self,
        memo: Dict[int, Any],
    ) -> "LogHandler":
        """
        Return a deep copy.
        """

        if id(self) in memo:

            return memo[id(self)]

        cloned = self.clone()

        memo[id(self)] = cloned

        return cloned                                                                        
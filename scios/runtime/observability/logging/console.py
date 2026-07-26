"""
SciOS-NG Console Handler

Console-based log handler.
"""

from __future__ import annotations

# =============================================================================
# Imports
# =============================================================================

import copy
import sys
import time
import uuid

from datetime import datetime, timezone
from typing import (
    Any,
    Dict,
    Mapping,
    Optional,
    TextIO,
    TypeAlias,
)

from .handlers import (
    HandlerResult,
    LogHandler,
)
from .record import LogRecord

# =============================================================================
# Constants
# =============================================================================

DEFAULT_NAME = "console"

DEFAULT_LEVEL = "INFO"

DEFAULT_STREAM = sys.stdout

DEFAULT_COLOR = True

DEFAULT_ENABLED = True

# =============================================================================
# Type Aliases
# =============================================================================

Metadata: TypeAlias = Dict[str, Any]

Statistics: TypeAlias = Dict[str, Any]

StreamType: TypeAlias = TextIO

# =============================================================================
# Console Handler
# =============================================================================


class ConsoleHandler(LogHandler):
    """
    Console log handler.

    Writes formatted log records to stdout or stderr.
    """

    # -------------------------------------------------------------------------
    # Constructor
    # -------------------------------------------------------------------------

    def __init__(
        self,
        name: str = DEFAULT_NAME,
        *,
        level: str = DEFAULT_LEVEL,
        formatter: Optional[Any] = None,
        stream: StreamType = DEFAULT_STREAM,
        color: bool = DEFAULT_COLOR,
        enabled: bool = DEFAULT_ENABLED,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> None:

        super().__init__(
            name=name,
            level=level,
            formatter=formatter,
            enabled=enabled,
            metadata=metadata,
        )

        # ---------------------------------------------------------------------
        # Identity
        # ---------------------------------------------------------------------

        self._id = str(
            uuid.uuid4()
        )

        self._name = name

        self.created_at = datetime.now(
            timezone.utc
        )

        self.updated_at = self.created_at

        # ---------------------------------------------------------------------
        # Runtime State
        # ---------------------------------------------------------------------

        self._enabled = enabled

        self._frozen = False

        self._closed = False

        # ---------------------------------------------------------------------
        # Console Configuration
        # ---------------------------------------------------------------------

        self._stream: StreamType = stream

        self._color = color

        self._buffer = []

        # ---------------------------------------------------------------------
        # Metadata
        # ---------------------------------------------------------------------

        self._metadata: Metadata = dict(
            metadata or {}
        )

        # ---------------------------------------------------------------------
        # Statistics
        # ---------------------------------------------------------------------

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
        Record runtime latency.
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
        """
        Update handler name.
        """

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
        Minimum logging level.
        """

        return self._level

    @level.setter
    def level(
        self,
        value: str,
    ) -> None:
        """
        Update logging level.
        """

        self._level = str(value).upper()

        self._touch()

    # -------------------------------------------------------------------------
    # Stream
    # -------------------------------------------------------------------------

    @property
    def stream(
        self,
    ) -> StreamType:
        """
        Current output stream.
        """

        return self._stream

    @stream.setter
    def stream(
        self,
        value: StreamType,
    ) -> None:
        """
        Update output stream.
        """

        self._stream = value

        self._touch()

    # -------------------------------------------------------------------------
    # Color
    # -------------------------------------------------------------------------

    @property
    def color(
        self,
    ) -> bool:
        """
        Whether ANSI color output is enabled.
        """

        return self._color

    @color.setter
    def color(
        self,
        value: bool,
    ) -> None:
        """
        Enable or disable colored output.
        """

        self._color = bool(value)

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
            - self.created_at
        ).total_seconds()

    # -------------------------------------------------------------------------
    # Write Count
    # -------------------------------------------------------------------------

    @property
    def write_count(
        self,
    ) -> int:
        """
        Number of successful console writes.
        """

        return self._statistics.get(
            "write",
            0,
        )
# =============================================================================
# Part 3. Console API
# =============================================================================

    # -------------------------------------------------------------------------
    # Write
    # -------------------------------------------------------------------------

    def write(
        self,
        output: Any,
    ) -> HandlerResult:
        """
        Write data to the configured console stream.
        """

        if not self._enabled:
            return HandlerResult(
                success=False,
                output=None,
                message="Console handler is disabled.",
            )

        if self._closed:
            return HandlerResult(
                success=False,
                output=None,
                message="Console handler is closed.",
            )

        started = time.perf_counter()

        try:

            self.before_write(output)

            text = str(output)

            self._stream.write(text)

            self._statistics["write"] += 1

            self.after_write(output)

            return HandlerResult(
                success=True,
                output=text,
                message="Console write completed.",
            )

        except Exception as exc:

            self._statistics["errors"] += 1

            return HandlerResult(
                success=False,
                output=None,
                message=str(exc),
            )

        finally:

            self._record_latency(started)

    # -------------------------------------------------------------------------
    # Writeln
    # -------------------------------------------------------------------------

    def writeln(
        self,
        output: Any,
    ) -> HandlerResult:
        """
        Write a line to the console.
        """

        return self.write(
            f"{output}\n"
        )

    # -------------------------------------------------------------------------
    # Print
    # -------------------------------------------------------------------------

    def print(
        self,
        *values: Any,
        sep: str = " ",
        end: str = "\n",
    ) -> HandlerResult:
        """
        Console equivalent of Python's print().
        """

        text = sep.join(
            map(str, values)
        ) + end

        return self.write(
            text
        )

    # -------------------------------------------------------------------------
    # Print Record
    # -------------------------------------------------------------------------

    def print_record(
        self,
        record: LogRecord,
    ) -> HandlerResult:
        """
        Format and print a LogRecord.
        """

        formatted = self.format_record(
            record
        )

        return self.writeln(
            formatted
        )

    # -------------------------------------------------------------------------
    # Flush
    # -------------------------------------------------------------------------

    def flush(
        self,
    ) -> HandlerResult:
        """
        Flush the output stream.
        """

        try:

            if hasattr(
                self._stream,
                "flush",
            ):

                self._stream.flush()

            self._statistics["flush"] += 1

            return HandlerResult(
                success=True,
                message="Console flushed.",
            )

        except Exception as exc:

            self._statistics["errors"] += 1

            return HandlerResult(
                success=False,
                message=str(exc),
            )

    # -------------------------------------------------------------------------
    # Clear Screen
    # -------------------------------------------------------------------------

    def clear_screen(
        self,
    ) -> HandlerResult:
        """
        Clear the terminal screen using ANSI escape codes.
        """

        try:

            self._stream.write(
                "\033[2J\033[H"
            )

            self.flush()

            return HandlerResult(
                success=True,
                message="Console cleared.",
            )

        except Exception as exc:

            self._statistics["errors"] += 1

            return HandlerResult(
                success=False,
                message=str(exc),
            )

    # -------------------------------------------------------------------------
    # Reset
    # -------------------------------------------------------------------------

    def reset(
        self,
    ) -> "ConsoleHandler":
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
    ) -> "ConsoleHandler":
        """
        Clear runtime buffers.
        """

        self._buffer.clear()

        self._touch()

        return self
# =============================================================================
# Part 4. Stream API
# =============================================================================

    # -------------------------------------------------------------------------
    # Set Stream
    # -------------------------------------------------------------------------

    def set_stream(
        self,
        stream: StreamType,
    ) -> "ConsoleHandler":
        """
        Set the output stream.
        """

        if self._closed:
            raise RuntimeError(
                "Console handler is closed."
            )

        if self._frozen:
            raise RuntimeError(
                "Console handler is frozen."
            )

        self._stream = stream

        self._touch()

        return self

    # -------------------------------------------------------------------------
    # Stream
    # -------------------------------------------------------------------------

    def stream(
        self,
    ) -> Optional[StreamType]:
        """
        Return the current output stream.
        """

        return self._stream

    # -------------------------------------------------------------------------
    # Has Stream
    # -------------------------------------------------------------------------

    def has_stream(
        self,
    ) -> bool:
        """
        Return True if a valid output stream is configured.
        """

        return self._stream is not None

    # -------------------------------------------------------------------------
    # Use Stdout
    # -------------------------------------------------------------------------

    def use_stdout(
        self,
    ) -> "ConsoleHandler":
        """
        Switch output to sys.stdout.
        """

        return self.set_stream(
            sys.stdout
        )

    # -------------------------------------------------------------------------
    # Use Stderr
    # -------------------------------------------------------------------------

    def use_stderr(
        self,
    ) -> "ConsoleHandler":
        """
        Switch output to sys.stderr.
        """

        return self.set_stream(
            sys.stderr
        )

    # -------------------------------------------------------------------------
    # Close Stream
    # -------------------------------------------------------------------------

    def close_stream(
        self,
    ) -> "ConsoleHandler":
        """
        Close the configured stream when appropriate.

        Standard streams (stdout/stderr) are never closed.
        """

        stream = self._stream

        if stream is None:

            return self

        if stream in (
            sys.stdout,
            sys.stderr,
        ):

            return self

        try:

            if hasattr(
                stream,
                "flush",
            ):

                stream.flush()

            if hasattr(
                stream,
                "close",
            ):

                stream.close()

        finally:

            self._stream = None

            self._touch()

        return self

    # -------------------------------------------------------------------------
    # Stream Name
    # -------------------------------------------------------------------------

    def stream_name(
        self,
    ) -> str:
        """
        Return a human-readable stream name.
        """

        stream = self._stream

        if stream is sys.stdout:

            return "stdout"

        if stream is sys.stderr:

            return "stderr"

        if stream is None:

            return "<none>"

        return getattr(
            stream,
            "name",
            type(stream).__name__,
        )
# =============================================================================
# Part 5. Lifecycle API
# =============================================================================

    # -------------------------------------------------------------------------
    # Enable
    # -------------------------------------------------------------------------

    def enable(
        self,
    ) -> "ConsoleHandler":
        """
        Enable the console handler.
        """

        if self._closed:
            raise RuntimeError(
                "Cannot enable a closed ConsoleHandler."
            )

        self._enabled = True

        self._touch()

        return self

    # -------------------------------------------------------------------------
    # Disable
    # -------------------------------------------------------------------------

    def disable(
        self,
    ) -> "ConsoleHandler":
        """
        Disable the console handler.
        """

        self._enabled = False

        self._touch()

        return self

    # -------------------------------------------------------------------------
    # Freeze
    # -------------------------------------------------------------------------

    def freeze(
        self,
    ) -> "ConsoleHandler":
        """
        Freeze the handler configuration.

        While frozen, runtime configuration such as stream,
        formatter and color cannot be modified.
        """

        if self._closed:
            raise RuntimeError(
                "ConsoleHandler is closed."
            )

        self._frozen = True

        self._touch()

        return self

    # -------------------------------------------------------------------------
    # Unfreeze
    # -------------------------------------------------------------------------

    def unfreeze(
        self,
    ) -> "ConsoleHandler":
        """
        Unfreeze the handler configuration.
        """

        if self._closed:
            raise RuntimeError(
                "ConsoleHandler is closed."
            )

        self._frozen = False

        self._touch()

        return self

    # -------------------------------------------------------------------------
    # Close
    # -------------------------------------------------------------------------

    def close(
        self,
    ) -> "ConsoleHandler":
        """
        Close the console handler.

        Flushes pending output and releases resources.
        Standard streams (stdout/stderr) remain open.
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
        *,
        stream: Optional[StreamType] = None,
    ) -> "ConsoleHandler":
        """
        Reopen the console handler.

        If no stream is provided, stdout is used.
        """

        self._closed = False

        self._enabled = True

        self._stream = (

            stream

            if stream is not None

            else sys.stdout

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
        Create a runtime snapshot of this ConsoleHandler.
        """

        return {

            # Identity
            "id": self._id,
            "name": self._name,

            # Runtime State
            "enabled": self._enabled,
            "frozen": self._frozen,
            "closed": self._closed,

            # Configuration
            "level": self._level,
            "stream_name": self.stream_name(),
            "color": self._color,
            "formatter": self._formatter,

            # Runtime Data
            "buffer": copy.deepcopy(
                self._buffer
            ),

            "metadata": copy.deepcopy(
                self._metadata
            ),

            "statistics": copy.deepcopy(
                self._statistics
            ),

            # Timestamps
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    # -------------------------------------------------------------------------
    # Restore
    # -------------------------------------------------------------------------

    def restore(
        self,
        snapshot: Mapping[str, Any],
    ) -> "ConsoleHandler":
        """
        Restore a previously captured snapshot.
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

        self._color = snapshot.get(
            "color",
            self._color,
        )

        self._formatter = snapshot.get(
            "formatter",
            self._formatter,
        )

        self._buffer = copy.deepcopy(
            snapshot.get(
                "buffer",
                [],
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

        stream_name = snapshot.get(
            "stream_name",
            "stdout",
        )

        if stream_name == "stderr":

            self._stream = sys.stderr

        else:

            self._stream = sys.stdout

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
    ) -> "ConsoleHandler":
        """
        Create a deep clone.
        """

        cloned = self.__class__(

            name=self._name,

            level=self._level,

            formatter=self._formatter,

            stream=self._stream,

            color=self._color,

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
    ) -> "ConsoleHandler":
        """
        Alias of clone().
        """

        return self.clone()

    # -------------------------------------------------------------------------
    # Optimize
    # -------------------------------------------------------------------------

    def optimize(
        self,
    ) -> "ConsoleHandler":
        """
        Optimize runtime structures.
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
    ) -> "ConsoleHandler":
        """
        Cleanup temporary runtime resources.
        """

        self._buffer.clear()

        self._statistics["latency"] = 0.0

        self._touch()

        return self

    # -------------------------------------------------------------------------
    # Compact
    # -------------------------------------------------------------------------

    def compact(
        self,
    ) -> "ConsoleHandler":
        """
        Compact the internal buffer by removing
        consecutive duplicate entries.
        """

        compacted = []

        previous = object()

        for item in self._buffer:

            if item != previous:

                compacted.append(
                    item
                )

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
        Return a concise runtime summary.
        """

        return {

            "id": self.id,

            "name": self.name,

            "type": self.__class__.__name__,

            "stream": self.stream_name(),

            "level": self.level,

            "enabled": self.enabled,

            "write_count": self.write_count,

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

                "type": self.__class__.__name__,

            },

            "runtime": {

                "enabled": self._enabled,

                "frozen": self._frozen,

                "closed": self._closed,

                "level": self._level,

                "stream": self.stream_name(),

                "color": self._color,

            },

            "statistics": copy.deepcopy(
                self._statistics
            ),

            "metadata": copy.deepcopy(
                self._metadata
            ),

            "buffer_size": len(
                self._buffer
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

            self._stream is not None

            and

            self.error_count == 0

        )

        return {

            "healthy": healthy,

            "status": self.status(),

            "stream": self.stream_name(),

            "write_count": self.write_count,

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
        Return current runtime status.
        """

        if self._closed:

            return "closed"

        if self._frozen:

            return "frozen"

        if not self._enabled:

            return "disabled"

        return "active"

    # -------------------------------------------------------------------------
    # Write Count
    # -------------------------------------------------------------------------

    @property
    def write_count(
        self,
    ) -> int:
        """
        Total successful console writes.
        """

        return self._statistics.get(
            "write",
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
        Average write latency in seconds.
        """

        writes = max(
            self.write_count,
            1,
        )

        return (

            self._statistics.get(
                "latency",
                0.0,
            )

            /

            writes

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
        Validate the entire ConsoleHandler.

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
    # Validate Stream
    # -------------------------------------------------------------------------

    def validate_stream(
        self,
        stream: Optional[StreamType] = None,
    ) -> bool:
        """
        Validate an output stream.
        """

        stream = stream if stream is not None else self._stream

        if stream is None:

            return False

        if not hasattr(stream, "write"):

            return False

        if not callable(stream.write):

            return False

        return True

    # -------------------------------------------------------------------------
    # Validate Record
    # -------------------------------------------------------------------------

    def validate_record(
        self,
        record: LogRecord,
    ) -> bool:
        """
        Validate a LogRecord before writing.
        """

        if not isinstance(
            record,
            LogRecord,
        ):

            return False

        if getattr(
            record,
            "message",
            None,
        ) is None:

            return False

        if getattr(
            record,
            "level",
            None,
        ) is None:

            return False

        return True

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

        if not isinstance(
            self._color,
            bool,
        ):

            return False

        if not self.validate_stream():

            return False

        if self._formatter is not None:

            if not (

                hasattr(
                    self._formatter,
                    "format",
                )

                or

                hasattr(
                    self._formatter,
                    "format_record",
                )

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
    # Before Write
    # -------------------------------------------------------------------------

    def before_write(
        self,
        output: Any,
    ) -> None:
        """
        Emit hook before writing to the console.
        """

        self.emit_event(
            "before_write",
            handler=self,
            output=output,
            stream=self._stream,
        )

    # -------------------------------------------------------------------------
    # After Write
    # -------------------------------------------------------------------------

    def after_write(
        self,
        output: Any,
    ) -> None:
        """
        Emit hook after writing to the console.
        """

        self.emit_event(
            "after_write",
            handler=self,
            output=output,
            stream=self._stream,
        )

    # -------------------------------------------------------------------------
    # Before Flush
    # -------------------------------------------------------------------------

    def before_flush(
        self,
    ) -> None:
        """
        Emit hook before flushing the stream.
        """

        self.emit_event(
            "before_flush",
            handler=self,
            stream=self._stream,
        )

    # -------------------------------------------------------------------------
    # After Flush
    # -------------------------------------------------------------------------

    def after_flush(
        self,
    ) -> None:
        """
        Emit hook after flushing the stream.
        """

        self.emit_event(
            "after_flush",
            handler=self,
            stream=self._stream,
        )

    # -------------------------------------------------------------------------
    # Add Hook
    # -------------------------------------------------------------------------

    def add_hook(
        self,
        event: str,
        callback: Hook,
    ) -> "ConsoleHandler":
        """
        Register a callback for an event.
        """

        self._hooks.setdefault(
            event,
            [],
        ).append(
            callback,
        )

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
        Remove a registered callback.
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
        Dispatch an event to all registered callbacks.
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
    ) -> "ConsoleHandler":
        """
        Subscribe to an event.

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
            f"level={self.level!r}, "
            f"stream={self.stream_name()!r}, "
            f"enabled={self.enabled}, "
            f"color={self.color})"
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
            f"{self.name}"
            f" [{self.level}] "
            f"-> {self.stream_name()} "
            f"({self.status()})"
        )

    # -------------------------------------------------------------------------
    # __len__
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
    # __iter__
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
    # __contains__
    # -------------------------------------------------------------------------

    def __contains__(
        self,
        item: Any,
    ) -> bool:
        """
        Support 'in' operator.
        """

        return item in self._buffer

    # -------------------------------------------------------------------------
    # __call__
    # -------------------------------------------------------------------------

    def __call__(
        self,
        record: LogRecord,
    ) -> HandlerResult:
        """
        Allow handler(record) syntax.

        Equivalent to:

            handler.emit(record)
        """

        return self.emit(
            record
        )

    # -------------------------------------------------------------------------
    # __copy__
    # -------------------------------------------------------------------------

    def __copy__(
        self,
    ) -> "ConsoleHandler":
        """
        Create a shallow copy.
        """

        copied = self.__class__(

            name=self._name,

            level=self._level,

            formatter=self._formatter,

            stream=self._stream,

            color=self._color,

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
    # __deepcopy__
    # -------------------------------------------------------------------------

    def __deepcopy__(
        self,
        memo: Dict[int, Any],
    ) -> "ConsoleHandler":
        """
        Create a deep copy.
        """

        if id(self) in memo:

            return memo[id(self)]

        cloned = self.clone()

        memo[id(self)] = cloned

        return cloned                                                                        
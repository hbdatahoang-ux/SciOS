"""
SciOS-NG File Handler

Persistent file-based logging handler.
"""

from __future__ import annotations

# =============================================================================
# Imports
# =============================================================================

import copy
import io
import os
import shutil
import time
import uuid

from datetime import datetime, timezone
from pathlib import Path
from typing import (
    Any,
    Dict,
    IO,
    Mapping,
    Optional,
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

DEFAULT_NAME = "file"

DEFAULT_LEVEL = "INFO"

DEFAULT_MODE = "a"

DEFAULT_ENCODING = "utf-8"

DEFAULT_ENABLED = True

DEFAULT_BUFFERING = 1

# =============================================================================
# Type Aliases
# =============================================================================

Metadata: TypeAlias = Dict[str, Any]

Statistics: TypeAlias = Dict[str, Any]

FileObject: TypeAlias = IO[str]

# =============================================================================
# File Handler
# =============================================================================


class FileHandler(LogHandler):
    """
    Persistent file logging handler.

    Responsible for writing formatted log records
    into a filesystem-backed log file.
    """

    # -------------------------------------------------------------------------
    # Constructor
    # -------------------------------------------------------------------------

    def __init__(
        self,
        path: str | Path,
        *,
        name: str = DEFAULT_NAME,
        level: str = DEFAULT_LEVEL,
        mode: str = DEFAULT_MODE,
        encoding: str = DEFAULT_ENCODING,
        buffering: int = DEFAULT_BUFFERING,
        formatter: Optional[Any] = None,
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
        # File Configuration
        # ---------------------------------------------------------------------

        self._path = Path(path)

        self._mode = mode

        self._encoding = encoding

        self._buffering = buffering

        self._file: Optional[FileObject] = None

        self._buffer: list[Any] = []

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

            "open": 0,

            "close": 0,

            "write": 0,

            "flush": 0,

            "errors": 0,

            "latency": 0.0,

        }

        # ---------------------------------------------------------------------
        # Auto-open
        # ---------------------------------------------------------------------

        self.open()

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
        Update latency statistics.
        """

        self._statistics["latency"] += (

            time.perf_counter()

            -

            started

        )

    def _ensure_parent_directory(
        self,
    ) -> None:
        """
        Ensure that the log directory exists.
        """

        self._path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    def _is_open(
        self,
    ) -> bool:
        """
        Return True if the file object is available.
        """

        return (

            self._file is not None

            and

            not self._file.closed

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
        Whether the handler is enabled.
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
        Current logging level.
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
    # Path
    # -------------------------------------------------------------------------

    @property
    def path(
        self,
    ) -> Path:
        """
        Log file path.
        """

        return self._path

    @path.setter
    def path(
        self,
        value: str | Path,
    ) -> None:
        """
        Update log file path.
        """

        if self._frozen:

            raise RuntimeError(
                "FileHandler is frozen."
            )

        self._path = Path(value)

        self._touch()

    # -------------------------------------------------------------------------
    # Mode
    # -------------------------------------------------------------------------

    @property
    def mode(
        self,
    ) -> str:
        """
        File open mode.
        """

        return self._mode

    @mode.setter
    def mode(
        self,
        value: str,
    ) -> None:
        """
        Update file open mode.
        """

        if self._frozen:

            raise RuntimeError(
                "FileHandler is frozen."
            )

        self._mode = str(value)

        self._touch()

    # -------------------------------------------------------------------------
    # Encoding
    # -------------------------------------------------------------------------

    @property
    def encoding(
        self,
    ) -> str:
        """
        File encoding.
        """

        return self._encoding

    @encoding.setter
    def encoding(
        self,
        value: str,
    ) -> None:
        """
        Update file encoding.
        """

        if self._frozen:

            raise RuntimeError(
                "FileHandler is frozen."
            )

        self._encoding = str(value)

        self._touch()

    # -------------------------------------------------------------------------
    # File
    # -------------------------------------------------------------------------

    @property
    def file(
        self,
    ) -> Optional[FileObject]:
        """
        Current file object.
        """

        return self._file

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
        Lifetime of this handler in seconds.
        """

        return (

            datetime.now(
                timezone.utc
            )

            -

            self.created_at

        ).total_seconds()

    # -------------------------------------------------------------------------
    # Write Count
    # -------------------------------------------------------------------------

    @property
    def write_count(
        self,
    ) -> int:
        """
        Total successful file writes.
        """

        return self._statistics.get(
            "write",
            0,
        )
# =============================================================================
# Part 3. File API
# =============================================================================

    # -------------------------------------------------------------------------
    # Open
    # -------------------------------------------------------------------------

    def open(
        self,
    ) -> HandlerResult:
        """
        Open the log file.
        """

        if self._closed:
            return HandlerResult(
                success=False,
                message="FileHandler is closed.",
            )

        if self._is_open():

            return HandlerResult(
                success=True,
                output=self._file,
                message="File already opened.",
            )

        started = time.perf_counter()

        try:

            self._ensure_parent_directory()

            self._file = open(
                self._path,
                self._mode,
                encoding=self._encoding,
                buffering=self._buffering,
            )

            self._statistics["open"] += 1

            self.emit_event(
                "after_open",
                handler=self,
                path=self._path,
            )

            return HandlerResult(
                success=True,
                output=self._file,
                message="File opened successfully.",
            )

        except Exception as exc:

            self._statistics["errors"] += 1

            return HandlerResult(
                success=False,
                message=str(exc),
            )

        finally:

            self._record_latency(
                started
            )

            self._touch()

    # -------------------------------------------------------------------------
    # Close File
    # -------------------------------------------------------------------------

    def close_file(
        self,
    ) -> HandlerResult:
        """
        Close the underlying file object.
        """

        if not self._is_open():

            return HandlerResult(
                success=True,
                message="File already closed.",
            )

        started = time.perf_counter()

        try:

            self.flush()

            self._file.close()

            self._statistics["close"] += 1

            self._file = None

            return HandlerResult(
                success=True,
                message="File closed.",
            )

        except Exception as exc:

            self._statistics["errors"] += 1

            return HandlerResult(
                success=False,
                message=str(exc),
            )

        finally:

            self._record_latency(
                started
            )

            self._touch()

    # -------------------------------------------------------------------------
    # Write
    # -------------------------------------------------------------------------

    def write(
        self,
        data: Any,
    ) -> HandlerResult:
        """
        Write raw data to file.
        """

        if not self._enabled:

            return HandlerResult(
                success=False,
                message="FileHandler disabled.",
            )

        if not self._is_open():

            result = self.open()

            if not result.success:

                return result

        started = time.perf_counter()

        try:

            self.emit_event(
                "before_write",
                handler=self,
                data=data,
            )

            text = str(data)

            self._file.write(
                text
            )

            self._statistics["write"] += 1

            self.emit_event(
                "after_write",
                handler=self,
                data=data,
            )

            return HandlerResult(
                success=True,
                output=text,
                message="Write completed.",
            )

        except Exception as exc:

            self._statistics["errors"] += 1

            return HandlerResult(
                success=False,
                message=str(exc),
            )

        finally:

            self._record_latency(
                started
            )

            self._touch()

    # -------------------------------------------------------------------------
    # Writeln
    # -------------------------------------------------------------------------

    def writeln(
        self,
        data: Any,
    ) -> HandlerResult:
        """
        Write data with newline.
        """

        return self.write(
            f"{data}\n"
        )

    # -------------------------------------------------------------------------
    # Write Record
    # -------------------------------------------------------------------------

    def write_record(
        self,
        record: LogRecord,
    ) -> HandlerResult:
        """
        Write a formatted LogRecord.
        """

        if not self.validate_record(
            record
        ):

            return HandlerResult(
                success=False,
                message="Invalid log record.",
            )

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
        Flush file buffer.
        """

        if not self._is_open():

            return HandlerResult(
                success=False,
                message="File is not open.",
            )

        try:

            self.emit_event(
                "before_flush",
                handler=self,
            )

            self._file.flush()

            self._statistics["flush"] += 1

            self.emit_event(
                "after_flush",
                handler=self,
            )

            return HandlerResult(
                success=True,
                message="File flushed.",
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
    ) -> "FileHandler":
        """
        Reset runtime statistics.
        """

        self._statistics = {

            "open": 0,

            "close": 0,

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
    ) -> "FileHandler":
        """
        Clear file content.
        """

        try:

            if self._is_open():

                self.flush()

                self.close_file()

            with open(
                self._path,
                "w",
                encoding=self._encoding,
            ):

                pass

            self._touch()

        except Exception:

            self._statistics["errors"] += 1

        return self
# =============================================================================
# Part 4. File Operations API
# =============================================================================

    # -------------------------------------------------------------------------
    # Exists
    # -------------------------------------------------------------------------

    def exists(
        self,
    ) -> bool:
        """
        Check whether the log file exists.
        """

        return self._path.exists()

    # -------------------------------------------------------------------------
    # Size
    # -------------------------------------------------------------------------

    def size(
        self,
    ) -> int:
        """
        Return file size in bytes.
        """

        if not self.exists():

            return 0

        try:

            return self._path.stat().st_size

        except OSError:

            self._statistics["errors"] += 1

            return 0

    # -------------------------------------------------------------------------
    # Filename
    # -------------------------------------------------------------------------

    def filename(
        self,
    ) -> str:
        """
        Return file name.
        """

        return self._path.name

    # -------------------------------------------------------------------------
    # Directory
    # -------------------------------------------------------------------------

    def directory(
        self,
    ) -> Path:
        """
        Return parent directory.
        """

        return self._path.parent

    # -------------------------------------------------------------------------
    # Rotate
    # -------------------------------------------------------------------------

    def rotate(
        self,
        suffix: Optional[str] = None,
    ) -> HandlerResult:
        """
        Rotate current log file.

        Example:

            app.log
            app.log.20260716
        """

        started = time.perf_counter()

        try:

            if self._is_open():

                self.close_file()

            if not self.exists():

                return HandlerResult(
                    success=False,
                    message="File does not exist.",
                )

            timestamp = (

                suffix

                if suffix is not None

                else datetime.now(
                    timezone.utc
                )
                .strftime(
                    "%Y%m%d_%H%M%S"
                )

            )

            rotated = self._path.with_name(
                f"{self._path.name}.{timestamp}"
            )

            shutil.move(
                str(self._path),
                str(rotated),
            )

            self.open()

            return HandlerResult(
                success=True,
                output=rotated,
                message="File rotated successfully.",
            )

        except Exception as exc:

            self._statistics["errors"] += 1

            return HandlerResult(
                success=False,
                message=str(exc),
            )

        finally:

            self._record_latency(
                started
            )

            self._touch()

    # -------------------------------------------------------------------------
    # Truncate
    # -------------------------------------------------------------------------

    def truncate(
        self,
        size: int = 0,
    ) -> HandlerResult:
        """
        Truncate file to specified size.
        """

        started = time.perf_counter()

        try:

            if self._is_open():

                self.flush()

                self._file.truncate(
                    size
                )

            else:

                with open(
                    self._path,
                    "r+",
                    encoding=self._encoding,
                ) as file:

                    file.truncate(
                        size
                    )

            return HandlerResult(
                success=True,
                message="File truncated.",
            )

        except Exception as exc:

            self._statistics["errors"] += 1

            return HandlerResult(
                success=False,
                message=str(exc),
            )

        finally:

            self._record_latency(
                started
            )

            self._touch()

    # -------------------------------------------------------------------------
    # Reopen
    # -------------------------------------------------------------------------

    def reopen(
        self,
    ) -> HandlerResult:
        """
        Close and reopen the log file.

        Useful after external rotation.
        """

        started = time.perf_counter()

        try:

            self.close_file()

            result = self.open()

            return result

        except Exception as exc:

            self._statistics["errors"] += 1

            return HandlerResult(
                success=False,
                message=str(exc),
            )

        finally:

            self._record_latency(
                started
            )

            self._touch()

    # -------------------------------------------------------------------------
    # Delete
    # -------------------------------------------------------------------------

    def delete(
        self,
    ) -> HandlerResult:
        """
        Delete the log file.
        """

        started = time.perf_counter()

        try:

            if self._is_open():

                self.close_file()

            if self.exists():

                self._path.unlink()

            return HandlerResult(
                success=True,
                message="File deleted.",
            )

        except Exception as exc:

            self._statistics["errors"] += 1

            return HandlerResult(
                success=False,
                message=str(exc),
            )

        finally:

            self._record_latency(
                started
            )

            self._touch()
# =============================================================================
# Part 5. Lifecycle API
# =============================================================================

    # -------------------------------------------------------------------------
    # Enable
    # -------------------------------------------------------------------------

    def enable(
        self,
    ) -> "FileHandler":
        """
        Enable file logging.
        """

        if self._closed:

            raise RuntimeError(
                "Cannot enable closed FileHandler."
            )

        self._enabled = True

        self._touch()

        return self

    # -------------------------------------------------------------------------
    # Disable
    # -------------------------------------------------------------------------

    def disable(
        self,
    ) -> "FileHandler":
        """
        Disable file logging.
        """

        self._enabled = False

        self._touch()

        return self

    # -------------------------------------------------------------------------
    # Freeze
    # -------------------------------------------------------------------------

    def freeze(
        self,
    ) -> "FileHandler":
        """
        Freeze configuration changes.

        Prevents modification of:
        - path
        - mode
        - encoding
        - file configuration
        """

        if self._closed:

            raise RuntimeError(
                "Cannot freeze closed FileHandler."
            )

        self._frozen = True

        self._touch()

        return self

    # -------------------------------------------------------------------------
    # Unfreeze
    # -------------------------------------------------------------------------

    def unfreeze(
        self,
    ) -> "FileHandler":
        """
        Allow configuration changes again.
        """

        if self._closed:

            raise RuntimeError(
                "Cannot unfreeze closed FileHandler."
            )

        self._frozen = False

        self._touch()

        return self

    # -------------------------------------------------------------------------
    # Close
    # -------------------------------------------------------------------------

    def close(
        self,
    ) -> "FileHandler":
        """
        Close handler lifecycle.

        Flushes data and closes file resource.
        """

        if self._closed:

            return self

        try:

            self.flush()

            self.close_file()

        finally:

            self._enabled = False

            self._closed = True

            self._touch()

        return self

    # -------------------------------------------------------------------------
    # Reopen Handler
    # -------------------------------------------------------------------------

    def reopen_handler(
        self,
    ) -> "FileHandler":
        """
        Reopen the FileHandler after close.

        Restores active runtime state.
        """

        if not self._closed:

            self.reopen()

            return self

        self._closed = False

        self._enabled = True

        result = self.open()

        if not result.success:

            raise RuntimeError(
                result.message
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
        Create a runtime snapshot of FileHandler.
        """

        return {

            # Identity
            "id": self._id,

            "name": self._name,

            # Runtime State
            "enabled": self._enabled,

            "frozen": self._frozen,

            "closed": self._closed,

            # File Configuration
            "path": str(self._path),

            "mode": self._mode,

            "encoding": self._encoding,

            "buffering": self._buffering,

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

            # Formatter
            "formatter": self._formatter,

            # Time
            "created_at": self.created_at,

            "updated_at": self.updated_at,

        }

    # -------------------------------------------------------------------------
    # Restore
    # -------------------------------------------------------------------------

    def restore(
        self,
        snapshot: Mapping[str, Any],
    ) -> "FileHandler":
        """
        Restore FileHandler state from snapshot.
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

        self._path = Path(
            snapshot.get(
                "path",
                self._path,
            )
        )

        self._mode = snapshot.get(
            "mode",
            self._mode,
        )

        self._encoding = snapshot.get(
            "encoding",
            self._encoding,
        )

        self._buffering = snapshot.get(
            "buffering",
            self._buffering,
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

        self._formatter = snapshot.get(
            "formatter",
            self._formatter,
        )

        self.created_at = snapshot.get(
            "created_at",
            self.created_at,
        )

        self.updated_at = snapshot.get(
            "updated_at",
            self.updated_at,
        )

        if not self._closed:

            self.open()

        self._touch()

        return self

    # -------------------------------------------------------------------------
    # Clone
    # -------------------------------------------------------------------------

    def clone(
        self,
    ) -> "FileHandler":
        """
        Create a deep clone of FileHandler.
        """

        cloned = self.__class__(

            path=self._path,

            name=self._name,

            level=self._level,

            mode=self._mode,

            encoding=self._encoding,

            buffering=self._buffering,

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
    ) -> "FileHandler":
        """
        Alias of clone().
        """

        return self.clone()

    # -------------------------------------------------------------------------
    # Optimize
    # -------------------------------------------------------------------------

    def optimize(
        self,
    ) -> "FileHandler":
        """
        Optimize runtime resources.
        """

        # Remove invalid buffer entries

        self._buffer = [

            item

            for item in self._buffer

            if item is not None

        ]

        # Ensure file handle state

        if self._enabled and not self._closed:

            if not self._is_open():

                self.open()

        self._touch()

        return self

    # -------------------------------------------------------------------------
    # Cleanup
    # -------------------------------------------------------------------------

    def cleanup(
        self,
    ) -> "FileHandler":
        """
        Cleanup temporary runtime resources.
        """

        self._buffer.clear()

        self.flush()

        self._touch()

        return self

    # -------------------------------------------------------------------------
    # Compact
    # -------------------------------------------------------------------------

    def compact(
        self,
    ) -> "FileHandler":
        """
        Compact file content by removing empty lines.
        """

        if not self.exists():

            return self

        try:

            if self._is_open():

                self.close_file()

            with open(
                self._path,
                "r",
                encoding=self._encoding,
            ) as source:

                lines = [

                    line

                    for line in source

                    if line.strip()

                ]

            with open(
                self._path,
                "w",
                encoding=self._encoding,
            ) as target:

                target.writelines(
                    lines
                )

            if not self._closed:

                self.open()

        except Exception:

            self._statistics["errors"] += 1

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
        Return compact runtime summary.
        """

        return {

            "id": self.id,

            "name": self.name,

            "path": str(self.path),

            "level": self.level,

            "enabled": self.enabled,

            "closed": self._closed,

            "frozen": self._frozen,

            "exists": self.exists(),

            "size": self.size(),

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
        Return detailed diagnostic report.
        """

        return {

            "identity": {

                "id": self.id,

                "name": self.name,

            },

            "configuration": {

                "path": str(self.path),

                "mode": self.mode,

                "encoding": self.encoding,

                "level": self.level,

            },

            "runtime": {

                "enabled": self.enabled,

                "frozen": self._frozen,

                "closed": self._closed,

                "file_open": self._is_open(),

            },

            "file": {

                "exists": self.exists(),

                "size": self.size(),

                "filename": self.filename(),

                "directory": str(
                    self.directory()
                ),

            },

            "statistics": self.statistics.copy(),

            "health": self.health(),

        }

    # -------------------------------------------------------------------------
    # Health
    # -------------------------------------------------------------------------

    def health(
        self,
    ) -> Dict[str, Any]:
        """
        Return health status.
        """

        healthy = (

            self.check_configuration()

            and

            self.check_integrity()

        )

        if self._closed:

            state = "closed"

        elif not self.enabled:

            state = "disabled"

        elif self._frozen:

            state = "frozen"

        else:

            state = "active"

        return {

            "healthy": healthy,

            "state": state,

            "file_available": self._is_open(),

            "path_exists": self.exists(),

            "errors": self.error_count,

        }

    # -------------------------------------------------------------------------
    # Status
    # -------------------------------------------------------------------------

    def status(
        self,
    ) -> str:
        """
        Return current lifecycle status.
        """

        if self._closed:

            return "closed"

        if self._frozen:

            return "frozen"

        if not self._enabled:

            return "disabled"

        if self._is_open():

            return "active"

        return "inactive"

    # -------------------------------------------------------------------------
    # Write Count
    # -------------------------------------------------------------------------

    @property
    def write_count(
        self,
    ) -> int:
        """
        Number of successful writes.
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
        Number of runtime errors.
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
        Total accumulated operation latency.
        """

        return self._statistics.get(
            "latency",
            0.0,
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
        Validate complete FileHandler state.

        Combines configuration validation
        and runtime integrity checks.
        """

        return (

            self.check_configuration()

            and

            self.check_integrity()

        )

    # -------------------------------------------------------------------------
    # Validate Path
    # -------------------------------------------------------------------------

    def validate_path(
        self,
        path: Optional[str | Path] = None,
    ) -> bool:
        """
        Validate file path configuration.
        """

        target = (

            Path(path)

            if path is not None

            else self._path

        )

        try:

            if not isinstance(
                target,
                Path,
            ):

                return False

            if not target.name:

                return False

            parent = target.parent

            if not parent:

                return False

            return True

        except Exception:

            self._statistics["errors"] += 1

            return False

    # -------------------------------------------------------------------------
    # Validate Record
    # -------------------------------------------------------------------------

    def validate_record(
        self,
        record: LogRecord,
    ) -> bool:
        """
        Validate log record before writing.
        """

        if record is None:

            return False

        if not isinstance(
            record,
            LogRecord,
        ):

            return False

        required_fields = (

            "message",

            "level",

            "timestamp",

        )

        for field in required_fields:

            if not hasattr(
                record,
                field,
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
        Validate FileHandler configuration.
        """

        checks = [

            isinstance(
                self._name,
                str,
            ),

            isinstance(
                self._level,
                str,
            ),

            self.validate_path(),

            isinstance(
                self._mode,
                str,
            ),

            isinstance(
                self._encoding,
                str,
            ),

            isinstance(
                self._buffering,
                int,
            ),

        ]

        return all(
            checks
        )

    # -------------------------------------------------------------------------
    # Check Integrity
    # -------------------------------------------------------------------------

    def check_integrity(
        self,
    ) -> bool:
        """
        Validate internal runtime consistency.
        """

        required_statistics = {

            "open",

            "close",

            "write",

            "flush",

            "errors",

            "latency",

        }

        # Metadata

        if not isinstance(
            self._metadata,
            dict,
        ):

            return False


        # Statistics

        if not isinstance(
            self._statistics,
            dict,
        ):

            return False


        if not required_statistics.issubset(
            self._statistics.keys()
        ):

            return False


        # File state consistency

        if self._closed:

            if self._file is not None:

                if not self._file.closed:

                    return False


        if self._is_open():

            if self._file.closed:

                return False


        # Buffer

        if not isinstance(
            self._buffer,
            list,
        ):

            return False


        # Timestamps

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
        data: Any,
    ) -> None:
        """
        Execute hooks before writing data to file.
        """

        self.emit_event(
            "before_write",
            handler=self,
            path=self._path,
            data=data,
        )

    # -------------------------------------------------------------------------
    # After Write
    # -------------------------------------------------------------------------

    def after_write(
        self,
        data: Any,
    ) -> None:
        """
        Execute hooks after writing data.
        """

        self.emit_event(
            "after_write",
            handler=self,
            path=self._path,
            data=data,
        )

    # -------------------------------------------------------------------------
    # Before Open
    # -------------------------------------------------------------------------

    def before_open(
        self,
    ) -> None:
        """
        Execute hooks before opening file.
        """

        self.emit_event(
            "before_open",
            handler=self,
            path=self._path,
            mode=self._mode,
        )

    # -------------------------------------------------------------------------
    # After Open
    # -------------------------------------------------------------------------

    def after_open(
        self,
    ) -> None:
        """
        Execute hooks after opening file.
        """

        self.emit_event(
            "after_open",
            handler=self,
            path=self._path,
            file=self._file,
        )

    # -------------------------------------------------------------------------
    # Add Hook
    # -------------------------------------------------------------------------

    def add_hook(
        self,
        event: str,
        callback: Any,
    ) -> "FileHandler":
        """
        Register an event callback.
        """

        if not callable(callback):

            raise TypeError(
                "Hook callback must be callable."
            )

        if not hasattr(
            self,
            "_hooks",
        ):

            self._hooks = {}

        self._hooks.setdefault(
            event,
            [],
        ).append(
            callback
        )

        self._touch()

        return self

    # -------------------------------------------------------------------------
    # Remove Hook
    # -------------------------------------------------------------------------

    def remove_hook(
        self,
        event: str,
        callback: Any,
    ) -> bool:
        """
        Remove an event callback.
        """

        hooks = getattr(
            self,
            "_hooks",
            {},
        )

        callbacks = hooks.get(
            event,
            [],
        )

        if callback not in callbacks:

            return False

        callbacks.remove(
            callback
        )

        if not callbacks:

            hooks.pop(
                event,
                None,
            )

        self._touch()

        return True

    # -------------------------------------------------------------------------
    # Emit Event
    # -------------------------------------------------------------------------

    def emit_event(
        self,
        event: str,
        **payload: Any,
    ) -> None:
        """
        Dispatch event to subscribed hooks.
        """

        hooks = getattr(
            self,
            "_hooks",
            {},
        )

        callbacks = hooks.get(
            event,
            [],
        )

        for callback in tuple(callbacks):

            try:

                callback(
                    **payload
                )

            except Exception:

                self._statistics["errors"] += 1

    # -------------------------------------------------------------------------
    # Subscribe
    # -------------------------------------------------------------------------

    def subscribe(
        self,
        event: str,
        callback: Any,
    ) -> "FileHandler":
        """
        Subscribe callback to event.

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

        Useful for debugging and inspection.
        """

        return (

            f"{self.__class__.__name__}("

            f"id={self.id!r}, "

            f"name={self.name!r}, "

            f"path={str(self.path)!r}, "

            f"level={self.level!r}, "

            f"enabled={self.enabled}, "

            f"closed={self._closed}"

            f")"

        )

    # -------------------------------------------------------------------------
    # __str__
    # -------------------------------------------------------------------------

    def __str__(
        self,
    ) -> str:
        """
        Human readable representation.
        """

        return (

            f"{self.name} "

            f"[{self.level}] "

            f"-> {self.filename()} "

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
        Support:

            item in handler
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
        Callable FileHandler.

        Example:

            handler(record)

        Equivalent:

            handler.write_record(record)
        """

        return self.write_record(
            record
        )

    # -------------------------------------------------------------------------
    # __copy__
    # -------------------------------------------------------------------------

    def __copy__(
        self,
    ) -> "FileHandler":
        """
        Create shallow copy.
        """

        copied = self.__class__(

            path=self._path,

            name=self._name,

            level=self._level,

            mode=self._mode,

            encoding=self._encoding,

            buffering=self._buffering,

            formatter=self._formatter,

            enabled=self._enabled,

            metadata=self._metadata.copy(),

        )

        copied._statistics = self._statistics.copy()

        copied._buffer = self._buffer.copy()

        copied._frozen = self._frozen

        copied._closed = self._closed

        return copied

    # -------------------------------------------------------------------------
    # __deepcopy__
    # -------------------------------------------------------------------------

    def __deepcopy__(
        self,
        memo: Dict[int, Any],
    ) -> "FileHandler":
        """
        Create deep copy.

        Handles recursive references safely.
        """

        if id(self) in memo:

            return memo[
                id(self)
            ]

        cloned = self.clone()

        memo[
            id(self)
        ] = cloned

        return cloned                                                                            
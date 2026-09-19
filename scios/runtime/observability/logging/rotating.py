# =============================================================================
# scios/runtime/observability/logging/rotating.py
#
# Part 1. Foundation
#
# RotatingHandler
# =============================================================================


# =============================================================================
# Imports
# =============================================================================

from __future__ import annotations

import copy

import os

import time

import uuid

from dataclasses import dataclass

from datetime import datetime, timezone

from pathlib import Path

from typing import (

    Any,

    Callable,

    Dict,

    List,

    Mapping,

    Optional,

    TypeAlias,

)


# =============================================================================
# Constants
# =============================================================================

DEFAULT_ROTATING_NAME = "rotating"

DEFAULT_LEVEL = "INFO"

DEFAULT_MAX_SIZE = 10 * 1024 * 1024

DEFAULT_MAX_FILES = 5

DEFAULT_ENABLED = True

DEFAULT_MODE = "a"

DEFAULT_ENCODING = "utf-8"


SUPPORTED_LEVELS = (

    "TRACE",

    "DEBUG",

    "INFO",

    "WARNING",

    "ERROR",

    "CRITICAL",

)


SUPPORTED_ROTATION = (

    "size",

    "time",

    "manual",

)



# =============================================================================
# Type Aliases
# =============================================================================

Metadata: TypeAlias = Dict[str, Any]

Statistics: TypeAlias = Dict[str, float | int]

LogRecord: TypeAlias = Dict[str, Any]

Hook: TypeAlias = Callable[..., None]



# =============================================================================
# Rotation Policy
# =============================================================================

@dataclass
class RotationPolicy:
    """
    Defines rotation strategy.

    Examples:

        size rotation:
            max_size=10485760

        time rotation:
            interval="daily"
    """

    strategy: str = "size"

    max_size: int = DEFAULT_MAX_SIZE

    max_files: int = DEFAULT_MAX_FILES

    interval: Optional[str] = None

    compress: bool = False



# =============================================================================
# RotatingHandler
# =============================================================================

class RotatingHandler:
    """
    File based logging handler with rotation support.

    Features:

    - size based rotation
    - time based rotation
    - backup management
    - retention control
    - runtime diagnostics
    """



    # =========================================================================
    # __init__
    # =========================================================================

    def __init__(
        self,
        path: str | Path,
        name: str = DEFAULT_ROTATING_NAME,
        level: str = DEFAULT_LEVEL,
        policy: Optional[RotationPolicy] = None,
        mode: str = DEFAULT_MODE,
        encoding: str = DEFAULT_ENCODING,
        enabled: bool = DEFAULT_ENABLED,
        metadata: Optional[Metadata] = None,
    ) -> None:


        # ---------------------------------------------------------------------
        # Identity
        # ---------------------------------------------------------------------

        self._id: str = str(
            uuid.uuid4()
        )

        self._name: str = name



        # ---------------------------------------------------------------------
        # Runtime State
        # ---------------------------------------------------------------------

        self._enabled: bool = enabled

        self._frozen: bool = False

        self._closed: bool = False


        self.created_at = datetime.now(
            timezone.utc
        )

        self.updated_at = self.created_at



        # ---------------------------------------------------------------------
        # Rotation Configuration
        # ---------------------------------------------------------------------

        self._policy: RotationPolicy = (

            policy

            if policy

            else RotationPolicy()

        )


        self._rotation_count: int = 0



        # ---------------------------------------------------------------------
        # File Configuration
        # ---------------------------------------------------------------------

        self._path: Path = Path(
            path
        )

        self._mode: str = mode

        self._encoding: str = encoding

        self._file = None



        # ---------------------------------------------------------------------
        # Metadata
        # ---------------------------------------------------------------------

        self._metadata: Metadata = (

            metadata.copy()

            if metadata

            else {}

        )



        # ---------------------------------------------------------------------
        # Hooks
        # ---------------------------------------------------------------------

        self._hooks: Dict[
            str,
            List[Hook]
        ] = {}



        # ---------------------------------------------------------------------
        # Statistics
        # ---------------------------------------------------------------------

        self._statistics: Statistics = {

            "write": 0,

            "rotation": 0,

            "errors": 0,

            "latency": 0.0,

        }



        # Runtime

        self._last_result: Optional[
            LogRecord
        ] = None



    # =========================================================================
    # Identity
    # =========================================================================

    @property
    def id(
        self,
    ) -> str:
        """
        Unique handler id.
        """

        return self._id



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

        self._name = str(
            value
        )

        self._touch()



    # =========================================================================
    # Runtime State
    # =========================================================================

    @property
    def enabled(
        self,
    ) -> bool:
        """
        Enable state.
        """

        return self._enabled



    @property
    def frozen(
        self,
    ) -> bool:

        return self._frozen



    @property
    def closed(
        self,
    ) -> bool:

        return self._closed



    # =========================================================================
    # Rotation Configuration
    # =========================================================================

    @property
    def policy(
        self,
    ) -> RotationPolicy:
        """
        Rotation policy.
        """

        return self._policy



    @property
    def max_size(
        self,
    ) -> int:

        return self._policy.max_size



    @property
    def max_files(
        self,
    ) -> int:

        return self._policy.max_files



    # =========================================================================
    # File Configuration
    # =========================================================================

    @property
    def path(
        self,
    ) -> Path:

        return self._path



    @property
    def encoding(
        self,
    ) -> str:

        return self._encoding



    @property
    def mode(
        self,
    ) -> str:

        return self._mode



    # =========================================================================
    # Metadata
    # =========================================================================

    @property
    def metadata(
        self,
    ) -> Metadata:

        return self._metadata



    # =========================================================================
    # Statistics
    # =========================================================================

    @property
    def statistics(
        self,
    ) -> Statistics:

        return self._statistics



    @property
    def age(
        self,
    ) -> float:
        """
        Handler lifetime seconds.
        """

        return (

            datetime.now(
                timezone.utc
            )

            -

            self.created_at

        ).total_seconds()



    # =========================================================================
    # Internal Helper
    # =========================================================================

    def _touch(
        self,
    ) -> None:
        """
        Update modification time.
        """

        self.updated_at = datetime.now(
            timezone.utc
        )



    def _record_latency(
        self,
        started: float,
    ) -> None:

        self._statistics["latency"] += (

            time.perf_counter()

            -

            started

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
        Unique handler identifier.
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
    # enabled
    # -------------------------------------------------------------------------

    @property
    def enabled(
        self,
    ) -> bool:
        """
        Whether handler is enabled.
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
        Current logging level.
        """

        return self._level


    @level.setter
    def level(
        self,
        value: str,
    ) -> None:

        value = str(value).upper()

        if value not in SUPPORTED_LEVELS:

            raise ValueError(
                f"Unsupported level: {value}"
            )

        self._level = value

        self._touch()


    # -------------------------------------------------------------------------
    # path
    # -------------------------------------------------------------------------

    @property
    def path(
        self,
    ) -> Path:
        """
        Log file path.
        """

        return self._path


    # -------------------------------------------------------------------------
    # max_size
    # -------------------------------------------------------------------------

    @property
    def max_size(
        self,
    ) -> int:
        """
        Rotation size threshold (bytes).
        """

        return self._policy.max_size


    # -------------------------------------------------------------------------
    # max_files
    # -------------------------------------------------------------------------

    @property
    def max_files(
        self,
    ) -> int:
        """
        Maximum retained backup files.
        """

        return self._policy.max_files


    # -------------------------------------------------------------------------
    # rotation_count
    # -------------------------------------------------------------------------

    @property
    def rotation_count(
        self,
    ) -> int:
        """
        Number of completed rotations.
        """

        return self._rotation_count


    # -------------------------------------------------------------------------
    # backups
    # -------------------------------------------------------------------------

    @property
    def backups(
        self,
    ) -> List[Path]:
        """
        Return backup log files.

        Files are ordered by modification time
        (newest first).
        """

        directory = self._path.parent

        prefix = self._path.name + "."

        if not directory.exists():

            return []


        files = [

            p

            for p in directory.iterdir()

            if (

                p.is_file()

                and

                p.name.startswith(prefix)

            )

        ]


        files.sort(

            key=lambda p: p.stat().st_mtime,

            reverse=True,

        )


        return files


    # -------------------------------------------------------------------------
    # metadata
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
        Lifetime in seconds.
        """

        return (

            datetime.now(
                timezone.utc
            )

            -

            self.created_at

        ).total_seconds()


    # -------------------------------------------------------------------------
    # write_count
    # -------------------------------------------------------------------------

    @property
    def write_count(
        self,
    ) -> int:
        """
        Total write operations.
        """

        return int(

            self._statistics.get(
                "write",
                0,
            )

        )
# =============================================================================
# Part 3. Rotation API
# =============================================================================

    # -------------------------------------------------------------------------
    # Write
    # -------------------------------------------------------------------------

    def write(
        self,
        message: str,
        level: Optional[str] = None,
        **metadata: Any,
    ) -> LogRecord:
        """
        Write message into rotating log.
        """

        record = {

            "timestamp": datetime.now(
                timezone.utc
            ),

            "level": level or self.level,

            "message": message,

            "metadata": metadata,

        }

        return self.write_record(
            record
        )


    # -------------------------------------------------------------------------
    # Write Record
    # -------------------------------------------------------------------------

    def write_record(
        self,
        record: LogRecord,
    ) -> LogRecord:
        """
        Write structured log record.
        """

        if not self.enabled:

            return record

        if self.frozen:

            raise RuntimeError(
                "Handler is frozen."
            )

        if self.closed:

            raise RuntimeError(
                "Handler is closed."
            )

        started = time.perf_counter()

        self.before_write(
            record
        )

        if self.should_rotate():

            self.rotate()

        text = (
            f"[{record['timestamp']}] "
            f"[{record['level']}] "
            f"{record['message']}\n"
        )

        self._path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(
            self._path,
            self._mode,
            encoding=self._encoding,
        ) as fp:

            fp.write(text)

        self._statistics["write"] += 1

        self._last_result = record

        self.after_write(
            record
        )

        self._record_latency(
            started
        )

        self._touch()

        return record


    # -------------------------------------------------------------------------
    # Rotate
    # -------------------------------------------------------------------------

    def rotate(
        self,
    ) -> bool:
        """
        Execute log rotation.
        """

        if not self._path.exists():

            return False

        self.before_rotate()

        self.create_backup()

        self._rotation_count += 1

        self._statistics[
            "rotation"
        ] += 1

        self.after_rotate()

        return True


    # -------------------------------------------------------------------------
    # Should Rotate
    # -------------------------------------------------------------------------

    def should_rotate(
        self,
    ) -> bool:
        """
        Determine whether rotation
        is required.
        """

        strategy = (
            self.policy.strategy
        )

        if strategy == "size":

            return self.rotate_size()

        if strategy == "time":

            return self.rotate_time()

        return False


    # -------------------------------------------------------------------------
    # Rotate Size
    # -------------------------------------------------------------------------

    def rotate_size(
        self,
    ) -> bool:
        """
        Rotation by file size.
        """

        if not self._path.exists():

            return False

        return (

            self._path.stat().st_size

            >=

            self.max_size

        )


    # -------------------------------------------------------------------------
    # Rotate Time
    # -------------------------------------------------------------------------

    def rotate_time(
        self,
    ) -> bool:
        """
        Rotation by time policy.

        Placeholder implementation.
        """

        interval = (
            self.policy.interval
        )

        if interval is None:

            return False

        now = datetime.now(
            timezone.utc
        )

        age = (

            now

            -

            datetime.fromtimestamp(
                self._path.stat().st_mtime,
                timezone.utc,
            )

        ).total_seconds()

        mapping = {

            "hourly": 3600,

            "daily": 86400,

            "weekly": 604800,

        }

        return age >= mapping.get(
            interval,
            float("inf"),
        )


    # -------------------------------------------------------------------------
    # Create Backup
    # -------------------------------------------------------------------------

    def create_backup(
        self,
    ) -> Path:
        """
        Rotate current log
        into numbered backups.
        """

        for i in range(

            self.max_files - 1,

            0,

            -1,

        ):

            src = Path(
                f"{self.path}.{i}"
            )

            dst = Path(
                f"{self.path}.{i+1}"
            )

            if src.exists():

                src.replace(
                    dst
                )

        backup = Path(
            f"{self.path}.1"
        )

        self._path.replace(
            backup
        )

        return backup


    # -------------------------------------------------------------------------
    # Remove Backup
    # -------------------------------------------------------------------------

    def remove_backup(
        self,
        index: int,
    ) -> bool:
        """
        Remove backup file.
        """

        backup = Path(
            f"{self.path}.{index}"
        )

        if not backup.exists():

            return False

        backup.unlink()

        return True


    # -------------------------------------------------------------------------
    # Restore Backup
    # -------------------------------------------------------------------------

    def restore_backup(
        self,
        index: int = 1,
    ) -> bool:
        """
        Restore backup file
        as current log.
        """

        backup = Path(
            f"{self.path}.{index}"
        )

        if not backup.exists():

            return False

        if self._path.exists():

            self._path.unlink()

        backup.replace(
            self._path
        )

        return True
# =============================================================================
# Part 4. File Management API
# =============================================================================

    # -------------------------------------------------------------------------
    # Open
    # -------------------------------------------------------------------------

    def open(
        self,
    ):
        """
        Open log file.

        Returns
        -------
        TextIO
            Open file handle.
        """

        if self._closed:

            raise RuntimeError(
                "Handler is closed."
            )

        if self._file is not None:

            return self._file

        self._path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._file = self._path.open(
            mode=self._mode,
            encoding=self._encoding,
        )

        self._touch()

        return self._file



    # -------------------------------------------------------------------------
    # Close File
    # -------------------------------------------------------------------------

    def close_file(
        self,
    ) -> None:
        """
        Close current file handle.
        """

        if self._file is None:

            return

        try:

            self._file.flush()

            self._file.close()

        finally:

            self._file = None

            self._touch()



    # -------------------------------------------------------------------------
    # Flush
    # -------------------------------------------------------------------------

    def flush(
        self,
    ) -> None:
        """
        Flush buffered file contents.
        """

        if self._file is None:

            return

        self.before_flush()

        self._file.flush()

        self.after_flush([])

        self._touch()



    # -------------------------------------------------------------------------
    # Exists
    # -------------------------------------------------------------------------

    def exists(
        self,
    ) -> bool:
        """
        Return True if log file exists.
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

        return self._path.stat().st_size



    # -------------------------------------------------------------------------
    # Filename
    # -------------------------------------------------------------------------

    def filename(
        self,
    ) -> str:
        """
        Return filename only.
        """

        return self._path.name



    # -------------------------------------------------------------------------
    # Directory
    # -------------------------------------------------------------------------

    def directory(
        self,
    ) -> Path:
        """
        Return log directory.
        """

        return self._path.parent



    # -------------------------------------------------------------------------
    # Truncate
    # -------------------------------------------------------------------------

    def truncate(
        self,
    ) -> None:
        """
        Remove all file contents while
        preserving the file.
        """

        self.close_file()

        self._path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with self._path.open(
            "w",
            encoding=self._encoding,
        ):
            pass

        self._touch()



    # -------------------------------------------------------------------------
    # Delete
    # -------------------------------------------------------------------------

    def delete(
        self,
    ) -> bool:
        """
        Delete current log file.
        """

        self.close_file()

        if not self.exists():

            return False

        self._path.unlink()

        self._touch()

        return True



    # -------------------------------------------------------------------------
    # Reopen
    # -------------------------------------------------------------------------

    def reopen(
        self,
    ):
        """
        Reopen file handle.
        """

        self.close_file()

        return self.open()
# =============================================================================
# Part 5. Lifecycle API
# =============================================================================

    # -------------------------------------------------------------------------
    # Enable
    # -------------------------------------------------------------------------

    def enable(
        self,
    ) -> "RotatingHandler":
        """
        Enable log processing.
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
    ) -> "RotatingHandler":
        """
        Disable log processing.

        Existing configuration and file remain unchanged.
        """

        if self._closed:

            raise RuntimeError(
                "Cannot disable a closed handler."
            )

        self._enabled = False

        self._touch()

        return self



    # -------------------------------------------------------------------------
    # Freeze
    # -------------------------------------------------------------------------

    def freeze(
        self,
    ) -> "RotatingHandler":
        """
        Freeze handler configuration.

        Writing operations are rejected while frozen.
        """

        if self._closed:

            raise RuntimeError(
                "Cannot freeze a closed handler."
            )

        self._frozen = True

        self._touch()

        return self



    # -------------------------------------------------------------------------
    # Unfreeze
    # -------------------------------------------------------------------------

    def unfreeze(
        self,
    ) -> "RotatingHandler":
        """
        Restore write capability.
        """

        if self._closed:

            raise RuntimeError(
                "Cannot unfreeze a closed handler."
            )

        self._frozen = False

        self._touch()

        return self



    # -------------------------------------------------------------------------
    # Close
    # -------------------------------------------------------------------------

    def close(
        self,
    ) -> "RotatingHandler":
        """
        Close handler and release resources.
        """

        if self._closed:

            return self

        self.close_file()

        self._enabled = False

        self._frozen = False

        self._closed = True

        self._touch()

        return self



    # -------------------------------------------------------------------------
    # Reopen Handler
    # -------------------------------------------------------------------------

    def reopen_handler(
        self,
    ) -> "RotatingHandler":
        """
        Reopen a previously closed handler.
        """

        if not self._closed:

            return self

        self._closed = False

        self._enabled = True

        self._frozen = False

        self.open()

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
        Capture current runtime state.
        """

        return {

            "id": self.id,

            "name": self.name,

            "enabled": self.enabled,

            "frozen": self.frozen,

            "closed": self.closed,

            "level": self.level,

            "path": str(
                self.path
            ),

            "mode": self.mode,

            "encoding": self.encoding,

            "policy": copy.deepcopy(
                self.policy
            ),

            "metadata": copy.deepcopy(
                self.metadata
            ),

            "statistics": copy.deepcopy(
                self.statistics
            ),

            "rotation_count": self.rotation_count,

            "created_at": self.created_at,

            "updated_at": self.updated_at,

        )


    # -------------------------------------------------------------------------
    # Restore
    # -------------------------------------------------------------------------

    def restore(
        self,
        snapshot: Mapping[str, Any],
    ) -> "RotatingHandler":
        """
        Restore runtime state from snapshot.
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

        self._policy = copy.deepcopy(
            snapshot.get(
                "policy",
                self._policy,
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

        self._rotation_count = snapshot.get(
            "rotation_count",
            0,
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
    ) -> "RotatingHandler":
        """
        Create an independent handler clone.
        """

        cloned = self.__class__(

            path=self.path,

            name=self.name,

            level=self.level,

            policy=copy.deepcopy(
                self.policy
            ),

            mode=self.mode,

            encoding=self.encoding,

            enabled=self.enabled,

            metadata=copy.deepcopy(
                self.metadata
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
    ) -> "RotatingHandler":
        """
        Return a runtime copy.

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
        Optimize runtime resources.
        """

        removed = self.cleanup()

        return {

            "optimized": True,

            "removed_backups": removed,

            "rotation_count": self.rotation_count,

        }


    # -------------------------------------------------------------------------
    # Cleanup
    # -------------------------------------------------------------------------

    def cleanup(
        self,
    ) -> int:
        """
        Remove backup files exceeding retention policy.

        Returns
        -------
        int
            Number of deleted backups.
        """

        removed = 0

        backups = self.backups

        if len(backups) <= self.max_files:

            return removed

        for backup in backups[
            self.max_files:
        ]:

            try:

                backup.unlink()

                removed += 1

            except OSError:

                self._statistics[
                    "errors"
                ] += 1

        return removed


    # -------------------------------------------------------------------------
    # Compact
    # -------------------------------------------------------------------------

    def compact(
        self,
    ) -> Dict[str, Any]:
        """
        Compact runtime state.

        Performs lightweight maintenance.
        """

        before = len(
            self.backups
        )

        removed = self.cleanup()

        after = len(
            self.backups
        )

        self._touch()

        return {

            "before": before,

            "after": after,

            "removed": removed,

            "optimized": True,

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
        Return compact runtime summary.
        """

        return {

            "id": self.id,

            "name": self.name,

            "path": str(self.path),

            "enabled": self.enabled,

            "level": self.level,

            "status": self.status(),

            "write_count": self.write_count,

            "rotation_count": self.rotation_count,

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
        Generate complete diagnostics report.
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

                "status": self.status(),

            },

            "file": {

                "path": str(self.path),

                "exists": self.exists(),

                "size": self.size(),

                "directory": str(
                    self.directory()
                ),

            },

            "rotation": {

                "strategy": self.policy.strategy,

                "max_size": self.max_size,

                "max_files": self.max_files,

                "rotation_count": self.rotation_count,

                "backup_count": len(
                    self.backups
                ),

            },

            "statistics": copy.deepcopy(

                self.statistics

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

            not self.closed

            and

            self.error_count == 0

        )


        return {

            "healthy": healthy,

            "status": (

                "healthy"

                if healthy

                else "degraded"

            ),

            "errors": self.error_count,

            "file_exists": self.exists(),

            "backup_count": len(

                self.backups

            ),

        }



    # -------------------------------------------------------------------------
    # Status
    # -------------------------------------------------------------------------

    def status(
        self,
    ) -> str:
        """
        Return lifecycle status.
        """

        if self.closed:

            return "closed"

        if self.frozen:

            return "frozen"

        if not self.enabled:

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
        Total write operations.
        """

        return int(

            self._statistics.get(

                "write",

                0,

            )

        )



    # -------------------------------------------------------------------------
    # Rotation Count
    # -------------------------------------------------------------------------

    @property
    def rotation_count(
        self,
    ) -> int:
        """
        Total successful rotations.
        """

        return int(

            self._statistics.get(

                "rotation",

                self._rotation_count,

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
        Total runtime errors.
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
        Total accumulated runtime latency.
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
        Validate the complete handler.

        Validation includes:

        - configuration
        - file path
        - rotation policy
        - runtime integrity
        """

        return (

            self.check_configuration()

            and

            self.validate_path()

            and

            self.validate_rotation()

            and

            self.check_integrity()

        )



    # -------------------------------------------------------------------------
    # Validate Path
    # -------------------------------------------------------------------------

    def validate_path(
        self,
    ) -> bool:
        """
        Validate log file path.
        """

        try:

            path = Path(
                self._path
            )

        except Exception:

            return False


        if not path.name:

            return False


        parent = path.parent

        if parent.exists():

            return parent.is_dir()


        return True



    # -------------------------------------------------------------------------
    # Validate Record
    # -------------------------------------------------------------------------

    def validate_record(
        self,
        record: LogRecord,
    ) -> bool:
        """
        Validate log record structure.
        """

        if not isinstance(
            record,
            dict,
        ):

            return False


        required = (

            "timestamp",

            "level",

            "message",

        )


        for field in required:

            if field not in record:

                return False


        if (

            record["level"]

            not in

            SUPPORTED_LEVELS

        ):

            return False


        return True



    # -------------------------------------------------------------------------
    # Validate Rotation
    # -------------------------------------------------------------------------

    def validate_rotation(
        self,
    ) -> bool:
        """
        Validate rotation policy.
        """

        policy = self.policy


        if (

            policy.strategy

            not in

            SUPPORTED_ROTATION

        ):

            return False


        if policy.max_size <= 0:

            return False


        if policy.max_files < 1:

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

        if not self.name:

            return False


        if (

            self.level

            not in

            SUPPORTED_LEVELS

        ):

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
        Validate runtime integrity.
        """

        #
        # Closed handlers
        # must not stay enabled.
        #

        if (

            self.closed

            and

            self.enabled

        ):

            return False


        #
        # Rotation counter consistency.
        #

        if (

            self.rotation_count

            <

            0

        ):

            return False


        #
        # Write counter consistency.
        #

        if (

            self.write_count

            <

            0

        ):

            return False


        #
        # Error counter consistency.
        #

        if (

            self.error_count

            <

            0

        ):

            return False


        #
        # Latency must never
        # become negative.
        #

        if (

            self.latency

            <

            0

        ):

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
        record: LogRecord,
    ) -> None:
        """
        Emit event before writing a log record.
        """

        self.emit_event(
            "before_write",
            handler=self,
            record=record,
        )


    # -------------------------------------------------------------------------
    # After Write
    # -------------------------------------------------------------------------

    def after_write(
        self,
        record: LogRecord,
    ) -> None:
        """
        Emit event after writing a log record.
        """

        self.emit_event(
            "after_write",
            handler=self,
            record=record,
        )


    # -------------------------------------------------------------------------
    # Before Rotate
    # -------------------------------------------------------------------------

    def before_rotate(
        self,
    ) -> None:
        """
        Emit event before rotating log files.
        """

        self.emit_event(
            "before_rotate",
            handler=self,
            path=self.path,
            rotation=self.rotation_count + 1,
        )


    # -------------------------------------------------------------------------
    # After Rotate
    # -------------------------------------------------------------------------

    def after_rotate(
        self,
    ) -> None:
        """
        Emit event after rotation completes.
        """

        self.emit_event(
            "after_rotate",
            handler=self,
            path=self.path,
            rotation=self.rotation_count,
        )


    # -------------------------------------------------------------------------
    # Before Cleanup
    # -------------------------------------------------------------------------

    def before_cleanup(
        self,
    ) -> None:
        """
        Emit event before cleanup begins.
        """

        self.emit_event(
            "before_cleanup",
            handler=self,
            backups=len(self.backups),
        )


    # -------------------------------------------------------------------------
    # After Cleanup
    # -------------------------------------------------------------------------

    def after_cleanup(
        self,
        removed: int,
    ) -> None:
        """
        Emit event after cleanup finishes.
        """

        self.emit_event(
            "after_cleanup",
            handler=self,
            removed=removed,
            remaining=len(self.backups),
        )


    # -------------------------------------------------------------------------
    # Add Hook
    # -------------------------------------------------------------------------

    def add_hook(
        self,
        event: str,
        callback: Hook,
    ) -> "RotatingHandler":
        """
        Register callback for an event.
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
        Remove callback from an event.
        """

        callbacks = self._hooks.get(
            event,
        )

        if not callbacks:

            return False

        try:

            callbacks.remove(
                callback
            )

        except ValueError:

            return False

        if not callbacks:

            self._hooks.pop(
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
        Dispatch event to all registered hooks.
        """

        callbacks = self._hooks.get(
            event,
            [],
        )

        for callback in tuple(callbacks):

            try:

                callback(
                    **payload
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
    ) -> "RotatingHandler":
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

            f"path={str(self.path)!r}, "

            f"enabled={self.enabled}, "

            f"rotation_count={self.rotation_count}"

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

            f"writes={self.write_count}, "

            f"rotations={self.rotation_count}"

        )


    # -------------------------------------------------------------------------
    # __len__
    # -------------------------------------------------------------------------

    def __len__(
        self,
    ) -> int:
        """
        Return number of backup log files.
        """

        return len(
            self.backups
        )


    # -------------------------------------------------------------------------
    # __iter__
    # -------------------------------------------------------------------------

    def __iter__(
        self,
    ):
        """
        Iterate over backup log files.

        Example:
            for backup in handler:
                ...
        """

        return iter(
            self.backups
        )


    # -------------------------------------------------------------------------
    # __contains__
    # -------------------------------------------------------------------------

    def __contains__(
        self,
        item: str | Path,
    ) -> bool:
        """
        Membership test for backup files.

        Example:
            "runtime.log.1" in handler
        """

        target = Path(item)

        return any(

            backup == target

            or

            backup.name == target.name

            for backup in self.backups

        )


    # -------------------------------------------------------------------------
    # __call__
    # -------------------------------------------------------------------------

    def __call__(
        self,
        message: str,
        level: Optional[str] = None,
        **metadata: Any,
    ) -> LogRecord:
        """
        Callable handler.

        Equivalent to write().
        """

        return self.write(

            message=message,

            level=level,

            **metadata,

        )


    # -------------------------------------------------------------------------
    # __copy__
    # -------------------------------------------------------------------------

    def __copy__(
        self,
    ) -> "RotatingHandler":
        """
        Create a shallow runtime copy.
        """

        copied = self.__class__(

            path=self.path,

            name=self.name,

            level=self.level,

            policy=self.policy,

            mode=self.mode,

            encoding=self.encoding,

            enabled=self.enabled,

            metadata=self.metadata.copy(),

        )

        copied._statistics = (

            self.statistics.copy()

        )

        copied._rotation_count = (

            self.rotation_count

        )

        copied._frozen = self.frozen

        copied._closed = self.closed

        return copied


    # -------------------------------------------------------------------------
    # __deepcopy__
    # -------------------------------------------------------------------------

    def __deepcopy__(
        self,
        memo: Dict[int, Any],
    ) -> "RotatingHandler":
        """
        Create a fully independent clone.
        """

        if id(self) in memo:

            return memo[id(self)]

        cloned = self.clone()

        memo[id(self)] = cloned

        return cloned                                                                        
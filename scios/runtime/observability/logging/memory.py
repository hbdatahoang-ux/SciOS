# =============================================================================
# scios/runtime/observability/logging/memory.py
#
# Part 1. Foundation
#
# MemoryHandler
# =============================================================================


# =============================================================================
# Imports
# =============================================================================

from __future__ import annotations

import copy

import time

import uuid

from collections import deque

from datetime import datetime, timezone

from typing import (

    Any,

    Callable,

    Deque,

    Dict,

    Iterable,

    List,

    Mapping,

    Optional,

    TypeAlias,

)


# =============================================================================
# Constants
# =============================================================================

DEFAULT_MEMORY_NAME = "memory"

DEFAULT_LEVEL = "INFO"

DEFAULT_CAPACITY = 10000

DEFAULT_ENABLED = True


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

Statistics: TypeAlias = Dict[str, float | int]

LogRecord: TypeAlias = Dict[str, Any]

Hook: TypeAlias = Callable[..., None]


# =============================================================================
# MemoryHandler
# =============================================================================

class MemoryHandler:
    """
    In-memory logging handler.

    Provides fast runtime log storage for:

    - debugging
    - tracing
    - agent execution history
    - temporary buffering
    - runtime replay
    """


    # =========================================================================
    # __init__
    # =========================================================================

    def __init__(
        self,
        name: str = DEFAULT_MEMORY_NAME,
        level: str = DEFAULT_LEVEL,
        capacity: int = DEFAULT_CAPACITY,
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
        # Memory Configuration
        # ---------------------------------------------------------------------

        self._level: str = level.upper()

        self._capacity: int = capacity

        self._buffer: Deque[LogRecord] = deque(
            maxlen=capacity
        )


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

            "read": 0,

            "flush": 0,

            "errors": 0,

            "latency": 0.0,

        }


        # Runtime buffer

        self._last_result: Optional[LogRecord] = None



    # =========================================================================
    # Identity
    # =========================================================================

    @property
    def id(
        self,
    ) -> str:
        """
        Unique MemoryHandler identifier.
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

        self._name = str(value)

        self._touch()



    # =========================================================================
    # Runtime State
    # =========================================================================

    @property
    def enabled(
        self,
    ) -> bool:
        """
        Enabled state.
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
    # Memory Configuration
    # =========================================================================

    @property
    def level(
        self,
    ) -> str:
        """
        Logging level.
        """

        return self._level



    @property
    def capacity(
        self,
    ) -> int:
        """
        Maximum records stored.
        """

        return self._capacity



    @property
    def buffer(
        self,
    ) -> Deque[LogRecord]:
        """
        Internal memory buffer.
        """

        return self._buffer



    # =========================================================================
    # Metadata
    # =========================================================================

    @property
    def metadata(
        self,
    ) -> Metadata:
        """
        Handler metadata.
        """

        return self._metadata



    # =========================================================================
    # Statistics
    # =========================================================================

    @property
    def statistics(
        self,
    ) -> Statistics:
        """
        Runtime statistics.
        """

        return self._statistics



    @property
    def age(
        self,
    ) -> float:
        """
        Handler lifetime.
        """

        return (

            datetime.now(
                timezone.utc
            )

            -

            self.created_at

        ).total_seconds()



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
        Unique MemoryHandler identifier.
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

        if self._frozen:

            raise RuntimeError(
                "MemoryHandler is frozen."
            )

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
        Whether memory logging is enabled.
        """

        return self._enabled


    @enabled.setter
    def enabled(
        self,
        value: bool,
    ) -> None:
        """
        Enable or disable handler.
        """

        if self._closed:

            raise RuntimeError(
                "MemoryHandler is closed."
            )

        self._enabled = bool(value)

        self._touch()


    # -------------------------------------------------------------------------
    # Level
    # -------------------------------------------------------------------------

    @property
    def level(
        self,
    ) -> str:
        """
        Logging level.
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

        if self._frozen:

            raise RuntimeError(
                "MemoryHandler is frozen."
            )

        level = str(value).upper()

        if level not in SUPPORTED_LEVELS:

            raise ValueError(
                f"Unsupported level: {level}"
            )

        self._level = level

        self._touch()


    # -------------------------------------------------------------------------
    # Capacity
    # -------------------------------------------------------------------------

    @property
    def capacity(
        self,
    ) -> int:
        """
        Maximum buffer capacity.
        """

        return self._capacity


    @capacity.setter
    def capacity(
        self,
        value: int,
    ) -> None:
        """
        Update buffer capacity.
        """

        if self._frozen:

            raise RuntimeError(
                "MemoryHandler is frozen."
            )

        if value <= 0:

            raise ValueError(
                "Capacity must be positive."
            )

        old_records = list(
            self._buffer
        )

        self._capacity = int(value)

        self._buffer = deque(
            old_records[-value:],
            maxlen=value,
        )

        self._touch()


    # -------------------------------------------------------------------------
    # Buffer Size
    # -------------------------------------------------------------------------

    @property
    def buffer_size(
        self,
    ) -> int:
        """
        Current number of stored records.
        """

        return len(
            self._buffer
        )


    # -------------------------------------------------------------------------
    # Records
    # -------------------------------------------------------------------------

    @property
    def records(
        self,
    ) -> List[LogRecord]:
        """
        Return stored records.

        Returns copy to prevent
        external mutation.
        """

        return list(
            self._buffer
        )


    # -------------------------------------------------------------------------
    # Metadata
    # -------------------------------------------------------------------------

    @property
    def metadata(
        self,
    ) -> Metadata:
        """
        Runtime metadata.
        """

        return self._metadata


    @metadata.setter
    def metadata(
        self,
        value: Metadata,
    ) -> None:
        """
        Replace metadata.
        """

        if not isinstance(
            value,
            dict,
        ):

            raise TypeError(
                "Metadata must be dict."
            )

        self._metadata = value.copy()

        self._touch()


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
    # Write Count
    # -------------------------------------------------------------------------

    @property
    def write_count(
        self,
    ) -> int:
        """
        Total number of records written.
        """

        return int(
            self._statistics.get(
                "write",
                0,
            )
        )
# =============================================================================
# Part 3. Memory API
# =============================================================================

    # -------------------------------------------------------------------------
    # Write
    # -------------------------------------------------------------------------

    def write(
        self,
        message: Any,
        level: Optional[str] = None,
        **metadata: Any,
    ) -> LogRecord:
        """
        Write message into memory buffer.

        Creates a log record and stores it.
        """

        started = time.perf_counter()

        try:

            record = {

                "id": str(
                    uuid.uuid4()
                ),

                "message": message,

                "level": (

                    level.upper()

                    if level

                    else self._level

                ),

                "timestamp": datetime.now(
                    timezone.utc
                ),

                "metadata": metadata,

            }


            self.before_write(
                record
            )


            self._buffer.append(
                record
            )


            self._statistics["write"] += 1


            self._last_result = record


            self.after_write(
                record
            )


            return record


        except Exception:

            self._statistics["errors"] += 1

            raise


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
        message: Any,
        **metadata: Any,
    ) -> LogRecord:
        """
        Write message with newline semantic.
        """

        return self.write(
            f"{message}\n",
            **metadata,
        )



    # -------------------------------------------------------------------------
    # Write Record
    # -------------------------------------------------------------------------

    def write_record(
        self,
        record: LogRecord,
    ) -> LogRecord:
        """
        Store an existing log record.
        """

        started = time.perf_counter()

        try:

            if not self.validate_record(
                record
            ):

                raise ValueError(
                    "Invalid log record."
                )


            self.before_write(
                record
            )


            self._buffer.append(
                record
            )


            self._statistics["write"] += 1


            self._last_result = record


            self.after_write(
                record
            )


            return record


        except Exception:

            self._statistics["errors"] += 1

            raise


        finally:

            self._record_latency(
                started
            )

            self._touch()



    # -------------------------------------------------------------------------
    # Read
    # -------------------------------------------------------------------------

    def read(
        self,
        limit: Optional[int] = None,
    ) -> List[LogRecord]:
        """
        Read records from memory.

        Does not remove records.
        """

        self._statistics["read"] += 1


        records = list(
            self._buffer
        )


        if limit is not None:

            return records[-limit:]


        return records



    # -------------------------------------------------------------------------
    # Latest
    # -------------------------------------------------------------------------

    def latest(
        self,
        count: int = 1,
    ) -> List[LogRecord]:
        """
        Return latest records.
        """

        if count <= 0:

            return []


        return list(
            self._buffer
        )[-count:]



    # -------------------------------------------------------------------------
    # First
    # -------------------------------------------------------------------------

    def first(
        self,
        count: int = 1,
    ) -> List[LogRecord]:
        """
        Return oldest records.
        """

        if count <= 0:

            return []


        return list(
            self._buffer
        )[:count]



    # -------------------------------------------------------------------------
    # Pop
    # -------------------------------------------------------------------------

    def pop(
        self,
    ) -> Optional[LogRecord]:
        """
        Remove and return oldest record.
        """

        if not self._buffer:

            return None


        return self._buffer.popleft()



    # -------------------------------------------------------------------------
    # Clear
    # -------------------------------------------------------------------------

    def clear(
        self,
    ) -> None:
        """
        Remove all records.
        """

        self._buffer.clear()

        self._touch()



    # -------------------------------------------------------------------------
    # Flush
    # -------------------------------------------------------------------------

    def flush(
        self,
    ) -> List[LogRecord]:
        """
        Flush memory buffer.

        Returns records and clears buffer.
        """

        started = time.perf_counter()

        try:

            self.before_flush()


            records = list(
                self._buffer
            )


            self._buffer.clear()


            self._statistics["flush"] += 1


            self.after_flush(
                records
            )


            return records


        except Exception:

            self._statistics["errors"] += 1

            raise


        finally:

            self._record_latency(
                started
            )

            self._touch()
# =============================================================================
# Part 4. Buffer Operations API
# =============================================================================

    # -------------------------------------------------------------------------
    # Append
    # -------------------------------------------------------------------------

    def append(
        self,
        record: LogRecord,
    ) -> LogRecord:
        """
        Append a single record into memory buffer.
        """

        if not self.validate_record(
            record
        ):

            raise ValueError(
                "Invalid log record."
            )

        self._buffer.append(
            record
        )

        self._statistics["write"] += 1

        self._last_result = record

        self._touch()

        return record



    # -------------------------------------------------------------------------
    # Extend
    # -------------------------------------------------------------------------

    def extend(
        self,
        records: Iterable[LogRecord],
    ) -> int:
        """
        Append multiple records.
        """

        count = 0

        for record in records:

            self.append(
                record
            )

            count += 1


        return count



    # -------------------------------------------------------------------------
    # Insert
    # -------------------------------------------------------------------------

    def insert(
        self,
        index: int,
        record: LogRecord,
    ) -> LogRecord:
        """
        Insert record at position.

        Note:
        deque has no direct insert on older Python versions,
        so buffer is rebuilt.
        """

        if not self.validate_record(
            record
        ):

            raise ValueError(
                "Invalid log record."
            )


        records = list(
            self._buffer
        )


        records.insert(
            index,
            record,
        )


        self._buffer = deque(
            records[-self._capacity:],
            maxlen=self._capacity,
        )


        self._touch()

        return record



    # -------------------------------------------------------------------------
    # Remove
    # -------------------------------------------------------------------------

    def remove(
        self,
        record: LogRecord,
    ) -> bool:
        """
        Remove first matching record.
        """

        try:

            self._buffer.remove(
                record
            )

            self._touch()

            return True


        except ValueError:

            return False



    # -------------------------------------------------------------------------
    # Search
    # -------------------------------------------------------------------------

    def search(
        self,
        query: str,
    ) -> List[LogRecord]:
        """
        Search records by message content.
        """

        result = []


        for record in self._buffer:

            message = str(
                record.get(
                    "message",
                    "",
                )
            )


            if query.lower() in message.lower():

                result.append(
                    record
                )


        return result



    # -------------------------------------------------------------------------
    # Filter
    # -------------------------------------------------------------------------

    def filter(
        self,
        predicate: Callable[
            [LogRecord],
            bool,
        ],
    ) -> List[LogRecord]:
        """
        Filter records using callback.
        """

        if not callable(
            predicate
        ):

            raise TypeError(
                "Predicate must be callable."
            )


        return [

            record

            for record in self._buffer

            if predicate(record)

        ]



    # -------------------------------------------------------------------------
    # Slice
    # -------------------------------------------------------------------------

    def slice(
        self,
        start: int,
        end: Optional[int] = None,
    ) -> List[LogRecord]:
        """
        Return buffer slice.
        """

        records = list(
            self._buffer
        )

        return records[
            start:end
        ]



    # -------------------------------------------------------------------------
    # Resize
    # -------------------------------------------------------------------------

    def resize(
        self,
        capacity: int,
    ) -> int:
        """
        Resize memory buffer capacity.
        """

        if capacity <= 0:

            raise ValueError(
                "Capacity must be positive."
            )


        records = list(
            self._buffer
        )


        self._capacity = capacity


        self._buffer = deque(
            records[-capacity:],
            maxlen=capacity,
        )


        self._touch()

        return self._capacity



    # -------------------------------------------------------------------------
    # Compact
    # -------------------------------------------------------------------------

    def compact(
        self,
    ) -> int:
        """
        Remove invalid or empty records.

        Returns removed count.
        """

        before = len(
            self._buffer
        )


        cleaned = [

            record

            for record in self._buffer

            if (

                record

                and

                record.get(
                    "message"
                )

                is not None

            )

        ]


        self._buffer = deque(
            cleaned,
            maxlen=self._capacity,
        )


        removed = (

            before

            -

            len(
                self._buffer
            )

        )


        self._touch()

        return removed
# =============================================================================
# Part 5. Lifecycle API
# =============================================================================

    # -------------------------------------------------------------------------
    # Enable
    # -------------------------------------------------------------------------

    def enable(
        self,
    ) -> "MemoryHandler":
        """
        Enable memory logging.
        """

        if self._closed:

            raise RuntimeError(
                "Cannot enable closed MemoryHandler."
            )


        self._enabled = True

        self._touch()


        return self



    # -------------------------------------------------------------------------
    # Disable
    # -------------------------------------------------------------------------

    def disable(
        self,
    ) -> "MemoryHandler":
        """
        Disable memory logging.

        Existing records remain.
        """

        if self._closed:

            raise RuntimeError(
                "Cannot disable closed MemoryHandler."
            )


        self._enabled = False

        self._touch()


        return self



    # -------------------------------------------------------------------------
    # Freeze
    # -------------------------------------------------------------------------

    def freeze(
        self,
    ) -> "MemoryHandler":
        """
        Freeze configuration and buffer mutation.

        Read operations remain available.
        """

        if self._closed:

            raise RuntimeError(
                "Cannot freeze closed MemoryHandler."
            )


        self._frozen = True

        self._touch()


        return self



    # -------------------------------------------------------------------------
    # Unfreeze
    # -------------------------------------------------------------------------

    def unfreeze(
        self,
    ) -> "MemoryHandler":
        """
        Restore write operations.
        """

        if self._closed:

            raise RuntimeError(
                "Cannot unfreeze closed MemoryHandler."
            )


        self._frozen = False

        self._touch()


        return self



    # -------------------------------------------------------------------------
    # Close
    # -------------------------------------------------------------------------

    def close(
        self,
    ) -> "MemoryHandler":
        """
        Close handler.

        Clears active resources but keeps statistics.
        """

        if self._closed:

            return self


        self._enabled = False

        self._closed = True

        self._frozen = False


        self._touch()


        return self



    # -------------------------------------------------------------------------
    # Reopen
    # -------------------------------------------------------------------------

    def reopen(
        self,
    ) -> "MemoryHandler":
        """
        Reopen closed MemoryHandler.
        """

        if not self._closed:

            return self


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
    ) -> Dict[str, Any]:
        """
        Create runtime snapshot.

        Captures:
        - configuration
        - lifecycle state
        - metadata
        - statistics
        - memory records
        """

        return {

            "id": self.id,

            "name": self.name,

            "level": self.level,

            "capacity": self.capacity,

            "enabled": self.enabled,

            "frozen": self.frozen,

            "closed": self.closed,

            "metadata": copy.deepcopy(
                self.metadata
            ),

            "records": copy.deepcopy(
                self.records
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
    ) -> "MemoryHandler":
        """
        Restore runtime state from snapshot.
        """

        if not isinstance(
            snapshot,
            Mapping,
        ):

            raise TypeError(
                "Snapshot must be mapping."
            )


        self._name = snapshot.get(
            "name",
            self._name,
        )


        self._level = snapshot.get(
            "level",
            self._level,
        )


        self._capacity = snapshot.get(
            "capacity",
            self._capacity,
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


        self._metadata = copy.deepcopy(
            snapshot.get(
                "metadata",
                {},
            )
        )


        self._buffer = deque(
            copy.deepcopy(
                snapshot.get(
                    "records",
                    [],
                )
            ),
            maxlen=self._capacity,
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
    ) -> "MemoryHandler":
        """
        Create independent MemoryHandler clone.
        """

        cloned = self.__class__(

            name=self.name,

            level=self.level,

            capacity=self.capacity,

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
    ) -> "MemoryHandler":
        """
        Create shallow runtime copy.
        """

        return self.clone()



    # -------------------------------------------------------------------------
    # Optimize
    # -------------------------------------------------------------------------

    def optimize(
        self,
    ) -> Dict[str, Any]:
        """
        Optimize memory usage.

        Actions:
        - remove invalid records
        - shrink unused buffer
        - rebuild deque
        """

        before = len(
            self._buffer
        )


        removed = self.compact()


        self._buffer = deque(
            self._buffer,
            maxlen=self._capacity,
        )


        after = len(
            self._buffer
        )


        return {

            "before": before,

            "after": after,

            "removed": removed,

            "capacity": self._capacity,

        }



    # -------------------------------------------------------------------------
    # Cleanup
    # -------------------------------------------------------------------------

    def cleanup(
        self,
        keep_last: Optional[int] = None,
    ) -> int:
        """
        Cleanup old records.

        Returns removed count.
        """

        current = list(
            self._buffer
        )


        if keep_last is None:

            removed = len(
                current
            )

            self._buffer.clear()

            return removed



        if keep_last < 0:

            raise ValueError(
                "keep_last must be positive."
            )


        removed = max(
            0,
            len(current) - keep_last,
        )


        self._buffer = deque(
            current[-keep_last:],
            maxlen=self._capacity,
        )


        self._touch()


        return removed



    # -------------------------------------------------------------------------
    # Compact
    # -------------------------------------------------------------------------

    def compact(
        self,
    ) -> int:
        """
        Remove empty or invalid records.
        """

        before = len(
            self._buffer
        )


        valid_records = [

            record

            for record in self._buffer

            if (

                isinstance(
                    record,
                    dict,
                )

                and

                record.get(
                    "message"
                )

                is not None

            )

        ]


        self._buffer = deque(
            valid_records,
            maxlen=self._capacity,
        )


        removed = (

            before

            -

            len(
                self._buffer
            )

        )


        self._touch()


        return removed
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

            "enabled": self.enabled,

            "level": self.level,

            "capacity": self.capacity,

            "buffer_size": self.buffer_size,

            "write_count": self.write_count,

            "error_count": self.error_count,

            "age": self.age,

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
        Generate detailed diagnostic report.
        """

        return {

            "handler": {

                "id": self.id,

                "name": self.name,

                "type": self.__class__.__name__,

            },


            "state": {

                "enabled": self.enabled,

                "frozen": self.frozen,

                "closed": self.closed,

            },


            "memory": {

                "capacity": self.capacity,

                "buffer_size": self.buffer_size,

                "records": len(
                    self.records
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

            not self.closed

            and

            self.error_count == 0

        )


        return {

            "healthy": healthy,

            "status": (

                "ok"

                if healthy

                else "degraded"

            ),

            "errors": self.error_count,

            "buffer_usage": (

                self.buffer_size

                /

                self.capacity

            )

            if self.capacity

            else 0,

        }



    # -------------------------------------------------------------------------
    # Status
    # -------------------------------------------------------------------------

    def status(
        self,
    ) -> str:
        """
        Return lifecycle status string.
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
        Validate complete MemoryHandler state.

        Checks:
        - configuration
        - capacity
        - buffer integrity
        - lifecycle state
        """

        return (

            self.check_configuration()

            and

            self.validate_capacity()

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
        Validate individual log record.
        """

        if not isinstance(
            record,
            dict,
        ):

            return False


        required_fields = (

            "message",

        )


        for field in required_fields:

            if field not in record:

                return False


        return True



    # -------------------------------------------------------------------------
    # Validate Capacity
    # -------------------------------------------------------------------------

    def validate_capacity(
        self,
    ) -> bool:
        """
        Validate memory buffer capacity.
        """

        if not isinstance(
            self._capacity,
            int,
        ):

            return False


        if self._capacity <= 0:

            return False


        if self._buffer.maxlen != self._capacity:

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

        if not self._name:

            return False


        if self._level not in SUPPORTED_LEVELS:

            return False


        if self._capacity <= 0:

            return False


        if not isinstance(
            self._metadata,
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
        Validate runtime internal integrity.
        """

        if not isinstance(
            self._buffer,
            deque,
        ):

            return False


        for record in self._buffer:

            if not self.validate_record(
                record
            ):

                return False


        if self._closed and self._enabled:

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
        Execute hooks before writing record.

        Event:
            before_write
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
        Execute hooks after writing record.

        Event:
            after_write
        """

        self.emit_event(
            "after_write",
            handler=self,
            record=record,
        )



    # -------------------------------------------------------------------------
    # Before Flush
    # -------------------------------------------------------------------------

    def before_flush(
        self,
    ) -> None:
        """
        Execute hooks before flushing memory buffer.

        Event:
            before_flush
        """

        self.emit_event(
            "before_flush",
            handler=self,
            size=self.buffer_size,
        )



    # -------------------------------------------------------------------------
    # After Flush
    # -------------------------------------------------------------------------

    def after_flush(
        self,
        records: List[LogRecord],
    ) -> None:
        """
        Execute hooks after flushing.

        Event:
            after_flush
        """

        self.emit_event(
            "after_flush",
            handler=self,
            count=len(records),
            records=records,
        )



    # -------------------------------------------------------------------------
    # Add Hook
    # -------------------------------------------------------------------------

    def add_hook(
        self,
        event: str,
        callback: Hook,
    ) -> "MemoryHandler":
        """
        Register callback for event.
        """

        if not callable(
            callback
        ):

            raise TypeError(
                "Hook must be callable."
            )


        if event not in self._hooks:

            self._hooks[event] = []


        self._hooks[event].append(
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
        Remove callback from event.
        """

        hooks = self._hooks.get(
            event,
            [],
        )


        if callback not in hooks:

            return False


        hooks.remove(
            callback
        )


        if not hooks:

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
        Dispatch event callbacks.
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

                self._statistics["errors"] += 1



    # -------------------------------------------------------------------------
    # Subscribe
    # -------------------------------------------------------------------------

    def subscribe(
        self,
        event: str,
        callback: Hook,
    ) -> "MemoryHandler":
        """
        Subscribe to event.

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

        Used by:
            repr(memory)
        """

        return (

            f"{self.__class__.__name__}("

            f"id={self.id!r}, "

            f"name={self.name!r}, "

            f"level={self.level!r}, "

            f"capacity={self.capacity}, "

            f"buffer_size={self.buffer_size}, "

            f"enabled={self.enabled}, "

            f"closed={self.closed}"

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

        Used by:
            str(memory)
        """

        return (

            f"{self.name} "

            f"[{self.level}] "

            f"{self.status()} "

            f"({self.buffer_size}/"

            f"{self.capacity} records)"

        )



    # -------------------------------------------------------------------------
    # __len__
    # -------------------------------------------------------------------------

    def __len__(
        self,
    ) -> int:
        """
        Return current buffer size.

        Example:
            len(memory)
        """

        return self.buffer_size



    # -------------------------------------------------------------------------
    # __iter__
    # -------------------------------------------------------------------------

    def __iter__(
        self,
    ):
        """
        Iterate through records.

        Example:

            for record in memory:
                ...
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
        Membership test.

        Example:

            record in memory
        """

        return item in self._buffer



    # -------------------------------------------------------------------------
    # __getitem__
    # -------------------------------------------------------------------------

    def __getitem__(
        self,
        index: int | slice,
    ) -> LogRecord | List[LogRecord]:
        """
        Index access.

        Examples:

            memory[0]

            memory[1:10]
        """

        records = list(
            self._buffer
        )


        return records[index]



    # -------------------------------------------------------------------------
    # __call__
    # -------------------------------------------------------------------------

    def __call__(
        self,
        message: Any,
        level: Optional[str] = None,
        **metadata: Any,
    ) -> LogRecord:
        """
        Callable MemoryHandler.

        Example:

            memory("system started")

        Equivalent:

            memory.write(...)
        """

        return self.write(
            message,
            level=level,
            **metadata,
        )



    # -------------------------------------------------------------------------
    # __copy__
    # -------------------------------------------------------------------------

    def __copy__(
        self,
    ) -> "MemoryHandler":
        """
        Create shallow copy.
        """

        copied = self.__class__(

            name=self.name,

            level=self.level,

            capacity=self.capacity,

            enabled=self.enabled,

            metadata=self.metadata.copy(),

        )


        copied._buffer = deque(

            self._buffer,

            maxlen=self.capacity,

        )


        copied._statistics = (

            self.statistics.copy()

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
    ) -> "MemoryHandler":
        """
        Create deep independent copy.
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
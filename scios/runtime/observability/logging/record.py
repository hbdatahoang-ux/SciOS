"""
SciOS-NG
runtime/observability/logging/record.py

Part 1. Foundation
"""

from __future__ import annotations


# =============================================================================
# Imports
# =============================================================================

import uuid

from datetime import datetime
from datetime import timezone

from typing import Any
from typing import Dict
from typing import Mapping
from typing import Optional


from .level import LogLevel


# =============================================================================
# Constants
# =============================================================================

DEFAULT_SOURCE = "scios"

DEFAULT_MESSAGE = ""


# =============================================================================
# Type Aliases
# =============================================================================

LogContext = Dict[str, Any]

LogMetadata = Dict[str, Any]


# =============================================================================
# LogRecord
# =============================================================================

class LogRecord:
    """
    Core structured log event.

    Represents one logging event inside SciOS-NG.

    A LogRecord contains:

    - identity
    - timestamp
    - severity level
    - message
    - execution context
    - metadata
    - statistics
    """

    # -------------------------------------------------------------------------
    # Constructor
    # -------------------------------------------------------------------------

    def __init__(
        self,
        message: str = DEFAULT_MESSAGE,
        level: LogLevel | str | int = LogLevel.INFO,
        *,
        source: str = DEFAULT_SOURCE,
        context: Optional[Mapping[str, Any]] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ):
        """
        Initialize a LogRecord.
        """

        # ---------------------------------------------------------------------
        # Identity
        # ---------------------------------------------------------------------

        self.id = str(uuid.uuid4())

        self.source = source


        # ---------------------------------------------------------------------
        # Timestamp
        # ---------------------------------------------------------------------

        now = datetime.now(
            timezone.utc
        )

        self.created_at = now
        self.timestamp = now


        # ---------------------------------------------------------------------
        # Level
        # ---------------------------------------------------------------------

        self.level = LogLevel.normalize(
            level
        )


        # ---------------------------------------------------------------------
        # Message
        # ---------------------------------------------------------------------

        self.message = str(
            message
        )


        # ---------------------------------------------------------------------
        # Context
        # ---------------------------------------------------------------------

        self.context: LogContext = dict(
            context or {}
        )


        # ---------------------------------------------------------------------
        # Metadata
        # ---------------------------------------------------------------------

        self.metadata: LogMetadata = dict(
            metadata or {}
        )


        # ---------------------------------------------------------------------
        # Statistics
        # ---------------------------------------------------------------------

        self.statistics = {
            "formatted": 0,
            "serialized": 0,
            "processed": 0,
        }


    # -------------------------------------------------------------------------
    # End Foundation
    # -------------------------------------------------------------------------
# =============================================================================
# Part 2. Properties
# =============================================================================

    # -------------------------------------------------------------------------
    # Identity Properties
    # -------------------------------------------------------------------------

    @property
    def id(self) -> str:
        """
        Return unique record identifier.
        """

        return self._id

    # -------------------------------------------------------------------------

    @id.setter
    def id(self, value: str) -> None:
        self._id = str(value)


    # -------------------------------------------------------------------------
    # Timestamp Properties
    # -------------------------------------------------------------------------

    @property
    def created_at(self) -> datetime:
        """
        Return record creation timestamp.
        """

        return self._created_at


    # -------------------------------------------------------------------------

    @created_at.setter
    def created_at(self, value: datetime) -> None:
        self._created_at = value


    # -------------------------------------------------------------------------

    @property
    def timestamp(self) -> datetime:
        """
        Return current record timestamp.
        """

        return self._timestamp


    # -------------------------------------------------------------------------

    @timestamp.setter
    def timestamp(self, value: datetime) -> None:
        self._timestamp = value


    # -------------------------------------------------------------------------
    # Level Property
    # -------------------------------------------------------------------------

    @property
    def level(self) -> LogLevel:
        """
        Return normalized log level.
        """

        return self._level


    # -------------------------------------------------------------------------

    @level.setter
    def level(
        self,
        value: LogLevel | str | int,
    ) -> None:
        self._level = LogLevel.normalize(
            value
        )


    # -------------------------------------------------------------------------
    # Message Property
    # -------------------------------------------------------------------------

    @property
    def message(self) -> str:
        """
        Return log message.
        """

        return self._message


    # -------------------------------------------------------------------------

    @message.setter
    def message(
        self,
        value: str,
    ) -> None:
        self._message = str(value)


    # -------------------------------------------------------------------------
    # Source Property
    # -------------------------------------------------------------------------

    @property
    def source(self) -> str:
        """
        Return log source.
        """

        return self._source


    # -------------------------------------------------------------------------

    @source.setter
    def source(
        self,
        value: str,
    ) -> None:
        self._source = str(value)


    # -------------------------------------------------------------------------
    # Context Property
    # -------------------------------------------------------------------------

    @property
    def context(self) -> LogContext:
        """
        Return execution context.
        """

        return self._context


    # -------------------------------------------------------------------------

    @context.setter
    def context(
        self,
        value: Mapping[str, Any],
    ) -> None:
        self._context = dict(value)


    # -------------------------------------------------------------------------
    # Metadata Property
    # -------------------------------------------------------------------------

    @property
    def metadata(self) -> LogMetadata:
        """
        Return additional metadata.
        """

        return self._metadata


    # -------------------------------------------------------------------------

    @metadata.setter
    def metadata(
        self,
        value: Mapping[str, Any],
    ) -> None:
        self._metadata = dict(value)


    # -------------------------------------------------------------------------
    # Runtime Properties
    # -------------------------------------------------------------------------

    @property
    def age(self) -> float:
        """
        Return record age in seconds.

        Calculated from creation timestamp.
        """

        now = datetime.now(
            timezone.utc
        )

        delta = now - self.created_at

        return delta.total_seconds()


    # -------------------------------------------------------------------------

    @property
    def severity(self) -> int:
        """
        Return numeric severity value.

        Example:
            ERROR -> 40
        """

        return self.level.value
# =============================================================================
# Part 3. Mutation API
# =============================================================================

    # -------------------------------------------------------------------------
    # Message Mutation
    # -------------------------------------------------------------------------

    def set_message(
        self,
        message: str,
    ) -> "LogRecord":
        """
        Update log message.

        Returns
        -------
        LogRecord
            Self for chaining.
        """

        self.message = message

        return self


    # -------------------------------------------------------------------------
    # Level Mutation
    # -------------------------------------------------------------------------

    def set_level(
        self,
        level: LogLevel | str | int,
    ) -> "LogRecord":
        """
        Update log severity level.
        """

        self.level = level

        return self


    # -------------------------------------------------------------------------
    # Context Mutation
    # -------------------------------------------------------------------------

    def update_context(
        self,
        values: Mapping[str, Any],
    ) -> "LogRecord":
        """
        Update execution context.

        Existing keys are overwritten.
        """

        self.context.update(
            dict(values)
        )

        return self


    # -------------------------------------------------------------------------

    def add_context(
        self,
        key: str,
        value: Any,
    ) -> "LogRecord":
        """
        Add a single context field.
        """

        self.context[key] = value

        return self


    # -------------------------------------------------------------------------

    def clear_context(
        self,
    ) -> "LogRecord":
        """
        Remove all context information.
        """

        self.context.clear()

        return self


    # -------------------------------------------------------------------------
    # Metadata Mutation
    # -------------------------------------------------------------------------

    def update_metadata(
        self,
        values: Mapping[str, Any],
    ) -> "LogRecord":
        """
        Update record metadata.
        """

        self.metadata.update(
            dict(values)
        )

        return self


    # -------------------------------------------------------------------------

    def add_metadata(
        self,
        key: str,
        value: Any,
    ) -> "LogRecord":
        """
        Add a single metadata field.
        """

        self.metadata[key] = value

        return self


    # -------------------------------------------------------------------------

    def clear_metadata(
        self,
    ) -> "LogRecord":
        """
        Remove all metadata.
        """

        self.metadata.clear()

        return self
# =============================================================================
# Part 4. Context API
# =============================================================================

    # -------------------------------------------------------------------------
    # Context Access
    # -------------------------------------------------------------------------

    def get_context(
        self,
    ) -> LogContext:
        """
        Return a copy of execution context.

        A copy is returned to prevent accidental
        mutation from outside.
        """

        return dict(
            self.context
        )


    # -------------------------------------------------------------------------

    def get_metadata(
        self,
    ) -> LogMetadata:
        """
        Return a copy of metadata.
        """

        return dict(
            self.metadata
        )


    # -------------------------------------------------------------------------
    # Existence Check
    # -------------------------------------------------------------------------

    def has_context(
        self,
        key: str,
    ) -> bool:
        """
        Check whether a context key exists.
        """

        return key in self.context


    # -------------------------------------------------------------------------

    def has_metadata(
        self,
        key: str,
    ) -> bool:
        """
        Check whether a metadata key exists.
        """

        return key in self.metadata


    # -------------------------------------------------------------------------
    # Value Retrieval
    # -------------------------------------------------------------------------

    def context_value(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve a context value.

        Returns default if key does not exist.
        """

        return self.context.get(
            key,
            default,
        )


    # -------------------------------------------------------------------------

    def metadata_value(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve a metadata value.
        """

        return self.metadata.get(
            key,
            default,
        )


    # -------------------------------------------------------------------------
    # Removal API
    # -------------------------------------------------------------------------

    def remove_context(
        self,
        key: str,
    ) -> bool:
        """
        Remove a context field.

        Returns
        -------
        bool
            True if removed.
        """

        if key not in self.context:
            return False

        del self.context[key]

        return True


    # -------------------------------------------------------------------------

    def remove_metadata(
        self,
        key: str,
    ) -> bool:
        """
        Remove a metadata field.
        """

        if key not in self.metadata:
            return False

        del self.metadata[key]

        return True
# =============================================================================
# Part 5. State API
# =============================================================================

    # -------------------------------------------------------------------------
    # State Checks
    # -------------------------------------------------------------------------

    def is_empty(
        self,
    ) -> bool:
        """
        Check whether record has no meaningful content.
        """

        return (
            not self.message
            and not self.context
            and not self.metadata
        )


    # -------------------------------------------------------------------------

    def has_message(
        self,
    ) -> bool:
        """
        Check whether record contains a message.
        """

        return bool(
            self.message.strip()
        )


    # -------------------------------------------------------------------------

    def has_level(
        self,
    ) -> bool:
        """
        Check whether record has a valid log level.
        """

        return isinstance(
            self.level,
            LogLevel,
        )


    # -------------------------------------------------------------------------
    # Severity State
    # -------------------------------------------------------------------------

    def is_error(
        self,
    ) -> bool:
        """
        Check whether record represents an error.
        """

        return self.level.is_error or self.level.is_critical


    # -------------------------------------------------------------------------

    def is_warning(
        self,
    ) -> bool:
        """
        Check whether record represents a warning.
        """

        return self.level.is_warning


    # -------------------------------------------------------------------------

    def is_success(
        self,
    ) -> bool:
        """
        Check whether record represents a successful operation.

        INFO level messages without error severity
        are considered successful states.
        """

        return (
            self.level.is_info
            and not self.is_error()
            and not self.is_warning()
        )


    # -------------------------------------------------------------------------
    # Statistics State
    # -------------------------------------------------------------------------

    def mark_processed(
        self,
    ) -> "LogRecord":
        """
        Mark this record as processed by a handler.
        """

        self.increment_stat(
            "processed"
        )

        return self


    # -------------------------------------------------------------------------

    def increment_stat(
        self,
        name: str,
        amount: int = 1,
    ) -> "LogRecord":
        """
        Increment an internal statistic counter.

        Parameters
        ----------
        name:
            Statistic name.

        amount:
            Increment value.
        """

        if name not in self.statistics:

            self.statistics[name] = 0

        self.statistics[name] += amount

        return self
# =============================================================================
# Part 6. Statistics API
# =============================================================================

    # -------------------------------------------------------------------------
    # Statistics Access
    # -------------------------------------------------------------------------

    def stat(
        self,
        name: str,
        default: int = 0,
    ) -> int:
        """
        Return a single statistic value.
        """

        return int(
            self.statistics.get(
                name,
                default,
            )
        )


    # -------------------------------------------------------------------------

    def statistics(
        self,
    ) -> Dict[str, int]:
        """
        Return all statistics.

        Returns a copy to prevent
        external mutation.
        """

        return dict(
            self.statistics
        )


    # -------------------------------------------------------------------------
    # Statistics Management
    # -------------------------------------------------------------------------

    def reset_statistics(
        self,
    ) -> "LogRecord":
        """
        Reset all runtime counters.
        """

        self.statistics.clear()

        self.statistics.update(
            {
                "formatted": 0,
                "serialized": 0,
                "processed": 0,
            }
        )

        return self


    # -------------------------------------------------------------------------
    # Counter Helpers
    # -------------------------------------------------------------------------

    def processing_count(
        self,
    ) -> int:
        """
        Return number of processing operations.
        """

        return self.stat(
            "processed"
        )


    # -------------------------------------------------------------------------

    def formatted_count(
        self,
    ) -> int:
        """
        Return formatting operation count.
        """

        return self.stat(
            "formatted"
        )


    # -------------------------------------------------------------------------

    def serialized_count(
        self,
    ) -> int:
        """
        Return serialization operation count.
        """

        return self.stat(
            "serialized"
        )


    # -------------------------------------------------------------------------
    # Timestamp Operations
    # -------------------------------------------------------------------------

    def update_timestamp(
        self,
    ) -> "LogRecord":
        """
        Update record timestamp to current UTC time.
        """

        self.timestamp = datetime.now(
            timezone.utc
        )

        return self


    # -------------------------------------------------------------------------

    def touch(
        self,
    ) -> "LogRecord":
        """
        Refresh timestamp.

        Alias for update_timestamp().
        """

        return self.update_timestamp()
# =============================================================================
# Part 7. Serialization API
# =============================================================================

    # -------------------------------------------------------------------------
    # Convert To Dictionary
    # -------------------------------------------------------------------------

    def to_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Convert LogRecord into dictionary format.
        """

        return {
            "id": self.id,
            "source": self.source,

            "created_at": self.created_at.isoformat(),
            "timestamp": self.timestamp.isoformat(),

            "level": self.level.to_dict(),

            "message": self.message,

            "context": dict(
                self.context
            ),

            "metadata": dict(
                self.metadata
            ),

            "statistics": dict(
                self.statistics
            ),
        }


    # -------------------------------------------------------------------------
    # Create From Dictionary
    # -------------------------------------------------------------------------

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "LogRecord":
        """
        Create LogRecord from dictionary.
        """

        if not isinstance(data, Mapping):
            raise TypeError(
                "LogRecord data must be a mapping."
            )


        record = cls(
            message=data.get(
                "message",
                ""
            ),

            level=data.get(
                "level",
                LogLevel.INFO
            ),

            source=data.get(
                "source",
                DEFAULT_SOURCE
            ),

            context=data.get(
                "context",
                {}
            ),

            metadata=data.get(
                "metadata",
                {}
            ),
        )


        # Restore identity

        if "id" in data:
            record.id = data["id"]


        # Restore timestamps

        if "created_at" in data:

            record.created_at = datetime.fromisoformat(
                data["created_at"]
            )


        if "timestamp" in data:

            record.timestamp = datetime.fromisoformat(
                data["timestamp"]
            )


        # Restore statistics

        if "statistics" in data:

            record.statistics.update(
                data["statistics"]
            )


        return record


    # -------------------------------------------------------------------------
    # JSON Conversion
    # -------------------------------------------------------------------------

    def to_json(
        self,
        *,
        indent: int | None = None,
        ensure_ascii: bool = False,
    ) -> str:
        """
        Convert LogRecord to JSON string.
        """

        return json.dumps(
            self.to_dict(),
            indent=indent,
            ensure_ascii=ensure_ascii,
        )


    # -------------------------------------------------------------------------

    @classmethod
    def from_json(
        cls,
        data: str,
    ) -> "LogRecord":
        """
        Create LogRecord from JSON string.
        """

        return cls.from_dict(
            json.loads(data)
        )


    # -------------------------------------------------------------------------
    # Generic Serialization
    # -------------------------------------------------------------------------

    def serialize(
        self,
    ) -> Dict[str, Any]:
        """
        Generic serialization interface.
        """

        self.increment_stat(
            "serialized"
        )

        return self.to_dict()


    # -------------------------------------------------------------------------

    @classmethod
    def deserialize(
        cls,
        data: Mapping[str, Any] | str,
    ) -> "LogRecord":
        """
        Generic deserialization interface.
        """

        if isinstance(data, str):

            return cls.from_json(
                data
            )


        return cls.from_dict(
            data
        )


    # -------------------------------------------------------------------------
    # Clone
    # -------------------------------------------------------------------------

    def clone(
        self,
    ) -> "LogRecord":
        """
        Create an independent copy of this record.
        """

        return self.from_dict(
            self.to_dict()
        )
# =============================================================================
# Part 8. Comparison API
# =============================================================================

    # -------------------------------------------------------------------------
    # Equality Comparison
    # -------------------------------------------------------------------------

    def equals(
        self,
        other: "LogRecord",
    ) -> bool:
        """
        Check whether two records are equivalent.
        """

        if not isinstance(
            other,
            LogRecord,
        ):
            return False


        return (
            self.id == other.id
            and
            self.level == other.level
            and
            self.message == other.message
            and
            self.source == other.source
            and
            self.context == other.context
            and
            self.metadata == other.metadata
        )


    # -------------------------------------------------------------------------
    # Source Comparison
    # -------------------------------------------------------------------------

    def same_source(
        self,
        other: "LogRecord | str",
    ) -> bool:
        """
        Check whether records have the same source.
        """

        if isinstance(
            other,
            LogRecord,
        ):

            return self.source == other.source


        return self.source == str(other)


    # -------------------------------------------------------------------------
    # Level Comparison
    # -------------------------------------------------------------------------

    def same_level(
        self,
        other: "LogRecord | LogLevel | str | int",
    ) -> bool:
        """
        Check whether records have the same log level.
        """

        if isinstance(
            other,
            LogRecord,
        ):

            return self.level == other.level


        return self.level == LogLevel.normalize(
            other
        )


    # -------------------------------------------------------------------------
    # Pattern Matching
    # -------------------------------------------------------------------------

    def matches(
        self,
        *,
        source: str | None = None,
        level: LogLevel | str | int | None = None,
        message: str | None = None,
    ) -> bool:
        """
        Match record against filtering criteria.
        """

        if source is not None:

            if self.source != source:
                return False


        if level is not None:

            if not self.same_level(level):
                return False


        if message is not None:

            if message not in self.message:
                return False


        return True


    # -------------------------------------------------------------------------
    # Timestamp Comparison
    # -------------------------------------------------------------------------

    def compare_timestamp(
        self,
        other: "LogRecord",
    ) -> int:
        """
        Compare timestamps.

        Returns
        -------
        1:
            self newer than other

        0:
            same timestamp

        -1:
            self older than other
        """

        if self.timestamp > other.timestamp:

            return 1


        if self.timestamp < other.timestamp:

            return -1


        return 0


    # -------------------------------------------------------------------------

    def older_than(
        self,
        other: "LogRecord",
    ) -> bool:
        """
        Check whether this record is older.
        """

        return (
            self.timestamp
            <
            other.timestamp
        )


    # -------------------------------------------------------------------------

    def newer_than(
        self,
        other: "LogRecord",
    ) -> bool:
        """
        Check whether this record is newer.
        """

        return (
            self.timestamp
            >
            other.timestamp
        )


    # -------------------------------------------------------------------------
    # Generic Comparison
    # -------------------------------------------------------------------------

    def compare(
        self,
        other: "LogRecord",
    ) -> int:
        """
        Compare two records.

        Priority:
        1. Timestamp
        2. Severity
        """

        timestamp_result = self.compare_timestamp(
            other
        )

        if timestamp_result != 0:

            return timestamp_result


        if self.level > other.level:

            return 1


        if self.level < other.level:

            return -1


        return 0
# =============================================================================
# Part 9. Events & Hooks
# =============================================================================

    # -------------------------------------------------------------------------
    # Event Lifecycle
    # -------------------------------------------------------------------------

    def before_emit(
        self,
    ) -> None:
        """
        Trigger before record emission.

        Used by:
        - handlers
        - serializers
        - telemetry exporters
        """

        self.emit(
            "before_emit",
            record=self,
        )


    # -------------------------------------------------------------------------

    def after_emit(
        self,
    ) -> None:
        """
        Trigger after record emission.
        """

        self.emit(
            "after_emit",
            record=self,
        )


    # -------------------------------------------------------------------------

    def before_update(
        self,
        field: str,
        value: Any,
    ) -> None:
        """
        Trigger before record mutation.
        """

        self.emit(
            "before_update",
            record=self,
            field=field,
            value=value,
        )


    # -------------------------------------------------------------------------

    def after_update(
        self,
        field: str,
        value: Any,
    ) -> None:
        """
        Trigger after record mutation.
        """

        self.emit(
            "after_update",
            record=self,
            field=field,
            value=value,
        )


    # -------------------------------------------------------------------------
    # Hook Management
    # -------------------------------------------------------------------------

    def add_hook(
        self,
        event: str,
        callback,
    ) -> "LogRecord":
        """
        Register an event callback.
        """

        if not hasattr(
            self,
            "_hooks",
        ):
            self._hooks = {}


        if event not in self._hooks:

            self._hooks[event] = []


        self._hooks[event].append(
            callback
        )


        return self


    # -------------------------------------------------------------------------

    def remove_hook(
        self,
        event: str,
        callback,
    ) -> bool:
        """
        Remove a registered callback.
        """

        hooks = getattr(
            self,
            "_hooks",
            {},
        )


        if event not in hooks:

            return False


        if callback not in hooks[event]:

            return False


        hooks[event].remove(
            callback
        )


        return True


    # -------------------------------------------------------------------------

    def emit(
        self,
        event: str,
        **payload,
    ) -> None:
        """
        Emit event to registered hooks.
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


        for callback in list(callbacks):

            try:

                callback(
                    **payload
                )

            except Exception:

                # Hooks must never break logging pipeline.
                continue


    # -------------------------------------------------------------------------

    def subscribe(
        self,
        event: str,
        callback,
    ) -> "LogRecord":
        """
        Alias for add_hook().

        Provides event subscription style API.
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
        Developer representation.
        """

        return (
            f"LogRecord("
            f"id={self.id!r}, "
            f"level={self.level.name!r}, "
            f"message={self.message!r}, "
            f"source={self.source!r}"
            f")"
        )


    # -------------------------------------------------------------------------

    def __str__(
        self,
    ) -> str:
        """
        Human readable representation.
        """

        return (
            f"[{self.level.name}] "
            f"{self.message}"
        )


    # -------------------------------------------------------------------------
    # Collection Protocols
    # -------------------------------------------------------------------------

    def __len__(
        self,
    ) -> int:
        """
        Return number of attached data fields.
        """

        return (
            len(self.context)
            +
            len(self.metadata)
        )


    # -------------------------------------------------------------------------

    def __iter__(
        self,
    ):
        """
        Iterate through serialized fields.
        """

        return iter(
            self.to_dict()
        )


    # -------------------------------------------------------------------------

    def __contains__(
        self,
        key: str,
    ) -> bool:
        """
        Check whether field exists.
        """

        return (
            key in self.context
            or
            key in self.metadata
            or
            key in self.to_dict()
        )


    # -------------------------------------------------------------------------
    # Comparison Protocols
    # -------------------------------------------------------------------------

    def __eq__(
        self,
        other: object,
    ) -> bool:
        """
        Equality comparison.
        """

        if not isinstance(
            other,
            LogRecord,
        ):
            return False


        return self.equals(
            other
        )


    # -------------------------------------------------------------------------

    def __hash__(
        self,
    ) -> int:
        """
        Hash based on immutable identity.
        """

        return hash(
            self.id
        )


    # -------------------------------------------------------------------------
    # Boolean Protocol
    # -------------------------------------------------------------------------

    def __bool__(
        self,
    ) -> bool:
        """
        Record is valid when it contains message
        and a valid level.
        """

        return (
            self.has_message()
            and
            self.has_level()
        )


    # -------------------------------------------------------------------------
    # Copy Protocols
    # -------------------------------------------------------------------------

    def __copy__(
        self,
    ) -> "LogRecord":
        """
        Shallow copy.
        """

        return self.clone()


    # -------------------------------------------------------------------------

    def __deepcopy__(
        self,
        memo,
    ) -> "LogRecord":
        """
        Deep copy.
        """

        return self.clone()                                                                    
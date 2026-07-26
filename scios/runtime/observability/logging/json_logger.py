# =============================================================================
# scios/runtime/observability/logging/json_logger.py
#
# Part 1. Foundation
# =============================================================================

from __future__ import annotations

# =============================================================================
# Imports
# =============================================================================

import copy
import json
import time
import uuid

from dataclasses import dataclass, field
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
    Union,
)

# =============================================================================
# Constants
# =============================================================================

DEFAULT_LOGGER_NAME = "json_logger"

DEFAULT_LEVEL = "INFO"

DEFAULT_ENABLED = True

DEFAULT_PRETTY = False

DEFAULT_INDENT = 4

DEFAULT_SORT_KEYS = False

DEFAULT_ENCODING = "utf-8"

SUPPORTED_LEVELS = (
    "TRACE",
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
)

JSON_VERSION = "1.0"

# =============================================================================
# Type Aliases
# =============================================================================

Metadata: TypeAlias = Dict[str, Any]

Statistics: TypeAlias = Dict[str, Union[int, float]]

Hook: TypeAlias = Callable[..., None]

JSONValue: TypeAlias = Union[
    None,
    bool,
    int,
    float,
    str,
    list,
    dict,
]

JSONRecordDict: TypeAlias = Dict[str, JSONValue]

# =============================================================================
# JSONLogRecord
# =============================================================================


@dataclass(slots=True)
class JSONLogRecord:
    """
    Structured JSON log record.
    """

    timestamp: datetime

    level: str

    message: str

    logger: str

    metadata: Metadata = field(
        default_factory=dict
    )

    extra: Metadata = field(
        default_factory=dict
    )

    def to_dict(
        self,
    ) -> JSONRecordDict:

        return {

            "timestamp": self.timestamp.isoformat(),

            "level": self.level,

            "logger": self.logger,

            "message": self.message,

            "metadata": self.metadata,

            "extra": self.extra,

        }


# =============================================================================
# JSONLogger
# =============================================================================


class JSONLogger:
    """
    Structured JSON logger for SciOS-NG.

    Features
    --------
    • JSON serialization
    • Structured logging
    • OpenTelemetry compatible payload
    • ELK / Loki friendly output
    • Runtime diagnostics
    """

    # =========================================================================
    # __init__
    # =========================================================================

    def __init__(
        self,
        name: str = DEFAULT_LOGGER_NAME,
        level: str = DEFAULT_LEVEL,
        *,
        pretty: bool = DEFAULT_PRETTY,
        indent: int = DEFAULT_INDENT,
        sort_keys: bool = DEFAULT_SORT_KEYS,
        enabled: bool = DEFAULT_ENABLED,
        metadata: Optional[Metadata] = None,
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
            JSONLogRecord
        ] = None

        # ---------------------------------------------------------------------
        # JSON Configuration
        # ---------------------------------------------------------------------

        self._level = level.upper()

        self._pretty = pretty

        self._indent = indent

        self._sort_keys = sort_keys

        self._encoding = DEFAULT_ENCODING

        # ---------------------------------------------------------------------
        # Metadata
        # ---------------------------------------------------------------------

        self._metadata: Metadata = (
            metadata.copy()
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

            "serialized": 0,

            "errors": 0,

            "latency": 0.0,

        }

    # =========================================================================
    # Identity
    # =========================================================================

    @property
    def id(
        self,
    ) -> str:
        """
        Unique logger identifier.
        """

        return self._id

    @property
    def name(
        self,
    ) -> str:
        """
        Logger name.
        """

        return self._name

    # =========================================================================
    # Runtime State
    # =========================================================================

    @property
    def enabled(
        self,
    ) -> bool:
        """
        Whether logger is enabled.
        """

        return self._enabled

    @property
    def frozen(
        self,
    ) -> bool:
        """
        Frozen state.
        """

        return self._frozen

    @property
    def closed(
        self,
    ) -> bool:
        """
        Closed state.
        """

        return self._closed

    # =========================================================================
    # JSON Configuration
    # =========================================================================

    @property
    def level(
        self,
    ) -> str:
        """
        Default log level.
        """

        return self._level

    @property
    def pretty(
        self,
    ) -> bool:
        """
        Pretty-print JSON.
        """

        return self._pretty

    @property
    def indent(
        self,
    ) -> int:
        """
        JSON indentation width.
        """

        return self._indent

    @property
    def sort_keys(
        self,
    ) -> bool:
        """
        Sort JSON keys.
        """

        return self._sort_keys

    @property
    def encoding(
        self,
    ) -> str:
        """
        Output encoding.
        """

        return self._encoding

    # =========================================================================
    # Metadata
    # =========================================================================

    @property
    def metadata(
        self,
    ) -> Metadata:
        """
        Logger metadata.
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
        Lifetime in seconds.
        """

        return (

            datetime.now(
                timezone.utc
            )

            -

            self.created_at

        ).total_seconds()

    @property
    def record_count(
        self,
    ) -> int:
        """
        Total JSON records created.
        """

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
        Accumulate runtime latency.
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
    # id
    # -------------------------------------------------------------------------

    @property
    def id(
        self,
    ) -> str:
        """
        Unique logger identifier.
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
        Whether logger is enabled.
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
        Default logging level.
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
    # pretty
    # -------------------------------------------------------------------------

    @property
    def pretty(
        self,
    ) -> bool:
        """
        Pretty-print JSON output.
        """

        return self._pretty


    @pretty.setter
    def pretty(
        self,
        value: bool,
    ) -> None:

        self._pretty = bool(value)

        self._touch()


    # -------------------------------------------------------------------------
    # indent
    # -------------------------------------------------------------------------

    @property
    def indent(
        self,
    ) -> int:
        """
        JSON indentation.
        """

        return self._indent


    @indent.setter
    def indent(
        self,
        value: int,
    ) -> None:

        if value < 0:

            raise ValueError(
                "Indent must be non-negative."
            )

        self._indent = int(value)

        self._touch()


    # -------------------------------------------------------------------------
    # sort_keys
    # -------------------------------------------------------------------------

    @property
    def sort_keys(
        self,
    ) -> bool:
        """
        Whether JSON keys are sorted.
        """

        return self._sort_keys


    @sort_keys.setter
    def sort_keys(
        self,
        value: bool,
    ) -> None:

        self._sort_keys = bool(value)

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
        Total JSON log records.
        """

        return int(

            self._statistics.get(

                "records",

                0,

            )

        )
# =============================================================================
# Part 3. Logging API
# =============================================================================

    # -------------------------------------------------------------------------
    # Log
    # -------------------------------------------------------------------------

    def log(
        self,
        message: str,
        level: Optional[str] = None,
        **extra: Any,
    ) -> JSONLogRecord:
        """
        Create and serialize a structured JSON log record.
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

        record = JSONLogRecord(

            timestamp=datetime.now(
                timezone.utc
            ),

            level=level,

            logger=self.name,

            message=str(message),

            metadata=copy.deepcopy(
                self.metadata
            ),

            extra=copy.deepcopy(
                extra
            ),

        )

        self._last_record = record

        self._statistics["records"] += 1

        self.serialize(
            record
        )

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
    ) -> JSONLogRecord:

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
    ) -> JSONLogRecord:

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
    ) -> JSONLogRecord:

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
    ) -> JSONLogRecord:

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
    ) -> JSONLogRecord:

        return self.log(
            message,
            level="CRITICAL",
            **extra,
        )


    # -------------------------------------------------------------------------
    # Exception
    # -------------------------------------------------------------------------

    def exception(
        self,
        exc: BaseException,
        **extra: Any,
    ) -> JSONLogRecord:
        """
        Log an exception.
        """

        return self.log(

            message=str(exc),

            level="ERROR",

            exception=exc.__class__.__name__,

            **extra,

        )


    # -------------------------------------------------------------------------
    # Serialize
    # -------------------------------------------------------------------------

    def serialize(
        self,
        record: JSONLogRecord,
    ) -> str:
        """
        Serialize a JSONLogRecord into JSON.
        """

        payload = json.dumps(

            record.to_dict(),

            indent=(
                self.indent
                if self.pretty
                else None
            ),

            sort_keys=self.sort_keys,

            ensure_ascii=False,

        )

        self._statistics[
            "serialized"
        ] += 1

        return payload


    # -------------------------------------------------------------------------
    # Deserialize
    # -------------------------------------------------------------------------

    def deserialize(
        self,
        payload: str,
    ) -> JSONLogRecord:
        """
        Deserialize JSON into JSONLogRecord.
        """

        data = json.loads(
            payload
        )

        return JSONLogRecord(

            timestamp=datetime.fromisoformat(

                data["timestamp"]

            ),

            level=data["level"],

            logger=data["logger"],

            message=data["message"],

            metadata=data.get(
                "metadata",
                {},
            ),

            extra=data.get(
                "extra",
                {},
            ),

        )
# =============================================================================
# Part 4. JSON API
# =============================================================================

    # -------------------------------------------------------------------------
    # Encode
    # -------------------------------------------------------------------------

    def encode(
        self,
        obj: Any,
    ) -> str:
        """
        Encode a Python object into a JSON string.
        """

        return json.dumps(

            obj,

            indent=(
                self.indent
                if self.pretty
                else None
            ),

            sort_keys=self.sort_keys,

            ensure_ascii=False,

        )


    # -------------------------------------------------------------------------
    # Decode
    # -------------------------------------------------------------------------

    def decode(
        self,
        payload: str,
    ) -> Any:
        """
        Decode a JSON string into a Python object.
        """

        return json.loads(
            payload
        )


    # -------------------------------------------------------------------------
    # Dumps
    # -------------------------------------------------------------------------

    def dumps(
        self,
        obj: Any,
    ) -> str:
        """
        Alias of encode().
        """

        return self.encode(
            obj
        )


    # -------------------------------------------------------------------------
    # Loads
    # -------------------------------------------------------------------------

    def loads(
        self,
        payload: str,
    ) -> Any:
        """
        Alias of decode().
        """

        return self.decode(
            payload
        )


    # -------------------------------------------------------------------------
    # Validate JSON
    # -------------------------------------------------------------------------

    def validate_json(
        self,
        payload: str,
    ) -> bool:
        """
        Validate whether a string contains valid JSON.
        """

        try:

            json.loads(
                payload
            )

            return True

        except (
            TypeError,
            ValueError,
            json.JSONDecodeError,
        ):

            self._statistics[
                "errors"
            ] += 1

            return False


    # -------------------------------------------------------------------------
    # Format JSON
    # -------------------------------------------------------------------------

    def format_json(
        self,
        payload: str,
    ) -> str:
        """
        Pretty-format a JSON string.
        """

        obj = self.decode(
            payload
        )

        return json.dumps(

            obj,

            indent=self.indent,

            sort_keys=self.sort_keys,

            ensure_ascii=False,

        )


    # -------------------------------------------------------------------------
    # Export
    # -------------------------------------------------------------------------

    def export(
        self,
        obj: Any,
        path: str | Path,
    ) -> Path:
        """
        Export an object as a JSON file.
        """

        path = Path(
            path
        )

        path.parent.mkdir(

            parents=True,

            exist_ok=True,

        )

        with path.open(

            "w",

            encoding=self.encoding,

        ) as fp:

            json.dump(

                obj,

                fp,

                indent=(
                    self.indent
                    if self.pretty
                    else None
                ),

                sort_keys=self.sort_keys,

                ensure_ascii=False,

            )

        self._touch()

        return path


    # -------------------------------------------------------------------------
    # Import JSON
    # -------------------------------------------------------------------------

    def import_json(
        self,
        path: str | Path,
    ) -> Any:
        """
        Import a JSON object from disk.
        """

        path = Path(
            path
        )

        with path.open(

            "r",

            encoding=self.encoding,

        ) as fp:

            data = json.load(
                fp
            )

        self._touch()

        return data
# =============================================================================
# Part 5. Lifecycle API
# =============================================================================

    # -------------------------------------------------------------------------
    # Enable
    # -------------------------------------------------------------------------

    def enable(
        self,
    ) -> "JSONLogger":
        """
        Enable the logger.
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
    ) -> "JSONLogger":
        """
        Disable the logger.

        Logging requests will be ignored or rejected
        until the logger is enabled again.
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
    ) -> "JSONLogger":
        """
        Freeze the logger.

        Configuration becomes read-only and no new
        log records may be created.
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
    ) -> "JSONLogger":
        """
        Resume normal logging operations.
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
    ) -> "JSONLogger":
        """
        Permanently close the logger.
        """

        if self._closed:

            return self

        self._enabled = False

        self._frozen = False

        self._closed = True

        self._touch()

        return self


    # -------------------------------------------------------------------------
    # Reopen
    # -------------------------------------------------------------------------

    def reopen(
        self,
    ) -> "JSONLogger":
        """
        Reopen a previously closed logger.
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
        Capture current runtime state.
        """

        return {

            "id": self.id,

            "name": self.name,

            "enabled": self.enabled,

            "frozen": self.frozen,

            "closed": self.closed,

            "level": self.level,

            "pretty": self.pretty,

            "indent": self.indent,

            "sort_keys": self.sort_keys,

            "encoding": self.encoding,

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
    ) -> "JSONLogger":
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

        self._pretty = snapshot.get(
            "pretty",
            self._pretty,
        )

        self._indent = snapshot.get(
            "indent",
            self._indent,
        )

        self._sort_keys = snapshot.get(
            "sort_keys",
            self._sort_keys,
        )

        self._encoding = snapshot.get(
            "encoding",
            self._encoding,
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
    ) -> "JSONLogger":
        """
        Create an independent clone.
        """

        cloned = self.__class__(

            name=self.name,

            level=self.level,

            pretty=self.pretty,

            indent=self.indent,

            sort_keys=self.sort_keys,

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
    ) -> "JSONLogger":
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
        Optimize runtime configuration.
        """

        removed = self.cleanup()

        return {

            "optimized": True,

            "removed": removed,

            "record_count": self.record_count,

        }


    # -------------------------------------------------------------------------
    # Cleanup
    # -------------------------------------------------------------------------

    def cleanup(
        self,
    ) -> int:
        """
        Cleanup transient runtime state.

        Returns
        -------
        int
            Number of cleaned objects.
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
        Compact runtime memory.

        Removes temporary state and
        compacts internal metadata.
        """

        before = len(
            self.metadata
        )

        self._metadata = {

            k: v

            for k, v in self._metadata.items()

            if v is not None

        }

        removed = self.cleanup()

        after = len(
            self.metadata
        )

        self._touch()

        return {

            "optimized": True,

            "metadata_before": before,

            "metadata_after": after,

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
        Return a compact runtime summary.
        """

        return {

            "id": self.id,

            "name": self.name,

            "enabled": self.enabled,

            "level": self.level,

            "status": self.status(),

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
        Return a detailed diagnostics report.
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

            "configuration": {

                "level": self.level,

                "pretty": self.pretty,

                "indent": self.indent,

                "sort_keys": self.sort_keys,

                "encoding": self.encoding,

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
        Return runtime health information.
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

            "records": self.record_count,

            "errors": self.error_count,

            "uptime": self.uptime,

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
    # Record Count
    # -------------------------------------------------------------------------

    @property
    def record_count(
        self,
    ) -> int:
        """
        Total JSON log records.
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
        Validate the complete JSONLogger runtime.

        This method validates:

        - configuration
        - logger state
        - runtime integrity
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
        record: JSONLogRecord,
    ) -> bool:
        """
        Validate a JSONLogRecord.
        """

        if not isinstance(
            record,
            JSONLogRecord,
        ):

            return False


        if not record.message:

            return False


        if (

            record.level

            not in

            SUPPORTED_LEVELS

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
    # Validate JSON
    # -------------------------------------------------------------------------

    def validate_json(
        self,
        payload: str,
    ) -> bool:
        """
        Validate JSON syntax.
        """

        try:

            obj = json.loads(
                payload
            )

        except (

            json.JSONDecodeError,

            TypeError,

            ValueError,

        ):

            self._statistics[
                "errors"
            ] += 1

            return False


        return isinstance(

            obj,

            (

                dict,

                list,

            ),

        )


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


        if (

            self.level

            not in

            SUPPORTED_LEVELS

        ):

            return False


        if self.indent < 0:

            return False


        if not isinstance(
            self.pretty,
            bool,
        ):

            return False


        if not isinstance(
            self.sort_keys,
            bool,
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
        Validate internal runtime consistency.
        """

        #
        # Closed logger cannot remain enabled.
        #

        if (

            self.closed

            and

            self.enabled

        ):

            return False


        #
        # Counters must never
        # become negative.
        #

        if self.record_count < 0:

            return False


        if self.error_count < 0:

            return False


        if self.latency < 0:

            return False


        #
        # Statistics consistency.
        #

        if (

            self.statistics.get(

                "serialized",

                0,

            )

            >

            self.record_count

        ):

            return False


        #
        # Metadata must remain mutable.
        #

        if not isinstance(
            self.metadata,
            dict,
        ):

            return False


        return True
# =============================================================================
# Part 9. Events & Hooks
# =============================================================================

    # -------------------------------------------------------------------------
    # Before Encode
    # -------------------------------------------------------------------------

    def before_encode(
        self,
        obj: Any,
    ) -> None:
        """
        Emit event before JSON encoding.
        """

        self.emit_event(

            "before_encode",

            logger=self,

            object=obj,

        )


    # -------------------------------------------------------------------------
    # After Encode
    # -------------------------------------------------------------------------

    def after_encode(
        self,
        payload: str,
    ) -> None:
        """
        Emit event after JSON encoding.
        """

        self.emit_event(

            "after_encode",

            logger=self,

            payload=payload,

        )


    # -------------------------------------------------------------------------
    # Before Log
    # -------------------------------------------------------------------------

    def before_log(
        self,
        record: JSONLogRecord,
    ) -> None:
        """
        Emit event before logging.
        """

        self.emit_event(

            "before_log",

            logger=self,

            record=record,

        )


    # -------------------------------------------------------------------------
    # After Log
    # -------------------------------------------------------------------------

    def after_log(
        self,
        record: JSONLogRecord,
    ) -> None:
        """
        Emit event after logging.
        """

        self.emit_event(

            "after_log",

            logger=self,

            record=record,

        )


    # -------------------------------------------------------------------------
    # Add Hook
    # -------------------------------------------------------------------------

    def add_hook(
        self,
        event: str,
        callback: Hook,
    ) -> "JSONLogger":
        """
        Register a callback for an event.
        """

        if not callable(
            callback,
        ):

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
        Remove a callback.
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
        Dispatch an event to subscribers.
        """

        callbacks = self._hooks.get(

            event,

            [],

        )

        for callback in tuple(
            callbacks
        ):

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
    ) -> "JSONLogger":
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
        Return number of generated records.
        """

        return self.record_count


    # -------------------------------------------------------------------------
    # __iter__
    # -------------------------------------------------------------------------

    def __iter__(
        self,
    ):
        """
        Iterate over metadata.

        Example
        -------
        for key, value in logger:
            ...
        """

        return iter(
            self.metadata.items()
        )


    # -------------------------------------------------------------------------
    # __contains__
    # -------------------------------------------------------------------------

    def __contains__(
        self,
        key: str,
    ) -> bool:
        """
        Membership test for metadata keys.

        Example
        -------
        if "hostname" in logger:
            ...
        """

        return key in self.metadata


    # -------------------------------------------------------------------------
    # __call__
    # -------------------------------------------------------------------------

    def __call__(
        self,
        message: str,
        level: Optional[str] = None,
        **extra: Any,
    ) -> JSONLogRecord:
        """
        Callable logger.

        Equivalent to log().
        """

        return self.log(

            message=message,

            level=level,

            **extra,

        )


    # -------------------------------------------------------------------------
    # __copy__
    # -------------------------------------------------------------------------

    def __copy__(
        self,
    ) -> "JSONLogger":
        """
        Create a shallow runtime copy.
        """

        copied = self.__class__(

            name=self.name,

            level=self.level,

            pretty=self.pretty,

            indent=self.indent,

            sort_keys=self.sort_keys,

            enabled=self.enabled,

            metadata=self.metadata.copy(),

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
    ) -> "JSONLogger":
        """
        Create a fully independent clone.
        """

        if id(self) in memo:

            return memo[id(self)]

        cloned = self.clone()

        memo[id(self)] = cloned

        return cloned                                                                        
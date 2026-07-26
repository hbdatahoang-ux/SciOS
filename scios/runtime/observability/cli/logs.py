"""
SciOS-NG Runtime Observability

CLI : Logs

logs.py

Part 1
Foundation

Provides

    • imports
    • constants
    • type aliases
    • utilities

The LogsCLI is a lightweight frontend for the runtime
logging subsystem. It performs no logging itself and
delegates storage and retrieval to the configured backend.
"""

from __future__ import annotations

import csv
import json
import logging
import time
import uuid

from pathlib import Path

from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Sequence,
)

# ==========================================================
# Optional Runtime Backend
# ==========================================================

try:

    from scios.runtime.observability.logging import (
        LoggingRuntime,
    )

except Exception:

    LoggingRuntime = Any


# ==========================================================
# Package Metadata
# ==========================================================

__all__ = [

    "LogsCLI",

    "LOG_LEVELS",

    "LOG_OUTPUT_FORMATS",

]

__version__ = "0.1.0"

__author__ = "SciOS-NG"

__description__ = (
    "Observability Logging Command Line Interface"
)

# ==========================================================
# Constants
# ==========================================================

LOG_LEVELS = (

    "TRACE",

    "DEBUG",

    "INFO",

    "WARNING",

    "ERROR",

    "CRITICAL",

)

LOG_OUTPUT_FORMATS = (

    "table",

    "json",

    "csv",

    "text",

    "yaml",

)

DEFAULT_EXPORT_FORMAT = "json"

DEFAULT_LIMIT = 100

DEFAULT_TIMEOUT = 30.0

LOG_ID_LENGTH = 8

DEFAULT_LOG_LEVEL = "INFO"

# ==========================================================
# Type Aliases
# ==========================================================

LogRecord = Dict[str, Any]

LogList = List[LogRecord]

LogFilter = Callable[[LogRecord], bool]

# ==========================================================
# Foundation Utilities
# ==========================================================


def generate_log_id() -> str:
    """
    Generate a short log identifier.
    """

    return uuid.uuid4().hex[:LOG_ID_LENGTH]


def timestamp() -> float:
    """
    Current UNIX timestamp.
    """

    return time.time()


def now_iso() -> str:
    """
    Current UTC ISO-8601 timestamp.
    """

    return time.strftime(

        "%Y-%m-%dT%H:%M:%SZ",

        time.gmtime(),

    )


def ensure_path(
    path: str | Path,
) -> Path:
    """
    Normalize filesystem path.
    """

    return Path(path).expanduser().resolve()


def pretty_json(
    obj: Any,
) -> str:
    """
    Pretty JSON serializer.
    """

    return json.dumps(

        obj,

        indent=4,

        ensure_ascii=False,

        default=str,

    )


def normalize_level(
    level: str | int,
) -> str:
    """
    Normalize logging level.

    Examples
    --------
    INFO -> INFO

    20 -> INFO

    logging.INFO -> INFO
    """

    if isinstance(level, str):

        return level.upper()

    return logging.getLevelName(level)


# ==========================================================
# Runtime Capability
# ==========================================================


def logging_available() -> bool:
    """
    Whether the runtime logging backend
    is available.
    """

    return LoggingRuntime is not Any


# ==========================================================
# Runtime Information
# ==========================================================


def runtime_info() -> dict:
    """
    Foundation runtime information.
    """

    return {

        "module":

            __name__,

        "version":

            __version__,

        "description":

            __description__,

        "logging_available":

            logging_available(),

        "default_level":

            DEFAULT_LOG_LEVEL,

        "default_export_format":

            DEFAULT_EXPORT_FORMAT,

        "supported_levels":

            list(LOG_LEVELS),

        "supported_formats":

            list(LOG_OUTPUT_FORMATS),

    }
# ==========================================================
# Part 2
# Constructor
#
# Provides:
#     • LogsCLI.__init__()
#     • Runtime identity
#     • Logging backend binding
#     • Configuration
#     • Runtime state
#     • Runtime statistics
#     • Metadata
# ==========================================================


class LogsCLI:
    """
    SciOS-NG Logging Command Line Interface.

    LogsCLI is a lightweight frontend for interacting with
    the runtime logging subsystem.

    This class delegates all log storage and retrieval to
    the configured LoggingRuntime backend.
    """

    # ------------------------------------------------------
    # Part 2.1 Constructor
    # ------------------------------------------------------

    def __init__(
        self,
        logger: Optional[LoggingRuntime] = None,
        *,
        name: str = "SciOS Logs CLI",
        version: str = __version__,
        description: str = __description__,
    ) -> None:
        """
        Initialize LogsCLI.
        """

        # ==================================================
        # Identity
        # ==================================================

        self.id: str = str(uuid.uuid4())

        self.name: str = name

        self.version: str = version

        self.description: str = description

        self.component: str = "logs-cli"

        # ==================================================
        # Runtime Backend
        # ==================================================

        self.logger: Optional[
            LoggingRuntime
        ] = logger

        # ==================================================
        # Configuration
        # ==================================================

        self.output_format: str = (
            DEFAULT_EXPORT_FORMAT
        )

        self.default_limit: int = (
            DEFAULT_LIMIT
        )

        self.default_level: str = (
            DEFAULT_LOG_LEVEL
        )

        self.timeout: float = (
            DEFAULT_TIMEOUT
        )

        self.verbose: bool = False

        self.color: bool = True

        self.auto_refresh: bool = False

        # ==================================================
        # Runtime State
        # ==================================================

        self.enabled: bool = True

        self.running: bool = False

        self.closed: bool = False

        self.last_error: Optional[str] = None

        # ==================================================
        # Runtime Statistics
        # ==================================================

        self.command_count: int = 0

        self.search_count: int = 0

        self.export_count: int = 0

        self.error_count: int = 0

        self.refresh_count: int = 0

        self.last_command: Optional[str] = None

        self.last_activity: float = (
            timestamp()
        )

        # ==================================================
        # Metadata
        # ==================================================

        now = timestamp()

        self.created_at: float = now

        self.updated_at: float = now

        self.revision: int = 0

    # ------------------------------------------------------
    # Part 2.2 Runtime Metadata
    # ------------------------------------------------------

    def touch(
        self,
    ) -> None:
        """
        Update runtime metadata.
        """

        self.updated_at = timestamp()

        self.last_activity = self.updated_at

        self.revision += 1

    # ------------------------------------------------------
    # Part 2.3 Backend Binding
    # ------------------------------------------------------

    def bind_logger(
        self,
        logger: LoggingRuntime,
    ) -> "LogsCLI":
        """
        Bind a logging backend.
        """

        self.logger = logger

        self.touch()

        return self

    def unbind_logger(
        self,
    ) -> "LogsCLI":
        """
        Remove the logging backend.
        """

        self.logger = None

        self.touch()

        return self

    def has_logger(
        self,
    ) -> bool:
        """
        Return whether a logging backend
        is configured.
        """

        return self.logger is not None

    # ------------------------------------------------------
    # Part 2.4 Identity
    # ------------------------------------------------------

    @property
    def identity(
        self,
    ) -> dict:
        """
        Runtime identity.
        """

        return {

            "id":

                self.id,

            "name":

                self.name,

            "component":

                self.component,

            "version":

                self.version,

            "description":

                self.description,

        }

    # ------------------------------------------------------
    # Part 2.5 Metadata
    # ------------------------------------------------------

    def metadata(
        self,
    ) -> dict:
        """
        Runtime metadata.
        """

        return {

            "created_at":

                self.created_at,

            "updated_at":

                self.updated_at,

            "last_activity":

                self.last_activity,

            "revision":

                self.revision,

        }

    # ------------------------------------------------------
    # Part 2.6 Runtime Information
    # ------------------------------------------------------

    def info(
        self,
    ) -> dict:
        """
        Return runtime information.
        """

        return {

            "identity":

                self.identity,

            "metadata":

                self.metadata(),

            "enabled":

                self.enabled,

            "running":

                self.running,

            "closed":

                self.closed,

            "logging_available":

                self.has_logger(),

            "default_level":

                self.default_level,

            "output_format":

                self.output_format,

            "default_limit":

                self.default_limit,

            "timeout":

                self.timeout,

        }
# ==========================================================
# Part 3
# Log Operations
#
# Provides:
#     • list()
#     • get()
#     • latest()
#     • first()
#     • clear()
#     • count()
#     • exists()
#
# Notes
# -----
# LogsCLI never stores log records itself.
# All operations are delegated to LoggingRuntime.
# ==========================================================

    # ------------------------------------------------------
    # Part 3.1 Internal Helpers
    # ------------------------------------------------------

    def _record_command(
        self,
        command: str,
    ) -> None:
        """
        Record CLI activity.
        """

        self.command_count += 1

        self.last_command = command

        self.touch()

    def _require_logger(
        self,
    ) -> LoggingRuntime:
        """
        Ensure a logging backend exists.
        """

        if self.logger is None:

            raise RuntimeError(

                "Logging runtime is not available."

            )

        return self.logger

    def _log_collection(
        self,
    ) -> LogList:
        """
        Return normalized log records.
        """

        backend = self._require_logger()

        #
        # Preferred API
        #

        if hasattr(

            backend,

            "list",

        ):

            logs = backend.list()

        #
        # Registry API
        #

        elif hasattr(

            backend,

            "logs",

        ):

            logs = backend.logs

        #
        # Fallback
        #

        else:

            logs = []

        normalized: LogList = []

        for record in logs:

            if isinstance(

                record,

                dict,

            ):

                normalized.append(record)

            elif hasattr(

                record,

                "to_dict",

            ):

                normalized.append(

                    record.to_dict()

                )

            elif hasattr(

                record,

                "__dict__",

            ):

                normalized.append(

                    dict(

                        record.__dict__

                    )

                )

            else:

                normalized.append(

                    {

                        "value": record

                    }

                )

        return normalized

    # ------------------------------------------------------
    # Part 3.2 List
    # ------------------------------------------------------

    def list(
        self,
        *,
        limit: int | None = None,
    ) -> LogList:
        """
        List log records.
        """

        self._record_command(

            "list"

        )

        logs = self._log_collection()

        if limit is None:

            return logs

        return logs[:limit]

    # ------------------------------------------------------
    # Part 3.3 Lookup
    # ------------------------------------------------------

    def get(
        self,
        log_id: str,
    ) -> LogRecord | None:
        """
        Get log by identifier.
        """

        self._record_command(

            "get"

        )

        backend = self._require_logger()

        if hasattr(

            backend,

            "get",

        ):

            record = backend.get(

                log_id

            )

            if record is None:

                return None

            if isinstance(

                record,

                dict,

            ):

                return record

            if hasattr(

                record,

                "to_dict",

            ):

                return record.to_dict()

            if hasattr(

                record,

                "__dict__",

            ):

                return dict(

                    record.__dict__

                )

            return {

                "value": record

            }

        #
        # Fallback search
        #

        for record in self._log_collection():

            if record.get(

                "id"

            ) == log_id:

                return record

        return None

    # ------------------------------------------------------
    # Part 3.4 Navigation
    # ------------------------------------------------------

    def latest(
        self,
    ) -> LogRecord | None:
        """
        Return newest log record.
        """

        logs = self._log_collection()

        if not logs:

            return None

        return logs[-1]

    def first(
        self,
    ) -> LogRecord | None:
        """
        Return oldest log record.
        """

        logs = self._log_collection()

        if not logs:

            return None

        return logs[0]

    # ------------------------------------------------------
    # Part 3.5 Statistics
    # ------------------------------------------------------

    def count(
        self,
    ) -> int:
        """
        Number of log records.
        """

        return len(

            self._log_collection()

        )

    def exists(
        self,
        log_id: str,
    ) -> bool:
        """
        Whether a log exists.
        """

        return (

            self.get(

                log_id

            )

            is not None

        )

    # ------------------------------------------------------
    # Part 3.6 Runtime Operations
    # ------------------------------------------------------

    def clear(
        self,
    ):
        """
        Remove every log record.
        """

        self._record_command(

            "clear"

        )

        backend = self._require_logger()

        #
        # Preferred backend API
        #

        if hasattr(

            backend,

            "clear",

        ):

            return backend.clear()

        #
        # Registry fallback
        #

        if hasattr(

            backend,

            "logs",

        ):

            backend.logs.clear()

            return True

        raise NotImplementedError(

            "Logging backend does not support clear()."

        )
# ==========================================================
# Part 4
# Search & Filter
#
# Provides:
#     • search()
#     • filter()
#     • filter_by_level()
#     • filter_by_logger()
#     • filter_by_module()
#     • filter_by_tag()
#     • filter_by_time()
#     • query()
#
# Notes
# -----
# All searching is backend-independent.
# Log records are normalized into dictionaries before
# filtering.
# ==========================================================

    # ------------------------------------------------------
    # Part 4.1 Internal Helpers
    # ------------------------------------------------------

    def _normalize_log(
        self,
        record: LogRecord | Any,
    ) -> LogRecord:
        """
        Normalize a log record.
        """

        if isinstance(record, dict):
            return record

        if hasattr(record, "to_dict"):
            return record.to_dict()

        if hasattr(record, "__dict__"):
            return dict(record.__dict__)

        return {
            "value": record,
        }

    def _contains_text(
        self,
        record: LogRecord,
        keyword: str,
    ) -> bool:
        """
        Case-insensitive text search.
        """

        keyword = keyword.casefold()

        return keyword in json.dumps(
            record,
            ensure_ascii=False,
            default=str,
        ).casefold()

    # ------------------------------------------------------
    # Part 4.2 Search
    # ------------------------------------------------------

    def search(
        self,
        keyword: str,
    ) -> LogList:
        """
        Full-text search.
        """

        self.search_count += 1

        self._record_command(
            "search"
        )

        results: LogList = []

        for record in self._log_collection():

            log = self._normalize_log(record)

            if self._contains_text(
                log,
                keyword,
            ):
                results.append(log)

        return results

    # ------------------------------------------------------
    # Part 4.3 Generic Filter
    # ------------------------------------------------------

    def filter(
        self,
        predicate: LogFilter,
    ) -> LogList:
        """
        Generic predicate filter.
        """

        self._record_command(
            "filter"
        )

        results: LogList = []

        for record in self._log_collection():

            log = self._normalize_log(record)

            try:

                if predicate(log):
                    results.append(log)

            except Exception:

                continue

        return results

    # ------------------------------------------------------
    # Part 4.4 Built-in Filters
    # ------------------------------------------------------

    def filter_by_level(
        self,
        level: str,
    ) -> LogList:
        """
        Filter by log level.
        """

        level = normalize_level(level)

        return self.filter(

            lambda r:

            normalize_level(

                r.get(
                    "level",
                    "",
                )

            ) == level

        )

    def filter_by_logger(
        self,
        logger: str,
    ) -> LogList:
        """
        Filter by logger name.
        """

        return self.filter(

            lambda r:

            r.get("logger") == logger

        )

    def filter_by_module(
        self,
        module: str,
    ) -> LogList:
        """
        Filter by module.
        """

        return self.filter(

            lambda r:

            r.get("module") == module

        )

    def filter_by_tag(
        self,
        tag: str,
    ) -> LogList:
        """
        Filter by tag.
        """

        return self.filter(

            lambda r:

            tag in r.get(

                "tags",

                [],

            )

        )

    def filter_by_time(
        self,
        start: float | None = None,
        end: float | None = None,
    ) -> LogList:
        """
        Filter by timestamp.

        Parameters
        ----------
        start
            Inclusive start timestamp.

        end
            Inclusive end timestamp.
        """

        def predicate(
            record: LogRecord,
        ) -> bool:

            ts = record.get(
                "timestamp"
            )

            if ts is None:
                return False

            if (

                start is not None

                and

                ts < start

            ):
                return False

            if (

                end is not None

                and

                ts > end

            ):
                return False

            return True

        return self.filter(
            predicate
        )

    # ------------------------------------------------------
    # Part 4.5 Multi-field Query
    # ------------------------------------------------------

    def query(
        self,
        **criteria,
    ) -> LogList:
        """
        Exact multi-field query.

        Example
        -------

        query(
            level="ERROR",
            module="runtime"
        )
        """

        self._record_command(
            "query"
        )

        results: LogList = []

        for record in self._log_collection():

            log = self._normalize_log(
                record
            )

            matched = True

            for key, expected in criteria.items():

                if log.get(key) != expected:

                    matched = False

                    break

            if matched:

                results.append(
                    log
                )

        return results
# ==========================================================
# Part 5
# Export
#
# Provides:
#     • export()
#     • export_json()
#     • export_csv()
#     • export_text()
#     • dumps()
#
# Notes
# -----
# Export operations are backend-independent.
# Every log record is normalized before serialization.
# ==========================================================

    # ------------------------------------------------------
    # Part 5.1 Internal Helpers
    # ------------------------------------------------------

    def _export_records(
        self,
    ) -> LogList:
        """
        Return normalized log records.
        """

        return [

            self._normalize_log(record)

            for record in self._log_collection()

        ]

    # ------------------------------------------------------
    # Part 5.2 JSON Export
    # ------------------------------------------------------

    def export_json(
        self,
        path: str | Path,
        *,
        indent: int = 4,
    ) -> Path:
        """
        Export logs to a JSON file.
        """

        path = ensure_path(path)

        records = self._export_records()

        with path.open(
            "w",
            encoding="utf-8",
        ) as fp:

            json.dump(

                records,

                fp,

                indent=indent,

                ensure_ascii=False,

                default=str,

            )

        self.export_count += 1

        self._record_command(
            "export_json"
        )

        return path

    # ------------------------------------------------------
    # Part 5.3 CSV Export
    # ------------------------------------------------------

    def export_csv(
        self,
        path: str | Path,
    ) -> Path:
        """
        Export logs to CSV.
        """

        path = ensure_path(path)

        records = self._export_records()

        if not records:

            with path.open(
                "w",
                newline="",
                encoding="utf-8",
            ):
                pass

            self.export_count += 1

            self._record_command(
                "export_csv"
            )

            return path

        fieldnames = sorted(

            {

                key

                for record in records

                for key in record.keys()

            }

        )

        with path.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as fp:

            writer = csv.DictWriter(

                fp,

                fieldnames=fieldnames,

                extrasaction="ignore",

            )

            writer.writeheader()

            for record in records:

                writer.writerow(record)

        self.export_count += 1

        self._record_command(
            "export_csv"
        )

        return path

    # ------------------------------------------------------
    # Part 5.4 Text Export
    # ------------------------------------------------------

    def export_text(
        self,
        path: str | Path,
    ) -> Path:
        """
        Export logs as formatted text.
        """

        path = ensure_path(path)

        with path.open(
            "w",
            encoding="utf-8",
        ) as fp:

            for record in self._export_records():

                timestamp = record.get(
                    "timestamp",
                    "-"
                )

                level = record.get(
                    "level",
                    "-"
                )

                logger = record.get(
                    "logger",
                    "-"
                )

                module = record.get(
                    "module",
                    "-"
                )

                message = record.get(
                    "message",
                    ""
                )

                fp.write(

                    f"[{timestamp}] "

                    f"[{level}] "

                    f"[{logger}] "

                    f"[{module}] "

                    f"{message}"

                )

                fp.write("\n")

        self.export_count += 1

        self._record_command(
            "export_text"
        )

        return path

    # ------------------------------------------------------
    # Part 5.5 Generic Export
    # ------------------------------------------------------

    def export(
        self,
        path: str | Path,
        *,
        format: str = DEFAULT_EXPORT_FORMAT,
    ) -> Path:
        """
        Generic export entry.

        Supported formats

            • json
            • csv
            • text
            • txt
        """

        format = format.lower()

        exporters = {

            "json":

                self.export_json,

            "csv":

                self.export_csv,

            "text":

                self.export_text,

            "txt":

                self.export_text,

        }

        exporter = exporters.get(
            format
        )

        if exporter is None:

            raise ValueError(

                f"Unsupported export format: {format}"

            )

        return exporter(path)

    # ------------------------------------------------------
    # Part 5.6 Dumps
    # ------------------------------------------------------

    def dumps(
        self,
        *,
        indent: int = 4,
    ) -> str:
        """
        Serialize logs into a JSON string.
        """

        self._record_command(
            "dumps"
        )

        return json.dumps(

            self._export_records(),

            indent=indent,

            ensure_ascii=False,

            default=str,

        )
# ==========================================================
# Part 6
# Runtime Helpers
#
# Provides:
#     • enable()
#     • disable()
#     • reset()
#     • diagnostics()
#     • runtime_snapshot()
#     • metadata()
#
# Notes
# -----
# These helpers manage only the LogsCLI runtime state.
# They do not modify the LoggingRuntime backend unless
# explicitly requested.
# ==========================================================

    # ------------------------------------------------------
    # Part 6.1 Runtime State
    # ------------------------------------------------------

    def enable(
        self,
    ) -> "LogsCLI":
        """
        Enable the CLI runtime.
        """

        self.enabled = True

        self.touch()

        return self

    def disable(
        self,
    ) -> "LogsCLI":
        """
        Disable the CLI runtime.
        """

        self.enabled = False

        self.touch()

        return self

    # ------------------------------------------------------
    # Part 6.2 Runtime Reset
    # ------------------------------------------------------

    def reset(
        self,
        *,
        clear_backend: bool = False,
    ) -> "LogsCLI":
        """
        Reset runtime statistics.

        Parameters
        ----------
        clear_backend
            Also clear the logging backend.
        """

        self.command_count = 0

        self.search_count = 0

        self.export_count = 0

        self.refresh_count = 0

        self.error_count = 0

        self.last_command = None

        self.last_error = None

        self.last_activity = timestamp()

        if (

            clear_backend

            and

            self.has_logger()

        ):

            try:

                self.clear()

            except Exception:

                pass

        self.touch()

        return self

    # ------------------------------------------------------
    # Part 6.3 Runtime Snapshot
    # ------------------------------------------------------

    def runtime_snapshot(
        self,
    ) -> dict:
        """
        Return a snapshot of the CLI runtime.
        """

        return {

            "identity":

                self.identity,

            "metadata":

                self.metadata(),

            "runtime": {

                "enabled":

                    self.enabled,

                "running":

                    self.running,

                "closed":

                    self.closed,

                "logging_available":

                    self.has_logger(),

            },

            "statistics": {

                "logs":

                    self.count(),

                "commands":

                    self.command_count,

                "searches":

                    self.search_count,

                "exports":

                    self.export_count,

                "refreshes":

                    self.refresh_count,

                "errors":

                    self.error_count,

            },

        }

    # ------------------------------------------------------
    # Part 6.4 Diagnostics
    # ------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict:
        """
        Return runtime diagnostics.
        """

        backend = None

        if self.logger is not None:

            backend = type(

                self.logger

            ).__name__

        return {

            "snapshot":

                self.runtime_snapshot(),

            "configuration": {

                "default_level":

                    self.default_level,

                "output_format":

                    self.output_format,

                "default_limit":

                    self.default_limit,

                "timeout":

                    self.timeout,

                "verbose":

                    self.verbose,

                "color":

                    self.color,

                "auto_refresh":

                    self.auto_refresh,

            },

            "backend": {

                "available":

                    self.has_logger(),

                "type":

                    backend,

            },

        }

    # ------------------------------------------------------
    # Part 6.5 Metadata
    # ------------------------------------------------------

    def metadata(
        self,
    ) -> dict:
        """
        Return runtime metadata.
        """

        return {

            "id":

                self.id,

            "name":

                self.name,

            "component":

                self.component,

            "version":

                self.version,

            "created_at":

                self.created_at,

            "updated_at":

                self.updated_at,

            "last_activity":

                self.last_activity,

            "revision":

                self.revision,

        }
# ==========================================================
# Part 7
# Python Protocols
#
# Provides:
#     • __repr__()
#     • __str__()
#     • __len__()
#     • __iter__()
#     • __contains__()
#     • __getitem__()
#     • __call__()
#     • __copy__()
#     • __deepcopy__()
#
# Notes
# -----
# LogsCLI behaves as:
#
#   • printable object
#   • iterable container
#   • mapping
#   • callable runtime
#   • copyable object
# ==========================================================

import copy as _copy

    # ------------------------------------------------------
    # Part 7.1 Representation
    # ------------------------------------------------------

    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """

        return (

            f"{self.__class__.__name__}("

            f"id='{self.id}', "

            f"name='{self.name}', "

            f"logs={self.count()}, "

            f"enabled={self.enabled}"

            ")"

        )

    def __str__(
        self,
    ) -> str:
        """
        Human-readable representation.
        """

        return (

            f"{self.name} "

            f"({self.count()} logs)"

        )

    # ------------------------------------------------------
    # Part 7.2 Container Protocols
    # ------------------------------------------------------

    def __len__(
        self,
    ) -> int:
        """
        Return the number of log records.
        """

        return self.count()

    def __iter__(
        self,
    ):
        """
        Iterate over log records.
        """

        return iter(

            self.list()

        )

    def __contains__(
        self,
        log_id: str,
    ) -> bool:
        """
        Membership test.

        Example
        -------
            if "log-001" in cli:
                ...
        """

        return self.exists(
            log_id
        )

    # ------------------------------------------------------
    # Part 7.3 Mapping Protocol
    # ------------------------------------------------------

    def __getitem__(
        self,
        key,
    ):
        """
        Mapping-style access.

        Supported keys
        --------------

            cli["status"]

            cli["metadata"]

            cli["runtime"]

            cli["diagnostics"]

            cli["identity"]

            cli["log-id"]
        """

        if not isinstance(
            key,
            str,
        ):
            raise KeyError(key)

        mapping = {

            "status": {

                "enabled":

                    self.enabled,

                "running":

                    self.running,

                "closed":

                    self.closed,

            },

            "metadata":

                self.metadata(),

            "runtime":

                self.runtime_snapshot(),

            "diagnostics":

                self.diagnostics(),

            "identity":

                self.identity,

        }

        if key in mapping:

            return mapping[key]

        record = self.get(key)

        if record is not None:

            return record

        raise KeyError(key)

    # ------------------------------------------------------
    # Part 7.4 Callable Runtime
    # ------------------------------------------------------

    def __call__(
        self,
        command: str | None = None,
        *args,
        **kwargs,
    ):
        """
        Callable interface.

        Examples
        --------

            cli()

            cli("list")

            cli("latest")

            cli("search", "ERROR")

            cli("query", level="ERROR")
        """

        if command is None:

            return self.runtime_snapshot()

        dispatch = {

            "list":

                self.list,

            "latest":

                self.latest,

            "first":

                self.first,

            "count":

                self.count,

            "search":

                self.search,

            "query":

                self.query,

            "diagnostics":

                self.diagnostics,

            "runtime":

                self.runtime_snapshot,

            "enable":

                self.enable,

            "disable":

                self.disable,

            "reset":

                self.reset,

        }

        handler = dispatch.get(
            command
        )

        if handler is None:

            raise ValueError(

                f"Unknown command: {command}"

            )

        return handler(

            *args,

            **kwargs,

        )

    # ------------------------------------------------------
    # Part 7.5 Copy Protocols
    # ------------------------------------------------------

    def __copy__(
        self,
    ):
        """
        Create a shallow copy.

        The LoggingRuntime backend
        reference is intentionally shared.
        """

        cls = self.__class__

        new = cls.__new__(cls)

        new.__dict__.update(

            self.__dict__

        )

        return new

    def __deepcopy__(
        self,
        memo,
    ):
        """
        Create a deep copy.

        The logging backend is intentionally
        not deep-copied because it usually
        manages shared runtime resources.
        """

        cls = self.__class__

        new = cls.__new__(cls)

        memo[id(self)] = new

        for key, value in self.__dict__.items():

            if key == "logger":

                #
                # Share backend instance.
                #

                setattr(

                    new,

                    key,

                    value,

                )

            else:

                setattr(

                    new,

                    key,

                    _copy.deepcopy(

                        value,

                        memo,

                    ),

                )

        return new                                            
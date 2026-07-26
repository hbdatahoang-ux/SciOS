"""
SciOS-NG Observability CLI

trace.py

Part 1
Foundation

Provides:
    • Imports
    • Package metadata
    • Constants
    • Type aliases
    • Foundation utilities
    • Optional tracing backend imports

Architecture:

        CLI
         │
         ▼
     TraceCLI
         │
         ▼
   Runtime Tracing Backend
"""


from __future__ import annotations

import json
import time
import uuid

from pathlib import Path

from typing import (
    Any,
    Dict,
    List,
    Optional,
    Iterable,
    Iterator,
    Sequence,
    Callable,
)

# ==========================================================
# Optional Runtime Imports
# ==========================================================

try:

    from scios.runtime.observability.tracing import (
        Tracer,
    )

except Exception:

    Tracer = Any


# ==========================================================
# Package Metadata
# ==========================================================

__all__ = [

    "TraceCLI",

    "TRACE_OUTPUT_FORMATS",

    "DEFAULT_EXPORT_FORMAT",

]

__version__ = "0.1.0"

__author__ = "SciOS-NG"

__description__ = (
    "Observability Trace Command Line Interface"
)

# ==========================================================
# Constants
# ==========================================================

TRACE_OUTPUT_FORMATS = (

    "table",

    "json",

    "yaml",

    "text",

)

DEFAULT_EXPORT_FORMAT = "json"

DEFAULT_LIMIT = 100

DEFAULT_TIMEOUT = 30.0

TRACE_ID_LENGTH = 8

# ==========================================================
# Type Aliases
# ==========================================================

TraceRecord = Dict[str, Any]

TraceList = List[TraceRecord]

TraceFilter = Callable[[TraceRecord], bool]

# ==========================================================
# Foundation Utilities
# ==========================================================


def generate_trace_id() -> str:
    """
    Generate a short trace identifier.
    """

    return uuid.uuid4().hex[:TRACE_ID_LENGTH]


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
    Pretty JSON serialization.
    """

    return json.dumps(

        obj,

        indent=4,

        ensure_ascii=False,

        default=str,

    )


# ==========================================================
# Runtime Capability Detection
# ==========================================================


def tracer_available() -> bool:
    """
    Return whether tracing backend
    is available.
    """

    return Tracer is not Any


# ==========================================================
# Base Runtime Diagnostics
# ==========================================================


def runtime_info() -> dict:
    """
    Runtime information.
    """

    return {

        "module": __name__,

        "version": __version__,

        "description": __description__,

        "tracer_available": tracer_available(),

        "default_format": DEFAULT_EXPORT_FORMAT,

        "supported_formats": list(

            TRACE_OUTPUT_FORMATS

        ),

    }
# ==========================================================
# Part 2
# Constructor
#
# Provides:
#     • TraceCLI initialization
#     • Runtime identity
#     • Tracer binding
#     • Configuration
#     • Runtime state
#     • Statistics
#     • Metadata
# ==========================================================


class TraceCLI:
    """
    SciOS-NG Trace Command Line Interface.

    A lightweight command interface for interacting with
    the runtime tracing subsystem.
    """

    # ------------------------------------------------------
    # Part 2.1 Constructor
    # ------------------------------------------------------

    def __init__(
        self,
        tracer: Optional[Tracer] = None,
        *,
        name: str = "SciOS Trace CLI",
        version: str = __version__,
        description: str = __description__,
    ) -> None:
        """
        Initialize TraceCLI.
        """

        # ==================================================
        # Identity
        # ==================================================

        self.id: str = str(
            uuid.uuid4()
        )

        self.name: str = name

        self.version: str = version

        self.description: str = description

        self.component: str = "trace-cli"

        # ==================================================
        # Runtime Binding
        # ==================================================

        self.tracer: Optional[Tracer] = tracer

        # ==================================================
        # Configuration
        # ==================================================

        self.output_format: str = (
            DEFAULT_EXPORT_FORMAT
        )

        self.default_limit: int = (
            DEFAULT_LIMIT
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
        # Statistics
        # ==================================================

        self.command_count: int = 0

        self.export_count: int = 0

        self.search_count: int = 0

        self.error_count: int = 0

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
    # Part 2.2 Metadata Helpers
    # ------------------------------------------------------

    def touch(
        self,
    ) -> None:
        """
        Update runtime metadata.
        """

        self.updated_at = timestamp()

        self.last_activity = (
            self.updated_at
        )

        self.revision += 1

    # ------------------------------------------------------
    # Part 2.3 Tracer Binding
    # ------------------------------------------------------

    def bind_tracer(
        self,
        tracer: Tracer,
    ) -> "TraceCLI":
        """
        Bind runtime tracer.
        """

        self.tracer = tracer

        self.touch()

        return self

    def unbind_tracer(
        self,
    ) -> "TraceCLI":
        """
        Remove tracer binding.
        """

        self.tracer = None

        self.touch()

        return self

    def has_tracer(
        self,
    ) -> bool:
        """
        Whether a tracer backend is available.
        """

        return self.tracer is not None

    # ------------------------------------------------------
    # Part 2.4 Identity
    # ------------------------------------------------------

    @property
    def identity(
        self,
    ) -> dict:
        """
        Component identity.
        """

        return {

            "id": self.id,

            "name": self.name,

            "version": self.version,

            "component": self.component,

            "description": self.description,

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

            "created_at": self.created_at,

            "updated_at": self.updated_at,

            "last_activity": self.last_activity,

            "revision": self.revision,

        }

    # ------------------------------------------------------
    # Part 2.6 Runtime Info
    # ------------------------------------------------------

    def info(
        self,
    ) -> dict:
        """
        Return CLI information.
        """

        return {

            "identity": self.identity,

            "metadata": self.metadata(),

            "enabled": self.enabled,

            "running": self.running,

            "closed": self.closed,

            "has_tracer": self.has_tracer(),

            "output_format": self.output_format,

            "default_limit": self.default_limit,

        }
# ==========================================================
# Part 3
# Trace Operations
#
# Provides:
#     • list()
#     • get()
#     • latest()
#     • first()
#     • clear()
#     • count()
#     • exists()
#     • refresh()
#     • trace_ids()
#     • traces()
# ==========================================================

    # ------------------------------------------------------
    # Internal Helpers
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

    def _require_tracer(
        self,
    ):
        """
        Ensure tracer backend exists.
        """

        if self.tracer is None:

            raise RuntimeError(
                "Tracer backend is not available."
            )

        return self.tracer

    def _trace_collection(
        self,
    ) -> list:
        """
        Return all trace records.
        """

        tracer = self._require_tracer()

        if hasattr(tracer, "list"):

            result = tracer.list()

        elif hasattr(tracer, "traces"):

            result = tracer.traces

        else:

            result = []

        return list(result)

    # ------------------------------------------------------
    # List Operations
    # ------------------------------------------------------

    def list(
        self,
        *,
        limit: int | None = None,
    ) -> TraceList:
        """
        List trace records.
        """

        self._record_command(
            "list"
        )

        traces = self._trace_collection()

        if limit is None:

            return traces

        return traces[:limit]

    def traces(
        self,
    ) -> TraceList:
        """
        Alias of list().
        """

        return self.list()

    # ------------------------------------------------------
    # Lookup Operations
    # ------------------------------------------------------

    def get(
        self,
        trace_id: str,
    ) -> TraceRecord | None:
        """
        Get trace by identifier.
        """

        self._record_command(
            "get"
        )

        tracer = self._require_tracer()

        if hasattr(tracer, "get"):

            return tracer.get(trace_id)

        for trace in self._trace_collection():

            if trace.get("id") == trace_id:

                return trace

        return None

    def exists(
        self,
        trace_id: str,
    ) -> bool:
        """
        Check whether a trace exists.
        """

        return self.get(
            trace_id
        ) is not None

    # ------------------------------------------------------
    # Navigation
    # ------------------------------------------------------

    def first(
        self,
    ) -> TraceRecord | None:
        """
        Return first trace.
        """

        traces = self._trace_collection()

        if not traces:

            return None

        return traces[0]

    def latest(
        self,
    ) -> TraceRecord | None:
        """
        Return latest trace.
        """

        traces = self._trace_collection()

        if not traces:

            return None

        return traces[-1]

    # ------------------------------------------------------
    # Statistics
    # ------------------------------------------------------

    def count(
        self,
    ) -> int:
        """
        Number of traces.
        """

        return len(
            self._trace_collection()
        )

    def trace_ids(
        self,
    ) -> list[str]:
        """
        Return trace identifiers.
        """

        ids = []

        for trace in self._trace_collection():

            trace_id = trace.get("id")

            if trace_id is not None:

                ids.append(trace_id)

        return ids

    # ------------------------------------------------------
    # Runtime Operations
    # ------------------------------------------------------

    def refresh(
        self,
    ) -> "TraceCLI":
        """
        Refresh runtime state.
        """

        self._record_command(
            "refresh"
        )

        tracer = self._require_tracer()

        if hasattr(
            tracer,
            "refresh",
        ):

            tracer.refresh()

        return self

    def clear(
        self,
    ):
        """
        Remove all traces.
        """

        self._record_command(
            "clear"
        )

        tracer = self._require_tracer()

        if hasattr(
            tracer,
            "clear",
        ):

            return tracer.clear()

        if hasattr(
            tracer,
            "traces",
        ):

            tracer.traces.clear()

            return True

        raise NotImplementedError(
            "Tracer backend does not support clear()."
        )
# ==========================================================
# Part 4
# Search & Filter
#
# Provides:
#     • search()
#     • filter()
#     • filter_by_name()
#     • filter_by_operation()
#     • filter_by_status()
#     • filter_by_tag()
#     • filter_by_time()
#     • find()
#     • contains()
#     • query()
# ==========================================================

    # ------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------

    def _normalize_trace(
        self,
        trace: TraceRecord | Any,
    ) -> dict:
        """
        Normalize trace into dictionary.
        """

        if isinstance(
            trace,
            dict,
        ):
            return trace

        if hasattr(
            trace,
            "to_dict",
        ):
            return trace.to_dict()

        if hasattr(
            trace,
            "__dict__",
        ):
            return dict(
                trace.__dict__
            )

        return {
            "value": trace,
        }

    def _match_text(
        self,
        trace: dict,
        keyword: str,
    ) -> bool:
        """
        Case-insensitive text search.
        """

        keyword = keyword.lower()

        return keyword in str(
            trace
        ).lower()

    # ------------------------------------------------------
    # Generic Search
    # ------------------------------------------------------

    def search(
        self,
        keyword: str,
    ) -> TraceList:
        """
        Search traces using free text.
        """

        self.search_count += 1

        self._record_command(
            "search"
        )

        result: TraceList = []

        for trace in self._trace_collection():

            item = self._normalize_trace(
                trace
            )

            if self._match_text(
                item,
                keyword,
            ):

                result.append(item)

        return result

    def find(
        self,
        keyword: str,
    ) -> TraceRecord | None:
        """
        Return first matching trace.
        """

        matches = self.search(
            keyword
        )

        if matches:

            return matches[0]

        return None

    # ------------------------------------------------------
    # Predicate Filter
    # ------------------------------------------------------

    def filter(
        self,
        predicate: TraceFilter,
    ) -> TraceList:
        """
        Filter traces using predicate.
        """

        self._record_command(
            "filter"
        )

        result: TraceList = []

        for trace in self._trace_collection():

            item = self._normalize_trace(
                trace
            )

            try:

                if predicate(item):

                    result.append(item)

            except Exception:

                continue

        return result

    # ------------------------------------------------------
    # Built-in Filters
    # ------------------------------------------------------

    def filter_by_name(
        self,
        name: str,
    ) -> TraceList:
        """
        Filter by trace name.
        """

        return self.filter(

            lambda t:

            t.get(
                "name"
            ) == name

        )

    def filter_by_operation(
        self,
        operation: str,
    ) -> TraceList:
        """
        Filter by operation.
        """

        return self.filter(

            lambda t:

            t.get(
                "operation"
            ) == operation

        )

    def filter_by_status(
        self,
        status: str,
    ) -> TraceList:
        """
        Filter by status.
        """

        return self.filter(

            lambda t:

            t.get(
                "status"
            ) == status

        )

    def filter_by_tag(
        self,
        tag: str,
    ) -> TraceList:
        """
        Filter by tag.
        """

        return self.filter(

            lambda t:

            tag in t.get(
                "tags",
                [],
            )

        )

    def filter_by_time(
        self,
        *,
        start: float | None = None,
        end: float | None = None,
    ) -> TraceList:
        """
        Filter traces by timestamp.
        """

        def predicate(
            trace: dict,
        ) -> bool:

            ts = trace.get(
                "timestamp"
            )

            if ts is None:

                return False

            if start is not None:

                if ts < start:

                    return False

            if end is not None:

                if ts > end:

                    return False

            return True

        return self.filter(
            predicate
        )

    # ------------------------------------------------------
    # Query API
    # ------------------------------------------------------

    def query(
        self,
        **criteria,
    ) -> TraceList:
        """
        Multi-field query.

        Example:

            query(
                status="ok",
                name="forward"
            )
        """

        self._record_command(
            "query"
        )

        result = []

        for trace in self._trace_collection():

            item = self._normalize_trace(
                trace
            )

            matched = True

            for key, value in criteria.items():

                if item.get(
                    key
                ) != value:

                    matched = False

                    break

            if matched:

                result.append(
                    item
                )

        return result

    # ------------------------------------------------------
    # Convenience Helpers
    # ------------------------------------------------------

    def contains(
        self,
        keyword: str,
    ) -> bool:
        """
        Whether any trace contains keyword.
        """

        return (

            self.find(
                keyword
            )

            is not None

        )

    def search_statistics(
        self,
    ) -> dict:
        """
        Search runtime statistics.
        """

        return {

            "search_count":
                self.search_count,

            "trace_count":
                self.count(),

            "last_command":
                self.last_command,

        }
# ==========================================================
# Part 5
# Export
#
# Provides:
#     • export()
#     • export_json()
#     • export_text()
#     • export_csv()
#     • save()
#     • dumps()
#     • export_statistics()
# ==========================================================

import csv


    # ------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------

    def _export_records(
        self,
    ) -> TraceList:
        """
        Return normalized trace records.
        """

        records: TraceList = []

        for trace in self._trace_collection():

            records.append(

                self._normalize_trace(
                    trace
                )

            )

        return records


    # ------------------------------------------------------
    # JSON Export
    # ------------------------------------------------------

    def export_json(
        self,
        path: str | Path,
        *,
        indent: int = 4,
    ) -> Path:
        """
        Export traces as JSON.
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
    # Text Export
    # ------------------------------------------------------

    def export_text(
        self,
        path: str | Path,
    ) -> Path:
        """
        Export traces as plain text.
        """

        path = ensure_path(path)

        with path.open(
            "w",
            encoding="utf-8",
        ) as fp:

            for trace in self._export_records():

                fp.write(

                    pretty_json(trace)

                )

                fp.write("\n")

        self.export_count += 1

        self._record_command(
            "export_text"
        )

        return path


    # ------------------------------------------------------
    # CSV Export
    # ------------------------------------------------------

    def export_csv(
        self,
        path: str | Path,
    ) -> Path:
        """
        Export traces as CSV.
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

            return path

        fields = sorted(

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

                fieldnames=fields,

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
    # Generic Export
    # ------------------------------------------------------

    def export(
        self,
        path: str | Path,
        *,
        format: str = DEFAULT_EXPORT_FORMAT,
    ) -> Path:
        """
        Export traces.

        Supported:

            json

            csv

            text
        """

        format = format.lower()

        if format == "json":

            return self.export_json(
                path
            )

        if format == "csv":

            return self.export_csv(
                path
            )

        if format in (

            "text",

            "txt",

        ):

            return self.export_text(
                path
            )

        raise ValueError(

            f"Unsupported export format: {format}"

        )


    # ------------------------------------------------------
    # Save
    # ------------------------------------------------------

    def save(
        self,
        path: str | Path,
    ) -> Path:
        """
        Alias of export().
        """

        return self.export(
            path
        )


    # ------------------------------------------------------
    # Dumps
    # ------------------------------------------------------

    def dumps(
        self,
        *,
        indent: int = 4,
    ) -> str:
        """
        Return traces as JSON string.
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


    # ------------------------------------------------------
    # Export Statistics
    # ------------------------------------------------------

    def export_statistics(
        self,
    ) -> dict:
        """
        Export runtime statistics.
        """

        return {

            "exports":

                self.export_count,

            "records":

                self.count(),

            "last_command":

                self.last_command,

            "default_format":

                self.output_format,

            "supported_formats":

                list(

                    TRACE_OUTPUT_FORMATS

                ),

        }
# ==========================================================
# Part 6
# Runtime Helpers
#
# Provides:
#     • enable()
#     • disable()
#     • reset()
#     • refresh()
#     • clear_statistics()
#     • status()
#     • diagnostics()
#     • runtime_snapshot()
#     • metadata()
#     • touch()
# ==========================================================

    # ------------------------------------------------------
    # Internal Helper
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
    # Lifecycle Helpers
    # ------------------------------------------------------

    def enable(
        self,
    ) -> "TraceCLI":
        """
        Enable CLI runtime.
        """

        self.enabled = True

        self.touch()

        return self

    def disable(
        self,
    ) -> "TraceCLI":
        """
        Disable CLI runtime.
        """

        self.enabled = False

        self.touch()

        return self

    def reset(
        self,
        *,
        clear_backend: bool = False,
    ) -> "TraceCLI":
        """
        Reset runtime statistics.

        Optionally clears backend traces.
        """

        self.command_count = 0

        self.search_count = 0

        self.export_count = 0

        self.error_count = 0

        self.last_command = None

        self.last_error = None

        self.last_activity = timestamp()

        if clear_backend and self.has_tracer():

            try:

                self.clear()

            except Exception:

                pass

        self.touch()

        return self

    def refresh(
        self,
    ) -> "TraceCLI":
        """
        Refresh runtime state.
        """

        if self.has_tracer():

            tracer = self.tracer

            if hasattr(
                tracer,
                "refresh",
            ):

                tracer.refresh()

        self.touch()

        return self

    # ------------------------------------------------------
    # Statistics Helpers
    # ------------------------------------------------------

    def clear_statistics(
        self,
    ) -> "TraceCLI":
        """
        Clear runtime counters only.
        """

        self.command_count = 0

        self.search_count = 0

        self.export_count = 0

        self.error_count = 0

        self.touch()

        return self

    @property
    def uptime(
        self,
    ) -> float:
        """
        CLI uptime in seconds.
        """

        return max(

            0.0,

            timestamp() - self.created_at,

        )

    # ------------------------------------------------------
    # Runtime State
    # ------------------------------------------------------

    def status(
        self,
    ) -> dict:
        """
        Return runtime status.
        """

        return {

            "enabled": self.enabled,

            "running": self.running,

            "closed": self.closed,

            "has_tracer": self.has_tracer(),

            "uptime": self.uptime,

        }

    def runtime_snapshot(
        self,
    ) -> dict:
        """
        Return runtime snapshot.
        """

        return {

            "identity": self.identity,

            "metadata": self.metadata(),

            "status": self.status(),

            "statistics": {

                "commands": self.command_count,

                "searches": self.search_count,

                "exports": self.export_count,

                "errors": self.error_count,

                "trace_count": self.count(),

            },

        }

    def diagnostics(
        self,
    ) -> dict:
        """
        Return complete diagnostics.
        """

        return {

            "runtime": self.runtime_snapshot(),

            "backend": {

                "available": self.has_tracer(),

                "type": (

                    type(self.tracer).__name__

                    if self.tracer is not None

                    else None

                ),

            },

            "configuration": {

                "output_format": self.output_format,

                "default_limit": self.default_limit,

                "timeout": self.timeout,

                "verbose": self.verbose,

                "color": self.color,

                "auto_refresh": self.auto_refresh,

            },

        }

    # ------------------------------------------------------
    # Metadata
    # ------------------------------------------------------

    def metadata(
        self,
    ) -> dict:
        """
        Runtime metadata.
        """

        return {

            "id": self.id,

            "created_at": self.created_at,

            "updated_at": self.updated_at,

            "last_activity": self.last_activity,

            "revision": self.revision,

        }
# ==========================================================
# Part 7
# Python Protocols
#
# Provides:
#     • __repr__()
#     • __str__()
#     • __len__()
#     • __bool__()
#     • __iter__()
#     • __contains__()
#     • __getitem__()
#     • __call__()
#     • __copy__()
#     • __deepcopy__()
#
# TraceCLI behaves as:
#
#     Runtime Object
#         │
#         ├── Printable
#         ├── Iterable
#         ├── Container
#         ├── Mapping-like
#         ├── Callable
#         └── Cloneable
# ==========================================================

import copy as _copy


    # ------------------------------------------------------
    # __repr__
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

            f"enabled={self.enabled}, "

            f"traces={self.count()}"

            ")"

        )


    # ------------------------------------------------------
    # __str__
    # ------------------------------------------------------

    def __str__(
        self,
    ) -> str:
        """
        Human-readable representation.
        """

        return (

            f"{self.name} "

            f"({self.count()} traces)"

        )


    # ------------------------------------------------------
    # __len__
    # ------------------------------------------------------

    def __len__(
        self,
    ) -> int:
        """
        Number of traces.
        """

        return self.count()


    # ------------------------------------------------------
    # __bool__
    # ------------------------------------------------------

    def __bool__(
        self,
    ) -> bool:
        """
        Truth value of runtime.
        """

        return (

            self.enabled

            and

            not self.closed

        )


    # ------------------------------------------------------
    # __iter__
    # ------------------------------------------------------

    def __iter__(
        self,
    ):
        """
        Iterate over trace records.
        """

        return iter(

            self.list()

        )


    # ------------------------------------------------------
    # __contains__
    # ------------------------------------------------------

    def __contains__(
        self,
        trace_id: str,
    ) -> bool:
        """
        Membership test.

        Example:

            if "abc123" in cli:
                ...
        """

        return self.exists(

            trace_id

        )


    # ------------------------------------------------------
    # __getitem__
    # ------------------------------------------------------

    def __getitem__(
        self,
        key,
    ):
        """
        Mapping-style access.

        Supported:

            cli["status"]

            cli["runtime"]

            cli["diagnostics"]

            cli["metadata"]

            cli["trace_id"]
        """

        if isinstance(

            key,

            str,

        ):

            mapping = {

                "status":

                    self.status(),


                "runtime":

                    self.runtime_snapshot(),


                "diagnostics":

                    self.diagnostics(),


                "metadata":

                    self.metadata(),


                "identity":

                    self.identity,

            }

            if key in mapping:

                return mapping[key]

            #
            # treat as trace id
            #

            trace = self.get(key)

            if trace is not None:

                return trace

        raise KeyError(

            key

        )


    # ------------------------------------------------------
    # __call__
    # ------------------------------------------------------

    def __call__(
        self,
        command: str | None = None,
        *args,
        **kwargs,
    ):
        """
        Callable interface.

        Examples:

            cli()

            cli("list")

            cli("latest")

            cli("search","kernel")
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


            "status":

                self.status,


            "diagnostics":

                self.diagnostics,


            "refresh":

                self.refresh,

        }

        if command not in dispatch:

            raise ValueError(

                f"Unknown command: {command}"

            )

        return dispatch[command](

            *args,

            **kwargs,

        )


    # ------------------------------------------------------
    # __copy__
    # ------------------------------------------------------

    def __copy__(
        self,
    ):
        """
        Shallow copy.

        Shares tracer backend.
        """

        cls = self.__class__

        new = cls.__new__(

            cls

        )

        new.__dict__.update(

            self.__dict__

        )

        return new


    # ------------------------------------------------------
    # __deepcopy__
    # ------------------------------------------------------

    def __deepcopy__(
        self,
        memo,
    ):
        """
        Deep copy.

        Tracer backend reference
        is intentionally shared.
        """

        cls = self.__class__

        new = cls.__new__(

            cls

        )

        memo[id(self)] = new

        for key, value in self.__dict__.items():

            if key == "tracer":

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
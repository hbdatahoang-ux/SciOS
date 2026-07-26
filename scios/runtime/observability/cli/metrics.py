"""
SciOS-NG Observability CLI

metrics.py

Part 1
Foundation

Provides:
    • Imports
    • Package metadata
    • Constants
    • Type aliases
    • Foundation utilities
    • Optional metrics backend imports

Architecture

        CLI
         │
         ▼
     MetricsCLI
         │
         ▼
 Runtime Metrics Backend
"""

from __future__ import annotations

import csv
import json
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
# Optional Runtime Imports
# ==========================================================

try:

    from scios.runtime.observability.metrics import (
        MetricsRuntime,
    )

except Exception:

    MetricsRuntime = Any


# ==========================================================
# Package Metadata
# ==========================================================

__all__ = [

    "MetricsCLI",

    "METRIC_OUTPUT_FORMATS",

    "DEFAULT_EXPORT_FORMAT",

]

__version__ = "0.1.0"

__author__ = "SciOS-NG"

__description__ = (
    "Observability Metrics Command Line Interface"
)


# ==========================================================
# Constants
# ==========================================================

METRIC_OUTPUT_FORMATS = (

    "table",

    "json",

    "csv",

    "text",

    "yaml",

)

DEFAULT_EXPORT_FORMAT = "json"

DEFAULT_LIMIT = 100

DEFAULT_TIMEOUT = 30.0

METRIC_ID_LENGTH = 8


# ==========================================================
# Type Aliases
# ==========================================================

MetricRecord = Dict[str, Any]

MetricList = List[MetricRecord]

MetricFilter = Callable[[MetricRecord], bool]


# ==========================================================
# Foundation Utilities
# ==========================================================


def generate_metric_id() -> str:
    """
    Generate a short metric identifier.
    """

    return uuid.uuid4().hex[:METRIC_ID_LENGTH]


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

    return Path(

        path

    ).expanduser().resolve()


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


def metrics_available() -> bool:
    """
    Whether Metrics backend is available.
    """

    return MetricsRuntime is not Any


# ==========================================================
# Runtime Diagnostics
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

        "metrics_available":

            metrics_available(),

        "default_export_format":

            DEFAULT_EXPORT_FORMAT,

        "supported_formats":

            list(

                METRIC_OUTPUT_FORMATS

            ),

    }
# ==========================================================
# Part 2
# Constructor
#
# Provides:
#     • MetricsCLI.__init__()
#     • Runtime identity
#     • Metrics backend binding
#     • Configuration
#     • Runtime state
#     • Runtime statistics
#     • Metadata
# ==========================================================


class MetricsCLI:
    """
    SciOS-NG Metrics Command Line Interface.

    MetricsCLI provides a lightweight command interface
    for interacting with the runtime metrics subsystem.

    This class does NOT implement the metrics engine.
    It delegates all metric operations to the configured
    MetricsRuntime backend.
    """

    # ------------------------------------------------------
    # Part 2.1 Constructor
    # ------------------------------------------------------

    def __init__(
        self,
        metrics: Optional[MetricsRuntime] = None,
        *,
        name: str = "SciOS Metrics CLI",
        version: str = __version__,
        description: str = __description__,
    ) -> None:
        """
        Initialize MetricsCLI.
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

        self.component: str = "metrics-cli"

        # ==================================================
        # Runtime Binding
        # ==================================================

        self.metrics: Optional[
            MetricsRuntime
        ] = metrics

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
    # Part 2.3 Metrics Backend Binding
    # ------------------------------------------------------

    def bind_metrics(
        self,
        metrics: MetricsRuntime,
    ) -> "MetricsCLI":
        """
        Bind a metrics runtime backend.
        """

        self.metrics = metrics

        self.touch()

        return self

    def unbind_metrics(
        self,
    ) -> "MetricsCLI":
        """
        Remove the metrics backend.
        """

        self.metrics = None

        self.touch()

        return self

    def has_metrics(
        self,
    ) -> bool:
        """
        Return whether a metrics backend exists.
        """

        return self.metrics is not None

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
        Return CLI information.
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

            "metrics_available":

                self.has_metrics(),

            "output_format":

                self.output_format,

            "default_limit":

                self.default_limit,

            "timeout":

                self.timeout,

        }
# ==========================================================
# Part 3
# Metrics Operations
#
# Provides:
#     • list()
#     • get()
#     • latest()
#     • clear()
#     • count()
#     • exists()
#
# Notes:
#     MetricsCLI delegates all metric operations to the
#     configured MetricsRuntime backend.
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

    def _require_metrics(
        self,
    ) -> MetricsRuntime:
        """
        Ensure metrics backend exists.
        """

        if self.metrics is None:

            raise RuntimeError(
                "Metrics runtime is not available."
            )

        return self.metrics

    def _metric_collection(
        self,
    ) -> MetricList:
        """
        Return all metric records.
        """

        metrics = self._require_metrics()

        #
        # Preferred API
        #

        if hasattr(
            metrics,
            "list",
        ):

            records = metrics.list()

        #
        # Registry-like API
        #

        elif hasattr(
            metrics,
            "metrics",
        ):

            records = metrics.metrics

        #
        # Fallback
        #

        else:

            records = []

        normalized: MetricList = []

        for item in records:

            if isinstance(
                item,
                dict,
            ):

                normalized.append(item)

            elif hasattr(
                item,
                "to_dict",
            ):

                normalized.append(
                    item.to_dict()
                )

            elif hasattr(
                item,
                "__dict__",
            ):

                normalized.append(
                    dict(item.__dict__)
                )

            else:

                normalized.append(

                    {

                        "value": item

                    }

                )

        return normalized

    # ------------------------------------------------------
    # Part 3.2 List Operations
    # ------------------------------------------------------

    def list(
        self,
        *,
        limit: int | None = None,
    ) -> MetricList:
        """
        List metric records.
        """

        self._record_command(
            "list"
        )

        records = self._metric_collection()

        if limit is None:

            return records

        return records[:limit]

    # ------------------------------------------------------
    # Part 3.3 Lookup Operations
    # ------------------------------------------------------

    def get(
        self,
        metric_id: str,
    ) -> MetricRecord | None:
        """
        Get a metric by identifier.
        """

        self._record_command(
            "get"
        )

        metrics = self._require_metrics()

        if hasattr(
            metrics,
            "get",
        ):

            result = metrics.get(
                metric_id
            )

            if result is None:

                return None

            if isinstance(
                result,
                dict,
            ):

                return result

            if hasattr(
                result,
                "to_dict",
            ):

                return result.to_dict()

            if hasattr(
                result,
                "__dict__",
            ):

                return dict(
                    result.__dict__
                )

            return {

                "value": result

            }

        #
        # Fallback search
        #

        for metric in self._metric_collection():

            if metric.get(
                "id"
            ) == metric_id:

                return metric

        return None

    def exists(
        self,
        metric_id: str,
    ) -> bool:
        """
        Whether a metric exists.
        """

        return (

            self.get(
                metric_id
            )

            is not None

        )

    # ------------------------------------------------------
    # Part 3.4 Navigation
    # ------------------------------------------------------

    def latest(
        self,
    ) -> MetricRecord | None:
        """
        Return latest metric.
        """

        records = self._metric_collection()

        if not records:

            return None

        return records[-1]

    # ------------------------------------------------------
    # Part 3.5 Statistics
    # ------------------------------------------------------

    def count(
        self,
    ) -> int:
        """
        Number of metrics.
        """

        return len(

            self._metric_collection()

        )

    # ------------------------------------------------------
    # Part 3.6 Runtime Operations
    # ------------------------------------------------------

    def clear(
        self,
    ):
        """
        Remove all metrics.
        """

        self._record_command(
            "clear"
        )

        metrics = self._require_metrics()

        #
        # Preferred API
        #

        if hasattr(
            metrics,
            "clear",
        ):

            return metrics.clear()

        #
        # Registry fallback
        #

        if hasattr(
            metrics,
            "metrics",
        ):

            metrics.metrics.clear()

            return True

        raise NotImplementedError(

            "Metrics backend does not "
            "support clear()."

        )
# ==========================================================
# Part 4
# Search & Filter
#
# Provides:
#     • search()
#     • filter()
#     • filter_by_name()
#     • filter_by_type()
#     • filter_by_tag()
#     • query()
#
# Notes:
#     Search is intentionally backend-agnostic.
#     Every metric record is normalized into a dictionary.
# ==========================================================

    # ------------------------------------------------------
    # Part 4.1 Internal Helpers
    # ------------------------------------------------------

    def _normalize_metric(
        self,
        metric: MetricRecord | Any,
    ) -> MetricRecord:
        """
        Normalize a metric into a dictionary.
        """

        if isinstance(metric, dict):

            return metric

        if hasattr(metric, "to_dict"):

            return metric.to_dict()

        if hasattr(metric, "__dict__"):

            return dict(metric.__dict__)

        return {

            "value": metric,

        }

    def _match_text(
        self,
        metric: MetricRecord,
        keyword: str,
    ) -> bool:
        """
        Perform case-insensitive text matching.
        """

        return (

            keyword.casefold()

            in

            json.dumps(

                metric,

                ensure_ascii=False,

                default=str,

            ).casefold()

        )

    # ------------------------------------------------------
    # Part 4.2 Search
    # ------------------------------------------------------

    def search(
        self,
        keyword: str,
    ) -> MetricList:
        """
        Search metrics using free text.
        """

        self.search_count += 1

        self._record_command(
            "search"
        )

        result: MetricList = []

        for metric in self._metric_collection():

            item = self._normalize_metric(
                metric
            )

            if self._match_text(
                item,
                keyword,
            ):

                result.append(
                    item
                )

        return result

    # ------------------------------------------------------
    # Part 4.3 Generic Filter
    # ------------------------------------------------------

    def filter(
        self,
        predicate: MetricFilter,
    ) -> MetricList:
        """
        Filter metrics using a predicate.
        """

        self._record_command(
            "filter"
        )

        result: MetricList = []

        for metric in self._metric_collection():

            item = self._normalize_metric(
                metric
            )

            try:

                if predicate(item):

                    result.append(
                        item
                    )

            except Exception:

                #
                # Ignore malformed records.
                #

                continue

        return result

    # ------------------------------------------------------
    # Part 4.4 Built-in Filters
    # ------------------------------------------------------

    def filter_by_name(
        self,
        name: str,
    ) -> MetricList:
        """
        Filter metrics by name.
        """

        return self.filter(

            lambda metric:

            metric.get("name") == name

        )

    def filter_by_type(
        self,
        metric_type: str,
    ) -> MetricList:
        """
        Filter metrics by type.
        """

        return self.filter(

            lambda metric:

            metric.get("type") == metric_type

        )

    def filter_by_tag(
        self,
        tag: str,
    ) -> MetricList:
        """
        Filter metrics by tag.
        """

        return self.filter(

            lambda metric:

            tag in metric.get(

                "tags",

                [],

            )

        )

    # ------------------------------------------------------
    # Part 4.5 Multi-field Query
    # ------------------------------------------------------

    def query(
        self,
        **criteria,
    ) -> MetricList:
        """
        Query metrics by exact field matching.

        Example:

            query(
                name="cpu",
                type="gauge"
            )
        """

        self._record_command(
            "query"
        )

        result: MetricList = []

        for metric in self._metric_collection():

            item = self._normalize_metric(
                metric
            )

            matched = True

            for key, expected in criteria.items():

                if item.get(key) != expected:

                    matched = False

                    break

            if matched:

                result.append(
                    item
                )

        return result
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
# Notes:
#     Export helpers are backend-independent. Every metric
#     is first normalized into a dictionary before writing.
# ==========================================================

    # ------------------------------------------------------
    # Part 5.1 Internal Helpers
    # ------------------------------------------------------

    def _export_records(
        self,
    ) -> MetricList:
        """
        Return normalized metric records.
        """

        return [

            self._normalize_metric(metric)

            for metric in self._metric_collection()

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
        Export metrics to JSON.
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
        Export metrics to CSV.
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
        Export metrics to plain text.
        """

        path = ensure_path(path)

        with path.open(
            "w",
            encoding="utf-8",
        ) as fp:

            for metric in self._export_records():

                fp.write(

                    pretty_json(metric)

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
        Export metrics.

        Supported formats:

            • json
            • csv
            • text
            • txt
        """

        format = format.lower()

        exporters = {

            "json": self.export_json,

            "csv": self.export_csv,

            "text": self.export_text,

            "txt": self.export_text,

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
        Serialize metrics into a JSON string.
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
# Notes:
#     Runtime helpers manage the CLI runtime only.
#     They do NOT modify the MetricsRuntime backend unless
#     explicitly requested.
# ==========================================================

    # ------------------------------------------------------
    # Part 6.1 Runtime State
    # ------------------------------------------------------

    def enable(
        self,
    ) -> "MetricsCLI":
        """
        Enable the CLI runtime.
        """

        self.enabled = True

        self.touch()

        return self

    def disable(
        self,
    ) -> "MetricsCLI":
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
    ) -> "MetricsCLI":
        """
        Reset CLI runtime statistics.

        Parameters
        ----------
        clear_backend:
            Also clear MetricsRuntime if supported.
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

            self.has_metrics()

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
        Return a runtime snapshot.
        """

        return {

            "identity": self.identity,

            "metadata": self.metadata(),

            "runtime": {

                "enabled":

                    self.enabled,

                "running":

                    self.running,

                "closed":

                    self.closed,

                "metrics_available":

                    self.has_metrics(),

            },

            "statistics": {

                "metrics":

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

        if self.metrics is not None:

            backend = type(

                self.metrics

            ).__name__

        return {

            "snapshot":

                self.runtime_snapshot(),

            "configuration": {

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

                    self.has_metrics(),

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
# MetricsCLI behaves like:
#
#   • printable object
#   • iterable container
#   • mapping
#   • callable runtime
#   • shallow/deep cloneable
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

            f"metrics={self.count()}, "

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

            f"({self.count()} metrics)"

        )

    # ------------------------------------------------------
    # Part 7.2 Container Protocols
    # ------------------------------------------------------

    def __len__(
        self,
    ) -> int:
        """
        Number of metrics.
        """

        return self.count()

    def __iter__(
        self,
    ):
        """
        Iterate over metrics.
        """

        return iter(

            self.list()

        )

    def __contains__(
        self,
        metric_id: str,
    ) -> bool:
        """
        Membership test.

        Example
        -------
            if "cpu_usage" in cli:
                ...
        """

        return self.exists(
            metric_id
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

            cli["status"]

            cli["metadata"]

            cli["runtime"]

            cli["diagnostics"]

            cli["metric_id"]
        """

        if not isinstance(
            key,
            str,
        ):
            raise KeyError(key)

        mapping = {

            "status": {

                "enabled": self.enabled,

                "running": self.running,

                "closed": self.closed,

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

        metric = self.get(key)

        if metric is not None:

            return metric

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

            cli("search", "cpu")
        """

        if command is None:

            return self.runtime_snapshot()

        dispatch = {

            "list":

                self.list,

            "latest":

                self.latest,

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

        handler = dispatch.get(command)

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
        Shallow copy.

        MetricsRuntime backend reference
        is intentionally shared.
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
        Deep copy.

        MetricsRuntime backend is
        intentionally NOT deep-copied.
        """

        cls = self.__class__

        new = cls.__new__(cls)

        memo[id(self)] = new

        for key, value in self.__dict__.items():

            if key == "metrics":

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
"""
SciOS-NG Runtime Observability

CLI : Inspector

inspect.py

Part 1
Foundation

Provides

    • imports
    • constants
    • type aliases
    • utilities

InspectCLI is the unified inspection frontend for the
SciOS runtime observability system.

Unlike TraceCLI, MetricsCLI and LogsCLI, InspectCLI does
not own any data. It aggregates information from multiple
runtime components and provides a unified inspection API.
"""

from __future__ import annotations

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
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
)

# ==========================================================
# Optional Runtime Components
# ==========================================================

try:

    from .trace import TraceCLI

except Exception:

    TraceCLI = Any

try:

    from .metrics import MetricsCLI

except Exception:

    MetricsCLI = Any

try:

    from .logs import LogsCLI

except Exception:

    LogsCLI = Any


# ==========================================================
# Package Metadata
# ==========================================================

__all__ = [

    "InspectCLI",

    "INSPECT_COMPONENTS",

    "DEFAULT_EXPORT_FORMAT",

]

__version__ = "0.1.0"

__author__ = "SciOS-NG"

__description__ = (
    "Unified Runtime Inspection Command Line Interface"
)

# ==========================================================
# Constants
# ==========================================================

INSPECT_COMPONENTS = (

    "runtime",

    "trace",

    "metrics",

    "logs",

    "dashboard",

)

DEFAULT_EXPORT_FORMAT = "json"

DEFAULT_TIMEOUT = 30.0

DEFAULT_LIMIT = 100

INSPECT_ID_LENGTH = 8

# ==========================================================
# Type Aliases
# ==========================================================

InspectionRecord = Dict[str, Any]

InspectionList = List[InspectionRecord]

InspectionFilter = Callable[[InspectionRecord], bool]

ComponentMap = Dict[str, Any]

# ==========================================================
# Foundation Utilities
# ==========================================================


def generate_inspection_id() -> str:
    """
    Generate a short inspection identifier.
    """

    return uuid.uuid4().hex[:INSPECT_ID_LENGTH]


def timestamp() -> float:
    """
    Return current UNIX timestamp.
    """

    return time.time()


def now_iso() -> str:
    """
    Return current UTC ISO-8601 timestamp.
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
    Pretty JSON serializer.
    """

    return json.dumps(

        obj,

        indent=4,

        ensure_ascii=False,

        default=str,

    )


def component_available(
    component: Any,
) -> bool:
    """
    Whether an optional component exists.
    """

    return component is not Any


# ==========================================================
# Runtime Information
# ==========================================================


def runtime_info() -> dict:
    """
    Return foundation runtime information.
    """

    return {

        "module":

            __name__,

        "version":

            __version__,

        "description":

            __description__,

        "components": {

            "trace":

                component_available(

                    TraceCLI

                ),

            "metrics":

                component_available(

                    MetricsCLI

                ),

            "logs":

                component_available(

                    LogsCLI

                ),

        },

        "supported_components":

            list(

                INSPECT_COMPONENTS

            ),

        "default_export_format":

            DEFAULT_EXPORT_FORMAT,

    }
# ==========================================================
# Part 2
# Constructor
#
# Provides:
#     • InspectCLI.__init__()
#     • Runtime identity
#     • Component bindings
#     • Configuration
#     • Runtime state
#     • Runtime statistics
#     • Metadata
# ==========================================================


class InspectCLI:
    """
    SciOS-NG Unified Runtime Inspector.

    InspectCLI aggregates multiple observability
    components into a single inspection interface.

    Supported components

        • TraceCLI
        • MetricsCLI
        • LogsCLI
    """

    # ------------------------------------------------------
    # Part 2.1 Constructor
    # ------------------------------------------------------

    def __init__(
        self,
        *,
        trace: Optional[TraceCLI] = None,
        metrics: Optional[MetricsCLI] = None,
        logs: Optional[LogsCLI] = None,
        name: str = "SciOS Inspector",
        version: str = __version__,
        description: str = __description__,
    ) -> None:
        """
        Initialize InspectCLI.
        """

        # ==================================================
        # Identity
        # ==================================================

        self.id: str = str(uuid.uuid4())

        self.name: str = name

        self.version: str = version

        self.description: str = description

        self.component: str = "inspect-cli"

        # ==================================================
        # Component Bindings
        # ==================================================

        self.trace: Optional[TraceCLI] = trace

        self.metrics: Optional[MetricsCLI] = metrics

        self.logs: Optional[LogsCLI] = logs

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

        self.inspect_count: int = 0

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

        now = timestamp()

        self.updated_at = now

        self.last_activity = now

        self.revision += 1

    # ------------------------------------------------------
    # Part 2.3 Component Binding
    # ------------------------------------------------------

    def bind_trace(
        self,
        trace: TraceCLI,
    ) -> "InspectCLI":
        """
        Bind TraceCLI.
        """

        self.trace = trace

        self.touch()

        return self

    def bind_metrics(
        self,
        metrics: MetricsCLI,
    ) -> "InspectCLI":
        """
        Bind MetricsCLI.
        """

        self.metrics = metrics

        self.touch()

        return self

    def bind_logs(
        self,
        logs: LogsCLI,
    ) -> "InspectCLI":
        """
        Bind LogsCLI.
        """

        self.logs = logs

        self.touch()

        return self

    def unbind_trace(
        self,
    ) -> "InspectCLI":
        """
        Remove TraceCLI binding.
        """

        self.trace = None

        self.touch()

        return self

    def unbind_metrics(
        self,
    ) -> "InspectCLI":
        """
        Remove MetricsCLI binding.
        """

        self.metrics = None

        self.touch()

        return self

    def unbind_logs(
        self,
    ) -> "InspectCLI":
        """
        Remove LogsCLI binding.
        """

        self.logs = None

        self.touch()

        return self

    # ------------------------------------------------------
    # Part 2.4 Component Status
    # ------------------------------------------------------

    def has_trace(
        self,
    ) -> bool:
        """
        Whether TraceCLI is available.
        """

        return self.trace is not None

    def has_metrics(
        self,
    ) -> bool:
        """
        Whether MetricsCLI is available.
        """

        return self.metrics is not None

    def has_logs(
        self,
    ) -> bool:
        """
        Whether LogsCLI is available.
        """

        return self.logs is not None

    # ------------------------------------------------------
    # Part 2.5 Identity
    # ------------------------------------------------------

    @property
    def identity(
        self,
    ) -> dict:
        """
        Runtime identity.
        """

        return {

            "id": self.id,

            "name": self.name,

            "component": self.component,

            "version": self.version,

            "description": self.description,

        }

    # ------------------------------------------------------
    # Part 2.6 Metadata
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
    # Part 2.7 Runtime Information
    # ------------------------------------------------------

    def info(
        self,
    ) -> dict:
        """
        Return runtime information.
        """

        return {

            "identity": self.identity,

            "metadata": self.metadata(),

            "enabled": self.enabled,

            "running": self.running,

            "closed": self.closed,

            "components": {

                "trace": self.has_trace(),

                "metrics": self.has_metrics(),

                "logs": self.has_logs(),

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
# ==========================================================
# Part 3
# Runtime Inspection
#
# Provides:
#     • inspect_runtime()
#     • inspect_metrics()
#     • inspect_logs()
#     • inspect_traces()
#     • inspect_dashboard()
#     • inspect_all()
#
# Notes
# -----
# InspectCLI is an aggregation layer. It delegates all
# inspection work to the bound CLI components and never
# owns runtime data itself.
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

        self.inspect_count += 1

        self.last_command = command

        self.touch()

    def _component_snapshot(
        self,
        component: Any,
    ) -> dict:
        """
        Safely obtain a runtime snapshot from a component.
        """

        if component is None:

            return {

                "available": False,

            }

        try:

            if hasattr(
                component,
                "runtime_snapshot",
            ):

                snapshot = component.runtime_snapshot()

                if isinstance(
                    snapshot,
                    dict,
                ):

                    snapshot["available"] = True

                    return snapshot

            if hasattr(
                component,
                "diagnostics",
            ):

                return {

                    "available": True,

                    "diagnostics":

                        component.diagnostics(),

                }

            return {

                "available": True,

                "type":

                    type(component).__name__,

            }

        except Exception as exc:

            self.error_count += 1

            self.last_error = str(exc)

            return {

                "available": False,

                "error": str(exc),

            }

    # ------------------------------------------------------
    # Part 3.2 Runtime
    # ------------------------------------------------------

    def inspect_runtime(
        self,
    ) -> dict:
        """
        Inspect the overall runtime.
        """

        self._record_command(
            "inspect_runtime"
        )

        return {

            "identity":

                self.identity,

            "metadata":

                self.metadata(),

            "state": {

                "enabled":

                    self.enabled,

                "running":

                    self.running,

                "closed":

                    self.closed,

            },

            "components": {

                "trace":

                    self.has_trace(),

                "metrics":

                    self.has_metrics(),

                "logs":

                    self.has_logs(),

            },

            "statistics": {

                "inspections":

                    self.inspect_count,

                "commands":

                    self.command_count,

                "errors":

                    self.error_count,

            },

        }

    # ------------------------------------------------------
    # Part 3.3 Metrics
    # ------------------------------------------------------

    def inspect_metrics(
        self,
    ) -> dict:
        """
        Inspect MetricsCLI.
        """

        self._record_command(
            "inspect_metrics"
        )

        return self._component_snapshot(

            self.metrics

        )

    # ------------------------------------------------------
    # Part 3.4 Logs
    # ------------------------------------------------------

    def inspect_logs(
        self,
    ) -> dict:
        """
        Inspect LogsCLI.
        """

        self._record_command(
            "inspect_logs"
        )

        return self._component_snapshot(

            self.logs

        )

    # ------------------------------------------------------
    # Part 3.5 Traces
    # ------------------------------------------------------

    def inspect_traces(
        self,
    ) -> dict:
        """
        Inspect TraceCLI.
        """

        self._record_command(
            "inspect_traces"
        )

        return self._component_snapshot(

            self.trace

        )

    # ------------------------------------------------------
    # Part 3.6 Dashboard
    # ------------------------------------------------------

    def inspect_dashboard(
        self,
    ) -> dict:
        """
        Inspect the observability dashboard.

        This method is intentionally generic so that
        dashboard support can be added later without
        changing the public API.
        """

        self._record_command(
            "inspect_dashboard"
        )

        dashboard = getattr(

            self,

            "dashboard",

            None,

        )

        return self._component_snapshot(

            dashboard

        )

    # ------------------------------------------------------
    # Part 3.7 Full Inspection
    # ------------------------------------------------------

    def inspect_all(
        self,
    ) -> dict:
        """
        Inspect every registered component.
        """

        self._record_command(
            "inspect_all"
        )

        return {

            "runtime":

                self.inspect_runtime(),

            "metrics":

                self.inspect_metrics(),

            "logs":

                self.inspect_logs(),

            "traces":

                self.inspect_traces(),

            "dashboard":

                self.inspect_dashboard(),

            "generated_at":

                timestamp(),

        }
# ==========================================================
# Part 4
# Search & Query
#
# Provides:
#     • search()
#     • query()
#     • filter()
#     • inspect_object()
#     • inspect_component()
#
# Notes
# -----
# Search operates across every registered CLI component.
# Components are queried only if they implement the
# requested capability.
# ==========================================================

    # ------------------------------------------------------
    # Part 4.1 Internal Helper
    # ------------------------------------------------------

    def _components(
        self,
    ) -> ComponentMap:
        """
        Return registered inspection components.
        """

        return {

            "trace": self.trace,

            "metrics": self.metrics,

            "logs": self.logs,

            "dashboard": getattr(

                self,

                "dashboard",

                None,

            ),

        }

    # ------------------------------------------------------
    # Part 4.2 Global Search
    # ------------------------------------------------------

    def search(
        self,
        keyword: str,
    ) -> dict:
        """
        Search every registered component.
        """

        self._record_command(
            "search"
        )

        self.search_count += 1

        results = {}

        for name, component in self._components().items():

            if component is None:

                continue

            if hasattr(

                component,

                "search",

            ):

                try:

                    results[name] = (

                        component.search(

                            keyword

                        )

                    )

                except Exception as exc:

                    self.error_count += 1

                    results[name] = {

                        "error": str(exc)

                    }

        return results

    # ------------------------------------------------------
    # Part 4.3 Multi-field Query
    # ------------------------------------------------------

    def query(
        self,
        **criteria,
    ) -> dict:
        """
        Query every registered component.
        """

        self._record_command(
            "query"
        )

        results = {}

        for name, component in self._components().items():

            if component is None:

                continue

            if hasattr(

                component,

                "query",

            ):

                try:

                    results[name] = (

                        component.query(

                            **criteria

                        )

                    )

                except Exception as exc:

                    self.error_count += 1

                    results[name] = {

                        "error": str(exc)

                    }

        return results

    # ------------------------------------------------------
    # Part 4.4 Generic Filter
    # ------------------------------------------------------

    def filter(
        self,
        predicate,
    ) -> dict:
        """
        Apply a predicate filter to every component.
        """

        self._record_command(
            "filter"
        )

        results = {}

        for name, component in self._components().items():

            if component is None:

                continue

            if hasattr(

                component,

                "filter",

            ):

                try:

                    results[name] = (

                        component.filter(

                            predicate

                        )

                    )

                except Exception as exc:

                    self.error_count += 1

                    results[name] = {

                        "error": str(exc)

                    }

        return results

    # ------------------------------------------------------
    # Part 4.5 Object Inspection
    # ------------------------------------------------------

    def inspect_object(
        self,
        obj: Any,
    ) -> dict:
        """
        Inspect an arbitrary Python object.
        """

        self._record_command(
            "inspect_object"
        )

        return {

            "type":

                type(obj).__name__,

            "module":

                getattr(

                    type(obj),

                    "__module__",

                    None,

                ),

            "repr":

                repr(obj),

            "attributes":

                sorted(

                    dir(obj)

                ),

            "callable":

                callable(obj),

            "id":

                id(obj),

        }

    # ------------------------------------------------------
    # Part 4.6 Component Inspection
    # ------------------------------------------------------

    def inspect_component(
        self,
        name: str,
    ) -> dict:
        """
        Inspect a named component.

        Supported names

            • trace
            • metrics
            • logs
            • dashboard
            • runtime
        """

        self._record_command(
            "inspect_component"
        )

        if name == "runtime":

            return self.inspect_runtime()

        component = self._components().get(
            name
        )

        if component is None:

            raise KeyError(

                f"Unknown component: {name}"

            )

        return self._component_snapshot(
            component
        )
# ==========================================================
# Part 5
# Export
#
# Provides:
#     • export()
#     • export_json()
#     • export_text()
#     • dumps()
#
# Notes
# -----
# Export operations serialize the unified inspection
# report produced by InspectCLI.
# ==========================================================

    # ------------------------------------------------------
    # Part 5.1 Internal Helper
    # ------------------------------------------------------

    def _export_payload(
        self,
    ) -> dict:
        """
        Build the export payload.
        """

        return {

            "runtime":

                self.inspect_runtime(),

            "components": {

                "trace":

                    self.inspect_traces(),

                "metrics":

                    self.inspect_metrics(),

                "logs":

                    self.inspect_logs(),

                "dashboard":

                    self.inspect_dashboard(),

            },

            "generated_at":

                now_iso(),

        }

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
        Export the inspection report as JSON.
        """

        path = ensure_path(path)

        payload = self._export_payload()

        with path.open(
            "w",
            encoding="utf-8",
        ) as fp:

            json.dump(

                payload,

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
    # Part 5.3 Text Export
    # ------------------------------------------------------

    def export_text(
        self,
        path: str | Path,
    ) -> Path:
        """
        Export the inspection report as text.
        """

        path = ensure_path(path)

        report = self._export_payload()

        with path.open(
            "w",
            encoding="utf-8",
        ) as fp:

            fp.write(
                "SciOS Runtime Inspection Report\n"
            )

            fp.write("=" * 60)

            fp.write("\n\n")

            fp.write(
                pretty_json(report)
            )

            fp.write("\n")

        self.export_count += 1

        self._record_command(
            "export_text"
        )

        return path

    # ------------------------------------------------------
    # Part 5.4 Generic Export
    # ------------------------------------------------------

    def export(
        self,
        path: str | Path,
        *,
        format: str = DEFAULT_EXPORT_FORMAT,
    ) -> Path:
        """
        Export an inspection report.

        Supported formats

            • json
            • text
            • txt
        """

        format = format.lower()

        exporters = {

            "json":

                self.export_json,

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
    # Part 5.5 Dumps
    # ------------------------------------------------------

    def dumps(
        self,
        *,
        indent: int = 4,
    ) -> str:
        """
        Serialize the inspection report into a JSON string.
        """

        self._record_command(
            "dumps"
        )

        return json.dumps(

            self._export_payload(),

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
# These helpers manage the InspectCLI runtime only.
# They do not modify TraceCLI, MetricsCLI or LogsCLI
# except when explicitly extended in the future.
# ==========================================================

    # ------------------------------------------------------
    # Part 6.1 Runtime State
    # ------------------------------------------------------

    def enable(
        self,
    ) -> "InspectCLI":
        """
        Enable the inspector.
        """

        self.enabled = True

        self.touch()

        return self

    def disable(
        self,
    ) -> "InspectCLI":
        """
        Disable the inspector.
        """

        self.enabled = False

        self.touch()

        return self

    # ------------------------------------------------------
    # Part 6.2 Reset
    # ------------------------------------------------------

    def reset(
        self,
        *,
        reset_components: bool = False,
    ) -> "InspectCLI":
        """
        Reset runtime statistics.

        Parameters
        ----------
        reset_components
            Reset all bound components that provide
            a reset() method.
        """

        self.command_count = 0
        self.inspect_count = 0
        self.search_count = 0
        self.export_count = 0
        self.refresh_count = 0
        self.error_count = 0

        self.last_command = None
        self.last_error = None

        self.last_activity = timestamp()

        if reset_components:

            for component in self._components().values():

                if (

                    component is not None

                    and

                    hasattr(component, "reset")

                ):

                    try:

                        component.reset()

                    except Exception:

                        self.error_count += 1

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

            },

            "statistics": {

                "commands":

                    self.command_count,

                "inspections":

                    self.inspect_count,

                "searches":

                    self.search_count,

                "exports":

                    self.export_count,

                "refreshes":

                    self.refresh_count,

                "errors":

                    self.error_count,

            },

            "components": {

                name: (

                    component is not None

                )

                for name, component

                in self._components().items()

            },

        }

    # ------------------------------------------------------
    # Part 6.4 Diagnostics
    # ------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict:
        """
        Return diagnostic information.
        """

        diagnostics = {

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

            "components": {},

        }

        for name, component in self._components().items():

            if component is None:

                diagnostics["components"][name] = {

                    "available": False

                }

                continue

            if hasattr(

                component,

                "diagnostics",

            ):

                try:

                    diagnostics["components"][name] = (

                        component.diagnostics()

                    )

                except Exception as exc:

                    diagnostics["components"][name] = {

                        "available": False,

                        "error": str(exc),

                    }

            else:

                diagnostics["components"][name] = {

                    "available": True,

                    "type": type(component).__name__,

                }

        return diagnostics

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
# InspectCLI behaves as
#
#   • printable object
#   • iterable container
#   • mapping
#   • callable runtime
#   • copyable object
#
# Unlike TraceCLI / MetricsCLI / LogsCLI, iteration is over
# registered observability components rather than records.
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

            f"components={len(self)}, "

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

            f"({len(self)} components)"

        )

    # ------------------------------------------------------
    # Part 7.2 Container Protocols
    # ------------------------------------------------------

    def __len__(
        self,
    ) -> int:
        """
        Return the number of registered components.
        """

        return sum(

            component is not None

            for component in self._components().values()

        )

    def __iter__(
        self,
    ):
        """
        Iterate over registered components.

        Yields
        ------
        (name, component)
        """

        return iter(

            self._components().items()

        )

    def __contains__(
        self,
        name: str,
    ) -> bool:
        """
        Membership test.

        Example
        -------
            "metrics" in inspector
        """

        return (

            name in self._components()

            and

            self._components()[name] is not None

        )

    # ------------------------------------------------------
    # Part 7.3 Mapping Protocol
    # ------------------------------------------------------

    def __getitem__(
        self,
        key: str,
    ):
        """
        Mapping-style access.

        Examples
        --------

            inspector["runtime"]

            inspector["metadata"]

            inspector["metrics"]

            inspector["logs"]

            inspector["trace"]

            inspector["diagnostics"]
        """

        mapping = {

            "identity":

                self.identity,

            "metadata":

                self.metadata(),

            "runtime":

                self.runtime_snapshot(),

            "diagnostics":

                self.diagnostics(),

        }

        if key in mapping:

            return mapping[key]

        components = self._components()

        if key in components:

            return components[key]

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

            inspector()

            inspector("runtime")

            inspector("inspect_all")

            inspector("search", "error")

            inspector("query", level="ERROR")
        """

        if command is None:

            return self.runtime_snapshot()

        dispatch = {

            "runtime":

                self.inspect_runtime,

            "metrics":

                self.inspect_metrics,

            "logs":

                self.inspect_logs,

            "traces":

                self.inspect_traces,

            "dashboard":

                self.inspect_dashboard,

            "inspect_all":

                self.inspect_all,

            "search":

                self.search,

            "query":

                self.query,

            "filter":

                self.filter,

            "diagnostics":

                self.diagnostics,

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
        Create a shallow copy.

        Bound CLI components remain shared.
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

        Runtime components remain shared because they
        usually represent singleton runtime services.
        """

        cls = self.__class__

        new = cls.__new__(cls)

        memo[id(self)] = new

        shared = {

            "trace",

            "metrics",

            "logs",

            "dashboard",

        }

        for key, value in self.__dict__.items():

            if key in shared:

                #
                # Share runtime services.
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
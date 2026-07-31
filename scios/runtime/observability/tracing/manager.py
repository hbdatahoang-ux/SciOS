"""
SciOS-NG
Runtime Observability - Trace Manager

File:
    scios/runtime/observability/tracing/manager.py

Part 1.1
Foundation

This module implements the central runtime tracing manager used by
SciOS-NG Observability.

The TraceManager is responsible for coordinating:

    • Trace lifecycle
    • Span lifecycle
    • TraceContext propagation
    • Sampling
    • Processing
    • Exporting
    • Runtime hooks
    • Diagnostics
    • Serialization
    • Runtime statistics

Author:
    SciOS-NG Project

License:
    MIT
"""

from __future__ import annotations

# ==============================================================================
# Imports
# ==============================================================================

import copy
import json
import threading
import time
import uuid

from collections import (
    defaultdict,
    deque,
)

from dataclasses import (
    asdict,
    dataclass,
    field,
)

from datetime import (
    datetime,
    timezone,
)

from enum import (
    Enum,
    IntFlag,
)

from threading import (
    RLock,
)

from typing import (
    Any,
    Callable,
    Deque,
    Dict,
    Iterable,
    Iterator,
    List,
    Mapping,
    MutableMapping,
    MutableSequence,
    Optional,
    Sequence,
    Set,
    TypeAlias,
    TYPE_CHECKING,
    Union,
)

# ==============================================================================
# Local Imports
# ==============================================================================

from .context import TraceContext
from .processor import TraceProcessor
from .sampler import TraceSampler
from .status import TraceStatus

if TYPE_CHECKING:
    from .trace import Trace
    from .span import TraceSpan

# ==============================================================================
# Module Information
# ==============================================================================

MODULE_NAME: str = "TraceManager"

MODULE_DESCRIPTION: str = (
    "SciOS-NG Runtime Observability Trace Manager"
)

MODULE_VERSION: str = "0.3.0-alpha"

MODULE_AUTHOR: str = "SciOS-NG"

MODULE_LICENSE: str = "MIT"

# ==============================================================================
# Manager Information
# ==============================================================================

MANAGER_NAME: str = "TraceManager"

MANAGER_DESCRIPTION: str = (
    "SciOS-NG Runtime Observability Trace Manager"
)

MANAGER_VERSION: str = MODULE_VERSION

# ==============================================================================
# Runtime Defaults
# ==============================================================================

DEFAULT_ENABLED: bool = True

DEFAULT_AUTO_INITIALIZE: bool = True

DEFAULT_AUTO_FLUSH: bool = True

DEFAULT_AUTO_PROCESS: bool = True

DEFAULT_AUTO_EXPORT: bool = True

DEFAULT_STRICT_VALIDATION: bool = False

DEFAULT_READ_ONLY: bool = False

DEFAULT_THREAD_SAFE: bool = True

# ==============================================================================
# Runtime Limits
# ==============================================================================

DEFAULT_HISTORY_LIMIT: int = 1024

DEFAULT_CACHE_SIZE: int = 512

DEFAULT_TIMEOUT: float = 30.0

DEFAULT_MAX_PROCESSORS: int = 64

DEFAULT_MAX_EXPORTERS: int = 32

DEFAULT_MAX_TRACERS: int = 64

DEFAULT_MAX_PIPELINES: int = 16

DEFAULT_MAX_TRACES: int = 4096

DEFAULT_MAX_SPANS: int = 65536

DEFAULT_METADATA_LIMIT: int = 256

DEFAULT_TAG_LIMIT: int = 256

DEFAULT_CALLBACK_LIMIT: int = 128

DEFAULT_HOOK_LIMIT: int = 128

DEFAULT_FILTER_LIMIT: int = 128

# ==============================================================================
# Serialization
# ==============================================================================

DEFAULT_ENCODING: str = "utf-8"

DEFAULT_JSON_INDENT: int = 2

DEFAULT_JSON_SORT_KEYS: bool = False

DEFAULT_JSON_ASCII: bool = False

# ==============================================================================
# Runtime Timing
# ==============================================================================

DEFAULT_HEALTH_INTERVAL: float = 5.0

DEFAULT_CLEANUP_INTERVAL: float = 60.0

DEFAULT_FLUSH_INTERVAL: float = 5.0

DEFAULT_SNAPSHOT_INTERVAL: float = 300.0

# ==============================================================================
# Runtime Keys
# ==============================================================================

TRACE_KEY: str = "trace"

SPAN_KEY: str = "span"

CONTEXT_KEY: str = "context"

PROCESSOR_KEY: str = "processor"

EXPORTER_KEY: str = "exporter"

PIPELINE_KEY: str = "pipeline"

SAMPLER_KEY: str = "sampler"

STATUS_KEY: str = "status"

# ==============================================================================
# Runtime Events
# ==============================================================================

EVENT_INITIALIZE: str = "initialize"

EVENT_START_TRACE: str = "start_trace"

EVENT_FINISH_TRACE: str = "finish_trace"

EVENT_START_SPAN: str = "start_span"

EVENT_FINISH_SPAN: str = "finish_span"

EVENT_PROCESS: str = "process"

EVENT_EXPORT: str = "export"

EVENT_FLUSH: str = "flush"

EVENT_RESET: str = "reset"

EVENT_CLEAR: str = "clear"

EVENT_CLOSE: str = "close"

# ==============================================================================
# End Part 1.1
# ==============================================================================
# ==============================================================================
# Part 1.2
# Type Aliases
# ==============================================================================

#
# Basic Identifiers
#

TraceId: TypeAlias = str

SpanId: TypeAlias = str

ParentSpanId: TypeAlias = Optional[str]

ManagerId: TypeAlias = str

ComponentId: TypeAlias = str

ComponentName: TypeAlias = str


# ------------------------------------------------------------------------------
# Generic Runtime Types
# ------------------------------------------------------------------------------

TraceValue: TypeAlias = Any

TraceRecord: TypeAlias = Dict[str, Any]

TraceData: TypeAlias = Dict[str, Any]

TraceMetadata: TypeAlias = Dict[str, Any]

TraceOptions: TypeAlias = Dict[str, Any]

ManagerMetadata: TypeAlias = Dict[str, Any]

ManagerContext: TypeAlias = Dict[str, Any]

ManagerOptions: TypeAlias = Dict[str, Any]


# ------------------------------------------------------------------------------
# Collections
# ------------------------------------------------------------------------------

TraceList: TypeAlias = List[Any]

SpanList: TypeAlias = List[Any]

ProcessorList: TypeAlias = List[TraceProcessor]

ExporterList: TypeAlias = List[Any]

TracerList: TypeAlias = List[Any]

PipelineList: TypeAlias = List[Any]


# ------------------------------------------------------------------------------
# Runtime Storage
# ------------------------------------------------------------------------------

TraceCache: TypeAlias = MutableMapping[str, Any]

TraceHistory: TypeAlias = Deque[Any]

RuntimeQueue: TypeAlias = Deque[Any]

RuntimeStack: TypeAlias = List[Any]


# ------------------------------------------------------------------------------
# Runtime Dictionaries
# ------------------------------------------------------------------------------

ComponentMap: TypeAlias = MutableMapping[
    str,
    Any,
]

ProcessorMap: TypeAlias = MutableMapping[
    str,
    TraceProcessor,
]

ExporterMap: TypeAlias = MutableMapping[
    str,
    Any,
]

TracerMap: TypeAlias = MutableMapping[
    str,
    Any,
]

PipelineMap: TypeAlias = MutableMapping[
    str,
    Any,
]

ContextMap: TypeAlias = MutableMapping[
    str,
    TraceContext,
]

SamplerMap: TypeAlias = MutableMapping[
    str,
    TraceSampler,
]


# ------------------------------------------------------------------------------
# Trace / Span Maps
# ------------------------------------------------------------------------------

TraceMap: TypeAlias = MutableMapping[
    TraceId,
    "Trace",
]

SpanMap: TypeAlias = MutableMapping[
    SpanId,
    "TraceSpan",
]


# ------------------------------------------------------------------------------
# Runtime Events
# ------------------------------------------------------------------------------

TraceEvent: TypeAlias = Dict[str, Any]

EventPayload: TypeAlias = Dict[str, Any]

EventQueue: TypeAlias = Deque[TraceEvent]


# ------------------------------------------------------------------------------
# Callback Types
# ------------------------------------------------------------------------------

TraceHook: TypeAlias = Callable[
    ...,
    None,
]

TraceCallback: TypeAlias = Callable[
    ...,
    None,
]

TraceFilter: TypeAlias = Callable[
    [Any],
    bool,
]

ProcessorCallback: TypeAlias = Callable[
    [TraceProcessor],
    None,
]

ExporterCallback: TypeAlias = Callable[
    [Any],
    None,
]

TracerCallback: TypeAlias = Callable[
    [Any],
    None,
]


# ------------------------------------------------------------------------------
# Factory Types
# ------------------------------------------------------------------------------

TraceFactory: TypeAlias = Callable[
    ...,
    "Trace",
]

SpanFactory: TypeAlias = Callable[
    ...,
    "TraceSpan",
]

ProcessorFactory: TypeAlias = Callable[
    ...,
    TraceProcessor,
]

SamplerFactory: TypeAlias = Callable[
    ...,
    TraceSampler,
]


# ------------------------------------------------------------------------------
# Runtime Iterators
# ------------------------------------------------------------------------------

TraceIterator: TypeAlias = Iterator["Trace"]

SpanIterator: TypeAlias = Iterator["TraceSpan"]

ProcessorIterator: TypeAlias = Iterator[
    TraceProcessor
]

ExporterIterator: TypeAlias = Iterator[Any]

TracerIterator: TypeAlias = Iterator[Any]

PipelineIterator: TypeAlias = Iterator[Any]


# ------------------------------------------------------------------------------
# Runtime Views
# ------------------------------------------------------------------------------

TraceMapping: TypeAlias = Mapping[
    TraceId,
    "Trace",
]

SpanMapping: TypeAlias = Mapping[
    SpanId,
    "TraceSpan",
]

ProcessorMapping: TypeAlias = Mapping[
    str,
    TraceProcessor,
]

ExporterMapping: TypeAlias = Mapping[
    str,
    Any,
]

TracerMapping: TypeAlias = Mapping[
    str,
    Any,
]


# ------------------------------------------------------------------------------
# Runtime Sequences
# ------------------------------------------------------------------------------

TraceSequence: TypeAlias = Sequence[
    "Trace"
]

SpanSequence: TypeAlias = Sequence[
    "TraceSpan"
]

ProcessorSequence: TypeAlias = Sequence[
    TraceProcessor
]


# ------------------------------------------------------------------------------
# Runtime Sets
# ------------------------------------------------------------------------------

ComponentSet: TypeAlias = Set[str]

TagSet: TypeAlias = Set[str]

CapabilitySet: TypeAlias = Set[str]


# ------------------------------------------------------------------------------
# Runtime State
# ------------------------------------------------------------------------------

RuntimeState: TypeAlias = Dict[str, Any]

RuntimeSnapshot: TypeAlias = Dict[str, Any]

RuntimeStatistics: TypeAlias = Dict[str, Any]

RuntimeReport: TypeAlias = Dict[str, Any]


# ==============================================================================
# End Part 1.2
# ==============================================================================
# ==============================================================================
# Part 1.3
# Exceptions
# ==============================================================================


class TraceManagerError(RuntimeError):
    """
    Base exception for the SciOS-NG TraceManager.

    Every TraceManager-specific exception derives from this class.
    """

    def __init__(
        self,
        message: str = "TraceManager runtime error.",
        *,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:

        super().__init__(message)

        self.message: str = str(message)

        self.details: Dict[str, Any] = dict(
            details or {}
        )

        self.timestamp: float = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize exception.
        """

        return {
            "type": self.__class__.__name__,
            "message": self.message,
            "details": dict(self.details),
            "timestamp": self.timestamp,
        }

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r})"
        )

    __str__ = RuntimeError.__str__


# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------


class ManagerConfigurationError(
    TraceManagerError
):
    """
    Invalid TraceManager configuration.
    """


class ManagerValidationError(
    TraceManagerError
):
    """
    Validation failure.
    """


class ManagerInitializationError(
    TraceManagerError
):
    """
    Initialization failed.
    """


class ManagerRuntimeError(
    TraceManagerError
):
    """
    Runtime execution failure.
    """


class ManagerStateError(
    TraceManagerError
):
    """
    Invalid manager state.
    """


class ManagerTimeoutError(
    TraceManagerError
):
    """
    Runtime timeout.
    """


class ManagerClosedError(
    TraceManagerError
):
    """
    Manager has already been closed.
    """


class ManagerFrozenError(
    TraceManagerError
):
    """
    Manager is frozen.
    """


class ManagerDisabledError(
    TraceManagerError
):
    """
    Manager is disabled.
    """


# ------------------------------------------------------------------------------
# Component Errors
# ------------------------------------------------------------------------------


class ComponentError(
    TraceManagerError
):
    """
    Base component error.
    """


class ComponentNotFoundError(
    ComponentError
):
    """
    Requested component does not exist.
    """


class DuplicateComponentError(
    ComponentError
):
    """
    Duplicate component registration.
    """


class ComponentRegistrationError(
    ComponentError
):
    """
    Component registration failed.
    """


class ComponentRemovalError(
    ComponentError
):
    """
    Component removal failed.
    """


# ------------------------------------------------------------------------------
# Processor
# ------------------------------------------------------------------------------


class ProcessorError(
    TraceManagerError
):
    """
    Processor failure.
    """


class ProcessorNotFoundError(
    ProcessorError
):
    """
    Processor not registered.
    """


# ------------------------------------------------------------------------------
# Exporter
# ------------------------------------------------------------------------------


class ExporterError(
    TraceManagerError
):
    """
    Exporter failure.
    """


class ExporterNotFoundError(
    ExporterError
):
    """
    Exporter not registered.
    """


# ------------------------------------------------------------------------------
# Tracer
# ------------------------------------------------------------------------------


class TracerError(
    TraceManagerError
):
    """
    Tracer failure.
    """


class TracerNotFoundError(
    TracerError
):
    """
    Tracer not registered.
    """


# ------------------------------------------------------------------------------
# Pipeline
# ------------------------------------------------------------------------------


class PipelineError(
    TraceManagerError
):
    """
    Pipeline failure.
    """


class PipelineNotFoundError(
    PipelineError
):
    """
    Pipeline not registered.
    """


# ------------------------------------------------------------------------------
# Trace
# ------------------------------------------------------------------------------


class TraceError(
    TraceManagerError
):
    """
    Trace lifecycle error.
    """


class TraceNotFoundError(
    TraceError
):
    """
    Requested trace does not exist.
    """


class ActiveTraceError(
    TraceError
):
    """
    Invalid active trace operation.
    """


# ------------------------------------------------------------------------------
# Span
# ------------------------------------------------------------------------------


class SpanError(
    TraceManagerError
):
    """
    Span lifecycle error.
    """


class SpanNotFoundError(
    SpanError
):
    """
    Requested span does not exist.
    """


class ActiveSpanError(
    SpanError
):
    """
    Invalid active span operation.
    """


# ------------------------------------------------------------------------------
# Context
# ------------------------------------------------------------------------------


class ContextError(
    TraceManagerError
):
    """
    Context operation failed.
    """


# ------------------------------------------------------------------------------
# Snapshot / Serialization
# ------------------------------------------------------------------------------


class SerializationError(
    TraceManagerError
):
    """
    Serialization failure.
    """


class DeserializationError(
    TraceManagerError
):
    """
    Deserialization failure.
    """


class SnapshotError(
    TraceManagerError
):
    """
    Snapshot operation failed.
    """


class RestoreError(
    TraceManagerError
):
    """
    Restore operation failed.
    """


# ------------------------------------------------------------------------------
# Callback / Hook
# ------------------------------------------------------------------------------


class CallbackError(
    TraceManagerError
):
    """
    Callback execution failed.
    """


class HookError(
    TraceManagerError
):
    """
    Hook execution failed.
    """


class FilterError(
    TraceManagerError
):
    """
    Filter execution failed.
    """


# ==============================================================================
# End Part 1.3
# ==============================================================================
# ==============================================================================
# Part 1.4
# Enums
# ==============================================================================


class ManagerType(str, Enum):
    """
    TraceManager implementation type.
    """

    STANDARD = "standard"

    DISTRIBUTED = "distributed"

    CLUSTER = "cluster"

    FEDERATED = "federated"

    HYBRID = "hybrid"

    EMBEDDED = "embedded"

    CUSTOM = "custom"


# ------------------------------------------------------------------------------


class ManagerState(str, Enum):
    """
    Runtime lifecycle state.
    """

    CREATED = "created"

    INITIALIZED = "initialized"

    STARTING = "starting"

    RUNNING = "running"

    PAUSED = "paused"

    STOPPING = "stopping"

    STOPPED = "stopped"

    FROZEN = "frozen"

    CLOSED = "closed"

    FAILED = "failed"


# ------------------------------------------------------------------------------


class ManagerMode(str, Enum):
    """
    Runtime execution mode.
    """

    SYNCHRONOUS = "synchronous"

    ASYNCHRONOUS = "asynchronous"

    PARALLEL = "parallel"

    DISTRIBUTED = "distributed"

    HYBRID = "hybrid"


# ------------------------------------------------------------------------------


class ManagerHealth(str, Enum):
    """
    Runtime health state.
    """

    UNKNOWN = "unknown"

    HEALTHY = "healthy"

    DEGRADED = "degraded"

    WARNING = "warning"

    UNHEALTHY = "unhealthy"

    FAILED = "failed"


# ------------------------------------------------------------------------------


class ManagerCapability(IntFlag):
    """
    Supported TraceManager capabilities.
    """

    NONE = 0

    #
    # Core
    #

    SAMPLING = 1 << 0

    PROCESSING = 1 << 1

    EXPORTING = 1 << 2

    CONTEXT = 1 << 3

    #
    # Runtime
    #

    PIPELINES = 1 << 4

    FILTERING = 1 << 5

    CACHING = 1 << 6

    HISTORY = 1 << 7

    #
    # Extension
    #

    CALLBACKS = 1 << 8

    HOOKS = 1 << 9

    EVENTS = 1 << 10

    TAGS = 1 << 11

    #
    # Diagnostics
    #

    DIAGNOSTICS = 1 << 12

    METRICS = 1 << 13

    SNAPSHOT = 1 << 14

    SERIALIZATION = 1 << 15

    #
    # Distributed
    #

    DISTRIBUTED = 1 << 16

    CLUSTER = 1 << 17

    FEDERATION = 1 << 18

    #
    # Everything
    #

    ALL = (
        SAMPLING
        | PROCESSING
        | EXPORTING
        | CONTEXT
        | PIPELINES
        | FILTERING
        | CACHING
        | HISTORY
        | CALLBACKS
        | HOOKS
        | EVENTS
        | TAGS
        | DIAGNOSTICS
        | METRICS
        | SNAPSHOT
        | SERIALIZATION
        | DISTRIBUTED
        | CLUSTER
        | FEDERATION
    )


# ------------------------------------------------------------------------------


class ComponentType(str, Enum):
    """
    Registered component type.
    """

    SAMPLER = "sampler"

    PROCESSOR = "processor"

    EXPORTER = "exporter"

    TRACER = "tracer"

    PIPELINE = "pipeline"

    CONTEXT = "context"

    CUSTOM = "custom"


# ------------------------------------------------------------------------------


class EventType(str, Enum):
    """
    Runtime event type.
    """

    INITIALIZE = "initialize"

    START_TRACE = "start_trace"

    FINISH_TRACE = "finish_trace"

    START_SPAN = "start_span"

    FINISH_SPAN = "finish_span"

    PROCESS = "process"

    EXPORT = "export"

    FLUSH = "flush"

    RESET = "reset"

    CLEAR = "clear"

    SNAPSHOT = "snapshot"

    RESTORE = "restore"

    CLOSE = "close"


# ------------------------------------------------------------------------------


class SerializationFormat(str, Enum):
    """
    Supported serialization formats.
    """

    DICT = "dict"

    JSON = "json"

    BINARY = "binary"

    CUSTOM = "custom"


# ------------------------------------------------------------------------------


class HookType(str, Enum):
    """
    Runtime hook names.
    """

    BEFORE_PROCESS = "before_process"

    AFTER_PROCESS = "after_process"

    BEFORE_FLUSH = "before_flush"

    AFTER_FLUSH = "after_flush"

    BEFORE_TRACE = "before_trace"

    AFTER_TRACE = "after_trace"

    BEFORE_SPAN = "before_span"

    AFTER_SPAN = "after_span"


# ==============================================================================
# End Part 1.4
# ==============================================================================
# ==============================================================================
# Part 1.5
# Dataclasses
# ==============================================================================


@dataclass(slots=True)
class ManagerStatistics:
    """
    Runtime statistics for TraceManager.

    Updated continuously while the manager is running.
    """

    # ------------------------------------------------------------------
    # Trace Statistics
    # ------------------------------------------------------------------

    trace_count: int = 0

    active_trace_count: int = 0

    created_trace_count: int = 0

    finished_trace_count: int = 0

    peak_trace_count: int = 0


    # ------------------------------------------------------------------
    # Span Statistics
    # ------------------------------------------------------------------

    span_count: int = 0

    active_span_count: int = 0

    created_span_count: int = 0

    finished_span_count: int = 0

    peak_span_count: int = 0


    # ------------------------------------------------------------------
    # Components
    # ------------------------------------------------------------------

    processor_count: int = 0

    exporter_count: int = 0

    tracer_count: int = 0

    pipeline_count: int = 0


    # ------------------------------------------------------------------
    # Runtime
    # ------------------------------------------------------------------

    process_count: int = 0

    flush_count: int = 0

    reset_count: int = 0

    clear_count: int = 0

    optimize_count: int = 0

    cleanup_count: int = 0

    snapshot_count: int = 0

    restore_count: int = 0

    validation_count: int = 0


    # ------------------------------------------------------------------
    # Success / Failure
    # ------------------------------------------------------------------

    success_count: int = 0

    failure_count: int = 0

    dropped_count: int = 0

    warning_count: int = 0

    error_count: int = 0


    # ------------------------------------------------------------------
    # Hooks
    # ------------------------------------------------------------------

    callback_count: int = 0

    hook_count: int = 0

    filter_count: int = 0


    # ------------------------------------------------------------------
    # Timing
    # ------------------------------------------------------------------

    created_at: float = field(
        default_factory=time.time
    )

    updated_at: float = field(
        default_factory=time.time
    )

    last_activity: float = field(
        default_factory=time.time
    )


    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def touch(self) -> None:
        """
        Update activity timestamp.
        """

        self.updated_at = time.time()

        self.last_activity = self.updated_at


    def reset(self) -> None:
        """
        Reset runtime counters.
        """

        now = time.time()

        created = self.created_at

        self.__dict__.update(
            ManagerStatistics().__dict__
        )

        self.created_at = created

        self.updated_at = now

        self.last_activity = now


    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize statistics.
        """

        return asdict(self)


# ==============================================================================
# Snapshot
# ==============================================================================


@dataclass(slots=True)
class ManagerSnapshot:
    """
    Serializable runtime snapshot.
    """

    identity: Dict[str, Any]

    configuration: Dict[str, Any]

    runtime: Dict[str, Any]

    statistics: Dict[str, Any]

    metadata: Dict[str, Any]

    tags: List[str]

    components: Dict[str, Any]

    created_at: float = field(
        default_factory=time.time
    )


    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize snapshot.
        """

        return asdict(self)


# ==============================================================================
# Report
# ==============================================================================


@dataclass(slots=True)
class ManagerReport:
    """
    High-level runtime report.
    """

    name: str

    version: str

    state: str

    enabled: bool


    # ------------------------------------------------------------------
    # Components
    # ------------------------------------------------------------------

    processors: int

    exporters: int

    tracers: int

    pipelines: int


    # ------------------------------------------------------------------
    # Runtime
    # ------------------------------------------------------------------

    traces: int

    spans: int

    success_rate: float

    failure_rate: float

    uptime: float


    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    failures: int = 0

    dropped: int = 0

    warnings: int = 0


    current_trace: Optional[str] = None

    current_span: Optional[str] = None


    processor_names: List[str] = field(
        default_factory=list
    )

    exporter_names: List[str] = field(
        default_factory=list
    )

    tracer_names: List[str] = field(
        default_factory=list
    )

    pipeline_names: List[str] = field(
        default_factory=list
    )


    metadata: TraceMetadata = field(
        default_factory=dict
    )

    generated_at: float = field(
        default_factory=time.time
    )


    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize report.
        """

        return asdict(self)


# ==============================================================================
# End Part 1.5
# ==============================================================================
# ==============================================================================
# Part 1.6
# Public API
# ==============================================================================

__all__ = [

    # --------------------------------------------------------------------------
    # Constants
    # --------------------------------------------------------------------------

    "MANAGER_NAME",
    "MANAGER_DESCRIPTION",
    "MANAGER_VERSION",
    "DEFAULT_ENCODING",
    "DEFAULT_HISTORY_LIMIT",
    "DEFAULT_TIMEOUT",
    "DEFAULT_MAX_PROCESSORS",
    "DEFAULT_MAX_EXPORTERS",
    "DEFAULT_MAX_TRACERS",
    "DEFAULT_MAX_PIPELINES",
    "DEFAULT_AUTO_INITIALIZE",
    "DEFAULT_AUTO_FLUSH",
    "DEFAULT_ENABLED",
    "DEFAULT_CACHE_SIZE",

    # --------------------------------------------------------------------------
    # Type Aliases
    # --------------------------------------------------------------------------

    "TraceRecord",
    "TraceData",
    "TraceMetadata",
    "TraceOptions",
    "TraceCache",
    "TraceHistory",
    "TraceHook",
    "TraceCallback",
    "TraceFilter",
    "TraceEvent",
    "ComponentMap",
    "ProcessorMap",
    "ExporterMap",
    "TracerMap",
    "PipelineMap",
    "ManagerMetadata",
    "ManagerContext",
    "ManagerOptions",

    # --------------------------------------------------------------------------
    # Exceptions
    # --------------------------------------------------------------------------

    "TraceManagerError",
    "ManagerConfigurationError",
    "ManagerValidationError",
    "ManagerInitializationError",
    "ManagerRuntimeError",
    "ManagerStateError",
    "ManagerTimeoutError",
    "ManagerClosedError",
    "ManagerFrozenError",
    "ManagerDisabledError",

    "ComponentError",
    "ComponentNotFoundError",
    "DuplicateComponentError",
    "ComponentRegistrationError",
    "ComponentRemovalError",

    "ProcessorError",
    "ProcessorNotFoundError",

    "ExporterError",
    "ExporterNotFoundError",

    "TracerError",
    "TracerNotFoundError",

    "PipelineError",
    "PipelineNotFoundError",

    "TraceError",
    "TraceNotFoundError",
    "ActiveTraceError",

    "SpanError",
    "SpanNotFoundError",
    "ActiveSpanError",

    "ContextError",

    "SerializationError",
    "DeserializationError",
    "SnapshotError",
    "RestoreError",

    "CallbackError",
    "HookError",
    "FilterError",

    # --------------------------------------------------------------------------
    # Enums
    # --------------------------------------------------------------------------

    "ManagerType",
    "ManagerState",
    "ManagerMode",
    "ManagerHealth",
    "ManagerCapability",
    "ComponentType",
    "EventType",
    "SerializationFormat",
    "HookType",

    # --------------------------------------------------------------------------
    # Dataclasses
    # --------------------------------------------------------------------------

    "ManagerStatistics",
    "ManagerSnapshot",
    "ManagerReport",

    # --------------------------------------------------------------------------
    # Main Class
    # --------------------------------------------------------------------------

    "TraceManager",
]


# ==============================================================================
# End Part 1
# Foundation Completed
# ==============================================================================
#
# Included
#
#   • Header
#   • Imports
#   • Constants
#   • Type Aliases
#   • Exceptions
#   • Enums
#   • Dataclasses
#   • Public API (__all__)
#
# Next
#
#   Part 2. Constructor
#
#       • __init__()
#       • Runtime initialization
#       • Component initialization
#       • Statistics initialization
#       • Cache / History
#       • Current Trace / Current Span
#       • Lock
#
# ==============================================================================
# ==============================================================================
# Part 2.1
# TraceManager Declaration
# ==============================================================================


class TraceManager:
    """
    SciOS-NG Runtime Trace Manager.

    TraceManager is the central orchestration component of the
    Runtime Observability tracing subsystem.

    Responsibilities
    ----------------
    • Manage trace lifecycle.
    • Manage span lifecycle.
    • Coordinate TraceSampler.
    • Coordinate TraceProcessor.
    • Manage TraceContext.
    • Register processors.
    • Register exporters.
    • Register tracers.
    • Register processing pipelines.
    • Dispatch runtime events.
    • Execute callbacks and hooks.
    • Maintain runtime statistics.
    • Collect diagnostics.
    • Create runtime snapshots.
    • Serialize runtime state.

    Thread Safety
    -------------
    All public operations are thread-safe.

    Notes
    -----
    A TraceManager instance owns the runtime tracing environment.
    Multiple TraceManager instances may coexist independently.
    """

    # ==========================================================================
    # Part 2.1
    # Constructor
    # ==========================================================================

    def __init__(
        self,
        *,
        # ------------------------------------------------------------------
        # Identity
        # ------------------------------------------------------------------
        name: str = MANAGER_NAME,
        description: str = MANAGER_DESCRIPTION,

        # ------------------------------------------------------------------
        # Configuration
        # ------------------------------------------------------------------
        manager_type: ManagerType = ManagerType.STANDARD,
        mode: ManagerMode = ManagerMode.SYNCHRONOUS,

        # ------------------------------------------------------------------
        # Core Components
        # ------------------------------------------------------------------
        sampler: Optional[TraceSampler] = None,
        processor: Optional[TraceProcessor] = None,
        context: Optional[TraceContext] = None,

        # ------------------------------------------------------------------
        # Runtime Configuration
        # ------------------------------------------------------------------
        enabled: bool = DEFAULT_ENABLED,
        auto_initialize: bool = DEFAULT_AUTO_INITIALIZE,
        auto_flush: bool = DEFAULT_AUTO_FLUSH,

        history_limit: int = DEFAULT_HISTORY_LIMIT,
        timeout: float = DEFAULT_TIMEOUT,
        encoding: str = DEFAULT_ENCODING,

        options: Optional[ManagerOptions] = None,
        metadata: Optional[ManagerMetadata] = None,
    ) -> None:
        """
        Initialize a TraceManager.

        Parameters
        ----------
        name:
            Human-readable manager name.

        description:
            Optional manager description.

        manager_type:
            Manager implementation type.

        mode:
            Runtime execution mode.

        sampler:
            Trace sampler instance.

        processor:
            Default trace processor.

        context:
            Root trace context.

        enabled:
            Enable manager immediately after creation.

        auto_initialize:
            Automatically initialize runtime.

        auto_flush:
            Automatically flush processors/exporters.

        history_limit:
            Maximum history records retained.

        timeout:
            Default runtime timeout in seconds.

        encoding:
            Default serialization encoding.

        options:
            Additional runtime configuration.

        metadata:
            User-defined metadata attached to manager.
        """

        # Part 2.2
        # Synchronization + Identity
        ...
        # ==========================================================================
        # Part 2.2
        # Synchronization
        # ==========================================================================

        self._lock: RLock = RLock()

        # ==========================================================================
        # Identity
        # ==========================================================================

        # ------------------------------------------------------------------
        # UUID
        # ------------------------------------------------------------------

        self._uuid: uuid.UUID = uuid.uuid4()

        self._id: str = self._uuid.hex

        # ------------------------------------------------------------------
        # Name
        # ------------------------------------------------------------------

        self._name: str = str(name).strip()

        if not self._name:

            self._name = MANAGER_NAME

        # ------------------------------------------------------------------
        # Description
        # ------------------------------------------------------------------

        self._description: str = str(description).strip()

        if not self._description:

            self._description = MANAGER_DESCRIPTION

        # ------------------------------------------------------------------
        # Version
        # ------------------------------------------------------------------

        self._version: str = MANAGER_VERSION

        # ------------------------------------------------------------------
        # Identity Metadata
        # ------------------------------------------------------------------

        self._qualified_name: str = (
            f"{self.__class__.__module__}."
            f"{self.__class__.__qualname__}"
        )

        self._display_name: str = self._name

        self._instance_name: str = (
            f"{self._name}-{self._id[:8]}"
        )

        # ------------------------------------------------------------------
        # Creation Timestamp
        # ------------------------------------------------------------------

        self._created_at: float = time.time()

        self._updated_at: float = self._created_at

        self._last_activity: float = self._created_at
        # ==========================================================================
        # Part 2.3
        # Configuration
        # ==========================================================================

        # ------------------------------------------------------------------
        # Manager Type
        # ------------------------------------------------------------------

        self._manager_type: ManagerType = (
            ManagerType(manager_type)
        )

        # ------------------------------------------------------------------
        # Execution Mode
        # ------------------------------------------------------------------

        self._mode: ManagerMode = (
            ManagerMode(mode)
        )

        # ------------------------------------------------------------------
        # Enabled
        # ------------------------------------------------------------------

        self._enabled: bool = bool(
            enabled
        )

        # ------------------------------------------------------------------
        # Auto Initialize
        # ------------------------------------------------------------------

        self._auto_initialize: bool = bool(
            auto_initialize
        )

        # ------------------------------------------------------------------
        # Auto Flush
        # ------------------------------------------------------------------

        self._auto_flush: bool = bool(
            auto_flush
        )

        # ------------------------------------------------------------------
        # History Limit
        # ------------------------------------------------------------------

        self._history_limit: int = int(
            history_limit
        )

        if self._history_limit <= 0:

            self._history_limit = (
                DEFAULT_HISTORY_LIMIT
            )

        # ------------------------------------------------------------------
        # Timeout
        # ------------------------------------------------------------------

        self._timeout: float = float(
            timeout
        )

        if self._timeout <= 0.0:

            self._timeout = (
                DEFAULT_TIMEOUT
            )

        # ------------------------------------------------------------------
        # Encoding
        # ------------------------------------------------------------------

        self._encoding: str = str(
            encoding
        ).strip()

        if not self._encoding:

            self._encoding = (
                DEFAULT_ENCODING
            )

        # ------------------------------------------------------------------
        # Options
        # ------------------------------------------------------------------

        self._options: ManagerOptions = (
            copy.deepcopy(
                options or {}
            )
        )

        # ------------------------------------------------------------------
        # Metadata
        # ------------------------------------------------------------------

        self._metadata: ManagerMetadata = (
            copy.deepcopy(
                metadata or {}
            )
        )

        # ------------------------------------------------------------------
        # Runtime Configuration Flags
        # ------------------------------------------------------------------

        self._configuration: Dict[str, Any] = {

            "manager_type":
                self._manager_type,

            "mode":
                self._mode,

            "enabled":
                self._enabled,

            "auto_initialize":
                self._auto_initialize,

            "auto_flush":
                self._auto_flush,

            "history_limit":
                self._history_limit,

            "timeout":
                self._timeout,

            "encoding":
                self._encoding,

        }
        
        # ==========================================================================
        # Part 2.4
        # Runtime Components
        # ==========================================================================

        # ------------------------------------------------------------------
        # Core Components
        # ------------------------------------------------------------------

        self._sampler: TraceSampler = (
            sampler
            if sampler is not None
            else TraceSampler()
        )

        self._processor: TraceProcessor = (
            processor
            if processor is not None
            else TraceProcessor()
        )

        self._context: TraceContext = (
            context
            if context is not None
            else TraceContext()
        )

        # ------------------------------------------------------------------
        # Registered Components
        # ------------------------------------------------------------------

        self._processors: ProcessorMap = {}

        self._exporters: ExporterMap = {}

        self._tracers: TracerMap = {}

        self._pipelines: PipelineMap = {}

        # ------------------------------------------------------------------
        # Active Runtime Objects
        # ------------------------------------------------------------------

        self._current_trace: Optional[Any] = None

        self._current_span: Optional[Any] = None

        self._active_traces: Dict[str, Any] = {}

        self._active_spans: Dict[str, Any] = {}

        # ------------------------------------------------------------------
        # Component Counters
        # ------------------------------------------------------------------

        self._processor_count: int = 0

        self._exporter_count: int = 0

        self._tracer_count: int = 0

        self._pipeline_count: int = 0

        self._trace_count: int = 0

        self._completed_trace_count: int = 0

        self._span_count: int = 0
        # ------------------------------------------------------------------
        # Component Limits
        # ------------------------------------------------------------------

        self._maximum_processors: int = (
            DEFAULT_MAX_PROCESSORS
        )

        self._maximum_exporters: int = (
            DEFAULT_MAX_EXPORTERS
        )

        self._maximum_tracers: int = (
            DEFAULT_MAX_TRACERS
        )

        self._maximum_pipelines: int = (
            DEFAULT_MAX_PIPELINES
        )

        # ------------------------------------------------------------------
        # Default Component Registration
        # ------------------------------------------------------------------

        self._processors["default"] = (
            self._processor
        )

        self._processor_count = len(
            self._processors
        )

        # ------------------------------------------------------------------
        # Default Tracer Bootstrap
        # ------------------------------------------------------------------

        try:

            from .trace import Tracer

            tracer = Tracer(
                name="default",
            )

            try:

                if hasattr(
                    tracer,
                    "initialize",
                ):
                    tracer.initialize()

                if hasattr(
                    tracer,
                    "start",
                ):
                    tracer.start()

            except Exception:
                pass

            self._tracers["default"] = tracer

            self._tracer_count = len(
                self._tracers
            )

        except Exception as exc:

            raise ManagerInitializationError(
                "Failed to initialize default tracer."
            ) from exc
        # ------------------------------------------------------------------
        # Component Registry
        # ------------------------------------------------------------------

        self._components: ComponentMap = {

            "sampler":
                self._sampler,

            "processor":
                self._processor,

            "context":
                self._context,

            "processors":
                self._processors,

            "exporters":
                self._exporters,

            "tracers":
                self._tracers,

            "pipelines":
                self._pipelines,

        }
        
        # ==========================================================================
        # Part 2.5
        # Runtime State
        # ==========================================================================

        # ------------------------------------------------------------------
        # Lifecycle State
        # ------------------------------------------------------------------

        self._state: ManagerState = (
            ManagerState.CREATED
        )

        # ------------------------------------------------------------------
        # Runtime Flags
        # ------------------------------------------------------------------

        self._initialized: bool = False

        self._running: bool = False

        self._active: bool = False

        self._frozen: bool = False

        self._closed: bool = False

        self._failed: bool = False

        self._healthy: bool = True

        # ------------------------------------------------------------------
        # Activity Flags
        # ------------------------------------------------------------------

        self._busy: bool = False

        self._processing: bool = False

        self._flushing: bool = False

        self._restoring: bool = False

        self._shutdown_requested: bool = False

        # ------------------------------------------------------------------
        # Runtime Timestamps
        # ------------------------------------------------------------------

        now = time.time()

        self._created_at: float = now

        self._updated_at: float = now

        self._last_activity: float = now

        self._initialized_at: Optional[float] = None

        self._started_at: Optional[float] = None

        self._stopped_at: Optional[float] = None

        self._paused_at: Optional[float] = None

        self._resumed_at: Optional[float] = None

        self._frozen_at: Optional[float] = None

        self._unfrozen_at: Optional[float] = None

        self._closed_at: Optional[float] = None

        self._failed_at: Optional[float] = None

        self._last_flush_at: Optional[float] = None

        self._last_reset_at: Optional[float] = None

        self._last_snapshot_at: Optional[float] = None

        self._last_restore_at: Optional[float] = None

        self._last_validation_at: Optional[float] = None

        self._last_cleanup_at: Optional[float] = None

        self._last_compaction_at: Optional[float] = None

        self._last_optimization_at: Optional[float] = None

        # ------------------------------------------------------------------
        # Runtime Versioning
        # ------------------------------------------------------------------

        self._generation: int = 0

        self._revision: int = 0

        self._epoch: int = 0

        # ------------------------------------------------------------------
        # Runtime Status Cache
        # ------------------------------------------------------------------

        self._status: TraceStatus = TraceStatus()

        self._status_message: str = ""

        self._last_error: Optional[BaseException] = None

        self._last_exception: Optional[BaseException] = None
        # ======================================================================
        # Part 2.6 — Statistics + Runtime Storage
        # ======================================================================

        # ----------------------------------------------------------------------
        # Runtime Statistics
        # ----------------------------------------------------------------------

        self._statistics: ManagerStatistics = (
            ManagerStatistics()
        )

        self._statistics.processor_count = (
            len(self._processors)
        )

        self._statistics.exporter_count = (
            len(self._exporters)
        )

        self._statistics.tracer_count = (
            len(self._tracers)
        )

        self._statistics.pipeline_count = (
            len(self._pipelines)
        )

        self._statistics.updated_at = (
            now
        )

        self._success_count: int = 0

        self._failure_count: int = 0

        self._dropped_count: int = 0

        self._flush_count: int = 0

        self._reset_count: int = 0

        self._validation_count: int = 0

        self._callback_count: int = 0

        self._hook_count: int = 0


        # ----------------------------------------------------------------------
        # Runtime Cache
        # ----------------------------------------------------------------------

        self._cache: TraceCache = {}

        self._cache_limit: int = (
            DEFAULT_CACHE_SIZE
        )


        # ----------------------------------------------------------------------
        # Runtime History
        # ----------------------------------------------------------------------

        self._history: TraceHistory = deque(
            maxlen=self._history_limit
        )


        # ----------------------------------------------------------------------
        # Callback Registry
        # ----------------------------------------------------------------------

        self._callbacks: List[
            TraceCallback
        ] = []


        # ----------------------------------------------------------------------
        # Hook Registry
        # ----------------------------------------------------------------------

        self._hooks: Dict[
            str,
            List[TraceHook],
        ] = defaultdict(list)


        # ----------------------------------------------------------------------
        # Runtime Filters
        # ----------------------------------------------------------------------

        self._filters: List[
            TraceFilter
        ] = []


        # ----------------------------------------------------------------------
        # Current Runtime Objects
        # ----------------------------------------------------------------------

        self._current_trace: Optional[Any] = (
            None
        )

        self._current_span: Optional[Any] = (
            None
        )


        # ----------------------------------------------------------------------
        # Active Runtime Objects
        # ----------------------------------------------------------------------

        self._active_traces: Dict[
            str,
            Any,
        ] = {}

        self._active_spans: Dict[
            str,
            Any,
        ] = {}


        # ----------------------------------------------------------------------
        # Internal Event Queue
        # ----------------------------------------------------------------------

        self._event_queue: Deque[
            TraceEvent
        ] = deque()


        # ----------------------------------------------------------------------
        # Runtime Metadata
        # ----------------------------------------------------------------------

        self._metadata: TraceMetadata = {}

        self._context_data: ManagerContext = {}

        self._tags: List[str] = []


        # ----------------------------------------------------------------------
        # Capability Flags
        # ----------------------------------------------------------------------

        self._capabilities: ManagerCapability = (
            ManagerCapability.ALL
        )


        # ----------------------------------------------------------------------
        # Auto Initialization
        # ----------------------------------------------------------------------

        if self._auto_initialize:

            self._initialized = True

            self._state = (
                ManagerState.INITIALIZED
            )
        # ======================================================================
        # Part 2.7 — Capability Detection + Auto Initialization
        # ======================================================================

        # ----------------------------------------------------------------------
        # Capability Detection
        # ----------------------------------------------------------------------

        self._capabilities: ManagerCapability = (
            ManagerCapability.NONE
        )

        # Core runtime
        self._capabilities |= (
            ManagerCapability.SAMPLING
        )

        self._capabilities |= (
            ManagerCapability.PROCESSING
        )

        self._capabilities |= (
            ManagerCapability.CACHING
        )

        self._capabilities |= (
            ManagerCapability.CALLBACKS
        )

        self._capabilities |= (
            ManagerCapability.HOOKS
        )

        self._capabilities |= (
            ManagerCapability.DIAGNOSTICS
        )

        self._capabilities |= (
            ManagerCapability.SERIALIZATION
        )

        self._capabilities |= (
            ManagerCapability.SNAPSHOT
        )


        # ----------------------------------------------------------------------
        # Optional Components
        # ----------------------------------------------------------------------

        if self._processors:

            self._capabilities |= (
                ManagerCapability.PROCESSING
            )

        if self._exporters:

            self._capabilities |= (
                ManagerCapability.EXPORTING
            )

        if self._pipelines:

            self._capabilities |= (
                ManagerCapability.PIPELINES
            )

        if self._filters:

            self._capabilities |= (
                ManagerCapability.FILTERING
            )

        if (
            self._manager_type
            == ManagerType.DISTRIBUTED
        ):

            self._capabilities |= (
                ManagerCapability.DISTRIBUTED
            )


        # ----------------------------------------------------------------------
        # Auto Initialization
        # ----------------------------------------------------------------------

        if self._auto_initialize:

            self.initialize()


    # ==========================================================================
    # End Part 2 — Constructor
    # ==========================================================================

    # ==========================================================================
    # Part 3.1 — Identity Properties
    # ==========================================================================

    @property
    def id(self) -> str:
        """
        Unique manager identifier.
        """

        return self._id


    @property
    def uuid(self) -> uuid.UUID:
        """
        UUID object of this manager.
        """

        return self._uuid


    @property
    def name(self) -> str:
        """
        Human-readable manager name.
        """

        return self._name


    @name.setter
    def name(
        self,
        value: str,
    ) -> None:
        """
        Update manager name.
        """

        with self._lock:

            self._name = str(value)

            self._updated_at = time.time()

            self._statistics.updated_at = (
                self._updated_at
            )


    @property
    def description(self) -> str:
        """
        Manager description.
        """

        return self._description


    @description.setter
    def description(
        self,
        value: str,
    ) -> None:
        """
        Update manager description.
        """

        with self._lock:

            self._description = str(value)

            self._updated_at = time.time()

            self._statistics.updated_at = (
                self._updated_at
            )


    @property
    def version(self) -> str:
        """
        Manager implementation version.
        """

        return self._version
    # ==========================================================================
    # Part 3.2 — Configuration Properties
    # ==========================================================================

    @property
    def manager_type(self) -> ManagerType:
        """
        Manager implementation type.
        """

        return self._manager_type


    @property
    def mode(self) -> ManagerMode:
        """
        Runtime execution mode.
        """

        return self._mode


    @property
    def sampler(self) -> TraceSampler:
        """
        Default trace sampler.
        """

        return self._sampler


    @property
    def processor(self) -> TraceProcessor:
        """
        Default trace processor.
        """

        return self._processor


    @property
    def context(self) -> TraceContext:
        """
        Runtime trace context.
        """

        return self._context


    @property
    def enabled(self) -> bool:
        """
        Whether manager is enabled.
        """

        return self._enabled


    @enabled.setter
    def enabled(
        self,
        value: bool,
    ) -> None:
        """
        Enable or disable manager.
        """

        with self._lock:

            self._enabled = bool(value)

            self._updated_at = time.time()

            self._statistics.updated_at = (
                self._updated_at
            )


    @property
    def auto_initialize(self) -> bool:
        """
        Auto initialization flag.
        """

        return self._auto_initialize


    @auto_initialize.setter
    def auto_initialize(
        self,
        value: bool,
    ) -> None:
        """
        Configure automatic initialization.
        """

        with self._lock:

            self._auto_initialize = bool(
                value
            )

            self._updated_at = time.time()

            self._statistics.updated_at = (
                self._updated_at
            )


    @property
    def auto_flush(self) -> bool:
        """
        Automatic flush flag.
        """

        return self._auto_flush


    @auto_flush.setter
    def auto_flush(
        self,
        value: bool,
    ) -> None:
        """
        Configure automatic flushing.
        """

        with self._lock:

            self._auto_flush = bool(
                value
            )

            self._updated_at = time.time()

            self._statistics.updated_at = (
                self._updated_at
            )


    @property
    def history_limit(self) -> int:
        """
        Maximum history size.
        """

        return self._history_limit


    @history_limit.setter
    def history_limit(
        self,
        value: int,
    ) -> None:
        """
        Update history limit.
        """

        value = int(value)

        if value <= 0:

            raise ValueError(
                "history_limit must be > 0."
            )

        with self._lock:

            self._history_limit = value

            self._history = deque(
                self._history,
                maxlen=value,
            )

            self._updated_at = time.time()

            self._statistics.updated_at = (
                self._updated_at
            )


    @property
    def timeout(self) -> float:
        """
        Runtime timeout (seconds).
        """

        return self._timeout


    @timeout.setter
    def timeout(
        self,
        value: float,
    ) -> None:
        """
        Update timeout.
        """

        value = float(value)

        if value < 0.0:

            raise ValueError(
                "timeout must be >= 0."
            )

        with self._lock:

            self._timeout = value

            self._updated_at = time.time()

            self._statistics.updated_at = (
                self._updated_at
            )


    @property
    def encoding(self) -> str:
        """
        Default text encoding.
        """

        return self._encoding


    @encoding.setter
    def encoding(
        self,
        value: str,
    ) -> None:
        """
        Update encoding.
        """

        with self._lock:

            self._encoding = str(value)

            self._updated_at = time.time()

            self._statistics.updated_at = (
                self._updated_at
            )


    @property
    def options(self) -> TraceOptions:
        """
        Runtime configuration options.
        """

        return copy.deepcopy(
            self._options
        )
    # ==========================================================================
    # Part 3.3 — Runtime State Properties
    # ==========================================================================


    @property
    def state(self) -> ManagerState:
        """
        Current runtime state.

        Returns
        -------
        ManagerState
            Current manager lifecycle state.
        """

        with self._lock:

            return self._state



    @property
    def initialized(self) -> bool:
        """
        Whether the manager has been initialized.

        Returns
        -------
        bool
            True if initialization completed.
        """

        with self._lock:

            return bool(
                self._initialized
            )



    @property
    def running(self) -> bool:
        """
        Whether the manager is currently running.

        Returns
        -------
        bool
            True if runtime execution is active.
        """

        with self._lock:

            return bool(
                self._running
            )



    @property
    def active(self) -> bool:
        """
        Whether the manager is active.

        Returns
        -------
        bool
            True if manager accepts operations.
        """

        with self._lock:

            return bool(
                self._active
            )



    @property
    def frozen(self) -> bool:
        """
        Whether the manager is frozen.

        Frozen managers preserve state
        but reject mutations.

        Returns
        -------
        bool
            True if frozen.
        """

        with self._lock:

            return bool(
                self._frozen
            )



    @property
    def closed(self) -> bool:
        """
        Whether the manager has been closed.

        Returns
        -------
        bool
            True after shutdown/close.
        """

        with self._lock:

            return bool(
                self._closed
            )



    @property
    def created_at(self) -> float:
        """
        Manager creation timestamp.

        Returns
        -------
        float
            Unix timestamp.
        """

        with self._lock:

            return float(
                self._created_at
            )



    @property
    def updated_at(self) -> float:
        """
        Last state update timestamp.

        Returns
        -------
        float
            Unix timestamp.
        """

        with self._lock:

            return float(
                self._updated_at
            )



    @property
    def last_activity(self) -> float:
        """
        Timestamp of latest runtime activity.

        Returns
        -------
        float
            Unix timestamp.
        """

        with self._lock:

            return float(
                self._last_activity
            )



    @property
    def uptime(self) -> float:
        """
        Runtime uptime in seconds.

        Notes
        -----
        Uses current wall clock time while active.
        After closing, uptime is calculated
        from final update timestamp.

        Returns
        -------
        float
            Non-negative uptime duration.
        """

        with self._lock:

            now = (
                self._updated_at
                if self._closed
                else time.time()
            )


            return max(
                0.0,
                float(now)
                -
                float(self._created_at),
            )
    # ==========================================================================
    # Part 3.4 — Statistics Properties
    # ==========================================================================


    @property
    def statistics(self) -> ManagerStatistics:
        """
        Runtime manager statistics snapshot.
        """

        with self._lock:
            return copy.deepcopy(
                self._statistics
            )



    @property
    def trace_count(self) -> int:
        """
        Number of managed traces.
        """

        with self._lock:
            return self._statistics.trace_count



    @property
    def span_count(self) -> int:
        """
        Number of managed spans.
        """

        with self._lock:
            return self._statistics.span_count



    @property
    def processor_count(self) -> int:
        """
        Number of registered processors.
        """

        with self._lock:
            return self._statistics.processor_count



    @property
    def exporter_count(self) -> int:
        """
        Number of registered exporters.
        """

        with self._lock:
            return self._statistics.exporter_count



    @property
    def tracer_count(self) -> int:
        """
        Number of registered tracers.
        """

        with self._lock:
            return self._statistics.tracer_count



    @property
    def pipeline_count(self) -> int:
        """
        Number of registered pipelines.
        """

        with self._lock:
            return self._statistics.pipeline_count



    @property
    def success_count(self) -> int:
        """
        Number of successful operations.
        """

        with self._lock:
            return self._statistics.success_count



    @property
    def failure_count(self) -> int:
        """
        Number of failed operations.
        """

        with self._lock:
            return self._statistics.failure_count



    @property
    def dropped_count(self) -> int:
        """
        Number of dropped traces/spans/events.
        """

        with self._lock:
            return self._statistics.dropped_count



    @property
    def success_rate(self) -> float:
        """
        Success ratio.

        Returns
        -------
        float
            Value in range [0.0, 1.0].
        """

        with self._lock:

            success = (
                self._statistics.success_count
            )

            failure = (
                self._statistics.failure_count
            )

            total = (
                success
                + failure
            )

            if total <= 0:
                return 1.0

            return min(
                1.0,
                max(
                    0.0,
                    success / total,
                ),
            )



    @property
    def failure_rate(self) -> float:
        """
        Failure ratio.

        Returns
        -------
        float
            Value in range [0.0, 1.0].
        """

        with self._lock:

            success = (
                self._statistics.success_count
            )

            failure = (
                self._statistics.failure_count
            )

            total = (
                success
                + failure
            )

            if total <= 0:
                return 0.0

            return min(
                1.0,
                max(
                    0.0,
                    failure / total,
                ),
            )
# ==========================================================================
# Part 3.5 — Runtime Storage Properties
# ==========================================================================

    @property
    def metadata(self) -> TraceMetadata:
        """
        Manager metadata.
        """

        return copy.deepcopy(
            self._metadata
        )


    @property
    def tags(self) -> List[str]:
        """
        Manager tags.
        """

        return list(
            self._tags
        )


    @property
    def context_data(self) -> ManagerContext:
        """
        Runtime context data.
        """

        return copy.deepcopy(
            self._context_data
        )


    @property
    def history(self) -> TraceHistory:
        """
        Runtime history buffer.
        """

        return self._history


    @property
    def cache(self) -> TraceCache:
        """
        Runtime cache.
        """

        return self._cache


    @property
    def callbacks(self) -> List[TraceCallback]:
        """
        Registered callbacks.
        """

        return list(
            self._callbacks
        )


    @property
    def hooks(self) -> Dict[
        str,
        List[TraceHook],
    ]:
        """
        Registered hooks.
        """

        return {
            name: list(items)
            for name, items in self._hooks.items()
        }


    @property
    def filters(self) -> List[TraceFilter]:
        """
        Registered filters.
        """

        return list(
            self._filters
        )


    @property
    def current_trace(self) -> Optional[Any]:
        """
        Current active trace.
        """

        return self._current_trace


    @property
    def current_span(self) -> Optional[Any]:
        """
        Current active span.
        """

        return self._current_span


    @property
    def active_traces(self) -> Dict[
        str,
        Any,
    ]:
        """
        Active trace registry.
        """

        return dict(
            self._active_traces
        )


    @property
    def active_spans(self) -> Dict[
        str,
        Any,
    ]:
        """
        Active span registry.
        """

        return dict(
            self._active_spans
        )


    @property
    def capabilities(
        self,
    ) -> ManagerCapability:
        """
        Supported runtime capabilities.
        """

        return self._capabilities

# ==========================================================================
# Part 4. Lifecycle
# ==========================================================================

# ==========================================================================
# Part 4.0.1 — initialize()
# ==========================================================================

    def initialize(self) -> "TraceManager":
        """
        Initialize the TraceManager runtime.

        Returns
        -------
        TraceManager
            This manager.
        """

        with self._lock:

            if self._closed:
                raise ManagerClosedError(
                    "Cannot initialize a closed TraceManager."
                )

            if self._initialized:
                return self

            self._initialized = True
            self._active = True
            self._running = True

            self._state = (
                ManagerState.INITIALIZED
            )

            now = time.time()

            self._initialized_at = now
            self._updated_at = now
            self._last_activity = now

            self._generation += 1

            if hasattr(
                self._status,
                "state",
            ):
                try:
                    self._status._state = (
                        TraceStatusState.INITIALIZED
                    )
                except Exception:
                    pass

            return self
            

# ==========================================================================
# Part 4.0.2 — start()
# ==========================================================================

    def start(self) -> "TraceManager":
        """
        Start the TraceManager runtime.

        Returns
        -------
        TraceManager
            This manager.
        """

        with self._lock:

            if self._closed:
                raise ManagerClosedError(
                    "Cannot start a closed TraceManager."
                )

            if not self._initialized:
                self.initialize()

            if self._running:
                return self

            self._running = True
            self._active = True
            self._busy = False
            self._enabled = True

            self._state = (
                ManagerState.RUNNING
            )

            now = time.time()

            self._started_at = now
            self._updated_at = now
            self._last_activity = now

            self._revision += 1

            if hasattr(
                self._status,
                "_state",
            ):
                try:
                    self._status._state = (
                        TraceStatusState.RUNNING
                    )
                except Exception:
                    pass

            return self

# ==========================================================================
# Part 4.0.3 — stop()
# ==========================================================================

    def stop(self) -> "TraceManager":
        """
        Stop the TraceManager runtime.

        Returns
        -------
        TraceManager
            This manager.
        """

        with self._lock:

            if self._closed:
                raise ManagerClosedError(
                    "Cannot stop a closed TraceManager."
                )

            if not self._initialized:
                return self

            if not self._running:
                return self

            self._running = False
            self._busy = False
            self._processing = False
            self._active = False

            self._state = (
                ManagerState.STOPPED
            )

            now = time.time()

            self._stopped_at = now
            self._updated_at = now
            self._last_activity = now

            self._revision += 1

            if hasattr(
                self._status,
                "_state",
            ):
                try:
                    self._status._state = (
                        TraceStatusState.STOPPED
                    )
                except Exception:
                    pass

            return self

# ==========================================================================
# Part 4.0.4 — shutdown()
# ==========================================================================

    def shutdown(self) -> "TraceManager":
        """
        Shut down the TraceManager runtime.

        Returns
        -------
        TraceManager
            This manager.
        """

        with self._lock:

            if self._closed:
                return self

            if self._shutdown_requested:
                return self

            self._shutdown_requested = True

            if self._running:
                self.stop()

            if self._auto_flush:
                try:
                    self.flush()
                except Exception:
                    pass

            self._initialized = False
            self._active = False
            self._busy = False
            self._processing = False
            self._flushing = False

            self._state = (
                ManagerState.SHUTDOWN
            )

            now = time.time()

            self._updated_at = now
            self._last_activity = now
            self._stopped_at = now

            self._generation += 1

            if hasattr(
                self._status,
                "_state",
            ):
                try:
                    self._status._state = (
                        TraceStatusState.SHUTDOWN
                    )
                except Exception:
                    pass

            return self

# ==========================================================================
# Part 4.0.5 — close()
# ==========================================================================

    def close(self) -> "TraceManager":
        """
        Close the TraceManager.

        Returns
        -------
        TraceManager
            This manager.
        """

        with self._lock:

            if self._closed:
                return self

            if self._running:
                self.stop()

            if self._auto_flush:
                try:
                    self.flush()
                except Exception:
                    pass

            self._initialized = False
            self._active = False
            self._running = False
            self._busy = False
            self._processing = False
            self._flushing = False

            self._closed = True

            self._state = (
                ManagerState.CLOSED
            )

            now = time.time()

            self._closed_at = now
            self._updated_at = now
            self._last_activity = now

            self._generation += 1

            if hasattr(
                self._status,
                "_state",
            ):
                try:
                    self._status._state = (
                        TraceStatusState.CLOSED
                    )
                except Exception:
                    pass

            return self

# ==========================================================================
# Part 4.0.6 — freeze()
# ==========================================================================

    def freeze(self) -> "TraceManager":
        """
        Freeze the TraceManager runtime.

        A frozen manager keeps its current state but prevents
        runtime mutations until unfreeze() is called.

        Returns
        -------
        TraceManager
            This manager.
        """

        with self._lock:

            if self._closed:
                raise ManagerClosedError(
                    "Cannot freeze a closed TraceManager."
                )

            if self._frozen:
                return self

            self._frozen = True

            self._state = (
                ManagerState.FROZEN
            )

            now = time.time()

            self._frozen_at = now
            self._updated_at = now
            self._last_activity = now

            self._revision += 1

            if hasattr(
                self._status,
                "_state",
            ):
                try:
                    self._status._state = (
                        TraceStatusState.FROZEN
                    )
                except Exception:
                    pass

            return self

# ==========================================================================
# Part 4.0.7 — unfreeze()
# ==========================================================================

    def unfreeze(self) -> "TraceManager":
        """
        Unfreeze the TraceManager runtime.

        Restores normal runtime operations after freeze().

        Returns
        -------
        TraceManager
            This manager.
        """

        with self._lock:

            if self._closed:
                raise ManagerClosedError(
                    "Cannot unfreeze a closed TraceManager."
                )

            if not self._frozen:
                return self

            self._frozen = False

            if self._running:
                self._state = (
                    ManagerState.RUNNING
                )

            elif self._initialized:
                self._state = (
                    ManagerState.INITIALIZED
                )

            else:
                self._state = (
                    ManagerState.CREATED
                )

            now = time.time()

            self._unfrozen_at = now
            self._updated_at = now
            self._last_activity = now

            self._revision += 1

            if hasattr(
                self._status,
                "_state",
            ):
                try:
                    if self._running:
                        self._status._state = (
                            TraceStatusState.RUNNING
                        )

                    elif self._initialized:
                        self._status._state = (
                            TraceStatusState.INITIALIZED
                        )

                    else:
                        self._status._state = (
                            TraceStatusState.CREATED
                        )

                except Exception:
                    pass

            return self

# ==========================================================================
# Part 4.0.8 — restart()
# ==========================================================================

    def restart(self) -> "TraceManager":
        """
        Restart the TraceManager runtime.

        Stops the current runtime and starts it again while
        preserving registered components and configuration.

        Returns
        -------
        TraceManager
            This manager.
        """

        with self._lock:

            if self._closed:
                raise ManagerClosedError(
                    "Cannot restart a closed TraceManager."
                )

            if self._frozen:
                raise ManagerFrozenError(
                    "Cannot restart a frozen TraceManager."
                )

            if self._running:
                self.stop()

            if not self._initialized:
                self.initialize()

            self._running = True
            self._active = True
            self._busy = False
            self._processing = False
            self._flushing = False

            self._state = (
                ManagerState.RUNNING
            )

            now = time.time()

            self._started_at = now
            self._updated_at = now
            self._last_activity = now

            self._generation += 1
            self._revision += 1

            if hasattr(
                self._status,
                "_state",
            ):
                try:
                    self._status._state = (
                        TraceStatusState.RUNNING
                    )
                except Exception:
                    pass

            return self

# ==========================================================================
# Part 4.0.9 — reset()
# ==========================================================================

    def reset(self) -> "TraceManager":
        """
        Reset the TraceManager runtime state.

        Clears active runtime objects and counters while
        preserving configuration and registered components.

        Returns
        -------
        TraceManager
            This manager.
        """

        with self._lock:

            if self._closed:
                raise ManagerClosedError(
                    "Cannot reset a closed TraceManager."
                )

            if self._frozen:
                raise ManagerFrozenError(
                    "Cannot reset a frozen TraceManager."
                )

            # ------------------------------------------------------------------
            # Runtime Objects
            # ------------------------------------------------------------------

            self._current_trace = None
            self._current_span = None

            self._active_traces.clear()
            self._active_spans.clear()

            # ------------------------------------------------------------------
            # Runtime Flags
            # ------------------------------------------------------------------

            self._busy = False
            self._processing = False
            self._flushing = False
            self._restoring = False

            # ------------------------------------------------------------------
            # Counters
            # ------------------------------------------------------------------

            self._trace_count = 0
            self._span_count = 0

            # ------------------------------------------------------------------
            # Cache / History
            # ------------------------------------------------------------------

            try:
                self._cache.clear()
            except Exception:
                pass

            try:
                self._history.clear()
            except Exception:
                pass

            # ------------------------------------------------------------------
            # Runtime State
            # ------------------------------------------------------------------

            if self._initialized:

                self._state = (
                    ManagerState.INITIALIZED
                )

            else:

                self._state = (
                    ManagerState.CREATED
                )

            now = time.time()

            self._last_reset_at = now
            self._updated_at = now
            self._last_activity = now

            self._generation += 1
            self._revision += 1

            if hasattr(
                self._status,
                "_state",
            ):
                try:
                    if self._initialized:
                        self._status._state = (
                            TraceStatusState.INITIALIZED
                        )
                    else:
                        self._status._state = (
                            TraceStatusState.CREATED
                        )

                except Exception:
                    pass

            return self

# ==========================================================================
# Part 4.0.10 — activate()
# ==========================================================================

    def activate(self) -> "TraceManager":
        """
        Activate the TraceManager runtime.

        Enables runtime activity without changing
        initialization or registered components.

        Returns
        -------
        TraceManager
            This manager.
        """

        with self._lock:

            if self._closed:
                raise ManagerClosedError(
                    "Cannot activate a closed TraceManager."
                )

            if not self._initialized:
                self.initialize()

            self._active = True

            if self._running:
                self._state = (
                    ManagerState.RUNNING
                )

            else:
                self._state = (
                    ManagerState.ACTIVE
                )

            now = time.time()

            self._updated_at = now
            self._last_activity = now

            self._revision += 1

            if hasattr(
                self._status,
                "_state",
            ):
                try:
                    self._status._state = (
                        TraceStatusState.ACTIVE
                    )
                except Exception:
                    pass

            return self

# ==========================================================================
# Part 4.0.11 — deactivate()
# ==========================================================================

    def deactivate(self) -> "TraceManager":
        """
        Deactivate the TraceManager runtime.

        Disables active runtime operations while keeping
        the manager initialized.

        Returns
        -------
        TraceManager
            This manager.
        """

        with self._lock:

            if self._closed:
                raise ManagerClosedError(
                    "Cannot deactivate a closed TraceManager."
                )

            self._active = False

            if self._running:
                self._state = (
                    ManagerState.STOPPED
                )

            elif self._initialized:
                self._state = (
                    ManagerState.INITIALIZED
                )

            else:
                self._state = (
                    ManagerState.CREATED
                )

            now = time.time()

            self._updated_at = now
            self._last_activity = now

            self._revision += 1

            if hasattr(
                self._status,
                "_state",
            ):
                try:
                    if self._running:
                        self._status._state = (
                            TraceStatusState.STOPPED
                        )

                    elif self._initialized:
                        self._status._state = (
                            TraceStatusState.INITIALIZED
                        )

                    else:
                        self._status._state = (
                            TraceStatusState.CREATED
                        )

                except Exception:
                    pass

            return self

# ==========================================================================
# Part 4.0.12 — enable()
# ==========================================================================

    def enable(self) -> "TraceManager":
        """
        Enable the TraceManager.

        Allows runtime operations to be executed.

        Returns
        -------
        TraceManager
            This manager.
        """

        with self._lock:

            if self._closed:
                raise ManagerClosedError(
                    "Cannot enable a closed TraceManager."
                )

            self._enabled = True

            if self._initialized:

                if self._running:
                    self._state = (
                        ManagerState.RUNNING
                    )

                else:
                    self._state = (
                        ManagerState.INITIALIZED
                    )

            else:

                self._state = (
                    ManagerState.CREATED
                )

            now = time.time()

            self._updated_at = now
            self._last_activity = now

            self._revision += 1

            if hasattr(
                self._status,
                "_enabled",
            ):
                try:
                    self._status._enabled = True
                except Exception:
                    pass

            return self

# ==========================================================================
# Part 4.0.13 — disable()
# ==========================================================================

    def disable(self) -> "TraceManager":
        """
        Disable the TraceManager.

        Prevents runtime operations while keeping
        the manager instance available.

        Returns
        -------
        TraceManager
            This manager.
        """

        with self._lock:

            if self._closed:
                raise ManagerClosedError(
                    "Cannot disable a closed TraceManager."
                )

            self._enabled = False

            self._active = False

            if self._running:
                self._state = (
                    ManagerState.STOPPED
                )

            elif self._initialized:
                self._state = (
                    ManagerState.INITIALIZED
                )

            else:
                self._state = (
                    ManagerState.CREATED
                )

            now = time.time()

            self._updated_at = now
            self._last_activity = now

            self._revision += 1

            if hasattr(
                self._status,
                "_enabled",
            ):
                try:
                    self._status._enabled = False
                except Exception:
                    pass

            return self

# ==========================================================================
# Part 4.0.14 — pause()
# ==========================================================================

    def pause(self) -> "TraceManager":
        """
        Pause the TraceManager runtime.

        Temporarily suspends runtime processing while
        preserving current state and resources.

        Returns
        -------
        TraceManager
            This manager.
        """

        with self._lock:

            if self._closed:
                raise ManagerClosedError(
                    "Cannot pause a closed TraceManager."
                )

            if self._frozen:
                raise ManagerFrozenError(
                    "Cannot pause a frozen TraceManager."
                )

            if not self._initialized:
                self.initialize()

            self._active = False
            self._running = False

            self._state = (
                ManagerState.PAUSED
            )

            now = time.time()

            self._paused_at = now
            self._updated_at = now
            self._last_activity = now

            self._revision += 1

            if hasattr(
                self._status,
                "_state",
            ):
                try:
                    self._status._state = (
                        TraceStatusState.PAUSED
                    )
                except Exception:
                    pass

            return self

# ==========================================================================
# Part 4.0.15 — resume()
# ==========================================================================

    def resume(self) -> "TraceManager":
        """
        Resume the TraceManager runtime.

        Restores runtime activity after pause().

        Returns
        -------
        TraceManager
            This manager.
        """

        with self._lock:

            if self._closed:
                raise ManagerClosedError(
                    "Cannot resume a closed TraceManager."
                )

            if self._frozen:
                raise ManagerFrozenError(
                    "Cannot resume a frozen TraceManager."
                )

            if not self._initialized:
                self.initialize()

            self._active = True
            self._running = True

            self._state = (
                ManagerState.RUNNING
            )

            now = time.time()

            self._resumed_at = now
            self._started_at = now
            self._updated_at = now
            self._last_activity = now

            self._revision += 1

            if hasattr(
                self._status,
                "_state",
            ):
                try:
                    self._status._state = (
                        TraceStatusState.RUNNING
                    )
                except Exception:
                    pass

            return self

# ==========================================================================
# Part 4.0.16 — is_alive()
# ==========================================================================

    def is_alive(self) -> bool:
        """
        Check whether the TraceManager instance is alive.
        """

        with self._lock:

            return bool(
                self._initialized
                and not self._closed
            )                                                                                                      

# ==========================================================================
# Part 4.0.17 — count()
# ==========================================================================

    def count(self) -> int:
        """
        Return the number of registered traces.

        Returns
        -------
        int
            Number of active traces.
        """

        with self._lock:

            return self._trace_count

# ==========================================================================
# Part 4.1 — register_processor()
# ==========================================================================

    def register_processor(
        self,
        name: str,
        processor: TraceProcessor,
    ) -> "TraceManager":
        """
        Register a trace processor.

        Parameters
        ----------
        name:
            Unique processor name.

        processor:
            TraceProcessor instance.

        Returns
        -------
        TraceManager
            Returns self for fluent chaining.

        Raises
        ------
        ManagerClosedError
            If the manager has been closed.

        TypeError
            If processor is not a TraceProcessor.

        ValueError
            If name is empty.

        DuplicateComponentError
            If a processor with the same name
            already exists.
        """

        if self._closed:

            raise ManagerClosedError(
                "TraceManager is closed."
            )

        if not isinstance(
            name,
            str,
        ):

            raise TypeError(
                "name must be a string."
            )

        name = name.strip()

        if not name:

            raise ValueError(
                "Processor name cannot be empty."
            )

        if not isinstance(
            processor,
            TraceProcessor,
        ):

            raise TypeError(
                "processor must be a TraceProcessor."
            )

        with self._lock:

            if name in self._processors:

                raise DuplicateComponentError(
                    f"Processor '{name}' is already registered."
                )

            if (
                len(self._processors)
                >= DEFAULT_MAX_PROCESSORS
            ):

                raise ManagerConfigurationError(
                    "Maximum processor limit reached."
                )

            self._processors[name] = processor

            self._statistics.processor_count = (
                len(self._processors)
            )

            self._last_activity = time.time()

            self._updated_at = (
                self._last_activity
            )

            self._statistics.updated_at = (
                self._updated_at
            )

            self._statistics.success_count += 1

            try:

                self.notify_callbacks(
                    "processor_registered",
                    name=name,
                    processor=processor,
                )

            except Exception:

                pass

            try:

                self.emit_event(
                    "processor_registered",
                    {
                        "name": name,
                        "processor": processor,
                    },
                )

            except Exception:

                pass

        return self
    # ==========================================================================
    # Part 4.2 — unregister_processor()
    # ==========================================================================

    def unregister_processor(
        self,
        name: str,
    ) -> "TraceManager":
        """
        Unregister a trace processor.

        Parameters
        ----------
        name:
            Registered processor name.

        Returns
        -------
        TraceManager
            Returns self for fluent chaining.

        Raises
        ------
        ManagerClosedError
            If the manager has been closed.

        TypeError
            If name is not a string.

        ValueError
            If name is empty.

        ComponentNotFoundError
            If the processor does not exist.
        """

        if self._closed:

            raise ManagerClosedError(
                "TraceManager is closed."
            )

        if not isinstance(
            name,
            str,
        ):

            raise TypeError(
                "name must be a string."
            )

        name = name.strip()

        if not name:

            raise ValueError(
                "Processor name cannot be empty."
            )

        with self._lock:

            if name not in self._processors:

                raise ComponentNotFoundError(
                    f"Processor '{name}' is not registered."
                )

            processor = self._processors.pop(
                name
            )

            if (
                self._processor
                is processor
            ):

                self._processor = (
                    next(
                        iter(
                            self._processors.values()
                        ),
                        None,
                    )
                )

            self._statistics.processor_count = (
                len(self._processors)
            )

            self._last_activity = time.time()

            self._updated_at = (
                self._last_activity
            )

            self._statistics.updated_at = (
                self._updated_at
            )

            self._statistics.success_count += 1

            try:

                self.notify_callbacks(
                    "processor_unregistered",
                    name=name,
                    processor=processor,
                )

            except Exception:

                pass

            try:

                self.emit_event(
                    "processor_unregistered",
                    {
                        "name": name,
                        "processor": processor,
                    },
                )

            except Exception:

                pass

        return self
# ==========================================================================
# Part 4.3 — register_exporter()
# ==========================================================================

    def register_exporter(
        self,
        name: str,
        exporter: Any,
    ) -> "TraceManager":
        """
        Register a trace exporter.

        Parameters
        ----------
        name:
            Unique exporter name.

        exporter:
            Exporter instance.

        Returns
        -------
        TraceManager
            Returns self for fluent chaining.

        Raises
        ------
        ManagerClosedError
            If the manager has been closed.

        TypeError
            If the arguments are invalid.

        ValueError
            If the exporter name is empty.

        DuplicateComponentError
            If the exporter already exists.

        ManagerConfigurationError
            If the maximum number of exporters
            has been reached.
        """

        if self._closed:

            raise ManagerClosedError(
                "TraceManager is closed."
            )

        if not isinstance(
            name,
            str,
        ):

            raise TypeError(
                "name must be a string."
            )

        name = name.strip()

        if not name:

            raise ValueError(
                "Exporter name cannot be empty."
            )

        if exporter is None:

            raise TypeError(
                "exporter cannot be None."
            )

        with self._lock:

            if name in self._exporters:

                raise DuplicateComponentError(
                    f"Exporter '{name}' is already registered."
                )

            if (
                len(self._exporters)
                >= DEFAULT_MAX_EXPORTERS
            ):

                raise ManagerConfigurationError(
                    "Maximum exporter limit reached."
                )

            self._exporters[name] = exporter

            self._statistics.exporter_count = (
                len(self._exporters)
            )

            self._last_activity = time.time()

            self._updated_at = (
                self._last_activity
            )

            self._statistics.updated_at = (
                self._updated_at
            )

            self._statistics.success_count += 1

            try:

                self.notify_callbacks(
                    "exporter_registered",
                    name=name,
                    exporter=exporter,
                )

            except Exception:

                pass

            try:

                self.emit_event(
                    "exporter_registered",
                    {
                        "name": name,
                        "exporter": exporter,
                    },
                )

            except Exception:

                pass

        return self
    # ==========================================================================
    # Part 4.4 — unregister_exporter()
    # ==========================================================================

    def unregister_exporter(
        self,
        name: str,
    ) -> "TraceManager":
        """
        Unregister a trace exporter.

        Parameters
        ----------
        name:
            Registered exporter name.

        Returns
        -------
        TraceManager
            Returns self for fluent chaining.

        Raises
        ------
        ManagerClosedError
            If the manager has been closed.

        TypeError
            If name is not a string.

        ValueError
            If name is empty.

        ComponentNotFoundError
            If the exporter is not registered.
        """

        if self._closed:

            raise ManagerClosedError(
                "TraceManager is closed."
            )

        if not isinstance(
            name,
            str,
        ):

            raise TypeError(
                "name must be a string."
            )

        name = name.strip()

        if not name:

            raise ValueError(
                "Exporter name cannot be empty."
            )

        with self._lock:

            if name not in self._exporters:

                raise ComponentNotFoundError(
                    f"Exporter '{name}' is not registered."
                )

            exporter = self._exporters.pop(
                name
            )

            self._statistics.exporter_count = (
                len(self._exporters)
            )

            self._last_activity = time.time()

            self._updated_at = (
                self._last_activity
            )

            self._statistics.updated_at = (
                self._updated_at
            )

            self._statistics.success_count += 1

            try:

                self.notify_callbacks(
                    "exporter_unregistered",
                    name=name,
                    exporter=exporter,
                )

            except Exception:

                pass

            try:

                self.emit_event(
                    "exporter_unregistered",
                    {
                        "name": name,
                        "exporter": exporter,
                    },
                )

            except Exception:

                pass

        return self
    # ==========================================================================
    # Part 4.5 — register_tracer()
    # ==========================================================================

    def register_tracer(
        self,
        name: str,
        tracer: Any,
    ) -> "TraceManager":
        """
        Register a tracer.

        Parameters
        ----------
        name:
            Unique tracer name.

        tracer:
            Tracer implementation instance.

        Returns
        -------
        TraceManager
            Self for fluent chaining.

        Raises
        ------
        ManagerClosedError
            If the manager has been closed.

        ManagerValidationError
            If the tracer name is invalid.

        DuplicateComponentError
            If a tracer with the same name already exists.
        """

        if self._closed:
            raise ManagerClosedError(
                "Cannot register tracer on a closed TraceManager."
            )

        if not isinstance(name, str) or not name.strip():
            raise ManagerValidationError(
                "Tracer name must be a non-empty string."
            )

        if tracer is None:
            raise ManagerValidationError(
                "Tracer instance cannot be None."
            )

        name = name.strip()

        with self._lock:

            if name in self._tracers:
                raise DuplicateComponentError(
                    f"Tracer '{name}' is already registered."
                )

            self._tracers[name] = tracer

            self._statistics.tracer_count = len(
                self._tracers
            )

            self._updated_at = time.time()

            self._history.append(
                {
                    "event": "register_tracer",
                    "name": name,
                    "timestamp": self._updated_at,
                }
            )

            self._cache.pop("component_count", None)

            try:
                self.notify_callbacks(
                    "register_tracer",
                    name=name,
                    tracer=tracer,
                )
            except Exception:
                pass

            try:
                self.emit_event(
                    "register_tracer",
                    {
                        "name": name,
                    },
                )
            except Exception:
                pass

        return self
# ==========================================================================
# Part 4.6 — unregister_tracer()
# ==========================================================================

    def unregister_tracer(
        self,
        name: str,
    ) -> "TraceManager":
        """
        Unregister a tracer.

        Parameters
        ----------
        name:
            Registered tracer name.

        Returns
        -------
        TraceManager
            Self for fluent chaining.

        Raises
        ------
        ManagerClosedError
            If the manager has already been closed.

        ComponentNotFoundError
            If the tracer does not exist.
        """

        with self._lock:

            if self._closed:
                raise ManagerClosedError(
                    "TraceManager has been closed."
                )

            if name not in self._tracers:
                raise ComponentNotFoundError(
                    f"Tracer '{name}' is not registered."
                )

            tracer = self._tracers.pop(name)

            # update statistics
            self._statistics.tracer_count = len(
                self._tracers
            )

            self._updated_at = time.time()

            # optional lifecycle cleanup
            close = getattr(
                tracer,
                "close",
                None,
            )

            if callable(close):

                try:
                    close()
                except Exception:
                    # Cleanup failure should never prevent
                    # successful unregistration.
                    pass

            # notify callbacks
            for callback in list(self._callbacks):

                try:
                    callback(
                        "tracer_unregistered",
                        name,
                        tracer,
                    )
                except Exception:
                    pass

            # emit hooks
            for hook in self._hooks.get(
                "tracer_unregistered",
                [],
            ):

                try:
                    hook(
                        self,
                        name,
                        tracer,
                    )
                except Exception:
                    pass

        return self
    # ==========================================================================
    # Part 4.7 — register_pipeline()
    # ==========================================================================

    def register_pipeline(
        self,
        name: str,
        pipeline: Any,
    ) -> "TraceManager":
        """
        Register a processing pipeline.

        Parameters
        ----------
        name:
            Unique pipeline name.

        pipeline:
            Pipeline instance.

        Returns
        -------
        TraceManager
            Self for fluent chaining.

        Raises
        ------
        ManagerClosedError
            If the manager has already been closed.

        DuplicateComponentError
            If a pipeline with the same name already exists.

        TypeError
            If pipeline is None.
        """

        if pipeline is None:
            raise TypeError(
                "pipeline cannot be None."
            )

        with self._lock:

            if self._closed:
                raise ManagerClosedError(
                    "TraceManager has been closed."
                )

            if name in self._pipelines:
                raise DuplicateComponentError(
                    f"Pipeline '{name}' already exists."
                )

            self._pipelines[name] = pipeline

            # update statistics
            self._statistics.pipeline_count = len(
                self._pipelines
            )

            self._updated_at = time.time()

            # optional initialize
            initialize = getattr(
                pipeline,
                "initialize",
                None,
            )

            if (
                callable(initialize)
                and self._initialized
            ):
                try:
                    initialize()
                except Exception:
                    pass

            # callbacks
            for callback in list(
                self._callbacks
            ):
                try:
                    callback(
                        "pipeline_registered",
                        name,
                        pipeline,
                    )
                except Exception:
                    pass

            # hooks
            for hook in self._hooks.get(
                "pipeline_registered",
                [],
            ):
                try:
                    hook(
                        self,
                        name,
                        pipeline,
                    )
                except Exception:
                    pass

        return self
    # ==========================================================================
    # Part 4.8 — unregister_pipeline()
    # ==========================================================================

    def unregister_pipeline(
        self,
        name: str,
    ) -> "TraceManager":
        """
        Unregister a processing pipeline.

        Parameters
        ----------
        name:
            Registered pipeline name.

        Returns
        -------
        TraceManager
            Self for fluent chaining.

        Raises
        ------
        ManagerClosedError
            If the manager has already been closed.

        ComponentNotFoundError
            If the pipeline is not registered.
        """

        with self._lock:

            if self._closed:
                raise ManagerClosedError(
                    "TraceManager has been closed."
                )

            if name not in self._pipelines:
                raise ComponentNotFoundError(
                    f"Pipeline '{name}' is not registered."
                )

            pipeline = self._pipelines.pop(name)

            # update statistics
            self._statistics.pipeline_count = len(
                self._pipelines
            )

            self._updated_at = time.time()

            # optional lifecycle cleanup
            shutdown = getattr(
                pipeline,
                "shutdown",
                None,
            )

            if callable(shutdown):
                try:
                    shutdown()
                except Exception:
                    # Ignore cleanup failures.
                    pass

            close = getattr(
                pipeline,
                "close",
                None,
            )

            if callable(close):
                try:
                    close()
                except Exception:
                    pass

            # callbacks
            for callback in list(
                self._callbacks
            ):
                try:
                    callback(
                        "pipeline_unregistered",
                        name,
                        pipeline,
                    )
                except Exception:
                    pass

            # hooks
            for hook in self._hooks.get(
                "pipeline_unregistered",
                [],
            ):
                try:
                    hook(
                        self,
                        name,
                        pipeline,
                    )
                except Exception:
                    pass

        return self

# ==========================================================================
# Part 5.0 — add_trace()
# ==========================================================================

    def add_trace(
        self,
        trace_id: str,
        trace: Optional[Any] = None,
    ) -> "TraceManager":
        """
        Add a trace into active trace registry.
        """

        with self._lock:

            if self._closed:
                raise ManagerClosedError(
                    "Cannot add trace to closed TraceManager."
                )

            if trace_id in self._active_traces:
                raise TraceError(
                    f"Trace already exists: {trace_id}"
                )

            if trace is None:
                trace = {
                    "id": trace_id,
                    "created_at": time.time(),
                }

            self._active_traces[trace_id] = trace

            self._trace_count = len(
                self._active_traces
            )

            self._statistics.trace_count = (
                self._trace_count
            )

            self._updated_at = time.time()

            return self

# ==============================================================================
# Part 5. Trace Lifecycle
# ==============================================================================

    def start_trace(
        self,
        name: str,
        **kwargs: Any,
    ) -> Any:
        """
        Start a new trace.
        """

        if self._closed:
            raise ManagerClosedError(
                "TraceManager is closed."
            )

        with self._lock:

            tracer = self._tracers.get(
                "default"
            )

            if (
                tracer is None
                and self._tracers
            ):
                tracer = next(
                    iter(
                        self._tracers.values()
                    )
                )

            if tracer is None:
                raise ManagerValidationError(
                    "No tracer registered."
                )

            if hasattr(
                tracer,
                "create_trace",
            ):

                trace = tracer.create_trace(
                    name=name,
                    **kwargs,
                )

            elif hasattr(
                tracer,
                "start_trace",
            ):

                # backward compatibility
                trace = tracer.start_trace(
                    name=name,
                    context=self._context,
                    **kwargs,
                )

            else:

                raise ManagerValidationError(
                    "Tracer does not support trace creation."
                )

            trace_id = getattr(
                trace,
                "trace_id",
                str(uuid.uuid4()),
            )

            self._active_traces[
                trace_id
            ] = trace

            self._current_trace = trace
            self._current_span = None

            self._trace_count = len(
                self._active_traces
            )

            self._statistics.trace_count = (
                self._trace_count
            )

            self._last_activity = time.time()
            self._updated_at = (
                self._last_activity
            )
            self._statistics.updated_at = (
                self._last_activity
            )

            return trace


    def finish_trace(
        self,
        trace: Optional[Any] = None,
    ) -> "TraceManager":
        """
        Finish a trace.
        """

        if trace is None:
            trace = self._current_trace

        if trace is None:
            return self

        if hasattr(
            trace,
            "finish",
        ):
            trace.finish()

        trace_id = getattr(
            trace,
            "trace_id",
            None,
        )

        if trace_id is not None:
            self._active_traces.pop(
                trace_id,
                None,
            )

        if trace is self._current_trace:
            self._current_trace = None
            self._current_span = None

        self._trace_count = len(
            self._active_traces
        )

        self._completed_trace_count += 1

        self._statistics.trace_count = (
            self._trace_count
        )

        self._last_activity = time.time()

        self._updated_at = (
            self._last_activity
        )

        return self


    def get_trace(
        self,
        trace_id: str,
    ) -> Optional[Any]:
        """
        Return trace by id.
        """

        with self._lock:

            return self._active_traces.get(
                trace_id
            )


    def remove_trace(
        self,
        trace_id: str,
    ) -> "TraceManager":
        """
        Remove a trace without finishing it.
        """

        with self._lock:

            trace = self._active_traces.pop(
                trace_id,
                None,
            )

            if trace is self._current_trace:

                self._current_trace = None
                self._current_span = None

            self._trace_count = len(
                self._active_traces
            )

            self._statistics.trace_count = (
                self._trace_count
            )

            self._updated_at = time.time()
            self._statistics.updated_at = (
                self._updated_at
            )

            return self


    @property
    def current_trace(
        self,
    ) -> Optional[Any]:
        """
        Current active trace.
        """

        return self._current_trace


    @property
    def active_traces(
        self,
    ) -> Dict[str, Any]:
        """
        Active trace mapping.
        """

        with self._lock:

            return dict(
                self._active_traces
            )

# ==========================================================================
# Part 5.1 — set_current()
# ==========================================================================

    def set_current(
        self,
        trace_id: str,
    ) -> "TraceManager":
        """
        Set the current active trace.
        """

        with self._lock:

            trace = self._active_traces.get(
                trace_id,
            )

            if trace is None:
                raise TraceNotFoundError(
                    f"Trace not found: {trace_id}"
                )

            self._current_trace = trace

            self._updated_at = time.time()

            return self


# ==========================================================================
# Part 5.2 — get_current()
# ==========================================================================

    def get_current(
        self,
    ) -> Optional[Any]:
        """
        Return the current active trace.
        """

        with self._lock:

            return self._current_trace


# ==========================================================================
# Part 5.3 — clear_current()
# ==========================================================================

    def clear_current(
        self,
    ) -> "TraceManager":
        """
        Clear the current active trace.
        """

        with self._lock:

            self._current_trace = None

            self._updated_at = time.time()

            return self

# ==========================================================================
# Part 5.4 — update()
# ==========================================================================

    def update(
        self,
        other: "TraceManager",
    ) -> "TraceManager":
        """
        Update this manager from another manager.
        """

        with self._lock:

            if not isinstance(
                other,
                TraceManager,
            ):
                raise TypeError(
                    "other must be a TraceManager."
                )

            self._active_traces.update(
                other._active_traces
            )

            self._active_spans.update(
                other._active_spans
            )

            self._trace_count = len(
                self._active_traces
            )

            self._span_count = len(
                self._active_spans
            )

            self._completed_trace_count = max(
                self._completed_trace_count,
                other._completed_trace_count,
            )

            self._statistics.trace_count = (
                self._trace_count
            )

            self._statistics.span_count = (
                self._span_count
            )

            self._updated_at = time.time()

            self._last_activity = (
                self._updated_at
            )

        return self


# ==========================================================================
# Part 5.4.1 — Properties
# ==========================================================================

    @property
    def completed_trace_count(
        self,
    ) -> int:
        """
        Number of completed traces.
        """

        return self._completed_trace_count
# ==========================================================================
# Part 5.5 — merge()
# ==========================================================================

    def merge(
        self,
        other: "TraceManager",
    ) -> "TraceManager":
        """
        Merge another TraceManager into this one.

        Parameters
        ----------
        other:
            Source manager.

        Returns
        -------
        TraceManager
            This manager.
        """

        return self.update(other)

# ==========================================================================
# Part 5.6 — copy()
# ==========================================================================

    def copy(self) -> "TraceManager":
        """
        Create a shallow copy of this TraceManager.

        Returns
        -------
        TraceManager
            A copied manager.
        """

        with self._lock:

            manager = TraceManager()

            manager._active_traces = dict(
                self._active_traces
            )

            manager._active_spans = dict(
                self._active_spans
            )

            manager._current_trace = (
                self._current_trace
            )

            manager._current_span = (
                self._current_span
            )

            manager._trace_count = (
                self._trace_count
            )

            manager._span_count = (
                self._span_count
            )

            manager._enabled = (
                self._enabled
            )

            manager._initialized = (
                self._initialized
            )

            manager._running = (
                self._running
            )

            manager._active = (
                self._active
            )

            manager._frozen = (
                self._frozen
            )

            manager._closed = (
                self._closed
            )

            manager._state = (
                self._state
            )

            manager._metadata = dict(
                self._metadata
            )

            manager._tags = list(
                self._tags
            )

            manager._updated_at = (
                time.time()
            )

            return manager

# ==========================================================================
# Part 5.7 — clone()
# ==========================================================================

    def clone(self) -> "TraceManager":
        """
        Create a deep clone of this TraceManager.

        Returns
        -------
        TraceManager
            A deep-cloned manager.
        """

        with self._lock:

            manager = TraceManager()

            manager._active_traces = copy.deepcopy(
                self._active_traces
            )

            manager._active_spans = copy.deepcopy(
                self._active_spans
            )

            manager._current_trace = copy.deepcopy(
                self._current_trace
            )

            manager._current_span = copy.deepcopy(
                self._current_span
            )

            manager._trace_count = (
                self._trace_count
            )

            manager._span_count = (
                self._span_count
            )

            manager._enabled = (
                self._enabled
            )

            manager._initialized = (
                self._initialized
            )

            manager._running = (
                self._running
            )

            manager._active = (
                self._active
            )

            manager._frozen = (
                self._frozen
            )

            manager._closed = (
                self._closed
            )

            manager._state = (
                self._state
            )

            manager._metadata = copy.deepcopy(
                self._metadata
            )

            manager._tags = copy.deepcopy(
                self._tags
            )

            manager._context_data = copy.deepcopy(
                self._context_data
            )

            manager._updated_at = time.time()

            return manager

# ==========================================================================
# Part 5.8 — to_dict()
# ==========================================================================

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the TraceManager into a dictionary.
        """

        with self._lock:

            return {
                "id": self._id,
                "uuid": str(self._uuid),
                "name": self._name,
                "description": self._description,
                "version": self._version,
                "state": self._state.value,
                "enabled": self._enabled,
                "initialized": self._initialized,
                "running": self._running,
                "active": self._active,
                "frozen": self._frozen,
                "closed": self._closed,
                "trace_count": self._trace_count,
                "span_count": self._span_count,
                "active_traces": copy.deepcopy(
                    self._active_traces
                ),
                "active_spans": copy.deepcopy(
                    self._active_spans
                ),
                "tags": list(
                    self._tags
                ),
                "metadata": copy.deepcopy(
                    self._metadata
                ),
                "created_at": self._created_at,
                "updated_at": self._updated_at,
            }

# ==========================================================================
# Part 5.9 — from_dict()
# ==========================================================================

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
    ) -> "TraceManager":
        """
        Create a TraceManager from a dictionary.

        Parameters
        ----------
        data:
            Serialized manager dictionary.

        Returns
        -------
        TraceManager
            Restored manager instance.
        """

        if not isinstance(
            data,
            dict,
        ):
            raise TypeError(
                "data must be a dictionary."
            )

        manager = cls()

        manager._active_traces = dict(
            data.get(
                "active_traces",
                {},
            )
        )

        manager._active_spans = dict(
            data.get(
                "active_spans",
                {},
            )
        )

        manager._current_trace = data.get(
            "current_trace",
        )

        manager._current_span = data.get(
            "current_span",
        )

        manager._trace_count = len(
            manager._active_traces
        )

        manager._span_count = len(
            manager._active_spans
        )

        manager._enabled = bool(
            data.get(
                "enabled",
                True,
            )
        )

        manager._initialized = bool(
            data.get(
                "initialized",
                True,
            )
        )

        manager._running = bool(
            data.get(
                "running",
                False,
            )
        )

        manager._active = bool(
            data.get(
                "active",
                False,
            )
        )

        manager._frozen = bool(
            data.get(
                "frozen",
                False,
            )
        )

        manager._closed = bool(
            data.get(
                "closed",
                False,
            )
        )

        state = data.get(
            "state",
        )

        if isinstance(
            state,
            ManagerState,
        ):
            manager._state = state

        elif isinstance(
            state,
            str,
        ):
            try:
                manager._state = ManagerState(
                    state
                )
            except Exception:
                try:
                    manager._state = (
                        ManagerState[
                            state.upper()
                        ]
                    )
                except Exception:
                    pass

        manager._metadata = dict(
            data.get(
                "metadata",
                {},
            )
        )

        manager._tags = list(
            data.get(
                "tags",
                [],
            )
        )

        manager._updated_at = time.time()

        if hasattr(
            manager,
            "_statistics",
        ):
            manager._statistics.trace_count = (
                manager._trace_count
            )
            manager._statistics.span_count = (
                manager._span_count
            )

        return manager

# ==========================================================================
# Part 5.10 — snapshot()
# ==========================================================================

    def snapshot(self) -> Dict[str, Any]:
        """
        Create a complete snapshot of current TraceManager state.

        Snapshot contains:
        - identity
        - runtime state
        - configuration
        - traces
        - spans
        - metadata
        - tags
        - counters
        - lifecycle information
        """

        with self._lock:

            traces = copy.deepcopy(
                self._active_traces
            )

            spans = copy.deepcopy(
                self._active_spans
            )

            snapshot = {

                # ----------------------------------------------------------
                # Identity
                # ----------------------------------------------------------

                "identity": {
                    "id": self._id,
                    "uuid": str(
                        self._uuid
                    ),
                    "name": self._name,
                    "description": self._description,
                    "version": self._version,
                },


                # ----------------------------------------------------------
                # Runtime
                # ----------------------------------------------------------

                "runtime": {
                    "state": self._state,
                    "initialized": self._initialized,
                    "running": self._running,
                    "active": self._active,
                    "frozen": self._frozen,
                    "closed": self._closed,
                },


                # ----------------------------------------------------------
                # Configuration
                # ----------------------------------------------------------

                "configuration": {
                    "enabled": self._enabled,
                },


                # ----------------------------------------------------------
                # Trace / Span state
                # ----------------------------------------------------------

                "current_trace": copy.deepcopy(
                    self._current_trace
                ),

                "current_span": copy.deepcopy(
                    self._current_span
                ),


                # New public names
                "traces": traces,

                "spans": spans,


                # Backward compatibility

                "active_traces": copy.deepcopy(
                    traces
                ),

                "active_spans": copy.deepcopy(
                    spans
                ),


                # ----------------------------------------------------------
                # Metadata
                # ----------------------------------------------------------

                "metadata": copy.deepcopy(
                    self._metadata
                ),

                "tags": copy.deepcopy(
                    self._tags
                ),


                # ----------------------------------------------------------
                # Statistics
                # ----------------------------------------------------------

                "statistics": {

                    "trace_count": self._trace_count,

                    "span_count": self._span_count,

                },


                # ----------------------------------------------------------
                # Lifecycle
                # ----------------------------------------------------------

                "trace_count": self._trace_count,

                "span_count": self._span_count,

                "created_at": self._created_at,

                "updated_at": self._updated_at,

                "last_activity": self._last_activity,

                "generation": self._generation,

                "revision": self._revision,

                "epoch": self._epoch,

            }


            self._last_snapshot_at = time.time()

            self._updated_at = (
                self._last_snapshot_at
            )


            return snapshot

# ==============================================================================
# Part 6. Span Lifecycle
# ==============================================================================

    def start_span(
        self,
        name: str,
        *,
        trace: Optional[Any] = None,
        parent: Optional[Any] = None,
        **kwargs: Any,
    ) -> Any:
        """
        Start a new span.
        """

        if self._closed:
            raise ManagerClosedError(
                "TraceManager is closed."
            )

        if trace is None:
            trace = self._current_trace

        if trace is None:
            raise ManagerValidationError(
                "No active trace."
            )

        if parent is None:
            parent = self._current_span

        if hasattr(trace, "start_span"):

            span = trace.start_span(
                name=name,
                parent=parent,
                **kwargs,
            )

        else:

            raise ManagerValidationError(
                "Current trace does not support start_span()."
            )

        span_id = getattr(
            span,
            "span_id",
            str(uuid.uuid4()),
        )

        self._active_spans[span_id] = span
        self._current_span = span

        self._statistics.span_count = len(
            self._active_spans
        )

        self._updated_at = time.time()

        return span


    def finish_span(
        self,
        span: Optional[Any] = None,
    ) -> "TraceManager":
        """
        Finish a span.
        """

        if span is None:
            span = self._current_span

        if span is None:
            return self

        if hasattr(span, "finish"):
            span.finish()

        span_id = getattr(
            span,
            "span_id",
            None,
        )

        if span_id is not None:
            self._active_spans.pop(
                span_id,
                None,
            )

        parent = getattr(
            span,
            "parent",
            None,
        )

        self._current_span = parent

        self._statistics.span_count = len(
            self._active_spans
        )

        self._updated_at = time.time()

        return self


    def get_span(
        self,
        span_id: str,
    ) -> Optional[Any]:
        """
        Return a span by id.
        """

        return self._active_spans.get(
            span_id
        )


    def remove_span(
        self,
        span_id: str,
    ) -> "TraceManager":
        """
        Remove a span from runtime.
        """

        span = self._active_spans.pop(
            span_id,
            None,
        )

        if span is self._current_span:

            self._current_span = getattr(
                span,
                "parent",
                None,
            )

        self._statistics.span_count = len(
            self._active_spans
        )

        self._updated_at = time.time()

        return self


    @property
    def current_span(self) -> Optional[Any]:
        """
        Current active span.
        """

        return self._current_span


    @property
    def active_spans(self) -> Dict[str, Any]:
        """
        Active span mapping.
        """

        return dict(
            self._active_spans
        )


    def span_hierarchy(
        self,
    ) -> Dict[str, List[Any]]:
        """
        Return nested span hierarchy.
        """

        hierarchy: Dict[str, List[Any]] = defaultdict(list)

        for span in self._active_spans.values():

            parent = getattr(
                span,
                "parent",
                None,
            )

            key = (
                getattr(parent, "span_id", "root")
                if parent is not None
                else "root"
            )

            hierarchy[key].append(span)

        return dict(
            hierarchy
        )
# ==============================================================================
# Part 7. Processing
# ==============================================================================

    def process(
        self,
        record: Any,
    ) -> Any:
        """
        Process a trace record through the registered processor.
        """

        if self._closed:
            raise ManagerClosedError(
                "TraceManager is closed."
            )

        if not self._enabled:
            return record

        processor = self._processor

        if processor is None:
            return record

        self.before_process(record)

        try:

            if hasattr(processor, "process"):
                result = processor.process(record)

            elif callable(processor):
                result = processor(record)

            else:
                result = record

            self._statistics.success_count += 1

            return result

        except Exception:

            self._statistics.failure_count += 1
            raise

        finally:

            self._updated_at = time.time()
            self.after_process(record)


    def flush(self) -> "TraceManager":
        """
        Flush processor and exporters.
        """

        self.before_flush()

        if (
            self._processor is not None
            and hasattr(
                self._processor,
                "flush",
            )
        ):
            self._processor.flush()

        for exporter in self._exporters.values():

            if hasattr(
                exporter,
                "flush",
            ):
                exporter.flush()

        self._statistics.flush_count += 1

        self._updated_at = time.time()

        self.after_flush()

        return self


    def clear(self) -> "TraceManager":
        """
        Clear runtime buffers.
        """

        self._cache.clear()

        self._history.clear()

        self._active_traces.clear()

        self._active_spans.clear()

        self._current_trace = None

        self._current_span = None

        self._updated_at = time.time()

        return self


    def reset(self) -> "TraceManager":
        """
        Reset runtime state.
        """

        self.clear()

        self._statistics = ManagerStatistics()

        self._state = ManagerState.CREATED

        self._initialized = False

        self._running = False

        self._active = False

        self._frozen = False

        self._statistics.reset_count += 1

        self._updated_at = time.time()

        return self
    # ==============================================================================
    # Part 8. Runtime Operations
    # ==============================================================================

    def snapshot(self) -> Dict[str, Any]:
        """
        Create a runtime snapshot.
        """

        return {
            "identity": {
                "id": self._id,
                "uuid": str(self._uuid),
                "name": self._name,
                "description": self._description,
                "version": self._version,
            },
            "configuration": {
                "manager_type": self._manager_type.value,
                "mode": self._mode.value,
                "enabled": self._enabled,
                "auto_initialize": self._auto_initialize,
                "auto_flush": self._auto_flush,
                "history_limit": self._history_limit,
                "timeout": self._timeout,
                "encoding": self._encoding,
                "options": copy.deepcopy(self._options),
            },
            "runtime": {
                "state": self._state.value,
                "initialized": self._initialized,
                "running": self._running,
                "active": self._active,
                "frozen": self._frozen,
                "closed": self._closed,
                "created_at": self._created_at,
                "updated_at": self._updated_at,
                "last_activity": self._last_activity,
            },
            "statistics": asdict(self._statistics),
            "metadata": copy.deepcopy(self._metadata),
            "tags": list(self._tags),
            "context": copy.deepcopy(self._context_data),
        }



    def clone(self) -> "TraceManager":
        """
        Create a cloned manager.
        """

        return self.__deepcopy__({})


    def copy(self) -> "TraceManager":
        """
        Shallow copy.
        """

        return self.__copy__()


    def compact(self) -> "TraceManager":
        """
        Compact runtime storage.
        """

        self._history = deque(
            self._history,
            maxlen=self._history_limit,
        )

        self._cache = dict(
            self._cache
        )

        self._updated_at = time.time()

        return self


    def cleanup(self) -> "TraceManager":
        """
        Cleanup temporary runtime resources.
        """

        self._cache.clear()

        self._current_span = None

        self._active_spans.clear()

        self._updated_at = time.time()

        return self


    def optimize(self) -> "TraceManager":
        """
        Optimize runtime structures.
        """

        self.compact()

        self._statistics.updated_at = (
            time.time()
        )

        return self


# ==============================================================================
# Part 9. Snapshot / Restore
# ==============================================================================


    def _serialize_entity(
        self,
        value: Any,
    ) -> Any:
        """
        Serialize runtime entity.

        Supports:
        - to_dict()
        - dataclass
        - deepcopy fallback
        """

        if value is None:
            return None


        if hasattr(
            value,
            "to_dict",
        ):

            return value.to_dict()


        return copy.deepcopy(
            value
        )



    def _restore_entity(
        self,
        value: Any,
        cls: Any = None,
    ) -> Any:
        """
        Restore runtime entity.

        Supports:
        - from_dict()
        - deepcopy fallback
        """

        if value is None:
            return None


        if (
            cls is not None
            and isinstance(
                value,
                Mapping,
            )
        ):

            if hasattr(
                cls,
                "from_dict",
            ):

                return cls.from_dict(
                    value
                )


        return copy.deepcopy(
            value
        )



    def _get_trace_class(self):
        """
        Resolve Trace class lazily.
        """

        try:

            from .trace import Trace

            return Trace

        except Exception:

            return None



    def _get_span_class(self):
        """
        Resolve Span class lazily.
        """

        try:

            from .span import Span

            return Span

        except Exception:

            return None



# ==============================================================================
# Snapshot
# ==============================================================================


    def snapshot(
        self,
    ) -> Dict[str, Any]:
        """
        Create complete runtime snapshot.

        Returns
        -------
        Dict[str, Any]
            Serializable TraceManager snapshot.
        """


        with self._lock:


            traces = {

                key:
                    self._serialize_entity(
                        value
                    )

                for key, value
                in self._active_traces.items()

            }



            spans = {

                key:
                    self._serialize_entity(
                        value
                    )

                for key, value
                in self._active_spans.items()

            }



            snapshot_time = time.time()



            snapshot = {

                # ----------------------------------------------------------
                # Identity
                # ----------------------------------------------------------

                "identity": {

                    "id":
                        self._id,

                    "uuid":
                        str(
                            self._uuid
                        ),

                    "name":
                        self._name,

                    "description":
                        self._description,

                    "version":
                        self._version,

                },


                # ----------------------------------------------------------
                # Configuration
                # ----------------------------------------------------------

                "configuration": {

                    "manager_type":
                        self._manager_type.value,

                    "mode":
                        self._mode.value,

                    "enabled":
                        self._enabled,

                    "auto_initialize":
                        self._auto_initialize,

                    "auto_flush":
                        self._auto_flush,

                    "history_limit":
                        self._history_limit,

                    "timeout":
                        self._timeout,

                    "encoding":
                        self._encoding,

                    "options":
                        copy.deepcopy(
                            self._options
                        ),

                },


                # ----------------------------------------------------------
                # Runtime
                # ----------------------------------------------------------

                "runtime": {

                    "state":
                        self._state.value,

                    "initialized":
                        self._initialized,

                    "running":
                        self._running,

                    "active":
                        self._active,

                    "frozen":
                        self._frozen,

                    "closed":
                        self._closed,

                    "created_at":
                        self._created_at,

                    "updated_at":
                        self._updated_at,

                    "last_activity":
                        self._last_activity,

                },


                # ----------------------------------------------------------
                # Statistics
                # ----------------------------------------------------------

                "statistics":
                    asdict(
                        self._statistics
                    ),



                # ----------------------------------------------------------
                # Metadata
                # ----------------------------------------------------------

                "metadata":
                    copy.deepcopy(
                        self._metadata
                    ),


                "tags":
                    copy.deepcopy(
                        self._tags
                    ),


                "context_data":
                    copy.deepcopy(
                        self._context_data
                    ),



                # ----------------------------------------------------------
                # Trace / Span
                # ----------------------------------------------------------

                "traces":
                    traces,


                "spans":
                    spans,


                # compatibility
                "active_traces":
                    copy.deepcopy(
                        traces
                    ),


                "active_spans":
                    copy.deepcopy(
                        spans
                    ),



                "current_trace":

                    self._serialize_entity(
                        self._current_trace
                    ),



                "current_span":

                    self._serialize_entity(
                        self._current_span
                    ),



                "current_trace_id":

                    getattr(
                        self._current_trace,
                        "id",
                        None,
                    ),



                "current_span_id":

                    getattr(
                        self._current_span,
                        "id",
                        None,
                    ),



                # ----------------------------------------------------------
                # Runtime Data
                # ----------------------------------------------------------

                "cache":
                    copy.deepcopy(
                        self._cache
                    ),


                "history":
                    copy.deepcopy(
                        list(
                            self._history
                        )
                    ),



                # ----------------------------------------------------------
                # Counters
                # ----------------------------------------------------------

                "trace_count":
                    self._trace_count,


                "span_count":
                    self._span_count,



                # ----------------------------------------------------------
                # Version
                # ----------------------------------------------------------

                "generation":
                    self._generation,


                "revision":
                    self._revision,


                "epoch":
                    self._epoch,



                # ----------------------------------------------------------
                # Snapshot Metadata
                # ----------------------------------------------------------

                "snapshot": {

                    "created_at":
                        snapshot_time,

                    "manager_id":
                        self._id,

                    "generation":
                        self._generation,

                    "revision":
                        self._revision,

                },

            }



            self._last_snapshot_at = snapshot_time



            return snapshot



# ==============================================================================
# Restore
# ==============================================================================


    def restore(
        self,
        snapshot: Mapping[str, Any],
    ) -> "TraceManager":
        """
        Restore TraceManager from snapshot.
        """


        if not isinstance(
            snapshot,
            Mapping,
        ):

            raise TypeError(
                "snapshot must be a mapping"
            )



        with self._lock:


            identity = snapshot.get(
                "identity",
                {},
            )


            configuration = snapshot.get(
                "configuration",
                {},
            )


            runtime = snapshot.get(
                "runtime",
                {},
            )



            # --------------------------------------------------------------
            # Identity
            # --------------------------------------------------------------

            self._id = identity.get(
                "id",
                self._id,
            )


            uuid_value = identity.get(
                "uuid"
            )


            if uuid_value:

                self._uuid = uuid.UUID(
                    uuid_value
                )


            self._name = identity.get(
                "name",
                self._name,
            )


            self._description = identity.get(
                "description",
                self._description,
            )


            self._version = identity.get(
                "version",
                self._version,
            )



            # --------------------------------------------------------------
            # Configuration
            # --------------------------------------------------------------

            if "manager_type" in configuration:

                self._manager_type = ManagerType(
                    configuration[
                        "manager_type"
                    ]
                )


            if "mode" in configuration:

                self._mode = ManagerMode(
                    configuration[
                        "mode"
                    ]
                )


            for key in (
                "enabled",
                "auto_initialize",
                "auto_flush",
                "history_limit",
                "timeout",
                "encoding",
            ):

                if key in configuration:

                    setattr(
                        self,
                        f"_{key}",
                        configuration[key],
                    )



            self._options = copy.deepcopy(
                configuration.get(
                    "options",
                    self._options,
                )
            )



            # --------------------------------------------------------------
            # Runtime
            # --------------------------------------------------------------

            if "state" in runtime:

                self._state = ManagerState(
                    runtime[
                        "state"
                    ]
                )


            for key in (
                "initialized",
                "running",
                "active",
                "frozen",
                "closed",
                "created_at",
                "updated_at",
                "last_activity",
            ):

                if key in runtime:

                    setattr(
                        self,
                        f"_{key}",
                        runtime[key],
                    )



            # --------------------------------------------------------------
            # Metadata
            # --------------------------------------------------------------

            self._metadata = copy.deepcopy(
                snapshot.get(
                    "metadata",
                    {},
                )
            )


            self._tags = copy.deepcopy(
                snapshot.get(
                    "tags",
                    [],
                )
            )


            self._context_data = copy.deepcopy(
                snapshot.get(
                    "context_data",
                    {},
                )
            )



            # --------------------------------------------------------------
            # Restore Trace / Span Objects
            # --------------------------------------------------------------

            trace_cls = self._get_trace_class()

            span_cls = self._get_span_class()



            trace_data = snapshot.get(
                "traces",
                snapshot.get(
                    "active_traces",
                    {},
                ),
            )


            span_data = snapshot.get(
                "spans",
                snapshot.get(
                    "active_spans",
                    {},
                ),
            )



            self._active_traces = {

                key:
                    self._restore_entity(
                        value,
                        trace_cls,
                    )

                for key, value
                in trace_data.items()

            }



            self._active_spans = {

                key:
                    self._restore_entity(
                        value,
                        span_cls,
                    )

                for key, value
                in span_data.items()

            }



            self._current_trace = self._restore_entity(
                snapshot.get(
                    "current_trace"
                ),
                trace_cls,
            )


            self._current_span = self._restore_entity(
                snapshot.get(
                    "current_span"
                ),
                span_cls,
            )



            # fallback id lookup

            if self._current_trace is None:

                self._current_trace = (
                    self._active_traces.get(
                        snapshot.get(
                            "current_trace_id"
                        )
                    )
                )



            if self._current_span is None:

                self._current_span = (
                    self._active_spans.get(
                        snapshot.get(
                            "current_span_id"
                        )
                    )
                )



            # --------------------------------------------------------------
            # Statistics
            # --------------------------------------------------------------

            statistics = snapshot.get(
                "statistics"
            )


            if statistics:

                self._statistics = ManagerStatistics(
                    **statistics
                )



            self._trace_count = snapshot.get(
                "trace_count",
                len(
                    self._active_traces
                ),
            )


            self._span_count = snapshot.get(
                "span_count",
                len(
                    self._active_spans
                ),
            )



            # --------------------------------------------------------------
            # Cache / History
            # --------------------------------------------------------------

            self._cache = copy.deepcopy(
                snapshot.get(
                    "cache",
                    {},
                )
            )


            self._history = deque(
                snapshot.get(
                    "history",
                    [],
                ),
                maxlen=self._history_limit,
            )



            # --------------------------------------------------------------
            # Version
            # --------------------------------------------------------------

            self._generation = snapshot.get(
                "generation",
                self._generation,
            )


            self._revision = snapshot.get(
                "revision",
                self._revision,
            )


            self._epoch = snapshot.get(
                "epoch",
                self._epoch,
            )



            self._last_restore_at = time.time()



            return self
        # ==============================================================================
        # Part 10. Serialization
        # ==============================================================================

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize TraceManager into a dictionary.
        """

        return {
            "identity": {
                "id": self._id,
                "uuid": str(self._uuid),
                "name": self._name,
                "description": self._description,
                "version": self._version,
            },
            "configuration": {
                "manager_type": self._manager_type.value,
                "mode": self._mode.value,
                "enabled": self._enabled,
                "auto_initialize": self._auto_initialize,
                "auto_flush": self._auto_flush,
                "history_limit": self._history_limit,
                "timeout": self._timeout,
                "encoding": self._encoding,
                "options": copy.deepcopy(self._options),
            },
            "runtime": {
                "state": self._state.value,
                "initialized": self._initialized,
                "running": self._running,
                "active": self._active,
                "frozen": self._frozen,
                "closed": self._closed,
                "created_at": self._created_at,
                "updated_at": self._updated_at,
                "last_activity": self._last_activity,
            },
            "statistics": asdict(self._statistics),
            "metadata": copy.deepcopy(self._metadata),
            "tags": list(self._tags),
            "context_data": copy.deepcopy(
                self._context_data
            ),
            "history": list(self._history),
            "cache": copy.deepcopy(self._cache),
        }


    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "TraceManager":
        """
        Create a TraceManager from a dictionary.
        """

        identity = data.get("identity", {})
        configuration = data.get(
            "configuration",
            {},
        )
        runtime = data.get("runtime", {})

        manager = cls(
            name=identity.get(
                "name",
                MANAGER_NAME,
            ),
            description=identity.get(
                "description",
                MANAGER_DESCRIPTION,
            ),
            manager_type=ManagerType(
                configuration.get(
                    "manager_type",
                    ManagerType.STANDARD.value,
                )
            ),
            mode=ManagerMode(
                configuration.get(
                    "mode",
                    ManagerMode.SYNCHRONOUS.value,
                )
            ),
            enabled=configuration.get(
                "enabled",
                DEFAULT_ENABLED,
            ),
            auto_initialize=configuration.get(
                "auto_initialize",
                DEFAULT_AUTO_INITIALIZE,
            ),
            auto_flush=configuration.get(
                "auto_flush",
                DEFAULT_AUTO_FLUSH,
            ),
            history_limit=configuration.get(
                "history_limit",
                DEFAULT_HISTORY_LIMIT,
            ),
            timeout=configuration.get(
                "timeout",
                DEFAULT_TIMEOUT,
            ),
            encoding=configuration.get(
                "encoding",
                DEFAULT_ENCODING,
            ),
            options=copy.deepcopy(
                configuration.get(
                    "options",
                    {},
                )
            ),
        )

        manager._id = identity.get(
            "id",
            manager._id,
        )

        manager._uuid = uuid.UUID(
            identity.get(
                "uuid",
                str(manager._uuid),
            )
        )

        manager._version = identity.get(
            "version",
            manager._version,
        )

        manager._state = ManagerState(
            runtime.get(
                "state",
                manager._state.value,
            )
        )

        manager._initialized = runtime.get(
            "initialized",
            manager._initialized,
        )

        manager._running = runtime.get(
            "running",
            manager._running,
        )

        manager._active = runtime.get(
            "active",
            manager._active,
        )

        manager._frozen = runtime.get(
            "frozen",
            manager._frozen,
        )

        manager._closed = runtime.get(
            "closed",
            manager._closed,
        )

        manager._created_at = runtime.get(
            "created_at",
            manager._created_at,
        )

        manager._updated_at = runtime.get(
            "updated_at",
            manager._updated_at,
        )

        manager._last_activity = runtime.get(
            "last_activity",
            manager._last_activity,
        )

        manager._statistics = ManagerStatistics(
            **data.get(
                "statistics",
                {},
            )
        )

        manager._metadata = copy.deepcopy(
            data.get(
                "metadata",
                {},
            )
        )

        manager._tags = list(
            data.get(
                "tags",
                [],
            )
        )

        manager._context_data = copy.deepcopy(
            data.get(
                "context_data",
                {},
            )
        )

        manager._cache = copy.deepcopy(
            data.get(
                "cache",
                {},
            )
        )

        manager._history = deque(
            data.get(
                "history",
                [],
            ),
            maxlen=manager._history_limit,
        )

        return manager


    def to_json(
        self,
        *,
        indent: int = 2,
    ) -> str:
        """
        Serialize manager into JSON.
        """

        return json.dumps(
            self.to_dict(),
            indent=indent,
            ensure_ascii=False,
            default=str,
        )


    @classmethod
    def from_json(
        cls,
        source: str,
    ) -> "TraceManager":
        """
        Deserialize manager from JSON.
        """

        return cls.from_dict(
            json.loads(source)
        )
# ==============================================================================
# Part 11. Statistics
# ==============================================================================

    def summary(self) -> Dict[str, Any]:
        """
        Return a high-level runtime summary.
        """

        return {
            "name": self._name,
            "version": self._version,
            "state": self._state.value,
            "enabled": self._enabled,
            "manager_type": self._manager_type.value,
            "mode": self._mode.value,
            "trace_count": self.trace_count,
            "span_count": self.span_count,
            "processor_count": self.processor_count,
            "exporter_count": self.exporter_count,
            "tracer_count": self.tracer_count,
            "pipeline_count": self.pipeline_count,
            "success_rate": self.success_rate,
            "failure_rate": self.failure_rate,
            "uptime": self.uptime,
        }


    def report(self) -> ManagerReport:
        """
        Generate a ManagerReport.
        """

        return ManagerReport(
            name=self._name,
            state=self._state.value,
            enabled=self._enabled,
            processors=self.processor_count,
            exporters=self.exporter_count,
            tracers=self.tracer_count,
            pipelines=self.pipeline_count,
            traces=self.trace_count,
            success_rate=self.success_rate,
            uptime=self.uptime,
            failures=self.failure_count,
            dropped=self.dropped_count,
            metadata=copy.deepcopy(
                self._metadata
            ),
        )


    def diagnostics(self) -> Dict[str, Any]:
        """
        Runtime diagnostics.
        """

        return {
            "identity": {
                "id": self._id,
                "uuid": str(self._uuid),
                "name": self._name,
                "version": self._version,
            },
            "runtime": {
                "state": self._state.value,
                "initialized": self._initialized,
                "running": self._running,
                "active": self._active,
                "frozen": self._frozen,
                "closed": self._closed,
                "uptime": self.uptime,
            },
            "statistics": asdict(
                self._statistics
            ),
            "components": {
                "processors": list(
                    self._processors.keys()
                ),
                "exporters": list(
                    self._exporters.keys()
                ),
                "tracers": list(
                    self._tracers.keys()
                ),
                "pipelines": list(
                    self._pipelines.keys()
                ),
            },
            "active": {
                "trace": (
                    getattr(
                        self._current_trace,
                        "name",
                        None,
                    )
                ),
                "span": (
                    getattr(
                        self._current_span,
                        "name",
                        None,
                    )
                ),
                "trace_count": len(
                    self._active_traces
                ),
                "span_count": len(
                    self._active_spans
                ),
            },
        }


    def health(self) -> Dict[str, Any]:
        """
        Runtime health report.
        """

        healthy = (
            self._enabled
            and not self._closed
            and self._state
            != ManagerState.FAILED
        )

        return {
            "healthy": healthy,
            "state": self._state.value,
            "enabled": self._enabled,
            "running": self._running,
            "success_rate": self.success_rate,
            "failure_rate": self.failure_rate,
            "active_traces": len(
                self._active_traces
            ),
            "active_spans": len(
                self._active_spans
            ),
        }


    def metrics(self) -> Dict[str, Union[int, float]]:
        """
        Numeric runtime metrics.
        """

        return {
            "trace_count": self.trace_count,
            "span_count": self.span_count,
            "processor_count": self.processor_count,
            "exporter_count": self.exporter_count,
            "tracer_count": self.tracer_count,
            "pipeline_count": self.pipeline_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "dropped_count": self.dropped_count,
            "success_rate": self.success_rate,
            "failure_rate": self.failure_rate,
            "uptime": self.uptime,
        }
# ==============================================================================
# Part 12. Diagnostics
# ==============================================================================

    def validate(self) -> bool:
        """
        Validate manager.
        """

        self._statistics.validation_count += 1

        return (
            self.validate_configuration()
            and self.validate_components()
            and self.validate_pipeline()
            and self.check_integrity()
        )


    def validate_configuration(self) -> bool:
        """
        Validate runtime configuration.
        """

        if self._history_limit <= 0:
            return False

        if self._timeout <= 0:
            return False

        if not isinstance(
            self._encoding,
            str,
        ):
            return False

        return True


    def validate_components(self) -> bool:
        """
        Validate registered components.
        """

        if (
            self._sampler is not None
            and not isinstance(
                self._sampler,
                TraceSampler,
            )
        ):
            return False

        if (
            self._processor is not None
            and not isinstance(
                self._processor,
                TraceProcessor,
            )
        ):
            return False

        if (
            self._context is not None
            and not isinstance(
                self._context,
                TraceContext,
            )
        ):
            return False

        for processor in self._processors.values():

            if not isinstance(
                processor,
                TraceProcessor,
            ):
                return False

        return True


    def validate_pipeline(self) -> bool:
        """
        Validate registered pipelines.
        """

        for name, pipeline in self._pipelines.items():

            if pipeline is None:
                return False

            if not isinstance(
                name,
                str,
            ):
                return False

        return True


    def check_integrity(self) -> bool:
        """
        Perform internal integrity checks.
        """

        if self._closed and self._running:
            return False

        if self._closed and self._active:
            return False

        if (
            self.trace_count
            < len(self._active_traces)
        ):
            return False

        if (
            self.span_count
            < len(self._active_spans)
        ):
            return False

        if (
            self.success_count
            + self.failure_count
            < self.dropped_count
        ):
            return False

        return True
# ==============================================================================
# Part 13. Hooks & Callbacks
# ==============================================================================

    def before_process(
        self,
        trace: Any,
    ) -> None:
        """
        Execute before-process hooks.
        """

        self.emit_event(
            "before_process",
            trace=trace,
        )

        for hook in self._hooks.get(
            "before_process",
            [],
        ):
            try:
                hook(trace)
            except Exception:
                pass


    def after_process(
        self,
        trace: Any,
    ) -> None:
        """
        Execute after-process hooks.
        """

        self.emit_event(
            "after_process",
            trace=trace,
        )

        for hook in self._hooks.get(
            "after_process",
            [],
        ):
            try:
                hook(trace)
            except Exception:
                pass


    def before_flush(self) -> None:
        """
        Execute before-flush hooks.
        """

        self.emit_event("before_flush")

        for hook in self._hooks.get(
            "before_flush",
            [],
        ):
            try:
                hook()
            except Exception:
                pass


    def after_flush(self) -> None:
        """
        Execute after-flush hooks.
        """

        self.emit_event("after_flush")

        for hook in self._hooks.get(
            "after_flush",
            [],
        ):
            try:
                hook()
            except Exception:
                pass


    def add_hook(
        self,
        event: str,
        hook: TraceHook,
    ) -> "TraceManager":
        """
        Register a hook.
        """

        with self._lock:

            self._hooks[event].append(
                hook
            )

            self._statistics.hook_count += 1

            self._updated_at = time.time()

        return self


    def remove_hook(
        self,
        event: str,
        hook: TraceHook,
    ) -> "TraceManager":
        """
        Remove a hook.
        """

        with self._lock:

            hooks = self._hooks.get(
                event,
                [],
            )

            if hook in hooks:
                hooks.remove(hook)

        return self


    def clear_hooks(
        self,
        event: Optional[str] = None,
    ) -> "TraceManager":
        """
        Clear hooks.
        """

        with self._lock:

            if event is None:

                self._hooks.clear()

            else:

                self._hooks.pop(
                    event,
                    None,
                )

        return self


    def emit_event(
        self,
        event: str,
        **payload: Any,
    ) -> None:
        """
        Emit runtime event.
        """

        self.notify_callbacks(
            event,
            **payload,
        )


    def subscribe(
        self,
        callback: TraceCallback,
    ) -> "TraceManager":
        """
        Subscribe callback.
        """

        with self._lock:

            if callback not in self._callbacks:

                self._callbacks.append(
                    callback
                )

                self._statistics.callback_count += 1

        return self


    def unsubscribe(
        self,
        callback: TraceCallback,
    ) -> "TraceManager":
        """
        Remove callback.
        """

        with self._lock:

            if callback in self._callbacks:

                self._callbacks.remove(
                    callback
                )

        return self


    def clear_callbacks(
        self,
    ) -> "TraceManager":
        """
        Remove all callbacks.
        """

        with self._lock:

            self._callbacks.clear()

        return self


    def notify_callbacks(
        self,
        event: str,
        **payload: Any,
    ) -> None:
        """
        Notify subscribers.
        """

        for callback in tuple(
            self._callbacks
        ):
            try:
                callback(
                    event,
                    **payload,
                )
            except Exception:
                pass
# ==============================================================================
# Part 14. Python Protocols
# ==============================================================================

    def __repr__(self) -> str:
        """
        Developer representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"name={self._name!r}, "
            f"state={self._state.value!r}, "
            f"enabled={self._enabled!r}, "
            f"traces={self.trace_count}, "
            f"spans={self.span_count})"
        )


    def __str__(self) -> str:
        """
        Human-readable representation.
        """

        return (
            f"{self._name} "
            f"[{self._state.value}] "
            f"(traces={self.trace_count}, "
            f"spans={self.span_count})"
        )


    def __len__(self) -> int:
        """
        Number of active traces.
        """

        return len(
            self._active_traces
        )


    def __iter__(self) -> Iterator[Any]:
        """
        Iterate over active traces.
        """

        return iter(
            self._active_traces.values()
        )


    def __contains__(
        self,
        item: object,
    ) -> bool:
        """
        Membership test.
        """

        if isinstance(item, str):

            return (
                item in self._active_traces
                or item in self._active_spans
            )

        return (
            item in self._active_traces.values()
            or item in self._active_spans.values()
        )


    def __getitem__(
        self,
        key: str,
    ) -> Any:
        """
        Lookup trace or span.
        """

        if key in self._active_traces:
            return self._active_traces[key]

        if key in self._active_spans:
            return self._active_spans[key]

        raise KeyError(key)


    def __call__(
        self,
        trace_name: str,
        **kwargs: Any,
    ) -> Any:
        """
        Shortcut for start_trace().
        """

        return self.start_trace(
            trace_name,
            **kwargs,
        )


    def __bool__(self) -> bool:
        """
        Truth value.
        """

        return (
            self._enabled
            and not self._closed
        )


    def __copy__(self):
        """
        Shallow copy.
        """

        return self.clone()


    def __deepcopy__(
        self,
        memo: Optional[
            Dict[int, Any]
        ] = None,
    ):
        """
        Deep copy.
        """

        if memo is None:
            memo = {}

        copied = self.from_dict(
            self.to_dict()
        )

        memo[id(self)] = copied

        return copied


    def __eq__(
        self,
        other: object,
    ) -> bool:
        """
        Equality.
        """

        if not isinstance(
            other,
            TraceManager,
        ):
            return NotImplemented

        return self._id == other._id


    def __hash__(self) -> int:
        """
        Hash.
        """

        return hash(
            self._id
        )


    def __enter__(self) -> "TraceManager":
        """
        Context manager enter.
        """

        if self._closed:
            raise ManagerClosedError(
                "Cannot enter a closed TraceManager."
            )

        if (
            self._auto_initialize
            and not self._initialized
        ):
            self.initialize()

        return self


    def __exit__(
        self,
        exc_type,
        exc,
        tb,
    ) -> bool:
        """
        Context manager exit.
        """

        try:

            if self._auto_flush:
                self.flush()

        finally:

            self.close()

        return False
# ==============================================================================
# Part 15. Public API
# ==============================================================================

__all__ = [

    # ------------------------------------------------------------------
    # Constants
    # ------------------------------------------------------------------

    "MANAGER_NAME",
    "MANAGER_DESCRIPTION",
    "MANAGER_VERSION",
    "DEFAULT_ENCODING",
    "DEFAULT_HISTORY_LIMIT",
    "DEFAULT_TIMEOUT",
    "DEFAULT_MAX_PROCESSORS",
    "DEFAULT_MAX_EXPORTERS",
    "DEFAULT_MAX_TRACERS",
    "DEFAULT_MAX_PIPELINES",
    "DEFAULT_AUTO_INITIALIZE",
    "DEFAULT_AUTO_FLUSH",
    "DEFAULT_ENABLED",
    "DEFAULT_CACHE_SIZE",

    # ------------------------------------------------------------------
    # Type Aliases
    # ------------------------------------------------------------------

    "TraceRecord",
    "TraceData",
    "TraceMetadata",
    "TraceOptions",
    "TraceCache",
    "TraceHistory",
    "TraceHook",
    "TraceCallback",
    "TraceFilter",
    "TraceEvent",
    "ComponentMap",
    "ProcessorMap",
    "ExporterMap",
    "TracerMap",
    "PipelineMap",
    "ManagerMetadata",
    "ManagerContext",
    "ManagerOptions",

    # ------------------------------------------------------------------
    # Exceptions
    # ------------------------------------------------------------------

    "TraceManagerError",
    "ManagerConfigurationError",
    "ManagerValidationError",
    "ComponentNotFoundError",
    "DuplicateComponentError",
    "ManagerClosedError",

    # ------------------------------------------------------------------
    # Enums
    # ------------------------------------------------------------------

    "ManagerType",
    "ManagerState",
    "ManagerMode",
    "ManagerCapability",

    # ------------------------------------------------------------------
    # Dataclasses
    # ------------------------------------------------------------------

    "ManagerStatistics",
    "ManagerReport",

    # ------------------------------------------------------------------
    # Main Class
    # ------------------------------------------------------------------

    "TraceManager",
]                        
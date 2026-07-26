# ==============================================================================
# Part 1. Foundation
# ==============================================================================
#
# trace.py
#
# 1.1 Imports
#
# ==============================================================================


# ==============================================================================
# Future Imports
# ==============================================================================

from __future__ import annotations


# ==============================================================================
# Standard Library Imports
# ==============================================================================

import copy

import json

import time

import uuid as uuid_lib



# ==============================================================================
# Abstract Base Classes
# ==============================================================================

from abc import (
    ABC,
    abstractmethod,
)



# ==============================================================================
# Dataclasses
# ==============================================================================

from dataclasses import (
    dataclass,
    field,
    asdict,
)



# ==============================================================================
# Enum
# ==============================================================================

from enum import (
    Enum,
    IntEnum,
    StrEnum,
    auto,
)



# ==============================================================================
# Threading
# ==============================================================================

from threading import (
    RLock,
    Lock,
)



# ==============================================================================
# Typing
# ==============================================================================

from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    Final,
    Iterable,
    Iterator,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Protocol,
    Sequence,
    Tuple,
    Type,
    TypeAlias,
    Union,
)
# ==============================================================================
# Part 1. Foundation
#
# 1.2 Constants
#
# SciOS-NG Runtime Observability - trace.py
# ==============================================================================


# ==============================================================================
# Identity Constants
# ==============================================================================

TRACE_NAME_DEFAULT: str = "anonymous.trace"

TRACER_NAME_DEFAULT: str = "SciOS-NG.Tracer"

TRACE_ID_LENGTH: int = 32

SPAN_ID_LENGTH: int = 16


TRACE_NAMESPACE: str = "scios.runtime.observability"


# ==============================================================================
# Version Constants
# ==============================================================================

TRACE_VERSION: str = "0.3.0-alpha"

TRACE_API_VERSION: str = "1.0"

TRACE_SCHEMA_VERSION: str = "1.0"

TRACE_FORMAT_VERSION: str = "1.0"


# ==============================================================================
# Runtime Constants
# ==============================================================================

DEFAULT_ENABLED: bool = True

DEFAULT_AUTO_START: bool = False

DEFAULT_AUTO_FINISH: bool = False


DEFAULT_TIMEOUT: float = 30.0


DEFAULT_RUNTIME_MODE: str = "sync"


DEFAULT_THREAD_SAFE: bool = True


DEFAULT_MAX_ACTIVE_TRACES: int = 10000


DEFAULT_MAX_ACTIVE_SPANS: int = 100000

DEFAULT_SPAN_NAME = "span"


# ==============================================================================
# Sampling Constants
# ==============================================================================

DEFAULT_SAMPLING_ENABLED: bool = True


DEFAULT_SAMPLE_RATE: float = 1.0


DEFAULT_RANDOM_SEED: int = 42


MIN_SAMPLE_RATE: float = 0.0


MAX_SAMPLE_RATE: float = 1.0



# ==============================================================================
# Export Constants
# ==============================================================================

DEFAULT_EXPORT_ENABLED: bool = True


DEFAULT_EXPORT_FORMAT: str = "json"


DEFAULT_EXPORT_MODE: str = "batch"


DEFAULT_EXPORT_TIMEOUT: float = 30.0


DEFAULT_EXPORT_BATCH_SIZE: int = 100


SUPPORTED_EXPORT_FORMATS: tuple[str, ...] = (
    "json",
    "yaml",
    "otlp",
    "prometheus",
)


SUPPORTED_EXPORT_MODES: tuple[str, ...] = (
    "sync",
    "async",
    "batch",
)



# ==============================================================================
# Serialization Constants
# ==============================================================================

DEFAULT_ENCODING: str = "utf-8"


DEFAULT_JSON_INDENT: int = 2


DEFAULT_JSON_ASCII: bool = False


DEFAULT_TIMESTAMP_FORMAT: str = "unix"


DEFAULT_SERIALIZATION_FORMAT: str = "json"



# ==============================================================================
# Limits Constants
# ==============================================================================

DEFAULT_HISTORY_LIMIT: int = 1000


DEFAULT_EVENT_LIMIT: int = 1000


DEFAULT_ATTRIBUTE_LIMIT: int = 1000


DEFAULT_TAG_LIMIT: int = 1000


DEFAULT_CONTEXT_LIMIT: int = 1000


DEFAULT_SPAN_LIMIT: int = 10000


MAX_TRACE_NAME_LENGTH: int = 256


MAX_ATTRIBUTE_KEY_LENGTH: int = 256


MAX_TAG_KEY_LENGTH: int = 256


MAX_EVENT_NAME_LENGTH: int = 256



# ==============================================================================
# Default Values
# ==============================================================================

DEFAULT_TRACE_LEVEL: str = "normal"


DEFAULT_TRACE_PRIORITY: int = 0


DEFAULT_TRACE_STATUS: str = "pending"


DEFAULT_TRACE_RESULT: str = "unknown"


DEFAULT_SPAN_KIND: str = "internal"


DEFAULT_SPAN_STATUS: str = "unset"


DEFAULT_TRACER_STATE: str = "created"


DEFAULT_PROCESSING_MODE: str = "sync"


DEFAULT_METRIC_TYPE: str = "counter"



# ==============================================================================
# Lifecycle Defaults
# ==============================================================================

TRACE_CREATED_STATE: str = "created"

TRACE_RUNNING_STATE: str = "running"

TRACE_FINISHED_STATE: str = "finished"

TRACE_FAILED_STATE: str = "failed"

TRACE_CANCELLED_STATE: str = "cancelled"

TRACE_FROZEN_STATE: str = "frozen"

TRACE_CLOSED_STATE: str = "closed"



# ==============================================================================
# Miscellaneous Constants
# ==============================================================================

TRACE_AUTHOR: str = "SciOS-NG"

TRACE_LICENSE: str = "Apache-2.0"


EMPTY_STRING: str = ""

UNKNOWN_VALUE: str = "unknown"


SUCCESS_STATUS: str = "success"

FAILED_STATUS: str = "failed"


UTC_TIMESTAMP_PRECISION: int = 6
# ==============================================================================
# Part 1. Foundation
#
# 1.3 Type Aliases
#
# SciOS-NG Runtime Observability - trace.py
# ==============================================================================


# ==============================================================================
# Identity Types
# ==============================================================================

TraceID = str

SpanID = str


# ==============================================================================
# Time Types
# ==============================================================================

Timestamp = float



# ==============================================================================
# Runtime Mapping Types
# ==============================================================================

AttributeDict = Dict[
    str,
    Any,
]


TagDict = Dict[
    str,
    Any,
]


ContextDict = Dict[
    str,
    Any,
]


MetadataDict = Dict[
    str,
    Any,
]



# ==============================================================================
# JSON Types
# ==============================================================================

JSONPrimitive = Union[
    str,
    int,
    float,
    bool,
    None,
]


JSONValue = Union[
    JSONPrimitive,
    List["JSONValue"],
    Dict[str, "JSONValue"],
]


JSONDict = Dict[
    str,
    JSONValue,
]



# ==============================================================================
# Event Types
# ==============================================================================

EventList = List[
    Any,
]



# ==============================================================================
# Collection Types
# ==============================================================================

AttributeKey = str

TagKey = str

ContextKey = str

EventName = str


TraceName = str

SpanName = str



# ==============================================================================
# Callable Types
# ==============================================================================

HookCallable = Callable[
    [...],
    Any,
]


ExporterCallable = Callable[
    [
        JSONDict
    ],
    Any,
]


ValidatorCallable = Callable[
    [
        Any
    ],
    bool,
]
# ==============================================================================
# Part 1. Foundation
#
# 1.4 Exceptions
#
# SciOS-NG Runtime Observability - trace.py
# ==============================================================================


# ==============================================================================
# Base Trace Exception
# ==============================================================================


class TraceError(Exception):
    """
    Base exception for all tracing related errors.
    """

    def __init__(
        self,
        message: str = "Trace error occurred.",
    ) -> None:

        self.message = message

        super().__init__(
            self.message
        )



# ==============================================================================
# Validation Errors
# ==============================================================================


class TraceValidationError(
    TraceError
):
    """
    Raised when trace validation fails.
    """

    pass



# ==============================================================================
# State Errors
# ==============================================================================


class TraceStateError(
    TraceError
):
    """
    Raised when invalid trace state transition occurs.
    """

    pass



# ==============================================================================
# Serialization Errors
# ==============================================================================


class TraceSerializationError(
    TraceError
):
    """
    Raised when trace serialization or deserialization fails.
    """

    pass



# ==============================================================================
# Export Errors
# ==============================================================================


class TraceExportError(
    TraceError
):
    """
    Raised when trace export operation fails.
    """

    pass



# ==============================================================================
# Span Errors
# ==============================================================================


class SpanError(
    TraceError
):
    """
    Raised when span operation fails.
    """

    pass



# ==============================================================================
# Sampling Errors
# ==============================================================================


class SamplingError(
    TraceError
):
    """
    Raised when sampling operation fails.
    """

    pass



# ==============================================================================
# Tracer Errors
# ==============================================================================


class TracerError(
    TraceError
):
    """
    Raised when tracer operation fails.
    """

    pass
# ==============================================================================
# Part 1. Foundation
#
# 1.5 Enums
#
# SciOS-NG Runtime Observability - trace.py
# ==============================================================================


# ==============================================================================
# Trace Lifecycle Enums
# ==============================================================================


class TraceState(
    StrEnum
):
    """
    Trace lifecycle state.
    """

    CREATED = "created"

    RUNNING = "running"

    FINISHED = "finished"

    FAILED = "failed"

    CANCELLED = "cancelled"

    FROZEN = "frozen"

    CLOSED = "closed"



class TraceStatus(
    StrEnum
):
    """
    Trace execution status.
    """

    PENDING = "pending"

    RUNNING = "running"

    SUCCESS = "success"

    FAILED = "failed"

    CANCELLED = "cancelled"

    CLOSED = "closed"



class TraceResult(
    StrEnum
):
    """
    Trace execution result.
    """

    UNKNOWN = "unknown"

    SUCCESS = "success"

    FAILURE = "failure"

    CANCELLED = "cancelled"

    TIMEOUT = "timeout"



class TracePriority(
    IntEnum
):
    """
    Trace priority level.
    """

    LOW = -1

    NORMAL = 0

    HIGH = 1

    CRITICAL = 2



class TraceLevel(
    StrEnum
):
    """
    Trace verbosity level.
    """

    DEBUG = "debug"

    NORMAL = "normal"

    INFO = "info"

    WARNING = "warning"

    ERROR = "error"

    CRITICAL = "critical"



# ==============================================================================
# Span Enums
# ==============================================================================


class SpanKind(
    StrEnum
):
    """
    Span operation type.
    """

    INTERNAL = "internal"

    SERVER = "server"

    CLIENT = "client"

    PRODUCER = "producer"

    CONSUMER = "consumer"



class SpanState(
    StrEnum
):
    """
    Span lifecycle state.
    """

    CREATED = "created"

    RUNNING = "running"

    FINISHED = "finished"

    ERROR = "error"

    CANCELLED = "cancelled"



class SpanStatus(
    StrEnum
):
    """
    Span execution status.
    """

    UNSET = "unset"

    OK = "ok"
    
    RUNNING = "running"

    SUCCESS = "success"

    ERROR = "error"

    FAILED = "failed"

    CANCELLED = "cancelled"



# ==============================================================================
# Tracer Enums
# ==============================================================================


class TracerType(
    StrEnum
):
    """
    Tracer implementation type.
    """

    DEFAULT = "default"

    LOCAL = "local"

    DISTRIBUTED = "distributed"

    ASYNC = "async"

    REMOTE = "remote"



class TracerState(
    StrEnum
):
    """
    Tracer lifecycle state.
    """

    CREATED = "created"

    INITIALIZED = "initialized"

    RUNNING = "running"

    STOPPED = "stopped"

    FROZEN = "frozen"

    CLOSED = "closed"



# ==============================================================================
# Export Enums
# ==============================================================================


class TraceFormat(
    StrEnum
):
    """
    Trace serialization formats.
    """

    JSON = "json"

    YAML = "yaml"

    OTLP = "otlp"

    PROMETHEUS = "prometheus"



class TraceExportMode(
    StrEnum
):
    """
    Export execution mode.
    """

    SYNC = "sync"

    ASYNC = "async"

    FULL = "full"

    BATCH = "batch"

    STREAM = "stream"

    INCREMENTAL = "incremental"




class ExportState(
    StrEnum
):
    """
    Export lifecycle state.
    """

    CREATED = "created"

    RUNNING = "running"

    COMPLETED = "completed"

    FAILED = "failed"

    CANCELLED = "cancelled"



# ==============================================================================
# Runtime Processing Enums
# ==============================================================================


class SamplingState(
    StrEnum
):
    """
    Sampling decision state.
    """

    UNKNOWN = "unknown"

    SAMPLED = "sampled"

    NOT_SAMPLED = "not_sampled"



class ProcessingMode(
    StrEnum
):
    """
    Runtime processing mode.
    """

    SYNC = "sync"

    ASYNC = "async"

    FULL = "full"

    BATCH = "batch"

    STREAM = "stream"

    INCREMENTAL = "incremental"



# ==============================================================================
# Metrics Enums
# ==============================================================================


class MetricType(
    StrEnum
):
    """
    Metric aggregation type.
    """

    COUNTER = "counter"

    GAUGE = "gauge"

    HISTOGRAM = "histogram"

    SUMMARY = "summary"

    RATE = "rate"
# ==============================================================================
# Part 1. Foundation
#
# 1.6 Protocols
#
# SciOS-NG Runtime Observability - trace.py
# ==============================================================================


# ==============================================================================
# Serializable Protocol
# ==============================================================================


class Serializable(
    Protocol
):
    """
    Object supporting serialization.
    """


    def to_dict(
        self,
    ) -> JSONDict:
        """
        Serialize object to dictionary.
        """

        ...


    def to_json(
        self,
        *,
        indent: int = 2,
    ) -> str:
        """
        Serialize object to JSON string.
        """

        ...



# ==============================================================================
# Validatable Protocol
# ==============================================================================


class Validatable(
    Protocol
):
    """
    Object supporting validation.
    """


    def validate(
        self,
    ) -> bool:
        """
        Validate object state.
        """

        ...



# ==============================================================================
# Snapshotable Protocol
# ==============================================================================


class Snapshotable(
    Protocol
):
    """
    Object supporting snapshot and restore.
    """


    def snapshot(
        self,
    ) -> JSONDict:
        """
        Create object snapshot.
        """

        ...


    def restore(
        self,
        snapshot: Mapping[str, Any],
    ) -> Any:
        """
        Restore object state.
        """

        ...



# ==============================================================================
# Exportable Protocol
# ==============================================================================


class Exportable(
    Protocol
):
    """
    Object supporting external export.
    """


    def export(
        self,
        format: TraceFormat = TraceFormat.JSON,
    ) -> Any:
        """
        Export object.
        """

        ...



# ==============================================================================
# Copyable Protocol
# ==============================================================================


class Copyable(
    Protocol
):
    """
    Object supporting copy operations.
    """


    def copy(
        self,
    ) -> Any:
        """
        Create shallow copy.
        """

        ...


    def clone(
        self,
    ) -> Any:
        """
        Create deep copy.
        """

        ...



# ==============================================================================
# RuntimeObject Protocol
# ==============================================================================


class RuntimeObject(
    Serializable,
    Validatable,
    Snapshotable,
    Copyable,
    Protocol,
):
    """
    Base runtime object protocol.

    All SciOS-NG runtime entities should implement:
    - serialization
    - validation
    - snapshot
    - copy
    """


    id: str


    created_at: Timestamp


    updated_at: Timestamp


    def diagnostics(
        self,
    ) -> JSONDict:
        """
        Runtime diagnostics.
        """

        ...


    def summary(
        self,
    ) -> str:
        """
        Runtime summary.
        """

        ...
# ==============================================================================
# Part 1. Foundation
#
# 1.7 Utility Functions
#
# SciOS-NG Runtime Observability - trace.py
# ==============================================================================


# ==============================================================================
# Identity Generators
# ==============================================================================


def generate_trace_id() -> TraceID:
    """
    Generate unique trace identifier.

    Returns
    -------
    TraceID
        32-character hexadecimal trace id.
    """

    return uuid_lib.uuid4().hex



def generate_span_id() -> SpanID:
    """
    Generate unique span identifier.

    Returns
    -------
    SpanID
        16-character hexadecimal span id.
    """

    return uuid_lib.uuid4().hex[:SPAN_ID_LENGTH]



# ==============================================================================
# Timestamp Utilities
# ==============================================================================


def current_timestamp() -> Timestamp:
    """
    Return current UTC timestamp.

    Returns
    -------
    Timestamp
        Unix timestamp.
    """

    return time.time()



# ==============================================================================
# Serialization Utilities
# ==============================================================================


def serialize_enum(
    value: Any,
) -> Any:
    """
    Serialize enum value safely.

    Parameters
    ----------
    value:
        Any object.

    Returns
    -------
    Any
        Serializable value.
    """

    if isinstance(
        value,
        Enum,
    ):
        return value.value

    return value



# ==============================================================================
# Copy Utilities
# ==============================================================================


def safe_copy(
    value: Any,
) -> Any:
    """
    Create safe deep copy.

    Returns original value if copy fails.
    """

    try:

        return copy.deepcopy(
            value
        )

    except Exception:

        return value



# ==============================================================================
# Type Normalization Utilities
# ==============================================================================


def ensure_mapping(
    value: Optional[
        Mapping[str, Any]
    ],
) -> Dict[str, Any]:
    """
    Ensure mapping object.
    """

    if value is None:

        return {}

    if isinstance(
        value,
        Mapping,
    ):

        return dict(value)

    raise TypeError(
        "Expected mapping type."
    )



def ensure_sequence(
    value: Optional[
        Sequence[Any]
    ],
) -> List[Any]:
    """
    Ensure sequence object.
    """

    if value is None:

        return []

    if isinstance(
        value,
        Sequence,
    ) and not isinstance(
        value,
        (str, bytes),
    ):

        return list(value)

    raise TypeError(
        "Expected sequence type."
    )



# ==============================================================================
# Validation Utilities
# ==============================================================================


def validate_trace_name(
    name: str,
) -> bool:
    """
    Validate trace name.

    Rules:
    - must be string
    - cannot be empty
    - maximum length limited
    """

    if not isinstance(
        name,
        str,
    ):
        return False


    if not name.strip():

        return False


    if len(name) > MAX_TRACE_NAME_LENGTH:

        return False


    return True



def validate_sample_rate(
    rate: float,
) -> bool:
    """
    Validate sampling rate.

    Range:
        0.0 <= rate <= 1.0
    """

    try:

        value = float(rate)

    except Exception:

        return False


    return (
        MIN_SAMPLE_RATE
        <= value
        <= MAX_SAMPLE_RATE
    )



# ==============================================================================
# Formatting Utilities
# ==============================================================================


def format_duration(
    seconds: Optional[float],
) -> str:
    """
    Format duration value.

    Examples
    --------
    0.001 -> 1ms
    1.5   -> 1.500s
    """

    if seconds is None:

        return "unknown"


    if seconds < 0:

        return "invalid"


    if seconds < 1:

        return (
            f"{seconds * 1000:.3f}ms"
        )


    if seconds < 60:

        return (
            f"{seconds:.3f}s"
        )


    minutes = int(
        seconds // 60
    )

    remain = (
        seconds % 60
    )


    return (
        f"{minutes}m {remain:.3f}s"
    )
# ==============================================================================
# Part 1. Foundation
#
# 1.8 __all__
#
# SciOS-NG Runtime Observability - trace.py
# ==============================================================================


# ==============================================================================
# 1.8 __all__
#
# Export list moved to Part 8 Public API
# ==============================================================================
# ==============================================================================
# Part 2. Dataclasses
#
# SciOS-NG Runtime Observability - trace.py
# ==============================================================================


# ==============================================================================
# 2.1 TraceConfiguration
# ==============================================================================


@dataclass
class TraceConfiguration:
    """
    Trace runtime configuration.
    """

    enabled: bool = DEFAULT_ENABLED

    auto_start: bool = DEFAULT_AUTO_START

    auto_finish: bool = DEFAULT_AUTO_FINISH

    timeout: float = DEFAULT_TIMEOUT

    sample_rate: float = DEFAULT_SAMPLE_RATE

    sampling_enabled: bool = DEFAULT_SAMPLING_ENABLED

    export_enabled: bool = DEFAULT_EXPORT_ENABLED

    export_format: TraceFormat = TraceFormat.JSON

    export_mode: TraceExportMode = TraceExportMode.BATCH

    metadata: MetadataDict = field(
        default_factory=dict
    )



# ==============================================================================
# 2.2 Core Runtime Objects
# ==============================================================================


@dataclass
class TraceAttribute:
    """
    Trace attribute key/value.
    """

    key: str

    value: Any

    created_at: Timestamp = field(
        default_factory=current_timestamp
    )



@dataclass
class TraceTag:
    """
    Trace tag object.
    """

    key: str

    value: Any

    created_at: Timestamp = field(
        default_factory=current_timestamp
    )



@dataclass
class TraceEvent:
    """
    Trace event record.
    """

    name: str

    timestamp: Timestamp = field(
        default_factory=current_timestamp
    )

    attributes: AttributeDict = field(
        default_factory=dict
    )



@dataclass
class TraceContext:
    """
    Trace execution context.
    """

    trace_id: TraceID

    span_id: Optional[SpanID] = None

    values: ContextDict = field(
        default_factory=dict
    )



# ==============================================================================
# 2.3 Runtime State
# ==============================================================================


@dataclass
class TraceRuntimeState:
    """
    Runtime execution state.
    """

    initialized: bool = False

    running: bool = False

    finished: bool = False

    cancelled: bool = False

    frozen: bool = False

    closed: bool = False

    started_threads: int = 0

    updated_at: Timestamp = field(
        default_factory=current_timestamp
    )


    def touch(
        self,
    ) -> None:

        self.updated_at = current_timestamp()



    def reset(
        self,
    ) -> None:

        self.initialized = False
        self.running = False
        self.finished = False
        self.cancelled = False
        self.frozen = False
        self.closed = False
        self.started_threads = 0

        self.touch()



# ==============================================================================
# 2.4 Statistics
# ==============================================================================


@dataclass
class TraceStatistics:
    """
    Trace execution statistics.
    """

    span_count: int = 0

    event_count: int = 0

    attribute_count: int = 0

    tag_count: int = 0

    error_count: int = 0

    duration: float = 0.0



@dataclass
class TraceMetrics:
    """
    Trace metrics container.
    """

    counters: Dict[str, int] = field(
        default_factory=dict
    )

    gauges: Dict[str, float] = field(
        default_factory=dict
    )

    values: Dict[str, float] = field(
        default_factory=dict
    )



# ==============================================================================
# 2.5 Serialization Objects
# ==============================================================================


@dataclass
class TraceSnapshot:
    """
    Serializable trace snapshot.
    """

    trace_id: TraceID

    timestamp: Timestamp

    data: JSONDict = field(
        default_factory=dict
    )



@dataclass
class TraceSummary:
    """
    Trace summary.
    """

    trace_id: TraceID

    name: str

    state: TraceState

    duration: Optional[float] = None

    span_count: int = 0



@dataclass
class TraceReport:
    """
    Trace report.
    """

    trace_id: TraceID

    summary: TraceSummary

    statistics: TraceStatistics



@dataclass
class TraceExportResult:
    """
    Trace export result.
    """

    success: bool

    format: TraceFormat

    exported_at: Timestamp = field(
        default_factory=current_timestamp
    )

    message: str = ""

    data: Optional[Any] = None



# ==============================================================================
# 2.6 Diagnostics
# ==============================================================================


@dataclass
class TraceHealth:
    """
    Trace health status.
    """

    healthy: bool = True

    status: str = "ok"

    messages: List[str] = field(
        default_factory=list
    )



@dataclass
class TraceValidationResult:
    """
    Trace validation result.
    """

    valid: bool

    errors: List[str] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )



@dataclass
class TraceDiagnostics:
    """
    Trace diagnostics information.
    """

    trace_id: TraceID

    state: TraceState

    status: TraceStatus

    health: TraceHealth

    details: JSONDict = field(
        default_factory=dict
    )



# ==============================================================================
# 2.7 Search
# ==============================================================================


@dataclass
class TraceSearchResult:
    """
    Search result container.
    """

    matched: bool

    trace_id: Optional[TraceID] = None

    field: Optional[str] = None

    value: Optional[Any] = None



# ==============================================================================
# Part 2 __all__
# ==============================================================================



# ==============================================================================
# Part 3. Span Entity
#
# SciOS-NG Runtime Observability - trace.py
# ==============================================================================


# ==============================================================================
# 3.1 SpanEvent
# ==============================================================================


@dataclass
class SpanEvent:
    """
    Event recorded inside a span.
    """

    name: str

    timestamp: Timestamp = field(
        default_factory=current_timestamp
    )

    attributes: AttributeDict = field(
        default_factory=dict
    )


    def to_dict(
        self,
    ) -> JSONDict:
        """
        Serialize span event.
        """

        return {
            "name": self.name,
            "timestamp": self.timestamp,
            "attributes": dict(self.attributes),
        }



# ==============================================================================
# 3.2 SpanLink
# ==============================================================================


@dataclass
class SpanLink:
    """
    Relationship between spans.
    """

    trace_id: TraceID

    span_id: SpanID

    attributes: AttributeDict = field(
        default_factory=dict
    )


    def to_dict(
        self,
    ) -> JSONDict:
        """
        Serialize span link.
        """

        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "attributes": dict(self.attributes),
        }



# ==============================================================================
# 3.3 SpanStatistics
# ==============================================================================


@dataclass
class SpanStatistics:
    """
    Span runtime statistics.
    """

    event_count: int = 0

    link_count: int = 0

    attribute_count: int = 0

    duration: float = 0.0

    error_count: int = 0


    def reset(
        self,
    ) -> None:
        """
        Reset statistics.
        """

        self.event_count = 0

        self.link_count = 0

        self.attribute_count = 0

        self.duration = 0.0

        self.error_count = 0


    def to_dict(
        self,
    ) -> JSONDict:
        """
        Serialize statistics.
        """

        return {
            "event_count": self.event_count,
            "link_count": self.link_count,
            "attribute_count": self.attribute_count,
            "duration": self.duration,
            "error_count": self.error_count,
        }



# ==============================================================================
# Part 3 __all__
# ==============================================================================

# ==============================================================================
# Part 3.4 TraceSpan
#
# SciOS-NG Runtime Observability - trace.py
# ==============================================================================


class TraceSpan:
    """
    SciOS-NG Span Entity.

    Represents a single operation inside a Trace.

    Responsibilities:
    - span identity
    - lifecycle management
    - attributes/events/links
    - serialization
    - diagnostics
    - statistics
    """


    # ==========================================================================
    # Constructor
    # ==========================================================================


    def __init__(
        self,
        span_id: Optional[SpanID] = None,
        name: Optional[str] = None,
        trace_id: Optional[TraceID] = None,
        parent_id: Optional[SpanID] = None,
        kind: SpanKind = SpanKind.INTERNAL,
    ) -> None:
        """
        Initialize TraceSpan.
        """


        self.span_id: SpanID = (
            span_id
            if span_id is not None
            else generate_span_id()
        )


        self.trace_id: TraceID = (
            trace_id
            if trace_id is not None
            else generate_trace_id()
        )


        self.parent_id: Optional[SpanID] = parent_id


        self.name: str = (
            name
            if name is not None
            else "anonymous.span"
        )


        self.kind: SpanKind = kind


        self.state: SpanState = (
            SpanState.CREATED
        )


        self.status: SpanStatus = (
            SpanStatus.UNSET
        )


        self.started_at: Optional[Timestamp] = None


        self.finished_at: Optional[Timestamp] = None


        self.attributes: AttributeDict = {}


        self.events: List[SpanEvent] = []


        self.links: List[SpanLink] = []


        self.statistics: SpanStatistics = (
            SpanStatistics()
        )


        self.metadata: MetadataDict = {}


        self._lock = RLock()



    # ==========================================================================
    # Properties
    # ==========================================================================


    @property
    def started(
        self,
    ) -> bool:
        """
        Check span started.
        """

        return self.started_at is not None



    @property
    def finished(
        self,
    ) -> bool:
        """
        Check span finished.
        """

        return self.finished_at is not None



    @property
    def duration(
        self,
    ) -> Optional[float]:
        """
        Return span duration.
        """

        if (
            self.started_at is None
            or self.finished_at is None
        ):
            return None


        return (
            self.finished_at
            -
            self.started_at
        )



    # ==========================================================================
    # Lifecycle
    # ==========================================================================


    def start(
        self,
    ) -> "TraceSpan":
        """
        Start span.
        """

        with self._lock:

            if self.started:
                return self


            self.started_at = current_timestamp()


            self.state = SpanState.RUNNING


            return self



    def finish(
        self,
        status: SpanStatus = SpanStatus.OK,
    ) -> "TraceSpan":
        """
        Finish span.
        """

        with self._lock:

            if self.started_at is None:

                self.started_at = current_timestamp()


            self.finished_at = current_timestamp()


            self.status = status


            if status == SpanStatus.OK:

                self.state = SpanState.FINISHED

            else:

                self.state = SpanState.ERROR



            self.statistics.duration = (
                self.duration
                or
                0.0
            )


            return self



    def cancel(
        self,
    ) -> "TraceSpan":
        """
        Cancel span.
        """

        with self._lock:

            self.state = SpanState.CANCELLED

            self.status = SpanStatus.CANCELLED

            self.finished_at = current_timestamp()

            return self



    # ==========================================================================
    # Attributes
    # ==========================================================================


    def set_attribute(
        self,
        key: str,
        value: Any,
    ) -> "TraceSpan":
        """
        Set span attribute.
        """

        with self._lock:

            self.attributes[key] = value

            self.statistics.attribute_count = (
                len(self.attributes)
            )

            return self



    def get_attribute(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Get span attribute.
        """

        return self.attributes.get(
            key,
            default,
        )



    # ==========================================================================
    # Events
    # ==========================================================================


    def add_event(
        self,
        name: str,
        attributes: Optional[AttributeDict] = None,
    ) -> SpanEvent:
        """
        Add span event.
        """

        event = SpanEvent(
            name=name,
            attributes=attributes or {},
        )


        with self._lock:

            self.events.append(
                event
            )


            self.statistics.event_count = (
                len(self.events)
            )


        return event



    # ==========================================================================
    # Links
    # ==========================================================================


    def add_link(
        self,
        link: SpanLink,
    ) -> "TraceSpan":
        """
        Add span link.
        """

        with self._lock:

            self.links.append(
                link
            )


            self.statistics.link_count = (
                len(self.links)
            )


        return self



    # ==========================================================================
    # Snapshot
    # ==========================================================================


    def snapshot(
        self,
    ) -> JSONDict:
        """
        Create snapshot.
        """

        return copy.deepcopy(
            self.to_dict()
        )



    def restore(
        self,
        snapshot: Mapping[str, Any],
    ) -> "TraceSpan":
        """
        Restore snapshot.
        """

        restored = self.from_dict(
            snapshot
        )


        self.__dict__.update(
            restored.__dict__
        )


        return self



    def clone(
        self,
    ) -> "TraceSpan":
        """
        Clone span.
        """

        return copy.deepcopy(
            self
        )



    # ==========================================================================
    # Serialization
    # ==========================================================================


    def to_dict(
        self,
    ) -> JSONDict:
        """
        Serialize span.
        """

        return {

            "span_id": self.span_id,

            "trace_id": self.trace_id,

            "parent_id": self.parent_id,

            "name": self.name,

            "kind": self.kind.value,

            "state": self.state.value,

            "status": self.status.value,

            "started_at": self.started_at,

            "finished_at": self.finished_at,

            "attributes": dict(
                self.attributes
            ),

            "events": [
                e.to_dict()
                for e in self.events
            ],

            "links": [
                l.to_dict()
                for l in self.links
            ],

        }



    def to_json(
        self,
    ) -> str:
        """
        Serialize JSON.
        """

        return json.dumps(
            self.to_dict(),
            default=str,
        )



    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "TraceSpan":
        """
        Create span from dictionary.
        """

        span = cls(
            span_id=data.get(
                "span_id"
            ),
            name=data.get(
                "name"
            ),
            trace_id=data.get(
                "trace_id"
            ),
            parent_id=data.get(
                "parent_id"
            ),
        )


        span.attributes.update(
            data.get(
                "attributes",
                {},
            )
        )


        return span



    @classmethod
    def from_json(
        cls,
        data: str,
    ) -> "TraceSpan":

        return cls.from_dict(
            json.loads(data)
        )



    # ==========================================================================
    # Validation
    # ==========================================================================


    def validate(
        self,
    ) -> bool:
        """
        Validate span.
        """

        return bool(
            self.span_id
            and self.name
        )



    # ==========================================================================
    # Diagnostics
    # ==========================================================================


    def diagnostics(
        self,
    ) -> JSONDict:
        """
        Return diagnostics.
        """

        return {

            "span_id": self.span_id,

            "state": self.state.value,

            "status": self.status.value,

            "duration": self.duration,

            "events": len(self.events),

        }



    # ==========================================================================
    # Statistics
    # ==========================================================================


    def get_statistics(
        self,
    ) -> SpanStatistics:
        """
        Return statistics.
        """

        return self.statistics



    # ==========================================================================
    # Summary
    # ==========================================================================


    def summary(
        self,
    ) -> str:
        """
        Human readable summary.
        """

        return (
            f"Span<{self.name}> "
            f"{self.state.value}"
        )



    # ==========================================================================
    # Python Protocols
    # ==========================================================================


    def __repr__(
        self,
    ) -> str:

        return (
            f"<TraceSpan "
            f"name={self.name} "
            f"id={self.span_id}>"
        )



    def __str__(
        self,
    ) -> str:

        return self.summary()



    def __len__(
        self,
    ) -> int:

        return len(
            self.events
        )



    def __contains__(
        self,
        key: str,
    ) -> bool:

        return key in self.attributes



    def __getitem__(
        self,
        key: str,
    ) -> Any:

        return self.attributes[key]



    def __setitem__(
        self,
        key: str,
        value: Any,
    ) -> None:

        self.set_attribute(
            key,
            value,
        )



# ==============================================================================
# Part 3 __all__
# ==============================================================================

# Part 2 exports collected in final __all__

# ==============================================================================
# Part 4. Trace Entity
# 4.1 Constructor
# ==============================================================================


class Trace:
    """
    SciOS-NG Trace Entity.

    Represents one execution trace.

    Responsibilities:
    - trace identity
    - lifecycle ownership
    - span management
    - attributes/tags/events/context storage
    - runtime state
    - statistics and metrics
    """


    def __init__(
        self,
        trace_id: Optional[TraceID] = None,
        name: Optional[str] = None,
        spans: Optional[
            Sequence["TraceSpan"]
        ] = None,
        attributes: Optional[
            Mapping[str, Any]
        ] = None,
        configuration: Optional[
            TraceConfiguration
        ] = None,
    ) -> None:
        """
        Initialize Trace Entity.
        """


        # ==========================================================================
        # Identity
        # ==========================================================================

        self.trace_id: TraceID = (
            trace_id
            if trace_id is not None
            else generate_trace_id()
        )


        self.name: str = (
            name
            if name is not None
            else DEFAULT_TRACE_NAME
        )


        # ==========================================================================
        # Validation Identity
        # ==========================================================================

        if not validate_trace_name(
            self.name
        ):
            raise TraceValidationError(
                "Invalid trace name"
            )


        # ==========================================================================
        # Span Container
        # ==========================================================================

        self.spans: List[
            "TraceSpan"
        ] = list(
            spans or []
        )


        # ==========================================================================
        # Data Containers
        # ==========================================================================

        self.attributes: AttributeDict = (
            dict(attributes or {})
        )


        self.tags: TagDict = {}


        self.events: EventList = []


        self.context: ContextDict = {}


        self.metadata: MetadataDict = {}



        # ==========================================================================
        # Configuration
        # ==========================================================================

        self.configuration: TraceConfiguration = (
            configuration
            if configuration is not None
            else TraceConfiguration()
        )



        # ==========================================================================
        # Lifecycle Timestamp
        # ==========================================================================

        self.created_at: Timestamp = (
            current_timestamp()
        )


        self.updated_at: Timestamp = (
            self.created_at
        )


        self.started_at: Optional[
            Timestamp
        ] = None


        self.finished_at: Optional[
            Timestamp
        ] = None



        # ==========================================================================
        # State Machine
        # ==========================================================================

        self.state: TraceState = (
            TraceState.CREATED
        )


        self.status: TraceStatus = (
            TraceStatus.PENDING
        )


        self.result: TraceResult = (
            TraceResult.UNKNOWN
        )


        self.priority: TracePriority = (
            TracePriority.NORMAL
        )


        self.level: TraceLevel = (
            TraceLevel.NORMAL
        )



        # ==========================================================================
        # Runtime State
        # ==========================================================================

        self.runtime: TraceRuntimeState = (
            TraceRuntimeState()
        )



        # ==========================================================================
        # Statistics
        # ==========================================================================

        self.statistics: TraceStatistics = (
            TraceStatistics()
        )


        self.metrics: TraceMetrics = (
            TraceMetrics()
        )



        # ==========================================================================
        # Diagnostics
        # ==========================================================================

        self.last_error: Optional[str] = None


        self.warnings: List[str] = []



        # ==========================================================================
        # Internal
        # ==========================================================================

        self._lock: RLock = RLock()
# ==============================================================================
# Part 4.2 Properties
# ==============================================================================


    @property
    def started(
        self,
    ) -> bool:
        """
        Check whether trace has started.
        """

        return (
            self.started_at is not None
        )



    @property
    def finished(
        self,
    ) -> bool:
        """
        Check whether trace has finished.
        """

        return (
            self.finished_at is not None
        )



    @property
    def cancelled(
        self,
    ) -> bool:
        """
        Check whether trace was cancelled.
        """

        return (
            self.state == TraceState.CANCELLED
            or self.status == TraceStatus.CANCELLED
        )



    @property
    def frozen(
        self,
    ) -> bool:
        """
        Check whether trace is frozen.
        """

        if hasattr(
            self.runtime,
            "frozen",
        ):
            return bool(
                self.runtime.frozen
            )

        return (
            self.state == TraceState.FROZEN
        )



    @property
    def closed(
        self,
    ) -> bool:
        """
        Check whether trace is closed.
        """

        if hasattr(
            self.runtime,
            "closed",
        ):
            return bool(
                self.runtime.closed
            )

        return (
            self.state == TraceState.CLOSED
        )



    @property
    def active(
        self,
    ) -> bool:
        """
        Check whether trace is active.

        Active states:
        - running
        - started but not finished
        """

        return (
            self.started
            and not self.finished
            and not self.cancelled
            and not self.closed
        )



    @property
    def duration(
        self,
    ) -> Optional[float]:
        """
        Trace execution duration in seconds.
        """

        if self.started_at is None:
            return None


        end_time = (
            self.finished_at
            if self.finished_at is not None
            else current_timestamp()
        )


        return (
            end_time - self.started_at
        )



    @property
    def span_count(
        self,
    ) -> int:
        """
        Number of spans.
        """

        return len(
            self.spans
        )



    @property
    def event_count(
        self,
    ) -> int:
        """
        Number of trace events.
        """

        return len(
            self.events
        )



    @property
    def attribute_count(
        self,
    ) -> int:
        """
        Number of attributes.
        """

        return len(
            self.attributes
        )



    @property
    def tag_count(
        self,
    ) -> int:
        """
        Number of tags.
        """

        return len(
            self.tags
        )



    @property
    def is_valid(
        self,
    ) -> bool:
        """
        Validate basic trace identity.
        """

        try:

            return (
                bool(self.trace_id)
                and validate_trace_name(
                    self.name
                )
            )

        except Exception:

            return False
# ==============================================================================
# Part 4.3 Lifecycle
# ==============================================================================


    def start(
        self,
    ) -> "Trace":
        """
        Start trace execution.

        Transition:
            CREATED -> RUNNING
        """

        with self._lock:

            if self.started:
                return self


            now = current_timestamp()


            self.started_at = now

            self.updated_at = now


            self.state = TraceState.RUNNING

            self.status = TraceStatus.RUNNING

            self.result = TraceResult.UNKNOWN


            self.runtime.initialized = True

            self.runtime.running = True

            self.runtime.finished = False

            self.runtime.cancelled = False


            if hasattr(
                self.runtime,
                "touch",
            ):
                self.runtime.touch()


            return self



    def finish(
        self,
        result: TraceResult = TraceResult.SUCCESS,
    ) -> "Trace":
        """
        Finish trace execution.

        Transition:
            RUNNING -> FINISHED
        """

        with self._lock:

            now = current_timestamp()


            if self.started_at is None:
                self.started_at = now


            self.finished_at = now

            self.updated_at = now


            self.result = result


            self.state = TraceState.FINISHED


            if result == TraceResult.SUCCESS:

                self.status = TraceStatus.SUCCESS

            elif result == TraceResult.CANCELLED:

                self.status = TraceStatus.CANCELLED

            else:

                self.status = TraceStatus.FAILED



            self.runtime.running = False

            self.runtime.finished = True



            if hasattr(
                self.runtime,
                "touch",
            ):
                self.runtime.touch()


            return self



    def reset(
        self,
    ) -> "Trace":
        """
        Reset lifecycle state.

        Keeps:
        - trace identity
        - configuration

        Clears:
        - runtime lifecycle
        """

        with self._lock:

            self.started_at = None

            self.finished_at = None


            self.state = TraceState.CREATED

            self.status = TraceStatus.PENDING

            self.result = TraceResult.UNKNOWN


            self.last_error = None

            self.warnings.clear()


            if hasattr(
                self.runtime,
                "reset",
            ):
                self.runtime.reset()


            self.updated_at = current_timestamp()


            return self



    def restart(
        self,
    ) -> "Trace":
        """
        Restart trace execution.

        Equivalent:

            reset()
            start()
        """

        with self._lock:

            self.reset()

            self.start()


            return self



    def cancel(
        self,
        reason: Optional[str] = None,
    ) -> "Trace":
        """
        Cancel trace execution.
        """

        with self._lock:

            self.state = TraceState.CANCELLED

            self.status = TraceStatus.CANCELLED

            self.result = TraceResult.CANCELLED


            self.runtime.running = False

            self.runtime.cancelled = True


            if reason:

                self.last_error = reason


            self.updated_at = current_timestamp()


            if hasattr(
                self.runtime,
                "touch",
            ):
                self.runtime.touch()


            return self



    def freeze(
        self,
    ) -> "Trace":
        """
        Freeze trace mutation.
        """

        with self._lock:

            self.state = TraceState.FROZEN


            self.runtime.frozen = True


            self.updated_at = current_timestamp()


            if hasattr(
                self.runtime,
                "touch",
            ):
                self.runtime.touch()


            return self



    def unfreeze(
        self,
    ) -> "Trace":
        """
        Unfreeze trace.
        """

        with self._lock:

            self.runtime.frozen = False


            if self.finished:

                self.state = TraceState.FINISHED


            elif self.started:

                self.state = TraceState.RUNNING


            else:

                self.state = TraceState.CREATED



            self.updated_at = current_timestamp()


            if hasattr(
                self.runtime,
                "touch",
            ):
                self.runtime.touch()


            return self



    def close(
        self,
    ) -> "Trace":
        """
        Permanently close trace.

        Transition:

            ANY -> CLOSED
        """

        with self._lock:

            self.state = TraceState.CLOSED

            self.status = TraceStatus.CLOSED


            self.runtime.running = False

            self.runtime.closed = True


            self.updated_at = current_timestamp()


            if hasattr(
                self.runtime,
                "touch",
            ):
                self.runtime.touch()


            return self
# ==============================================================================
# Part 4.4 – Attributes
# ==============================================================================


    def set_attribute(
        self,
        key: str,
        value: Any,
    ) -> "Trace":
        """
        Set trace attribute.

        Parameters
        ----------
        key:
            Attribute name.

        value:
            Attribute value.
        """

        with self._lock:

            if not key:
                raise TraceValidationError(
                    "Attribute key cannot be empty"
                )

            self.attributes[key] = value

            self.updated_at = time.time()

            return self



    def get_attribute(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Get trace attribute.
        """

        with self._lock:

            return self.attributes.get(
                key,
                default,
            )



    def has_attribute(
        self,
        key: str,
    ) -> bool:
        """
        Check attribute existence.
        """

        with self._lock:

            return key in self.attributes



    def remove_attribute(
        self,
        key: str,
    ) -> Any:
        """
        Remove trace attribute.

        Returns removed value.
        """

        with self._lock:

            value = self.attributes.pop(
                key,
                None,
            )

            self.updated_at = time.time()

            return value



    def update_attributes(
        self,
        attributes: Mapping[str, Any],
    ) -> "Trace":
        """
        Update multiple attributes.
        """

        with self._lock:

            if attributes:

                self.attributes.update(
                    attributes
                )

                self.updated_at = time.time()


            return self



    def clear_attributes(
        self,
    ) -> "Trace":
        """
        Remove all attributes.
        """

        with self._lock:

            self.attributes.clear()

            self.updated_at = time.time()

            return self



    def iter_attributes(
        self,
    ) -> Iterator[
        Tuple[str, Any]
    ]:
        """
        Iterate trace attributes.
        """

        with self._lock:

            yield from (
                self.attributes.items()
            )
# ==============================================================================
# Part 4.5 – Tags
# ==============================================================================


    def set_tag(
        self,
        key: str,
        value: Any,
    ) -> "Trace":
        """
        Set trace tag.

        Parameters
        ----------
        key:
            Tag name.

        value:
            Tag value.
        """

        with self._lock:

            if not key:
                raise TraceValidationError(
                    "Tag key cannot be empty"
                )

            self.tags[key] = value

            self.updated_at = time.time()

            return self



    def get_tag(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Get trace tag.
        """

        with self._lock:

            return self.tags.get(
                key,
                default,
            )



    def has_tag(
        self,
        key: str,
    ) -> bool:
        """
        Check tag existence.
        """

        with self._lock:

            return key in self.tags



    def remove_tag(
        self,
        key: str,
    ) -> Any:
        """
        Remove trace tag.

        Returns
        -------
        Any
            Removed tag value.
        """

        with self._lock:

            value = self.tags.pop(
                key,
                None,
            )

            self.updated_at = time.time()

            return value



    def update_tags(
        self,
        tags: Mapping[str, Any],
    ) -> "Trace":
        """
        Update multiple tags.
        """

        with self._lock:

            if tags:

                self.tags.update(
                    tags
                )

                self.updated_at = time.time()


            return self



    def clear_tags(
        self,
    ) -> "Trace":
        """
        Remove all tags.
        """

        with self._lock:

            self.tags.clear()

            self.updated_at = time.time()

            return self



    def iter_tags(
        self,
    ) -> Iterator[
        Tuple[str, Any]
    ]:
        """
        Iterate trace tags.
        """

        with self._lock:

            yield from (
                self.tags.items()
            )
# ==============================================================================
# Part 4.6 – Events
# ==============================================================================


    def add_event(
        self,
        event: Any,
    ) -> "Trace":
        """
        Add trace event.

        Parameters
        ----------
        event:
            Event object or dictionary.
        """

        with self._lock:

            self.events.append(
                event
            )

            self.updated_at = time.time()

            return self



    def extend_events(
        self,
        events: Iterable[Any],
    ) -> "Trace":
        """
        Add multiple trace events.
        """

        with self._lock:

            self.events.extend(
                events
            )

            self.updated_at = time.time()

            return self



    def get_event(
        self,
        index: int,
    ) -> Any:
        """
        Get event by index.
        """

        with self._lock:

            if index < 0:
                index += len(
                    self.events
                )


            if (
                index < 0
                or index >= len(self.events)
            ):
                raise IndexError(
                    "Event index out of range"
                )


            return self.events[index]



    def iter_events(
        self,
    ) -> Iterator[Any]:
        """
        Iterate trace events.
        """

        with self._lock:

            yield from self.events



    def clear_events(
        self,
    ) -> "Trace":
        """
        Remove all events.
        """

        with self._lock:

            self.events.clear()

            self.updated_at = time.time()

            return self



    def remove_event(
        self,
        event: Any,
    ) -> bool:
        """
        Remove specific event.

        Returns
        -------
        bool
            True if removed.
        """

        with self._lock:

            try:

                self.events.remove(
                    event
                )

                self.updated_at = time.time()

                return True


            except ValueError:

                return False
# ==============================================================================
# Part 4.7 – Context
# ==============================================================================


    def set_context(
        self,
        key: str,
        value: Any,
    ) -> "Trace":
        """
        Set trace context value.
        """

        with self._lock:

            if not key:
                raise TraceValidationError(
                    "Context key cannot be empty"
                )

            self.context[key] = value

            self.updated_at = time.time()

            return self



    def get_context(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Get trace context value.
        """

        with self._lock:

            return self.context.get(
                key,
                default,
            )



    def update_context(
        self,
        context: Mapping[str, Any],
    ) -> "Trace":
        """
        Update multiple context values.
        """

        with self._lock:

            if context:

                self.context.update(
                    context
                )

                self.updated_at = time.time()


            return self



    def clear_context(
        self,
    ) -> "Trace":
        """
        Clear all trace context.
        """

        with self._lock:

            self.context.clear()

            self.updated_at = time.time()

            return self



    def context_copy(
        self,
    ) -> ContextDict:
        """
        Return a copy of trace context.
        """

        with self._lock:

            return copy.deepcopy(
                self.context
            )
# ==============================================================================
# Part 4.8 – Span Management
# ==============================================================================


    def create_span(
        self,
        name: str = DEFAULT_SPAN_NAME,
        **kwargs: Any,
    ) -> "TraceSpan":
        """
        Create and attach a new span.

        Parameters
        ----------
        name:
            Span name.

        Returns
        -------
        TraceSpan
        """

        with self._lock:

            span = TraceSpan(
                trace_id=self.trace_id,
                name=name,
                **kwargs,
            )

            self.spans.append(span)

            self.updated_at = time.time()

            return span



    def add_span(
        self,
        span: TraceSpan,
    ) -> "Trace":
        """
        Add existing span to trace.
        """

        with self._lock:

            if span not in self.spans:

                self.spans.append(
                    span
                )

                self.updated_at = time.time()

            return self



    def remove_span(
        self,
        span_id: SpanID,
    ) -> bool:
        """
        Remove span by id.
        """

        with self._lock:

            for index, span in enumerate(self.spans):

                if getattr(
                    span,
                    "span_id",
                    None,
                ) == span_id:

                    del self.spans[index]

                    self.updated_at = time.time()

                    return True

            return False



    def get_span(
        self,
        span_id: SpanID,
    ) -> Optional["TraceSpan"]:
        """
        Get span by id.
        """

        with self._lock:

            for span in self.spans:

                if getattr(
                    span,
                    "span_id",
                    None,
                ) == span_id:

                    return span

            return None



    def find_span(
        self,
        predicate: Optional[
            Callable[["TraceSpan"], bool]
        ] = None,
        name: Optional[str] = None,
    ) -> Optional["TraceSpan"]:
        """
        Find first matching span.
        """

        with self._lock:

            for span in self.spans:

                if predicate is not None:

                    if predicate(span):

                        return span


                elif name is not None:

                    if getattr(
                        span,
                        "name",
                        None,
                    ) == name:

                        return span


            return None



    def iter_spans(
        self,
    ) -> Iterator["TraceSpan"]:
        """
        Iterate spans.
        """

        with self._lock:

            yield from list(
                self.spans
            )



    def clear_spans(
        self,
    ) -> "Trace":
        """
        Remove all spans.
        """

        with self._lock:

            self.spans.clear()

            self.updated_at = time.time()

            return self



    def root_span(
        self,
    ) -> Optional["TraceSpan"]:
        """
        Return root span.

        The first span without parent.
        """

        with self._lock:

            if not self.spans:

                return None


            for span in self.spans:

                parent_id = getattr(
                    span,
                    "parent_span_id",
                    None,
                )

                if parent_id is None:

                    return span


            return self.spans[0]
# ==============================================================================
# Part 4.9 – Snapshot
# ==============================================================================


    def snapshot(
        self,
    ) -> TraceSnapshot:
        """
        Create immutable snapshot of current trace state.
        """

        with self._lock:

            return TraceSnapshot(
                trace_id=self.trace_id,
                data=copy.deepcopy(
                    self.to_dict()
                ),
                created_at=time.time(),
            )



    def restore(
        self,
        snapshot: Union[
            TraceSnapshot,
            Mapping[str, Any],
        ],
    ) -> "Trace":
        """
        Restore trace from snapshot.
        """

        with self._lock:

            if isinstance(
                snapshot,
                TraceSnapshot,
            ):

                data = snapshot.data

            else:

                data = snapshot


            restored = Trace.from_dict(
                data
            )


            self.__dict__.update(
                restored.__dict__
            )


            self.updated_at = time.time()


            if hasattr(
                self.runtime,
                "touch",
            ):

                self.runtime.touch()


            return self



    def clone(
        self,
    ) -> "Trace":
        """
        Create deep clone of trace.
        """

        with self._lock:

            return copy.deepcopy(
                self
            )



    def copy(
        self,
    ) -> "Trace":
        """
        Create shallow copy of trace.
        """

        with self._lock:

            return copy.copy(
                self
            )



    def save_state(
        self,
    ) -> Dict[str, Any]:
        """
        Save current trace state.

        Alias of snapshot().
        """

        snapshot = self.snapshot()


        if isinstance(
            snapshot,
            TraceSnapshot,
        ):

            return copy.deepcopy(
                snapshot.data
            )


        return copy.deepcopy(
            snapshot
        )



    def load_state(
        self,
        state: Mapping[str, Any],
    ) -> "Trace":
        """
        Load previously saved trace state.

        Alias of restore().
        """

        return self.restore(
            state
        )
# ==============================================================================
# Part 4.10 – Serialization
# ==============================================================================


    def to_dict(
        self,
        include_spans: bool = True,
        include_statistics: bool = True,
        include_runtime: bool = True,
        include_metadata: bool = True,
    ) -> Dict[str, Any]:
        """
        Serialize Trace entity to dictionary.
        """

        with self._lock:

            data: Dict[str, Any] = {

                # Identity
                "trace_id": self.trace_id,
                "name": self.name,

                # State
                "state": serialize_enum(
                    self.state
                ),
                "status": serialize_enum(
                    self.status
                ),
                "result": serialize_enum(
                    self.result
                ),
                "priority": serialize_enum(
                    self.priority
                ),
                "level": serialize_enum(
                    self.level
                ),

                # Collections
                "attributes": copy.deepcopy(
                    self.attributes
                ),
                "tags": copy.deepcopy(
                    self.tags
                ),
                "events": copy.deepcopy(
                    self.events
                ),
                "context": copy.deepcopy(
                    self.context
                ),

                # Lifecycle
                "created_at": self.created_at,
                "updated_at": self.updated_at,
                "started_at": self.started_at,
                "finished_at": self.finished_at,

            }


            if include_metadata:

                data["metadata"] = copy.deepcopy(
                    self.metadata
                )


            if include_spans:

                data["spans"] = [

                    (
                        span.to_dict()
                        if hasattr(
                            span,
                            "to_dict",
                        )
                        else span
                    )

                    for span in self.spans
                ]


            if include_runtime:

                if hasattr(
                    self.runtime,
                    "to_dict",
                ):

                    data["runtime"] = (
                        self.runtime.to_dict()
                    )


            if include_statistics:

                if hasattr(
                    self.trace_statistics,
                    "to_dict",
                ):

                    data["trace_statistics"] = (
                        self.trace_statistics.to_dict()
                    )


                if hasattr(
                    self.metrics,
                    "to_dict",
                ):

                    data["metrics"] = (
                        self.metrics.to_dict()
                    )


            return data



    def to_json(
        self,
        *,
        indent: int = 2,
        ensure_ascii: bool = False,
    ) -> str:
        """
        Serialize Trace entity to JSON.
        """

        try:

            return json.dumps(
                self.to_dict(),
                indent=indent,
                ensure_ascii=ensure_ascii,
                default=str,
            )

        except Exception as exc:

            raise TraceSerializationError(
                str(exc)
            ) from exc



    def to_yaml(
        self,
    ) -> str:
        """
        Serialize Trace entity to YAML.

        Requires PyYAML.
        """

        try:

            import yaml

            return yaml.safe_dump(
                self.to_dict(),
                allow_unicode=True,
                sort_keys=False,
            )

        except ImportError as exc:

            raise TraceSerializationError(
                "PyYAML is required"
            ) from exc



    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "Trace":
        """
        Restore Trace entity from dictionary.
        """

        trace = cls(

            trace_id=data.get(
                "trace_id"
            ),

            name=data.get(
                "name"
            ),

            attributes=data.get(
                "attributes",
                {},
            ),

        )


        trace.tags.update(
            data.get(
                "tags",
                {},
            )
        )


        trace.events.extend(
            data.get(
                "events",
                [],
            )
        )


        trace.context.update(
            data.get(
                "context",
                {},
            )
        )


        trace.metadata.update(
            data.get(
                "metadata",
                {},
            )
        )


        trace.created_at = data.get(
            "created_at",
            trace.created_at,
        )


        trace.updated_at = data.get(
            "updated_at",
            trace.updated_at,
        )


        trace.started_at = data.get(
            "started_at"
        )


        trace.finished_at = data.get(
            "finished_at"
        )


        if "state" in data:

            trace.state = TraceState(
                data["state"]
            )


        if "status" in data:

            trace.status = TraceStatus(
                data["status"]
            )


        if "result" in data:

            trace.result = TraceResult(
                data["result"]
            )


        if "priority" in data:

            trace.priority = TracePriority(
                data["priority"]
            )


        if "level" in data:

            trace.level = TraceLevel(
                data["level"]
            )


        if "runtime" in data:

            if hasattr(
                trace.runtime,
                "from_dict",
            ):

                trace.runtime = (
                    TraceRuntimeState.from_dict(
                        data["runtime"]
                    )
                )


        return trace



    @classmethod
    def from_json(
        cls,
        data: str,
    ) -> "Trace":
        """
        Restore Trace entity from JSON.
        """

        try:

            payload = json.loads(
                data
            )

            return cls.from_dict(
                payload
            )


        except Exception as exc:

            raise TraceSerializationError(
                str(exc)
            ) from exc



    @classmethod
    def from_yaml(
        cls,
        data: str,
    ) -> "Trace":
        """
        Restore Trace entity from YAML.
        """

        try:

            import yaml

            payload = yaml.safe_load(
                data
            )

            return cls.from_dict(
                payload
            )


        except ImportError as exc:

            raise TraceSerializationError(
                "PyYAML is required"
            ) from exc
# ==============================================================================
# Part 4.11 – Validation
# ==============================================================================


    def validate(
        self,
    ) -> TraceValidationResult:
        """
        Validate complete Trace entity.

        Checks:
        - identity
        - state
        - spans
        - events
        - attributes
        """

        with self._lock:

            errors: List[str] = []


            # --------------------------------------------------------------
            # Identity validation
            # --------------------------------------------------------------

            if not self.trace_id:

                errors.append(
                    "trace_id is empty"
                )


            if not self.name:

                errors.append(
                    "trace name is empty"
                )


            # --------------------------------------------------------------
            # State validation
            # --------------------------------------------------------------

            state_result = (
                self.validate_state()
            )

            errors.extend(
                state_result
            )


            # --------------------------------------------------------------
            # Span validation
            # --------------------------------------------------------------

            span_result = (
                self.validate_spans()
            )

            errors.extend(
                span_result
            )


            # --------------------------------------------------------------
            # Event validation
            # --------------------------------------------------------------

            event_result = (
                self.validate_events()
            )

            errors.extend(
                event_result
            )


            return TraceValidationResult(

                valid=(
                    len(errors) == 0
                ),

                errors=errors,

                checked_at=time.time(),

            )



    def validate_state(
        self,
    ) -> List[str]:
        """
        Validate lifecycle state.
        """

        errors: List[str] = []


        if self.state == TraceState.RUNNING:

            if self.started_at is None:

                errors.append(
                    "RUNNING trace has no started_at"
                )


        if self.state == TraceState.FINISHED:

            if self.finished_at is None:

                errors.append(
                    "FINISHED trace has no finished_at"
                )


        if (
            self.finished_at is not None
            and self.started_at is not None
        ):

            if self.finished_at < self.started_at:

                errors.append(
                    "finished_at before started_at"
                )


        return errors



    def validate_spans(
        self,
    ) -> List[str]:
        """
        Validate trace spans.
        """

        errors: List[str] = []


        span_ids = set()


        for index, span in enumerate(
            self.spans
        ):

            span_id = getattr(
                span,
                "span_id",
                None,
            )


            if span_id is None:

                errors.append(
                    f"span[{index}] missing span_id"
                )


            else:

                if span_id in span_ids:

                    errors.append(
                        f"duplicate span_id: {span_id}"
                    )

                span_ids.add(
                    span_id
                )


            if hasattr(
                span,
                "validate",
            ):

                result = span.validate()


                if hasattr(
                    result,
                    "errors",
                ):

                    errors.extend(
                        result.errors
                    )


        return errors



    def validate_events(
        self,
    ) -> List[str]:
        """
        Validate trace events.
        """

        errors: List[str] = []


        for index, event in enumerate(
            self.events
        ):

            if event is None:

                errors.append(
                    f"event[{index}] is None"
                )


        return errors



    def validate_attributes(
        self,
    ) -> List[str]:
        """
        Validate trace attributes.
        """

        errors: List[str] = []


        for key in self.attributes:

            if not isinstance(
                key,
                str,
            ):

                errors.append(
                    "attribute key must be string"
                )


        return errors
# ==============================================================================
# Part 4.12 – Diagnostics
# ==============================================================================


    def diagnostics(
        self,
    ) -> TraceDiagnostics:
        """
        Collect complete trace diagnostics.
        """

        with self._lock:

            validation = self.validate()


            return TraceDiagnostics(

                trace_id=self.trace_id,

                name=self.name,

                state=self.state,

                status=self.status,

                result=self.result,

                valid=validation.valid,

                errors=list(
                    validation.errors
                ),

                warnings=list(
                    self.warnings
                ),

                statistics={
                    "span_count": len(self.spans),
                    "event_count": len(self.events),
                    "attribute_count": len(self.attributes),
                    "tag_count": len(self.tags),
                },

                runtime=(
                    self.runtime.to_dict()
                    if hasattr(
                        self.runtime,
                        "to_dict",
                    )
                    else {}
                ),

                generated_at=time.time(),

            )



    def health(
        self,
    ) -> TraceHealth:
        """
        Evaluate trace health.
        """

        with self._lock:

            validation = self.validate()


            healthy = (
                validation.valid
                and self.state != TraceState.CLOSED
            )


            return TraceHealth(

                healthy=healthy,

                status=(
                    "healthy"
                    if healthy
                    else "unhealthy"
                ),

                trace_id=self.trace_id,

                checks={

                    "identity": bool(
                        self.trace_id
                    ),

                    "state": (
                        self.validate_state()
                        == []
                    ),

                    "spans": (
                        self.validate_spans()
                        == []
                    ),

                    "events": (
                        self.validate_events()
                        == []
                    ),

                },

                checked_at=time.time(),

            )



    def inspect(
        self,
    ) -> Dict[str, Any]:
        """
        Return detailed runtime inspection.
        """

        with self._lock:

            return {

                "trace_id": self.trace_id,

                "name": self.name,

                "state": serialize_enum(
                    self.state
                ),

                "status": serialize_enum(
                    self.status
                ),

                "result": serialize_enum(
                    self.result
                ),

                "started": self.started,

                "finished": self.finished,

                "duration": self.duration,

                "spans": len(
                    self.spans
                ),

                "events": len(
                    self.events
                ),

                "attributes": len(
                    self.attributes
                ),

                "tags": len(
                    self.tags
                ),

                "valid": self.is_valid,

            }



    def status(
        self,
    ) -> Dict[str, Any]:
        """
        Return current trace status.
        """

        with self._lock:

            return {

                "trace_id": self.trace_id,

                "state": serialize_enum(
                    self.state
                ),

                "status": serialize_enum(
                    self.status
                ),

                "result": serialize_enum(
                    self.result
                ),

                "active": self.active,

                "started": self.started,

                "finished": self.finished,

                "duration": self.duration,

            }



    def api_summary(
        self,
    ) -> Dict[str, Any]:
        """
        Return public API summary.
        """

        return {

            "entity": "Trace",

            "version": TRACE_VERSION,

            "trace_id": self.trace_id,

            "name": self.name,

            "methods": [

                "start",

                "finish",

                "reset",

                "restart",

                "cancel",

                "freeze",

                "unfreeze",

                "close",

                "set_attribute",

                "set_tag",

                "add_event",

                "set_context",

                "create_span",

                "snapshot",

                "restore",

                "to_dict",

                "to_json",

                "validate",

                "diagnostics",

                "summary",

            ],

            "properties": [

                "started",

                "finished",

                "cancelled",

                "frozen",

                "closed",

                "active",

                "duration",

                "span_count",

                "event_count",

                "attribute_count",

                "tag_count",

                "is_valid",

            ],

        }
# ==============================================================================
# Part 4.13 – Statistics
# ==============================================================================


    def update_statistics(
        self,
    ) -> TraceStatistics:
        """
        Update trace statistics.

        Returns
        -------
        TraceStatistics
            Updated statistics object.
        """

        with self._lock:

            now = time.time()


            self.trace_statistics.trace_count = 1

            self.trace_statistics.span_count = len(
                self.spans
            )

            self.trace_statistics.event_count = len(
                self.events
            )

            self.trace_statistics.attribute_count = len(
                self.attributes
            )

            self.trace_statistics.tag_count = len(
                self.tags
            )


            self.trace_statistics.duration = (
                self.duration
            )


            self.trace_statistics.updated_at = now


            return self.trace_statistics



    def reset_statistics(
        self,
    ) -> "Trace":
        """
        Reset trace statistics and metrics.
        """

        with self._lock:

            self.statistics = (
                TracerStatistics()
            )


            self.trace_statistics = (
                TraceStatistics()
            )


            self.metrics = (
                TraceMetrics()
            )


            self.updated_at = time.time()


            return self



    def runtime_statistics(
        self,
    ) -> Dict[str, Any]:
        """
        Return runtime statistics.
        """

        with self._lock:

            self.update_statistics()


            return {

                "trace_id": self.trace_id,

                "name": self.name,

                "state": serialize_enum(
                    self.state
                ),

                "status": serialize_enum(
                    self.status
                ),

                "duration": self.duration,

                "started": self.started,

                "finished": self.finished,

                "spans": len(
                    self.spans
                ),

                "events": len(
                    self.events
                ),

                "attributes": len(
                    self.attributes
                ),

                "tags": len(
                    self.tags
                ),

                "statistics": (
                    self.trace_statistics.to_dict()
                    if hasattr(
                        self.trace_statistics,
                        "to_dict",
                    )
                    else {}
                ),

            }



    def metrics(
        self,
    ) -> TraceMetrics:
        """
        Return trace metrics.
        """

        with self._lock:

            self.update_statistics()


            if hasattr(
                self.metrics,
                "update",
            ):

                self.metrics.update(
                    self.trace_statistics
                )


            return self.metrics



    def statistics_report(
        self,
    ) -> Dict[str, Any]:
        """
        Generate complete statistics report.
        """

        with self._lock:

            self.update_statistics()


            return {

                "trace_id": self.trace_id,

                "name": self.name,


                "lifecycle": {

                    "created_at": self.created_at,

                    "started_at": self.started_at,

                    "finished_at": self.finished_at,

                    "duration": self.duration,

                },


                "counts": {

                    "spans": len(
                        self.spans
                    ),

                    "events": len(
                        self.events
                    ),

                    "attributes": len(
                        self.attributes
                    ),

                    "tags": len(
                        self.tags
                    ),

                },


                "statistics": (

                    self.trace_statistics.to_dict()

                    if hasattr(
                        self.trace_statistics,
                        "to_dict",
                    )

                    else {}

                ),


                "metrics": (

                    self.metrics.to_dict()

                    if hasattr(
                        self.metrics,
                        "to_dict",
                    )

                    else {}

                ),


                "generated_at": time.time(),

            }
# ==============================================================================
# Part 4.14 – Search
# ==============================================================================


    def search(
        self,
        query: str,
    ) -> TraceSearchResult:
        """
        Search trace content.

        Searches:
        - attributes
        - tags
        - events
        - spans
        """

        with self._lock:

            matches: Dict[str, Any] = {

                "attributes": self.find_attribute(
                    query
                ),

                "tags": self.find_tag(
                    query
                ),

                "events": self.find_event(
                    query
                ),

                "spans": self.find_span(
                    query
                ),

            }


            total = sum(
                len(value)
                for value in matches.values()
                if isinstance(
                    value,
                    list,
                )
            )


            return TraceSearchResult(

                query=query,

                trace_id=self.trace_id,

                matches=matches,

                count=total,

                found=(
                    total > 0
                ),

                searched_at=time.time(),

            )



    def find_attribute(
        self,
        query: str,
    ) -> List[Dict[str, Any]]:
        """
        Find attributes by key or value.
        """

        with self._lock:

            results: List[
                Dict[str, Any]
            ] = []


            query_lower = query.lower()


            for key, value in self.attributes.items():

                if (

                    query_lower in str(
                        key
                    ).lower()

                    or

                    query_lower in str(
                        value
                    ).lower()

                ):

                    results.append(

                        {
                            "key": key,
                            "value": value,
                        }

                    )


            return results



    def find_tag(
        self,
        query: str,
    ) -> List[Dict[str, Any]]:
        """
        Find tags by key or value.
        """

        with self._lock:

            results: List[
                Dict[str, Any]
            ] = []


            query_lower = query.lower()


            for key, value in self.tags.items():

                if (

                    query_lower in str(
                        key
                    ).lower()

                    or

                    query_lower in str(
                        value
                    ).lower()

                ):

                    results.append(

                        {
                            "key": key,
                            "value": value,
                        }

                    )


            return results



    def find_event(
        self,
        query: str,
    ) -> List[Any]:
        """
        Find events containing query.
        """

        with self._lock:

            results: List[Any] = []


            query_lower = query.lower()


            for event in self.events:

                if query_lower in str(
                    event
                ).lower():

                    results.append(
                        event
                    )


            return results



    def find_span(
        self,
        query: str,
    ) -> List[TraceSpan]:
        """
        Find spans by id or name.
        """

        with self._lock:

            results: List[
                TraceSpan
            ] = []


            query_lower = query.lower()


            for span in self.spans:

                span_id = str(
                    getattr(
                        span,
                        "span_id",
                        "",
                    )
                )


                name = str(
                    getattr(
                        span,
                        "name",
                        "",
                    )
                )


                if (

                    query_lower in span_id.lower()

                    or

                    query_lower in name.lower()

                ):

                    results.append(
                        span
                    )


            return results
# ==============================================================================
# Part 4.15 – Export
# ==============================================================================


    def export(
        self,
        format: TraceFormat = TraceFormat.JSON,
        mode: TraceExportMode = TraceExportMode.FULL,
    ) -> TraceExportResult:
        """
        Export trace using selected format.
        """

        with self._lock:

            try:

                if format == TraceFormat.JSON:

                    payload = self.export_json()


                elif format == TraceFormat.YAML:

                    payload = self.export_yaml()


                elif format == TraceFormat.OTLP:

                    payload = self.export_otlp()


                else:

                    payload = self.to_dict()



                return TraceExportResult(

                    success=True,

                    format=format,

                    mode=mode,

                    trace_id=self.trace_id,

                    data=payload,

                    exported_at=time.time(),

                )


            except Exception as exc:

                raise TraceExportError(
                    str(exc)
                ) from exc



    def export_json(
        self,
        *,
        indent: int = 2,
    ) -> str:
        """
        Export trace as JSON.
        """

        with self._lock:

            return json.dumps(

                self.to_dict(),

                indent=indent,

                ensure_ascii=False,

                default=str,

            )



    def export_yaml(
        self,
    ) -> str:
        """
        Export trace as YAML.

        Uses yaml when available.
        """

        with self._lock:

            try:

                import yaml


                return yaml.safe_dump(

                    self.to_dict(),

                    allow_unicode=True,

                    sort_keys=False,

                )


            except ImportError:

                raise TraceExportError(

                    "PyYAML is required for YAML export"

                )



    def export_otlp(
        self,
    ) -> Dict[str, Any]:
        """
        Export trace using OTLP compatible structure.
        """

        with self._lock:

            spans = []


            for span in self.spans:

                if hasattr(
                    span,
                    "to_dict",
                ):

                    spans.append(
                        span.to_dict()
                    )

                else:

                    spans.append(
                        span
                    )


            return {

                "resourceSpans": [

                    {

                        "resource": {

                            "attributes": [

                                {

                                    "key": "service.name",

                                    "value": self.name,

                                },

                            ],

                        },

                        "scopeSpans": [

                            {

                                "spans": spans,

                            }

                        ],

                    }

                ],


                "trace_id": self.trace_id,

                "start_time": self.started_at,

                "end_time": self.finished_at,

            }
# ==============================================================================
# Part 4.16 – Summary
# ==============================================================================


    def summary(
        self,
    ) -> TraceSummary:
        """
        Generate complete trace summary.
        """

        with self._lock:

            return TraceSummary(

                trace_id=self.trace_id,

                name=self.name,

                state=self.state,

                status=self.status,

                result=self.result,

                duration=self.duration,

                span_count=len(
                    self.spans
                ),

                event_count=len(
                    self.events
                ),

                attribute_count=len(
                    self.attributes
                ),

                tag_count=len(
                    self.tags
                ),

                created_at=self.created_at,

                started_at=self.started_at,

                finished_at=self.finished_at,

            )



    def brief(
        self,
    ) -> Dict[str, Any]:
        """
        Generate short trace summary.
        """

        with self._lock:

            return {

                "trace_id": self.trace_id,

                "name": self.name,

                "state": serialize_enum(
                    self.state
                ),

                "status": serialize_enum(
                    self.status
                ),

                "result": serialize_enum(
                    self.result
                ),

                "duration": self.duration,

                "spans": len(
                    self.spans
                ),

                "events": len(
                    self.events
                ),

            }



    def describe(
        self,
    ) -> str:
        """
        Return human readable description.
        """

        with self._lock:

            return (

                f"Trace("
                f"id={self.trace_id}, "
                f"name={self.name}, "
                f"state={self.state.value}, "
                f"status={self.status.value}, "
                f"spans={len(self.spans)}, "
                f"duration={self.duration}"
                f")"

            )



    def report(
        self,
    ) -> TraceReport:
        """
        Generate full trace report.
        """

        with self._lock:

            return TraceReport(

                trace_id=self.trace_id,

                name=self.name,

                summary=self.summary(),

                diagnostics=self.diagnostics(),

                statistics=self.statistics_report(),

                health=self.health(),

                generated_at=time.time(),

            )
# ==============================================================================
# Part 4.17 – Python Protocols
# ==============================================================================


    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """

        return (

            f"<Trace "
            f"id={self.trace_id!r} "
            f"name={self.name!r} "
            f"state={self.state.value!r} "
            f"spans={len(self.spans)}"
            f">"

        )



    def __str__(
        self,
    ) -> str:
        """
        Human readable representation.
        """

        return (

            f"Trace("
            f"{self.name}, "
            f"{self.trace_id}, "
            f"{self.state.value}"
            f")"

        )



    def __len__(
        self,
    ) -> int:
        """
        Return number of spans.
        """

        return len(
            self.spans
        )



    def __iter__(
        self,
    ) -> Iterator[TraceSpan]:
        """
        Iterate trace spans.
        """

        return iter(
            self.spans
        )



    def __contains__(
        self,
        item: Any,
    ) -> bool:
        """
        Check membership.

        Supports:
        - span
        - span_id
        - attribute key
        - tag key
        """

        with self._lock:

            if item in self.spans:

                return True


            if isinstance(
                item,
                str,
            ):

                if any(

                    getattr(
                        span,
                        "span_id",
                        None,
                    )
                    == item

                    for span in self.spans

                ):

                    return True


                if item in self.attributes:

                    return True


                if item in self.tags:

                    return True


            return False



    def __getitem__(
        self,
        key: Union[int, str],
    ) -> Any:
        """
        Indexed access.

        int:
            span index

        str:
            attribute/tag lookup
        """

        with self._lock:

            if isinstance(
                key,
                int,
            ):

                return self.spans[key]


            if key in self.attributes:

                return self.attributes[key]


            if key in self.tags:

                return self.tags[key]


            raise KeyError(
                key
            )



    def __setitem__(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Set attribute by key.
        """

        self.set_attribute(
            key,
            value,
        )



    def __copy__(
        self,
    ) -> "Trace":
        """
        Shallow copy.
        """

        with self._lock:

            return self.copy()



    def __deepcopy__(
        self,
        memo: Optional[Dict[int, Any]] = None,
    ) -> "Trace":
        """
        Deep copy.
        """

        if memo is None:

            memo = {}


        with self._lock:

            copied = self.__class__.__new__(
                self.__class__
            )


            memo[id(self)] = copied


            for key, value in self.__dict__.items():

                if key == "_lock":

                    setattr(
                        copied,
                        key,
                        RLock(),
                    )

                else:

                    setattr(

                        copied,

                        key,

                        copy.deepcopy(
                            value,
                            memo,
                        ),

                    )


            return copied
# ==============================================================================
# Part 4.18 – Trace Entity __all__
# ==============================================================================


class Tracer:
# ==============================================================================
# Part 5.1 – Tracer Constructor
# ==============================================================================

    def __init__(
        self,
        name: Optional[str] = None,
        configuration: Optional[
            TraceConfiguration
        ] = None,
        sample_rate: float = DEFAULT_SAMPLE_RATE,
        enabled: bool = DEFAULT_ENABLED,
        auto_start: bool = DEFAULT_AUTO_START,
    ) -> None:
        """
        Initialize Tracer engine.

        Creates:
        - identity
        - configuration
        - lifecycle state
        - trace registry
        - span registry
        - sampling controller
        - statistics
        - hooks
        - synchronization lock
        """

        # ----------------------------------------------------------------------
        # Identity
        # ----------------------------------------------------------------------

        self.name: str = (
            name
            if name is not None
            else DEFAULT_TRACER_NAME
        )

        self.tracer_id: str = (
            generate_trace_id()
        )


        # ----------------------------------------------------------------------
        # Configuration
        # ----------------------------------------------------------------------

        self.configuration: TraceConfiguration = (

            configuration

            if configuration is not None

            else TraceConfiguration()

        )


        # ----------------------------------------------------------------------
        # Lifecycle State
        # ----------------------------------------------------------------------

        self.state: TracerState = (
            TracerState.CREATED
        )

        self.enabled: bool = enabled

        self.started_at: Optional[
            float
        ] = None

        self.stopped_at: Optional[
            float
        ] = None


        # ----------------------------------------------------------------------
        # Sampling
        # ----------------------------------------------------------------------

        self.sample_rate: float = (

            sample_rate

            if 0.0 <= sample_rate <= 1.0

            else DEFAULT_SAMPLE_RATE

        )

        self.sampling_enabled: bool = (
            DEFAULT_SAMPLING_ENABLED
        )


        # ----------------------------------------------------------------------
        # Trace Registry
        # ----------------------------------------------------------------------

        self.traces: Dict[
            TraceID,
            Trace,
        ] = {}


        # ----------------------------------------------------------------------
        # Span Registry
        # ----------------------------------------------------------------------

        self.spans: Dict[
            SpanID,
            TraceSpan,
        ] = {}


        # ----------------------------------------------------------------------
        # Runtime Containers
        # ----------------------------------------------------------------------

        self.statistics: Dict[
            str,
            Any,
        ] = {

            "traces_created": 0,

            "traces_finished": 0,

            "spans_created": 0,

            "exports": 0,

            "errors": 0,

        }


        self.metrics: Dict[
            str,
            Any,
        ] = {}


        # ----------------------------------------------------------------------
        # Hooks
        # ----------------------------------------------------------------------

        self.hooks: Dict[
            str,
            List[Callable],
        ] = {

            "before_trace": [],

            "after_trace": [],

            "before_span": [],

            "after_span": [],

            "before_export": [],

            "after_export": [],

            "on_error": [],

        }


        # ----------------------------------------------------------------------
        # Diagnostics
        # ----------------------------------------------------------------------

        self.last_error: Optional[
            str
        ] = None

        self.warnings: List[
            str
        ] = []


        # ----------------------------------------------------------------------
        # Internal
        # ----------------------------------------------------------------------

        self._lock: RLock = (
            RLock()
        )


        # ----------------------------------------------------------------------
        # Auto Start
        # ----------------------------------------------------------------------

        if auto_start:

            self.start()

# ==============================================================================
# Part 5.2 – Properties
# ==============================================================================


    @property
    def disabled(
        self,
    ) -> bool:
        """
        Return whether tracer is disabled.
        """

        return not self.enabled



    @property
    def running(
        self,
    ) -> bool:
        """
        Return whether tracer is running.
        """

        return (
            self.state == TracerState.RUNNING
        )



    @property
    def frozen(
        self,
    ) -> bool:
        """
        Return whether tracer is frozen.
        """

        return (
            self.state == TracerState.FROZEN
        )



    @property
    def closed(
        self,
    ) -> bool:
        """
        Return whether tracer is closed.
        """

        return (
            self.state == TracerState.CLOSED
        )



    @property
    def active_trace_count(
        self,
    ) -> int:
        """
        Number of active traces.
        """

        with self._lock:

            return sum(

                1

                for trace in self.traces.values()

                if trace.active

            )



    @property
    def finished_trace_count(
        self,
    ) -> int:
        """
        Number of finished traces.
        """

        with self._lock:

            return sum(

                1

                for trace in self.traces.values()

                if trace.finished

            )



    @property
    def total_span_count(
        self,
    ) -> int:
        """
        Total registered spans.
        """

        with self._lock:

            return len(
                self.spans
            )



    @property
    def sample_rate(
        self,
    ) -> float:
        """
        Current sampling rate.
        """

        return self._sample_rate



    @sample_rate.setter
    def sample_rate(
        self,
        value: float,
    ) -> None:
        """
        Update sampling rate.
        """

        if not (
            0.0 <= value <= 1.0
        ):

            raise SamplingError(
                "sample_rate must be between 0.0 and 1.0"
            )


        self._sample_rate = float(
            value
        )



    @property
    def configuration(
        self,
    ) -> TraceConfiguration:
        """
        Return tracer configuration.
        """

        return self._configuration



    @configuration.setter
    def configuration(
        self,
        value: TraceConfiguration,
    ) -> None:
        """
        Update tracer configuration.
        """

        if value is None:

            value = TraceConfiguration()


        self._configuration = value
# ==============================================================================
# Part 5.3 – Lifecycle
# ==============================================================================


    def initialize(
        self,
    ) -> "Tracer":
        """
        Initialize tracer engine.

        Transition:
            CREATED -> INITIALIZED
        """

        with self._lock:

            if self.state != TracerState.CREATED:

                return self


            self.state = (
                TracerState.INITIALIZED
            )


            return self



    def start(
        self,
    ) -> "Tracer":
        """
        Start tracer execution.

        Transition:
            INITIALIZED -> RUNNING
        """

        with self._lock:

            if self.running:

                return self


            if self.state == TracerState.CREATED:

                self.initialize()


            self.started_at = (
                time.time()
            )


            self.state = (
                TracerState.RUNNING
            )


            return self



    def stop(
        self,
    ) -> "Tracer":
        """
        Stop tracer execution.

        Transition:
            RUNNING -> STOPPED
        """

        with self._lock:

            self.stopped_at = (
                time.time()
            )


            self.state = (
                TracerState.STOPPED
            )


            return self



    def reset(
        self,
    ) -> "Tracer":
        """
        Reset tracer runtime state.
        """

        with self._lock:

            self.traces.clear()

            self.spans.clear()


            self.statistics.clear()

            self.metrics.clear()


            self.last_error = None

            self.warnings.clear()


            self.started_at = None

            self.stopped_at = None


            self.state = (
                TracerState.CREATED
            )


            return self



    def restart(
        self,
    ) -> "Tracer":
        """
        Restart tracer.

        Equivalent:
            reset()
            start()
        """

        with self._lock:

            self.reset()

            self.start()


            return self



    def enable(
        self,
    ) -> "Tracer":
        """
        Enable tracing.
        """

        with self._lock:

            self.enabled = True


            return self



    def disable(
        self,
    ) -> "Tracer":
        """
        Disable tracing.
        """

        with self._lock:

            self.enabled = False


            return self



    def freeze(
        self,
    ) -> "Tracer":
        """
        Freeze tracer mutation.
        """

        with self._lock:

            self.state = (
                TracerState.FROZEN
            )


            return self



    def unfreeze(
        self,
    ) -> "Tracer":
        """
        Unfreeze tracer.
        """

        with self._lock:

            if self.closed:

                return self


            if self.running:

                self.state = (
                    TracerState.RUNNING
                )

            else:

                self.state = (
                    TracerState.INITIALIZED
                )


            return self



    def close(
        self,
    ) -> "Tracer":
        """
        Permanently close tracer.

        Transition:
            ANY -> CLOSED
        """

        with self._lock:

            self.enabled = False


            self.state = (
                TracerState.CLOSED
            )


            self.traces.clear()

            self.spans.clear()


            return self
# ==============================================================================
# Part 5.4 – Trace Management
# ==============================================================================


    def create_trace(
        self,
        name: Optional[str] = None,
        **kwargs: Any,
    ) -> Trace:
        """
        Create and register new Trace.
        """

        with self._lock:

            if not self.enabled:

                raise TracerError(
                    "Tracer is disabled"
                )


            trace = Trace(
                name=name,
                **kwargs,
            )


            self.register_trace(
                trace
            )


            self.statistics[
                "traces_created"
            ] += 1


            return trace



    def register_trace(
        self,
        trace: Trace,
    ) -> Trace:
        """
        Register existing Trace.
        """

        with self._lock:

            if not isinstance(
                trace,
                Trace,
            ):

                raise TraceValidationError(
                    "Object must be Trace instance"
                )


            self.traces[
                trace.trace_id
            ] = trace


            return trace



    def unregister_trace(
        self,
        trace_id: TraceID,
    ) -> Optional[Trace]:
        """
        Unregister trace without destroying it.
        """

        with self._lock:

            return self.traces.pop(
                trace_id,
                None,
            )



    def remove_trace(
        self,
        trace_id: TraceID,
    ) -> bool:
        """
        Remove trace permanently.
        """

        with self._lock:

            if trace_id not in self.traces:

                return False


            del self.traces[
                trace_id
            ]


            return True



    def clear_traces(
        self,
    ) -> "Tracer":
        """
        Clear all registered traces.
        """

        with self._lock:

            self.traces.clear()


            return self



    def get_trace(
        self,
        trace_id: TraceID,
    ) -> Optional[Trace]:
        """
        Get trace by id.
        """

        with self._lock:

            return self.traces.get(
                trace_id
            )



    def find_trace(
        self,
        query: str,
    ) -> List[Trace]:
        """
        Search traces.

        Matches:
        - trace_id
        - name
        - attributes
        - tags
        """

        with self._lock:

            results: List[Trace] = []


            query_lower = query.lower()


            for trace in self.traces.values():

                if (

                    query_lower in trace.trace_id.lower()

                    or

                    query_lower in trace.name.lower()

                    or

                    trace.find_attribute(query)

                    or

                    trace.find_tag(query)

                ):

                    results.append(
                        trace
                    )


            return results



    def iter_traces(
        self,
    ) -> Iterator[Trace]:
        """
        Iterate all traces.
        """

        with self._lock:

            yield from (
                self.traces.values()
            )



    def active_traces(
        self,
    ) -> List[Trace]:
        """
        Return running traces.
        """

        with self._lock:

            return [

                trace

                for trace in self.traces.values()

                if trace.active

            ]



    def finished_traces(
        self,
    ) -> List[Trace]:
        """
        Return finished traces.
        """

        with self._lock:

            return [

                trace

                for trace in self.traces.values()

                if trace.finished

            ]
# ==============================================================================
# Part 5.5 – Span Management
# ==============================================================================


    def create_span(
        self,
        trace: Trace,
        name: Optional[str] = None,
        **kwargs: Any,
    ) -> TraceSpan:
        """
        Create and register a new span.
        """

        with self._lock:

            if not isinstance(
                trace,
                Trace,
            ):
                raise TraceValidationError(
                    "trace must be Trace instance"
                )


            span = TraceSpan(
                trace_id=trace.trace_id,
                name=(
                    name
                    if name is not None
                    else DEFAULT_SPAN_NAME
                ),
                **kwargs,
            )


            trace.add_span(
                span
            )


            self.spans[
                span.span_id
            ] = span


            self.statistics[
                "spans_created"
            ] += 1


            return span



    def start_span(
        self,
        trace: Trace,
        name: Optional[str] = None,
        **kwargs: Any,
    ) -> TraceSpan:
        """
        Create and start a span.
        """

        with self._lock:

            span = self.create_span(
                trace,
                name=name,
                **kwargs,
            )


            span.start()


            return span



    def finish_span(
        self,
        span_id: SpanID,
        status: SpanStatus = SpanStatus.SUCCESS,
    ) -> Optional[TraceSpan]:
        """
        Finish span execution.
        """

        with self._lock:

            span = self.spans.get(
                span_id
            )


            if span is None:

                return None


            span.finish(
                status=status
            )


            return span



    def get_span(
        self,
        span_id: SpanID,
    ) -> Optional[TraceSpan]:
        """
        Get span by id.
        """

        with self._lock:

            return self.spans.get(
                span_id
            )



    def find_span(
        self,
        query: str,
    ) -> List[TraceSpan]:
        """
        Search spans by id or name.
        """

        with self._lock:

            results: List[
                TraceSpan
            ] = []


            query_lower = query.lower()


            for span in self.spans.values():

                span_id = str(
                    getattr(
                        span,
                        "span_id",
                        "",
                    )
                )


                name = str(
                    getattr(
                        span,
                        "name",
                        "",
                    )
                )


                if (

                    query_lower in span_id.lower()

                    or

                    query_lower in name.lower()

                ):

                    results.append(
                        span
                    )


            return results



    def remove_span(
        self,
        span_id: SpanID,
    ) -> bool:
        """
        Remove span from registry.
        """

        with self._lock:

            span = self.spans.pop(
                span_id,
                None,
            )


            if span is None:

                return False


            return True



    def iter_spans(
        self,
    ) -> Iterator[TraceSpan]:
        """
        Iterate all spans.
        """

        with self._lock:

            yield from (
                self.spans.values()
            )



    def clear_spans(
        self,
    ) -> "Tracer":
        """
        Clear all spans.
        """

        with self._lock:

            self.spans.clear()


            for trace in self.traces.values():

                trace.clear_spans()


            return self
# ==============================================================================
# Part 5.6 – Sampling
# ==============================================================================


    def should_sample(
        self,
        trace_id: Optional[TraceID] = None,
    ) -> bool:
        """
        Decide whether a trace should be sampled.

        Returns
        -------
        bool
            True if trace is sampled.
        """

        with self._lock:

            if not self.sampling_enabled:

                return False


            if self.sample_rate >= 1.0:

                return True


            if self.sample_rate <= 0.0:

                return False


            seed = (
                trace_id
                if trace_id is not None
                else generate_trace_id()
            )


            value = (
                int(
                    seed[:8],
                    16,
                )
                %
                1000000
            )
            
            1000000


            return value < self.sample_rate



    def sample(
        self,
        trace: Trace,
    ) -> bool:
        """
        Apply sampling decision to trace.
        """

        with self._lock:

            sampled = self.should_sample(
                trace.trace_id
            )


            if sampled:

                trace.context[
                    "sampled"
                ] = True

            else:

                trace.context[
                    "sampled"
                ] = False


            return sampled



    def set_sample_rate(
        self,
        rate: float,
    ) -> "Tracer":
        """
        Update sampling rate.
        """

        with self._lock:

            if not (
                0.0 <= rate <= 1.0
            ):

                raise SamplingError(
                    "sample rate must be between 0.0 and 1.0"
                )


            self._sample_rate = float(
                rate
            )


            return self



    def enable_sampling(
        self,
    ) -> "Tracer":
        """
        Enable sampling.
        """

        with self._lock:

            self.sampling_enabled = True


            return self



    def disable_sampling(
        self,
    ) -> "Tracer":
        """
        Disable sampling.
        """

        with self._lock:

            self.sampling_enabled = False


            return self



    def sampling_statistics(
        self,
    ) -> Dict[str, Any]:
        """
        Return sampling statistics.
        """

        with self._lock:

            total = self.statistics.get(
                "traces_created",
                0,
            )


            sampled = sum(

                1

                for trace in self.traces.values()

                if trace.context.get(
                    "sampled",
                    False,
                )

            )


            return {

                "enabled": self.sampling_enabled,

                "sample_rate": self.sample_rate,

                "total_traces": total,

                "sampled_traces": sampled,

                "dropped_traces": (
                    total - sampled
                ),

                "sampling_ratio": (

                    sampled / total

                    if total > 0

                    else 0.0

                ),

            }
# ==============================================================================
# Part 5.7 – Search
# ==============================================================================


    def search(
        self,
        query: str,
    ) -> Dict[str, Any]:
        """
        Global search across traces and spans.
        """

        with self._lock:

            return {

                "query": query,

                "traces": self.search_trace(
                    query
                ),

                "spans": self.search_span(
                    query
                ),

                "attributes": self.search_attribute(
                    query
                ),

                "tags": self.search_tag(
                    query
                ),

                "events": self.search_event(
                    query
                ),

                "searched_at": time.time(),

            }



    def search_trace(
        self,
        query: str,
    ) -> List[Trace]:
        """
        Search traces.
        """

        with self._lock:

            results: List[
                Trace
            ] = []


            query_lower = query.lower()


            for trace in self.traces.values():

                matched = (

                    query_lower in trace.trace_id.lower()

                    or

                    query_lower in trace.name.lower()

                )


                if not matched:

                    matched = bool(
                        trace.find_attribute(
                            query
                        )
                        or
                        trace.find_tag(
                            query
                        )
                        or
                        trace.find_event(
                            query
                        )
                    )


                if matched:

                    results.append(
                        trace
                    )


            return results



    def search_span(
        self,
        query: str,
    ) -> List[TraceSpan]:
        """
        Search spans.
        """

        with self._lock:

            results: List[
                TraceSpan
            ] = []


            query_lower = query.lower()


            for span in self.spans.values():

                span_id = str(
                    getattr(
                        span,
                        "span_id",
                        "",
                    )
                )


                name = str(
                    getattr(
                        span,
                        "name",
                        "",
                    )
                )


                if (

                    query_lower in span_id.lower()

                    or

                    query_lower in name.lower()

                ):

                    results.append(
                        span
                    )


            return results



    def search_attribute(
        self,
        query: str,
    ) -> List[Dict[str, Any]]:
        """
        Search attributes across traces.
        """

        with self._lock:

            results: List[
                Dict[str, Any]
            ] = []


            for trace in self.traces.values():

                matches = trace.find_attribute(
                    query
                )


                for item in matches:

                    results.append(

                        {

                            "trace_id": trace.trace_id,

                            "attribute": item,

                        }

                    )


            return results



    def search_tag(
        self,
        query: str,
    ) -> List[Dict[str, Any]]:
        """
        Search tags across traces.
        """

        with self._lock:

            results: List[
                Dict[str, Any]
            ] = []


            for trace in self.traces.values():

                matches = trace.find_tag(
                    query
                )


                for item in matches:

                    results.append(

                        {

                            "trace_id": trace.trace_id,

                            "tag": item,

                        }

                    )


            return results



    def search_event(
        self,
        query: str,
    ) -> List[Dict[str, Any]]:
        """
        Search events across traces.
        """

        with self._lock:

            results: List[
                Dict[str, Any]
            ] = []


            for trace in self.traces.values():

                matches = trace.find_event(
                    query
                )


                for event in matches:

                    results.append(

                        {

                            "trace_id": trace.trace_id,

                            "event": event,

                        }

                    )


            return results
# ==============================================================================
# Part 5.8 – Export
# ==============================================================================


    def export(
        self,
        format: TraceFormat = TraceFormat.JSON,
        mode: TraceExportMode = TraceExportMode.FULL,
    ) -> TraceExportResult:
        """
        Export tracer data.
        """

        with self._lock:

            try:

                if format == TraceFormat.JSON:

                    data = self.export_json()


                elif format == TraceFormat.YAML:

                    data = self.export_yaml()


                elif format == TraceFormat.OTLP:

                    data = self.export_otlp()


                elif format == TraceFormat.PROMETHEUS:

                    data = self.export_prometheus()


                else:

                    data = self.to_dict()



                self.statistics[
                    "exports"
                ] += 1


                return TraceExportResult(

                    success=True,

                    format=format,

                    mode=mode,

                    data=data,

                    exported_at=time.time(),

                )


            except Exception as exc:

                self.statistics[
                    "errors"
                ] += 1


                raise TraceExportError(
                    str(exc)
                ) from exc



    def export_json(
        self,
        indent: int = 2,
    ) -> str:
        """
        Export tracer state as JSON.
        """

        with self._lock:

            return json.dumps(

                self.to_dict(),

                indent=indent,

                ensure_ascii=False,

                default=str,

            )



    def export_yaml(
        self,
    ) -> str:
        """
        Export tracer state as YAML.
        """

        with self._lock:

            try:

                import yaml


                return yaml.safe_dump(

                    self.to_dict(),

                    allow_unicode=True,

                    sort_keys=False,

                )


            except ImportError:

                raise TraceExportError(

                    "PyYAML required for YAML export"

                )



    def export_otlp(
        self,
    ) -> Dict[str, Any]:
        """
        Export tracer data in OTLP compatible format.
        """

        with self._lock:

            resource_spans = []


            for trace in self.traces.values():

                resource_spans.append(

                    {

                        "trace_id": trace.trace_id,

                        "spans": [

                            span.to_dict()

                            if hasattr(
                                span,
                                "to_dict",
                            )

                            else span

                            for span in trace.spans

                        ],

                    }

                )


            return {

                "resourceSpans": resource_spans,

            }



    def export_prometheus(
        self,
    ) -> str:
        """
        Export metrics in Prometheus format.
        """

        with self._lock:

            lines = [

                "# HELP scios_traces_total Total traces",

                "# TYPE scios_traces_total counter",

                f"scios_traces_total {len(self.traces)}",

                "# HELP scios_spans_total Total spans",

                "# TYPE scios_spans_total counter",

                f"scios_spans_total {len(self.spans)}",

            ]


            return "\n".join(
                lines
            )



    def export_all(
        self,
    ) -> Dict[str, Any]:
        """
        Export all supported formats.
        """

        with self._lock:

            return {

                "json": self.export_json(),

                "yaml": self.export_yaml(),

                "otlp": self.export_otlp(),

                "prometheus": self.export_prometheus(),

            }
# ==============================================================================
# Part 5.9 – Serialization
# ==============================================================================


    def to_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Serialize tracer into dictionary.
        """

        with self._lock:

            return {

                # ------------------------------------------------------------------
                # Identity
                # ------------------------------------------------------------------

                "tracer_id": self.tracer_id,

                "name": self.name,


                # ------------------------------------------------------------------
                # State
                # ------------------------------------------------------------------

                "state": serialize_enum(
                    self.state
                ),

                "enabled": self.enabled,


                # ------------------------------------------------------------------
                # Configuration
                # ------------------------------------------------------------------

                "configuration":

                    self.configuration.to_dict()

                    if hasattr(
                        self.configuration,
                        "to_dict",
                    )

                    else self.configuration,


                # ------------------------------------------------------------------
                # Sampling
                # ------------------------------------------------------------------

                "sample_rate": self.sample_rate,

                "sampling_enabled": self.sampling_enabled,


                # ------------------------------------------------------------------
                # Traces
                # ------------------------------------------------------------------

                "traces": [

                    trace.to_dict()

                    for trace in self.traces.values()

                ],


                # ------------------------------------------------------------------
                # Statistics
                # ------------------------------------------------------------------

                "statistics": safe_copy(
                    self.statistics
                ),


                "metrics": safe_copy(
                    self.metrics
                ),


                # ------------------------------------------------------------------
                # Time
                # ------------------------------------------------------------------

                "started_at": self.started_at,

                "stopped_at": self.stopped_at,

            }



    def to_json(
        self,
        indent: int = 2,
    ) -> str:
        """
        Serialize tracer into JSON.
        """

        return json.dumps(

            self.to_dict(),

            indent=indent,

            ensure_ascii=False,

            default=str,

        )



    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "Tracer":
        """
        Create tracer from dictionary.
        """

        tracer = cls(

            name=data.get(
                "name"
            ),

            sample_rate=data.get(
                "sample_rate",
                DEFAULT_SAMPLE_RATE,
            ),

            enabled=data.get(
                "enabled",
                True,
            ),

        )


        if "tracer_id" in data:

            tracer.tracer_id = data[
                "tracer_id"
            ]


        if "state" in data:

            tracer.state = TracerState(
                data["state"]
            )


        tracer.sampling_enabled = data.get(
            "sampling_enabled",
            True,
        )


        tracer.started_at = data.get(
            "started_at"
        )


        tracer.stopped_at = data.get(
            "stopped_at"
        )


        tracer.statistics.update(

            data.get(
                "statistics",
                {},
            )

        )


        tracer.metrics.update(

            data.get(
                "metrics",
                {},
            )

        )


        for trace_data in data.get(
            "traces",
            [],
        ):

            trace = Trace.from_dict(
                trace_data
            )

            tracer.register_trace(
                trace
            )


        return tracer



    @classmethod
    def from_json(
        cls,
        data: str,
    ) -> "Tracer":
        """
        Create tracer from JSON.
        """

        return cls.from_dict(

            json.loads(
                data
            )

        )



    def snapshot(
        self,
    ) -> Dict[str, Any]:
        """
        Create deep runtime snapshot.
        """

        with self._lock:

            return copy.deepcopy(

                self.to_dict()

            )



    def restore(
        self,
        snapshot: Mapping[str, Any],
    ) -> "Tracer":
        """
        Restore tracer from snapshot.
        """

        with self._lock:

            restored = self.from_dict(
                snapshot
            )


            self.__dict__.update(

                restored.__dict__

            )


            self._lock = RLock()


            return self
# ==============================================================================
# Part 5.10 – Validation
# ==============================================================================


    def validate(
        self,
    ) -> TraceValidationResult:
        """
        Validate tracer state.
        """

        with self._lock:

            errors: List[str] = []

            warnings: List[str] = []


            # --------------------------------------------------------------
            # Configuration
            # --------------------------------------------------------------

            config_errors = (
                self.validate_configuration()
            )

            errors.extend(
                config_errors
            )



            # --------------------------------------------------------------
            # Traces
            # --------------------------------------------------------------

            trace_errors = (
                self.validate_traces()
            )

            errors.extend(
                trace_errors
            )



            # --------------------------------------------------------------
            # Spans
            # --------------------------------------------------------------

            span_errors = (
                self.validate_spans()
            )

            errors.extend(
                span_errors
            )



            return TraceValidationResult(

                valid=(
                    len(errors) == 0
                ),

                errors=errors,

                warnings=warnings,

                checked_at=time.time(),

            )



    def validate_configuration(
        self,
    ) -> List[str]:
        """
        Validate tracer configuration.
        """

        errors: List[str] = []


        if self.configuration is None:

            errors.append(
                "configuration is missing"
            )


        if not (
            0.0 <= self.sample_rate <= 1.0
        ):

            errors.append(
                "invalid sample_rate"
            )


        return errors



    def validate_traces(
        self,
    ) -> List[str]:
        """
        Validate registered traces.
        """

        errors: List[str] = []


        for trace_id, trace in self.traces.items():

            if not isinstance(
                trace,
                Trace,
            ):

                errors.append(

                    f"Invalid trace object: {trace_id}"

                )

                continue


            if trace.trace_id != trace_id:

                errors.append(

                    f"Trace id mismatch: {trace_id}"

                )


            if not trace.validate().valid:

                errors.append(

                    f"Trace validation failed: {trace_id}"

                )


        return errors



    def validate_spans(
        self,
    ) -> List[str]:
        """
        Validate registered spans.
        """

        errors: List[str] = []


        for span_id, span in self.spans.items():

            if not isinstance(
                span,
                TraceSpan,
            ):

                errors.append(

                    f"Invalid span object: {span_id}"

                )

                continue


            if getattr(
                span,
                "span_id",
                None,
            ) != span_id:

                errors.append(

                    f"Span id mismatch: {span_id}"

                )


        return errors



    def validation_report(
        self,
    ) -> Dict[str, Any]:
        """
        Generate validation report.
        """

        result = self.validate()


        return {

            "valid": result.valid,

            "errors": result.errors,

            "warnings": result.warnings,

            "trace_count": len(
                self.traces
            ),

            "span_count": len(
                self.spans
            ),

            "checked_at": time.time(),

        }
# ==============================================================================
# Part 5.11 – Diagnostics
# ==============================================================================


    def diagnostics(
        self,
    ) -> TraceDiagnostics:
        """
        Generate tracer diagnostics information.
        """

        with self._lock:

            return TraceDiagnostics(

                tracer_id=self.tracer_id,

                name=self.name,

                state=self.state,

                enabled=self.enabled,

                trace_count=len(
                    self.traces
                ),

                span_count=len(
                    self.spans
                ),

                statistics=safe_copy(
                    self.statistics
                ),

                metrics=safe_copy(
                    self.metrics
                ),

                errors=[

                    self.last_error

                ]
                if self.last_error

                else [],

                warnings=list(
                    self.warnings
                ),

                generated_at=time.time(),

            )



    def inspect(
        self,
    ) -> Dict[str, Any]:
        """
        Inspect internal tracer state.
        """

        with self._lock:

            return {

                "tracer_id": self.tracer_id,

                "name": self.name,

                "state": serialize_enum(
                    self.state
                ),

                "enabled": self.enabled,

                "running": self.running,

                "frozen": self.frozen,

                "closed": self.closed,

                "trace_count": len(
                    self.traces
                ),

                "span_count": len(
                    self.spans
                ),

                "sample_rate": self.sample_rate,

                "sampling_enabled": self.sampling_enabled,

                "started_at": self.started_at,

                "stopped_at": self.stopped_at,

            }



    def health(
        self,
    ) -> TraceHealth:
        """
        Return tracer health status.
        """

        with self._lock:

            healthy = (

                not self.closed

                and

                self.enabled

                and

                len(
                    self.validate().errors
                ) == 0

            )


            return TraceHealth(

                healthy=healthy,

                status=(

                    "healthy"

                    if healthy

                    else "unhealthy"

                ),

                state=self.state,

                checks={

                    "configuration":

                        len(
                            self.validate_configuration()
                        )
                        == 0,


                    "traces":

                        len(
                            self.validate_traces()
                        )
                        == 0,


                    "spans":

                        len(
                            self.validate_spans()
                        )
                        == 0,

                },

                checked_at=time.time(),

            )



    def status(
        self,
    ) -> Dict[str, Any]:
        """
        Return current tracer status.
        """

        with self._lock:

            return {

                "state": serialize_enum(
                    self.state
                ),

                "enabled": self.enabled,

                "running": self.running,

                "frozen": self.frozen,

                "closed": self.closed,

                "active_traces": self.active_trace_count,

                "finished_traces": self.finished_trace_count,

                "total_spans": self.total_span_count,

            }



    def api_summary(
        self,
    ) -> Dict[str, Any]:
        """
        Return public API summary.
        """

        return {

            "class": "Tracer",

            "version": TRACE_VERSION,

            "capabilities": [

                "trace_management",

                "span_management",

                "sampling",

                "search",

                "export",

                "serialization",

                "validation",

                "diagnostics",

                "statistics",

                "hooks",

            ],

            "methods": [

                "create_trace",

                "create_span",

                "export",

                "search",

                "validate",

                "diagnostics",

                "health",

                "summary",

            ],

        }
# ==============================================================================
# 5.12 Statistics
# ==============================================================================


    def statistics(
        self,
    ) -> Dict[str, Any]:
        """
        Return tracer statistics.
        """

        with self._lock:

            return {

                "traces_created": self.statistics.get(
                    "traces_created",
                    0,
                ),

                "traces_finished": self.statistics.get(
                    "traces_finished",
                    0,
                ),

                "spans_created": self.statistics.get(
                    "spans_created",
                    0,
                ),

                "exports": self.statistics.get(
                    "exports",
                    0,
                ),

                "errors": self.statistics.get(
                    "errors",
                    0,
                ),

                "active_traces": self.active_trace_count,

                "finished_traces": self.finished_trace_count,

                "total_spans": self.total_span_count,

                "sample_rate": self.sample_rate,

                "sampling_enabled": self.sampling_enabled,

            }



    def runtime_statistics(
        self,
    ) -> Dict[str, Any]:
        """
        Return runtime execution statistics.
        """

        with self._lock:

            uptime = None


            if self.started_at is not None:

                end_time = (

                    self.stopped_at

                    if self.stopped_at is not None

                    else time.time()

                )


                uptime = (
                    end_time
                    -
                    self.started_at
                )


            return {

                "state": serialize_enum(
                    self.state
                ),

                "enabled": self.enabled,

                "running": self.running,

                "frozen": self.frozen,

                "closed": self.closed,

                "uptime": uptime,

                "started_at": self.started_at,

                "stopped_at": self.stopped_at,

                "active_trace_count": self.active_trace_count,

                "finished_trace_count": self.finished_trace_count,

                "span_count": self.total_span_count,

            }



    def performance_statistics(
        self,
    ) -> Dict[str, Any]:
        """
        Return performance metrics.
        """

        with self._lock:

            trace_count = len(
                self.traces
            )

            span_count = len(
                self.spans
            )


            return {

                "trace_count": trace_count,

                "span_count": span_count,

                "average_spans_per_trace": (

                    span_count / trace_count

                    if trace_count > 0

                    else 0.0

                ),

                "export_count": self.statistics.get(
                    "exports",
                    0,
                ),

                "error_count": self.statistics.get(
                    "errors",
                    0,
                ),

            }



    def reset_statistics(
        self,
    ) -> "Tracer":
        """
        Reset all statistics counters.
        """

        with self._lock:

            self.statistics = {

                "traces_created": 0,

                "traces_finished": 0,

                "spans_created": 0,

                "exports": 0,

                "errors": 0,

            }


            self.metrics.clear()


            return self



    def statistics_report(
        self,
    ) -> Dict[str, Any]:
        """
        Generate complete statistics report.
        """

        with self._lock:

            return {

                "statistics": self.statistics(),

                "runtime": self.runtime_statistics(),

                "performance": self.performance_statistics(),

                "generated_at": time.time(),

            }
# ==============================================================================
# 5.13 Hooks
# ==============================================================================


    def before_trace(
        self,
        trace: Trace,
    ) -> None:
        """
        Execute hooks before trace start.
        """

        self._execute_hooks(
            "before_trace",
            trace,
        )



    def after_trace(
        self,
        trace: Trace,
    ) -> None:
        """
        Execute hooks after trace finish.
        """

        self._execute_hooks(
            "after_trace",
            trace,
        )



    def before_span(
        self,
        span: TraceSpan,
    ) -> None:
        """
        Execute hooks before span start.
        """

        self._execute_hooks(
            "before_span",
            span,
        )



    def after_span(
        self,
        span: TraceSpan,
    ) -> None:
        """
        Execute hooks after span finish.
        """

        self._execute_hooks(
            "after_span",
            span,
        )



    def before_export(
        self,
        data: Any = None,
    ) -> None:
        """
        Execute hooks before export.
        """

        self._execute_hooks(
            "before_export",
            data,
        )



    def after_export(
        self,
        result: Any = None,
    ) -> None:
        """
        Execute hooks after export.
        """

        self._execute_hooks(
            "after_export",
            result,
        )



    def on_error(
        self,
        error: Exception,
    ) -> None:
        """
        Execute error hooks.
        """

        self.last_error = str(
            error
        )


        self.statistics[
            "errors"
        ] += 1


        self._execute_hooks(
            "on_error",
            error,
        )



    def register_hook(
        self,
        event: str,
        callback: Callable,
    ) -> "Tracer":
        """
        Register callback hook.

        Parameters
        ----------
        event:
            Hook event name.

        callback:
            Callable function.
        """

        with self._lock:

            if event not in self.hooks:

                self.hooks[
                    event
                ] = []


            if not callable(
                callback
            ):

                raise TracerError(
                    "Hook must be callable"
                )


            self.hooks[
                event
            ].append(
                callback
            )


            return self



    def _execute_hooks(
        self,
        event: str,
        payload: Any = None,
    ) -> None:
        """
        Internal hook executor.
        """

        callbacks = self.hooks.get(
            event,
            [],
        )


        for callback in callbacks:

            try:

                callback(
                    payload
                )


            except Exception as exc:

                self.last_error = str(
                    exc
                )

                self.statistics[
                    "errors"
                ] += 1
# ==============================================================================
# 5.14 Summary
# ==============================================================================


    def summary(
        self,
    ) -> Dict[str, Any]:
        """
        Return complete tracer summary.
        """

        with self._lock:

            return {

                "tracer_id": self.tracer_id,

                "name": self.name,

                "state": serialize_enum(
                    self.state
                ),

                "enabled": self.enabled,

                "running": self.running,

                "frozen": self.frozen,

                "closed": self.closed,

                "statistics": self.statistics(),

                "runtime": self.runtime_statistics(),

                "performance": self.performance_statistics(),

                "health": self.health(),

                "trace_count": len(
                    self.traces
                ),

                "span_count": len(
                    self.spans
                ),

                "generated_at": time.time(),

            }



    def brief(
        self,
    ) -> Dict[str, Any]:
        """
        Return lightweight tracer summary.
        """

        with self._lock:

            return {

                "name": self.name,

                "state": serialize_enum(
                    self.state
                ),

                "enabled": self.enabled,

                "traces": len(
                    self.traces
                ),

                "spans": len(
                    self.spans
                ),

                "sample_rate": self.sample_rate,

            }



    def report(
        self,
    ) -> TraceReport:
        """
        Generate tracer report.
        """

        with self._lock:

            return TraceReport(

                name=self.name,

                tracer_id=self.tracer_id,

                summary=self.summary(),

                statistics=self.statistics(),

                diagnostics=self.diagnostics(),

                generated_at=time.time(),

            )



    def describe(
        self,
    ) -> str:
        """
        Human readable tracer description.
        """

        with self._lock:

            return (

                f"Tracer("
                f"name={self.name}, "
                f"state={self.state.value}, "
                f"enabled={self.enabled}, "
                f"traces={len(self.traces)}, "
                f"spans={len(self.spans)}"
                f")"

            )
# ==============================================================================
# 5.15 Python Protocols
# ==============================================================================


    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """

        return (

            f"<Tracer "
            f"id={self.tracer_id!r} "
            f"name={self.name!r} "
            f"state={self.state.value!r} "
            f"traces={len(self.traces)} "
            f"spans={len(self.spans)}>"
            
        )



    def __str__(
        self,
    ) -> str:
        """
        Human readable representation.
        """

        return (

            f"Tracer[{self.name}] "
            f"({self.state.value})"

        )



    def __len__(
        self,
    ) -> int:
        """
        Return number of registered traces.
        """

        return len(
            self.traces
        )



    def __iter__(
        self,
    ) -> Iterator[Trace]:
        """
        Iterate traces.
        """

        with self._lock:

            yield from (
                self.traces.values()
            )



    def __contains__(
        self,
        item: Any,
    ) -> bool:
        """
        Check trace or span existence.
        """

        with self._lock:

            if isinstance(
                item,
                str,
            ):

                return (

                    item in self.traces

                    or

                    item in self.spans

                )


            if isinstance(
                item,
                Trace,
            ):

                return (
                    item.trace_id
                    in
                    self.traces
                )


            if isinstance(
                item,
                TraceSpan,
            ):

                return (
                    item.span_id
                    in
                    self.spans
                )


            return False



    def __getitem__(
        self,
        key: Union[
            TraceID,
            SpanID,
        ],
    ) -> Any:
        """
        Access trace or span by id.
        """

        with self._lock:

            if key in self.traces:

                return self.traces[key]


            if key in self.spans:

                return self.spans[key]


            raise KeyError(
                key
            )



    def __setitem__(
        self,
        key: TraceID,
        value: Trace,
    ) -> None:
        """
        Register trace using dictionary syntax.
        """

        with self._lock:

            if not isinstance(
                value,
                Trace,
            ):

                raise TraceValidationError(
                    "value must be Trace instance"
                )


            self.traces[key] = value



    def __copy__(
        self,
    ) -> "Tracer":
        """
        Create shallow copy.
        """

        with self._lock:

            new = type(
                self
            )(
                name=self.name,
                sample_rate=self.sample_rate,
                enabled=self.enabled,
            )


            new.traces = self.traces.copy()

            new.spans = self.spans.copy()

            new.statistics = self.statistics.copy()

            new.metrics = self.metrics.copy()

            new.state = self.state


            return new



    def __deepcopy__(
        self,
        memo: Optional[Dict[int, Any]] = None,
    ) -> "Tracer":
        """
        Create deep copy.
        """

        if memo is None:

            memo = {}


        with self._lock:

            new = type(
                self
            )(
                name=self.name,
                sample_rate=self.sample_rate,
                enabled=self.enabled,
            )


            memo[id(self)] = new


            new.__dict__.update(

                copy.deepcopy(

                    self.__dict__,

                    memo,

                )

            )


            new._lock = RLock()


            return new
# ==============================================================================
# Part 5.16 – Public API
# ==============================================================================

# ==============================================================================
# Compatibility Alias
# ==============================================================================

TraceTracer = Tracer

# ==============================================================================
# Part 6. Factory Functions
# ==============================================================================


# ==============================================================================
# 6.1 create_trace()
# ==============================================================================


def create_trace(
    name: Optional[str] = None,
    trace_id: Optional[TraceID] = None,
    attributes: Optional[
        AttributeDict
    ] = None,
    configuration: Optional[
        TraceConfiguration
    ] = None,
) -> Trace:
    """
    Factory function for creating Trace instance.

    Parameters
    ----------
    name:
        Trace name.

    trace_id:
        Optional custom trace identifier.

    attributes:
        Initial trace attributes.

    configuration:
        Trace configuration.

    Returns
    -------
    Trace
        New Trace instance.
    """


    trace = Trace(

        name=name,

        trace_id=trace_id,

        attributes=attributes,

        configuration=configuration,

    )


    return trace
# ==============================================================================
# 6.2 create_span()
# ==============================================================================


def create_span(
    trace: Trace,
    name: Optional[str] = None,
    kind: SpanKind = SpanKind.INTERNAL,
) -> TraceSpan:
    """
    Factory function for creating TraceSpan instance.

    Parameters
    ----------
    trace:
        Parent Trace instance.

    name:
        Span name.

    kind:
        Span kind.

    Returns
    -------
    TraceSpan
        New span instance.
    """


    if not isinstance(
        trace,
        Trace,
    ):
        raise TraceValidationError(
            "trace must be a Trace instance"
        )


    span = TraceSpan(

        trace_id=trace.trace_id,

        name=(

            name

            if name is not None

            else DEFAULT_SPAN_NAME

        ),

        kind=kind,

    )


    trace.add_span(
        span
    )


    return span
# ==============================================================================
# 6.3 create_tracer()
# ==============================================================================


def create_tracer(
    configuration: Optional[
        TraceConfiguration
    ] = None,
) -> Tracer:
    """
    Factory function for creating Tracer instance.

    Parameters
    ----------
    configuration:
        Tracer configuration.

    Returns
    -------
    Tracer
        New Tracer instance.
    """


    if configuration is None:

        configuration = TraceConfiguration()



    tracer = Tracer(

        configuration=configuration,

    )


    return tracer
# ==============================================================================
# 6.4 load_trace()
# ==============================================================================


def load_trace(
    source: Union[
        str,
        Mapping[str, Any],
    ],
    format: Optional[
        TraceFormat
    ] = None,
) -> Trace:
    """
    Load Trace from JSON, YAML, or dictionary.

    Parameters
    ----------
    source:
        Trace data source.

        Supported:
            - dict
            - JSON string
            - YAML string

    format:
        Optional trace format.

    Returns
    -------
    Trace
        Restored Trace instance.
    """


    try:

        # ------------------------------------------------------------------
        # Dictionary
        # ------------------------------------------------------------------

        if isinstance(
            source,
            Mapping,
        ):

            return Trace.from_dict(
                source
            )



        # ------------------------------------------------------------------
        # String formats
        # ------------------------------------------------------------------

        if isinstance(
            source,
            str,
        ):


            # JSON

            if (

                format == TraceFormat.JSON

                or

                source.strip().startswith(
                    "{"
                )

            ):

                return Trace.from_json(
                    source
                )



            # YAML

            if (

                format == TraceFormat.YAML

                or

                "\n" in source

            ):

                try:

                    import yaml


                    data = yaml.safe_load(
                        source
                    )


                    return Trace.from_dict(
                        data
                    )


                except ImportError:

                    raise TraceSerializationError(

                        "PyYAML required for YAML loading"

                    )



        raise TraceSerializationError(

            "Unsupported trace source format"

        )



    except Exception as exc:

        if isinstance(
            exc,
            TraceError,
        ):

            raise


        raise TraceSerializationError(
            str(exc)
        ) from exc
# ==============================================================================
# 6.5 save_trace()
# ==============================================================================


def save_trace(
    trace: Trace,
    path: str,
    format: TraceFormat = TraceFormat.JSON,
) -> str:
    """
    Save Trace to file.

    Parameters
    ----------
    trace:
        Trace instance.

    path:
        Output file path.

    format:
        Export format.

    Returns
    -------
    str
        Saved file path.
    """


    if not isinstance(
        trace,
        Trace,
    ):

        raise TraceValidationError(

            "trace must be a Trace instance"

        )



    try:

        # ------------------------------------------------------------------
        # JSON
        # ------------------------------------------------------------------

        if format == TraceFormat.JSON:

            content = trace.to_json()



        # ------------------------------------------------------------------
        # YAML
        # ------------------------------------------------------------------

        elif format == TraceFormat.YAML:

            try:

                import yaml


                content = yaml.safe_dump(

                    trace.to_dict(),

                    allow_unicode=True,

                    sort_keys=False,

                )


            except ImportError:

                raise TraceSerializationError(

                    "PyYAML required for YAML export"

                )



        # ------------------------------------------------------------------
        # Dict
        # ------------------------------------------------------------------

        elif format == TraceFormat.DICT:

            content = trace.to_dict()



        else:

            raise TraceExportError(

                f"Unsupported format: {format}"

            )



        # ------------------------------------------------------------------
        # Write file
        # ------------------------------------------------------------------

        if isinstance(
            content,
            dict,
        ):

            import json


            with open(
                path,
                "w",
                encoding=DEFAULT_ENCODING,
            ) as file:

                json.dump(

                    content,

                    file,

                    indent=2,

                    ensure_ascii=False,

                    default=str,

                )


        else:

            with open(
                path,
                "w",
                encoding=DEFAULT_ENCODING,
            ) as file:

                file.write(
                    content
                )



        return path



    except Exception as exc:

        if isinstance(
            exc,
            TraceError,
        ):

            raise


        raise TraceExportError(
            str(exc)
        ) from exc
# ==============================================================================
# 6.6 clone_trace()
# ==============================================================================


def clone_trace(
    trace: Trace,
) -> Trace:
    """
    Create a deep copy of Trace.

    Parameters
    ----------
    trace:
        Source Trace instance.

    Returns
    -------
    Trace
        Deep cloned Trace instance.
    """


    if not isinstance(
        trace,
        Trace,
    ):

        raise TraceValidationError(

            "trace must be a Trace instance"

        )


    return copy.deepcopy(
        trace
    )
# ==============================================================================
# 6.7 Factory Registry
# ==============================================================================


TRACE_FACTORIES: Dict[
    str,
    Callable[..., Any],
] = {

    # ------------------------------------------------------------------
    # Core Entities
    # ------------------------------------------------------------------

    "trace": create_trace,

    "span": create_span,

    "tracer": create_tracer,


    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    "load": load_trace,

    "save": save_trace,


    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    "clone": clone_trace,

}



def get_factory(
    name: str,
) -> Callable[..., Any]:
    """
    Get factory function by name.
    """


    if name not in TRACE_FACTORIES:

        raise TraceError(

            f"Unknown factory: {name}"

        )


    return TRACE_FACTORIES[name]



def register_factory(
    name: str,
    factory: Callable[..., Any],
) -> None:
    """
    Register custom factory.
    """


    if not callable(
        factory
    ):

        raise TraceValidationError(

            "factory must be callable"

        )


    TRACE_FACTORIES[name] = factory



def unregister_factory(
    name: str,
) -> None:
    """
    Remove factory from registry.
    """


    TRACE_FACTORIES.pop(
        name,
        None,
    )
# ==============================================================================
# Part 7. Utility Functions
# ==============================================================================


# ==============================================================================
# 7.1 generate_trace_id()
# ==============================================================================


def generate_trace_id() -> TraceID:
    """
    Generate unique trace identifier.
    """

    return uuid_lib.uuid4().hex



# ==============================================================================
# 7.2 generate_span_id()
# ==============================================================================


def generate_span_id() -> SpanID:
    """
    Generate unique span identifier.
    """

    return uuid_lib.uuid4().hex[
        :DEFAULT_SPAN_ID_LENGTH
    ]



# ==============================================================================
# 7.3 current_timestamp()
# ==============================================================================


def current_timestamp() -> Timestamp:
    """
    Return current UTC timestamp.

    Returns
    -------
    float
        Unix timestamp.
    """

    return time.time()



# ==============================================================================
# 7.4 validate_trace_id()
# ==============================================================================


def validate_trace_id(
    trace_id: TraceID,
) -> bool:
    """
    Validate trace identifier format.
    """

    if not isinstance(
        trace_id,
        str,
    ):

        return False


    return (

        len(trace_id)

        ==

        DEFAULT_TRACE_ID_LENGTH

    )



# ==============================================================================
# 7.5 validate_span_id()
# ==============================================================================


def validate_span_id(
    span_id: SpanID,
) -> bool:
    """
    Validate span identifier format.
    """

    if not isinstance(
        span_id,
        str,
    ):

        return False


    return (

        len(span_id)

        ==

        DEFAULT_SPAN_ID_LENGTH

    )



# ==============================================================================
# 7.6 format_duration()
# ==============================================================================


def format_duration(
    duration: Optional[float],
) -> str:
    """
    Format duration value.

    Examples
    --------
    0.001 -> 1ms
    1.5   -> 1.500s
    """

    if duration is None:

        return "0s"



    if duration < 1.0:

        return (

            f"{duration * 1000:.3f}ms"

        )



    if duration < 60.0:

        return (

            f"{duration:.3f}s"

        )



    minutes = int(
        duration // 60
    )

    seconds = (
        duration
        %
        60
    )


    return (

        f"{minutes}m {seconds:.3f}s"

    )



# ==============================================================================
# 7.7 merge_attributes()
# ==============================================================================


def merge_attributes(
    *attributes: Optional[
        Mapping[str, Any]
    ],
) -> AttributeDict:
    """
    Merge multiple attribute dictionaries.

    Later values override previous values.
    """

    result: AttributeDict = {}



    for item in attributes:

        if item is None:

            continue


        if not isinstance(
            item,
            Mapping,
        ):

            raise TraceValidationError(

                "attributes must be mapping"

            )


        result.update(
            item
        )



    return result
# ==============================================================================
# Part 8. Public API
# ==============================================================================


# ==============================================================================
# 8.1 Module Metadata
# ==============================================================================


__version__: str = (
    TRACE_VERSION
)


__author__: str = (
    "SciOS-NG Team"
)


__license__: str = (
    "Apache-2.0"
)


__status__: str = (
    "alpha"
)
# ==============================================================================
# 8.2 Public Symbols
# ==============================================================================


# ------------------------------------------------------------------------------
# Exceptions
# ------------------------------------------------------------------------------

_PUBLIC_EXCEPTIONS = [

    "TraceError",

    "TraceValidationError",

    "TraceStateError",

    "TraceSerializationError",

    "TraceExportError",

    "SpanError",

    "SamplingError",

    "TracerError",

]



# ------------------------------------------------------------------------------
# Enums
# ------------------------------------------------------------------------------

_PUBLIC_ENUMS = [

    "TraceState",

    "TraceStatus",

    "TraceResult",

    "TracePriority",

    "TraceLevel",

    "SpanKind",

    "SpanState",

    "SpanStatus",

    "TracerType",

    "TracerState",

    "TraceFormat",

    "TraceExportMode",

    "ExportState",

    "SamplingState",

    "ProcessingMode",

    "MetricType",

]



# ------------------------------------------------------------------------------
# Dataclasses
# ------------------------------------------------------------------------------

_PUBLIC_DATACLASSES = [

    "TraceConfiguration",

    "TraceAttribute",

    "TraceTag",

    "TraceEvent",

    "TraceContext",

    "TraceRuntimeState",

    "TraceStatistics",

    "TraceMetrics",

    "TraceSnapshot",

    "TraceSummary",

    "TraceReport",

    "TraceExportResult",

    "TraceHealth",

    "TraceValidationResult",

    "TraceDiagnostics",

    "TraceSearchResult",

]



# ------------------------------------------------------------------------------
# Entities
# ------------------------------------------------------------------------------

_PUBLIC_ENTITIES = [

    "TraceSpan",

    "Trace",

    "Tracer",

    "TraceTracer",

]



# ------------------------------------------------------------------------------
# Factory Functions
# ------------------------------------------------------------------------------

_PUBLIC_FACTORIES = [

    "create_trace",

    "create_span",

    "create_tracer",

    "load_trace",

    "save_trace",

    "clone_trace",

]



# ------------------------------------------------------------------------------
# Utilities
# ------------------------------------------------------------------------------

_PUBLIC_UTILITIES = [

    "generate_trace_id",

    "generate_span_id",

    "current_timestamp",

    "validate_trace_id",

    "validate_span_id",

    "format_duration",

    "merge_attributes",

]



# ==============================================================================
# Public Symbol Registry
# ==============================================================================


PUBLIC_SYMBOLS = (

    _PUBLIC_EXCEPTIONS

    +

    _PUBLIC_ENUMS

    +

    _PUBLIC_DATACLASSES

    +

    _PUBLIC_ENTITIES

    +

    _PUBLIC_FACTORIES

    +

    _PUBLIC_UTILITIES

)
# ==============================================================================
# 8.3 __all__
# ==============================================================================


__all__ = [

    # --------------------------------------------------------------------------
    # Metadata
    # --------------------------------------------------------------------------

    "__version__",
    "__author__",
    "__license__",
    "__status__",


    # --------------------------------------------------------------------------
    # Exceptions
    # --------------------------------------------------------------------------

    "TraceError",
    "TraceValidationError",
    "TraceStateError",
    "TraceSerializationError",
    "TraceExportError",
    "SpanError",
    "SamplingError",
    "TracerError",


    # --------------------------------------------------------------------------
    # Enums
    # --------------------------------------------------------------------------

    "TraceState",
    "TraceStatus",
    "TraceResult",
    "TracePriority",
    "TraceLevel",

    "SpanKind",
    "SpanState",
    "SpanStatus",

    "TracerType",
    "TracerState",

    "TraceFormat",
    "TraceExportMode",
    "ExportState",

    "SamplingState",
    "ProcessingMode",
    "MetricType",


    # --------------------------------------------------------------------------
    # Dataclasses
    # --------------------------------------------------------------------------

    "TraceConfiguration",

    "TraceAttribute",
    "TraceTag",
    "TraceEvent",
    "TraceContext",

    "TraceRuntimeState",

    "TraceStatistics",
    "TraceMetrics",

    "TraceSnapshot",
    "TraceSummary",
    "TraceReport",
    "TraceExportResult",

    "TraceHealth",
    "TraceValidationResult",
    "TraceDiagnostics",
    "TraceSearchResult",


    # --------------------------------------------------------------------------
    # Entities
    # --------------------------------------------------------------------------

    "TraceSpan",
    "Trace",
    "Tracer",


    # --------------------------------------------------------------------------
    # Factory Functions
    # --------------------------------------------------------------------------

    "create_trace",
    "create_span",
    "create_tracer",
    "load_trace",
    "save_trace",
    "clone_trace",


    # --------------------------------------------------------------------------
    # Utility Functions
    # --------------------------------------------------------------------------

    "generate_trace_id",
    "generate_span_id",
    "current_timestamp",

    "validate_trace_id",
    "validate_span_id",

    "format_duration",
    "merge_attributes",

]



# ==============================================================================
# 8.4 API Summary
# ==============================================================================


API_SUMMARY = {

    "module": "scios.runtime.observability.tracing.trace",

    "version": __version__,

    "author": __author__,

    "license": __license__,

    "status": __status__,


    "components": {

        "exceptions": len(
            _PUBLIC_EXCEPTIONS
        ),

        "enums": len(
            _PUBLIC_ENUMS
        ),

        "dataclasses": len(
            _PUBLIC_DATACLASSES
        ),

        "entities": len(
            _PUBLIC_ENTITIES
        ),

        "factories": len(
            _PUBLIC_FACTORIES
        ),

        "utilities": len(
            _PUBLIC_UTILITIES
        ),

    },


    "core_entities": [

        "Trace",

        "TraceSpan",

        "Tracer",

    ],


    "capabilities": [

        "lifecycle_management",

        "attributes",

        "tags",

        "events",

        "context",

        "span_management",

        "snapshot",

        "serialization",

        "validation",

        "diagnostics",

        "statistics",

        "search",

        "export",

        "sampling",

        "hooks",

    ],


    "public_api_count": len(
        __all__
    ),

}


# ==============================================================================
# End Of File
# ==============================================================================
"""
SciOS-NG Runtime Observability

Trace Span Runtime Core

File:
    scios/runtime/observability/tracing/span.py

Description:
    Core implementation foundation for distributed tracing spans.

Part 1. Foundation
Part 1.1:
    - Module Docstring
    - Future Annotations
    - Imports
    - Constants
"""


# ==============================================================================
# Future
# ==============================================================================

from __future__ import annotations



# ==============================================================================
# Imports
# ==============================================================================

# Standard Library

import copy

import json

import threading

import time

import uuid


from abc import (
    ABC,
    abstractmethod,
)


from collections import (
    deque,
)


from dataclasses import (
    asdict,
    dataclass,
    field,
)


from enum import (
    Enum,
    IntFlag,
    auto,
)


from pathlib import (
    Path,
)


from threading import (
    RLock,
)


from types import (
    TracebackType,
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
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    TypeAlias,
    Union,
)



# ==============================================================================
# Constants
# ==============================================================================


SPAN_NAME: str = (
    "TraceSpan"
)


SPAN_DESCRIPTION: str = (
    "SciOS-NG Trace Span Runtime Object"
)


SPAN_VERSION: str = (
    "0.1.0"
)

DEFAULT_SPAN_NAME = "span"

DEFAULT_SPAN_KIND = "internal"

DEFAULT_SPAN_STATUS = "unset"

DEFAULT_SPAN_TIMEOUT = 30.0


# ------------------------------------------------------------------------------
# Default configuration
# ------------------------------------------------------------------------------


DEFAULT_KIND: str = (
    "internal"
)


DEFAULT_STATUS: str = (
    "unset"
)


DEFAULT_ENCODING: str = (
    "utf-8"
)


DEFAULT_HISTORY_LIMIT: int = (
    1024
)


DEFAULT_CACHE_SIZE: int = (
    256
)


DEFAULT_ENABLED: bool = (
    True
)


DEFAULT_AUTO_START: bool = (
    False
)


DEFAULT_AUTO_FINISH: bool = (
    False
)



# ------------------------------------------------------------------------------
# Limits
# ------------------------------------------------------------------------------


DEFAULT_ATTRIBUTES_LIMIT: int = (
    128
)


DEFAULT_EVENTS_LIMIT: int = (
    512
)


DEFAULT_LINKS_LIMIT: int = (
    64
)


DEFAULT_TAG_LIMIT: int = (
    64
)


DEFAULT_CHILD_LIMIT: int = (
    1024
)



# ------------------------------------------------------------------------------
# Runtime metadata
# ------------------------------------------------------------------------------


SPAN_SCHEMA_VERSION: str = (
    "1.0"
)


LOGGER_NAME: str = (
    "scios.runtime.observability.tracing.span"
)



# ------------------------------------------------------------------------------
# Serialization
# ------------------------------------------------------------------------------


DEFAULT_INDENT: int = (
    2
)


DEFAULT_JSON_SORT_KEYS: bool = (
    True
)



# ------------------------------------------------------------------------------
# Runtime UUID
# ------------------------------------------------------------------------------


SPAN_ID_LENGTH: int = (
    32
)


TRACE_ID_LENGTH: int = (
    32
)
# ==============================================================================
# Type Aliases
# ==============================================================================


# ------------------------------------------------------------------------------
# Identifier Types
# ------------------------------------------------------------------------------


TraceId: TypeAlias = str


SpanId: TypeAlias = str


ParentSpanId: TypeAlias = str



# ------------------------------------------------------------------------------
# Attribute Types
# ------------------------------------------------------------------------------


AttributeKey: TypeAlias = str


AttributeValue: TypeAlias = Any


Attributes: TypeAlias = Dict[
    AttributeKey,
    AttributeValue,
]



# ------------------------------------------------------------------------------
# Event Types
# ------------------------------------------------------------------------------


TraceEvent: TypeAlias = Dict[
    str,
    Any,
]


TraceAnnotation: TypeAlias = Dict[
    str,
    Any,
]



# ------------------------------------------------------------------------------
# Link Types
# ------------------------------------------------------------------------------


TraceLink: TypeAlias = Dict[
    str,
    Any,
]



# ------------------------------------------------------------------------------
# Metadata Types
# ------------------------------------------------------------------------------


TraceMetadata: TypeAlias = Dict[
    str,
    Any,
]


TraceContextData: TypeAlias = Dict[
    str,
    Any,
]



# ------------------------------------------------------------------------------
# Runtime Storage Types
# ------------------------------------------------------------------------------


TraceCache: TypeAlias = Dict[
    str,
    Any,
]


TraceHistory: TypeAlias = Deque[
    Any,
]



# ------------------------------------------------------------------------------
# Collection Types
# ------------------------------------------------------------------------------


SpanCollection: TypeAlias = Dict[
    SpanId,
    Any,
]


EventCollection: TypeAlias = List[
    TraceEvent,
]


LinkCollection: TypeAlias = List[
    TraceLink,
]



# ------------------------------------------------------------------------------
# Callback / Hook Types
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
    ...,
    bool,
]



# ------------------------------------------------------------------------------
# Configuration Types
# ------------------------------------------------------------------------------


SpanOptions: TypeAlias = Dict[
    str,
    Any,
]


SpanConfiguration: TypeAlias = Dict[
    str,
    Any,
]


SpanAttributes: TypeAlias = Dict[
    str,
    Any,
]



# ------------------------------------------------------------------------------
# Serialization Types
# ------------------------------------------------------------------------------


SerializedSpan: TypeAlias = Dict[
    str,
    Any,
]


SerializedSnapshot: TypeAlias = Dict[
    str,
    Any,
]



# ------------------------------------------------------------------------------
# Generic Runtime Types
# ------------------------------------------------------------------------------


JSONValue: TypeAlias = Union[
    str,
    int,
    float,
    bool,
    None,
    Dict[str, Any],
    List[Any],
]


RuntimeObject: TypeAlias = Any
# ==============================================================================
# Exceptions
# ==============================================================================


class TraceSpanError(Exception):
    """
    Base exception for SciOS-NG TraceSpan runtime.

    All span-related exceptions inherit from this class.
    """

    def __init__(
        self,
        message: str = "",
        *,
        code: str = "SPAN_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:

        self.message: str = message

        self.code: str = code

        self.details: Dict[str, Any] = (
            details or {}
        )

        super().__init__(
            self.message
        )


    def to_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Serialize exception information.
        """

        return {
            "type": self.__class__.__name__,
            "message": self.message,
            "code": self.code,
            "details": self.details,
        }


    def __repr__(
        self,
    ) -> str:

        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r}, "
            f"code={self.code!r})"
        )


# ------------------------------------------------------------------------------


class SpanValidationError(
    TraceSpanError,
):
    """
    Raised when span validation fails.
    """

    def __init__(
        self,
        message: str,
        *,
        field: Optional[str] = None,
        value: Any = None,
    ) -> None:

        details = {}

        if field is not None:
            details["field"] = field

        if value is not None:
            details["value"] = value


        super().__init__(
            message,
            code="SPAN_VALIDATION_ERROR",
            details=details,
        )



# ------------------------------------------------------------------------------


class SpanStateError(
    TraceSpanError,
):
    """
    Raised when span lifecycle state transition is invalid.
    """

    def __init__(
        self,
        message: str,
        *,
        current_state: Optional[str] = None,
        expected_state: Optional[str] = None,
    ) -> None:

        super().__init__(
            message,
            code="SPAN_STATE_ERROR",
            details={
                "current_state": current_state,
                "expected_state": expected_state,
            },
        )



# ------------------------------------------------------------------------------


class SpanClosedError(
    SpanStateError,
):
    """
    Raised when operation is performed on closed span.
    """

    def __init__(
        self,
        message: str = (
            "Span is already closed."
        ),
    ) -> None:

        super().__init__(
            message,
            current_state="closed",
        )

        self.code = (
            "SPAN_CLOSED_ERROR"
        )



# ------------------------------------------------------------------------------


class SpanFinishedError(
    SpanStateError,
):
    """
    Raised when operation is performed on finished span.
    """

    def __init__(
        self,
        message: str = (
            "Span is already finished."
        ),
    ) -> None:

        super().__init__(
            message,
            current_state="finished",
        )

        self.code = (
            "SPAN_FINISHED_ERROR"
        )



# ------------------------------------------------------------------------------


class InvalidTraceError(
    TraceSpanError,
):
    """
    Raised when trace information is invalid.
    """

    def __init__(
        self,
        message: str,
        *,
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None,
    ) -> None:

        super().__init__(
            message,
            code="INVALID_TRACE_ERROR",
            details={
                "trace_id": trace_id,
                "span_id": span_id,
            },
        )

# ==============================================================================
# Compatibility aliases
# ==============================================================================

# ==============================================================================
# Enums
# ==============================================================================


# ------------------------------------------------------------------------------
# Span Kind
# ------------------------------------------------------------------------------


class SpanKind(Enum):
    """
    Defines the semantic role of a span.

    Compatible with distributed tracing models:
        - internal
        - server
        - client
        - producer
        - consumer
    """

    INTERNAL = (
        "internal"
    )

    SERVER = (
        "server"
    )

    CLIENT = (
        "client"
    )

    PRODUCER = (
        "producer"
    )

    CONSUMER = (
        "consumer"
    )


    def __str__(
        self,
    ) -> str:

        return self.value



# ------------------------------------------------------------------------------
# Span Lifecycle State
# ------------------------------------------------------------------------------


class SpanState(Enum):
    """
    Runtime lifecycle state of TraceSpan.
    """

    CREATED = (
        "created"
    )


    INITIALIZED = (
        "initialized"
    )


    STARTED = (
        "started"
    )


    RUNNING = (
        "running"
    )


    FINISHED = (
        "finished"
    )


    CLOSED = (
        "closed"
    )


    FROZEN = (
        "frozen"
    )


    ERROR = (
        "error"
    )


    def __str__(
        self,
    ) -> str:

        return self.value



# ------------------------------------------------------------------------------
# Span Status
# ------------------------------------------------------------------------------


class SpanStatus(Enum):
    """
    Execution status of a span.
    """

    UNSET = (
        "unset"
    )


    OK = (
        "ok"
    )


    ERROR = (
        "error"
    )


    def __str__(
        self,
    ) -> str:

        return self.value



# ------------------------------------------------------------------------------
# Span Capability Flags
# ------------------------------------------------------------------------------


class SpanCapability(IntFlag):
    """
    Capability flags supported by TraceSpan.

    Allows runtime feature discovery.
    """

    NONE = 0


    # ------------------------------------------------------------------
    # Data operations
    # ------------------------------------------------------------------

    EVENTS = auto()

    ATTRIBUTES = auto()

    LINKS = auto()

    STATUS = auto()


    # ------------------------------------------------------------------
    # Error handling
    # ------------------------------------------------------------------

    EXCEPTIONS = auto()


    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    SERIALIZATION = auto()

    SNAPSHOTS = auto()


    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    VALIDATION = auto()


    # ------------------------------------------------------------------
    # Runtime hooks
    # ------------------------------------------------------------------

    CALLBACKS = auto()

    HOOKS = auto()



    # ------------------------------------------------------------------
    # Advanced features
    # ------------------------------------------------------------------

    CACHE = auto()

    HISTORY = auto()

    CHILDREN = auto()



    # ------------------------------------------------------------------
    # Full capability set
    # ------------------------------------------------------------------

    ALL = (
        EVENTS
        |
        ATTRIBUTES
        |
        LINKS
        |
        STATUS
        |
        EXCEPTIONS
        |
        SERIALIZATION
        |
        SNAPSHOTS
        |
        VALIDATION
        |
        CALLBACKS
        |
        HOOKS
        |
        CACHE
        |
        HISTORY
        |
        CHILDREN
    )
# ==============================================================================
# Dataclasses
# ==============================================================================


# ------------------------------------------------------------------------------
# Span Statistics
# ------------------------------------------------------------------------------


@dataclass(slots=True)
class SpanStatistics:
    """
    Runtime statistics for TraceSpan.

    Stores counters and runtime measurements.
    """


    # ------------------------------------------------------------------
    # Counters
    # ------------------------------------------------------------------

    event_count: int = 0


    attribute_count: int = 0


    annotation_count: int = 0


    link_count: int = 0


    child_count: int = 0



    # ------------------------------------------------------------------
    # Runtime operations
    # ------------------------------------------------------------------

    update_count: int = 0


    validation_count: int = 0


    export_count: int = 0


    callback_count: int = 0


    hook_count: int = 0



    # ------------------------------------------------------------------
    # Errors
    # ------------------------------------------------------------------

    error_count: int = 0



    # ------------------------------------------------------------------
    # Timing
    # ------------------------------------------------------------------

    start_time: float = 0.0


    end_time: float = 0.0


    duration: float = 0.0



    # ------------------------------------------------------------------
    # Lifecycle timestamps
    # ------------------------------------------------------------------

    created_at: float = field(
        default_factory=time.time,
    )


    updated_at: float = field(
        default_factory=time.time,
    )



    def reset(
        self,
    ) -> None:
        """
        Reset statistics.
        """

        self.event_count = 0

        self.attribute_count = 0

        self.annotation_count = 0

        self.link_count = 0

        self.child_count = 0

        self.update_count = 0

        self.validation_count = 0

        self.export_count = 0

        self.callback_count = 0

        self.hook_count = 0

        self.error_count = 0

        self.start_time = 0.0

        self.end_time = 0.0

        self.duration = 0.0

        self.updated_at = time.time()



    def to_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Serialize statistics.
        """

        return asdict(
            self
        )



# ------------------------------------------------------------------------------
# Span Snapshot
# ------------------------------------------------------------------------------


@dataclass(slots=True)
class SpanSnapshot:
    """
    Immutable-style serializable snapshot of TraceSpan state.
    """


    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    trace_id: str


    span_id: str


    parent_span_id: Optional[str]



    # ------------------------------------------------------------------
    # Span information
    # ------------------------------------------------------------------

    name: str


    kind: str


    status: str



    # ------------------------------------------------------------------
    # Runtime state
    # ------------------------------------------------------------------

    state: str



    start_time: float


    end_time: Optional[float]


    duration: float



    # ------------------------------------------------------------------
    # Data
    # ------------------------------------------------------------------

    attributes: Dict[str, Any]


    events: List[Dict[str, Any]]


    links: List[Dict[str, Any]]



    metadata: Dict[str, Any]



    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    statistics: Dict[str, Any]



    created_at: float = field(
        default_factory=time.time,
    )



    def to_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Convert snapshot to dictionary.
        """

        return asdict(
            self
        )



    def to_json(
        self,
        *,
        indent: int = DEFAULT_INDENT,
    ) -> str:
        """
        Convert snapshot to JSON.
        """

        return json.dumps(
            self.to_dict(),
            indent=indent,
            sort_keys=DEFAULT_JSON_SORT_KEYS,
            default=str,
        )



# ------------------------------------------------------------------------------
# Span Report
# ------------------------------------------------------------------------------


@dataclass(slots=True)
class SpanReport:
    """
    Runtime summary report of TraceSpan.
    """


    name: str


    trace_id: str


    span_id: str


    kind: str


    status: str


    state: str



    duration: float



    event_count: int


    attribute_count: int


    link_count: int


    child_count: int



    error_count: int



    created_at: float



    generated_at: float = field(
        default_factory=time.time,
    )



    def to_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Convert report to dictionary.
        """

        return asdict(
            self
        )



    def to_json(
        self,
        *,
        indent: int = DEFAULT_INDENT,
    ) -> str:

        return json.dumps(
            self.to_dict(),
            indent=indent,
            sort_keys=DEFAULT_JSON_SORT_KEYS,
            default=str,
        )
# ==============================================================================
# Base Span (ABC)
# ==============================================================================


class BaseSpan(
    ABC,
):
    """
    Abstract base class for SciOS-NG Trace Span.

    Defines the common contract for all span implementations.

    Concrete implementation:
        TraceSpan
    """



    # ==========================================================================
    # Identity
    # ==========================================================================


    @property
    @abstractmethod
    def trace_id(
        self,
    ) -> TraceId:
        """
        Return trace identifier.
        """

        raise NotImplementedError



    @property
    @abstractmethod
    def span_id(
        self,
    ) -> SpanId:
        """
        Return span identifier.
        """

        raise NotImplementedError



    @property
    @abstractmethod
    def parent_span_id(
        self,
    ) -> Optional[SpanId]:
        """
        Return parent span identifier.
        """

        raise NotImplementedError



    # ==========================================================================
    # Metadata
    # ==========================================================================


    @property
    @abstractmethod
    def name(
        self,
    ) -> str:
        """
        Return span name.
        """

        raise NotImplementedError



    @property
    @abstractmethod
    def kind(
        self,
    ) -> SpanKind:
        """
        Return span kind.
        """

        raise NotImplementedError



    @property
    @abstractmethod
    def status(
        self,
    ) -> SpanStatus:
        """
        Return span status.
        """

        raise NotImplementedError



    # ==========================================================================
    # Lifecycle
    # ==========================================================================


    @abstractmethod
    def start(
        self,
    ) -> None:
        """
        Start span execution.
        """

        raise NotImplementedError



    @abstractmethod
    def finish(
        self,
    ) -> None:
        """
        Finish span execution.
        """

        raise NotImplementedError



    @abstractmethod
    def close(
        self,
    ) -> None:
        """
        Close span resources.
        """

        raise NotImplementedError



    # ==========================================================================
    # Attributes
    # ==========================================================================


    @abstractmethod
    def set_attribute(
        self,
        key: AttributeKey,
        value: AttributeValue,
    ) -> None:
        """
        Set span attribute.
        """

        raise NotImplementedError



    @abstractmethod
    def get_attribute(
        self,
        key: AttributeKey,
        default: Any = None,
    ) -> Any:
        """
        Retrieve span attribute.
        """

        raise NotImplementedError



    @abstractmethod
    def attributes(
        self,
    ) -> Mapping[str, Any]:
        """
        Return span attributes.
        """

        raise NotImplementedError



    # ==========================================================================
    # Events
    # ==========================================================================


    @abstractmethod
    def add_event(
        self,
        name: str,
        **attributes: Any,
    ) -> None:
        """
        Add trace event.
        """

        raise NotImplementedError



    @abstractmethod
    def events(
        self,
    ) -> Sequence[TraceEvent]:
        """
        Return span events.
        """

        raise NotImplementedError



    # ==========================================================================
    # Links
    # ==========================================================================


    @abstractmethod
    def add_link(
        self,
        trace_id: TraceId,
        span_id: SpanId,
        **metadata: Any,
    ) -> None:
        """
        Add linked span reference.
        """

        raise NotImplementedError



    @abstractmethod
    def links(
        self,
    ) -> Sequence[TraceLink]:
        """
        Return span links.
        """

        raise NotImplementedError



    # ==========================================================================
    # State
    # ==========================================================================


    @property
    @abstractmethod
    def state(
        self,
    ) -> SpanState:
        """
        Return runtime state.
        """

        raise NotImplementedError



    @property
    @abstractmethod
    def is_finished(
        self,
    ) -> bool:
        """
        Check whether span finished.
        """

        raise NotImplementedError



    @property
    @abstractmethod
    def is_closed(
        self,
    ) -> bool:
        """
        Check whether span closed.
        """

        raise NotImplementedError



    # ==========================================================================
    # Statistics
    # ==========================================================================


    @property
    @abstractmethod
    def statistics(
        self,
    ) -> SpanStatistics:
        """
        Return runtime statistics.
        """

        raise NotImplementedError



    # ==========================================================================
    # Serialization
    # ==========================================================================


    @abstractmethod
    def snapshot(
        self,
    ) -> SpanSnapshot:
        """
        Create immutable snapshot.
        """

        raise NotImplementedError



    @abstractmethod
    def report(
        self,
    ) -> SpanReport:
        """
        Create runtime report.
        """

        raise NotImplementedError



    @abstractmethod
    def to_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Serialize span.
        """

        raise NotImplementedError



    @abstractmethod
    def to_json(
        self,
        *,
        indent: int = DEFAULT_INDENT,
    ) -> str:
        """
        Serialize span as JSON.
        """

        raise NotImplementedError



    # ==========================================================================
    # Context Manager Protocol
    # ==========================================================================


    def __enter__(
        self,
    ) -> "BaseSpan":
        """
        Context manager enter.
        """

        self.start()

        return self



    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        """
        Context manager exit.
        """

        self.finish()

        self.close()                    
# ==============================================================================
# Part 2. BaseSpan (ABC)
# ==============================================================================

from abc import ABC, abstractmethod


class BaseSpan(ABC):
    """
    Abstract base class for SciOS-NG Trace Span.

    Defines the contract that every span implementation
    must provide.
    """

    # ==========================================================================
    # Identity Properties
    # ==========================================================================

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Span name.
        """
        raise NotImplementedError


    @property
    @abstractmethod
    def trace_id(self) -> TraceId:
        """
        Trace identifier.
        """
        raise NotImplementedError


    @property
    @abstractmethod
    def span_id(self) -> SpanId:
        """
        Span identifier.
        """
        raise NotImplementedError


    @property
    @abstractmethod
    def state(self) -> SpanState:
        """
        Current span state.
        """
        raise NotImplementedError


    @property
    @abstractmethod
    def status(self) -> SpanStatus:
        """
        Current span status.
        """
        raise NotImplementedError


    # ==========================================================================
    # Lifecycle
    # ==========================================================================

    @abstractmethod
    def start(self) -> "BaseSpan":
        """
        Start span execution.
        """
        raise NotImplementedError


    @abstractmethod
    def finish(
        self,
        status: SpanStatus = SpanStatus.OK,
    ) -> "BaseSpan":
        """
        Finish span.
        """
        raise NotImplementedError


    @abstractmethod
    def close(self) -> None:
        """
        Close span resources.
        """
        raise NotImplementedError


    @abstractmethod
    def reset(self) -> "BaseSpan":
        """
        Reset span state.
        """
        raise NotImplementedError


    # ==========================================================================
    # Attributes
    # ==========================================================================

    @abstractmethod
    def set_attribute(
        self,
        key: AttributeKey,
        value: AttributeValue,
    ) -> "BaseSpan":
        """
        Set span attribute.
        """
        raise NotImplementedError


    @abstractmethod
    def get_attribute(
        self,
        key: AttributeKey,
        default: Any = None,
    ) -> AttributeValue:
        """
        Get span attribute.
        """
        raise NotImplementedError


    @abstractmethod
    def remove_attribute(
        self,
        key: AttributeKey,
    ) -> bool:
        """
        Remove span attribute.
        """
        raise NotImplementedError


    @abstractmethod
    def clear_attributes(self) -> None:
        """
        Remove all attributes.
        """
        raise NotImplementedError


    # ==========================================================================
    # Events
    # ==========================================================================

    @abstractmethod
    def add_event(
        self,
        name: str,
        attributes: Optional[
            Attributes
        ] = None,
    ) -> "BaseSpan":
        """
        Add trace event.
        """
        raise NotImplementedError


    @abstractmethod
    def clear_events(self) -> None:
        """
        Clear events.
        """
        raise NotImplementedError


    # ==========================================================================
    # Links
    # ==========================================================================

    @abstractmethod
    def add_link(
        self,
        trace_id: TraceId,
        span_id: SpanId,
    ) -> "BaseSpan":
        """
        Add linked span.
        """
        raise NotImplementedError


    @abstractmethod
    def clear_links(self) -> None:
        """
        Clear links.
        """
        raise NotImplementedError


    # ==========================================================================
    # Serialization
    # ==========================================================================

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize span.
        """
        raise NotImplementedError


    @classmethod
    @abstractmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "BaseSpan":
        """
        Deserialize span.
        """
        raise NotImplementedError


    @abstractmethod
    def snapshot(self) -> SpanSnapshot:
        """
        Create immutable snapshot.
        """
        raise NotImplementedError


    # ==========================================================================
    # Utilities
    # ==========================================================================

    @abstractmethod
    def clone(self) -> "BaseSpan":
        """
        Clone span.
        """
        raise NotImplementedError


    @abstractmethod
    def copy(self) -> "BaseSpan":
        """
        Shallow copy.
        """
        raise NotImplementedError


    @abstractmethod
    def validate(self) -> bool:
        """
        Validate internal state.
        """
        raise NotImplementedError


    # ==========================================================================
    # Context Manager
    # ==========================================================================

    def __enter__(self) -> "BaseSpan":
        """
        Context manager enter.
        """

        self.start()

        return self


    def __exit__(
        self,
        exc_type: Optional[type],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        """
        Context manager exit.
        """

        if exc_type is not None:

            self.finish(
                status=SpanStatus.ERROR
            )

        else:

            self.finish(
                status=SpanStatus.OK
            )
# ==============================================================================
# Part 3. TraceSpan Constructor
# ==============================================================================


class TraceSpan(BaseSpan):
    """
    SciOS-NG Runtime Trace Span.

    Concrete implementation of BaseSpan.
    """


    def __init__(
        self,
        name: str = SPAN_NAME,
        *,
        trace_id: Optional[TraceId] = None,
        span_id: Optional[SpanId] = None,
        parent_span_id: Optional[SpanId] = None,
        kind: SpanKind = SpanKind.INTERNAL,
        enabled: bool = DEFAULT_ENABLED,
        auto_start: bool = DEFAULT_AUTO_START,
        auto_finish: bool = DEFAULT_AUTO_FINISH,
        attributes: Optional[Attributes] = None,
        metadata: Optional[TraceMetadata] = None,
        tags: Optional[Sequence[str]] = None,
    ) -> None:
        """
        Initialize TraceSpan runtime.
        """


        # ----------------------------------------------------------------------
        # Identity
        # ----------------------------------------------------------------------

        self._trace_id: TraceId = (
            trace_id
            if trace_id is not None
            else str(uuid.uuid4())
        )


        self._span_id: SpanId = (
            span_id
            if span_id is not None
            else str(uuid.uuid4())
        )


        self._parent_span_id: Optional[SpanId] = (
            parent_span_id
        )


        self._name: str = name



        # ----------------------------------------------------------------------
        # Configuration
        # ----------------------------------------------------------------------

        self._kind: SpanKind = kind

        self._enabled: bool = enabled

        self._auto_start: bool = auto_start

        self._auto_finish: bool = auto_finish



        self._capabilities: SpanCapability = (
            SpanCapability.ALL
        )



        # ----------------------------------------------------------------------
        # Runtime State
        # ----------------------------------------------------------------------

        self._state: SpanState = (
            SpanState.CREATED
        )


        self._status: SpanStatus = (
            SpanStatus.UNSET
        )


        self._started_at: Optional[float] = None


        self._finished_at: Optional[float] = None


        self._duration: float = 0.0



        # ----------------------------------------------------------------------
        # Data Containers
        # ----------------------------------------------------------------------

        self._attributes: Attributes = dict(
            attributes or {}
        )


        self._events: List[TraceEvent] = []


        self._links: List[TraceLink] = []


        self._tags: List[str] = list(
            tags or []
        )


        self._metadata: TraceMetadata = dict(
            metadata or {}
        )



        # ----------------------------------------------------------------------
        # Child Spans
        # ----------------------------------------------------------------------

        self._children: Dict[
            SpanId,
            "TraceSpan",
        ] = {}



        # ----------------------------------------------------------------------
        # Runtime Hooks
        # ----------------------------------------------------------------------

        self._callbacks: List[
            TraceCallback
        ] = []


        self._hooks: Dict[
            str,
            List[TraceHook],
        ] = {}



        # ----------------------------------------------------------------------
        # Synchronization
        # ----------------------------------------------------------------------

        self._lock = RLock()



        # ----------------------------------------------------------------------
        # Statistics
        # ----------------------------------------------------------------------

        self._statistics = (
            SpanStatistics()
        )



        # ----------------------------------------------------------------------
        # Lifecycle timestamps
        # ----------------------------------------------------------------------

        self._created_at: float = (
            time.time()
        )


        self._updated_at: float = (
            self._created_at
        )



        # ----------------------------------------------------------------------
        # Cache
        # ----------------------------------------------------------------------

        self._cache: Dict[
            str,
            Any,
        ] = {}



        # ----------------------------------------------------------------------
        # History
        # ----------------------------------------------------------------------

        self._history: deque[Any] = deque(
            maxlen=DEFAULT_HISTORY_LIMIT
        )



        # ----------------------------------------------------------------------
        # Final initialization
        # ----------------------------------------------------------------------

        self._state = (
            SpanState.INITIALIZED
        )


        self._updated_at = (
            time.time()
        )


        if self._auto_start:

            self.start()
# ==============================================================================
# Part 4. Properties
# ==============================================================================


    # ==========================================================================
    # Identity
    # ==========================================================================

    @property
    def name(self) -> str:
        """
        Return span name.
        """

        return self._name



    @name.setter
    def name(
        self,
        value: str,
    ) -> None:
        """
        Update span name.
        """

        if not value:
            raise SpanValidationError(
                "Span name cannot be empty."
            )

        self._name = value

        self._updated_at = time.time()



    @property
    def trace_id(self) -> TraceId:
        """
        Return trace identifier.
        """

        return self._trace_id



    @property
    def span_id(self) -> SpanId:
        """
        Return span identifier.
        """

        return self._span_id



    @property
    def parent_span_id(
        self,
    ) -> Optional[SpanId]:
        """
        Return parent span identifier.
        """

        return self._parent_span_id



    # ==========================================================================
    # Configuration
    # ==========================================================================

    @property
    def kind(self) -> SpanKind:
        """
        Return span kind.
        """

        return self._kind



    @kind.setter
    def kind(
        self,
        value: SpanKind,
    ) -> None:
        """
        Update span kind.
        """

        if not isinstance(
            value,
            SpanKind,
        ):
            raise SpanValidationError(
                "kind must be SpanKind."
            )

        self._kind = value

        self._updated_at = time.time()



    @property
    def enabled(self) -> bool:
        """
        Whether span is enabled.
        """

        return self._enabled



    @enabled.setter
    def enabled(
        self,
        value: bool,
    ) -> None:
        """
        Enable or disable span.
        """

        self._enabled = bool(value)

        self._updated_at = time.time()



    @property
    def capabilities(self) -> SpanCapability:
        """
        Supported capabilities.
        """

        return self._capabilities



    # ==========================================================================
    # Runtime State
    # ==========================================================================

    @property
    def state(self) -> SpanState:
        """
        Current span state.
        """

        return self._state



    @property
    def status(self) -> SpanStatus:
        """
        Current span status.
        """

        return self._status



    @status.setter
    def status(
        self,
        value: SpanStatus,
    ) -> None:
        """
        Update span status.
        """

        if not isinstance(
            value,
            SpanStatus,
        ):
            raise SpanValidationError(
                "status must be SpanStatus."
            )

        self._status = value

        self._updated_at = time.time()



    @property
    def started_at(
        self,
    ) -> Optional[float]:
        """
        Start timestamp.
        """

        return self._started_at



    @property
    def finished_at(
        self,
    ) -> Optional[float]:
        """
        Finish timestamp.
        """

        return self._finished_at



    @property
    def duration(self) -> float:
        """
        Span duration.
        """

        return self._duration



    # ==========================================================================
    # Data
    # ==========================================================================

    @property
    def attributes(self) -> Mapping[str, Any]:
        """
        Span attributes.
        """

        return dict(
            self._attributes
        )



    @property
    def events(self) -> Sequence[TraceEvent]:
        """
        Span events.
        """

        return list(
            self._events
        )



    @property
    def links(self) -> Sequence[TraceLink]:
        """
        Span links.
        """

        return list(
            self._links
        )



    @property
    def tags(self) -> Sequence[str]:
        """
        Span tags.
        """

        return list(
            self._tags
        )



    @tags.setter
    def tags(
        self,
        value: Sequence[str],
    ) -> None:
        """
        Replace tags.
        """

        self._tags = list(value)

        self._updated_at = time.time()



    @property
    def metadata(self) -> Mapping[str, Any]:
        """
        Span metadata.
        """

        return dict(
            self._metadata
        )



    @metadata.setter
    def metadata(
        self,
        value: Mapping[str, Any],
    ) -> None:
        """
        Replace metadata.
        """

        self._metadata = dict(value)

        self._updated_at = time.time()



    # ==========================================================================
    # Runtime Containers
    # ==========================================================================

    @property
    def statistics(
        self,
    ) -> SpanStatistics:
        """
        Span statistics.
        """

        return self._statistics



    @property
    def children(
        self,
    ) -> Mapping[SpanId, "TraceSpan"]:
        """
        Child spans.
        """

        return dict(
            self._children
        )



    @property
    def created_at(self) -> float:
        """
        Creation timestamp.
        """

        return self._created_at



    @property
    def updated_at(self) -> float:
        """
        Last update timestamp.
        """

        return self._updated_at



    # ==========================================================================
    # State Helpers
    # ==========================================================================

    @property
    def active(self) -> bool:
        """
        Whether span is running.
        """

        return self._state in (
            SpanState.STARTED,
            SpanState.RUNNING,
        )



    @property
    def finished(self) -> bool:
        """
        Whether span finished.
        """

        return (
            self._state == SpanState.FINISHED
        )



    @property
    def closed(self) -> bool:
        """
        Whether span closed.
        """

        return (
            self._state == SpanState.CLOSED
        )



    @property
    def valid(self) -> bool:
        """
        Validate current span state.
        """

        try:
            return self.validate()

        except Exception:
            return False
# ==============================================================================
# Part 5. Lifecycle
# ==============================================================================


    # ==========================================================================
    # Internal State Transition
    # ==========================================================================

    def _transition_state(
        self,
        state: SpanState,
    ) -> None:
        """
        Update span lifecycle state.
        """

        if not isinstance(
            state,
            SpanState,
        ):
            raise SpanStateError(
                "Invalid span state."
            )

        self._state = state

        self._updated_at = time.time()



    # ==========================================================================
    # Start
    # ==========================================================================

    def start(self) -> "TraceSpan":
        """
        Start span execution.
        """

        with self._lock:

            if self.closed:
                raise SpanClosedError(
                    "Cannot start closed span."
                )


            if self.active:
                return self


            self._before_start()


            now = time.time()

            self._started_at = now

            self._finished_at = None

            self._duration = 0.0


            self._transition_state(
                SpanState.STARTED
            )


            self._transition_state(
                SpanState.RUNNING
            )


            self._history.append(
                {
                    "event": "start",
                    "timestamp": now,
                }
            )


            self._statistics.update_count += 1


            self._after_start()


            return self



    # ==========================================================================
    # Finish
    # ==========================================================================

    def finish(
        self,
        status: SpanStatus = SpanStatus.OK,
    ) -> "TraceSpan":
        """
        Finish span execution.
        """

        with self._lock:

            if self.closed:
                raise SpanClosedError(
                    "Cannot finish closed span."
                )


            if self.finished:

                return self


            self._before_finish()


            now = time.time()


            self._finished_at = now


            if self._started_at is not None:

                self._duration = (
                    now -
                    self._started_at
                )


            self._status = status


            self._transition_state(
                SpanState.FINISHED
            )


            self._statistics.update_count += 1


            if status == SpanStatus.ERROR:

                self._statistics.error_count += 1



            self._history.append(
                {
                    "event": "finish",
                    "status": status.value,
                    "timestamp": now,
                }
            )


            self._after_finish()


            return self



    # ==========================================================================
    # Close
    # ==========================================================================

    def close(self) -> None:
        """
        Close span resources.
        """

        with self._lock:

            if self.closed:

                return


            self._before_close()


            if self.active:

                self.finish()



            self._transition_state(
                SpanState.CLOSED
            )


            self._history.append(
                {
                    "event": "close",
                    "timestamp": time.time(),
                }
            )


            self._after_close()



    # ==========================================================================
    # Reset
    # ==========================================================================

    def reset(self) -> "TraceSpan":
        """
        Reset span runtime state.
        """

        with self._lock:

            if self.closed:

                raise SpanClosedError(
                    "Cannot reset closed span."
                )


            self._state = (
                SpanState.INITIALIZED
            )


            self._status = (
                SpanStatus.UNSET
            )


            self._started_at = None


            self._finished_at = None


            self._duration = 0.0


            self._events.clear()

            self._links.clear()

            self._children.clear()


            self._history.clear()


            self._statistics = (
                SpanStatistics()
            )


            self._updated_at = (
                time.time()
            )


            return self



    # ==========================================================================
    # Enable / Disable
    # ==========================================================================

    def enable(self) -> "TraceSpan":
        """
        Enable span.
        """

        self._enabled = True

        self._updated_at = time.time()

        return self



    def disable(self) -> "TraceSpan":
        """
        Disable span.
        """

        self._enabled = False

        self._updated_at = time.time()

        return self



    # ==========================================================================
    # Freeze / Unfreeze
    # ==========================================================================

    def freeze(self) -> "TraceSpan":
        """
        Freeze span mutation.
        """

        with self._lock:

            if self.closed:

                raise SpanClosedError(
                    "Closed span cannot freeze."
                )


            self._transition_state(
                SpanState.FROZEN
            )


            return self



    def unfreeze(self) -> "TraceSpan":
        """
        Resume span mutation.
        """

        with self._lock:

            if self._state != SpanState.FROZEN:

                return self


            self._transition_state(
                SpanState.RUNNING
            )


            return self



    # ==========================================================================
    # Lifecycle Hooks
    # ==========================================================================

    def _before_start(self) -> None:
        """
        Hook before start.
        """

        return None



    def _after_start(self) -> None:
        """
        Hook after start.
        """

        return None



    def _before_finish(self) -> None:
        """
        Hook before finish.
        """

        return None



    def _after_finish(self) -> None:
        """
        Hook after finish.
        """

        return None



    def _before_close(self) -> None:
        """
        Hook before close.
        """

        return None



    def _after_close(self) -> None:
        """
        Hook after close.
        """

        return None
# ==============================================================================
# Part 6. Attributes
# ==============================================================================


    # ==========================================================================
    # Set Attribute
    # ==========================================================================

    def set_attribute(
        self,
        key: AttributeKey,
        value: AttributeValue,
    ) -> "TraceSpan":
        """
        Set or update span attribute.
        """

        with self._lock:

            if self.closed:
                raise SpanClosedError(
                    "Cannot modify closed span."
                )


            if not isinstance(
                key,
                str,
            ):
                raise SpanValidationError(
                    "Attribute key must be string."
                )


            if not key:
                raise SpanValidationError(
                    "Attribute key cannot be empty."
                )


            self._before_attribute_update(
                key,
                value,
            )


            self._attributes[key] = value


            self._statistics.attribute_count = (
                len(self._attributes)
            )


            self._statistics.update_count += 1


            self._updated_at = time.time()


            self._history.append(
                {
                    "event": "attribute_set",
                    "key": key,
                    "timestamp": self._updated_at,
                }
            )


            self._after_attribute_update(
                key,
                value,
            )


            return self



    # ==========================================================================
    # Get Attribute
    # ==========================================================================

    def get_attribute(
        self,
        key: AttributeKey,
        default: AttributeValue = None,
    ) -> AttributeValue:
        """
        Get attribute value.
        """

        return self._attributes.get(
            key,
            default,
        )



    # ==========================================================================
    # Has Attribute
    # ==========================================================================

    def has_attribute(
        self,
        key: AttributeKey,
    ) -> bool:
        """
        Check attribute existence.
        """

        return key in self._attributes



    # ==========================================================================
    # Remove Attribute
    # ==========================================================================

    def remove_attribute(
        self,
        key: AttributeKey,
    ) -> bool:
        """
        Remove attribute.
        """

        with self._lock:

            if self.closed:
                raise SpanClosedError(
                    "Cannot modify closed span."
                )


            if key not in self._attributes:

                return False


            del self._attributes[key]


            self._statistics.attribute_count = (
                len(self._attributes)
            )


            self._statistics.update_count += 1


            self._updated_at = time.time()


            self._history.append(
                {
                    "event": "attribute_remove",
                    "key": key,
                    "timestamp": self._updated_at,
                }
            )


            return True



    # ==========================================================================
    # Clear Attributes
    # ==========================================================================

    def clear_attributes(
        self,
    ) -> None:
        """
        Remove all attributes.
        """

        with self._lock:

            if self.closed:
                raise SpanClosedError(
                    "Cannot modify closed span."
                )


            self._attributes.clear()


            self._statistics.attribute_count = 0


            self._statistics.update_count += 1


            self._updated_at = time.time()



    # ==========================================================================
    # Bulk Operations
    # ==========================================================================

    def set_attributes(
        self,
        attributes: Mapping[str, Any],
    ) -> "TraceSpan":
        """
        Set multiple attributes.
        """

        with self._lock:

            for key, value in attributes.items():

                self.set_attribute(
                    key,
                    value,
                )


        return self



    def update_attributes(
        self,
        attributes: Mapping[str, Any],
    ) -> "TraceSpan":
        """
        Update attributes from mapping.
        """

        return self.set_attributes(
            attributes
        )



    def copy_attributes(
        self,
    ) -> Attributes:
        """
        Return attribute copy.
        """

        return dict(
            self._attributes
        )



    # ==========================================================================
    # Attribute Statistics
    # ==========================================================================

    @property
    def attribute_count(
        self,
    ) -> int:
        """
        Number of attributes.
        """

        return len(
            self._attributes
        )



    # ==========================================================================
    # Attribute Hooks
    # ==========================================================================

    def _before_attribute_update(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Hook before attribute update.
        """

        return None



    def _after_attribute_update(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Hook after attribute update.
        """

        return None
# ==============================================================================
# Part 7. Events
# ==============================================================================


    # ==========================================================================
    # Add Event
    # ==========================================================================

    def add_event(
        self,
        name: str,
        attributes: Optional[Attributes] = None,
    ) -> "TraceSpan":
        """
        Add tracing event.

        Example:
            span.add_event(
                "database.query",
                {
                    "sql": "SELECT *"
                }
            )
        """

        with self._lock:

            if self.closed:
                raise SpanClosedError(
                    "Cannot add event to closed span."
                )


            if not isinstance(name, str):

                raise SpanValidationError(
                    "Event name must be string."
                )


            if not name:

                raise SpanValidationError(
                    "Event name cannot be empty."
                )


            self._before_event(
                name,
                attributes,
            )


            event = {

                "id":
                    str(uuid.uuid4()),

                "name":
                    name,

                "timestamp":
                    time.time(),

                "attributes":
                    dict(attributes or {}),

            }


            self._events.append(
                event
            )


            self._statistics.event_count = (
                len(self._events)
            )


            self._statistics.update_count += 1


            self._updated_at = time.time()


            self._history.append(
                {
                    "event": "event_added",
                    "name": name,
                    "timestamp": self._updated_at,
                }
            )


            self._after_event(
                event
            )


            return self



    # ==========================================================================
    # Get Event
    # ==========================================================================

    def get_event(
        self,
        event_id: str,
    ) -> Optional[TraceEvent]:
        """
        Retrieve event by id.
        """

        for event in self._events:

            if event.get(
                "id"
            ) == event_id:

                return dict(event)


        return None



    # ==========================================================================
    # Get Events
    # ==========================================================================

    def get_events(
        self,
    ) -> List[TraceEvent]:
        """
        Return all events.
        """

        return [
            dict(event)
            for event in self._events
        ]



    # ==========================================================================
    # Remove Event
    # ==========================================================================

    def remove_event(
        self,
        event_id: str,
    ) -> bool:
        """
        Remove event.
        """

        with self._lock:

            if self.closed:
                raise SpanClosedError(
                    "Cannot modify closed span."
                )


            for index, event in enumerate(
                self._events
            ):

                if event.get(
                    "id"
                ) == event_id:

                    del self._events[index]


                    self._statistics.event_count = (
                        len(self._events)
                    )


                    self._statistics.update_count += 1


                    self._updated_at = time.time()


                    return True


            return False



    # ==========================================================================
    # Clear Events
    # ==========================================================================

    def clear_events(
        self,
    ) -> None:
        """
        Remove all events.
        """

        with self._lock:

            if self.closed:

                raise SpanClosedError(
                    "Cannot modify closed span."
                )


            self._events.clear()


            self._statistics.event_count = 0


            self._statistics.update_count += 1


            self._updated_at = time.time()



    # ==========================================================================
    # Record Exception
    # ==========================================================================

    def record_exception(
        self,
        exception: BaseException,
        *,
        attributes: Optional[Attributes] = None,
    ) -> "TraceSpan":
        """
        Record exception as tracing event.
        """

        if not isinstance(
            exception,
            BaseException,
        ):

            raise SpanValidationError(
                "exception must derive from BaseException."
            )


        data = {

            "exception.type":
                type(exception).__name__,


            "exception.message":
                str(exception),


        }


        if attributes:

            data.update(
                attributes
            )


        self.add_event(
            "exception",
            data,
        )


        self._status = (
            SpanStatus.ERROR
        )


        self._statistics.error_count += 1


        return self



    # ==========================================================================
    # Event Count
    # ==========================================================================

    @property
    def event_count(
        self,
    ) -> int:
        """
        Number of events.
        """

        return len(
            self._events
        )



    # ==========================================================================
    # Event Hooks
    # ==========================================================================

    def _before_event(
        self,
        name: str,
        attributes: Optional[Attributes],
    ) -> None:
        """
        Hook before adding event.
        """

        return None



    def _after_event(
        self,
        event: TraceEvent,
    ) -> None:
        """
        Hook after adding event.
        """

        return None
# ==============================================================================
# Part 8. Serialization
# ==============================================================================


    # ==========================================================================
    # Convert To Dictionary
    # ==========================================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Serialize TraceSpan into dictionary.
        """

        with self._lock:

            self._before_serialize()


            data = {

                "identity": {

                    "trace_id":
                        self.trace_id,

                    "span_id":
                        self.span_id,

                    "parent_id":
                        self.parent_id,

                    "name":
                        self.name,

                },


                "configuration": {

                    "kind":
                        self.kind.value
                        if isinstance(
                            self.kind,
                            Enum,
                        )
                        else self.kind,

                },


                "runtime": {

                    "state":
                        self._state.value
                        if isinstance(
                            self._state,
                            Enum,
                        )
                        else self._state,


                    "status":
                        self._status.value
                        if isinstance(
                            self._status,
                            Enum,
                        )
                        else self._status,


                    "started_at":
                        self._started_at,


                    "finished_at":
                        self._finished_at,


                    "duration":
                        self.duration,

                },


                "attributes":
                    dict(
                        self._attributes
                    ),


                "events":
                    list(
                        self._events
                    ),


                "links":
                    list(
                        self._links
                    ),


                "statistics":
                    asdict(
                        self._statistics
                    ),


                "metadata":
                    dict(
                        self._metadata
                    ),

            }


            return data



    # ==========================================================================
    # Create From Dictionary
    # ==========================================================================

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "TraceSpan":
        """
        Restore TraceSpan from dictionary.
        """

        identity = (
            data.get(
                "identity",
                {},
            )
        )


        configuration = (
            data.get(
                "configuration",
                {},
            )
        )


        span = cls(

            name=
                identity.get(
                    "name",
                    DEFAULT_SPAN_NAME,
                ),

            trace_id=
                identity.get(
                    "trace_id",
                ),

            parent_id=
                identity.get(
                    "parent_id",
                ),

            kind=
                SpanKind(
                    configuration.get(
                        "kind",
                        DEFAULT_KIND,
                    )
                ),

        )


        span._attributes.update(
            data.get(
                "attributes",
                {},
            )
        )


        span._events.extend(
            data.get(
                "events",
                [],
            )
        )


        span._links.extend(
            data.get(
                "links",
                [],
            )
        )


        runtime = (
            data.get(
                "runtime",
                {},
            )
        )


        if runtime.get(
            "status"
        ):

            span._status = SpanStatus(
                runtime["status"]
            )


        if runtime.get(
            "state"
        ):

            span._state = SpanState(
                runtime["state"]
            )


        span._started_at = (
            runtime.get(
                "started_at"
            )
        )


        span._finished_at = (
            runtime.get(
                "finished_at"
            )
        )


        span._metadata.update(
            data.get(
                "metadata",
                {},
            )
        )


        span._after_deserialize()


        return span



    # ==========================================================================
    # JSON Serialization
    # ==========================================================================

    def to_json(
        self,
        *,
        indent: int = 2,
    ) -> str:
        """
        Serialize span to JSON.
        """

        return json.dumps(

            self.to_dict(),

            indent=indent,

            default=str,

        )



    @classmethod
    def from_json(
        cls,
        payload: str,
    ) -> "TraceSpan":
        """
        Restore span from JSON.
        """

        return cls.from_dict(
            json.loads(
                payload
            )
        )



    # ==========================================================================
    # File Persistence
    # ==========================================================================

    def save(
        self,
        path: Union[str, Path],
    ) -> None:
        """
        Save span snapshot to file.
        """

        target = Path(
            path
        )


        target.write_text(

            self.to_json(),

            encoding=DEFAULT_ENCODING,

        )



    @classmethod
    def load(
        cls,
        path: Union[str, Path],
    ) -> "TraceSpan":
        """
        Load span from file.
        """

        source = Path(
            path
        )


        return cls.from_json(

            source.read_text(
                encoding=DEFAULT_ENCODING,
            )

        )



    # ==========================================================================
    # Snapshot
    # ==========================================================================

    def snapshot(
        self,
    ) -> SpanSnapshot:
        """
        Create runtime snapshot.
        """

        return SpanSnapshot(

            identity={
                "trace_id":
                    self.trace_id,

                "span_id":
                    self.span_id,

                "name":
                    self.name,
            },


            runtime={
                "state":
                    self._state.value,

                "status":
                    self._status.value,

            },


            attributes=
                dict(
                    self._attributes
                ),


            events=
                list(
                    self._events
                ),


            links=
                list(
                    self._links
                ),


            statistics=
                asdict(
                    self._statistics
                ),

        )



    def restore(
        self,
        snapshot: SpanSnapshot,
    ) -> "TraceSpan":
        """
        Restore runtime snapshot.
        """

        self._attributes.clear()

        self._attributes.update(
            snapshot.attributes
        )


        self._events.clear()

        self._events.extend(
            snapshot.events
        )


        self._links.clear()

        self._links.extend(
            snapshot.links
        )


        self._statistics = (
            SpanStatistics(
                **snapshot.statistics
            )
        )


        return self



    # ==========================================================================
    # Serialization Hooks
    # ==========================================================================

    def _before_serialize(
        self,
    ) -> None:
        """
        Hook before serialization.
        """

        return None



    def _after_deserialize(
        self,
    ) -> None:
        """
        Hook after deserialization.
        """

        return None
# ==============================================================================
# Part 9. Statistics & Reports
# ==============================================================================


    # ==========================================================================
    # Statistics
    # ==========================================================================

    def statistics(
        self,
    ) -> SpanStatistics:
        """
        Return runtime statistics snapshot.
        """

        with self._lock:

            return copy.deepcopy(
                self._statistics
            )



    # ==========================================================================
    # Runtime Statistics
    # ==========================================================================

    def runtime_statistics(
        self,
    ) -> Dict[str, Any]:
        """
        Return detailed runtime metrics.
        """

        with self._lock:

            now = time.time()


            return {

                "identity": {

                    "trace_id":
                        self.trace_id,

                    "span_id":
                        self.span_id,

                    "name":
                        self.name,

                },


                "state":
                    self._state.value,


                "status":
                    self._status.value,


                "duration":
                    self.duration,


                "uptime":

                    now -
                    self._created_at,


                "events":

                    len(
                        self._events
                    ),


                "attributes":

                    len(
                        self._attributes
                    ),


                "links":

                    len(
                        self._links
                    ),


                "statistics":

                    asdict(
                        self._statistics
                    ),

            }



    # ==========================================================================
    # Report
    # ==========================================================================

    def report(
        self,
    ) -> SpanReport:
        """
        Generate span report.
        """

        duration = (
            self.duration
        )


        return SpanReport(

            name=self.name,

            trace_id=self.trace_id,

            span_id=self.span_id,

            kind=(
                self.kind.value
                if isinstance(
                    self.kind,
                    Enum,
                )
                else str(self.kind)
            ),


            status=(
                self._status.value
                if isinstance(
                    self._status,
                    Enum,
                )
                else str(self._status)
            ),


            duration=duration,


            event_count=
                len(
                    self._events
                ),


            attribute_count=
                len(
                    self._attributes
                ),


            error_count=
                self._statistics.error_count,


            created_at=
                self._created_at,

        )



    # ==========================================================================
    # Summary
    # ==========================================================================

    def summary(
        self,
    ) -> Dict[str, Any]:
        """
        Compact human-readable summary.
        """

        return {

            "name":
                self.name,


            "trace_id":
                self.trace_id,


            "span_id":
                self.span_id,


            "status":
                self._status.value,


            "state":
                self._state.value,


            "duration":
                self.duration,


            "events":
                self.event_count,


            "attributes":
                len(
                    self._attributes
                ),


            "errors":
                self._statistics.error_count,

        }



    # ==========================================================================
    # Diagnostics
    # ==========================================================================

    def diagnostics(
        self,
    ) -> Dict[str, Any]:
        """
        Full diagnostic information.
        """

        return {

            "healthy":
                self.health(),


            "summary":
                self.summary(),


            "runtime":
                self.runtime_statistics(),


            "snapshot":
                self.snapshot(),

        }



    # ==========================================================================
    # Success Rate
    # ==========================================================================

    def success_rate(
        self,
    ) -> float:
        """
        Calculate successful execution rate.

        Span level:
            OK -> 1.0
            ERROR -> 0.0
        """

        if self._status == SpanStatus.OK:

            return 1.0


        if self._status == SpanStatus.ERROR:

            return 0.0


        return 0.5



    # ==========================================================================
    # Failure Rate
    # ==========================================================================

    def failure_rate(
        self,
    ) -> float:
        """
        Calculate failure rate.
        """

        return (
            1.0 -
            self.success_rate()
        )



    # ==========================================================================
    # Duration Statistics
    # ==========================================================================

    def duration_statistics(
        self,
    ) -> Dict[str, float]:
        """
        Duration metrics.
        """

        duration = (
            self.duration
        )


        return {

            "current":
                duration,


            "minimum":
                duration,


            "maximum":
                duration,


            "average":
                duration,

        }



    # ==========================================================================
    # Throughput
    # ==========================================================================

    def throughput(
        self,
    ) -> float:
        """
        Calculate events throughput.
        """

        duration = (
            self.duration
        )


        if duration <= 0:

            return 0.0


        return (
            self.event_count /
            duration
        )



    # ==========================================================================
    # Health Check
    # ==========================================================================

    def health(
        self,
    ) -> bool:
        """
        Runtime health status.
        """

        if self.closed:

            return False


        if self._state == SpanState.ERROR:

            return False


        return True
# ==============================================================================
# Part 10. Python Protocols
# ==============================================================================


    # ==========================================================================
    # Representation
    # ==========================================================================

    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """

        return (
            f"TraceSpan("
            f"name={self.name!r}, "
            f"trace_id={self.trace_id!r}, "
            f"span_id={self.span_id!r}, "
            f"state={self._state.value!r}, "
            f"status={self._status.value!r}"
            f")"
        )



    def __str__(
        self,
    ) -> str:
        """
        Human readable representation.
        """

        return (
            f"{self.name}"
            f"[{self.span_id}] "
            f"{self._status.value}"
        )



    # ==========================================================================
    # Container Protocol
    # ==========================================================================

    def __len__(
        self,
    ) -> int:
        """
        Return number of stored items.

        Items:
            attributes
            events
            links
        """

        return (
            len(self._attributes)
            +
            len(self._events)
            +
            len(self._links)
        )



    def __iter__(
        self,
    ) -> Iterator[str]:
        """
        Iterate attributes.
        """

        return iter(
            self._attributes
        )



    def __contains__(
        self,
        item: str,
    ) -> bool:
        """
        Check attribute existence.
        """

        return (
            item in self._attributes
        )



    # ==========================================================================
    # Mapping Protocol
    # ==========================================================================

    def __getitem__(
        self,
        key: str,
    ) -> Any:
        """
        Dictionary-style access.

        Example:

            span["service"]

        """

        return self._attributes[key]



    def __setitem__(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Dictionary-style assignment.

        Example:

            span["model"] = "QTC"

        """

        self.set_attribute(
            key,
            value,
        )



    # ==========================================================================
    # Boolean Protocol
    # ==========================================================================

    def __bool__(
        self,
    ) -> bool:
        """
        Span truth evaluation.
        """

        return (
            not self.closed
            and
            self._state
            != SpanState.ERROR
        )



    # ==========================================================================
    # Copy Protocol
    # ==========================================================================

    def __copy__(
        self,
    ) -> "TraceSpan":
        """
        Shallow copy.
        """

        return self.from_dict(
            self.to_dict()
        )



    def __deepcopy__(
        self,
        memo: Optional[Dict[int, Any]] = None,
    ) -> "TraceSpan":
        """
        Deep copy.
        """

        if memo is None:

            memo = {}


        copied = self.from_dict(
            copy.deepcopy(
                self.to_dict(),
                memo,
            )
        )


        memo[id(self)] = copied


        return copied



    # ==========================================================================
    # Context Manager
    # ==========================================================================

    def __enter__(
        self,
    ) -> "TraceSpan":
        """
        Enter tracing context.
        """

        self.start()

        return self



    def __exit__(
        self,
        exc_type: Optional[type],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        """
        Exit tracing context.
        """

        if exc_value is not None:

            self.record_exception(
                exc_value
            )


        self.finish()
# ==============================================================================
# Part 11. Public API
# ==============================================================================

Span = TraceSpan

__all__ = [

    # --------------------------------------------------------------------------
    # Metadata
    # --------------------------------------------------------------------------

    "__version__",


    # --------------------------------------------------------------------------
    # Constants
    # --------------------------------------------------------------------------

    "TRACER_NAME",

    "TRACER_DESCRIPTION",

    "TRACER_VERSION",

    "DEFAULT_HISTORY_LIMIT",

    "DEFAULT_TIMEOUT",

    "DEFAULT_ENCODING",

    "DEFAULT_TRACER_TYPE",

    "DEFAULT_TRACE_NAME",

    "DEFAULT_SPAN_NAME",

    "DEFAULT_CACHE_SIZE",

    "DEFAULT_MAX_ACTIVE_SPANS",

    "LOGGER_NAME",



    # --------------------------------------------------------------------------
    # Type Aliases
    # --------------------------------------------------------------------------

    "TraceId",

    "SpanId",

    "TracerOptions",

    "TracerMetadata",

    "TracerStatisticsMap",

    "HookName",

    "TraceHook",

    "TraceCallback",

    "SpanCollection",

    "TraceCollection",



    # --------------------------------------------------------------------------
    # Exceptions
    # --------------------------------------------------------------------------

    "TracerError",

    "TracerClosedError",

    "TracerValidationError",

    "TraceNotFoundError",

    "SpanNotFoundError",



    # --------------------------------------------------------------------------
    # Enums
    # --------------------------------------------------------------------------

    "TracerType",

    "TracerState",



    # --------------------------------------------------------------------------
    # Dataclasses
    # --------------------------------------------------------------------------

    "TracerStatistics",

    "TracerSnapshot",

    "TracerReport",



    # --------------------------------------------------------------------------
    # Base Classes
    # --------------------------------------------------------------------------

    "BaseTracer",



    # --------------------------------------------------------------------------
    # Main Implementation
    # --------------------------------------------------------------------------

    "TraceTracer",

]                                                                                    
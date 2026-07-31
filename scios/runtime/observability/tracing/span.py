"""
SciOS Runtime Observability

Trace Span Runtime

File:
    scios/runtime/observability/tracing/span.py

Description:
    Core implementation of the SciOS runtime tracing span.
"""

from __future__ import annotations


# ==============================================================================
# Imports
# ==============================================================================

import copy
import json
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
    Mapping,
    Optional,
    Sequence,
    TypeAlias,
)

# ==============================================================================
# Part 1.1 – Constants
# ==============================================================================

# ------------------------------------------------------------------------------
# Module Metadata
# ------------------------------------------------------------------------------

MODULE_NAME: str = "TraceSpan"

MODULE_DESCRIPTION: str = (
    "SciOS Runtime Trace Span"
)

MODULE_VERSION: str = "0.1.0"


# ------------------------------------------------------------------------------
# Default Configuration
# ------------------------------------------------------------------------------

DEFAULT_SPAN_NAME: str = "span"

DEFAULT_SPAN_KIND: str = "internal"

DEFAULT_SPAN_STATUS: str = "unset"

DEFAULT_ENABLED: bool = True

DEFAULT_AUTO_START: bool = False

DEFAULT_AUTO_FINISH: bool = False

DEFAULT_TIMEOUT: float = 30.0


# ------------------------------------------------------------------------------
# Runtime Limits
# ------------------------------------------------------------------------------

DEFAULT_ATTRIBUTES_LIMIT: int = 128

DEFAULT_EVENTS_LIMIT: int = 512

DEFAULT_LINKS_LIMIT: int = 64

DEFAULT_TAGS_LIMIT: int = 64

DEFAULT_HISTORY_LIMIT: int = 1024

DEFAULT_CACHE_SIZE: int = 256


# ------------------------------------------------------------------------------
# Serialization
# ------------------------------------------------------------------------------

DEFAULT_ENCODING: str = "utf-8"

DEFAULT_INDENT: int = 2

# Alias for compatibility with older code
DEFAULT_JSON_INDENT: int = DEFAULT_INDENT

DEFAULT_JSON_SORT_KEYS: bool = True

DEFAULT_JSON_ENSURE_ASCII: bool = False

DEFAULT_JSON_ALLOW_NAN: bool = False


# ------------------------------------------------------------------------------
# UUID / Identifier
# ------------------------------------------------------------------------------

UUID_HEX_LENGTH: int = 32

TRACE_ID_LENGTH: int = UUID_HEX_LENGTH

SPAN_ID_LENGTH: int = UUID_HEX_LENGTH


# ------------------------------------------------------------------------------
# Logger
# ------------------------------------------------------------------------------

LOGGER_NAME: str = (
    "scios.runtime.observability.tracing.span"
)

# ==============================================================================
# Part 1.2 – Type Aliases
# ==============================================================================

# ------------------------------------------------------------------------------
# Identity
# ------------------------------------------------------------------------------

TraceId: TypeAlias = str

SpanId: TypeAlias = str

ParentSpanId: TypeAlias = str


# ------------------------------------------------------------------------------
# Attributes
# ------------------------------------------------------------------------------

AttributeKey: TypeAlias = str

AttributeValue: TypeAlias = Any

Attributes: TypeAlias = dict[
    AttributeKey,
    AttributeValue,
]


# ------------------------------------------------------------------------------
# Events
# ------------------------------------------------------------------------------

TraceEvent: TypeAlias = dict[
    str,
    Any,
]

EventCollection: TypeAlias = list[
    TraceEvent,
]


# ------------------------------------------------------------------------------
# Links
# ------------------------------------------------------------------------------

TraceLink: TypeAlias = dict[
    str,
    Any,
]

LinkCollection: TypeAlias = list[
    TraceLink,
]


# ------------------------------------------------------------------------------
# Metadata
# ------------------------------------------------------------------------------

TraceMetadata: TypeAlias = dict[
    str,
    Any,
]


# ------------------------------------------------------------------------------
# Collections
# ------------------------------------------------------------------------------

SpanCollection: TypeAlias = dict[
    SpanId,
    "TraceSpan",
]

HistoryCollection: TypeAlias = Deque[
    dict[str, Any]
]

CacheMap: TypeAlias = dict[
    str,
    Any,
]


# ------------------------------------------------------------------------------
# Hooks / Callbacks
# ------------------------------------------------------------------------------

TraceHook: TypeAlias = Callable[
    ...,
    None,
]

TraceCallback: TypeAlias = Callable[
    ...,
    None,
]


# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------

SpanConfiguration: TypeAlias = dict[
    str,
    Any,
]

SpanOptions: TypeAlias = dict[
    str,
    Any,
]


# ------------------------------------------------------------------------------
# Serialization
# ------------------------------------------------------------------------------

SerializedSpan: TypeAlias = dict[
    str,
    Any,
]

SerializedSnapshot: TypeAlias = dict[
    str,
    Any,
]


# ------------------------------------------------------------------------------
# Generic Types
# ------------------------------------------------------------------------------

JSONValue: TypeAlias = (
    str
    | int
    | float
    | bool
    | None
    | dict[str, Any]
    | list[Any]
)

RuntimeObject: TypeAlias = Any
# ==============================================================================
# Part 1.3 – Exceptions
# ==============================================================================


class TraceSpanError(Exception):
    """
    Base exception for TraceSpan.
    """

    def __init__(
        self,
        message: str = "",
        *,
        code: str = "SPAN_ERROR",
        details: Optional[
            Mapping[str, Any]
        ] = None,
    ) -> None:

        self.message = message

        self.code = code

        self.details = dict(
            details or {}
        )

        super().__init__(
            message
        )


    def to_dict(
        self,
    ) -> dict[str, Any]:

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
            f"code={self.code!r}"
            f")"
        )



class SpanValidationError(
    TraceSpanError,
):
    """
    Invalid span data.
    """

    def __init__(
        self,
        message: str,
        *,
        field: str | None = None,
        value: Any = None,
    ) -> None:

        details: dict[str, Any] = {}

        if field is not None:
            details["field"] = field

        if value is not None:
            details["value"] = value

        super().__init__(
            message,
            code="SPAN_VALIDATION_ERROR",
            details=details,
        )



class SpanStateError(
    TraceSpanError,
):
    """
    Invalid lifecycle transition.
    """

    def __init__(
        self,
        message: str,
        *,
        current_state: str | None = None,
        expected_state: str | None = None,
    ) -> None:

        super().__init__(
            message,
            code="SPAN_STATE_ERROR",
            details={
                "current_state": current_state,
                "expected_state": expected_state,
            },
        )



class SpanClosedError(
    SpanStateError,
):
    """
    Span already closed.
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



class SpanFinishedError(
    SpanStateError,
):
    """
    Span already finished.
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



class InvalidTraceError(
    TraceSpanError,
):
    """
    Invalid trace identity.
    """

    def __init__(
        self,
        message: str,
        *,
        trace_id: TraceId | None = None,
        span_id: SpanId | None = None,
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
# Part 1.4 – Enums
# ==============================================================================


class SpanKind(
    Enum,
):
    """
    Semantic role of a span.
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



class SpanState(
    Enum,
):
    """
    Runtime lifecycle state.
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



class SpanStatus(
    Enum,
):
    """
    Execution status.
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



class SpanCapability(
    IntFlag,
):
    """
    Supported runtime capabilities.
    """

    NONE = 0

    ATTRIBUTES = auto()

    EVENTS = auto()

    LINKS = auto()

    CHILDREN = auto()

    STATUS = auto()

    EXCEPTIONS = auto()

    SERIALIZATION = auto()

    SNAPSHOT = auto()

    VALIDATION = auto()

    CALLBACKS = auto()

    HOOKS = auto()

    CACHE = auto()

    HISTORY = auto()


    ALL = (
        ATTRIBUTES
        | EVENTS
        | LINKS
        | CHILDREN
        | STATUS
        | EXCEPTIONS
        | SERIALIZATION
        | SNAPSHOT
        | VALIDATION
        | CALLBACKS
        | HOOKS
        | CACHE
        | HISTORY
    )

# ==============================================================================
# Part 1.5 – Dataclasses
# ==============================================================================

# ------------------------------------------------------------------------------
# SpanStatistics
# ------------------------------------------------------------------------------

@dataclass(slots=True)
class SpanStatistics:
    """
    Runtime statistics for TraceSpan.
    """

    # ------------------------------------------------------------------
    # Counters
    # ------------------------------------------------------------------

    event_count: int = 0
    attribute_count: int = 0
    link_count: int = 0
    child_count: int = 0

    error_count: int = 0

    update_count: int = 0
    validation_count: int = 0
    callback_count: int = 0
    hook_count: int = 0
    export_count: int = 0

    # ------------------------------------------------------------------
    # Timing
    # ------------------------------------------------------------------

    start_time: float = 0.0
    end_time: float = 0.0
    duration: float = 0.0

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    created_at: float = field(
        default_factory=time.time,
    )

    updated_at: float = field(
        default_factory=time.time,
    )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def reset(self) -> None:
        """
        Reset runtime statistics.
        """

        self.event_count = 0
        self.attribute_count = 0
        self.link_count = 0
        self.child_count = 0

        self.error_count = 0

        self.update_count = 0
        self.validation_count = 0
        self.callback_count = 0
        self.hook_count = 0
        self.export_count = 0

        self.start_time = 0.0
        self.end_time = 0.0
        self.duration = 0.0

        self.updated_at = time.time()

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize statistics.
        """

        return asdict(self)

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "SpanStatistics":
        """
        Restore statistics from dictionary.
        """

        return cls(**dict(data))


# ------------------------------------------------------------------------------
# SpanSnapshot
# ------------------------------------------------------------------------------

@dataclass(slots=True, frozen=True)
class SpanSnapshot:
    """
    Immutable runtime snapshot of TraceSpan.
    """

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    trace_id: TraceId
    span_id: SpanId
    parent_span_id: ParentSpanId | None

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    name: str
    kind: str
    status: str
    state: str

    # ------------------------------------------------------------------
    # Timing
    # ------------------------------------------------------------------

    start_time: float
    end_time: float | None
    duration: float

    # ------------------------------------------------------------------
    # Runtime Data
    # ------------------------------------------------------------------

    attributes: dict[str, Any]
    events: list[TraceEvent]
    links: list[TraceLink]
    metadata: dict[str, Any]

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    statistics: dict[str, Any]

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    created_at: float = field(
        default_factory=time.time,
    )

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------

    def __post_init__(self) -> None:
        """
        Normalize mutable containers.
        """

        object.__setattr__(
            self,
            "attributes",
            dict(self.attributes),
        )

        object.__setattr__(
            self,
            "events",
            list(self.events),
        )

        object.__setattr__(
            self,
            "links",
            list(self.links),
        )

        object.__setattr__(
            self,
            "metadata",
            dict(self.metadata),
        )

        object.__setattr__(
            self,
            "statistics",
            dict(self.statistics),
        )

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize snapshot.
        """

        return asdict(self)

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "SpanSnapshot":
        """
        Restore snapshot.
        """

        return cls(**dict(data))

    def to_json(
        self,
        *,
        indent: int = DEFAULT_INDENT,
    ) -> str:
        """
        Serialize snapshot to JSON.
        """

        return json.dumps(
            self.to_dict(),
            indent=indent,
            sort_keys=DEFAULT_JSON_SORT_KEYS,
            ensure_ascii=DEFAULT_JSON_ENSURE_ASCII,
            default=str,
        )


# ------------------------------------------------------------------------------
# SpanReport
# ------------------------------------------------------------------------------

@dataclass(slots=True)
class SpanReport:

    pass

    
    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize report.
        """

        return asdict(self)

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "SpanReport":
        """
        Restore report.
        """

        return cls(**dict(data))

    def to_json(
        self,
        *,
        indent: int = DEFAULT_INDENT,
    ) -> str:
        """
        Serialize report to JSON.
        """

        return json.dumps(
            self.to_dict(),
            indent=indent,
            sort_keys=DEFAULT_JSON_SORT_KEYS,
            ensure_ascii=DEFAULT_JSON_ENSURE_ASCII,
            default=str,
        )


# ==============================================================================
# Part 2. Constructor
# ==============================================================================


class TraceSpan:
    """
    Core runtime tracing span.
    """


    def __init__(
        self,
        name: str = DEFAULT_SPAN_NAME,
        *,
        trace_id: TraceId | None = None,
        span_id: SpanId | None = None,
        parent_span_id: ParentSpanId | None = None,
        kind: SpanKind = SpanKind.INTERNAL,

        attributes: Attributes | None = None,
        metadata: TraceMetadata | None = None,
        context: TraceMetadata | None = None,
        tags: dict[str, Any] | None = None,

        auto_start: bool = False,
        enabled: bool = True,

    ) -> None:
        """
        Initialize TraceSpan.
        """


        if not name or not name.strip():

            raise SpanValidationError(
                "Span name cannot be empty."
            )


        now = time.time()


        # ------------------------------------------------------------------
        # Identity
        # ------------------------------------------------------------------

        self._trace_id = (
            trace_id
            if trace_id is not None
            else uuid.uuid4().hex
        )


        self._span_id = (
            span_id
            if span_id is not None
            else uuid.uuid4().hex
        )


        self._parent_span_id = parent_span_id


        self._name = name.strip()


        self._kind = kind



        # ------------------------------------------------------------------
        # Runtime Flags
        # ------------------------------------------------------------------

        self._enabled = enabled

        self._initialized = True

        self._started = False

        self._finished = False



        # ------------------------------------------------------------------
        # Lifecycle
        # ------------------------------------------------------------------

        self._state = SpanState.INITIALIZED


        self._status = SpanStatus.UNSET


        self._closed = False



        # ------------------------------------------------------------------
        # Timing
        # ------------------------------------------------------------------

        self._created_at = now

        self._updated_at = now


        self._start_time = 0.0

        self._end_time = 0.0


        self._duration = 0.0



        # ------------------------------------------------------------------
        # Context
        # ------------------------------------------------------------------

        self._context = dict(
            context or {}
        )


        self._attributes = dict(
            attributes or {}
        )


        self._metadata = dict(
            metadata or {}
        )


        self._tags = dict(
            tags or {}
        )


        self._events = []

        self._links = []



        # ------------------------------------------------------------------
        # Hierarchy
        # ------------------------------------------------------------------

        self._children = {}



        # ------------------------------------------------------------------
        # Runtime
        # ------------------------------------------------------------------

        self._statistics = SpanStatistics()



        self._lock = RLock()



        self._history = deque(
            maxlen=DEFAULT_HISTORY_LIMIT,
        )


        self._cache = {}


        self._capabilities = (
            SpanCapability.ALL
        )



        # ------------------------------------------------------------------
        # Auto lifecycle
        # ------------------------------------------------------------------

        if auto_start:

            self.start()   

# ==============================================================================
# Part 3. Properties
# ==============================================================================


    # --------------------------------------------------------------------------
    # Identity
    # --------------------------------------------------------------------------

    @property
    def trace_id(
        self,
    ) -> TraceId:
        return self._trace_id


    @property
    def span_id(
        self,
    ) -> SpanId:
        return self._span_id


    @property
    def parent_span_id(
        self,
    ) -> ParentSpanId | None:
        return self._parent_span_id


    @property
    def parent(
        self,
    ) -> "TraceSpan | None":
        return getattr(
            self,
            "_parent",
            None,
        )


    @property
    def name(
        self,
    ) -> str:
        return self._name


    @name.setter
    def name(
        self,
        value: str,
    ) -> None:

        if not isinstance(
            value,
            str,
        ):
            raise SpanValidationError(
                "Span name must be string."
            )

        value = value.strip()

        if not value:
            raise SpanValidationError(
                "Span name cannot be empty."
            )

        self._name = value
        self._updated_at = time.time()



    @property
    def kind(
        self,
    ) -> SpanKind:
        return self._kind


    @kind.setter
    def kind(
        self,
        value: SpanKind,
    ) -> None:

        if not isinstance(
            value,
            SpanKind,
        ):
            raise SpanValidationError(
                "Invalid span kind."
            )

        self._kind = value
        self._updated_at = time.time()



    # --------------------------------------------------------------------------
    # Lifecycle State
    # --------------------------------------------------------------------------

    @property
    def state(
        self,
    ) -> SpanState:
        return self._state


    @property
    def status(
        self,
    ) -> SpanStatus:
        return self._status


    @status.setter
    def status(
        self,
        value: SpanStatus,
    ) -> None:

        if not isinstance(
            value,
            SpanStatus,
        ):
            raise SpanValidationError(
                "Invalid span status."
            )

        self._status = value
        self._updated_at = time.time()



    @property
    def enabled(
        self,
    ) -> bool:
        return self._enabled


    @enabled.setter
    def enabled(
        self,
        value: bool,
    ) -> None:

        self._enabled = bool(value)
        self._updated_at = time.time()



    @property
    def started(
        self,
    ) -> bool:
        return self._started


    @property
    def finished(
        self,
    ) -> bool:
        return self._finished


    @property
    def cancelled(
        self,
    ) -> bool:

        return getattr(
            self,
            "_cancelled",
            False,
        )


    @property
    def closed(
        self,
    ) -> bool:

        return self._closed



    # --------------------------------------------------------------------------
    # Timing
    # --------------------------------------------------------------------------

    @property
    def created_at(
        self,
    ) -> float:
        return self._created_at


    @property
    def updated_at(
        self,
    ) -> float:
        return self._updated_at


    @property
    def start_time(
        self,
    ) -> float:
        return self._start_time


    @property
    def end_time(
        self,
    ) -> float:
        return self._end_time


    @property
    def started_at(
        self,
    ) -> float | None:

        return (
            self._start_time
            if self._started
            else None
        )


    @property
    def finished_at(
        self,
    ) -> float | None:

        return (
            self._end_time
            if self._finished
            else None
        )


    @property
    def duration(
        self,
    ) -> float:

        if (
            self._started
            and not self._finished
            and self._start_time > 0.0
        ):

            return max(
                0.0,
                time.time()
                -
                self._start_time,
            )

        return self._duration



    # --------------------------------------------------------------------------
    # Context
    # --------------------------------------------------------------------------

    @property
    def context(
        self,
    ) -> TraceMetadata:

        return dict(
            self._context
        )


    @context.setter
    def context(
        self,
        value: TraceMetadata,
    ) -> None:

        self._context = dict(
            value
        )

        self._updated_at = time.time()



    @property
    def metadata(
        self,
    ) -> TraceMetadata:

        return dict(
            self._metadata
        )



    @property
    def tags(
        self,
    ) -> list[str]:

        return list(
            self._tags.keys()
        )



    @property
    def statistics(
        self,
    ) -> SpanStatistics:

        return self._statistics



    @property
    def capabilities(
        self,
    ) -> SpanCapability:

        return self._capabilities



    # --------------------------------------------------------------------------
    # Attributes
    # --------------------------------------------------------------------------

    @property
    def attributes(
        self,
    ) -> Attributes:

        return dict(
            self._attributes
        )


    @property
    def attribute_count(
        self,
    ) -> int:

        return len(
            self._attributes
        )



    # --------------------------------------------------------------------------
    # Events
    # --------------------------------------------------------------------------

    @property
    def events(
        self,
    ) -> EventCollection:

        return list(
            self._events
        )


    @property
    def event_count(
        self,
    ) -> int:

        return len(
            self._events
        )



    # --------------------------------------------------------------------------
    # Links
    # --------------------------------------------------------------------------

    @property
    def links(
        self,
    ) -> LinkCollection:

        return list(
            self._links
        )


    @property
    def link_count(
        self,
    ) -> int:

        return len(
            self._links
        )



    # --------------------------------------------------------------------------
    # Children
    # --------------------------------------------------------------------------

    @property
    def children(
        self,
    ) -> SpanCollection:

        return dict(
            self._children
        )


    @property
    def child_count(
        self,
    ) -> int:

        return len(
            self._children
        )




# ==============================================================================
# Part 4. Lifecycle
# ==============================================================================


    def start(
        self,
    ) -> "TraceSpan":

        with self._lock:

            if self._closed:
                raise SpanClosedError()


            if not self._enabled:
                return self


            if self._started:
                return self


            now = time.time()


            self._started = True
            self._finished = False
            self._cancelled = False


            self._start_time = now
            self._end_time = 0.0


            self._started_at = now
            self._finished_at = None


            self._duration = 0.0


            self._state = SpanState.RUNNING

            self._status = SpanStatus.UNSET


            self._statistics.start_time = now


            self._updated_at = now


            return self





    def end(
        self,
        status: SpanStatus = SpanStatus.OK,
    ) -> "TraceSpan":

        return self.finish(
            status=status,
        )





    def finish(
        self,
        status: SpanStatus = SpanStatus.OK,
    ) -> "TraceSpan":


        if not isinstance(
            status,
            SpanStatus,
        ):

            raise SpanValidationError(
                "Invalid span status."
            )


        with self._lock:


            if self._closed:
                raise SpanClosedError()


            if self._finished:
                return self


            now = time.time()


            self._finished = True

            self._finished_at = now


            if self._start_time > 0.0:

                self._duration = (
                    now
                    -
                    self._start_time
                )


            self._end_time = now


            self._state = SpanState.FINISHED


            self._status = status


            self._statistics.end_time = now

            self._statistics.duration = (
                self._duration
            )


            if status == SpanStatus.ERROR:

                self._statistics.error_count += 1


            self._updated_at = now


            return self





    def cancel(
        self,
    ) -> "TraceSpan":


        with self._lock:


            if self._closed:
                raise SpanClosedError()


            now = time.time()


            self._cancelled = True

            self._finished = True


            self._finished_at = now

            self._end_time = now


            if self._start_time > 0.0:

                self._duration = (
                    now
                    -
                    self._start_time
                )


            self._state = SpanState.ERROR

            self._status = SpanStatus.ERROR


            self._statistics.error_count += 1


            self._statistics.end_time = now

            self._statistics.duration = (
                self._duration
            )


            self._updated_at = now


            return self





    def reset(
        self,
    ) -> "TraceSpan":


        with self._lock:


            if self._closed:
                raise SpanClosedError()


            self._started = False

            self._finished = False

            self._cancelled = False


            self._started_at = None

            self._finished_at = None


            self._start_time = 0.0

            self._end_time = 0.0

            self._duration = 0.0


            self._state = SpanState.INITIALIZED

            self._status = SpanStatus.UNSET



            self._events.clear()

            self._links.clear()

            self._attributes.clear()

            self._metadata.clear()

            self._context.clear()

            self._tags.clear()

            self._children.clear()



            if hasattr(
                self,
                "_cache",
            ):
                self._cache.clear()



            if hasattr(
                self,
                "_history",
            ):
                self._history.clear()



            self._statistics.reset()


            self._updated_at = time.time()


            return self





    def close(
        self,
    ) -> "TraceSpan":


        with self._lock:


            if self._closed:
                return self


            self._closed = True


            self._state = SpanState.CLOSED


            self._updated_at = time.time()


            return self





    def disable(
        self,
    ) -> "TraceSpan":

        self.enabled = False

        return self





    def enable(
        self,
    ) -> "TraceSpan":

        self.enabled = True

        return self





    def freeze(
        self,
    ) -> "TraceSpan":

        self._frozen = True

        return self





    def unfreeze(
        self,
    ) -> "TraceSpan":

        self._frozen = False

        return self

# ==============================================================================
# Part 5. Attributes
# ==============================================================================

# ------------------------------------------------------------------------------
# copy_attributes()
# ------------------------------------------------------------------------------

    def copy_attributes(
        self,
    ) -> dict[str, Any]:
        """
        Return a deep copy of all attributes.
        """

        with self._lock:

            return copy.deepcopy(
                self._attributes
            )


    # ------------------------------------------------------------------------------
    # set_attribute()
    # ------------------------------------------------------------------------------

    def set_attribute(
        self,
        key: AttributeKey,
        value: AttributeValue,
    ) -> "TraceSpan":
        """
        Set or replace one attribute.
        """

        with self._lock:

            if self._closed:
                raise SpanClosedError()

            if not isinstance(
                key,
                str,
            ):
                raise SpanValidationError(
                    "Attribute key must be string."
                )

            key = key.strip()

            if not key:
                raise SpanValidationError(
                    "Attribute key cannot be empty."
                )

            if (
                key not in self._attributes
                and
                len(self._attributes)
                >= DEFAULT_ATTRIBUTES_LIMIT
            ):
                raise SpanValidationError(
                    "Maximum attribute limit exceeded."
                )

            self._attributes[key] = value

            self._statistics.attribute_count = (
                len(self._attributes)
            )

            self._statistics.update_count += 1

            self._updated_at = time.time()

            return self


    # ------------------------------------------------------------------------------
    # set_attributes()
    # ------------------------------------------------------------------------------

    def set_attributes(
        self,
        attributes: Mapping[str, Any],
    ) -> "TraceSpan":
        """
        Set multiple attributes.
        """

        if not isinstance(
            attributes,
            Mapping,
        ):
            raise SpanValidationError(
                "Attributes must be mapping."
            )

        with self._lock:

            if self._closed:
                raise SpanClosedError()

            for key, value in attributes.items():

                if not isinstance(
                    key,
                    str,
                ):
                    raise SpanValidationError(
                        "Attribute key must be string."
                    )

                key = key.strip()

                if not key:
                    raise SpanValidationError(
                        "Attribute key cannot be empty."
                    )

                if (
                    key not in self._attributes
                    and
                    len(self._attributes)
                    >= DEFAULT_ATTRIBUTES_LIMIT
                ):
                    raise SpanValidationError(
                        "Maximum attribute limit exceeded."
                    )

                self._attributes[key] = value

            self._statistics.attribute_count = (
                len(self._attributes)
            )

            self._statistics.update_count += 1

            self._updated_at = time.time()

            return self


    # ------------------------------------------------------------------------------
    # update_attributes()
    # ------------------------------------------------------------------------------

    def update_attributes(
        self,
        attributes: Mapping[str, Any],
    ) -> "TraceSpan":
        """
        Alias of set_attributes().
        """

        return self.set_attributes(
            attributes
        )


    # ------------------------------------------------------------------------------
    # remove_attribute()
    # ------------------------------------------------------------------------------

    def remove_attribute(
        self,
        key: AttributeKey,
    ) -> bool:
        """
        Remove one attribute.
        """

        with self._lock:

            if self._closed:
                raise SpanClosedError()

            if not isinstance(
                key,
                str,
            ):
                raise SpanValidationError(
                    "Attribute key must be string."
                )

            key = key.strip()

            if key not in self._attributes:
                return False

            del self._attributes[key]

            self._statistics.attribute_count = (
                len(self._attributes)
            )

            self._statistics.update_count += 1

            self._updated_at = time.time()

            return True


    # ------------------------------------------------------------------------------
    # clear_attributes()
    # ------------------------------------------------------------------------------

    def clear_attributes(
        self,
    ) -> "TraceSpan":
        """
        Remove all attributes.
        """

        with self._lock:

            if self._closed:
                raise SpanClosedError()

            if not self._attributes:
                return self

            self._attributes.clear()

            self._statistics.attribute_count = 0

            self._statistics.update_count += 1

            self._updated_at = time.time()

            return self


    # ------------------------------------------------------------------------------
    # get_attribute()
    # ------------------------------------------------------------------------------

    def get_attribute(
        self,
        key: AttributeKey,
        default: Any = None,
    ) -> Any:
        """
        Get one attribute.
        """

        with self._lock:

            return self._attributes.get(
                key,
                default,
            )


    # ------------------------------------------------------------------------------
    # has_attribute()
    # ------------------------------------------------------------------------------

    def has_attribute(
        self,
        key: AttributeKey,
    ) -> bool:
        """
        Return True if attribute exists.
        """

        with self._lock:

            return key in self._attributes


    # ------------------------------------------------------------------------------
    # attribute_keys()
    # ------------------------------------------------------------------------------

    def attribute_keys(
        self,
    ) -> list[str]:
        """
        Return attribute keys.
        """

        with self._lock:

            return list(
                self._attributes.keys()
            )


    # ------------------------------------------------------------------------------
    # attribute_values()
    # ------------------------------------------------------------------------------

    def attribute_values(
        self,
    ) -> list[Any]:
        """
        Return attribute values.
        """

        with self._lock:

            return list(
                self._attributes.values()
            )


    # ------------------------------------------------------------------------------
    # attribute_items()
    # ------------------------------------------------------------------------------

    def attribute_items(
        self,
    ) -> list[tuple[str, Any]]:
        """
        Return attribute items.
        """

        with self._lock:

            return list(
                self._attributes.items()
            )

# ==============================================================================
# Part 6. Events
# ==============================================================================

# ------------------------------------------------------------------------------
# add_event()
# ------------------------------------------------------------------------------

    def add_event(
        self,
        name: str,
        attributes: Mapping[str, Any] | None = None,
    ) -> "TraceSpan":
        """
        Record a runtime event.
        """

        with self._lock:

            if self._closed:
                raise SpanClosedError()

            if not isinstance(
                name,
                str,
            ):
                raise SpanValidationError(
                    "Event name must be string."
                )

            name = name.strip()

            if not name:
                raise SpanValidationError(
                    "Event name cannot be empty."
                )

            if (
                len(self._events)
                >= DEFAULT_EVENTS_LIMIT
            ):
                raise SpanValidationError(
                    "Maximum event limit exceeded."
                )

            if (
                attributes is not None
                and
                not isinstance(
                    attributes,
                    Mapping,
                )
            ):
                raise SpanValidationError(
                    "Event attributes must be mapping."
                )

            now = time.time()

            event: TraceEvent = {

                "id":
                    uuid.uuid4().hex,

                "name":
                    name,

                "timestamp":
                    now,

                "attributes":
                    copy.deepcopy(
                        dict(
                            attributes or {}
                        )
                    ),
            }

            self._events.append(
                event
            )

            self._statistics.event_count = (
                len(self._events)
            )

            self._statistics.update_count += 1

            self._updated_at = now

            return self


    # ------------------------------------------------------------------------------
    # get_event()
    # ------------------------------------------------------------------------------

    def get_event(
        self,
        event_id: str,
    ) -> TraceEvent | None:
        """
        Return event by id.
        """

        with self._lock:

            for event in self._events:

                if (
                    event.get("id")
                    ==
                    event_id
                ):
                    return copy.deepcopy(
                        event
                    )

            return None


    # ------------------------------------------------------------------------------
    # get_events()
    # ------------------------------------------------------------------------------

    def get_events(
        self,
    ) -> list[TraceEvent]:
        """
        Return all events.
        """

        with self._lock:

            return copy.deepcopy(
                self._events
            )


    # ------------------------------------------------------------------------------
    # event_count
    # ------------------------------------------------------------------------------

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


    # ------------------------------------------------------------------------------
    # has_event()
    # ------------------------------------------------------------------------------

    def has_event(
        self,
        event_id: str,
    ) -> bool:
        """
        Check event existence.
        """

        return (
            self.get_event(
                event_id
            )
            is not None
        )


    # ------------------------------------------------------------------------------
    # remove_event()
    # ------------------------------------------------------------------------------

    def remove_event(
        self,
        event_id: str,
    ) -> bool:
        """
        Remove event by id.
        """

        with self._lock:

            if self._closed:
                raise SpanClosedError()

            for index, event in enumerate(
                self._events
            ):

                if (
                    event.get("id")
                    ==
                    event_id
                ):

                    del self._events[
                        index
                    ]

                    self._statistics.event_count = (
                        len(
                            self._events
                        )
                    )

                    self._statistics.update_count += 1

                    self._updated_at = (
                        time.time()
                    )

                    return True

            return False


    # ------------------------------------------------------------------------------
    # clear_events()
    # ------------------------------------------------------------------------------

    def clear_events(
        self,
    ) -> "TraceSpan":
        """
        Remove all events.
        """

        with self._lock:

            if self._closed:
                raise SpanClosedError()

            if not self._events:
                return self

            self._events.clear()

            self._statistics.event_count = 0

            self._statistics.update_count += 1

            self._updated_at = time.time()

            return self


    # ------------------------------------------------------------------------------
    # record_exception()
    # ------------------------------------------------------------------------------

    def record_exception(
        self,
        exc: BaseException,
        **attributes: Any,
    ) -> "TraceSpan":
        """
        Record exception as an event.
        """

        if not isinstance(
            exc,
            BaseException,
        ):
            raise SpanValidationError(
                "exc must be BaseException."
            )

        payload = {

            "type":
                exc.__class__.__name__,

            "message":
                str(exc),
        }

        payload.update(
            attributes
        )

        self.add_event(
            "exception",
            payload,
        )

        self._status = (
            SpanStatus.ERROR
        )

        self._statistics.error_count += 1

        return self

# ==============================================================================
# Part 7. Links
# ==============================================================================

# ------------------------------------------------------------------------------
# add_link()
# ------------------------------------------------------------------------------

    def add_link(
        self,
        trace_id: TraceId,
        span_id: SpanId,
        attributes: Mapping[str, Any] | None = None,
        **metadata: Any,
    ) -> "TraceSpan":
        """
        Add a link to another span.
        """

        with self._lock:

            if self._closed:
                raise SpanClosedError()

            if (
                not isinstance(trace_id, str)
                or
                not trace_id.strip()
            ):
                raise SpanValidationError(
                    "trace_id cannot be empty."
                )

            if (
                not isinstance(span_id, str)
                or
                not span_id.strip()
            ):
                raise SpanValidationError(
                    "span_id cannot be empty."
                )

            trace_id = trace_id.strip()
            span_id = span_id.strip()

            payload: dict[str, Any] = {}

            if attributes is not None:

                if not isinstance(
                    attributes,
                    Mapping,
                ):
                    raise SpanValidationError(
                        "Link attributes must be mapping."
                    )

                payload.update(attributes)

            payload.update(metadata)

            if (
                len(self._links)
                >=
                DEFAULT_LINKS_LIMIT
            ):
                raise SpanValidationError(
                    "Maximum link limit exceeded."
                )

            for link in self._links:

                if (
                    link["trace_id"] == trace_id
                    and
                    link["span_id"] == span_id
                ):
                    link["attributes"].update(
                        copy.deepcopy(payload)
                    )

                    self._updated_at = time.time()

                    return self

            now = time.time()

            link: TraceLink = {

                "id":
                    uuid.uuid4().hex,

                "trace_id":
                    trace_id,

                "span_id":
                    span_id,

                "attributes":
                    copy.deepcopy(payload),

                "timestamp":
                    now,
            }

            self._links.append(
                link
            )

            self._statistics.link_count = (
                len(self._links)
            )

            self._statistics.update_count += 1

            self._updated_at = now

            return self


    # ------------------------------------------------------------------------------
    # get_link()
    # ------------------------------------------------------------------------------

    def get_link(
        self,
        trace_id: TraceId,
        span_id: SpanId,
    ) -> TraceLink | None:
        """
        Return one link.
        """

        with self._lock:

            for link in self._links:

                if (
                    link["trace_id"] == trace_id
                    and
                    link["span_id"] == span_id
                ):
                    return copy.deepcopy(
                        link
                    )

            return None


    # ------------------------------------------------------------------------------
    # get_links()
    # ------------------------------------------------------------------------------

    def get_links(
        self,
    ) -> list[TraceLink]:
        """
        Return all links.
        """

        with self._lock:

            return copy.deepcopy(
                self._links
            )


    # ------------------------------------------------------------------------------
    # has_link()
    # ------------------------------------------------------------------------------

    def has_link(
        self,
        trace_id: TraceId,
        span_id: SpanId,
    ) -> bool:
        """
        Check whether link exists.
        """

        return (
            self.get_link(
                trace_id,
                span_id,
            )
            is not None
        )


    # ------------------------------------------------------------------------------
    # remove_link()
    # ------------------------------------------------------------------------------

    def remove_link(
        self,
        trace_id: TraceId,
        span_id: SpanId | None = None,
    ) -> bool:
        """
        Remove a link.

        Supports:
            remove_link(link_id)
            remove_link(trace_id, span_id)
        """

        with self._lock:

            if self._closed:
                raise SpanClosedError()

            for index, link in enumerate(
                self._links
            ):

                matched = False

                if span_id is None:

                    matched = (
                        link["id"]
                        ==
                        trace_id
                    )

                else:

                    matched = (

                        link["trace_id"]
                        ==
                        trace_id

                        and

                        link["span_id"]
                        ==
                        span_id

                    )

                if matched:

                    del self._links[index]

                    self._statistics.link_count = (
                        len(self._links)
                    )

                    self._statistics.update_count += 1

                    self._updated_at = (
                        time.time()
                    )

                    return True

            return False


    # ------------------------------------------------------------------------------
    # clear_links()
    # ------------------------------------------------------------------------------

    def clear_links(
        self,
    ) -> "TraceSpan":
        """
        Remove all links.
        """

        with self._lock:

            if self._closed:
                raise SpanClosedError()

            if not self._links:
                return self

            self._links.clear()

            self._statistics.link_count = 0

            self._statistics.update_count += 1

            self._updated_at = time.time()

            return self


    # ------------------------------------------------------------------------------
    # link_count
    # ------------------------------------------------------------------------------

    @property
    def link_count(
        self,
    ) -> int:
        """
        Number of links.
        """

        return len(
            self._links
        )

# ==============================================================================
# Part 8. Serialization
# ==============================================================================

# ------------------------------------------------------------------------------
# to_dict()
# ------------------------------------------------------------------------------

    def to_dict(
        self,
    ) -> SerializedSpan:
        """
        Serialize span into dictionary.
        """

        with self._lock:

            return {

                # ------------------------------------------------------------------
                # Identity
                # ------------------------------------------------------------------

                "trace_id":
                    self._trace_id,

                "span_id":
                    self._span_id,

                "parent_span_id":
                    self._parent_span_id,

                # ------------------------------------------------------------------
                # Metadata
                # ------------------------------------------------------------------

                "name":
                    self._name,

                "kind":
                    self._kind.value,

                # ------------------------------------------------------------------
                # Lifecycle
                # ------------------------------------------------------------------

                "state":
                    self._state.value,

                "status":
                    self._status.value,

                "enabled":
                    self._enabled,

                "started":
                    self._started,

                "finished":
                    self._finished,

                "cancelled":
                    getattr(
                        self,
                        "_cancelled",
                        False,
                    ),

                "closed":
                    getattr(
                        self,
                        "_closed",
                        False,
                    ),

                # ------------------------------------------------------------------
                # Timing
                # ------------------------------------------------------------------

                "created_at":
                    self._created_at,

                "updated_at":
                    self._updated_at,

                "started_at":
                    self._started_at,

                "finished_at":
                    self._finished_at,

                "start_time":
                    self._start_time,

                "end_time":
                    self._end_time,

                "duration":
                    self.duration,

                # ------------------------------------------------------------------
                # Runtime
                # ------------------------------------------------------------------

                "context":
                    copy.deepcopy(
                        self._context
                    ),

                "metadata":
                    copy.deepcopy(
                        self._metadata
                    ),

                "tags":
                    copy.deepcopy(
                        self._tags
                    ),

                "attributes":
                    copy.deepcopy(
                        self._attributes
                    ),

                "events":
                    copy.deepcopy(
                        self._events
                    ),

                "links":
                    copy.deepcopy(
                        self._links
                    ),

                # ------------------------------------------------------------------
                # Statistics
                # ------------------------------------------------------------------

                "statistics":
                    self._statistics.to_dict(),
            }


    # ------------------------------------------------------------------------------
    # from_dict()
    # ------------------------------------------------------------------------------

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "TraceSpan":
        """
        Restore span from dictionary.
        """

        if not isinstance(
            data,
            Mapping,
        ):
            raise SpanValidationError(
                "Serialized span must be mapping."
            )

        span = cls(

            name=data.get(
                "name",
                DEFAULT_SPAN_NAME,
            ),

            trace_id=data.get(
                "trace_id",
            ),

            span_id=data.get(
                "span_id",
            ),

            parent_span_id=data.get(
                "parent_span_id",
            ),

            kind=SpanKind(
                data.get(
                    "kind",
                    SpanKind.INTERNAL.value,
                )
            ),

            attributes=copy.deepcopy(
                data.get(
                    "attributes",
                    {},
                )
            ),

            metadata=copy.deepcopy(
                data.get(
                    "metadata",
                    {},
                )
            ),

            tags=copy.deepcopy(
                data.get(
                    "tags",
                    {},
                )
            ),

            enabled=bool(
                data.get(
                    "enabled",
                    True,
                )
            ),
        )

        # ------------------------------------------------------------------
        # Lifecycle
        # ------------------------------------------------------------------

        span._state = SpanState(
            data.get(
                "state",
                SpanState.INITIALIZED.value,
            )
        )

        span._status = SpanStatus(
            data.get(
                "status",
                SpanStatus.UNSET.value,
            )
        )

        span._started = bool(
            data.get(
                "started",
                False,
            )
        )

        span._finished = bool(
            data.get(
                "finished",
                False,
            )
        )

        span._cancelled = bool(
            data.get(
                "cancelled",
                False,
            )
        )

        span._closed = bool(
            data.get(
                "closed",
                False,
            )
        )

        # ------------------------------------------------------------------
        # Timing
        # ------------------------------------------------------------------

        span._created_at = float(
            data.get(
                "created_at",
                span._created_at,
            )
        )

        span._updated_at = float(
            data.get(
                "updated_at",
                span._updated_at,
            )
        )

        span._started_at = data.get(
            "started_at",
        )

        span._finished_at = data.get(
            "finished_at",
        )

        span._start_time = float(
            data.get(
                "start_time",
                0.0,
            )
        )

        span._end_time = float(
            data.get(
                "end_time",
                0.0,
            )
        )

        span._duration = float(
            data.get(
                "duration",
                0.0,
            )
        )

        # ------------------------------------------------------------------
        # Collections
        # ------------------------------------------------------------------

        span._context = copy.deepcopy(
            data.get(
                "context",
                {},
            )
        )

        span._events = copy.deepcopy(
            data.get(
                "events",
                [],
            )
        )

        span._links = copy.deepcopy(
            data.get(
                "links",
                [],
            )
        )

        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------

        statistics = data.get(
            "statistics",
        )

        if (
            isinstance(
                statistics,
                Mapping,
            )
            and
            hasattr(
                SpanStatistics,
                "from_dict",
            )
        ):
            span._statistics = (
                SpanStatistics.from_dict(
                    statistics
                )
            )

        elif isinstance(
            statistics,
            Mapping,
        ):
            span._statistics = (
                SpanStatistics(
                    **statistics
                )
            )

        else:

            span._statistics.attribute_count = (
                len(
                    span._attributes
                )
            )

            span._statistics.event_count = (
                len(
                    span._events
                )
            )

            span._statistics.link_count = (
                len(
                    span._links
                )
            )

        return span


    # ------------------------------------------------------------------------------
    # to_json()
    # ------------------------------------------------------------------------------

    def to_json(
        self,
        *,
        indent: int = DEFAULT_INDENT,
    ) -> str:
        """
        Serialize span into JSON.
        """

        return json.dumps(

            self.to_dict(),

            indent=indent,

            sort_keys=DEFAULT_JSON_SORT_KEYS,

            ensure_ascii=DEFAULT_JSON_ENSURE_ASCII,

            default=str,

        )


    # ------------------------------------------------------------------------------
    # from_json()
    # ------------------------------------------------------------------------------

    @classmethod
    def from_json(
        cls,
        payload: str,
    ) -> "TraceSpan":
        """
        Restore span from JSON.
        """

        if not isinstance(
            payload,
            str,
        ):
            raise SpanValidationError(
                "JSON payload must be string."
            )

        return cls.from_dict(
            json.loads(
                payload
            )
        )


    # ------------------------------------------------------------------------------
    # snapshot()
    # ------------------------------------------------------------------------------

    def snapshot(
        self,
    ) -> SpanSnapshot:
        """
        Create snapshot.
        """

        with self._lock:

            return SpanSnapshot(

                trace_id=self._trace_id,

                span_id=self._span_id,

                parent_span_id=self._parent_span_id,

                name=self._name,

                kind=self._kind.value,

                state=self._state.value,

                status=self._status.value,

                start_time=self._start_time,

                end_time=self._end_time,

                duration=self.duration,

                attributes=copy.deepcopy(
                    self._attributes
                ),

                events=copy.deepcopy(
                    self._events
                ),

                links=copy.deepcopy(
                    self._links
                ),

                metadata=copy.deepcopy(
                    self._metadata
                ),

                statistics=self._statistics.to_dict(),

            )


    # ------------------------------------------------------------------------------
    # restore()
    # ------------------------------------------------------------------------------

    def restore(
        self,
        snapshot: SpanSnapshot,
    ) -> "TraceSpan":
        """
        Restore current object from snapshot.
        """

        if not isinstance(
            snapshot,
            SpanSnapshot,
        ):
            raise SpanValidationError(
                "Invalid snapshot."
            )

        with self._lock:

            self._trace_id = snapshot.trace_id
            self._span_id = snapshot.span_id
            self._parent_span_id = (
                snapshot.parent_span_id
            )

            self._name = snapshot.name
            self._kind = SpanKind(
                snapshot.kind
            )
            self._state = SpanState(
                snapshot.state
            )
            self._status = SpanStatus(
                snapshot.status
            )

            self._start_time = (
                snapshot.start_time
            )

            self._end_time = (
                snapshot.end_time
                or
                0.0
            )

            self._duration = (
                snapshot.duration
            )

            self._attributes = copy.deepcopy(
                snapshot.attributes
            )

            self._events = copy.deepcopy(
                snapshot.events
            )

            self._links = copy.deepcopy(
                snapshot.links
            )

            self._metadata = copy.deepcopy(
                snapshot.metadata
            )

            if hasattr(
                SpanStatistics,
                "from_dict",
            ):
                self._statistics = (
                    SpanStatistics.from_dict(
                        snapshot.statistics
                    )
                )
            else:
                self._statistics = (
                    SpanStatistics(
                        **snapshot.statistics
                    )
                )

            self._updated_at = time.time()

            return self

    
# ==============================================================================
# Part 9. Validation
# ==============================================================================

# ------------------------------------------------------------------------------
# validate()
# ------------------------------------------------------------------------------

    def validate(
        self,
    ) -> bool:
        """
        Validate runtime integrity.
        """

        with self._lock:

            self._validate_identity()
            self._validate_state()
            self._validate_flags()
            self._validate_timing()
            self._validate_collections()
            self._validate_statistics()

            return True


    # ------------------------------------------------------------------------------
    # _validate_identity()
    # ------------------------------------------------------------------------------

    def _validate_identity(
        self,
    ) -> None:
        """
        Validate identity fields.
        """

        if (
            not isinstance(
                self._trace_id,
                str,
            )
            or
            not self._trace_id.strip()
        ):
            raise SpanValidationError(
                "Invalid trace_id."
            )

        if (
            not isinstance(
                self._span_id,
                str,
            )
            or
            not self._span_id.strip()
        ):
            raise SpanValidationError(
                "Invalid span_id."
            )

        if (
            self._parent_span_id is not None
            and
            (
                not isinstance(
                    self._parent_span_id,
                    str,
                )
                or
                not self._parent_span_id.strip()
            )
        ):
            raise SpanValidationError(
                "Invalid parent_span_id."
            )

        if (
            not isinstance(
                self._name,
                str,
            )
            or
            not self._name.strip()
        ):
            raise SpanValidationError(
                "Span name cannot be empty."
            )


    # ------------------------------------------------------------------------------
    # _validate_state()
    # ------------------------------------------------------------------------------

    def _validate_state(
        self,
    ) -> None:
        """
        Validate enum objects.
        """

        if not isinstance(
            self._kind,
            SpanKind,
        ):
            raise SpanValidationError(
                "Invalid span kind."
            )

        if not isinstance(
            self._state,
            SpanState,
        ):
            raise SpanValidationError(
                "Invalid span state."
            )

        if not isinstance(
            self._status,
            SpanStatus,
        ):
            raise SpanValidationError(
                "Invalid span status."
            )


    # ------------------------------------------------------------------------------
    # _validate_flags()
    # ------------------------------------------------------------------------------

    def _validate_flags(
        self,
    ) -> None:
        """
        Validate lifecycle flags.
        """

        flags = (

            getattr(
                self,
                "_enabled",
                True,
            ),

            getattr(
                self,
                "_started",
                False,
            ),

            getattr(
                self,
                "_finished",
                False,
            ),

            getattr(
                self,
                "_cancelled",
                False,
            ),

            getattr(
                self,
                "_closed",
                False,
            ),
        )

        if not all(
            isinstance(
                value,
                bool,
            )
            for value in flags
        ):
            raise SpanValidationError(
                "Lifecycle flags must be bool."
            )

        if (
            self._finished
            and
            not self._started
        ):
            raise SpanValidationError(
                "Finished span must be started."
            )

        if (
            self._closed
            and
            not self._finished
            and
            not self._cancelled
        ):
            raise SpanValidationError(
                "Closed span must be finished or cancelled."
            )

        if (
            self._cancelled
            and
            self._status
            not in (
                SpanStatus.ERROR,
                SpanStatus.CANCELLED,
            )
        ):
            raise SpanValidationError(
                "Cancelled span has invalid status."
            )


    # ------------------------------------------------------------------------------
    # _validate_timing()
    # ------------------------------------------------------------------------------

    def _validate_timing(
        self,
    ) -> None:
        """
        Validate timestamps.
        """

        values = (

            self._created_at,

            self._updated_at,

            self._start_time,

            self._end_time,
        )

        for value in values:

            if (
                value is not None
                and
                value < 0.0
            ):
                raise SpanValidationError(
                    "Timestamp cannot be negative."
                )

        if (
            self._updated_at
            <
            self._created_at
        ):
            raise SpanValidationError(
                "updated_at precedes created_at."
            )

        if (
            self._start_time > 0.0
            and
            self._end_time > 0.0
            and
            self._end_time < self._start_time
        ):
            raise SpanValidationError(
                "end_time precedes start_time."
            )

        duration = getattr(
            self,
            "_duration",
            self.duration,
        )

        if duration < 0.0:
            raise SpanValidationError(
                "Negative duration."
            )

        if (
            self._finished
            and
            self._start_time > 0.0
            and
            self._end_time > 0.0
        ):

            expected = (
                self._end_time
                -
                self._start_time
            )

            if abs(
                expected - duration
            ) > 1e-6:
                raise SpanValidationError(
                    "Duration mismatch."
                )


    # ------------------------------------------------------------------------------
    # _validate_collections()
    # ------------------------------------------------------------------------------

    def _validate_collections(
        self,
    ) -> None:
        """
        Validate runtime collections.
        """

        mappings = {

            "attributes":
                self._attributes,

            "context":
                self._context,

            "metadata":
                self._metadata,

            "children":
                self._children,

            "cache":
                self._cache,
        }

        for name, value in mappings.items():

            if not isinstance(
                value,
                dict,
            ):
                raise SpanValidationError(
                    f"{name} must be dict."
                )

        if not isinstance(
            self._tags,
            (
                dict,
                list,
                set,
            ),
        ):
            raise SpanValidationError(
                "tags must be collection."
            )

        if not isinstance(
            self._events,
            list,
        ):
            raise SpanValidationError(
                "events must be list."
            )

        if not isinstance(
            self._links,
            list,
        ):
            raise SpanValidationError(
                "links must be list."
            )

        if not isinstance(
            self._history,
            deque,
        ):
            raise SpanValidationError(
                "history must be deque."
            )


    # ------------------------------------------------------------------------------
    # _validate_statistics()
    # ------------------------------------------------------------------------------

    def _validate_statistics(
        self,
    ) -> None:
        """
        Validate statistics consistency.
        """

        if not isinstance(
            self._statistics,
            SpanStatistics,
        ):
            raise SpanValidationError(
                "Invalid statistics object."
            )

        checks = (

            (
                "attribute_count",
                len(
                    self._attributes
                ),
            ),

            (
                "event_count",
                len(
                    self._events
                ),
            ),

            (
                "link_count",
                len(
                    self._links
                ),
            ),
        )

        for field, expected in checks:

            actual = getattr(
                self._statistics,
                field,
                expected,
            )

            if actual != expected:
                raise SpanValidationError(
                    f"{field} mismatch."
                )
# ==============================================================================
# Part 10. Diagnostics
# ==============================================================================

# ------------------------------------------------------------------------------
# health()
# ------------------------------------------------------------------------------

    def health(
        self,
    ) -> bool:
        """
        Return runtime health status.
        """

        with self._lock:

            try:

                self.validate()

            except Exception:

                return False

            return (

                not getattr(
                    self,
                    "_closed",
                    False,
                )

                and

                self._state is not SpanState.CLOSED

            )


    # ------------------------------------------------------------------------------
    # diagnostics()
    # ------------------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, Any]:
        """
        Return detailed runtime diagnostics.
        """

        with self._lock:

            statistics = self._statistics.to_dict()

            return {

                # --------------------------------------------------------------
                # Health
                # --------------------------------------------------------------

                "healthy":
                    self.health(),

                "valid":
                    self.health(),

                # --------------------------------------------------------------
                # Identity
                # --------------------------------------------------------------

                "trace_id":
                    self._trace_id,

                "span_id":
                    self._span_id,

                "parent_span_id":
                    self._parent_span_id,

                "name":
                    self._name,

                "kind":
                    self._kind.value,

                # --------------------------------------------------------------
                # Lifecycle
                # --------------------------------------------------------------

                "state":
                    self._state.value,

                "status":
                    self._status.value,

                "enabled":
                    self._enabled,

                "started":
                    self._started,

                "finished":
                    self._finished,

                "cancelled":
                    getattr(
                        self,
                        "_cancelled",
                        False,
                    ),

                "closed":
                    getattr(
                        self,
                        "_closed",
                        False,
                    ),

                # --------------------------------------------------------------
                # Timing
                # --------------------------------------------------------------

                "created_at":
                    self._created_at,

                "updated_at":
                    self._updated_at,

                "started_at":
                    self._started_at,

                "finished_at":
                    self._finished_at,

                "start_time":
                    self._start_time,

                "end_time":
                    self._end_time,

                "duration":
                    self.duration,

                # --------------------------------------------------------------
                # Collections
                # --------------------------------------------------------------

                "attributes":
                    len(self._attributes),

                "events":
                    len(self._events),

                "links":
                    len(self._links),

                "children":
                    len(self._children),

                "history":
                    len(self._history),

                "tags":
                    copy.deepcopy(
                        self._tags,
                    ),

                "metadata":
                    copy.deepcopy(
                        self._metadata,
                    ),

                "context":
                    copy.deepcopy(
                        self._context,
                    ),

                # --------------------------------------------------------------
                # Statistics
                # --------------------------------------------------------------

                "statistics":
                    statistics,
            }


    # ------------------------------------------------------------------------------
    # summary()
    # ------------------------------------------------------------------------------

    def summary(
        self,
    ) -> dict[str, Any]:
        """
        Return compact runtime summary.
        """

        with self._lock:

            return {

                "trace_id":
                    self._trace_id,

                "span_id":
                    self._span_id,

                "name":
                    self._name,

                "kind":
                    self._kind.value,

                "state":
                    self._state.value,

                "status":
                    self._status.value,

                "duration":
                    self.duration,

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

                "healthy":
                    self.health(),

            }


    # ------------------------------------------------------------------------------
    # report()
    # ------------------------------------------------------------------------------

    def report(
        self,
    ) -> SpanReport:
        """
        Generate SpanReport.
        """

        with self._lock:

            report = SpanReport()

            report.trace_id = self._trace_id
            report.span_id = self._span_id
            report.parent_span_id = self._parent_span_id

            report.name = self._name
            report.kind = self._kind.value

            report.state = self._state.value
            report.status = self._status.value

            report.duration = self.duration

            report.event_count = len(
                self._events
            )

            report.attribute_count = len(
                self._attributes
            )

            report.link_count = len(
                self._links
            )

            report.child_count = len(
                self._children
            )

            report.error_count = getattr(
                self._statistics,
                "error_count",
                0,
            )

            report.created_at = self._created_at

            return report


    # ------------------------------------------------------------------------------
    # runtime_statistics()
    # ------------------------------------------------------------------------------

    def runtime_statistics(
        self,
    ) -> dict[str, Any]:
        """
        Return runtime statistics.
        """

        with self._lock:

            uptime = max(

                0.0,

                time.time()
                -
                self._created_at,

            )

            return {

                "identity": {

                    "trace_id":
                        self._trace_id,

                    "span_id":
                        self._span_id,

                    "name":
                        self._name,

                },

                "lifecycle": {

                    "state":
                        self._state.value,

                    "status":
                        self._status.value,

                    "enabled":
                        self._enabled,

                    "started":
                        self._started,

                    "finished":
                        self._finished,

                },

                "counts": {

                    "attributes":
                        len(
                            self._attributes
                        ),

                    "events":
                        len(
                            self._events
                        ),

                    "links":
                        len(
                            self._links
                        ),

                    "children":
                        len(
                            self._children
                        ),

                },

                "timing": {

                    "duration":
                        self.duration,

                    "uptime":
                        uptime,

                },

                "statistics":
                    self._statistics.to_dict(),

            }


    # ------------------------------------------------------------------------------
    # success_rate()
    # ------------------------------------------------------------------------------

    def success_rate(
        self,
    ) -> float:
        """
        Return success rate.
        """

        with self._lock:

            status = self._status

            if status is SpanStatus.OK:
                return 1.0

            if status is SpanStatus.ERROR:
                return 0.0

            if status is SpanStatus.UNSET:
                return 0.5

            return 0.5


    # ------------------------------------------------------------------------------
    # failure_rate()
    # ------------------------------------------------------------------------------

    def failure_rate(
        self,
    ) -> float:
        """
        Return failure rate.
        """

        return max(

            0.0,

            1.0
            -
            self.success_rate(),

        )


    # ------------------------------------------------------------------------------
    # duration_statistics()
    # ------------------------------------------------------------------------------

    def duration_statistics(
        self,
    ) -> dict[str, float]:
        """
        Return duration statistics.
        """

        with self._lock:

            duration = max(
                0.0,
                self.duration,
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


    # ------------------------------------------------------------------------------
    # throughput()
    # ------------------------------------------------------------------------------

    def throughput(
        self,
    ) -> float:
        """
        Return event throughput.
        """

        with self._lock:

            duration = self.duration

            if duration <= 0.0:

                return 0.0

            return (

                len(
                    self._events
                )

                /

                duration

            ) 

# ==============================================================================
# Part 11. Python Protocols
# ==============================================================================

# ------------------------------------------------------------------------------
# Representation
# ------------------------------------------------------------------------------

    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """

        with self._lock:

            return (

                "TraceSpan("

                f"name={self._name!r}, "

                f"trace_id={self._trace_id!r}, "

                f"span_id={self._span_id!r}, "

                f"state={self._state.value!r}, "

                f"status={self._status.value!r}, "

                f"events={len(self._events)}, "

                f"attributes={len(self._attributes)}, "

                f"links={len(self._links)}"

                ")"

            )


    def __str__(
        self,
    ) -> str:
        """
        Human readable representation.
        """

        with self._lock:

            return (

                f"{self._name}"

                f"[{self._span_id}] "

                f"{self._status.value}"

            )


    # ------------------------------------------------------------------------------
    # Container Protocol
    # ------------------------------------------------------------------------------

    def __len__(
        self,
    ) -> int:
        """
        Return runtime object count.

        attributes + events + links
        """

        with self._lock:

            return (

                len(
                    self._attributes
                )

                +

                len(
                    self._events
                )

                +

                len(
                    self._links
                )

            )


    def __iter__(
        self,
    ) -> Iterator[str]:
        """
        Iterate attribute keys.
        """

        with self._lock:

            return iter(

                tuple(
                    self._attributes.keys()
                )

            )


    def __contains__(
        self,
        key: object,
    ) -> bool:
        """
        Check attribute existence.
        """

        if not isinstance(
            key,
            str,
        ):

            return False

        with self._lock:

            return (

                key
                in
                self._attributes

            )


    # ------------------------------------------------------------------------------
    # Mapping Protocol
    # ------------------------------------------------------------------------------

    def __getitem__(
        self,
        key: str,
    ) -> Any:
        """
        Get attribute.
        """

        with self._lock:

            return self._attributes[
                key
            ]


    def __setitem__(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Set attribute.
        """

        self.set_attribute(

            key,

            value,

        )


    def __delitem__(
        self,
        key: str,
    ) -> None:
        """
        Delete attribute.
        """

        if not self.remove_attribute(
            key
        ):

            raise KeyError(
                key
            )


    # ------------------------------------------------------------------------------
    # Boolean Protocol
    # ------------------------------------------------------------------------------

    def __bool__(
        self,
    ) -> bool:
        """
        Runtime truth state.
        """

        with self._lock:

            return (

                self._enabled

                and

                not getattr(
                    self,
                    "_cancelled",
                    False,
                )

                and

                not getattr(
                    self,
                    "_closed",
                    False,
                )

                and

                self._state
                is not SpanState.CLOSED

            )


    # ------------------------------------------------------------------------------
    # Copy Protocol
    # ------------------------------------------------------------------------------

    def __copy__(
        self,
    ) -> "TraceSpan":
        """
        Shallow runtime copy.
        """

        return self.__class__.from_dict(

            self.to_dict()

        )


    def __deepcopy__(
        self,
        memo: dict[int, Any] | None = None,
    ) -> "TraceSpan":
        """
        Deep runtime copy.
        """

        if memo is None:

            memo = {}


        existing = memo.get(
            id(self)
        )

        if existing is not None:

            return existing


        obj = self.__class__.from_dict(

            copy.deepcopy(

                self.to_dict(),

                memo,

            )

        )

        memo[
            id(self)
        ] = obj

        return obj


    # ------------------------------------------------------------------------------
    # Equality / Hash
    # ------------------------------------------------------------------------------

    def __eq__(
        self,
        other: object,
    ) -> bool:
        """
        Compare spans by identity.
        """

        if not isinstance(
            other,
            TraceSpan,
        ):

            return NotImplemented

        return (

            self._trace_id
            ==
            other._trace_id

            and

            self._span_id
            ==
            other._span_id

        )


    def __hash__(
        self,
    ) -> int:
        """
        Hash by identity.
        """

        return hash(

            (

                self._trace_id,

                self._span_id,

            )

        )


    # ------------------------------------------------------------------------------
    # Context Manager
    # ------------------------------------------------------------------------------

    def __enter__(
        self,
    ) -> "TraceSpan":
        """
        Enter runtime context.
        """

        self.start()

        return self


    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        """
        Exit runtime context.
        """

        if exc_value is not None:

            self.finish()

            self._status = SpanStatus.ERROR

            if hasattr(
                self,
                "record_exception",
            ):

                self.record_exception(
                    exc_value
                )

        else:

            self.finish()

            self._status = SpanStatus.OK

        return False

# ==============================================================================
# Public Alias
# ==============================================================================

Span = TraceSpan



# ==============================================================================
# Public API
# ==============================================================================


__all__ = [

    # ------------------------------------------------------------------
    # Main Runtime Objects
    # ------------------------------------------------------------------

    "TraceSpan",

    "Span",


    # ------------------------------------------------------------------
    # Dataclasses
    # ------------------------------------------------------------------

    "SpanStatistics",

    "SpanSnapshot",

    "SpanReport",


    # ------------------------------------------------------------------
    # Enumerations
    # ------------------------------------------------------------------

    "SpanKind",

    "SpanState",

    "SpanStatus",

    "SpanCapability",


    # ------------------------------------------------------------------
    # Exceptions
    # ------------------------------------------------------------------

    "TraceSpanError",

    "SpanValidationError",

    "SpanStateError",

    "SpanClosedError",

    "SpanFinishedError",

    "InvalidTraceError",

]
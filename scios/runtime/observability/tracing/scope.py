# ==============================================================================
# SciOS-NG
# Runtime Observability - Trace Scope
#
# File:
#     scios/runtime/observability/tracing/scope.py
#
# Part 1.1. Imports
# ==============================================================================

from __future__ import annotations

# ==============================================================================
# Standard Library
# ==============================================================================

import copy
import functools
import json
import logging
import threading
import time
import uuid

from abc import ABC
from collections import deque
from collections import defaultdict
from collections.abc import Callable
from collections.abc import Iterable
from collections.abc import Iterator
from collections.abc import Mapping
from collections.abc import MutableMapping
from contextlib import ContextDecorator
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from enum import Flag
from enum import auto
from pathlib import Path
from threading import RLock
from types import TracebackType
from typing import Any
from typing import Dict
from typing import Final
from typing import List
from typing import Optional
from typing import Sequence
from typing import Set
from typing import Tuple
from typing import Type
from typing import TypeAlias
from typing import Union

# ==============================================================================
# SciOS Runtime
# ==============================================================================

from .context import (
    TraceContext,
)

from .manager import (
    TraceManager,
)

from .provider import (
    TraceProvider,
)

from .tracer import (
    TraceTracer,
)

from .span import (
    TraceSpan,
    SpanKind,
    SpanStatus,
    SpanStatistics,
    SpanSnapshot,
)

# ==============================================================================
# Module Logger
# ==============================================================================

logger = logging.getLogger(__name__)
# ==============================================================================
# Part 1.2. Constants
# ==============================================================================

#
# ------------------------------------------------------------------------------
# Module
# ------------------------------------------------------------------------------

SCOPE_VERSION: Final[str] = "0.1.0"

LOGGER_NAME: Final[str] = (
    "scios.runtime.observability.tracing.scope"
)

#
# ------------------------------------------------------------------------------
# Default Names
# ------------------------------------------------------------------------------

DEFAULT_TRACE_SCOPE_NAME: Final[str] = (
    "TraceScope"
)

DEFAULT_SPAN_SCOPE_NAME: Final[str] = (
    "SpanScope"
)

DEFAULT_TRACE_NAME: Final[str] = (
    "Trace"
)

DEFAULT_SPAN_NAME: Final[str] = (
    "Span"
)

#
# ------------------------------------------------------------------------------
# Runtime
# ------------------------------------------------------------------------------

DEFAULT_TIMEOUT: Final[float] = 30.0

DEFAULT_HISTORY_LIMIT: Final[int] = 1024

DEFAULT_CACHE_SIZE: Final[int] = 256

DEFAULT_ENCODING: Final[str] = (
    "utf-8"
)

DEFAULT_PRIORITY: Final[int] = 0

#
# ------------------------------------------------------------------------------
# State
# ------------------------------------------------------------------------------

DEFAULT_ENABLED: Final[bool] = True

DEFAULT_ACTIVE: Final[bool] = False

DEFAULT_RUNNING: Final[bool] = False

DEFAULT_FROZEN: Final[bool] = False

DEFAULT_CLOSED: Final[bool] = False

DEFAULT_AUTO_START: Final[bool] = True

DEFAULT_AUTO_FINISH: Final[bool] = True

#
# ------------------------------------------------------------------------------
# Callback / Hook
# ------------------------------------------------------------------------------

DEFAULT_CALLBACK_EVENT: Final[str] = (
    "scope"
)

HOOK_BEFORE_ENTER: Final[str] = (
    "before_enter"
)

HOOK_AFTER_ENTER: Final[str] = (
    "after_enter"
)

HOOK_BEFORE_EXIT: Final[str] = (
    "before_exit"
)

HOOK_AFTER_EXIT: Final[str] = (
    "after_exit"
)

HOOK_BEFORE_TRACE: Final[str] = (
    "before_trace"
)

HOOK_AFTER_TRACE: Final[str] = (
    "after_trace"
)

HOOK_BEFORE_SPAN: Final[str] = (
    "before_span"
)

HOOK_AFTER_SPAN: Final[str] = (
    "after_span"
)

HOOK_EXCEPTION: Final[str] = (
    "exception"
)

#
# ------------------------------------------------------------------------------
# Metadata
# ------------------------------------------------------------------------------

DEFAULT_METADATA: Final[dict[str, Any]] = {}

DEFAULT_OPTIONS: Final[dict[str, Any]] = {}

DEFAULT_TAGS: Final[list[str]] = []

DEFAULT_ATTRIBUTES: Final[
    dict[str, Any]
] = {}

#
# ------------------------------------------------------------------------------
# Snapshot / Serialization
# ------------------------------------------------------------------------------

SNAPSHOT_VERSION: Final[str] = (
    "1.0"
)

JSON_INDENT: Final[int] = 4

JSON_SORT_KEYS: Final[bool] = True

JSON_ENSURE_ASCII: Final[bool] = False

#
# ------------------------------------------------------------------------------
# Context Keys
# ------------------------------------------------------------------------------

CONTEXT_TRACE_ID: Final[str] = (
    "trace_id"
)

CONTEXT_SPAN_ID: Final[str] = (
    "span_id"
)

CONTEXT_PARENT_SPAN_ID: Final[str] = (
    "parent_span_id"
)

CONTEXT_SCOPE_NAME: Final[str] = (
    "scope_name"
)

CONTEXT_SCOPE_TYPE: Final[str] = (
    "scope_type"
)

#
# ------------------------------------------------------------------------------
# Statistics
# ------------------------------------------------------------------------------

DEFAULT_ENTER_COUNT: Final[int] = 0

DEFAULT_EXIT_COUNT: Final[int] = 0

DEFAULT_EXCEPTION_COUNT: Final[int] = 0

DEFAULT_CALLBACK_COUNT: Final[int] = 0

DEFAULT_HOOK_COUNT: Final[int] = 0

DEFAULT_TOTAL_DURATION: Final[float] = 0.0

DEFAULT_MIN_DURATION: Final[float] = 0.0

DEFAULT_MAX_DURATION: Final[float] = 0.0
# ==============================================================================
# Part 1.3. Type Aliases
# ==============================================================================

#
# ------------------------------------------------------------------------------
# Identity
# ------------------------------------------------------------------------------

ScopeId: TypeAlias = str

ScopeName: TypeAlias = str

ScopeUUID: TypeAlias = uuid.UUID

#
# ------------------------------------------------------------------------------
# Runtime Objects
# ------------------------------------------------------------------------------

TraceObject: TypeAlias = TraceSpan

SpanObject: TypeAlias = TraceSpan

TracerObject: TypeAlias = TraceTracer

ManagerObject: TypeAlias = TraceManager

ProviderObject: TypeAlias = TraceProvider

ContextObject: TypeAlias = TraceContext

#
# ------------------------------------------------------------------------------
# Metadata
# ------------------------------------------------------------------------------

ScopeMetadata: TypeAlias = Dict[
    str,
    Any,
]

ScopeOptions: TypeAlias = Dict[
    str,
    Any,
]

ScopeAttributes: TypeAlias = Dict[
    str,
    Any,
]

ScopeContext: TypeAlias = Dict[
    str,
    Any,
]

ScopeSnapshot: TypeAlias = Dict[
    str,
    Any,
]

#
# ------------------------------------------------------------------------------
# Collections
# ------------------------------------------------------------------------------

ScopeList: TypeAlias = List[
    "BaseScope"
]

ScopeSequence: TypeAlias = Sequence[
    "BaseScope"
]

ScopeIterator: TypeAlias = Iterator[
    "BaseScope"
]

SpanCollection: TypeAlias = Dict[
    str,
    TraceSpan,
]

TraceCollection: TypeAlias = Dict[
    str,
    TraceSpan,
]

HookCollection: TypeAlias = Dict[
    str,
    List["ScopeHook"],
]

CallbackCollection: TypeAlias = List[
    "ScopeCallback",
]

FilterCollection: TypeAlias = List[
    "ScopeFilter",
]

#
# ------------------------------------------------------------------------------
# Callback Types
# ------------------------------------------------------------------------------

ScopeCallback: TypeAlias = Callable[
    ...,
    Any,
]

ScopeHook: TypeAlias = Callable[
    ...,
    Any,
]

ScopeFilter: TypeAlias = Callable[
    [
        TraceSpan,
    ],
    bool,
]

ScopeFactory: TypeAlias = Callable[
    [],
    "BaseScope",
]

#
# ------------------------------------------------------------------------------
# Decorator Types
# ------------------------------------------------------------------------------

DecoratorFunction: TypeAlias = Callable[
    ...,
    Any,
]

WrappedFunction: TypeAlias = Callable[
    ...,
    Any,
]

DecoratorFactory: TypeAlias = Callable[
    [
        DecoratorFunction,
    ],
    WrappedFunction,
]

#
# ------------------------------------------------------------------------------
# Context Manager Types
# ------------------------------------------------------------------------------

EnterResult: TypeAlias = Union[
    TraceSpan,
    None,
]

ExitResult: TypeAlias = bool

ExceptionType: TypeAlias = Optional[
    Type[BaseException]
]

ExceptionValue: TypeAlias = Optional[
    BaseException
]

ExceptionTraceback: TypeAlias = Optional[
    TracebackType
]

#
# ------------------------------------------------------------------------------
# Serialization
# ------------------------------------------------------------------------------

Serializable: TypeAlias = Union[
    Dict[str, Any],
    List[Any],
    str,
    int,
    float,
    bool,
    None,
]

JSONValue: TypeAlias = Union[
    str,
    bytes,
    bytearray,
    Path,
]

#
# ------------------------------------------------------------------------------
# Generic Runtime Types
# ------------------------------------------------------------------------------

Timestamp: TypeAlias = float

Duration: TypeAlias = float

Priority: TypeAlias = int

TagSet: TypeAlias = Set[
    str,
]

TagSequence: TypeAlias = Sequence[
    str,
]

History: TypeAlias = deque[
    Any,
]

Cache: TypeAlias = MutableMapping[
    str,
    Any,
]

RuntimeState: TypeAlias = Dict[
    str,
    Any,
]
# ==============================================================================
# Part 1.4. Exceptions
# ==============================================================================


class ScopeError(RuntimeError):
    """
    Base exception for all tracing scope errors.

    Every exception raised from TraceScope, SpanScope,
    or BaseScope should inherit from this class.
    """


# ------------------------------------------------------------------------------
# Lifecycle
# ------------------------------------------------------------------------------


class ScopeClosedError(ScopeError):
    """
    Raised when attempting to use a closed scope.
    """


class ScopeFrozenError(ScopeError):
    """
    Raised when a frozen scope is modified.
    """


class ScopeDisposedError(ScopeError):
    """
    Raised when a disposed scope is accessed.
    """


class ScopeStateError(ScopeError):
    """
    Raised when the scope is in an invalid runtime state.
    """


# ------------------------------------------------------------------------------
# Validation
# ------------------------------------------------------------------------------


class ScopeValidationError(ScopeError):
    """
    Raised when scope validation fails.
    """


class ScopeConfigurationError(ScopeError):
    """
    Raised when the scope configuration is invalid.
    """


class ScopeInitializationError(ScopeError):
    """
    Raised when the scope cannot be initialized.
    """


# ------------------------------------------------------------------------------
# Tracing
# ------------------------------------------------------------------------------


class TraceScopeError(ScopeError):
    """
    Raised while creating or finishing a trace scope.
    """


class SpanScopeError(ScopeError):
    """
    Raised while creating or finishing a span scope.
    """


class TraceStartError(TraceScopeError):
    """
    Raised when a trace cannot be started.
    """


class TraceFinishError(TraceScopeError):
    """
    Raised when a trace cannot be finished.
    """


class SpanStartError(SpanScopeError):
    """
    Raised when a span cannot be started.
    """


class SpanFinishError(SpanScopeError):
    """
    Raised when a span cannot be finished.
    """


# ------------------------------------------------------------------------------
# Runtime Components
# ------------------------------------------------------------------------------


class ManagerNotAvailableError(ScopeError):
    """
    Raised when no TraceManager is available.
    """


class TracerNotAvailableError(ScopeError):
    """
    Raised when no TraceTracer is available.
    """


class ContextNotAvailableError(ScopeError):
    """
    Raised when no TraceContext is available.
    """


# ------------------------------------------------------------------------------
# Callback / Hook
# ------------------------------------------------------------------------------


class CallbackError(ScopeError):
    """
    Raised when callback registration fails.
    """


class HookError(ScopeError):
    """
    Raised when hook execution fails.
    """


# ------------------------------------------------------------------------------
# Serialization
# ------------------------------------------------------------------------------


class ScopeSerializationError(ScopeError):
    """
    Raised when serialization fails.
    """


class ScopeDeserializationError(ScopeError):
    """
    Raised when deserialization fails.
    """


# ------------------------------------------------------------------------------
# Context Manager
# ------------------------------------------------------------------------------


class ScopeEnterError(ScopeError):
    """
    Raised during __enter__().
    """


class ScopeExitError(ScopeError):
    """
    Raised during __exit__().
    """


# ------------------------------------------------------------------------------
# Internal Runtime
# ------------------------------------------------------------------------------


class ScopeTimeoutError(ScopeError):
    """
    Raised when a scope operation times out.
    """


class ScopeRuntimeError(ScopeError):
    """
    Raised for unexpected runtime failures.
    """
# ==============================================================================
# Part 1.5. Enums
# ==============================================================================

# ==============================================================================
# ScopeType
# ==============================================================================


class ScopeType(str, Enum):
    """
    Scope implementation type.

    Used to distinguish different runtime scope objects.
    """

    TRACE = "trace"

    SPAN = "span"

    AUTO = "auto"

    MANUAL = "manual"

    DECORATOR = "decorator"

    CONTEXT_MANAGER = "context_manager"

    CUSTOM = "custom"


# ==============================================================================
# ScopeState
# ==============================================================================


class ScopeState(str, Enum):
    """
    Runtime lifecycle state.
    """

    CREATED = "created"

    INITIALIZED = "initialized"

    ENTERED = "entered"

    ACTIVE = "active"

    EXITING = "exiting"

    FINISHED = "finished"

    CANCELLED = "cancelled"

    FROZEN = "frozen"

    CLOSED = "closed"

    ERROR = "error"


# ==============================================================================
# ScopeMode
# ==============================================================================


class ScopeMode(str, Enum):
    """
    Scope execution mode.
    """

    SYNCHRONOUS = "sync"

    ASYNCHRONOUS = "async"

    MANUAL = "manual"

    AUTOMATIC = "automatic"


# ==============================================================================
# ScopeCapability
# ==============================================================================


class ScopeCapability(Flag):
    """
    Runtime capabilities supported by a scope.

    Multiple capabilities may be combined.
    """

    NONE = 0

    TRACE = auto()

    SPAN = auto()

    CONTEXT = auto()

    DECORATOR = auto()

    CONTEXT_MANAGER = auto()

    CALLBACKS = auto()

    HOOKS = auto()

    FILTERS = auto()

    SERIALIZATION = auto()

    SNAPSHOT = auto()

    CLONE = auto()

    COPY = auto()

    RESTORE = auto()

    VALIDATION = auto()

    STATISTICS = auto()

    METADATA = auto()

    TAGS = auto()

    HISTORY = auto()

    CACHE = auto()

    THREAD_LOCAL = auto()

    AUTO_START = auto()

    AUTO_FINISH = auto()

    ALL = (
        TRACE
        | SPAN
        | CONTEXT
        | DECORATOR
        | CONTEXT_MANAGER
        | CALLBACKS
        | HOOKS
        | FILTERS
        | SERIALIZATION
        | SNAPSHOT
        | CLONE
        | COPY
        | RESTORE
        | VALIDATION
        | STATISTICS
        | METADATA
        | TAGS
        | HISTORY
        | CACHE
        | THREAD_LOCAL
        | AUTO_START
        | AUTO_FINISH
    )


# ==============================================================================
# ScopeEvent
# ==============================================================================


class ScopeEvent(str, Enum):
    """
    Standard lifecycle events emitted by TraceScope and SpanScope.
    """

    BEFORE_ENTER = "before_enter"

    AFTER_ENTER = "after_enter"

    BEFORE_EXIT = "before_exit"

    AFTER_EXIT = "after_exit"

    BEFORE_TRACE = "before_trace"

    AFTER_TRACE = "after_trace"

    BEFORE_SPAN = "before_span"

    AFTER_SPAN = "after_span"

    BEFORE_CALLBACK = "before_callback"

    AFTER_CALLBACK = "after_callback"

    BEFORE_HOOK = "before_hook"

    AFTER_HOOK = "after_hook"

    EXCEPTION = "exception"

    VALIDATION = "validation"

    SNAPSHOT = "snapshot"

    RESTORE = "restore"


# ==============================================================================
# ScopeStatus
# ==============================================================================


class ScopeStatus(str, Enum):
    """
    Final execution status of a scope.
    """

    UNKNOWN = "unknown"

    SUCCESS = "success"

    FAILURE = "failure"

    CANCELLED = "cancelled"

    TIMEOUT = "timeout"

    EXCEPTION = "exception"
# ==============================================================================
# Part 1.6. Dataclasses
# ==============================================================================

# ==============================================================================
# ScopeStatistics
# ==============================================================================


@dataclass(slots=True)
class ScopeStatistics:
    """
    Runtime statistics for TraceScope and SpanScope.

    Notes
    -----
    Statistics are accumulated during the lifetime of a scope and
    are intended for diagnostics, profiling, monitoring and testing.
    """

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    enter_count: int = 0

    exit_count: int = 0

    start_count: int = 0

    finish_count: int = 0

    cancel_count: int = 0

    reset_count: int = 0

    close_count: int = 0

    # ------------------------------------------------------------------
    # Runtime
    # ------------------------------------------------------------------

    callback_count: int = 0

    hook_count: int = 0

    validation_count: int = 0

    serialization_count: int = 0

    restore_count: int = 0

    clone_count: int = 0

    copy_count: int = 0

    exception_count: int = 0

    # ------------------------------------------------------------------
    # Timing
    # ------------------------------------------------------------------

    total_duration: float = 0.0

    minimum_duration: float = 0.0

    maximum_duration: float = 0.0

    average_duration: float = 0.0

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    created_at: float = field(
        default_factory=time.time,
    )

    updated_at: float = field(
        default_factory=time.time,
    )

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def touch(self) -> None:
        """
        Update timestamp.
        """

        self.updated_at = time.time()

    # ------------------------------------------------------------------

    def reset(self) -> None:
        """
        Reset runtime counters.
        """

        self.enter_count = 0

        self.exit_count = 0

        self.start_count = 0

        self.finish_count = 0

        self.cancel_count = 0

        self.reset_count = 0

        self.close_count = 0

        self.callback_count = 0

        self.hook_count = 0

        self.validation_count = 0

        self.serialization_count = 0

        self.restore_count = 0

        self.clone_count = 0

        self.copy_count = 0

        self.exception_count = 0

        self.total_duration = 0.0

        self.minimum_duration = 0.0

        self.maximum_duration = 0.0

        self.average_duration = 0.0

        self.touch()


# ==============================================================================
# ScopeSnapshot
# ==============================================================================


@dataclass(slots=True)
class ScopeSnapshot:
    """
    Serializable runtime snapshot.

    Used by

        snapshot()

        restore()

        clone()

        copy()

    of TraceScope and SpanScope.
    """

    identity: Dict[str, Any]

    configuration: Dict[str, Any]

    runtime: Dict[str, Any]

    statistics: Dict[str, Any]

    metadata: Dict[str, Any]

    created_at: float = field(
        default_factory=time.time,
    )


# ==============================================================================
# ScopeReport
# ==============================================================================


@dataclass(slots=True)
class ScopeReport:
    """
    Human-readable diagnostics report.
    """

    scope_name: str

    scope_type: str

    runtime_state: str

    running: bool

    active: bool

    closed: bool

    enter_count: int

    exit_count: int

    callback_count: int

    hook_count: int

    exception_count: int

    total_duration: float

    average_duration: float

    generated_at: float = field(
        default_factory=time.time,
    )


# ==============================================================================
# ScopeRecord
# ==============================================================================


@dataclass(slots=True)
class ScopeRecord:
    """
    One runtime history record.
    """

    event: str

    timestamp: float = field(
        default_factory=time.time,
    )

    data: Dict[str, Any] = field(
        default_factory=dict,
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict,
    )


# ==============================================================================
# CallbackRecord
# ==============================================================================


@dataclass(slots=True)
class CallbackRecord:
    """
    Callback execution record.
    """

    callback: str

    event: str

    success: bool

    duration: float = 0.0

    timestamp: float = field(
        default_factory=time.time,
    )

    error: Optional[str] = None


# ==============================================================================
# HookRecord
# ==============================================================================


@dataclass(slots=True)
class HookRecord:
    """
    Hook execution record.
    """

    hook: str

    event: str

    success: bool

    duration: float = 0.0

    timestamp: float = field(
        default_factory=time.time,
    )

    error: Optional[str] = None
# ==============================================================================
# Part 2.1. TraceScope Class Declaration
# ==============================================================================


class TraceScope(ContextDecorator, ABC):
    """
    Runtime trace scope.

    TraceScope provides the highest-level tracing context used by the
    SciOS-NG observability subsystem. It can be used both as a Python
    context manager and as a function decorator.

    Examples
    --------
    Context manager::

        with TraceScope(manager, "Inference"):
            ...

    Decorator::

        @TraceScope(manager, "Training")
        def train():
            ...

    Notes
    -----
    A TraceScope is responsible for

    • creating a root trace

    • managing the current TraceTracer

    • coordinating TraceManager

    • synchronizing TraceContext

    • invoking callbacks

    • invoking hooks

    • collecting runtime statistics

    • handling automatic cleanup

    Lifecycle
    ---------

    CREATED
        ↓

    INITIALIZED
        ↓

    ENTERED
        ↓

    ACTIVE
        ↓

    EXITING
        ↓

    FINISHED

    Thread Safety
    -------------

    TraceScope is thread-safe.

    Every public operation is synchronized using an internal
    re-entrant lock.

    Relationships
    -------------

    TraceScope
        ├── TraceManager
        ├── TraceTracer
        ├── TraceContext
        ├── TraceSpan
        └── TraceProvider

    See Also
    --------

    SpanScope

    TraceManager

    TraceTracer

    TraceSpan
    """

    __slots__ = (

        # ------------------------------------------------------------------
        # Identity
        # ------------------------------------------------------------------

        "_id",

        "_uuid",

        "_name",

        "_version",

        "_scope_type",

        # ------------------------------------------------------------------
        # Components
        # ------------------------------------------------------------------

        "_manager",

        "_provider",

        "_tracer",

        "_context",

        "_trace",

        # ------------------------------------------------------------------
        # Configuration
        # ------------------------------------------------------------------

        "_enabled",

        "_auto_start",

        "_auto_finish",

        "_timeout",

        "_history_limit",

        "_encoding",

        "_options",

        "_capabilities",

        # ------------------------------------------------------------------
        # Runtime
        # ------------------------------------------------------------------

        "_state",

        "_status",

        "_initialized",

        "_running",

        "_active",

        "_frozen",

        "_closed",

        "_disposed",

        "_created_at",

        "_updated_at",

        "_started_at",

        "_finished_at",

        "_duration",

        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------

        "_statistics",

        # ------------------------------------------------------------------
        # Metadata
        # ------------------------------------------------------------------

        "_metadata",

        "_attributes",

        "_tags",

        "_history",

        "_cache",

        # ------------------------------------------------------------------
        # Events
        # ------------------------------------------------------------------

        "_callbacks",

        "_hooks",

        "_filters",

        # ------------------------------------------------------------------
        # Runtime Objects
        # ------------------------------------------------------------------

        "_logger",

        "_lock",

        "_thread_local",
    )
# ==============================================================================
# Part 2.2. Constructor Signature
# ==============================================================================

def __init__(
    self,
    manager: TraceManager,
    name: str = DEFAULT_TRACE_NAME,
    *,
    provider: Optional["TraceProvider"] = None,
    tracer: Optional[TraceTracer] = None,
    context: Optional[TraceContext] = None,
    enabled: bool = True,
    auto_start: bool = True,
    auto_finish: bool = True,
    timeout: float = DEFAULT_TIMEOUT,
    history_limit: int = DEFAULT_HISTORY_LIMIT,
    encoding: str = DEFAULT_ENCODING,
    options: Optional[Mapping[str, Any]] = None,
    metadata: Optional[Mapping[str, Any]] = None,
    attributes: Optional[Mapping[str, Any]] = None,
    tags: Optional[Iterable[str]] = None,
) -> None:
    """
    Initialize a TraceScope.

    Parameters
    ----------
    manager
        TraceManager responsible for coordinating tracing operations.

    name
        Human-readable trace name.

    provider
        Optional TraceProvider. If omitted, the provider will be
        obtained from the manager when available.

    tracer
        Optional TraceTracer. If omitted, the active tracer will be
        obtained from the manager.

    context
        Optional TraceContext. If omitted, the active tracing context
        will be created or retrieved automatically.

    enabled
        Enable this scope.

    auto_start
        Automatically call TraceTracer.start_trace() when entering
        the context.

    auto_finish
        Automatically call TraceTracer.end_trace() when leaving
        the context.

    timeout
        Maximum execution timeout (seconds).

    history_limit
        Maximum number of runtime history records.

    encoding
        Default serialization encoding.

    options
        Runtime configuration options.

    metadata
        User-defined metadata.

    attributes
        Initial trace attributes.

    tags
        Initial runtime tags.

    Raises
    ------
    ManagerNotAvailableError
        If manager is None.

    ScopeValidationError
        If configuration values are invalid.

    ScopeInitializationError
        If initialization fails.

    Notes
    -----
    The constructor performs initialization in the following order:

    1. Identity

    2. Components

    3. Configuration

    4. Runtime State

    5. Statistics

    6. Metadata

    7. Runtime Objects

    8. Validation

    See Also
    --------
    TraceManager

    TraceTracer

    TraceContext
    """
# ==============================================================================
# Part 2.3. Identity
# ==============================================================================

        # ----------------------------------------------------------------------
        # Identity
        # ----------------------------------------------------------------------

        self._id: str = uuid.uuid4().hex

        self._uuid: uuid.UUID = uuid.UUID(
            self._id,
        )

        self._name: str = (
            str(name).strip()
            if name
            else DEFAULT_TRACE_NAME
        )

        self._version: str = (
            SCOPE_VERSION
        )

        self._scope_type: ScopeType = (
            ScopeType.TRACE
        )

        # ----------------------------------------------------------------------
        # Creation Time
        # ----------------------------------------------------------------------

        now = time.time()

        self._created_at: float = now

        self._updated_at: float = now

        self._started_at: Optional[
            float
        ] = None

        self._finished_at: Optional[
            float
        ] = None

        self._duration: float = 0.0

        # ----------------------------------------------------------------------
        # Validation
        # ----------------------------------------------------------------------

        if not self._name:

            raise ScopeValidationError(
                "Scope name cannot be empty."
            )

        if len(
            self._name
        ) > 255:

            raise ScopeValidationError(
                "Scope name exceeds the maximum length "
                "(255 characters)."
            )

        # ----------------------------------------------------------------------
        # Logger
        # ----------------------------------------------------------------------

        logger.debug(

            "Creating TraceScope "

            "(id=%s, name=%s)",

            self._id,

            self._name,

        )
# ==============================================================================
# Part 2.4. Components
# ==============================================================================

        # ----------------------------------------------------------------------
        # Trace Manager
        # ----------------------------------------------------------------------

        if manager is None:

            raise ManagerNotAvailableError(
                "TraceManager cannot be None."
            )

        self._manager: TraceManager = manager

        # ----------------------------------------------------------------------
        # Trace Provider
        # ----------------------------------------------------------------------

        if provider is None:

            provider = getattr(
                manager,
                "provider",
                None,
            )

            if provider is None:

                getter = getattr(
                    manager,
                    "current_provider",
                    None,
                )

                if callable(
                    getter,
                ):

                    provider = getter()

        self._provider: Optional[
            TraceProvider
        ] = provider

        # ----------------------------------------------------------------------
        # Trace Tracer
        # ----------------------------------------------------------------------

        if tracer is None:

            getter = getattr(
                manager,
                "current_tracer",
                None,
            )

            if callable(
                getter,
            ):

                tracer = getter()

        if tracer is None:

            raise TracerNotAvailableError(
                "No active TraceTracer is available."
            )

        self._tracer: TraceTracer = tracer

        # ----------------------------------------------------------------------
        # Trace Context
        # ----------------------------------------------------------------------

        if context is None:

            context = getattr(
                tracer,
                "context",
                None,
            )

        if context is None:

            context = TraceContext()

        self._context: TraceContext = context

        # ----------------------------------------------------------------------
        # Active Runtime Objects
        # ----------------------------------------------------------------------

        #
        # Root trace created by this scope.
        #

        self._trace: Optional[
            TraceSpan
        ] = None

        #
        # Current active span while the scope is alive.
        #

        self._active_span: Optional[
            TraceSpan
        ] = None

        #
        # Cached root span.
        #

        self._root_span: Optional[
            TraceSpan
        ] = None

        # ----------------------------------------------------------------------
        # Validation
        # ----------------------------------------------------------------------

        if self._manager is None:

            raise ManagerNotAvailableError(
                "TraceScope requires a valid TraceManager."
            )

        if self._tracer is None:

            raise TracerNotAvailableError(
                "TraceScope requires a valid TraceTracer."
            )

        if self._context is None:

            raise ContextNotAvailableError(
                "TraceScope requires a valid TraceContext."
            )

        # ----------------------------------------------------------------------
        # Logger
        # ----------------------------------------------------------------------

        logger.debug(

            "TraceScope '%s' attached to "

            "manager='%s', tracer='%s'.",

            self._name,

            type(self._manager).__name__,

            type(self._tracer).__name__,

        )
# ==============================================================================
# Part 2.5. Configuration
# ==============================================================================

        # ----------------------------------------------------------------------
        # Enable / Disable
        # ----------------------------------------------------------------------

        self._enabled: bool = bool(
            enabled,
        )

        # ----------------------------------------------------------------------
        # Automatic Behaviour
        # ----------------------------------------------------------------------

        self._auto_start: bool = bool(
            auto_start,
        )

        self._auto_finish: bool = bool(
            auto_finish,
        )

        # ----------------------------------------------------------------------
        # Runtime Configuration
        # ----------------------------------------------------------------------

        self._timeout: float = max(
            0.0,
            float(timeout),
        )

        self._history_limit: int = max(
            1,
            int(history_limit),
        )

        self._encoding: str = str(
            encoding,
        ).strip() or DEFAULT_ENCODING

        # ----------------------------------------------------------------------
        # Runtime Options
        # ----------------------------------------------------------------------

        self._options: Dict[
            str,
            Any,
        ] = copy.deepcopy(

            dict(options)

            if options is not None

            else {}

        )

        # ----------------------------------------------------------------------
        # Capabilities
        # ----------------------------------------------------------------------

        self._capabilities: ScopeCapability = (

            ScopeCapability.TRACE

            | ScopeCapability.CONTEXT_MANAGER

            | ScopeCapability.DECORATOR

            | ScopeCapability.CONTEXT

            | ScopeCapability.CALLBACKS

            | ScopeCapability.HOOKS

            | ScopeCapability.FILTERS

            | ScopeCapability.SERIALIZATION

            | ScopeCapability.SNAPSHOT

            | ScopeCapability.RESTORE

            | ScopeCapability.CLONE

            | ScopeCapability.COPY

            | ScopeCapability.STATISTICS

            | ScopeCapability.METADATA

            | ScopeCapability.TAGS

            | ScopeCapability.HISTORY

            | ScopeCapability.CACHE

            | ScopeCapability.THREAD_LOCAL

            | ScopeCapability.VALIDATION

        )

        # ----------------------------------------------------------------------
        # Limits
        # ----------------------------------------------------------------------

        self._maximum_history: int = (
            self._history_limit
        )

        self._maximum_cache_size: int = (
            DEFAULT_CACHE_SIZE
        )

        self._maximum_callbacks: int = 1024

        self._maximum_hooks: int = 1024

        self._maximum_filters: int = 256

        # ----------------------------------------------------------------------
        # Validation
        # ----------------------------------------------------------------------

        if self._timeout < 0.0:

            raise ScopeValidationError(
                "timeout must be >= 0."
            )

        if self._history_limit <= 0:

            raise ScopeValidationError(
                "history_limit must be > 0."
            )

        if not self._encoding:

            raise ScopeValidationError(
                "encoding cannot be empty."
            )

        # ----------------------------------------------------------------------
        # Logger
        # ----------------------------------------------------------------------

        logger.debug(

            "TraceScope configuration "

            "(enabled=%s, auto_start=%s, "

            "auto_finish=%s, timeout=%s, "

            "history_limit=%s)",

            self._enabled,

            self._auto_start,

            self._auto_finish,

            self._timeout,

            self._history_limit,

        )
# ==============================================================================
# Part 2.6. Runtime State
# ==============================================================================

        # ----------------------------------------------------------------------
        # Lifecycle State
        # ----------------------------------------------------------------------

        self._state: ScopeState = (
            ScopeState.CREATED
        )

        self._status: ScopeStatus = (
            ScopeStatus.UNKNOWN
        )

        # ----------------------------------------------------------------------
        # Runtime Flags
        # ----------------------------------------------------------------------

        self._initialized: bool = False

        self._running: bool = False

        self._active: bool = False

        self._entered: bool = False

        self._finished: bool = False

        self._cancelled: bool = False

        self._frozen: bool = False

        self._closed: bool = False

        self._disposed: bool = False

        # ----------------------------------------------------------------------
        # Runtime Timing
        # ----------------------------------------------------------------------

        self._started_at: Optional[
            float
        ] = None

        self._finished_at: Optional[
            float
        ] = None

        self._last_enter: Optional[
            float
        ] = None

        self._last_exit: Optional[
            float
        ] = None

        self._last_callback: Optional[
            float
        ] = None

        self._last_hook: Optional[
            float
        ] = None

        self._duration: float = 0.0

        # ----------------------------------------------------------------------
        # Runtime Counters
        # ----------------------------------------------------------------------

        self._enter_count: int = 0

        self._exit_count: int = 0

        self._callback_count: int = 0

        self._hook_count: int = 0

        self._exception_count: int = 0

        # ----------------------------------------------------------------------
        # Current Runtime Objects
        # ----------------------------------------------------------------------

        #
        # Root trace created by this scope.
        #

        self._trace: Optional[
            TraceSpan
        ] = None

        #
        # Current active span.
        #

        self._active_span: Optional[
            TraceSpan
        ] = None

        #
        # Current exception captured by __exit__().
        #

        self._exception: Optional[
            BaseException
        ] = None

        #
        # Current traceback captured by __exit__().
        #

        self._traceback: Optional[
            TracebackType
        ] = None

        # ----------------------------------------------------------------------
        # Thread Runtime
        # ----------------------------------------------------------------------

        self._thread_id: int = threading.get_ident()

        self._owner_thread: int = (
            self._thread_id
        )

        # ----------------------------------------------------------------------
        # Initialization
        # ----------------------------------------------------------------------

        self._initialized = True

        self._state = (
            ScopeState.INITIALIZED
        )

        # ----------------------------------------------------------------------
        # Logger
        # ----------------------------------------------------------------------

        logger.debug(

            "TraceScope runtime initialized "

            "(state=%s)",

            self._state.value,

        )
# ==============================================================================
# Part 2.7 – Statistics
# ==============================================================================

        #
        # Runtime statistics
        #

        self._statistics: TraceScopeStatistics = (
            TraceScopeStatistics()
        )

        #
        # Counters
        #

        self._enter_count: int = 0

        self._exit_count: int = 0

        self._success_count: int = 0

        self._failure_count: int = 0

        self._exception_count: int = 0

        self._cancelled_count: int = 0

        self._nested_count: int = 0

        self._reentrant_count: int = 0

        #
        # Timing
        #

        self._total_duration: float = 0.0

        self._last_duration: float = 0.0

        self._minimum_duration: float = 0.0

        self._maximum_duration: float = 0.0

        self._average_duration: float = 0.0

        #
        # Runtime timestamps
        #

        self._last_enter: Optional[float] = None

        self._last_exit: Optional[float] = None

        self._last_success: Optional[float] = None

        self._last_failure: Optional[float] = None

        self._last_exception: Optional[float] = None

        #
        # Internal runtime values
        #

        self._enter_timestamp: Optional[float] = None

        self._exit_timestamp: Optional[float] = None

        self._current_duration: float = 0.0
# ==============================================================================
# Part 2.8 – Metadata
# ==============================================================================

        # ----------------------------------------------------------------------
        # User Metadata
        # ----------------------------------------------------------------------

        self._metadata: ScopeMetadata = (
            copy.deepcopy(metadata)
            if metadata is not None
            else {}
        )

        # ----------------------------------------------------------------------
        # User Attributes
        # ----------------------------------------------------------------------

        self._attributes: ScopeAttributes = (
            copy.deepcopy(attributes)
            if attributes is not None
            else {}
        )

        # ----------------------------------------------------------------------
        # User Context
        # ----------------------------------------------------------------------

        self._context: ScopeContext = (
            copy.deepcopy(context)
            if context is not None
            else {}
        )

        # ----------------------------------------------------------------------
        # Tags
        # ----------------------------------------------------------------------

        self._tags: set[str] = set()

        # ----------------------------------------------------------------------
        # Labels
        # ----------------------------------------------------------------------

        self._labels: dict[
            str,
            str,
        ] = {}

        # ----------------------------------------------------------------------
        # User Data
        # ----------------------------------------------------------------------

        self._user_data: dict[
            str,
            Any,
        ] = {}

        # ----------------------------------------------------------------------
        # Notes
        # ----------------------------------------------------------------------

        self._notes: list[str] = []

        # ----------------------------------------------------------------------
        # History
        # ----------------------------------------------------------------------

        self._history: deque[
            ScopeRecord
        ] = deque(
            maxlen=self._history_limit,
        )

        # ----------------------------------------------------------------------
        # Runtime Cache
        # ----------------------------------------------------------------------

        self._cache: dict[
            str,
            Any,
        ] = {}

        # ----------------------------------------------------------------------
        # Arbitrary Runtime Storage
        # ----------------------------------------------------------------------

        self._runtime_data: dict[
            str,
            Any,
        ] = {}

        # ----------------------------------------------------------------------
        # Extra Properties
        # ----------------------------------------------------------------------

        self._properties: dict[
            str,
            Any,
        ] = {}

        # ----------------------------------------------------------------------
        # Extension Data
        # ----------------------------------------------------------------------

        self._extensions: dict[
            str,
            Any,
        ] = {}

        # ----------------------------------------------------------------------
        # Audit Information
        # ----------------------------------------------------------------------

        self._audit: dict[
            str,
            Any,
        ] = {
            "created_by": None,
            "updated_by": None,
            "created_at": self._created_at,
            "updated_at": self._updated_at,
        }
# ==============================================================================
# Part 2.9 – Runtime Objects
# ==============================================================================

        # ----------------------------------------------------------------------
        # Thread Synchronization
        # ----------------------------------------------------------------------

        self._lock: threading.RLock = (
            threading.RLock()
        )

        self._thread_local = (
            threading.local()
        )

        # ----------------------------------------------------------------------
        # Logger
        # ----------------------------------------------------------------------

        self._logger = logging.getLogger(
            LOGGER_NAME,
        )

        # ----------------------------------------------------------------------
        # Hooks
        # ----------------------------------------------------------------------

        self._hooks: dict[
            HookName,
            list[ScopeHook],
        ] = defaultdict(
            list,
        )

        # ----------------------------------------------------------------------
        # Callbacks
        # ----------------------------------------------------------------------

        self._callbacks: list[
            ScopeCallback
        ] = []

        # ----------------------------------------------------------------------
        # Filters
        # ----------------------------------------------------------------------

        self._filters: list[
            ScopeFilter
        ] = []

        # ----------------------------------------------------------------------
        # Event Subscribers
        # ----------------------------------------------------------------------

        self._subscribers: dict[
            str,
            list[ScopeCallback],
        ] = defaultdict(
            list,
        )

        # ----------------------------------------------------------------------
        # Runtime Flags
        # ----------------------------------------------------------------------

        self._disposed: bool = False

        self._entered: bool = False

        self._exited: bool = False

        self._exception: BaseException | None = None

        # ----------------------------------------------------------------------
        # Active Objects
        # ----------------------------------------------------------------------

        self._trace: TraceSpan | None = None

        self._span: TraceSpan | None = None

        self._parent_span: TraceSpan | None = None

        # ----------------------------------------------------------------------
        # Timing
        # ----------------------------------------------------------------------

        self._start_time: float | None = None

        self._end_time: float | None = None

        self._duration: float = 0.0

        # ----------------------------------------------------------------------
        # Runtime Identifiers
        # ----------------------------------------------------------------------

        self._thread_id: int | None = None

        self._process_id: int | None = None

        # ----------------------------------------------------------------------
        # Final Initialization
        # ----------------------------------------------------------------------

        self._initialized = True

        self._state = ScopeState.INITIALIZED

        self._logger.debug(

            "%s '%s' initialized.",

            self.__class__.__name__,

            self._name,

        )
# ==============================================================================
# Part 2.10 – Final Initialization
# ==============================================================================

        # ----------------------------------------------------------------------
        # Validate Configuration
        # ----------------------------------------------------------------------

        self.validate()

        # ----------------------------------------------------------------------
        # Initialize Runtime State
        # ----------------------------------------------------------------------

        self._initialized = True

        self._running = False

        self._active = False

        self._entered = False

        self._finished = False

        self._cancelled = False

        self._disposed = False

        self._state = ScopeState.INITIALIZED

        self._status = ScopeStatus.READY

        # ----------------------------------------------------------------------
        # Initialize Statistics
        # ----------------------------------------------------------------------

        self._statistics.created_at = (
            self._created_at
        )

        self._statistics.updated_at = (
            self._updated_at
        )

        # ----------------------------------------------------------------------
        # Initialize Thread Information
        # ----------------------------------------------------------------------

        self._thread_id = threading.get_ident()

        self._owner_thread = (
            self._thread_id
        )

        self._process_id = os.getpid()

        # ----------------------------------------------------------------------
        # Initialize Runtime Cache
        # ----------------------------------------------------------------------

        self._cache.clear()

        self._runtime_data.clear()

        # ----------------------------------------------------------------------
        # Notify Hooks
        # ----------------------------------------------------------------------

        initialize_hook = getattr(
            self,
            "notify_hooks",
            None,
        )

        if callable(
            initialize_hook,
        ):

            initialize_hook(
                "initialize",
                self,
            )

        # ----------------------------------------------------------------------
        # Notify Callbacks
        # ----------------------------------------------------------------------

        callback_notify = getattr(
            self,
            "notify_callbacks",
            None,
        )

        if callable(
            callback_notify,
        ):

            callback_notify(
                "initialize",
                self,
            )

        # ----------------------------------------------------------------------
        # Logging
        # ----------------------------------------------------------------------

        self._logger.debug(

            "%s '%s' successfully initialized.",

            self.__class__.__name__,

            self._name,

        )
# ==============================================================================
# Part 3. TraceScope Properties
# ==============================================================================

# ==============================================================================
# Part 3.1 – Identity
# ==============================================================================

@property
def id(self) -> str:
    """
    Unique scope identifier.
    """
    return self._id


# ------------------------------------------------------------------------------

@property
def uuid(self) -> uuid.UUID:
    """
    UUID object of this scope.
    """
    return self._uuid


# ------------------------------------------------------------------------------

@property
def name(self) -> str:
    """
    Scope name.
    """
    return self._name


@name.setter
def name(
    self,
    value: str,
) -> None:
    """
    Update scope name.
    """
    self._name = str(value)

    self.touch()


# ------------------------------------------------------------------------------

@property
def description(self) -> str:
    """
    Scope description.
    """
    return self._description


@description.setter
def description(
    self,
    value: str,
) -> None:
    """
    Update scope description.
    """
    self._description = str(value)

    self.touch()


# ------------------------------------------------------------------------------

@property
def version(self) -> str:
    """
    Scope version.
    """
    return self._version


# ------------------------------------------------------------------------------

@property
def scope_type(self) -> ScopeType:
    """
    Scope implementation type.
    """
    return self._scope_type
# ==============================================================================
# Part 3.2 – Components
# ==============================================================================

@property
def manager(self) -> TraceManager:
    """
    Associated TraceManager.

    Returns
    -------
    TraceManager
    """
    return self._manager


# ------------------------------------------------------------------------------

@property
def tracer(self) -> TraceTracer:
    """
    Associated TraceTracer.

    Returns
    -------
    TraceTracer
    """
    return self._tracer


# ------------------------------------------------------------------------------

@property
def trace(self) -> Optional[TraceSpan]:
    """
    Root trace started by this scope.

    Returns
    -------
    Optional[TraceSpan]
    """
    return self._trace


# ------------------------------------------------------------------------------

@property
def span(self) -> Optional[TraceSpan]:
    """
    Active span owned by this scope.

    Returns
    -------
    Optional[TraceSpan]
    """
    return self._span


# ------------------------------------------------------------------------------

@property
def parent_span(self) -> Optional[TraceSpan]:
    """
    Parent span of the active span.

    Returns
    -------
    Optional[TraceSpan]
    """
    return self._parent_span
# ==============================================================================
# Part 3.3 – Configuration
# ==============================================================================

@property
def enabled(self) -> bool:
    """
    Whether this scope is enabled.

    Returns
    -------
    bool
    """
    return self._enabled


@enabled.setter
def enabled(
    self,
    value: bool,
) -> None:
    """
    Enable or disable the scope.
    """
    self._enabled = bool(value)

    self.touch()


# ------------------------------------------------------------------------------

@property
def auto_start(self) -> bool:
    """
    Automatically start tracing when entering
    the scope.

    Returns
    -------
    bool
    """
    return self._auto_start


@auto_start.setter
def auto_start(
    self,
    value: bool,
) -> None:
    """
    Enable or disable automatic trace start.
    """
    self._auto_start = bool(value)

    self.touch()


# ------------------------------------------------------------------------------

@property
def auto_finish(self) -> bool:
    """
    Automatically finish tracing when leaving
    the scope.

    Returns
    -------
    bool
    """
    return self._auto_finish


@auto_finish.setter
def auto_finish(
    self,
    value: bool,
) -> None:
    """
    Enable or disable automatic trace finish.
    """
    self._auto_finish = bool(value)

    self.touch()


# ------------------------------------------------------------------------------

@property
def timeout(self) -> float:
    """
    Scope timeout in seconds.

    Returns
    -------
    float
    """
    return self._timeout


@timeout.setter
def timeout(
    self,
    value: float,
) -> None:
    """
    Set runtime timeout.

    Raises
    ------
    ValueError
        If timeout is negative.
    """
    value = float(value)

    if value < 0.0:

        raise ValueError(
            "timeout must be >= 0."
        )

    self._timeout = value

    self.touch()


# ------------------------------------------------------------------------------

@property
def history_limit(self) -> int:
    """
    Maximum history capacity.

    Returns
    -------
    int
    """
    return self._history_limit


@history_limit.setter
def history_limit(
    self,
    value: int,
) -> None:
    """
    Set history limit.

    Raises
    ------
    ValueError
        If limit is smaller than one.
    """
    value = int(value)

    if value < 1:

        raise ValueError(
            "history_limit must be >= 1."
        )

    self._history_limit = value

    self.touch()


# ------------------------------------------------------------------------------

@property
def encoding(self) -> str:
    """
    Default serialization encoding.

    Returns
    -------
    str
    """
    return self._encoding


@encoding.setter
def encoding(
    self,
    value: str,
) -> None:
    """
    Set default encoding.
    """
    self._encoding = str(value)

    self.touch()


# ------------------------------------------------------------------------------

@property
def options(
    self,
) -> Mapping[str, Any]:
    """
    Runtime configuration options.

    Returns
    -------
    Mapping[str, Any]
    """
    return self._options
# ==============================================================================
# Part 3.4 – Runtime State
# ==============================================================================

@property
def initialized(self) -> bool:
    """
    Whether the scope has been initialized.
    """
    return self._initialized


# ------------------------------------------------------------------------------

@property
def running(self) -> bool:
    """
    Whether the scope is currently running.
    """
    return self._running


# ------------------------------------------------------------------------------

@property
def active(self) -> bool:
    """
    Whether the scope is currently active.
    """
    return self._active


# ------------------------------------------------------------------------------

@property
def entered(self) -> bool:
    """
    Whether __enter__() has been executed.
    """
    return self._entered


# ------------------------------------------------------------------------------

@property
def exited(self) -> bool:
    """
    Whether __exit__() has completed.
    """
    return self._exited


# ------------------------------------------------------------------------------

@property
def frozen(self) -> bool:
    """
    Whether the scope is frozen.
    """
    return self._frozen


# ------------------------------------------------------------------------------

@property
def closed(self) -> bool:
    """
    Whether the scope has been closed.
    """
    return self._closed


# ------------------------------------------------------------------------------

@property
def disposed(self) -> bool:
    """
    Whether runtime resources have been disposed.
    """
    return self._disposed


# ------------------------------------------------------------------------------

@property
def state(self) -> ScopeState:
    """
    Current runtime state.
    """
    return self._state


# ------------------------------------------------------------------------------

@property
def status(self) -> ScopeStatus:
    """
    Current runtime status.
    """
    return self._status


# ------------------------------------------------------------------------------

@property
def created_at(self) -> float:
    """
    Creation timestamp.
    """
    return self._created_at


# ------------------------------------------------------------------------------

@property
def updated_at(self) -> float:
    """
    Last update timestamp.
    """
    return self._updated_at


# ------------------------------------------------------------------------------

@property
def start_time(self) -> Optional[float]:
    """
    Scope start timestamp.
    """
    return self._start_time


# ------------------------------------------------------------------------------

@property
def end_time(self) -> Optional[float]:
    """
    Scope end timestamp.
    """
    return self._end_time


# ------------------------------------------------------------------------------

@property
def duration(self) -> float:
    """
    Latest measured execution duration.

    Returns
    -------
    float
        Duration in seconds.
    """
    return self._duration


# ------------------------------------------------------------------------------

@property
def uptime(self) -> float:
    """
    Lifetime of the scope.

    If the scope has already finished, the lifetime is
    measured from creation until exit. Otherwise it is
    measured until the current time.

    Returns
    -------
    float
        Lifetime in seconds.
    """

    if self._end_time is not None:

        return max(
            0.0,
            self._end_time - self._created_at,
        )

    return max(
        0.0,
        time.time() - self._created_at,
    )
# ==============================================================================
# Part 3.5 – Statistics
# ==============================================================================

@property
def statistics(
    self,
) -> TraceScopeStatistics:
    """
    Runtime statistics.

    Returns
    -------
    TraceScopeStatistics
    """
    return self._statistics


# ------------------------------------------------------------------------------

@property
def enter_count(self) -> int:
    """
    Number of successful __enter__() calls.

    Returns
    -------
    int
    """
    return self._enter_count


# ------------------------------------------------------------------------------

@property
def exit_count(self) -> int:
    """
    Number of completed __exit__() calls.

    Returns
    -------
    int
    """
    return self._exit_count


# ------------------------------------------------------------------------------

@property
def success_count(self) -> int:
    """
    Number of successful scope executions.

    Returns
    -------
    int
    """
    return self._success_count


# ------------------------------------------------------------------------------

@property
def failure_count(self) -> int:
    """
    Number of failed scope executions.

    Returns
    -------
    int
    """
    return self._failure_count


# ------------------------------------------------------------------------------

@property
def exception_count(self) -> int:
    """
    Number of exceptions observed while the
    scope was active.

    Returns
    -------
    int
    """
    return self._exception_count


# ------------------------------------------------------------------------------

@property
def cancelled_count(self) -> int:
    """
    Number of cancelled executions.

    Returns
    -------
    int
    """
    return self._cancelled_count


# ------------------------------------------------------------------------------

@property
def nested_count(self) -> int:
    """
    Number of nested scope entries.

    Returns
    -------
    int
    """
    return self._nested_count


# ------------------------------------------------------------------------------

@property
def reentrant_count(self) -> int:
    """
    Number of reentrant executions.

    Returns
    -------
    int
    """
    return self._reentrant_count


# ------------------------------------------------------------------------------

@property
def average_duration(self) -> float:
    """
    Average execution duration.

    Returns
    -------
    float
        Seconds.
    """
    return self._average_duration


# ------------------------------------------------------------------------------

@property
def minimum_duration(self) -> float:
    """
    Minimum observed execution duration.

    Returns
    -------
    float
        Seconds.
    """
    return self._minimum_duration


# ------------------------------------------------------------------------------

@property
def maximum_duration(self) -> float:
    """
    Maximum observed execution duration.

    Returns
    -------
    float
        Seconds.
    """
    return self._maximum_duration
# ==============================================================================
# Part 3.6 – Metadata
# ==============================================================================

@property
def metadata(
    self,
) -> Mapping[str, Any]:
    """
    User metadata.

    Returns
    -------
    Mapping[str, Any]
    """
    return self._metadata


# ------------------------------------------------------------------------------

@property
def attributes(
    self,
) -> Mapping[str, Any]:
    """
    User-defined attributes.

    Returns
    -------
    Mapping[str, Any]
    """
    return self._attributes


# ------------------------------------------------------------------------------

@property
def context(
    self,
) -> Mapping[str, Any]:
    """
    Context values associated with this scope.

    Returns
    -------
    Mapping[str, Any]
    """
    return self._context


# ------------------------------------------------------------------------------

@property
def tags(
    self,
) -> frozenset[str]:
    """
    Tags assigned to this scope.

    Returns
    -------
    frozenset[str]
    """
    return frozenset(
        self._tags,
    )


# ------------------------------------------------------------------------------

@property
def labels(
    self,
) -> Mapping[str, str]:
    """
    User labels.

    Returns
    -------
    Mapping[str, str]
    """
    return self._labels


# ------------------------------------------------------------------------------

@property
def notes(
    self,
) -> tuple[str, ...]:
    """
    Runtime notes.

    Returns
    -------
    tuple[str, ...]
    """
    return tuple(
        self._notes,
    )


# ------------------------------------------------------------------------------

@property
def history(
    self,
) -> tuple[ScopeRecord, ...]:
    """
    Runtime history records.

    Returns
    -------
    tuple[ScopeRecord, ...]
    """
    return tuple(
        self._history,
    )


# ------------------------------------------------------------------------------

@property
def cache(
    self,
) -> Mapping[str, Any]:
    """
    Runtime cache.

    Returns
    -------
    Mapping[str, Any]
    """
    return self._cache


# ------------------------------------------------------------------------------

@property
def runtime_data(
    self,
) -> Mapping[str, Any]:
    """
    Arbitrary runtime storage.

    Returns
    -------
    Mapping[str, Any]
    """
    return self._runtime_data


# ------------------------------------------------------------------------------

@property
def extensions(
    self,
) -> Mapping[str, Any]:
    """
    Extension-specific data.

    Returns
    -------
    Mapping[str, Any]
    """
    return self._extensions
# ==============================================================================
# Part 3.7 – Runtime Objects
# ==============================================================================

@property
def callbacks(
    self,
) -> tuple[ScopeCallback, ...]:
    """
    Registered callbacks.

    Returns
    -------
    tuple[ScopeCallback, ...]
    """
    return tuple(
        self._callbacks,
    )


# ------------------------------------------------------------------------------

@property
def hooks(
    self,
) -> Mapping[
    str,
    Sequence[ScopeHook],
]:
    """
    Registered hooks.

    Returns
    -------
    Mapping[str, Sequence[ScopeHook]]
    """
    return self._hooks


# ------------------------------------------------------------------------------

@property
def filters(
    self,
) -> tuple[ScopeFilter, ...]:
    """
    Registered runtime filters.

    Returns
    -------
    tuple[ScopeFilter, ...]
    """
    return tuple(
        self._filters,
    )


# ------------------------------------------------------------------------------

@property
def subscribers(
    self,
) -> tuple[ScopeSubscriber, ...]:
    """
    Registered subscribers.

    Returns
    -------
    tuple[ScopeSubscriber, ...]
    """
    return tuple(
        self._subscribers,
    )


# ------------------------------------------------------------------------------

@property
def logger(
    self,
) -> logging.Logger:
    """
    Runtime logger.

    Returns
    -------
    logging.Logger
    """
    return self._logger


# ------------------------------------------------------------------------------

@property
def lock(
    self,
) -> RLock:
    """
    Internal synchronization lock.

    Returns
    -------
    RLock
    """
    return self._lock


# ------------------------------------------------------------------------------

@property
def thread_id(
    self,
) -> int:
    """
    Thread identifier that owns this scope.

    Returns
    -------
    int
    """
    return self._thread_id


# ------------------------------------------------------------------------------

@property
def process_id(
    self,
) -> int:
    """
    Operating-system process identifier.

    Returns
    -------
    int
    """
    return self._process_id
# ==============================================================================
# Part 4.1 – Initialization
# ==============================================================================

def initialize(
    self,
) -> "TraceScope":
    """
    Initialize the runtime scope.

    This method prepares the scope for execution, validates the
    runtime environment, resets transient state, and records the
    initialization timestamp. Calling this method multiple times is
    safe and has no effect after the first successful initialization.

    Returns
    -------
    TraceScope
        The initialized scope instance.

    Raises
    ------
    ScopeClosedError
        If the scope has already been closed.

    ScopeValidationError
        If the runtime configuration is invalid.
    """

    with self._lock:

        if self._closed:

            raise ScopeClosedError(
                "Cannot initialize a closed TraceScope."
            )

        if self._initialized:

            return self

        #
        # ------------------------------------------------------------------
        # Validate configuration
        # ------------------------------------------------------------------
        #

        self.validate()

        #
        # ------------------------------------------------------------------
        # Reset transient runtime state
        # ------------------------------------------------------------------
        #

        self._running = False

        self._active = False

        self._entered = False

        self._exited = False

        self._disposed = False

        self._start_time = None

        self._end_time = None

        self._duration = 0.0

        self._trace = None

        self._span = None

        self._parent_span = None

        self._runtime_data.clear()

        self._cache.clear()

        #
        # ------------------------------------------------------------------
        # Runtime state
        # ------------------------------------------------------------------
        #

        self._initialized = True

        self._state = ScopeState.INITIALIZED

        now = time.time()

        self._updated_at = now

        #
        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------
        #

        if hasattr(
            self._statistics,
            "initialization_count",
        ):
            self._statistics.initialization_count += 1

        if hasattr(
            self._statistics,
            "updated_at",
        ):
            self._statistics.updated_at = now

        #
        # ------------------------------------------------------------------
        # Runtime bookkeeping
        # ------------------------------------------------------------------
        #

        self.touch()

        #
        # ------------------------------------------------------------------
        # Notify lifecycle hooks
        # ------------------------------------------------------------------
        #

        self.notify_hooks(
            "initialize",
            scope=self,
        )

        self.notify_callbacks(
            "initialize",
            scope=self,
        )

        self.notify_subscribers(
            "initialize",
            scope=self,
        )

        #
        # ------------------------------------------------------------------
        # Logging
        # ------------------------------------------------------------------
        #

        self._logger.debug(
            "TraceScope '%s' initialized.",
            self._name,
        )

        return self
# ==============================================================================
# Part 4.2 – Enter
# ==============================================================================

def enter(
    self,
) -> TraceSpan:
    """
    Enter the tracing scope.

    This method starts a new trace or span (depending on the configured
    scope type), updates the runtime state, records timing information,
    invokes lifecycle hooks, and returns the active TraceSpan.

    Returns
    -------
    TraceSpan
        Active span created or activated by this scope.

    Raises
    ------
    ScopeClosedError
        If the scope has been closed.

    ScopeFrozenError
        If the scope is frozen.

    ScopeValidationError
        If the scope configuration is invalid.

    TracerError
        If the underlying tracer fails to create the trace/span.
    """

    with self._lock:

        #
        # ------------------------------------------------------------------
        # Validate runtime state
        # ------------------------------------------------------------------
        #

        if self._closed:

            raise ScopeClosedError(
                "Cannot enter a closed TraceScope."
            )

        if self._frozen:

            raise ScopeFrozenError(
                "Cannot enter a frozen TraceScope."
            )

        if not self._initialized:

            self.initialize()

        self.validate()

        #
        # ------------------------------------------------------------------
        # Prevent duplicate entry
        # ------------------------------------------------------------------
        #

        if self._entered:

            self._statistics.reentrant_count += 1

            if self._trace is not None:

                return self._trace

        #
        # ------------------------------------------------------------------
        # Runtime state
        # ------------------------------------------------------------------
        #

        self._running = True

        self._active = True

        self._entered = True

        self._exited = False

        self._state = ScopeState.RUNNING

        self._start_time = time.time()

        self._updated_at = self._start_time

        #
        # ------------------------------------------------------------------
        # Obtain tracer
        # ------------------------------------------------------------------
        #

        if self._tracer is None:

            if self._manager is None:

                raise ScopeValidationError(
                    "TraceScope requires a manager or tracer."
                )

            self._tracer = self._manager.current_tracer()

        if self._tracer is None:

            raise ScopeValidationError(
                "No active TraceTracer available."
            )

        #
        # ------------------------------------------------------------------
        # Remember parent span
        # ------------------------------------------------------------------
        #

        self._parent_span = (
            self._tracer.current_span()
        )

        #
        # ------------------------------------------------------------------
        # Start trace/span
        # ------------------------------------------------------------------
        #

        if self._scope_type is ScopeType.TRACE:

            self._trace = self._tracer.start_trace(
                name=self._name,
                **copy.deepcopy(
                    self._options,
                ),
            )

        else:

            self._trace = self._tracer.start_span(
                name=self._name,
                parent=self._parent_span,
                **copy.deepcopy(
                    self._options,
                ),
            )

        self._span = self._trace

        #
        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------
        #

        self._statistics.enter_count += 1

        self._statistics.success_count += 1

        self._statistics.updated_at = (
            self._updated_at
        )

        #
        # ------------------------------------------------------------------
        # Runtime bookkeeping
        # ------------------------------------------------------------------
        #

        self.touch()

        self._history.append(

            {
                "event": "enter",
                "timestamp": self._start_time,
                "scope": self._name,
            }

        )

        #
        # ------------------------------------------------------------------
        # Lifecycle notifications
        # ------------------------------------------------------------------
        #

        self.notify_hooks(
            "enter",
            scope=self,
            trace=self._trace,
        )

        self.notify_callbacks(
            "enter",
            scope=self,
            trace=self._trace,
        )

        self.notify_subscribers(
            "enter",
            scope=self,
            trace=self._trace,
        )

        #
        # ------------------------------------------------------------------
        # Logging
        # ------------------------------------------------------------------
        #

        self._logger.debug(
            "TraceScope '%s' entered.",
            self._name,
        )

        return self._trace


# ------------------------------------------------------------------------------

def __enter__(
    self,
) -> TraceSpan:
    """
    Context manager entry.

    Returns
    -------
    TraceSpan
        Active trace/span created by this scope.
    """

    return self.enter()
# ==============================================================================
# Part 4.3 – Exit
# ==============================================================================

def exit(
    self,
    exc_type: Optional[type[BaseException]] = None,
    exc_value: Optional[BaseException] = None,
    traceback: Optional[TracebackType] = None,
) -> bool:
    """
    Exit the tracing scope.

    Finishes the active trace/span, updates runtime state,
    records execution statistics, invokes callbacks/hooks,
    and optionally suppresses exceptions.

    Parameters
    ----------
    exc_type
        Exception type raised inside the scope.

    exc_value
        Exception instance.

    traceback
        Exception traceback.

    Returns
    -------
    bool
        True if the exception should be suppressed,
        otherwise False.
    """

    with self._lock:

        #
        # ------------------------------------------------------------------
        # Ignore duplicate exits
        # ------------------------------------------------------------------
        #

        if self._exited:

            return False

        if not self._entered:

            return False

        end_time = time.time()

        #
        # ------------------------------------------------------------------
        # Runtime timing
        # ------------------------------------------------------------------
        #

        self._end_time = end_time

        self._duration = max(
            0.0,
            end_time - (
                self._start_time
                or end_time
            ),
        )

        self._updated_at = end_time

        #
        # ------------------------------------------------------------------
        # Runtime state
        # ------------------------------------------------------------------
        #

        self._running = False

        self._active = False

        self._entered = False

        self._exited = True

        self._state = ScopeState.IDLE

        #
        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------
        #

        self._statistics.exit_count += 1

        self._statistics.updated_at = end_time

        self._statistics.total_duration += (
            self._duration
        )

        if (
            self._statistics.minimum_duration == 0.0
            or self._duration
            < self._statistics.minimum_duration
        ):

            self._statistics.minimum_duration = (
                self._duration
            )

        self._statistics.maximum_duration = max(
            self._statistics.maximum_duration,
            self._duration,
        )

        if self._statistics.exit_count > 0:

            self._statistics.average_duration = (
                self._statistics.total_duration
                / self._statistics.exit_count
            )

        #
        # ------------------------------------------------------------------
        # Exception handling
        # ------------------------------------------------------------------
        #

        if exc_type is None:

            self._statistics.success_count += 1

        else:

            self._statistics.failure_count += 1

            self._statistics.exception_count += 1

            self._history.append(

                {
                    "event": "exception",
                    "type": exc_type.__name__,
                    "message": str(exc_value),
                    "timestamp": end_time,
                }

            )

        #
        # ------------------------------------------------------------------
        # Finish tracing
        # ------------------------------------------------------------------
        #

        try:

            if (
                self._tracer is not None
                and self._trace is not None
            ):

                if self._scope_type is ScopeType.TRACE:

                    self._tracer.end_trace()

                else:

                    self._tracer.end_span(
                        self._trace,
                    )

        finally:

            self._trace = None

            self._span = None

            self._parent_span = None

        #
        # ------------------------------------------------------------------
        # History
        # ------------------------------------------------------------------
        #

        self._history.append(

            {
                "event": "exit",
                "timestamp": end_time,
                "duration": self._duration,
            }

        )

        #
        # ------------------------------------------------------------------
        # Runtime bookkeeping
        # ------------------------------------------------------------------
        #

        self.touch()

        #
        # ------------------------------------------------------------------
        # Notifications
        # ------------------------------------------------------------------
        #

        self.notify_hooks(
            "exit",
            scope=self,
            exception=exc_value,
        )

        self.notify_callbacks(
            "exit",
            scope=self,
            exception=exc_value,
        )

        self.notify_subscribers(
            "exit",
            scope=self,
            exception=exc_value,
        )

        #
        # ------------------------------------------------------------------
        # Logging
        # ------------------------------------------------------------------
        #

        if exc_type is None:

            self._logger.debug(
                "TraceScope '%s' exited successfully.",
                self._name,
            )

        else:

            self._logger.exception(
                "TraceScope '%s' exited with exception.",
                self._name,
                exc_info=(
                    exc_type,
                    exc_value,
                    traceback,
                ),
            )

        #
        # ------------------------------------------------------------------
        # Never suppress exceptions by default
        # ------------------------------------------------------------------
        #

        return False


# ------------------------------------------------------------------------------

def __exit__(
    self,
    exc_type: Optional[type[BaseException]],
    exc_value: Optional[BaseException],
    traceback: Optional[TracebackType],
) -> bool:
    """
    Context-manager exit.

    Parameters
    ----------
    exc_type
        Raised exception type.

    exc_value
        Raised exception.

    traceback
        Exception traceback.

    Returns
    -------
    bool
        Whether the exception should be suppressed.
    """

    return self.exit(
        exc_type,
        exc_value,
        traceback,
    )
# ==============================================================================
# Part 4.4 – Start
# ==============================================================================

def start(
    self,
) -> TraceSpan:
    """
    Start this tracing scope.

    This is an alias of :meth:`enter`.

    Returns
    -------
    TraceSpan
        Active trace/span.

    Raises
    ------
    ScopeClosedError
        If the scope has been closed.

    ScopeFrozenError
        If the scope is frozen.

    ScopeValidationError
        If the scope configuration is invalid.

    TracerError
        If the underlying tracer cannot create
        the trace/span.
    """

    return self.enter()


# ------------------------------------------------------------------------------

def begin(
    self,
) -> TraceSpan:
    """
    Begin this tracing scope.

    This is a convenience alias of :meth:`start`.

    Returns
    -------
    TraceSpan
        Active trace/span.
    """

    return self.start()
# ==============================================================================
# Part 4.5 – Stop
# ==============================================================================

def stop(
    self,
) -> "TraceScope":
    """
    Stop this tracing scope.

    This method is the runtime equivalent of leaving
    a context-managed scope.

    Returns
    -------
    TraceScope
        Current scope.
    """

    self.exit()

    return self


# ------------------------------------------------------------------------------

def finish(
    self,
) -> "TraceScope":
    """
    Finish this tracing scope.

    Alias of :meth:`stop`.

    Returns
    -------
    TraceScope
        Current scope.
    """

    return self.stop()


# ------------------------------------------------------------------------------

def end(
    self,
) -> "TraceScope":
    """
    End this tracing scope.

    Alias of :meth:`finish`.

    Returns
    -------
    TraceScope
        Current scope.
    """

    return self.finish()
# ==============================================================================
# Part 4.6 – Cancel
# ==============================================================================

def cancel(
    self,
    reason: Optional[str] = None,
) -> "TraceScope":
    """
    Cancel the current tracing scope.

    Unlike :meth:`stop`, a cancelled scope is treated
    as an aborted execution and updates cancellation
    statistics.

    Parameters
    ----------
    reason
        Optional cancellation reason.

    Returns
    -------
    TraceScope
        Current scope.
    """

    with self._lock:

        if self._closed:

            return self

        now = time.time()

        #
        # ------------------------------------------------------------------
        # Runtime state
        # ------------------------------------------------------------------
        #

        self._active = False

        self._running = False

        self._cancelled = True

        self._updated_at = now

        self._state = ScopeState.CANCELLED

        #
        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------
        #

        self._statistics.cancelled_count += 1

        self._statistics.updated_at = now

        #
        # ------------------------------------------------------------------
        # Metadata
        # ------------------------------------------------------------------
        #

        if reason is not None:

            self._metadata[
                "cancel_reason"
            ] = str(reason)

        #
        # ------------------------------------------------------------------
        # History
        # ------------------------------------------------------------------
        #

        self._history.append(

            {
                "event": "cancel",
                "reason": reason,
                "timestamp": now,
            }

        )

        #
        # ------------------------------------------------------------------
        # Notifications
        # ------------------------------------------------------------------
        #

        self.notify_hooks(

            "cancel",

            scope=self,

            reason=reason,

        )

        self.notify_callbacks(

            "cancel",

            scope=self,

            reason=reason,

        )

        self.notify_subscribers(

            "cancel",

            scope=self,

            reason=reason,

        )

        #
        # ------------------------------------------------------------------
        # Logging
        # ------------------------------------------------------------------
        #

        self._logger.warning(

            "TraceScope '%s' cancelled.",

            self._name,

        )

    #
    # Finish runtime cleanup.
    #

    self.exit()

    return self


# ------------------------------------------------------------------------------

def abort(
    self,
    reason: Optional[str] = None,
) -> "TraceScope":
    """
    Abort this tracing scope.

    Alias of :meth:`cancel`.

    Parameters
    ----------
    reason
        Abort reason.

    Returns
    -------
    TraceScope
        Current scope.
    """

    return self.cancel(
        reason=reason,
    )
# ==============================================================================
# Part 4.7 – Freeze
# ==============================================================================

def freeze(
    self,
) -> "TraceScope":
    """
    Freeze this tracing scope.

    A frozen scope cannot be entered, started, or modified until
    :meth:`unfreeze` is called.

    Returns
    -------
    TraceScope
        Current scope.

    Raises
    ------
    ScopeClosedError
        If the scope has already been closed.
    """

    with self._lock:

        if self._closed:

            raise ScopeClosedError(
                "Cannot freeze a closed TraceScope."
            )

        if self._frozen:

            return self

        now = time.time()

        #
        # ------------------------------------------------------------------
        # Runtime state
        # ------------------------------------------------------------------
        #

        self._frozen = True

        self._state = ScopeState.FROZEN

        self._updated_at = now

        #
        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------
        #

        if hasattr(
            self._statistics,
            "freeze_count",
        ):
            self._statistics.freeze_count += 1

        self._statistics.updated_at = now

        #
        # ------------------------------------------------------------------
        # History
        # ------------------------------------------------------------------
        #

        self._history.append(

            {
                "event": "freeze",
                "timestamp": now,
            }

        )

        #
        # ------------------------------------------------------------------
        # Runtime bookkeeping
        # ------------------------------------------------------------------
        #

        self.touch()

        #
        # ------------------------------------------------------------------
        # Notifications
        # ------------------------------------------------------------------
        #

        self.notify_hooks(
            "freeze",
            scope=self,
        )

        self.notify_callbacks(
            "freeze",
            scope=self,
        )

        self.notify_subscribers(
            "freeze",
            scope=self,
        )

        #
        # ------------------------------------------------------------------
        # Logging
        # ------------------------------------------------------------------
        #

        self._logger.debug(
            "TraceScope '%s' frozen.",
            self._name,
        )

        return self


# ------------------------------------------------------------------------------

def unfreeze(
    self,
) -> "TraceScope":
    """
    Unfreeze this tracing scope.

    Returns
    -------
    TraceScope
        Current scope.

    Raises
    ------
    ScopeClosedError
        If the scope has already been closed.
    """

    with self._lock:

        if self._closed:

            raise ScopeClosedError(
                "Cannot unfreeze a closed TraceScope."
            )

        if not self._frozen:

            return self

        now = time.time()

        #
        # ------------------------------------------------------------------
        # Runtime state
        # ------------------------------------------------------------------
        #

        self._frozen = False

        self._state = (

            ScopeState.RUNNING

            if self._running

            else ScopeState.IDLE

        )

        self._updated_at = now

        #
        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------
        #

        if hasattr(
            self._statistics,
            "unfreeze_count",
        ):
            self._statistics.unfreeze_count += 1

        self._statistics.updated_at = now

        #
        # ------------------------------------------------------------------
        # History
        # ------------------------------------------------------------------
        #

        self._history.append(

            {
                "event": "unfreeze",
                "timestamp": now,
            }

        )

        #
        # ------------------------------------------------------------------
        # Runtime bookkeeping
        # ------------------------------------------------------------------
        #

        self.touch()

        #
        # ------------------------------------------------------------------
        # Notifications
        # ------------------------------------------------------------------
        #

        self.notify_hooks(
            "unfreeze",
            scope=self,
        )

        self.notify_callbacks(
            "unfreeze",
            scope=self,
        )

        self.notify_subscribers(
            "unfreeze",
            scope=self,
        )

        #
        # ------------------------------------------------------------------
        # Logging
        # ------------------------------------------------------------------
        #

        self._logger.debug(
            "TraceScope '%s' unfrozen.",
            self._name,
        )

        return self
# ==============================================================================
# Part 4.8 – Enable
# ==============================================================================

def enable(
    self,
) -> "TraceScope":
    """
    Enable this tracing scope.

    Once enabled, the scope may participate in tracing operations
    again. Calling this method multiple times is safe.

    Returns
    -------
    TraceScope
        Current scope.

    Raises
    ------
    ScopeClosedError
        If the scope has already been closed.
    """

    with self._lock:

        if self._closed:

            raise ScopeClosedError(
                "Cannot enable a closed TraceScope."
            )

        if self._enabled:

            return self

        now = time.time()

        #
        # ------------------------------------------------------------------
        # Runtime state
        # ------------------------------------------------------------------
        #

        self._enabled = True

        if self._state == ScopeState.DISABLED:

            self._state = (

                ScopeState.RUNNING

                if self._running

                else ScopeState.IDLE

            )

        self._updated_at = now

        #
        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------
        #

        if hasattr(
            self._statistics,
            "enable_count",
        ):
            self._statistics.enable_count += 1

        self._statistics.updated_at = now

        #
        # ------------------------------------------------------------------
        # History
        # ------------------------------------------------------------------
        #

        self._history.append(

            {
                "event": "enable",
                "timestamp": now,
            }

        )

        #
        # ------------------------------------------------------------------
        # Runtime bookkeeping
        # ------------------------------------------------------------------
        #

        self.touch()

        #
        # ------------------------------------------------------------------
        # Notifications
        # ------------------------------------------------------------------
        #

        self.notify_hooks(
            "enable",
            scope=self,
        )

        self.notify_callbacks(
            "enable",
            scope=self,
        )

        self.notify_subscribers(
            "enable",
            scope=self,
        )

        #
        # ------------------------------------------------------------------
        # Logging
        # ------------------------------------------------------------------
        #

        self._logger.debug(
            "TraceScope '%s' enabled.",
            self._name,
        )

        return self


# ------------------------------------------------------------------------------

def disable(
    self,
) -> "TraceScope":
    """
    Disable this tracing scope.

    A disabled scope cannot create new traces or spans until
    :meth:`enable` is called.

    Returns
    -------
    TraceScope
        Current scope.

    Raises
    ------
    ScopeClosedError
        If the scope has already been closed.
    """

    with self._lock:

        if self._closed:

            raise ScopeClosedError(
                "Cannot disable a closed TraceScope."
            )

        if not self._enabled:

            return self

        now = time.time()

        #
        # ------------------------------------------------------------------
        # Runtime state
        # ------------------------------------------------------------------
        #

        self._enabled = False

        self._active = False

        self._running = False

        self._state = ScopeState.DISABLED

        self._updated_at = now

        #
        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------
        #

        if hasattr(
            self._statistics,
            "disable_count",
        ):
            self._statistics.disable_count += 1

        self._statistics.updated_at = now

        #
        # ------------------------------------------------------------------
        # History
        # ------------------------------------------------------------------
        #

        self._history.append(

            {
                "event": "disable",
                "timestamp": now,
            }

        )

        #
        # ------------------------------------------------------------------
        # Runtime bookkeeping
        # ------------------------------------------------------------------
        #

        self.touch()

        #
        # ------------------------------------------------------------------
        # Notifications
        # ------------------------------------------------------------------
        #

        self.notify_hooks(
            "disable",
            scope=self,
        )

        self.notify_callbacks(
            "disable",
            scope=self,
        )

        self.notify_subscribers(
            "disable",
            scope=self,
        )

        #
        # ------------------------------------------------------------------
        # Logging
        # ------------------------------------------------------------------
        #

        self._logger.debug(
            "TraceScope '%s' disabled.",
            self._name,
        )

        return self
# ==============================================================================
# Part 4.9 – Activate
# ==============================================================================

def activate(
    self,
) -> "TraceScope":
    """
    Activate this tracing scope.

    Activation marks the scope as the current runtime scope without
    creating a new trace.

    Returns
    -------
    TraceScope
        Current scope.

    Raises
    ------
    ScopeClosedError
        If the scope has already been closed.

    ScopeFrozenError
        If the scope is frozen.
    """

    with self._lock:

        if self._closed:

            raise ScopeClosedError(
                "Cannot activate a closed TraceScope."
            )

        if self._frozen:

            raise ScopeFrozenError(
                "Cannot activate a frozen TraceScope."
            )

        if not self._enabled:

            raise ScopeValidationError(
                "Cannot activate a disabled TraceScope."
            )

        if self._active:

            return self

        now = time.time()

        #
        # ------------------------------------------------------------------
        # Runtime state
        # ------------------------------------------------------------------
        #

        self._active = True

        self._running = True

        self._state = ScopeState.RUNNING

        self._updated_at = now

        #
        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------
        #

        if hasattr(
            self._statistics,
            "activation_count",
        ):
            self._statistics.activation_count += 1

        self._statistics.updated_at = now

        #
        # ------------------------------------------------------------------
        # Runtime bookkeeping
        # ------------------------------------------------------------------
        #

        self.touch()

        self._history.append(

            {
                "event": "activate",
                "timestamp": now,
            }

        )

        #
        # ------------------------------------------------------------------
        # Notifications
        # ------------------------------------------------------------------
        #

        self.notify_hooks(
            "activate",
            scope=self,
        )

        self.notify_callbacks(
            "activate",
            scope=self,
        )

        self.notify_subscribers(
            "activate",
            scope=self,
        )

        #
        # ------------------------------------------------------------------
        # Logging
        # ------------------------------------------------------------------
        #

        self._logger.debug(
            "TraceScope '%s' activated.",
            self._name,
        )

        return self


# ------------------------------------------------------------------------------

def deactivate(
    self,
) -> "TraceScope":
    """
    Deactivate this tracing scope.

    Deactivation removes the scope from the active runtime state
    without disabling or closing it.

    Returns
    -------
    TraceScope
        Current scope.

    Raises
    ------
    ScopeClosedError
        If the scope has already been closed.
    """

    with self._lock:

        if self._closed:

            raise ScopeClosedError(
                "Cannot deactivate a closed TraceScope."
            )

        if not self._active:

            return self

        now = time.time()

        #
        # ------------------------------------------------------------------
        # Runtime state
        # ------------------------------------------------------------------
        #

        self._active = False

        self._running = False

        self._state = ScopeState.IDLE

        self._updated_at = now

        #
        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------
        #

        if hasattr(
            self._statistics,
            "deactivation_count",
        ):
            self._statistics.deactivation_count += 1

        self._statistics.updated_at = now

        #
        # ------------------------------------------------------------------
        # Runtime bookkeeping
        # ------------------------------------------------------------------
        #

        self.touch()

        self._history.append(

            {
                "event": "deactivate",
                "timestamp": now,
            }

        )

        #
        # ------------------------------------------------------------------
        # Notifications
        # ------------------------------------------------------------------
        #

        self.notify_hooks(
            "deactivate",
            scope=self,
        )

        self.notify_callbacks(
            "deactivate",
            scope=self,
        )

        self.notify_subscribers(
            "deactivate",
            scope=self,
        )

        #
        # ------------------------------------------------------------------
        # Logging
        # ------------------------------------------------------------------
        #

        self._logger.debug(
            "TraceScope '%s' deactivated.",
            self._name,
        )

        return self
# ==============================================================================
# Part 4.10 – Close
# ==============================================================================

def close(
    self,
) -> "TraceScope":
    """
    Close this tracing scope.

    Closing releases runtime resources and prevents further tracing
    operations until :meth:`reopen` is called.

    Returns
    -------
    TraceScope
        Current scope.
    """

    with self._lock:

        if self._closed:

            return self

        #
        # ------------------------------------------------------------------
        # Stop active execution
        # ------------------------------------------------------------------
        #

        if self._active:

            self.deactivate()

        now = time.time()

        #
        # ------------------------------------------------------------------
        # Runtime state
        # ------------------------------------------------------------------
        #

        self._closed = True

        self._running = False

        self._active = False

        self._enabled = False

        self._initialized = False

        self._disposed = True

        self._state = ScopeState.CLOSED

        self._updated_at = now

        #
        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------
        #

        if hasattr(
            self._statistics,
            "close_count",
        ):
            self._statistics.close_count += 1

        self._statistics.updated_at = now

        #
        # ------------------------------------------------------------------
        # History
        # ------------------------------------------------------------------
        #

        self._history.append(

            {
                "event": "close",
                "timestamp": now,
            }

        )

        #
        # ------------------------------------------------------------------
        # Release runtime resources
        # ------------------------------------------------------------------
        #

        self._trace = None

        self._span = None

        self._parent_span = None

        self._cache.clear()

        self._runtime_data.clear()

        #
        # ------------------------------------------------------------------
        # Notifications
        # ------------------------------------------------------------------
        #

        self.notify_hooks(
            "close",
            scope=self,
        )

        self.notify_callbacks(
            "close",
            scope=self,
        )

        self.notify_subscribers(
            "close",
            scope=self,
        )

        #
        # ------------------------------------------------------------------
        # Logging
        # ------------------------------------------------------------------
        #

        self._logger.debug(
            "TraceScope '%s' closed.",
            self._name,
        )

        return self


# ------------------------------------------------------------------------------

def reopen(
    self,
) -> "TraceScope":
    """
    Reopen a previously closed tracing scope.

    Returns
    -------
    TraceScope
        Current scope.
    """

    with self._lock:

        if not self._closed:

            return self

        now = time.time()

        #
        # ------------------------------------------------------------------
        # Runtime state
        # ------------------------------------------------------------------
        #

        self._closed = False

        self._disposed = False

        self._enabled = True

        self._initialized = True

        self._running = False

        self._active = False

        self._state = ScopeState.IDLE

        self._updated_at = now

        #
        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------
        #

        if hasattr(
            self._statistics,
            "reopen_count",
        ):
            self._statistics.reopen_count += 1

        self._statistics.updated_at = now

        #
        # ------------------------------------------------------------------
        # History
        # ------------------------------------------------------------------
        #

        self._history.append(

            {
                "event": "reopen",
                "timestamp": now,
            }

        )

        #
        # ------------------------------------------------------------------
        # Runtime bookkeeping
        # ------------------------------------------------------------------
        #

        self.touch()

        #
        # ------------------------------------------------------------------
        # Notifications
        # ------------------------------------------------------------------
        #

        self.notify_hooks(
            "reopen",
            scope=self,
        )

        self.notify_callbacks(
            "reopen",
            scope=self,
        )

        self.notify_subscribers(
            "reopen",
            scope=self,
        )

        #
        # ------------------------------------------------------------------
        # Logging
        # ------------------------------------------------------------------
        #

        self._logger.debug(
            "TraceScope '%s' reopened.",
            self._name,
        )

        return self
# ==============================================================================
# Part 4.11 – Dispose
# ==============================================================================

def dispose(
    self,
) -> None:
    """
    Permanently dispose this TraceScope.

    Unlike :meth:`close`, disposal is irreversible and releases all
    runtime resources owned by this scope.

    After disposal the scope must not be used again.

    Returns
    -------
    None
    """

    with self._lock:

        if self._disposed:

            return

        #
        # ------------------------------------------------------------------
        # Ensure closed
        # ------------------------------------------------------------------
        #

        if not self._closed:

            self.close()

        now = time.time()

        #
        # ------------------------------------------------------------------
        # Runtime state
        # ------------------------------------------------------------------
        #

        self._disposed = True

        self._closed = True

        self._enabled = False

        self._initialized = False

        self._running = False

        self._active = False

        self._frozen = False

        self._state = ScopeState.CLOSED

        self._updated_at = now

        #
        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------
        #

        if hasattr(
            self._statistics,
            "dispose_count",
        ):
            self._statistics.dispose_count += 1

        self._statistics.updated_at = now

        #
        # ------------------------------------------------------------------
        # History
        # ------------------------------------------------------------------
        #

        self._history.append(

            {
                "event": "dispose",
                "timestamp": now,
            }

        )

        #
        # ------------------------------------------------------------------
        # Release tracing objects
        # ------------------------------------------------------------------
        #

        self._trace = None

        self._span = None

        self._parent_span = None

        self._tracer = None

        self._manager = None

        #
        # ------------------------------------------------------------------
        # Release runtime containers
        # ------------------------------------------------------------------
        #

        self._callbacks.clear()

        self._hooks.clear()

        self._filters.clear()

        self._subscribers.clear()

        self._runtime_data.clear()

        self._cache.clear()

        self._extensions.clear()

        self._attributes.clear()

        self._context.clear()

        self._labels.clear()

        self._notes.clear()

        self._metadata.clear()

        self._tags.clear()

        #
        # ------------------------------------------------------------------
        # Logging
        # ------------------------------------------------------------------
        #

        if self._logger is not None:

            self._logger.debug(
                "TraceScope '%s' disposed.",
                self._name,
            )

        #
        # ------------------------------------------------------------------
        # Release runtime objects
        # ------------------------------------------------------------------
        #

        self._thread_id = None

        self._process_id = None

        self._logger = None

        self._lock = None
# ==============================================================================
# Part 4.12 – Reset
# ==============================================================================

def reset(
    self,
) -> "TraceScope":
    """
    Reset this TraceScope to its initial runtime state.

    Identity and configuration are preserved while all runtime state,
    statistics, tracing objects and temporary data are cleared.

    Returns
    -------
    TraceScope
        Current scope.
    """

    with self._lock:

        if self._disposed:

            raise ScopeRuntimeError(
                "Cannot reset a disposed TraceScope."
            )

        now = time.time()

        #
        # ------------------------------------------------------------------
        # Runtime state
        # ------------------------------------------------------------------
        #

        self._running = False

        self._active = False

        self._entered = False

        self._exited = False

        self._frozen = False

        self._closed = False

        self._state = ScopeState.INITIALIZED

        self._status = ScopeStatus.READY

        self._start_time = None

        self._end_time = None

        self._updated_at = now

        #
        # ------------------------------------------------------------------
        # Tracing objects
        # ------------------------------------------------------------------
        #

        self._trace = None

        self._span = None

        self._parent_span = None

        #
        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------
        #

        self._statistics = ScopeStatistics()

        if hasattr(
            self._statistics,
            "reset_count",
        ):
            self._statistics.reset_count = 1

        self._statistics.updated_at = now

        #
        # ------------------------------------------------------------------
        # Runtime containers
        # ------------------------------------------------------------------
        #

        self._history.clear()

        self._cache.clear()

        self._runtime_data.clear()

        self._extensions.clear()

        self._attributes.clear()

        self._context.clear()

        self._labels.clear()

        self._notes.clear()

        #
        # ------------------------------------------------------------------
        # Metadata
        # ------------------------------------------------------------------
        #
        # Preserve:
        #   _metadata
        #   _tags
        #   configuration
        #

        #
        # ------------------------------------------------------------------
        # Notifications
        # ------------------------------------------------------------------
        #

        self.notify_hooks(
            "reset",
            scope=self,
        )

        self.notify_callbacks(
            "reset",
            scope=self,
        )

        self.notify_subscribers(
            "reset",
            scope=self,
        )

        #
        # ------------------------------------------------------------------
        # Logging
        # ------------------------------------------------------------------
        #

        if self._logger is not None:

            self._logger.debug(
                "TraceScope '%s' reset.",
                self._name,
            )

        self.touch()

        return self
# ==============================================================================
# Part 4.13 – Touch
# ==============================================================================

def touch(
    self,
) -> "TraceScope":
    """
    Update the runtime timestamp of this TraceScope.

    This helper marks the scope as recently modified and refreshes
    runtime statistics. It is intended to be called internally by
    lifecycle and runtime operations.

    Returns
    -------
    TraceScope
        Current scope.

    Raises
    ------
    ScopeRuntimeError
        If the scope has already been disposed.
    """

    with self._lock:

        if self._disposed:

            raise ScopeRuntimeError(
                "Cannot touch a disposed TraceScope."
            )

        now = time.time()

        #
        # ------------------------------------------------------------------
        # Runtime timestamps
        # ------------------------------------------------------------------
        #

        self._updated_at = now

        self._last_access = now

        #
        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------
        #

        if hasattr(
            self._statistics,
            "touch_count",
        ):

            self._statistics.touch_count += 1

        if hasattr(
            self._statistics,
            "update_count",
        ):

            self._statistics.update_count += 1

        self._statistics.updated_at = now

        #
        # ------------------------------------------------------------------
        # Runtime metadata
        # ------------------------------------------------------------------
        #

        self._runtime_data[
            "last_touch"
        ] = now

        #
        # ------------------------------------------------------------------
        # History
        # ------------------------------------------------------------------
        #

        self._history.append(

            {
                "event": "touch",
                "timestamp": now,
            }

        )

        #
        # ------------------------------------------------------------------
        # Logging
        # ------------------------------------------------------------------
        #

        if self._logger is not None:

            self._logger.debug(
                "TraceScope '%s' touched.",
                self._name,
            )

        return self
# ==============================================================================
# Part 4.14 – Validate
# ==============================================================================

def validate(
    self,
    *,
    strict: bool = True,
) -> bool:
    """
    Validate the internal state of this TraceScope.

    Parameters
    ----------
    strict
        If True, raise ScopeValidationError on the first validation
        failure. Otherwise return False.

    Returns
    -------
    bool
        True if the scope is valid.

    Raises
    ------
    ScopeValidationError
        If validation fails while ``strict`` is True.
    """

    with self._lock:

        now = time.time()

        #
        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------
        #

        if hasattr(
            self._statistics,
            "validation_count",
        ):
            self._statistics.validation_count += 1

        self._statistics.updated_at = now

        #
        # ------------------------------------------------------------------
        # Helper
        # ------------------------------------------------------------------
        #

        def _fail(
            message: str,
        ) -> bool:

            if hasattr(
                self._statistics,
                "failure_count",
            ):
                self._statistics.failure_count += 1

            if self._logger is not None:

                self._logger.error(
                    "TraceScope validation failed: %s",
                    message,
                )

            if strict:

                raise ScopeValidationError(
                    message,
                )

            return False

        #
        # ------------------------------------------------------------------
        # Identity
        # ------------------------------------------------------------------
        #

        if not self._id:

            return _fail(
                "Missing scope identifier."
            )

        if self._uuid is None:

            return _fail(
                "Missing UUID."
            )

        if not self._name:

            return _fail(
                "Scope name is empty."
            )

        #
        # ------------------------------------------------------------------
        # Components
        # ------------------------------------------------------------------
        #

        if self._manager is None:

            return _fail(
                "Manager is not assigned."
            )

        if self._tracer is None:

            return _fail(
                "Tracer is not assigned."
            )

        #
        # ------------------------------------------------------------------
        # Runtime state
        # ------------------------------------------------------------------
        #

        if self._disposed and not self._closed:

            return _fail(
                "Disposed scope must be closed."
            )

        if self._active and not self._running:

            return _fail(
                "Active scope must be running."
            )

        if self._entered and self._start_time is None:

            return _fail(
                "Entered scope has no start time."
            )

        if (
            self._exited
            and self._end_time is None
        ):

            return _fail(
                "Exited scope has no end time."
            )

        if (
            self._start_time is not None
            and self._end_time is not None
            and self._end_time < self._start_time
        ):

            return _fail(
                "End time is earlier than start time."
            )

        #
        # ------------------------------------------------------------------
        # Trace consistency
        # ------------------------------------------------------------------
        #

        if (
            self._span is not None
            and self._trace is None
        ):

            return _fail(
                "Span exists without trace."
            )

        #
        # ------------------------------------------------------------------
        # Configuration
        # ------------------------------------------------------------------
        #

        if self._timeout < 0:

            return _fail(
                "Timeout must be non-negative."
            )

        if self._history_limit <= 0:

            return _fail(
                "History limit must be positive."
            )

        if not isinstance(
            self._options,
            dict,
        ):

            return _fail(
                "Options must be a dictionary."
            )

        #
        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------
        #

        if (
            hasattr(
                self._statistics,
                "enter_count",
            )
            and hasattr(
                self._statistics,
                "exit_count",
            )
            and self._statistics.exit_count
            > self._statistics.enter_count
        ):

            return _fail(
                "Exit count exceeds enter count."
            )

        #
        # ------------------------------------------------------------------
        # Metadata
        # ------------------------------------------------------------------
        #

        if not isinstance(
            self._metadata,
            dict,
        ):

            return _fail(
                "Metadata must be a dictionary."
            )

        if not isinstance(
            self._attributes,
            dict,
        ):

            return _fail(
                "Attributes must be a dictionary."
            )

        if not isinstance(
            self._context,
            dict,
        ):

            return _fail(
                "Context must be a dictionary."
            )

        #
        # ------------------------------------------------------------------
        # Success
        # ------------------------------------------------------------------
        #

        if self._logger is not None:

            self._logger.debug(
                "TraceScope '%s' validated successfully.",
                self._name,
            )

        self.touch()

        return True
# ==============================================================================
# Part 4.15 – Notify
# ==============================================================================

# ==============================================================================
# Part 4.15.1 – notify_callbacks()
# ==============================================================================

def notify_callbacks(
    self,
    event: str,
    *args: Any,
    **kwargs: Any,
) -> "TraceScope":
    """
    Notify all registered callbacks.

    Callback failures are isolated and never interrupt TraceScope.

    Parameters
    ----------
    event
        Runtime event name.

    Returns
    -------
    TraceScope
    """

    callbacks = tuple(
        self._callbacks
    )

    for callback in callbacks:

        try:

            callback(
                event,
                self,
                *args,
                **kwargs,
            )

        except Exception as exc:

            if hasattr(
                self._statistics,
                "callback_failure_count",
            ):
                self._statistics.callback_failure_count += 1

            if self._logger is not None:

                self._logger.exception(
                    "TraceScope callback failed (%s): %s",
                    event,
                    exc,
                )

    return self


# ==============================================================================
# Part 4.15.2 – notify_hooks()
# ==============================================================================

def notify_hooks(
    self,
    event: str,
    *args: Any,
    **kwargs: Any,
) -> "TraceScope":
    """
    Notify all hooks registered for an event.

    Parameters
    ----------
    event
        Hook event name.

    Returns
    -------
    TraceScope
    """

    hooks = tuple(

        self._hooks.get(
            event,
            (),
        )

    )

    for hook in hooks:

        try:

            hook(
                self,
                *args,
                **kwargs,
            )

        except Exception as exc:

            if hasattr(
                self._statistics,
                "hook_failure_count",
            ):
                self._statistics.hook_failure_count += 1

            if self._logger is not None:

                self._logger.exception(
                    "TraceScope hook failed (%s): %s",
                    event,
                    exc,
                )

    return self


# ==============================================================================
# Part 4.15.3 – notify_subscribers()
# ==============================================================================

def notify_subscribers(
    self,
    event: str,
    *args: Any,
    **kwargs: Any,
) -> "TraceScope":
    """
    Notify all subscribers.

    Subscribers may be callables or objects exposing one of:

        on_event(...)
        notify(...)

    Parameters
    ----------
    event
        Runtime event.

    Returns
    -------
    TraceScope
    """

    subscribers = tuple(
        self._subscribers
    )

    for subscriber in subscribers:

        try:

            #
            # --------------------------------------------------------------
            # Callable subscriber
            # --------------------------------------------------------------
            #

            if callable(
                subscriber,
            ):

                subscriber(
                    event,
                    self,
                    *args,
                    **kwargs,
                )

            #
            # --------------------------------------------------------------
            # on_event()
            # --------------------------------------------------------------
            #

            elif hasattr(
                subscriber,
                "on_event",
            ):

                subscriber.on_event(
                    event,
                    self,
                    *args,
                    **kwargs,
                )

            #
            # --------------------------------------------------------------
            # notify()
            # --------------------------------------------------------------
            #

            elif hasattr(
                subscriber,
                "notify",
            ):

                subscriber.notify(
                    event,
                    self,
                    *args,
                    **kwargs,
                )

        except Exception as exc:

            if hasattr(
                self._statistics,
                "subscriber_failure_count",
            ):
                self._statistics.subscriber_failure_count += 1

            if self._logger is not None:

                self._logger.exception(
                    "TraceScope subscriber failed (%s): %s",
                    event,
                    exc,
                )

    return self
# ==============================================================================
# Part 4.16 – Statistics Update
# ==============================================================================

# ==============================================================================
# Part 4.16.1 – update_statistics()
# ==============================================================================

def update_statistics(
    self,
    *,
    success: bool = True,
) -> "TraceScope":
    """
    Update runtime statistics.

    Parameters
    ----------
    success
        Whether the operation completed successfully.

    Returns
    -------
    TraceScope
    """

    with self._lock:

        self._statistics.update_count += 1

        self._statistics.updated_at = time.time()

        if success:

            self._statistics.success_count += 1

        else:

            self._statistics.failure_count += 1

        self.touch()

        return self


# ==============================================================================
# Part 4.16.2 – record_duration()
# ==============================================================================

def record_duration(
    self,
    duration: Optional[float] = None,
) -> float:
    """
    Record scope execution duration.

    Parameters
    ----------
    duration
        Explicit duration. If omitted the duration is computed
        from start_time and end_time.

    Returns
    -------
    float
        Recorded duration.
    """

    with self._lock:

        #
        # --------------------------------------------------------------
        # Calculate duration
        # --------------------------------------------------------------
        #

        if duration is None:

            if self._start_time is None:

                duration = 0.0

            else:

                end_time = (

                    self._end_time

                    if self._end_time is not None

                    else time.time()

                )

                duration = max(
                    0.0,
                    end_time - self._start_time,
                )

        duration = float(duration)

        #
        # --------------------------------------------------------------
        # Update statistics
        # --------------------------------------------------------------
        #

        stats = self._statistics

        stats.total_duration += duration

        if stats.minimum_duration == 0.0:

            stats.minimum_duration = duration

        else:

            stats.minimum_duration = min(
                stats.minimum_duration,
                duration,
            )

        stats.maximum_duration = max(
            stats.maximum_duration,
            duration,
        )

        count = max(
            1,
            stats.success_count
            + stats.failure_count,
        )

        stats.average_duration = (

            stats.total_duration / count

        )

        stats.updated_at = time.time()

        self.touch()

        return duration


# ==============================================================================
# Part 4.16.3 – record_exception()
# ==============================================================================

def record_exception(
    self,
    exception: BaseException,
) -> "TraceScope":
    """
    Record an exception raised while the scope is active.

    Parameters
    ----------
    exception
        Exception instance.

    Returns
    -------
    TraceScope
    """

    with self._lock:

        self._statistics.exception_count += 1

        self._statistics.failure_count += 1

        self._statistics.updated_at = time.time()

        self._runtime_data[
            "last_exception"
        ] = exception

        self._runtime_data[
            "last_exception_type"
        ] = type(exception).__name__

        self._runtime_data[
            "last_exception_message"
        ] = str(exception)

        if self._logger is not None:

            self._logger.exception(
                "TraceScope '%s' captured exception.",
                self._name,
                exc_info=exception,
            )

        self.touch()

        return self
# ==============================================================================
# Part 5.1 – __call__()
# ==============================================================================

def __call__(
    self,
    func: Callable[..., Any],
) -> Callable[..., Any]:
    """
    Decorate a callable with this TraceScope.

    The wrapped callable is executed inside this TraceScope.

    Examples
    --------
    >>> @TraceScope(manager, "database")
    ... def query():
    ...     ...

    >>> wrapped = scope(query)
    >>> wrapped()

    Parameters
    ----------
    func
        Callable to decorate.

    Returns
    -------
    Callable
        Wrapped callable.

    Raises
    ------
    TypeError
        If *func* is not callable.
    """

    if not callable(func):

        raise TypeError(
            "func must be callable."
        )

    #
    # Delegate to the internal decorator implementation.
    #
    return self.decorate_function(
        func,
    )
# ==============================================================================
# Part 5.2 – decorate_function()
# ==============================================================================

def decorate_function(
    self,
    func: Callable[..., Any],
) -> Callable[..., Any]:
    """
    Decorate a Python function.

    The decorated function is executed inside this TraceScope.

    Lifecycle
    ---------
        before_call()
            ↓
        enter()
            ↓
        function(...)
            ↓
        on_success() / on_exception()
            ↓
        exit()
            ↓
        after_call()
            ↓
        on_finally()

    Parameters
    ----------
    func
        Function to decorate.

    Returns
    -------
    Callable
        Wrapped callable.

    Raises
    ------
    TypeError
        If func is not callable.
    """

    import functools

    if not callable(func):

        raise TypeError(
            "func must be callable."
        )

    #
    # ------------------------------------------------------------------
    # Prevent duplicate wrapping.
    # ------------------------------------------------------------------
    #

    if getattr(
        func,
        "__trace_scope_wrapped__",
        False,
    ):

        return func

    #
    # ------------------------------------------------------------------
    # Wrapper
    # ------------------------------------------------------------------
    #

    @functools.wraps(func)
    def wrapper(
        *args: Any,
        **kwargs: Any,
    ) -> Any:

        self.before_call(
            func,
            args,
            kwargs,
        )

        result: Any = None

        success: bool = False

        try:

            self.enter()

            result = func(
                *args,
                **kwargs,
            )

            success = True

            self.on_success(
                result,
            )

            return result

        except BaseException as exc:

            self.record_exception(
                exc,
            )

            self.on_exception(
                exc,
            )

            raise

        finally:

            try:

                self.exit()

            finally:

                self.after_call(
                    func,
                    result,
                )

                self.update_statistics(
                    success=success,
                )

                self.record_duration()

                self.on_finally()

    #
    # ------------------------------------------------------------------
    # Wrapper metadata
    # ------------------------------------------------------------------
    #

    wrapper.__trace_scope_wrapped__ = True

    wrapper.__trace_scope__ = self

    wrapper.__wrapped_function__ = func

    wrapper.__scope_name__ = self.name

    wrapper.__scope_id__ = self.id

    wrapper.__scope_version__ = self.version

    wrapper.__scope_type__ = self.scope_type

    return wrapper
# ==============================================================================
# Part 5.3 – decorate_method()
# ==============================================================================

def decorate_method(
    self,
    method: Callable[..., Any],
) -> Callable[..., Any]:
    """
    Decorate an instance method, class method or static method.

    This method delegates the actual wrapping logic to
    ``decorate_function()`` while preserving descriptor behavior.

    Supported
    ---------
    • instance methods
    • class methods
    • static methods

    Parameters
    ----------
    method
        Method to decorate.

    Returns
    -------
    Callable
        Decorated method.

    Raises
    ------
    TypeError
        If the supplied object is not callable.
    """

    import functools

    #
    # ------------------------------------------------------------------
    # classmethod
    # ------------------------------------------------------------------
    #

    if isinstance(
        method,
        classmethod,
    ):

        wrapped = self.decorate_function(
            method.__func__,
        )

        return classmethod(
            wrapped,
        )

    #
    # ------------------------------------------------------------------
    # staticmethod
    # ------------------------------------------------------------------
    #

    if isinstance(
        method,
        staticmethod,
    ):

        wrapped = self.decorate_function(
            method.__func__,
        )

        return staticmethod(
            wrapped,
        )

    #
    # ------------------------------------------------------------------
    # Normal bound / unbound method
    # ------------------------------------------------------------------
    #

    if not callable(
        method,
    ):

        raise TypeError(
            "method must be callable."
        )

    decorated = self.decorate_function(
        method,
    )

    @functools.wraps(method)
    def wrapper(
        *args: Any,
        **kwargs: Any,
    ) -> Any:

        return decorated(
            *args,
            **kwargs,
        )

    #
    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------
    #

    wrapper.__trace_scope_method__ = True

    wrapper.__trace_scope__ = self

    wrapper.__wrapped_method__ = method

    wrapper.__scope_name__ = self.name

    wrapper.__scope_id__ = self.id

    wrapper.__scope_version__ = self.version

    wrapper.__scope_type__ = self.scope_type

    return wrapper
# ==============================================================================
# Part 5.4 – decorate_class()
# ==============================================================================

def decorate_class(
    self,
    cls: type,
) -> type:
    """
    Decorate a class.

    All suitable methods are automatically wrapped by this
    TraceScope.

    Decorated members
    -----------------
    • instance methods
    • class methods
    • static methods

    Ignored members
    ---------------
    • properties
    • descriptors
    • private runtime attributes
    • dunder methods
      (__repr__, __str__, __class__, ...)

    Parameters
    ----------
    cls
        Class to decorate.

    Returns
    -------
    type
        Decorated class.

    Raises
    ------
    TypeError
        If cls is not a class.
    """

    import inspect

    if not inspect.isclass(cls):

        raise TypeError(
            "decorate_class() expects a class."
        )

    #
    # ------------------------------------------------------------------
    # Iterate through class namespace.
    # ------------------------------------------------------------------
    #

    for name, member in list(
        vars(cls).items()
    ):

        #
        # --------------------------------------------------------------
        # Ignore dunder methods.
        # --------------------------------------------------------------
        #

        if (
            name.startswith("__")
            and name.endswith("__")
        ):

            continue

        #
        # --------------------------------------------------------------
        # Ignore properties.
        # --------------------------------------------------------------
        #

        if isinstance(
            member,
            property,
        ):

            continue

        #
        # --------------------------------------------------------------
        # Ignore already wrapped methods.
        # --------------------------------------------------------------
        #

        if getattr(
            member,
            "__trace_scope_wrapped__",
            False,
        ):

            continue

        #
        # --------------------------------------------------------------
        # classmethod
        # --------------------------------------------------------------
        #

        if isinstance(
            member,
            classmethod,
        ):

            setattr(

                cls,

                name,

                self.decorate_method(
                    member,
                ),

            )

            continue

        #
        # --------------------------------------------------------------
        # staticmethod
        # --------------------------------------------------------------
        #

        if isinstance(
            member,
            staticmethod,
        ):

            setattr(

                cls,

                name,

                self.decorate_method(
                    member,
                ),

            )

            continue

        #
        # --------------------------------------------------------------
        # Normal callable
        # --------------------------------------------------------------
        #

        if callable(
            member,
        ):

            setattr(

                cls,

                name,

                self.decorate_method(
                    member,
                ),

            )

    #
    # ------------------------------------------------------------------
    # Attach metadata.
    # ------------------------------------------------------------------
    #

    cls.__trace_scope_wrapped__ = True

    cls.__trace_scope__ = self

    cls.__scope_name__ = self.name

    cls.__scope_id__ = self.id

    cls.__scope_version__ = self.version

    cls.__scope_type__ = self.scope_type

    return cls
# ==============================================================================
# Part 5.5 – wrap_callable()
# ==============================================================================

def wrap_callable(
    self,
    target: Callable[..., Any],
    *,
    name: Optional[str] = None,
) -> Callable[..., Any]:
    """
    Create a TraceScope wrapper around a callable.

    This is the internal implementation used by

        • decorate_function()
        • decorate_method()
        • decorate_class()

    The wrapped callable executes inside this TraceScope.

    Parameters
    ----------
    target
        Callable to wrap.

    name
        Optional runtime operation name.

    Returns
    -------
    Callable
        Wrapped callable.

    Raises
    ------
    TypeError
        If *target* is not callable.
    """

    import functools

    if not callable(target):

        raise TypeError(
            "target must be callable."
        )

    #
    # ------------------------------------------------------------------
    # Prevent double wrapping.
    # ------------------------------------------------------------------
    #

    if getattr(
        target,
        "__trace_scope_wrapped__",
        False,
    ):

        return target

    operation_name = (
        name
        or getattr(
            target,
            "__qualname__",
            target.__name__,
        )
    )

    @functools.wraps(target)
    def wrapper(
        *args: Any,
        **kwargs: Any,
    ) -> Any:

        result: Any = None

        success: bool = False

        self.before_call(
            target,
            args,
            kwargs,
        )

        try:

            #
            # ----------------------------------------------------------
            # Enter TraceScope
            # ----------------------------------------------------------
            #

            self.enter()

            #
            # ----------------------------------------------------------
            # Execute callable
            # ----------------------------------------------------------
            #

            result = target(
                *args,
                **kwargs,
            )

            success = True

            self.on_success(
                result,
            )

            return result

        except BaseException as exc:

            self.record_exception(
                exc,
            )

            self.on_exception(
                exc,
            )

            raise

        finally:

            try:

                self.exit()

            finally:

                self.after_call(
                    target,
                    result,
                )

                self.update_statistics(
                    success=success,
                )

                self.record_duration()

                self.on_finally()

    #
    # ------------------------------------------------------------------
    # Wrapper metadata
    # ------------------------------------------------------------------
    #

    wrapper.__trace_scope_wrapped__ = True

    wrapper.__trace_scope__ = self

    wrapper.__wrapped_callable__ = target

    wrapper.__scope_name__ = self.name

    wrapper.__scope_id__ = self.id

    wrapper.__scope_uuid__ = self.uuid

    wrapper.__scope_type__ = self.scope_type

    wrapper.__scope_version__ = self.version

    wrapper.__scope_operation__ = operation_name

    wrapper.__scope_created_at__ = time.time()

    return wrapper
# ==============================================================================
# Part 5.6 – before_call()
# ==============================================================================

def before_call(
    self,
    target: Callable[..., Any],
    args: Sequence[Any],
    kwargs: Mapping[str, Any],
) -> "TraceScope":
    """
    Execute pre-call processing.

    This method is invoked immediately before the wrapped callable
    is executed.

    Responsibilities
    ----------------
    • Validate runtime state.
    • Record invocation metadata.
    • Update runtime statistics.
    • Store runtime information.
    • Notify callbacks.
    • Notify hooks.
    • Notify subscribers.

    Parameters
    ----------
    target
        Callable about to be executed.

    args
        Positional arguments.

    kwargs
        Keyword arguments.

    Returns
    -------
    TraceScope
    """

    with self._lock:

        #
        # --------------------------------------------------------------
        # Runtime validation
        # --------------------------------------------------------------
        #

        self.validate()

        if not self._enabled:

            return self

        #
        # --------------------------------------------------------------
        # Runtime timestamps
        # --------------------------------------------------------------
        #

        now = time.time()

        self._start_time = now

        self._updated_at = now

        self._running = True

        self._active = True

        self._entered = True

        self._state = "running"

        #
        # --------------------------------------------------------------
        # Statistics
        # --------------------------------------------------------------
        #

        stats = self._statistics

        if hasattr(stats, "enter_count"):

            stats.enter_count += 1

        if hasattr(stats, "update_count"):

            stats.update_count += 1

        if hasattr(stats, "updated_at"):

            stats.updated_at = now

        #
        # --------------------------------------------------------------
        # Runtime data
        # --------------------------------------------------------------
        #

        self._runtime_data["callable"] = target

        self._runtime_data["callable_name"] = getattr(
            target,
            "__qualname__",
            getattr(
                target,
                "__name__",
                str(target),
            ),
        )

        self._runtime_data["args"] = tuple(args)

        self._runtime_data["kwargs"] = dict(kwargs)

        self._runtime_data["thread_id"] = threading.get_ident()

        #
        # --------------------------------------------------------------
        # History
        # --------------------------------------------------------------
        #

        if hasattr(
            self,
            "_history",
        ):

            self._history.append(

                {
                    "event": "before_call",
                    "timestamp": now,
                    "callable": self._runtime_data[
                        "callable_name"
                    ],
                }

            )

        #
        # --------------------------------------------------------------
        # Call notifications
        # --------------------------------------------------------------
        #

        self.notify_callbacks(
            "before_call",
            target=target,
            args=args,
            kwargs=kwargs,
        )

        self.notify_hooks(
            "before_call",
            target=target,
            args=args,
            kwargs=kwargs,
        )

        self.notify_subscribers(
            "before_call",
            target=target,
            args=args,
            kwargs=kwargs,
        )

        #
        # --------------------------------------------------------------
        # Logger
        # --------------------------------------------------------------
        #

        if self._logger is not None:

            self._logger.debug(

                "TraceScope '%s' entering callable '%s'.",

                self._name,

                self._runtime_data[
                    "callable_name"
                ],

            )

        self.touch()

        return self
# ==============================================================================
# Part 5.7 – after_call()
# ==============================================================================

def after_call(
    self,
    target: Callable[..., Any],
    result: Any = None,
) -> "TraceScope":
    """
    Execute post-call processing.

    This method is invoked after the wrapped callable has finished
    execution.

    Responsibilities
    ----------------
    • Update runtime timestamps.
    • Record execution result.
    • Update runtime statistics.
    • Append history.
    • Notify callbacks.
    • Notify hooks.
    • Notify subscribers.

    Parameters
    ----------
    target
        Executed callable.

    result
        Callable return value.

    Returns
    -------
    TraceScope
    """

    with self._lock:

        if not self._enabled:

            return self

        #
        # ------------------------------------------------------------------
        # Runtime timestamps
        # ------------------------------------------------------------------
        #

        now = time.time()

        self._end_time = now

        self._updated_at = now

        self._running = False

        self._active = False

        self._exited = True

        self._state = "completed"

        #
        # ------------------------------------------------------------------
        # Runtime data
        # ------------------------------------------------------------------
        #

        self._runtime_data["result"] = result

        self._runtime_data["end_time"] = now

        self._runtime_data["duration"] = (

            max(
                0.0,
                now - self._start_time,
            )

            if self._start_time is not None

            else 0.0

        )

        #
        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------
        #

        stats = self._statistics

        if hasattr(
            stats,
            "exit_count",
        ):

            stats.exit_count += 1

        if hasattr(
            stats,
            "update_count",
        ):

            stats.update_count += 1

        if hasattr(
            stats,
            "updated_at",
        ):

            stats.updated_at = now

        #
        # ------------------------------------------------------------------
        # History
        # ------------------------------------------------------------------
        #

        if hasattr(
            self,
            "_history",
        ):

            self._history.append(

                {
                    "event": "after_call",
                    "timestamp": now,
                    "callable": getattr(
                        target,
                        "__qualname__",
                        getattr(
                            target,
                            "__name__",
                            str(target),
                        ),
                    ),
                    "duration": self._runtime_data[
                        "duration"
                    ],
                }

            )

        #
        # ------------------------------------------------------------------
        # Notifications
        # ------------------------------------------------------------------
        #

        self.notify_callbacks(
            "after_call",
            target=target,
            result=result,
        )

        self.notify_hooks(
            "after_call",
            target=target,
            result=result,
        )

        self.notify_subscribers(
            "after_call",
            target=target,
            result=result,
        )

        #
        # ------------------------------------------------------------------
        # Logger
        # ------------------------------------------------------------------
        #

        if self._logger is not None:

            self._logger.debug(
                "TraceScope '%s' finished callable '%s'.",
                self._name,
                getattr(
                    target,
                    "__qualname__",
                    getattr(
                        target,
                        "__name__",
                        str(target),
                    ),
                ),
            )

        self.touch()

        return self
# ==============================================================================
# Part 5.8 – on_success()
# ==============================================================================

def on_success(
    self,
    result: Any = None,
) -> "TraceScope":
    """
    Handle successful execution.

    This method is invoked when the wrapped callable completes
    successfully without raising an exception.

    Responsibilities
    ----------------
    • Update success statistics.
    • Store result metadata.
    • Update runtime state.
    • Notify callbacks.
    • Notify hooks.
    • Notify subscribers.
    • Append history.
    • Emit logger event.

    Parameters
    ----------
    result
        Return value produced by the wrapped callable.

    Returns
    -------
    TraceScope
    """

    with self._lock:

        if not self._enabled:

            return self

        now = time.time()

        #
        # ------------------------------------------------------------------
        # Runtime state
        # ------------------------------------------------------------------
        #

        self._updated_at = now

        self._runtime_data["success"] = True

        self._runtime_data["result"] = result

        self._runtime_data["completed"] = True

        self._runtime_data["failed"] = False

        self._runtime_data["last_success"] = now

        #
        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------
        #

        stats = self._statistics

        if hasattr(
            stats,
            "success_count",
        ):

            stats.success_count += 1

        if hasattr(
            stats,
            "update_count",
        ):

            stats.update_count += 1

        if hasattr(
            stats,
            "updated_at",
        ):

            stats.updated_at = now

        #
        # ------------------------------------------------------------------
        # History
        # ------------------------------------------------------------------
        #

        if hasattr(
            self,
            "_history",
        ):

            self._history.append(

                {
                    "event": "success",
                    "timestamp": now,
                    "scope": self._name,
                    "result_type": (
                        type(result).__name__
                        if result is not None
                        else None
                    ),
                }

            )

        #
        # ------------------------------------------------------------------
        # Notifications
        # ------------------------------------------------------------------
        #

        self.notify_callbacks(
            "success",
            scope=self,
            result=result,
        )

        self.notify_hooks(
            "success",
            scope=self,
            result=result,
        )

        self.notify_subscribers(
            "success",
            scope=self,
            result=result,
        )

        #
        # ------------------------------------------------------------------
        # Logger
        # ------------------------------------------------------------------
        #

        if self._logger is not None:

            self._logger.debug(
                "TraceScope '%s' completed successfully.",
                self._name,
            )

        self.touch()

        return self
# ==============================================================================
# Part 5.9 – on_exception()
# ==============================================================================

def on_exception(
    self,
    exception: BaseException,
) -> "TraceScope":
    """
    Handle an exception raised by the wrapped callable.

    This method is invoked immediately after an exception is
    caught inside the TraceScope decorator wrapper.

    Responsibilities
    ----------------
    • Update runtime state.
    • Record exception information.
    • Update statistics.
    • Store runtime metadata.
    • Notify callbacks.
    • Notify hooks.
    • Notify subscribers.
    • Append history.
    • Emit logger event.

    Parameters
    ----------
    exception
        Exception instance.

    Returns
    -------
    TraceScope
    """

    with self._lock:

        if not self._enabled:

            return self

        now = time.time()

        #
        # ------------------------------------------------------------------
        # Runtime state
        # ------------------------------------------------------------------
        #

        self._updated_at = now

        self._runtime_data["success"] = False

        self._runtime_data["failed"] = True

        self._runtime_data["completed"] = False

        self._runtime_data["last_exception"] = exception

        self._runtime_data["last_exception_type"] = (
            type(exception).__name__
        )

        self._runtime_data["last_exception_message"] = (
            str(exception)
        )

        self._runtime_data["last_exception_time"] = now

        self._state = "exception"

        #
        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------
        #

        stats = self._statistics

        if hasattr(
            stats,
            "exception_count",
        ):

            stats.exception_count += 1

        if hasattr(
            stats,
            "failure_count",
        ):

            stats.failure_count += 1

        if hasattr(
            stats,
            "update_count",
        ):

            stats.update_count += 1

        if hasattr(
            stats,
            "updated_at",
        ):

            stats.updated_at = now

        #
        # ------------------------------------------------------------------
        # History
        # ------------------------------------------------------------------
        #

        if hasattr(
            self,
            "_history",
        ):

            self._history.append(
                {
                    "event": "exception",
                    "timestamp": now,
                    "scope": self._name,
                    "exception": type(exception).__name__,
                    "message": str(exception),
                }
            )

        #
        # ------------------------------------------------------------------
        # Notifications
        # ------------------------------------------------------------------
        #

        self.notify_callbacks(
            "exception",
            scope=self,
            exception=exception,
        )

        self.notify_hooks(
            "exception",
            scope=self,
            exception=exception,
        )

        self.notify_subscribers(
            "exception",
            scope=self,
            exception=exception,
        )

        #
        # ------------------------------------------------------------------
        # Logger
        # ------------------------------------------------------------------
        #

        if self._logger is not None:

            self._logger.exception(
                "TraceScope '%s' captured exception: %s",
                self._name,
                type(exception).__name__,
                exc_info=exception,
            )

        self.touch()

        return self
# ==============================================================================
# Part 5.10 – on_finally()
# ==============================================================================

def on_finally(
    self,
) -> "TraceScope":
    """
    Final cleanup executed after every wrapped callable.

    This method is always executed regardless of whether the wrapped
    callable completed successfully or raised an exception.

    Responsibilities
    ----------------
    • Update runtime timestamps.
    • Finalize runtime state.
    • Clear temporary runtime data.
    • Record final statistics.
    • Notify callbacks.
    • Notify hooks.
    • Notify subscribers.
    • Append history.
    • Emit logger event.

    Returns
    -------
    TraceScope
    """

    with self._lock:

        now = time.time()

        #
        # ------------------------------------------------------------------
        # Runtime timestamps
        # ------------------------------------------------------------------
        #

        self._updated_at = now

        self._runtime_data["finally_time"] = now

        #
        # ------------------------------------------------------------------
        # Runtime state
        # ------------------------------------------------------------------
        #

        self._running = False

        self._active = False

        self._runtime_data["completed"] = True

        self._runtime_data["cleanup"] = True

        #
        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------
        #

        stats = self._statistics

        if hasattr(
            stats,
            "update_count",
        ):

            stats.update_count += 1

        if hasattr(
            stats,
            "updated_at",
        ):

            stats.updated_at = now

        #
        # ------------------------------------------------------------------
        # History
        # ------------------------------------------------------------------
        #

        if hasattr(
            self,
            "_history",
        ):

            self._history.append(
                {
                    "event": "finally",
                    "timestamp": now,
                    "scope": self._name,
                }
            )

        #
        # ------------------------------------------------------------------
        # Notifications
        # ------------------------------------------------------------------
        #

        self.notify_callbacks(
            "finally",
            scope=self,
        )

        self.notify_hooks(
            "finally",
            scope=self,
        )

        self.notify_subscribers(
            "finally",
            scope=self,
        )

        #
        # ------------------------------------------------------------------
        # Logger
        # ------------------------------------------------------------------
        #

        if self._logger is not None:

            self._logger.debug(
                "TraceScope '%s' finalized.",
                self._name,
            )

        #
        # ------------------------------------------------------------------
        # Cleanup temporary runtime objects
        # ------------------------------------------------------------------
        #

        self._runtime_data.pop(
            "callable",
            None,
        )

        self._runtime_data.pop(
            "args",
            None,
        )

        self._runtime_data.pop(
            "kwargs",
            None,
        )

        self._runtime_data.pop(
            "result",
            None,
        )

        self.touch()

        return self
# ==============================================================================
# Part 5.11 – unwrap()
# ==============================================================================

def unwrap(
    self,
    target: Callable[..., Any],
    *,
    recursive: bool = True,
) -> Callable[..., Any]:
    """
    Remove TraceScope wrapping from a callable.

    This method returns the original callable that was wrapped by
    TraceScope. It does not modify the wrapper itself; it simply
    returns the underlying callable.

    Parameters
    ----------
    target
        Wrapped callable.

    recursive
        If True, recursively unwrap nested wrappers until the
        original callable is reached.

    Returns
    -------
    Callable
        Original callable.

    Raises
    ------
    TypeError
        If target is not callable.
    """

    if not callable(target):

        raise TypeError(
            "target must be callable."
        )

    current = target

    #
    # ------------------------------------------------------------------
    # Recursive unwrapping
    # ------------------------------------------------------------------
    #

    while True:

        wrapped = getattr(
            current,
            "__wrapped_callable__",
            None,
        )

        if wrapped is None:

            wrapped = getattr(
                current,
                "__wrapped__",
                None,
            )

        if wrapped is None:

            break

        current = wrapped

        if not recursive:

            break

    return current
# ==============================================================================
# Part 5.12 – is_wrapped()
# ==============================================================================

def is_wrapped(
    self,
    target: Any,
    *,
    recursive: bool = True,
) -> bool:
    """
    Determine whether an object has been wrapped by TraceScope.

    A callable is considered wrapped if it contains one or more of the
    TraceScope wrapper metadata attributes or the standard functools
    ``__wrapped__`` attribute.

    Parameters
    ----------
    target
        Object to inspect.

    recursive
        If True, recursively inspect nested wrappers.

    Returns
    -------
    bool
        True if the object is wrapped by TraceScope, otherwise False.
    """

    if target is None:

        return False

    if not callable(target):

        return False

    current = target

    while True:

        #
        # ------------------------------------------------------------------
        # SciOS TraceScope wrapper metadata
        # ------------------------------------------------------------------
        #

        if getattr(
            current,
            "__trace_scope_wrapped__",
            False,
        ):

            return True

        if hasattr(
            current,
            "__trace_scope__",
        ):

            return True

        if hasattr(
            current,
            "__wrapped_callable__",
        ):

            return True

        #
        # ------------------------------------------------------------------
        # functools.wraps support
        # ------------------------------------------------------------------
        #

        wrapped = getattr(
            current,
            "__wrapped__",
            None,
        )

        if wrapped is None:

            break

        if not recursive:

            return True

        current = wrapped

    return False
# ==============================================================================
# Part 5.13 – decorator_metadata()
# ==============================================================================

def decorator_metadata(
    self,
    target: Callable[..., Any],
) -> Dict[str, Any]:
    """
    Return TraceScope decorator metadata for a wrapped callable.

    This method extracts all TraceScope-specific metadata attached to a
    decorated callable. If the callable is not wrapped, an empty metadata
    dictionary is returned.

    Parameters
    ----------
    target
        Decorated callable.

    Returns
    -------
    Dict[str, Any]
        TraceScope metadata dictionary.
    """

    if not callable(target):

        raise TypeError(
            "target must be callable."
        )

    #
    # ------------------------------------------------------------------
    # Locate wrapped object
    # ------------------------------------------------------------------
    #

    wrapped = self.is_wrapped(
        target,
        recursive=False,
    )

    metadata: Dict[str, Any] = {

        #
        # Identity
        #

        "wrapped": bool(wrapped),

        "scope_name": getattr(
            target,
            "__scope_name__",
            None,
        ),

        "scope_id": getattr(
            target,
            "__scope_id__",
            None,
        ),

        "scope_uuid": getattr(
            target,
            "__scope_uuid__",
            None,
        ),

        "scope_version": getattr(
            target,
            "__scope_version__",
            None,
        ),

        "scope_type": getattr(
            target,
            "__scope_type__",
            None,
        ),

        #
        # Runtime
        #

        "operation": getattr(
            target,
            "__scope_operation__",
            None,
        ),

        "created_at": getattr(
            target,
            "__scope_created_at__",
            None,
        ),

        #
        # Wrapped callable
        #

        "wrapped_callable": getattr(
            target,
            "__wrapped_callable__",
            None,
        ),

        "trace_scope": getattr(
            target,
            "__trace_scope__",
            None,
        ),

        #
        # Python metadata
        #

        "callable_name": getattr(
            target,
            "__qualname__",
            getattr(
                target,
                "__name__",
                None,
            ),
        ),

        "module": getattr(
            target,
            "__module__",
            None,
        ),

        "doc": getattr(
            target,
            "__doc__",
            None,
        ),

    }

    #
    # ------------------------------------------------------------------
    # Remove empty values
    # ------------------------------------------------------------------
    #

    metadata = {

        key: value

        for key, value in metadata.items()

        if value is not None

    }

    return metadata
# ==============================================================================
# Part 6.1 – SpanScope Class Declaration
# ==============================================================================

class SpanScope(ContextDecorator):
    """
    Runtime span scope.

    SpanScope is a context manager and decorator responsible for
    managing the lifecycle of a single TraceSpan.

    It can be used in three ways:

    Context Manager
    ---------------
    >>> with SpanScope(manager, "Database"):
    ...     ...

    Decorator
    ---------
    >>> @SpanScope(manager, "Database")
    ... def query():
    ...     ...

    Manual API
    ----------
    >>> scope = SpanScope(manager, "Database")
    >>> scope.enter()
    >>> ...
    >>> scope.exit()

    Features
    --------
    • Automatic span creation
    • Automatic span completion
    • Parent-child span relationships
    • Runtime statistics
    • Exception recording
    • Callback notifications
    • Hook execution
    • Metadata propagation
    • Thread-safe operation
    • ContextDecorator compatible

    Notes
    -----
    SpanScope manages exactly one runtime span during its lifetime.
    Nested SpanScope instances automatically form parent-child span
    relationships through the active TraceTracer.
    """
# ==============================================================================
# Part 6.2 – Constructor Signature
# ==============================================================================

def __init__(
    self,
    manager: TraceManager,
    name: str = DEFAULT_SPAN_NAME,
    *,
    description: str = "",
    parent: Optional[TraceSpan] = None,
    context: Optional[TraceContext] = None,
    kind: SpanKind = SpanKind.INTERNAL,
    enabled: bool = True,
    auto_start: bool = True,
    auto_finish: bool = True,
    timeout: float = DEFAULT_TIMEOUT,
    history_limit: int = DEFAULT_HISTORY_LIMIT,
    encoding: str = DEFAULT_ENCODING,
    options: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    attributes: Optional[Dict[str, Any]] = None,
    tags: Optional[Iterable[str]] = None,
) -> None:
    """
    Initialize a SpanScope.

    Parameters
    ----------
    manager
        Active TraceManager used to resolve the current TraceTracer.

    name
        Span name.

    description
        Human-readable description.

    parent
        Optional parent TraceSpan. If None, the current active span
        from the tracer will be used.

    context
        Optional TraceContext.

    kind
        Span kind.

    enabled
        Enable this scope.

    auto_start
        Automatically start the span when entering the scope.

    auto_finish
        Automatically finish the span when leaving the scope.

    timeout
        Runtime timeout in seconds.

    history_limit
        Maximum number of history records.

    encoding
        Default serialization encoding.

    options
        Runtime configuration options.

    metadata
        User metadata.

    attributes
        Span attributes.

    tags
        Initial tags.
    """
# ==============================================================================
# Part 6.3 – Identity
# ==============================================================================

#
# ------------------------------------------------------------------------------
# Unique identity
# ------------------------------------------------------------------------------

self._id: str = uuid.uuid4().hex

self._uuid: uuid.UUID = uuid.UUID(
    self._id,
)

#
# ------------------------------------------------------------------------------
# Human-readable identity
# ------------------------------------------------------------------------------

self._name: str = str(
    name,
)

self._description: str = str(
    description,
)

#
# ------------------------------------------------------------------------------
# Version
# ------------------------------------------------------------------------------

self._version: str = CONTEXT_VERSION

#
# ------------------------------------------------------------------------------
# Scope type
# ------------------------------------------------------------------------------

self._scope_type: ScopeType = (
    ScopeType.SPAN
)

#
# ------------------------------------------------------------------------------
# Identity metadata
# ------------------------------------------------------------------------------

self._qualified_name: str = (
    f"{self._scope_type.value}:"
    f"{self._name}"
)

self._display_name: str = (
    self._name
)

self._instance_name: str = (
    f"{self._name}-"
    f"{self._id[:8]}"
)
# ==============================================================================
# Part 6.4 – Components
# ==============================================================================

#
# ------------------------------------------------------------------------------
# Trace Manager
# ------------------------------------------------------------------------------

self._manager: TraceManager = manager

#
# ------------------------------------------------------------------------------
# Active Tracer
# ------------------------------------------------------------------------------

self._tracer: Optional[TraceTracer] = None

if hasattr(
    self._manager,
    "current_tracer",
):

    try:

        self._tracer = (
            self._manager.current_tracer()
        )

    except Exception:

        self._tracer = None

#
# ------------------------------------------------------------------------------
# Trace Context
# ------------------------------------------------------------------------------

self._context: TraceContext = (

    context

    if context is not None

    else (

        self._tracer.context

        if (

            self._tracer is not None

            and hasattr(
                self._tracer,
                "context",
            )

        )

        else TraceContext()

    )

)

#
# ------------------------------------------------------------------------------
# Active Trace
# ------------------------------------------------------------------------------

self._trace: Optional[
    TraceSpan
] = None

if (

    self._tracer is not None

    and hasattr(
        self._tracer,
        "current_trace",
    )

):

    try:

        self._trace = (
            self._tracer.current_trace()
        )

    except Exception:

        self._trace = None

#
# ------------------------------------------------------------------------------
# Active Span
# ------------------------------------------------------------------------------

self._span: Optional[
    TraceSpan
] = None

#
# ------------------------------------------------------------------------------
# Parent Span
# ------------------------------------------------------------------------------

self._parent_span: Optional[
    TraceSpan
] = parent

if (

    self._parent_span is None

    and self._tracer is not None

    and hasattr(
        self._tracer,
        "current_span",
    )

):

    try:

        self._parent_span = (
            self._tracer.current_span()
        )

    except Exception:

        self._parent_span = None
# ==============================================================================
# Part 6.5 – Configuration
# ==============================================================================

#
# ------------------------------------------------------------------------------
# Enabled
# ------------------------------------------------------------------------------

self._enabled: bool = bool(
    enabled,
)

#
# ------------------------------------------------------------------------------
# Automatic lifecycle
# ------------------------------------------------------------------------------

self._auto_start: bool = bool(
    auto_start,
)

self._auto_finish: bool = bool(
    auto_finish,
)

#
# ------------------------------------------------------------------------------
# Runtime timeout
# ------------------------------------------------------------------------------

self._timeout: float = max(
    0.0,
    float(timeout),
)

#
# ------------------------------------------------------------------------------
# History limit
# ------------------------------------------------------------------------------

self._history_limit: int = max(
    1,
    int(history_limit),
)

#
# ------------------------------------------------------------------------------
# Serialization encoding
# ------------------------------------------------------------------------------

self._encoding: str = str(
    encoding,
)

#
# ------------------------------------------------------------------------------
# Runtime options
# ------------------------------------------------------------------------------

self._options: Dict[
    str,
    Any,
] = (

    copy.deepcopy(
        options,
    )

    if options is not None

    else {}

)

#
# ------------------------------------------------------------------------------
# Default runtime configuration
# ------------------------------------------------------------------------------

self._options.setdefault(
    "record_exceptions",
    True,
)

self._options.setdefault(
    "record_return_value",
    False,
)

self._options.setdefault(
    "record_arguments",
    False,
)

self._options.setdefault(
    "notify_callbacks",
    True,
)

self._options.setdefault(
    "notify_hooks",
    True,
)

self._options.setdefault(
    "notify_subscribers",
    True,
)

self._options.setdefault(
    "collect_statistics",
    True,
)

self._options.setdefault(
    "enable_history",
    True,
)

self._options.setdefault(
    "enable_cache",
    True,
)

self._options.setdefault(
    "validate_on_enter",
    True,
)

self._options.setdefault(
    "validate_on_exit",
    False,
)

#
# ------------------------------------------------------------------------------
# Capabilities
# ------------------------------------------------------------------------------

self._capabilities: Set[str] = {
    "context_manager",
    "decorator",
    "runtime_api",
    "callbacks",
    "hooks",
    "statistics",
    "history",
    "metadata",
    "thread_safe",
}

#
# ------------------------------------------------------------------------------
# Configuration validation
# ------------------------------------------------------------------------------

if self._history_limit <= 0:

    raise ValueError(
        "history_limit must be greater than zero."
    )

if self._timeout < 0:

    raise ValueError(
        "timeout cannot be negative."
    )

if not self._encoding:

    raise ValueError(
        "encoding cannot be empty."
    )
# ==============================================================================
# Part 6.6 – Runtime State
# ==============================================================================

#
# ------------------------------------------------------------------------------
# Initialization State
# ------------------------------------------------------------------------------

self._initialized: bool = True

#
# ------------------------------------------------------------------------------
# Execution State
# ------------------------------------------------------------------------------

self._running: bool = False

self._active: bool = False

self._entered: bool = False

self._exited: bool = False

#
# ------------------------------------------------------------------------------
# Lifecycle State
# ------------------------------------------------------------------------------

self._frozen: bool = False

self._closed: bool = False

self._disposed: bool = False

#
# ------------------------------------------------------------------------------
# Runtime Status
# ------------------------------------------------------------------------------

self._state: ScopeState = ScopeState.CREATED

self._status: ScopeStatus = (
    ScopeStatus.IDLE
)

#
# ------------------------------------------------------------------------------
# Runtime Timestamps
# ------------------------------------------------------------------------------

_now = time.time()

self._created_at: float = _now

self._updated_at: float = _now

self._start_time: Optional[
    float
] = None

self._end_time: Optional[
    float
] = None

#
# ------------------------------------------------------------------------------
# Runtime Duration
# ------------------------------------------------------------------------------

self._duration: float = 0.0

self._last_duration: float = 0.0

self._total_duration: float = 0.0

#
# ------------------------------------------------------------------------------
# Runtime Flags
# ------------------------------------------------------------------------------

self._cancelled: bool = False

self._failed: bool = False

self._completed: bool = False

self._successful: bool = False

#
# ------------------------------------------------------------------------------
# Nested Runtime State
# ------------------------------------------------------------------------------

self._depth: int = 0

self._nesting_level: int = 0

self._reentrant: bool = False

#
# ------------------------------------------------------------------------------
# Runtime Validation
# ------------------------------------------------------------------------------

if self._closed:

    self._state = ScopeState.CLOSED

    self._status = ScopeStatus.CLOSED

elif self._frozen:

    self._state = ScopeState.FROZEN

    self._status = ScopeStatus.FROZEN

elif self._running:

    self._state = ScopeState.RUNNING

    self._status = ScopeStatus.ACTIVE

else:

    self._state = ScopeState.CREATED

    self._status = ScopeStatus.IDLE
# ==============================================================================
# Part 6.7 – Statistics
# ==============================================================================

#
# ------------------------------------------------------------------------------
# Runtime Statistics Object
# ------------------------------------------------------------------------------

self._statistics = ScopeStatistics()

#
# ------------------------------------------------------------------------------
# Basic Counters
# ------------------------------------------------------------------------------

self._statistics.enter_count = 0

self._statistics.exit_count = 0

self._statistics.success_count = 0

self._statistics.failure_count = 0

self._statistics.exception_count = 0

self._statistics.cancelled_count = 0

#
# ------------------------------------------------------------------------------
# Nested / Reentrant Statistics
# ------------------------------------------------------------------------------

self._statistics.nested_count = 0

self._statistics.reentrant_count = 0

#
# ------------------------------------------------------------------------------
# Runtime Statistics
# ------------------------------------------------------------------------------

self._statistics.update_count = 0

self._statistics.validation_count = 0

self._statistics.callback_count = 0

self._statistics.hook_count = 0

self._statistics.notification_count = 0

#
# ------------------------------------------------------------------------------
# Timing Statistics
# ------------------------------------------------------------------------------

self._statistics.total_duration = 0.0

self._statistics.average_duration = 0.0

self._statistics.minimum_duration = 0.0

self._statistics.maximum_duration = 0.0

self._statistics.last_duration = 0.0

#
# ------------------------------------------------------------------------------
# Timestamp Statistics
# ------------------------------------------------------------------------------

_now = time.time()

self._statistics.created_at = _now

self._statistics.updated_at = _now

#
# ------------------------------------------------------------------------------
# Success / Failure Ratios
# ------------------------------------------------------------------------------

self._statistics.success_rate = 0.0

self._statistics.failure_rate = 0.0

self._statistics.exception_rate = 0.0

#
# ------------------------------------------------------------------------------
# Internal Statistic Cache
# ------------------------------------------------------------------------------

self._statistics_cache: Dict[
    str,
    Any,
] = {}

#
# ------------------------------------------------------------------------------
# Statistic Flags
# ------------------------------------------------------------------------------

self._statistics_enabled: bool = True

self._statistics_dirty: bool = False

#
# ------------------------------------------------------------------------------
# Statistic Validation
# ------------------------------------------------------------------------------

if self._statistics.enter_count < 0:

    self._statistics.enter_count = 0

if self._statistics.exit_count < 0:

    self._statistics.exit_count = 0

if self._statistics.success_count < 0:

    self._statistics.success_count = 0

if self._statistics.failure_count < 0:

    self._statistics.failure_count = 0

if self._statistics.exception_count < 0:

    self._statistics.exception_count = 0

if self._statistics.cancelled_count < 0:

    self._statistics.cancelled_count = 0
# ==============================================================================
# Part 6.8 – Metadata
# ==============================================================================

#
# ------------------------------------------------------------------------------
# User Metadata
# ------------------------------------------------------------------------------

self._metadata: Dict[
    str,
    Any,
] = (

    copy.deepcopy(
        metadata,
    )

    if metadata is not None

    else {}

)

#
# ------------------------------------------------------------------------------
# Span Attributes
# ------------------------------------------------------------------------------

self._attributes: Dict[
    str,
    Any,
] = (

    copy.deepcopy(
        attributes,
    )

    if attributes is not None

    else {}

)

#
# ------------------------------------------------------------------------------
# Tags
# ------------------------------------------------------------------------------

self._tags: Set[str] = (

    set(tags)

    if tags is not None

    else set()

)

#
# ------------------------------------------------------------------------------
# Labels
# ------------------------------------------------------------------------------

self._labels: Dict[
    str,
    str,
] = {}

#
# ------------------------------------------------------------------------------
# Notes
# ------------------------------------------------------------------------------

self._notes: List[str] = []

#
# ------------------------------------------------------------------------------
# Runtime History
# ------------------------------------------------------------------------------

self._history = deque(
    maxlen=self._history_limit,
)

#
# ------------------------------------------------------------------------------
# Runtime Cache
# ------------------------------------------------------------------------------

self._cache: Dict[
    str,
    Any,
] = {}

#
# ------------------------------------------------------------------------------
# Runtime Data
# ------------------------------------------------------------------------------

self._runtime_data: Dict[
    str,
    Any,
] = {

    #
    # Identity
    #

    "scope_id": self._id,

    "scope_uuid": str(
        self._uuid,
    ),

    "scope_name": self._name,

    #
    # Runtime
    #

    "entered": False,

    "exited": False,

    "running": False,

    "active": False,

    "successful": False,

    "failed": False,

    "cancelled": False,

    "completed": False,

    #
    # Timing
    #

    "start_time": None,

    "end_time": None,

    "duration": 0.0,

}

#
# ------------------------------------------------------------------------------
# Extensions
# ------------------------------------------------------------------------------

self._extensions: Dict[
    str,
    Any,
] = {}

#
# ------------------------------------------------------------------------------
# Default Metadata
# ------------------------------------------------------------------------------

self._metadata.setdefault(
    "created_by",
    "SpanScope",
)

self._metadata.setdefault(
    "version",
    self._version,
)

self._metadata.setdefault(
    "scope_type",
    self._scope_type.value,
)

#
# ------------------------------------------------------------------------------
# Default Attributes
# ------------------------------------------------------------------------------

self._attributes.setdefault(
    "scope.name",
    self._name,
)

self._attributes.setdefault(
    "scope.id",
    self._id,
)

self._attributes.setdefault(
    "scope.uuid",
    str(self._uuid),
)

self._attributes.setdefault(
    "scope.type",
    self._scope_type.value,
)

#
# ------------------------------------------------------------------------------
# Internal Labels
# ------------------------------------------------------------------------------

self._labels.setdefault(
    "state",
    self._state.value,
)

self._labels.setdefault(
    "status",
    self._status.value,
)

#
# ------------------------------------------------------------------------------
# Extension Registration
# ------------------------------------------------------------------------------

self._extensions["metadata"] = (
    self._metadata
)

self._extensions["attributes"] = (
    self._attributes
)

self._extensions["runtime"] = (
    self._runtime_data
)

#
# ------------------------------------------------------------------------------
# Metadata Validation
# ------------------------------------------------------------------------------

if not isinstance(
    self._metadata,
    dict,
):

    raise TypeError(
        "metadata must be a dictionary."
    )

if not isinstance(
    self._attributes,
    dict,
):

    raise TypeError(
        "attributes must be a dictionary."
    )

if not isinstance(
    self._tags,
    set,
):

    raise TypeError(
        "tags must be a set."
    )
# ==============================================================================
# Part 6.9 – Runtime Objects
# ==============================================================================

#
# ------------------------------------------------------------------------------
# Runtime Callbacks
# ------------------------------------------------------------------------------

self._callbacks: List[
    TraceCallback
] = []

#
# ------------------------------------------------------------------------------
# Runtime Hooks
# ------------------------------------------------------------------------------

self._hooks: Dict[
    HookName,
    List[TraceHook],
] = {}

#
# ------------------------------------------------------------------------------
# Runtime Filters
# ------------------------------------------------------------------------------

self._filters: List[
    Callable[..., bool]
] = []

#
# ------------------------------------------------------------------------------
# Runtime Subscribers
# ------------------------------------------------------------------------------

self._subscribers: List[
    Callable[..., Any]
] = []

#
# ------------------------------------------------------------------------------
# Logger
# ------------------------------------------------------------------------------

self._logger = logging.getLogger(
    LOGGER_NAME,
)

#
# ------------------------------------------------------------------------------
# Synchronization Lock
# ------------------------------------------------------------------------------

self._lock = RLock()

#
# ------------------------------------------------------------------------------
# Thread-Local Storage
# ------------------------------------------------------------------------------

self._thread_local = (
    threading.local()
)

#
# ------------------------------------------------------------------------------
# Process Identifier
# ------------------------------------------------------------------------------

try:

    import os

    self._process_id: int = (
        os.getpid()
    )

except Exception:

    self._process_id = -1

#
# ------------------------------------------------------------------------------
# Thread Identifier
# ------------------------------------------------------------------------------

self._thread_id: int = (
    threading.get_ident()
)

#
# ------------------------------------------------------------------------------
# Runtime Event Queue
# ------------------------------------------------------------------------------

self._event_queue: deque[
    Dict[str, Any]
] = deque()

#
# ------------------------------------------------------------------------------
# Deferred Tasks
# ------------------------------------------------------------------------------

self._pending_tasks: List[
    Callable[..., Any]
] = []

#
# ------------------------------------------------------------------------------
# Runtime Context Stack
# ------------------------------------------------------------------------------

self._context_stack: List[
    TraceContext
] = []

#
# ------------------------------------------------------------------------------
# Active Runtime Resources
# ------------------------------------------------------------------------------

self._resources: Dict[
    str,
    Any,
] = {}

#
# ------------------------------------------------------------------------------
# Object Registration
# ------------------------------------------------------------------------------

self._resources["callbacks"] = (
    self._callbacks
)

self._resources["hooks"] = (
    self._hooks
)

self._resources["filters"] = (
    self._filters
)

self._resources["subscribers"] = (
    self._subscribers
)

self._resources["thread_local"] = (
    self._thread_local
)

#
# ------------------------------------------------------------------------------
# Runtime Validation
# ------------------------------------------------------------------------------

if self._logger is None:

    raise RuntimeError(
        "Logger initialization failed."
    )

if self._lock is None:

    raise RuntimeError(
        "Lock initialization failed."
    )
# ==============================================================================
# Part 6.10 – Final Initialization
# ==============================================================================

#
# ------------------------------------------------------------------------------
# Initialize Runtime Objects
# ------------------------------------------------------------------------------

#
# Runtime object registry
#

self._object_registry: Dict[
    str,
    Any,
] = {

    "manager": self._manager,

    "tracer": self._tracer,

    "context": self._context,

    "logger": self._logger,

    "lock": self._lock,

    "thread_local": self._thread_local,

    "statistics": self._statistics,

    "metadata": self._metadata,

    "attributes": self._attributes,

    "runtime_data": self._runtime_data,

}

#
# Runtime initialization marker
#

self._runtime_data["initialized"] = True

self._runtime_data["initialization_time"] = (
    time.time()
)

#
# ------------------------------------------------------------------------------
# Set Initial Runtime State
# ------------------------------------------------------------------------------

if self._closed:

    self._state = ScopeState.CLOSED

    self._status = ScopeStatus.CLOSED

elif self._disposed:

    self._state = ScopeState.DISPOSED

    self._status = ScopeStatus.DISPOSED

elif self._frozen:

    self._state = ScopeState.FROZEN

    self._status = ScopeStatus.FROZEN

elif self._running:

    self._state = ScopeState.RUNNING

    self._status = ScopeStatus.ACTIVE

elif self._enabled:

    self._state = ScopeState.CREATED

    self._status = ScopeStatus.IDLE

else:

    self._state = ScopeState.DISABLED

    self._status = ScopeStatus.DISABLED

#
# Synchronize runtime metadata
#

self._runtime_data["state"] = (
    self._state.value
)

self._runtime_data["status"] = (
    self._status.value
)

#
# ------------------------------------------------------------------------------
# Validation
# ------------------------------------------------------------------------------

self.validate()

#
# ------------------------------------------------------------------------------
# Logger
# ------------------------------------------------------------------------------

if self._logger.isEnabledFor(
    logging.DEBUG,
):

    self._logger.debug(

        (
            "SpanScope initialized "
            "(id=%s, "
            "name=%s, "
            "state=%s, "
            "status=%s)"
        ),

        self._id,

        self._name,

        self._state.value,

        self._status.value,

    )

#
# ------------------------------------------------------------------------------
# Final Timestamp
# ------------------------------------------------------------------------------

self.touch()

#
# ------------------------------------------------------------------------------
# Initialization Complete
# ------------------------------------------------------------------------------

self._initialized = True
# ==============================================================================
# Part 7.1 – Identity
# ==============================================================================

@property
def id(self) -> str:
    """
    Unique identifier of this SpanScope.
    """
    return self._id


@property
def uuid(self) -> uuid.UUID:
    """
    Universally unique identifier.
    """
    return self._uuid


@property
def name(self) -> str:
    """
    Human-readable scope name.
    """
    return self._name


@property
def description(self) -> str:
    """
    Scope description.
    """
    return self._description


@property
def version(self) -> str:
    """
    Runtime version.
    """
    return self._version


@property
def scope_type(self) -> ScopeType:
    """
    Scope type.

    Returns
    -------
    ScopeType
        Usually ScopeType.SPAN.
    """
    return self._scope_type
# ==============================================================================
# Part 7.2 – Components
# ==============================================================================

@property
def manager(self) -> TraceManager:
    """
    Trace manager associated with this SpanScope.

    Returns
    -------
    TraceManager
        Active TraceManager.
    """
    return self._manager


@property
def tracer(self) -> Optional[TraceTracer]:
    """
    Active TraceTracer.

    Returns
    -------
    Optional[TraceTracer]
        Current tracer, or None if unavailable.
    """
    return self._tracer


@property
def context(self) -> TraceContext:
    """
    Trace context associated with this scope.

    Returns
    -------
    TraceContext
    """
    return self._context


@property
def trace(self) -> Optional[TraceSpan]:
    """
    Current root trace.

    Returns
    -------
    Optional[TraceSpan]
        Root trace span, if available.
    """
    return self._trace


@property
def span(self) -> Optional[TraceSpan]:
    """
    Managed runtime span.

    Returns
    -------
    Optional[TraceSpan]
        Current span owned by this SpanScope.
    """
    return self._span


@property
def parent_span(self) -> Optional[TraceSpan]:
    """
    Parent span.

    Returns
    -------
    Optional[TraceSpan]
        Parent of the managed span.
    """
    return self._parent_span
# ==============================================================================
# Part 7.3 – Configuration
# ==============================================================================

@property
def enabled(self) -> bool:
    """
    Whether this SpanScope is enabled.
    """
    return self._enabled


@property
def auto_start(self) -> bool:
    """
    Whether the span is automatically started when entering the scope.
    """
    return self._auto_start


@property
def auto_finish(self) -> bool:
    """
    Whether the span is automatically finished when leaving the scope.
    """
    return self._auto_finish


@property
def timeout(self) -> float:
    """
    Runtime timeout in seconds.
    """
    return self._timeout


@property
def history_limit(self) -> int:
    """
    Maximum history capacity.
    """
    return self._history_limit


@property
def encoding(self) -> str:
    """
    Default serialization encoding.
    """
    return self._encoding


@property
def options(self) -> Mapping[str, Any]:
    """
    Runtime configuration options.

    Returns
    -------
    Mapping[str, Any]
        Read-only runtime options.
    """
    return self._options


@property
def capabilities(self) -> frozenset[str]:
    """
    Supported SpanScope capabilities.

    Returns
    -------
    frozenset[str]
        Immutable capability set.
    """
    return frozenset(
        self._capabilities
    )
# ==============================================================================
# Part 7.4 – Runtime State
# ==============================================================================

@property
def initialized(self) -> bool:
    """
    Whether the SpanScope has been initialized.
    """
    return self._initialized


@property
def running(self) -> bool:
    """
    Whether the scope is currently running.
    """
    return self._running


@property
def active(self) -> bool:
    """
    Whether the scope is currently active.
    """
    return self._active


@property
def entered(self) -> bool:
    """
    Whether the scope has been entered.
    """
    return self._entered


@property
def exited(self) -> bool:
    """
    Whether the scope has already exited.
    """
    return self._exited


@property
def frozen(self) -> bool:
    """
    Whether runtime execution is frozen.
    """
    return self._frozen


@property
def closed(self) -> bool:
    """
    Whether the scope has been closed.
    """
    return self._closed


@property
def disposed(self) -> bool:
    """
    Whether the scope has been disposed.
    """
    return self._disposed


@property
def state(self) -> ScopeState:
    """
    Current lifecycle state.
    """
    return self._state


@property
def status(self) -> ScopeStatus:
    """
    Current runtime status.
    """
    return self._status


@property
def created_at(self) -> float:
    """
    Creation timestamp (Unix time).
    """
    return self._created_at


@property
def updated_at(self) -> float:
    """
    Last update timestamp.
    """
    return self._updated_at


@property
def start_time(self) -> Optional[float]:
    """
    Scope start timestamp.
    """
    return self._start_time


@property
def end_time(self) -> Optional[float]:
    """
    Scope end timestamp.
    """
    return self._end_time


@property
def duration(self) -> float:
    """
    Latest execution duration.

    If the scope is still running, the duration is calculated
    dynamically from the current time.
    """

    if (
        self._running
        and self._start_time is not None
    ):
        return (
            time.time()
            - self._start_time
        )

    return self._duration


@property
def uptime(self) -> float:
    """
    Object lifetime since creation.
    """
    return (
        time.time()
        - self._created_at
    )
# ==============================================================================
# Part 7.5 – Statistics
# ==============================================================================

@property
def statistics(
    self,
) -> ScopeStatistics:
    """
    Runtime statistics object.

    Returns
    -------
    ScopeStatistics
        Internal statistics container.
    """
    return self._statistics


@property
def enter_count(
    self,
) -> int:
    """
    Number of successful enter operations.
    """
    return self._statistics.enter_count


@property
def exit_count(
    self,
) -> int:
    """
    Number of successful exit operations.
    """
    return self._statistics.exit_count


@property
def success_count(
    self,
) -> int:
    """
    Number of successful executions.
    """
    return self._statistics.success_count


@property
def failure_count(
    self,
) -> int:
    """
    Number of failed executions.
    """
    return self._statistics.failure_count


@property
def exception_count(
    self,
) -> int:
    """
    Number of recorded exceptions.
    """
    return self._statistics.exception_count


@property
def cancelled_count(
    self,
) -> int:
    """
    Number of cancelled executions.
    """
    return self._statistics.cancelled_count


@property
def nested_count(
    self,
) -> int:
    """
    Number of nested scope executions.
    """
    return self._statistics.nested_count


@property
def reentrant_count(
    self,
) -> int:
    """
    Number of reentrant executions.
    """
    return self._statistics.reentrant_count


@property
def success_rate(
    self,
) -> float:
    """
    Success ratio.

    Returns
    -------
    float
        Value in range [0.0, 1.0].
    """

    total = (
        self.success_count
        + self.failure_count
        + self.cancelled_count
    )

    if total == 0:
        return 1.0

    return (
        self.success_count
        / total
    )


@property
def failure_rate(
    self,
) -> float:
    """
    Failure ratio.

    Returns
    -------
    float
        Value in range [0.0, 1.0].
    """

    total = (
        self.success_count
        + self.failure_count
        + self.cancelled_count
    )

    if total == 0:
        return 0.0

    return (
        self.failure_count
        / total
    )
# ==============================================================================
# Part 7.6 – Metadata
# ==============================================================================

@property
def metadata(
    self,
) -> Mapping[str, Any]:
    """
    User-defined metadata.

    Returns
    -------
    Mapping[str, Any]
        Read-only metadata mapping.
    """
    return self._metadata


@property
def attributes(
    self,
) -> Mapping[str, Any]:
    """
    Span attributes.

    Returns
    -------
    Mapping[str, Any]
        Read-only attribute mapping.
    """
    return self._attributes


@property
def tags(
    self,
) -> frozenset[str]:
    """
    Runtime tags.

    Returns
    -------
    frozenset[str]
        Immutable tag collection.
    """
    return frozenset(
        self._tags
    )


@property
def labels(
    self,
) -> Mapping[str, str]:
    """
    Runtime labels.

    Returns
    -------
    Mapping[str, str]
        Read-only label mapping.
    """
    return self._labels


@property
def notes(
    self,
) -> tuple[str, ...]:
    """
    Runtime notes.

    Returns
    -------
    tuple[str, ...]
        Immutable notes.
    """
    return tuple(
        self._notes
    )


@property
def history(
    self,
) -> tuple[Any, ...]:
    """
    Runtime execution history.

    Returns
    -------
    tuple
        Immutable history records.
    """
    return tuple(
        self._history
    )


@property
def cache(
    self,
) -> Mapping[str, Any]:
    """
    Runtime cache.

    Returns
    -------
    Mapping[str, Any]
        Read-only cache.
    """
    return self._cache


@property
def runtime_data(
    self,
) -> Mapping[str, Any]:
    """
    Runtime state information.

    Returns
    -------
    Mapping[str, Any]
        Read-only runtime data.
    """
    return self._runtime_data


@property
def extensions(
    self,
) -> Mapping[str, Any]:
    """
    Registered runtime extensions.

    Returns
    -------
    Mapping[str, Any]
        Read-only extension registry.
    """
    return self._extensions
# ==============================================================================
# Part 7.7 – Runtime Objects
# ==============================================================================

@property
def callbacks(
    self,
) -> tuple[TraceCallback, ...]:
    """
    Registered runtime callbacks.

    Returns
    -------
    tuple[TraceCallback, ...]
        Immutable callback collection.
    """
    return tuple(
        self._callbacks
    )


@property
def hooks(
    self,
) -> Mapping[
    HookName,
    Sequence[TraceHook],
]:
    """
    Registered runtime hooks.

    Returns
    -------
    Mapping[HookName, Sequence[TraceHook]]
        Read-only hook registry.
    """
    return self._hooks


@property
def filters(
    self,
) -> tuple[
    Callable[..., bool],
    ...
]:
    """
    Runtime filters.

    Returns
    -------
    tuple
        Immutable filter collection.
    """
    return tuple(
        self._filters
    )


@property
def subscribers(
    self,
) -> tuple[
    Callable[..., Any],
    ...
]:
    """
    Runtime subscribers.

    Returns
    -------
    tuple
        Immutable subscriber collection.
    """
    return tuple(
        self._subscribers
    )


@property
def logger(
    self,
) -> logging.Logger:
    """
    Runtime logger.

    Returns
    -------
    logging.Logger
    """
    return self._logger


@property
def lock(
    self,
) -> RLock:
    """
    Synchronization lock.

    Returns
    -------
    RLock
    """
    return self._lock


@property
def thread_local(
    self,
) -> threading.local:
    """
    Thread-local runtime storage.

    Returns
    -------
    threading.local
    """
    return self._thread_local


@property
def process_id(
    self,
) -> int:
    """
    Current operating-system process identifier.

    Returns
    -------
    int
    """
    return self._process_id


@property
def thread_id(
    self,
) -> int:
    """
    Thread identifier where this scope was created.

    Returns
    -------
    int
    """
    return self._thread_id


@property
def event_queue(
    self,
) -> tuple[
    Dict[str, Any],
    ...
]:
    """
    Pending runtime events.

    Returns
    -------
    tuple
        Immutable event queue snapshot.
    """
    return tuple(
        self._event_queue
    )


@property
def resources(
    self,
) -> Mapping[
    str,
    Any,
]:
    """
    Runtime resource registry.

    Returns
    -------
    Mapping[str, Any]
        Read-only runtime resources.
    """
    return self._resources
# ==============================================================================
# Part 8.1 – initialize()
# ==============================================================================

def initialize(
    self,
    *,
    force: bool = False,
) -> "SpanScope":
    """
    Initialize the SpanScope runtime.

    This method prepares the runtime state before the scope can be
    entered or started. Calling initialize() multiple times is safe.

    Parameters
    ----------
    force
        Reinitialize even if already initialized.

    Returns
    -------
    SpanScope
        Self.

    Raises
    ------
    SpanScopeError
        If the scope has already been disposed.
    """

    with self._lock:

        #
        # --------------------------------------------------------------
        # Validation
        # --------------------------------------------------------------
        #

        if self._disposed:

            raise SpanScopeError(
                "Cannot initialize a disposed SpanScope."
            )

        if self._initialized and not force:

            return self

        #
        # --------------------------------------------------------------
        # Runtime state
        # --------------------------------------------------------------
        #

        now = time.time()

        self._initialized = True
        self._running = False
        self._active = False
        self._entered = False
        self._exited = False

        self._cancelled = False
        self._failed = False
        self._completed = False
        self._successful = False

        self._start_time = None
        self._end_time = None
        self._duration = 0.0

        self._updated_at = now

        self._state = ScopeState.CREATED
        self._status = ScopeStatus.IDLE

        #
        # --------------------------------------------------------------
        # Runtime containers
        # --------------------------------------------------------------
        #

        self._history.clear()
        self._cache.clear()
        self._event_queue.clear()
        self._pending_tasks.clear()
        self._context_stack.clear()

        #
        # --------------------------------------------------------------
        # Runtime metadata
        # --------------------------------------------------------------
        #

        self._runtime_data.update(
            {
                "initialized": True,
                "running": False,
                "active": False,
                "entered": False,
                "exited": False,
                "cancelled": False,
                "failed": False,
                "completed": False,
                "successful": False,
                "state": self._state.value,
                "status": self._status.value,
                "initialization_time": now,
            }
        )

        #
        # --------------------------------------------------------------
        # Statistics
        # --------------------------------------------------------------
        #

        self._statistics.update_count += 1
        self._statistics.updated_at = now

        #
        # --------------------------------------------------------------
        # Logging
        # --------------------------------------------------------------
        #

        self._logger.debug(
            "SpanScope '%s' initialized.",
            self._name,
        )

        return self
# ==============================================================================
# Part 8.2 – enter()
# ==============================================================================

def enter(
    self,
) -> TraceSpan:
    """
    Enter the SpanScope.

    Initializes the runtime (if necessary), resolves the current
    TraceTracer, creates or activates the managed TraceSpan, updates
    runtime state and statistics, and returns the active span.

    Returns
    -------
    TraceSpan
        Active span managed by this SpanScope.

    Raises
    ------
    SpanScopeError
        If the scope cannot be entered.
    """

    with self._lock:

        #
        # ------------------------------------------------------------------
        # Validation
        # ------------------------------------------------------------------
        #

        self.validate()

        if self._closed:

            raise SpanScopeError(
                "Cannot enter a closed SpanScope."
            )

        if self._disposed:

            raise SpanScopeError(
                "Cannot enter a disposed SpanScope."
            )

        if self._entered and not self._reentrant:

            raise SpanScopeError(
                "SpanScope has already been entered."
            )

        #
        # ------------------------------------------------------------------
        # Initialization
        # ------------------------------------------------------------------
        #

        if not self._initialized:

            self.initialize()

        #
        # ------------------------------------------------------------------
        # Resolve tracer
        # ------------------------------------------------------------------
        #

        if self._tracer is None:

            self._tracer = (
                self._manager.current_tracer()
            )

        if self._tracer is None:

            raise SpanScopeError(
                "No active TraceTracer available."
            )

        #
        # ------------------------------------------------------------------
        # Auto start
        # ------------------------------------------------------------------
        #

        if self._auto_start:

            self.start()

        #
        # ------------------------------------------------------------------
        # Runtime state
        # ------------------------------------------------------------------
        #

        now = time.time()

        self._entered = True
        self._running = True
        self._active = True

        self._start_time = now
        self._updated_at = now

        self._state = ScopeState.RUNNING
        self._status = ScopeStatus.ACTIVE

        #
        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------
        #

        self._statistics.enter_count += 1
        self._statistics.update_count += 1
        self._statistics.updated_at = now

        #
        # ------------------------------------------------------------------
        # Runtime metadata
        # ------------------------------------------------------------------
        #

        self._runtime_data.update(
            {
                "entered": True,
                "running": True,
                "active": True,
                "start_time": now,
                "state": self._state.value,
                "status": self._status.value,
            }
        )

        #
        # ------------------------------------------------------------------
        # History
        # ------------------------------------------------------------------
        #

        self._history.append(
            {
                "event": "enter",
                "timestamp": now,
                "scope": self._name,
            }
        )

        #
        # ------------------------------------------------------------------
        # Notifications
        # ------------------------------------------------------------------
        #

        self.notify_callbacks(
            "enter",
            self,
        )

        self.notify_hooks(
            "enter",
            self,
        )

        self.notify_subscribers(
            "enter",
            self,
        )

        #
        # ------------------------------------------------------------------
        # Logging
        # ------------------------------------------------------------------
        #

        self._logger.debug(
            "SpanScope '%s' entered.",
            self._name,
        )

        return self._span


# ==============================================================================
# Part 8.2 – __enter__()
# ==============================================================================

def __enter__(
    self,
) -> TraceSpan:
    """
    Context-manager entry.

    Returns
    -------
    TraceSpan
        Active managed span.
    """
    return self.enter()
# ==============================================================================
# Part 8.3 – exit()
# ==============================================================================

def exit(
    self,
    exc_type: Optional[type[BaseException]] = None,
    exc_val: Optional[BaseException] = None,
    exc_tb: Optional[Any] = None,
) -> bool:
    """
    Leave the SpanScope.

    Parameters
    ----------
    exc_type
        Exception type raised inside the context.

    exc_val
        Exception instance.

    exc_tb
        Exception traceback.

    Returns
    -------
    bool
        Always False. Exceptions are never suppressed.

    Raises
    ------
    SpanScopeError
        If the scope is invalid.
    """

    with self._lock:

        #
        # ------------------------------------------------------------------
        # Validation
        # ------------------------------------------------------------------
        #

        self.validate()

        if self._disposed:

            raise SpanScopeError(
                "Cannot exit a disposed SpanScope."
            )

        if not self._entered:

            raise SpanScopeError(
                "SpanScope has not been entered."
            )

        if self._exited:

            return False

        now = time.time()

        #
        # ------------------------------------------------------------------
        # Exception handling
        # ------------------------------------------------------------------
        #

        if exc_type is not None:

            self._failed = True
            self._successful = False

            self.record_exception(
                exc_type,
                exc_val,
                exc_tb,
            )

        else:

            self._successful = True
            self._failed = False

        #
        # ------------------------------------------------------------------
        # Auto finish
        # ------------------------------------------------------------------
        #

        if self._auto_finish:

            self.finish()

        #
        # ------------------------------------------------------------------
        # Runtime state
        # ------------------------------------------------------------------
        #

        self._running = False
        self._active = False

        self._entered = False
        self._exited = True

        self._completed = True

        self._end_time = now
        self._updated_at = now

        if self._start_time is not None:

            self._duration = (
                now - self._start_time
            )

        self._state = ScopeState.COMPLETED
        self._status = ScopeStatus.COMPLETED

        #
        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------
        #

        self._statistics.exit_count += 1

        if self._successful:

            self._statistics.success_count += 1

        else:

            self._statistics.failure_count += 1

        self.record_duration(
            self._duration,
        )

        self.update_statistics()

        #
        # ------------------------------------------------------------------
        # Runtime metadata
        # ------------------------------------------------------------------
        #

        self._runtime_data.update(
            {
                "running": False,
                "active": False,
                "entered": False,
                "exited": True,
                "completed": True,
                "successful": self._successful,
                "failed": self._failed,
                "duration": self._duration,
                "end_time": now,
                "state": self._state.value,
                "status": self._status.value,
            }
        )

        #
        # ------------------------------------------------------------------
        # History
        # ------------------------------------------------------------------
        #

        self._history.append(
            {
                "event": "exit",
                "timestamp": now,
                "duration": self._duration,
                "success": self._successful,
            }
        )

        #
        # ------------------------------------------------------------------
        # Notifications
        # ------------------------------------------------------------------
        #

        self.notify_callbacks(
            "exit",
            self,
        )

        self.notify_hooks(
            "exit",
            self,
        )

        self.notify_subscribers(
            "exit",
            self,
        )

        #
        # ------------------------------------------------------------------
        # Logging
        # ------------------------------------------------------------------
        #

        self._logger.debug(
            "SpanScope '%s' exited "
            "(duration=%.6fs).",
            self._name,
            self._duration,
        )

        #
        # Never suppress exceptions
        #

        return False


# ==============================================================================
# Part 8.3 – __exit__()
# ==============================================================================

def __exit__(
    self,
    exc_type: Optional[type[BaseException]],
    exc_val: Optional[BaseException],
    exc_tb: Optional[Any],
) -> bool:
    """
    Context manager exit.

    Parameters
    ----------
    exc_type
        Exception type.

    exc_val
        Exception value.

    exc_tb
        Exception traceback.

    Returns
    -------
    bool
        Always False.
    """

    return self.exit(
        exc_type,
        exc_val,
        exc_tb,
    )
# ==============================================================================
# Part 8.4 – start()
# ==============================================================================

def start(
    self,
) -> TraceSpan:
    """
    Start the managed span.

    This method creates (or reuses) the TraceSpan associated with this
    SpanScope and registers it with the active TraceTracer.

    Returns
    -------
    TraceSpan
        Active runtime span.

    Raises
    ------
    SpanScopeError
        If no TraceTracer is available or the scope is invalid.
    """

    with self._lock:

        #
        # ------------------------------------------------------------------
        # Validation
        # ------------------------------------------------------------------
        #

        self.validate()

        if not self._enabled:

            raise SpanScopeError(
                "SpanScope is disabled."
            )

        if self._closed:

            raise SpanScopeError(
                "SpanScope has been closed."
            )

        if self._disposed:

            raise SpanScopeError(
                "SpanScope has been disposed."
            )

        #
        # ------------------------------------------------------------------
        # Resolve tracer
        # ------------------------------------------------------------------
        #

        if self._tracer is None:

            self._tracer = (
                self._manager.current_tracer()
            )

        if self._tracer is None:

            raise SpanScopeError(
                "No active TraceTracer."
            )

        #
        # ------------------------------------------------------------------
        # Already started
        # ------------------------------------------------------------------
        #

        if self._span is not None:

            return self._span

        #
        # ------------------------------------------------------------------
        # Resolve parent span
        # ------------------------------------------------------------------
        #

        if self._parent_span is None:

            if hasattr(
                self._tracer,
                "current_span",
            ):

                self._parent_span = (
                    self._tracer.current_span()
                )

        #
        # ------------------------------------------------------------------
        # Create span
        # ------------------------------------------------------------------
        #

        self._span = (
            self._tracer.start_span(
                name=self._name,
                parent=self._parent_span,
                attributes=self._attributes,
            )
        )

        #
        # ------------------------------------------------------------------
        # Runtime state
        # ------------------------------------------------------------------
        #

        now = time.time()

        self._running = True
        self._active = True

        self._start_time = now
        self._updated_at = now

        self._state = ScopeState.RUNNING
        self._status = ScopeStatus.ACTIVE

        #
        # ------------------------------------------------------------------
        # Runtime metadata
        # ------------------------------------------------------------------
        #

        self._runtime_data.update(
            {
                "running": True,
                "active": True,
                "start_time": now,
                "span_started": True,
            }
        )

        #
        # ------------------------------------------------------------------
        # History
        # ------------------------------------------------------------------
        #

        self._history.append(
            {
                "event": "start",
                "timestamp": now,
                "span": self._name,
            }
        )

        #
        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------
        #

        self._statistics.update_count += 1
        self._statistics.updated_at = now

        #
        # ------------------------------------------------------------------
        # Notifications
        # ------------------------------------------------------------------
        #

        self.notify_callbacks(
            "start",
            self,
        )

        self.notify_hooks(
            "start",
            self,
        )

        self.notify_subscribers(
            "start",
            self,
        )

        #
        # ------------------------------------------------------------------
        # Logging
        # ------------------------------------------------------------------
        #

        self._logger.debug(
            "Span '%s' started.",
            self._name,
        )

        return self._span


# ==============================================================================
# Part 8.4 – begin()
# ==============================================================================

def begin(
    self,
) -> TraceSpan:
    """
    Alias of start().

    Returns
    -------
    TraceSpan
        Active runtime span.
    """

    return self.start()
# ==============================================================================
# Part 8.5 – stop()
# ==============================================================================

def stop(
    self,
) -> Optional[TraceSpan]:
    """
    Stop the managed span.

    This method finalizes the active TraceSpan, records the execution
    duration, updates runtime state/statistics, and notifies all
    registered observers.

    Returns
    -------
    Optional[TraceSpan]
        Finished TraceSpan.

    Raises
    ------
    SpanScopeError
        If the scope has been disposed.
    """

    with self._lock:

        #
        # ------------------------------------------------------------------
        # Validation
        # ------------------------------------------------------------------
        #

        self.validate()

        if self._disposed:

            raise SpanScopeError(
                "Cannot stop a disposed SpanScope."
            )

        #
        # ------------------------------------------------------------------
        # Nothing to stop
        # ------------------------------------------------------------------
        #

        if self._span is None:

            return None

        now = time.time()

        #
        # ------------------------------------------------------------------
        # Finish span
        # ------------------------------------------------------------------
        #

        if self._tracer is not None:

            self._tracer.end_span(
                self._span,
            )

        #
        # ------------------------------------------------------------------
        # Runtime timing
        # ------------------------------------------------------------------
        #

        self._end_time = now
        self._updated_at = now

        if self._start_time is not None:

            self._duration = (
                now - self._start_time
            )

        #
        # ------------------------------------------------------------------
        # Runtime state
        # ------------------------------------------------------------------
        #

        self._running = False
        self._active = False
        self._completed = True

        self._state = ScopeState.COMPLETED
        self._status = ScopeStatus.COMPLETED

        #
        # ------------------------------------------------------------------
        # Runtime metadata
        # ------------------------------------------------------------------
        #

        self._runtime_data.update(
            {
                "running": False,
                "active": False,
                "completed": True,
                "duration": self._duration,
                "end_time": now,
                "state": self._state.value,
                "status": self._status.value,
            }
        )

        #
        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------
        #

        self.record_duration(
            self._duration,
        )

        self.update_statistics()

        #
        # ------------------------------------------------------------------
        # History
        # ------------------------------------------------------------------
        #

        self._history.append(
            {
                "event": "stop",
                "timestamp": now,
                "duration": self._duration,
            }
        )

        #
        # ------------------------------------------------------------------
        # Notifications
        # ------------------------------------------------------------------
        #

        self.notify_callbacks(
            "stop",
            self,
        )

        self.notify_hooks(
            "stop",
            self,
        )

        self.notify_subscribers(
            "stop",
            self,
        )

        #
        # ------------------------------------------------------------------
        # Logging
        # ------------------------------------------------------------------
        #

        self._logger.debug(
            "Span '%s' stopped "
            "(%.6fs).",
            self._name,
            self._duration,
        )

        finished_span = self._span

        self._span = None

        return finished_span


# ==============================================================================
# Part 8.5 – finish()
# ==============================================================================

def finish(
    self,
) -> Optional[TraceSpan]:
    """
    Alias of stop().

    Returns
    -------
    Optional[TraceSpan]
    """

    return self.stop()


# ==============================================================================
# Part 8.5 – end()
# ==============================================================================

def end(
    self,
) -> Optional[TraceSpan]:
    """
    Alias of stop().

    Returns
    -------
    Optional[TraceSpan]
    """

    return self.stop()
# ==============================================================================
# Part 8.6 – cancel()
# ==============================================================================

def cancel(
    self,
    reason: Optional[str] = None,
) -> bool:
    """
    Cancel the current SpanScope.

    The managed span is terminated immediately without being marked as a
    successful execution. Runtime state, metadata, statistics and
    notifications are updated accordingly.

    Parameters
    ----------
    reason
        Optional cancellation reason.

    Returns
    -------
    bool
        True if cancellation occurred, False if the scope had already
        finished.

    Raises
    ------
    SpanScopeError
        If the scope has been disposed.
    """

    with self._lock:

        #
        # ------------------------------------------------------------------
        # Validation
        # ------------------------------------------------------------------
        #

        self.validate()

        if self._disposed:

            raise SpanScopeError(
                "Cannot cancel a disposed SpanScope."
            )

        #
        # ------------------------------------------------------------------
        # Already completed
        # ------------------------------------------------------------------
        #

        if self._completed:

            return False

        now = time.time()

        #
        # ------------------------------------------------------------------
        # Finish active span
        # ------------------------------------------------------------------
        #

        if self._span is not None:

            try:

                if self._tracer is not None:

                    self._tracer.end_span(
                        self._span,
                    )

            finally:

                self._span = None

        #
        # ------------------------------------------------------------------
        # Timing
        # ------------------------------------------------------------------
        #

        self._end_time = now
        self._updated_at = now

        if self._start_time is not None:

            self._duration = (
                now - self._start_time
            )

        #
        # ------------------------------------------------------------------
        # Runtime state
        # ------------------------------------------------------------------
        #

        self._running = False
        self._active = False

        self._cancelled = True
        self._completed = True
        self._successful = False
        self._failed = False

        self._state = ScopeState.CANCELLED
        self._status = ScopeStatus.CANCELLED

        #
        # ------------------------------------------------------------------
        # Runtime metadata
        # ------------------------------------------------------------------
        #

        self._runtime_data.update(
            {
                "running": False,
                "active": False,
                "cancelled": True,
                "completed": True,
                "duration": self._duration,
                "end_time": now,
                "cancel_reason": reason,
                "state": self._state.value,
                "status": self._status.value,
            }
        )

        #
        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------
        #

        self._statistics.cancelled_count += 1

        self.record_duration(
            self._duration,
        )

        self.update_statistics()

        #
        # ------------------------------------------------------------------
        # History
        # ------------------------------------------------------------------
        #

        self._history.append(
            {
                "event": "cancel",
                "timestamp": now,
                "reason": reason,
                "duration": self._duration,
            }
        )

        #
        # ------------------------------------------------------------------
        # Notifications
        # ------------------------------------------------------------------
        #

        self.notify_callbacks(
            "cancel",
            self,
        )

        self.notify_hooks(
            "cancel",
            self,
        )

        self.notify_subscribers(
            "cancel",
            self,
        )

        #
        # ------------------------------------------------------------------
        # Logging
        # ------------------------------------------------------------------
        #

        self._logger.warning(
            "Span '%s' cancelled (%s).",
            self._name,
            reason or "no reason",
        )

        return True


# ==============================================================================
# Part 8.6 – abort()
# ==============================================================================

def abort(
    self,
    reason: Optional[str] = None,
) -> bool:
    """
    Alias of cancel().

    Parameters
    ----------
    reason
        Optional cancellation reason.

    Returns
    -------
    bool
    """

    return self.cancel(
        reason=reason,
    )
# ==============================================================================
# Part 8.7 – freeze()
# ==============================================================================

def freeze(
    self,
) -> "SpanScope":
    """
    Freeze this SpanScope.

    Freezing temporarily suspends runtime operations while preserving
    all runtime state and collected data.

    Returns
    -------
    SpanScope
        Self.

    Raises
    ------
    SpanScopeError
        If the scope has already been closed or disposed.
    """

    with self._lock:

        #
        # ------------------------------------------------------------------
        # Validation
        # ------------------------------------------------------------------
        #

        self.validate()

        if self._disposed:

            raise SpanScopeError(
                "Cannot freeze a disposed SpanScope."
            )

        if self._closed:

            raise SpanScopeError(
                "Cannot freeze a closed SpanScope."
            )

        if self._frozen:

            return self

        now = time.time()

        #
        # ------------------------------------------------------------------
        # Runtime state
        # ------------------------------------------------------------------
        #

        self._frozen = True

        self._state = ScopeState.FROZEN
        self._status = ScopeStatus.FROZEN

        self._updated_at = now

        #
        # ------------------------------------------------------------------
        # Runtime metadata
        # ------------------------------------------------------------------
        #

        self._runtime_data.update(
            {
                "frozen": True,
                "state": self._state.value,
                "status": self._status.value,
                "updated_at": now,
            }
        )

        #
        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------
        #

        self._statistics.update_count += 1
        self._statistics.updated_at = now

        #
        # ------------------------------------------------------------------
        # History
        # ------------------------------------------------------------------
        #

        self._history.append(
            {
                "event": "freeze",
                "timestamp": now,
            }
        )

        #
        # ------------------------------------------------------------------
        # Notifications
        # ------------------------------------------------------------------
        #

        self.notify_callbacks(
            "freeze",
            self,
        )

        self.notify_hooks(
            "freeze",
            self,
        )

        self.notify_subscribers(
            "freeze",
            self,
        )

        #
        # ------------------------------------------------------------------
        # Logging
        # ------------------------------------------------------------------
        #

        self._logger.debug(
            "SpanScope '%s' frozen.",
            self._name,
        )

        return self


# ==============================================================================
# Part 8.7 – unfreeze()
# ==============================================================================

def unfreeze(
    self,
) -> "SpanScope":
    """
    Resume execution after freeze().

    Returns
    -------
    SpanScope
        Self.

    Raises
    ------
    SpanScopeError
        If the scope has been disposed.
    """

    with self._lock:

        #
        # ------------------------------------------------------------------
        # Validation
        # ------------------------------------------------------------------
        #

        self.validate()

        if self._disposed:

            raise SpanScopeError(
                "Cannot unfreeze a disposed SpanScope."
            )

        if not self._frozen:

            return self

        now = time.time()

        #
        # ------------------------------------------------------------------
        # Runtime state
        # ------------------------------------------------------------------
        #

        self._frozen = False

        if self._running:

            self._state = ScopeState.RUNNING
            self._status = ScopeStatus.ACTIVE

        else:

            self._state = ScopeState.CREATED
            self._status = ScopeStatus.IDLE

        self._updated_at = now

        #
        # ------------------------------------------------------------------
        # Runtime metadata
        # ------------------------------------------------------------------
        #

        self._runtime_data.update(
            {
                "frozen": False,
                "state": self._state.value,
                "status": self._status.value,
                "updated_at": now,
            }
        )

        #
        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------
        #

        self._statistics.update_count += 1
        self._statistics.updated_at = now

        #
        # ------------------------------------------------------------------
        # History
        # ------------------------------------------------------------------
        #

        self._history.append(
            {
                "event": "unfreeze",
                "timestamp": now,
            }
        )

        #
        # ------------------------------------------------------------------
        # Notifications
        # ------------------------------------------------------------------
        #

        self.notify_callbacks(
            "unfreeze",
            self,
        )

        self.notify_hooks(
            "unfreeze",
            self,
        )

        self.notify_subscribers(
            "unfreeze",
            self,
        )

        #
        # ------------------------------------------------------------------
        # Logging
        # ------------------------------------------------------------------
        #

        self._logger.debug(
            "SpanScope '%s' unfrozen.",
            self._name,
        )

        return self
# ==============================================================================
# Part 8.8 – enable()
# ==============================================================================

def enable(
    self,
) -> "SpanScope":
    """
    Enable this SpanScope.

    Returns
    -------
    SpanScope
        Self.

    Raises
    ------
    SpanScopeError
        If the scope has been disposed.
    """

    with self._lock:

        #
        # ------------------------------------------------------------------
        # Validation
        # ------------------------------------------------------------------
        #

        self.validate()

        if self._disposed:

            raise SpanScopeError(
                "Cannot enable a disposed SpanScope."
            )

        if self._enabled:

            return self

        now = time.time()

        #
        # ------------------------------------------------------------------
        # Runtime state
        # ------------------------------------------------------------------
        #

        self._enabled = True

        if self._running:

            self._state = ScopeState.RUNNING
            self._status = ScopeStatus.ACTIVE

        elif self._frozen:

            self._state = ScopeState.FROZEN
            self._status = ScopeStatus.FROZEN

        else:

            self._state = ScopeState.CREATED
            self._status = ScopeStatus.IDLE

        self._updated_at = now

        #
        # ------------------------------------------------------------------
        # Runtime metadata
        # ------------------------------------------------------------------
        #

        self._runtime_data.update(
            {
                "enabled": True,
                "state": self._state.value,
                "status": self._status.value,
                "updated_at": now,
            }
        )

        #
        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------
        #

        self._statistics.update_count += 1
        self._statistics.updated_at = now

        #
        # ------------------------------------------------------------------
        # History
        # ------------------------------------------------------------------
        #

        self._history.append(
            {
                "event": "enable",
                "timestamp": now,
            }
        )

        #
        # ------------------------------------------------------------------
        # Notifications
        # ------------------------------------------------------------------
        #

        self.notify_callbacks(
            "enable",
            self,
        )

        self.notify_hooks(
            "enable",
            self,
        )

        self.notify_subscribers(
            "enable",
            self,
        )

        #
        # ------------------------------------------------------------------
        # Logging
        # ------------------------------------------------------------------
        #

        self._logger.info(
            "SpanScope '%s' enabled.",
            self._name,
        )

        return self


# ==============================================================================
# Part 8.8 – disable()
# ==============================================================================

def disable(
    self,
) -> "SpanScope":
    """
    Disable this SpanScope.

    While disabled, enter(), start(), and decorator execution are
    prevented until enable() is called.

    Returns
    -------
    SpanScope
        Self.

    Raises
    ------
    SpanScopeError
        If the scope has been disposed.
    """

    with self._lock:

        #
        # ------------------------------------------------------------------
        # Validation
        # ------------------------------------------------------------------
        #

        self.validate()

        if self._disposed:

            raise SpanScopeError(
                "Cannot disable a disposed SpanScope."
            )

        if not self._enabled:

            return self

        now = time.time()

        #
        # ------------------------------------------------------------------
        # Runtime state
        # ------------------------------------------------------------------
        #

        self._enabled = False

        self._state = ScopeState.DISABLED
        self._status = ScopeStatus.DISABLED

        self._updated_at = now

        #
        # ------------------------------------------------------------------
        # Runtime metadata
        # ------------------------------------------------------------------
        #

        self._runtime_data.update(
            {
                "enabled": False,
                "state": self._state.value,
                "status": self._status.value,
                "updated_at": now,
            }
        )

        #
        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------
        #

        self._statistics.update_count += 1
        self._statistics.updated_at = now

        #
        # ------------------------------------------------------------------
        # History
        # ------------------------------------------------------------------
        #

        self._history.append(
            {
                "event": "disable",
                "timestamp": now,
            }
        )

        #
        # ------------------------------------------------------------------
        # Notifications
        # ------------------------------------------------------------------
        #

        self.notify_callbacks(
            "disable",
            self,
        )

        self.notify_hooks(
            "disable",
            self,
        )

        self.notify_subscribers(
            "disable",
            self,
        )

        #
        # ------------------------------------------------------------------
        # Logging
        # ------------------------------------------------------------------
        #

        self._logger.info(
            "SpanScope '%s' disabled.",
            self._name,
        )

        return self
# ==============================================================================
# Part 8.9 – activate()
# ==============================================================================

def activate(
    self,
) -> "SpanScope":
    """
    Activate this SpanScope.

    Marks the scope as the current active runtime scope without creating
    a new TraceSpan. If a TraceTracer is available, the managed span is
    pushed into the tracer's active context.

    Returns
    -------
    SpanScope
        Self.

    Raises
    ------
    SpanScopeError
        If the scope cannot be activated.
    """

    with self._lock:

        #
        # ------------------------------------------------------------------
        # Validation
        # ------------------------------------------------------------------
        #

        self.validate()

        if self._disposed:

            raise SpanScopeError(
                "Cannot activate a disposed SpanScope."
            )

        if self._closed:

            raise SpanScopeError(
                "Cannot activate a closed SpanScope."
            )

        if not self._enabled:

            raise SpanScopeError(
                "Cannot activate a disabled SpanScope."
            )

        if self._active:

            return self

        now = time.time()

        #
        # ------------------------------------------------------------------
        # Runtime state
        # ------------------------------------------------------------------
        #

        self._active = True

        if self._running:

            self._state = ScopeState.RUNNING
            self._status = ScopeStatus.ACTIVE

        self._updated_at = now

        #
        # ------------------------------------------------------------------
        # Activate inside tracer
        # ------------------------------------------------------------------
        #

        if (
            self._tracer is not None
            and self._span is not None
            and hasattr(
                self._tracer,
                "activate_span",
            )
        ):

            self._tracer.activate_span(
                self._span,
            )

        #
        # ------------------------------------------------------------------
        # Runtime metadata
        # ------------------------------------------------------------------
        #

        self._runtime_data.update(
            {
                "active": True,
                "state": self._state.value,
                "status": self._status.value,
                "updated_at": now,
            }
        )

        #
        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------
        #

        self._statistics.update_count += 1
        self._statistics.updated_at = now

        #
        # ------------------------------------------------------------------
        # History
        # ------------------------------------------------------------------
        #

        self._history.append(
            {
                "event": "activate",
                "timestamp": now,
            }
        )

        #
        # ------------------------------------------------------------------
        # Notifications
        # ------------------------------------------------------------------
        #

        self.notify_callbacks(
            "activate",
            self,
        )

        self.notify_hooks(
            "activate",
            self,
        )

        self.notify_subscribers(
            "activate",
            self,
        )

        #
        # ------------------------------------------------------------------
        # Logging
        # ------------------------------------------------------------------
        #

        self._logger.debug(
            "SpanScope '%s' activated.",
            self._name,
        )

        return self


# ==============================================================================
# Part 8.9 – deactivate()
# ==============================================================================

def deactivate(
    self,
) -> "SpanScope":
    """
    Deactivate this SpanScope.

    Removes the scope from the active runtime context while preserving
    the managed TraceSpan and all collected runtime data.

    Returns
    -------
    SpanScope
        Self.

    Raises
    ------
    SpanScopeError
        If the scope has been disposed.
    """

    with self._lock:

        #
        # ------------------------------------------------------------------
        # Validation
        # ------------------------------------------------------------------
        #

        self.validate()

        if self._disposed:

            raise SpanScopeError(
                "Cannot deactivate a disposed SpanScope."
            )

        if not self._active:

            return self

        now = time.time()

        #
        # ------------------------------------------------------------------
        # Runtime state
        # ------------------------------------------------------------------
        #

        self._active = False

        if self._running:

            self._status = ScopeStatus.RUNNING

        else:

            self._status = ScopeStatus.IDLE

        self._updated_at = now

        #
        # ------------------------------------------------------------------
        # Remove from tracer
        # ------------------------------------------------------------------
        #

        if (
            self._tracer is not None
            and hasattr(
                self._tracer,
                "deactivate_span",
            )
        ):

            self._tracer.deactivate_span()

        #
        # ------------------------------------------------------------------
        # Runtime metadata
        # ------------------------------------------------------------------
        #

        self._runtime_data.update(
            {
                "active": False,
                "status": self._status.value,
                "updated_at": now,
            }
        )

        #
        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------
        #

        self._statistics.update_count += 1
        self._statistics.updated_at = now

        #
        # ------------------------------------------------------------------
        # History
        # ------------------------------------------------------------------
        #

        self._history.append(
            {
                "event": "deactivate",
                "timestamp": now,
            }
        )

        #
        # ------------------------------------------------------------------
        # Notifications
        # ------------------------------------------------------------------
        #

        self.notify_callbacks(
            "deactivate",
            self,
        )

        self.notify_hooks(
            "deactivate",
            self,
        )

        self.notify_subscribers(
            "deactivate",
            self,
        )

        #
        # ------------------------------------------------------------------
        # Logging
        # ------------------------------------------------------------------
        #

        self._logger.debug(
            "SpanScope '%s' deactivated.",
            self._name,
        )

        return self
# ==============================================================================
# Part 8.10 – close()
# ==============================================================================

def close(
    self,
) -> "SpanScope":
    """
    Close this SpanScope.

    Closing prevents any future runtime activity until ``reopen()`` is
    called. Existing runtime information is preserved.

    Returns
    -------
    SpanScope
        Self.

    Raises
    ------
    SpanScopeError
        If the scope has already been disposed.
    """

    with self._lock:

        #
        # ------------------------------------------------------------------
        # Validation
        # ------------------------------------------------------------------
        #

        self.validate()

        if self._disposed:

            raise SpanScopeError(
                "Cannot close a disposed SpanScope."
            )

        if self._closed:

            return self

        #
        # ------------------------------------------------------------------
        # Stop active span
        # ------------------------------------------------------------------
        #

        if self._running:

            self.stop()

        now = time.time()

        #
        # ------------------------------------------------------------------
        # Runtime state
        # ------------------------------------------------------------------
        #

        self._closed = True
        self._active = False
        self._running = False

        self._state = ScopeState.CLOSED
        self._status = ScopeStatus.CLOSED

        self._updated_at = now

        #
        # ------------------------------------------------------------------
        # Runtime metadata
        # ------------------------------------------------------------------
        #

        self._runtime_data.update(
            {
                "closed": True,
                "running": False,
                "active": False,
                "state": self._state.value,
                "status": self._status.value,
                "updated_at": now,
            }
        )

        #
        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------
        #

        self._statistics.update_count += 1
        self._statistics.updated_at = now

        #
        # ------------------------------------------------------------------
        # History
        # ------------------------------------------------------------------
        #

        self._history.append(
            {
                "event": "close",
                "timestamp": now,
            }
        )

        #
        # ------------------------------------------------------------------
        # Notifications
        # ------------------------------------------------------------------
        #

        self.notify_callbacks(
            "close",
            self,
        )

        self.notify_hooks(
            "close",
            self,
        )

        self.notify_subscribers(
            "close",
            self,
        )

        #
        # ------------------------------------------------------------------
        # Logging
        # ------------------------------------------------------------------
        #

        self._logger.info(
            "SpanScope '%s' closed.",
            self._name,
        )

        return self


# ==============================================================================
# Part 8.10 – reopen()
# ==============================================================================

def reopen(
    self,
) -> "SpanScope":
    """
    Reopen a previously closed SpanScope.

    Returns
    -------
    SpanScope
        Self.

    Raises
    ------
    SpanScopeError
        If the scope has already been disposed.
    """

    with self._lock:

        #
        # ------------------------------------------------------------------
        # Validation
        # ------------------------------------------------------------------
        #

        self.validate()

        if self._disposed:

            raise SpanScopeError(
                "Cannot reopen a disposed SpanScope."
            )

        if not self._closed:

            return self

        now = time.time()

        #
        # ------------------------------------------------------------------
        # Runtime state
        # ------------------------------------------------------------------
        #

        self._closed = False

        if self._enabled:

            self._state = ScopeState.CREATED
            self._status = ScopeStatus.IDLE

        else:

            self._state = ScopeState.DISABLED
            self._status = ScopeStatus.DISABLED

        self._updated_at = now

        #
        # ------------------------------------------------------------------
        # Runtime metadata
        # ------------------------------------------------------------------
        #

        self._runtime_data.update(
            {
                "closed": False,
                "state": self._state.value,
                "status": self._status.value,
                "updated_at": now,
            }
        )

        #
        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------
        #

        self._statistics.update_count += 1
        self._statistics.updated_at = now

        #
        # ------------------------------------------------------------------
        # History
        # ------------------------------------------------------------------
        #

        self._history.append(
            {
                "event": "reopen",
                "timestamp": now,
            }
        )

        #
        # ------------------------------------------------------------------
        # Notifications
        # ------------------------------------------------------------------
        #

        self.notify_callbacks(
            "reopen",
            self,
        )

        self.notify_hooks(
            "reopen",
            self,
        )

        self.notify_subscribers(
            "reopen",
            self,
        )

        #
        # ------------------------------------------------------------------
        # Logging
        # ------------------------------------------------------------------
        #

        self._logger.info(
            "SpanScope '%s' reopened.",
            self._name,
        )

        return self
# ==============================================================================
# Part 8.11 – dispose()
# ==============================================================================

def dispose(self) -> None:
    """
    Permanently dispose this SpanScope.

    Disposal is irreversible. All runtime objects are released,
    callbacks are removed, caches are cleared, and the scope becomes
    unusable.

    Raises
    ------
    SpanScopeError
        If disposal fails.
    """

    with self._lock:

        #
        # ------------------------------------------------------------------
        # Already disposed
        # ------------------------------------------------------------------
        #

        if self._disposed:
            return

        now = time.time()

        #
        # ------------------------------------------------------------------
        # Stop runtime if necessary
        # ------------------------------------------------------------------
        #

        try:

            if self._running:
                self.stop()

        except Exception:

            #
            # Best-effort cleanup.
            #
            pass

        #
        # ------------------------------------------------------------------
        # Runtime state
        # ------------------------------------------------------------------
        #

        self._disposed = True
        self._closed = True
        self._enabled = False

        self._running = False
        self._active = False
        self._entered = False
        self._exited = True
        self._frozen = False

        self._state = ScopeState.DISPOSED
        self._status = ScopeStatus.DISPOSED

        self._updated_at = now

        #
        # ------------------------------------------------------------------
        # Runtime metadata
        # ------------------------------------------------------------------
        #

        self._runtime_data.update(
            {
                "disposed": True,
                "closed": True,
                "enabled": False,
                "running": False,
                "active": False,
                "state": self._state.value,
                "status": self._status.value,
                "updated_at": now,
            }
        )

        #
        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------
        #

        self._statistics.update_count += 1
        self._statistics.updated_at = now

        #
        # ------------------------------------------------------------------
        # History
        # ------------------------------------------------------------------
        #

        self._history.append(
            {
                "event": "dispose",
                "timestamp": now,
            }
        )

        #
        # ------------------------------------------------------------------
        # Notifications
        # ------------------------------------------------------------------
        #

        try:

            self.notify_callbacks(
                "dispose",
                self,
            )

            self.notify_hooks(
                "dispose",
                self,
            )

            self.notify_subscribers(
                "dispose",
                self,
            )

        except Exception:

            pass

        #
        # ------------------------------------------------------------------
        # Release runtime objects
        # ------------------------------------------------------------------
        #

        self._span = None
        self._trace = None
        self._parent_span = None
        self._context = None

        self._callbacks.clear()
        self._hooks.clear()
        self._filters.clear()
        self._subscribers.clear()

        self._cache.clear()
        self._history.clear()
        self._event_queue.clear()
        self._pending_tasks.clear()
        self._context_stack.clear()
        self._resources.clear()

        #
        # ------------------------------------------------------------------
        # Logging
        # ------------------------------------------------------------------
        #

        try:

            self._logger.info(
                "SpanScope '%s' disposed.",
                self._name,
            )

        except Exception:

            pass
# ==============================================================================
# Part 8.12 – reset()
# ==============================================================================

def reset(
    self,
    *,
    clear_history: bool = True,
    clear_statistics: bool = False,
    clear_metadata: bool = False,
) -> "SpanScope":
    """
    Reset the SpanScope to its initial runtime state.

    Unlike dispose(), reset() preserves the object identity and allows
    the SpanScope to be reused.

    Parameters
    ----------
    clear_history
        Remove runtime history.

    clear_statistics
        Reset runtime statistics.

    clear_metadata
        Clear metadata, attributes, tags, labels and notes.

    Returns
    -------
    SpanScope
        Self.

    Raises
    ------
    SpanScopeError
        If the scope has already been disposed.
    """

    with self._lock:

        #
        # ------------------------------------------------------------------
        # Validation
        # ------------------------------------------------------------------
        #

        self.validate()

        if self._disposed:

            raise SpanScopeError(
                "Cannot reset a disposed SpanScope."
            )

        #
        # ------------------------------------------------------------------
        # Stop runtime
        # ------------------------------------------------------------------
        #

        if self._running:

            self.stop()

        now = time.time()

        #
        # ------------------------------------------------------------------
        # Runtime state
        # ------------------------------------------------------------------
        #

        self._running = False
        self._active = False
        self._entered = False
        self._exited = False

        self._cancelled = False
        self._completed = False
        self._successful = False
        self._failed = False

        self._frozen = False

        self._span = None
        self._parent_span = None

        self._start_time = None
        self._end_time = None
        self._duration = 0.0

        self._state = ScopeState.CREATED

        if self._enabled:

            self._status = ScopeStatus.IDLE

        else:

            self._status = ScopeStatus.DISABLED

        self._updated_at = now

        #
        # ------------------------------------------------------------------
        # Runtime containers
        # ------------------------------------------------------------------
        #

        self._cache.clear()
        self._event_queue.clear()
        self._pending_tasks.clear()
        self._context_stack.clear()

        if clear_history:

            self._history.clear()

        #
        # ------------------------------------------------------------------
        # Metadata
        # ------------------------------------------------------------------
        #

        if clear_metadata:

            self._metadata.clear()
            self._attributes.clear()
            self._tags.clear()
            self._labels.clear()
            self._notes.clear()
            self._extensions.clear()

        #
        # ------------------------------------------------------------------
        # Runtime data
        # ------------------------------------------------------------------
        #

        self._runtime_data.clear()

        self._runtime_data.update(
            {
                "running": False,
                "active": False,
                "entered": False,
                "exited": False,
                "completed": False,
                "cancelled": False,
                "successful": False,
                "failed": False,
                "state": self._state.value,
                "status": self._status.value,
                "updated_at": now,
            }
        )

        #
        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------
        #

        if clear_statistics:

            self._statistics.reset()

        else:

            self._statistics.update_count += 1
            self._statistics.updated_at = now

        #
        # ------------------------------------------------------------------
        # History
        # ------------------------------------------------------------------
        #

        self._history.append(
            {
                "event": "reset",
                "timestamp": now,
            }
        )

        #
        # ------------------------------------------------------------------
        # Notifications
        # ------------------------------------------------------------------
        #

        self.notify_callbacks(
            "reset",
            self,
        )

        self.notify_hooks(
            "reset",
            self,
        )

        self.notify_subscribers(
            "reset",
            self,
        )

        #
        # ------------------------------------------------------------------
        # Logging
        # ------------------------------------------------------------------
        #

        self._logger.info(
            "SpanScope '%s' reset.",
            self._name,
        )

        return self
# ==============================================================================
# Part 8.13 – touch()
# ==============================================================================

def touch(
    self,
    *,
    key: Optional[str] = None,
    value: Any = None,
) -> "SpanScope":
    """
    Refresh the runtime timestamp of this SpanScope.

    This method is intentionally lightweight. It updates the internal
    modification timestamp, optionally stores a runtime value, records
    the operation in history, updates statistics, and notifies runtime
    observers.

    Parameters
    ----------
    key
        Optional runtime-data key to update.

    value
        Value associated with ``key``.

    Returns
    -------
    SpanScope
        Self.

    Raises
    ------
    SpanScopeError
        If the scope has already been disposed.
    """

    with self._lock:

        #
        # ------------------------------------------------------------------
        # Validation
        # ------------------------------------------------------------------
        #

        self.validate()

        if self._disposed:

            raise SpanScopeError(
                "Cannot touch a disposed SpanScope."
            )

        now = time.time()

        #
        # ------------------------------------------------------------------
        # Runtime timestamps
        # ------------------------------------------------------------------
        #

        self._updated_at = now

        #
        # ------------------------------------------------------------------
        # Runtime data
        # ------------------------------------------------------------------
        #

        self._runtime_data["updated_at"] = now
        self._runtime_data["last_touch"] = now

        if key is not None:

            self._runtime_data[key] = value

        #
        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------
        #

        self._statistics.update_count += 1
        self._statistics.updated_at = now

        #
        # ------------------------------------------------------------------
        # History
        # ------------------------------------------------------------------
        #

        history_record = {
            "event": "touch",
            "timestamp": now,
        }

        if key is not None:

            history_record["key"] = key

        self._history.append(
            history_record
        )

        #
        # ------------------------------------------------------------------
        # Notifications
        # ------------------------------------------------------------------
        #

        self.notify_callbacks(
            "touch",
            self,
        )

        self.notify_hooks(
            "touch",
            self,
        )

        self.notify_subscribers(
            "touch",
            self,
        )

        #
        # ------------------------------------------------------------------
        # Logging
        # ------------------------------------------------------------------
        #

        if key is None:

            self._logger.debug(
                "SpanScope '%s' touched.",
                self._name,
            )

        else:

            self._logger.debug(
                "SpanScope '%s' touched (%s=%r).",
                self._name,
                key,
                value,
            )

        return self
# ==============================================================================
# Part 8.14 – validate()
# ==============================================================================

def validate(
    self,
) -> bool:
    """
    Validate the internal state of this SpanScope.

    This method performs consistency checks on the runtime state,
    configuration, timestamps, runtime objects and statistics.
    It raises an exception immediately if an invalid state is detected.

    Returns
    -------
    bool
        True if validation succeeds.

    Raises
    ------
    SpanScopeError
        Invalid runtime state.

    SpanScopeValidationError
        Internal consistency error.
    """

    #
    # ----------------------------------------------------------------------
    # Identity
    # ----------------------------------------------------------------------
    #

    if not self._id:

        raise SpanScopeValidationError(
            "SpanScope id is missing."
        )

    if not self._uuid:

        raise SpanScopeValidationError(
            "SpanScope uuid is missing."
        )

    if not self._name:

        raise SpanScopeValidationError(
            "SpanScope name is missing."
        )

    #
    # ----------------------------------------------------------------------
    # Runtime lifecycle
    # ----------------------------------------------------------------------
    #

    if self._disposed and self._running:

        raise SpanScopeValidationError(
            "Disposed SpanScope cannot be running."
        )

    if self._disposed and self._active:

        raise SpanScopeValidationError(
            "Disposed SpanScope cannot be active."
        )

    if self._closed and self._running:

        raise SpanScopeValidationError(
            "Closed SpanScope cannot be running."
        )

    if self._running and self._start_time is None:

        raise SpanScopeValidationError(
            "Running SpanScope has no start_time."
        )

    if (
        self._completed
        and self._end_time is None
    ):

        raise SpanScopeValidationError(
            "Completed SpanScope has no end_time."
        )

    #
    # ----------------------------------------------------------------------
    # Time consistency
    # ----------------------------------------------------------------------
    #

    if (
        self._start_time is not None
        and self._end_time is not None
        and self._end_time < self._start_time
    ):

        raise SpanScopeValidationError(
            "end_time is earlier than start_time."
        )

    if self._duration < 0:

        raise SpanScopeValidationError(
            "Duration cannot be negative."
        )

    #
    # ----------------------------------------------------------------------
    # Runtime objects
    # ----------------------------------------------------------------------
    #

    if self._running and self._span is None:

        raise SpanScopeValidationError(
            "Running SpanScope has no TraceSpan."
        )

    if self._running and self._tracer is None:

        raise SpanScopeValidationError(
            "Running SpanScope has no TraceTracer."
        )

    #
    # ----------------------------------------------------------------------
    # Statistics
    # ----------------------------------------------------------------------
    #

    if self._statistics.enter_count < 0:

        raise SpanScopeValidationError(
            "Negative enter_count."
        )

    if self._statistics.exit_count < 0:

        raise SpanScopeValidationError(
            "Negative exit_count."
        )

    if self._statistics.success_count < 0:

        raise SpanScopeValidationError(
            "Negative success_count."
        )

    if self._statistics.failure_count < 0:

        raise SpanScopeValidationError(
            "Negative failure_count."
        )

    if self._statistics.exception_count < 0:

        raise SpanScopeValidationError(
            "Negative exception_count."
        )

    if self._statistics.cancelled_count < 0:

        raise SpanScopeValidationError(
            "Negative cancelled_count."
        )

    #
    # ----------------------------------------------------------------------
    # Collections
    # ----------------------------------------------------------------------
    #

    if self._history is None:

        raise SpanScopeValidationError(
            "History container is missing."
        )

    if self._runtime_data is None:

        raise SpanScopeValidationError(
            "Runtime data container is missing."
        )

    if self._cache is None:

        raise SpanScopeValidationError(
            "Cache container is missing."
        )

    #
    # ----------------------------------------------------------------------
    # Logger
    # ----------------------------------------------------------------------
    #

    if self._logger is None:

        raise SpanScopeValidationError(
            "Logger is missing."
        )

    #
    # ----------------------------------------------------------------------
    # Success
    # ----------------------------------------------------------------------
    #

    return True
# ==============================================================================
# Part 8.15 – notify_callbacks()
# ==============================================================================

def notify_callbacks(
    self,
    event: str,
    *args: Any,
    **kwargs: Any,
) -> int:
    """
    Notify all registered callbacks.

    Parameters
    ----------
    event
        Runtime event name.

    Returns
    -------
    int
        Number of successfully executed callbacks.
    """

    executed = 0

    callbacks = tuple(self._callbacks)

    for callback in callbacks:

        try:

            callback(
                event,
                self,
                *args,
                **kwargs,
            )

            executed += 1

        except Exception as exc:

            self._statistics.exception_count += 1

            self._logger.exception(
                "Callback failed (%s): %s",
                event,
                exc,
            )

    self._runtime_data["last_callback_event"] = event

    return executed


# ==============================================================================
# Part 8.15 – notify_hooks()
# ==============================================================================

def notify_hooks(
    self,
    event: str,
    *args: Any,
    **kwargs: Any,
) -> int:
    """
    Notify all runtime hooks.

    Parameters
    ----------
    event
        Runtime event.

    Returns
    -------
    int
        Number of executed hooks.
    """

    executed = 0

    hooks = tuple(self._hooks)

    for hook in hooks:

        try:

            #
            # Hook object
            #

            if hasattr(
                hook,
                "notify",
            ):

                hook.notify(
                    event,
                    self,
                    *args,
                    **kwargs,
                )

            #
            # Callable hook
            #

            else:

                hook(
                    event,
                    self,
                    *args,
                    **kwargs,
                )

            executed += 1

        except Exception as exc:

            self._statistics.exception_count += 1

            self._logger.exception(
                "Hook failed (%s): %s",
                event,
                exc,
            )

    self._runtime_data["last_hook_event"] = event

    return executed


# ==============================================================================
# Part 8.15 – notify_subscribers()
# ==============================================================================

def notify_subscribers(
    self,
    event: str,
    *args: Any,
    **kwargs: Any,
) -> int:
    """
    Publish an event to all subscribers.

    Parameters
    ----------
    event
        Runtime event.

    Returns
    -------
    int
        Number of subscribers successfully notified.
    """

    executed = 0

    subscribers = tuple(self._subscribers)

    for subscriber in subscribers:

        try:

            #
            # Event bus style
            #

            if hasattr(
                subscriber,
                "publish",
            ):

                subscriber.publish(
                    event=event,
                    scope=self,
                    args=args,
                    kwargs=kwargs,
                )

            #
            # Observer style
            #

            elif hasattr(
                subscriber,
                "update",
            ):

                subscriber.update(
                    event,
                    self,
                    *args,
                    **kwargs,
                )

            #
            # Callable subscriber
            #

            else:

                subscriber(
                    event,
                    self,
                    *args,
                    **kwargs,
                )

            executed += 1

        except Exception as exc:

            self._statistics.exception_count += 1

            self._logger.exception(
                "Subscriber failed (%s): %s",
                event,
                exc,
            )

    self._runtime_data["last_subscriber_event"] = event

    return executed
# ==============================================================================
# Part 8.16 – update_statistics()
# ==============================================================================

def update_statistics(
    self,
) -> "SpanScope":
    """
    Recompute runtime statistics.

    Returns
    -------
    SpanScope
        Self.
    """

    with self._lock:

        now = time.time()

        stats = self._statistics

        #
        # --------------------------------------------------------------
        # Duration statistics
        # --------------------------------------------------------------
        #

        samples = self._duration_history

        if samples:

            stats.average_duration = (
                sum(samples) / len(samples)
            )

            stats.minimum_duration = min(samples)
            stats.maximum_duration = max(samples)

        else:

            stats.average_duration = 0.0
            stats.minimum_duration = 0.0
            stats.maximum_duration = 0.0

        #
        # --------------------------------------------------------------
        # Success / Failure rates
        # --------------------------------------------------------------
        #

        total_finished = (
            stats.success_count
            + stats.failure_count
            + stats.cancelled_count
        )

        if total_finished > 0:

            stats.success_rate = (
                stats.success_count
                / total_finished
            )

            stats.failure_rate = (
                stats.failure_count
                / total_finished
            )

        else:

            stats.success_rate = 0.0
            stats.failure_rate = 0.0

        #
        # --------------------------------------------------------------
        # Runtime
        # --------------------------------------------------------------
        #

        stats.updated_at = now
        stats.update_count += 1

        self._runtime_data["statistics_updated"] = now

        return self


# ==============================================================================
# Part 8.16 – record_duration()
# ==============================================================================

def record_duration(
    self,
    duration: Optional[float],
) -> float:
    """
    Record a duration sample.

    Parameters
    ----------
    duration
        Runtime duration in seconds.

    Returns
    -------
    float
        Stored duration.
    """

    with self._lock:

        if duration is None:

            duration = 0.0

        duration = max(
            float(duration),
            0.0,
        )

        self._duration = duration

        self._duration_history.append(
            duration,
        )

        #
        # Keep bounded history
        #

        if (
            self._history_limit > 0
            and len(self._duration_history)
            > self._history_limit
        ):

            self._duration_history.pop(0)

        self._statistics.last_duration = duration

        self._runtime_data[
            "last_duration"
        ] = duration

        return duration


# ==============================================================================
# Part 8.16 – record_exception()
# ==============================================================================

def record_exception(
    self,
    exc_type: Optional[type[BaseException]],
    exc_value: Optional[BaseException],
    exc_traceback: Optional[Any],
) -> None:
    """
    Record an exception raised inside the SpanScope.

    Parameters
    ----------
    exc_type
        Exception class.

    exc_value
        Exception instance.

    exc_traceback
        Python traceback.
    """

    with self._lock:

        now = time.time()

        self._statistics.exception_count += 1

        self._runtime_data["last_exception"] = {
            "type": (
                exc_type.__name__
                if exc_type
                else None
            ),
            "message": (
                str(exc_value)
                if exc_value
                else None
            ),
            "timestamp": now,
        }

        self._history.append(
            {
                "event": "exception",
                "timestamp": now,
                "type": (
                    exc_type.__name__
                    if exc_type
                    else None
                ),
                "message": (
                    str(exc_value)
                    if exc_value
                    else None
                ),
            }
        )

        #
        # Attach exception to span if supported
        #

        if (
            self._span is not None
            and hasattr(
                self._span,
                "record_exception",
            )
        ):

            try:

                self._span.record_exception(
                    exc_value,
                )

            except Exception:

                pass

        #
        # Log
        #

        if exc_value is not None:

            self._logger.exception(
                "SpanScope '%s' exception: %s",
                self._name,
                exc_value,
            )
# ==============================================================================
# Part 9.1 – __call__()
# ==============================================================================

def __call__(
    self,
    obj,
):
    """
    Dispatch SpanScope decorator.

    Supported
    ---------
    • Function
    • Method
    • Class

    Parameters
    ----------
    obj
        Object being decorated.

    Returns
    -------
    Decorated object.

    Raises
    ------
    TypeError
        Unsupported object type.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    #
    # ------------------------------------------------------------------
    # Disabled
    # ------------------------------------------------------------------
    #

    if not self._enabled:

        return obj

    #
    # ------------------------------------------------------------------
    # Class
    # ------------------------------------------------------------------
    #

    if isinstance(obj, type):

        return self.decorate_class(
            obj,
        )

    #
    # ------------------------------------------------------------------
    # Callable
    # ------------------------------------------------------------------
    #

    if callable(obj):

        qualname = getattr(
            obj,
            "__qualname__",
            "",
        )

        #
        # Method
        #

        if "." in qualname:

            return self.decorate_method(
                obj,
            )

        #
        # Function
        #

        return self.decorate_function(
            obj,
        )

    #
    # ------------------------------------------------------------------
    # Unsupported object
    # ------------------------------------------------------------------
    #

    raise TypeError(
        f"{self.__class__.__name__} cannot decorate "
        f"objects of type "
        f"{type(obj).__name__}."
    )
# ==============================================================================
# Part 9.2 – decorate_function()
# ==============================================================================

def decorate_function(
    self,
    func,
):
    """
    Decorate a Python function with SpanScope.

    A new runtime span is automatically created around every invocation
    of the function.

    Parameters
    ----------
    func
        Function to decorate.

    Returns
    -------
    callable
        Wrapped function.
    """

    #
    # ------------------------------------------------------------------
    # Already wrapped
    # ------------------------------------------------------------------
    #

    if self.is_wrapped(func):

        return func

    scope = self

    @wraps(func)
    def wrapper(*args, **kwargs):

        #
        # --------------------------------------------------------------
        # Disabled shortcut
        # --------------------------------------------------------------
        #

        if not scope.enabled:

            return func(*args, **kwargs)

        #
        # --------------------------------------------------------------
        # Before call
        # --------------------------------------------------------------
        #

        scope.before_call(
            func,
            args,
            kwargs,
        )

        scope.start()

        try:

            #
            # ----------------------------------------------------------
            # Execute function
            # ----------------------------------------------------------
            #

            result = func(
                *args,
                **kwargs,
            )

            #
            # ----------------------------------------------------------
            # Success
            # ----------------------------------------------------------
            #

            scope.on_success(
                func,
                result,
            )

            return result

        except Exception as exc:

            #
            # ----------------------------------------------------------
            # Exception
            # ----------------------------------------------------------
            #

            scope.record_exception(
                type(exc),
                exc,
                exc.__traceback__,
            )

            scope.on_exception(
                func,
                exc,
            )

            raise

        finally:

            #
            # ----------------------------------------------------------
            # Finalize
            # ----------------------------------------------------------
            #

            scope.after_call(
                func,
            )

            scope.stop()

            scope.on_finally(
                func,
            )

    #
    # ------------------------------------------------------------------
    # Decorator metadata
    # ------------------------------------------------------------------
    #

    wrapper.__span_scope__ = self
    wrapper.__wrapped_by_span_scope__ = True

    self.decorator_metadata(
        wrapper,
        original=func,
        decorator="SpanScope",
        scope=self,
    )

    return wrapper
# ==============================================================================
# Part 9.3 – decorate_method()
# ==============================================================================

def decorate_method(
    self,
    method,
):
    """
    Decorate an instance/class/static method with SpanScope.

    Parameters
    ----------
    method
        Method to decorate.

    Returns
    -------
    callable
        Wrapped method.
    """

    #
    # ------------------------------------------------------------------
    # Already wrapped
    # ------------------------------------------------------------------
    #

    if self.is_wrapped(method):

        return method

    scope = self

    @wraps(method)
    def wrapper(instance, *args, **kwargs):

        #
        # ------------------------------------------------------------------
        # Disabled shortcut
        # ------------------------------------------------------------------
        #

        if not scope.enabled:

            return method(
                instance,
                *args,
                **kwargs,
            )

        #
        # ------------------------------------------------------------------
        # Before call
        # ------------------------------------------------------------------
        #

        scope.before_call(
            method,
            args,
            kwargs,
        )

        #
        # ------------------------------------------------------------------
        # Runtime metadata
        # ------------------------------------------------------------------
        #

        scope.runtime_data["method"] = getattr(
            method,
            "__qualname__",
            method.__name__,
        )

        scope.runtime_data["owner"] = (
            instance.__class__.__name__
            if instance is not None
            else None
        )

        #
        # ------------------------------------------------------------------
        # Start Span
        # ------------------------------------------------------------------
        #

        scope.start()

        try:

            #
            # --------------------------------------------------------------
            # Execute method
            # --------------------------------------------------------------
            #

            result = method(
                instance,
                *args,
                **kwargs,
            )

            #
            # --------------------------------------------------------------
            # Success
            # --------------------------------------------------------------
            #

            scope.on_success(
                method,
                result,
            )

            return result

        except Exception as exc:

            #
            # --------------------------------------------------------------
            # Exception
            # --------------------------------------------------------------
            #

            scope.record_exception(
                type(exc),
                exc,
                exc.__traceback__,
            )

            scope.on_exception(
                method,
                exc,
            )

            raise

        finally:

            #
            # --------------------------------------------------------------
            # After call
            # --------------------------------------------------------------
            #

            scope.after_call(
                method,
            )

            scope.stop()

            scope.on_finally(
                method,
            )

    #
    # ------------------------------------------------------------------
    # Decorator metadata
    # ------------------------------------------------------------------
    #

    wrapper.__span_scope__ = self
    wrapper.__wrapped_by_span_scope__ = True
    wrapper.__original_method__ = method

    self.decorator_metadata(
        wrapper,
        original=method,
        decorator="SpanScope",
        target="method",
        scope=self,
    )

    return wrapper
# ==============================================================================
# Part 9.4 – decorate_class()
# ==============================================================================

def decorate_class(
    self,
    cls,
):
    """
    Decorate an entire class with SpanScope.

    Every user-defined callable member of the class will be wrapped
    automatically. Special (dunder) methods are ignored except those
    explicitly required by the runtime.

    Parameters
    ----------
    cls
        Class to decorate.

    Returns
    -------
    type
        Decorated class.
    """

    #
    # ------------------------------------------------------------------
    # Already decorated
    # ------------------------------------------------------------------
    #

    if self.is_wrapped(cls):

        return cls

    #
    # ------------------------------------------------------------------
    # Class metadata
    # ------------------------------------------------------------------
    #

    self.runtime_data["class"] = cls.__name__
    self.runtime_data["module"] = getattr(
        cls,
        "__module__",
        None,
    )

    #
    # ------------------------------------------------------------------
    # Iterate through class dictionary
    # ------------------------------------------------------------------
    #

    for name, member in list(cls.__dict__.items()):

        #
        # --------------------------------------------------------------
        # Ignore most dunder methods
        # --------------------------------------------------------------
        #

        if (
            name.startswith("__")
            and name.endswith("__")
            and name not in (
                "__call__",
            )
        ):

            continue

        #
        # --------------------------------------------------------------
        # Static method
        # --------------------------------------------------------------
        #

        if isinstance(
            member,
            staticmethod,
        ):

            wrapped = self.decorate_method(
                member.__func__,
            )

            setattr(
                cls,
                name,
                staticmethod(
                    wrapped,
                ),
            )

            continue

        #
        # --------------------------------------------------------------
        # Class method
        # --------------------------------------------------------------
        #

        if isinstance(
            member,
            classmethod,
        ):

            wrapped = self.decorate_method(
                member.__func__,
            )

            setattr(
                cls,
                name,
                classmethod(
                    wrapped,
                ),
            )

            continue

        #
        # --------------------------------------------------------------
        # Normal function
        # --------------------------------------------------------------
        #

        if callable(member):

            setattr(
                cls,
                name,
                self.decorate_method(
                    member,
                ),
            )

    #
    # ------------------------------------------------------------------
    # Decorator metadata
    # ------------------------------------------------------------------
    #

    cls.__span_scope__ = self
    cls.__wrapped_by_span_scope__ = True
    cls.__original_class__ = cls

    self.decorator_metadata(
        cls,
        original=cls,
        decorator="SpanScope",
        target="class",
        scope=self,
    )

    #
    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    #

    self.logger.debug(
        "Class '%s' decorated by SpanScope.",
        cls.__name__,
    )

    return cls
# ==============================================================================
# Part 9.5 – wrap_callable()
# ==============================================================================

def wrap_callable(
    self,
    target,
):
    """
    Wrap any supported callable object with SpanScope.

    Supported
    ---------
    • function
    • method
    • class
    • arbitrary callable object (__call__)

    Parameters
    ----------
    target
        Object to wrap.

    Returns
    -------
    object
        Wrapped object.

    Raises
    ------
    TypeError
        Unsupported object type.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    #
    # ------------------------------------------------------------------
    # Already wrapped
    # ------------------------------------------------------------------
    #

    if self.is_wrapped(target):

        return target

    #
    # ------------------------------------------------------------------
    # Class
    # ------------------------------------------------------------------
    #

    if isinstance(target, type):

        return self.decorate_class(
            target,
        )

    #
    # ------------------------------------------------------------------
    # Callable
    # ------------------------------------------------------------------
    #

    if callable(target):

        qualname = getattr(
            target,
            "__qualname__",
            "",
        )

        #
        # --------------------------------------------------------------
        # Method
        # --------------------------------------------------------------
        #

        if "." in qualname:

            return self.decorate_method(
                target,
            )

        #
        # --------------------------------------------------------------
        # Function
        # --------------------------------------------------------------
        #

        if hasattr(
            target,
            "__code__",
        ):

            return self.decorate_function(
                target,
            )

        #
        # --------------------------------------------------------------
        # Generic callable object
        # --------------------------------------------------------------
        #

        if hasattr(
            target,
            "__call__",
        ):

            original_call = target.__call__

            target.__call__ = self.decorate_function(
                original_call,
            )

            setattr(
                target,
                "__span_scope__",
                self,
            )

            setattr(
                target,
                "__wrapped_by_span_scope__",
                True,
            )

            return target

    #
    # ------------------------------------------------------------------
    # Unsupported
    # ------------------------------------------------------------------
    #

    raise TypeError(
        f"Unsupported callable type: "
        f"{type(target).__name__}"
    )
# ==============================================================================
# Part 9.6 – before_call()
# ==============================================================================

def before_call(
    self,
    target,
    args=None,
    kwargs=None,
):
    """
    Runtime hook executed immediately before a wrapped callable.

    Parameters
    ----------
    target
        Function, method or callable about to execute.

    args
        Positional arguments.

    kwargs
        Keyword arguments.

    Returns
    -------
    SpanScope
        Self.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    if self._disposed:

        return self

    args = args or ()
    kwargs = kwargs or {}

    now = time.time()

    #
    # ------------------------------------------------------------------
    # Runtime timestamps
    # ------------------------------------------------------------------
    #

    self._updated_at = now

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    target_name = getattr(
        target,
        "__qualname__",
        getattr(
            target,
            "__name__",
            str(target),
        ),
    )

    self._runtime_data["current_target"] = target_name
    self._runtime_data["last_call"] = now
    self._runtime_data["argument_count"] = (
        len(args) + len(kwargs)
    )

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    self._statistics.enter_count += 1
    self._statistics.updated_at = now

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    self._history.append(
        {
            "event": "before_call",
            "target": target_name,
            "timestamp": now,
        }
    )

    #
    # ------------------------------------------------------------------
    # Notifications
    # ------------------------------------------------------------------
    #

    self.notify_callbacks(
        "before_call",
        self,
        target,
        args,
        kwargs,
    )

    self.notify_hooks(
        "before_call",
        self,
        target,
        args,
        kwargs,
    )

    self.notify_subscribers(
        "before_call",
        self,
        target,
        args,
        kwargs,
    )

    #
    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    #

    self._logger.debug(
        "SpanScope '%s' entering %s",
        self._name,
        target_name,
    )

    return self
# ==============================================================================
# Part 9.7 – after_call()
# ==============================================================================

def after_call(
    self,
    target,
    result=None,
):
    """
    Runtime hook executed immediately after a wrapped callable.

    This hook is always executed after the callable finishes successfully
    or after exception handling has completed.

    Parameters
    ----------
    target
        Function, method or callable that has just executed.

    result
        Returned object, if available.

    Returns
    -------
    SpanScope
        Self.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    if self._disposed:

        return self

    now = time.time()

    #
    # ------------------------------------------------------------------
    # Runtime timestamps
    # ------------------------------------------------------------------
    #

    self._updated_at = now

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    target_name = getattr(
        target,
        "__qualname__",
        getattr(
            target,
            "__name__",
            str(target),
        ),
    )

    self._runtime_data["last_target"] = target_name
    self._runtime_data["last_return"] = result
    self._runtime_data["last_finished"] = now

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    self._statistics.exit_count += 1
    self._statistics.updated_at = now

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    self._history.append(
        {
            "event": "after_call",
            "target": target_name,
            "timestamp": now,
        }
    )

    #
    # ------------------------------------------------------------------
    # Notifications
    # ------------------------------------------------------------------
    #

    self.notify_callbacks(
        "after_call",
        self,
        target,
        result,
    )

    self.notify_hooks(
        "after_call",
        self,
        target,
        result,
    )

    self.notify_subscribers(
        "after_call",
        self,
        target,
        result,
    )

    #
    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    #

    self._logger.debug(
        "SpanScope '%s' finished %s",
        self._name,
        target_name,
    )

    return self
# ==============================================================================
# Part 9.8 – on_success()
# ==============================================================================

def on_success(
    self,
    target,
    result=None,
):
    """
    Runtime hook executed after successful execution.

    Parameters
    ----------
    target
        Function, method or callable that completed successfully.

    result
        Returned value.

    Returns
    -------
    SpanScope
        Self.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    if self._disposed:

        return self

    now = time.time()

    target_name = getattr(
        target,
        "__qualname__",
        getattr(
            target,
            "__name__",
            str(target),
        ),
    )

    #
    # ------------------------------------------------------------------
    # Runtime state
    # ------------------------------------------------------------------
    #

    self._successful = True
    self._failed = False
    self._cancelled = False

    self._updated_at = now

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    self._statistics.success_count += 1
    self._statistics.updated_at = now

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    self._runtime_data["last_success"] = now
    self._runtime_data["last_success_target"] = target_name
    self._runtime_data["last_result"] = result

    #
    # ------------------------------------------------------------------
    # Span metadata
    # ------------------------------------------------------------------
    #

    if self._span is not None:

        if hasattr(
            self._span,
            "set_attribute",
        ):

            self._span.set_attribute(
                "status",
                "success",
            )

            self._span.set_attribute(
                "target",
                target_name,
            )

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    self._history.append(
        {
            "event": "success",
            "target": target_name,
            "timestamp": now,
        }
    )

    #
    # ------------------------------------------------------------------
    # Notifications
    # ------------------------------------------------------------------
    #

    self.notify_callbacks(
        "success",
        self,
        target,
        result,
    )

    self.notify_hooks(
        "success",
        self,
        target,
        result,
    )

    self.notify_subscribers(
        "success",
        self,
        target,
        result,
    )

    #
    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    #

    self._logger.debug(
        "SpanScope '%s' succeeded: %s",
        self._name,
        target_name,
    )

    return self
# ==============================================================================
# Part 9.9 – on_exception()
# ==============================================================================

def on_exception(
    self,
    target,
    exception,
):
    """
    Runtime hook executed when a decorated callable raises an exception.

    Parameters
    ----------
    target
        Function, method or callable that raised the exception.

    exception
        Exception instance.

    Returns
    -------
    SpanScope
        Self.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    if self._disposed:

        return self

    now = time.time()

    target_name = getattr(
        target,
        "__qualname__",
        getattr(
            target,
            "__name__",
            str(target),
        ),
    )

    #
    # ------------------------------------------------------------------
    # Runtime state
    # ------------------------------------------------------------------
    #

    self._successful = False
    self._failed = True

    self._updated_at = now

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    self._statistics.failure_count += 1
    self._statistics.exception_count += 1
    self._statistics.updated_at = now

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    self._runtime_data["last_exception"] = {
        "type": type(exception).__name__,
        "message": str(exception),
        "timestamp": now,
    }

    self._runtime_data["last_exception_target"] = (
        target_name
    )

    #
    # ------------------------------------------------------------------
    # Span metadata
    # ------------------------------------------------------------------
    #

    if self._span is not None:

        if hasattr(
            self._span,
            "record_exception",
        ):

            try:

                self._span.record_exception(
                    exception,
                )

            except Exception:

                pass

        if hasattr(
            self._span,
            "set_attribute",
        ):

            try:

                self._span.set_attribute(
                    "status",
                    "exception",
                )

                self._span.set_attribute(
                    "exception.type",
                    type(exception).__name__,
                )

                self._span.set_attribute(
                    "exception.message",
                    str(exception),
                )

            except Exception:

                pass

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    self._history.append(
        {
            "event": "exception",
            "target": target_name,
            "type": type(exception).__name__,
            "message": str(exception),
            "timestamp": now,
        }
    )

    #
    # ------------------------------------------------------------------
    # Notifications
    # ------------------------------------------------------------------
    #

    self.notify_callbacks(
        "exception",
        self,
        target,
        exception,
    )

    self.notify_hooks(
        "exception",
        self,
        target,
        exception,
    )

    self.notify_subscribers(
        "exception",
        self,
        target,
        exception,
    )

    #
    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    #

    self._logger.exception(
        "SpanScope '%s' exception in %s: %s",
        self._name,
        target_name,
        exception,
    )

    return self
# ==============================================================================
# Part 9.10 – on_finally()
# ==============================================================================

def on_finally(
    self,
    target,
):
    """
    Runtime hook executed unconditionally after every decorated call.

    This hook is always executed regardless of whether the callable
    completed successfully, raised an exception, or was cancelled.

    Parameters
    ----------
    target
        Function, method or callable.

    Returns
    -------
    SpanScope
        Self.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    if self._disposed:

        return self

    now = time.time()

    target_name = getattr(
        target,
        "__qualname__",
        getattr(
            target,
            "__name__",
            str(target),
        ),
    )

    #
    # ------------------------------------------------------------------
    # Runtime state
    # ------------------------------------------------------------------
    #

    self._completed = True
    self._updated_at = now

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    self._runtime_data["last_finally"] = now
    self._runtime_data["last_finally_target"] = (
        target_name
    )

    #
    # ------------------------------------------------------------------
    # Update statistics
    # ------------------------------------------------------------------
    #

    self.update_statistics()

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    self._history.append(
        {
            "event": "finally",
            "target": target_name,
            "timestamp": now,
        }
    )

    #
    # ------------------------------------------------------------------
    # Notifications
    # ------------------------------------------------------------------
    #

    self.notify_callbacks(
        "finally",
        self,
        target,
    )

    self.notify_hooks(
        "finally",
        self,
        target,
    )

    self.notify_subscribers(
        "finally",
        self,
        target,
    )

    #
    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    #

    self._logger.debug(
        "SpanScope '%s' finalized: %s",
        self._name,
        target_name,
    )

    return self
# ==============================================================================
# Part 9.11 – unwrap()
# ==============================================================================

def unwrap(
    self,
    obj,
):
    """
    Remove the SpanScope wrapper from a decorated object.

    If the object is not wrapped, it is returned unchanged.

    Supported
    ---------
    • Function
    • Method
    • Class
    • Callable object

    Parameters
    ----------
    obj
        Wrapped object.

    Returns
    -------
    object
        Original object.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    if obj is None:

        return None

    #
    # ------------------------------------------------------------------
    # Not wrapped
    # ------------------------------------------------------------------
    #

    if not self.is_wrapped(obj):

        return obj

    #
    # ------------------------------------------------------------------
    # Recover original object
    # ------------------------------------------------------------------
    #

    original = getattr(
        obj,
        "__wrapped__",
        None,
    )

    if original is None:

        original = getattr(
            obj,
            "__original_function__",
            None,
        )

    if original is None:

        original = getattr(
            obj,
            "__original_method__",
            None,
        )

    if original is None:

        original = getattr(
            obj,
            "__original_class__",
            None,
        )

    if original is None:

        return obj

    #
    # ------------------------------------------------------------------
    # Cleanup metadata (best effort)
    # ------------------------------------------------------------------
    #

    for attribute in (
        "__span_scope__",
        "__wrapped_by_span_scope__",
        "__original_function__",
        "__original_method__",
        "__original_class__",
        "__decorator_metadata__",
    ):

        try:

            if hasattr(obj, attribute):

                delattr(
                    obj,
                    attribute,
                )

        except Exception:

            #
            # Ignore immutable objects.
            #
            pass

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    self._runtime_data["last_unwrap"] = getattr(
        original,
        "__qualname__",
        getattr(
            original,
            "__name__",
            str(original),
        ),
    )

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    self._history.append(
        {
            "event": "unwrap",
            "target": self._runtime_data["last_unwrap"],
            "timestamp": time.time(),
        }
    )

    #
    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    #

    self._logger.debug(
        "SpanScope '%s' unwrapped %s",
        self._name,
        self._runtime_data["last_unwrap"],
    )

    return original
# ==============================================================================
# Part 9.12 – is_wrapped()
# ==============================================================================

def is_wrapped(
    self,
    obj,
):
    """
    Determine whether an object has already been wrapped by SpanScope.

    Supported
    ---------
    • Function
    • Method
    • Class
    • Callable object

    Parameters
    ----------
    obj
        Object to inspect.

    Returns
    -------
    bool
        True if the object is wrapped by SpanScope, otherwise False.
    """

    if obj is None:

        return False

    #
    # ------------------------------------------------------------------
    # Explicit SpanScope marker
    # ------------------------------------------------------------------
    #

    if getattr(
        obj,
        "__wrapped_by_span_scope__",
        False,
    ):

        return True

    #
    # ------------------------------------------------------------------
    # Associated SpanScope
    # ------------------------------------------------------------------
    #

    scope = getattr(
        obj,
        "__span_scope__",
        None,
    )

    if scope is self:

        return True

    #
    # ------------------------------------------------------------------
    # functools.wraps marker
    # ------------------------------------------------------------------
    #

    if hasattr(
        obj,
        "__wrapped__",
    ):

        return True

    #
    # ------------------------------------------------------------------
    # Original object markers
    # ------------------------------------------------------------------
    #

    if hasattr(
        obj,
        "__original_function__",
    ):

        return True

    if hasattr(
        obj,
        "__original_method__",
    ):

        return True

    if hasattr(
        obj,
        "__original_class__",
    ):

        return True

    #
    # ------------------------------------------------------------------
    # Decorator metadata
    # ------------------------------------------------------------------
    #

    metadata = getattr(
        obj,
        "__decorator_metadata__",
        None,
    )

    if isinstance(
        metadata,
        dict,
    ):

        if metadata.get("decorator") == "SpanScope":

            return True

    #
    # ------------------------------------------------------------------
    # Not wrapped
    # ------------------------------------------------------------------
    #

    return False
# ==============================================================================
# Part 9.13 – decorator_metadata()
# ==============================================================================

def decorator_metadata(
    self,
    obj,
    **metadata,
):
    """
    Attach SpanScope decorator metadata to an object.

    Parameters
    ----------
    obj
        Decorated function, method, class or callable.

    **metadata
        Additional metadata to attach.

    Returns
    -------
    object
        The same decorated object.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    if obj is None:

        return None

    now = time.time()

    #
    # ------------------------------------------------------------------
    # Existing metadata
    # ------------------------------------------------------------------
    #

    current = getattr(
        obj,
        "__decorator_metadata__",
        None,
    )

    if not isinstance(current, dict):

        current = {}

    #
    # ------------------------------------------------------------------
    # Standard metadata
    # ------------------------------------------------------------------
    #

    current.update(
        {
            "decorator": "SpanScope",
            "scope_id": self._id,
            "scope_uuid": self._uuid,
            "scope_name": self._name,
            "scope_type": self._scope_type,
            "version": self._version,
            "module": getattr(
                obj,
                "__module__",
                None,
            ),
            "qualname": getattr(
                obj,
                "__qualname__",
                getattr(
                    obj,
                    "__name__",
                    str(obj),
                ),
            ),
            "created_at": now,
        }
    )

    #
    # ------------------------------------------------------------------
    # User metadata
    # ------------------------------------------------------------------
    #

    current.update(metadata)

    #
    # ------------------------------------------------------------------
    # Attach metadata
    # ------------------------------------------------------------------
    #

    setattr(
        obj,
        "__decorator_metadata__",
        current,
    )

    setattr(
        obj,
        "__span_scope__",
        self,
    )

    setattr(
        obj,
        "__wrapped_by_span_scope__",
        True,
    )

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    self._runtime_data["last_decorated"] = current[
        "qualname"
    ]

    self._runtime_data["last_decorator"] = (
        "SpanScope"
    )

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    self._history.append(
        {
            "event": "decorator_metadata",
            "target": current["qualname"],
            "timestamp": now,
        }
    )

    #
    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    #

    self._logger.debug(
        "Decorator metadata attached to '%s'.",
        current["qualname"],
    )

    return obj
# ==============================================================================
# Part 10.1 – register_callback()
# ==============================================================================

def register_callback(
    self,
    callback,
    *,
    name=None,
    enabled=True,
    priority=100,
    metadata=None,
):
    """
    Register a runtime callback.

    Parameters
    ----------
    callback
        Callable object.

    name
        Optional callback name.

    enabled
        Initial enabled state.

    priority
        Smaller values execute earlier.

    metadata
        Optional metadata dictionary.

    Returns
    -------
    callable
        Registered callback.

    Raises
    ------
    TypeError
        Callback is not callable.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    if not callable(callback):

        raise TypeError(
            "callback must be callable."
        )

    #
    # ------------------------------------------------------------------
    # Already registered
    # ------------------------------------------------------------------
    #

    if self.has_callback(callback):

        return callback

    now = time.time()

    callback_name = (
        name
        or getattr(
            callback,
            "__qualname__",
            getattr(
                callback,
                "__name__",
                repr(callback),
            ),
        )
    )

    callback_info = {
        "callback": callback,
        "name": callback_name,
        "enabled": bool(enabled),
        "priority": int(priority),
        "metadata": dict(metadata or {}),
        "created_at": now,
        "updated_at": now,
        "invoke_count": 0,
        "exception_count": 0,
    }

    #
    # ------------------------------------------------------------------
    # Store callback
    # ------------------------------------------------------------------
    #

    self._callbacks.append(
        callback
    )

    self._callback_registry[
        callback
    ] = callback_info

    #
    # ------------------------------------------------------------------
    # Keep callbacks ordered by priority
    # ------------------------------------------------------------------
    #

    self._callbacks.sort(
        key=lambda cb: self._callback_registry[
            cb
        ]["priority"]
    )

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    self._runtime_data[
        "callback_count"
    ] = len(
        self._callbacks
    )

    self._runtime_data[
        "last_callback_registered"
    ] = callback_name

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    self._statistics.update_count += 1
    self._statistics.updated_at = now

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    self._history.append(
        {
            "event": "register_callback",
            "callback": callback_name,
            "timestamp": now,
        }
    )

    #
    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    #

    self._logger.debug(
        "Registered callback '%s'.",
        callback_name,
    )

    return callback
# ==============================================================================
# Part 10.2 – unregister_callback()
# ==============================================================================

def unregister_callback(
    self,
    callback,
):
    """
    Unregister a runtime callback.

    Parameters
    ----------
    callback
        Callback object or callback name.

    Returns
    -------
    bool
        True if a callback was removed, otherwise False.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    now = time.time()

    target = None

    #
    # ------------------------------------------------------------------
    # Lookup by callable
    # ------------------------------------------------------------------
    #

    if callable(callback):

        if callback in self._callback_registry:

            target = callback

    #
    # ------------------------------------------------------------------
    # Lookup by name
    # ------------------------------------------------------------------
    #

    else:

        for cb, info in self._callback_registry.items():

            if info.get("name") == callback:

                target = cb
                break

    #
    # ------------------------------------------------------------------
    # Callback not found
    # ------------------------------------------------------------------
    #

    if target is None:

        return False

    callback_name = self._callback_registry[
        target
    ]["name"]

    #
    # ------------------------------------------------------------------
    # Remove from callback list
    # ------------------------------------------------------------------
    #

    try:

        self._callbacks.remove(
            target,
        )

    except ValueError:

        pass

    #
    # ------------------------------------------------------------------
    # Remove registry entry
    # ------------------------------------------------------------------
    #

    self._callback_registry.pop(
        target,
        None,
    )

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    self._runtime_data[
        "callback_count"
    ] = len(
        self._callbacks
    )

    self._runtime_data[
        "last_callback_unregistered"
    ] = callback_name

    self._updated_at = now

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    self._statistics.update_count += 1
    self._statistics.updated_at = now

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    self._history.append(
        {
            "event": "unregister_callback",
            "callback": callback_name,
            "timestamp": now,
        }
    )

    #
    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    #

    self._logger.debug(
        "Unregistered callback '%s'.",
        callback_name,
    )

    return True
# ==============================================================================
# Part 10.3 – clear_callbacks()
# ==============================================================================

def clear_callbacks(
    self,
):
    """
    Remove all registered callbacks.

    Returns
    -------
    int
        Number of callbacks removed.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    now = time.time()

    removed = len(self._callbacks)

    #
    # ------------------------------------------------------------------
    # Clear callback containers
    # ------------------------------------------------------------------
    #

    self._callbacks.clear()

    if hasattr(
        self,
        "_callback_registry",
    ):

        self._callback_registry.clear()

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    self._runtime_data[
        "callback_count"
    ] = 0

    self._runtime_data[
        "last_callback_clear"
    ] = now

    self._updated_at = now

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    self._statistics.update_count += 1
    self._statistics.updated_at = now

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    self._history.append(
        {
            "event": "clear_callbacks",
            "removed": removed,
            "timestamp": now,
        }
    )

    #
    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    #

    self._logger.debug(
        "Cleared %d callback(s).",
        removed,
    )

    return removed
# ==============================================================================
# Part 10.4 – get_callbacks()
# ==============================================================================

def get_callbacks(
    self,
    *,
    enabled_only=False,
    include_metadata=False,
):
    """
    Return the registered callbacks.

    Parameters
    ----------
    enabled_only
        Return only enabled callbacks.

    include_metadata
        Return callback registry records instead of callable objects.

    Returns
    -------
    list
        Registered callbacks or callback metadata records.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    #
    # ------------------------------------------------------------------
    # Registry unavailable
    # ------------------------------------------------------------------
    #

    if not hasattr(
        self,
        "_callback_registry",
    ):

        return []

    #
    # ------------------------------------------------------------------
    # Collect callbacks
    # ------------------------------------------------------------------
    #

    callbacks = []

    for callback in self._callbacks:

        info = self._callback_registry.get(
            callback,
        )

        if info is None:

            continue

        #
        # --------------------------------------------------------------
        # Enabled filter
        # --------------------------------------------------------------
        #

        if (
            enabled_only
            and not info.get(
                "enabled",
                True,
            )
        ):

            continue

        #
        # --------------------------------------------------------------
        # Return metadata
        # --------------------------------------------------------------
        #

        if include_metadata:

            callbacks.append(
                dict(info),
            )

        #
        # --------------------------------------------------------------
        # Return callable
        # --------------------------------------------------------------
        #

        else:

            callbacks.append(
                callback,
            )

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    self._runtime_data[
        "last_callback_query"
    ] = time.time()

    return callbacks
# ==============================================================================
# Part 10.5 – has_callback()
# ==============================================================================

def has_callback(
    self,
    callback,
):
    """
    Determine whether a callback is registered.

    Parameters
    ----------
    callback
        Callback object or callback name.

    Returns
    -------
    bool
        True if the callback exists, otherwise False.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    #
    # ------------------------------------------------------------------
    # Registry unavailable
    # ------------------------------------------------------------------
    #

    if not hasattr(
        self,
        "_callback_registry",
    ):

        return False

    #
    # ------------------------------------------------------------------
    # Lookup by callable
    # ------------------------------------------------------------------
    #

    if callable(callback):

        return (
            callback
            in self._callback_registry
        )

    #
    # ------------------------------------------------------------------
    # Lookup by callback name
    # ------------------------------------------------------------------
    #

    for info in self._callback_registry.values():

        if info.get("name") == callback:

            return True

    #
    # ------------------------------------------------------------------
    # Callback not found
    # ------------------------------------------------------------------
    #

    return False
# ==============================================================================
# Part 10.6 – callback_count()
# ==============================================================================

def callback_count(
    self,
    *,
    enabled_only=False,
):
    """
    Return the number of registered callbacks.

    Parameters
    ----------
    enabled_only
        Count only enabled callbacks.

    Returns
    -------
    int
        Number of callbacks.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    #
    # ------------------------------------------------------------------
    # Registry unavailable
    # ------------------------------------------------------------------
    #

    if not hasattr(
        self,
        "_callback_registry",
    ):

        return 0

    #
    # ------------------------------------------------------------------
    # Count all callbacks
    # ------------------------------------------------------------------
    #

    if not enabled_only:

        count = len(
            self._callbacks
        )

    #
    # ------------------------------------------------------------------
    # Count enabled callbacks
    # ------------------------------------------------------------------
    #

    else:

        count = 0

        for info in self._callback_registry.values():

            if info.get(
                "enabled",
                True,
            ):

                count += 1

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    self._runtime_data[
        "callback_count"
    ] = count

    self._runtime_data[
        "last_callback_count"
    ] = time.time()

    return count
# ==============================================================================
# Part 10.7 – enable_callback()
# ==============================================================================

def enable_callback(
    self,
    callback,
):
    """
    Enable a registered callback.

    Parameters
    ----------
    callback
        Callback object or callback name.

    Returns
    -------
    bool
        True if the callback was enabled, otherwise False.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    if not hasattr(
        self,
        "_callback_registry",
    ):

        return False

    target = None

    #
    # ------------------------------------------------------------------
    # Lookup by callable
    # ------------------------------------------------------------------
    #

    if callable(callback):

        if callback in self._callback_registry:

            target = callback

    #
    # ------------------------------------------------------------------
    # Lookup by callback name
    # ------------------------------------------------------------------
    #

    else:

        for cb, info in self._callback_registry.items():

            if info.get("name") == callback:

                target = cb
                break

    #
    # ------------------------------------------------------------------
    # Callback not found
    # ------------------------------------------------------------------
    #

    if target is None:

        return False

    info = self._callback_registry[target]

    #
    # ------------------------------------------------------------------
    # Already enabled
    # ------------------------------------------------------------------
    #

    if info.get(
        "enabled",
        True,
    ):

        return True

    now = time.time()

    #
    # ------------------------------------------------------------------
    # Enable callback
    # ------------------------------------------------------------------
    #

    info["enabled"] = True
    info["updated_at"] = now

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    self._runtime_data[
        "last_callback_enabled"
    ] = info["name"]

    self._runtime_data[
        "callback_count"
    ] = len(
        self._callbacks
    )

    self._updated_at = now

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    self._statistics.update_count += 1
    self._statistics.updated_at = now

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    self._history.append(
        {
            "event": "enable_callback",
            "callback": info["name"],
            "timestamp": now,
        }
    )

    #
    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    #

    self._logger.debug(
        "Enabled callback '%s'.",
        info["name"],
    )

    return True
# ==============================================================================
# Part 10.8 – disable_callback()
# ==============================================================================

def disable_callback(
    self,
    callback,
):
    """
    Disable a registered callback.

    The callback remains in the registry but will no longer be invoked
    until it is enabled again.

    Parameters
    ----------
    callback
        Callback object or callback name.

    Returns
    -------
    bool
        True if the callback was disabled, otherwise False.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    if not hasattr(
        self,
        "_callback_registry",
    ):

        return False

    target = None

    #
    # ------------------------------------------------------------------
    # Lookup by callable
    # ------------------------------------------------------------------
    #

    if callable(callback):

        target = self._callback_registry.get(
            callback
        )

        if target is not None:

            target = callback

    #
    # ------------------------------------------------------------------
    # Lookup by callback name
    # ------------------------------------------------------------------
    #

    else:

        for cb, info in self._callback_registry.items():

            if info.get("name") == callback:

                target = cb
                break

    #
    # ------------------------------------------------------------------
    # Callback not found
    # ------------------------------------------------------------------
    #

    if target is None:

        return False

    info = self._callback_registry[target]

    #
    # ------------------------------------------------------------------
    # Already disabled
    # ------------------------------------------------------------------
    #

    if not info.get(
        "enabled",
        True,
    ):

        return True

    now = time.time()

    #
    # ------------------------------------------------------------------
    # Disable callback
    # ------------------------------------------------------------------
    #

    info["enabled"] = False
    info["updated_at"] = now

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    self._runtime_data[
        "last_callback_disabled"
    ] = info["name"]

    self._runtime_data[
        "callback_count"
    ] = len(
        self._callbacks
    )

    self._updated_at = now

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    self._statistics.update_count += 1
    self._statistics.updated_at = now

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    self._history.append(
        {
            "event": "disable_callback",
            "callback": info["name"],
            "timestamp": now,
        }
    )

    #
    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    #

    self._logger.debug(
        "Disabled callback '%s'.",
        info["name"],
    )

    return True
# ==============================================================================
# Part 10.9 – invoke_callback()
# ==============================================================================

def invoke_callback(
    self,
    callback,
    *args,
    **kwargs,
):
    """
    Invoke a registered callback.

    Parameters
    ----------
    callback
        Callback object or callback name.

    *args
        Positional arguments forwarded to the callback.

    **kwargs
        Keyword arguments forwarded to the callback.

    Returns
    -------
    object
        Callback return value, or None if the callback is not found or
        disabled.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    if not hasattr(
        self,
        "_callback_registry",
    ):

        return None

    target = None

    #
    # ------------------------------------------------------------------
    # Lookup by callable
    # ------------------------------------------------------------------
    #

    if callable(callback):

        if callback in self._callback_registry:

            target = callback

    #
    # ------------------------------------------------------------------
    # Lookup by callback name
    # ------------------------------------------------------------------
    #

    else:

        for cb, info in self._callback_registry.items():

            if info.get("name") == callback:

                target = cb
                break

    #
    # ------------------------------------------------------------------
    # Callback not found
    # ------------------------------------------------------------------
    #

    if target is None:

        return None

    info = self._callback_registry[target]

    #
    # ------------------------------------------------------------------
    # Disabled callback
    # ------------------------------------------------------------------
    #

    if not info.get(
        "enabled",
        True,
    ):

        return None

    now = time.time()

    try:

        #
        # --------------------------------------------------------------
        # Execute callback
        # --------------------------------------------------------------
        #

        result = target(
            *args,
            **kwargs,
        )

        #
        # --------------------------------------------------------------
        # Statistics
        # --------------------------------------------------------------
        #

        info["invoke_count"] += 1
        info["updated_at"] = now

        self._runtime_data[
            "last_callback_invoked"
        ] = info["name"]

        self._runtime_data[
            "last_callback_result"
        ] = result

        #
        # --------------------------------------------------------------
        # History
        # --------------------------------------------------------------
        #

        self._history.append(
            {
                "event": "invoke_callback",
                "callback": info["name"],
                "timestamp": now,
            }
        )

        #
        # --------------------------------------------------------------
        # Logging
        # --------------------------------------------------------------
        #

        self._logger.debug(
            "Invoked callback '%s'.",
            info["name"],
        )

        return result

    except Exception as exc:

        #
        # --------------------------------------------------------------
        # Statistics
        # --------------------------------------------------------------
        #

        info["exception_count"] += 1
        info["updated_at"] = now

        self.record_exception(
            type(exc),
            exc,
            exc.__traceback__,
        )

        #
        # --------------------------------------------------------------
        # History
        # --------------------------------------------------------------
        #

        self._history.append(
            {
                "event": "callback_exception",
                "callback": info["name"],
                "exception": type(exc).__name__,
                "timestamp": now,
            }
        )

        #
        # --------------------------------------------------------------
        # Logging
        # --------------------------------------------------------------
        #

        self._logger.exception(
            "Callback '%s' failed.",
            info["name"],
        )

        raise
# ==============================================================================
# Part 10.10 – invoke_all_callbacks()
# ==============================================================================

def invoke_all_callbacks(
    self,
    *args,
    ignore_errors=True,
    **kwargs,
):
    """
    Invoke all registered callbacks in priority order.

    Disabled callbacks are skipped automatically.

    Parameters
    ----------
    *args
        Positional arguments forwarded to callbacks.

    ignore_errors
        Continue executing remaining callbacks after an exception.
        If False, the first exception is re-raised.

    **kwargs
        Keyword arguments forwarded to callbacks.

    Returns
    -------
    list
        List of callback return values in execution order.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    if not hasattr(
        self,
        "_callback_registry",
    ):

        return []

    now = time.time()

    results = []

    #
    # ------------------------------------------------------------------
    # Execute callbacks
    # ------------------------------------------------------------------
    #

    for callback in tuple(self._callbacks):

        info = self._callback_registry.get(
            callback,
        )

        if info is None:

            continue

        #
        # --------------------------------------------------------------
        # Skip disabled callbacks
        # --------------------------------------------------------------
        #

        if not info.get(
            "enabled",
            True,
        ):

            continue

        try:

            result = callback(
                *args,
                **kwargs,
            )

            info["invoke_count"] += 1
            info["updated_at"] = now

            results.append(
                result,
            )

        except Exception as exc:

            info["exception_count"] += 1
            info["updated_at"] = now

            self.record_exception(
                type(exc),
                exc,
                exc.__traceback__,
            )

            self._logger.exception(
                "Callback '%s' failed.",
                info["name"],
            )

            if not ignore_errors:

                raise

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    self._runtime_data[
        "last_callback_batch"
    ] = now

    self._runtime_data[
        "last_callback_batch_size"
    ] = len(results)

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    self._history.append(
        {
            "event": "invoke_all_callbacks",
            "executed": len(results),
            "timestamp": now,
        }
    )

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    self._statistics.update_count += 1
    self._statistics.updated_at = now

    #
    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    #

    self._logger.debug(
        "Executed %d callback(s).",
        len(results),
    )

    return results
# ==============================================================================
# Part 10.11 – callback_metadata()
# ==============================================================================

def callback_metadata(
    self,
    callback,
    *,
    update=False,
    **metadata,
):
    """
    Get or update callback metadata.

    Parameters
    ----------
    callback
        Callback object or callback name.

    update
        If True, update the metadata with **metadata.

    **metadata
        Metadata values to update.

    Returns
    -------
    dict | None
        Callback metadata dictionary, or None if the callback
        does not exist.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    if not hasattr(
        self,
        "_callback_registry",
    ):

        return None

    target = None

    #
    # ------------------------------------------------------------------
    # Lookup by callable
    # ------------------------------------------------------------------
    #

    if callable(callback):

        if callback in self._callback_registry:

            target = callback

    #
    # ------------------------------------------------------------------
    # Lookup by callback name
    # ------------------------------------------------------------------
    #

    else:

        for cb, info in self._callback_registry.items():

            if info.get("name") == callback:

                target = cb
                break

    #
    # ------------------------------------------------------------------
    # Callback not found
    # ------------------------------------------------------------------
    #

    if target is None:

        return None

    info = self._callback_registry[target]

    #
    # ------------------------------------------------------------------
    # Update metadata
    # ------------------------------------------------------------------
    #

    if update and metadata:

        now = time.time()

        info.setdefault(
            "metadata",
            {},
        ).update(
            metadata,
        )

        info["updated_at"] = now

        self._runtime_data[
            "last_callback_metadata_update"
        ] = info["name"]

        self._statistics.update_count += 1
        self._statistics.updated_at = now

        self._history.append(
            {
                "event": "callback_metadata_update",
                "callback": info["name"],
                "timestamp": now,
            }
        )

        self._logger.debug(
            "Updated callback metadata '%s'.",
            info["name"],
        )

    #
    # ------------------------------------------------------------------
    # Return metadata copy
    # ------------------------------------------------------------------
    #

    return {
        "name": info["name"],
        "enabled": info["enabled"],
        "priority": info["priority"],
        "metadata": dict(
            info.get(
                "metadata",
                {},
            )
        ),
        "created_at": info["created_at"],
        "updated_at": info["updated_at"],
        "invoke_count": info["invoke_count"],
        "exception_count": info["exception_count"],
    }
# ==============================================================================
# Part 10.12 – callback_statistics()
# ==============================================================================

def callback_statistics(
    self,
    callback=None,
):
    """
    Return callback execution statistics.

    Parameters
    ----------
    callback
        Optional callback object or callback name.
        If None, aggregate statistics for all callbacks are returned.

    Returns
    -------
    dict
        Callback statistics.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    if not hasattr(
        self,
        "_callback_registry",
    ):

        return {}

    #
    # ------------------------------------------------------------------
    # Aggregate statistics
    # ------------------------------------------------------------------
    #

    if callback is None:

        total = len(self._callback_registry)
        enabled = 0
        disabled = 0

        total_invocations = 0
        total_exceptions = 0

        for info in self._callback_registry.values():

            if info.get(
                "enabled",
                True,
            ):

                enabled += 1

            else:

                disabled += 1

            total_invocations += info.get(
                "invoke_count",
                0,
            )

            total_exceptions += info.get(
                "exception_count",
                0,
            )

        success = (
            total_invocations
            - total_exceptions
        )

        success_rate = (
            success / total_invocations
            if total_invocations
            else 1.0
        )

        failure_rate = (
            total_exceptions / total_invocations
            if total_invocations
            else 0.0
        )

        return {
            "total_callbacks": total,
            "enabled_callbacks": enabled,
            "disabled_callbacks": disabled,
            "total_invocations": total_invocations,
            "total_exceptions": total_exceptions,
            "successful_invocations": success,
            "success_rate": success_rate,
            "failure_rate": failure_rate,
        }

    #
    # ------------------------------------------------------------------
    # Lookup callback
    # ------------------------------------------------------------------
    #

    target = None

    if callable(callback):

        if callback in self._callback_registry:

            target = callback

    else:

        for cb, info in self._callback_registry.items():

            if info.get("name") == callback:

                target = cb
                break

    #
    # ------------------------------------------------------------------
    # Callback not found
    # ------------------------------------------------------------------
    #

    if target is None:

        return {}

    info = self._callback_registry[target]

    invocations = info.get(
        "invoke_count",
        0,
    )

    exceptions = info.get(
        "exception_count",
        0,
    )

    successes = invocations - exceptions

    success_rate = (
        successes / invocations
        if invocations
        else 1.0
    )

    failure_rate = (
        exceptions / invocations
        if invocations
        else 0.0
    )

    return {
        "name": info["name"],
        "enabled": info["enabled"],
        "priority": info["priority"],
        "invoke_count": invocations,
        "exception_count": exceptions,
        "success_count": successes,
        "success_rate": success_rate,
        "failure_rate": failure_rate,
        "created_at": info["created_at"],
        "updated_at": info["updated_at"],
    }
# ==============================================================================
# Part 10.13 – callback_history()
# ==============================================================================

def callback_history(
    self,
    callback=None,
    *,
    limit=None,
):
    """
    Return callback execution history.

    Parameters
    ----------
    callback
        Optional callback object or callback name.
        If omitted, the history of all callbacks is returned.

    limit
        Maximum number of history records to return.

    Returns
    -------
    list
        Callback history records.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    history = self._runtime_data.setdefault(
        "callback_history",
        [],
    )

    #
    # ------------------------------------------------------------------
    # Return complete history
    # ------------------------------------------------------------------
    #

    if callback is None:

        records = list(history)

    #
    # ------------------------------------------------------------------
    # Resolve callback name
    # ------------------------------------------------------------------
    #

    else:

        callback_name = None

        if callable(callback):

            if (
                hasattr(self, "_callback_registry")
                and callback in self._callback_registry
            ):

                callback_name = (
                    self._callback_registry[
                        callback
                    ]["name"]
                )

            else:

                callback_name = getattr(
                    callback,
                    "__qualname__",
                    getattr(
                        callback,
                        "__name__",
                        str(callback),
                    ),
                )

        else:

            callback_name = str(callback)

        records = [
            record
            for record in history
            if record.get("callback")
            == callback_name
        ]

    #
    # ------------------------------------------------------------------
    # Apply limit
    # ------------------------------------------------------------------
    #

    if limit is not None:

        limit = max(
            0,
            int(limit),
        )

        records = records[-limit:]

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    self._runtime_data[
        "last_callback_history_query"
    ] = time.time()

    #
    # ------------------------------------------------------------------
    # Return copy
    # ------------------------------------------------------------------
    #

    return [
        dict(record)
        for record in records
    ]
# ==============================================================================
# Part 11.1 – register_hook()
# ==============================================================================

def register_hook(
    self,
    event,
    hook,
    *,
    name=None,
    enabled=True,
    priority=100,
    metadata=None,
):
    """
    Register a runtime hook for a specific event.

    Parameters
    ----------
    event
        Hook event name.

    hook
        Callable hook.

    name
        Optional hook name.

    enabled
        Initial enabled state.

    priority
        Execution priority (smaller executes first).

    metadata
        Optional metadata dictionary.

    Returns
    -------
    callable
        Registered hook.

    Raises
    ------
    TypeError
        If hook is not callable.

    ValueError
        If event is empty.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    if not event:

        raise ValueError(
            "event must not be empty."
        )

    if not callable(hook):

        raise TypeError(
            "hook must be callable."
        )

    event = str(event)

    #
    # ------------------------------------------------------------------
    # Runtime containers
    # ------------------------------------------------------------------
    #

    if not hasattr(
        self,
        "_hooks",
    ):

        self._hooks = {}

    if not hasattr(
        self,
        "_hook_registry",
    ):

        self._hook_registry = {}

    self._hooks.setdefault(
        event,
        [],
    )

    now = time.time()

    hook_name = (
        name
        or getattr(
            hook,
            "__qualname__",
            getattr(
                hook,
                "__name__",
                repr(hook),
            ),
        )
    )

    key = (
        event,
        hook,
    )

    #
    # ------------------------------------------------------------------
    # Already registered
    # ------------------------------------------------------------------
    #

    if key in self._hook_registry:

        return hook

    hook_info = {
        "event": event,
        "hook": hook,
        "name": hook_name,
        "enabled": bool(enabled),
        "priority": int(priority),
        "metadata": dict(metadata or {}),
        "created_at": now,
        "updated_at": now,
        "invoke_count": 0,
        "exception_count": 0,
    }

    #
    # ------------------------------------------------------------------
    # Store hook
    # ------------------------------------------------------------------
    #

    self._hooks[event].append(
        hook,
    )

    self._hook_registry[
        key
    ] = hook_info

    #
    # ------------------------------------------------------------------
    # Sort by priority
    # ------------------------------------------------------------------
    #

    self._hooks[event].sort(
        key=lambda item: self._hook_registry[
            (
                event,
                item,
            )
        ]["priority"]
    )

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    self._runtime_data[
        "hook_count"
    ] = sum(
        len(items)
        for items in self._hooks.values()
    )

    self._runtime_data[
        "last_hook_registered"
    ] = hook_name

    self._updated_at = now

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    self._statistics.update_count += 1
    self._statistics.updated_at = now

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    self._history.append(
        {
            "event": "register_hook",
            "hook": hook_name,
            "hook_event": event,
            "timestamp": now,
        }
    )

    #
    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    #

    self._logger.debug(
        "Registered hook '%s' for event '%s'.",
        hook_name,
        event,
    )

    return hook
# ==============================================================================
# Part 11.2 – unregister_hook()
# ==============================================================================

def unregister_hook(
    self,
    event,
    hook,
):
    """
    Unregister a hook from an event.

    Parameters
    ----------
    event
        Event name.

    hook
        Hook callable or hook name.

    Returns
    -------
    bool
        True if the hook was removed, otherwise False.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    if not hasattr(self, "_hooks"):

        return False

    if not hasattr(self, "_hook_registry"):

        return False

    event = str(event)

    if event not in self._hooks:

        return False

    target = None

    #
    # ------------------------------------------------------------------
    # Lookup by callable
    # ------------------------------------------------------------------
    #

    if callable(hook):

        key = (event, hook)

        if key in self._hook_registry:

            target = hook

    #
    # ------------------------------------------------------------------
    # Lookup by hook name
    # ------------------------------------------------------------------
    #

    else:

        for (registered_event, registered_hook), info in self._hook_registry.items():

            if registered_event != event:

                continue

            if info.get("name") == hook:

                target = registered_hook
                break

    #
    # ------------------------------------------------------------------
    # Hook not found
    # ------------------------------------------------------------------
    #

    if target is None:

        return False

    key = (event, target)

    info = self._hook_registry[key]

    hook_name = info["name"]

    now = time.time()

    #
    # ------------------------------------------------------------------
    # Remove from event list
    # ------------------------------------------------------------------
    #

    try:

        self._hooks[event].remove(
            target,
        )

    except ValueError:

        pass

    #
    # ------------------------------------------------------------------
    # Remove empty event container
    # ------------------------------------------------------------------
    #

    if not self._hooks[event]:

        del self._hooks[event]

    #
    # ------------------------------------------------------------------
    # Remove registry entry
    # ------------------------------------------------------------------
    #

    self._hook_registry.pop(
        key,
        None,
    )

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    self._runtime_data["hook_count"] = sum(
        len(hooks)
        for hooks in self._hooks.values()
    )

    self._runtime_data[
        "last_hook_unregistered"
    ] = hook_name

    self._updated_at = now

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    self._statistics.update_count += 1
    self._statistics.updated_at = now

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    self._history.append(
        {
            "event": "unregister_hook",
            "hook": hook_name,
            "hook_event": event,
            "timestamp": now,
        }
    )

    #
    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    #

    self._logger.debug(
        "Unregistered hook '%s' from event '%s'.",
        hook_name,
        event,
    )

    return True
# ==============================================================================
# Part 11.3 – clear_hooks()
# ==============================================================================

def clear_hooks(
    self,
    event=None,
):
    """
    Remove registered hooks.

    Parameters
    ----------
    event
        Optional event name.

        None
            Remove every registered hook.

        str
            Remove only hooks belonging to the specified event.

    Returns
    -------
    int
        Number of removed hooks.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    if not hasattr(
        self,
        "_hooks",
    ):

        return 0

    if not hasattr(
        self,
        "_hook_registry",
    ):

        return 0

    now = time.time()

    removed = 0

    #
    # ------------------------------------------------------------------
    # Clear all hooks
    # ------------------------------------------------------------------
    #

    if event is None:

        removed = len(
            self._hook_registry
        )

        self._hooks.clear()

        self._hook_registry.clear()

    #
    # ------------------------------------------------------------------
    # Clear hooks for one event
    # ------------------------------------------------------------------
    #

    else:

        event = str(event)

        if event in self._hooks:

            removed = len(
                self._hooks[event]
            )

            for hook in tuple(
                self._hooks[event]
            ):

                self._hook_registry.pop(
                    (
                        event,
                        hook,
                    ),
                    None,
                )

            del self._hooks[event]

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    self._runtime_data[
        "hook_count"
    ] = sum(
        len(hooks)
        for hooks in self._hooks.values()
    )

    self._runtime_data[
        "last_hook_clear"
    ] = (
        event
        if event is not None
        else "__all__"
    )

    self._updated_at = now

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    self._statistics.update_count += 1
    self._statistics.updated_at = now

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    self._history.append(
        {
            "event": "clear_hooks",
            "hook_event": (
                event
                if event is not None
                else "__all__"
            ),
            "removed": removed,
            "timestamp": now,
        }
    )

    #
    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    #

    if event is None:

        self._logger.debug(
            "Cleared %d hook(s).",
            removed,
        )

    else:

        self._logger.debug(
            "Cleared %d hook(s) from event '%s'.",
            removed,
            event,
        )

    return removed
# ==============================================================================
# Part 11.4 – get_hooks()
# ==============================================================================

def get_hooks(
    self,
    event=None,
    *,
    enabled_only=False,
    include_metadata=False,
):
    """
    Return registered hooks.

    Parameters
    ----------
    event
        Optional event name.

        None
            Return hooks from every event.

    enabled_only
        Return only enabled hooks.

    include_metadata
        Return hook registry records instead of callable objects.

    Returns
    -------
    list
        Registered hooks or hook metadata records.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    if not hasattr(
        self,
        "_hooks",
    ):

        return []

    if not hasattr(
        self,
        "_hook_registry",
    ):

        return []

    records = []

    #
    # ------------------------------------------------------------------
    # Select events
    # ------------------------------------------------------------------
    #

    if event is None:

        events = list(
            self._hooks.keys()
        )

    else:

        event = str(event)

        if event not in self._hooks:

            return []

        events = [event]

    #
    # ------------------------------------------------------------------
    # Collect hooks
    # ------------------------------------------------------------------
    #

    for event_name in events:

        for hook in self._hooks[event_name]:

            info = self._hook_registry.get(
                (
                    event_name,
                    hook,
                )
            )

            if info is None:

                continue

            #
            # ----------------------------------------------------------
            # Enabled filter
            # ----------------------------------------------------------
            #

            if (
                enabled_only
                and not info.get(
                    "enabled",
                    True,
                )
            ):

                continue

            #
            # ----------------------------------------------------------
            # Metadata
            # ----------------------------------------------------------
            #

            if include_metadata:

                records.append(
                    dict(info)
                )

            #
            # ----------------------------------------------------------
            # Callable
            # ----------------------------------------------------------
            #

            else:

                records.append(
                    hook
                )

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    self._runtime_data[
        "last_hook_query"
    ] = time.time()

    return records
# ==============================================================================
# Part 11.5 – has_hook()
# ==============================================================================

def has_hook(
    self,
    event,
    hook,
):
    """
    Determine whether a hook is registered for an event.

    Parameters
    ----------
    event
        Event name.

    hook
        Hook callable or hook name.

    Returns
    -------
    bool
        True if the hook exists for the specified event,
        otherwise False.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    if not hasattr(
        self,
        "_hook_registry",
    ):

        return False

    event = str(event)

    #
    # ------------------------------------------------------------------
    # Lookup by callable
    # ------------------------------------------------------------------
    #

    if callable(hook):

        return (
            event,
            hook,
        ) in self._hook_registry

    #
    # ------------------------------------------------------------------
    # Lookup by hook name
    # ------------------------------------------------------------------
    #

    for (registered_event, _), info in self._hook_registry.items():

        if registered_event != event:

            continue

        if info.get("name") == hook:

            return True

    #
    # ------------------------------------------------------------------
    # Hook not found
    # ------------------------------------------------------------------
    #

    return False
# ==============================================================================
# Part 11.6 – hook_count()
# ==============================================================================

def hook_count(
    self,
    event=None,
    *,
    enabled_only=False,
):
    """
    Return the number of registered hooks.

    Parameters
    ----------
    event
        Optional event name.

        None
            Count hooks from every event.

    enabled_only
        Count only enabled hooks.

    Returns
    -------
    int
        Number of registered hooks.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    if not hasattr(
        self,
        "_hook_registry",
    ):

        return 0

    #
    # ------------------------------------------------------------------
    # Count hooks
    # ------------------------------------------------------------------
    #

    count = 0

    if event is None:

        iterable = self._hook_registry.items()

    else:

        event = str(event)

        iterable = (
            item
            for item in self._hook_registry.items()
            if item[0][0] == event
        )

    for _, info in iterable:

        if enabled_only:

            if not info.get(
                "enabled",
                True,
            ):

                continue

        count += 1

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    self._runtime_data[
        "hook_count"
    ] = count

    self._runtime_data[
        "last_hook_count"
    ] = time.time()

    return count
# ==============================================================================
# Part 11.7 – enable_hook()
# ==============================================================================

def enable_hook(
    self,
    event,
    hook,
):
    """
    Enable a registered hook.

    Parameters
    ----------
    event
        Event name.

    hook
        Hook callable or hook name.

    Returns
    -------
    bool
        True if the hook was enabled, otherwise False.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    if not hasattr(
        self,
        "_hook_registry",
    ):

        return False

    event = str(event)

    target = None

    #
    # ------------------------------------------------------------------
    # Lookup by callable
    # ------------------------------------------------------------------
    #

    if callable(hook):

        key = (
            event,
            hook,
        )

        if key in self._hook_registry:

            target = key

    #
    # ------------------------------------------------------------------
    # Lookup by hook name
    # ------------------------------------------------------------------
    #

    else:

        for key, info in self._hook_registry.items():

            if key[0] != event:

                continue

            if info.get("name") == hook:

                target = key
                break

    #
    # ------------------------------------------------------------------
    # Hook not found
    # ------------------------------------------------------------------
    #

    if target is None:

        return False

    info = self._hook_registry[target]

    #
    # ------------------------------------------------------------------
    # Already enabled
    # ------------------------------------------------------------------
    #

    if info.get(
        "enabled",
        True,
    ):

        return True

    now = time.time()

    #
    # ------------------------------------------------------------------
    # Enable hook
    # ------------------------------------------------------------------
    #

    info["enabled"] = True
    info["updated_at"] = now

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    self._runtime_data[
        "last_hook_enabled"
    ] = info["name"]

    self._runtime_data[
        "hook_count"
    ] = self.hook_count()

    self._updated_at = now

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    self._statistics.update_count += 1
    self._statistics.updated_at = now

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    self._history.append(
        {
            "event": "enable_hook",
            "hook": info["name"],
            "hook_event": event,
            "timestamp": now,
        }
    )

    #
    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    #

    self._logger.debug(
        "Enabled hook '%s' for event '%s'.",
        info["name"],
        event,
    )

    return True
# ==============================================================================
# Part 11.8 – disable_hook()
# ==============================================================================

def disable_hook(
    self,
    event,
    hook,
):
    """
    Disable a registered hook.

    Parameters
    ----------
    event
        Event name.

    hook
        Hook callable or hook name.

    Returns
    -------
    bool
        True if the hook was disabled, otherwise False.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    if not hasattr(
        self,
        "_hook_registry",
    ):

        return False

    event = str(event)

    target = None

    #
    # ------------------------------------------------------------------
    # Lookup by callable
    # ------------------------------------------------------------------
    #

    if callable(hook):

        key = (
            event,
            hook,
        )

        if key in self._hook_registry:

            target = key

    #
    # ------------------------------------------------------------------
    # Lookup by hook name
    # ------------------------------------------------------------------
    #

    else:

        for key, info in self._hook_registry.items():

            if key[0] != event:

                continue

            if info.get("name") == hook:

                target = key
                break

    #
    # ------------------------------------------------------------------
    # Hook not found
    # ------------------------------------------------------------------
    #

    if target is None:

        return False

    info = self._hook_registry[target]

    #
    # ------------------------------------------------------------------
    # Already disabled
    # ------------------------------------------------------------------
    #

    if not info.get(
        "enabled",
        True,
    ):

        return True

    now = time.time()

    #
    # ------------------------------------------------------------------
    # Disable hook
    # ------------------------------------------------------------------
    #

    info["enabled"] = False
    info["updated_at"] = now

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    self._runtime_data[
        "last_hook_disabled"
    ] = info["name"]

    self._runtime_data[
        "hook_count"
    ] = self.hook_count()

    self._updated_at = now

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    self._statistics.update_count += 1
    self._statistics.updated_at = now

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    self._history.append(
        {
            "event": "disable_hook",
            "hook": info["name"],
            "hook_event": event,
            "timestamp": now,
        }
    )

    #
    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    #

    self._logger.debug(
        "Disabled hook '%s' for event '%s'.",
        info["name"],
        event,
    )

    return True
# ==============================================================================
# Part 11.9 – invoke_hook()
# ==============================================================================

def invoke_hook(
    self,
    event,
    hook,
    *args,
    **kwargs,
):
    """
    Invoke a registered hook.

    Parameters
    ----------
    event
        Event name.

    hook
        Hook callable or hook name.

    *args
        Positional arguments forwarded to the hook.

    **kwargs
        Keyword arguments forwarded to the hook.

    Returns
    -------
    object
        Hook return value.

    Raises
    ------
    Exception
        Re-raises any exception raised by the hook.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    if not hasattr(
        self,
        "_hook_registry",
    ):

        return None

    event = str(event)

    target = None

    #
    # ------------------------------------------------------------------
    # Lookup by callable
    # ------------------------------------------------------------------
    #

    if callable(hook):

        key = (
            event,
            hook,
        )

        if key in self._hook_registry:

            target = key

    #
    # ------------------------------------------------------------------
    # Lookup by hook name
    # ------------------------------------------------------------------
    #

    else:

        for key, info in self._hook_registry.items():

            if key[0] != event:

                continue

            if info.get("name") == hook:

                target = key
                break

    #
    # ------------------------------------------------------------------
    # Hook not found
    # ------------------------------------------------------------------
    #

    if target is None:

        return None

    info = self._hook_registry[target]

    #
    # ------------------------------------------------------------------
    # Disabled hook
    # ------------------------------------------------------------------
    #

    if not info.get(
        "enabled",
        True,
    ):

        return None

    now = time.time()

    try:

        #
        # --------------------------------------------------------------
        # Execute hook
        # --------------------------------------------------------------
        #

        result = info["hook"](
            *args,
            **kwargs,
        )

        #
        # --------------------------------------------------------------
        # Statistics
        # --------------------------------------------------------------
        #

        info["invoke_count"] += 1
        info["updated_at"] = now

        self._runtime_data[
            "last_hook_invoked"
        ] = info["name"]

        self._runtime_data[
            "last_hook_event"
        ] = event

        self._runtime_data[
            "last_hook_result"
        ] = result

        #
        # --------------------------------------------------------------
        # History
        # --------------------------------------------------------------
        #

        self._runtime_data.setdefault(
            "hook_history",
            [],
        ).append(
            {
                "event": event,
                "hook": info["name"],
                "success": True,
                "timestamp": now,
            }
        )

        self._history.append(
            {
                "event": "invoke_hook",
                "hook": info["name"],
                "hook_event": event,
                "timestamp": now,
            }
        )

        #
        # --------------------------------------------------------------
        # Logging
        # --------------------------------------------------------------
        #

        self._logger.debug(
            "Invoked hook '%s' for event '%s'.",
            info["name"],
            event,
        )

        return result

    except Exception as exc:

        #
        # --------------------------------------------------------------
        # Statistics
        # --------------------------------------------------------------
        #

        info["exception_count"] += 1
        info["updated_at"] = now

        self.record_exception(
            type(exc),
            exc,
            exc.__traceback__,
        )

        #
        # --------------------------------------------------------------
        # History
        # --------------------------------------------------------------
        #

        self._runtime_data.setdefault(
            "hook_history",
            [],
        ).append(
            {
                "event": event,
                "hook": info["name"],
                "success": False,
                "exception": type(exc).__name__,
                "timestamp": now,
            }
        )

        self._history.append(
            {
                "event": "hook_exception",
                "hook": info["name"],
                "hook_event": event,
                "exception": type(exc).__name__,
                "timestamp": now,
            }
        )

        #
        # --------------------------------------------------------------
        # Logging
        # --------------------------------------------------------------
        #

        self._logger.exception(
            "Hook '%s' failed during '%s'.",
            info["name"],
            event,
        )

        raise
# ==============================================================================
# Part 11.10 – invoke_all_hooks()
# ==============================================================================

def invoke_all_hooks(
    self,
    event,
    *args,
    ignore_errors=True,
    **kwargs,
):
    """
    Invoke all hooks registered for an event.

    Hooks are executed in ascending priority order.
    Disabled hooks are skipped automatically.

    Parameters
    ----------
    event
        Event name.

    *args
        Positional arguments forwarded to every hook.

    ignore_errors
        Continue invoking remaining hooks after an exception.
        If False, the first exception is re-raised.

    **kwargs
        Keyword arguments forwarded to every hook.

    Returns
    -------
    list
        List of hook return values.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    if not hasattr(
        self,
        "_hooks",
    ):

        return []

    if not hasattr(
        self,
        "_hook_registry",
    ):

        return []

    event = str(event)

    if event not in self._hooks:

        return []

    now = time.time()

    results = []
    executed = 0
    failed = 0

    #
    # ------------------------------------------------------------------
    # Execute hooks
    # ------------------------------------------------------------------
    #

    for hook in tuple(self._hooks[event]):

        info = self._hook_registry.get(
            (
                event,
                hook,
            )
        )

        if info is None:

            continue

        #
        # --------------------------------------------------------------
        # Skip disabled hooks
        # --------------------------------------------------------------
        #

        if not info.get(
            "enabled",
            True,
        ):

            continue

        try:

            result = hook(
                *args,
                **kwargs,
            )

            executed += 1

            info["invoke_count"] += 1
            info["updated_at"] = now

            results.append(
                result,
            )

            #
            # ----------------------------------------------------------
            # Runtime hook history
            # ----------------------------------------------------------
            #

            self._runtime_data.setdefault(
                "hook_history",
                [],
            ).append(
                {
                    "event": event,
                    "hook": info["name"],
                    "success": True,
                    "timestamp": now,
                }
            )

        except Exception as exc:

            failed += 1

            info["exception_count"] += 1
            info["updated_at"] = now

            self.record_exception(
                type(exc),
                exc,
                exc.__traceback__,
            )

            self._runtime_data.setdefault(
                "hook_history",
                [],
            ).append(
                {
                    "event": event,
                    "hook": info["name"],
                    "success": False,
                    "exception": type(exc).__name__,
                    "timestamp": now,
                }
            )

            self._logger.exception(
                "Hook '%s' failed during '%s'.",
                info["name"],
                event,
            )

            if not ignore_errors:

                raise

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    self._runtime_data[
        "last_hook_batch"
    ] = now

    self._runtime_data[
        "last_hook_event"
    ] = event

    self._runtime_data[
        "last_hook_batch_size"
    ] = executed

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    self._statistics.update_count += 1
    self._statistics.updated_at = now

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    self._history.append(
        {
            "event": "invoke_all_hooks",
            "hook_event": event,
            "executed": executed,
            "failed": failed,
            "timestamp": now,
        }
    )

    #
    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    #

    self._logger.debug(
        "Executed %d hook(s) for '%s' (%d failed).",
        executed,
        event,
        failed,
    )

    return results
# ==============================================================================
# Part 11.11 – hook_metadata()
# ==============================================================================

def hook_metadata(
    self,
    event,
    hook,
    *,
    update=False,
    **metadata,
):
    """
    Get or update hook metadata.

    Parameters
    ----------
    event
        Event name.

    hook
        Hook callable or hook name.

    update
        Update metadata if True.

    **metadata
        Metadata values.

    Returns
    -------
    dict | None
        Hook metadata.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    if not hasattr(
        self,
        "_hook_registry",
    ):

        return None

    event = str(event)

    target = None

    #
    # ------------------------------------------------------------------
    # Lookup by callable
    # ------------------------------------------------------------------
    #

    if callable(hook):

        key = (
            event,
            hook,
        )

        if key in self._hook_registry:

            target = key

    #
    # ------------------------------------------------------------------
    # Lookup by hook name
    # ------------------------------------------------------------------
    #

    else:

        for key, info in self._hook_registry.items():

            if key[0] != event:

                continue

            if info.get("name") == hook:

                target = key
                break

    #
    # ------------------------------------------------------------------
    # Hook not found
    # ------------------------------------------------------------------
    #

    if target is None:

        return None

    info = self._hook_registry[target]

    #
    # ------------------------------------------------------------------
    # Update metadata
    # ------------------------------------------------------------------
    #

    if update and metadata:

        now = time.time()

        info.setdefault(
            "metadata",
            {},
        ).update(
            metadata,
        )

        info["updated_at"] = now

        self._runtime_data[
            "last_hook_metadata_update"
        ] = info["name"]

        self._statistics.update_count += 1
        self._statistics.updated_at = now

        self._history.append(
            {
                "event": "hook_metadata_update",
                "hook": info["name"],
                "hook_event": event,
                "timestamp": now,
            }
        )

        self._logger.debug(
            "Updated hook metadata '%s'.",
            info["name"],
        )

    #
    # ------------------------------------------------------------------
    # Return metadata copy
    # ------------------------------------------------------------------
    #

    return {
        "event": info["event"],
        "name": info["name"],
        "enabled": info["enabled"],
        "priority": info["priority"],
        "metadata": dict(
            info.get(
                "metadata",
                {},
            )
        ),
        "created_at": info["created_at"],
        "updated_at": info["updated_at"],
        "invoke_count": info["invoke_count"],
        "exception_count": info["exception_count"],
    }
# ==============================================================================
# Part 11.12 – hook_statistics()
# ==============================================================================

def hook_statistics(
    self,
    event=None,
    hook=None,
):
    """
    Return hook execution statistics.

    Parameters
    ----------
    event
        Optional event name.

    hook
        Optional hook callable or hook name.

    Returns
    -------
    dict
        Hook statistics.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    if not hasattr(
        self,
        "_hook_registry",
    ):

        return {}

    #
    # ------------------------------------------------------------------
    # Aggregate statistics
    # ------------------------------------------------------------------
    #

    if hook is None:

        total = 0
        enabled = 0
        disabled = 0

        invocations = 0
        exceptions = 0

        for (registered_event, _), info in self._hook_registry.items():

            if (
                event is not None
                and registered_event != str(event)
            ):

                continue

            total += 1

            if info.get(
                "enabled",
                True,
            ):

                enabled += 1

            else:

                disabled += 1

            invocations += info.get(
                "invoke_count",
                0,
            )

            exceptions += info.get(
                "exception_count",
                0,
            )

        successes = (
            invocations
            - exceptions
        )

        success_rate = (
            successes / invocations
            if invocations
            else 1.0
        )

        failure_rate = (
            exceptions / invocations
            if invocations
            else 0.0
        )

        return {
            "event": event,
            "total_hooks": total,
            "enabled_hooks": enabled,
            "disabled_hooks": disabled,
            "total_invocations": invocations,
            "total_exceptions": exceptions,
            "success_count": successes,
            "success_rate": success_rate,
            "failure_rate": failure_rate,
        }

    #
    # ------------------------------------------------------------------
    # Lookup hook
    # ------------------------------------------------------------------
    #

    if event is None:

        return {}

    event = str(event)

    target = None

    if callable(hook):

        key = (
            event,
            hook,
        )

        if key in self._hook_registry:

            target = key

    else:

        for key, info in self._hook_registry.items():

            if key[0] != event:

                continue

            if info.get("name") == hook:

                target = key
                break

    #
    # ------------------------------------------------------------------
    # Hook not found
    # ------------------------------------------------------------------
    #

    if target is None:

        return {}

    info = self._hook_registry[target]

    invocations = info.get(
        "invoke_count",
        0,
    )

    exceptions = info.get(
        "exception_count",
        0,
    )

    successes = (
        invocations
        - exceptions
    )

    success_rate = (
        successes / invocations
        if invocations
        else 1.0
    )

    failure_rate = (
        exceptions / invocations
        if invocations
        else 0.0
    )

    return {
        "event": info["event"],
        "name": info["name"],
        "enabled": info["enabled"],
        "priority": info["priority"],
        "invoke_count": invocations,
        "exception_count": exceptions,
        "success_count": successes,
        "success_rate": success_rate,
        "failure_rate": failure_rate,
        "created_at": info["created_at"],
        "updated_at": info["updated_at"],
    }
# ==============================================================================
# Part 11.13 – hook_history()
# ==============================================================================

def hook_history(
    self,
    event=None,
    hook=None,
    *,
    limit=None,
):
    """
    Return hook execution history.

    Parameters
    ----------
    event
        Optional event name.

    hook
        Optional hook callable or hook name.

    limit
        Maximum number of history records.

    Returns
    -------
    list
        Hook history records.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    history = self._runtime_data.setdefault(
        "hook_history",
        [],
    )

    records = list(history)

    #
    # ------------------------------------------------------------------
    # Filter by event
    # ------------------------------------------------------------------
    #

    if event is not None:

        event = str(event)

        records = [
            record
            for record in records
            if record.get("event") == event
        ]

    #
    # ------------------------------------------------------------------
    # Filter by hook
    # ------------------------------------------------------------------
    #

    if hook is not None:

        if callable(hook):

            if (
                hasattr(self, "_hook_registry")
                and event is not None
                and (event, hook) in self._hook_registry
            ):

                hook_name = self._hook_registry[
                    (
                        event,
                        hook,
                    )
                ]["name"]

            else:

                hook_name = getattr(
                    hook,
                    "__qualname__",
                    getattr(
                        hook,
                        "__name__",
                        str(hook),
                    ),
                )

        else:

            hook_name = str(hook)

        records = [
            record
            for record in records
            if record.get("hook") == hook_name
        ]

    #
    # ------------------------------------------------------------------
    # Apply limit
    # ------------------------------------------------------------------
    #

    if limit is not None:

        limit = max(
            0,
            int(limit),
        )

        records = records[-limit:]

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    self._runtime_data[
        "last_hook_history_query"
    ] = time.time()

    #
    # ------------------------------------------------------------------
    # Return copy
    # ------------------------------------------------------------------
    #

    return [
        dict(record)
        for record in records
    ]
# ==============================================================================
# Part 12.1 – snapshot()
# ==============================================================================

def snapshot(
    self,
):
    """
    Create a runtime snapshot.

    Returns
    -------
    dict
        Immutable snapshot of the current runtime state.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    now = time.time()

    #
    # ------------------------------------------------------------------
    # Snapshot
    # ------------------------------------------------------------------
    #

    snapshot = {
        #
        # Identity
        #
        "id": self._id,
        "uuid": self._uuid,
        "name": self._name,
        "description": self._description,
        "version": self._version,
        "scope_type": self._scope_type,

        #
        # Runtime state
        #
        "initialized": self._initialized,
        "running": self._running,
        "active": self._active,
        "entered": self._entered,
        "exited": self._exited,
        "frozen": self._frozen,
        "closed": self._closed,
        "disposed": self._disposed,
        "state": self._state,
        "status": self._status,

        #
        # Timing
        #
        "created_at": self._created_at,
        "updated_at": self._updated_at,
        "start_time": self._start_time,
        "end_time": self._end_time,

        #
        # Metadata
        #
        "metadata": copy.deepcopy(
            self._metadata,
        ),
        "attributes": copy.deepcopy(
            self._attributes,
        ),
        "tags": copy.deepcopy(
            self._tags,
        ),
        "labels": copy.deepcopy(
            self._labels,
        ),
        "notes": copy.deepcopy(
            self._notes,
        ),

        #
        # Runtime containers
        #
        "runtime_data": copy.deepcopy(
            self._runtime_data,
        ),
        "cache": copy.deepcopy(
            self._cache,
        ),
        "history": copy.deepcopy(
            self._history,
        ),
        "extensions": copy.deepcopy(
            self._extensions,
        ),

        #
        # Statistics
        #
        "statistics": copy.deepcopy(
            self._statistics,
        ),

        #
        # Callback / Hook registry
        #
        "callback_registry": copy.deepcopy(
            getattr(
                self,
                "_callback_registry",
                {},
            ),
        ),
        "hook_registry": copy.deepcopy(
            getattr(
                self,
                "_hook_registry",
                {},
            ),
        ),

        #
        # Snapshot metadata
        #
        "snapshot_time": now,
        "snapshot_version": 1,
    }

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    self._runtime_data[
        "last_snapshot"
    ] = now

    self._history.append(
        {
            "event": "snapshot",
            "timestamp": now,
        }
    )

    #
    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    #

    self._logger.debug(
        "Runtime snapshot created."
    )

    return snapshot
# ==============================================================================
# Part 12.2 – restore()
# ==============================================================================

def restore(
    self,
    snapshot,
):
    """
    Restore runtime state from a snapshot.

    Parameters
    ----------
    snapshot
        Snapshot previously produced by ``snapshot()``.

    Returns
    -------
    SpanScope
        Self.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    if not isinstance(
        snapshot,
        dict,
    ):

        raise TypeError(
            "snapshot must be a dictionary."
        )

    now = time.time()

    #
    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------
    #

    self._id = snapshot.get(
        "id",
        self._id,
    )

    self._uuid = snapshot.get(
        "uuid",
        self._uuid,
    )

    self._name = snapshot.get(
        "name",
        self._name,
    )

    self._description = snapshot.get(
        "description",
        self._description,
    )

    self._version = snapshot.get(
        "version",
        self._version,
    )

    self._scope_type = snapshot.get(
        "scope_type",
        self._scope_type,
    )

    #
    # ------------------------------------------------------------------
    # Runtime state
    # ------------------------------------------------------------------
    #

    self._initialized = snapshot.get(
        "initialized",
        self._initialized,
    )

    self._running = snapshot.get(
        "running",
        self._running,
    )

    self._active = snapshot.get(
        "active",
        self._active,
    )

    self._entered = snapshot.get(
        "entered",
        self._entered,
    )

    self._exited = snapshot.get(
        "exited",
        self._exited,
    )

    self._frozen = snapshot.get(
        "frozen",
        self._frozen,
    )

    self._closed = snapshot.get(
        "closed",
        self._closed,
    )

    self._disposed = snapshot.get(
        "disposed",
        self._disposed,
    )

    self._state = snapshot.get(
        "state",
        self._state,
    )

    self._status = snapshot.get(
        "status",
        self._status,
    )

    #
    # ------------------------------------------------------------------
    # Timing
    # ------------------------------------------------------------------
    #

    self._created_at = snapshot.get(
        "created_at",
        self._created_at,
    )

    self._updated_at = snapshot.get(
        "updated_at",
        now,
    )

    self._start_time = snapshot.get(
        "start_time",
        self._start_time,
    )

    self._end_time = snapshot.get(
        "end_time",
        self._end_time,
    )

    #
    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------
    #

    self._metadata = copy.deepcopy(
        snapshot.get(
            "metadata",
            {},
        )
    )

    self._attributes = copy.deepcopy(
        snapshot.get(
            "attributes",
            {},
        )
    )

    self._tags = copy.deepcopy(
        snapshot.get(
            "tags",
            [],
        )
    )

    self._labels = copy.deepcopy(
        snapshot.get(
            "labels",
            {},
        )
    )

    self._notes = copy.deepcopy(
        snapshot.get(
            "notes",
            [],
        )
    )

    #
    # ------------------------------------------------------------------
    # Runtime containers
    # ------------------------------------------------------------------
    #

    self._runtime_data = copy.deepcopy(
        snapshot.get(
            "runtime_data",
            {},
        )
    )

    self._cache = copy.deepcopy(
        snapshot.get(
            "cache",
            {},
        )
    )

    self._history = copy.deepcopy(
        snapshot.get(
            "history",
            [],
        )
    )

    self._extensions = copy.deepcopy(
        snapshot.get(
            "extensions",
            {},
        )
    )

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    self._statistics = copy.deepcopy(
        snapshot.get(
            "statistics",
            self._statistics,
        )
    )

    #
    # ------------------------------------------------------------------
    # Callback / Hook registry
    # ------------------------------------------------------------------
    #

    self._callback_registry = copy.deepcopy(
        snapshot.get(
            "callback_registry",
            {},
        )
    )

    self._hook_registry = copy.deepcopy(
        snapshot.get(
            "hook_registry",
            {},
        )
    )

    #
    # ------------------------------------------------------------------
    # Rebuild callback container
    # ------------------------------------------------------------------
    #

    self._callbacks = []

    for callback in self._callback_registry:

        self._callbacks.append(
            callback,
        )

    #
    # ------------------------------------------------------------------
    # Rebuild hook container
    # ------------------------------------------------------------------
    #

    self._hooks = {}

    for (event, hook), _ in self._hook_registry.items():

        self._hooks.setdefault(
            event,
            [],
        ).append(
            hook,
        )

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    self._runtime_data[
        "last_restore"
    ] = now

    self._history.append(
        {
            "event": "restore",
            "timestamp": now,
        }
    )

    #
    # ------------------------------------------------------------------
    # Logger
    # ------------------------------------------------------------------
    #

    self._logger.debug(
        "Runtime restored from snapshot."
    )

    return self
# ==============================================================================
# Part 12.3 – clone()
# ==============================================================================

def clone(
    self,
):
    """
    Create a deep clone of this SpanScope.

    Returns
    -------
    SpanScope
        Independent cloned instance.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    #
    # ------------------------------------------------------------------
    # Create clone
    # ------------------------------------------------------------------
    #

    cloned = self.__class__()

    #
    # ------------------------------------------------------------------
    # Restore snapshot
    # ------------------------------------------------------------------
    #

    cloned.restore(
        self.snapshot(),
    )

    #
    # ------------------------------------------------------------------
    # Generate new identity
    # ------------------------------------------------------------------
    #

    cloned._id = uuid.uuid4().hex

    cloned._uuid = uuid.uuid4()

    cloned._created_at = time.time()

    cloned._updated_at = cloned._created_at

    cloned._runtime_data[
        "cloned_from"
    ] = self._uuid

    cloned._runtime_data[
        "clone_time"
    ] = cloned._created_at

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    cloned._history.append(
        {
            "event": "clone",
            "source_uuid": str(
                self._uuid,
            ),
            "timestamp": cloned._created_at,
        }
    )

    #
    # ------------------------------------------------------------------
    # Logger
    # ------------------------------------------------------------------
    #

    cloned._logger.debug(
        "Runtime cloned from %s.",
        self._uuid,
    )

    return cloned
# ==============================================================================
# Part 12.4 – copy()
# ==============================================================================

def copy(
    self,
):
    """
    Create a shallow runtime copy.

    Unlike ``clone()``, the copied object preserves the same
    runtime identity.

    Returns
    -------
    SpanScope
        Copied instance.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    copied = self.__class__()

    #
    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------
    #

    copied._id = self._id
    copied._uuid = self._uuid
    copied._name = self._name
    copied._description = self._description
    copied._version = self._version
    copied._scope_type = self._scope_type

    #
    # ------------------------------------------------------------------
    # Runtime state
    # ------------------------------------------------------------------
    #

    copied._initialized = self._initialized
    copied._running = self._running
    copied._active = self._active
    copied._entered = self._entered
    copied._exited = self._exited
    copied._frozen = self._frozen
    copied._closed = self._closed
    copied._disposed = self._disposed
    copied._state = self._state
    copied._status = self._status

    #
    # ------------------------------------------------------------------
    # Timing
    # ------------------------------------------------------------------
    #

    copied._created_at = self._created_at
    copied._updated_at = self._updated_at
    copied._start_time = self._start_time
    copied._end_time = self._end_time

    #
    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------
    #

    copied._metadata = copy.deepcopy(
        self._metadata,
    )

    copied._attributes = copy.deepcopy(
        self._attributes,
    )

    copied._tags = copy.deepcopy(
        self._tags,
    )

    copied._labels = copy.deepcopy(
        self._labels,
    )

    copied._notes = copy.deepcopy(
        self._notes,
    )

    copied._extensions = copy.deepcopy(
        self._extensions,
    )

    #
    # ------------------------------------------------------------------
    # Runtime containers
    # ------------------------------------------------------------------
    #

    copied._runtime_data = copy.deepcopy(
        self._runtime_data,
    )

    copied._cache = copy.deepcopy(
        self._cache,
    )

    copied._history = copy.deepcopy(
        self._history,
    )

    copied._statistics = copy.deepcopy(
        self._statistics,
    )

    #
    # ------------------------------------------------------------------
    # Callback / Hook registry
    # ------------------------------------------------------------------
    #

    copied._callback_registry = copy.deepcopy(
        getattr(
            self,
            "_callback_registry",
            {},
        )
    )

    copied._callbacks = list(
        getattr(
            self,
            "_callbacks",
            [],
        )
    )

    copied._hook_registry = copy.deepcopy(
        getattr(
            self,
            "_hook_registry",
            {},
        )
    )

    copied._hooks = {
        key: list(value)
        for key, value in getattr(
            self,
            "_hooks",
            {},
        ).items()
    }

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    now = time.time()

    copied._runtime_data[
        "copied_at"
    ] = now

    copied._runtime_data[
        "copied_from"
    ] = self._uuid

    copied._history.append(
        {
            "event": "copy",
            "timestamp": now,
        }
    )

    #
    # ------------------------------------------------------------------
    # Logger
    # ------------------------------------------------------------------
    #

    copied._logger.debug(
        "Runtime copied."
    )

    return copied
# ==============================================================================
# Part 12.5 – clear()
# ==============================================================================

def clear(
    self,
    *,
    keep_identity=True,
    keep_configuration=True,
):
    """
    Clear runtime data.

    Parameters
    ----------
    keep_identity
        Preserve runtime identity.

    keep_configuration
        Preserve configuration values.

    Returns
    -------
    SpanScope
        Self.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    now = time.time()

    #
    # ------------------------------------------------------------------
    # Runtime state
    # ------------------------------------------------------------------
    #

    self._running = False
    self._active = False
    self._entered = False
    self._exited = False

    self._state = "idle"
    self._status = "cleared"

    self._start_time = None
    self._end_time = None

    self._updated_at = now

    #
    # ------------------------------------------------------------------
    # Runtime containers
    # ------------------------------------------------------------------
    #

    self._runtime_data.clear()
    self._cache.clear()
    self._history.clear()

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    self._statistics.reset()

    #
    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------
    #

    self._notes.clear()

    #
    # ------------------------------------------------------------------
    # Callback / Hook runtime statistics
    # ------------------------------------------------------------------
    #

    for info in getattr(
        self,
        "_callback_registry",
        {},
    ).values():

        info["invoke_count"] = 0
        info["exception_count"] = 0
        info["updated_at"] = now

    for info in getattr(
        self,
        "_hook_registry",
        {},
    ).values():

        info["invoke_count"] = 0
        info["exception_count"] = 0
        info["updated_at"] = now

    #
    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------
    #

    if not keep_identity:

        self._id = uuid.uuid4().hex
        self._uuid = uuid.uuid4()

        self._created_at = now

    #
    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------
    #

    if not keep_configuration:

        self._enabled = True
        self._auto_start = False
        self._auto_finish = False

        self._timeout = None
        self._history_limit = 1000

        self._options.clear()
        self._capabilities.clear()

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    self._runtime_data[
        "last_clear"
    ] = now

    self._history.append(
        {
            "event": "clear",
            "timestamp": now,
        }
    )

    #
    # ------------------------------------------------------------------
    # Logger
    # ------------------------------------------------------------------
    #

    self._logger.debug(
        "Runtime cleared."
    )

    return self
# ==============================================================================
# Part 12.6 – reset_runtime()
# ==============================================================================

def reset_runtime(
    self,
):
    """
    Reset the runtime to its initial operational state.

    Runtime identity, configuration, callbacks and hooks are preserved.

    Returns
    -------
    SpanScope
        Self.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    now = time.time()

    #
    # ------------------------------------------------------------------
    # Runtime state
    # ------------------------------------------------------------------
    #

    self._initialized = True

    self._running = False
    self._active = False

    self._entered = False
    self._exited = False

    self._frozen = False
    self._closed = False
    self._disposed = False

    self._state = "ready"
    self._status = "initialized"

    #
    # ------------------------------------------------------------------
    # Timing
    # ------------------------------------------------------------------
    #

    self._start_time = None
    self._end_time = None
    self._updated_at = now

    #
    # ------------------------------------------------------------------
    # Runtime containers
    # ------------------------------------------------------------------
    #

    self._runtime_data.clear()
    self._cache.clear()

    #
    # ------------------------------------------------------------------
    # Runtime history
    # ------------------------------------------------------------------
    #

    self._history.clear()

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    self._statistics.reset()

    #
    # ------------------------------------------------------------------
    # Callback runtime statistics
    # ------------------------------------------------------------------
    #

    for info in getattr(
        self,
        "_callback_registry",
        {},
    ).values():

        info["invoke_count"] = 0
        info["exception_count"] = 0
        info["updated_at"] = now

    #
    # ------------------------------------------------------------------
    # Hook runtime statistics
    # ------------------------------------------------------------------
    #

    for info in getattr(
        self,
        "_hook_registry",
        {},
    ).values():

        info["invoke_count"] = 0
        info["exception_count"] = 0
        info["updated_at"] = now

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    self._runtime_data[
        "runtime_reset_at"
    ] = now

    self._history.append(
        {
            "event": "reset_runtime",
            "timestamp": now,
        }
    )

    #
    # ------------------------------------------------------------------
    # Logger
    # ------------------------------------------------------------------
    #

    self._logger.info(
        "Runtime reset completed."
    )

    return self
# ==============================================================================
# Part 12.7 – cleanup()
# ==============================================================================

def cleanup(
    self,
):
    """
    Perform runtime cleanup.

    This method releases temporary runtime resources while preserving
    runtime identity, configuration, callbacks, hooks and metadata.

    Returns
    -------
    SpanScope
        Self.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    now = time.time()

    #
    # ------------------------------------------------------------------
    # Clear temporary runtime containers
    # ------------------------------------------------------------------
    #

    self._cache.clear()

    self._runtime_data.clear()

    #
    # ------------------------------------------------------------------
    # Trim history
    # ------------------------------------------------------------------
    #

    history_limit = getattr(
        self,
        "_history_limit",
        None,
    )

    if (
        history_limit is not None
        and history_limit > 0
        and len(self._history) > history_limit
    ):

        self._history = self._history[
            -history_limit:
        ]

    #
    # ------------------------------------------------------------------
    # Cleanup callback history
    # ------------------------------------------------------------------
    #

    if hasattr(
        self,
        "_callback_registry",
    ):

        for info in self._callback_registry.values():

            info["updated_at"] = now

    #
    # ------------------------------------------------------------------
    # Cleanup hook history
    # ------------------------------------------------------------------
    #

    if hasattr(
        self,
        "_hook_registry",
    ):

        for info in self._hook_registry.values():

            info["updated_at"] = now

    #
    # ------------------------------------------------------------------
    # Runtime state
    # ------------------------------------------------------------------
    #

    self._updated_at = now

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    self._runtime_data[
        "cleanup_at"
    ] = now

    self._runtime_data[
        "cleanup_completed"
    ] = True

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    self._history.append(
        {
            "event": "cleanup",
            "timestamp": now,
        }
    )

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    self._statistics.update_count += 1
    self._statistics.updated_at = now

    #
    # ------------------------------------------------------------------
    # Logger
    # ------------------------------------------------------------------
    #

    self._logger.info(
        "Runtime cleanup completed."
    )

    return self
# ==============================================================================
# Part 12.8 – diagnostics()
# ==============================================================================

def diagnostics(
    self,
):
    """
    Collect runtime diagnostic information.

    Returns
    -------
    dict
        Runtime diagnostics.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    now = time.time()

    callback_total = len(
        getattr(
            self,
            "_callback_registry",
            {},
        )
    )

    callback_enabled = sum(
        1
        for info in getattr(
            self,
            "_callback_registry",
            {},
        ).values()
        if info.get(
            "enabled",
            True,
        )
    )

    hook_total = len(
        getattr(
            self,
            "_hook_registry",
            {},
        )
    )

    hook_enabled = sum(
        1
        for info in getattr(
            self,
            "_hook_registry",
            {},
        ).values()
        if info.get(
            "enabled",
            True,
        )
    )

    diagnostics = {
        #
        # Identity
        #
        "id": self._id,
        "uuid": str(
            self._uuid,
        ),
        "name": self._name,
        "version": self._version,
        "scope_type": self._scope_type,

        #
        # Runtime state
        #
        "initialized": self._initialized,
        "running": self._running,
        "active": self._active,
        "entered": self._entered,
        "exited": self._exited,
        "frozen": self._frozen,
        "closed": self._closed,
        "disposed": self._disposed,
        "state": self._state,
        "status": self._status,

        #
        # Timing
        #
        "created_at": self._created_at,
        "updated_at": self._updated_at,
        "start_time": self._start_time,
        "end_time": self._end_time,

        #
        # Runtime objects
        #
        "callback_count": callback_total,
        "enabled_callbacks": callback_enabled,
        "disabled_callbacks": (
            callback_total
            - callback_enabled
        ),

        "hook_count": hook_total,
        "enabled_hooks": hook_enabled,
        "disabled_hooks": (
            hook_total
            - hook_enabled
        ),

        #
        # Containers
        #
        "runtime_data_size": len(
            self._runtime_data,
        ),
        "cache_size": len(
            self._cache,
        ),
        "history_size": len(
            self._history,
        ),
        "extensions_size": len(
            self._extensions,
        ),

        #
        # Statistics
        #
        "statistics": copy.deepcopy(
            self._statistics,
        ),

        #
        # Diagnostic metadata
        #
        "diagnostic_time": now,
        "healthy": (
            self._initialized
            and not self._disposed
        ),
    }

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    self._runtime_data[
        "last_diagnostics"
    ] = now

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    self._history.append(
        {
            "event": "diagnostics",
            "timestamp": now,
        }
    )

    #
    # ------------------------------------------------------------------
    # Logger
    # ------------------------------------------------------------------
    #

    self._logger.debug(
        "Runtime diagnostics generated."
    )

    return diagnostics
# ==============================================================================
# Part 12.9 – summary()
# ==============================================================================

def summary(
    self,
):
    """
    Return a concise runtime summary.

    Returns
    -------
    dict
        Runtime summary.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    now = time.time()

    callback_count = len(
        getattr(
            self,
            "_callback_registry",
            {},
        )
    )

    hook_count = len(
        getattr(
            self,
            "_hook_registry",
            {},
        )
    )

    summary = {
        #
        # Identity
        #
        "id": self._id,
        "uuid": str(
            self._uuid,
        ),
        "name": self._name,
        "version": self._version,

        #
        # Runtime
        #
        "state": self._state,
        "status": self._status,

        "running": self._running,
        "active": self._active,

        #
        # Timing
        #
        "uptime": self.uptime,
        "duration": self.duration,

        #
        # Runtime objects
        #
        "callbacks": callback_count,
        "hooks": hook_count,

        #
        # Statistics
        #
        "enter_count": self._statistics.enter_count,
        "exit_count": self._statistics.exit_count,
        "success_count": self._statistics.success_count,
        "failure_count": self._statistics.failure_count,
        "exception_count": self._statistics.exception_count,

        #
        # Health
        #
        "healthy": (
            self._initialized
            and not self._disposed
        ),

        #
        # Timestamp
        #
        "generated_at": now,
    }

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    self._runtime_data[
        "last_summary"
    ] = now

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    self._history.append(
        {
            "event": "summary",
            "timestamp": now,
        }
    )

    #
    # ------------------------------------------------------------------
    # Logger
    # ------------------------------------------------------------------
    #

    self._logger.debug(
        "Runtime summary generated."
    )

    return summary
# ==============================================================================
# Part 12.10 – export_runtime()
# ==============================================================================

def export_runtime(
    self,
    *,
    include_history=True,
    include_cache=False,
    include_callbacks=True,
    include_hooks=True,
):
    """
    Export the complete runtime state.

    Parameters
    ----------
    include_history
        Include runtime history.

    include_cache
        Include runtime cache.

    include_callbacks
        Include callback registry.

    include_hooks
        Include hook registry.

    Returns
    -------
    dict
        Exported runtime data.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    now = time.time()

    exported = {
        #
        # Export metadata
        #
        "export_type": "SpanScope",
        "export_version": 1,
        "export_time": now,

        #
        # Runtime snapshot
        #
        "runtime": self.snapshot(),
    }

    #
    # ------------------------------------------------------------------
    # Optional sections
    # ------------------------------------------------------------------
    #

    if include_history:

        exported["history"] = copy.deepcopy(
            self._history,
        )

    if include_cache:

        exported["cache"] = copy.deepcopy(
            self._cache,
        )

    if include_callbacks:

        exported["callback_registry"] = copy.deepcopy(
            getattr(
                self,
                "_callback_registry",
                {},
            ),
        )

    if include_hooks:

        exported["hook_registry"] = copy.deepcopy(
            getattr(
                self,
                "_hook_registry",
                {},
            ),
        )

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    self._runtime_data[
        "last_runtime_export"
    ] = now

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    self._history.append(
        {
            "event": "export_runtime",
            "timestamp": now,
        }
    )

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    self._statistics.update_count += 1
    self._statistics.updated_at = now

    #
    # ------------------------------------------------------------------
    # Logger
    # ------------------------------------------------------------------
    #

    self._logger.info(
        "Runtime exported."
    )

    return exported
# ==============================================================================
# Part 12.11 – import_runtime()
# ==============================================================================

def import_runtime(
    self,
    runtime,
):
    """
    Import a previously exported runtime.

    Parameters
    ----------
    runtime
        Runtime package produced by ``export_runtime()``.

    Returns
    -------
    SpanScope
        Self.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    if not isinstance(
        runtime,
        dict,
    ):

        raise TypeError(
            "runtime must be a dictionary."
        )

    if "runtime" not in runtime:

        raise ValueError(
            "Invalid runtime package."
        )

    now = time.time()

    #
    # ------------------------------------------------------------------
    # Restore runtime snapshot
    # ------------------------------------------------------------------
    #

    self.restore(
        runtime["runtime"],
    )

    #
    # ------------------------------------------------------------------
    # Optional history
    # ------------------------------------------------------------------
    #

    if "history" in runtime:

        self._history = copy.deepcopy(
            runtime["history"],
        )

    #
    # ------------------------------------------------------------------
    # Optional cache
    # ------------------------------------------------------------------
    #

    if "cache" in runtime:

        self._cache = copy.deepcopy(
            runtime["cache"],
        )

    #
    # ------------------------------------------------------------------
    # Optional callback registry
    # ------------------------------------------------------------------
    #

    if "callback_registry" in runtime:

        self._callback_registry = copy.deepcopy(
            runtime["callback_registry"],
        )

        self._callbacks = list(
            self._callback_registry.keys(),
        )

    #
    # ------------------------------------------------------------------
    # Optional hook registry
    # ------------------------------------------------------------------
    #

    if "hook_registry" in runtime:

        self._hook_registry = copy.deepcopy(
            runtime["hook_registry"],
        )

        self._hooks = {}

        for (
            event,
            hook,
        ), _ in self._hook_registry.items():

            self._hooks.setdefault(
                event,
                [],
            ).append(
                hook,
            )

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    self._runtime_data[
        "last_runtime_import"
    ] = now

    self._runtime_data[
        "runtime_import_version"
    ] = runtime.get(
        "export_version",
        1,
    )

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    self._history.append(
        {
            "event": "import_runtime",
            "timestamp": now,
        }
    )

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    self._statistics.update_count += 1
    self._statistics.updated_at = now

    #
    # ------------------------------------------------------------------
    # Logger
    # ------------------------------------------------------------------
    #

    self._logger.info(
        "Runtime imported."
    )

    return self
# ==============================================================================
# Part 12.12 – to_dict()
# ==============================================================================

def to_dict(
    self,
):
    """
    Convert the SpanScope into a serializable dictionary.

    Returns
    -------
    dict
        Dictionary representation.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    now = time.time()

    data = {
        #
        # Identity
        #
        "id": self._id,
        "uuid": str(
            self._uuid,
        ),
        "name": self._name,
        "description": self._description,
        "version": self._version,
        "scope_type": self._scope_type,

        #
        # Runtime state
        #
        "initialized": self._initialized,
        "running": self._running,
        "active": self._active,
        "entered": self._entered,
        "exited": self._exited,
        "frozen": self._frozen,
        "closed": self._closed,
        "disposed": self._disposed,
        "state": self._state,
        "status": self._status,

        #
        # Timing
        #
        "created_at": self._created_at,
        "updated_at": self._updated_at,
        "start_time": self._start_time,
        "end_time": self._end_time,

        #
        # Configuration
        #
        "enabled": self._enabled,
        "auto_start": self._auto_start,
        "auto_finish": self._auto_finish,
        "timeout": self._timeout,
        "history_limit": self._history_limit,
        "encoding": self._encoding,

        #
        # Metadata
        #
        "metadata": copy.deepcopy(
            self._metadata,
        ),
        "attributes": copy.deepcopy(
            self._attributes,
        ),
        "tags": copy.deepcopy(
            self._tags,
        ),
        "labels": copy.deepcopy(
            self._labels,
        ),
        "notes": copy.deepcopy(
            self._notes,
        ),

        #
        # Runtime
        #
        "runtime_data": copy.deepcopy(
            self._runtime_data,
        ),

        #
        # Statistics
        #
        "statistics": copy.deepcopy(
            self._statistics,
        ),
    }

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    self._runtime_data[
        "last_to_dict"
    ] = now

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    self._history.append(
        {
            "event": "to_dict",
            "timestamp": now,
        }
    )

    #
    # ------------------------------------------------------------------
    # Logger
    # ------------------------------------------------------------------
    #

    self._logger.debug(
        "Converted runtime to dictionary."
    )

    return data
# ==============================================================================
# Part 12.13 – from_dict()
# ==============================================================================

@classmethod
def from_dict(
    cls,
    data,
):
    """
    Create a SpanScope instance from a dictionary.

    Parameters
    ----------
    data
        Dictionary produced by ``to_dict()``.

    Returns
    -------
    SpanScope
        Restored instance.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    if not isinstance(
        data,
        dict,
    ):

        raise TypeError(
            "data must be a dictionary."
        )

    obj = cls()

    #
    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------
    #

    obj._id = data.get(
        "id",
        obj._id,
    )

    uuid_value = data.get(
        "uuid",
    )

    if uuid_value is not None:

        obj._uuid = uuid.UUID(
            str(uuid_value),
        )

    obj._name = data.get(
        "name",
        obj._name,
    )

    obj._description = data.get(
        "description",
        obj._description,
    )

    obj._version = data.get(
        "version",
        obj._version,
    )

    obj._scope_type = data.get(
        "scope_type",
        obj._scope_type,
    )

    #
    # ------------------------------------------------------------------
    # Runtime state
    # ------------------------------------------------------------------
    #

    obj._initialized = data.get(
        "initialized",
        obj._initialized,
    )

    obj._running = data.get(
        "running",
        obj._running,
    )

    obj._active = data.get(
        "active",
        obj._active,
    )

    obj._entered = data.get(
        "entered",
        obj._entered,
    )

    obj._exited = data.get(
        "exited",
        obj._exited,
    )

    obj._frozen = data.get(
        "frozen",
        obj._frozen,
    )

    obj._closed = data.get(
        "closed",
        obj._closed,
    )

    obj._disposed = data.get(
        "disposed",
        obj._disposed,
    )

    obj._state = data.get(
        "state",
        obj._state,
    )

    obj._status = data.get(
        "status",
        obj._status,
    )

    #
    # ------------------------------------------------------------------
    # Timing
    # ------------------------------------------------------------------
    #

    obj._created_at = data.get(
        "created_at",
        obj._created_at,
    )

    obj._updated_at = data.get(
        "updated_at",
        obj._updated_at,
    )

    obj._start_time = data.get(
        "start_time",
        obj._start_time,
    )

    obj._end_time = data.get(
        "end_time",
        obj._end_time,
    )

    #
    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------
    #

    obj._enabled = data.get(
        "enabled",
        obj._enabled,
    )

    obj._auto_start = data.get(
        "auto_start",
        obj._auto_start,
    )

    obj._auto_finish = data.get(
        "auto_finish",
        obj._auto_finish,
    )

    obj._timeout = data.get(
        "timeout",
        obj._timeout,
    )

    obj._history_limit = data.get(
        "history_limit",
        obj._history_limit,
    )

    obj._encoding = data.get(
        "encoding",
        obj._encoding,
    )

    #
    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------
    #

    obj._metadata = copy.deepcopy(
        data.get(
            "metadata",
            {},
        )
    )

    obj._attributes = copy.deepcopy(
        data.get(
            "attributes",
            {},
        )
    )

    obj._tags = copy.deepcopy(
        data.get(
            "tags",
            [],
        )
    )

    obj._labels = copy.deepcopy(
        data.get(
            "labels",
            {},
        )
    )

    obj._notes = copy.deepcopy(
        data.get(
            "notes",
            [],
        )
    )

    #
    # ------------------------------------------------------------------
    # Runtime
    # ------------------------------------------------------------------
    #

    obj._runtime_data = copy.deepcopy(
        data.get(
            "runtime_data",
            {},
        )
    )

    obj._statistics = copy.deepcopy(
        data.get(
            "statistics",
            obj._statistics,
        )
    )

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    obj._runtime_data[
        "created_from_dict"
    ] = time.time()

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    obj._history.append(
        {
            "event": "from_dict",
            "timestamp": time.time(),
        }
    )

    #
    # ------------------------------------------------------------------
    # Logger
    # ------------------------------------------------------------------
    #

    obj._logger.debug(
        "SpanScope restored from dictionary."
    )

    return obj
# ==============================================================================
# Part 12.14 – serialize()
# ==============================================================================

def serialize(
    self,
    *,
    indent=4,
    sort_keys=False,
    ensure_ascii=False,
):
    """
    Serialize the runtime into a JSON string.

    Parameters
    ----------
    indent
        JSON indentation.

    sort_keys
        Sort JSON keys.

    ensure_ascii
        Preserve unicode characters.

    Returns
    -------
    str
        Serialized runtime.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    now = time.time()

    #
    # ------------------------------------------------------------------
    # Dictionary representation
    # ------------------------------------------------------------------
    #

    payload = self.to_dict()

    #
    # ------------------------------------------------------------------
    # Serialize
    # ------------------------------------------------------------------
    #

    serialized = json.dumps(
        payload,
        indent=indent,
        sort_keys=sort_keys,
        ensure_ascii=ensure_ascii,
        default=str,
    )

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    self._runtime_data[
        "last_serialized_at"
    ] = now

    self._runtime_data[
        "last_serialized_size"
    ] = len(
        serialized,
    )

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    self._history.append(
        {
            "event": "serialize",
            "timestamp": now,
            "size": len(serialized),
        }
    )

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    self._statistics.update_count += 1
    self._statistics.updated_at = now

    #
    # ------------------------------------------------------------------
    # Logger
    # ------------------------------------------------------------------
    #

    self._logger.debug(
        "Runtime serialized (%d bytes).",
        len(serialized),
    )

    return serialized
# ==============================================================================
# Part 12.15 – deserialize()
# ==============================================================================

@classmethod
def deserialize(
    cls,
    serialized,
):
    """
    Deserialize a JSON string into a SpanScope.

    Parameters
    ----------
    serialized
        JSON string produced by ``serialize()``.

    Returns
    -------
    SpanScope
        Restored SpanScope instance.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    if not isinstance(
        serialized,
        str,
    ):

        raise TypeError(
            "serialized must be a JSON string."
        )

    #
    # ------------------------------------------------------------------
    # Decode JSON
    # ------------------------------------------------------------------
    #

    try:

        data = json.loads(
            serialized,
        )

    except json.JSONDecodeError as exc:

        raise ValueError(
            "Invalid serialized runtime."
        ) from exc

    #
    # ------------------------------------------------------------------
    # Restore object
    # ------------------------------------------------------------------
    #

    obj = cls.from_dict(
        data,
    )

    now = time.time()

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    obj._runtime_data[
        "last_deserialized_at"
    ] = now

    obj._runtime_data[
        "last_deserialized_size"
    ] = len(
        serialized,
    )

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    obj._history.append(
        {
            "event": "deserialize",
            "timestamp": now,
            "size": len(serialized),
        }
    )

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    obj._statistics.update_count += 1
    obj._statistics.updated_at = now

    #
    # ------------------------------------------------------------------
    # Logger
    # ------------------------------------------------------------------
    #

    obj._logger.debug(
        "Runtime deserialized (%d bytes).",
        len(serialized),
    )

    return obj
# ==============================================================================
# Part 13.1 – to_json()
# ==============================================================================

def to_json(
    self,
    *,
    indent=4,
    sort_keys=False,
    ensure_ascii=False,
):
    """
    Convert the SpanScope to a JSON string.

    Parameters
    ----------
    indent
        JSON indentation.

    sort_keys
        Sort JSON keys.

    ensure_ascii
        Preserve unicode characters.

    Returns
    -------
    str
        JSON representation.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    now = time.time()

    #
    # ------------------------------------------------------------------
    # Dictionary representation
    # ------------------------------------------------------------------
    #

    payload = self.to_dict()

    #
    # ------------------------------------------------------------------
    # JSON serialization
    # ------------------------------------------------------------------
    #

    json_text = json.dumps(
        payload,
        indent=indent,
        sort_keys=sort_keys,
        ensure_ascii=ensure_ascii,
        default=str,
    )

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    self._runtime_data[
        "last_json_export"
    ] = now

    self._runtime_data[
        "last_json_size"
    ] = len(
        json_text,
    )

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    self._history.append(
        {
            "event": "to_json",
            "timestamp": now,
            "size": len(json_text),
        }
    )

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    self._statistics.update_count += 1
    self._statistics.updated_at = now

    #
    # ------------------------------------------------------------------
    # Logger
    # ------------------------------------------------------------------
    #

    self._logger.debug(
        "SpanScope exported to JSON (%d bytes).",
        len(json_text),
    )

    return json_text
# ==============================================================================
# Part 13.2 – from_json()
# ==============================================================================

@classmethod
def from_json(
    cls,
    json_text,
):
    """
    Create a SpanScope from a JSON string.

    Parameters
    ----------
    json_text
        JSON string produced by ``to_json()``.

    Returns
    -------
    SpanScope
        Restored SpanScope instance.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    if not isinstance(
        json_text,
        str,
    ):

        raise TypeError(
            "json_text must be a string."
        )

    #
    # ------------------------------------------------------------------
    # Decode JSON
    # ------------------------------------------------------------------
    #

    try:

        data = json.loads(
            json_text,
        )

    except json.JSONDecodeError as exc:

        raise ValueError(
            "Invalid JSON document."
        ) from exc

    #
    # ------------------------------------------------------------------
    # Restore object
    # ------------------------------------------------------------------
    #

    obj = cls.from_dict(
        data,
    )

    now = time.time()

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    obj._runtime_data[
        "last_json_import"
    ] = now

    obj._runtime_data[
        "last_json_size"
    ] = len(
        json_text,
    )

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    obj._history.append(
        {
            "event": "from_json",
            "timestamp": now,
            "size": len(json_text),
        }
    )

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    obj._statistics.update_count += 1
    obj._statistics.updated_at = now

    #
    # ------------------------------------------------------------------
    # Logger
    # ------------------------------------------------------------------
    #

    obj._logger.debug(
        "SpanScope restored from JSON (%d bytes).",
        len(json_text),
    )

    return obj
# ==============================================================================
# Part 13.3 – to_yaml()
# ==============================================================================

def to_yaml(
    self,
    *,
    sort_keys=False,
    allow_unicode=True,
):
    """
    Convert the SpanScope to a YAML string.

    Parameters
    ----------
    sort_keys
        Sort YAML keys.

    allow_unicode
        Preserve unicode characters.

    Returns
    -------
    str
        YAML representation.

    Raises
    ------
    RuntimeError
        If PyYAML is not installed.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    try:

        import yaml

    except ImportError as exc:

        raise RuntimeError(
            "PyYAML is required for YAML serialization."
        ) from exc

    now = time.time()

    #
    # ------------------------------------------------------------------
    # Dictionary representation
    # ------------------------------------------------------------------
    #

    payload = self.to_dict()

    #
    # ------------------------------------------------------------------
    # YAML serialization
    # ------------------------------------------------------------------
    #

    yaml_text = yaml.safe_dump(
        payload,
        sort_keys=sort_keys,
        allow_unicode=allow_unicode,
        default_flow_style=False,
    )

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    self._runtime_data[
        "last_yaml_export"
    ] = now

    self._runtime_data[
        "last_yaml_size"
    ] = len(
        yaml_text,
    )

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    self._history.append(
        {
            "event": "to_yaml",
            "timestamp": now,
            "size": len(yaml_text),
        }
    )

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    self._statistics.update_count += 1
    self._statistics.updated_at = now

    #
    # ------------------------------------------------------------------
    # Logger
    # ------------------------------------------------------------------
    #

    self._logger.debug(
        "SpanScope exported to YAML (%d bytes).",
        len(yaml_text),
    )

    return yaml_text
# ==============================================================================
# Part 13.4 – from_yaml()
# ==============================================================================

@classmethod
def from_yaml(
    cls,
    yaml_text,
):
    """
    Create a SpanScope from a YAML document.

    Parameters
    ----------
    yaml_text
        YAML string produced by ``to_yaml()``.

    Returns
    -------
    SpanScope
        Restored SpanScope instance.

    Raises
    ------
    RuntimeError
        If PyYAML is not installed.

    ValueError
        If the YAML document is invalid.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    if not isinstance(
        yaml_text,
        str,
    ):

        raise TypeError(
            "yaml_text must be a string."
        )

    try:

        import yaml

    except ImportError as exc:

        raise RuntimeError(
            "PyYAML is required for YAML deserialization."
        ) from exc

    #
    # ------------------------------------------------------------------
    # Parse YAML
    # ------------------------------------------------------------------
    #

    try:

        data = yaml.safe_load(
            yaml_text,
        )

    except yaml.YAMLError as exc:

        raise ValueError(
            "Invalid YAML document."
        ) from exc

    if not isinstance(
        data,
        dict,
    ):

        raise ValueError(
            "YAML document must contain a dictionary."
        )

    #
    # ------------------------------------------------------------------
    # Restore object
    # ------------------------------------------------------------------
    #

    obj = cls.from_dict(
        data,
    )

    now = time.time()

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    obj._runtime_data[
        "last_yaml_import"
    ] = now

    obj._runtime_data[
        "last_yaml_size"
    ] = len(
        yaml_text,
    )

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    obj._history.append(
        {
            "event": "from_yaml",
            "timestamp": now,
            "size": len(yaml_text),
        }
    )

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    obj._statistics.update_count += 1
    obj._statistics.updated_at = now

    #
    # ------------------------------------------------------------------
    # Logger
    # ------------------------------------------------------------------
    #

    obj._logger.debug(
        "SpanScope restored from YAML (%d bytes).",
        len(yaml_text),
    )

    return obj
# ==============================================================================
# Part 13.5 – to_pickle()
# ==============================================================================

def to_pickle(
    self,
    *,
    protocol=pickle.HIGHEST_PROTOCOL,
):
    """
    Serialize the SpanScope into Pickle bytes.

    Parameters
    ----------
    protocol
        Pickle protocol version.

    Returns
    -------
    bytes
        Pickled runtime.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    now = time.time()

    #
    # ------------------------------------------------------------------
    # Dictionary representation
    # ------------------------------------------------------------------
    #

    payload = self.to_dict()

    #
    # ------------------------------------------------------------------
    # Pickle serialization
    # ------------------------------------------------------------------
    #

    serialized = pickle.dumps(
        payload,
        protocol=protocol,
    )

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    self._runtime_data[
        "last_pickle_export"
    ] = now

    self._runtime_data[
        "last_pickle_size"
    ] = len(
        serialized,
    )

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    self._history.append(
        {
            "event": "to_pickle",
            "timestamp": now,
            "size": len(serialized),
        }
    )

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    self._statistics.update_count += 1
    self._statistics.updated_at = now

    #
    # ------------------------------------------------------------------
    # Logger
    # ------------------------------------------------------------------
    #

    self._logger.debug(
        "SpanScope exported to Pickle (%d bytes).",
        len(serialized),
    )

    return serialized
# ==============================================================================
# Part 13.6 – from_pickle()
# ==============================================================================

@classmethod
def from_pickle(
    cls,
    serialized,
):
    """
    Restore a SpanScope from Pickle bytes.

    Parameters
    ----------
    serialized
        Pickle bytes produced by ``to_pickle()``.

    Returns
    -------
    SpanScope
        Restored SpanScope instance.

    Raises
    ------
    TypeError
        If serialized is not bytes.

    ValueError
        If the Pickle payload is invalid.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    if not isinstance(
        serialized,
        (
            bytes,
            bytearray,
        ),
    ):

        raise TypeError(
            "serialized must be bytes."
        )

    #
    # ------------------------------------------------------------------
    # Decode Pickle
    # ------------------------------------------------------------------
    #

    try:

        data = pickle.loads(
            serialized,
        )

    except (
        pickle.UnpicklingError,
        EOFError,
        AttributeError,
        ValueError,
        TypeError,
    ) as exc:

        raise ValueError(
            "Invalid Pickle payload."
        ) from exc

    if not isinstance(
        data,
        dict,
    ):

        raise ValueError(
            "Pickle payload must contain a dictionary."
        )

    #
    # ------------------------------------------------------------------
    # Restore object
    # ------------------------------------------------------------------
    #

    obj = cls.from_dict(
        data,
    )

    now = time.time()

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    obj._runtime_data[
        "last_pickle_import"
    ] = now

    obj._runtime_data[
        "last_pickle_size"
    ] = len(
        serialized,
    )

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    obj._history.append(
        {
            "event": "from_pickle",
            "timestamp": now,
            "size": len(serialized),
        }
    )

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    obj._statistics.update_count += 1
    obj._statistics.updated_at = now

    #
    # ------------------------------------------------------------------
    # Logger
    # ------------------------------------------------------------------
    #

    obj._logger.debug(
        "SpanScope restored from Pickle (%d bytes).",
        len(serialized),
    )

    return obj
# ==============================================================================
# Part 13.7 – save()
# ==============================================================================

def save(
    self,
    path,
    *,
    format="json",
    indent=4,
):
    """
    Save the SpanScope to a file.

    Parameters
    ----------
    path
        Destination file path.

    format
        Serialization format.

        Supported:
            - json
            - yaml
            - pickle

    indent
        JSON indentation.

    Returns
    -------
    str
        Saved file path.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    if not isinstance(
        path,
        str,
    ):

        raise TypeError(
            "path must be a string."
        )

    format = format.lower()

    now = time.time()

    #
    # ------------------------------------------------------------------
    # JSON
    # ------------------------------------------------------------------
    #

    if format == "json":

        content = self.to_json(
            indent=indent,
        )

        with open(
            path,
            "w",
            encoding="utf-8",
        ) as stream:

            stream.write(
                content,
            )

    #
    # ------------------------------------------------------------------
    # YAML
    # ------------------------------------------------------------------
    #

    elif format == "yaml":

        content = self.to_yaml()

        with open(
            path,
            "w",
            encoding="utf-8",
        ) as stream:

            stream.write(
                content,
            )

    #
    # ------------------------------------------------------------------
    # Pickle
    # ------------------------------------------------------------------
    #

    elif format == "pickle":

        content = self.to_pickle()

        with open(
            path,
            "wb",
        ) as stream:

            stream.write(
                content,
            )

    #
    # ------------------------------------------------------------------
    # Unsupported format
    # ------------------------------------------------------------------
    #

    else:

        raise ValueError(
            f"Unsupported format: {format}"
        )

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    self._runtime_data[
        "last_saved_file"
    ] = path

    self._runtime_data[
        "last_saved_format"
    ] = format

    self._runtime_data[
        "last_saved_at"
    ] = now

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    self._history.append(
        {
            "event": "save",
            "path": path,
            "format": format,
            "timestamp": now,
        }
    )

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    self._statistics.update_count += 1
    self._statistics.updated_at = now

    #
    # ------------------------------------------------------------------
    # Logger
    # ------------------------------------------------------------------
    #

    self._logger.info(
        "SpanScope saved to %s (%s).",
        path,
        format,
    )

    return path
# ==============================================================================
# Part 13.8 – load()
# ==============================================================================

@classmethod
def load(
    cls,
    path,
    *,
    format="json",
):
    """
    Load a SpanScope from a file.

    Parameters
    ----------
    path
        Source file path.

    format
        Serialization format.

        Supported:
            - json
            - yaml
            - pickle

    Returns
    -------
    SpanScope
        Restored SpanScope instance.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    if not isinstance(
        path,
        str,
    ):

        raise TypeError(
            "path must be a string."
        )

    format = format.lower()

    #
    # ------------------------------------------------------------------
    # JSON
    # ------------------------------------------------------------------
    #

    if format == "json":

        with open(
            path,
            "r",
            encoding="utf-8",
        ) as stream:

            content = stream.read()

        obj = cls.from_json(
            content,
        )

    #
    # ------------------------------------------------------------------
    # YAML
    # ------------------------------------------------------------------
    #

    elif format == "yaml":

        with open(
            path,
            "r",
            encoding="utf-8",
        ) as stream:

            content = stream.read()

        obj = cls.from_yaml(
            content,
        )

    #
    # ------------------------------------------------------------------
    # Pickle
    # ------------------------------------------------------------------
    #

    elif format == "pickle":

        with open(
            path,
            "rb",
        ) as stream:

            content = stream.read()

        obj = cls.from_pickle(
            content,
        )

    #
    # ------------------------------------------------------------------
    # Unsupported format
    # ------------------------------------------------------------------
    #

    else:

        raise ValueError(
            f"Unsupported format: {format}"
        )

    now = time.time()

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    obj._runtime_data[
        "last_loaded_file"
    ] = path

    obj._runtime_data[
        "last_loaded_format"
    ] = format

    obj._runtime_data[
        "last_loaded_at"
    ] = now

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    obj._history.append(
        {
            "event": "load",
            "path": path,
            "format": format,
            "timestamp": now,
        }
    )

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    obj._statistics.update_count += 1
    obj._statistics.updated_at = now

    #
    # ------------------------------------------------------------------
    # Logger
    # ------------------------------------------------------------------
    #

    obj._logger.info(
        "SpanScope loaded from %s (%s).",
        path,
        format,
    )

    return obj
# ==============================================================================
# Part 13.9 – export()
# ==============================================================================

def export(
    self,
    *,
    format="json",
):
    """
    Export the SpanScope into a portable representation.

    Parameters
    ----------
    format
        Export format.

        Supported:
            - json
            - yaml
            - pickle
            - dict

    Returns
    -------
    object
        Exported object.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    format = format.lower()

    now = time.time()

    #
    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------
    #

    if format == "dict":

        exported = self.to_dict()

    elif format == "json":

        exported = self.to_json()

    elif format == "yaml":

        exported = self.to_yaml()

    elif format == "pickle":

        exported = self.to_pickle()

    else:

        raise ValueError(
            f"Unsupported export format: {format}"
        )

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    self._runtime_data[
        "last_export_format"
    ] = format

    self._runtime_data[
        "last_export_time"
    ] = now

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    self._history.append(
        {
            "event": "export",
            "format": format,
            "timestamp": now,
        }
    )

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    self._statistics.update_count += 1
    self._statistics.updated_at = now

    #
    # ------------------------------------------------------------------
    # Logger
    # ------------------------------------------------------------------
    #

    self._logger.info(
        "SpanScope exported (%s).",
        format,
    )

    return exported
# ==============================================================================
# Part 13.10 – import_data()
# ==============================================================================

@classmethod
def import_data(
    cls,
    data,
    *,
    format="json",
):
    """
    Import a SpanScope from serialized data.

    Parameters
    ----------
    data
        Serialized runtime object.

    format
        Serialization format.

        Supported:
            - dict
            - json
            - yaml
            - pickle

    Returns
    -------
    SpanScope
        Restored SpanScope instance.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    format = str(
        format,
    ).lower()

    #
    # ------------------------------------------------------------------
    # Import
    # ------------------------------------------------------------------
    #

    if format == "dict":

        obj = cls.from_dict(
            data,
        )

    elif format == "json":

        obj = cls.from_json(
            data,
        )

    elif format == "yaml":

        obj = cls.from_yaml(
            data,
        )

    elif format == "pickle":

        obj = cls.from_pickle(
            data,
        )

    else:

        raise ValueError(
            f"Unsupported import format: {format}"
        )

    now = time.time()

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    obj._runtime_data[
        "last_import_format"
    ] = format

    obj._runtime_data[
        "last_import_time"
    ] = now

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    obj._history.append(
        {
            "event": "import_data",
            "format": format,
            "timestamp": now,
        }
    )

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    obj._statistics.update_count += 1
    obj._statistics.updated_at = now

    #
    # ------------------------------------------------------------------
    # Logger
    # ------------------------------------------------------------------
    #

    obj._logger.info(
        "SpanScope imported (%s).",
        format,
    )

    return obj
# ==============================================================================
# Part 13.11 – checksum()
# ==============================================================================

def checksum(
    self,
    *,
    algorithm="sha256",
):
    """
    Compute a checksum for the current runtime.

    Parameters
    ----------
    algorithm
        Hash algorithm.

        Supported:
            - md5
            - sha1
            - sha224
            - sha256
            - sha384
            - sha512

    Returns
    -------
    str
        Hexadecimal checksum.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    algorithm = str(
        algorithm,
    ).lower()

    try:

        hasher = hashlib.new(
            algorithm,
        )

    except ValueError as exc:

        raise ValueError(
            f"Unsupported checksum algorithm: {algorithm}"
        ) from exc

    now = time.time()

    #
    # ------------------------------------------------------------------
    # Serialize runtime
    # ------------------------------------------------------------------
    #

    payload = self.to_json(
        sort_keys=True,
        ensure_ascii=True,
    )

    #
    # ------------------------------------------------------------------
    # Hash
    # ------------------------------------------------------------------
    #

    hasher.update(
        payload.encode(
            "utf-8",
        )
    )

    digest = hasher.hexdigest()

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    self._runtime_data[
        "last_checksum"
    ] = digest

    self._runtime_data[
        "last_checksum_algorithm"
    ] = algorithm

    self._runtime_data[
        "last_checksum_time"
    ] = now

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    self._history.append(
        {
            "event": "checksum",
            "algorithm": algorithm,
            "timestamp": now,
        }
    )

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    self._statistics.update_count += 1
    self._statistics.updated_at = now

    #
    # ------------------------------------------------------------------
    # Logger
    # ------------------------------------------------------------------
    #

    self._logger.debug(
        "Checksum generated using %s.",
        algorithm,
    )

    return digest
# ==============================================================================
# Part 13.12 – verify_checksum()
# ==============================================================================

def verify_checksum(
    self,
    checksum,
    *,
    algorithm="sha256",
):
    """
    Verify a runtime checksum.

    Parameters
    ----------
    checksum
        Expected hexadecimal checksum.

    algorithm
        Hash algorithm.

    Returns
    -------
    bool
        True if checksum matches.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    if not isinstance(
        checksum,
        str,
    ):

        raise TypeError(
            "checksum must be a string."
        )

    algorithm = str(
        algorithm,
    ).lower()

    now = time.time()

    #
    # ------------------------------------------------------------------
    # Compute current checksum
    # ------------------------------------------------------------------
    #

    current = self.checksum(
        algorithm=algorithm,
    )

    verified = (
        current == checksum
    )

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    self._runtime_data[
        "last_checksum_verification"
    ] = verified

    self._runtime_data[
        "last_verified_checksum"
    ] = checksum

    self._runtime_data[
        "last_verification_algorithm"
    ] = algorithm

    self._runtime_data[
        "last_verification_time"
    ] = now

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    self._history.append(
        {
            "event": "verify_checksum",
            "algorithm": algorithm,
            "verified": verified,
            "timestamp": now,
        }
    )

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    self._statistics.update_count += 1
    self._statistics.updated_at = now

    #
    # ------------------------------------------------------------------
    # Logger
    # ------------------------------------------------------------------
    #

    if verified:

        self._logger.debug(
            "Checksum verification succeeded."
        )

    else:

        self._logger.warning(
            "Checksum verification failed."
        )

    return verified 
# ==============================================================================
# Part 13.13 – compress()
# ==============================================================================

def compress(
    self,
    *,
    level=9,
):
    """
    Compress the serialized runtime.

    Parameters
    ----------
    level
        Compression level (0-9).

    Returns
    -------
    bytes
        Compressed runtime.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    if not isinstance(
        level,
        int,
    ):

        raise TypeError(
            "level must be an integer."
        )

    if level < 0 or level > 9:

        raise ValueError(
            "level must be between 0 and 9."
        )

    now = time.time()

    #
    # ------------------------------------------------------------------
    # Serialize runtime
    # ------------------------------------------------------------------
    #

    serialized = self.to_json(
        sort_keys=True,
        ensure_ascii=True,
    )

    raw = serialized.encode(
        "utf-8",
    )

    #
    # ------------------------------------------------------------------
    # Compress
    # ------------------------------------------------------------------
    #

    compressed = zlib.compress(
        raw,
        level,
    )

    ratio = 0.0

    if len(raw) > 0:

        ratio = (
            len(compressed)
            / len(raw)
        )

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    self._runtime_data[
        "last_compression_time"
    ] = now

    self._runtime_data[
        "last_compression_level"
    ] = level

    self._runtime_data[
        "last_raw_size"
    ] = len(
        raw,
    )

    self._runtime_data[
        "last_compressed_size"
    ] = len(
        compressed,
    )

    self._runtime_data[
        "last_compression_ratio"
    ] = ratio

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    self._history.append(
        {
            "event": "compress",
            "timestamp": now,
            "level": level,
            "raw_size": len(raw),
            "compressed_size": len(compressed),
        }
    )

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    self._statistics.update_count += 1
    self._statistics.updated_at = now

    #
    # ------------------------------------------------------------------
    # Logger
    # ------------------------------------------------------------------
    #

    self._logger.debug(
        "Runtime compressed (%d -> %d bytes).",
        len(raw),
        len(compressed),
    )

    return compressed
# ==============================================================================
# Part 13.14 – decompress()
# ==============================================================================

@classmethod
def decompress(
    cls,
    compressed,
):
    """
    Decompress a compressed SpanScope runtime.

    Parameters
    ----------
    compressed
        Compressed bytes produced by ``compress()``.

    Returns
    -------
    SpanScope
        Restored SpanScope instance.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    if not isinstance(
        compressed,
        (
            bytes,
            bytearray,
        ),
    ):

        raise TypeError(
            "compressed must be bytes."
        )

    #
    # ------------------------------------------------------------------
    # Decompress
    # ------------------------------------------------------------------
    #

    try:

        raw = zlib.decompress(
            compressed,
        )

    except zlib.error as exc:

        raise ValueError(
            "Invalid compressed runtime."
        ) from exc

    #
    # ------------------------------------------------------------------
    # Decode UTF-8
    # ------------------------------------------------------------------
    #

    try:

        json_text = raw.decode(
            "utf-8",
        )

    except UnicodeDecodeError as exc:

        raise ValueError(
            "Invalid UTF-8 runtime payload."
        ) from exc

    #
    # ------------------------------------------------------------------
    # Restore object
    # ------------------------------------------------------------------
    #

    obj = cls.from_json(
        json_text,
    )

    now = time.time()

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    obj._runtime_data[
        "last_decompression_time"
    ] = now

    obj._runtime_data[
        "last_raw_size"
    ] = len(
        raw,
    )

    obj._runtime_data[
        "last_compressed_size"
    ] = len(
        compressed,
    )

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    obj._history.append(
        {
            "event": "decompress",
            "timestamp": now,
            "compressed_size": len(compressed),
            "raw_size": len(raw),
        }
    )

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    obj._statistics.update_count += 1
    obj._statistics.updated_at = now

    #
    # ------------------------------------------------------------------
    # Logger
    # ------------------------------------------------------------------
    #

    obj._logger.debug(
        "Runtime decompressed (%d -> %d bytes).",
        len(compressed),
        len(raw),
    )

    return obj
# ==============================================================================
# Part 13.15 – serialization_summary()
# ==============================================================================

def serialization_summary(
    self,
):
    """
    Return serialization statistics.

    Returns
    -------
    dict
        Serialization summary.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    now = time.time()

    summary = {
        #
        # JSON
        #
        "last_json_export": self._runtime_data.get(
            "last_json_export",
        ),
        "last_json_import": self._runtime_data.get(
            "last_json_import",
        ),
        "last_json_size": self._runtime_data.get(
            "last_json_size",
        ),

        #
        # YAML
        #
        "last_yaml_export": self._runtime_data.get(
            "last_yaml_export",
        ),
        "last_yaml_import": self._runtime_data.get(
            "last_yaml_import",
        ),
        "last_yaml_size": self._runtime_data.get(
            "last_yaml_size",
        ),

        #
        # Pickle
        #
        "last_pickle_export": self._runtime_data.get(
            "last_pickle_export",
        ),
        "last_pickle_import": self._runtime_data.get(
            "last_pickle_import",
        ),
        "last_pickle_size": self._runtime_data.get(
            "last_pickle_size",
        ),

        #
        # Compression
        #
        "last_compression_time": self._runtime_data.get(
            "last_compression_time",
        ),
        "last_decompression_time": self._runtime_data.get(
            "last_decompression_time",
        ),
        "last_compression_level": self._runtime_data.get(
            "last_compression_level",
        ),
        "last_compression_ratio": self._runtime_data.get(
            "last_compression_ratio",
        ),

        #
        # Checksum
        #
        "last_checksum": self._runtime_data.get(
            "last_checksum",
        ),
        "last_checksum_algorithm": self._runtime_data.get(
            "last_checksum_algorithm",
        ),
        "last_checksum_verification": self._runtime_data.get(
            "last_checksum_verification",
        ),

        #
        # File I/O
        #
        "last_saved_file": self._runtime_data.get(
            "last_saved_file",
        ),
        "last_saved_format": self._runtime_data.get(
            "last_saved_format",
        ),
        "last_loaded_file": self._runtime_data.get(
            "last_loaded_file",
        ),
        "last_loaded_format": self._runtime_data.get(
            "last_loaded_format",
        ),

        #
        # Generic Import / Export
        #
        "last_export_format": self._runtime_data.get(
            "last_export_format",
        ),
        "last_import_format": self._runtime_data.get(
            "last_import_format",
        ),

        #
        # Timestamp
        #
        "generated_at": now,
    }

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    self._runtime_data[
        "last_serialization_summary"
    ] = now

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    self._history.append(
        {
            "event": "serialization_summary",
            "timestamp": now,
        }
    )

    #
    # ------------------------------------------------------------------
    # Logger
    # ------------------------------------------------------------------
    #

    self._logger.debug(
        "Serialization summary generated."
    )

    return summary
# ==============================================================================
# Part 14.1 – generate_id()
# ==============================================================================

@staticmethod
def generate_id(
    *,
    prefix="scope",
):
    """
    Generate a unique runtime identifier.

    Parameters
    ----------
    prefix
        Identifier prefix.

    Returns
    -------
    str
        Generated identifier.
    """

    if not isinstance(
        prefix,
        str,
    ):

        raise TypeError(
            "prefix must be a string."
        )

    prefix = prefix.strip().lower()

    if not prefix:

        prefix = "scope"

    return (
        f"{prefix}-"
        f"{uuid.uuid4().hex}"
    )
# ==============================================================================
# Part 14.2 – generate_uuid()
# ==============================================================================

@staticmethod
def generate_uuid():
    """
    Generate a new UUID.

    Returns
    -------
    uuid.UUID
        Newly generated UUID object.
    """

    return uuid.uuid4()
# ==============================================================================
# Part 14.3 – generate_timestamp()
# ==============================================================================

@staticmethod
def generate_timestamp(
    *,
    as_datetime=False,
):
    """
    Generate the current timestamp.

    Parameters
    ----------
    as_datetime
        Return a datetime object instead of a Unix timestamp.

    Returns
    -------
    float | datetime.datetime
        Current timestamp.
    """

    if as_datetime:

        return datetime.datetime.now(
            datetime.timezone.utc,
        )

    return time.time()
# ==============================================================================
# Part 14.4 – normalize_name()
# ==============================================================================

@staticmethod
def normalize_name(
    name,
    *,
    lowercase=True,
    separator="_",
):
    """
    Normalize an object name.

    Parameters
    ----------
    name
        Original name.

    lowercase
        Convert the name to lowercase.

    separator
        Separator used to replace whitespace.

    Returns
    -------
    str
        Normalized name.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    if not isinstance(
        name,
        str,
    ):

        raise TypeError(
            "name must be a string."
        )

    if not isinstance(
        separator,
        str,
    ):

        raise TypeError(
            "separator must be a string."
        )

    #
    # ------------------------------------------------------------------
    # Normalize
    # ------------------------------------------------------------------
    #

    normalized = name.strip()

    normalized = re.sub(
        r"\s+",
        separator,
        normalized,
    )

    normalized = re.sub(
        rf"{re.escape(separator)}+",
        separator,
        normalized,
    )

    normalized = re.sub(
        rf"[^A-Za-z0-9{re.escape(separator)}]",
        "",
        normalized,
    )

    normalized = normalized.strip(
        separator,
    )

    #
    # ------------------------------------------------------------------
    # Letter case
    # ------------------------------------------------------------------
    #

    if lowercase:

        normalized = normalized.lower()

    #
    # ------------------------------------------------------------------
    # Empty fallback
    # ------------------------------------------------------------------
    #

    if not normalized:

        normalized = "unnamed"

    return normalized
# ==============================================================================
# Part 14.5 – safe_copy()
# ==============================================================================

@staticmethod
def safe_copy(
    obj,
    *,
    default=None,
):
    """
    Safely create a shallow copy of an object.

    Parameters
    ----------
    obj
        Object to copy.

    default
        Value returned if copying fails.

    Returns
    -------
    object
        Shallow copy or default value.
    """

    #
    # ------------------------------------------------------------------
    # None
    # ------------------------------------------------------------------
    #

    if obj is None:

        return default

    #
    # ------------------------------------------------------------------
    # Built-in containers
    # ------------------------------------------------------------------
    #

    if isinstance(
        obj,
        dict,
    ):

        return obj.copy()

    if isinstance(
        obj,
        list,
    ):

        return obj.copy()

    if isinstance(
        obj,
        set,
    ):

        return obj.copy()

    if isinstance(
        obj,
        tuple,
    ):

        return tuple(obj)

    #
    # ------------------------------------------------------------------
    # Generic copy
    # ------------------------------------------------------------------
    #

    try:

        return copy.copy(
            obj,
        )

    except Exception:

        return default
# ==============================================================================
# Part 14.6 – safe_deepcopy()
# ==============================================================================

@staticmethod
def safe_deepcopy(
    obj,
    *,
    default=None,
):
    """
    Safely create a deep copy of an object.

    Parameters
    ----------
    obj
        Object to deep copy.

    default
        Value returned if deep copying fails.

    Returns
    -------
    object
        Deep copy or default value.
    """

    #
    # ------------------------------------------------------------------
    # None
    # ------------------------------------------------------------------
    #

    if obj is None:

        return default

    #
    # ------------------------------------------------------------------
    # Immutable objects
    # ------------------------------------------------------------------
    #

    if isinstance(
        obj,
        (
            str,
            int,
            float,
            bool,
            bytes,
            complex,
            type(None),
        ),
    ):

        return obj

    #
    # ------------------------------------------------------------------
    # Deep copy
    # ------------------------------------------------------------------
    #

    try:

        return copy.deepcopy(
            obj,
        )

    except Exception:

        return default
# ==============================================================================
# Part 14.7 – safe_dict()
# ==============================================================================

@staticmethod
def safe_dict(
    obj=None,
):
    """
    Safely convert an object into a dictionary.

    Parameters
    ----------
    obj
        Object to convert.

    Returns
    -------
    dict
        Dictionary representation.
    """

    #
    # ------------------------------------------------------------------
    # None
    # ------------------------------------------------------------------
    #

    if obj is None:

        return {}

    #
    # ------------------------------------------------------------------
    # Already a dictionary
    # ------------------------------------------------------------------
    #

    if isinstance(
        obj,
        dict,
    ):

        return obj.copy()

    #
    # ------------------------------------------------------------------
    # Dataclass
    # ------------------------------------------------------------------
    #

    try:

        if dataclasses.is_dataclass(
            obj,
        ):

            return dataclasses.asdict(
                obj,
            )

    except Exception:

        pass

    #
    # ------------------------------------------------------------------
    # to_dict()
    # ------------------------------------------------------------------
    #

    to_dict = getattr(
        obj,
        "to_dict",
        None,
    )

    if callable(
        to_dict,
    ):

        try:

            value = to_dict()

            if isinstance(
                value,
                dict,
            ):

                return value

        except Exception:

            pass

    #
    # ------------------------------------------------------------------
    # __dict__
    # ------------------------------------------------------------------
    #

    if hasattr(
        obj,
        "__dict__",
    ):

        try:

            return dict(
                vars(obj),
            )

        except Exception:

            pass

    #
    # ------------------------------------------------------------------
    # Mapping
    # ------------------------------------------------------------------
    #

    try:

        return dict(
            obj,
        )

    except Exception:

        return {}
# ==============================================================================
# Part 14.8 – safe_list()
# ==============================================================================

@staticmethod
def safe_list(
    obj=None,
):
    """
    Safely convert an object into a list.

    Parameters
    ----------
    obj
        Object to convert.

    Returns
    -------
    list
        List representation.
    """

    #
    # ------------------------------------------------------------------
    # None
    # ------------------------------------------------------------------
    #

    if obj is None:

        return []

    #
    # ------------------------------------------------------------------
    # Already a list
    # ------------------------------------------------------------------
    #

    if isinstance(
        obj,
        list,
    ):

        return obj.copy()

    #
    # ------------------------------------------------------------------
    # Tuple / Set
    # ------------------------------------------------------------------
    #

    if isinstance(
        obj,
        (
            tuple,
            set,
            frozenset,
        ),
    ):

        return list(
            obj,
        )

    #
    # ------------------------------------------------------------------
    # Dictionary
    # ------------------------------------------------------------------
    #

    if isinstance(
        obj,
        dict,
    ):

        return list(
            obj.items(),
        )

    #
    # ------------------------------------------------------------------
    # String / Bytes
    # ------------------------------------------------------------------
    #

    if isinstance(
        obj,
        (
            str,
            bytes,
            bytearray,
        ),
    ):

        return [
            obj,
        ]

    #
    # ------------------------------------------------------------------
    # Generic iterable
    # ------------------------------------------------------------------
    #

    try:

        return list(
            obj,
        )

    except Exception:

        return [
            obj,
        ]
# ==============================================================================
# Part 14.9 – safe_call()
# ==============================================================================

@staticmethod
def safe_call(
    func,
    *args,
    default=None,
    exceptions=(Exception,),
    **kwargs,
):
    """
    Safely invoke a callable.

    Parameters
    ----------
    func
        Callable object.

    *args
        Positional arguments.

    default
        Value returned if the call fails.

    exceptions
        Exception types to catch.

    **kwargs
        Keyword arguments.

    Returns
    -------
    object
        Callable result or default value.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    if not callable(
        func,
    ):

        raise TypeError(
            "func must be callable."
        )

    #
    # ------------------------------------------------------------------
    # Invoke
    # ------------------------------------------------------------------
    #

    try:

        return func(
            *args,
            **kwargs,
        )

    except exceptions:

        return default
# ==============================================================================
# Part 14.10 – safe_execute()
# ==============================================================================

@staticmethod
def safe_execute(
    func,
    *args,
    default=None,
    exceptions=(Exception,),
    logger=None,
    **kwargs,
):
    """
    Safely execute a callable with optional logging.

    Parameters
    ----------
    func
        Callable object.

    *args
        Positional arguments.

    default
        Value returned if execution fails.

    exceptions
        Exception types to catch.

    logger
        Optional logger used to record failures.

    **kwargs
        Keyword arguments.

    Returns
    -------
    object
        Callable result or default value.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    if not callable(
        func,
    ):

        raise TypeError(
            "func must be callable."
        )

    #
    # ------------------------------------------------------------------
    # Execute
    # ------------------------------------------------------------------
    #

    try:

        return func(
            *args,
            **kwargs,
        )

    except exceptions as exc:

        if logger is not None:

            try:

                logger.exception(
                    "Execution failed: %s",
                    func.__name__,
                )

            except Exception:

                pass

        return default
# ==============================================================================
# Part 14.11 – format_duration()
# ==============================================================================

@staticmethod
def format_duration(
    duration,
    *,
    precision=3,
):
    """
    Format a duration into a human-readable string.

    Parameters
    ----------
    duration
        Duration in seconds.

    precision
        Decimal precision.

    Returns
    -------
    str
        Formatted duration.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    if not isinstance(
        duration,
        (
            int,
            float,
        ),
    ):

        raise TypeError(
            "duration must be numeric."
        )

    if duration < 0:

        raise ValueError(
            "duration must be non-negative."
        )

    #
    # ------------------------------------------------------------------
    # Formatting
    # ------------------------------------------------------------------
    #

    if duration < 1e-6:

        return f"{duration * 1e9:.{precision}f} ns"

    if duration < 1e-3:

        return f"{duration * 1e6:.{precision}f} µs"

    if duration < 1:

        return f"{duration * 1e3:.{precision}f} ms"

    if duration < 60:

        return f"{duration:.{precision}f} s"

    minutes, seconds = divmod(
        duration,
        60,
    )

    if duration < 3600:

        return (
            f"{int(minutes)}m "
            f"{seconds:.{precision}f}s"
        )

    hours, minutes = divmod(
        int(minutes),
        60,
    )

    return (
        f"{hours}h "
        f"{minutes}m "
        f"{seconds:.{precision}f}s"
    )
# ==============================================================================
# Part 14.12 – format_timestamp()
# ==============================================================================

@staticmethod
def format_timestamp(
    timestamp=None,
    *,
    fmt="%Y-%m-%d %H:%M:%S.%f UTC",
    utc=True,
):
    """
    Format a Unix timestamp into a readable string.

    Parameters
    ----------
    timestamp
        Unix timestamp in seconds. If None, the current time is used.

    fmt
        datetime.strftime() format string.

    utc
        If True, format using UTC.
        Otherwise use the local timezone.

    Returns
    -------
    str
        Formatted timestamp.
    """

    #
    # ------------------------------------------------------------------
    # Default timestamp
    # ------------------------------------------------------------------
    #

    if timestamp is None:

        timestamp = time.time()

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    if not isinstance(
        timestamp,
        (
            int,
            float,
        ),
    ):

        raise TypeError(
            "timestamp must be numeric."
        )

    #
    # ------------------------------------------------------------------
    # Convert
    # ------------------------------------------------------------------
    #

    if utc:

        dt = datetime.datetime.fromtimestamp(
            timestamp,
            tz=datetime.timezone.utc,
        )

    else:

        dt = datetime.datetime.fromtimestamp(
            timestamp,
        )

    #
    # ------------------------------------------------------------------
    # Format
    # ------------------------------------------------------------------
    #

    text = dt.strftime(
        fmt,
    )

    #
    # ------------------------------------------------------------------
    # Trim trailing microseconds when not requested
    # ------------------------------------------------------------------
    #

    if "%f" not in fmt:

        return text

    return text
# ==============================================================================
# Part 14.13 – elapsed_time()
# ==============================================================================

@staticmethod
def elapsed_time(
    start_time,
    end_time=None,
):
    """
    Compute elapsed time between two timestamps.

    Parameters
    ----------
    start_time
        Start timestamp (Unix seconds).

    end_time
        End timestamp.
        If None, the current time is used.

    Returns
    -------
    float
        Elapsed time in seconds.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    if not isinstance(
        start_time,
        (
            int,
            float,
        ),
    ):

        raise TypeError(
            "start_time must be numeric."
        )

    if end_time is None:

        end_time = time.time()

    if not isinstance(
        end_time,
        (
            int,
            float,
        ),
    ):

        raise TypeError(
            "end_time must be numeric."
        )

    #
    # ------------------------------------------------------------------
    # Compute elapsed time
    # ------------------------------------------------------------------
    #

    elapsed = end_time - start_time

    #
    # ------------------------------------------------------------------
    # Clamp negative values
    # ------------------------------------------------------------------
    #

    if elapsed < 0:

        elapsed = 0.0

    return elapsed
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   # ==============================================================================
# Part 14.14 – runtime_age()
# ==============================================================================

def runtime_age(
    self,
    *,
    formatted=False,
):
    """
    Return the runtime age.

    Parameters
    ----------
    formatted
        If True, return a human-readable duration.

    Returns
    -------
    float | str
        Runtime age in seconds or formatted duration.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    #
    # ------------------------------------------------------------------
    # Determine creation time
    # ------------------------------------------------------------------
    #

    created_at = getattr(
        self,
        "_created_at",
        None,
    )

    if created_at is None:

        created_at = self._runtime_data.get(
            "created_at",
        )

    if created_at is None:

        raise RuntimeError(
            "Runtime creation timestamp is unavailable."
        )

    #
    # ------------------------------------------------------------------
    # Compute age
    # ------------------------------------------------------------------
    #

    age = self.elapsed_time(
        created_at,
    )

    #
    # ------------------------------------------------------------------
    # Return
    # ------------------------------------------------------------------
    #

    if formatted:

        return self.format_duration(
            age,
        )

    return age
# ==============================================================================
# Part 14.15 – helper_summary()
# ==============================================================================

def helper_summary(
    self,
):
    """
    Return a summary of helper utilities.

    Returns
    -------
    dict
        Helper function summary.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    now = time.time()

    #
    # ------------------------------------------------------------------
    # Build summary
    # ------------------------------------------------------------------
    #

    summary = {
        #
        # Identifier helpers
        #
        "generate_id": "available",
        "generate_uuid": "available",

        #
        # Time helpers
        #
        "generate_timestamp": "available",
        "format_timestamp": "available",
        "format_duration": "available",
        "elapsed_time": "available",
        "runtime_age": self.runtime_age(
            formatted=True,
        ),

        #
        # Safe helpers
        #
        "safe_copy": "available",
        "safe_deepcopy": "available",
        "safe_dict": "available",
        "safe_list": "available",
        "safe_call": "available",
        "safe_execute": "available",

        #
        # Name helper
        #
        "normalize_name": "available",

        #
        # Runtime
        #
        "generated_at": now,
    }

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    self._runtime_data[
        "last_helper_summary"
    ] = now

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    self._history.append(
        {
            "event": "helper_summary",
            "timestamp": now,
        }
    )

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    self._statistics.update_count += 1
    self._statistics.updated_at = now

    #
    # ------------------------------------------------------------------
    # Logger
    # ------------------------------------------------------------------
    #

    self._logger.debug(
        "Helper summary generated."
    )

    return summary
# ==============================================================================
# Part 15.1 – __repr__()
# ==============================================================================

def __repr__(
    self,
):
    """
    Return the official string representation of the SpanScope.

    Returns
    -------
    str
        Unambiguous representation suitable for debugging.
    """

    #
    # ------------------------------------------------------------------
    # Safe attribute lookup
    # ------------------------------------------------------------------
    #

    scope_id = getattr(
        self,
        "_id",
        None,
    )

    name = getattr(
        self,
        "_name",
        None,
    )

    enabled = getattr(
        self,
        "_enabled",
        None,
    )

    active = getattr(
        self,
        "_active",
        None,
    )

    callback_count = len(
        getattr(
            self,
            "_callbacks",
            {},
        )
    )

    hook_count = len(
        getattr(
            self,
            "_hooks",
            {},
        )
    )

    history_size = len(
        getattr(
            self,
            "_history",
            [],
        )
    )

    #
    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------
    #

    return (
        f"{self.__class__.__name__}("
        f"id={scope_id!r}, "
        f"name={name!r}, "
        f"enabled={enabled!r}, "
        f"active={active!r}, "
        f"callbacks={callback_count}, "
        f"hooks={hook_count}, "
        f"history={history_size}"
        f")"
    )
# ==============================================================================
# Part 15.2 – __str__()
# ==============================================================================

def __str__(
    self,
):
    """
    Return a human-readable representation of the SpanScope.

    Returns
    -------
    str
        Friendly description of the runtime.
    """

    #
    # ------------------------------------------------------------------
    # Safe attribute lookup
    # ------------------------------------------------------------------
    #

    scope_id = getattr(
        self,
        "_id",
        "unknown",
    )

    name = getattr(
        self,
        "_name",
        "unnamed",
    )

    enabled = getattr(
        self,
        "_enabled",
        False,
    )

    active = getattr(
        self,
        "_active",
        False,
    )

    age = "unknown"

    try:

        age = self.runtime_age(
            formatted=True,
        )

    except Exception:

        pass

    #
    # ------------------------------------------------------------------
    # State
    # ------------------------------------------------------------------
    #

    if active:

        state = "active"

    elif enabled:

        state = "enabled"

    else:

        state = "disabled"

    #
    # ------------------------------------------------------------------
    # Human-readable string
    # ------------------------------------------------------------------
    #

    return (
        f"SpanScope "
        f"'{name}' "
        f"[{scope_id}] "
        f"({state}, "
        f"age={age})"
    )
# ==============================================================================
# Part 15.3 – __len__()
# ==============================================================================

def __len__(
    self,
):
    """
    Return the logical size of the SpanScope.

    Returns
    -------
    int
        Number of registered runtime entries.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    total = 0

    #
    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------
    #

    total += len(
        getattr(
            self,
            "_callbacks",
            {},
        )
    )

    #
    # ------------------------------------------------------------------
    # Hooks
    # ------------------------------------------------------------------
    #

    total += len(
        getattr(
            self,
            "_hooks",
            {},
        )
    )

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    total += len(
        getattr(
            self,
            "_runtime_data",
            {},
        )
    )

    #
    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------
    #

    total += len(
        getattr(
            self,
            "_metadata",
            {},
        )
    )

    #
    # ------------------------------------------------------------------
    # Return
    # ------------------------------------------------------------------
    #

    return total
# ==============================================================================
# Part 15.4 – __iter__()
# ==============================================================================

def __iter__(
    self,
):
    """
    Iterate over the runtime metadata.

    Yields
    ------
    tuple
        (key, value) pairs from the runtime state.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    #
    # ------------------------------------------------------------------
    # Runtime data
    # ------------------------------------------------------------------
    #

    runtime_data = getattr(
        self,
        "_runtime_data",
        {},
    )

    for key, value in runtime_data.items():

        yield key, value
# ==============================================================================
# Part 15.5 – __contains__()
# ==============================================================================

def __contains__(
    self,
    key,
):
    """
    Determine whether a key exists in the SpanScope.

    Parameters
    ----------
    key
        Lookup key.

    Returns
    -------
    bool
        True if the key exists, otherwise False.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    if not isinstance(
        key,
        str,
    ):

        return False

    #
    # ------------------------------------------------------------------
    # Runtime data
    # ------------------------------------------------------------------
    #

    runtime_data = getattr(
        self,
        "_runtime_data",
        {},
    )

    if key in runtime_data:

        return True

    #
    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------
    #

    metadata = getattr(
        self,
        "_metadata",
        {},
    )

    if key in metadata:

        return True

    #
    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------
    #

    callbacks = getattr(
        self,
        "_callbacks",
        {},
    )

    if key in callbacks:

        return True

    #
    # ------------------------------------------------------------------
    # Hooks
    # ------------------------------------------------------------------
    #

    hooks = getattr(
        self,
        "_hooks",
        {},
    )

    if key in hooks:

        return True

    #
    # ------------------------------------------------------------------
    # Not found
    # ------------------------------------------------------------------
    #

    return False
# ==============================================================================
# Part 15.6 – __getitem__()
# ==============================================================================

def __getitem__(
    self,
    key,
):
    """
    Retrieve a value from the SpanScope.

    Search order
    ------------
    1. runtime_data
    2. metadata
    3. callbacks
    4. hooks

    Parameters
    ----------
    key
        Lookup key.

    Returns
    -------
    object
        Associated value.

    Raises
    ------
    KeyError
        If the key does not exist.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    if not isinstance(
        key,
        str,
    ):

        raise TypeError(
            "key must be a string."
        )

    #
    # ------------------------------------------------------------------
    # Runtime data
    # ------------------------------------------------------------------
    #

    runtime_data = getattr(
        self,
        "_runtime_data",
        {},
    )

    if key in runtime_data:

        return runtime_data[key]

    #
    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------
    #

    metadata = getattr(
        self,
        "_metadata",
        {},
    )

    if key in metadata:

        return metadata[key]

    #
    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------
    #

    callbacks = getattr(
        self,
        "_callbacks",
        {},
    )

    if key in callbacks:

        return callbacks[key]

    #
    # ------------------------------------------------------------------
    # Hooks
    # ------------------------------------------------------------------
    #

    hooks = getattr(
        self,
        "_hooks",
        {},
    )

    if key in hooks:

        return hooks[key]

    #
    # ------------------------------------------------------------------
    # Missing key
    # ------------------------------------------------------------------
    #

    raise KeyError(
        f"{key!r} not found in SpanScope."
    )
# ==============================================================================
# Part 15.7 – __setitem__()
# ==============================================================================

def __setitem__(
    self,
    key,
    value,
):
    """
    Store a value in the SpanScope.

    Existing keys are updated in-place.
    New keys are inserted into runtime_data.

    Parameters
    ----------
    key
        Key name.

    value
        Value to store.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    if not isinstance(
        key,
        str,
    ):

        raise TypeError(
            "key must be a string."
        )

    key = self.normalize_name(
        key,
    )

    now = time.time()

    #
    # ------------------------------------------------------------------
    # Runtime data
    # ------------------------------------------------------------------
    #

    runtime_data = getattr(
        self,
        "_runtime_data",
        {},
    )

    if key in runtime_data:

        runtime_data[key] = value

    #
    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------
    #

    elif key in getattr(
        self,
        "_metadata",
        {},
    ):

        self._metadata[key] = value

    #
    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------
    #

    elif key in getattr(
        self,
        "_callbacks",
        {},
    ):

        self._callbacks[key] = value

    #
    # ------------------------------------------------------------------
    # Hooks
    # ------------------------------------------------------------------
    #

    elif key in getattr(
        self,
        "_hooks",
        {},
    ):

        self._hooks[key] = value

    #
    # ------------------------------------------------------------------
    # New runtime entry
    # ------------------------------------------------------------------
    #

    else:

        runtime_data[key] = value

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    runtime_data["updated_at"] = now

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    self._history.append(
        {
            "event": "setitem",
            "key": key,
            "timestamp": now,
        }
    )

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    self._statistics.update_count += 1
    self._statistics.updated_at = now

    #
    # ------------------------------------------------------------------
    # Logger
    # ------------------------------------------------------------------
    #

    self._logger.debug(
        "Set item: %s",
        key,
    )
# ==============================================================================
# Part 15.8 – __delitem__()
# ==============================================================================

def __delitem__(
    self,
    key,
):
    """
    Remove an item from the SpanScope.

    Search order
    ------------
    1. runtime_data
    2. metadata
    3. callbacks
    4. hooks

    Parameters
    ----------
    key
        Key to remove.

    Raises
    ------
    KeyError
        If the key does not exist.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    if not isinstance(
        key,
        str,
    ):

        raise TypeError(
            "key must be a string."
        )

    key = self.normalize_name(
        key,
    )

    now = time.time()

    removed = False

    #
    # ------------------------------------------------------------------
    # Runtime data
    # ------------------------------------------------------------------
    #

    runtime_data = getattr(
        self,
        "_runtime_data",
        {},
    )

    if key in runtime_data:

        del runtime_data[key]
        removed = True

    #
    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------
    #

    elif key in getattr(
        self,
        "_metadata",
        {},
    ):

        del self._metadata[key]
        removed = True

    #
    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------
    #

    elif key in getattr(
        self,
        "_callbacks",
        {},
    ):

        del self._callbacks[key]
        removed = True

    #
    # ------------------------------------------------------------------
    # Hooks
    # ------------------------------------------------------------------
    #

    elif key in getattr(
        self,
        "_hooks",
        {},
    ):

        del self._hooks[key]
        removed = True

    #
    # ------------------------------------------------------------------
    # Missing key
    # ------------------------------------------------------------------
    #

    if not removed:

        raise KeyError(
            f"{key!r} not found in SpanScope."
        )

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    runtime_data["updated_at"] = now

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    self._history.append(
        {
            "event": "delitem",
            "key": key,
            "timestamp": now,
        }
    )

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    self._statistics.update_count += 1
    self._statistics.updated_at = now

    #
    # ------------------------------------------------------------------
    # Logger
    # ------------------------------------------------------------------
    #

    self._logger.debug(
        "Deleted item: %s",
        key,
    )
# ==============================================================================
# Part 15.9 – __call__()
# ==============================================================================

def __call__(
    self,
    action=None,
    *args,
    **kwargs,
):
    """
    Execute a runtime action.

    Parameters
    ----------
    action
        Runtime action or callable.

    *args
        Positional arguments.

    **kwargs
        Keyword arguments.

    Returns
    -------
    object
        Result of the executed action.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    #
    # ------------------------------------------------------------------
    # Default action
    # ------------------------------------------------------------------
    #

    if action is None:

        return self.summary()

    #
    # ------------------------------------------------------------------
    # Callable
    # ------------------------------------------------------------------
    #

    if callable(
        action,
    ):

        return self.safe_execute(
            action,
            *args,
            logger=self._logger,
            **kwargs,
        )

    #
    # ------------------------------------------------------------------
    # Named runtime action
    # ------------------------------------------------------------------
    #

    if isinstance(
        action,
        str,
    ):

        action = self.normalize_name(
            action,
        )

        method = getattr(
            self,
            action,
            None,
        )

        if callable(
            method,
        ):

            return self.safe_execute(
                method,
                *args,
                logger=self._logger,
                **kwargs,
            )

        raise AttributeError(
            f"Unknown runtime action: {action!r}"
        )

    #
    # ------------------------------------------------------------------
    # Unsupported
    # ------------------------------------------------------------------
    #

    raise TypeError(
        "action must be None, a callable, or a method name."
    )
# ==============================================================================
# Part 15.10 – __bool__()
# ==============================================================================

def __bool__(
    self,
):
    """
    Return the truth value of the SpanScope.

    Returns
    -------
    bool
        True if the runtime is enabled, active, and not closed.
    """

    #
    # ------------------------------------------------------------------
    # Safe state lookup
    # ------------------------------------------------------------------
    #

    enabled = bool(
        getattr(
            self,
            "_enabled",
            False,
        )
    )

    active = bool(
        getattr(
            self,
            "_active",
            False,
        )
    )

    closed = bool(
        getattr(
            self,
            "_closed",
            False,
        )
    )

    #
    # ------------------------------------------------------------------
    # Truth value
    # ------------------------------------------------------------------
    #

    return (
        enabled
        and active
        and not closed
    )
# ==============================================================================
# Part 15.11 – __eq__()
# ==============================================================================

def __eq__(
    self,
    other,
):
    """
    Compare two SpanScope objects.

    Equality is determined by the runtime identifier.

    Parameters
    ----------
    other
        Object to compare.

    Returns
    -------
    bool
        True if both objects represent the same runtime.
    """

    #
    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------
    #

    if self is other:

        return True

    #
    # ------------------------------------------------------------------
    # Type
    # ------------------------------------------------------------------
    #

    if not isinstance(
        other,
        self.__class__,
    ):

        return NotImplemented

    #
    # ------------------------------------------------------------------
    # Compare runtime identifier
    # ------------------------------------------------------------------
    #

    return (
        getattr(
            self,
            "_id",
            None,
        )
        ==
        getattr(
            other,
            "_id",
            None,
        )
    )
# ==============================================================================
# Part 15.12 – __hash__()
# ==============================================================================

def __hash__(
    self,
):
    """
    Return the hash of the SpanScope.

    The hash is derived from the immutable runtime identifier.

    Returns
    -------
    int
        Hash value.
    """

    runtime_id = getattr(
        self,
        "_id",
        None,
    )

    if runtime_id is None:

        raise TypeError(
            "Cannot hash a SpanScope without a runtime identifier."
        )

    return hash(
        runtime_id,
    )
# ==============================================================================
# Part 15.13 – __copy__()
# ==============================================================================

def __copy__(
    self,
):
    """
    Create a shallow copy of the SpanScope.

    Returns
    -------
    SpanScope
        Shallow copied instance.
    """

    #
    # ------------------------------------------------------------------
    # Create new instance
    # ------------------------------------------------------------------
    #

    cls = self.__class__

    new_obj = cls.__new__(
        cls,
    )

    #
    # ------------------------------------------------------------------
    # Shallow copy attributes
    # ------------------------------------------------------------------
    #

    for key, value in self.__dict__.items():

        setattr(
            new_obj,
            key,
            copy.copy(
                value,
            ),
        )

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    if hasattr(
        new_obj,
        "_history",
    ):

        new_obj._history.append(
            {
                "event": "__copy__",
                "timestamp": time.time(),
            }
        )

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    if hasattr(
        new_obj,
        "_statistics",
    ):

        new_obj._statistics.update_count += 1
        new_obj._statistics.updated_at = time.time()

    #
    # ------------------------------------------------------------------
    # Logger
    # ------------------------------------------------------------------
    #

    logger = getattr(
        new_obj,
        "_logger",
        None,
    )

    if logger is not None:

        logger.debug(
            "Shallow copy created."
        )

    return new_obj
# ==============================================================================
# Part 15.14 – __deepcopy__()
# ==============================================================================

def __deepcopy__(
    self,
    memo,
):
    """
    Create a deep copy of the SpanScope.

    Parameters
    ----------
    memo
        Memoization dictionary used by copy.deepcopy().

    Returns
    -------
    SpanScope
        Deep copied instance.
    """

    #
    # ------------------------------------------------------------------
    # Memo lookup
    # ------------------------------------------------------------------
    #

    obj_id = id(self)

    if obj_id in memo:

        return memo[obj_id]

    #
    # ------------------------------------------------------------------
    # Create instance
    # ------------------------------------------------------------------
    #

    cls = self.__class__

    new_obj = cls.__new__(
        cls,
    )

    memo[obj_id] = new_obj

    #
    # ------------------------------------------------------------------
    # Deep copy attributes
    # ------------------------------------------------------------------
    #

    for key, value in self.__dict__.items():

        setattr(
            new_obj,
            key,
            copy.deepcopy(
                value,
                memo,
            ),
        )

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    if hasattr(
        new_obj,
        "_history",
    ):

        new_obj._history.append(
            {
                "event": "__deepcopy__",
                "timestamp": time.time(),
            }
        )

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    if hasattr(
        new_obj,
        "_statistics",
    ):

        new_obj._statistics.update_count += 1
        new_obj._statistics.updated_at = time.time()

    #
    # ------------------------------------------------------------------
    # Logger
    # ------------------------------------------------------------------
    #

    logger = getattr(
        new_obj,
        "_logger",
        None,
    )

    if logger is not None:

        logger.debug(
            "Deep copy created."
        )

    return new_obj
# ==============================================================================
# Part 15.15 – __enter__()
# ==============================================================================

def __enter__(
    self,
):
    """
    Enter the runtime context.

    Returns
    -------
    SpanScope
        Current runtime instance.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    now = time.time()

    #
    # ------------------------------------------------------------------
    # Activate runtime
    # ------------------------------------------------------------------
    #

    if hasattr(
        self,
        "_active",
    ):

        self._active = True

    if hasattr(
        self,
        "_runtime_data",
    ):

        self._runtime_data[
            "entered_at"
        ] = now

        self._runtime_data[
            "updated_at"
        ] = now

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    if hasattr(
        self,
        "_history",
    ):

        self._history.append(
            {
                "event": "__enter__",
                "timestamp": now,
            }
        )

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    if hasattr(
        self,
        "_statistics",
    ):

        self._statistics.update_count += 1
        self._statistics.updated_at = now

    #
    # ------------------------------------------------------------------
    # Logger
    # ------------------------------------------------------------------
    #

    logger = getattr(
        self,
        "_logger",
        None,
    )

    if logger is not None:

        logger.debug(
            "Entered SpanScope context."
        )

    #
    # ------------------------------------------------------------------
    # Return self
    # ------------------------------------------------------------------
    #

    return self
# ==============================================================================
# Part 15.16 – __exit__()
# ==============================================================================

def __exit__(
    self,
    exc_type,
    exc_value,
    traceback,
):
    """
    Exit the runtime context.

    Parameters
    ----------
    exc_type
        Exception type raised inside the context.

    exc_value
        Exception instance.

    traceback
        Exception traceback.

    Returns
    -------
    bool
        False to propagate exceptions.
    """

    #
    # ------------------------------------------------------------------
    # Timestamp
    # ------------------------------------------------------------------
    #

    now = time.time()

    #
    # ------------------------------------------------------------------
    # Deactivate runtime
    # ------------------------------------------------------------------
    #

    if hasattr(
        self,
        "_active",
    ):

        self._active = False

    if hasattr(
        self,
        "_runtime_data",
    ):

        self._runtime_data[
            "exited_at"
        ] = now

        self._runtime_data[
            "updated_at"
        ] = now

    #
    # ------------------------------------------------------------------
    # Exception information
    # ------------------------------------------------------------------
    #

    exception_info = None

    if exc_type is not None:

        exception_info = {
            "type": exc_type.__name__,
            "message": str(exc_value),
        }

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    if hasattr(
        self,
        "_history",
    ):

        self._history.append(
            {
                "event": "__exit__",
                "timestamp": now,
                "exception": exception_info,
            }
        )

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    if hasattr(
        self,
        "_statistics",
    ):

        self._statistics.update_count += 1
        self._statistics.updated_at = now

        if (
            exc_type is not None
            and hasattr(
                self._statistics,
                "error_count",
            )
        ):

            self._statistics.error_count += 1

    #
    # ------------------------------------------------------------------
    # Logger
    # ------------------------------------------------------------------
    #

    logger = getattr(
        self,
        "_logger",
        None,
    )

    if logger is not None:

        if exc_type is None:

            logger.debug(
                "Exited SpanScope context."
            )

        else:

            logger.exception(
                "SpanScope context exited with exception."
            )

    #
    # ------------------------------------------------------------------
    # Invoke exit hooks
    # ------------------------------------------------------------------
    #

    try:

        self.invoke_all_hooks(
            event="exit",
            exception=exception_info,
        )

    except Exception:

        pass

    #
    # ------------------------------------------------------------------
    # Invoke callbacks
    # ------------------------------------------------------------------
    #

    try:

        self.invoke_all_callbacks(
            event="exit",
            exception=exception_info,
        )

    except Exception:

        pass

    #
    # ------------------------------------------------------------------
    # Do not suppress exceptions
    # ------------------------------------------------------------------
    #

    return False
# ==============================================================================
# Part 16.1 – get()
# ==============================================================================

def get(
    self,
    key,
    default=None,
):
    """
    Retrieve a value from the SpanScope.

    Search order
    ------------
    1. runtime_data
    2. metadata
    3. callbacks
    4. hooks

    Parameters
    ----------
    key
        Lookup key.

    default
        Value returned if the key is not found.

    Returns
    -------
    object
        Stored value or default.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    if not isinstance(
        key,
        str,
    ):

        raise TypeError(
            "key must be a string."
        )

    key = self.normalize_name(
        key,
    )

    #
    # ------------------------------------------------------------------
    # Runtime data
    # ------------------------------------------------------------------
    #

    runtime_data = getattr(
        self,
        "_runtime_data",
        {},
    )

    if key in runtime_data:

        return runtime_data[key]

    #
    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------
    #

    metadata = getattr(
        self,
        "_metadata",
        {},
    )

    if key in metadata:

        return metadata[key]

    #
    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------
    #

    callbacks = getattr(
        self,
        "_callbacks",
        {},
    )

    if key in callbacks:

        return callbacks[key]

    #
    # ------------------------------------------------------------------
    # Hooks
    # ------------------------------------------------------------------
    #

    hooks = getattr(
        self,
        "_hooks",
        {},
    )

    if key in hooks:

        return hooks[key]

    #
    # ------------------------------------------------------------------
    # Default
    # ------------------------------------------------------------------
    #

    return default
# ==============================================================================
# Part 16.2 – set()
# ==============================================================================

def set(
    self,
    key,
    value,
):
    """
    Store a value in the SpanScope.

    Existing keys are updated in-place.
    New keys are inserted into runtime_data.

    Parameters
    ----------
    key
        Key name.

    value
        Value to store.

    Returns
    -------
    SpanScope
        Current instance (method chaining).
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    if not isinstance(
        key,
        str,
    ):

        raise TypeError(
            "key must be a string."
        )

    #
    # ------------------------------------------------------------------
    # Delegate to mapping protocol
    # ------------------------------------------------------------------
    #

    self[key] = value

    #
    # ------------------------------------------------------------------
    # Return self
    # ------------------------------------------------------------------
    #

    return self
# ==============================================================================
# Part 16.3 – remove()
# ==============================================================================

def remove(
    self,
    key,
    *,
    silent=False,
):
    """
    Remove a key from the SpanScope.

    Search order
    ------------
    1. runtime_data
    2. metadata
    3. callbacks
    4. hooks

    Parameters
    ----------
    key
        Key to remove.

    silent
        If True, ignore missing keys.

    Returns
    -------
    SpanScope
        Current instance (method chaining).

    Raises
    ------
    KeyError
        If the key does not exist and silent=False.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    if not isinstance(
        key,
        str,
    ):

        raise TypeError(
            "key must be a string."
        )

    key = self.normalize_name(
        key,
    )

    #
    # ------------------------------------------------------------------
    # Remove
    # ------------------------------------------------------------------
    #

    try:

        del self[key]

    except KeyError:

        if not silent:

            raise

    #
    # ------------------------------------------------------------------
    # Return self
    # ------------------------------------------------------------------
    #

    return self
# ==============================================================================
# Part 16.4 – update()
# ==============================================================================

def update(
    self,
    mapping=None,
    **kwargs,
):
    """
    Update multiple values in the SpanScope.

    Parameters
    ----------
    mapping
        Dictionary or mapping object containing values to update.

    **kwargs
        Additional key/value pairs.

    Returns
    -------
    SpanScope
        Current instance (method chaining).
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    #
    # ------------------------------------------------------------------
    # Normalize input
    # ------------------------------------------------------------------
    #

    updates = {}

    if mapping is not None:

        if hasattr(
            mapping,
            "items",
        ):

            updates.update(
                dict(mapping.items()),
            )

        else:

            raise TypeError(
                "mapping must be a mapping object."
            )

    if kwargs:

        updates.update(
            kwargs,
        )

    #
    # ------------------------------------------------------------------
    # Apply updates
    # ------------------------------------------------------------------
    #

    for key, value in updates.items():

        self.set(
            key,
            value,
        )

    #
    # ------------------------------------------------------------------
    # Return self
    # ------------------------------------------------------------------
    #

    return self
# ==============================================================================
# Part 16.5 – exists()
# ==============================================================================

def exists(
    self,
    key,
):
    """
    Determine whether a key exists in the SpanScope.

    Search order
    ------------
    1. runtime_data
    2. metadata
    3. callbacks
    4. hooks

    Parameters
    ----------
    key
        Lookup key.

    Returns
    -------
    bool
        True if the key exists, otherwise False.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    if not isinstance(
        key,
        str,
    ):

        raise TypeError(
            "key must be a string."
        )

    #
    # ------------------------------------------------------------------
    # Normalize
    # ------------------------------------------------------------------
    #

    key = self.normalize_name(
        key,
    )

    #
    # ------------------------------------------------------------------
    # Delegate to mapping protocol
    # ------------------------------------------------------------------
    #

    return key in self
# ==============================================================================
# Part 16.6 – keys()
# ==============================================================================

def keys(
    self,
):
    """
    Return all logical keys in the SpanScope.

    Returns
    -------
    tuple[str, ...]
        Sorted unique keys.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    #
    # ------------------------------------------------------------------
    # Collect keys
    # ------------------------------------------------------------------
    #

    key_set = set()

    key_set.update(
        getattr(
            self,
            "_runtime_data",
            {},
        ).keys()
    )

    key_set.update(
        getattr(
            self,
            "_metadata",
            {},
        ).keys()
    )

    key_set.update(
        getattr(
            self,
            "_callbacks",
            {},
        ).keys()
    )

    key_set.update(
        getattr(
            self,
            "_hooks",
            {},
        ).keys()
    )

    #
    # ------------------------------------------------------------------
    # Return
    # ------------------------------------------------------------------
    #

    return tuple(
        sorted(
            key_set,
        )
    )
# ==============================================================================
# Part 16.7 – values()
# ==============================================================================

def values(
    self,
):
    """
    Return all logical values stored in the SpanScope.

    Values are returned following the logical key order.

    Returns
    -------
    tuple
        Values corresponding to keys().
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    #
    # ------------------------------------------------------------------
    # Collect values
    # ------------------------------------------------------------------
    #

    values = []

    for key in self.keys():

        values.append(
            self.get(
                key,
            )
        )

    #
    # ------------------------------------------------------------------
    # Return
    # ------------------------------------------------------------------
    #

    return tuple(
        values,
    )
# ==============================================================================
# Part 16.8 – items()
# ==============================================================================

def items(
    self,
):
    """
    Return all logical key/value pairs stored in the SpanScope.

    Returns
    -------
    tuple[tuple[str, object], ...]
        Tuple of (key, value) pairs.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    #
    # ------------------------------------------------------------------
    # Collect items
    # ------------------------------------------------------------------
    #

    result = []

    for key in self.keys():

        result.append(
            (
                key,
                self.get(
                    key,
                ),
            )
        )

    #
    # ------------------------------------------------------------------
    # Return
    # ------------------------------------------------------------------
    #

    return tuple(
        result,
    )
# ==============================================================================
# Part 16.9 – merge()
# ==============================================================================

def merge(
    self,
    other,
    *,
    overwrite=True,
):
    """
    Merge another mapping or SpanScope into this runtime.

    Parameters
    ----------
    other
        SpanScope or mapping object.

    overwrite
        If True, existing values are replaced.
        Otherwise, existing values are preserved.

    Returns
    -------
    SpanScope
        Current instance (method chaining).
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    #
    # ------------------------------------------------------------------
    # Normalize source
    # ------------------------------------------------------------------
    #

    if isinstance(
        other,
        self.__class__,
    ):

        source = dict(
            other.items(),
        )

    elif hasattr(
        other,
        "items",
    ):

        source = dict(
            other.items(),
        )

    else:

        raise TypeError(
            "other must be a SpanScope or mapping object."
        )

    #
    # ------------------------------------------------------------------
    # Merge
    # ------------------------------------------------------------------
    #

    merged = 0
    skipped = 0

    for key, value in source.items():

        if overwrite:

            self.set(
                key,
                value,
            )

            merged += 1

        else:

            if not self.exists(
                key,
            ):

                self.set(
                    key,
                    value,
                )

                merged += 1

            else:

                skipped += 1

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    now = time.time()

    self._runtime_data["updated_at"] = now
    self._runtime_data["last_merge"] = now

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    self._history.append(
        {
            "event": "merge",
            "merged": merged,
            "skipped": skipped,
            "overwrite": overwrite,
            "timestamp": now,
        }
    )

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    self._statistics.update_count += 1
    self._statistics.updated_at = now

    #
    # ------------------------------------------------------------------
    # Logger
    # ------------------------------------------------------------------
    #

    self._logger.debug(
        "Merged %d item(s), skipped %d.",
        merged,
        skipped,
    )

    return self
# ==============================================================================
# Part 16.10 – apply()
# ==============================================================================

def apply(
    self,
    func,
    *,
    keys=None,
    inplace=True,
):
    """
    Apply a transformation function to one or more runtime values.

    Parameters
    ----------
    func
        Callable with signature:
            func(key, value) -> new_value

    keys
        Optional iterable of keys.
        If None, all logical keys are processed.

    inplace
        If True, update the current runtime.
        Otherwise, return a transformed dictionary.

    Returns
    -------
    SpanScope | dict
        Current instance (method chaining) or transformed dictionary.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    if not callable(func):

        raise TypeError(
            "func must be callable."
        )

    #
    # ------------------------------------------------------------------
    # Determine target keys
    # ------------------------------------------------------------------
    #

    if keys is None:

        target_keys = self.keys()

    else:

        target_keys = tuple(keys)

    #
    # ------------------------------------------------------------------
    # Apply transformation
    # ------------------------------------------------------------------
    #

    result = {}

    for key in target_keys:

        if not self.exists(key):

            continue

        old_value = self.get(key)

        new_value = self.safe_execute(
            func,
            key,
            old_value,
            logger=self._logger,
        )

        result[key] = new_value

        if inplace:

            self.set(
                key,
                new_value,
            )

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    now = time.time()

    if inplace:

        self._runtime_data["updated_at"] = now
        self._runtime_data["last_apply"] = now

        self._history.append(
            {
                "event": "apply",
                "count": len(result),
                "timestamp": now,
            }
        )

        self._statistics.update_count += 1
        self._statistics.updated_at = now

        self._logger.debug(
            "Applied transformation to %d item(s).",
            len(result),
        )

        return self

    #
    # ------------------------------------------------------------------
    # Return transformed data
    # ------------------------------------------------------------------
    #

    return result
# ==============================================================================
# Part 16.11 – execute()
# ==============================================================================

def execute(
    self,
    operation,
    *args,
    **kwargs,
):
    """
    Execute a runtime operation.

    Parameters
    ----------
    operation
        Callable or method name.

    *args
        Positional arguments.

    **kwargs
        Keyword arguments.

    Returns
    -------
    object
        Result returned by the executed operation.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    #
    # ------------------------------------------------------------------
    # Timestamp
    # ------------------------------------------------------------------
    #

    started_at = time.time()

    #
    # ------------------------------------------------------------------
    # Execute callable
    # ------------------------------------------------------------------
    #

    if callable(
        operation,
    ):

        result = self.safe_execute(
            operation,
            *args,
            logger=self._logger,
            **kwargs,
        )

        operation_name = getattr(
            operation,
            "__name__",
            "<callable>",
        )

    #
    # ------------------------------------------------------------------
    # Execute member function
    # ------------------------------------------------------------------
    #

    elif isinstance(
        operation,
        str,
    ):

        operation_name = self.normalize_name(
            operation,
        )

        method = getattr(
            self,
            operation_name,
            None,
        )

        if method is None:

            raise AttributeError(
                f"Unknown runtime operation: {operation_name!r}"
            )

        result = self.safe_execute(
            method,
            *args,
            logger=self._logger,
            **kwargs,
        )

    #
    # ------------------------------------------------------------------
    # Unsupported
    # ------------------------------------------------------------------
    #

    else:

        raise TypeError(
            "operation must be callable or method name."
        )

    #
    # ------------------------------------------------------------------
    # Runtime metadata
    # ------------------------------------------------------------------
    #

    finished_at = time.time()

    duration = (
        finished_at
        - started_at
    )

    self._runtime_data["updated_at"] = finished_at
    self._runtime_data["last_execution"] = operation_name

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    self._history.append(
        {
            "event": "execute",
            "operation": operation_name,
            "duration": duration,
            "timestamp": finished_at,
        }
    )

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    self._statistics.update_count += 1
    self._statistics.updated_at = finished_at

    if hasattr(
        self._statistics,
        "execution_count",
    ):

        self._statistics.execution_count += 1

    #
    # ------------------------------------------------------------------
    # Logger
    # ------------------------------------------------------------------
    #

    self._logger.debug(
        "Executed '%s' in %.6f s.",
        operation_name,
        duration,
    )

    #
    # ------------------------------------------------------------------
    # Return
    # ------------------------------------------------------------------
    #

    return result
# ==============================================================================
# Part 16.12 – inspect()
# ==============================================================================

def inspect(
    self,
):
    """
    Inspect the current SpanScope runtime.

    Returns
    -------
    dict
        Human-readable runtime inspection report.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    #
    # ------------------------------------------------------------------
    # Timestamp
    # ------------------------------------------------------------------
    #

    now = time.time()

    #
    # ------------------------------------------------------------------
    # Build inspection report
    # ------------------------------------------------------------------
    #

    report = {
        #
        # Identity
        #
        "id": getattr(
            self,
            "_id",
            None,
        ),
        "name": getattr(
            self,
            "_name",
            None,
        ),
        "uuid": getattr(
            self,
            "_uuid",
            None,
        ),
        #
        # Runtime state
        #
        "enabled": getattr(
            self,
            "_enabled",
            False,
        ),
        "active": getattr(
            self,
            "_active",
            False,
        ),
        "closed": getattr(
            self,
            "_closed",
            False,
        ),
        #
        # Statistics
        #
        "runtime_age": self.runtime_age(),
        "callback_count": len(
            getattr(
                self,
                "_callbacks",
                {},
            )
        ),
        "hook_count": len(
            getattr(
                self,
                "_hooks",
                {},
            )
        ),
        "runtime_keys": len(
            getattr(
                self,
                "_runtime_data",
                {},
            )
        ),
        "metadata_keys": len(
            getattr(
                self,
                "_metadata",
                {},
            )
        ),
        "history_size": len(
            getattr(
                self,
                "_history",
                [],
            )
        ),
        #
        # Activity
        #
        "last_execution": getattr(
            self,
            "_runtime_data",
            {},
        ).get(
            "last_execution",
        ),
        "updated_at": getattr(
            self,
            "_runtime_data",
            {},
        ).get(
            "updated_at",
        ),
        #
        # Timestamp
        #
        "inspection_time": now,
    }

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    self._history.append(
        {
            "event": "inspect",
            "timestamp": now,
        }
    )

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    self._statistics.update_count += 1
    self._statistics.updated_at = now

    #
    # ------------------------------------------------------------------
    # Logger
    # ------------------------------------------------------------------
    #

    self._logger.debug(
        "Runtime inspection generated."
    )

    #
    # ------------------------------------------------------------------
    # Return
    # ------------------------------------------------------------------
    #

    return report
# ==============================================================================
# Part 16.13 – status()
# ==============================================================================

def status(
    self,
):
    """
    Return the current runtime status.

    Returns
    -------
    dict
        Runtime status information.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    now = time.time()

    #
    # ------------------------------------------------------------------
    # Determine runtime state
    # ------------------------------------------------------------------
    #

    if getattr(
        self,
        "_closed",
        False,
    ):

        state = "closed"

    elif getattr(
        self,
        "_active",
        False,
    ):

        state = "active"

    elif getattr(
        self,
        "_enabled",
        False,
    ):

        state = "idle"

    else:

        state = "disabled"

    #
    # ------------------------------------------------------------------
    # Build status
    # ------------------------------------------------------------------
    #

    result = {
        "state": state,
        "enabled": getattr(
            self,
            "_enabled",
            False,
        ),
        "active": getattr(
            self,
            "_active",
            False,
        ),
        "closed": getattr(
            self,
            "_closed",
            False,
        ),
        "runtime_age": self.runtime_age(),
        "last_execution": getattr(
            self,
            "_runtime_data",
            {},
        ).get(
            "last_execution",
        ),
        "updated_at": getattr(
            self,
            "_runtime_data",
            {},
        ).get(
            "updated_at",
        ),
        "timestamp": now,
    }

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    self._history.append(
        {
            "event": "status",
            "timestamp": now,
        }
    )

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    self._statistics.update_count += 1
    self._statistics.updated_at = now

    #
    # ------------------------------------------------------------------
    # Logger
    # ------------------------------------------------------------------
    #

    self._logger.debug(
        "Runtime status requested."
    )

    #
    # ------------------------------------------------------------------
    # Return
    # ------------------------------------------------------------------
    #

    return result
# ==============================================================================
# Part 16.14 – health()
# ==============================================================================

def health(
    self,
):
    """
    Perform a health check on the SpanScope runtime.

    Returns
    -------
    dict
        Runtime health report.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    now = time.time()

    issues = []

    #
    # ------------------------------------------------------------------
    # Runtime state checks
    # ------------------------------------------------------------------
    #

    if getattr(
        self,
        "_closed",
        False,
    ):

        issues.append(
            "runtime_closed"
        )

    if not getattr(
        self,
        "_enabled",
        False,
    ):

        issues.append(
            "runtime_disabled"
        )

    #
    # ------------------------------------------------------------------
    # Required components
    # ------------------------------------------------------------------
    #

    if not hasattr(
        self,
        "_runtime_data",
    ):

        issues.append(
            "missing_runtime_data"
        )

    if not hasattr(
        self,
        "_metadata",
    ):

        issues.append(
            "missing_metadata"
        )

    if not hasattr(
        self,
        "_callbacks",
    ):

        issues.append(
            "missing_callbacks"
        )

    if not hasattr(
        self,
        "_hooks",
    ):

        issues.append(
            "missing_hooks"
        )

    if not hasattr(
        self,
        "_statistics",
    ):

        issues.append(
            "missing_statistics"
        )

    #
    # ------------------------------------------------------------------
    # Overall status
    # ------------------------------------------------------------------
    #

    healthy = (
        len(issues) == 0
    )

    report = {
        "healthy": healthy,
        "status": (
            "healthy"
            if healthy
            else "unhealthy"
        ),
        "issues": tuple(
            issues,
        ),
        "runtime_age": self.runtime_age(),
        "callback_count": len(
            getattr(
                self,
                "_callbacks",
                {},
            )
        ),
        "hook_count": len(
            getattr(
                self,
                "_hooks",
                {},
            )
        ),
        "timestamp": now,
    }

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    self._history.append(
        {
            "event": "health",
            "healthy": healthy,
            "timestamp": now,
        }
    )

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    self._statistics.update_count += 1
    self._statistics.updated_at = now

    if (
        not healthy
        and hasattr(
            self._statistics,
            "warning_count",
        )
    ):

        self._statistics.warning_count += 1

    #
    # ------------------------------------------------------------------
    # Logger
    # ------------------------------------------------------------------
    #

    if healthy:

        self._logger.debug(
            "Runtime health check passed."
        )

    else:

        self._logger.warning(
            "Runtime health check failed: %s",
            issues,
        )

    #
    # ------------------------------------------------------------------
    # Return
    # ------------------------------------------------------------------
    #

    return report
# ==============================================================================
# Part 16.15 – api_summary()
# ==============================================================================

def api_summary(
    self,
):
    """
    Return a summary of the public SpanScope API.

    Returns
    -------
    dict
        Public API summary.
    """

    #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    self.validate()

    now = time.time()

    #
    # ------------------------------------------------------------------
    # API groups
    # ------------------------------------------------------------------
    #

    api = {
        "mapping": (
            "get",
            "set",
            "remove",
            "update",
            "exists",
            "keys",
            "values",
            "items",
            "merge",
            "apply",
        ),
        "runtime": (
            "execute",
            "inspect",
            "status",
            "health",
        ),
        "utilities": (
            "snapshot",
            "restore",
            "clone",
            "copy",
            "clear",
            "reset_runtime",
            "cleanup",
            "diagnostics",
            "summary",
        ),
        "serialization": (
            "to_dict",
            "from_dict",
            "serialize",
            "deserialize",
            "to_json",
            "from_json",
            "to_yaml",
            "from_yaml",
            "save",
            "load",
        ),
        "callbacks": (
            "register_callback",
            "unregister_callback",
            "invoke_callback",
            "invoke_all_callbacks",
        ),
        "hooks": (
            "register_hook",
            "unregister_hook",
            "invoke_hook",
            "invoke_all_hooks",
        ),
        "python_protocols": (
            "__repr__",
            "__str__",
            "__len__",
            "__iter__",
            "__contains__",
            "__getitem__",
            "__setitem__",
            "__delitem__",
            "__call__",
            "__bool__",
            "__eq__",
            "__hash__",
            "__copy__",
            "__deepcopy__",
            "__enter__",
            "__exit__",
        ),
    }

    #
    # ------------------------------------------------------------------
    # Build report
    # ------------------------------------------------------------------
    #

    total_methods = sum(
        len(group)
        for group in api.values()
    )

    report = {
        "class": self.__class__.__name__,
        "version": getattr(
            self,
            "__version__",
            "unknown",
        ),
        "groups": api,
        "group_count": len(api),
        "method_count": total_methods,
        "generated_at": now,
    }

    #
    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    #

    self._history.append(
        {
            "event": "api_summary",
            "timestamp": now,
        }
    )

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    self._statistics.update_count += 1
    self._statistics.updated_at = now

    #
    # ------------------------------------------------------------------
    # Logger
    # ------------------------------------------------------------------
    #

    self._logger.debug(
        "Public API summary generated."
    )

    #
    # ------------------------------------------------------------------
    # Return
    # ------------------------------------------------------------------
    #

    return report                                                                                                                                                                                                                                                                                                                                                                                                        
# ==============================================================================
# Part 1. Foundation
# ==============================================================================

from __future__ import annotations

# ==============================================================================
# Imports
# ==============================================================================

import copy
import json
import threading
import time
import uuid

from collections import deque
from dataclasses import (
    asdict,
    dataclass,
    field,
)
from enum import Enum
from pathlib import Path
from types import TracebackType
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

from .context import TraceContext
from .manager import TraceManager
from .processor import TraceProcessor
from .sampler import TraceSampler
from .trace import TraceTracer

# ==============================================================================
# Constants
# ==============================================================================

DEFAULT_PROVIDER_NAME = "TraceProvider"

DEFAULT_PROVIDER_DESCRIPTION = (
    "SciOS-NG Tracing Provider"
)

DEFAULT_PROVIDER_VERSION = "0.1.0"

DEFAULT_HISTORY_LIMIT = 1000

DEFAULT_TIMEOUT = 30.0

DEFAULT_ENCODING = "utf-8"

DEFAULT_MAX_TRACERS = 1024

DEFAULT_CACHE_SIZE = 256

# ==============================================================================
# Type Aliases
# ==============================================================================

ProviderCallback: TypeAlias = Callable[
    ...,
    Any,
]

ProviderHook: TypeAlias = Callable[
    ...,
    Any,
]

ProviderId: TypeAlias = str

ProviderOptions: TypeAlias = Dict[
    str,
    Any,
]

MetadataDict: TypeAlias = Dict[
    str,
    Any,
]

# ==============================================================================
# Exceptions
# ==============================================================================

class TraceProviderError(RuntimeError):
    """
    Base exception for TraceProvider.
    """


class ProviderValidationError(
    TraceProviderError,
):
    """
    Provider validation failed.
    """


class ProviderStateError(
    TraceProviderError,
):
    """
    Invalid runtime state.
    """


class TracerRegistrationError(
    TraceProviderError,
):
    """
    Tracer registration error.
    """


# ==============================================================================
# Enums
# ==============================================================================

class ProviderType(str, Enum):
    """
    Provider implementation.
    """

    DEFAULT = "default"

    LOCAL = "local"

    GLOBAL = "global"

    DISTRIBUTED = "distributed"

    CUSTOM = "custom"


class ProviderState(str, Enum):
    """
    Runtime state.
    """

    CREATED = "created"

    INITIALIZED = "initialized"

    RUNNING = "running"

    IDLE = "idle"

    FROZEN = "frozen"

    CLOSED = "closed"

    ERROR = "error"

# ==============================================================================
# Provider Capability
# ==============================================================================


class ProviderCapability(str, Enum):
    """
    Trace provider capability registry.

    Defines supported runtime features.
    """

    PROVIDER = "provider"

    TRACING = "tracing"

    MULTIPLE_TRACERS = "multiple-tracers"

    MANAGEMENT = "management"

    SERIALIZATION = "serialization"

    CALLBACKS = "callbacks"

    HOOKS = "hooks"

    SNAPSHOT = "snapshot"

    DIAGNOSTICS = "diagnostics"

    EXPORT = "export"

    METRICS = "metrics"

    CONTEXT = "context"
# ==============================================================================
# Dataclasses
# ==============================================================================

@dataclass(slots=True)
class ProviderStatistics:
    """
    Runtime statistics.
    """

    tracer_count: int = 0

    active_tracer_count: int = 0

    trace_count: int = 0

    span_count: int = 0

    exporter_count: int = 0

    error_count: int = 0

    callback_count: int = 0

    hook_count: int = 0

    validation_count: int = 0

    update_count: int = 0

    created_at: float = field(
        default_factory=time.time,
    )

    updated_at: float = field(
        default_factory=time.time,
    )


@dataclass(slots=True)
class ProviderSnapshot:
    """
    Serializable provider snapshot.
    """

    identity: Dict[str, Any]

    configuration: Dict[str, Any]

    runtime: Dict[str, Any]

    statistics: Dict[str, Any]

    tracers: List[Dict[str, Any]]

    metadata: Dict[str, Any]


@dataclass(slots=True)
class ProviderReport:
    """
    Provider diagnostics report.
    """

    name: str

    provider_type: str

    version: str

    runtime_state: str

    tracer_count: int

    trace_count: int

    span_count: int

    success_rate: float

    failure_rate: float

    uptime: float
# ==============================================================================
# Provider Capability Enum
# ==============================================================================


class ProviderCapability(str, Enum):
    """
    Capabilities supported by TraceProvider.

    Used for runtime feature discovery.
    """


    TRACING = "tracing"


    MULTIPLE_TRACERS = (
        "multiple-tracers"
    )


    MANAGEMENT = (
        "management"
    )


    SERIALIZATION = (
        "serialization"
    )


    CALLBACKS = (
        "callbacks"
    )


    HOOKS = (
        "hooks"
    )


    SNAPSHOT = (
        "snapshot"
    )


    DIAGNOSTICS = (
        "diagnostics"
    )


    EXPORTING = (
        "exporting"
    )


    PROCESSING = (
        "processing"
    )    
# ==============================================================================
# Part 2. Constructor
# ==============================================================================


# ==============================================================================
# Main Provider Declaration
# ==============================================================================


class TraceProvider:
    """
    SciOS-NG Runtime Trace Provider.

    Central runtime registry and lifecycle
    manager for tracing components.
    """


    def __init__(
        self,
        *,
        # ------------------------------------------------------------------
        # Identity
        # ------------------------------------------------------------------

        name: str = DEFAULT_PROVIDER_NAME,

        description: str = DEFAULT_PROVIDER_DESCRIPTION,

        version: str = DEFAULT_PROVIDER_VERSION,

        provider_type: ProviderType = ProviderType.DEFAULT,


        # ------------------------------------------------------------------
        # Components
        # ------------------------------------------------------------------

        manager: Optional[TraceManager] = None,

        sampler: Optional[TraceSampler] = None,

        processor: Optional[TraceProcessor] = None,

        context: Optional[TraceContext] = None,

        exporters: Optional[Iterable[Any]] = None,

        tracers: Optional[Iterable["TraceTracer"]] = None,


        # ------------------------------------------------------------------
        # Configuration
        # ------------------------------------------------------------------

        enabled: bool = True,

        auto_initialize: bool = True,

        auto_shutdown: bool = True,

        default_tracer: Optional[str] = None,

        history_limit: int = DEFAULT_HISTORY_LIMIT,

        timeout: float = DEFAULT_TIMEOUT,

        encoding: str = DEFAULT_ENCODING,

        options: Optional[Mapping[str, Any]] = None,

        metadata: Optional[Mapping[str, Any]] = None,

    ) -> None:
        """
        Initialize TraceProvider.
        """


        # ==================================================================
        # Identity
        # ==================================================================

        self._id: ProviderId = uuid.uuid4().hex

        self._uuid: uuid.UUID = uuid.uuid4()


        self._name: str = str(name)

        self._description: str = str(description)

        self._version: str = str(version)


        if isinstance(
            provider_type,
            ProviderType,
        ):

            self._provider_type = provider_type

        else:

            self._provider_type = ProviderType(
                provider_type
            )


        # ==================================================================
        # Validation
        # ==================================================================

        if history_limit <= 0:

            raise ValueError(
                "history_limit must be > 0"
            )


        if timeout <= 0:

            raise ValueError(
                "timeout must be > 0"
            )


        # ==================================================================
        # Components
        # ==================================================================

        self._manager = (
            manager
            if manager is not None
            else TraceManager()
        )


        self._sampler = (
            sampler
            if sampler is not None
            else TraceSampler()
        )


        self._processor = (
            processor
            if processor is not None
            else TraceProcessor()
        )


        self._context = (
            context
            if context is not None
            else TraceContext()
        )


        self._exporters: List[Any] = list(
            exporters or []
        )


        # ------------------------------------------------------------------
        # Tracer registry
        # ------------------------------------------------------------------

        self._tracers: Dict[
            str,
            "TraceTracer",
        ] = {}


        if tracers:

            for tracer in tracers:

                self._tracers[
                    tracer.name
                ] = tracer



        self._active_tracer = None



        if default_tracer:

            if default_tracer not in self._tracers:

                raise KeyError(
                    f"Unknown tracer: {default_tracer}"
                )


            self._active_tracer = (
                self._tracers[
                    default_tracer
                ]
            )


        elif self._tracers:

            self._active_tracer = next(
                iter(
                    self._tracers.values()
                )
            )



        # ==================================================================
        # Configuration
        # ==================================================================

        self._enabled = bool(enabled)

        self._auto_initialize = bool(
            auto_initialize
        )

        self._auto_shutdown = bool(
            auto_shutdown
        )


        self._default_tracer = (
            default_tracer
        )


        self._history_limit = int(
            history_limit
        )


        self._timeout = float(
            timeout
        )


        self._encoding = str(
            encoding
        )


        self._options = dict(
            options or {}
        )


        self._capabilities: Set[str] = {

    capability.value

    for capability in ProviderCapability

}


        # ==================================================================
        # Runtime State
        # ==================================================================

        self._initialized = False

        self._running = False

        self._active = False

        self._frozen = False

        self._closed = False


        self._state = (
            ProviderState.CREATED
        )


        now = time.time()


        self._created_at = now

        self._updated_at = now

        self._last_activity = now



        # ==================================================================
        # Statistics
        # ==================================================================

        self._statistics = ProviderStatistics()


        self._statistics.tracer_count = len(
            self._tracers
        )


        self._statistics.exporter_count = len(
            self._exporters
        )


        self._statistics.active_tracer_count = (

            1

            if self._active_tracer

            else 0

        )



        # ==================================================================
        # Metadata
        # ==================================================================

        self._metadata = dict(
            metadata or {}
        )


        self._tags: Set[str] = set()


        self._context_data = {}


        self._history = deque(
            maxlen=self._history_limit
        )


        self._cache = {}


        self._callbacks = []


        self._hooks = {}


        self._filters = []



        # ==================================================================
        # Runtime Objects
        # ==================================================================

        self._lock = threading.RLock()


        self._condition = threading.Condition(
            self._lock
        )


        self._shutdown_event = (
            threading.Event()
        )


        self._local = threading.local()


        self._start_timestamp = now



        # ==================================================================
        # Auto Initialize
        # ==================================================================

        if self._auto_initialize:

            initializer = getattr(
                self,
                "initialize",
                None,
            )


            if callable(initializer):

                initializer()
# ==============================================================================
# Part 3.1. Identity Properties
# ==============================================================================


# ------------------------------------------------------------------------------
# id
# ------------------------------------------------------------------------------

@property
def id(self) -> ProviderId:
    """
    Unique provider identifier.

    Returns
    -------
    ProviderId
    """

    return self._id



# ------------------------------------------------------------------------------
# uuid
# ------------------------------------------------------------------------------

@property
def uuid(self) -> uuid.UUID:
    """
    Universally unique identifier.

    Returns
    -------
    uuid.UUID
    """

    return self._uuid



# ------------------------------------------------------------------------------
# name
# ------------------------------------------------------------------------------

@property
def name(self) -> str:
    """
    Provider name.

    Returns
    -------
    str
    """

    return self._name



@name.setter
def name(
    self,
    value: str,
) -> None:
    """
    Update provider name.
    """

    value = str(value).strip()


    if not value:

        raise ValueError(
            "Provider name cannot be empty."
        )


    with self._lock:

        self._name = value


        if hasattr(
            self,
            "_statistics",
        ):

            self._statistics.update_count += 1


        self.touch()



# ------------------------------------------------------------------------------
# description
# ------------------------------------------------------------------------------

@property
def description(self) -> str:
    """
    Provider description.

    Returns
    -------
    str
    """

    return self._description



@description.setter
def description(
    self,
    value: str,
) -> None:
    """
    Update provider description.
    """

    value = str(value).strip()


    with self._lock:

        self._description = value


        if hasattr(
            self,
            "_statistics",
        ):

            self._statistics.update_count += 1


        self.touch()



# ------------------------------------------------------------------------------
# version
# ------------------------------------------------------------------------------

@property
def version(self) -> str:
    """
    Provider version.

    Returns
    -------
    str
    """

    return self._version



@version.setter
def version(
    self,
    value: str,
) -> None:
    """
    Update provider version.
    """

    value = str(value).strip()


    if not value:

        raise ValueError(
            "Provider version cannot be empty."
        )


    with self._lock:

        self._version = value


        if hasattr(
            self,
            "_statistics",
        ):

            self._statistics.update_count += 1


        self.touch()



# ------------------------------------------------------------------------------
# provider_type
# ------------------------------------------------------------------------------

@property
def provider_type(self) -> ProviderType:
    """
    Provider implementation type.

    Returns
    -------
    ProviderType
    """

    return self._provider_type



@provider_type.setter
def provider_type(
    self,
    value: ProviderType,
) -> None:
    """
    Update provider type.
    """


    if not isinstance(
        value,
        ProviderType,
    ):

        value = ProviderType(
            str(value)
        )


    with self._lock:

        self._provider_type = value


        if hasattr(
            self,
            "_statistics",
        ):

            self._statistics.update_count += 1


        self.touch()
# ==============================================================================
# Part 3.2. Components Properties
# ==============================================================================


# ------------------------------------------------------------------------------
# manager
# ------------------------------------------------------------------------------

@property
def manager(
    self,
) -> TraceManager:
    """
    Return trace manager.
    """

    return self._manager



@manager.setter
def manager(
    self,
    value: TraceManager,
) -> None:
    """
    Replace trace manager.
    """

    if not isinstance(
        value,
        TraceManager,
    ):
        raise TypeError(
            "manager must be TraceManager."
        )


    with self._lock:

        self._manager = value

        self._touch_update()



# ------------------------------------------------------------------------------
# sampler
# ------------------------------------------------------------------------------

@property
def sampler(
    self,
) -> TraceSampler:
    """
    Return trace sampler.
    """

    return self._sampler



@sampler.setter
def sampler(
    self,
    value: TraceSampler,
) -> None:
    """
    Replace trace sampler.
    """

    if not isinstance(
        value,
        TraceSampler,
    ):
        raise TypeError(
            "sampler must be TraceSampler."
        )


    with self._lock:

        self._sampler = value

        self._touch_update()



# ------------------------------------------------------------------------------
# processor
# ------------------------------------------------------------------------------

@property
def processor(
    self,
) -> TraceProcessor:
    """
    Return trace processor.
    """

    return self._processor



@processor.setter
def processor(
    self,
    value: TraceProcessor,
) -> None:
    """
    Replace trace processor.
    """

    if not isinstance(
        value,
        TraceProcessor,
    ):
        raise TypeError(
            "processor must be TraceProcessor."
        )


    with self._lock:

        self._processor = value

        self._touch_update()



# ------------------------------------------------------------------------------
# exporters
# ------------------------------------------------------------------------------

@property
def exporters(
    self,
) -> Tuple[Any, ...]:
    """
    Return registered exporters.
    """

    return tuple(
        self._exporters
    )



@exporters.setter
def exporters(
    self,
    value: Iterable[Any],
) -> None:
    """
    Replace exporter collection.
    """

    if value is None:

        value = []


    with self._lock:

        self._exporters = list(value)


        if hasattr(
            self,
            "_statistics",
        ):

            self._statistics.exporter_count = (
                len(self._exporters)
            )


        self._touch_update()



# ------------------------------------------------------------------------------
# tracers
# ------------------------------------------------------------------------------

@property
def tracers(
    self,
) -> Mapping[str, "TraceTracer"]:
    """
    Return tracer registry.

    Returns immutable view.
    """

    return dict(
        self._tracers
    )



@tracers.setter
def tracers(
    self,
    value: Mapping[str, "TraceTracer"],
) -> None:
    """
    Replace tracer registry.
    """

    registry: Dict[
        str,
        "TraceTracer",
    ] = {}


    for name, tracer in value.items():

        if not isinstance(
            tracer,
            TraceTracer,
        ):
            raise TypeError(
                f"{name!r} must be TraceTracer."
            )


        registry[str(name)] = tracer



    with self._lock:

        self._tracers = registry


        if (
            self._active_tracer is not None
            and
            self._active_tracer.name
            not in registry
        ):

            self._active_tracer = None



        self._sync_tracer_statistics()

        self._touch_update()



# ------------------------------------------------------------------------------
# active_tracer
# ------------------------------------------------------------------------------

@property
def active_tracer(
    self,
) -> Optional["TraceTracer"]:
    """
    Return active tracer.
    """

    return self._active_tracer



@active_tracer.setter
def active_tracer(
    self,
    value: Optional["TraceTracer"],
) -> None:
    """
    Set active tracer.
    """

    if (
        value is not None
        and not isinstance(
            value,
            TraceTracer,
        )
    ):
        raise TypeError(
            "active_tracer must be TraceTracer or None."
        )



    with self._lock:

        if value is not None:

            self._tracers[
                value.name
            ] = value



        self._active_tracer = value


        self._default_tracer = (

            value.name

            if value is not None

            else None

        )


        self._sync_tracer_statistics()

        self._touch_update()



# ------------------------------------------------------------------------------
# context
# ------------------------------------------------------------------------------

@property
def context(
    self,
) -> TraceContext:
    """
    Return trace context.
    """

    return self._context



@context.setter
def context(
    self,
    value: TraceContext,
) -> None:
    """
    Replace trace context.
    """

    if not isinstance(
        value,
        TraceContext,
    ):
        raise TypeError(
            "context must be TraceContext."
        )


    with self._lock:

        self._context = value

        self._touch_update()
# ==============================================================================
# Part 3.3. Configuration Properties
# ==============================================================================


# ------------------------------------------------------------------------------
# enabled
# ------------------------------------------------------------------------------

@property
def enabled(
    self,
) -> bool:
    """
    Whether provider is enabled.
    """

    return self._enabled



@enabled.setter
def enabled(
    self,
    value: bool,
) -> None:
    """
    Enable or disable provider.
    """

    with self._lock:

        self._enabled = bool(value)

        self._touch_update()



# ------------------------------------------------------------------------------
# auto_initialize
# ------------------------------------------------------------------------------

@property
def auto_initialize(
    self,
) -> bool:
    """
    Automatically initialize provider.
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

        self._auto_initialize = bool(value)

        self._touch_update()



# ------------------------------------------------------------------------------
# auto_shutdown
# ------------------------------------------------------------------------------

@property
def auto_shutdown(
    self,
) -> bool:
    """
    Automatically shutdown provider.
    """

    return self._auto_shutdown



@auto_shutdown.setter
def auto_shutdown(
    self,
    value: bool,
) -> None:
    """
    Configure automatic shutdown.
    """

    with self._lock:

        self._auto_shutdown = bool(value)

        self._touch_update()



# ------------------------------------------------------------------------------
# default_tracer
# ------------------------------------------------------------------------------

@property
def default_tracer(
    self,
) -> Optional[str]:
    """
    Name of default tracer.
    """

    return self._default_tracer



@default_tracer.setter
def default_tracer(
    self,
    value: Optional[str],
) -> None:
    """
    Select default tracer.
    """

    with self._lock:

        if value is None:

            self._default_tracer = None

            self._active_tracer = None


        else:

            value = str(value).strip()


            if value not in self._tracers:

                raise KeyError(
                    f"Unknown tracer: {value!r}"
                )


            self._default_tracer = value

            self._active_tracer = (
                self._tracers[value]
            )


        self._sync_tracer_statistics()

        self._touch_update()



# ------------------------------------------------------------------------------
# history_limit
# ------------------------------------------------------------------------------

@property
def history_limit(
    self,
) -> int:
    """
    Maximum history capacity.
    """

    return self._history_limit



@history_limit.setter
def history_limit(
    self,
    value: int,
) -> None:
    """
    Resize history buffer.
    """

    value = int(value)


    if value <= 0:

        raise ValueError(
            "history_limit must be positive."
        )


    with self._lock:

        self._history_limit = value


        self._history = deque(
            self._history,
            maxlen=value,
        )


        self._touch_update()



# ------------------------------------------------------------------------------
# timeout
# ------------------------------------------------------------------------------

@property
def timeout(
    self,
) -> float:
    """
    Processing timeout seconds.
    """

    return self._timeout



@timeout.setter
def timeout(
    self,
    value: float,
) -> None:
    """
    Update processing timeout.
    """

    value = float(value)


    if value <= 0:

        raise ValueError(
            "timeout must be greater than zero."
        )


    with self._lock:

        self._timeout = value

        self._touch_update()



# ------------------------------------------------------------------------------
# encoding
# ------------------------------------------------------------------------------

@property
def encoding(
    self,
) -> str:
    """
    Serialization encoding.
    """

    return self._encoding



@encoding.setter
def encoding(
    self,
    value: str,
) -> None:
    """
    Update serialization encoding.
    """

    value = str(value).strip()


    if not value:

        raise ValueError(
            "encoding cannot be empty."
        )


    with self._lock:

        self._encoding = value

        self._touch_update()



# ------------------------------------------------------------------------------
# options
# ------------------------------------------------------------------------------

@property
def options(
    self,
) -> Dict[str, Any]:
    """
    Provider options.

    Returns copy.
    """

    return dict(
        self._options
    )



@options.setter
def options(
    self,
    value: Mapping[str, Any],
) -> None:
    """
    Replace provider options.
    """

    if value is None:

        value = {}


    with self._lock:

        self._options = dict(value)

        self._touch_update()



# ------------------------------------------------------------------------------
# capabilities
# ------------------------------------------------------------------------------

@property
def capabilities(
    self,
) -> frozenset[str]:
    """
    Supported provider capabilities.
    """

    return frozenset(
        self._capabilities
    )



@capabilities.setter
def capabilities(
    self,
    value: Iterable[str],
) -> None:
    """
    Replace provider capabilities.
    """

    if value is None:

        value = []


    with self._lock:

        self._capabilities = {

            str(item).strip()

            for item in value

            if str(item).strip()

        }


        self._touch_update()
# ==============================================================================
# Part 3.4. Runtime Properties
# ==============================================================================


# ------------------------------------------------------------------------------
# initialized
# ------------------------------------------------------------------------------

@property
def initialized(self) -> bool:
    """
    Whether provider initialization completed.
    """
    return self._initialized


@initialized.setter
def initialized(
    self,
    value: bool,
) -> None:

    new_value = bool(value)

    if self._initialized != new_value:

        self._initialized = new_value

        self._statistics.update_count += 1

        self.touch()


# ------------------------------------------------------------------------------
# running
# ------------------------------------------------------------------------------

@property
def running(self) -> bool:
    """
    Whether provider runtime loop is running.
    """
    return self._running


@running.setter
def running(
    self,
    value: bool,
) -> None:

    new_value = bool(value)

    if self._running != new_value:

        self._running = new_value

        self._statistics.update_count += 1

        self.touch()


# ------------------------------------------------------------------------------
# active
# ------------------------------------------------------------------------------

@property
def active(self) -> bool:
    """
    Whether provider is currently active.
    """
    return self._active


@active.setter
def active(
    self,
    value: bool,
) -> None:

    new_value = bool(value)

    if self._active != new_value:

        self._active = new_value

        self._statistics.update_count += 1

        self.touch()


# ------------------------------------------------------------------------------
# frozen
# ------------------------------------------------------------------------------

@property
def frozen(self) -> bool:
    """
    Whether provider configuration is frozen.
    """
    return self._frozen


@frozen.setter
def frozen(
    self,
    value: bool,
) -> None:

    new_value = bool(value)

    if self._frozen != new_value:

        self._frozen = new_value

        self._statistics.update_count += 1

        self.touch()


# ------------------------------------------------------------------------------
# closed
# ------------------------------------------------------------------------------

@property
def closed(self) -> bool:
    """
    Whether provider has been permanently closed.
    """
    return self._closed


@closed.setter
def closed(
    self,
    value: bool,
) -> None:

    new_value = bool(value)

    if new_value and self._closed:

        return

    self._closed = new_value


    if new_value:

        self._running = False

        self._active = False

        self._state = ProviderState.CLOSED


    self._statistics.update_count += 1

    self.touch()



# ------------------------------------------------------------------------------
# state
# ------------------------------------------------------------------------------

@property
def state(self) -> ProviderState:
    """
    Current provider lifecycle state.
    """
    return self._state


@state.setter
def state(
    self,
    value: ProviderState,
) -> None:

    if not isinstance(
        value,
        ProviderState,
    ):

        value = ProviderState(value)


    if self._state != value:

        self._state = value

        self._statistics.update_count += 1

        self.touch()



# ------------------------------------------------------------------------------
# created_at
# ------------------------------------------------------------------------------

@property
def created_at(self) -> float:
    """
    Provider creation timestamp.
    """
    return self._created_at



# ------------------------------------------------------------------------------
# updated_at
# ------------------------------------------------------------------------------

@property
def updated_at(self) -> float:
    """
    Last modification timestamp.
    """
    return self._updated_at



# ------------------------------------------------------------------------------
# last_activity
# ------------------------------------------------------------------------------

@property
def last_activity(self) -> float:
    """
    Last runtime activity timestamp.
    """
    return self._last_activity


@last_activity.setter
def last_activity(
    self,
    value: float,
) -> None:

    self._last_activity = float(value)



# ------------------------------------------------------------------------------
# uptime
# ------------------------------------------------------------------------------

@property
def uptime(self) -> float:
    """
    Provider uptime in seconds.
    """

    if self._closed:

        return max(
            0.0,
            self._updated_at - self._created_at,
        )


    return max(
        0.0,
        time.time() - self._created_at,
    )
# ==============================================================================
# Part 3.5. Statistics Properties
# ==============================================================================


# ------------------------------------------------------------------------------
# statistics
# ------------------------------------------------------------------------------

@property
def statistics(self) -> ProviderStatistics:
    """
    Return provider statistics snapshot.

    Returns
    -------
    ProviderStatistics
    """
    return self._statistics



# ------------------------------------------------------------------------------
# tracer_count
# ------------------------------------------------------------------------------

@property
def tracer_count(self) -> int:
    """
    Number of registered tracers.

    Returns
    -------
    int
    """

    return len(
        self._tracers
    )



# ------------------------------------------------------------------------------
# active_tracer_count
# ------------------------------------------------------------------------------

@property
def active_tracer_count(self) -> int:
    """
    Number of active tracers.

    Returns
    -------
    int
    """

    return (
        1
        if self._active_tracer is not None
        else 0
    )



# ------------------------------------------------------------------------------
# trace_count
# ------------------------------------------------------------------------------

@property
def trace_count(self) -> int:
    """
    Total processed traces.

    Returns
    -------
    int
    """

    if self._manager is None:

        return int(
            self._statistics.trace_count
        )


    value = getattr(
        self._manager,
        "trace_count",
        self._statistics.trace_count,
    )


    try:

        return int(value)

    except (
        TypeError,
        ValueError,
    ):

        return int(
            self._statistics.trace_count
        )



# ------------------------------------------------------------------------------
# span_count
# ------------------------------------------------------------------------------

@property
def span_count(self) -> int:
    """
    Total processed spans.

    Returns
    -------
    int
    """

    if self._manager is None:

        return int(
            self._statistics.span_count
        )


    value = getattr(
        self._manager,
        "span_count",
        self._statistics.span_count,
    )


    try:

        return int(value)

    except (
        TypeError,
        ValueError,
    ):

        return int(
            self._statistics.span_count
        )



# ------------------------------------------------------------------------------
# exporter_count
# ------------------------------------------------------------------------------

@property
def exporter_count(self) -> int:
    """
    Number of registered exporters.

    Returns
    -------
    int
    """

    return len(
        self._exporters
    )



# ------------------------------------------------------------------------------
# error_count
# ------------------------------------------------------------------------------

@property
def error_count(self) -> int:
    """
    Total provider errors.

    Returns
    -------
    int
    """

    return int(
        self._statistics.error_count
    )



# ------------------------------------------------------------------------------
# total_operation_count
# ------------------------------------------------------------------------------

@property
def total_operation_count(self) -> int:
    """
    Total successful and failed operations.

    Returns
    -------
    int
    """

    return (
        self.trace_count
        +
        self.error_count
    )



# ------------------------------------------------------------------------------
# success_rate
# ------------------------------------------------------------------------------

@property
def success_rate(self) -> float:
    """
    Provider success rate.

    Returns
    -------
    float
    """

    total = self.total_operation_count


    if total <= 0:

        return 1.0


    return min(
        1.0,
        max(
            0.0,
            self.trace_count / total,
        ),
    )



# ------------------------------------------------------------------------------
# failure_rate
# ------------------------------------------------------------------------------

@property
def failure_rate(self) -> float:
    """
    Provider failure rate.

    Returns
    -------
    float
    """

    total = self.total_operation_count


    if total <= 0:

        return 0.0


    return min(
        1.0,
        max(
            0.0,
            self.error_count / total,
        ),
    )
# ==============================================================================
# Part 3.6. Metadata Properties
# ==============================================================================


# ------------------------------------------------------------------------------
# metadata
# ------------------------------------------------------------------------------

@property
def metadata(self) -> Dict[str, Any]:
    """
    Provider metadata snapshot.

    Returns
    -------
    Dict[str, Any]
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
    Replace provider metadata.
    """

    if value is None:

        value = {}


    new_value = dict(value)


    if self._metadata != new_value:

        self._metadata = new_value

        self._statistics.update_count += 1

        self.touch()



# ------------------------------------------------------------------------------
# tags
# ------------------------------------------------------------------------------

@property
def tags(self) -> Set[str]:
    """
    Provider tags snapshot.

    Returns
    -------
    Set[str]
    """

    return set(
        self._tags
    )


@tags.setter
def tags(
    self,
    value: Iterable[str],
) -> None:
    """
    Replace provider tags.
    """

    if value is None:

        value = ()


    new_tags = {

        str(tag).strip().lower()

        for tag in value

        if str(tag).strip()

    }


    if self._tags != new_tags:

        self._tags = new_tags

        self._statistics.update_count += 1

        self.touch()



# ------------------------------------------------------------------------------
# context_data
# ------------------------------------------------------------------------------

@property
def context_data(self) -> Dict[str, Any]:
    """
    Runtime context data snapshot.
    """

    return dict(
        self._context_data
    )


@context_data.setter
def context_data(
    self,
    value: Mapping[str, Any],
) -> None:
    """
    Replace context data.
    """

    if value is None:

        value = {}


    new_value = dict(value)


    if self._context_data != new_value:

        self._context_data = new_value

        self._statistics.update_count += 1

        self.touch()



# ------------------------------------------------------------------------------
# history
# ------------------------------------------------------------------------------

@property
def history(self) -> Deque[Any]:
    """
    Provider history snapshot.
    """

    return deque(
        self._history,
        maxlen=self._history_limit,
    )


@history.setter
def history(
    self,
    value: Iterable[Any],
) -> None:
    """
    Replace history buffer.
    """

    if value is None:

        value = ()


    new_history = deque(
        value,
        maxlen=self._history_limit,
    )


    if list(self._history) != list(new_history):

        self._history = new_history

        self._statistics.update_count += 1

        self.touch()



# ------------------------------------------------------------------------------
# cache
# ------------------------------------------------------------------------------

@property
def cache(self) -> Dict[str, Any]:
    """
    Internal cache snapshot.
    """

    return dict(
        self._cache
    )


@cache.setter
def cache(
    self,
    value: Mapping[str, Any],
) -> None:
    """
    Replace internal cache.
    """

    if value is None:

        value = {}


    new_cache = dict(value)


    if self._cache != new_cache:

        self._cache = new_cache

        self._statistics.update_count += 1

        self.touch()



# ------------------------------------------------------------------------------
# callbacks
# ------------------------------------------------------------------------------

@property
def callbacks(
    self,
) -> Tuple[ProviderCallback, ...]:
    """
    Registered callbacks.

    Returns
    -------
    Tuple
    """

    return tuple(
        self._callbacks
    )


@callbacks.setter
def callbacks(
    self,
    value: Iterable[ProviderCallback],
) -> None:
    """
    Replace callback registry.
    """

    if value is None:

        value = ()


    callbacks = list(value)


    if self._callbacks != callbacks:

        self._callbacks = callbacks

        self._statistics.callback_count = len(
            callbacks
        )

        self._statistics.update_count += 1

        self.touch()



# ------------------------------------------------------------------------------
# hooks
# ------------------------------------------------------------------------------

@property
def hooks(
    self,
) -> Dict[str, Tuple[ProviderHook, ...]]:
    """
    Hook registry snapshot.
    """

    return {

        key: tuple(value)

        for key, value in self._hooks.items()

    }



@hooks.setter
def hooks(
    self,
    value: Mapping[
        str,
        Iterable[ProviderHook],
    ],
) -> None:
    """
    Replace hook registry.
    """

    if value is None:

        value = {}


    registry = {

        str(event): list(items)

        for event, items in value.items()

    }


    if self._hooks != registry:

        self._hooks = registry


        self._statistics.hook_count = sum(
            len(items)
            for items in registry.values()
        )


        self._statistics.update_count += 1

        self.touch()



# ------------------------------------------------------------------------------
# filters
# ------------------------------------------------------------------------------

@property
def filters(self) -> Tuple[Any, ...]:
    """
    Registered filters snapshot.
    """

    return tuple(
        self._filters
    )


@filters.setter
def filters(
    self,
    value: Iterable[Any],
) -> None:
    """
    Replace filter registry.
    """

    if value is None:

        value = ()


    filters = list(value)


    if self._filters != filters:

        self._filters = filters

        self._statistics.update_count += 1

        self.touch()
# ==============================================================================
# Part 4.1. Tracer Management
# ==============================================================================

def create_tracer(
    self,
    name: str,
    *,
    description: str = "",
    version: Optional[str] = None,
    tracer_type: Optional[Any] = None,
    activate: bool = False,
    register: bool = True,
    **kwargs: Any,
) -> TraceTracer:
    """
    Create a new TraceTracer.

    Parameters
    ----------
    name : str
        Tracer name.
    description : str, optional
        Tracer description.
    version : str, optional
        Tracer version.
    tracer_type : Any, optional
        Tracer implementation type.
    activate : bool, default=False
        Make the created tracer the active tracer.
    register : bool, default=True
        Automatically register the tracer.

    Returns
    -------
    TraceTracer
    """

    if not name:
        raise ValueError(
            "Tracer name cannot be empty."
        )

    with self._lock:

        if name in self._tracers:
            raise TracerRegistrationError(
                f"Tracer '{name}' already exists."
            )

        tracer = TraceTracer(
            name=name,
            description=description,
            version=version or self.version,
            manager=self._manager,
            sampler=self._sampler,
            processor=self._processor,
            exporter=self._exporters[0]
            if self._exporters
            else None,
            **kwargs,
        )

        if tracer_type is not None:
            tracer.tracer_type = tracer_type

        if register:
            self._tracers[name] = tracer

        if activate:
            self._active_tracer = tracer
            self._default_tracer = name

        self._statistics.tracer_count = len(
            self._tracers
        )

        self._statistics.active_tracer_count = (
            1 if self._active_tracer else 0
        )

        self._statistics.update_count += 1

        self.touch()

        return tracer


# ------------------------------------------------------------------------------


def get_tracer(
    self,
    name: Optional[str] = None,
) -> Optional[TraceTracer]:
    """
    Return a registered tracer.

    Parameters
    ----------
    name : str, optional
        Tracer name.

    Returns
    -------
    Optional[TraceTracer]
    """

    with self._lock:

        if name is None:
            return self._active_tracer

        return self._tracers.get(name)


# ------------------------------------------------------------------------------


def register_tracer(
    self,
    tracer: TraceTracer,
    *,
    activate: bool = False,
    replace: bool = False,
) -> TraceTracer:
    """
    Register an existing TraceTracer.

    Parameters
    ----------
    tracer : TraceTracer
    activate : bool
    replace : bool

    Returns
    -------
    TraceTracer
    """

    if not isinstance(
        tracer,
        TraceTracer,
    ):
        raise TypeError(
            "Expected TraceTracer."
        )

    with self._lock:

        name = tracer.name

        if (
            name in self._tracers
            and not replace
        ):
            raise TracerRegistrationError(
                f"Tracer '{name}' already registered."
            )

        self._tracers[name] = tracer

        if activate or self._active_tracer is None:

            self._active_tracer = tracer

            self._default_tracer = name

        self._statistics.tracer_count = len(
            self._tracers
        )

        self._statistics.active_tracer_count = (
            1 if self._active_tracer else 0
        )

        self._statistics.update_count += 1

        self.touch()

        return tracer


# ------------------------------------------------------------------------------


def unregister_tracer(
    self,
    name: str,
) -> Optional[TraceTracer]:
    """
    Remove a registered tracer.

    Parameters
    ----------
    name : str

    Returns
    -------
    Optional[TraceTracer]
    """

    with self._lock:

        tracer = self._tracers.pop(
            name,
            None,
        )

        if tracer is None:
            return None

        if self._active_tracer is tracer:

            self._active_tracer = None

            self._default_tracer = None

            if self._tracers:

                self._active_tracer = next(
                    iter(self._tracers.values())
                )

                self._default_tracer = (
                    self._active_tracer.name
                )

        self._statistics.tracer_count = len(
            self._tracers
        )

        self._statistics.active_tracer_count = (
            1 if self._active_tracer else 0
        )

        self._statistics.update_count += 1

        self.touch()

        return tracer
# ==============================================================================
# Part 4.2. Active Tracer
# ==============================================================================

def set_active_tracer(
    self,
    tracer: Union[str, TraceTracer],
) -> TraceTracer:
    """
    Set the active tracer.

    Parameters
    ----------
    tracer : Union[str, TraceTracer]
        Tracer instance or registered tracer name.

    Returns
    -------
    TraceTracer
        Newly activated tracer.

    Raises
    ------
    RuntimeError
        If the provider is closed.
    KeyError
        If the tracer name does not exist.
    TypeError
        If the object is not a TraceTracer.
    """

    if self._closed:
        raise RuntimeError(
            "Provider has been closed."
        )

    with self._lock:

        # --------------------------------------------------------------
        # Resolve tracer
        # --------------------------------------------------------------

        if isinstance(tracer, str):

            if tracer not in self._tracers:

                raise KeyError(
                    f"Unknown tracer: {tracer!r}"
                )

            tracer_obj = self._tracers[tracer]

        else:

            if not isinstance(
                tracer,
                TraceTracer,
            ):
                raise TypeError(
                    "Expected TraceTracer or str."
                )

            tracer_obj = tracer

            if tracer_obj.name not in self._tracers:

                self._tracers[
                    tracer_obj.name
                ] = tracer_obj

        # --------------------------------------------------------------
        # Update active tracer
        # --------------------------------------------------------------

        previous = self._active_tracer

        self._active_tracer = tracer_obj

        self._default_tracer = tracer_obj.name

        self._statistics.tracer_count = len(
            self._tracers
        )

        self._statistics.active_tracer_count = 1

        self._statistics.update_count += 1

        self.touch()

        # --------------------------------------------------------------
        # Hooks
        # --------------------------------------------------------------

        try:

            self.emit_event(
                "tracer_changed",
                previous=previous,
                current=tracer_obj,
            )

        except Exception:

            pass

        return tracer_obj


# ------------------------------------------------------------------------------


def current_tracer(
    self,
    *,
    create: bool = True,
) -> Optional[TraceTracer]:
    """
    Return the current active tracer.

    Parameters
    ----------
    create : bool, default=True
        Automatically create a default tracer when none exists.

    Returns
    -------
    Optional[TraceTracer]
    """

    with self._lock:

        if self._active_tracer is not None:

            return self._active_tracer

        if not create:

            return None

        name = (

            self._default_tracer

            or

            "default"

        )

        tracer = self.create_tracer(

            name=name,

            activate=True,

            register=True,

        )

        return tracer
# ==============================================================================
# Part 4.3. Runtime Operations
# ==============================================================================

def flush(
    self,
    *,
    timeout: Optional[float] = None,
) -> bool:
    """
    Flush all pending tracing data.

    Parameters
    ----------
    timeout : Optional[float]
        Flush timeout.

    Returns
    -------
    bool
        True if every component was flushed successfully.
    """

    if self._closed:
        return False

    timeout = (
        self._timeout
        if timeout is None
        else float(timeout)
    )

    success = True

    with self._lock:

        self.emit_event("before_flush")

        # --------------------------------------------------------------
        # Flush tracers
        # --------------------------------------------------------------

        for tracer in self._tracers.values():

            flush = getattr(
                tracer,
                "flush",
                None,
            )

            if callable(flush):

                try:
                    success &= bool(
                        flush(timeout=timeout)
                    )
                except Exception:
                    self._statistics.error_count += 1
                    success = False

        # --------------------------------------------------------------
        # Flush processor
        # --------------------------------------------------------------

        processor_flush = getattr(
            self._processor,
            "flush",
            None,
        )

        if callable(processor_flush):

            try:
                success &= bool(
                    processor_flush()
                )
            except Exception:
                self._statistics.error_count += 1
                success = False

        # --------------------------------------------------------------
        # Flush exporters
        # --------------------------------------------------------------

        for exporter in self._exporters:

            exporter_flush = getattr(
                exporter,
                "flush",
                None,
            )

            if callable(exporter_flush):

                try:
                    success &= bool(
                        exporter_flush()
                    )
                except Exception:
                    self._statistics.error_count += 1
                    success = False

        self.touch()

        self.emit_event(
            "after_flush",
            success=success,
        )

    return success


# ------------------------------------------------------------------------------


def shutdown(
    self,
    *,
    flush: bool = True,
) -> bool:
    """
    Shutdown the provider.

    Parameters
    ----------
    flush : bool
        Flush before shutdown.

    Returns
    -------
    bool
    """

    if self._closed:
        return True

    with self._lock:

        if flush:

            self.flush()

        # --------------------------------------------------------------
        # Shutdown tracers
        # --------------------------------------------------------------

        for tracer in self._tracers.values():

            shutdown_fn = getattr(
                tracer,
                "shutdown",
                None,
            )

            if callable(shutdown_fn):

                try:
                    shutdown_fn()
                except Exception:
                    self._statistics.error_count += 1

        # --------------------------------------------------------------
        # Shutdown processor
        # --------------------------------------------------------------

        processor_shutdown = getattr(
            self._processor,
            "shutdown",
            None,
        )

        if callable(processor_shutdown):

            try:
                processor_shutdown()
            except Exception:
                self._statistics.error_count += 1

        self._running = False
        self._active = False
        self._initialized = False
        self._closed = True
        self._state = ProviderState.CLOSED

        self._shutdown_event.set()

        self.touch()

    return True


# ------------------------------------------------------------------------------


def clear(self) -> None:
    """
    Clear runtime objects without removing configuration.
    """

    with self._lock:

        self._history.clear()

        self._cache.clear()

        self._context_data.clear()

        self._callbacks.clear()

        self._hooks.clear()

        self._filters.clear()

        self._active_tracer = None

        self._default_tracer = None

        self._statistics.active_tracer_count = 0

        self._statistics.update_count += 1

        self.touch()


# ------------------------------------------------------------------------------


def reset(self) -> None:
    """
    Reset provider to its initial runtime state.
    """

    with self._lock:

        self.clear()

        self._statistics = ProviderStatistics()

        self._statistics.tracer_count = len(
            self._tracers
        )

        self._statistics.exporter_count = len(
            self._exporters
        )

        self._initialized = False

        self._running = False

        self._active = False

        self._frozen = False

        self._closed = False

        self._state = ProviderState.CREATED

        self._shutdown_event.clear()

        now = time.time()

        self._created_at = now

        self._updated_at = now

        self._last_activity = now

        self._start_timestamp = now

        self.touch()
# ==============================================================================
# Part 5.1. Snapshot
# ==============================================================================

def snapshot(
    self,
    *,
    include_runtime: bool = True,
    include_statistics: bool = True,
    include_metadata: bool = True,
    deep: bool = True,
) -> Dict[str, Any]:
    """
    Create a snapshot of the provider state.

    Parameters
    ----------
    include_runtime : bool, default=True
        Include runtime state.
    include_statistics : bool, default=True
        Include statistics.
    include_metadata : bool, default=True
        Include metadata.
    deep : bool, default=True
        Perform deep copy.

    Returns
    -------
    Dict[str, Any]
        Serializable provider snapshot.
    """

    with self._lock:

        copier = deepcopy if deep else copy

        snapshot: Dict[str, Any] = {
            "identity": {
                "id": self._id,
                "uuid": str(self._uuid),
                "name": self._name,
                "description": self._description,
                "version": self._version,
                "provider_type": self._provider_type.value,
            },
            "configuration": {
                "enabled": self._enabled,
                "auto_initialize": self._auto_initialize,
                "auto_shutdown": self._auto_shutdown,
                "default_tracer": self._default_tracer,
                "history_limit": self._history_limit,
                "timeout": self._timeout,
                "encoding": self._encoding,
                "options": copier(self._options),
                "capabilities": list(self._capabilities),
            },
            "components": {
                "tracers": list(self._tracers.keys()),
                "active_tracer": (
                    self._active_tracer.name
                    if self._active_tracer
                    else None
                ),
                "exporter_count": len(self._exporters),
            },
        }

        if include_runtime:

            snapshot["runtime"] = {
                "initialized": self._initialized,
                "running": self._running,
                "active": self._active,
                "frozen": self._frozen,
                "closed": self._closed,
                "state": self._state.value,
                "created_at": self._created_at,
                "updated_at": self._updated_at,
                "last_activity": self._last_activity,
            }

        if include_statistics:

            if hasattr(
                self._statistics,
                "to_dict",
            ):
                snapshot["statistics"] = (
                    self._statistics.to_dict()
                )
            else:
                snapshot["statistics"] = copier(
                    vars(self._statistics)
                )

        if include_metadata:

            snapshot["metadata"] = {
                "metadata": copier(
                    self._metadata
                ),
                "tags": list(
                    self._tags
                ),
                "context_data": copier(
                    self._context_data
                ),
                "history": list(
                    self._history
                ),
                "cache": copier(
                    self._cache
                ),
            }

        return snapshot


# ------------------------------------------------------------------------------


def restore(
    self,
    snapshot: Mapping[str, Any],
) -> "TraceProvider":
    """
    Restore provider from a snapshot.

    Parameters
    ----------
    snapshot : Mapping[str, Any]
        Snapshot previously produced by snapshot().

    Returns
    -------
    TraceProvider
        Self.
    """

    if not isinstance(
        snapshot,
        Mapping,
    ):
        raise TypeError(
            "snapshot must be a mapping."
        )

    with self._lock:

        # --------------------------------------------------------------
        # Configuration
        # --------------------------------------------------------------

        config = snapshot.get(
            "configuration",
            {},
        )

        self._enabled = bool(
            config.get(
                "enabled",
                self._enabled,
            )
        )

        self._auto_initialize = bool(
            config.get(
                "auto_initialize",
                self._auto_initialize,
            )
        )

        self._auto_shutdown = bool(
            config.get(
                "auto_shutdown",
                self._auto_shutdown,
            )
        )

        self._default_tracer = config.get(
            "default_tracer",
            self._default_tracer,
        )

        self._history_limit = int(
            config.get(
                "history_limit",
                self._history_limit,
            )
        )

        self._timeout = float(
            config.get(
                "timeout",
                self._timeout,
            )
        )

        self._encoding = config.get(
            "encoding",
            self._encoding,
        )

        self._options = dict(
            config.get(
                "options",
                {},
            )
        )

        self._capabilities = set(
            config.get(
                "capabilities",
                [],
            )
        )

        # --------------------------------------------------------------
        # Runtime
        # --------------------------------------------------------------

        runtime = snapshot.get(
            "runtime",
            {},
        )

        self._initialized = bool(
            runtime.get(
                "initialized",
                self._initialized,
            )
        )

        self._running = bool(
            runtime.get(
                "running",
                self._running,
            )
        )

        self._active = bool(
            runtime.get(
                "active",
                self._active,
            )
        )

        self._frozen = bool(
            runtime.get(
                "frozen",
                self._frozen,
            )
        )

        self._closed = bool(
            runtime.get(
                "closed",
                self._closed,
            )
        )

        if "state" in runtime:

            self._state = ProviderState(
                runtime["state"]
            )

        self._created_at = runtime.get(
            "created_at",
            self._created_at,
        )

        self._updated_at = runtime.get(
            "updated_at",
            self._updated_at,
        )

        self._last_activity = runtime.get(
            "last_activity",
            self._last_activity,
        )

        # --------------------------------------------------------------
        # Statistics
        # --------------------------------------------------------------

        stats = snapshot.get(
            "statistics",
        )

        if stats:

            if hasattr(
                self._statistics,
                "from_dict",
            ):
                self._statistics.from_dict(
                    stats
                )
            else:

                for key, value in stats.items():

                    setattr(
                        self._statistics,
                        key,
                        value,
                    )

        # --------------------------------------------------------------
        # Metadata
        # --------------------------------------------------------------

        metadata = snapshot.get(
            "metadata",
            {},
        )

        self._metadata = dict(
            metadata.get(
                "metadata",
                {},
            )
        )

        self._tags = set(
            metadata.get(
                "tags",
                [],
            )
        )

        self._context_data = dict(
            metadata.get(
                "context_data",
                {},
            )
        )

        self._history = deque(
            metadata.get(
                "history",
                [],
            ),
            maxlen=self._history_limit,
        )

        self._cache = dict(
            metadata.get(
                "cache",
                {},
            )
        )

        self.touch()

        return self
# ==============================================================================
# Part 5.2. Copying
# ==============================================================================

from copy import copy as _copy
from copy import deepcopy
from typing import Self


# ------------------------------------------------------------------------------
# clone
# ------------------------------------------------------------------------------

def clone(
    self,
    *,
    deep: bool = True,
    preserve_runtime: bool = True,
    preserve_statistics: bool = True,
) -> Self:
    """
    Clone this TraceProvider.

    Parameters
    ----------
    deep : bool, default=True
        Perform a deep clone.
    preserve_runtime : bool, default=True
        Preserve runtime state.
    preserve_statistics : bool, default=True
        Preserve runtime statistics.

    Returns
    -------
    Self
        New TraceProvider instance.
    """

    with self._lock:

        snapshot = self.snapshot(
            include_runtime=preserve_runtime,
            include_statistics=preserve_statistics,
            include_metadata=True,
            deep=deep,
        )

        clone = self.__class__(
            name=self._name,
            description=self._description,
            version=self._version,
            provider_type=self._provider_type,
            manager=self._manager,
            sampler=self._sampler,
            processor=self._processor,
            context=self._context,
            exporters=(
                deepcopy(self._exporters)
                if deep
                else list(self._exporters)
            ),
            enabled=self._enabled,
            auto_initialize=False,
            auto_shutdown=self._auto_shutdown,
            default_tracer=self._default_tracer,
            history_limit=self._history_limit,
            timeout=self._timeout,
            encoding=self._encoding,
            options=(
                deepcopy(self._options)
                if deep
                else dict(self._options)
            ),
            metadata=(
                deepcopy(self._metadata)
                if deep
                else dict(self._metadata)
            ),
        )

        # --------------------------------------------------------------
        # Clone tracer registry
        # --------------------------------------------------------------

        clone._tracers.clear()

        for name, tracer in self._tracers.items():

            clone._tracers[name] = (
                deepcopy(tracer)
                if deep
                else tracer
            )

        if self._active_tracer is not None:

            clone._active_tracer = (
                clone._tracers.get(
                    self._active_tracer.name
                )
            )

        clone.restore(snapshot)

        clone.touch()

        return clone


# ------------------------------------------------------------------------------
# copy
# ------------------------------------------------------------------------------

def copy(
    self,
    *,
    deep: bool = False,
) -> Self:
    """
    Copy this TraceProvider.

    Parameters
    ----------
    deep : bool, default=False
        If True, perform a deep copy.

    Returns
    -------
    Self
        Copied TraceProvider.
    """

    if deep:

        return self.clone(
            deep=True,
            preserve_runtime=True,
            preserve_statistics=True,
        )

    with self._lock:

        obj = self.__class__(
            name=self._name,
            description=self._description,
            version=self._version,
            provider_type=self._provider_type,
            manager=self._manager,
            sampler=self._sampler,
            processor=self._processor,
            context=self._context,
            exporters=list(self._exporters),
            enabled=self._enabled,
            auto_initialize=False,
            auto_shutdown=self._auto_shutdown,
            default_tracer=self._default_tracer,
            history_limit=self._history_limit,
            timeout=self._timeout,
            encoding=self._encoding,
            options=dict(self._options),
            metadata=dict(self._metadata),
        )

        obj._tracers = dict(self._tracers)

        obj._active_tracer = self._active_tracer

        obj._tags = set(self._tags)

        obj._context_data = dict(
            self._context_data
        )

        obj._history = self._history.copy()

        obj._cache = dict(self._cache)

        obj._statistics = deepcopy(
            self._statistics
        )

        obj.touch()

        return obj
# ==============================================================================
# Part 5.3. Maintenance
# ==============================================================================

def compact(
    self,
) -> int:
    """
    Compact internal runtime containers.

    Removes obsolete history entries, shrinks caches and compacts
    all registered tracers.

    Returns
    -------
    int
        Number of objects compacted.
    """

    with self._lock:

        compacted = 0

        # --------------------------------------------------------------
        # Compact history
        # --------------------------------------------------------------

        history = deque(

            (
                item

                for item in self._history

                if item is not None
            ),

            maxlen=self._history_limit,

        )

        compacted += (

            len(self._history)

            -

            len(history)

        )

        self._history = history

        # --------------------------------------------------------------
        # Compact cache
        # --------------------------------------------------------------

        stale_keys = [

            key

            for key, value

            in self._cache.items()

            if value is None

        ]

        for key in stale_keys:

            del self._cache[key]

        compacted += len(stale_keys)

        # --------------------------------------------------------------
        # Compact tracers
        # --------------------------------------------------------------

        for tracer in self._tracers.values():

            compact_fn = getattr(

                tracer,

                "compact",

                None,

            )

            if callable(compact_fn):

                try:

                    compacted += int(
                        compact_fn()
                    )

                except Exception:

                    self._statistics.error_count += 1

        self._statistics.update_count += 1

        self.touch()

        return compacted


# ------------------------------------------------------------------------------


def cleanup(
    self,
) -> int:
    """
    Remove expired runtime objects.

    Returns
    -------
    int
        Number of cleaned objects.
    """

    with self._lock:

        cleaned = 0

        # --------------------------------------------------------------
        # Cache
        # --------------------------------------------------------------

        cleaned += len(self._cache)

        self._cache.clear()

        # --------------------------------------------------------------
        # History overflow
        # --------------------------------------------------------------

        self._history = deque(

            list(self._history)[
                -self._history_limit:
            ],

            maxlen=self._history_limit,

        )

        # --------------------------------------------------------------
        # Cleanup tracers
        # --------------------------------------------------------------

        for tracer in self._tracers.values():

            cleanup_fn = getattr(

                tracer,

                "cleanup",

                None,

            )

            if callable(cleanup_fn):

                try:

                    cleaned += int(
                        cleanup_fn()
                    )

                except Exception:

                    self._statistics.error_count += 1

        self._statistics.update_count += 1

        self.touch()

        return cleaned


# ------------------------------------------------------------------------------


def optimize(
    self,
) -> Dict[str, Any]:
    """
    Optimize the provider.

    Performs lightweight maintenance operations across all
    provider components.

    Returns
    -------
    Dict[str, Any]
        Optimization report.
    """

    with self._lock:

        report = {

            "history_before": len(
                self._history
            ),

            "cache_before": len(
                self._cache
            ),

            "tracer_count": len(
                self._tracers
            ),

        }

        compacted = self.compact()

        cleaned = self.cleanup()

        report.update(

            {

                "compacted": compacted,

                "cleaned": cleaned,

                "history_after": len(
                    self._history
                ),

                "cache_after": len(
                    self._cache
                ),

                "optimized_at": time.time(),

            }

        )

        self._statistics.update_count += 1

        self.touch()

        return report
# ==============================================================================
# Part 6.1. Summary
# ==============================================================================

def summary(
    self,
) -> Dict[str, Any]:
    """
    Return a high-level summary of the provider.

    Returns
    -------
    Dict[str, Any]
        Provider summary.
    """

    with self._lock:

        uptime = self.uptime

        return {

            # ----------------------------------------------------------
            # Identity
            # ----------------------------------------------------------

            "id": self.id,
            "uuid": str(self.uuid),
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "provider_type": self.provider_type,

            # ----------------------------------------------------------
            # Runtime
            # ----------------------------------------------------------

            "enabled": self.enabled,
            "initialized": self.initialized,
            "running": self.running,
            "active": self.active,
            "frozen": self.frozen,
            "closed": self.closed,
            "state": self.state,

            # ----------------------------------------------------------
            # Components
            # ----------------------------------------------------------

            "tracer_count": self.tracer_count,
            "active_tracer_count": self.active_tracer_count,
            "exporter_count": self.exporter_count,

            # ----------------------------------------------------------
            # Statistics
            # ----------------------------------------------------------

            "trace_count": self.trace_count,
            "span_count": self.span_count,
            "error_count": self.error_count,
            "success_rate": self.success_rate,
            "failure_rate": self.failure_rate,

            # ----------------------------------------------------------
            # Metadata
            # ----------------------------------------------------------

            "tag_count": len(self.tags),
            "history_size": len(self.history),
            "cache_size": len(self.cache),

            # ----------------------------------------------------------
            # Timing
            # ----------------------------------------------------------

            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "last_activity": self.last_activity,
            "uptime": uptime,

        }


# ------------------------------------------------------------------------------


def metrics(
    self,
) -> Dict[str, Union[int, float]]:
    """
    Return runtime metrics suitable for dashboards,
    exporters and monitoring systems.

    Returns
    -------
    Dict[str, Union[int, float]]
    """

    with self._lock:

        uptime = self.uptime

        metrics = {

            # ----------------------------------------------------------
            # Runtime
            # ----------------------------------------------------------

            "uptime_seconds": uptime,

            "enabled": int(
                self.enabled
            ),

            "running": int(
                self.running
            ),

            "active": int(
                self.active
            ),

            "initialized": int(
                self.initialized
            ),

            # ----------------------------------------------------------
            # Tracing
            # ----------------------------------------------------------

            "trace_count": self.trace_count,

            "span_count": self.span_count,

            "tracer_count": self.tracer_count,

            "active_tracer_count":
                self.active_tracer_count,

            # ----------------------------------------------------------
            # Exporting
            # ----------------------------------------------------------

            "exporter_count":
                self.exporter_count,

            # ----------------------------------------------------------
            # Errors
            # ----------------------------------------------------------

            "error_count":
                self.error_count,

            "success_rate":
                self.success_rate,

            "failure_rate":
                self.failure_rate,

            # ----------------------------------------------------------
            # Metadata
            # ----------------------------------------------------------

            "history_size":
                len(self.history),

            "cache_size":
                len(self.cache),

            "tag_count":
                len(self.tags),

        }

        return metrics
# ==============================================================================
# Part 6.2. Reporting
# ==============================================================================

def report(
    self,
    *,
    include_identity: bool = True,
    include_runtime: bool = True,
    include_components: bool = True,
    include_statistics: bool = True,
    include_metadata: bool = True,
    include_metrics: bool = True,
    include_configuration: bool = False,
    include_tracers: bool = True,
) -> Dict[str, Any]:
    """
    Generate a comprehensive provider report.

    Parameters
    ----------
    include_identity : bool, default=True
        Include identity information.
    include_runtime : bool, default=True
        Include runtime information.
    include_components : bool, default=True
        Include component information.
    include_statistics : bool, default=True
        Include statistics.
    include_metadata : bool, default=True
        Include metadata.
    include_metrics : bool, default=True
        Include runtime metrics.
    include_configuration : bool, default=False
        Include provider configuration.
    include_tracers : bool, default=True
        Include registered tracer information.

    Returns
    -------
    Dict[str, Any]
        Complete provider report.
    """

    with self._lock:

        report: Dict[str, Any] = {}

        # ------------------------------------------------------------------
        # Identity
        # ------------------------------------------------------------------

        if include_identity:

            report["identity"] = {

                "id": self.id,
                "uuid": str(self.uuid),
                "name": self.name,
                "description": self.description,
                "version": self.version,
                "provider_type": self.provider_type,

            }

        # ------------------------------------------------------------------
        # Runtime
        # ------------------------------------------------------------------

        if include_runtime:

            report["runtime"] = {

                "initialized": self.initialized,
                "running": self.running,
                "active": self.active,
                "enabled": self.enabled,
                "frozen": self.frozen,
                "closed": self.closed,
                "state": self.state,

                "created_at": self.created_at,
                "updated_at": self.updated_at,
                "last_activity": self.last_activity,
                "uptime": self.uptime,

            }

        # ------------------------------------------------------------------
        # Components
        # ------------------------------------------------------------------

        if include_components:

            report["components"] = {

                "manager": (
                    type(self.manager).__name__
                    if self.manager
                    else None
                ),

                "sampler": (
                    type(self.sampler).__name__
                    if self.sampler
                    else None
                ),

                "processor": (
                    type(self.processor).__name__
                    if self.processor
                    else None
                ),

                "context": (
                    type(self.context).__name__
                    if self.context
                    else None
                ),

                "active_tracer": (
                    self.active_tracer.name
                    if self.active_tracer
                    else None
                ),

                "tracer_count":
                    self.tracer_count,

                "exporter_count":
                    self.exporter_count,

            }

        # ------------------------------------------------------------------
        # Configuration
        # ------------------------------------------------------------------

        if include_configuration:

            report["configuration"] = {

                "enabled":
                    self.enabled,

                "auto_initialize":
                    self.auto_initialize,

                "auto_shutdown":
                    self.auto_shutdown,

                "default_tracer":
                    self.default_tracer,

                "history_limit":
                    self.history_limit,

                "timeout":
                    self.timeout,

                "encoding":
                    self.encoding,

                "capabilities":
                    sorted(self.capabilities),

                "options":
                    deepcopy(self.options),

            }

        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------

        if include_statistics:

            report["statistics"] = {

                "trace_count":
                    self.trace_count,

                "span_count":
                    self.span_count,

                "tracer_count":
                    self.tracer_count,

                "active_tracer_count":
                    self.active_tracer_count,

                "exporter_count":
                    self.exporter_count,

                "error_count":
                    self.error_count,

                "success_rate":
                    self.success_rate,

                "failure_rate":
                    self.failure_rate,

            }

        # ------------------------------------------------------------------
        # Metadata
        # ------------------------------------------------------------------

        if include_metadata:

            report["metadata"] = {

                "tags":
                    sorted(self.tags),

                "metadata":
                    deepcopy(self.metadata),

                "context_data":
                    deepcopy(self.context_data),

                "history_size":
                    len(self.history),

                "cache_size":
                    len(self.cache),

                "callback_count":
                    len(self.callbacks),

                "hook_count":
                    sum(
                        len(v)
                        for v in self.hooks.values()
                    ),

                "filter_count":
                    len(self.filters),

            }

        # ------------------------------------------------------------------
        # Metrics
        # ------------------------------------------------------------------

        if include_metrics:

            report["metrics"] = self.metrics()

        # ------------------------------------------------------------------
        # Tracers
        # ------------------------------------------------------------------

        if include_tracers:

            tracers = []

            for tracer in self.tracers.values():

                summary = getattr(
                    tracer,
                    "summary",
                    None,
                )

                if callable(summary):

                    tracers.append(
                        summary()
                    )

                else:

                    tracers.append(

                        {

                            "name": tracer.name,

                            "type": tracer.tracer_type,

                            "running": tracer.running,

                        }

                    )

            report["tracers"] = tracers

        # ------------------------------------------------------------------
        # Timestamp
        # ------------------------------------------------------------------

        report["generated_at"] = time.time()

        report["provider"] = self.name

        report["report_version"] = "1.0"

        return report
# ==============================================================================
# Part 6.3. Diagnostics
# ==============================================================================

def diagnostics(
    self,
    *,
    include_components: bool = True,
    include_tracers: bool = True,
    include_exporters: bool = True,
) -> Dict[str, Any]:
    """
    Run provider diagnostics.

    Parameters
    ----------
    include_components : bool, default=True
        Include manager/sampler/processor diagnostics.
    include_tracers : bool, default=True
        Include tracer diagnostics.
    include_exporters : bool, default=True
        Include exporter diagnostics.

    Returns
    -------
    Dict[str, Any]
        Diagnostic report.
    """

    with self._lock:

        diagnostics: Dict[str, Any] = {

            "healthy": True,

            "provider": self.name,

            "provider_type": self.provider_type,

            "state": self.state,

            "generated_at": time.time(),

            "issues": [],

            "warnings": [],

        }

        # ------------------------------------------------------------------
        # Runtime
        # ------------------------------------------------------------------

        runtime = {

            "enabled": self.enabled,

            "initialized": self.initialized,

            "running": self.running,

            "active": self.active,

            "closed": self.closed,

            "frozen": self.frozen,

            "uptime": self.uptime,

        }

        diagnostics["runtime"] = runtime

        if self.closed:

            diagnostics["warnings"].append(
                "Provider is closed."
            )

        if not self.enabled:

            diagnostics["warnings"].append(
                "Provider is disabled."
            )

        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------

        diagnostics["statistics"] = {

            "trace_count": self.trace_count,

            "span_count": self.span_count,

            "tracer_count": self.tracer_count,

            "exporter_count": self.exporter_count,

            "error_count": self.error_count,

            "success_rate": self.success_rate,

            "failure_rate": self.failure_rate,

        }

        if self.error_count > 0:

            diagnostics["warnings"].append(

                f"{self.error_count} runtime errors detected."

            )

        # ------------------------------------------------------------------
        # Components
        # ------------------------------------------------------------------

        if include_components:

            component_report = {}

            for name, component in {

                "manager": self.manager,

                "sampler": self.sampler,

                "processor": self.processor,

                "context": self.context,

            }.items():

                if component is None:

                    component_report[name] = {

                        "status": "missing",

                    }

                    diagnostics["issues"].append(

                        f"{name} is not configured."

                    )

                    diagnostics["healthy"] = False

                    continue

                fn = getattr(

                    component,

                    "health",

                    None,

                )

                if callable(fn):

                    try:

                        component_report[name] = fn()

                    except Exception as exc:

                        diagnostics["healthy"] = False

                        component_report[name] = {

                            "status": "error",

                            "message": str(exc),

                        }

                else:

                    component_report[name] = {

                        "status": "available",

                    }

            diagnostics["components"] = component_report

        # ------------------------------------------------------------------
        # Tracers
        # ------------------------------------------------------------------

        if include_tracers:

            tracer_report = {}

            for name, tracer in self.tracers.items():

                fn = getattr(

                    tracer,

                    "health",

                    None,

                )

                if callable(fn):

                    try:

                        tracer_report[name] = fn()

                    except Exception as exc:

                        tracer_report[name] = {

                            "status": "error",

                            "message": str(exc),

                        }

                        diagnostics["healthy"] = False

                else:

                    tracer_report[name] = {

                        "status": "registered",

                    }

            diagnostics["tracers"] = tracer_report

        # ------------------------------------------------------------------
        # Exporters
        # ------------------------------------------------------------------

        if include_exporters:

            exporter_report = []

            for exporter in self.exporters:

                fn = getattr(

                    exporter,

                    "health",

                    None,

                )

                if callable(fn):

                    try:

                        exporter_report.append(

                            fn()

                        )

                    except Exception as exc:

                        exporter_report.append(

                            {

                                "status": "error",

                                "message": str(exc),

                            }

                        )

                        diagnostics["healthy"] = False

                else:

                    exporter_report.append(

                        {

                            "name": type(exporter).__name__,

                            "status": "registered",

                        }

                    )

            diagnostics["exporters"] = exporter_report

        diagnostics["issue_count"] = len(

            diagnostics["issues"]

        )

        diagnostics["warning_count"] = len(

            diagnostics["warnings"]

        )

        return diagnostics


# ------------------------------------------------------------------------------


def health(
    self,
) -> Dict[str, Any]:
    """
    Return provider health information.

    Returns
    -------
    Dict[str, Any]
        Health information.
    """

    diagnostics = self.diagnostics(

        include_components=True,

        include_tracers=False,

        include_exporters=False,

    )

    healthy = (

        diagnostics["healthy"]

        and

        not self.closed

        and

        self.enabled

    )

    return {

        "healthy": healthy,

        "status": (

            "healthy"

            if healthy

            else "unhealthy"

        ),

        "provider": self.name,

        "state": self.state,

        "enabled": self.enabled,

        "running": self.running,

        "initialized": self.initialized,

        "active": self.active,

        "trace_count": self.trace_count,

        "span_count": self.span_count,

        "error_count": self.error_count,

        "success_rate": self.success_rate,

        "failure_rate": self.failure_rate,

        "uptime": self.uptime,

        "checked_at": time.time(),

    }
# ==============================================================================
# Part 7.1. Core Validation
# ==============================================================================

def validate(
    self,
    *,
    raise_exception: bool = False,
) -> bool:
    """
    Validate the provider.

    This method performs a complete validation of the provider by
    validating its configuration, registered tracers, provider state
    and internal integrity.

    Parameters
    ----------
    raise_exception : bool, default=False
        Raise ValidationError on failure.

    Returns
    -------
    bool
        True if validation succeeds.
    """

    with self._lock:

        validators = (

            self.validate_configuration,

            self.validate_tracers,

            self.validate_provider,

            self.check_integrity,

        )

        errors: List[str] = []

        for validator in validators:

            try:

                result = validator()

            except Exception as exc:

                errors.append(str(exc))

                continue

            if result is True:

                continue

            if isinstance(result, str):

                errors.append(result)

                continue

            if isinstance(result, (list, tuple)):

                errors.extend(

                    str(item)

                    for item in result

                )

        valid = len(errors) == 0

        self._cache["last_validation"] = {

            "timestamp": time.time(),

            "success": valid,

            "errors": errors,

        }

        if not valid:

            self._statistics.error_count += 1

            if raise_exception:

                raise ValidationError(

                    "Provider validation failed:\n"

                    + "\n".join(errors)

                )

        return valid


# ------------------------------------------------------------------------------


def check_integrity(
    self,
) -> bool:
    """
    Check internal provider integrity.

    Returns
    -------
    bool
        True if the provider is internally consistent.

    Raises
    ------
    ValidationError
        If integrity verification fails.
    """

    with self._lock:

        #
        # Identity
        #

        if not self._id:

            raise ValidationError(

                "Provider id is empty."

            )

        if self._uuid is None:

            raise ValidationError(

                "Provider UUID is missing."

            )

        if not self._name:

            raise ValidationError(

                "Provider name is empty."

            )

        #
        # Runtime containers
        #

        if self._tracers is None:

            raise ValidationError(

                "Tracer registry is missing."

            )

        if self._exporters is None:

            raise ValidationError(

                "Exporter registry is missing."

            )

        if self._history is None:

            raise ValidationError(

                "History buffer is missing."

            )

        if self._cache is None:

            raise ValidationError(

                "Cache storage is missing."

            )

        if self._metadata is None:

            raise ValidationError(

                "Metadata storage is missing."

            )

        #
        # Active tracer
        #

        if (

            self._active_tracer is not None

            and

            self._active_tracer.name

            not in self._tracers

        ):

            raise ValidationError(

                "Active tracer is not registered."

            )

        #
        # Statistics
        #

        if self._statistics is None:

            raise ValidationError(

                "Statistics object is missing."

            )

        #
        # History size
        #

        if (

            len(self._history)

            >

            self._history_limit

        ):

            raise ValidationError(

                "History exceeds configured limit."

            )

        #
        # Component counts
        #

        if (

            self.tracer_count

            !=

            len(self._tracers)

        ):

            raise ValidationError(

                "Tracer count mismatch."

            )

        if (

            self.exporter_count

            !=

            len(self._exporters)

        ):

            raise ValidationError(

                "Exporter count mismatch."

            )

        #
        # Runtime state
        #

        if self._closed and self._running:

            raise ValidationError(

                "Closed provider cannot be running."

            )

        if self._closed and self._active:

            raise ValidationError(

                "Closed provider cannot be active."

            )

        #
        # Success
        #

        return True
# ==============================================================================
# Part 7.2. Configuration Validation
# ==============================================================================

def validate_configuration(
    self,
) -> bool:
    """
    Validate provider configuration.

    This method verifies that the provider configuration is
    internally consistent and ready for runtime execution.

    Returns
    -------
    bool
        True if configuration is valid.

    Raises
    ------
    ValidationError
        If any configuration entry is invalid.
    """

    with self._lock:

        # ------------------------------------------------------------------
        # Identity
        # ------------------------------------------------------------------

        if not isinstance(self._name, str):

            raise ValidationError(
                "Provider name must be a string."
            )

        if not self._name.strip():

            raise ValidationError(
                "Provider name cannot be empty."
            )

        if not isinstance(self._version, str):

            raise ValidationError(
                "Version must be a string."
            )

        # ------------------------------------------------------------------
        # Configuration Flags
        # ------------------------------------------------------------------

        if not isinstance(
            self._enabled,
            bool,
        ):
            raise ValidationError(
                "enabled must be bool."
            )

        if not isinstance(
            self._auto_initialize,
            bool,
        ):
            raise ValidationError(
                "auto_initialize must be bool."
            )

        if not isinstance(
            self._auto_shutdown,
            bool,
        ):
            raise ValidationError(
                "auto_shutdown must be bool."
            )

        # ------------------------------------------------------------------
        # History
        # ------------------------------------------------------------------

        if not isinstance(
            self._history_limit,
            int,
        ):
            raise ValidationError(
                "history_limit must be int."
            )

        if self._history_limit <= 0:

            raise ValidationError(
                "history_limit must be > 0."
            )

        # ------------------------------------------------------------------
        # Timeout
        # ------------------------------------------------------------------

        if not isinstance(
            self._timeout,
            (int, float),
        ):
            raise ValidationError(
                "timeout must be numeric."
            )

        if self._timeout <= 0:

            raise ValidationError(
                "timeout must be positive."
            )

        # ------------------------------------------------------------------
        # Encoding
        # ------------------------------------------------------------------

        if not isinstance(
            self._encoding,
            str,
        ):
            raise ValidationError(
                "encoding must be a string."
            )

        try:

            "".encode(self._encoding)

        except LookupError as exc:

            raise ValidationError(

                f"Unsupported encoding: "
                f"{self._encoding}"

            ) from exc

        # ------------------------------------------------------------------
        # Default tracer
        # ------------------------------------------------------------------

        if self._default_tracer is not None:

            if not isinstance(
                self._default_tracer,
                str,
            ):
                raise ValidationError(
                    "default_tracer must be str."
                )

        # ------------------------------------------------------------------
        # Options
        # ------------------------------------------------------------------

        if not isinstance(
            self._options,
            dict,
        ):
            raise ValidationError(
                "options must be dict."
            )

        # ------------------------------------------------------------------
        # Capabilities
        # ------------------------------------------------------------------

        if not isinstance(
            self._capabilities,
            (set, list, tuple),
        ):
            raise ValidationError(
                "capabilities must be iterable."
            )

        for capability in self._capabilities:

            if not isinstance(
                capability,
                str,
            ):
                raise ValidationError(
                    "Capability names "
                    "must be strings."
                )

        # ------------------------------------------------------------------
        # Metadata
        # ------------------------------------------------------------------

        if not isinstance(
            self._metadata,
            dict,
        ):
            raise ValidationError(
                "metadata must be dict."
            )

        if not isinstance(
            self._tags,
            set,
        ):
            raise ValidationError(
                "tags must be a set."
            )

        if not isinstance(
            self._context_data,
            dict,
        ):
            raise ValidationError(
                "context_data must be dict."
            )

        # ------------------------------------------------------------------
        # Runtime Containers
        # ------------------------------------------------------------------

        if not isinstance(
            self._history,
            deque,
        ):
            raise ValidationError(
                "history must be deque."
            )

        if not isinstance(
            self._cache,
            dict,
        ):
            raise ValidationError(
                "cache must be dict."
            )

        if not isinstance(
            self._callbacks,
            list,
        ):
            raise ValidationError(
                "callbacks must be list."
            )

        if not isinstance(
            self._hooks,
            dict,
        ):
            raise ValidationError(
                "hooks must be dict."
            )

        if not isinstance(
            self._filters,
            list,
        ):
            raise ValidationError(
                "filters must be list."
            )

        # ------------------------------------------------------------------
        # Statistics Object
        # ------------------------------------------------------------------

        if self._statistics is None:

            raise ValidationError(
                "Statistics object is missing."
            )

        # ------------------------------------------------------------------
        # Success
        # ------------------------------------------------------------------

        return True
# ==============================================================================
# Part 7.3. Component Validation
# ==============================================================================

# ------------------------------------------------------------------------------
# validate_tracers
# ------------------------------------------------------------------------------

def validate_tracers(
    self,
) -> bool:
    """
    Validate all registered tracers.

    Returns
    -------
    bool
        True if every tracer is valid.

    Raises
    ------
    ValidationError
        If any tracer is invalid.
    """

    with self._lock:

        #
        # Registry
        #

        if self._tracers is None:

            raise ValidationError(
                "Tracer registry is missing."
            )

        if not isinstance(
            self._tracers,
            dict,
        ):
            raise ValidationError(
                "Tracer registry must be a dictionary."
            )

        #
        # Validate each tracer
        #

        for name, tracer in self._tracers.items():

            if not isinstance(
                name,
                str,
            ):

                raise ValidationError(
                    "Tracer registry contains "
                    "a non-string key."
                )

            if tracer is None:

                raise ValidationError(

                    f"Tracer '{name}' is None."

                )

            if not isinstance(
                tracer,
                TraceTracer,
            ):

                raise ValidationError(

                    f"'{name}' is not "
                    "a TraceTracer."

                )

            #
            # Name consistency
            #

            if tracer.name != name:

                raise ValidationError(

                    f"Tracer name mismatch "
                    f"('{name}' != '{tracer.name}')."

                )

            #
            # Delegate validation
            #

            validate = getattr(

                tracer,

                "validate",

                None,

            )

            if callable(validate):

                result = validate()

                if result is False:

                    raise ValidationError(

                        f"Tracer '{name}' "
                        "validation failed."

                    )

        #
        # Active tracer
        #

        if self._active_tracer is not None:

            if (

                self._active_tracer.name

                not in

                self._tracers

            ):

                raise ValidationError(

                    "Active tracer is "
                    "not registered."

                )

        return True


# ------------------------------------------------------------------------------
# validate_provider
# ------------------------------------------------------------------------------

def validate_provider(
    self,
) -> bool:
    """
    Validate provider runtime components.

    Returns
    -------
    bool
        True if provider components are valid.

    Raises
    ------
    ValidationError
        If provider runtime is inconsistent.
    """

    with self._lock:

        #
        # Manager
        #

        if self._manager is None:

            raise ValidationError(
                "TraceManager is missing."
            )

        #
        # Processor
        #

        if self._processor is None:

            raise ValidationError(
                "TraceProcessor is missing."
            )

        #
        # Sampler
        #

        if self._sampler is None:

            raise ValidationError(
                "TraceSampler is missing."
            )

        #
        # Context
        #

        if self._context is None:

            raise ValidationError(
                "TraceContext is missing."
            )

        #
        # Exporters
        #

        if self._exporters is None:

            raise ValidationError(
                "Exporter registry is missing."
            )

        if not isinstance(
            self._exporters,
            list,
        ):

            raise ValidationError(
                "Exporters must be stored "
                "as a list."
            )

        for exporter in self._exporters:

            if exporter is None:

                raise ValidationError(
                    "Exporter cannot be None."
                )

            validate = getattr(

                exporter,

                "validate",

                None,

            )

            if callable(validate):

                result = validate()

                if result is False:

                    raise ValidationError(

                        f"Exporter "
                        f"{type(exporter).__name__} "
                        "validation failed."

                    )

        #
        # Manager consistency
        #

        manager_provider = getattr(

            self._manager,

            "provider",

            None,

        )

        if (

            manager_provider is not None

            and

            manager_provider is not self

        ):

            raise ValidationError(

                "Manager references "
                "another provider."

            )

        #
        # Runtime state
        #

        if self._closed and self._running:

            raise ValidationError(

                "Closed provider "
                "cannot be running."

            )

        if self._closed and self._active:

            raise ValidationError(

                "Closed provider "
                "cannot be active."

            )

        if (

            self._active

            and

            self._active_tracer is None

        ):

            raise ValidationError(

                "Provider is active "
                "without an active tracer."

            )

        return True
# ==============================================================================
# Part 8.1. Lifecycle Hooks
# ==============================================================================

def before_create(
    self,
    **kwargs: Any,
) -> None:
    """
    Execute hooks before provider creation/initialization.

    Parameters
    ----------
    **kwargs
        Additional event payload.
    """

    with self._lock:

        payload = {
            "provider": self,
            "provider_id": self.id,
            "provider_name": self.name,
            "timestamp": time.time(),
            **kwargs,
        }

        # Dedicated lifecycle event
        self.emit_event(
            "before_create",
            **payload,
        )

        # Generic lifecycle event
        self.emit_event(
            "lifecycle.before_create",
            **payload,
        )


# ------------------------------------------------------------------------------


def after_create(
    self,
    **kwargs: Any,
) -> None:
    """
    Execute hooks after provider creation/initialization.

    Parameters
    ----------
    **kwargs
        Additional event payload.
    """

    with self._lock:

        payload = {
            "provider": self,
            "provider_id": self.id,
            "provider_name": self.name,
            "state": self.state,
            "timestamp": time.time(),
            **kwargs,
        }

        self.emit_event(
            "after_create",
            **payload,
        )

        self.emit_event(
            "lifecycle.after_create",
            **payload,
        )


# ------------------------------------------------------------------------------


def before_shutdown(
    self,
    **kwargs: Any,
) -> None:
    """
    Execute hooks before provider shutdown.

    Parameters
    ----------
    **kwargs
        Additional event payload.
    """

    with self._lock:

        payload = {
            "provider": self,
            "provider_id": self.id,
            "provider_name": self.name,
            "running": self.running,
            "active": self.active,
            "timestamp": time.time(),
            **kwargs,
        }

        self.emit_event(
            "before_shutdown",
            **payload,
        )

        self.emit_event(
            "lifecycle.before_shutdown",
            **payload,
        )


# ------------------------------------------------------------------------------


def after_shutdown(
    self,
    **kwargs: Any,
) -> None:
    """
    Execute hooks after provider shutdown.

    Parameters
    ----------
    **kwargs
        Additional event payload.
    """

    with self._lock:

        payload = {
            "provider": self,
            "provider_id": self.id,
            "provider_name": self.name,
            "state": self.state,
            "closed": self.closed,
            "timestamp": time.time(),
            **kwargs,
        }

        self.emit_event(
            "after_shutdown",
            **payload,
        )

        self.emit_event(
            "lifecycle.after_shutdown",
            **payload,
        )
# ==============================================================================
# Part 8.2. Hook Management
# ==============================================================================

from collections.abc import Callable
from typing import Any, Optional


# ------------------------------------------------------------------------------
# add_hook
# ------------------------------------------------------------------------------

def add_hook(
    self,
    event: str,
    hook: Callable[..., Any],
) -> Callable[..., Any]:
    """
    Register a hook for an event.

    Parameters
    ----------
    event : str
        Event name.
    hook : Callable[..., Any]
        Hook callback.

    Returns
    -------
    Callable[..., Any]
        Registered hook.

    Raises
    ------
    ValidationError
        If the event or hook is invalid.
    """

    with self._lock:

        if not isinstance(event, str):

            raise ValidationError(
                "Event name must be a string."
            )

        event = event.strip()

        if not event:

            raise ValidationError(
                "Event name cannot be empty."
            )

        if not callable(hook):

            raise ValidationError(
                "Hook must be callable."
            )

        registry = self._hooks.setdefault(
            event,
            [],
        )

        if hook not in registry:

            registry.append(hook)

        self.touch()

        return hook


# ------------------------------------------------------------------------------
# remove_hook
# ------------------------------------------------------------------------------

def remove_hook(
    self,
    event: str,
    hook: Callable[..., Any],
) -> bool:
    """
    Remove a registered hook.

    Parameters
    ----------
    event : str
        Event name.
    hook : Callable[..., Any]
        Hook callback.

    Returns
    -------
    bool
        True if removed.
    """

    with self._lock:

        hooks = self._hooks.get(event)

        if not hooks:

            return False

        try:

            hooks.remove(hook)

        except ValueError:

            return False

        if not hooks:

            del self._hooks[event]

        self.touch()

        return True


# ------------------------------------------------------------------------------
# clear_hooks
# ------------------------------------------------------------------------------

def clear_hooks(
    self,
    event: Optional[str] = None,
) -> int:
    """
    Remove hooks.

    Parameters
    ----------
    event : str | None, default=None
        Event whose hooks should be cleared.
        If None, every registered hook is removed.

    Returns
    -------
    int
        Number of hooks removed.
    """

    with self._lock:

        #
        # Clear all hooks
        #

        if event is None:

            removed = sum(

                len(v)

                for v in self._hooks.values()

            )

            self._hooks.clear()

            self.touch()

            return removed

        #
        # Clear a single event
        #

        hooks = self._hooks.pop(

            event,

            [],

        )

        self.touch()

        return len(hooks)
# ==============================================================================
# Part 8.3. Event Dispatching
# ==============================================================================

from typing import Any, Dict, List


def emit_event(
    self,
    event: str,
    **payload: Any,
) -> Dict[str, Any]:
    """
    Emit an event to all registered hooks and callbacks.

    Supported dispatch targets
    --------------------------
    1. Event-specific hooks
    2. Wildcard hooks ("*")
    3. Registered callbacks

    Parameters
    ----------
    event : str
        Event name.
    **payload
        Event payload.

    Returns
    -------
    Dict[str, Any]
        Dispatch report.
    """

    if not isinstance(event, str):

        raise ValidationError(
            "event must be a string."
        )

    event = event.strip()

    if not event:

        raise ValidationError(
            "event cannot be empty."
        )

    with self._lock:

        timestamp = time.time()

        event_payload = {

            "event": event,

            "provider": self,

            "provider_id": self.id,

            "provider_name": self.name,

            "timestamp": timestamp,

            **payload,

        }

        dispatched = 0

        failures = 0

        errors: List[str] = []

        # --------------------------------------------------------------
        # Collect hooks
        # --------------------------------------------------------------

        hooks: List[Any] = []

        hooks.extend(

            self._hooks.get(

                event,

                [],

            )

        )

        hooks.extend(

            self._hooks.get(

                "*",

                [],

            )

        )

        # --------------------------------------------------------------
        # Dispatch hooks
        # --------------------------------------------------------------

        for hook in hooks:

            try:

                hook(**event_payload)

                dispatched += 1

            except Exception as exc:

                failures += 1

                self._statistics.error_count += 1

                errors.append(

                    f"{hook!r}: {exc}"

                )

        # --------------------------------------------------------------
        # Notify callbacks
        # --------------------------------------------------------------

        for callback in list(self._callbacks):

            try:

                callback(

                    event,

                    event_payload,

                )

                dispatched += 1

            except Exception as exc:

                failures += 1

                self._statistics.error_count += 1

                errors.append(

                    f"{callback!r}: {exc}"

                )

        # --------------------------------------------------------------
        # History
        # --------------------------------------------------------------

        self._history.append(

            {

                "event": event,

                "timestamp": timestamp,

                "success": failures == 0,

                "dispatch_count": dispatched,

            }

        )

        # --------------------------------------------------------------
        # Statistics
        # --------------------------------------------------------------

        self._statistics.update_count += 1

        self.touch()

        # --------------------------------------------------------------
        # Dispatch report
        # --------------------------------------------------------------

        return {

            "event": event,

            "success": failures == 0,

            "dispatch_count": dispatched,

            "failure_count": failures,

            "errors": errors,

            "timestamp": timestamp,

        }
# ==============================================================================
# Part 9.1. Callback Management
# ==============================================================================


from collections.abc import Callable
from typing import Any, Optional


# ------------------------------------------------------------------------------
# subscribe
# ------------------------------------------------------------------------------

def subscribe(
    self,
    callback: Callable[..., Any],
) -> Callable[..., Any]:
    """
    Register a runtime callback.

    Parameters
    ----------
    callback : Callable[..., Any]
        Callback to register.

    Returns
    -------
    Callable[..., Any]
        Registered callback.

    Raises
    ------
    ValidationError
        If callback is invalid.
    """

    with self._lock:

        if not callable(callback):

            raise ValidationError(
                "Callback must be callable."
            )

        if callback not in self._callbacks:

            self._callbacks.append(
                callback
            )

            if self._statistics is not None:

                self._statistics.update_count += 1

        self.touch()

        return callback


# ------------------------------------------------------------------------------
# unsubscribe
# ------------------------------------------------------------------------------

def unsubscribe(
    self,
    callback: Callable[..., Any],
) -> bool:
    """
    Remove a callback.

    Parameters
    ----------
    callback : Callable[..., Any]

    Returns
    -------
    bool
        True if removed.
    """

    with self._lock:

        try:

            self._callbacks.remove(
                callback
            )

        except ValueError:

            return False

        if self._statistics is not None:

            self._statistics.update_count += 1

        self.touch()

        return True


# ------------------------------------------------------------------------------
# clear_callbacks
# ------------------------------------------------------------------------------

def clear_callbacks(
    self,
) -> int:
    """
    Remove every registered callback.

    Returns
    -------
    int
        Number of callbacks removed.
    """

    with self._lock:

        removed = len(
            self._callbacks
        )

        self._callbacks.clear()

        if self._statistics is not None:

            self._statistics.update_count += 1

        self.touch()

        return removed
# ==============================================================================
# Part 9.2. Callback Dispatch
# ==============================================================================

from typing import Any, Dict, List, Optional
import inspect
import time


def notify_callbacks(
    self,
    event: str,
    payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Notify all registered callbacks.

    Parameters
    ----------
    event : str
        Event name.
    payload : dict, optional
        Event payload.

    Returns
    -------
    Dict[str, Any]
        Dispatch report.

    Notes
    -----
    Supported callback signatures::

        callback(event, payload)

        callback(provider, event, payload)

        callback(payload)

        callback()

    Exceptions raised by one callback do not prevent the remaining
    callbacks from executing.
    """

    if not isinstance(event, str):

        raise ValidationError(
            "event must be a string."
        )

    event = event.strip()

    if not event:

        raise ValidationError(
            "event cannot be empty."
        )

    with self._lock:

        payload = dict(payload or {})

        payload.setdefault(
            "provider",
            self,
        )

        payload.setdefault(
            "provider_id",
            self.id,
        )

        payload.setdefault(
            "provider_name",
            self.name,
        )

        payload.setdefault(
            "timestamp",
            time.time(),
        )

        callbacks = list(
            self._callbacks
        )

    # --------------------------------------------------------------
    # Dispatch outside the lock
    # --------------------------------------------------------------

    dispatched = 0

    failures = 0

    errors: List[str] = []

    for callback in callbacks:

        try:

            parameter_count = len(

                inspect.signature(
                    callback
                ).parameters

            )

            if parameter_count == 0:

                callback()

            elif parameter_count == 1:

                callback(
                    payload
                )

            elif parameter_count == 2:

                callback(
                    event,
                    payload,
                )

            else:

                callback(
                    self,
                    event,
                    payload,
                )

            dispatched += 1

        except Exception as exc:

            failures += 1

            errors.append(

                f"{callback!r}: {exc}"

            )

    # --------------------------------------------------------------
    # Update runtime state
    # --------------------------------------------------------------

    with self._lock:

        if self._statistics is not None:

            self._statistics.update_count += 1

            self._statistics.error_count += failures

        self._history.append(

            {

                "type": "callback_dispatch",

                "event": event,

                "timestamp": payload[
                    "timestamp"
                ],

                "callback_count": dispatched,

                "failure_count": failures,

            }

        )

        self.touch()

        return {

            "event": event,

            "success": failures == 0,

            "callback_count": len(
                callbacks
            ),

            "dispatched": dispatched,

            "failures": failures,

            "errors": errors,

            "timestamp": payload[
                "timestamp"
            ],

        }
# ==============================================================================
# Part 10.1.1.a
# Dictionary Serialization
#
# Identity
# Configuration
# Runtime State
# ==============================================================================

def to_dict(
    self,
    *,
    deep: bool = True,
    include_runtime: bool = True,
    include_statistics: bool = True,
    include_metadata: bool = True,
    include_components: bool = True,
) -> Dict[str, Any]:
    """
    Serialize TraceProvider into a Python dictionary.

    Parameters
    ----------
    deep : bool, default=True
        Perform deep serialization.

    include_runtime : bool, default=True
        Include runtime state.

    include_statistics : bool, default=True
        Include runtime statistics.

    include_metadata : bool, default=True
        Include metadata.

    include_components : bool, default=True
        Include component summaries.

    Returns
    -------
    Dict[str, Any]
    """

    with self._lock:

        data: Dict[str, Any] = {

            # ----------------------------------------------------------
            # Schema
            # ----------------------------------------------------------

            "__class__": self.__class__.__name__,

            "__module__": self.__class__.__module__,

            "__version__": self.version,

            "serialization_version": 1,

            # ----------------------------------------------------------
            # Identity
            # ----------------------------------------------------------

            "identity": {

                "id": self.id,

                "uuid": str(self.uuid),

                "name": self.name,

                "description": self.description,

                "version": self.version,

                "provider_type": (

                    self.provider_type.name

                    if hasattr(
                        self.provider_type,
                        "name",
                    )
                    else str(
                        self.provider_type
                    )

                ),

            },

            # ----------------------------------------------------------
            # Configuration
            # ----------------------------------------------------------

            "configuration": {

                "enabled": self.enabled,

                "auto_initialize":
                    self.auto_initialize,

                "auto_shutdown":
                    self.auto_shutdown,

                "default_tracer":
                    self.default_tracer,

                "history_limit":
                    self.history_limit,

                "timeout":
                    self.timeout,

                "encoding":
                    self.encoding,

                "options":

                    copy.deepcopy(
                        self.options
                    )

                    if deep

                    else dict(
                        self.options
                    ),

                "capabilities":

                    sorted(

                        list(
                            self.capabilities
                        )

                    ),

            },

        }

        # --------------------------------------------------------------
        # Runtime
        # --------------------------------------------------------------

        if include_runtime:

            data["runtime"] = {

                "initialized":
                    self.initialized,

                "running":
                    self.running,

                "active":
                    self.active,

                "frozen":
                    self.frozen,

                "closed":
                    self.closed,

                "state":

                    self.state.name

                    if hasattr(
                        self.state,
                        "name",
                    )
                    else str(
                        self.state
                    ),

                "created_at":
                    self.created_at,

                "updated_at":
                    self.updated_at,

                "last_activity":
                    self.last_activity,

                "uptime":
                    self.uptime,

            }

        # --------------------------------------------------------------
        # Remaining sections
        # --------------------------------------------------------------

        #
        # Implemented in
        #
        # Part 10.1.1.b
        # Statistics
        # Metadata
        #
        # Part 10.1.1.c
        # Components
        #

        return data
        # --------------------------------------------------------------
        # Statistics
        # --------------------------------------------------------------

        if include_statistics:

            statistics = self.statistics

            if hasattr(statistics, "to_dict"):

                data["statistics"] = (

                    statistics.to_dict()

                    if deep

                    else dict(
                        statistics.to_dict()
                    )

                )

            elif statistics is not None:

                data["statistics"] = {

                    "tracer_count":
                        self.tracer_count,

                    "active_tracer_count":
                        self.active_tracer_count,

                    "trace_count":
                        self.trace_count,

                    "span_count":
                        self.span_count,

                    "exporter_count":
                        self.exporter_count,

                    "error_count":
                        self.error_count,

                    "success_rate":
                        self.success_rate,

                    "failure_rate":
                        self.failure_rate,

                    "update_count":

                        getattr(

                            statistics,

                            "update_count",

                            0,

                        ),

                }

            else:

                data["statistics"] = None

        # --------------------------------------------------------------
        # Metadata
        # --------------------------------------------------------------

        if include_metadata:

            data["metadata"] = {

                "metadata":

                    copy.deepcopy(
                        self.metadata
                    )

                    if deep

                    else dict(
                        self.metadata
                    ),

                "tags":

                    sorted(

                        list(
                            self.tags
                        )

                    ),

                "context_data":

                    copy.deepcopy(
                        self.context_data
                    )

                    if deep

                    else dict(
                        self.context_data
                    ),

            }

        # --------------------------------------------------------------
        # History
        # --------------------------------------------------------------

        if include_metadata:

            history_items = list(
                self.history
            )

            if deep:

                history_items = (

                    copy.deepcopy(
                        history_items
                    )

                )

            data["history"] = history_items

        # --------------------------------------------------------------
        # Cache
        # --------------------------------------------------------------

        if include_metadata:

            if deep:

                cache = copy.deepcopy(
                    self.cache
                )

            else:

                cache = dict(
                    self.cache
                )

            #
            # Remove transient runtime entries
            #

            for transient_key in (

                "last_validation",

                "last_snapshot",

                "temporary",

                "runtime_cache",

            ):

                cache.pop(

                    transient_key,

                    None,

                )

            data["cache"] = cache
        # --------------------------------------------------------------
        # Components
        # --------------------------------------------------------------

        if include_components:

            components: Dict[str, Any] = {}

            # ----------------------------------------------------------
            # Manager summary
            # ----------------------------------------------------------

            manager = self.manager

            if manager is None:

                components["manager"] = None

            elif hasattr(manager, "to_dict"):

                try:

                    components["manager"] = {

                        "type": type(manager).__name__,

                        "summary": manager.to_dict()

                        if deep

                        else {

                            "name": getattr(

                                manager,

                                "name",

                                None,

                            ),

                        },

                    }

                except Exception:

                    components["manager"] = {

                        "type": type(manager).__name__,

                        "id": getattr(

                            manager,

                            "id",

                            None,

                        ),

                    }

            else:

                components["manager"] = {

                    "type": type(manager).__name__,

                    "id": getattr(

                        manager,

                        "id",

                        None,

                    ),

                }

            # ----------------------------------------------------------
            # Sampler summary
            # ----------------------------------------------------------

            sampler = self.sampler

            if sampler is None:

                components["sampler"] = None

            elif hasattr(sampler, "to_dict"):

                try:

                    components["sampler"] = {

                        "type": type(sampler).__name__,

                        "summary": sampler.to_dict()

                        if deep

                        else {

                            "name": getattr(

                                sampler,

                                "name",

                                None,

                            ),

                        },

                    }

                except Exception:

                    components["sampler"] = {

                        "type": type(sampler).__name__,

                    }

            else:

                components["sampler"] = {

                    "type": type(sampler).__name__,

                }

            # ----------------------------------------------------------
            # Processor summary
            # ----------------------------------------------------------

            processor = self.processor

            if processor is None:

                components["processor"] = None

            elif hasattr(processor, "to_dict"):

                try:

                    components["processor"] = {

                        "type": type(processor).__name__,

                        "summary": processor.to_dict()

                        if deep

                        else {

                            "name": getattr(

                                processor,

                                "name",

                                None,

                            ),

                        },

                    }

                except Exception:

                    components["processor"] = {

                        "type": type(processor).__name__,

                    }

            else:

                components["processor"] = {

                    "type": type(processor).__name__,

                }

            # ----------------------------------------------------------
            # Context summary
            # ----------------------------------------------------------

            context = self.context

            if context is None:

                components["context"] = None

            elif hasattr(context, "to_dict"):

                try:

                    components["context"] = {

                        "type": type(context).__name__,

                        "summary": context.to_dict()

                        if deep

                        else {},

                    }

                except Exception:

                    components["context"] = {

                        "type": type(context).__name__,

                    }

            else:

                components["context"] = {

                    "type": type(context).__name__,

                }

            # ----------------------------------------------------------
            # Tracer summaries
            # ----------------------------------------------------------

            tracer_summaries: List[Dict[str, Any]] = []

            for tracer in self.tracers.values():

                info = {

                    "id": getattr(

                        tracer,

                        "id",

                        None,

                    ),

                    "name": getattr(

                        tracer,

                        "name",

                        None,

                    ),

                    "type": type(tracer).__name__,

                    "active":

                        tracer is self.active_tracer,

                }

                if deep and hasattr(tracer, "to_dict"):

                    try:

                        info["summary"] = (

                            tracer.to_dict()

                        )

                    except Exception:

                        pass

                tracer_summaries.append(info)

            components["tracers"] = tracer_summaries

            # ----------------------------------------------------------
            # Exporter summaries
            # ----------------------------------------------------------

            exporter_summaries: List[Dict[str, Any]] = []

            for exporter in self.exporters:

                info = {

                    "type": type(exporter).__name__,

                    "name": getattr(

                        exporter,

                        "name",

                        None,

                    ),

                }

                if deep and hasattr(exporter, "to_dict"):

                    try:

                        info["summary"] = (

                            exporter.to_dict()

                        )

                    except Exception:

                        pass

                exporter_summaries.append(info)

            components["exporters"] = exporter_summaries

            # ----------------------------------------------------------
            # Component statistics
            # ----------------------------------------------------------

            components["counts"] = {

                "tracers":

                    len(self.tracers),

                "exporters":

                    len(self.exporters),

            }

            data["components"] = components

        # --------------------------------------------------------------
        # Final dictionary assembly
        # --------------------------------------------------------------

        data["serialization"] = {

            "deep": deep,

            "generated_at": time.time(),

            "provider_class":

                self.__class__.__name__,

            "module":

                self.__class__.__module__,

        }

        return data
# ==============================================================================
# Part 10.1.2.a
# Provider Reconstruction
# ==============================================================================

@classmethod
def from_dict(
    cls,
    data: Dict[str, Any],
    *,
    validate: bool = True,
) -> "TraceProvider":
    """
    Restore a TraceProvider from a serialized dictionary.
    """

    if not isinstance(data, dict):

        raise ValidationError(
            "Serialized provider must be a dictionary."
        )

    #
    # Version compatibility
    #

    serialization_version = int(
        data.get(
            "serialization_version",
            1,
        )
    )

    if serialization_version > 1:

        raise ValidationError(
            f"Unsupported serialization version "
            f"{serialization_version}."
        )

    identity = data.get(
        "identity",
        {},
    )

    configuration = data.get(
        "configuration",
        {},
    )

    #
    # Create provider
    #

    provider = cls(

        name=identity.get(
            "name",
            "TraceProvider",
        ),

        description=identity.get(
            "description",
            "",
        ),

    )

    #
    # Restore identity
    #

    provider._id = identity.get(
        "id",
        provider._id,
    )

    uuid_value = identity.get(
        "uuid",
    )

    if uuid_value is not None:

        try:

            provider._uuid = UUID(
                str(uuid_value)
            )

        except Exception:

            pass

    provider._version = identity.get(
        "version",
        provider._version,
    )

    provider._provider_type = identity.get(
        "provider_type",
        provider._provider_type,
    )

    #
    # Restore configuration
    #

    provider._enabled = bool(
        configuration.get(
            "enabled",
            provider._enabled,
        )
    )

    provider._auto_initialize = bool(
        configuration.get(
            "auto_initialize",
            provider._auto_initialize,
        )
    )

    provider._auto_shutdown = bool(
        configuration.get(
            "auto_shutdown",
            provider._auto_shutdown,
        )
    )

    provider._default_tracer = configuration.get(
        "default_tracer",
        provider._default_tracer,
    )

    provider._history_limit = int(
        configuration.get(
            "history_limit",
            provider._history_limit,
        )
    )

    provider._timeout = float(
        configuration.get(
            "timeout",
            provider._timeout,
        )
    )

    provider._encoding = configuration.get(
        "encoding",
        provider._encoding,
    )

    provider._options = dict(
        configuration.get(
            "options",
            provider._options,
        )
    )

    provider._capabilities = set(
        configuration.get(
            "capabilities",
            provider._capabilities,
        )
    )
    # ------------------------------------------------------------------
    # Restore runtime
    # ------------------------------------------------------------------

    runtime = data.get(
        "runtime",
        {},
    )

    provider._initialized = bool(
        runtime.get(
            "initialized",
            provider._initialized,
        )
    )

    provider._running = bool(
        runtime.get(
            "running",
            provider._running,
        )
    )

    provider._active = bool(
        runtime.get(
            "active",
            provider._active,
        )
    )

    provider._frozen = bool(
        runtime.get(
            "frozen",
            provider._frozen,
        )
    )

    provider._closed = bool(
        runtime.get(
            "closed",
            provider._closed,
        )
    )

    provider._state = runtime.get(
        "state",
        provider._state,
    )

    provider._created_at = runtime.get(
        "created_at",
        provider._created_at,
    )

    provider._updated_at = runtime.get(
        "updated_at",
        provider._updated_at,
    )

    provider._last_activity = runtime.get(
        "last_activity",
        provider._last_activity,
    )

    # uptime được tính lại từ created_at nên không restore.

    # ------------------------------------------------------------------
    # Restore statistics
    # ------------------------------------------------------------------

    statistics = data.get(
        "statistics",
    )

    if statistics is not None:

        if (
            hasattr(provider._statistics, "from_dict")
            and
            callable(provider._statistics.from_dict)
        ):

            provider._statistics = (
                provider._statistics.from_dict(
                    statistics
                )
            )

        else:

            provider._statistics.trace_count = (
                statistics.get(
                    "trace_count",
                    provider._statistics.trace_count,
                )
            )

            provider._statistics.span_count = (
                statistics.get(
                    "span_count",
                    provider._statistics.span_count,
                )
            )

            provider._statistics.tracer_count = (
                statistics.get(
                    "tracer_count",
                    provider._statistics.tracer_count,
                )
            )

            provider._statistics.active_tracer_count = (
                statistics.get(
                    "active_tracer_count",
                    provider._statistics.active_tracer_count,
                )
            )

            provider._statistics.exporter_count = (
                statistics.get(
                    "exporter_count",
                    provider._statistics.exporter_count,
                )
            )

            provider._statistics.error_count = (
                statistics.get(
                    "error_count",
                    provider._statistics.error_count,
                )
            )

            provider._statistics.success_rate = (
                statistics.get(
                    "success_rate",
                    provider._statistics.success_rate,
                )
            )

            provider._statistics.failure_rate = (
                statistics.get(
                    "failure_rate",
                    provider._statistics.failure_rate,
                )
            )

            provider._statistics.update_count = (
                statistics.get(
                    "update_count",
                    getattr(
                        provider._statistics,
                        "update_count",
                        0,
                    ),
                )
            )

    # ------------------------------------------------------------------
    # Restore metadata
    # ------------------------------------------------------------------

    metadata = data.get(
        "metadata",
        {},
    )

    provider._metadata = dict(
        metadata.get(
            "metadata",
            {},
        )
    )

    provider._tags = set(
        metadata.get(
            "tags",
            [],
        )
    )

    provider._context_data = dict(
        metadata.get(
            "context_data",
            {},
        )
    )

    # ------------------------------------------------------------------
    # Restore history
    # ------------------------------------------------------------------

    provider._history.clear()

    provider._history.extend(

        copy.deepcopy(

            data.get(
                "history",
                [],
            )

        )

    )

    # ------------------------------------------------------------------
    # Restore cache
    # ------------------------------------------------------------------

    provider._cache.clear()

    provider._cache.update(

        copy.deepcopy(

            data.get(
                "cache",
                {},
            )

        )

    )
    # ------------------------------------------------------------------
    # Restore components
    # ------------------------------------------------------------------

    components = data.get(
        "components",
        {},
    )

    # ------------------------------------------------------------------
    # Restore manager
    # ------------------------------------------------------------------

    manager_data = components.get(
        "manager",
    )

    if isinstance(
        manager_data,
        Mapping,
    ):

        payload = manager_data.get(
            "summary",
            manager_data,
        )

        if isinstance(
            payload,
            Mapping,
        ):

            provider._manager = (
                TraceManager.from_dict(
                    payload,
                )
            )

    # ------------------------------------------------------------------
    # Restore sampler
    # ------------------------------------------------------------------

    sampler_data = components.get(
        "sampler",
    )

    if isinstance(
        sampler_data,
        Mapping,
    ):

        payload = sampler_data.get(
            "summary",
            sampler_data,
        )

        if isinstance(
            payload,
            Mapping,
        ):

            provider._sampler = (
                TraceSampler.from_dict(
                    payload,
                )
            )

    # ------------------------------------------------------------------
    # Restore processor
    # ------------------------------------------------------------------

    processor_data = components.get(
        "processor",
    )

    if isinstance(
        processor_data,
        Mapping,
    ):

        payload = processor_data.get(
            "summary",
            processor_data,
        )

        if isinstance(
            payload,
            Mapping,
        ):

            provider._processor = (
                TraceProcessor.from_dict(
                    payload,
                )
            )

    # ------------------------------------------------------------------
    # Restore tracers
    # ------------------------------------------------------------------

    provider._tracers.clear()

    active_tracer = None

    for item in components.get(
        "tracers",
        [],
    ):

        if not isinstance(
            item,
            Mapping,
        ):

            continue

        payload = item.get(
            "summary",
        )

        if not isinstance(
            payload,
            Mapping,
        ):

            continue

        tracer = TraceTracer.from_dict(
            payload,
        )

        tracer_name = getattr(
            tracer,
            "name",
            None,
        ) or item.get(
            "name",
        )

        if tracer_name is None:

            tracer_name = str(
                tracer.id,
            )

        provider._tracers[
            tracer_name
        ] = tracer

        if item.get(
            "active",
            False,
        ):

            active_tracer = tracer

    provider._active_tracer = (
        active_tracer
    )

    if (
        provider._active_tracer is None
        and provider._tracers
    ):

        provider._active_tracer = next(

            iter(
                provider._tracers.values()
            )

        )

    # ------------------------------------------------------------------
    # Restore exporters
    # ------------------------------------------------------------------

    provider._exporters.clear()

    for item in components.get(
        "exporters",
        [],
    ):

        if not isinstance(
            item,
            Mapping,
        ):

            continue

        payload = item.get(
            "summary",
        )

        if not isinstance(
            payload,
            Mapping,
        ):

            continue

        exporter = BaseExporter.from_dict(
            payload,
        )

        provider._exporters.append(
            exporter,
        )

    # ------------------------------------------------------------------
    # Synchronize component counters
    # ------------------------------------------------------------------

    provider._tracer_count = len(
        provider._tracers,
    )

    provider._active_tracer_count = sum(

        1

        for tracer in provider._tracers.values()

        if getattr(
            tracer,
            "active",
            False,
        )

    )

    provider._exporter_count = len(
        provider._exporters,
    )

    # ------------------------------------------------------------------
    # Validation after restore
    # ------------------------------------------------------------------

    if validate:

        provider.validate_configuration()

        provider.validate_tracers()

        provider.validate_provider()

        provider.check_integrity()

    # ------------------------------------------------------------------
    # Final timestamp
    # ------------------------------------------------------------------

    provider.touch()

    # ------------------------------------------------------------------
    # Return restored provider
    # ------------------------------------------------------------------

    return provider
# ==============================================================================
# Part 10.2 – JSON Serialization
# ==============================================================================

# ------------------------------------------------------------------------------
# to_json()
# ------------------------------------------------------------------------------

def to_json(
    self,
    *,
    indent: int = 4,
    ensure_ascii: bool = False,
    sort_keys: bool = True,
    validate: bool = False,
) -> str:
    """
    Serialize the TraceProvider into a JSON string.

    Parameters
    ----------
    indent
        JSON indentation.

    ensure_ascii
        Preserve Unicode characters.

    sort_keys
        Sort dictionary keys.

    validate
        Validate the provider before serialization.

    Returns
    -------
    str
        JSON representation.
    """

    if validate:

        self.validate()

    payload = self.to_dict()

    return json.dumps(

        payload,

        indent=indent,

        ensure_ascii=ensure_ascii,

        sort_keys=sort_keys,

        default=str,

    )


# ------------------------------------------------------------------------------
# from_json()
# ------------------------------------------------------------------------------

@classmethod
def from_json(
    cls,
    value: Union[
        str,
        bytes,
        bytearray,
        Path,
    ],
    *,
    validate: bool = True,
) -> "TraceProvider":
    """
    Create a TraceProvider from JSON.

    Parameters
    ----------
    value
        JSON string, bytes, bytearray or file path.

    validate
        Validate after reconstruction.

    Returns
    -------
    TraceProvider
    """

    if isinstance(
        value,
        Path,
    ):

        payload = value.read_text(
            encoding="utf-8",
        )

    elif isinstance(
        value,
        (
            bytes,
            bytearray,
        ),
    ):

        payload = value.decode(
            "utf-8",
        )

    elif isinstance(
        value,
        str,
    ):

        stripped = value.lstrip()

        if stripped.startswith("{"):

            payload = value

        else:

            candidate = Path(value)

            if candidate.exists():

                payload = candidate.read_text(
                    encoding="utf-8",
                )

            else:

                payload = value

    else:

        raise TypeError(

            "value must be a JSON string, "
            "bytes, bytearray or pathlib.Path."

        )

    data = json.loads(
        payload,
    )

    if not isinstance(
        data,
        Mapping,
    ):

        raise TypeError(
            "JSON root must be an object."
        )

    return cls.from_dict(

        data,

        validate=validate,

    )
# ==============================================================================
# Part 11. Utilities
# ==============================================================================

# ------------------------------------------------------------------------------
# supports()
# ------------------------------------------------------------------------------

def supports(
    self,
    capability: Any,
) -> bool:
    """
    Return whether the provider supports a capability.

    Parameters
    ----------
    capability
        Capability name, enum or object.

    Returns
    -------
    bool
    """

    if capability is None:

        return False

    if hasattr(
        capability,
        "value",
    ):

        capability = capability.value

    return capability in self._capabilities


# ------------------------------------------------------------------------------
# add_tag()
# ------------------------------------------------------------------------------

def add_tag(
    self,
    tag: str,
) -> "TraceProvider":
    """
    Add a provider tag.
    """

    if tag:

        self._tags.add(
            str(tag),
        )

        self.touch()

    return self


# ------------------------------------------------------------------------------
# remove_tag()
# ------------------------------------------------------------------------------

def remove_tag(
    self,
    tag: str,
) -> "TraceProvider":
    """
    Remove a provider tag.
    """

    self._tags.discard(
        str(tag),
    )

    self.touch()

    return self


# ------------------------------------------------------------------------------
# clear_tags()
# ------------------------------------------------------------------------------

def clear_tags(
    self,
) -> "TraceProvider":
    """
    Remove all provider tags.
    """

    self._tags.clear()

    self.touch()

    return self


# ------------------------------------------------------------------------------
# touch()
# ------------------------------------------------------------------------------

def touch(
    self,
) -> float:
    """
    Update the provider timestamp.

    Returns
    -------
    float
        Updated timestamp.
    """

    self._updated_at = time.time()

    self._last_activity = self._updated_at

    return self._updated_at


# ------------------------------------------------------------------------------
# age()
# ------------------------------------------------------------------------------

def age(
    self,
) -> float:
    """
    Return provider age in seconds.
    """

    return max(

        0.0,

        time.time() - self._created_at,

    )


# ------------------------------------------------------------------------------
# timestamp()
# ------------------------------------------------------------------------------

def timestamp(
    self,
) -> float:
    """
    Return the current timestamp.
    """

    return time.time()


# ------------------------------------------------------------------------------
# tracer_names()
# ------------------------------------------------------------------------------

def tracer_names(
    self,
) -> list[str]:
    """
    Return registered tracer names.
    """

    return sorted(

        self._tracers.keys(),

    )


# ------------------------------------------------------------------------------
# active_tracers()
# ------------------------------------------------------------------------------

def active_tracers(
    self,
) -> list["TraceTracer"]:
    """
    Return active tracers.
    """

    return [

        tracer

        for tracer in self._tracers.values()

        if getattr(
            tracer,
            "active",
            False,
        )

    ]
# ==============================================================================
# Part 12. Python Protocols
# ==============================================================================

# ------------------------------------------------------------------------------
# __repr__()
# ------------------------------------------------------------------------------

def __repr__(self) -> str:
    """
    Return an unambiguous representation of the provider.
    """

    return (

        f"{self.__class__.__name__}("

        f"name={self._name!r}, "

        f"type={self._provider_type!r}, "

        f"enabled={self._enabled!r}, "

        f"running={self._running!r}, "

        f"tracers={len(self._tracers)!r}, "

        f"exporters={len(self._exporters)!r}"

        ")"

    )


# ------------------------------------------------------------------------------
# __str__()
# ------------------------------------------------------------------------------

def __str__(self) -> str:
    """
    Return a human-readable provider summary.
    """

    return (

        f"{self._name} "

        f"[{self._provider_type}] "

        f"({len(self._tracers)} tracers, "

        f"{len(self._exporters)} exporters)"

    )


# ------------------------------------------------------------------------------
# __len__()
# ------------------------------------------------------------------------------

def __len__(self) -> int:
    """
    Return the number of registered tracers.
    """

    return len(
        self._tracers,
    )


# ------------------------------------------------------------------------------
# __iter__()
# ------------------------------------------------------------------------------

def __iter__(self):
    """
    Iterate over registered tracers.
    """

    return iter(
        self._tracers.values(),
    )


# ------------------------------------------------------------------------------
# __contains__()
# ------------------------------------------------------------------------------

def __contains__(
    self,
    item: object,
) -> bool:
    """
    Return whether a tracer exists.

    Parameters
    ----------
    item
        Tracer name or TraceTracer instance.
    """

    if isinstance(
        item,
        str,
    ):

        return item in self._tracers

    name = getattr(
        item,
        "name",
        None,
    )

    if name is None:

        return False

    return name in self._tracers


# ------------------------------------------------------------------------------
# __getitem__()
# ------------------------------------------------------------------------------

def __getitem__(
    self,
    name: str,
) -> "TraceTracer":
    """
    Retrieve a tracer by name.

    Raises
    ------
    KeyError
        If the tracer does not exist.
    """

    return self._tracers[
        name
    ]


# ------------------------------------------------------------------------------
# __call__()
# ------------------------------------------------------------------------------

def __call__(
    self,
    name: Optional[str] = None,
) -> "TraceTracer":
    """
    Return the active tracer or a named tracer.
    """

    if name is None:

        return self.current_tracer()

    return self.get_tracer(
        name,
    )


# ------------------------------------------------------------------------------
# __bool__()
# ------------------------------------------------------------------------------

def __bool__(self) -> bool:
    """
    Return provider availability.
    """

    return (

        self._enabled

        and not self._closed

    )


# ------------------------------------------------------------------------------
# __copy__()
# ------------------------------------------------------------------------------

def __copy__(
    self,
) -> "TraceProvider":
    """
    Create a shallow copy.
    """

    return self.copy()


# ------------------------------------------------------------------------------
# __deepcopy__()
# ------------------------------------------------------------------------------

def __deepcopy__(
    self,
    memo: dict[int, object],
) -> "TraceProvider":
    """
    Create a deep copy.
    """

    copied = self.clone()

    memo[id(self)] = copied

    return copied


# ------------------------------------------------------------------------------
# __eq__()
# ------------------------------------------------------------------------------

def __eq__(
    self,
    other: object,
) -> bool:
    """
    Compare providers by UUID.
    """

    if not isinstance(
        other,
        TraceProvider,
    ):

        return NotImplemented

    return self._uuid == other._uuid


# ------------------------------------------------------------------------------
# __hash__()
# ------------------------------------------------------------------------------

def __hash__(self) -> int:
    """
    Return the provider hash.
    """

    return hash(
        self._uuid,
    )
# ==============================================================================
# Part 13. Context Manager
# ==============================================================================

# ------------------------------------------------------------------------------
# __enter__()
# ------------------------------------------------------------------------------

def __enter__(
    self,
) -> "TraceProvider":
    """
    Enter the runtime context.

    Returns
    -------
    TraceProvider
        Initialized provider.
    """

    if not self._initialized:

        self.initialize()

    self._running = True
    self._active = True

    self.touch()

    return self


# ------------------------------------------------------------------------------
# __exit__()
# ------------------------------------------------------------------------------

def __exit__(
    self,
    exc_type,
    exc_value,
    traceback,
) -> bool:
    """
    Exit the runtime context.

    Flush pending traces and optionally perform
    automatic shutdown.

    Returns
    -------
    bool
        Always False so exceptions propagate.
    """

    try:

        self.flush()

    finally:

        self._running = False
        self._active = False

        if self._auto_shutdown:

            self.shutdown()

        self.touch()

    #
    # Never suppress exceptions.
    #

    return False


# ==============================================================================
# Part 14. Public API
# ==============================================================================

__all__ = [

    # ------------------------------------------------------------------
    # Constants
    # ------------------------------------------------------------------

    "PROVIDER_NAME",
    "PROVIDER_DESCRIPTION",
    "PROVIDER_VERSION",
    "DEFAULT_HISTORY_LIMIT",
    "DEFAULT_TIMEOUT",
    "DEFAULT_ENCODING",
    "DEFAULT_AUTO_INITIALIZE",
    "DEFAULT_AUTO_SHUTDOWN",
    "DEFAULT_ENABLED",

    # ------------------------------------------------------------------
    # Type Aliases
    # ------------------------------------------------------------------

    "ProviderOptions",
    "ProviderMetadata",
    "ProviderContext",
    "ProviderHistory",
    "ProviderCache",
    "ProviderHook",
    "ProviderCallback",
    "ProviderFilter",

    # ------------------------------------------------------------------
    # Exceptions
    # ------------------------------------------------------------------

    "TraceProviderError",
    "ProviderConfigurationError",
    "ProviderValidationError",

    # ------------------------------------------------------------------
    # Enums
    # ------------------------------------------------------------------

    "ProviderType",
    "ProviderState",
    "ProviderCapability",

    # ------------------------------------------------------------------
    # Dataclasses
    # ------------------------------------------------------------------

    "ProviderStatistics",
    "ProviderReport",

    # ------------------------------------------------------------------
    # Main Class
    # ------------------------------------------------------------------

    "TraceProvider",

]                                                                                                                                                                                                                                
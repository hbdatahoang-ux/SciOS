"""
SciOS-NG
Runtime Observability - Trace Context

File:
    scios/runtime/observability/tracing/context.py

Part 1. Foundation
    • Imports
    • Constants
    • Type Aliases
    • Exceptions
    • Enums
    • Dataclasses
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

from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, Flag, auto
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    TypeAlias,
    Union,
)

# ==============================================================================
# Constants
# ==============================================================================

CONTEXT_VERSION: str = "0.3.0-alpha"

DEFAULT_CONTEXT_NAME: str = "TraceContext"

DEFAULT_ENCODING: str = "utf-8"

DEFAULT_HISTORY_LIMIT: int = 1024

DEFAULT_CACHE_SIZE: int = 256

DEFAULT_TIMEOUT: float = 30.0

DEFAULT_TRACE_ID: str = ""

DEFAULT_SPAN_ID: str = ""

DEFAULT_PARENT_SPAN_ID: str = ""

DEFAULT_TRACE_STATE: str = ""

DEFAULT_TRACE_FLAGS: int = 0

DEFAULT_BAGGAGE: Dict[str, str] = {}

DEFAULT_METADATA: Dict[str, Any] = {}

DEFAULT_ATTRIBUTES: Dict[str, Any] = {}

DEFAULT_TAGS: List[str] = []

# ==============================================================================
# Type Aliases
# ==============================================================================

ContextKey: TypeAlias = str

ContextValue: TypeAlias = Any

ContextData: TypeAlias = Dict[str, Any]

ContextMetadata: TypeAlias = Dict[str, Any]

ContextAttributes: TypeAlias = Dict[str, Any]

ContextSnapshot: TypeAlias = Dict[str, Any]

ContextFilter: TypeAlias = Callable[[ContextKey, ContextValue], bool]

ContextHook: TypeAlias = Callable[..., Any]

ContextCallback: TypeAlias = Callable[..., None]

ContextFactory: TypeAlias = Callable[[], Dict[str, Any]]

# ==============================================================================
# Exceptions
# ==============================================================================


class TraceContextError(Exception):
    """Base exception for TraceContext."""


class ContextValidationError(TraceContextError):
    """Context validation failed."""


class ContextRuntimeError(TraceContextError):
    """Runtime state error."""


class ContextClosedError(TraceContextError):
    """Context has been closed."""


class ContextFrozenError(TraceContextError):
    """Context is frozen."""


class ContextKeyError(TraceContextError):
    """Invalid context key."""


# ==============================================================================
# Enums
# ==============================================================================


class TraceContextState(str, Enum):
    """
    Runtime state of TraceContext.
    """

    CREATED = "created"

    INITIALIZED = "initialized"

    ACTIVE = "active"

    FROZEN = "frozen"

    CLOSED = "closed"


class TraceContextFormat(str, Enum):
    """
    Serialization format.
    """

    DICT = "dict"

    JSON = "json"

    BINARY = "binary"

    CUSTOM = "custom"


class TraceContextFlag(Flag):
    """
    Context feature flags.
    """

    NONE = 0

    READ_ONLY = auto()

    IMMUTABLE = auto()

    COMPRESSED = auto()

    ENCRYPTED = auto()

    PERSISTENT = auto()

    REMOTE = auto()

    LOCAL = auto()

    ROOT = auto()


# ==============================================================================
# Dataclasses
# ==============================================================================


@dataclass(slots=True)
class TraceContextStatistics:
    """
    Runtime statistics.
    """

    updates: int = 0

    lookups: int = 0

    hits: int = 0

    misses: int = 0

    merges: int = 0

    resets: int = 0

    validations: int = 0

    failures: int = 0

    created_at: float = field(
        default_factory=time.time
    )

    updated_at: float = field(
        default_factory=time.time
    )


@dataclass(slots=True)
class TraceContextRecord:
    """
    One context entry.
    """

    key: str

    value: Any

    timestamp: float = field(
        default_factory=time.time
    )

    metadata: ContextMetadata = field(
        default_factory=dict
    )


@dataclass(slots=True)
class TraceContextSnapshot:
    """
    Snapshot returned by snapshot().
    """

    trace_id: str

    span_id: str

    parent_span_id: str

    state: str

    context: ContextData

    metadata: ContextMetadata

    created_at: float

    updated_at: float
# ==============================================================================
# Part 2. Constructor
# ==============================================================================

class TraceContext:
    """
    Runtime trace context.

    A TraceContext stores trace identifiers, baggage,
    metadata and arbitrary key-value context shared across
    spans during execution.
    """

    def __init__(
        self,
        *,
        name: str = DEFAULT_CONTEXT_NAME,
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
        trace_state: str = DEFAULT_TRACE_STATE,
        trace_flags: int = DEFAULT_TRACE_FLAGS,
        baggage: Optional[Mapping[str, str]] = None,
        metadata: Optional[ContextMetadata] = None,
        attributes: Optional[ContextAttributes] = None,
        context: Optional[ContextData] = None,
    ) -> None:

        # ==================================================================
        # Identity
        # ==================================================================

        self._id: str = str(
            uuid.uuid4()
        )

        self._uuid: uuid.UUID = uuid.UUID(
            self._id
        )

        self._name: str = str(name)

        self._version: str = CONTEXT_VERSION

        # ==================================================================
        # Trace Information
        # ==================================================================

        self._trace_id: str = (
            trace_id
            or uuid.uuid4().hex
        )

        self._span_id: str = (
            span_id
            or uuid.uuid4().hex[:16]
        )

        self._parent_span_id: str = (
            parent_span_id
            or DEFAULT_PARENT_SPAN_ID
        )

        self._trace_state: str = str(
            trace_state
        )

        self._trace_flags: int = int(
            trace_flags
        )

        self._baggage: Dict[str, str] = dict(
            baggage or {}
        )

        # ==================================================================
        # Runtime State
        # ==================================================================

        self._enabled: bool = True

        self._initialized: bool = False

        self._running: bool = False

        self._active: bool = False

        self._frozen: bool = False

        self._closed: bool = False

        self._state: TraceContextState = (
            TraceContextState.CREATED
        )

        self._created_at: float = time.time()

        self._updated_at: float = (
            self._created_at
        )

        self._last_access: Optional[float] = None

        self._last_update: Optional[float] = None

        # ==================================================================
        # Statistics
        # ==================================================================

        self._statistics = (
            TraceContextStatistics()
        )

        self._update_count: int = 0

        self._lookup_count: int = 0

        self._hit_count: int = 0

        self._miss_count: int = 0

        self._merge_count: int = 0

        self._reset_count: int = 0

        self._validation_count: int = 0

        self._failure_count: int = 0

        # ==================================================================
        # Metadata
        # ==================================================================

        self._metadata: ContextMetadata = dict(
            metadata or {}
        )

        self._attributes: ContextAttributes = dict(
            attributes or {}
        )

        self._context: ContextData = dict(
            context or {}
        )

        self._tags: List[str] = list(
            DEFAULT_TAGS
        )

        self._flags: TraceContextFlag = (
            TraceContextFlag.NONE
        )

        self._encoding: str = (
            DEFAULT_ENCODING
        )

        self._history_limit: int = (
            DEFAULT_HISTORY_LIMIT
        )

        # ==================================================================
        # Runtime Objects
        # ==================================================================

        self._lock = threading.RLock()

        self._hooks: Dict[
            str,
            List[ContextHook]
        ] = defaultdict(list)

        self._callbacks: List[
            ContextCallback
        ] = []

        self._filters: List[
            ContextFilter
        ] = []

        self._history: List[
            TraceContextRecord
        ] = []

        self._cache: MutableMapping[
            str,
            Any
        ] = {}

        self._runtime: Dict[
            str,
            Any
        ] = {}

        self._initialized = True

        self._state = (
            TraceContextState.INITIALIZED
        )
    # ==============================================================================
    # Part 3. Properties
    # ==============================================================================

    # ==============================================================================
    # Identity
    # ==============================================================================

    @property
    def id(self) -> str:
        """Unique context identifier."""
        return self._id


    # ------------------------------------------------------------------------------

    @property
    def uuid(self) -> uuid.UUID:
        """UUID object."""
        return self._uuid


    # ------------------------------------------------------------------------------

    @property
    def name(self) -> str:
        """Context name."""
        return self._name


    @name.setter
    def name(
        self,
        value: str,
    ) -> None:
        self._name = str(value)


    # ------------------------------------------------------------------------------

    @property
    def version(self) -> str:
        """Context version."""
        return self._version


    # ==============================================================================
    # Trace
    # ==============================================================================

    @property
    def trace_id(self) -> str:
        """Trace identifier."""
        return self._trace_id


    @trace_id.setter
    def trace_id(
        self,
        value: str,
    ) -> None:
        self._trace_id = str(value)


    # ------------------------------------------------------------------------------

    @property
    def span_id(self) -> str:
        """Current span identifier."""
        return self._span_id


    @span_id.setter
    def span_id(
        self,
        value: str,
    ) -> None:
        self._span_id = str(value)


    # ------------------------------------------------------------------------------

    @property
    def parent_span_id(self) -> str:
        """Parent span identifier."""
        return self._parent_span_id


    @parent_span_id.setter
    def parent_span_id(
        self,
        value: str,
    ) -> None:
        self._parent_span_id = str(value)


    # ------------------------------------------------------------------------------

    @property
    def trace_state(self) -> str:
        """Trace state."""
        return self._trace_state


    @trace_state.setter
    def trace_state(
        self,
        value: str,
    ) -> None:
        self._trace_state = str(value)


    # ------------------------------------------------------------------------------

    @property
    def trace_flags(self) -> int:
        """Trace flags."""
        return self._trace_flags


    @trace_flags.setter
    def trace_flags(
        self,
        value: int,
    ) -> None:
        self._trace_flags = int(value)


    # ------------------------------------------------------------------------------

    @property
    def baggage(self) -> Dict[str, str]:
        """Baggage entries."""
        return copy.deepcopy(
            self._baggage
        )


    # ==============================================================================
    # Runtime
    # ==============================================================================

    @property
    def enabled(self) -> bool:
        return self._enabled


    # ------------------------------------------------------------------------------

    @property
    def initialized(self) -> bool:
        return self._initialized


    # ------------------------------------------------------------------------------

    @property
    def running(self) -> bool:
        return self._running


    # ------------------------------------------------------------------------------

    @property
    def active(self) -> bool:
        return self._active


    # ------------------------------------------------------------------------------

    @property
    def frozen(self) -> bool:
        return self._frozen


    # ------------------------------------------------------------------------------

    @property
    def closed(self) -> bool:
        return self._closed


    # ------------------------------------------------------------------------------

    @property
    def state(self) -> TraceContextState:
        return self._state


    # ------------------------------------------------------------------------------

    @property
    def created_at(self) -> float:
        return self._created_at


    # ------------------------------------------------------------------------------

    @property
    def updated_at(self) -> float:
        return self._updated_at


    # ------------------------------------------------------------------------------

    @property
    def last_access(self) -> Optional[float]:
        return self._last_access


    # ------------------------------------------------------------------------------

    @property
    def last_update(self) -> Optional[float]:
        return self._last_update


    # ------------------------------------------------------------------------------

    @property
    def uptime(self) -> float:
        """Context lifetime in seconds."""
        return max(
            0.0,
            time.time() - self._created_at,
        )


    # ==============================================================================
    # Statistics
    # ==============================================================================

    @property
    def statistics(self) -> TraceContextStatistics:
        """Runtime statistics."""
        return copy.deepcopy(
            self._statistics
        )


    # ------------------------------------------------------------------------------

    @property
    def update_count(self) -> int:
        return self._update_count


    # ------------------------------------------------------------------------------

    @property
    def lookup_count(self) -> int:
        return self._lookup_count


    # ------------------------------------------------------------------------------

    @property
    def hit_count(self) -> int:
        return self._hit_count


    # ------------------------------------------------------------------------------

    @property
    def miss_count(self) -> int:
        return self._miss_count


    # ------------------------------------------------------------------------------

    @property
    def merge_count(self) -> int:
        return self._merge_count


    # ------------------------------------------------------------------------------

    @property
    def reset_count(self) -> int:
        return self._reset_count


    # ------------------------------------------------------------------------------

    @property
    def validation_count(self) -> int:
        return self._validation_count


    # ------------------------------------------------------------------------------

    @property
    def failure_count(self) -> int:
        return self._failure_count


    # ------------------------------------------------------------------------------

    @property
    def hit_rate(self) -> float:
        """
        Cache hit rate.
        """

        total = (
            self._hit_count
            + self._miss_count
        )

        if total == 0:
            return 0.0

        return self._hit_count / total


    # ------------------------------------------------------------------------------

    @property
    def miss_rate(self) -> float:
        """
        Cache miss rate.
        """

        total = (
            self._hit_count
            + self._miss_count
        )

        if total == 0:
            return 0.0

        return self._miss_count / total


    # ==============================================================================
    # Metadata
    # ==============================================================================

    @property
    def metadata(self) -> ContextMetadata:
        """Metadata dictionary."""
        return copy.deepcopy(
            self._metadata
        )


    # ------------------------------------------------------------------------------

    @property
    def attributes(self) -> ContextAttributes:
        """Attributes dictionary."""
        return copy.deepcopy(
            self._attributes
        )


    # ------------------------------------------------------------------------------

    @property
    def context(self) -> ContextData:
        """Context storage."""
        return copy.deepcopy(
            self._context
        )


    # ------------------------------------------------------------------------------

    @property
    def tags(self) -> List[str]:
        """Context tags."""
        return list(
            self._tags
        )


    # ------------------------------------------------------------------------------

    @property
    def flags(self) -> TraceContextFlag:
        """Context flags."""
        return self._flags


    # ------------------------------------------------------------------------------

    @property
    def encoding(self) -> str:
        """Serialization encoding."""
        return self._encoding


    # ------------------------------------------------------------------------------

    @property
    def history_limit(self) -> int:
        """Maximum history size."""
        return self._history_limit


    # ------------------------------------------------------------------------------

    @property
    def history(
        self,
    ) -> List[TraceContextRecord]:
        """History buffer."""
        return list(
            self._history
        )


    # ------------------------------------------------------------------------------

    @property
    def cache(
        self,
    ) -> Dict[str, Any]:
        """Runtime cache."""
        return dict(
            self._cache
        )


    # ------------------------------------------------------------------------------

    @property
    def callbacks(
        self,
    ) -> List[ContextCallback]:
        """Registered callbacks."""
        return list(
            self._callbacks
        )


    # ------------------------------------------------------------------------------

    @property
    def hooks(
        self,
    ) -> Dict[
        str,
        List[ContextHook],
    ]:
        """Registered hooks."""

        return {

            event: list(callbacks)

            for event, callbacks

            in self._hooks.items()

        }


    # ------------------------------------------------------------------------------

    @property
    def filters(
        self,
    ) -> List[ContextFilter]:
        """Registered filters."""
        return list(
            self._filters
        )
    # ==============================================================================
    # Part 4. Context API
    # ==============================================================================

    def set(
        self,
        key: ContextKey,
        value: ContextValue,
    ) -> "TraceContext":
        """
        Set a context value.

        Parameters
        ----------
        key:
            Context key.

        value:
            Context value.

        Returns
        -------
        TraceContext
        """

        self.validate_key(
            key,
            raise_error=True,
        )

        self.validate_value(
            value,
            raise_error=True,
        )

        with self._lock:

            self._context[key] = value

            self._history.append(

                TraceContextRecord(
                    key=key,
                    value=copy.deepcopy(value),
                )

            )

            if len(self._history) > self._history_limit:

                self._history.pop(0)

            self._update_count += 1

            self._statistics.updates += 1

            self._updated_at = time.time()

            self._last_update = self._updated_at

        return self


    # ------------------------------------------------------------------------------

    def get(
        self,
        key: ContextKey,
        default: Any = None,
    ) -> Any:
        """
        Get a context value.
        """

        self._lookup_count += 1

        self._statistics.lookups += 1

        self._last_access = time.time()

        if key in self._context:

            self._hit_count += 1

            self._statistics.hits += 1

            return self._context[key]

        self._miss_count += 1

        self._statistics.misses += 1

        return default


    # ------------------------------------------------------------------------------

    def update(
        self,
        data: Mapping[
            ContextKey,
            ContextValue,
        ],
    ) -> "TraceContext":
        """
        Update multiple context values.
        """

        if not isinstance(
            data,
            Mapping,
        ):
            raise TypeError(
                "data must be a mapping"
            )

        for key, value in data.items():

            self.set(
                key,
                value,
            )

        return self


    # ------------------------------------------------------------------------------

    def remove(
        self,
        key: ContextKey,
        *,
        default: Any = None,
    ) -> Any:
        """
        Remove one context entry.
        """

        with self._lock:

            value = self._context.pop(
                key,
                default,
            )

            self._updated_at = time.time()

            self._last_update = self._updated_at

        return value


    # ------------------------------------------------------------------------------

    def clear(
        self,
    ) -> "TraceContext":
        """
        Remove all context entries.
        """

        with self._lock:

            self._context.clear()

            self._updated_at = time.time()

            self._last_update = self._updated_at

        return self


    # ------------------------------------------------------------------------------

    def contains(
        self,
        key: ContextKey,
    ) -> bool:
        """
        Return True if key exists.
        """

        return key in self._context


    # ------------------------------------------------------------------------------

    def keys(
        self,
    ) -> List[ContextKey]:
        """
        Return context keys.
        """

        return list(
            self._context.keys()
        )


    # ------------------------------------------------------------------------------

    def values(
        self,
    ) -> List[ContextValue]:
        """
        Return context values.
        """

        return list(
            self._context.values()
        )


    # ------------------------------------------------------------------------------

    def items(
        self,
    ) -> List[
        tuple[
            ContextKey,
            ContextValue,
        ]
    ]:
        """
        Return context items.
        """

        return list(
            self._context.items()
        )


    # ------------------------------------------------------------------------------

    def merge(
        self,
        other: Union[
            "TraceContext",
            Mapping[
                ContextKey,
                ContextValue,
            ],
        ],
        *,
        overwrite: bool = True,
    ) -> "TraceContext":
        """
        Merge another context.

        Parameters
        ----------
        other:
            TraceContext or Mapping.

        overwrite:
            Whether existing keys are replaced.

        Returns
        -------
        TraceContext
        """

        if isinstance(
            other,
            TraceContext,
        ):

            source = other._context

        elif isinstance(
            other,
            Mapping,
        ):

            source = other

        else:

            raise TypeError(
                "other must be TraceContext or Mapping"
            )

        with self._lock:

            for key, value in source.items():

                if (

                    overwrite

                    or key not in self._context

                ):

                    self._context[key] = copy.deepcopy(
                        value
                    )

            self._merge_count += 1

            self._statistics.merges += 1

            self._updated_at = time.time()

            self._last_update = self._updated_at

        return self
    # ==============================================================================
    # Part 5. Runtime Operations
    # ==============================================================================

    def snapshot(
        self,
    ) -> TraceContextSnapshot:
        """
        Create an immutable snapshot of the current context.

        Returns
        -------
        TraceContextSnapshot
        """

        return TraceContextSnapshot(

            trace_id=self._trace_id,

            span_id=self._span_id,

            parent_span_id=self._parent_span_id,

            state=self._state.value,

            context=copy.deepcopy(
                self._context
            ),

            metadata=copy.deepcopy(
                self._metadata
            ),

            created_at=self._created_at,

            updated_at=self._updated_at,

        )


    # ------------------------------------------------------------------------------

    def restore(
        self,
        snapshot: Union[
            TraceContextSnapshot,
            Mapping[str, Any],
        ],
    ) -> "TraceContext":
        """
        Restore runtime state from a snapshot.

        Parameters
        ----------
        snapshot:
            TraceContextSnapshot or dictionary.

        Returns
        -------
        TraceContext
        """

        if isinstance(
            snapshot,
            TraceContextSnapshot,
        ):

            data = snapshot.__dict__

        elif isinstance(
            snapshot,
            Mapping,
        ):

            data = snapshot

        else:

            raise TypeError(
                "snapshot must be TraceContextSnapshot or Mapping"
            )

        with self._lock:

            self._trace_id = data.get(
                "trace_id",
                self._trace_id,
            )

            self._span_id = data.get(
                "span_id",
                self._span_id,
            )

            self._parent_span_id = data.get(
                "parent_span_id",
                self._parent_span_id,
            )

            self._state = TraceContextState(

                data.get(
                    "state",
                    self._state.value,
                )

            )

            self._context = copy.deepcopy(

                data.get(
                    "context",
                    self._context,
                )

            )

            self._metadata = copy.deepcopy(

                data.get(
                    "metadata",
                    self._metadata,
                )

            )

            self._created_at = data.get(
                "created_at",
                self._created_at,
            )

            self._updated_at = data.get(
                "updated_at",
                self._updated_at,
            )

            self._last_update = time.time()

        return self


    # ------------------------------------------------------------------------------

    def clone(
        self,
    ) -> "TraceContext":
        """
        Create a deep clone of this context.

        Returns
        -------
        TraceContext
        """

        return copy.deepcopy(
            self
        )


    # ------------------------------------------------------------------------------

    def copy(
        self,
    ) -> "TraceContext":
        """
        Create a shallow copy.

        Returns
        -------
        TraceContext
        """

        return copy.copy(
            self
        )


    # ------------------------------------------------------------------------------

    def reset(
        self,
    ) -> "TraceContext":
        """
        Reset runtime state while preserving identity.

        Returns
        -------
        TraceContext
        """

        with self._lock:

            self._context.clear()

            self._metadata.clear()

            self._attributes.clear()

            self._baggage.clear()

            self._history.clear()

            self._cache.clear()

            self._tags.clear()

            self._statistics = TraceContextStatistics()

            self._update_count = 0

            self._lookup_count = 0

            self._hit_count = 0

            self._miss_count = 0

            self._merge_count = 0

            self._reset_count += 1

            self._validation_count = 0

            self._failure_count = 0

            self._last_access = None

            self._last_update = None

            self._state = (
                TraceContextState.INITIALIZED
            )

            self._updated_at = time.time()

        return self


    # ------------------------------------------------------------------------------

    def compact(
        self,
    ) -> "TraceContext":
        """
        Compact runtime memory usage.

        - Trim history.
        - Clear transient cache.

        Returns
        -------
        TraceContext
        """

        with self._lock:

            if len(
                self._history
            ) > self._history_limit:

                self._history = self._history[
                    -self._history_limit:
                ]

            self._cache.clear()

            self._updated_at = time.time()

        return self


    # ------------------------------------------------------------------------------

    def cleanup(
        self,
    ) -> "TraceContext":
        """
        Cleanup temporary runtime objects.

        Does not remove context values.

        Returns
        -------
        TraceContext
        """

        with self._lock:

            self._cache.clear()

            self._callbacks.clear()

            self._filters.clear()

            self._hooks.clear()

            self._updated_at = time.time()

        return self
    # ==============================================================================
    # Part 6. Statistics & Diagnostics
    # ==============================================================================

    def summary(
        self,
    ) -> Dict[str, Any]:
        """
        Return a concise summary of the trace context.
        """

        return {

            # ------------------------------------------------------------------
            # Identity
            # ------------------------------------------------------------------

            "id": self._id,

            "name": self._name,

            "trace_id": self._trace_id,

            "span_id": self._span_id,

            # ------------------------------------------------------------------
            # Runtime
            # ------------------------------------------------------------------

            "state": self._state.value,

            "enabled": self._enabled,

            "running": self._running,

            "active": self._active,

            # ------------------------------------------------------------------
            # Statistics
            # ------------------------------------------------------------------

            "updates": self._update_count,

            "lookups": self._lookup_count,

            "hits": self._hit_count,

            "misses": self._miss_count,

            "hit_rate": self.hit_rate,

            "uptime": self.uptime,

        }


    # ------------------------------------------------------------------------------

    def report(
        self,
    ) -> Dict[str, Any]:
        """
        Return a complete runtime report.
        """

        return {

            "identity": {

                "id": self._id,

                "uuid": str(
                    self._uuid
                ),

                "name": self._name,

                "version": self._version,

            },

            "trace": {

                "trace_id": self._trace_id,

                "span_id": self._span_id,

                "parent_span_id": self._parent_span_id,

                "trace_state": self._trace_state,

                "trace_flags": self._trace_flags,

                "baggage": copy.deepcopy(
                    self._baggage
                ),

            },

            "runtime": {

                "state": self._state.value,

                "enabled": self._enabled,

                "initialized": self._initialized,

                "running": self._running,

                "active": self._active,

                "frozen": self._frozen,

                "closed": self._closed,

                "created_at": self._created_at,

                "updated_at": self._updated_at,

                "last_access": self._last_access,

                "last_update": self._last_update,

                "uptime": self.uptime,

            },

            "statistics": {

                "updates": self._update_count,

                "lookups": self._lookup_count,

                "hits": self._hit_count,

                "misses": self._miss_count,

                "merges": self._merge_count,

                "resets": self._reset_count,

                "validations": self._validation_count,

                "failures": self._failure_count,

                "hit_rate": self.hit_rate,

                "miss_rate": self.miss_rate,

                "statistics": copy.deepcopy(
                    self._statistics
                ),

            },

            "metadata": {

                "metadata": copy.deepcopy(
                    self._metadata
                ),

                "attributes": copy.deepcopy(
                    self._attributes
                ),

                "context_size": len(
                    self._context
                ),

                "tags": list(
                    self._tags
                ),

                "flags": str(
                    self._flags
                ),

                "encoding": self._encoding,

            },

        }


    # ------------------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> Dict[str, Any]:
        """
        Return diagnostic information.
        """

        return {

            "healthy": (

                self._enabled

                and not self._closed

                and not self._frozen

            ),

            "integrity": self.check_integrity(),

            "state": self._state.value,

            "history_size": len(
                self._history
            ),

            "cache_size": len(
                self._cache
            ),

            "context_size": len(
                self._context
            ),

            "callback_count": len(
                self._callbacks
            ),

            "hook_count": sum(

                len(v)

                for v in self._hooks.values()

            ),

            "filter_count": len(
                self._filters
            ),

        }


    # ------------------------------------------------------------------------------

    def health(
        self,
    ) -> Dict[str, Any]:
        """
        Return runtime health information.
        """

        healthy = (

            self._enabled

            and self._initialized

            and not self._closed

            and not self._frozen

        )

        return {

            "healthy": healthy,

            "state": self._state.value,

            "enabled": self._enabled,

            "running": self._running,

            "active": self._active,

            "failures": self._failure_count,

            "uptime": self.uptime,

        }


    # ------------------------------------------------------------------------------

    def metrics(
        self,
    ) -> Dict[str, Union[int, float]]:
        """
        Return numeric runtime metrics.
        """

        return {

            "update_count": self._update_count,

            "lookup_count": self._lookup_count,

            "hit_count": self._hit_count,

            "miss_count": self._miss_count,

            "merge_count": self._merge_count,

            "reset_count": self._reset_count,

            "validation_count": self._validation_count,

            "failure_count": self._failure_count,

            "history_size": len(
                self._history
            ),

            "cache_size": len(
                self._cache
            ),

            "context_size": len(
                self._context
            ),

            "hit_rate": self.hit_rate,

            "miss_rate": self.miss_rate,

            "uptime": self.uptime,

        }
    # ==============================================================================
    # Part 7. Validation
    # ==============================================================================

    def validate(
        self,
        *,
        raise_error: bool = False,
    ) -> bool:
        """
        Validate the complete TraceContext.

        Returns
        -------
        bool
            True if the context is valid.
        """

        self._validation_count += 1

        validators = (

            self.validate_context,

            self.check_integrity,

        )

        try:

            for validator in validators:

                validator(
                    raise_error=True,
                )

            return True

        except Exception:

            self._failure_count += 1

            if raise_error:
                raise

            return False


    # ------------------------------------------------------------------------------

    def validate_key(
        self,
        key: ContextKey,
        *,
        raise_error: bool = False,
    ) -> bool:
        """
        Validate a context key.
        """

        try:

            if not isinstance(
                key,
                str,
            ):
                raise TypeError(
                    "context key must be str"
                )

            if not key.strip():
                raise ValueError(
                    "context key cannot be empty"
                )

            return True

        except Exception:

            if raise_error:
                raise

            return False


    # ------------------------------------------------------------------------------

    def validate_value(
        self,
        value: ContextValue,
        *,
        raise_error: bool = False,
    ) -> bool:
        """
        Validate a context value.
        """

        try:

            #
            # None is allowed.
            #
            # Context values may be arbitrary Python objects.
            #

            if isinstance(
                value,
                (
                    threading.Lock,
                    threading.RLock,
                ),
            ):
                raise TypeError(
                    "thread lock objects cannot be stored in context"
                )

            return True

        except Exception:

            if raise_error:
                raise

            return False


    # ------------------------------------------------------------------------------

    def validate_context(
        self,
        *,
        raise_error: bool = False,
    ) -> bool:
        """
        Validate the entire context dictionary.
        """

        try:

            if not isinstance(
                self._context,
                MutableMapping,
            ):
                raise TypeError(
                    "context must be a mutable mapping"
                )

            for key, value in self._context.items():

                self.validate_key(
                    key,
                    raise_error=True,
                )

                self.validate_value(
                    value,
                    raise_error=True,
                )

            return True

        except Exception:

            if raise_error:
                raise

            return False


    # ------------------------------------------------------------------------------

    def check_integrity(
        self,
        *,
        raise_error: bool = False,
    ) -> bool:
        """
        Verify internal runtime integrity.
        """

        try:

            runtime_objects = (

                self._statistics,

                self._metadata,

                self._attributes,

                self._context,

                self._history,

                self._cache,

                self._hooks,

                self._callbacks,

                self._filters,

                self._lock,

            )

            if any(
                obj is None
                for obj in runtime_objects
            ):
                raise RuntimeError(
                    "runtime object is not initialized"
                )

            if not isinstance(
                self._trace_id,
                str,
            ):
                raise TypeError(
                    "trace_id must be str"
                )

            if not isinstance(
                self._span_id,
                str,
            ):
                raise TypeError(
                    "span_id must be str"
                )

            if self._history_limit <= 0:
                raise ValueError(
                    "history_limit must be positive"
                )

            if self._encoding == "":
                raise ValueError(
                    "encoding cannot be empty"
                )

            return True

        except Exception:

            if raise_error:
                raise

            return False
    # ==============================================================================
    # Part 8. Events & Hooks
    # ==============================================================================

    def before_update(
        self,
        key: Optional[ContextKey] = None,
        value: Any = None,
    ) -> None:
        """
        Hook executed before a context update.
        """

        self.emit_event(
            "before_update",
            context=self,
            key=key,
            value=value,
        )


    # ------------------------------------------------------------------------------

    def after_update(
        self,
        key: Optional[ContextKey] = None,
        value: Any = None,
    ) -> None:
        """
        Hook executed after a context update.
        """

        self.emit_event(
            "after_update",
            context=self,
            key=key,
            value=value,
        )


    # ------------------------------------------------------------------------------

    def add_hook(
        self,
        event: str,
        hook: ContextHook,
    ) -> "TraceContext":
        """
        Register an event hook.

        Parameters
        ----------
        event:
            Event name.

        hook:
            Callable to execute.

        Returns
        -------
        TraceContext
        """

        if not callable(hook):
            raise TypeError(
                "hook must be callable"
            )

        with self._lock:

            if hook not in self._hooks[event]:

                self._hooks[event].append(
                    hook
                )

        return self


    # ------------------------------------------------------------------------------

    def remove_hook(
        self,
        event: str,
        hook: ContextHook,
    ) -> "TraceContext":
        """
        Remove a registered hook.
        """

        with self._lock:

            hooks = self._hooks.get(event)

            if hooks is None:
                return self

            try:

                hooks.remove(hook)

            except ValueError:

                pass

            if not hooks:

                self._hooks.pop(
                    event,
                    None,
                )

        return self


    # ------------------------------------------------------------------------------

    def clear_hooks(
        self,
        event: Optional[str] = None,
    ) -> "TraceContext":
        """
        Clear hooks.

        Parameters
        ----------
        event:
            If None, remove all hooks.
            Otherwise remove hooks for one event.
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


    # ------------------------------------------------------------------------------

    def emit_event(
        self,
        event: str,
        *args,
        **kwargs,
    ) -> None:
        """
        Emit an event.

        Hook failures never interrupt TraceContext execution.
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
                    *args,
                    **kwargs,
                )

            except Exception:

                #
                # Hooks should never break
                # runtime execution.
                #
                continue

        #
        # Notify subscribers.
        #
        self.notify_callbacks(
            event,
            *args,
            **kwargs,
        )
    # ==============================================================================
    # Part 9. Callbacks
    # ==============================================================================

    def subscribe(
        self,
        callback: ContextCallback,
    ) -> "TraceContext":
        """
        Subscribe a callback.

        Parameters
        ----------
        callback:
            Callable receiving emitted events.

        Returns
        -------
        TraceContext
        """

        if not callable(callback):
            raise TypeError(
                "callback must be callable"
            )

        with self._lock:

            if callback not in self._callbacks:

                self._callbacks.append(
                    callback
                )

        return self


    # ------------------------------------------------------------------------------

    def unsubscribe(
        self,
        callback: ContextCallback,
    ) -> "TraceContext":
        """
        Unsubscribe a callback.

        Parameters
        ----------
        callback:
            Previously subscribed callback.

        Returns
        -------
        TraceContext
        """

        with self._lock:

            try:

                self._callbacks.remove(
                    callback
                )

            except ValueError:

                pass

        return self


    # ------------------------------------------------------------------------------

    def clear_callbacks(
        self,
    ) -> "TraceContext":
        """
        Remove all registered callbacks.

        Returns
        -------
        TraceContext
        """

        with self._lock:

            self._callbacks.clear()

        return self


    # ------------------------------------------------------------------------------

    def notify_callbacks(
        self,
        event: str,
        *args,
        **kwargs,
    ) -> None:
        """
        Notify all subscribed callbacks.

        Parameters
        ----------
        event:
            Event name.

        Notes
        -----
        Callback failures never interrupt runtime execution.
        """

        callbacks = tuple(
            self._callbacks
        )

        for callback in callbacks:

            try:

                callback(
                    event,
                    *args,
                    **kwargs,
                )

            except Exception:

                #
                # User callbacks must never
                # interrupt TraceContext.
                #
                continue
    # ==============================================================================
    # Part 10. Serialization Helpers
    # ==============================================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Serialize this TraceContext to a dictionary.

        Returns
        -------
        Dict[str, Any]
        """

        return {

            # ------------------------------------------------------------------
            # Identity
            # ------------------------------------------------------------------

            "id": self._id,

            "uuid": str(self._uuid),

            "name": self._name,

            "version": self._version,

            # ------------------------------------------------------------------
            # Trace
            # ------------------------------------------------------------------

            "trace_id": self._trace_id,

            "span_id": self._span_id,

            "parent_span_id": self._parent_span_id,

            "trace_state": self._trace_state,

            "trace_flags": self._trace_flags,

            "baggage": copy.deepcopy(
                self._baggage
            ),

            # ------------------------------------------------------------------
            # Runtime
            # ------------------------------------------------------------------

            "enabled": self._enabled,

            "initialized": self._initialized,

            "running": self._running,

            "active": self._active,

            "frozen": self._frozen,

            "closed": self._closed,

            "state": self._state.value,

            "created_at": self._created_at,

            "updated_at": self._updated_at,

            "last_access": self._last_access,

            "last_update": self._last_update,

            # ------------------------------------------------------------------
            # Statistics
            # ------------------------------------------------------------------

            "statistics": copy.deepcopy(
                self._statistics
            ),

            "update_count": self._update_count,

            "lookup_count": self._lookup_count,

            "hit_count": self._hit_count,

            "miss_count": self._miss_count,

            "merge_count": self._merge_count,

            "reset_count": self._reset_count,

            "validation_count": self._validation_count,

            "failure_count": self._failure_count,

            # ------------------------------------------------------------------
            # Metadata
            # ------------------------------------------------------------------

            "metadata": copy.deepcopy(
                self._metadata
            ),

            "attributes": copy.deepcopy(
                self._attributes
            ),

            "context": copy.deepcopy(
                self._context
            ),

            "tags": list(
                self._tags
            ),

            "flags": int(
                self._flags
            ),

            "encoding": self._encoding,

            "history_limit": self._history_limit,

        }


    # ------------------------------------------------------------------------------

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "TraceContext":
        """
        Create a TraceContext from a dictionary.

        Parameters
        ----------
        data:
            Serialized context dictionary.

        Returns
        -------
        TraceContext
        """

        if not isinstance(
            data,
            Mapping,
        ):
            raise TypeError(
                "data must be a mapping"
            )

        obj = cls(

            name=data.get(
                "name",
                DEFAULT_CONTEXT_NAME,
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

            trace_state=data.get(
                "trace_state",
                DEFAULT_TRACE_STATE,
            ),

            trace_flags=data.get(
                "trace_flags",
                DEFAULT_TRACE_FLAGS,
            ),

            baggage=data.get(
                "baggage",
                {},
            ),

            metadata=data.get(
                "metadata",
                {},
            ),

            attributes=data.get(
                "attributes",
                {},
            ),

            context=data.get(
                "context",
                {},
            ),

        )

        obj._enabled = data.get(
            "enabled",
            True,
        )

        obj._initialized = data.get(
            "initialized",
            True,
        )

        obj._running = data.get(
            "running",
            False,
        )

        obj._active = data.get(
            "active",
            False,
        )

        obj._frozen = data.get(
            "frozen",
            False,
        )

        obj._closed = data.get(
            "closed",
            False,
        )

        obj._state = TraceContextState(

            data.get(
                "state",
                TraceContextState.CREATED.value,
            )

        )

        obj._created_at = data.get(
            "created_at",
            obj._created_at,
        )

        obj._updated_at = data.get(
            "updated_at",
            obj._updated_at,
        )

        obj._last_access = data.get(
            "last_access",
        )

        obj._last_update = data.get(
            "last_update",
        )

        statistics = data.get(
            "statistics",
        )

        if isinstance(
            statistics,
            TraceContextStatistics,
        ):
            obj._statistics = copy.deepcopy(
                statistics
            )

        obj._update_count = data.get(
            "update_count",
            0,
        )

        obj._lookup_count = data.get(
            "lookup_count",
            0,
        )

        obj._hit_count = data.get(
            "hit_count",
            0,
        )

        obj._miss_count = data.get(
            "miss_count",
            0,
        )

        obj._merge_count = data.get(
            "merge_count",
            0,
        )

        obj._reset_count = data.get(
            "reset_count",
            0,
        )

        obj._validation_count = data.get(
            "validation_count",
            0,
        )

        obj._failure_count = data.get(
            "failure_count",
            0,
        )

        obj._tags = list(
            data.get(
                "tags",
                [],
            )
        )

        obj._flags = TraceContextFlag(
            data.get(
                "flags",
                0,
            )
        )

        obj._encoding = data.get(
            "encoding",
            DEFAULT_ENCODING,
        )

        obj._history_limit = data.get(
            "history_limit",
            DEFAULT_HISTORY_LIMIT,
        )

        return obj


    # ------------------------------------------------------------------------------

    def to_json(
        self,
        *,
        indent: Optional[int] = 2,
        ensure_ascii: bool = False,
    ) -> str:
        """
        Serialize TraceContext to JSON.

        Parameters
        ----------
        indent:
            JSON indentation.

        ensure_ascii:
            JSON encoding option.

        Returns
        -------
        str
        """

        return json.dumps(

            self.to_dict(),

            indent=indent,

            ensure_ascii=ensure_ascii,

            default=str,

        )


    # ------------------------------------------------------------------------------

    @classmethod
    def from_json(
        cls,
        payload: Union[str, bytes],
    ) -> "TraceContext":
        """
        Deserialize TraceContext from JSON.

        Parameters
        ----------
        payload:
            JSON string or bytes.

        Returns
        -------
        TraceContext
        """

        if isinstance(
            payload,
            bytes,
        ):
            payload = payload.decode(
                DEFAULT_ENCODING
            )

        if not isinstance(
            payload,
            str,
        ):
            raise TypeError(
                "payload must be str or bytes"
            )

        return cls.from_dict(

            json.loads(
                payload
            )

        )
    # ==============================================================================
    # Part 11. Utilities
    # ==============================================================================

    def exists(
        self,
        key: ContextKey,
    ) -> bool:
        """
        Return whether a context key exists.

        Parameters
        ----------
        key:
            Context key.

        Returns
        -------
        bool
        """

        return key in self._context


    # ------------------------------------------------------------------------------

    def get_or_default(
        self,
        key: ContextKey,
        default: Any = None,
    ) -> Any:
        """
        Return a context value or the supplied default.

        This method is equivalent to dict.get() while also
        updating runtime lookup statistics.

        Parameters
        ----------
        key:
            Context key.

        default:
            Value returned if the key does not exist.

        Returns
        -------
        Any
        """

        return self.get(
            key,
            default,
        )


    # ------------------------------------------------------------------------------

    def touch(
        self,
    ) -> "TraceContext":
        """
        Update the last modification timestamp.

        Returns
        -------
        TraceContext
        """

        now = time.time()

        self._updated_at = now

        self._last_update = now

        return self


    # ------------------------------------------------------------------------------

    def age(
        self,
    ) -> float:
        """
        Return the context age in seconds.

        Returns
        -------
        float
        """

        return max(
            0.0,
            time.time() - self._created_at,
        )


    # ------------------------------------------------------------------------------

    def timestamp(
        self,
    ) -> float:
        """
        Return the current Unix timestamp.

        Returns
        -------
        float
        """

        return time.time()


    # ------------------------------------------------------------------------------

    def size(
        self,
    ) -> int:
        """
        Return the number of context entries.

        Returns
        -------
        int
        """

        return len(
            self._context
        )


    # ------------------------------------------------------------------------------

    def clear_metadata(
        self,
    ) -> "TraceContext":
        """
        Remove all metadata entries.

        Returns
        -------
        TraceContext
        """

        with self._lock:

            self._metadata.clear()

            self.touch()

        return self


    # ------------------------------------------------------------------------------

    def clear_attributes(
        self,
    ) -> "TraceContext":
        """
        Remove all attributes.

        Returns
        -------
        TraceContext
        """

        with self._lock:

            self._attributes.clear()

            self.touch()

        return self
    # ==============================================================================
    # Part 12. Python Protocols
    # ==============================================================================

    def __repr__(
        self,
    ) -> str:
        """
        Developer-friendly representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"id={self._id!r}, "
            f"name={self._name!r}, "
            f"trace_id={self._trace_id!r}, "
            f"span_id={self._span_id!r}, "
            f"state={self._state.value!r}, "
            f"size={len(self._context)})"
        )


    # ------------------------------------------------------------------------------

    def __str__(
        self,
    ) -> str:
        """
        Human-readable representation.
        """

        return (
            f"{self._name}"
            f"("
            f"{self._trace_id}:"
            f"{self._span_id}"
            f")"
        )


    # ------------------------------------------------------------------------------

    def __len__(
        self,
    ) -> int:
        """
        Number of context entries.
        """

        return len(
            self._context
        )


    # ------------------------------------------------------------------------------

    def __iter__(
        self,
    ) -> Iterator[Tuple[ContextKey, ContextValue]]:
        """
        Iterate over context items.
        """

        return iter(
            self._context.items()
        )


    # ------------------------------------------------------------------------------

    def __contains__(
        self,
        key: object,
    ) -> bool:
        """
        Membership test.

        Examples
        --------
        >>> "user_id" in context
        """

        return key in self._context


    # ------------------------------------------------------------------------------

    def __getitem__(
        self,
        key: ContextKey,
    ) -> ContextValue:
        """
        Dictionary-style lookup.

        Examples
        --------
        >>> context["trace_id"]
        """

        return self.get(
            key
        )


    # ------------------------------------------------------------------------------

    def __setitem__(
        self,
        key: ContextKey,
        value: ContextValue,
    ) -> None:
        """
        Dictionary-style assignment.

        Examples
        --------
        >>> context["user"] = "alice"
        """

        self.set(
            key,
            value,
        )


    # ------------------------------------------------------------------------------

    def __delitem__(
        self,
        key: ContextKey,
    ) -> None:
        """
        Dictionary-style deletion.

        Examples
        --------
        >>> del context["user"]
        """

        self.remove(
            key
        )


    # ------------------------------------------------------------------------------

    def __bool__(
        self,
    ) -> bool:
        """
        Truth value of the context.

        Returns True only when the context
        is available for use.
        """

        return (

            self._enabled

            and not self._closed

            and not self._frozen

        )


    # ------------------------------------------------------------------------------

    def __copy__(
        self,
    ) -> "TraceContext":
        """
        Shallow copy.
        """

        return self.copy()


    # ------------------------------------------------------------------------------

    def __deepcopy__(
        self,
        memo: Dict[int, Any],
    ) -> "TraceContext":
        """
        Deep copy.

        Thread locks are recreated instead
        of being copied.
        """

        cls = self.__class__

        obj = cls.__new__(cls)

        memo[id(self)] = obj

        for key, value in self.__dict__.items():

            if key == "_lock":

                setattr(
                    obj,
                    key,
                    threading.RLock(),
                )

            else:

                setattr(
                    obj,
                    key,
                    copy.deepcopy(
                        value,
                        memo,
                    ),
                )

        return obj


    # ------------------------------------------------------------------------------

    def __eq__(
        self,
        other: object,
    ) -> bool:
        """
        Equality comparison.

        Equality is based on the unique id.
        """

        if not isinstance(
            other,
            TraceContext,
        ):
            return NotImplemented

        return self._id == other._id


    # ------------------------------------------------------------------------------

    def __hash__(
        self,
    ) -> int:
        """
        Hash based on the unique id.
        """

        return hash(
            self._id
        )
    # ==============================================================================
    # Part 13. Context Manager
    # ==============================================================================

    def __enter__(
        self,
    ) -> "TraceContext":
        """
        Enter the runtime context.

        Returns
        -------
        TraceContext
            The current TraceContext instance.

        Notes
        -----
        Automatically initializes and starts the context
        if necessary.

        Examples
        --------
        >>> with TraceContext() as ctx:
        ...     ctx["user"] = "alice"
        """

        if self._closed:
            self.reopen()

        if not self._initialized:
            self.initialize()

        if not self._running:
            self.start()

        self._active = True

        self._last_access = time.time()

        return self


    # ------------------------------------------------------------------------------

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> bool:
        """
        Exit the runtime context.

        Parameters
        ----------
        exc_type
            Exception type.

        exc_value
            Exception instance.

        traceback
            Python traceback object.

        Returns
        -------
        bool
            False so any exception is propagated.

        Notes
        -----
        Always stops the context before leaving.

        Examples
        --------
        >>> with TraceContext() as ctx:
        ...     ...
        """

        self._last_access = time.time()

        self._active = False

        if self._running:
            self.stop()

        #
        # Returning False propagates any exception.
        #
        return False
# ==============================================================================
# Part 14. Public API
# ==============================================================================

# ==============================================================================
# Compatibility aliases
# ==============================================================================


__all__ = [

    # ------------------------------------------------------------------
    # Constants
    # ------------------------------------------------------------------

    "DEFAULT_CONTEXT_NAME",
    "DEFAULT_TRACE_STATE",
    "DEFAULT_TRACE_FLAGS",
    "DEFAULT_ENCODING",
    "DEFAULT_HISTORY_LIMIT",
    "TRACE_CONTEXT_VERSION",

    # ------------------------------------------------------------------
    # Type Aliases
    # ------------------------------------------------------------------

    "ContextKey",
    "ContextValue",
    "ContextData",
    "ContextMetadata",
    "ContextAttributes",
    "ContextHook",
    "ContextCallback",
    "ContextFilter",

    # ------------------------------------------------------------------
    # Exceptions
    # ------------------------------------------------------------------

    "TraceContextError",
    "TraceContextValidationError",
    "TraceContextClosedError",
    "TraceContextFrozenError",

    # ------------------------------------------------------------------
    # Enums
    # ------------------------------------------------------------------

    "TraceContextState",
    "TraceContextFlag",

    # ------------------------------------------------------------------
    # Dataclasses
    # ------------------------------------------------------------------

    "TraceContextStatistics",

    # ------------------------------------------------------------------
    # Main Class
    # ------------------------------------------------------------------

    "TraceContext",

    # Compatibility aliases
    "TraceScope",
    "SpanScope",
    "trace_scope",
    "span_scope",

] 
class TraceScope:
    def __init__(self, manager, name, **kwargs):
        self.manager = manager
        self.name = name
        self.kwargs = kwargs
        self.trace = None

    def __enter__(self):
        self.trace = self.manager.start_trace(
            self.name,
            **self.kwargs,
        )
        return self.trace

    def __exit__(self, exc_type, exc, tb):
        if self.trace is not None:
            self.trace.finish()
        return False
class SpanScope:
    def __init__(self, manager, name, **kwargs):
        self.manager = manager
        self.name = name
        self.kwargs = kwargs
        self.span = None

    def __enter__(self):
        self.span = self.manager.start_span(
            self.name,
            **self.kwargs,
        )
        return self.span

    def __exit__(self, exc_type, exc, tb):
        if self.span is not None:
            self.span.finish()
        return False

from functools import wraps
def trace_scope(manager, name, **kwargs):

    def decorator(fn):

        @wraps(fn)
        def wrapper(*args, **kw):

            with TraceScope(manager, name, **kwargs):
                return fn(*args, **kw)

        return wrapper

    return decorator

def span_scope(manager, name, **kwargs):

    def decorator(fn):

        @wraps(fn)
        def wrapper(*args, **kw):

            with SpanScope(manager, name, **kwargs):
                return fn(*args, **kw)

        return wrapper

    return decorator


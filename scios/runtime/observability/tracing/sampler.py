# ==============================================================================
# SciOS Runtime Observability
# Trace Sampler
# ==============================================================================
#
# File:
#     scios/runtime/observability/tracing/sampler.py
#
# Python 3.11+
# ==============================================================================

from __future__ import annotations

# ==============================================================================
# Part 1. Foundation
# ==============================================================================

from abc import ABC
from collections import defaultdict, deque
from copy import deepcopy
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Flag, IntFlag, auto, Enum
import json
import random as _random
import threading
import time
import uuid
from typing import (
    Any,
    Callable,
    Deque,
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    TypeAlias,
)


# ==============================================================================
# Constants
# ==============================================================================

DEFAULT_SAMPLER_NAME: str = "TraceSampler"
DEFAULT_SAMPLE_RATE: float = 1.0
DEFAULT_SEED: Optional[int] = None
DEFAULT_HISTORY_LIMIT: int = 1024
DEFAULT_ENCODING: str = "utf-8"
SAMPLER_VERSION: str = "0.3.0-alpha"


# ==============================================================================
# Type Aliases
# ==============================================================================

TraceId: TypeAlias = str
SpanId: TypeAlias = str
SampleRate: TypeAlias = float

SampleMetadata: TypeAlias = dict[str, Any]
SampleAttributes: TypeAlias = dict[str, Any]
SampleOptions: TypeAlias = dict[str, Any]
SampleContext: TypeAlias = dict[str, Any]
SamplePayload: TypeAlias = dict[str, Any]

SampleHook: TypeAlias = Callable[..., Any]
SampleCallback: TypeAlias = Callable[..., Any]
SampleFilter: TypeAlias = Callable[[Any], bool]
SampleHistory: TypeAlias = Deque[Any]


# ==============================================================================
# Exceptions
# ==============================================================================


class SamplerError(RuntimeError):
    """Base exception for TraceSampler."""


class SamplingError(SamplerError):
    """Sampling execution error."""


class InvalidSampleRateError(SamplerError):
    """Invalid sampling probability."""


class SamplerClosedError(SamplerError):
    """Operation attempted on a closed sampler."""


class SamplerFrozenError(SamplerError):
    """Operation attempted on a frozen sampler."""


class SamplerConfigurationError(SamplerError):
    """Invalid sampler configuration."""


# ==============================================================================
# Part 2. Enums
# ==============================================================================


class SamplingDecision(str, Enum):
    """Sampling decision."""

    DROP = "drop"
    RECORD = "record"
    RECORD_AND_SAMPLE = "record_and_sample"


class SamplerType(str, Enum):
    """Sampler implementation type."""

    ALWAYS_ON = "always_on"
    ALWAYS_OFF = "always_off"
    TRACE_ID_RATIO = "trace_id_ratio"
    PARENT_BASED = "parent_based"
    PROBABILISTIC = "probabilistic"
    ADAPTIVE = "adaptive"
    CUSTOM = "custom"


class SamplerState(str, Enum):
    """Runtime sampler state."""

    CREATED = "created"
    INITIALIZED = "initialized"
    READY = "ready"
    RUNNING = "running"
    STOPPED = "stopped"
    FROZEN = "frozen"
    CLOSED = "closed"
    FAILED = "failed"


class SamplerCapability(Flag):
    """Sampler capabilities."""

    NONE = 0
    DETERMINISTIC = auto()
    PROBABILISTIC = auto()
    PARENT_BASED = auto()
    ADAPTIVE = auto()
    DYNAMIC_RATE = auto()
    FILTERING = auto()
    SERIALIZATION = auto()
    CALLBACKS = auto()
    HOOKS = auto()
    METRICS = auto()


# ==============================================================================
# Part 3. Dataclasses
# ==============================================================================

@dataclass(eq=False)
class SamplingStatistics:
    """
    Runtime sampling statistics.
    """

    samples: int = 0
    accepted: int = 0
    rejected: int = 0
    errors: int = 0

    acceptance_rate: float = 0.0
    rejection_rate: float = 0.0

    last_sample: Optional[float] = None

    average_latency: float = 0.0
    minimum_latency: float = 0.0
    maximum_latency: float = 0.0

    bytes_processed: int = 0


@dataclass(eq=False)
class SamplingResult:
    """
    Result of one sampling operation.

    SamplingRecord is intentionally an alias of this class for
    compatibility. ``record`` may therefore contain another
    SamplingResult, so serialization and equality must not rely
    on dataclass recursive traversal.
    """

    id: str = field(
        default_factory=lambda: str(uuid.uuid4()),
    )

    decision: SamplingDecision = (
        SamplingDecision.RECORD_AND_SAMPLE
    )

    sampled: bool = True

    probability: float = 1.0

    trace_id: Optional[TraceId] = None
    span_id: Optional[SpanId] = None
    parent_trace_id: Optional[TraceId] = None

    timestamp: float = field(
        default_factory=time.time,
    )

    duration: float = 0.0

    sampler_type: SamplerType = (
        SamplerType.PROBABILISTIC
    )

    payload: SamplePayload = field(
        default_factory=dict,
    )

    metadata: SampleMetadata = field(
        default_factory=dict,
    )

    attributes: SampleAttributes = field(
        default_factory=dict,
    )

    context: SampleContext = field(
        default_factory=dict,
    )

    record: Optional["SamplingResult"] = None

    message: str = ""

    def __eq__(
        self,
        other: object,
    ) -> bool:

        if not isinstance(
            other,
            SamplingResult,
        ):
            return NotImplemented

        return (
            self.id
            == other.id
        )

    def __hash__(
        self,
    ) -> int:

        return hash(
            self.id
        )


# IMPORTANT:
#
# Compatibility contract:
#
#     assert SamplingRecord is SamplingResult
#
SamplingRecord = SamplingResult


# ==============================================================================
# Part 4. Constructor
# ==============================================================================


class TraceSampler(ABC):
    """
    SciOS Runtime Trace Sampler.

    Supports:

        ALWAYS_ON
        ALWAYS_OFF
        TRACE_ID_RATIO
        PARENT_BASED
        PROBABILISTIC
        ADAPTIVE
        CUSTOM
    """

    def __init__(
        self,
        name: str = DEFAULT_SAMPLER_NAME,
        *,
        sampler_type: SamplerType = (
            SamplerType.TRACE_ID_RATIO
        ),
        sample_rate: SampleRate = DEFAULT_SAMPLE_RATE,
        seed: Optional[int] = DEFAULT_SEED,
        parent_based: bool = False,
        deterministic: bool = False,
        sampler_fn: Optional[
            Callable[..., Any]
        ] = None,
        metadata: Optional[
            SampleMetadata
        ] = None,
        options: Optional[
            SampleOptions
        ] = None,
        description: str = "",
        encoding: str = DEFAULT_ENCODING,
        history_limit: int = DEFAULT_HISTORY_LIMIT,
        auto_start: bool = False,
    ) -> None:

        self._lock = threading.RLock()

        # ------------------------------------------------------------------
        # Identity
        # ------------------------------------------------------------------

        self._uuid = uuid.uuid4()

        self._id = self._uuid.hex

        self._name = str(name)

        self._description = str(
            description
        )

        self._version = SAMPLER_VERSION

        try:
            self._sampler_type = SamplerType(
                sampler_type
            )

        except (
            ValueError,
            TypeError,
        ) as exc:

            raise SamplerConfigurationError(
                "invalid sampler_type"
            ) from exc

        # ------------------------------------------------------------------
        # Configuration
        # ------------------------------------------------------------------

        self._sample_rate = self._coerce_rate(
            sample_rate
        )

        self._seed = self._coerce_seed(
            seed
        )

        self._parent_based = bool(
            parent_based
        )

        self._deterministic = bool(
            deterministic
        )

        if sampler_fn is not None and not callable(
            sampler_fn
        ):
            raise SamplerConfigurationError(
                "sampler_fn must be callable"
            )

        self._sampler_fn = sampler_fn

        self._encoding = str(
            encoding
        )

        try:
            self._history_limit = int(
                history_limit
            )

        except (
            TypeError,
            ValueError,
        ) as exc:

            raise SamplerConfigurationError(
                "history_limit must be an integer"
            ) from exc

        if self._history_limit < 1:
            raise SamplerConfigurationError(
                "history_limit must be >= 1"
            )

        self._options: SampleOptions = deepcopy(
            options or {}
        )

        # Keep metadata explicitly available through the public
        # metadata property.

        self._metadata: SampleMetadata = deepcopy(
            metadata or {}
        )

        # options.enabled explicitly overrides default enabled state.

        self._enabled = bool(
            self._options.get(
                "enabled",
                True,
            )
        )

        # ------------------------------------------------------------------
        # Capabilities
        # ------------------------------------------------------------------

        self._capabilities = (
            SamplerCapability.SERIALIZATION
            | SamplerCapability.CALLBACKS
            | SamplerCapability.HOOKS
            | SamplerCapability.METRICS
        )

        if self._deterministic:

            self._capabilities |= (
                SamplerCapability.DETERMINISTIC
            )

        else:

            self._capabilities |= (
                SamplerCapability.PROBABILISTIC
            )

        if self._parent_based:

            self._capabilities |= (
                SamplerCapability.PARENT_BASED
            )

        if self._sampler_type is SamplerType.ADAPTIVE:

            self._capabilities |= (
                SamplerCapability.ADAPTIVE
                | SamplerCapability.DYNAMIC_RATE
            )

        if self._sampler_type is SamplerType.CUSTOM:

            self._capabilities |= (
                SamplerCapability.FILTERING
            )

        # ------------------------------------------------------------------
        # Runtime
        # ------------------------------------------------------------------

        self._initialized = False

        self._running = False

        self._active = False

        self._frozen = False

        self._closed = False

        self._state = SamplerState.CREATED

        now = time.time()

        self._created_at = now

        self._updated_at = now

        self._last_sample: Optional[float] = None

        self._last_decision: Optional[
            SamplingDecision
        ] = None

        self._last_trace_id: Optional[
            TraceId
        ] = None

        self._last_span_id: Optional[
            SpanId
        ] = None

        self._current_context: SampleContext = {}

        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------

        self._statistics = (
            SamplingStatistics()
        )

        self._sample_count = 0

        self._accepted_count = 0

        self._rejected_count = 0

        self._error_count = 0

        self._decision_count: dict[
            SamplingDecision,
            int,
        ] = defaultdict(int)

        self._parent_sample_count = 0

        self._forced_sample_count = 0

        self._last_latency = 0.0

        self._minimum_latency = 0.0

        self._maximum_latency = 0.0

        # ------------------------------------------------------------------
        # Resources
        # ------------------------------------------------------------------

        self._history: SampleHistory = deque(
            maxlen=self._history_limit
        )

        self._cache: dict[
            str,
            Any,
        ] = {}

        self._callbacks: list[
            SampleCallback
        ] = []

        self._hooks: dict[
            str,
            list[SampleHook],
        ] = defaultdict(list)

        self._filters: list[
            SampleFilter
        ] = []

        self._event_queue: deque[
            tuple[
                str,
                tuple[Any, ...],
                dict[str, Any],
            ]
        ] = deque()

        self._tags: list[str] = []

        # ------------------------------------------------------------------
        # Random engine
        # ------------------------------------------------------------------

        self._random = _random.Random(
            self._seed
        )

        # ------------------------------------------------------------------
        # Automatic lifecycle
        # ------------------------------------------------------------------

        if auto_start:

            self.initialize()

            self.start()


# ==============================================================================
# Part 5. Properties
# ==============================================================================


    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    @property
    def id(self) -> str:
        return self._id


    @property
    def uuid(self) -> uuid.UUID:
        return self._uuid


    @property
    def name(self) -> str:
        return self._name


    @name.setter
    def name(
        self,
        value: str,
    ) -> None:

        self._name = str(value)
        self.touch()


    @property
    def description(self) -> str:
        return self._description


    @description.setter
    def description(
        self,
        value: str,
    ) -> None:

        self._description = str(value)
        self.touch()


    @property
    def version(self) -> str:
        return self._version


    @property
    def sampler_type(self) -> SamplerType:
        return self._sampler_type


    @sampler_type.setter
    def sampler_type(
        self,
        value: SamplerType,
    ) -> None:

        try:
            self._sampler_type = SamplerType(
                value
            )

        except (
            ValueError,
            TypeError,
        ) as exc:

            raise SamplerConfigurationError(
                "invalid sampler_type"
            ) from exc

        self.touch()


    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    @property
    def sample_rate(self) -> float:
        return self._sample_rate


    @sample_rate.setter
    def sample_rate(
        self,
        value: float,
    ) -> None:

        self._sample_rate = self._coerce_rate(
            value
        )

        self.touch()


    @property
    def seed(self) -> Optional[int]:
        return self._seed


    @seed.setter
    def seed(
        self,
        value: Optional[int],
    ) -> None:

        self._seed = self._coerce_seed(
            value
        )

        self._random.seed(
            self._seed
        )

        self.touch()


    @property
    def parent_based(self) -> bool:
        return self._parent_based


    @parent_based.setter
    def parent_based(
        self,
        value: bool,
    ) -> None:

        self._parent_based = bool(
            value
        )

        self.touch()


    @property
    def deterministic(self) -> bool:
        return self._deterministic


    @deterministic.setter
    def deterministic(
        self,
        value: bool,
    ) -> None:

        self._deterministic = bool(
            value
        )

        self.touch()


    @property
    def sampler_fn(
        self,
    ) -> Optional[Callable[..., Any]]:

        return self._sampler_fn


    @sampler_fn.setter
    def sampler_fn(
        self,
        value: Optional[
            Callable[..., Any]
        ],
    ) -> None:

        if (
            value is not None
            and not callable(value)
        ):
            raise TypeError(
                "sampler_fn must be callable"
            )

        self._sampler_fn = value
        self.touch()


    @property
    def metadata(self) -> SampleMetadata:
        return deepcopy(
            self._metadata
        )


    @metadata.setter
    def metadata(
        self,
        value: Optional[
            SampleMetadata
        ],
    ) -> None:

        self._metadata = deepcopy(
            value or {}
        )

        self.touch()


    @property
    def encoding(self) -> str:
        return self._encoding


    @encoding.setter
    def encoding(
        self,
        value: str,
    ) -> None:

        self._encoding = str(
            value
        )

        self.touch()


    @property
    def history_limit(self) -> int:
        return self._history_limit


    @history_limit.setter
    def history_limit(
        self,
        value: int,
    ) -> None:

        value = int(value)

        if value <= 0:
            raise ValueError(
                "history_limit must be positive"
            )

        self._history_limit = value

        self._history = deque(
            self._history,
            maxlen=value,
        )

        self.touch()


    @property
    def options(self) -> SampleOptions:
        return deepcopy(
            self._options
        )


    @options.setter
    def options(
        self,
        value: Optional[
            SampleOptions
        ],
    ) -> None:

        self._options = deepcopy(
            value or {}
        )

        if "enabled" in self._options:
            self._enabled = bool(
                self._options["enabled"]
            )

        self.touch()


    @property
    def capabilities(
        self,
    ) -> SamplerCapability:

        return self._capabilities


    # ------------------------------------------------------------------
    # Runtime
    # ------------------------------------------------------------------

    @property
    def enabled(self) -> bool:
        return self._enabled


    @enabled.setter
    def enabled(
        self,
        value: bool,
    ) -> None:

        self._enabled = bool(
            value
        )

        if (
            self._running
            and not self._frozen
            and not self._closed
        ):
            self._active = self._enabled

        self.touch()


    @property
    def initialized(self) -> bool:
        return self._initialized


    @property
    def running(self) -> bool:
        return self._running


    @property
    def active(self) -> bool:
        return self._active


    @property
    def frozen(self) -> bool:
        return self._frozen


    @property
    def closed(self) -> bool:
        return self._closed


    @property
    def state(self) -> SamplerState:
        return self._state


    @property
    def created_at(self) -> float:
        return self._created_at


    @property
    def updated_at(self) -> float:
        return self._updated_at


    @property
    def last_sample(
        self,
    ) -> Optional[float]:

        return self._last_sample


    @property
    def uptime(self) -> float:

        return max(
            0.0,
            time.time()
            - self._created_at,
        )


    @property
    def last_decision(
        self,
    ) -> Optional[SamplingDecision]:

        return self._last_decision


    @property
    def last_trace_id(
        self,
    ) -> Optional[TraceId]:

        return self._last_trace_id


    @property
    def last_span_id(
        self,
    ) -> Optional[SpanId]:

        return self._last_span_id


    @property
    def current_context(
        self,
    ) -> SampleContext:

        return deepcopy(
            self._current_context
        )


    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    @property
    def statistics(
        self,
    ) -> SamplingStatistics:

        return deepcopy(
            self._statistics
        )


    @property
    def sample_count(self) -> int:
        return self._sample_count


    @property
    def accepted_count(self) -> int:
        return self._accepted_count


    @property
    def rejected_count(self) -> int:
        return self._rejected_count


    @property
    def error_count(self) -> int:
        return self._error_count


    @property
    def decision_count(self) -> int:
        """
        Total number of sampling decisions.

        Compatibility contract:
            sampler.decision_count >= 1
        """

        return sum(
            self._decision_count.values()
        )


    @property
    def decision_counts(
        self,
    ) -> dict[
        SamplingDecision,
        int,
    ]:

        return dict(
            self._decision_count
        )


    @property
    def parent_sample_count(self) -> int:
        return self._parent_sample_count


    @property
    def forced_sample_count(self) -> int:
        return self._forced_sample_count


    @property
    def success_rate(self) -> float:

        if self._sample_count <= 0:
            return 0.0

        return (
            self._accepted_count
            / self._sample_count
        )


    @property
    def failure_rate(self) -> float:

        if self._sample_count <= 0:
            return 0.0

        return (
            self._rejected_count
            / self._sample_count
        )


    @property
    def acceptance_rate(self) -> float:
        return self.success_rate


    @property
    def rejection_rate(self) -> float:
        return self.failure_rate


    @property
    def last_latency(self) -> float:
        return self._last_latency


    @property
    def minimum_latency(self) -> float:
        return self._minimum_latency


    @property
    def maximum_latency(self) -> float:
        return self._maximum_latency


    # ------------------------------------------------------------------
    # Resources
    # ------------------------------------------------------------------

    @property
    def history(
        self,
    ) -> list[SamplingResult]:

        return list(
            self._history
        )


    @property
    def cache(self) -> dict[str, Any]:

        return deepcopy(
            self._cache
        )


    @property
    def callbacks(
        self,
    ) -> list[SampleCallback]:

        return list(
            self._callbacks
        )


    @property
    def hooks(
        self,
    ) -> dict[
        str,
        list[SampleHook],
    ]:

        return {
            key: list(value)
            for key, value
            in self._hooks.items()
        }


    @property
    def filters(
        self,
    ) -> list[SampleFilter]:

        return list(
            self._filters
        )


# ==============================================================================
# Part 6. Lifecycle
# ==============================================================================


    def initialize(
        self,
    ) -> "TraceSampler":

        with self._lock:

            self._ensure_open()

            if self._initialized:
                return self

            if self._frozen:
                raise SamplerFrozenError(
                    "sampler is frozen"
                )

            self.validate(
                raise_error=True
            )

            self._initialized = True

            self._state = (
                SamplerState.READY
            )

            self.touch()

        return self


    def start(
        self,
    ) -> "TraceSampler":

        with self._lock:

            self._ensure_open()

            if self._frozen:
                raise SamplerFrozenError(
                    "sampler is frozen"
                )

            if not self._initialized:
                self.initialize()

            self._running = True

            self._active = bool(
                self._enabled
            )

            self._state = (
                SamplerState.RUNNING
            )

            self.touch()

        return self


    def stop(
        self,
    ) -> "TraceSampler":

        with self._lock:

            self._ensure_open()

            self._running = False

            self._active = False

            self._state = (
                SamplerState.STOPPED
            )

            self.touch()

        return self


    def freeze(
        self,
    ) -> "TraceSampler":

        with self._lock:

            self._ensure_open()

            self._frozen = True

            self._active = False

            self._state = (
                SamplerState.FROZEN
            )

            self.touch()

        return self


    def unfreeze(
        self,
    ) -> "TraceSampler":

        with self._lock:

            self._ensure_open()

            self._frozen = False

            if self._running:

                self._active = bool(
                    self._enabled
                )

                self._state = (
                    SamplerState.RUNNING
                )

            elif self._initialized:

                self._state = (
                    SamplerState.READY
                )

            else:

                self._state = (
                    SamplerState.CREATED
                )

            self.touch()

        return self


    def close(
        self,
    ) -> "TraceSampler":

        with self._lock:

            if self._closed:
                return self

            self._running = False

            self._active = False

            self._frozen = False

            self._closed = True

            self._state = (
                SamplerState.CLOSED
            )

            self._event_queue.clear()

            self.touch()

        return self


    def reset(
        self,
    ) -> "TraceSampler":

        with self._lock:

            self._ensure_open()

            self._statistics = (
                SamplingStatistics()
            )

            self._sample_count = 0

            self._accepted_count = 0

            self._rejected_count = 0

            self._error_count = 0

            self._decision_count.clear()

            self._parent_sample_count = 0

            self._forced_sample_count = 0

            self._last_latency = 0.0

            self._minimum_latency = 0.0

            self._maximum_latency = 0.0

            self._last_sample = None

            self._last_decision = None

            self._last_trace_id = None

            self._last_span_id = None

            self._history.clear()

            self._cache.clear()

            self._event_queue.clear()

            self._current_context.clear()

            self.touch()

        return self


    def restart(
        self,
    ) -> "TraceSampler":

        self._ensure_open()

        self.stop()

        self.reset()

        self.start()

        return self


    def cleanup(
        self,
    ) -> "TraceSampler":

        with self._lock:

            self._history.clear()

            self._cache.clear()

            self._event_queue.clear()

            self._active = False

            if not self._closed:
                self._running = False

            self.touch()

        return self


    def __enter__(
        self,
    ) -> "TraceSampler":

        self._ensure_open()

        if not self._initialized:
            self.initialize()

        if not self._running:
            self.start()

        self._active = True

        return self


    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:

        # Compatibility contract:
        #
        # with TraceSampler() as sampler:
        #     ...
        #
        # exiting the context closes the sampler.

        self.close()

        return None


# ==============================================================================
# Part 7. Validation
# ==============================================================================

    def validate(
        self,
        *,
        raise_error: bool = False,
    ) -> bool:

        validators = (
            self.validate_rate,
            self.validate_seed,
            self.validate_configuration,
            self.check_integrity,
        )

        for validator in validators:
            try:
                validator(
                    raise_error=True,
                )

            except Exception:
                if raise_error:
                    raise

                return False

        return True

    def validate_rate(
        self,
        rate: Optional[float] = None,
        *,
        raise_error: bool = False,
    ) -> bool:

        try:
            value = (
                self._sample_rate
                if rate is None
                else rate
            )

            value = float(value)

            if not 0.0 <= value <= 1.0:
                raise InvalidSampleRateError(
                    "sample_rate must be between 0.0 and 1.0"
                )

            return True

        except Exception:
            if raise_error:
                raise

            return False

    def validate_seed(
        self,
        *,
        raise_error: bool = False,
    ) -> bool:

        try:
            if (
                self._seed is not None
                and not isinstance(
                    self._seed,
                    int,
                )
            ):
                raise SamplerConfigurationError(
                    "seed must be int or None"
                )

            return True

        except Exception:
            if raise_error:
                raise

            return False

    def validate_configuration(
        self,
        *,
        raise_error: bool = False,
    ) -> bool:

        try:
            if not isinstance(
                self._sampler_type,
                SamplerType,
            ):
                raise SamplerConfigurationError(
                    "invalid sampler_type"
                )

            if not isinstance(
                self._state,
                SamplerState,
            ):
                raise SamplerConfigurationError(
                    "invalid state"
                )

            if (
                not isinstance(
                    self._history_limit,
                    int,
                )
                or self._history_limit <= 0
            ):
                raise SamplerConfigurationError(
                    "history_limit must be positive"
                )

            if not isinstance(
                self._encoding,
                str,
            ):
                raise SamplerConfigurationError(
                    "encoding must be string"
                )

            if not isinstance(
                self._options,
                dict,
            ):
                raise SamplerConfigurationError(
                    "options must be mapping"
                )

            if not isinstance(
                self._metadata,
                dict,
            ):
                raise SamplerConfigurationError(
                    "metadata must be mapping"
                )

            if not isinstance(
                self._enabled,
                bool,
            ):
                raise SamplerConfigurationError(
                    "enabled must be bool"
                )

            return True

        except Exception:
            if raise_error:
                raise

            return False

    def check_integrity(
        self,
        *,
        raise_error: bool = False,
    ) -> bool:

        try:
            counters = (
                self._sample_count,
                self._accepted_count,
                self._rejected_count,
                self._error_count,
                self._parent_sample_count,
                self._forced_sample_count,
            )

            if any(
                not isinstance(
                    value,
                    int,
                )
                or value < 0
                for value in counters
            ):
                raise SamplerConfigurationError(
                    "counters cannot be negative"
                )

            if (
                self._accepted_count
                + self._rejected_count
                > self._sample_count
            ):
                raise SamplerConfigurationError(
                    "accepted/rejected count exceeds samples"
                )

            if self._history is None:
                raise SamplerConfigurationError(
                    "history is missing"
                )

            if self._cache is None:
                raise SamplerConfigurationError(
                    "cache is missing"
                )

            if self._random is None:
                raise SamplerConfigurationError(
                    "random engine is missing"
                )

            if self._statistics is None:
                raise SamplerConfigurationError(
                    "statistics are missing"
                )

            statistics = self._statistics

            if statistics.samples < 0:
                raise SamplerConfigurationError(
                    "statistics.samples cannot be negative"
                )

            if statistics.accepted < 0:
                raise SamplerConfigurationError(
                    "statistics.accepted cannot be negative"
                )

            if statistics.rejected < 0:
                raise SamplerConfigurationError(
                    "statistics.rejected cannot be negative"
                )

            if statistics.errors < 0:
                raise SamplerConfigurationError(
                    "statistics.errors cannot be negative"
                )

            if (
                statistics.accepted
                + statistics.rejected
                > statistics.samples
            ):
                raise SamplerConfigurationError(
                    "statistics accepted/rejected "
                    "count exceeds samples"
                )

            return True

        except Exception:
            if raise_error:
                raise

            return False


# ==============================================================================
# Part 8. Events & Hooks
# ==============================================================================


    @property
    def hooks(
        self,
    ) -> tuple[SampleHook, ...]:

        return tuple(
            hook
            for hooks in self._hooks.values()
            for hook in hooks
        )


    def add_hook(
        self,
        hook: SampleHook,
        event: str = "*",
    ) -> "TraceSampler":

        if not callable(hook):
            raise TypeError(
                "hook must be callable"
            )

        with self._lock:

            hooks = self._hooks.setdefault(
                event,
                [],
            )

            if hook not in hooks:
                hooks.append(
                    hook
                )

        return self


    def remove_hook(
        self,
        hook: SampleHook,
        event: str = "*",
    ) -> "TraceSampler":

        with self._lock:

            hooks = self._hooks.get(
                event,
                [],
            )

            if hook in hooks:
                hooks.remove(
                    hook
                )

            if not hooks:
                self._hooks.pop(
                    event,
                    None,
                )

        return self


    def clear_hooks(
        self,
        event: Optional[str] = None,
    ) -> "TraceSampler":

        with self._lock:

            if event is None:
                self._hooks.clear()

            else:
                self._hooks.pop(
                    event,
                    None,
                )

        return self


    def add_callback(
        self,
        callback: SampleCallback,
    ) -> "TraceSampler":

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


    def remove_callback(
        self,
        callback: SampleCallback,
    ) -> "TraceSampler":

        with self._lock:

            try:
                self._callbacks.remove(
                    callback
                )

            except ValueError:
                pass

        return self


    def clear_callbacks(
        self,
    ) -> "TraceSampler":

        with self._lock:
            self._callbacks.clear()

        return self


    def _emit_event_safe(
        self,
        event: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:

        with self._lock:

            hooks = list(
                self._hooks.get(
                    event,
                    (),
                )
            )

            wildcard_hooks = list(
                self._hooks.get(
                    "*",
                    (),
                )
            )

            callbacks = list(
                self._callbacks
            )

        for hook in (
            *wildcard_hooks,
            *hooks,
        ):

            try:
                hook(
                    *args,
                    **kwargs,
                )

            except Exception:
                continue

        for callback in callbacks:

            try:
                callback(
                    event,
                    *args,
                    **kwargs,
                )

            except Exception:
                continue


    def emit_event(
        self,
        event: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:

        self._emit_event_safe(
            event,
            *args,
            **kwargs,
        )


    def before_sample(
        self,
        *,
        trace_id: Optional[TraceId] = None,
        span_id: Optional[SpanId] = None,
        parent_trace_id: Optional[TraceId] = None,
        parent_sampled: Optional[bool] = None,
        attributes: Optional[SampleAttributes] = None,
        metadata: Optional[SampleMetadata] = None,
        payload: Optional[SamplePayload] = None,
        context: Optional[SampleContext] = None,
    ) -> "TraceSampler":

        self.emit_event(
            "before_sample",
            trace_id=trace_id,
            span_id=span_id,
            parent_trace_id=parent_trace_id,
            parent_sampled=parent_sampled,
            attributes=attributes,
            metadata=metadata,
            payload=payload,
            context=context,
        )

        return self


    def after_sample(
        self,
        result: SamplingResult,
        *,
        trace_id: Optional[TraceId] = None,
        span_id: Optional[SpanId] = None,
        parent_trace_id: Optional[TraceId] = None,
        parent_sampled: Optional[bool] = None,
        attributes: Optional[SampleAttributes] = None,
        metadata: Optional[SampleMetadata] = None,
        payload: Optional[SamplePayload] = None,
        context: Optional[SampleContext] = None,
    ) -> SamplingResult:

        self.emit_event(
            "after_sample",
            result,
            trace_id=trace_id,
            span_id=span_id,
            parent_trace_id=parent_trace_id,
            parent_sampled=parent_sampled,
            attributes=attributes,
            metadata=metadata,
            payload=payload,
            context=context,
        )

        return result

# ==============================================================================
# Part 9. Filtering & Context
# ==============================================================================

    def add_filter(
        self,
        filter_fn: SampleFilter,
    ) -> "TraceSampler":

        if not callable(filter_fn):
            raise TypeError(
                "filter must be callable"
            )

        with self._lock:
            if filter_fn not in self._filters:
                self._filters.append(
                    filter_fn
                )

            self._capabilities |= (
                SamplerCapability.FILTERING
            )

        return self

    def remove_filter(
        self,
        filter_fn: SampleFilter,
    ) -> "TraceSampler":

        with self._lock:
            if filter_fn in self._filters:
                self._filters.remove(
                    filter_fn
                )

        return self

    def clear_filters(
        self,
    ) -> "TraceSampler":

        with self._lock:
            self._filters.clear()

        return self

    def apply_filters(
        self,
        value: Any,
    ) -> bool:

        for filter_fn in list(
            self._filters
        ):
            try:
                if not bool(
                    filter_fn(value)
                ):
                    return False

            except Exception:
                return False

        return True

    def set_context(
        self,
        context: Optional[SampleContext] = None,
        *,
        trace_id: Optional[TraceId] = None,
        span_id: Optional[SpanId] = None,
        parent_trace_id: Optional[TraceId] = None,
        **kwargs: Any,
    ) -> "TraceSampler":

        with self._lock:
            if context is not None:
                self._current_context = deepcopy(
                    context
                )
            else:
                self._current_context = {}

            if trace_id is not None:
                self._current_context[
                    "trace_id"
                ] = trace_id

            if span_id is not None:
                self._current_context[
                    "span_id"
                ] = span_id

            if parent_trace_id is not None:
                self._current_context[
                    "parent_trace_id"
                ] = parent_trace_id

            if kwargs:
                self._current_context.update(
                    deepcopy(kwargs)
                )

            self.touch()

        return self

    def update_context(
        self,
        context: Optional[SampleContext] = None,
        *,
        trace_id: Optional[TraceId] = None,
        span_id: Optional[SpanId] = None,
        parent_trace_id: Optional[TraceId] = None,
        **kwargs: Any,
    ) -> "TraceSampler":

        with self._lock:
            if context:
                self._current_context.update(
                    deepcopy(context)
                )

            if trace_id is not None:
                self._current_context[
                    "trace_id"
                ] = trace_id

            if span_id is not None:
                self._current_context[
                    "span_id"
                ] = span_id

            if parent_trace_id is not None:
                self._current_context[
                    "parent_trace_id"
                ] = parent_trace_id

            if kwargs:
                self._current_context.update(
                    deepcopy(kwargs)
                )

            self.touch()

        return self

    def clear_context(
        self,
    ) -> "TraceSampler":

        with self._lock:
            self._current_context.clear()
            self.touch()

        return self


# ==============================================================================
# Part 10. Sampling Engine
# ==============================================================================

    def sample(
        self,
        trace_id: Optional[TraceId] = None,
        *,
        span_id: Optional[SpanId] = None,
        parent_trace_id: Optional[TraceId] = None,
        parent_sampled: Optional[bool] = None,
        attributes: Optional[SampleAttributes] = None,
        metadata: Optional[SampleMetadata] = None,
        payload: Optional[SamplePayload] = None,
        context: Optional[SampleContext] = None,
        force: bool = False,
    ) -> SamplingResult:

        started = time.perf_counter()

        self._ensure_sample_operation()

        attrs = deepcopy(
            attributes
            if attributes is not None
            else {}
        )

        ctx = deepcopy(
            context
            if context is not None
            else self._current_context
        )

        meta = deepcopy(
            metadata
            if metadata is not None
            else self._metadata
        )

        body = deepcopy(
            payload
            if payload is not None
            else {}
        )

        # ------------------------------------------------------------------
        # Before-sample event
        # ------------------------------------------------------------------

        self.emit_event(
            "before_sample",
            trace_id=trace_id,
            span_id=span_id,
            parent_trace_id=parent_trace_id,
            parent_sampled=parent_sampled,
            attributes=attrs,
            metadata=meta,
            payload=body,
            context=ctx,
        )

        try:

            sample_input = {
                "trace_id": trace_id,
                "span_id": span_id,
                "parent_trace_id": parent_trace_id,
                "parent_sampled": parent_sampled,
                "attributes": attrs,
                "metadata": meta,
                "payload": body,
                "context": ctx,
            }

            # ------------------------------------------------------------------
            # Filtering
            # ------------------------------------------------------------------

            if not self.apply_filters(
                sample_input
            ):

                sampled = False
                probability = 0.0

                decision = (
                    SamplingDecision.DROP
                )

            # ------------------------------------------------------------------
            # Forced sampling
            # ------------------------------------------------------------------

            elif force:

                sampled = True
                probability = 1.0

                decision = (
                    SamplingDecision.RECORD_AND_SAMPLE
                )

                with self._lock:
                    self._forced_sample_count += 1

            # ------------------------------------------------------------------
            # Normal strategy
            # ------------------------------------------------------------------

            else:

                sampled, probability = (
                    self._sample_internal(
                        trace_id=trace_id,
                        parent_sampled=parent_sampled,
                        attributes=attrs,
                        context=ctx,
                    )
                )

                decision = (
                    SamplingDecision.RECORD_AND_SAMPLE
                    if sampled
                    else SamplingDecision.DROP
                )

            # ------------------------------------------------------------------
            # Duration
            # ------------------------------------------------------------------

            duration = (
                time.perf_counter()
                - started
            )

            # ------------------------------------------------------------------
            # Result
            #
            # SamplingRecord is an alias of SamplingResult.
            # ------------------------------------------------------------------

            result = SamplingResult(
                trace_id=trace_id,
                span_id=span_id,
                parent_trace_id=parent_trace_id,
                decision=decision,
                sampled=sampled,
                probability=probability,
                sampler_type=self._sampler_type,
                payload=deepcopy(body),
                metadata=deepcopy(meta),
                attributes=deepcopy(attrs),
                context=deepcopy(ctx),
                duration=duration,
            )

            # ------------------------------------------------------------------
            # Compatibility invariant
            #
            # SamplingRecord is SamplingResult.
            # Therefore record points to the final result itself.
            # ------------------------------------------------------------------

            result.record = result

            # ------------------------------------------------------------------
            # Bookkeeping
            # ------------------------------------------------------------------

            self._record_sample(
                result
            )

            # ------------------------------------------------------------------
            # After-sample event
            #
            # Emit only after bookkeeping so callbacks observe the
            # completed sampling state.
            # ------------------------------------------------------------------

            self.emit_event(
                "after_sample",
                result,
                trace_id=trace_id,
                span_id=span_id,
                parent_trace_id=parent_trace_id,
                parent_sampled=parent_sampled,
                attributes=attrs,
                metadata=meta,
                payload=body,
                context=ctx,
            )

            return result

        except (
            SamplerClosedError,
            SamplerFrozenError,
        ):
            raise

        except SamplingError:
            raise

        except Exception as exc:

            with self._lock:

                self._error_count += 1

                self._statistics.errors = (
                    self._error_count
                )

                self._state = (
                    SamplerState.FAILED
                )

                self.touch()

            raise SamplingError(
                str(exc)
            ) from exc


    def sample_many(
        self,
        traces: Iterable[TraceId],
        **kwargs: Any,
    ) -> list[SamplingResult]:

        return [
            self.sample(
                trace_id=trace_id,
                **kwargs,
            )
            for trace_id in traces
        ]


    def sample_batch(
        self,
        traces: Sequence[TraceId],
        **kwargs: Any,
    ) -> list[SamplingResult]:

        return self.sample_many(
            traces,
            **kwargs,
        )


    def decision(
        self,
        trace_id: Optional[TraceId] = None,
        **kwargs: Any,
    ) -> SamplingDecision:

        return self.sample(
            trace_id=trace_id,
            **kwargs,
        ).decision


    def probability(
        self,
        trace_id: Optional[TraceId] = None,
        *,
        parent_sampled: Optional[bool] = None,
        attributes: Optional[SampleAttributes] = None,
        context: Optional[SampleContext] = None,
    ) -> float:
        """
        Return the effective sampling probability.

        This method is observational only and must not mutate
        sampling counters, history, cache, or runtime state.
        """

        sampler_type = self._sampler_type

        if sampler_type is SamplerType.ALWAYS_ON:
            return 1.0

        if sampler_type is SamplerType.ALWAYS_OFF:
            return 0.0

        if sampler_type is SamplerType.PARENT_BASED:

            if parent_sampled is not None:
                return (
                    1.0
                    if parent_sampled
                    else 0.0
                )

            return float(
                self._sample_rate
            )

        if sampler_type is SamplerType.ADAPTIVE:

            target = self._options.get(
                "adaptive_rate",
                self._sample_rate,
            )

            try:
                return self.clamp_rate(
                    float(target)
                )

            except (
                TypeError,
                ValueError,
            ):
                return float(
                    self._sample_rate
                )

        if sampler_type is SamplerType.CUSTOM:
            return float(
                self._sample_rate
            )

        return float(
            self._sample_rate
        )


    def next_probability(
        self,
    ) -> float:

        return self.probability()


    def random(
        self,
    ) -> float:

        with self._lock:
            return self._random.random()


    # ------------------------------------------------------------------
    # Strategies
    # ------------------------------------------------------------------

    def _sample_internal(
        self,
        *,
        trace_id: Optional[TraceId],
        parent_sampled: Optional[bool],
        attributes: SampleAttributes,
        context: SampleContext,
    ) -> tuple[bool, float]:

        if self._parent_based:

            return self._sample_parent_based(
                trace_id=trace_id,
                parent_sampled=parent_sampled,
                attributes=attributes,
                context=context,
            )

        strategies = {
            SamplerType.ALWAYS_ON:
                self._sample_always_on,

            SamplerType.ALWAYS_OFF:
                self._sample_always_off,

            SamplerType.TRACE_ID_RATIO:
                self._sample_trace_id_ratio,

            SamplerType.PARENT_BASED:
                self._sample_parent_based,

            SamplerType.PROBABILISTIC:
                self._sample_probabilistic,

            SamplerType.ADAPTIVE:
                self._sample_adaptive,

            SamplerType.CUSTOM:
                self._sample_custom,
        }

        strategy = strategies.get(
            self._sampler_type
        )

        if strategy is None:
            raise SamplerConfigurationError(
                f"Unsupported sampler type: "
                f"{self._sampler_type!r}"
            )

        return strategy(
            trace_id=trace_id,
            parent_sampled=parent_sampled,
            attributes=attributes,
            context=context,
        )


    def _sample_always_on(
        self,
        **kwargs: Any,
    ) -> tuple[bool, float]:

        return True, 1.0


    def _sample_always_off(
        self,
        **kwargs: Any,
    ) -> tuple[bool, float]:

        return False, 0.0


    def _sample_trace_id_ratio(
        self,
        *,
        trace_id: Optional[TraceId],
        **kwargs: Any,
    ) -> tuple[bool, float]:

        if trace_id is None:

            value = self.random()

        else:

            digest = uuid.uuid5(
                uuid.NAMESPACE_URL,
                str(trace_id),
            )

            value = (
                digest.int
                / float(
                    1 << 128
                )
            )

        probability = float(
            self._sample_rate
        )

        return (
            value < probability,
            probability,
        )


    def _sample_parent_based(
        self,
        *,
        parent_sampled: Optional[bool],
        **kwargs: Any,
    ) -> tuple[bool, float]:

        with self._lock:
            self._parent_sample_count += 1

        if parent_sampled is not None:

            return (
                bool(parent_sampled),
                1.0
                if parent_sampled
                else 0.0,
            )

        return self._sample_probabilistic(
            **kwargs
        )


    def _sample_probabilistic(
        self,
        **kwargs: Any,
    ) -> tuple[bool, float]:

        probability = float(
            self._sample_rate
        )

        return (
            self.random() < probability,
            probability,
        )


    def _sample_adaptive(
        self,
        **kwargs: Any,
    ) -> tuple[bool, float]:

        default_rate = float(
            self._sample_rate
        )

        target = self._options.get(
            "adaptive_rate",
            default_rate,
        )

        try:

            rate = self.clamp_rate(
                float(target)
            )

        except (
            TypeError,
            ValueError,
        ):

            rate = default_rate

        return (
            self.random() < rate,
            rate,
        )


    def _sample_custom(
        self,
        *,
        trace_id: Optional[TraceId],
        parent_sampled: Optional[bool],
        attributes: SampleAttributes,
        context: SampleContext,
    ) -> tuple[bool, float]:

        if self._sampler_fn is None:

            raise SamplerConfigurationError(
                "CUSTOM sampler requires sampler_fn"
            )

        result = self._sampler_fn(
            trace_id=trace_id,
            parent_sampled=parent_sampled,
            attributes=attributes,
            context=context,
            sampler=self,
        )

        if isinstance(
            result,
            tuple,
        ):

            if not result:
                raise SamplerConfigurationError(
                    "CUSTOM sampler returned empty tuple"
                )

            sampled = bool(
                result[0]
            )

            probability = (
                float(result[1])
                if len(result) > 1
                else float(
                    self._sample_rate
                )
            )

            return (
                sampled,
                self.clamp_rate(
                    probability
                ),
            )

        return (
            bool(result),
            float(
                self._sample_rate
            ),
        )


    # ------------------------------------------------------------------
    # Bookkeeping
    # ------------------------------------------------------------------

    def _record_sample(
        self,
        result: SamplingResult,
    ) -> None:

        with self._lock:

            self._sample_count += 1

            if result.sampled:
                self._accepted_count += 1
            else:
                self._rejected_count += 1

            self._decision_count[
                result.decision
            ] += 1

            self._last_decision = (
                result.decision
            )

            self._last_trace_id = (
                result.trace_id
            )

            self._last_span_id = (
                result.span_id
            )

            self._last_sample = (
                result.timestamp
            )

            self._update_latency(
                result.duration
            )

            self._history.append(
                deepcopy(result)
            )

            cache_key = (
                result.trace_id
                or result.span_id
            )

            if cache_key:

                self._cache[
                    str(cache_key)
                ] = deepcopy(result)

            self._update_statistics()

            self.touch()


    def _update_statistics(
        self,
    ) -> None:

        self._statistics.samples = (
            self._sample_count
        )

        self._statistics.accepted = (
            self._accepted_count
        )

        self._statistics.rejected = (
            self._rejected_count
        )

        self._statistics.errors = (
            self._error_count
        )

        self._statistics.acceptance_rate = (
            self.success_rate
        )

        self._statistics.rejection_rate = (
            self.failure_rate
        )

        self._statistics.last_sample = (
            self._last_sample
        )

        self._statistics.minimum_latency = (
            self._minimum_latency
        )

        self._statistics.maximum_latency = (
            self._maximum_latency
        )

        self._statistics.bytes_processed = (
            sum(
                len(
                    json.dumps(
                        item.payload,
                        default=str,
                    ).encode(
                        self._encoding
                    )
                )
                for item in self._history
            )
        )


    def _update_latency(
        self,
        latency: float,
    ) -> None:

        latency = max(
            0.0,
            float(latency),
        )

        self._last_latency = latency

        if (
            self._minimum_latency == 0.0
            or latency < self._minimum_latency
        ):

            self._minimum_latency = latency

        if latency > self._maximum_latency:

            self._maximum_latency = latency

        count = self._sample_count

        if count <= 1:

            self._statistics.average_latency = (
                latency
            )

        else:

            previous = (
                self._statistics.average_latency
            )

            self._statistics.average_latency = (
                (
                    previous * (count - 1)
                    + latency
                )
                / count
            )

# ==============================================================================
# Part 11. Statistics & Diagnostics
# ==============================================================================

    def diagnostics(
        self,
    ) -> dict[str, Any]:

        healthy = (
            self._enabled
            and self._initialized
            and not self._closed
            and not self._frozen
            and self._state
            not in {
                SamplerState.FAILED,
                SamplerState.CLOSED,
            }
            and self.check_integrity()
        )

        return {
            "healthy": healthy,

            "health_score": (
                1.0
                if healthy
                else 0.0
            ),

            "state": self._state.value,

            "sampler_type": (
                self._sampler_type.value
            ),

            "sample_rate": (
                self._sample_rate
            ),

            "statistics": {
                "samples":
                    self._sample_count,

                "accepted":
                    self._accepted_count,

                "rejected":
                    self._rejected_count,

                "errors":
                    self._error_count,

                "acceptance_rate":
                    self.success_rate,

                "rejection_rate":
                    self.failure_rate,

                "average_latency":
                    self._statistics.average_latency,

                "minimum_latency":
                    self._minimum_latency,

                "maximum_latency":
                    self._maximum_latency,

                "bytes_processed":
                    self._statistics.bytes_processed,
            },
        }



    def health(
        self,
    ) -> bool:

        try:

            return bool(
                self._enabled
                and not self._closed
                and not self._frozen
                and self._state
                not in {
                    SamplerState.FAILED,
                    SamplerState.CLOSED,
                }
            )

        except Exception:
            return False


    def metrics(
        self,
    ) -> dict[str, Any]:

        return {
            "sampler.samples.total":
                self._sample_count,

            "sampler.samples.accepted":
                self._accepted_count,

            "sampler.samples.rejected":
                self._rejected_count,

            "sampler.errors.total":
                self._error_count,

            "sampler.success.rate":
                self.success_rate,

            "sampler.failure.rate":
                self.failure_rate,

            "sampler.latency.last":
                self._last_latency,

            "sampler.latency.min":
                self._minimum_latency,

            "sampler.latency.max":
                self._maximum_latency,

            "sampler.latency.avg":
                self._statistics.average_latency,

            "sampler.bytes.processed":
                self._statistics.bytes_processed,

            "sampler.history.size":
                len(self._history),

            "sampler.cache.size":
                len(self._cache),

            "sampler.uptime.seconds":
                self.uptime,
        }


    def statistics_snapshot(
        self,
    ) -> dict[str, Any]:

        with self._lock:

            return deepcopy(
                asdict(
                    self._statistics
                )
            )


    def summary(
        self,
    ) -> dict[str, Any]:

        return {
            "id":
                self._id,

            "name":
                self._name,

            "version":
                self._version,

            "sampler_type":
                self._sampler_type.value,

            "sample_rate":
                self._sample_rate,

            "state":
                self._state.value,

            "enabled":
                self._enabled,

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

            "samples":
                self._sample_count,

            "accepted":
                self._accepted_count,

            "rejected":
                self._rejected_count,

            "errors":
                self._error_count,

            "success_rate":
                self.success_rate,

            "failure_rate":
                self.failure_rate,

            "average_latency":
                self._statistics.average_latency,

            "minimum_latency":
                self._minimum_latency,

            "maximum_latency":
                self._maximum_latency,

            "bytes_processed":
                self._statistics.bytes_processed,

            "uptime":
                self.uptime,
        }


# ==============================================================================
# Part 12. Persistence
# ==============================================================================

    def to_dict(
        self,
    ) -> dict[str, Any]:

        with self._lock:

            return {
                # ------------------------------------------------------------------
                # Identity
                # ------------------------------------------------------------------

                "id":
                    self._id,

                "uuid":
                    str(self._uuid),

                "name":
                    self._name,

                "description":
                    self._description,

                "version":
                    self._version,

                # ------------------------------------------------------------------
                # Configuration
                # ------------------------------------------------------------------

                "sampler_type":
                    self._sampler_type.value,

                "sample_rate":
                    self._sample_rate,

                "seed":
                    self._seed,

                "parent_based":
                    self._parent_based,

                "deterministic":
                    self._deterministic,

                "encoding":
                    self._encoding,

                "history_limit":
                    self._history_limit,

                "options":
                    deepcopy(
                        self._options
                    ),

                "capabilities":
                    int(
                        self._capabilities.value
                    ),

                # ------------------------------------------------------------------
                # Runtime
                # ------------------------------------------------------------------

                "enabled":
                    self._enabled,

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

                "state":
                    self._state.value,

                "created_at":
                    self._created_at,

                "updated_at":
                    self._updated_at,

                "last_sample":
                    self._last_sample,

                "last_decision": (
                    self._last_decision.value
                    if self._last_decision is not None
                    else None
                ),

                "last_trace_id":
                    self._last_trace_id,

                "last_span_id":
                    self._last_span_id,

                "current_context":
                    deepcopy(
                        self._current_context
                    ),

                # ------------------------------------------------------------------
                # Statistics
                # ------------------------------------------------------------------

                "statistics":
                    deepcopy(
                        asdict(
                            self._statistics
                        )
                    ),

                # ------------------------------------------------------------------
                # Counters
                # ------------------------------------------------------------------

                "sample_count":
                    self._sample_count,

                "accepted_count":
                    self._accepted_count,

                "rejected_count":
                    self._rejected_count,

                "error_count":
                    self._error_count,

                "decision_count": {
                    key.value: value
                    for key, value
                    in self._decision_count.items()
                },

                "parent_sample_count":
                    self._parent_sample_count,

                "forced_sample_count":
                    self._forced_sample_count,

                # ------------------------------------------------------------------
                # Performance
                # ------------------------------------------------------------------

                "last_latency":
                    self._last_latency,

                "minimum_latency":
                    self._minimum_latency,

                "maximum_latency":
                    self._maximum_latency,

                # ------------------------------------------------------------------
                # Metadata
                # ------------------------------------------------------------------

                "metadata":
                    deepcopy(
                        self._metadata
                    ),

                "tags":
                    list(
                        self._tags
                    ),

                # ------------------------------------------------------------------
                # History
                # ------------------------------------------------------------------

                "history": [
                    self._serialize_result(
                        result
                    )
                    for result
                    in self._history
                ],

                # ------------------------------------------------------------------
                # Cache
                # ------------------------------------------------------------------

                "cache": {
                    str(key):
                        self._serialize_value(
                            value
                        )
                    for key, value
                    in self._cache.items()
                },
            }


    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "TraceSampler":

        if not isinstance(
            data,
            Mapping,
        ):
            raise SamplerConfigurationError(
                "data must be a mapping"
            )

        sampler_type = data.get(
            "sampler_type",
            SamplerType.TRACE_ID_RATIO.value,
        )

        try:
            sampler_type = SamplerType(
                sampler_type
            )
        except (
            TypeError,
            ValueError,
        ) as exc:

            raise SamplerConfigurationError(
                f"invalid sampler_type: "
                f"{sampler_type!r}"
            ) from exc

        sampler = cls(
            name=data.get(
                "name",
                DEFAULT_SAMPLER_NAME,
            ),
            sampler_type=sampler_type,
            sample_rate=float(
                data.get(
                    "sample_rate",
                    DEFAULT_SAMPLE_RATE,
                )
            ),
            seed=data.get(
                "seed",
                DEFAULT_SEED,
            ),
            parent_based=bool(
                data.get(
                    "parent_based",
                    False,
                )
            ),
            deterministic=bool(
                data.get(
                    "deterministic",
                    False,
                )
            ),
            metadata=deepcopy(
                data.get(
                    "metadata",
                    {},
                )
            ),
            options=deepcopy(
                data.get(
                    "options",
                    {},
                )
            ),
            description=data.get(
                "description",
                "",
            ),
            encoding=data.get(
                "encoding",
                DEFAULT_ENCODING,
            ),
            history_limit=int(
                data.get(
                    "history_limit",
                    DEFAULT_HISTORY_LIMIT,
                )
            ),
        )

        sampler._restore_dict(
            data
        )

        return sampler


    def to_json(
        self,
    ) -> str:

        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            default=str,
        )


    @classmethod
    def from_json(
        cls,
        data: str,
    ) -> "TraceSampler":

        if not isinstance(
            data,
            str,
        ):
            raise SamplerConfigurationError(
                "data must be string"
            )

        try:
            payload = json.loads(
                data
            )
        except json.JSONDecodeError as exc:

            raise SamplerConfigurationError(
                "invalid JSON data"
            ) from exc

        if not isinstance(
            payload,
            Mapping,
        ):
            raise SamplerConfigurationError(
                "JSON root must be an object"
            )

        return cls.from_dict(
            payload
        )


    def snapshot(
        self,
    ) -> dict[str, Any]:

        return deepcopy(
            self.to_dict()
        )


    def restore(
        self,
        snapshot: Mapping[str, Any],
    ) -> "TraceSampler":

        if not isinstance(
            snapshot,
            Mapping,
        ):
            raise SamplerConfigurationError(
                "snapshot must be mapping"
            )

        with self._lock:

            self._restore_dict(
                snapshot
            )

        return self


# ==============================================================================
# Part 13. Copying & Utilities
# ==============================================================================

    def clone(
        self,
    ) -> "TraceSampler":

        return self.from_dict(
            self.snapshot()
        )

    def copy(
        self,
    ) -> "TraceSampler":

        return self.clone()

    def set_rate(
        self,
        rate: float,
    ) -> "TraceSampler":

        self.sample_rate = rate

        return self

    def get_rate(
        self,
    ) -> float:

        return self._sample_rate

    def clamp_rate(
        self,
        rate: float,
    ) -> float:

        return max(
            0.0,
            min(
                1.0,
                float(rate),
            ),
        )

    def touch(
        self,
    ) -> "TraceSampler":

        self._updated_at = time.time()

        return self

    def age(
        self,
    ) -> float:

        return max(
            0.0,
            time.time()
            - self._created_at,
        )

    def timestamp(
        self,
    ) -> float:

        return time.time()

    def is_ready(
        self,
    ) -> bool:

        return (
            self._initialized
            and self._enabled
            and not self._closed
            and not self._frozen
        )

    def is_sampling(
        self,
    ) -> bool:

        return (
            self.is_ready()
            and self._state
            in {
                SamplerState.READY,
                SamplerState.RUNNING,
            }
        )

    def reset_seed(
        self,
    ) -> "TraceSampler":

        with self._lock:

            self._random.seed(
                self._seed
            )

        return self

    def reseed(
        self,
        seed: Optional[int],
    ) -> "TraceSampler":

        self.seed = seed

        return self

    def compact(
        self,
    ) -> "TraceSampler":

        with self._lock:

            self._history = deque(
                list(self._history)[
                    -self._history_limit:
                ],
                maxlen=self._history_limit,
            )

            self._cache.clear()

        return self


# ==============================================================================
# Part 14. Python Protocols
# ==============================================================================

    def __repr__(
        self,
    ) -> str:

        return (
            f"TraceSampler("
            f"id={self._id!r}, "
            f"name={self._name!r}, "
            f"type={self._sampler_type.value!r}, "
            f"rate={self._sample_rate:.4f}, "
            f"state={self._state.value!r}, "
            f"samples={self._sample_count}"
            f")"
        )

    def __str__(
        self,
    ) -> str:

        return (
            f"{self._name} "
            f"[{self._sampler_type.value}] "
            f"rate={self._sample_rate:.3f} "
            f"state={self._state.value}"
        )

    def __bool__(
        self,
    ) -> bool:

        return (
            self._enabled
            and not self._closed
            and not self._frozen
            and self._state
            not in {
                SamplerState.FAILED,
                SamplerState.CLOSED,
            }
        )

    def __call__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> SamplingResult:

        return self.sample(
            *args,
            **kwargs,
        )

    def __len__(
        self,
    ) -> int:

        return len(
            self._history
        )

    def __iter__(
        self,
    ) -> Iterator[SamplingResult]:

        return iter(
            self._history
        )

    def __contains__(
        self,
        item: object,
    ) -> bool:

        if item in self._history:
            return True

        if isinstance(
            item,
            SamplingResult,
        ):
            item_id = getattr(
                item,
                "id",
                None,
            )

            if item_id is not None:
                for entry in self._history:
                    if getattr(
                        entry,
                        "id",
                        None,
                    ) == item_id:
                        return True

        return False

    def __getitem__(
        self,
        index: int,
    ) -> SamplingResult:

        return list(
            self._history
        )[index]

    def __eq__(
        self,
        other: object,
    ) -> bool:

        if self is other:
            return True

        if not isinstance(
            other,
            TraceSampler,
        ):
            return NotImplemented

        return (
            self._uuid
            == other._uuid
        )

    def __hash__(
        self,
    ) -> int:

        return hash(
            self._uuid
        )


# ==============================================================================
# Internal Helpers
# ==============================================================================

    @staticmethod
    def _coerce_rate(
        value: float,
    ) -> float:

        try:
            rate = float(value)

        except (
            TypeError,
            ValueError,
        ) as exc:

            raise InvalidSampleRateError(
                "sample_rate must be numeric"
            ) from exc

        if not (
            0.0 <= rate <= 1.0
        ):
            raise InvalidSampleRateError(
                "sample_rate must be between 0.0 and 1.0"
            )

        return rate

    @staticmethod
    def _coerce_seed(
        value: Optional[int],
    ) -> Optional[int]:

        if value is None:
            return None

        if not isinstance(
            value,
            int,
        ):
            raise SamplerConfigurationError(
                "seed must be int or None"
            )

        return value

    def _ensure_open(
        self,
    ) -> None:

        if self._closed:
            raise SamplerClosedError(
                "sampler is closed"
            )

    def _ensure_sample_operation(
        self,
    ) -> None:

        self._ensure_open()

        if self._frozen:
            raise SamplerFrozenError(
                "sampler is frozen"
            )

        if not self._enabled:
            return

        if not self._initialized:
            self.initialize()

        if not self._running:
            self.start()

    @staticmethod
    def _serialize_value(
        value: Any,
    ) -> Any:

        if isinstance(
            value,
            Enum,
        ):
            return value.value

        if isinstance(
            value,
            Mapping,
        ):
            return {
                str(key):
                    TraceSampler._serialize_value(
                        item
                    )
                for key, item
                in value.items()
            }

        if isinstance(
            value,
            (list, tuple),
        ):
            return [
                TraceSampler._serialize_value(
                    item
                )
                for item in value
            ]

        return deepcopy(
            value
        )

    @classmethod
    def _serialize_record(
        cls,
        record: SamplingRecord,
    ) -> dict[str, Any]:

        # Do NOT use dataclasses.asdict().
        # asdict() recursively traverses nested objects and
        # can enter circular references through metadata/context.

        return {
            "id": record.id,
            "timestamp": record.timestamp,
            "trace_id": record.trace_id,
            "span_id": record.span_id,
            "parent_trace_id":
                record.parent_trace_id,
            "decision":
                record.decision.value,
            "sampled":
                record.sampled,
            "probability":
                record.probability,
            "sampler_type":
                record.sampler_type.value,
            "payload":
                cls._serialize_value(
                    record.payload
                ),
            "metadata":
                cls._serialize_value(
                    record.metadata
                ),
            "attributes":
                cls._serialize_value(
                    record.attributes
                ),
            "context":
                cls._serialize_value(
                    record.context
                ),
            "duration":
                record.duration,
        }

    @classmethod
    def _serialize_result(
        cls,
        result: SamplingResult,
    ) -> dict[str, Any]:

        # Do NOT use asdict(result).
        # SamplingResult may contain nested objects that refer
        # back to the sampler or context.

        data = {
            "decision":
                result.decision.value,
            "sampled":
                result.sampled,
            "probability":
                result.probability,
            "trace_id":
                result.trace_id,
            "span_id":
                result.span_id,
            "timestamp":
                result.timestamp,
            "duration":
                result.duration,
            "metadata":
                cls._serialize_value(
                    result.metadata
                ),
            "attributes":
                cls._serialize_value(
                    result.attributes
                ),
            "message":
                result.message,
        }

        if result.record is not None:
            data["record"] = (
                cls._serialize_record(
                    result.record
                )
            )
        else:
            data["record"] = None

        return data

    @staticmethod
    def _deserialize_record(
        data: Mapping[str, Any],
    ) -> SamplingRecord:

        return SamplingRecord(
            id=data.get(
                "id",
                str(uuid.uuid4()),
            ),
            timestamp=float(
                data.get(
                    "timestamp",
                    time.time(),
                )
            ),
            trace_id=data.get(
                "trace_id"
            ),
            span_id=data.get(
                "span_id"
            ),
            parent_trace_id=data.get(
                "parent_trace_id"
            ),
            decision=SamplingDecision(
                data.get(
                    "decision",
                    SamplingDecision.RECORD_AND_SAMPLE.value,
                )
            ),
            sampled=bool(
                data.get(
                    "sampled",
                    True,
                )
            ),
            probability=float(
                data.get(
                    "probability",
                    1.0,
                )
            ),
            sampler_type=SamplerType(
                data.get(
                    "sampler_type",
                    SamplerType.PROBABILISTIC.value,
                )
            ),
            payload=deepcopy(
                data.get(
                    "payload",
                    {},
                )
            ),
            metadata=deepcopy(
                data.get(
                    "metadata",
                    {},
                )
            ),
            attributes=deepcopy(
                data.get(
                    "attributes",
                    {},
                )
            ),
            context=deepcopy(
                data.get(
                    "context",
                    {},
                )
            ),
            duration=float(
                data.get(
                    "duration",
                    0.0,
                )
            ),
        )

    @classmethod
    def _deserialize_result(
        cls,
        data: Mapping[str, Any],
    ) -> SamplingResult:

        record_data = data.get(
            "record"
        )

        record = (
            cls._deserialize_record(
                record_data
            )
            if isinstance(
                record_data,
                Mapping,
            )
            else None
        )

        return SamplingResult(
            decision=SamplingDecision(
                data.get(
                    "decision",
                    SamplingDecision.RECORD_AND_SAMPLE.value,
                )
            ),
            sampled=bool(
                data.get(
                    "sampled",
                    True,
                )
            ),
            probability=float(
                data.get(
                    "probability",
                    1.0,
                )
            ),
            trace_id=data.get(
                "trace_id"
            ),
            span_id=data.get(
                "span_id"
            ),
            timestamp=float(
                data.get(
                    "timestamp",
                    time.time(),
                )
            ),
            duration=float(
                data.get(
                    "duration",
                    0.0,
                )
            ),
            metadata=deepcopy(
                data.get(
                    "metadata",
                    {})
            ),
            attributes=deepcopy(
                data.get(
                    "attributes",
                    {})
            ),
            record=record,
            message=str(
                data.get(
                    "message",
                    "",
                )
            ),
        )

    def _restore_dict(
        self,
        data: Mapping[str, Any],
    ) -> None:

        identity = data.get(
            "identity",
            {},
        )

        configuration = data.get(
            "configuration",
            {},
        )

        runtime = data.get(
            "runtime",
            {},
        )

        counters = data.get(
            "counters",
            {},
        )

        performance = data.get(
            "performance",
            {},
        )

        statistics = data.get(
            "statistics",
            {},
        )

        # ------------------------------------------------------------------
        # Identity
        # ------------------------------------------------------------------

        if identity:
            self._id = identity.get(
                "id",
                self._id,
            )

            uuid_value = identity.get(
                "uuid",
            )

            if uuid_value:
                try:
                    self._uuid = uuid.UUID(
                        str(uuid_value),
                    )
                except (
                    TypeError,
                    ValueError,
                ):
                    pass

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

            sampler_type = identity.get(
                "sampler_type",
            )

            if sampler_type is not None:
                self._sampler_type = SamplerType(
                    sampler_type,
                )

        else:
            self._id = data.get(
                "id",
                self._id,
            )

            uuid_value = data.get(
                "uuid",
            )

            if uuid_value:
                try:
                    self._uuid = uuid.UUID(
                        str(uuid_value),
                    )
                except (
                    TypeError,
                    ValueError,
                ):
                    pass

            self._name = data.get(
                "name",
                self._name,
            )

            self._description = data.get(
                "description",
                self._description,
            )

            self._version = data.get(
                "version",
                self._version,
            )

            if "sampler_type" in data:
                self._sampler_type = SamplerType(
                    data["sampler_type"],
                )

        # ------------------------------------------------------------------
        # Configuration
        # ------------------------------------------------------------------

        if configuration:
            self._sample_rate = self._coerce_rate(
                configuration.get(
                    "sample_rate",
                    self._sample_rate,
                ),
            )

            self._seed = configuration.get(
                "seed",
                self._seed,
            )

            self._parent_based = bool(
                configuration.get(
                    "parent_based",
                    self._parent_based,
                ),
            )

            self._deterministic = bool(
                configuration.get(
                    "deterministic",
                    self._deterministic,
                ),
            )

            self._encoding = configuration.get(
                "encoding",
                self._encoding,
            )

            self._history_limit = int(
                configuration.get(
                    "history_limit",
                    self._history_limit,
                ),
            )

            self._options = deepcopy(
                configuration.get(
                    "options",
                    self._options,
                ),
            )

            if "capabilities" in configuration:
                self._capabilities = SamplerCapability(
                    int(
                        configuration["capabilities"],
                    ),
                )

        else:
            if "sample_rate" in data:
                self._sample_rate = self._coerce_rate(
                    data["sample_rate"],
                )

            if "seed" in data:
                self._seed = data["seed"]

        # ------------------------------------------------------------------
        # Runtime
        # ------------------------------------------------------------------

        runtime_data = (
            runtime
            if runtime
            else data
        )

        self._enabled = bool(
            runtime_data.get(
                "enabled",
                self._enabled,
            ),
        )

        self._initialized = bool(
            runtime_data.get(
                "initialized",
                self._initialized,
            ),
        )

        self._running = bool(
            runtime_data.get(
                "running",
                self._running,
            ),
        )

        self._active = bool(
            runtime_data.get(
                "active",
                self._active,
            ),
        )

        self._frozen = bool(
            runtime_data.get(
                "frozen",
                self._frozen,
            ),
        )

        self._closed = bool(
            runtime_data.get(
                "closed",
                self._closed,
            ),
        )

        self._state = SamplerState(
            runtime_data.get(
                "state",
                self._state.value,
            ),
        )

        self._created_at = float(
            runtime_data.get(
                "created_at",
                self._created_at,
            ),
        )

        self._updated_at = float(
            runtime_data.get(
                "updated_at",
                self._updated_at,
            ),
        )

        self._last_sample = runtime_data.get(
            "last_sample",
            self._last_sample,
        )

        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------

        if statistics:
            statistics_copy = deepcopy(
                statistics,
            )

            self._statistics = SamplingStatistics(
                samples=int(
                    statistics_copy.get(
                        "samples",
                        self._sample_count,
                    ),
                ),
                accepted=int(
                    statistics_copy.get(
                        "accepted",
                        self._accepted_count,
                    ),
                ),
                rejected=int(
                    statistics_copy.get(
                        "rejected",
                        self._rejected_count,
                    ),
                ),
                errors=int(
                    statistics_copy.get(
                        "errors",
                        self._error_count,
                    ),
                ),
                acceptance_rate=float(
                    statistics_copy.get(
                        "acceptance_rate",
                        0.0,
                    ),
                ),
                rejection_rate=float(
                    statistics_copy.get(
                        "rejection_rate",
                        0.0,
                    ),
                ),
                last_sample=statistics_copy.get(
                    "last_sample",
                ),
                average_latency=float(
                    statistics_copy.get(
                        "average_latency",
                        0.0,
                    ),
                ),
                minimum_latency=float(
                    statistics_copy.get(
                        "minimum_latency",
                        0.0,
                    ),
                ),
                maximum_latency=float(
                    statistics_copy.get(
                        "maximum_latency",
                        0.0,
                    ),
                ),
                bytes_processed=int(
                    statistics_copy.get(
                        "bytes_processed",
                        0,
                    ),
                ),
            )

        # ------------------------------------------------------------------
        # Counters
        # ------------------------------------------------------------------

        self._sample_count = int(
            counters.get(
                "sample_count",
                data.get(
                    "sample_count",
                    self._sample_count,
                ),
            ),
        )

        self._accepted_count = int(
            counters.get(
                "accepted_count",
                data.get(
                    "accepted_count",
                    self._accepted_count,
                ),
            ),
        )

        self._rejected_count = int(
            counters.get(
                "rejected_count",
                data.get(
                    "rejected_count",
                    self._rejected_count,
                ),
            ),
        )

        self._error_count = int(
            counters.get(
                "error_count",
                data.get(
                    "error_count",
                    self._error_count,
                ),
            ),
        )

        self._parent_sample_count = int(
            data.get(
                "parent_sample_count",
                self._parent_sample_count,
            ),
        )

        self._forced_sample_count = int(
            data.get(
                "forced_sample_count",
                self._forced_sample_count,
            ),
        )

        # ------------------------------------------------------------------
        # Performance
        # ------------------------------------------------------------------

        self._last_latency = float(
            performance.get(
                "last_latency",
                data.get(
                    "last_latency",
                    self._last_latency,
                ),
            ),
        )

        self._minimum_latency = float(
            performance.get(
                "minimum_latency",
                data.get(
                    "minimum_latency",
                    self._minimum_latency,
                ),
            ),
        )

        self._maximum_latency = float(
            performance.get(
                "maximum_latency",
                data.get(
                    "maximum_latency",
                    self._maximum_latency,
                ),
            ),
        )

        # ------------------------------------------------------------------
        # Last decision / context
        # ------------------------------------------------------------------

        if "last_decision" in data:
            value = data["last_decision"]

            self._last_decision = (
                SamplingDecision(value)
                if value is not None
                else None
            )

        self._last_trace_id = data.get(
            "last_trace_id",
            self._last_trace_id,
        )

        self._last_span_id = data.get(
            "last_span_id",
            self._last_span_id,
        )

        self._current_context = deepcopy(
            data.get(
                "current_context",
                self._current_context,
            ),
        )

        self._metadata = deepcopy(
            data.get(
                "metadata",
                self._metadata,
            ),
        )

        self._tags = list(
            data.get(
                "tags",
                self._tags,
            ),
        )

        # ------------------------------------------------------------------
        # History
        # ------------------------------------------------------------------

        self._history.clear()

        for item in data.get(
            "history",
            [],
        ):
            if isinstance(
                item,
                Mapping,
            ):
                self._history.append(
                    self._deserialize_result(
                        item,
                    ),
                )

        # ------------------------------------------------------------------
        # Cache
        # ------------------------------------------------------------------

        self._cache = deepcopy(
            data.get(
                "cache",
                {},
            ),
        )

        # ------------------------------------------------------------------
        # Random state
        # ------------------------------------------------------------------

        self._random.seed(
            self._seed,
        )

        self._updated_at = time.time()

# ==============================================================================
# Part 15. Public API Helpers
# ==============================================================================

    def supports(
        self,
        capability: SamplerCapability,
    ) -> bool:

        if not isinstance(
            capability,
            SamplerCapability,
        ):
            raise TypeError(
                "capability must be SamplerCapability"
            )

        return (
            self._capabilities
            & capability
        ) == capability


# ==============================================================================
# Part 16. Compatibility Methods
# ==============================================================================

    def should_sample(
        self,
        trace_id: Optional[TraceId] = None,
        *,
        parent_sampled: Optional[bool] = None,
        attributes: Optional[
            SampleAttributes
        ] = None,
    ) -> bool:

        result, _ = self._sample_internal(
            trace_id=trace_id,
            parent_sampled=parent_sampled,
            attributes=deepcopy(
                attributes or {},
            ),
            context=deepcopy(
                self._current_context,
            ),
        )

        return bool(
            result
        )

    def report(
        self,
    ) -> dict[str, Any]:

        return {
            "identity": {
                "id": self._id,
                "uuid": str(
                    self._uuid,
                ),
                "name": self._name,
                "description": self._description,
                "version": self._version,
                "sampler_type": (
                    self._sampler_type.value
                ),
            },

            "configuration": {
                "sample_rate": self._sample_rate,
                "seed": self._seed,
                "parent_based": self._parent_based,
                "deterministic": self._deterministic,
                "encoding": self._encoding,
                "history_limit": self._history_limit,
                "options": deepcopy(
                    self._options,
                ),
            },

            "runtime": {
                "enabled": self._enabled,
                "initialized": self._initialized,
                "running": self._running,
                "active": self._active,
                "frozen": self._frozen,
                "closed": self._closed,
                "state": self._state.value,
            },

            "statistics": (
                self.statistics_snapshot()
            ),

            "resources": {
                "history": len(
                    self._history,
                ),

                "cache": len(
                    self._cache,
                ),

                "callbacks": len(
                    self._callbacks,
                ),

                "hooks": sum(
                    len(value)
                    for value in self._hooks.values()
                ),

                "filters": len(
                    self._filters,
                ),
            },
        }

# ==============================================================================
# End of TraceSampler class
# ==============================================================================


# ==============================================================================
# Part 17. Public API
# ==============================================================================

Sampler = TraceSampler


__all__ = [

    # --------------------------------------------------------------------------
    # Constants
    # --------------------------------------------------------------------------

    "DEFAULT_SAMPLER_NAME",
    "DEFAULT_SAMPLE_RATE",
    "DEFAULT_SEED",
    "DEFAULT_HISTORY_LIMIT",
    "DEFAULT_ENCODING",
    "SAMPLER_VERSION",

    # --------------------------------------------------------------------------
    # Type Aliases
    # --------------------------------------------------------------------------

    "TraceId",
    "SpanId",
    "SampleRate",
    "SampleMetadata",
    "SampleAttributes",
    "SampleOptions",
    "SampleContext",
    "SamplePayload",
    "SampleHook",
    "SampleCallback",
    "SampleFilter",
    "SampleHistory",

    # --------------------------------------------------------------------------
    # Exceptions
    # --------------------------------------------------------------------------

    "SamplerError",
    "SamplingError",
    "InvalidSampleRateError",
    "SamplerClosedError",
    "SamplerFrozenError",
    "SamplerConfigurationError",

    # --------------------------------------------------------------------------
    # Enums
    # --------------------------------------------------------------------------

    "SamplingDecision",
    "SamplerType",
    "SamplerState",
    "SamplerCapability",

    # --------------------------------------------------------------------------
    # Dataclasses
    # --------------------------------------------------------------------------

    "SamplingRecord",
    "SamplingStatistics",
    "SamplingResult",

    # --------------------------------------------------------------------------
    # Classes
    # --------------------------------------------------------------------------

    "TraceSampler",

    # --------------------------------------------------------------------------
    # Compatibility
    # --------------------------------------------------------------------------

    "Sampler",
]

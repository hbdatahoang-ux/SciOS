"""
SciOS-NG
Runtime Observability - Trace Sampler

File:
    scios/runtime/observability/tracing/sampler.py

Part 1. Foundation
"""

from __future__ import annotations


# ==============================================================================
# Imports
# ==============================================================================

from abc import ABC, abstractmethod

from collections import defaultdict, deque

from copy import copy, deepcopy

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
    Flag,
    auto,
)

from pathlib import Path

from threading import (
    Lock,
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
    Optional,
    Sequence,
    Tuple,
    TypeAlias,
    Union,
)

import json
import random
import threading
import time
import uuid



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


SampleMetadata: TypeAlias = Dict[str, Any]

SampleAttributes: TypeAlias = Dict[str, Any]

SampleOptions: TypeAlias = Dict[str, Any]

SampleContext: TypeAlias = Dict[str, Any]

SamplePayload: TypeAlias = Dict[str, Any]


SampleHook: TypeAlias = Callable[..., Any]

SampleCallback: TypeAlias = Callable[..., None]

SampleFilter: TypeAlias = Callable[[Any], bool]

SampleHistory: TypeAlias = Deque[Any]



# ==============================================================================
# Exceptions
# ==============================================================================


class SamplerError(RuntimeError):
    """
    Base exception for TraceSampler.
    """



class SamplingError(SamplerError):
    """
    Sampling execution error.
    """



class InvalidSampleRateError(SamplerError):
    """
    Invalid sample rate.
    """



class SamplerClosedError(SamplerError):
    """
    Sampler already closed.
    """



class SamplerFrozenError(SamplerError):
    """
    Sampler frozen.
    """



class SamplerConfigurationError(SamplerError):
    """
    Invalid sampler configuration.
    """



# ==============================================================================
# Enums
# ==============================================================================


class SamplingDecision(str, Enum):
    """
    Sampling decision.
    """

    DROP = "drop"

    RECORD = "record"

    RECORD_AND_SAMPLE = (
        "record_and_sample"
    )



class SamplerType(str, Enum):
    """
    Sampler implementation type.
    """

    ALWAYS_ON = "always_on"

    ALWAYS_OFF = "always_off"

    TRACE_ID_RATIO = "trace_id_ratio"

    PARENT_BASED = "parent_based"

    PROBABILISTIC = "probabilistic"

    ADAPTIVE = "adaptive"

    CUSTOM = "custom"



class SamplerState(str, Enum):
    """
    Runtime sampler state.
    """

    CREATED = "created"

    INITIALIZED = "initialized"

    READY = "ready"

    RUNNING = "running"

    STOPPED = "stopped"

    FROZEN = "frozen"

    CLOSED = "closed"

    FAILED = "failed"



class SamplerCapability(Flag):
    """
    Sampler capabilities.
    """

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
# Dataclasses
# ==============================================================================


@dataclass(slots=True)
class SamplingRecord:
    """
    Single sampling operation record.
    """

    id: str = field(
        default_factory=lambda:
            str(uuid.uuid4())
    )


    timestamp: float = field(
        default_factory=time.time
    )


    trace_id: Optional[TraceId] = None


    span_id: Optional[SpanId] = None


    parent_trace_id: Optional[TraceId] = None


    decision: SamplingDecision = (
        SamplingDecision.RECORD_AND_SAMPLE
    )


    sampled: bool = True


    probability: float = 1.0


    sampler_type: SamplerType = (
        SamplerType.PROBABILISTIC
    )


    payload: SamplePayload = field(
        default_factory=dict
    )


    metadata: SampleMetadata = field(
        default_factory=dict
    )


    attributes: SampleAttributes = field(
        default_factory=dict
    )


    context: SampleContext = field(
        default_factory=dict
    )


    duration: float = 0.0



@dataclass(slots=True)
class SamplingStatistics:
    """
    Runtime sampler statistics.
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



@dataclass(slots=True)
class SamplingResult:
    """
    Result of sampling operation.
    """

    decision: SamplingDecision = (
        SamplingDecision.RECORD_AND_SAMPLE
    )


    sampled: bool = True


    probability: float = 1.0


    trace_id: Optional[TraceId] = None


    span_id: Optional[SpanId] = None


    timestamp: float = field(
        default_factory=time.time
    )


    duration: float = 0.0


    metadata: SampleMetadata = field(
        default_factory=dict
    )


    attributes: SampleAttributes = field(
        default_factory=dict
    )


    record: Optional[
        SamplingRecord
    ] = None


    message: str = ""
# ------------------------------------------------------------------------------
# Backward Compatibility Alias
# ------------------------------------------------------------------------------

SamplingRecord = SamplingResult    
# ==============================================================================
# Part 2. Constructor
# ==============================================================================

class TraceSampler:
    """
    Runtime trace sampler.

    Supports:

        • AlwaysOn
        • AlwaysOff
        • TraceIdRatio
        • ParentBased
        • Probabilistic
        • Custom
    """

    def __init__(
        self,
        name: str = DEFAULT_SAMPLER_NAME,
        *,
        sampler_type: SamplerType = SamplerType.TRACE_ID_RATIO,
        sample_rate: SampleRate = DEFAULT_SAMPLE_RATE,
        seed: Optional[int] = DEFAULT_SEED,
        parent_based: bool = False,
        deterministic: bool = False,
        sampler_fn: Optional[
            Callable[..., bool]
        ] = None,
        metadata: Optional[
            SampleMetadata
        ] = None,
        options: Optional[
            SampleOptions
        ] = None,
    ) -> None:


        # ------------------------------------------------------------------
        # Lock
        # ------------------------------------------------------------------

        self._lock = RLock()


        # ------------------------------------------------------------------
        # Validate
        # ------------------------------------------------------------------

        sample_rate = float(sample_rate)

        if not (
            0.0 <= sample_rate <= 1.0
        ):
            raise InvalidSampleRateError(
                "sample_rate must be between 0.0 and 1.0"
            )


        # ------------------------------------------------------------------
        # Identity
        # ------------------------------------------------------------------

        self._uuid: uuid.UUID = uuid.uuid4()

        self._id: str = self._uuid.hex

        self._name: str = str(name)

        self._version: str = SAMPLER_VERSION

        self._description: str = ""

        self._sampler_type: SamplerType = (
            SamplerType(sampler_type)
        )


        # ------------------------------------------------------------------
        # Sampling Configuration
        # ------------------------------------------------------------------

        self._sample_rate: float = sample_rate

        self._seed: Optional[int] = seed

        self._parent_based: bool = bool(
            parent_based
        )

        self._deterministic: bool = bool(
            deterministic
        )

        self._sampler_fn = sampler_fn

        self._encoding: str = DEFAULT_ENCODING

        self._history_limit: int = DEFAULT_HISTORY_LIMIT

        self._options: SampleOptions = deepcopy(
            options or {}
        )


        # ------------------------------------------------------------------
        # Capability Detection
        # ------------------------------------------------------------------

        self._capabilities = (
            SamplerCapability.SERIALIZATION
            |
            SamplerCapability.CALLBACKS
            |
            SamplerCapability.HOOKS
        )


        if deterministic:

            self._capabilities |= (
                SamplerCapability.DETERMINISTIC
            )

        else:

            self._capabilities |= (
                SamplerCapability.PROBABILISTIC
            )


        if parent_based:

            self._capabilities |= (
                SamplerCapability.PARENT_BASED
            )


        if sampler_fn:

            self._capabilities |= (
                SamplerCapability.ADAPTIVE
            )


        # ------------------------------------------------------------------
        # Runtime State
        # ------------------------------------------------------------------

        self._enabled = True

        self._initialized = False

        self._running = False

        self._active = False

        self._frozen = False

        self._closed = False


        self._state = SamplerState.CREATED


        now = time.time()

        self._created_at = now

        self._updated_at = now

        self._last_sample = None



        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------

        self._statistics = SamplingStatistics()


        self._sample_count = 0

        self._accepted_count = 0

        self._rejected_count = 0

        self._error_count = 0


        self._last_latency = 0.0

        self._minimum_latency = 0.0

        self._maximum_latency = 0.0



        # ------------------------------------------------------------------
        # Metadata
        # ------------------------------------------------------------------

        self._metadata = deepcopy(
            metadata or {}
        )

        self._tags = []



        # ------------------------------------------------------------------
        # Runtime Storage
        # ------------------------------------------------------------------

        self._history = deque(
            maxlen=self._history_limit
        )

        self._cache = {}

        self._callbacks = []

        self._hooks = defaultdict(list)

        self._filters = []

        self._event_queue = deque()

        self._snapshot = {}



        # ------------------------------------------------------------------
        # Random Engine
        # ------------------------------------------------------------------

        self._random = random.Random(
            self._seed
        )

# ==============================================================================
# Compatibility aliases
# ==============================================================================

# ==============================================================================
# Part 3. Properties
# ==============================================================================


# ------------------------------------------------------------------------------
# Identity
# ------------------------------------------------------------------------------

    @property
    def id(self) -> str:
        """Unique sampler identifier."""
        return self._id


    @property
    def uuid(self) -> uuid.UUID:
        """Sampler UUID."""
        return self._uuid


    @property
    def name(self) -> str:
        """Sampler name."""
        return self._name


    @name.setter
    def name(
        self,
        value: str,
    ) -> None:

        self._name = str(value)
        self._updated_at = time.time()



    @property
    def version(self) -> str:
        """Sampler version."""
        return self._version



    @property
    def description(self) -> str:
        """Sampler description."""
        return self._description


    @description.setter
    def description(
        self,
        value: str,
    ) -> None:

        self._description = str(value)
        self._updated_at = time.time()



    @property
    def sampler_type(self) -> SamplerType:
        """Sampler implementation type."""
        return self._sampler_type


    @sampler_type.setter
    def sampler_type(
        self,
        value: SamplerType,
    ) -> None:

        self._sampler_type = SamplerType(value)
        self._updated_at = time.time()



    # ------------------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------------------


    @property
    def sample_rate(self) -> float:
        """Sampling probability."""
        return self._sample_rate


    @sample_rate.setter
    def sample_rate(
        self,
        value: float,
    ) -> None:

        value = float(value)

        if not 0.0 <= value <= 1.0:
            raise InvalidSampleRateError(
                "sample_rate must be between 0.0 and 1.0"
            )

        self._sample_rate = value
        self._updated_at = time.time()



    @property
    def seed(self) -> Optional[int]:
        """Random seed."""
        return self._seed


    @seed.setter
    def seed(
        self,
        value: Optional[int],
    ) -> None:

        self._seed = value
        self._random.seed(value)
        self._updated_at = time.time()



    @property
    def parent_based(self) -> bool:
        """Parent based sampling."""
        return self._parent_based


    @parent_based.setter
    def parent_based(
        self,
        value: bool,
    ) -> None:

        self._parent_based = bool(value)
        self._updated_at = time.time()



    @property
    def deterministic(self) -> bool:
        """Deterministic sampling."""
        return self._deterministic


    @deterministic.setter
    def deterministic(
        self,
        value: bool,
    ) -> None:

        self._deterministic = bool(value)
        self._updated_at = time.time()



    @property
    def encoding(self) -> str:
        return self._encoding


    @encoding.setter
    def encoding(
        self,
        value: str,
    ) -> None:

        self._encoding = str(value)
        self._updated_at = time.time()



    @property
    def history_limit(self) -> int:
        return self._history_limit


    @history_limit.setter
    def history_limit(
        self,
        value: int,
    ) -> None:

        value = max(
            1,
            int(value),
        )

        if value != self._history_limit:

            self._history_limit = value

            self._history = deque(
                self._history,
                maxlen=value,
            )

        self._updated_at = time.time()



    @property
    def options(self) -> SampleOptions:
        return deepcopy(
            self._options
        )



    @property
    def capabilities(self) -> SamplerCapability:
        return self._capabilities



    # ------------------------------------------------------------------------------
    # Runtime
    # ------------------------------------------------------------------------------


    @property
    def enabled(self) -> bool:
        return self._enabled


    @enabled.setter
    def enabled(
        self,
        value: bool,
    ) -> None:

        self._enabled = bool(value)
        self._updated_at = time.time()



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
    def last_sample(self) -> Optional[float]:
        return self._last_sample


    @property
    def uptime(self) -> float:
        return time.time() - self._created_at



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



    # ------------------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------------------


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
    def decision_count(
        self,
    ) -> Dict[SamplingDecision, int]:

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
    def last_latency(self) -> float:
        return self._last_latency


    @property
    def minimum_latency(self) -> float:
        return self._minimum_latency


    @property
    def maximum_latency(self) -> float:
        return self._maximum_latency



    @property
    def success_rate(self) -> float:

        if self._sample_count == 0:
            return 0.0

        return (
            self._accepted_count
            /
            self._sample_count
        )



    @property
    def failure_rate(self) -> float:

        if self._sample_count == 0:
            return 0.0

        return (
            self._rejected_count
            /
            self._sample_count
        )



    # ------------------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------------------


    @property
    def metadata(self) -> SampleMetadata:

        return deepcopy(
            self._metadata
        )



    @property
    def tags(self) -> List[str]:

        return list(
            self._tags
        )



    @property
    def history(
        self,
    ) -> List[SamplingResult]:

        return list(
            self._history
        )



    @property
    def cache(
        self,
    ) -> Dict[str, Any]:

        return deepcopy(
            self._cache
        )



    @property
    def callbacks(
        self,
    ) -> List[SampleCallback]:

        return list(
            self._callbacks
        )



    @property
    def hooks(
        self,
    ) -> Dict[str, List[SampleHook]]:

        return {

            name: list(callbacks)

            for name, callbacks
            in self._hooks.items()

        }



    @property
    def filters(
        self,
    ) -> List[SampleFilter]:

        return list(
            self._filters
        )
# ==============================================================================
# Part 4. Sampling API
# ==============================================================================


    def should_sample(
        self,
        trace_id: Optional[TraceId] = None,
        *,
        parent_sampled: Optional[bool] = None,
        attributes: Optional[SampleAttributes] = None,
    ) -> bool:
        """
        Determine whether trace should be sampled.
        """

        if not self._enabled:
            return False

        if self._closed:
            raise SamplerClosedError(
                "Sampler is closed"
            )

        if self._frozen:
            raise SamplerFrozenError(
                "Sampler is frozen"
            )


        #
        # Parent based sampling
        #
        if (
            self._parent_based
            and parent_sampled is not None
        ):
            return bool(parent_sampled)


        #
        # Always ON
        #
        if self._sampler_type == SamplerType.ALWAYS_ON:
            return True


        #
        # Always OFF
        #
        if self._sampler_type == SamplerType.ALWAYS_OFF:
            return False


        #
        # Deterministic Trace ID Ratio
        #
        if (
            self._sampler_type
            == SamplerType.TRACE_ID_RATIO
            and trace_id is not None
        ):

            value = (
                hash(trace_id)
                % 1000000
            ) / 1000000

            return (
                value
                < self._sample_rate
            )


        #
        # Probabilistic
        #
        return (
            self._random.random()
            < self._sample_rate
        )



    # ------------------------------------------------------------------------------


    def sample(
        self,
        trace_id: Optional[TraceId] = None,
        *,
        span_id: Optional[SpanId] = None,
        parent_sampled: Optional[bool] = None,
        attributes: Optional[SampleAttributes] = None,
    ) -> SamplingResult:
        """
        Execute sampling operation.
        """

        start = time.perf_counter()


        try:

            sampled = self.should_sample(
                trace_id=trace_id,
                parent_sampled=parent_sampled,
                attributes=attributes,
            )


            decision = (

                SamplingDecision.RECORD_AND_SAMPLE

                if sampled

                else

                SamplingDecision.DROP

            )


            latency = (
                time.perf_counter()
                - start
            )


            with self._lock:

                self._sample_count += 1


                if sampled:

                    self._accepted_count += 1

                else:

                    self._rejected_count += 1



                self._last_latency = latency


                if (
                    self._minimum_latency == 0.0
                    or latency < self._minimum_latency
                ):

                    self._minimum_latency = latency



                if latency > self._maximum_latency:

                    self._maximum_latency = latency



                self._last_sample = time.time()

                self._updated_at = (
                    self._last_sample
                )



                #
                # Statistics update
                #
                self._statistics.samples = (
                    self._sample_count
                )

                self._statistics.accepted = (
                    self._accepted_count
                )

                self._statistics.rejected = (
                    self._rejected_count
                )


                self._statistics.acceptance_rate = (

                    self._accepted_count
                    /
                    self._sample_count

                    if self._sample_count

                    else 0.0

                )


                self._statistics.rejection_rate = (

                    self._rejected_count
                    /
                    self._sample_count

                    if self._sample_count

                    else 0.0

                )


                self._statistics.last_sample = (
                    self._last_sample
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



                self._statistics.average_latency = (

                    (
                        self._statistics.average_latency
                        *
                        (self._sample_count - 1)
                    )
                    +
                    latency

                )
            
                self._sample_count



                result = SamplingResult(

                    decision=decision,

                    sampled=sampled,

                    probability=self._sample_rate,

                    trace_id=trace_id,

                    span_id=span_id,

                    metadata={

                        "sampler": (
                            self._sampler_type.value
                        ),

                        "timestamp": (
                            self._last_sample
                        ),

                    },

                    attributes=dict(
                        attributes or {}
                    ),

                )



                self._history.append(
                    result
                )


                if (
                    len(self._history)
                    > self._history_limit
                ):

                    self._history.pop(0)



            self._emit_event_safe(
                "after_sample",
                result,
            )


            return result



        except Exception:

            with self._lock:

                self._error_count += 1

                self._statistics.errors = (
                    self._error_count
                )

            raise



    # ------------------------------------------------------------------------------


    def sample_many(
        self,
        traces: Iterable[TraceId],
    ) -> List[SamplingResult]:
        """
        Sample multiple traces.
        """

        return [

            self.sample(
                trace_id=item
            )

            for item in traces

        ]



    # ------------------------------------------------------------------------------


    def sample_batch(
        self,
        traces: Sequence[TraceId],
    ) -> List[SamplingResult]:
        """
        Batch sampling.
        """

        return self.sample_many(
            traces
        )



    # ------------------------------------------------------------------------------


    def decision(
        self,
        trace_id: Optional[TraceId] = None,
    ) -> SamplingDecision:
        """
        Return only decision.
        """

        return self.sample(
            trace_id=trace_id
        ).decision



    # ------------------------------------------------------------------------------


    def probability(
        self,
    ) -> float:
        """
        Current sampling probability.
        """

        return self._sample_rate



    # ------------------------------------------------------------------------------


    def reset_seed(
        self,
    ) -> "TraceSampler":
        """
        Reset random generator.
        """

        with self._lock:

            self._random.seed(
                self._seed
            )

        return self



    # ------------------------------------------------------------------------------


    def reseed(
        self,
        seed: Optional[int],
    ) -> "TraceSampler":
        """
        Change random seed.
        """

        with self._lock:

            self._seed = seed

            self._random.seed(
                seed
            )


        return self
# ==============================================================================
# Part 5. Runtime Operations
# ==============================================================================


    def snapshot(
        self,
    ) -> Dict[str, Any]:
        """
        Create immutable sampler snapshot.
        """

        with self._lock:

            return {

                "identity": {

                    "id": self._id,

                    "uuid": str(
                        self._uuid
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
                        self._options
                    ),

                    "capabilities": int(
                        self._capabilities.value
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

                    "created_at": self._created_at,

                    "updated_at": self._updated_at,

                    "last_sample": self._last_sample,

                },


                "statistics": asdict(
                    self._statistics
                ),


                "counters": {

                    "sample_count": self._sample_count,

                    "accepted_count": self._accepted_count,

                    "rejected_count": self._rejected_count,

                    "error_count": self._error_count,

                },


                "performance": {

                    "last_latency": self._last_latency,

                    "minimum_latency": self._minimum_latency,

                    "maximum_latency": self._maximum_latency,

                },


                "metadata": {

                    "metadata": deepcopy(
                        self._metadata
                    ),

                    "tags": list(
                        self._tags
                    ),

                },

            }



    # ------------------------------------------------------------------------------


    def restore(
        self,
        snapshot: Mapping[str, Any],
    ) -> "TraceSampler":
        """
        Restore sampler from snapshot.
        """

        if not snapshot:
            raise ValueError(
                "Empty snapshot"
            )


        with self._lock:

            identity = snapshot.get(
                "identity",
                {},
            )

            config = snapshot.get(
                "configuration",
                {},
            )

            runtime = snapshot.get(
                "runtime",
                {},
            )

            counters = snapshot.get(
                "counters",
                {},
            )

            performance = snapshot.get(
                "performance",
                {})



            self._name = identity.get(
                "name",
                self._name,
            )


            self._description = identity.get(
                "description",
                self._description,
            )


            self._sampler_type = SamplerType(
                identity.get(
                    "sampler_type",
                    self._sampler_type.value,
                )
            )


            self._sample_rate = float(
                config.get(
                    "sample_rate",
                    self._sample_rate,
                )
            )


            self._seed = config.get(
                "seed",
                self._seed,
            )


            self._parent_based = bool(
                config.get(
                    "parent_based",
                    self._parent_based,
                )
            )


            self._deterministic = bool(
                config.get(
                    "deterministic",
                    self._deterministic,
                )
            )


            self._options = deepcopy(
                config.get(
                    "options",
                    {},
                )
            )


            self._enabled = bool(
                runtime.get(
                    "enabled",
                    self._enabled,
                )
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


            self._state = SamplerState(
                runtime.get(
                    "state",
                    SamplerState.CREATED.value,
                )
            )


            self._sample_count = int(
                counters.get(
                    "sample_count",
                    0,
                )
            )

            self._accepted_count = int(
                counters.get(
                    "accepted_count",
                    0,
                )
            )

            self._rejected_count = int(
                counters.get(
                    "rejected_count",
                    0,
                )
            )

            self._error_count = int(
                counters.get(
                    "error_count",
                    0,
                )
            )


            self._last_latency = float(
                performance.get(
                    "last_latency",
                    0.0,
                )
            )


            self._minimum_latency = float(
                performance.get(
                    "minimum_latency",
                    0.0,
                )
            )


            self._maximum_latency = float(
                performance.get(
                    "maximum_latency",
                    0.0,
                )
            )


            self._metadata = deepcopy(
                snapshot.get(
                    "metadata",
                    {},
                ).get(
                    "metadata",
                    {},
                )
            )


            self._tags = list(
                snapshot.get(
                    "metadata",
                    {},
                ).get(
                    "tags",
                    [],
                )
            )


            self._random.seed(
                self._seed
            )


            self._updated_at = time.time()


        return self



    # ------------------------------------------------------------------------------


    def clone(
        self,
    ) -> "TraceSampler":
        """
        Create independent sampler clone.
        """

        new_sampler = TraceSampler(

            name=self._name,

            sampler_type=self._sampler_type,

            sample_rate=self._sample_rate,

            seed=self._seed,

            parent_based=self._parent_based,

            deterministic=self._deterministic,

            metadata=self._metadata,

            options=self._options,

        )


        new_sampler.restore(
            self.snapshot()
        )

        return new_sampler



    # ------------------------------------------------------------------------------


    def copy(
        self,
    ) -> "TraceSampler":
        """
        Create lightweight copy.
        """

        return self.clone()



    # ------------------------------------------------------------------------------


    def reset(
        self,
    ) -> "TraceSampler":
        """
        Reset runtime counters.
        """

        with self._lock:

            self._statistics = SamplingStatistics()

            self._sample_count = 0

            self._accepted_count = 0

            self._rejected_count = 0

            self._error_count = 0

            self._last_latency = 0.0

            self._minimum_latency = 0.0

            self._maximum_latency = 0.0

            self._last_sample = None

            self._history.clear()

            self._cache.clear()

            self._updated_at = time.time()


        return self



    # ------------------------------------------------------------------------------


    def compact(
        self,
    ) -> "TraceSampler":
        """
        Compact runtime memory.
        """

        with self._lock:

            while len(self._history) > self._history_limit:

                self._history.pop(0)


            self._cache.clear()


        return self



    # ------------------------------------------------------------------------------


    def cleanup(
        self,
    ) -> "TraceSampler":
        """
        Cleanup temporary resources.
        """

        with self._lock:

            self._history.clear()

            self._cache.clear()

            self._active = False

            self._running = False

            self._updated_at = time.time()


        return self



    # ------------------------------------------------------------------------------


    def clear_history(
        self,
    ) -> "TraceSampler":

        with self._lock:

            self._history.clear()

        return self



    # ------------------------------------------------------------------------------


    def touch(
        self,
    ) -> "TraceSampler":

        self._updated_at = time.time()

        return self
# ==============================================================================
# Part 6. Statistics & Diagnostics
# ==============================================================================


    def summary(
        self,
    ) -> Dict[str, Any]:
        """
        Return concise sampler summary.
        """

        with self._lock:

            return {

                "id": self._id,

                "name": self._name,

                "version": self._version,

                "sampler_type": (
                    self._sampler_type.value
                ),

                "sample_rate": (
                    self._sample_rate
                ),

                "state": (
                    self._state.value
                ),

                "enabled": (
                    self._enabled
                ),

                "samples": (
                    self._sample_count
                ),

                "accepted": (
                    self._accepted_count
                ),

                "rejected": (
                    self._rejected_count
                ),

                "errors": (
                    self._error_count
                ),

                "success_rate": (
                    self.success_rate
                ),

                "failure_rate": (
                    self.failure_rate
                ),

                "uptime": (
                    self.uptime
                ),

                "timestamp": (
                    time.time()
                ),

            }



    # ------------------------------------------------------------------------------


    def report(
        self,
    ) -> Dict[str, Any]:
        """
        Generate full runtime report.
        """

        with self._lock:

            return {


                "identity": {

                    "id": self._id,

                    "uuid": str(
                        self._uuid
                    ),

                    "name": self._name,

                    "description": self._description,

                    "version": self._version,

                    "sampler_type":
                        self._sampler_type.value,

                },


                "configuration": {

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

                    "capabilities": [

                        item.name

                        for item in SamplerCapability

                        if (
                            item != SamplerCapability.NONE
                            and item in self._capabilities
                        )

                    ],

                },


                "runtime": {

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

                    "uptime":
                        self.uptime,

                },


                "statistics": {

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

                },


                "resources": {

                    "history_size":
                        len(self._history),

                    "cache_size":
                        len(self._cache),

                    "callbacks":
                        len(self._callbacks),

                    "hooks":
                        sum(
                            len(value)
                            for value
                            in self._hooks.values()
                        ),

                    "filters":
                        len(self._filters),

                },


                "metadata":
                    deepcopy(
                        self._metadata
                    ),


                "tags":
                    list(
                        self._tags
                    ),


                "timestamp":
                    time.time(),

            }



    # ------------------------------------------------------------------------------


    def diagnostics(
        self,
    ) -> Dict[str, Any]:
        """
        Runtime diagnostic information.
        """

        with self._lock:


            healthy = (

                self._enabled

                and not self._closed

                and self._state
                != SamplerState.ERROR

            )


            return {


                "healthy":
                    healthy,


                "health_score":
                    1.0
                    if healthy
                    else 0.0,


                "state":
                    self._state.value,


                "runtime": {

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

                },


                "sampling": {

                    "type":
                        self._sampler_type.value,

                    "rate":
                        self._sample_rate,

                    "parent_based":
                        self._parent_based,

                    "deterministic":
                        self._deterministic,

                },


                "statistics": {

                    "samples":
                        self._sample_count,

                    "accepted":
                        self._accepted_count,

                    "rejected":
                        self._rejected_count,

                    "errors":
                        self._error_count,

                },


                "resources": {

                    "history":
                        len(self._history),

                    "cache":
                        len(self._cache),

                    "callbacks":
                        len(self._callbacks),

                    "hooks":
                        len(self._hooks),

                    "filters":
                        len(self._filters),

                },


                "timestamp":
                    time.time(),

            }



    # ------------------------------------------------------------------------------


    def health(
        self,
    ) -> Dict[str, Any]:
        """
        Return health check result.
        """

        with self._lock:

            healthy = (

                self._enabled

                and not self._closed

                and self._state
                != SamplerState.ERROR

            )


            return {

                "healthy":
                    healthy,

                "status":
                    (
                        "ok"
                        if healthy
                        else "failed"
                    ),

                "state":
                    self._state.value,

                "enabled":
                    self._enabled,

                "running":
                    self._running,

                "active":
                    self._active,

                "sample_rate":
                    self._sample_rate,

                "error_count":
                    self._error_count,

                "last_sample":
                    self._last_sample,

                "timestamp":
                    time.time(),

            }



    # ------------------------------------------------------------------------------


    def metrics(
        self,
    ) -> Dict[str, Any]:
        """
        Export runtime metrics.
        """

        with self._lock:

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


                "sampler.history.size":
                    len(self._history),


                "sampler.cache.size":
                    len(self._cache),


                "sampler.uptime.seconds":
                    self.uptime,


                "timestamp":
                    time.time(),

            }
# ==============================================================================
# Part 7. Validation
# ==============================================================================


    # ------------------------------------------------------------------------------
    # validate()
    # ------------------------------------------------------------------------------

    def validate(
        self,
        *,
        raise_error: bool = False,
    ) -> bool:
        """
        Validate complete sampler integrity.

        Parameters
        ----------
        raise_error:
            Raise validation exception.

        Returns
        -------
        bool
            True if sampler is valid.
        """

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



    # ------------------------------------------------------------------------------
    # validate_rate()
    # ------------------------------------------------------------------------------

    def validate_rate(
        self,
        *,
        raise_error: bool = False,
    ) -> bool:
        """
        Validate sampling probability.

        Valid range:

            0.0 <= sample_rate <= 1.0
        """

        try:

            if not isinstance(
                self._sample_rate,
                (
                    int,
                    float,
                ),
            ):

                raise TypeError(
                    "sample_rate must be numeric."
                )


            rate = float(
                self._sample_rate
            )


            if not (
                0.0
                <= rate
                <= 1.0
            ):

                raise ValueError(
                    "sample_rate must be between 0.0 and 1.0."
                )


            return True


        except Exception:

            if raise_error:
                raise


            return False



    # ------------------------------------------------------------------------------
    # validate_seed()
    # ------------------------------------------------------------------------------

    def validate_seed(
        self,
        *,
        raise_error: bool = False,
    ) -> bool:
        """
        Validate random seed configuration.
        """

        try:

            if self._seed is None:

                return True


            if not isinstance(
                self._seed,
                int,
            ):

                raise TypeError(
                    "seed must be int or None."
                )


            return True


        except Exception:

            if raise_error:
                raise


            return False



    # ------------------------------------------------------------------------------
    # validate_configuration()
    # ------------------------------------------------------------------------------

    def validate_configuration(
        self,
        *,
        raise_error: bool = False,
    ) -> bool:
        """
        Validate sampler configuration.
        """

        try:


            if not isinstance(
                self._sampler_type,
                SamplerType,
            ):

                raise TypeError(
                    "invalid sampler_type."
                )


            if not isinstance(
                self._state,
                SamplerState,
            ):

                raise TypeError(
                    "invalid sampler state."
                )


            if not isinstance(
                self._history_limit,
                int,
            ):

                raise TypeError(
                    "history_limit must be integer."
                )


            if self._history_limit <= 0:

                raise ValueError(
                    "history_limit must be positive."
                )


            if not isinstance(
                self._encoding,
                str,
            ):

                raise TypeError(
                    "encoding must be string."
                )


            if not isinstance(
                self._options,
                dict,
            ):

                raise TypeError(
                    "options must be dictionary."
                )


            if not isinstance(
                self._metadata,
                dict,
            ):

                raise TypeError(
                    "metadata must be dictionary."
                )


            if not isinstance(
                self._capabilities,
                SamplerCapability,
            ):

                raise TypeError(
                    "invalid capabilities."
                )


            if not isinstance(
                self._enabled,
                bool,
            ):

                raise TypeError(
                    "enabled must be bool."
                )


            if not isinstance(
                self._parent_based,
                bool,
            ):

                raise TypeError(
                    "parent_based must be bool."
                )


            if not isinstance(
                self._deterministic,
                bool,
            ):

                raise TypeError(
                    "deterministic must be bool."
                )


            return True


        except Exception:

            if raise_error:
                raise


            return False



    # ------------------------------------------------------------------------------
    # check_integrity()
    # ------------------------------------------------------------------------------

    def check_integrity(
        self,
        *,
        raise_error: bool = False,
    ) -> bool:
        """
        Verify internal runtime objects.
        """

        try:


            if self._statistics is None:

                raise RuntimeError(
                    "statistics object missing."
                )


            if self._history is None:

                raise RuntimeError(
                    "history buffer missing."
                )


            if self._cache is None:

                raise RuntimeError(
                    "cache object missing."
                )


            if self._callbacks is None:

                raise RuntimeError(
                    "callbacks registry missing."
                )


            if self._hooks is None:

                raise RuntimeError(
                    "hooks registry missing."
                )


            if self._filters is None:

                raise RuntimeError(
                    "filters registry missing."
                )


            if self._random is None:

                raise RuntimeError(
                    "random generator missing."
                )


            if self._lock is None:

                raise RuntimeError(
                    "lock object missing."
                )


            #
            # Counter integrity
            #

            counters = (

                self._sample_count,

                self._accepted_count,

                self._rejected_count,

                self._error_count,

            )


            if any(
                value < 0
                for value in counters
            ):

                raise RuntimeError(
                    "statistics counters cannot be negative."
                )


            #
            # Logical integrity
            #

            if (
                self._accepted_count
                +
                self._rejected_count
                >
                self._sample_count
            ):

                raise RuntimeError(
                    "accepted/rejected count exceeds samples."
                )


            return True


        except Exception:

            if raise_error:
                raise


            return False
# ==============================================================================
# Part 8. Events & Hooks
# ==============================================================================


    # ------------------------------------------------------------------------------
    # Sampling Lifecycle Hooks
    # ------------------------------------------------------------------------------

    def before_sample(
        self,
        trace_id: Optional[TraceId] = None,
        **kwargs: Any,
    ) -> None:
        """
        Hook executed before sampling.
        """

        self.emit_event(
            "before_sample",
            trace_id=trace_id,
            sampler=self,
            **kwargs,
        )


    # ------------------------------------------------------------------------------

    def after_sample(
        self,
        result: SamplingResult,
        **kwargs: Any,
    ) -> SamplingResult:
        """
        Hook executed after sampling.
        """

        self.emit_event(
            "after_sample",
            result=result,
            sampler=self,
            **kwargs,
        )

        return result



    # ------------------------------------------------------------------------------
    # Hook Management
    # ------------------------------------------------------------------------------

    def add_hook(
        self,
        event: str,
        hook: SampleHook,
    ) -> "TraceSampler":
        """
        Register a hook handler.
        """

        if not callable(hook):
            raise TypeError(
                "hook must be callable."
            )

        with self._lock:

            hooks = self._hooks.setdefault(
                event,
                [],
            )

            if hook not in hooks:
                hooks.append(hook)

        return self



    # ------------------------------------------------------------------------------

    def remove_hook(
        self,
        event: str,
        hook: SampleHook,
    ) -> "TraceSampler":
        """
        Remove hook handler.
        """

        with self._lock:

            hooks = self._hooks.get(
                event
            )

            if not hooks:
                return self

            if hook in hooks:
                hooks.remove(hook)

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
    ) -> "TraceSampler":
        """
        Clear hooks.

        If event is None:
            remove all hooks.
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
    # Callback Management
    # ------------------------------------------------------------------------------

    def add_callback(
        self,
        callback: SampleCallback,
    ) -> "TraceSampler":
        """
        Register global callback.
        """

        if not callable(callback):
            raise TypeError(
                "callback must be callable."
            )

        with self._lock:

            if callback not in self._callbacks:
                self._callbacks.append(
                    callback
                )

        return self



    # ------------------------------------------------------------------------------

    def remove_callback(
        self,
        callback: SampleCallback,
    ) -> "TraceSampler":
        """
        Remove callback.
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
    ) -> "TraceSampler":
        """
        Remove all callbacks.
        """

        with self._lock:

            self._callbacks.clear()

        return self



    # ------------------------------------------------------------------------------
    # Event Dispatcher
    # ------------------------------------------------------------------------------

    def emit_event(
        self,
        event: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Emit sampler event.

        Hook failures never interrupt
        sampling runtime.
        """

        hooks = list(
            self._hooks.get(
                event,
                [],
            )
        )


        for hook in hooks:

            try:

                hook(
                    *args,
                    **kwargs,
                )

            except Exception:

                continue


        self.notify_callbacks(
            event,
            *args,
            **kwargs,
        )



    # ------------------------------------------------------------------------------

    def notify_callbacks(
        self,
        event: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Notify registered callbacks.
        """

        callbacks = list(
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

                continue
# ==============================================================================
# Part 9. Callbacks
# ==============================================================================


    # ------------------------------------------------------------------------------
    # Subscription API
    # ------------------------------------------------------------------------------

    def subscribe(
        self,
        callback: SampleCallback,
    ) -> "TraceSampler":
        """
        Subscribe callback to sampler events.

        Callback signature:

            callback(
                event,
                *args,
                sampler=self,
                **kwargs
            )
        """

        if not callable(callback):
            raise TypeError(
                "callback must be callable."
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
        callback: SampleCallback,
    ) -> "TraceSampler":
        """
        Remove subscribed callback.
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
    ) -> "TraceSampler":
        """
        Remove all callbacks.
        """

        with self._lock:

            self._callbacks.clear()


        return self



    # ------------------------------------------------------------------------------
    # Callback Notification
    # ------------------------------------------------------------------------------

    def notify_callbacks(
        self,
        event: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Notify all registered callbacks.

        Callback errors are isolated and ignored.
        """

        callbacks = list(
            self._callbacks
        )


        for callback in callbacks:

            try:

                callback(

                    event,

                    *args,

                    sampler=self,

                    **kwargs,

                )


            except Exception:

                #
                # Never allow callback failure
                # to affect runtime sampling.
                #
                continue



    # ------------------------------------------------------------------------------
    # Callback Inspection
    # ------------------------------------------------------------------------------

    def callback_count(
        self,
    ) -> int:
        """
        Return number of registered callbacks.
        """

        return len(
            self._callbacks
        )



    # ------------------------------------------------------------------------------

    def has_callback(
        self,
        callback: SampleCallback,
    ) -> bool:
        """
        Check whether callback exists.
        """

        return callback in self._callbacks
# ==============================================================================
# Part 10. Serialization Helpers
# ==============================================================================


    def to_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Serialize sampler into dictionary.
        """

        with self._lock:

            return {

                # ----------------------------------------------------------
                # Identity
                # ----------------------------------------------------------

                "id": self._id,

                "uuid": str(
                    self._uuid
                ),

                "name": self._name,

                "description": self._description,

                "version": self._version,


                # ----------------------------------------------------------
                # Configuration
                # ----------------------------------------------------------

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


                # ----------------------------------------------------------
                # Runtime
                # ----------------------------------------------------------

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


                # ----------------------------------------------------------
                # Statistics
                # ----------------------------------------------------------

                "statistics":
                    asdict(
                        self._statistics
                    ),

                "sample_count":
                    self._sample_count,

                "accepted_count":
                    self._accepted_count,

                "rejected_count":
                    self._rejected_count,

                "error_count":
                    self._error_count,

                "last_latency":
                    self._last_latency,

                "minimum_latency":
                    self._minimum_latency,

                "maximum_latency":
                    self._maximum_latency,


                # ----------------------------------------------------------
                # Metadata
                # ----------------------------------------------------------

                "metadata":
                    deepcopy(
                        self._metadata
                    ),

                "tags":
                    list(
                        self._tags
                    ),

            }



    # ------------------------------------------------------------------------------

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "TraceSampler":
        """
        Restore sampler from dictionary.
        """


        sampler = cls(

            name=data.get(
                "name",
                DEFAULT_SAMPLER_NAME,
            ),

            sampler_type=SamplerType(
                data.get(
                    "sampler_type",
                    SamplerType.PROBABILISTIC.value,
                )
            ),

            sample_rate=float(
                data.get(
                    "sample_rate",
                    DEFAULT_SAMPLE_RATE,
                )
            ),

            seed=data.get(
                "seed"
            ),

        )


        # ----------------------------------------------------------
        # Identity
        # ----------------------------------------------------------

        sampler._id = data.get(
            "id",
            sampler._id,
        )


        uuid_value = data.get(
            "uuid"
        )

        if uuid_value:

            sampler._uuid = uuid.UUID(
                uuid_value
            )


        # ----------------------------------------------------------
        # Configuration
        # ----------------------------------------------------------

        sampler._description = data.get(
            "description",
            "",
        )


        sampler._parent_based = bool(
            data.get(
                "parent_based",
                False,
            )
        )


        sampler._deterministic = bool(
            data.get(
                "deterministic",
                False,
            )
        )


        sampler._encoding = data.get(
            "encoding",
            DEFAULT_ENCODING,
        )


        sampler._history_limit = int(
            data.get(
                "history_limit",
                DEFAULT_HISTORY_LIMIT,
            )
        )


        sampler._options = deepcopy(
            data.get(
                "options",
                {},
            )
        )


        sampler._capabilities = SamplerCapability(
            data.get(
                "capabilities",
                int(
                    SamplerCapability.NONE.value
                ),
            )
        )


        # ----------------------------------------------------------
        # Runtime
        # ----------------------------------------------------------

        sampler._enabled = bool(
            data.get(
                "enabled",
                True,
            )
        )


        sampler._initialized = bool(
            data.get(
                "initialized",
                False,
            )
        )


        sampler._running = bool(
            data.get(
                "running",
                False,
            )
        )


        sampler._active = bool(
            data.get(
                "active",
                False,
            )
        )


        sampler._frozen = bool(
            data.get(
                "frozen",
                False,
            )
        )


        sampler._closed = bool(
            data.get(
                "closed",
                False,
            )
        )


        sampler._state = SamplerState(
            data.get(
                "state",
                SamplerState.CREATED.value,
            )
        )


        sampler._created_at = data.get(
            "created_at",
            sampler._created_at,
        )


        sampler._updated_at = data.get(
            "updated_at",
            sampler._updated_at,
        )


        sampler._last_sample = data.get(
            "last_sample"
        )


        # ----------------------------------------------------------
        # Statistics
        # ----------------------------------------------------------

        statistics = data.get(
            "statistics"
        )


        if isinstance(
            statistics,
            Mapping,
        ):

            sampler._statistics = SamplingStatistics(
                **statistics
            )


        sampler._sample_count = int(
            data.get(
                "sample_count",
                0,
            )
        )


        sampler._accepted_count = int(
            data.get(
                "accepted_count",
                0,
            )
        )


        sampler._rejected_count = int(
            data.get(
                "rejected_count",
                0,
            )
        )


        sampler._error_count = int(
            data.get(
                "error_count",
                0,
            )
        )


        sampler._last_latency = float(
            data.get(
                "last_latency",
                0.0,
            )
        )


        sampler._minimum_latency = float(
            data.get(
                "minimum_latency",
                0.0,
            )
        )


        sampler._maximum_latency = float(
            data.get(
                "maximum_latency",
                0.0,
            )
        )


        # ----------------------------------------------------------
        # Metadata
        # ----------------------------------------------------------

        sampler._metadata = deepcopy(
            data.get(
                "metadata",
                {},
            )
        )


        sampler._tags = list(
            data.get(
                "tags",
                [],
            )
        )


        return sampler



    # ------------------------------------------------------------------------------

    def to_json(
        self,
        *,
        indent: int = 4,
        sort_keys: bool = True,
    ) -> str:
        """
        Serialize sampler to JSON.
        """

        return json.dumps(

            self.to_dict(),

            indent=indent,

            sort_keys=sort_keys,

            ensure_ascii=False,

        )



    # ------------------------------------------------------------------------------

    @classmethod
    def from_json(
        cls,
        value: str,
    ) -> "TraceSampler":
        """
        Restore sampler from JSON.
        """

        return cls.from_dict(
            json.loads(
                value
            )
        )
# ==============================================================================
# Part 11. Utilities
# ==============================================================================


    def supports(
        self,
        capability: SamplerCapability,
    ) -> bool:
        """
        Check sampler capability support.
        """

        if not isinstance(
            capability,
            SamplerCapability,
        ):
            raise TypeError(
                "capability must be SamplerCapability."
            )


        return (
            self._capabilities & capability
        ) == capability



    # ------------------------------------------------------------------------------

    def random(
        self,
    ) -> float:
        """
        Generate random probability value.

        Returns
        -------
        float
            Value in range [0.0, 1.0)
        """

        with self._lock:

            return self._random.random()



    # ------------------------------------------------------------------------------

    def next_probability(
        self,
    ) -> float:
        """
        Generate next sampling probability.
        """

        return self.random()



    # ------------------------------------------------------------------------------

    def set_rate(
        self,
        rate: float,
    ) -> "TraceSampler":
        """
        Update sampling rate.
        """

        rate = float(rate)


        if not (
            0.0 <= rate <= 1.0
        ):
            raise ValueError(
                "sample_rate must be between 0.0 and 1.0."
            )


        with self._lock:

            self._sample_rate = rate

            self.touch()


        return self



    # ------------------------------------------------------------------------------

    def get_rate(
        self,
    ) -> float:
        """
        Return current sampling rate.
        """

        return self._sample_rate



    # ------------------------------------------------------------------------------

    def age(
        self,
    ) -> float:
        """
        Return sampler lifetime in seconds.
        """

        return (
            time.time()
            -
            self._created_at
        )



    # ------------------------------------------------------------------------------

    def touch(
        self,
    ) -> "TraceSampler":
        """
        Update sampler timestamps.
        """

        now = time.time()

        self._updated_at = now

        if hasattr(
            self,
            "_last_activity",
        ):

            self._last_activity = now


        return self



    # ------------------------------------------------------------------------------

    def timestamp(
        self,
    ) -> float:
        """
        Return current UNIX timestamp.
        """

        return time.time()



    # ------------------------------------------------------------------------------

    def is_ready(
        self,
    ) -> bool:
        """
        Check sampler readiness.
        """

        return (
            self._initialized
            and
            self._enabled
            and
            not self._closed
            and
            not self._frozen
        )



    # ------------------------------------------------------------------------------

    def is_sampling(
        self,
    ) -> bool:
        """
        Check whether sampler can perform sampling.
        """

        return (
            self.is_ready()
            and
            self._state
            in (
                SamplerState.READY,
                SamplerState.RUNNING,
            )
        )



    # ------------------------------------------------------------------------------

    def clamp_rate(
        self,
        rate: float,
    ) -> float:
        """
        Clamp sampling rate into valid range.

        Examples
        --------
        -0.5 -> 0.0
        0.5 -> 0.5
        2.0 -> 1.0
        """

        return max(
            0.0,
            min(
                1.0,
                float(rate),
            ),
        )
# ==============================================================================
# Part 12. Python Protocols
# ==============================================================================


    # ------------------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------------------

    def __repr__(self) -> str:
        """
        Developer representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"id={self._id!r}, "
            f"name={self._name!r}, "
            f"type={self._sampler_type.value!r}, "
            f"rate={self._sample_rate:.4f}, "
            f"state={self._state.value!r}, "
            f"samples={self._sample_count})"
        )


    # ------------------------------------------------------------------------------

    def __str__(self) -> str:
        """
        Human readable representation.
        """

        return (
            f"{self._name} "
            f"[{self._sampler_type.value}] "
            f"rate={self._sample_rate:.3f} "
            f"state={self._state.value}"
        )


    # ------------------------------------------------------------------------------
    # Boolean Protocol
    # ------------------------------------------------------------------------------

    def __bool__(self) -> bool:
        """
        True when sampler is operational.
        """

        return (
            self._enabled
            and self._initialized
            and not self._closed
            and not self._frozen
            and self._state
            not in (
                SamplerState.ERROR,
                SamplerState.CLOSED,
            )
        )


    # ------------------------------------------------------------------------------
    # Callable Protocol
    # ------------------------------------------------------------------------------

    def __call__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> SamplingResult:
        """
        Shortcut:

            sampler(...)
            ==
            sampler.sample(...)
        """

        return self.sample(
            *args,
            **kwargs,
        )


    # ------------------------------------------------------------------------------
    # Length Protocol
    # ------------------------------------------------------------------------------

    def __len__(self) -> int:
        """
        Number of stored sampling records.
        """

        return len(
            self._history
        )


    # ------------------------------------------------------------------------------
    # Iterator Protocol
    # ------------------------------------------------------------------------------

    def __iter__(
        self,
    ) -> Iterator[SamplingResult]:
        """
        Iterate over sampling history.
        """

        return iter(
            self._history
        )


    # ------------------------------------------------------------------------------
    # Container Protocol
    # ------------------------------------------------------------------------------

    def __contains__(
        self,
        item: object,
    ) -> bool:
        """
        Check whether a sampling result exists.
        """

        return item in self._history


    # ------------------------------------------------------------------------------
    # Index Protocol
    # ------------------------------------------------------------------------------

    def __getitem__(
        self,
        index: int,
    ) -> SamplingResult:
        """
        Access sampling history by index.
        """

        return self._history[index]


    # ------------------------------------------------------------------------------
    # Context Manager Protocol
    # ------------------------------------------------------------------------------

    def __enter__(
        self,
    ) -> "TraceSampler":
        """
        Enter runtime context.
        """

        if self._closed:

            raise SamplerClosedError(
                "Cannot enter closed sampler."
            )

        self._active = True

        self._running = True

        self._state = SamplerState.RUNNING

        self.touch()

        return self



    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:
        """
        Exit runtime context.
        """

        self._active = False

        self._running = False

        self.touch()


    # ------------------------------------------------------------------------------
    # Copy Protocol
    # ------------------------------------------------------------------------------

    def __copy__(
        self,
    ) -> "TraceSampler":
        """
        Create shallow copy.
        """

        cls = self.__class__

        obj = cls.__new__(cls)


        for key, value in self.__dict__.items():

            if key == "_lock":

                setattr(
                    obj,
                    key,
                    RLock(),
                )

            else:

                setattr(
                    obj,
                    key,
                    value,
                )


        return obj



    # ------------------------------------------------------------------------------
    # Deep Copy Protocol
    # ------------------------------------------------------------------------------

    def __deepcopy__(
        self,
        memo: Dict[int, Any],
    ) -> "TraceSampler":
        """
        Create deep copy.

        Locks and runtime primitives are recreated.
        """

        cls = self.__class__

        obj = cls.__new__(
            cls
        )


        memo[id(self)] = obj


        for key, value in self.__dict__.items():


            if key == "_lock":

                setattr(
                    obj,
                    key,
                    RLock(),
                )


            elif key == "_random":

                setattr(
                    obj,
                    key,
                    random.Random(
                        self._seed
                    ),
                )


            else:

                setattr(
                    obj,
                    key,
                    deepcopy(
                        value,
                        memo,
                    ),
                )


        return obj



    # ------------------------------------------------------------------------------
    # Equality Protocol
    # ------------------------------------------------------------------------------

    def __eq__(
        self,
        other: object,
    ) -> bool:
        """
        Compare sampler identity.
        """

        if not isinstance(
            other,
            TraceSampler,
        ):
            return NotImplemented


        return (
            self._uuid
            ==
            other._uuid
        )



    # ------------------------------------------------------------------------------
    # Hash Protocol
    # ------------------------------------------------------------------------------

    def __hash__(
        self,
    ) -> int:
        """
        Hash by UUID.
        """

        return hash(
            self._uuid
        )



    # ------------------------------------------------------------------------------
    # Size Protocol
    # ------------------------------------------------------------------------------

    def __sizeof__(
        self,
    ) -> int:
        """
        Approximate memory footprint.
        """

        size = object.__sizeof__(
            self
        )

        size += len(
            self._history
        )

        size += len(
            self._cache
        )

        size += len(
            self._callbacks
        )

        return size
# ==============================================================================
# Part 13. Context Manager
# ==============================================================================


    def __enter__(
        self,
    ) -> "TraceSampler":
        """
        Enter runtime context.

        Automatically:

            1. Initialize sampler
            2. Start sampler
            3. Activate runtime

        Example
        -------

        >>> with TraceSampler() as sampler:
        ...     sampler.sample()

        Returns
        -------
        TraceSampler
        """

        with self._lock:

            if self._closed:

                raise SamplerClosedError(
                    "Cannot enter closed sampler."
                )


            #
            # Initialize
            #
            if not self._initialized:

                self.initialize()


            #
            # Start runtime
            #
            if not self._running:

                self.start()


            self._active = True

            self._updated_at = time.time()


        return self



    # ------------------------------------------------------------------------------


    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> bool:
        """
        Exit runtime context.

        Shutdown sequence:

            1. Stop runtime
            2. Flush transient resources
            3. Cleanup temporary objects
            4. Preserve configuration

        Returns
        -------
        bool

            False:
                Exception is propagated.
        """

        try:

            with self._lock:


                #
                # Stop runtime
                #
                if self._running:

                    self.stop()



                #
                # Cleanup runtime resources
                #
                self.cleanup()



                #
                # Mark inactive
                #
                self._active = False


                self._updated_at = (
                    time.time()
                )


        except Exception:

            #
            # Context exit must never hide
            # original user exception.
            #
            pass


        #
        # Never suppress exceptions
        #
        return False
# ==============================================================================
# Part 14. Public API
# ==============================================================================
Sampler = TraceSampler

__all__ = [

    # ------------------------------------------------------------------
    # Constants
    # ------------------------------------------------------------------

    "DEFAULT_SAMPLER_NAME",

    "DEFAULT_SAMPLE_RATE",

    "DEFAULT_SEED",

    "DEFAULT_HISTORY_LIMIT",

    "DEFAULT_ENCODING",

    "SAMPLER_VERSION",



    # ------------------------------------------------------------------
    # Type Aliases
    # ------------------------------------------------------------------

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



    # ------------------------------------------------------------------
    # Exceptions
    # ------------------------------------------------------------------

    "SamplerError",

    "SamplingError",

    "InvalidSampleRateError",

    "SamplerClosedError",

    "SamplerFrozenError",



    # ------------------------------------------------------------------
    # Enums
    # ------------------------------------------------------------------

    "SamplingDecision",

    "SamplerType",

    "SamplerState",

    "SamplerCapability",



    # ------------------------------------------------------------------
    # Dataclasses
    # ------------------------------------------------------------------

    "SamplingStatistics",

    "SamplingResult",

    "SamplingRecord",



    # ------------------------------------------------------------------
    # Main Class
    # ------------------------------------------------------------------

    "TraceSampler",
    "Sampler",

]
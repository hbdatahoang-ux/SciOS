"""
SciOS-NG
Runtime Observability - Trace Processor

File:
    scios/runtime/observability/tracing/processor.py

Part 1. Foundation
"""


from __future__ import annotations


# ==============================================================================
# Imports
# ==============================================================================

from abc import ABC, abstractmethod

from dataclasses import (
    dataclass,
    field,
)

from enum import (
    Enum,
    Flag,
    auto,
)

from typing import (
    Any,
    Callable,
    Dict,
    Deque,
    List,
    Optional,
    TypeAlias,
)

from collections import deque

import time
import uuid



# ==============================================================================
# Constants
# ==============================================================================

DEFAULT_PROCESSOR_NAME: str = "TraceProcessor"

DEFAULT_BATCH_SIZE: int = 100

DEFAULT_QUEUE_SIZE: int = 10000

DEFAULT_TIMEOUT: float = 30.0

DEFAULT_RETRY_COUNT: int = 3

DEFAULT_HISTORY_LIMIT: int = 1000

DEFAULT_ENCODING: str = "utf-8"


PROCESSOR_VERSION: str = "0.3.0-alpha"

PROCESSOR_API_VERSION: str = "1.0"



# ==============================================================================
# Type Aliases
# ==============================================================================

TraceRecord: TypeAlias = Dict[str, Any]

TracePayload: TypeAlias = Any


ProcessorOptions: TypeAlias = Dict[str, Any]

ProcessorMetadata: TypeAlias = Dict[str, Any]

ProcessorContext: TypeAlias = Dict[str, Any]

ProcessorCache: TypeAlias = Dict[str, Any]


ProcessorHook: TypeAlias = Callable[..., Any]

ProcessorCallback: TypeAlias = Callable[..., None]


ProcessorFilter: TypeAlias = Callable[
    [TraceRecord],
    bool,
]


ProcessorQueue: TypeAlias = Deque[TraceRecord]


ProcessorId: TypeAlias = str

ProcessorName: TypeAlias = str



# ==============================================================================
# Exceptions
# ==============================================================================


class ProcessorError(RuntimeError):
    """
    Base processor exception.
    """



class ProcessorConfigurationError(ProcessorError):
    """
    Invalid processor configuration.
    """



class ProcessorValidationError(ProcessorError):
    """
    Processor validation failure.
    """



class ProcessingError(ProcessorError):
    """
    Runtime processing error.
    """



class QueueOverflowError(ProcessingError):
    """
    Processing queue overflow.
    """



# ==============================================================================
# Enums
# ==============================================================================


class ProcessorState(str, Enum):
    """
    Processor lifecycle state.
    """

    CREATED = "created"

    INITIALIZED = "initialized"

    RUNNING = "running"

    STOPPED = "stopped"

    FROZEN = "frozen"

    CLOSED = "closed"

    FAILED = "failed"



class ProcessorMode(str, Enum):
    """
    Processor execution mode.
    """

    SYNC = "sync"

    ASYNC = "async"

    STREAM = "stream"

    BATCH = "batch"



class ProcessorType(str, Enum):
    """
    Processor implementation type.
    """

    SIMPLE = "simple"

    BATCH = "batch"

    FILTERING = "filtering"

    PIPELINE = "pipeline"

    CUSTOM = "custom"



class ProcessDecision(str, Enum):
    """
    Processing decision.
    """

    ACCEPT = "accept"

    DROP = "drop"

    RETRY = "retry"

    SKIP = "skip"

    ERROR = "error"



class ProcessorCapability(Flag):
    """
    Processor capabilities.
    """

    NONE = 0

    FILTERING = auto()

    BATCHING = auto()

    STREAMING = auto()

    BUFFERING = auto()

    SERIALIZATION = auto()

    VALIDATION = auto()

    RETRY = auto()

    CALLBACKS = auto()

    HOOKS = auto()

    METRICS = auto()

    EXPORT = auto()

    IMPORT = auto()

    CONCURRENT = auto()

    ASYNC_IO = auto()

    PERSISTENCE = auto()



# ==============================================================================
# Dataclasses
# ==============================================================================


@dataclass(slots=True)
class ProcessingRecord:
    """
    Single trace processing request.
    """

    id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    timestamp: float = field(
        default_factory=time.time
    )

    payload: TracePayload = None

    metadata: ProcessorMetadata = field(
        default_factory=dict
    )

    context: ProcessorContext = field(
        default_factory=dict
    )

    tags: List[str] = field(
        default_factory=list
    )



@dataclass(slots=True)
class ProcessingStatistics:
    """
    Processor runtime statistics.
    """

    process_count: int = 0

    success_count: int = 0

    failure_count: int = 0

    dropped_count: int = 0

    filtered_count: int = 0

    retry_count: int = 0

    queued_count: int = 0

    bytes_processed: int = 0


    last_latency: float = 0.0

    minimum_latency: float = 0.0

    maximum_latency: float = 0.0

    average_latency: float = 0.0


    created_at: float = field(
        default_factory=time.time
    )

    updated_at: float = field(
        default_factory=time.time
    )



@dataclass(slots=True)
class ProcessingResult:
    """
    Result of processing operation.
    """

    success: bool = False

    decision: ProcessDecision = ProcessDecision.ACCEPT

    processed: int = 0

    duration: float = 0.0

    message: str = ""

    metadata: ProcessorMetadata = field(
        default_factory=dict
    )

    record: Optional[ProcessingRecord] = None

    exception: Optional[BaseException] = None

    timestamp: float = field(
        default_factory=time.time
    )


    record: Optional[ProcessingRecord] = None


    exception: Optional[BaseException] = None


    timestamp: float = field(
        default_factory=time.time
    )



# ==============================================================================
# Abstract Foundation
# ==============================================================================


class BaseProcessor(ABC):
    """
    Abstract processor contract.
    """

    @abstractmethod
    def process(
        self,
        record: ProcessingRecord,
    ) -> ProcessingResult:
        """
        Process a trace record.
        """
        raise NotImplementedError



# ==============================================================================
# Main Processor Declaration
# ==============================================================================


class TraceProcessor(BaseProcessor):
    """
    SciOS-NG Runtime Trace Processor.
    """

    def process(
        self,
        record: ProcessingRecord,
    ) -> ProcessingResult:

        raise NotImplementedError(
            "TraceProcessor.process() "
            "implemented in later parts"
        )

SpanProcessor = TraceProcessor

# ==============================================================================
# Compatibility aliases
# ==============================================================================

try:
    __all__.append("SpanProcessor")
except NameError:
    pass


    # ==========================================================================
    # Part 2. Constructor
    # ==========================================================================

    def __init__(
        self,
        name: str = DEFAULT_PROCESSOR_NAME,
        *,
        processor_type: ProcessorType = ProcessorType.SIMPLE,
        mode: ProcessorMode = ProcessorMode.SYNC,
        batch_size: int = DEFAULT_BATCH_SIZE,
        queue_size: int = DEFAULT_QUEUE_SIZE,
        timeout: float = DEFAULT_TIMEOUT,
        retry_count: int = DEFAULT_RETRY_COUNT,
        options: Optional[ProcessorOptions] = None,
    ) -> None:
        """
        Initialize TraceProcessor runtime.
        """


        # ----------------------------------------------------------------------
        # Validate configuration
        # ----------------------------------------------------------------------

        if batch_size <= 0:
            raise ProcessorConfigurationError(
                "batch_size must be greater than zero"
            )

        if queue_size <= 0:
            raise ProcessorConfigurationError(
                "queue_size must be greater than zero"
            )

        if timeout <= 0:
            raise ProcessorConfigurationError(
                "timeout must be greater than zero"
            )

        if retry_count < 0:
            raise ProcessorConfigurationError(
                "retry_count cannot be negative"
            )


        # ----------------------------------------------------------------------
        # Identity
        # ----------------------------------------------------------------------

        self._id: str = str(uuid.uuid4())

        self._uuid: uuid.UUID = uuid.UUID(
            self._id
        )

        self._name: str = name

        self._description: str = ""

        self._version: str = PROCESSOR_VERSION

        self._processor_type: ProcessorType = (
            processor_type
        )


        # ----------------------------------------------------------------------
        # Configuration
        # ----------------------------------------------------------------------

        self._mode: ProcessorMode = mode

        self._batch_size: int = batch_size

        self._queue_size: int = queue_size

        self._timeout: float = timeout

        self._retry_count: int = retry_count

        self._history_limit: int = (
            DEFAULT_HISTORY_LIMIT
        )

        self._encoding: str = (
            DEFAULT_ENCODING
        )

        self._options: ProcessorOptions = dict(
            options or {}
        )


        # ----------------------------------------------------------------------
        # Capabilities
        # ----------------------------------------------------------------------

        self._capabilities = (
            ProcessorCapability.VALIDATION
            |
            ProcessorCapability.METRICS
            |
            ProcessorCapability.CALLBACKS
            |
            ProcessorCapability.HOOKS
        )


        if mode == ProcessorMode.BATCH:
            self._capabilities |= (
                ProcessorCapability.BATCHING
            )

        if mode == ProcessorMode.ASYNC:
            self._capabilities |= (
                ProcessorCapability.ASYNC_IO
            )


        # ----------------------------------------------------------------------
        # Lifecycle State
        # ----------------------------------------------------------------------

        self._enabled: bool = True

        self._initialized: bool = False

        self._running: bool = False

        self._active: bool = False

        self._frozen: bool = False

        self._closed: bool = False


        self._state: ProcessorState = (
            ProcessorState.CREATED
        )


        self._created_at: float = time.time()

        self._updated_at: float = (
            self._created_at
        )


        self._last_process: Optional[float] = None


        # ----------------------------------------------------------------------
        # Statistics
        # ----------------------------------------------------------------------

        self._statistics = (
            ProcessingStatistics()
        )


        # ----------------------------------------------------------------------
        # Metadata
        # ----------------------------------------------------------------------

        self._metadata: ProcessorMetadata = {}

        self._context: ProcessorContext = {}

        self._tags: List[str] = []


        # ----------------------------------------------------------------------
        # History
        # ----------------------------------------------------------------------

        self._history: List[
            ProcessingResult
        ] = []


        # ----------------------------------------------------------------------
        # Runtime Containers
        # ----------------------------------------------------------------------

        self._lock = RLock()


        self._queue: ProcessorQueue = deque(
            maxlen=self._queue_size
        )


        self._cache: ProcessorCache = {}


        self._callbacks: List[
            ProcessorCallback
        ] = []


        self._hooks: Dict[
            str,
            List[ProcessorHook],
        ] = defaultdict(list)


        self._filters: List[
            ProcessorFilter
        ] = []


        # ----------------------------------------------------------------------
        # Finalize
        # ----------------------------------------------------------------------

        self._initialized = True

        self._state = (
            ProcessorState.INITIALIZED
        )

        self._updated_at = time.time()

        # ==============================================================================
        # Part 3. Properties
        # ==============================================================================


        # ==============================================================================
        # Identity
        # ==============================================================================


        @property
        def id(
            self,
        ) -> str:
            """
            Unique processor identifier.
            """
            return self._id


        @property
        def uuid(
            self,
        ) -> uuid.UUID:
            """
            Processor UUID.
            """
            return self._uuid


        @property
        def name(
            self,
        ) -> str:
            """
            Processor name.
            """
            return self._name


        @name.setter
        def name(
            self,
            value: str,
        ) -> None:

            with self._lock:

                self._name = str(value)

                self._updated_at = time.time()



        @property
        def description(
            self,
        ) -> str:
            """
            Processor description.
            """
            return self._description


        @description.setter
        def description(
            self,
            value: str,
        ) -> None:

            with self._lock:

                self._description = str(value)

                self._updated_at = time.time()



        @property
        def version(
            self,
        ) -> str:
            """
            Processor version.
            """
            return self._version



        @property
        def processor_type(
            self,
        ) -> ProcessorType:
            """
            Processor implementation type.
            """
            return self._processor_type



        # ==============================================================================
        # Configuration
        # ==============================================================================


        @property
        def mode(
            self,
        ) -> ProcessorMode:
            """
            Processing mode.
            """
            return self._mode


        @mode.setter
        def mode(
            self,
            value: ProcessorMode,
        ) -> None:

            with self._lock:

                self._mode = ProcessorMode(value)

                self._updated_at = time.time()



        @property
        def batch_size(
            self,
        ) -> int:
            """
            Maximum batch size.
            """
            return self._batch_size


        @batch_size.setter
        def batch_size(
            self,
            value: int,
        ) -> None:

            with self._lock:

                self._batch_size = max(
                    1,
                    int(value),
                )

                self._updated_at = time.time()



        @property
        def queue_size(
            self,
        ) -> int:
            """
            Maximum queue size.
            """
            return self._queue_size


        @queue_size.setter
        def queue_size(
            self,
            value: int,
        ) -> None:

            with self._lock:

                value = max(
                    1,
                    int(value),
                )

                if value != self._queue_size:

                    self._queue_size = value

                    self._queue = deque(
                        self._queue,
                        maxlen=value,
                    )

                self._updated_at = time.time()



        @property
        def queue_depth(
            self,
        ) -> int:
            """
            Current queue depth.
            """
            return len(
                self._queue
            )



        @property
        def timeout(
            self,
        ) -> float:
            """
            Processing timeout.
            """
            return self._timeout


        @timeout.setter
        def timeout(
            self,
            value: float,
        ) -> None:

            with self._lock:

                self._timeout = float(value)

                self._updated_at = time.time()



        @property
        def retry_count(
            self,
        ) -> int:
            """
            Retry count.
            """
            return self._retry_count


        @retry_count.setter
        def retry_count(
            self,
            value: int,
        ) -> None:

            with self._lock:

                self._retry_count = max(
                    0,
                    int(value),
                )

                self._updated_at = time.time()



        @property
        def history_limit(
            self,
        ) -> int:
            """
            Maximum history size.
            """
            return self._history_limit


        @history_limit.setter
        def history_limit(
            self,
            value: int,
        ) -> None:

            with self._lock:

                self._history_limit = max(
                    1,
                    int(value),
                )

                self._updated_at = time.time()



        @property
        def encoding(
            self,
        ) -> str:
            """
            Encoding.
            """
            return self._encoding


        @encoding.setter
        def encoding(
            self,
            value: str,
        ) -> None:

            with self._lock:

                self._encoding = str(value)

                self._updated_at = time.time()



        @property
        def options(
            self,
        ) -> ProcessorOptions:
            """
            Processor options.
            """
            return deepcopy(
                self._options
            )



        @property
        def capabilities(
            self,
        ) -> ProcessorCapability:
            """
            Processor capabilities.
            """
            return self._capabilities



        # ==============================================================================
        # Runtime Lifecycle
        # ==============================================================================


        @property
        def enabled(
            self,
        ) -> bool:
            return self._enabled



        @property
        def initialized(
            self,
        ) -> bool:
            return self._initialized



        @property
        def running(
            self,
        ) -> bool:
            return self._running



        @property
        def active(
            self,
        ) -> bool:
            return self._active



        @property
        def frozen(
            self,
        ) -> bool:
            return self._frozen



        @property
        def closed(
            self,
        ) -> bool:
            return self._closed



        @property
        def state(
            self,
        ) -> ProcessorState:
            return self._state



        @property
        def ready(
            self,
        ) -> bool:
            """
            Processor ready state.
            """

            return (
                self._initialized
                and
                not self._closed
            )



        @property
        def available(
            self,
        ) -> bool:
            """
            Processor availability.
            """

            return (
                self._enabled
                and
                self.ready
            )



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
        def last_process(
            self,
        ) -> Optional[float]:
            return self._last_process



        @property
        def uptime(
            self,
        ) -> float:
            """
            Processor uptime.
            """

            return (
                time.time()
                -
                self._created_at
            )



        # ==============================================================================
        # Statistics
        # ==============================================================================


        @property
        def statistics(
            self,
        ) -> ProcessingStatistics:
            """
            Runtime statistics snapshot.
            """

            return deepcopy(
                self._statistics
            )



        @property
        def process_count(
            self,
        ) -> int:

            return (
                self._statistics.process_count
            )



        @property
        def success_count(
            self,
        ) -> int:

            return (
                self._statistics.success_count
            )



        @property
        def failure_count(
            self,
        ) -> int:

            return (
                self._statistics.failure_count
            )



        @property
        def dropped_count(
            self,
        ) -> int:

            return (
                self._statistics.dropped_count
            )



        @property
        def queued_count(
            self,
        ) -> int:

            return (
                self._statistics.queued_count
            )



        @property
        def success_rate(
            self,
        ) -> float:
            """
            Successful processing ratio.
            """

            total = (
                self._statistics.process_count
            )

            if total == 0:
                return 0.0

            return (
                self._statistics.success_count
                /
                total
            )



        @property
        def failure_rate(
            self,
        ) -> float:
            """
            Failure processing ratio.
            """

            total = (
                self._statistics.process_count
            )

            if total == 0:
                return 0.0

            return (
                self._statistics.failure_count
                /
                total
            )



        @property
        def latency(
            self,
        ) -> Dict[str, float]:
            """
            Latency statistics.
            """

            return {
                "last": self._statistics.last_latency,
                "minimum": self._statistics.minimum_latency,
                "maximum": self._statistics.maximum_latency,
                "average": self._statistics.average_latency,
            }



        # ==============================================================================
        # Metadata
        # ==============================================================================


        @property
        def metadata(
            self,
        ) -> ProcessorMetadata:
            """
            Processor metadata.
            """

            return deepcopy(
                self._metadata
            )



        @property
        def context(
            self,
        ) -> ProcessorContext:
            """
            Runtime context.
            """

            return deepcopy(
                self._context
            )



        @property
        def tags(
            self,
        ) -> List[str]:
            """
            Processor tags.
            """

            return list(
                self._tags
            )



        @property
        def history(
            self,
        ) -> List[ProcessingResult]:
            """
            Processing history.
            """

            return list(
                self._history
            )



        @property
        def history_count(
            self,
        ) -> int:
            """
            Number of history records.
            """

            return len(
                self._history
            )



        @property
        def cache(
            self,
        ) -> ProcessorCache:
            """
            Runtime cache snapshot.
            """

            return deepcopy(
                self._cache
            )



        @property
        def callbacks(
            self,
        ) -> List[ProcessorCallback]:
            """
            Registered callbacks.
            """

            return list(
                self._callbacks
            )



        @property
        def hooks(
            self,
        ) -> Dict[str, List[ProcessorHook]]:
            """
            Registered hooks.
            """

            return {

                name: list(items)

                for name, items

                in self._hooks.items()

            }



        @property
        def filters(
            self,
        ) -> List[ProcessorFilter]:
            """
            Registered filters.
            """

            return list(
                self._filters
            )
# ==============================================================================
# Part 4. Processing API
# ==============================================================================

def process(
    self,
    record: Union[
        ProcessingRecord,
        TraceRecord,
        Mapping[str, Any],
    ],
) -> ProcessingResult:
    """
    Process a single trace record.

    This is the primary processing entry point.

    Parameters
    ----------
    record
        Trace record to process.

    Returns
    -------
    ProcessingResult
        Processing result.
    """

    self.validate()

    if not isinstance(
        record,
        ProcessingRecord,
    ):
        record = ProcessingRecord(
            payload=dict(record),
        )

    self.before_process(
        record,
    )

    started = time.perf_counter()

    try:

        for processor_filter in self._filters:

            if not processor_filter(
                record.payload,
            ):

                result = ProcessingResult(
                    success=False,
                    decision=ProcessDecision.DROP,
                    processed=0,
                    duration=0.0,
                    message="Record rejected by filter.",
                )

                self._dropped_count += 1
                self._failure_count += 1
                self._process_count += 1

                self.after_process(
                    record,
                    result,
                )

                return result

        payload = self.serialize(
            record,
        )

        self.write(
            payload,
        )

        latency = (
            time.perf_counter()
            - started
        )

        self._last_latency = latency

        if (
            self._minimum_latency == 0.0
            or latency < self._minimum_latency
        ):
            self._minimum_latency = latency

        if latency > self._maximum_latency:
            self._maximum_latency = latency

        self._statistics.last_latency = latency

        self._statistics.minimum_latency = (
            self._minimum_latency
        )

        self._statistics.maximum_latency = (
            self._maximum_latency
        )

        self._statistics.process_count += 1
        self._statistics.success_count += 1

        self._process_count += 1
        self._success_count += 1

        self._last_process = time.time()
        self._updated_at = self._last_process

        result = ProcessingResult(
            success=True,
            decision=ProcessDecision.ACCEPT,
            processed=1,
            duration=latency,
        )

        self._history.append(
            result,
        )

        if (
            len(self._history)
            > self._history_limit
        ):
            self._history.pop(0)

        self.after_process(
            record,
            result,
        )

        return result

    except Exception as exc:

        latency = (
            time.perf_counter()
            - started
        )

        self._statistics.process_count += 1
        self._statistics.failure_count += 1

        self._process_count += 1
        self._failure_count += 1

        result = ProcessingResult(
            success=False,
            decision=ProcessDecision.ERROR,
            processed=0,
            duration=latency,
            message=str(exc),
        )

        self.after_process(
            record,
            result,
        )

        raise


# ------------------------------------------------------------------------------

def process_batch(
    self,
    records: Iterable[
        ProcessingRecord,
    ],
) -> List[ProcessingResult]:
    """
    Process a batch of records.
    """

    results: List[
        ProcessingResult
    ] = []

    for record in records:

        results.append(
            self.process(
                record,
            )
        )

    return results


# ------------------------------------------------------------------------------

def process_many(
    self,
    records: Iterable[
        ProcessingRecord,
    ],
) -> List[ProcessingResult]:
    """
    Alias of process_batch().
    """

    return self.process_batch(
        records,
    )


# ------------------------------------------------------------------------------

def enqueue(
    self,
    record: ProcessingRecord,
) -> "TraceProcessor":
    """
    Add a record to the processing queue.
    """

    with self._lock:

        if (
            len(self._queue)
            >= self._queue.maxlen
        ):
            raise QueueOverflowError(
                "Processor queue is full."
            )

        self._queue.append(
            record,
        )

        self._queued_count += 1

        self._statistics.queued_count += 1

    return self


# ------------------------------------------------------------------------------

def dequeue(
    self,
) -> Optional[
    ProcessingRecord
]:
    """
    Remove one record from the queue.
    """

    with self._lock:

        if not self._queue:
            return None

        return self._queue.popleft()


# ------------------------------------------------------------------------------

def flush(self) -> List[
    ProcessingResult
]:
    """
    Process every queued record.
    """

    self.before_flush()

    results: List[
        ProcessingResult
    ] = []

    while True:

        record = self.dequeue()

        if record is None:
            break

        results.append(
            self.process(
                record,
            )
        )

    self.after_flush()

    return results


# ------------------------------------------------------------------------------

def clear(self) -> "TraceProcessor":
    """
    Clear runtime state.
    """

    with self._lock:

        self._queue.clear()

        self._cache.clear()

        self._history.clear()

    return self


# ------------------------------------------------------------------------------

def reset_queue(
    self,
) -> "TraceProcessor":
    """
    Remove every queued record.
    """

    with self._lock:

        self._queue.clear()

        self._queued_count = 0

        self._statistics.queued_count = 0

    return self
# ==============================================================================
# Part 5. Runtime Operations
# ==============================================================================

def snapshot(self) -> Dict[str, Any]:
    """
    Create a snapshot of the processor state.

    Returns
    -------
    Dict[str, Any]
        Serializable runtime snapshot.
    """

    return {
        # ------------------------------------------------------------------
        # Identity
        # ------------------------------------------------------------------
        "id": self._id,
        "uuid": str(self._uuid),
        "name": self._name,
        "description": self._description,
        "version": self._version,
        "processor_type": self._processor_type.value,

        # ------------------------------------------------------------------
        # Configuration
        # ------------------------------------------------------------------
        "mode": self._mode.value,
        "batch_size": self._batch_size,
        "queue_size": self._queue_size,
        "timeout": self._timeout,
        "retry_count": self._retry_count,
        "history_limit": self._history_limit,
        "encoding": self._encoding,
        "options": deepcopy(self._options),

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
        "last_process": self._last_process,

        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------
        "statistics": deepcopy(
            self._statistics
        ),
        "process_count": self._process_count,
        "success_count": self._success_count,
        "failure_count": self._failure_count,
        "dropped_count": self._dropped_count,
        "queued_count": self._queued_count,
        "last_latency": self._last_latency,
        "minimum_latency": self._minimum_latency,
        "maximum_latency": self._maximum_latency,

        # ------------------------------------------------------------------
        # Metadata
        # ------------------------------------------------------------------
        "metadata": deepcopy(
            self._metadata
        ),
        "context": deepcopy(
            self._context
        ),
        "tags": list(
            self._tags
        ),
    }


# ------------------------------------------------------------------------------

def restore(
    self,
    snapshot: Dict[str, Any],
) -> "TraceProcessor":
    """
    Restore the processor from a snapshot.

    Parameters
    ----------
    snapshot
        Snapshot created by snapshot().

    Returns
    -------
    TraceProcessor
    """

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    self._id = snapshot.get(
        "id",
        self._id,
    )

    self._uuid = uuid.UUID(
        snapshot.get(
            "uuid",
            str(self._uuid),
        )
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

    self._processor_type = (
        ProcessorType(
            snapshot.get(
                "processor_type",
                self._processor_type.value,
            )
        )
    )

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    self._mode = ProcessorMode(
        snapshot.get(
            "mode",
            self._mode.value,
        )
    )

    self._batch_size = snapshot.get(
        "batch_size",
        self._batch_size,
    )

    self._queue_size = snapshot.get(
        "queue_size",
        self._queue_size,
    )

    self._timeout = snapshot.get(
        "timeout",
        self._timeout,
    )

    self._retry_count = snapshot.get(
        "retry_count",
        self._retry_count,
    )

    self._history_limit = snapshot.get(
        "history_limit",
        self._history_limit,
    )

    self._encoding = snapshot.get(
        "encoding",
        self._encoding,
    )

    self._options = deepcopy(
        snapshot.get(
            "options",
            self._options,
        )
    )

    # ------------------------------------------------------------------
    # Runtime
    # ------------------------------------------------------------------

    self._enabled = snapshot.get(
        "enabled",
        self._enabled,
    )

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

    self._frozen = snapshot.get(
        "frozen",
        self._frozen,
    )

    self._closed = snapshot.get(
        "closed",
        self._closed,
    )

    self._state = ProcessorState(
        snapshot.get(
            "state",
            self._state.value,
        )
    )

    self._created_at = snapshot.get(
        "created_at",
        self._created_at,
    )

    self._updated_at = snapshot.get(
        "updated_at",
        self._updated_at,
    )

    self._last_process = snapshot.get(
        "last_process",
        self._last_process,
    )

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    statistics = snapshot.get(
        "statistics",
    )

    if isinstance(
        statistics,
        ProcessingStatistics,
    ):
        self._statistics = deepcopy(
            statistics
        )

    self._process_count = snapshot.get(
        "process_count",
        self._process_count,
    )

    self._success_count = snapshot.get(
        "success_count",
        self._success_count,
    )

    self._failure_count = snapshot.get(
        "failure_count",
        self._failure_count,
    )

    self._dropped_count = snapshot.get(
        "dropped_count",
        self._dropped_count,
    )

    self._queued_count = snapshot.get(
        "queued_count",
        self._queued_count,
    )

    self._last_latency = snapshot.get(
        "last_latency",
        self._last_latency,
    )

    self._minimum_latency = snapshot.get(
        "minimum_latency",
        self._minimum_latency,
    )

    self._maximum_latency = snapshot.get(
        "maximum_latency",
        self._maximum_latency,
    )

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    self._metadata = deepcopy(
        snapshot.get(
            "metadata",
            self._metadata,
        )
    )

    self._context = deepcopy(
        snapshot.get(
            "context",
            self._context,
        )
    )

    self._tags = list(
        snapshot.get(
            "tags",
            self._tags,
        )
    )

    return self


# ------------------------------------------------------------------------------

def clone(self) -> "TraceProcessor":
    """
    Create a deep clone.
    """

    return deepcopy(self)


# ------------------------------------------------------------------------------

def copy(self) -> "TraceProcessor":
    """
    Create a shallow copy.
    """

    return copy(self)


# ------------------------------------------------------------------------------

def reset(self) -> "TraceProcessor":
    """
    Reset runtime state and statistics while preserving
    processor identity and configuration.
    """

    self._queue.clear()

    self._cache.clear()

    self._history.clear()

    self._statistics = (
        ProcessingStatistics()
    )

    self._process_count = 0
    self._success_count = 0
    self._failure_count = 0
    self._dropped_count = 0
    self._queued_count = 0

    self._last_latency = 0.0
    self._minimum_latency = 0.0
    self._maximum_latency = 0.0

    self._last_process = None

    self._running = False
    self._active = False
    self._initialized = False

    self._state = (
        ProcessorState.CREATED
    )

    self._updated_at = time.time()

    return self


# ------------------------------------------------------------------------------

def compact(self) -> "TraceProcessor":
    """
    Compact runtime memory.

    Keeps only the newest history entry.
    """

    if len(self._history) > 1:

        self._history[:] = (
            self._history[-1:]
        )

    return self


# ------------------------------------------------------------------------------

def cleanup(self) -> "TraceProcessor":
    """
    Cleanup transient runtime resources.
    """

    self._queue.clear()

    self._cache.clear()

    self._history.clear()

    return self
# ==============================================================================
# Part 6. Statistics & Diagnostics
# ==============================================================================

def summary(self) -> Dict[str, Any]:
    """
    Return a concise processor summary.
    """

    return {
        "id": self._id,
        "name": self._name,
        "type": self._processor_type.value,
        "mode": self._mode.value,
        "state": self._state.value,
        "enabled": self._enabled,
        "running": self._running,
        "processes": self._process_count,
        "successes": self._success_count,
        "failures": self._failure_count,
        "dropped": self._dropped_count,
        "queued": len(self._queue),
        "success_rate": self.success_rate,
        "uptime": self.uptime,
    }


# ------------------------------------------------------------------------------

def report(self) -> Dict[str, Any]:
    """
    Return a complete runtime report.
    """

    return {

        # ------------------------------------------------------------------
        # Identity
        # ------------------------------------------------------------------

        "identity": {

            "id": self._id,

            "uuid": str(self._uuid),

            "name": self._name,

            "description": self._description,

            "version": self._version,

            "processor_type": (
                self._processor_type.value
            ),
        },

        # ------------------------------------------------------------------
        # Configuration
        # ------------------------------------------------------------------

        "configuration": {

            "mode": self._mode.value,

            "batch_size": self._batch_size,

            "queue_size": self._queue_size,

            "timeout": self._timeout,

            "retry_count": self._retry_count,

            "history_limit": self._history_limit,

            "encoding": self._encoding,

            "options": deepcopy(
                self._options
            ),

            "capabilities": [
                capability.name
                for capability in ProcessorCapability
                if (
                    capability
                    != ProcessorCapability.NONE
                    and capability
                    in self._capabilities
                )
            ],
        },

        # ------------------------------------------------------------------
        # Runtime
        # ------------------------------------------------------------------

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

            "last_process": self._last_process,

            "uptime": self.uptime,
        },

        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------

        "statistics": {

            "process_count": self._process_count,

            "success_count": self._success_count,

            "failure_count": self._failure_count,

            "dropped_count": self._dropped_count,

            "queued_count": self._queued_count,

            "queue_length": len(
                self._queue
            ),

            "last_latency": self._last_latency,

            "minimum_latency": (
                self._minimum_latency
            ),

            "maximum_latency": (
                self._maximum_latency
            ),

            "average_latency": (
                self._statistics.average_latency
            ),

            "bytes_processed": (
                self._statistics.bytes_processed
            ),

            "success_rate": (
                self.success_rate
            ),

            "failure_rate": (
                self.failure_rate
            ),
        },

        # ------------------------------------------------------------------
        # Metadata
        # ------------------------------------------------------------------

        "metadata": deepcopy(
            self._metadata
        ),

        "context": deepcopy(
            self._context
        ),

        "tags": list(
            self._tags
        ),
    }


# ------------------------------------------------------------------------------

def diagnostics(self) -> Dict[str, Any]:
    """
    Return processor diagnostic information.
    """

    return {

        "healthy": (
            self._enabled
            and not self._closed
            and self._state
            != ProcessorState.FAILED
        ),

        "state": self._state.value,

        "queue_length": len(
            self._queue
        ),

        "queue_capacity": (
            self._queue_size
        ),

        "cache_entries": len(
            self._cache
        ),

        "history_entries": len(
            self._history
        ),

        "callback_count": len(
            self._callbacks
        ),

        "hook_events": len(
            self._hooks
        ),

        "filter_count": len(
            self._filters
        ),

        "uptime": self.uptime,
    }


# ------------------------------------------------------------------------------

def health(self) -> Dict[str, Any]:
    """
    Return processor health information.
    """

    healthy = (

        self._enabled

        and self._initialized

        and not self._closed

        and self._state
        != ProcessorState.FAILED

    )

    return {

        "healthy": healthy,

        "enabled": self._enabled,

        "initialized": (
            self._initialized
        ),

        "running": self._running,

        "active": self._active,

        "state": self._state.value,

        "queue": len(
            self._queue
        ),

        "errors": (
            self._failure_count
        ),
    }


# ------------------------------------------------------------------------------

def metrics(self) -> Dict[str, Any]:
    """
    Return runtime metrics.
    """

    return {

        "process_count": (
            self._process_count
        ),

        "success_count": (
            self._success_count
        ),

        "failure_count": (
            self._failure_count
        ),

        "dropped_count": (
            self._dropped_count
        ),

        "queued_count": (
            self._queued_count
        ),

        "queue_length": len(
            self._queue
        ),

        "last_latency": (
            self._last_latency
        ),

        "minimum_latency": (
            self._minimum_latency
        ),

        "maximum_latency": (
            self._maximum_latency
        ),

        "average_latency": (
            self._statistics.average_latency
        ),

        "bytes_processed": (
            self._statistics.bytes_processed
        ),

        "success_rate": (
            self.success_rate
        ),

        "failure_rate": (
            self.failure_rate
        ),

        "uptime": self.uptime,
    }
# ==============================================================================
# Part 7. Validation
# ==============================================================================

def validate(self) -> bool:
    """
    Validate the processor.

    Returns
    -------
    bool
        True if the processor is valid.

    Raises
    ------
    ProcessorValidationError
        If validation fails.
    """

    self.validate_configuration()

    self.validate_queue()

    self.check_integrity()

    return True


# ------------------------------------------------------------------------------

def validate_record(
    self,
    record: Union[
        ProcessingRecord,
        TraceRecord,
        Mapping[str, Any],
    ],
) -> bool:
    """
    Validate a processing record.

    Parameters
    ----------
    record
        Processing record.

    Returns
    -------
    bool
    """

    if record is None:

        raise ProcessorValidationError(
            "Record cannot be None."
        )

    if isinstance(
        record,
        ProcessingRecord,
    ):

        payload = record.payload

    elif isinstance(
        record,
        Mapping,
    ):

        payload = record

    else:

        raise ProcessorValidationError(
            "Invalid processing record."
        )

    if payload is None:

        raise ProcessorValidationError(
            "Record payload cannot be None."
        )

    return True


# ------------------------------------------------------------------------------

def validate_configuration(self) -> bool:
    """
    Validate processor configuration.

    Returns
    -------
    bool
    """

    if self._batch_size <= 0:

        raise ProcessorConfigurationError(
            "batch_size must be greater than zero."
        )

    if self._queue_size <= 0:

        raise ProcessorConfigurationError(
            "queue_size must be greater than zero."
        )

    if self._timeout < 0:

        raise ProcessorConfigurationError(
            "timeout cannot be negative."
        )

    if self._retry_count < 0:

        raise ProcessorConfigurationError(
            "retry_count cannot be negative."
        )

    if self._history_limit <= 0:

        raise ProcessorConfigurationError(
            "history_limit must be greater than zero."
        )

    if not isinstance(
        self._mode,
        ProcessorMode,
    ):

        raise ProcessorConfigurationError(
            "Invalid processor mode."
        )

    if not isinstance(
        self._processor_type,
        ProcessorType,
    ):

        raise ProcessorConfigurationError(
            "Invalid processor type."
        )

    if not isinstance(
        self._encoding,
        str,
    ):

        raise ProcessorConfigurationError(
            "Invalid encoding."
        )

    return True


# ------------------------------------------------------------------------------

def validate_queue(self) -> bool:
    """
    Validate processor queue.

    Returns
    -------
    bool
    """

    if not isinstance(
        self._queue,
        deque,
    ):

        raise ProcessorValidationError(
            "Queue must be a deque."
        )

    if self._queue.maxlen != self._queue_size:

        raise ProcessorValidationError(
            "Queue size does not match configuration."
        )

    if len(self._queue) > self._queue_size:

        raise ProcessorValidationError(
            "Queue exceeds configured capacity."
        )

    for record in self._queue:

        self.validate_record(
            record,
        )

    return True


# ------------------------------------------------------------------------------

def check_integrity(self) -> bool:
    """
    Check processor integrity.

    Returns
    -------
    bool
    """

    if self._success_count > self._process_count:

        raise ProcessorValidationError(
            "success_count exceeds process_count."
        )

    if self._failure_count > self._process_count:

        raise ProcessorValidationError(
            "failure_count exceeds process_count."
        )

    if (
        self._success_count
        + self._failure_count
    ) > self._process_count:

        raise ProcessorValidationError(
            "Statistics are inconsistent."
        )

    if self._last_latency < 0:

        raise ProcessorValidationError(
            "Invalid last latency."
        )

    if self._minimum_latency < 0:

        raise ProcessorValidationError(
            "Invalid minimum latency."
        )

    if self._maximum_latency < 0:

        raise ProcessorValidationError(
            "Invalid maximum latency."
        )

    if (
        self._maximum_latency
        < self._minimum_latency
        and self._maximum_latency > 0
    ):

        raise ProcessorValidationError(
            "Maximum latency is smaller than minimum latency."
        )

    if not isinstance(
        self._statistics,
        ProcessingStatistics,
    ):

        raise ProcessorValidationError(
            "Invalid statistics object."
        )

    if not isinstance(
        self._metadata,
        dict,
    ):

        raise ProcessorValidationError(
            "Metadata must be a dictionary."
        )

    if not isinstance(
        self._context,
        dict,
    ):

        raise ProcessorValidationError(
            "Context must be a dictionary."
        )

    return True
# ==============================================================================
# Part 8. Events & Hooks
# ==============================================================================

def before_process(
    self,
    record: ProcessingRecord,
) -> ProcessingRecord:
    """
    Hook executed before processing a record.

    Parameters
    ----------
    record
        Processing record.

    Returns
    -------
    ProcessingRecord
        The original processing record.
    """

    self.emit_event(
        "before_process",
        record,
    )

    return record


# ------------------------------------------------------------------------------

def after_process(
    self,
    record: ProcessingRecord,
    result: ProcessingResult,
) -> ProcessingResult:
    """
    Hook executed after processing a record.

    Parameters
    ----------
    record
        Processing record.

    result
        Processing result.

    Returns
    -------
    ProcessingResult
        The processing result.
    """

    self.emit_event(
        "after_process",
        record,
        result,
    )

    return result


# ------------------------------------------------------------------------------

def before_flush(self) -> None:
    """
    Hook executed before flushing the processing queue.
    """

    self.emit_event(
        "before_flush",
    )


# ------------------------------------------------------------------------------

def after_flush(self) -> None:
    """
    Hook executed after flushing the processing queue.
    """

    self.emit_event(
        "after_flush",
    )


# ------------------------------------------------------------------------------

def add_hook(
    self,
    event: str,
    hook: ProcessorHook,
) -> "TraceProcessor":
    """
    Register a hook for an event.

    Parameters
    ----------
    event
        Event name.

    hook
        Hook callable.

    Returns
    -------
    TraceProcessor
    """

    with self._lock:

        self._hooks[event].append(
            hook,
        )

    return self


# ------------------------------------------------------------------------------

def remove_hook(
    self,
    event: str,
    hook: ProcessorHook,
) -> "TraceProcessor":
    """
    Remove a hook from an event.

    Parameters
    ----------
    event
        Event name.

    hook
        Registered hook.

    Returns
    -------
    TraceProcessor
    """

    with self._lock:

        hooks = self._hooks.get(
            event,
        )

        if hooks is None:
            return self

        try:

            hooks.remove(
                hook,
            )

            if not hooks:
                self._hooks.pop(
                    event,
                    None,
                )

        except ValueError:
            pass

    return self


# ------------------------------------------------------------------------------

def clear_hooks(
    self,
    event: Optional[str] = None,
) -> "TraceProcessor":
    """
    Clear registered hooks.

    Parameters
    ----------
    event
        Event name. If None, all hooks are removed.

    Returns
    -------
    TraceProcessor
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
    Emit a processor event.

    All hooks are executed first, followed by subscribed
    callbacks. Exceptions raised by hooks or callbacks
    are intentionally ignored to avoid interrupting the
    processing pipeline.

    Parameters
    ----------
    event
        Event name.
    """

    hooks = list(
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
            # Hooks must never interrupt processing.
            #
            continue

    for callback in list(
        self._callbacks
    ):

        try:

            callback(
                event,
                *args,
                **kwargs,
            )

        except Exception:
            #
            # Callbacks are best-effort only.
            #
            continue
# ==============================================================================
# Part 9. Callbacks
# ==============================================================================

def subscribe(
    self,
    callback: ProcessorCallback,
) -> "TraceProcessor":
    """
    Subscribe to processor events.

    Parameters
    ----------
    callback
        Callback function.

    Returns
    -------
    TraceProcessor
    """

    with self._lock:

        if callback not in self._callbacks:

            self._callbacks.append(
                callback,
            )

    return self


# ------------------------------------------------------------------------------

def unsubscribe(
    self,
    callback: ProcessorCallback,
) -> "TraceProcessor":
    """
    Unsubscribe a callback.

    Parameters
    ----------
    callback
        Registered callback.

    Returns
    -------
    TraceProcessor
    """

    with self._lock:

        try:

            self._callbacks.remove(
                callback,
            )

        except ValueError:
            pass

    return self


# ------------------------------------------------------------------------------

def clear_callbacks(
    self,
) -> "TraceProcessor":
    """
    Remove every subscribed callback.

    Returns
    -------
    TraceProcessor
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
    Notify every subscribed callback.

    Parameters
    ----------
    event
        Event name.

    *args
        Positional event arguments.

    **kwargs
        Keyword event arguments.

    Notes
    -----
    Callback failures are ignored to ensure the processor
    execution pipeline is never interrupted.
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
            #
            # Callbacks are best-effort.
            # They must never interrupt trace processing.
            #
            continue
# ==============================================================================
# Part 10. Serialization Helpers
# ==============================================================================

def to_dict(self) -> Dict[str, Any]:
    """
    Convert the processor to a serializable dictionary.

    Returns
    -------
    Dict[str, Any]
        Serializable processor representation.
    """

    return {

        # ------------------------------------------------------------------
        # Identity
        # ------------------------------------------------------------------

        "id": self._id,

        "uuid": str(self._uuid),

        "name": self._name,

        "description": self._description,

        "version": self._version,

        "processor_type": (
            self._processor_type.value
        ),

        # ------------------------------------------------------------------
        # Configuration
        # ------------------------------------------------------------------

        "mode": self._mode.value,

        "batch_size": self._batch_size,

        "queue_size": self._queue_size,

        "timeout": self._timeout,

        "retry_count": self._retry_count,

        "history_limit": self._history_limit,

        "encoding": self._encoding,

        "options": deepcopy(
            self._options
        ),

        "capabilities": [
            capability.name
            for capability in ProcessorCapability
            if (
                capability
                != ProcessorCapability.NONE
                and capability
                in self._capabilities
            )
        ],

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

        "last_process": self._last_process,

        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------

        "statistics": asdict(
            self._statistics
        ),

        "process_count": self._process_count,

        "success_count": self._success_count,

        "failure_count": self._failure_count,

        "dropped_count": self._dropped_count,

        "queued_count": self._queued_count,

        "last_latency": self._last_latency,

        "minimum_latency": self._minimum_latency,

        "maximum_latency": self._maximum_latency,

        # ------------------------------------------------------------------
        # Metadata
        # ------------------------------------------------------------------

        "metadata": deepcopy(
            self._metadata
        ),

        "context": deepcopy(
            self._context
        ),

        "tags": list(
            self._tags
        ),
    }


# ------------------------------------------------------------------------------

@classmethod
def from_dict(
    cls,
    data: Mapping[str, Any],
) -> "TraceProcessor":
    """
    Create a processor from a dictionary.

    Parameters
    ----------
    data
        Serialized processor dictionary.

    Returns
    -------
    TraceProcessor
    """

    processor = cls(

        name=data.get(
            "name",
            DEFAULT_PROCESSOR_NAME,
        ),

        processor_type=ProcessorType(
            data.get(
                "processor_type",
                ProcessorType.SIMPLE.value,
            )
        ),

        mode=ProcessorMode(
            data.get(
                "mode",
                ProcessorMode.SYNC.value,
            )
        ),

        batch_size=data.get(
            "batch_size",
            DEFAULT_BATCH_SIZE,
        ),

        queue_size=data.get(
            "queue_size",
            DEFAULT_QUEUE_SIZE,
        ),

        timeout=data.get(
            "timeout",
            DEFAULT_TIMEOUT,
        ),

        retry_count=data.get(
            "retry_count",
            DEFAULT_RETRY_COUNT,
        ),

        options=deepcopy(
            data.get(
                "options",
                {},
            )
        ),
    )

    processor.restore(
        data,
    )

    statistics = data.get(
        "statistics",
        {},
    )

    if isinstance(
        statistics,
        Mapping,
    ):

        processor._statistics = (
            ProcessingStatistics(
                **statistics
            )
        )

    return processor


# ------------------------------------------------------------------------------

def to_json(
    self,
    *,
    indent: int = 4,
    ensure_ascii: bool = False,
) -> str:
    """
    Serialize the processor to JSON.

    Parameters
    ----------
    indent
        JSON indentation.

    ensure_ascii
        Preserve Unicode characters.

    Returns
    -------
    str
    """

    return json.dumps(

        self.to_dict(),

        indent=indent,

        ensure_ascii=ensure_ascii,

        sort_keys=True,

        default=str,
    )


# ------------------------------------------------------------------------------

@classmethod
def from_json(
    cls,
    value: Union[
        str,
        bytes,
        bytearray,
    ],
) -> "TraceProcessor":
    """
    Deserialize a processor from JSON.

    Parameters
    ----------
    value
        JSON string.

    Returns
    -------
    TraceProcessor
    """

    if isinstance(
        value,
        (
            bytes,
            bytearray,
        ),
    ):
        value = value.decode(
            DEFAULT_ENCODING,
        )

    data = json.loads(
        value,
    )

    return cls.from_dict(
        data,
    )
# ==============================================================================
# Part 11. Utilities
# ==============================================================================

def supports(
    self,
    capability: ProcessorCapability,
) -> bool:
    """
    Check whether the processor supports a capability.

    Parameters
    ----------
    capability
        Capability to check.

    Returns
    -------
    bool
    """

    return (
        capability
        in self._capabilities
    )


# ------------------------------------------------------------------------------

def enqueue_many(
    self,
    records: Iterable[
        ProcessingRecord,
    ],
) -> "TraceProcessor":
    """
    Enqueue multiple processing records.

    Parameters
    ----------
    records
        Processing records.

    Returns
    -------
    TraceProcessor
    """

    for record in records:
        self.enqueue(
            record,
        )

    return self


# ------------------------------------------------------------------------------

def queue_size(self) -> int:
    """
    Return the current queue size.

    Returns
    -------
    int
    """

    return len(
        self._queue
    )


# ------------------------------------------------------------------------------

def clear_metadata(
    self,
) -> "TraceProcessor":
    """
    Clear processor metadata.

    Returns
    -------
    TraceProcessor
    """

    self._metadata.clear()

    self._updated_at = time.time()

    return self


# ------------------------------------------------------------------------------

def add_tag(
    self,
    tag: str,
) -> "TraceProcessor":
    """
    Add a tag.

    Parameters
    ----------
    tag
        Tag name.

    Returns
    -------
    TraceProcessor
    """

    tag = str(tag).strip()

    if (
        tag
        and tag not in self._tags
    ):
        self._tags.append(
            tag,
        )

        self._updated_at = time.time()

    return self


# ------------------------------------------------------------------------------

def remove_tag(
    self,
    tag: str,
) -> "TraceProcessor":
    """
    Remove a tag.

    Parameters
    ----------
    tag
        Tag name.

    Returns
    -------
    TraceProcessor
    """

    try:

        self._tags.remove(
            tag,
        )

        self._updated_at = time.time()

    except ValueError:
        pass

    return self


# ------------------------------------------------------------------------------

def age(self) -> float:
    """
    Return the processor age in seconds.

    Returns
    -------
    float
    """

    return (
        time.time()
        - self._created_at
    )


# ------------------------------------------------------------------------------

def touch(self) -> "TraceProcessor":
    """
    Update the last modification timestamp.

    Returns
    -------
    TraceProcessor
    """

    self._updated_at = time.time()

    return self


# ------------------------------------------------------------------------------

def timestamp(self) -> float:
    """
    Return the current Unix timestamp.

    Returns
    -------
    float
    """

    return time.time()
# ==============================================================================
# Part 12. Python Protocols
# ==============================================================================

def __repr__(self) -> str:
    """
    Developer-friendly representation.
    """

    return (
        f"{self.__class__.__name__}("
        f"id={self._id!r}, "
        f"name={self._name!r}, "
        f"type={self._processor_type.value!r}, "
        f"state={self._state.value!r})"
    )


# ------------------------------------------------------------------------------

def __str__(self) -> str:
    """
    Human-readable representation.
    """

    return (
        f"{self._name}"
        f" [{self._processor_type.value}]"
        f" ({self._state.value})"
    )


# ------------------------------------------------------------------------------

def __len__(self) -> int:
    """
    Return the number of processed records.
    """

    return self._process_count


# ------------------------------------------------------------------------------

def __iter__(self) -> Iterator[ProcessingResult]:
    """
    Iterate over processing history.
    """

    return iter(self._history)


# ------------------------------------------------------------------------------

def __contains__(
    self,
    item: Any,
) -> bool:
    """
    Membership test against processing history.
    """

    return item in self._history


# ------------------------------------------------------------------------------

def __call__(
    self,
    record: Union[
        ProcessingRecord,
        TraceRecord,
        Mapping[str, Any],
    ],
) -> ProcessingResult:
    """
    Shortcut for process().
    """

    return self.process(
        record,
    )


# ------------------------------------------------------------------------------

def __bool__(self) -> bool:
    """
    Truth value of the processor.

    Returns True only if the processor is available
    for processing.
    """

    return (

        self._enabled

        and self._initialized

        and not self._closed

        and not self._frozen

    )


# ------------------------------------------------------------------------------

def __copy__(self):
    """
    Create a shallow copy.
    """

    return self.copy()


# ------------------------------------------------------------------------------

def __deepcopy__(
    self,
    memo,
):
    """
    Create a deep copy.

    Thread synchronization objects are recreated.
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
                deepcopy(
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
    Equality based on processor id.
    """

    if not isinstance(
        other,
        TraceProcessor,
    ):
        return NotImplemented

    return (
        self._id
        == other._id
    )


# ------------------------------------------------------------------------------

def __hash__(self) -> int:
    """
    Hash based on processor id.
    """

    return hash(
        self._id
    )
# ==============================================================================
# Part 13. Context Manager
# ==============================================================================

def __enter__(self) -> "TraceProcessor":
    """
    Enter the processor runtime context.

    The processor is automatically initialized and started
    if necessary.

    Returns
    -------
    TraceProcessor
        This processor instance.

    Examples
    --------
    >>> with TraceProcessor() as processor:
    ...     processor.process(record)
    """

    if not self._initialized:
        self.initialize()

    if (
        not self._running
        and not self._closed
    ):
        self.start()

    return self


# ------------------------------------------------------------------------------

def __exit__(
    self,
    exc_type,
    exc_value,
    traceback,
) -> bool:
    """
    Exit the processor runtime context.

    Any queued records are flushed before stopping the
    processor. Runtime resources are then cleaned up.

    Parameters
    ----------
    exc_type
        Exception type.

    exc_value
        Exception instance.

    traceback
        Traceback object.

    Returns
    -------
    bool
        Always False so exceptions are propagated.
    """

    try:

        #
        # Process remaining queued records.
        #
        self.flush()

    except Exception:
        #
        # Cleanup should still continue.
        #
        pass

    finally:

        try:

            if self._running:
                self.stop()

        finally:

            self.cleanup()

    #
    # Never suppress exceptions raised inside
    # the with-statement.
    #
    return False
# ==============================================================================
# Compatibility Aliases
# ==============================================================================

Processor = TraceProcessor

ProcessorRecord = ProcessingRecord

ProcessorResult = ProcessingResult

ProcessorStats = ProcessingStatistics

# ==============================================================================
# Part 14. Public API
# ==============================================================================

__all__ = [

    # ------------------------------------------------------------------
    # Constants
    # ------------------------------------------------------------------

    "DEFAULT_PROCESSOR_NAME",

    "DEFAULT_BATCH_SIZE",

    "DEFAULT_QUEUE_SIZE",

    "DEFAULT_TIMEOUT",

    "DEFAULT_RETRY_COUNT",

    "DEFAULT_HISTORY_LIMIT",

    "DEFAULT_ENCODING",

    "PROCESSOR_VERSION",

    # ------------------------------------------------------------------
    # Type Aliases
    # ------------------------------------------------------------------

    "TraceRecord",

    "TracePayload",

    "ProcessorOptions",

    "ProcessorMetadata",

    "ProcessorContext",

    "ProcessorCache",

    "ProcessorHook",

    "ProcessorCallback",

    "ProcessorFilter",

    "ProcessorQueue",

    # ------------------------------------------------------------------
    # Exceptions
    # ------------------------------------------------------------------

    "ProcessorError",

    "ProcessorConfigurationError",

    "ProcessorValidationError",

    "ProcessingError",

    "QueueOverflowError",

    # ------------------------------------------------------------------
    # Enums
    # ------------------------------------------------------------------

    "ProcessorState",

    "ProcessorMode",

    "ProcessorType",

    "ProcessDecision",

    "ProcessorCapability",

    # ------------------------------------------------------------------
    # Dataclasses
    # ------------------------------------------------------------------

    "ProcessingRecord",

    "ProcessingStatistics",

    "ProcessingResult",

    # ------------------------------------------------------------------
    # Main Class
    # ------------------------------------------------------------------

    "TraceProcessor",
 

]                                                            
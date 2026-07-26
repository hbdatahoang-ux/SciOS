"""
SciOS-NG
Runtime Observability - Base Exporter

File:
    scios/runtime/observability/exporters/base.py

Description
-----------
Foundation definitions for all SciOS-NG telemetry exporters.

All concrete exporters inherit from ``BaseExporter``.

Supported exporters
-------------------
- JSON
- Stdout
- Prometheus
- OpenTelemetry
- Jaeger
- Zipkin

Version
-------
0.3.0-alpha
"""

from __future__ import annotations

# ==============================================================================
# Part 1. Foundation
# ==============================================================================

# ==============================================================================
# Imports
# ==============================================================================

from abc import ABC, abstractmethod

import copy
import copy as copy_module
import json
import threading
import time
import uuid

from collections import defaultdict

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

from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    Iterable,
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

EXPORTER_VERSION: str = "0.3.0-alpha"

DEFAULT_EXPORTER_NAME: str = "BaseExporter"

DEFAULT_DESCRIPTION: str = ""

DEFAULT_DESTINATION: str = "stdout"

DEFAULT_BATCH_SIZE: int = 100

DEFAULT_TIMEOUT: float = 30.0

DEFAULT_RETRY_COUNT: int = 3

DEFAULT_HISTORY_SIZE: int = 1024

DEFAULT_ENCODING: str = "utf-8"

DEFAULT_EXPORT_FORMAT: str = "json"

# ==============================================================================
# Type Aliases
# ==============================================================================

ExportPayload: TypeAlias = Any

ExportData: TypeAlias = Dict[str, Any]

ExportOptions: TypeAlias = Dict[str, Any]

ExportMetadata: TypeAlias = Dict[str, Any]

ExportStatisticsMap: TypeAlias = Dict[str, Any]

ExportSnapshot: TypeAlias = Dict[str, Any]

ExportDestination: TypeAlias = Union[str, Path]

ExportHook: TypeAlias = Callable[..., Any]

ExportCallback: TypeAlias = Callable[..., None]

ExportFilter: TypeAlias = Callable[[Any], bool]

ExportSerializer: TypeAlias = Callable[[Any], Any]

ExportDeserializer: TypeAlias = Callable[[Any], Any]

# ==============================================================================
# Exceptions
# ==============================================================================


class ExporterError(Exception):
    """
    Base exporter exception.
    """


class ExportConfigurationError(ExporterError):
    """
    Invalid exporter configuration.
    """


class ExportValidationError(ExporterError):
    """
    Invalid export payload.
    """


class ExportRuntimeError(ExporterError):
    """
    Export runtime failure.
    """


class ExportSerializationError(ExporterError):
    """
    Serialization failure.
    """


class ExportDestinationError(ExporterError):
    """
    Destination unavailable.
    """


class ExportTimeoutError(ExporterError):
    """
    Export timeout.
    """


class ExportClosedError(ExporterError):
    """
    Exporter already closed.
    """


class ExportFrozenError(ExporterError):
    """
    Exporter is frozen.
    """


class ExportDisabledError(ExporterError):
    """
    Exporter is disabled.
    """

# ==============================================================================
# Enums
# ==============================================================================


class ExportFormat(str, Enum):
    """
    Supported exporter formats.
    """

    JSON = "json"

    STDOUT = "stdout"

    PROMETHEUS = "prometheus"

    OPENTELEMETRY = "opentelemetry"

    JAEGER = "jaeger"

    ZIPKIN = "zipkin"

    CUSTOM = "custom"


class ExportStatus(str, Enum):
    """
    Runtime exporter status.
    """

    CREATED = "created"

    READY = "ready"

    RUNNING = "running"

    EXPORTING = "exporting"

    SUCCESS = "success"

    FAILED = "failed"

    STOPPED = "stopped"

    DISABLED = "disabled"

    FROZEN = "frozen"

    CLOSED = "closed"


class ExportMode(str, Enum):
    """
    Export execution mode.
    """

    SYNC = "sync"

    ASYNC = "async"

    STREAM = "stream"

    BATCH = "batch"


class ExportCapability(Flag):
    """
    Exporter capabilities.
    """

    NONE = 0

    SERIALIZE = auto()

    DESERIALIZE = auto()

    STREAM = auto()

    BATCH = auto()

    FILTER = auto()

    COMPRESS = auto()

    ENCRYPT = auto()

    RETRY = auto()

    FLUSH = auto()

    SNAPSHOT = auto()

# ==============================================================================
# Dataclasses
# ==============================================================================


@dataclass(slots=True)
class ExportRecord:
    """
    Generic telemetry record.
    """

    id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    timestamp: float = field(
        default_factory=time.time
    )

    payload: ExportPayload = None

    metadata: ExportMetadata = field(
        default_factory=dict
    )

    tags: List[str] = field(
        default_factory=list
    )

    source: str = ""


@dataclass(slots=True)
class ExportResult:
    """
    Result of one export operation.
    """

    success: bool = False

    status: ExportStatus = ExportStatus.CREATED

    message: str = ""

    exported: int = 0

    duration: float = 0.0

    bytes_sent: int = 0

    metadata: ExportMetadata = field(
        default_factory=dict
    )


@dataclass(slots=True)
class ExportStatistics:
    """
    Runtime statistics.
    """

    exports: int = 0

    successes: int = 0

    failures: int = 0

    bytes_sent: int = 0

    average_latency: float = 0.0

    minimum_latency: float = 0.0

    maximum_latency: float = 0.0

    last_export: Optional[float] = None

    started_at: float = field(
        default_factory=time.time
    )

    uptime: float = 0.0
class BaseExporter(ABC):

    """
    Abstract base class for every SciOS-NG exporter.
    """

    def __init__(
        self,
        *,
        name: str = DEFAULT_EXPORTER_NAME,
        description: str = DEFAULT_DESCRIPTION,
        exporter_format: ExportFormat = ExportFormat.JSON,
        destination: ExportDestination = DEFAULT_DESTINATION,
        mode: ExportMode = ExportMode.SYNC,
        options: Optional[ExportOptions] = None,
    ) -> None:

        # ------------------------------------------------------------------
        # Identity
        # ------------------------------------------------------------------

        self._id: str = str(uuid.uuid4())

        self._uuid: uuid.UUID = uuid.UUID(self._id)

        self._name: str = str(name)

        self._description: str = str(description)

        self._version: str = EXPORTER_VERSION

        self._exporter_type: str = type(self).__name__

        # ------------------------------------------------------------------
        # Configuration
        # ------------------------------------------------------------------

        self._format: ExportFormat = exporter_format

        self._destination: ExportDestination = destination

        self._mode: ExportMode = mode

        self._options: ExportOptions = dict(options or {})

        self._timeout: float = DEFAULT_TIMEOUT

        self._batch_size: int = DEFAULT_BATCH_SIZE

        self._retry_count: int = DEFAULT_RETRY_COUNT

        self._history_limit: int = DEFAULT_HISTORY_SIZE

        self._encoding: str = DEFAULT_ENCODING

        self._capabilities: ExportCapability = (
            ExportCapability.NONE
        )

        # ------------------------------------------------------------------
        # Runtime State
        # ------------------------------------------------------------------

        self._enabled: bool = True

        self._frozen: bool = False

        self._closed: bool = False

        self._running: bool = False

        self._initialized: bool = False

        self._status: ExportStatus = (
            ExportStatus.CREATED
        )

        now = time.time()

        self._created_at: float = now

        self._updated_at: float = now

        self._last_export: Optional[float] = None

        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------

        self._statistics = ExportStatistics()

        self._export_count: int = 0

        self._success_count: int = 0

        self._failure_count: int = 0

        self._bytes_sent: int = 0

        self._last_latency: float = 0.0

        self._minimum_latency: float = 0.0

        self._maximum_latency: float = 0.0

        self._started_at: float = now

        # ------------------------------------------------------------------
        # Runtime Objects
        # ------------------------------------------------------------------

        self._lock = threading.RLock()

        self._hooks: Dict[
            str,
            List[ExportHook],
        ] = defaultdict(list)

        self._callbacks: List[
            ExportCallback
        ] = []

        self._cache: Dict[
            str,
            Any,
        ] = {}

        self._history: List[
            ExportResult
        ] = []

        self._metadata: ExportMetadata = {}

        self._tags: List[str] = []

        self._filters: List[
            ExportFilter
        ] = []

        self._context: Dict[
            str,
            Any,
        ] = {}
# ==============================================================================
# Part 3. Properties
# ==============================================================================

# ==============================================================================
# Identity
# ==============================================================================

@property
def id(self) -> str:
    """Unique exporter identifier."""
    return self._id


@property
def uuid(self) -> uuid.UUID:
    """Exporter UUID."""
    return self._uuid


@property
def name(self) -> str:
    """Exporter name."""
    return self._name


@name.setter
def name(
    self,
    value: str,
) -> None:
    self._name = str(value)
    self._updated_at = time.time()


@property
def description(self) -> str:
    """Exporter description."""
    return self._description


@description.setter
def description(
    self,
    value: str,
) -> None:
    self._description = str(value)
    self._updated_at = time.time()


@property
def version(self) -> str:
    """Exporter version."""
    return self._version


@property
def exporter_type(self) -> str:
    """Concrete exporter type."""
    return self._exporter_type


# ==============================================================================
# Configuration
# ==============================================================================

@property
def format(self) -> ExportFormat:
    """Exporter format."""
    return self._format


@format.setter
def format(
    self,
    value: ExportFormat,
) -> None:
    self._format = ExportFormat(value)
    self._updated_at = time.time()


@property
def destination(self) -> ExportDestination:
    """Export destination."""
    return self._destination


@destination.setter
def destination(
    self,
    value: ExportDestination,
) -> None:
    self._destination = value
    self._updated_at = time.time()


@property
def mode(self) -> ExportMode:
    """Export execution mode."""
    return self._mode


@mode.setter
def mode(
    self,
    value: ExportMode,
) -> None:
    self._mode = ExportMode(value)
    self._updated_at = time.time()


@property
def options(self) -> ExportOptions:
    """Exporter options."""
    return copy.deepcopy(self._options)


@property
def timeout(self) -> float:
    """Export timeout."""
    return self._timeout


@timeout.setter
def timeout(
    self,
    value: float,
) -> None:
    self._timeout = float(value)
    self._updated_at = time.time()


@property
def batch_size(self) -> int:
    """Batch size."""
    return self._batch_size


@batch_size.setter
def batch_size(
    self,
    value: int,
) -> None:
    self._batch_size = int(value)
    self._updated_at = time.time()


@property
def retry_count(self) -> int:
    """Maximum retry count."""
    return self._retry_count


@retry_count.setter
def retry_count(
    self,
    value: int,
) -> None:
    self._retry_count = int(value)
    self._updated_at = time.time()


@property
def history_limit(self) -> int:
    """Maximum history size."""
    return self._history_limit


@history_limit.setter
def history_limit(
    self,
    value: int,
) -> None:
    self._history_limit = max(1, int(value))
    self._updated_at = time.time()


@property
def encoding(self) -> str:
    """Encoding used by exporter."""
    return self._encoding


@encoding.setter
def encoding(
    self,
    value: str,
) -> None:
    self._encoding = str(value)
    self._updated_at = time.time()


@property
def capabilities(self) -> ExportCapability:
    """Exporter capabilities."""
    return self._capabilities


# ==============================================================================
# Runtime
# ==============================================================================

@property
def enabled(self) -> bool:
    """Whether exporter is enabled."""
    return self._enabled


@property
def frozen(self) -> bool:
    """Whether exporter is frozen."""
    return self._frozen


@property
def closed(self) -> bool:
    """Whether exporter is closed."""
    return self._closed


@property
def running(self) -> bool:
    """Whether exporter is running."""
    return self._running


@property
def initialized(self) -> bool:
    """Whether exporter has been initialized."""
    return self._initialized


@property
def active(self) -> bool:
    """
    True when exporter can export records.
    """
    return (
        self._enabled
        and not self._closed
        and not self._frozen
    )


@property
def status(self) -> ExportStatus:
    """Current runtime status."""
    return self._status


@property
def created_at(self) -> float:
    """Creation timestamp."""
    return self._created_at


@property
def updated_at(self) -> float:
    """Last update timestamp."""
    return self._updated_at


@property
def last_export(self) -> Optional[float]:
    """Timestamp of last successful export."""
    return self._last_export


@property
def uptime(self) -> float:
    """Exporter uptime in seconds."""
    return time.time() - self._started_at


# ==============================================================================
# Statistics
# ==============================================================================

@property
def statistics(self) -> ExportStatistics:
    """Runtime statistics."""
    return copy.deepcopy(self._statistics)


@property
def export_count(self) -> int:
    """Total exports."""
    return self._export_count


@property
def success_count(self) -> int:
    """Successful exports."""
    return self._success_count


@property
def failure_count(self) -> int:
    """Failed exports."""
    return self._failure_count


@property
def bytes_sent(self) -> int:
    """Total bytes exported."""
    return self._bytes_sent


@property
def last_latency(self) -> float:
    """Last export latency."""
    return self._last_latency


@property
def minimum_latency(self) -> float:
    """Minimum export latency."""
    return self._minimum_latency


@property
def maximum_latency(self) -> float:
    """Maximum export latency."""
    return self._maximum_latency


@property
def success_rate(self) -> float:
    """
    Success ratio in range [0.0, 1.0].
    """
    total = self._export_count

    if total == 0:
        return 0.0

    return self._success_count / total


@property
def failure_rate(self) -> float:
    """
    Failure ratio in range [0.0, 1.0].
    """
    total = self._export_count

    if total == 0:
        return 0.0

    return self._failure_count / total


# ==============================================================================
# Metadata
# ==============================================================================

@property
def metadata(self) -> ExportMetadata:
    """Exporter metadata."""
    return copy.deepcopy(self._metadata)


@property
def tags(self) -> list[str]:
    """Exporter tags."""
    return list(self._tags)


@property
def history(self) -> list[ExportResult]:
    """Export history."""
    return list(self._history)


@property
def cache(self) -> dict[str, Any]:
    """Runtime cache."""
    return dict(self._cache)


@property
def callbacks(self) -> list[ExportCallback]:
    """Registered callbacks."""
    return list(self._callbacks)


@property
def hooks(self) -> dict[str, list[ExportHook]]:
    """Registered hooks."""
    return {
        event: list(hooks)
        for event, hooks in self._hooks.items()
    }


@property
def filters(self) -> list[ExportFilter]:
    """Registered filters."""
    return list(self._filters)


@property
def context(self) -> dict[str, Any]:
    """Runtime context."""
    return copy.deepcopy(self._context)
# ==============================================================================
# Part 4. Lifecycle
# ==============================================================================

def initialize(self) -> "BaseExporter":
    """
    Initialize exporter runtime.

    This method is safe to call multiple times.
    """

    with self._lock:

        if self._initialized:
            return self

        now = time.time()

        self._initialized = True
        self._running = False
        self._closed = False

        self._status = ExportStatus.READY

        self._created_at = now
        self._updated_at = now
        self._started_at = now

        self.emit_event("initialize")

    return self


# ------------------------------------------------------------------------------

def start(self) -> "BaseExporter":
    """
    Start exporter.
    """

    with self._lock:

        if not self._initialized:
            self.initialize()

        if self._running:
            return self

        if self._closed:
            raise ExportClosedError(
                "Exporter has been closed."
            )

        if not self._enabled:
            raise ExportDisabledError(
                "Exporter is disabled."
            )

        if self._frozen:
            raise ExportFrozenError(
                "Exporter is frozen."
            )

        self._running = True
        self._status = ExportStatus.RUNNING
        self._updated_at = time.time()

        self.emit_event("start")

    return self


# ------------------------------------------------------------------------------

def stop(self) -> "BaseExporter":
    """
    Stop exporter.
    """

    with self._lock:

        if not self._running:
            return self

        self._running = False
        self._status = ExportStatus.STOPPED
        self._updated_at = time.time()

        self.emit_event("stop")

    return self


# ------------------------------------------------------------------------------

def enable(self) -> "BaseExporter":
    """
    Enable exporter.
    """

    with self._lock:

        if self._enabled:
            return self

        self._enabled = True

        if not self._closed:
            self._status = ExportStatus.READY

        self._updated_at = time.time()

        self.emit_event("enable")

    return self


# ------------------------------------------------------------------------------

def disable(self) -> "BaseExporter":
    """
    Disable exporter.
    """

    with self._lock:

        if not self._enabled:
            return self

        self._enabled = False
        self._running = False

        self._status = ExportStatus.DISABLED

        self._updated_at = time.time()

        self.emit_event("disable")

    return self


# ------------------------------------------------------------------------------

def freeze(self) -> "BaseExporter":
    """
    Freeze exporter.

    Export requests should be rejected while frozen.
    """

    with self._lock:

        if self._frozen:
            return self

        self._frozen = True
        self._running = False

        self._status = ExportStatus.FROZEN

        self._updated_at = time.time()

        self.emit_event("freeze")

    return self


# ------------------------------------------------------------------------------

def unfreeze(self) -> "BaseExporter":
    """
    Unfreeze exporter.
    """

    with self._lock:

        if not self._frozen:
            return self

        self._frozen = False

        if self._enabled and not self._closed:
            self._status = ExportStatus.READY

        self._updated_at = time.time()

        self.emit_event("unfreeze")

    return self


# ------------------------------------------------------------------------------

def close(self) -> "BaseExporter":
    """
    Close exporter permanently.

    Runtime resources are released.
    """

    with self._lock:

        if self._closed:
            return self

        self._running = False
        self._closed = True

        self._status = ExportStatus.CLOSED

        self._updated_at = time.time()

        self.emit_event("close")

        #
        # Release transient runtime resources.
        #

        self._cache.clear()

    return self


# ------------------------------------------------------------------------------

def reopen(self) -> "BaseExporter":
    """
    Reopen a previously closed exporter.
    """

    with self._lock:

        if not self._closed:
            return self

        self._closed = False

        if not self._initialized:
            self.initialize()

        if self._enabled:

            if self._frozen:
                self._status = ExportStatus.FROZEN
            else:
                self._status = ExportStatus.READY

        else:
            self._status = ExportStatus.DISABLED

        self._updated_at = time.time()

        self.emit_event("reopen")

    return self
# ==============================================================================
# Part 5. Export API
# ==============================================================================

def export(
    self,
    record: ExportRecord,
) -> ExportResult:
    """
    Export a single record.

    Workflow
    --------
    validate
        ↓
    before_export
        ↓
    serialize
        ↓
    write
        ↓
    statistics
        ↓
    after_export
    """

    start = time.perf_counter()

    self.validate_record(
        record,
        raise_error=True,
    )

    if not self._enabled:
        raise ExportDisabledError(
            "Exporter is disabled."
        )

    if self._closed:
        raise ExportClosedError(
            "Exporter has been closed."
        )

    if self._frozen:
        raise ExportFrozenError(
            "Exporter is frozen."
        )

    self.before_export(record)

    self._status = ExportStatus.EXPORTING

    try:

        prepared = self.prepare(record)

        payload = self.serialize(prepared)

        written = self.write(payload)

        duration = (
            time.perf_counter() - start
        )

        #
        # Runtime state
        #

        self._last_export = time.time()

        self._updated_at = self._last_export

        self._status = ExportStatus.SUCCESS

        #
        # Statistics
        #

        self._export_count += 1

        self._success_count += 1

        self._bytes_sent += written

        self._last_latency = duration

        if (
            self._minimum_latency == 0.0
            or duration < self._minimum_latency
        ):
            self._minimum_latency = duration

        if duration > self._maximum_latency:
            self._maximum_latency = duration

        stats = self._statistics

        stats.exports += 1
        stats.successes += 1
        stats.bytes_sent += written
        stats.last_export = self._last_export

        if stats.average_latency == 0.0:
            stats.average_latency = duration
        else:
            stats.average_latency = (
                (
                    stats.average_latency
                    * (stats.exports - 1)
                )
                + duration
            ) / stats.exports

        result = ExportResult(
            success=True,
            status=ExportStatus.SUCCESS,
            exported=1,
            duration=duration,
            bytes_sent=written,
        )

        self._history.append(result)

        if len(self._history) > self._history_limit:
            self._history.pop(0)

        self.after_export(
            prepared,
            result,
        )

        return self.finalize(result)

    except Exception as exc:

        duration = (
            time.perf_counter() - start
        )

        self._status = ExportStatus.FAILED

        self._updated_at = time.time()

        self._export_count += 1

        self._failure_count += 1

        self._statistics.exports += 1

        self._statistics.failures += 1

        result = ExportResult(
            success=False,
            status=ExportStatus.FAILED,
            message=str(exc),
            exported=0,
            duration=duration,
            bytes_sent=0,
        )

        self._history.append(result)

        self.after_export(
            record,
            result,
        )

        return self.finalize(result)


# ------------------------------------------------------------------------------

def export_batch(
    self,
    records: Iterable[ExportRecord],
) -> list[ExportResult]:
    """
    Export multiple records.
    """

    results: list[ExportResult] = []

    for record in records:

        results.append(
            self.export(record)
        )

    return results


# ------------------------------------------------------------------------------

def export_many(
    self,
    records: Iterable[ExportRecord],
) -> list[ExportResult]:
    """
    Alias of export_batch().
    """

    return self.export_batch(records)


# ------------------------------------------------------------------------------

@abstractmethod
def serialize(
    self,
    record: ExportRecord,
) -> Any:
    """
    Serialize one ExportRecord.

    Returns
    -------
    Backend specific payload.
    """
    raise NotImplementedError


# ------------------------------------------------------------------------------

@abstractmethod
def deserialize(
    self,
    payload: Any,
) -> ExportRecord:
    """
    Deserialize backend payload.
    """
    raise NotImplementedError


# ------------------------------------------------------------------------------

@abstractmethod
def write(
    self,
    payload: Any,
) -> int:
    """
    Write serialized payload.

    Returns
    -------
    int
        Number of bytes written.
    """
    raise NotImplementedError


# ------------------------------------------------------------------------------

def flush(self) -> "BaseExporter":
    """
    Flush pending export buffers.

    Concrete exporters may override this.
    """

    self.emit_event("before_flush")

    self.emit_event("after_flush")

    return self


# ------------------------------------------------------------------------------

def clear(self) -> "BaseExporter":
    """
    Clear runtime buffers.
    """

    with self._lock:

        self._history.clear()

        self._cache.clear()

        self._updated_at = time.time()

    return self
# ==============================================================================
# Part 6. Runtime Operations
# ==============================================================================

def snapshot(self) -> ExportSnapshot:
    """
    Create a snapshot of the exporter runtime state.

    Returns
    -------
    ExportSnapshot
        Serializable exporter state.
    """

    with self._lock:

        return {

            # Identity

            "id": self._id,

            "uuid": str(self._uuid),

            "name": self._name,

            "description": self._description,

            "version": self._version,

            "exporter_type": self._exporter_type,

            # Configuration

            "format": self._format.value,

            "destination": str(self._destination),

            "mode": self._mode.value,

            "options": copy.deepcopy(
                self._options
            ),

            "timeout": self._timeout,

            "batch_size": self._batch_size,

            "retry_count": self._retry_count,

            "history_limit": self._history_limit,

            "encoding": self._encoding,

            # Runtime

            "enabled": self._enabled,

            "frozen": self._frozen,

            "closed": self._closed,

            "running": self._running,

            "initialized": self._initialized,

            "status": self._status.value,

            "created_at": self._created_at,

            "updated_at": self._updated_at,

            "last_export": self._last_export,

            # Statistics

            "statistics": copy.deepcopy(
                self._statistics
            ),

            "export_count": self._export_count,

            "success_count": self._success_count,

            "failure_count": self._failure_count,

            "bytes_sent": self._bytes_sent,

            "last_latency": self._last_latency,

            "minimum_latency": self._minimum_latency,

            "maximum_latency": self._maximum_latency,

            # Metadata

            "metadata": copy.deepcopy(
                self._metadata
            ),

            "tags": list(
                self._tags
            ),

        }


# ------------------------------------------------------------------------------

def restore(
    self,
    snapshot: ExportSnapshot,
) -> "BaseExporter":
    """
    Restore exporter from a snapshot.
    """

    with self._lock:

        self._name = snapshot.get(
            "name",
            self._name,
        )

        self._description = snapshot.get(
            "description",
            self._description,
        )

        self._format = ExportFormat(
            snapshot.get(
                "format",
                self._format.value,
            )
        )

        self._destination = snapshot.get(
            "destination",
            self._destination,
        )

        self._mode = ExportMode(
            snapshot.get(
                "mode",
                self._mode.value,
            )
        )

        self._options = copy.deepcopy(
            snapshot.get(
                "options",
                self._options,
            )
        )

        self._timeout = snapshot.get(
            "timeout",
            self._timeout,
        )

        self._batch_size = snapshot.get(
            "batch_size",
            self._batch_size,
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

        self._enabled = snapshot.get(
            "enabled",
            self._enabled,
        )

        self._frozen = snapshot.get(
            "frozen",
            self._frozen,
        )

        self._closed = snapshot.get(
            "closed",
            self._closed,
        )

        self._running = snapshot.get(
            "running",
            self._running,
        )

        self._initialized = snapshot.get(
            "initialized",
            self._initialized,
        )

        self._status = ExportStatus(
            snapshot.get(
                "status",
                self._status.value,
            )
        )

        self._created_at = snapshot.get(
            "created_at",
            self._created_at,
        )

        self._updated_at = time.time()

        self._last_export = snapshot.get(
            "last_export",
            self._last_export,
        )

        self._statistics = copy.deepcopy(
            snapshot.get(
                "statistics",
                self._statistics,
            )
        )

        self._export_count = snapshot.get(
            "export_count",
            self._export_count,
        )

        self._success_count = snapshot.get(
            "success_count",
            self._success_count,
        )

        self._failure_count = snapshot.get(
            "failure_count",
            self._failure_count,
        )

        self._bytes_sent = snapshot.get(
            "bytes_sent",
            self._bytes_sent,
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

        self._metadata = copy.deepcopy(
            snapshot.get(
                "metadata",
                self._metadata,
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

def clone(self) -> "BaseExporter":
    """
    Deep clone exporter.
    """

    return copy.deepcopy(self)


# ------------------------------------------------------------------------------

def copy(self) -> "BaseExporter":
    """
    Shallow copy exporter.
    """

    return copy.copy(self)


# ------------------------------------------------------------------------------

def optimize(self) -> "BaseExporter":
    """
    Optimize runtime memory.
    """

    with self._lock:

        self._cache.clear()

        if len(self._history) > self._history_limit:
            self._history = self._history[
                -self._history_limit:
            ]

        self._updated_at = time.time()

    return self


# ------------------------------------------------------------------------------

def compact(self) -> "BaseExporter":
    """
    Compact runtime state.
    """

    with self._lock:

        if len(self._history) > 1:

            self._history = [
                self._history[-1]
            ]

        self._cache.clear()

        self._updated_at = time.time()

    return self


# ------------------------------------------------------------------------------

def cleanup(self) -> "BaseExporter":
    """
    Cleanup transient runtime objects.
    """

    with self._lock:

        self._cache.clear()

        self._callbacks.clear()

        self._hooks.clear()

        self._filters.clear()

        self._context.clear()

        self._updated_at = time.time()

    return self


# ------------------------------------------------------------------------------

def reset(self) -> "BaseExporter":
    """
    Reset runtime statistics and temporary state.

    Configuration is preserved.
    """

    with self._lock:

        self._history.clear()

        self._cache.clear()

        self._statistics = ExportStatistics()

        self._export_count = 0

        self._success_count = 0

        self._failure_count = 0

        self._bytes_sent = 0

        self._last_latency = 0.0

        self._minimum_latency = 0.0

        self._maximum_latency = 0.0

        self._last_export = None

        self._status = ExportStatus.READY

        self._updated_at = time.time()

    return self  
# ==============================================================================
# Part 7. Statistics & Diagnostics
# ==============================================================================

def summary(self) -> dict[str, Any]:
    """
    Return a concise exporter summary.
    """

    return {

        "id": self._id,

        "name": self._name,

        "type": self._exporter_type,

        "version": self._version,

        "status": self._status.value,

        "enabled": self._enabled,

        "running": self._running,

        "format": self._format.value,

        "destination": str(self._destination),

        "exports": self._export_count,

        "successes": self._success_count,

        "failures": self._failure_count,

        "success_rate": self.success_rate,

        "uptime": self.uptime,

    }


# ------------------------------------------------------------------------------

def report(self) -> dict[str, Any]:
    """
    Return a complete exporter report.
    """

    return {

        "identity": {

            "id": self._id,

            "uuid": str(self._uuid),

            "name": self._name,

            "description": self._description,

            "type": self._exporter_type,

            "version": self._version,

        },

        "configuration": {

            "format": self._format.value,

            "destination": str(
                self._destination
            ),

            "mode": self._mode.value,

            "timeout": self._timeout,

            "batch_size": self._batch_size,

            "retry_count": self._retry_count,

            "history_limit": self._history_limit,

            "encoding": self._encoding,

        },

        "runtime": {

            "enabled": self._enabled,

            "running": self._running,

            "initialized": self._initialized,

            "frozen": self._frozen,

            "closed": self._closed,

            "status": self._status.value,

            "created_at": self._created_at,

            "updated_at": self._updated_at,

            "last_export": self._last_export,

            "uptime": self.uptime,

        },

        "statistics": self.metrics(),

        "metadata": copy.deepcopy(
            self._metadata
        ),

        "tags": list(self._tags),

    }


# ------------------------------------------------------------------------------

def diagnostics(self) -> dict[str, Any]:
    """
    Return runtime diagnostics.
    """

    return {

        "healthy": (

            self._enabled

            and not self._closed

            and not self._frozen

        ),

        "active": self.active,

        "status": self._status.value,

        "cache_entries": len(
            self._cache
        ),

        "history_size": len(
            self._history
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

        "thread_safe": True,

    }


# ------------------------------------------------------------------------------

def health(self) -> dict[str, Any]:
    """
    Return exporter health information.
    """

    issues: list[str] = []

    if not self._enabled:

        issues.append(
            "exporter_disabled"
        )

    if self._closed:

        issues.append(
            "exporter_closed"
        )

    if self._frozen:

        issues.append(
            "exporter_frozen"
        )

    if self._status == ExportStatus.FAILED:

        issues.append(
            "runtime_failure"
        )

    return {

        "healthy": len(issues) == 0,

        "status": self._status.value,

        "issues": issues,

    }


# ------------------------------------------------------------------------------

def metrics(self) -> dict[str, Any]:
    """
    Return exporter metrics snapshot.
    """

    stats = self._statistics

    return {

        "exports": self._export_count,

        "successes": self._success_count,

        "failures": self._failure_count,

        "bytes_sent": self._bytes_sent,

        "last_latency": self._last_latency,

        "minimum_latency": self._minimum_latency,

        "maximum_latency": self._maximum_latency,

        "average_latency": (
            stats.average_latency
        ),

        "success_rate": self.success_rate,

        "failure_rate": self.failure_rate,

        "last_export": self._last_export,

        "uptime": self.uptime,

    }
# ==============================================================================
# Part 8. Validation
# ==============================================================================

def validate(
    self,
    *,
    raise_error: bool = False,
) -> bool:
    """
    Validate the exporter.

    This method validates:

        • configuration
        • destination
        • runtime integrity
    """

    validators = (

        self.validate_configuration,

        self.validate_destination,

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

def validate_record(
    self,
    record: ExportRecord,
    *,
    raise_error: bool = False,
) -> bool:
    """
    Validate an export record.
    """

    try:

        if not isinstance(
            record,
            ExportRecord,
        ):
            raise TypeError(
                "record must be ExportRecord"
            )

        if record.payload is None:
            raise ValueError(
                "payload cannot be None"
            )

        if not isinstance(
            record.metadata,
            dict,
        ):
            raise TypeError(
                "metadata must be dict"
            )

        if not isinstance(
            record.tags,
            list,
        ):
            raise TypeError(
                "tags must be list"
            )

        return True

    except Exception:

        if raise_error:
            raise

        return False


# ------------------------------------------------------------------------------

def validate_configuration(
    self,
    *,
    raise_error: bool = False,
) -> bool:
    """
    Validate exporter configuration.
    """

    try:

        if not isinstance(
            self._format,
            ExportFormat,
        ):
            raise TypeError(
                "invalid export format"
            )

        if not isinstance(
            self._mode,
            ExportMode,
        ):
            raise TypeError(
                "invalid export mode"
            )

        if self._timeout <= 0:

            raise ValueError(
                "timeout must be positive"
            )

        if self._batch_size <= 0:

            raise ValueError(
                "batch_size must be positive"
            )

        if self._retry_count < 0:

            raise ValueError(
                "retry_count cannot be negative"
            )

        if self._history_limit <= 0:

            raise ValueError(
                "history_limit must be positive"
            )

        if not isinstance(
            self._encoding,
            str,
        ):
            raise TypeError(
                "encoding must be str"
            )

        if not self._encoding:

            raise ValueError(
                "encoding cannot be empty"
            )

        return True

    except Exception:

        if raise_error:
            raise

        return False


# ------------------------------------------------------------------------------

def validate_destination(
    self,
    *,
    raise_error: bool = False,
) -> bool:
    """
    Validate exporter destination.
    """

    try:

        destination = self._destination

        if destination is None:

            raise ValueError(
                "destination is not configured"
            )

        if isinstance(
            destination,
            str,
        ):

            if not destination.strip():

                raise ValueError(
                    "destination cannot be empty"
                )

        elif isinstance(
            destination,
            Path,
        ):

            #
            # Path object is always accepted.
            #

            pass

        else:

            raise TypeError(
                "destination must be str or Path"
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
    Check exporter runtime integrity.
    """

    try:

        required = (

            self._statistics,

            self._cache,

            self._history,

            self._hooks,

            self._callbacks,

            self._filters,

            self._context,

        )

        if any(
            obj is None
            for obj in required
        ):
            raise RuntimeError(
                "runtime object missing"
            )

        if self._success_count > self._export_count:

            raise RuntimeError(
                "success_count exceeds export_count"
            )

        if self._failure_count > self._export_count:

            raise RuntimeError(
                "failure_count exceeds export_count"
            )

        if (
            self._success_count
            + self._failure_count
            > self._export_count
        ):

            raise RuntimeError(
                "statistics are inconsistent"
            )

        if self._bytes_sent < 0:

            raise RuntimeError(
                "bytes_sent cannot be negative"
            )

        return True

    except Exception:

        if raise_error:
            raise

        return False
# ==============================================================================
# Part 9. Events & Hooks
# ==============================================================================

def before_export(
    self,
    record: ExportRecord,
) -> ExportRecord:
    """
    Hook executed before exporting a record.
    """

    self.emit_event(
        "before_export",
        record,
    )

    return record


# ------------------------------------------------------------------------------

def after_export(
    self,
    record: ExportRecord,
    result: ExportResult,
) -> ExportResult:
    """
    Hook executed after exporting a record.
    """

    self.emit_event(
        "after_export",
        record,
        result,
    )

    return result


# ------------------------------------------------------------------------------

def before_flush(self) -> None:
    """
    Hook executed before flush().
    """

    self.emit_event(
        "before_flush",
    )


# ------------------------------------------------------------------------------

def after_flush(self) -> None:
    """
    Hook executed after flush().
    """

    self.emit_event(
        "after_flush",
    )


# ------------------------------------------------------------------------------

def add_hook(
    self,
    event: str,
    hook: ExportHook,
) -> "BaseExporter":
    """
    Register a hook for an event.

    Duplicate hooks are ignored.
    """

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

            hooks.append(hook)

    return self


# ------------------------------------------------------------------------------

def remove_hook(
    self,
    event: str,
    hook: ExportHook,
) -> "BaseExporter":
    """
    Remove a registered hook.
    """

    with self._lock:

        hooks = self._hooks.get(event)

        if not hooks:

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
    event: str | None = None,
) -> "BaseExporter":
    """
    Remove registered hooks.

    Parameters
    ----------
    event
        None -> remove all hooks.
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
    *args: Any,
    **kwargs: Any,
) -> None:
    """
    Emit an exporter event.

    Hook exceptions never interrupt exporter execution.
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
            # Hooks must never stop exporter execution.
            #

            continue

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
            # Global callbacks are also isolated.
            #

            continue
# ==============================================================================
# Part 10. Callbacks
# ==============================================================================

def subscribe(
    self,
    callback: ExportCallback,
) -> "BaseExporter":
    """
    Subscribe a global callback.

    Duplicate callbacks are ignored.

    Parameters
    ----------
    callback
        Callable receiving:

            callback(
                event: str,
                *args,
                **kwargs,
            )
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
    callback: ExportCallback,
) -> "BaseExporter":
    """
    Remove a subscribed callback.

    This method is idempotent.
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
) -> "BaseExporter":
    """
    Remove all subscribed callbacks.
    """

    with self._lock:

        self._callbacks.clear()

    return self


# ------------------------------------------------------------------------------

def notify_callbacks(
    self,
    event: str,
    *args: Any,
    **kwargs: Any,
) -> None:
    """
    Notify all subscribed callbacks.

    Callback exceptions are isolated and never
    interrupt exporter execution.
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
            # Callback failures must never stop
            # exporter execution.
            #

            continue
# ==============================================================================
# Part 11. Serialization Helpers
# ==============================================================================

def to_dict(self) -> dict[str, Any]:
    """
    Serialize exporter into a dictionary.

    Returns
    -------
    dict
        Serializable exporter representation.
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

        "exporter_type": self._exporter_type,

        # ------------------------------------------------------------------
        # Configuration
        # ------------------------------------------------------------------

        "format": self._format.value,

        "destination": str(
            self._destination
        ),

        "mode": self._mode.value,

        "options": copy.deepcopy(
            self._options
        ),

        "timeout": self._timeout,

        "batch_size": self._batch_size,

        "retry_count": self._retry_count,

        "history_limit": self._history_limit,

        "encoding": self._encoding,

        # ------------------------------------------------------------------
        # Runtime
        # ------------------------------------------------------------------

        "enabled": self._enabled,

        "frozen": self._frozen,

        "closed": self._closed,

        "running": self._running,

        "initialized": self._initialized,

        "status": self._status.value,

        "created_at": self._created_at,

        "updated_at": self._updated_at,

        "last_export": self._last_export,

        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------

        "statistics": {

            "exports": self._statistics.exports,

            "successes": self._statistics.successes,

            "failures": self._statistics.failures,

            "bytes_sent": self._statistics.bytes_sent,

            "average_latency": (
                self._statistics.average_latency
            ),

            "last_export": (
                self._statistics.last_export
            ),

            "uptime": self._statistics.uptime,

        },

        "export_count": self._export_count,

        "success_count": self._success_count,

        "failure_count": self._failure_count,

        "bytes_sent": self._bytes_sent,

        "last_latency": self._last_latency,

        "minimum_latency": self._minimum_latency,

        "maximum_latency": self._maximum_latency,

        # ------------------------------------------------------------------
        # Metadata
        # ------------------------------------------------------------------

        "metadata": copy.deepcopy(
            self._metadata
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
) -> "BaseExporter":
    """
    Create an exporter from a dictionary.
    """

    exporter = cls(
        name=data.get(
            "name",
            DEFAULT_EXPORTER_NAME,
        ),
        exporter_format=ExportFormat(
            data.get(
                "format",
                ExportFormat.JSON.value,
            )
        ),
        destination=data.get(
            "destination",
            DEFAULT_DESTINATION,
        ),
        mode=ExportMode(
            data.get(
                "mode",
                ExportMode.SYNC.value,
            )
        ),
        options=copy.deepcopy(
            data.get(
                "options",
                {},
            )
        ),
    )

    exporter.restore(data)

    return exporter


# ------------------------------------------------------------------------------

def to_json(
    self,
    *,
    indent: int = 2,
    ensure_ascii: bool = False,
) -> str:
    """
    Serialize exporter to JSON.
    """

    return json.dumps(

        self.to_dict(),

        indent=indent,

        ensure_ascii=ensure_ascii,

        default=str,

        sort_keys=True,

    )


# ------------------------------------------------------------------------------

@classmethod
def from_json(
    cls,
    text: str,
) -> "BaseExporter":
    """
    Create exporter from JSON.
    """

    data = json.loads(text)

    if not isinstance(data, dict):

        raise TypeError(
            "JSON must contain an object."
        )

    return cls.from_dict(data)
# ==============================================================================
# Part 12. Utilities
# ==============================================================================

def supports(
    self,
    capability: ExportCapability,
) -> bool:
    """
    Check whether this exporter supports a capability.

    Parameters
    ----------
    capability
        Capability flag.

    Returns
    -------
    bool
    """

    return bool(
        self._capabilities & capability
    )


# ------------------------------------------------------------------------------

def set_option(
    self,
    key: str,
    value: Any,
) -> "BaseExporter":
    """
    Set one exporter option.
    """

    if not isinstance(key, str):

        raise TypeError(
            "option key must be str"
        )

    with self._lock:

        self._options[key] = value

        self._updated_at = time.time()

    return self


# ------------------------------------------------------------------------------

def get_option(
    self,
    key: str,
    default: Any = None,
) -> Any:
    """
    Get one exporter option.
    """

    return self._options.get(
        key,
        default,
    )


# ------------------------------------------------------------------------------

def update_options(
    self,
    options: Mapping[str, Any],
    **kwargs: Any,
) -> "BaseExporter":
    """
    Update exporter options.

    Parameters
    ----------
    options
        Mapping of options.

    kwargs
        Additional options.
    """

    if not isinstance(
        options,
        Mapping,
    ):
        raise TypeError(
            "options must be a mapping"
        )

    with self._lock:

        self._options.update(
            dict(options)
        )

        if kwargs:

            self._options.update(
                kwargs
            )

        self._updated_at = time.time()

    return self


# ------------------------------------------------------------------------------

def add_tag(
    self,
    tag: str,
) -> "BaseExporter":
    """
    Add a metadata tag.

    Duplicate tags are ignored.
    """

    if not isinstance(
        tag,
        str,
    ):
        raise TypeError(
            "tag must be str"
        )

    tag = tag.strip()

    if not tag:
        return self

    with self._lock:

        if tag not in self._tags:

            self._tags.append(
                tag
            )

            self._updated_at = time.time()

    return self


# ------------------------------------------------------------------------------

def remove_tag(
    self,
    tag: str,
) -> "BaseExporter":
    """
    Remove a metadata tag.
    """

    with self._lock:

        try:

            self._tags.remove(
                tag
            )

            self._updated_at = time.time()

        except ValueError:

            pass

    return self


# ------------------------------------------------------------------------------

def clear_tags(
    self,
) -> "BaseExporter":
    """
    Remove all metadata tags.
    """

    with self._lock:

        self._tags.clear()

        self._updated_at = time.time()

    return self
# ==============================================================================
# Part 13. Python Protocols
# ==============================================================================

def __repr__(self) -> str:
    """
    Developer-friendly representation.
    """

    return (
        f"{self.__class__.__name__}("
        f"id={self._id!r}, "
        f"name={self._name!r}, "
        f"format={self._format.value!r}, "
        f"status={self._status.value!r})"
    )


# ------------------------------------------------------------------------------

def __str__(self) -> str:
    """
    Human-readable representation.
    """

    return (
        f"{self._name} "
        f"[{self._format.value}] "
        f"({self._status.value})"
    )


# ------------------------------------------------------------------------------

def __len__(self) -> int:
    """
    Number of export operations.
    """

    return self._export_count


# ------------------------------------------------------------------------------

def __iter__(self) -> Iterator[ExportResult]:
    """
    Iterate over export history.
    """

    return iter(self._history)


# ------------------------------------------------------------------------------

def __contains__(
    self,
    item: object,
) -> bool:
    """
    Membership test against export history.
    """

    return item in self._history


# ------------------------------------------------------------------------------

def __getitem__(
    self,
    index: int | slice,
) -> ExportResult | list[ExportResult]:
    """
    Access export history by index or slice.
    """

    return self._history[index]


# ------------------------------------------------------------------------------

def __call__(
    self,
    record: ExportRecord,
) -> ExportResult:
    """
    Shortcut for export().
    """

    return self.export(record)


# ------------------------------------------------------------------------------

def __bool__(self) -> bool:
    """
    True if exporter is available for exporting.
    """

    return (
        self._enabled
        and self._initialized
        and not self._closed
        and not self._frozen
    )


# ------------------------------------------------------------------------------

def __enter__(self) -> "BaseExporter":
    """
    Context manager entry.
    """

    self.initialize()

    self.start()

    return self


# ------------------------------------------------------------------------------

def __exit__(
    self,
    exc_type,
    exc,
    traceback,
) -> bool:
    """
    Context manager exit.
    """

    self.stop()

    self.close()

    #
    # Never suppress exceptions.
    #

    return False


# ------------------------------------------------------------------------------

def __copy__(self) -> "BaseExporter":
    """
    Create a shallow copy.

    Thread locks are recreated.
    """

    cls = self.__class__

    obj = cls.__new__(cls)

    obj.__dict__.update(self.__dict__)

    obj._lock = threading.RLock()

    obj._callbacks = list(self._callbacks)

    obj._history = list(self._history)

    obj._cache = dict(self._cache)

    obj._hooks = {
        k: list(v)
        for k, v in self._hooks.items()
    }

    obj._filters = list(self._filters)

    obj._context = dict(self._context)

    return obj


# ------------------------------------------------------------------------------

def __deepcopy__(
    self,
    memo: dict[int, object],
) -> "BaseExporter":
    """
    Deep copy.

    RLock cannot be deep-copied directly.
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
    Equality based on UUID.
    """

    if not isinstance(
        other,
        BaseExporter,
    ):
        return NotImplemented

    return self._uuid == other._uuid


# ------------------------------------------------------------------------------

def __hash__(self) -> int:
    """
    Hash based on UUID.
    """

    return hash(self._uuid)
# ==============================================================================
# Part 14. Public API
# ==============================================================================

__all__ = [

    # ------------------------------------------------------------------
    # Constants
    # ------------------------------------------------------------------

    "DEFAULT_EXPORTER_NAME",

    "DEFAULT_EXPORT_FORMAT",

    "DEFAULT_DESTINATION",

    "DEFAULT_BATCH_SIZE",

    "DEFAULT_TIMEOUT",

    "DEFAULT_RETRY_COUNT",

    "EXPORTER_VERSION",

    # ------------------------------------------------------------------
    # Enums
    # ------------------------------------------------------------------

    "ExportFormat",

    "ExportStatus",

    "ExportMode",

    "ExportCapability",

    # ------------------------------------------------------------------
    # Dataclasses
    # ------------------------------------------------------------------

    "ExportRecord",

    "ExportResult",

    "ExportStatistics",

    # ------------------------------------------------------------------
    # Exceptions
    # ------------------------------------------------------------------

    "ExporterError",

    "ExportError",

    "ExportConfigurationError",

    "ExportValidationError",

    "ExportRuntimeError",

    "ExportTimeoutError",

    "ExportDisabledError",

    "ExportFrozenError",

    "ExportClosedError",

    # ------------------------------------------------------------------
    # Base Class
    # ------------------------------------------------------------------

    "BaseExporter",

]                                                                  
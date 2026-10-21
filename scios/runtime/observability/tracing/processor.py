# ==============================================================================
# SciOS Runtime Observability
# Trace Processor
# ==============================================================================
#
# File:
# scios/runtime/observability/tracing/processor.py
#
# Part 1. Module Header
#
# Python 3.11+
# ==============================================================================

"""
SciOS Runtime Observability Trace Processor.

Provides the foundational processor layer for processing Trace and Span
entities within the SciOS tracing subsystem.

Python 3.11+
"""

from __future__ import annotations


# ==============================================================================
# Part 2. Imports
# ==============================================================================

# ------------------------------------------------------------------------------
# Standard library
# ------------------------------------------------------------------------------

from abc import ABC
import copy
from datetime import datetime
from enum import Enum
import json
import threading

from typing import (
    Any,
    Mapping,
    TypeAlias,
)


# ------------------------------------------------------------------------------
# SciOS tracing
# ------------------------------------------------------------------------------

from .span import (
    Span,
)

from .trace import (
    Trace,
)


# ==============================================================================
# Part 3. Constants
# ==============================================================================

DEFAULT_PROCESSOR_NAME = "TraceProcessor"

DEFAULT_PROCESSOR_VERSION = "1.0.0"

DEFAULT_PROCESSOR_ENABLED = True

DEFAULT_PROCESSOR_AUTO_START = False

PROCESSOR_VERSION = DEFAULT_PROCESSOR_VERSION


# ==============================================================================
# Part 4. Type Aliases
# ==============================================================================

TraceData: TypeAlias = Mapping[str, Any]

SpanData: TypeAlias = Mapping[str, Any]

TraceInput: TypeAlias = Trace | TraceData

SpanInput: TypeAlias = Span | SpanData

ProcessResult: TypeAlias = (
    Trace
    | Span
    | dict[str, Any]
    | bool
    | None
)


# ==============================================================================
# Part 5. Exceptions
# ==============================================================================


class ProcessorError(
    Exception,
):
    """
    Base exception for Trace Processor errors.
    """

    pass


class ProcessorValidationError(
    ProcessorError,
):
    """
    Raised when processor input or configuration is invalid.
    """

    pass


class ProcessorStateError(
    ProcessorError,
):
    """
    Raised when a processor operation is invalid for its current state.
    """

    pass

# ==============================================================================
# Part 6. Enums
# ==============================================================================


class ProcessorType(
    Enum,
):
    """
    Processor type.
    """

    TRACE = "trace"
    SPAN = "span"
    GENERIC = "generic"


class ProcessorState(
    Enum,
):
    """
    Processor lifecycle state.
    """

    CREATED = "created"
    RUNNING = "running"
    STOPPED = "stopped"
    FROZEN = "frozen"
    CLOSED = "closed"


class ProcessorMode(
    Enum,
):
    """
    Processor execution mode.
    """

    SYNC = "sync"
    ASYNC = "async"
    BATCH = "batch"

# ==============================================================================
# Part 7. Dataclasses
# ==============================================================================

from dataclasses import dataclass


@dataclass
class ProcessorConfig:
    """
    Processor configuration.
    """

    name: str = DEFAULT_PROCESSOR_NAME
    version: str = DEFAULT_PROCESSOR_VERSION
    enabled: bool = DEFAULT_PROCESSOR_ENABLED
    auto_start: bool = DEFAULT_PROCESSOR_AUTO_START
    mode: ProcessorMode = ProcessorMode.SYNC


@dataclass(frozen=True)
class ProcessorCapability:
    """
    Processor capability declaration.
    """

    process_trace: bool = True
    process_span: bool = True
    batch: bool = True
    flush: bool = True


@dataclass
class ProcessingStatistics:
    """
    Runtime processor statistics.
    """

    processed: int = 0
    dropped: int = 0
    errors: int = 0
    last_process_time: datetime | None = None

# ==============================================================================
# Part 8. Processor
# ==============================================================================


class Processor(
    ABC,
):
    """
    SciOS Runtime Trace Processor.
    """

    # --------------------------------------------------------------------------
    # Constructor
    # --------------------------------------------------------------------------

    def __init__(
        self,
        name: str = DEFAULT_PROCESSOR_NAME,
        version: str = DEFAULT_PROCESSOR_VERSION,
        enabled: bool = DEFAULT_PROCESSOR_ENABLED,
        auto_start: bool = DEFAULT_PROCESSOR_AUTO_START,
    ) -> None:

        self._id = (
            f"processor-"
            f"{id(self):x}"
        )

        self._config = ProcessorConfig(
            name=name,
            version=version,
            enabled=enabled,
            auto_start=auto_start,
        )

        self._state = ProcessorState.CREATED

        self._traces: list[Trace] = []

        self._spans: list[Span] = []

        self._pending: list[Any] = []

        self._statistics = ProcessingStatistics()

        self._lock = threading.RLock()

        if auto_start:
            self.start()

    # --------------------------------------------------------------------------
    # Identity
    # --------------------------------------------------------------------------

    @property
    def id(
        self,
    ) -> str:
        return self._id

    @property
    def name(
        self,
    ) -> str:
        return self._config.name

    @property
    def version(
        self,
    ) -> str:
        return self._config.version

    # --------------------------------------------------------------------------
    # State
    # --------------------------------------------------------------------------

    @property
    def state(
        self,
    ) -> ProcessorState:
        return self._state

    @property
    def enabled(
        self,
    ) -> bool:
        return self._config.enabled

    @property
    def active(
        self,
    ) -> bool:
        return (
            self.enabled
            and self._state
            is ProcessorState.RUNNING
        )

    @property
    def started(
        self,
    ) -> bool:
        return self._state in {
            ProcessorState.RUNNING,
            ProcessorState.FROZEN,
            ProcessorState.STOPPED,
        }

    @property
    def stopped(
        self,
    ) -> bool:
        return self._state is ProcessorState.STOPPED

    @property
    def frozen(
        self,
    ) -> bool:
        return self._state is ProcessorState.FROZEN

    @property
    def closed(
        self,
    ) -> bool:
        return self._state is ProcessorState.CLOSED

    # --------------------------------------------------------------------------
    # Lifecycle
    # --------------------------------------------------------------------------

    def start(
        self,
    ) -> "Processor":

        with self._lock:

            if self.closed:
                raise ProcessorStateError(
                    "processor is closed"
                )

            self._state = ProcessorState.RUNNING

        return self

    def stop(
        self,
    ) -> "Processor":

        with self._lock:

            if self.closed:
                raise ProcessorStateError(
                    "processor is closed"
                )

            self._state = ProcessorState.STOPPED

        return self

    def reset(
        self,
    ) -> "Processor":

        with self._lock:

            if self.closed:
                raise ProcessorStateError(
                    "processor is closed"
                )

            self._state = ProcessorState.CREATED

            self._traces.clear()

            self._spans.clear()

            self._pending.clear()

            self._statistics = (
                ProcessingStatistics()
            )

        return self

    def restart(
        self,
    ) -> "Processor":

        with self._lock:

            if self.closed:
                raise ProcessorStateError(
                    "processor is closed"
                )

            self._state = ProcessorState.CREATED

            self._traces.clear()

            self._spans.clear()

            self._pending.clear()

            self._statistics = (
                ProcessingStatistics()
            )

            self._state = ProcessorState.RUNNING

        return self

    def freeze(
        self,
    ) -> "Processor":

        with self._lock:

            if self.closed:
                raise ProcessorStateError(
                    "processor is closed"
                )

            self._state = ProcessorState.FROZEN

        return self

    def unfreeze(
        self,
    ) -> "Processor":

        with self._lock:

            if self.closed:
                raise ProcessorStateError(
                    "processor is closed"
                )

            self._state = ProcessorState.RUNNING

        return self

    def close(
        self,
    ) -> "Processor":

        with self._lock:

            self._pending.clear()

            self._state = ProcessorState.CLOSED

        return self

    # --------------------------------------------------------------------------
    # Input Validation
    # --------------------------------------------------------------------------

    def _validate_input(
        self,
        value: Any,
    ) -> bool:

        if value is None:
            return False

        if isinstance(
            value,
            Trace,
        ):
            return True

        if isinstance(
            value,
            Span,
        ):
            return True

        if isinstance(
            value,
            Mapping,
        ):

            value_type = value.get(
                "type",
            )

            if value_type in {
                "trace",
                "span",
            }:
                return True

            return False

        return False

    # --------------------------------------------------------------------------
    # Trace Processing
    # --------------------------------------------------------------------------

    def process_trace(
        self,
        trace: TraceInput,
    ) -> ProcessResult:

        with self._lock:

            if not self._validate_input(
                trace,
            ):
                self._statistics.errors += 1

                return False

            if not self.enabled:
                self._statistics.dropped += 1

                return False

            if self.closed:
                self._statistics.dropped += 1

                return False

            if self.frozen:
                self._statistics.dropped += 1

                return False

            if isinstance(
                trace,
                Trace,
            ):
                value = trace

            else:
                value = Trace.from_dict(
                    dict(trace),
                )

            self._traces.append(
                value,
            )

            self._statistics.processed += 1

            self._statistics.last_process_time = (
                datetime.now()
            )

            return value

    def process_span(
        self,
        span: SpanInput,
    ) -> ProcessResult:

        with self._lock:

            if not self._validate_input(
                span,
            ):
                self._statistics.errors += 1

                return False

            if not self.enabled:
                self._statistics.dropped += 1

                return False

            if self.closed:
                self._statistics.dropped += 1

                return False

            if self.frozen:
                self._statistics.dropped += 1

                return False

            if isinstance(
                span,
                Span,
            ):
                value = span

            else:
                value = Span.from_snapshot(
                    dict(span),
                )

            self._spans.append(
                value,
            )

            self._statistics.processed += 1

            self._statistics.last_process_time = (
                datetime.now()
            )

            return value

    # --------------------------------------------------------------------------
    # Generic Processing
    # --------------------------------------------------------------------------

    def process(
        self,
        value: Any,
    ) -> ProcessResult:

        if isinstance(
            value,
            Trace,
        ):
            return self.process_trace(
                value,
            )

        if isinstance(
            value,
            Span,
        ):
            return self.process_span(
                value,
            )

        if isinstance(
            value,
            Mapping,
        ):

            value_type = value.get(
                "type",
            )

            if value_type == "trace":
                return self.process_trace(
                    value,
                )

            if value_type == "span":
                return self.process_span(
                    value,
                )

            with self._lock:

                self._statistics.dropped += 1

            return False

        with self._lock:

            self._statistics.dropped += 1

        return False

    # --------------------------------------------------------------------------
    # Flush
    # --------------------------------------------------------------------------

    def flush(
        self,
    ) -> list[Any]:

        with self._lock:

            result = list(
                self._pending,
            )

            self._pending.clear()

            return result

    # --------------------------------------------------------------------------
    # Collection
    # --------------------------------------------------------------------------

    @property
    def traces(
        self,
    ) -> list[Trace]:

        with self._lock:

            return list(
                self._traces,
            )

    @property
    def spans(
        self,
    ) -> list[Span]:

        with self._lock:

            return list(
                self._spans,
            )

    @property
    def trace_count(
        self,
    ) -> int:

        with self._lock:

            return len(
                self._traces,
            )

    @property
    def span_count(
        self,
    ) -> int:

        with self._lock:

            return len(
                self._spans,
            )

    @property
    def pending_count(
        self,
    ) -> int:

        with self._lock:

            return len(
                self._pending,
            )

    # --------------------------------------------------------------------------
    # Statistics
    # --------------------------------------------------------------------------

    @property
    def statistics(
        self,
    ) -> ProcessingStatistics:

        with self._lock:

            return copy.deepcopy(
                self._statistics,
            )

    @property
    def processed_count(
        self,
    ) -> int:

        with self._lock:

            return self._statistics.processed

    @property
    def dropped_count(
        self,
    ) -> int:

        with self._lock:

            return self._statistics.dropped

    @property
    def error_count(
        self,
    ) -> int:

        with self._lock:

            return self._statistics.errors

    @property
    def last_process_time(
        self,
    ) -> datetime | None:

        with self._lock:

            return (
                self._statistics.last_process_time
            )

    # --------------------------------------------------------------------------
    # Processor Validation
    # --------------------------------------------------------------------------

    def validate(
        self,
    ) -> bool:

        with self._lock:

            if not self.name:
                return False

            if not self.version:
                return False

            if self.closed:
                return False

            return True

    def health(
        self,
    ) -> bool:

        return (
            self.validate()
            and self.enabled
        )

    # --------------------------------------------------------------------------
    # Persistence
    # --------------------------------------------------------------------------

    def to_dict(
        self,
    ) -> dict[str, Any]:

        with self._lock:

            return {
                "id": self.id,
                "name": self.name,
                "version": self.version,
                "enabled": self.enabled,
                "auto_start": self._config.auto_start,
                "mode": self._config.mode.value,
                "state": self.state.value,
                "traces": [
                    (
                        value.to_dict()
                        if hasattr(
                            value,
                            "to_dict",
                        )
                        else copy.deepcopy(
                            value,
                        )
                    )
                    for value in self._traces
                ],
                "spans": [
                    (
                        value.to_dict()
                        if hasattr(
                            value,
                            "to_dict",
                        )
                        else copy.deepcopy(
                            value,
                        )
                    )
                    for value in self._spans
                ],
                "pending": copy.deepcopy(
                    self._pending,
                ),
                "statistics": {
                    "processed": (
                        self._statistics.processed
                    ),
                    "dropped": (
                        self._statistics.dropped
                    ),
                    "errors": (
                        self._statistics.errors
                    ),
                    "last_process_time": (
                        self._statistics.last_process_time.isoformat()
                        if self._statistics.last_process_time
                        is not None
                        else None
                    ),
                },
            }

    def to_json(
        self,
    ) -> str:

        return json.dumps(
            self.to_dict(),
            default=str,
        )

    def snapshot(
        self,
    ) -> dict[str, Any]:

        return copy.deepcopy(
            self.to_dict(),
        )

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "Processor":

        if not isinstance(
            data,
            Mapping,
        ):
            raise ProcessorValidationError(
                "data must be a mapping"
            )

        value = cls(
            name=data.get(
                "name",
                DEFAULT_PROCESSOR_NAME,
            ),
            version=data.get(
                "version",
                DEFAULT_PROCESSOR_VERSION,
            ),
            enabled=data.get(
                "enabled",
                DEFAULT_PROCESSOR_ENABLED,
            ),
            auto_start=False,
        )

        value.restore(
            data,
        )

        return value

    @classmethod
    def from_json(
        cls,
        data: str,
    ) -> "Processor":

        if not isinstance(
            data,
            str,
        ):
            raise ProcessorValidationError(
                "data must be a string"
            )

        try:
            payload = json.loads(
                data,
            )
        except json.JSONDecodeError as exc:
            raise ProcessorValidationError(
                "invalid JSON"
            ) from exc

        return cls.from_dict(
            payload,
        )

    def restore(
        self,
        snapshot: Mapping[str, Any],
    ) -> "Processor":

        if not isinstance(
            snapshot,
            Mapping,
        ):
            raise ProcessorValidationError(
                "snapshot must be a mapping"
            )

        with self._lock:

            self._id = snapshot.get(
                "id",
                self._id,
            )

            self._config.name = snapshot.get(
                "name",
                self._config.name,
            )

            self._config.version = snapshot.get(
                "version",
                self._config.version,
            )

            self._config.enabled = bool(
                snapshot.get(
                    "enabled",
                    self._config.enabled,
                )
            )

            self._config.auto_start = bool(
                snapshot.get(
                    "auto_start",
                    self._config.auto_start,
                )
            )

            mode = snapshot.get(
                "mode",
                self._config.mode.value,
            )

            try:
                self._config.mode = (
                    ProcessorMode(
                        mode,
                    )
                )
            except (
                ValueError,
                TypeError,
            ) as exc:
                raise ProcessorValidationError(
                    f"invalid processor mode: {mode!r}"
                ) from exc

            state = snapshot.get(
                "state",
                ProcessorState.CREATED.value,
            )

            try:
                self._state = (
                    ProcessorState(
                        state,
                    )
                )
            except (
                ValueError,
                TypeError,
            ) as exc:
                raise ProcessorValidationError(
                    f"invalid processor state: {state!r}"
                ) from exc

            self._pending = copy.deepcopy(
                snapshot.get(
                    "pending",
                    [],
                ),
            )

            self._traces.clear()

            for item in snapshot.get(
                "traces",
                [],
            ):

                if isinstance(
                    item,
                    Trace,
                ):
                    self._traces.append(
                        copy.deepcopy(
                            item,
                        )
                    )
                    continue

                if isinstance(
                    item,
                    Mapping,
                ):

                    try:
                        trace = Trace.from_dict(
                            item,
                        )
                    except (
                        AttributeError,
                        TypeError,
                        ValueError,
                    ):
                        trace = copy.deepcopy(
                            item,
                        )

                    self._traces.append(
                        trace,
                    )

            self._spans.clear()

            for item in snapshot.get(
                "spans",
                [],
            ):

                if isinstance(
                    item,
                    Span,
                ):
                    self._spans.append(
                        copy.deepcopy(
                            item,
                        )
                    )
                    continue

                if isinstance(
                    item,
                    Mapping,
                ):

                    try:
                        span = Span.from_snapshot(
                            item,
                        )
                    except (
                        AttributeError,
                        TypeError,
                        ValueError,
                    ):
                        span = copy.deepcopy(
                            item,
                        )

                    self._spans.append(
                        span,
                    )

            stats = snapshot.get(
                "statistics",
                {},
            )

            if not isinstance(
                stats,
                Mapping,
            ):
                stats = {}

            last_time = stats.get(
                "last_process_time",
            )

            if isinstance(
                last_time,
                str,
            ):

                try:
                    last_time = (
                        datetime.fromisoformat(
                            last_time,
                        )
                    )
                except ValueError as exc:
                    raise ProcessorValidationError(
                        "invalid last_process_time"
                    ) from exc

            self._statistics = (
                ProcessingStatistics(
                    processed=int(
                        stats.get(
                            "processed",
                            0,
                        )
                    ),
                    dropped=int(
                        stats.get(
                            "dropped",
                            0,
                        )
                    ),
                    errors=int(
                        stats.get(
                            "errors",
                            0,
                        )
                    ),
                    last_process_time=last_time,
                )
            )

        return self

    # --------------------------------------------------------------------------
    # Copying
    # --------------------------------------------------------------------------

    def clone(
        self,
    ) -> "Processor":

        return self.from_dict(
            self.snapshot(),
        )

    def copy(
        self,
    ) -> "Processor":

        return self.clone()

    # --------------------------------------------------------------------------
    # Python Protocols
    # --------------------------------------------------------------------------

    def __repr__(
        self,
    ) -> str:

        return (
            f"Processor("
            f"id={self.id!r}, "
            f"name={self.name!r}, "
            f"state={self.state.value!r}"
            f")"
        )

    def __str__(
        self,
    ) -> str:

        return (
            f"Processor("
            f"{self.name}"
            f")"
        )

    def __bool__(
        self,
    ) -> bool:

        return self.health()

    def __eq__(
        self,
        other: Any,
    ) -> bool:

        if self is other:
            return True

        if not isinstance(
            other,
            Processor,
        ):
            return NotImplemented

        return self.id == other.id

    def __hash__(
        self,
    ) -> int:

        return hash(
            self.id,
        )

    def __len__(
        self,
    ) -> int:

        return (
            self.trace_count
            + self.span_count
            + self.pending_count
        )


# ==============================================================================
# Part 9. Public API
# ==============================================================================

TraceProcessor = Processor


__all__ = [
    "Processor",
    "TraceProcessor",
    "ProcessorType",
    "ProcessorState",
    "ProcessorMode",
    "ProcessorCapability",
    "ProcessorConfig",
    "ProcessingStatistics",
]

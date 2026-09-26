"""
SciOS-NG Runtime Observability

Trace Schema

trace_schema.py

Part 1
Foundation

Provides

    • imports
    • constants
    • enums
    • type aliases
    • utilities

This module defines the foundation for the runtime
trace schema used throughout the SciOS observability
stack (Tracing, Dashboard, Exporters, CLI, REST API).
"""

from __future__ import annotations

import json
import time
import uuid

from dataclasses import asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

from typing import (
    Any,
    Callable,
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

# ==========================================================
# Package Metadata
# ==========================================================

__all__ = [

    "TraceStatus",
    "TraceKind",

    "TraceDict",
    "TraceList",
    "TraceTags",
    "TraceAttributes",

    "TRACE_VERSION",

    "generate_trace_id",
    "generate_span_id",
    "utc_now",
    "timestamp",
    "ensure_path",
    "pretty_json",

]

__version__ = "0.1.0"

__author__ = "SciOS-NG"

__description__ = (
    "Runtime Trace Schema"
)

# ==========================================================
# Constants
# ==========================================================

TRACE_VERSION = "1.0"

TRACE_ID_LENGTH = 32

SPAN_ID_LENGTH = 16

DEFAULT_TRACE_NAME = "runtime"

DEFAULT_SERVICE_NAME = "SciOS"

DEFAULT_NAMESPACE = "runtime"

DEFAULT_TRACE_KIND = "internal"

DEFAULT_ENCODING = "utf-8"

DEFAULT_TIMEOUT = 30.0

# ==========================================================
# Enums
# ==========================================================


class TraceStatus(str, Enum):
    """
    Runtime trace status.
    """

    CREATED = "created"

    RUNNING = "running"

    COMPLETED = "completed"

    FAILED = "failed"

    CANCELLED = "cancelled"


class TraceKind(str, Enum):
    """
    Trace classification.
    """

    INTERNAL = "internal"

    SERVER = "server"

    CLIENT = "client"

    PRODUCER = "producer"

    CONSUMER = "consumer"

    SCHEDULED = "scheduled"


# ==========================================================
# Type Aliases
# ==========================================================

TraceDict: TypeAlias = Dict[str, Any]

TraceList: TypeAlias = List[TraceDict]

TraceTags: TypeAlias = Dict[str, str]

TraceAttributes: TypeAlias = Dict[str, Any]

TraceFilter: TypeAlias = Callable[
    [TraceDict],
    bool,
]

TraceID: TypeAlias = str

SpanID: TypeAlias = str

# ==========================================================
# Utilities
# ==========================================================


def generate_trace_id() -> TraceID:
    """
    Generate a 128-bit trace identifier.
    """

    return uuid.uuid4().hex


def generate_span_id() -> SpanID:
    """
    Generate a 64-bit span identifier.
    """

    return uuid.uuid4().hex[:SPAN_ID_LENGTH]


def timestamp() -> float:
    """
    Current UNIX timestamp.
    """

    return time.time()


def utc_now() -> str:
    """
    Current UTC ISO-8601 timestamp.
    """

    return datetime.now(

        timezone.utc

    ).isoformat()


def ensure_path(
    path: str | Path,
) -> Path:
    """
    Normalize filesystem path.
    """

    return Path(

        path

    ).expanduser().resolve()


def pretty_json(
    obj: Any,
) -> str:
    """
    Pretty JSON serialization.
    """

    return json.dumps(

        obj,

        indent=4,

        ensure_ascii=False,

        default=str,

    )


def enum_value(
    value: Any,
) -> Any:
    """
    Convert Enum values into their primitive value.
    """

    if isinstance(value, Enum):

        return value.value

    return value


def dataclass_to_dict(
    obj: Any,
) -> Dict[str, Any]:
    """
    Convert a dataclass into a dictionary.

    Non-dataclass objects are returned unchanged
    when possible.
    """

    try:

        return asdict(obj)

    except Exception:

        if hasattr(obj, "__dict__"):

            return dict(obj.__dict__)

        return {

            "value": obj,

        }


def runtime_info() -> dict:
    """
    Foundation runtime information.
    """

    return {

        "module":

            __name__,

        "version":

            __version__,

        "description":

            __description__,

        "trace_version":

            TRACE_VERSION,

        "default_service":

            DEFAULT_SERVICE_NAME,

        "default_namespace":

            DEFAULT_NAMESPACE,

        "supported_status":

            [

                status.value

                for status

                in TraceStatus

            ],

        "supported_kinds":

            [

                kind.value

                for kind

                in TraceKind

            ],

    }
# ==========================================================
# Part 2
# Dataclasses
#
# Provides
#     • TraceSchema
#     • TraceContext
#     • TraceMetadata
#
# Notes
# -----
# These dataclasses represent the canonical trace model
# used throughout the SciOS observability subsystem.
#
# They intentionally contain data only. Validation and
# behavior are implemented in later parts.
# ==========================================================

from dataclasses import dataclass, field


# ==========================================================
# Part 2.1
# Trace Context
# ==========================================================

@dataclass(slots=True)
class TraceContext:
    """
    Runtime trace context.

    Stores correlation information that allows traces to
    propagate across processes, services and runtime
    components.
    """

    trace_id: TraceID = field(
        default_factory=generate_trace_id
    )

    parent_trace_id: Optional[TraceID] = None

    parent_span_id: Optional[SpanID] = None

    root_span_id: Optional[SpanID] = None

    correlation_id: Optional[str] = None

    request_id: Optional[str] = None

    session_id: Optional[str] = None

    user_id: Optional[str] = None

    tenant_id: Optional[str] = None

    service_name: str = DEFAULT_SERVICE_NAME

    namespace: str = DEFAULT_NAMESPACE

    trace_kind: TraceKind = TraceKind.INTERNAL

    baggage: Dict[str, Any] = field(
        default_factory=dict
    )


# ==========================================================
# Part 2.2
# Trace Metadata
# ==========================================================

@dataclass(slots=True)
class TraceMetadata:
    """
    Runtime metadata describing a trace.
    """

    name: str = DEFAULT_TRACE_NAME

    description: str = ""

    version: str = TRACE_VERSION

    source: str = "runtime"

    environment: str = "production"

    host: Optional[str] = None

    process_id: Optional[int] = None

    thread_id: Optional[int] = None

    runtime: str = "SciOS"

    runtime_version: str = __version__

    language: str = "Python"

    tags: TraceTags = field(
        default_factory=dict
    )

    attributes: TraceAttributes = field(
        default_factory=dict
    )

    labels: Dict[str, str] = field(
        default_factory=dict
    )

    extras: Dict[str, Any] = field(
        default_factory=dict
    )


# ==========================================================
# Part 2.3
# Trace Schema
# ==========================================================

@dataclass(slots=True)
class TraceSchema:
    """
    Canonical runtime trace schema.

    This is the primary trace object shared by

        • Runtime
        • Dashboard
        • CLI
        • Exporters
        • OpenTelemetry
        • Jaeger
        • Zipkin

    Behavioral methods are implemented in later parts.
    """

    # ------------------------------------------------------
    # Identity
    # ------------------------------------------------------

    id: TraceID = field(
        default_factory=generate_trace_id
    )

    name: str = DEFAULT_TRACE_NAME

    kind: TraceKind = TraceKind.INTERNAL

    status: TraceStatus = TraceStatus.CREATED

    # ------------------------------------------------------
    # Core Models
    # ------------------------------------------------------

    context: TraceContext = field(
        default_factory=TraceContext
    )

    metadata: TraceMetadata = field(
        default_factory=TraceMetadata
    )

    # ------------------------------------------------------
    # Runtime Timing
    # ------------------------------------------------------

    started_at: Optional[float] = None

    finished_at: Optional[float] = None

    created_at: float = field(
        default_factory=timestamp
    )

    updated_at: float = field(
        default_factory=timestamp
    )

    # ------------------------------------------------------
    # Runtime Collections
    # ------------------------------------------------------

    spans: List[Any] = field(
        default_factory=list
    )

    events: List[Any] = field(
        default_factory=list
    )

    links: List[Any] = field(
        default_factory=list
    )

    # ------------------------------------------------------
    # Runtime Attributes
    # ------------------------------------------------------

    tags: TraceTags = field(
        default_factory=dict
    )

    attributes: TraceAttributes = field(
        default_factory=dict
    )

    metrics: Dict[str, Any] = field(
        default_factory=dict
    )

    diagnostics: Dict[str, Any] = field(
        default_factory=dict
    )

    # ------------------------------------------------------
    # Runtime Flags
    # ------------------------------------------------------

    sampled: bool = True

    exported: bool = False

    completed: bool = False

    failed: bool = False

    # ------------------------------------------------------
    # User Data
    # ------------------------------------------------------

    payload: Dict[str, Any] = field(
        default_factory=dict
    )

    extras: Dict[str, Any] = field(
        default_factory=dict
    )
# ==========================================================
# Part 3
# Constructor
#
# Provides
#     • __post_init__()
#     • validation
#     • normalization
#
# Notes
# -----
# Constructor logic performs lightweight validation and
# normalization only. Runtime operations (start, finish,
# reset, etc.) are implemented in later parts.
# ==========================================================

    # ------------------------------------------------------
    # Part 3.1
    # Dataclass Constructor
    # ------------------------------------------------------

    def __post_init__(self) -> None:
        """
        Initialize and normalize a TraceSchema instance.
        """

        #
        # Normalize values.
        #

        self._normalize()

        #
        # Validate structure.
        #

        self._validate()

        #
        # Refresh timestamp.
        #

        self.updated_at = timestamp()

    # ------------------------------------------------------
    # Part 3.2
    # Validation
    # ------------------------------------------------------

    def _validate(self) -> None:
        """
        Validate the trace schema.
        """

        #
        # Identifier
        #

        if not self.id:

            raise ValueError(
                "Trace id cannot be empty."
            )

        #
        # Name
        #

        if not self.name:

            raise ValueError(
                "Trace name cannot be empty."
            )

        #
        # Context
        #

        if not isinstance(
            self.context,
            TraceContext,
        ):

            raise TypeError(
                "context must be a TraceContext."
            )

        #
        # Metadata
        #

        if not isinstance(
            self.metadata,
            TraceMetadata,
        ):

            raise TypeError(
                "metadata must be a TraceMetadata."
            )

        #
        # Status
        #

        if not isinstance(
            self.status,
            TraceStatus,
        ):

            try:

                self.status = TraceStatus(
                    self.status
                )

            except Exception as exc:

                raise ValueError(
                    f"Invalid trace status: {self.status}"
                ) from exc

        #
        # Kind
        #

        if not isinstance(
            self.kind,
            TraceKind,
        ):

            try:

                self.kind = TraceKind(
                    self.kind
                )

            except Exception as exc:

                raise ValueError(
                    f"Invalid trace kind: {self.kind}"
                ) from exc

        #
        # Runtime collections
        #

        if self.spans is None:
            self.spans = []

        if self.events is None:
            self.events = []

        if self.links is None:
            self.links = []

        #
        # Runtime mappings
        #

        if self.tags is None:
            self.tags = {}

        if self.attributes is None:
            self.attributes = {}

        if self.metrics is None:
            self.metrics = {}

        if self.diagnostics is None:
            self.diagnostics = {}

        if self.payload is None:
            self.payload = {}

        if self.extras is None:
            self.extras = {}

    # ------------------------------------------------------
    # Part 3.3
    # Normalization
    # ------------------------------------------------------

    def _normalize(self) -> None:
        """
        Normalize runtime values.
        """

        #
        # Normalize identifier.
        #

        self.id = str(self.id)

        #
        # Normalize name.
        #

        self.name = self.name.strip()

        if not self.name:

            self.name = DEFAULT_TRACE_NAME

        #
        # Synchronize metadata.
        #

        if not self.metadata.name:

            self.metadata.name = self.name

        #
        # Synchronize context.
        #

        if not self.context.trace_id:

            self.context.trace_id = self.id

        #
        # Normalize timestamps.
        #

        now = timestamp()

        if self.created_at <= 0:

            self.created_at = now

        if self.updated_at <= 0:

            self.updated_at = now

        #
        # Normalize runtime state.
        #

        if self.completed:

            self.status = TraceStatus.COMPLETED

        elif self.failed:

            self.status = TraceStatus.FAILED

        #
        # Normalize exported flag.
        #

        self.exported = bool(
            self.exported
        )

        self.sampled = bool(
            self.sampled
        )

    # ------------------------------------------------------
    # Part 3.4
    # Public Validation
    # ------------------------------------------------------

    def validate(self) -> bool:
        """
        Validate the trace.

        Returns
        -------
        bool
            True if validation succeeds.
        """

        self._validate()

        return True

    # ------------------------------------------------------
    # Part 3.5
    # Public Normalization
    # ------------------------------------------------------

    def normalize(self) -> "TraceSchema":
        """
        Normalize the trace.

        Returns
        -------
        TraceSchema
            Self.
        """

        self._normalize()

        self.updated_at = timestamp()

        return self
# ==========================================================
# Part 4
# Properties
#
# Provides
#     • duration
#     • running
#     • finished
#     • failed
#     • span_count
#     • event_count
#
# Notes
# -----
# These properties expose the current runtime state of a
# TraceSchema instance. They are computed dynamically and
# are read-only.
# ==========================================================

    # ------------------------------------------------------
    # Part 4.1
    # Duration
    # ------------------------------------------------------

    @property
    def duration(self) -> float:
        """
        Trace duration in seconds.

        Returns
        -------
        float
            Current duration if the trace is still running,
            otherwise the completed duration.
        """

        if self.started_at is None:
            return 0.0

        end_time = (
            self.finished_at
            if self.finished_at is not None
            else timestamp()
        )

        return max(
            0.0,
            end_time - self.started_at,
        )

    # ------------------------------------------------------
    # Part 4.2
    # Running
    # ------------------------------------------------------

    @property
    def running(self) -> bool:
        """
        Whether the trace is currently running.
        """

        return (
            self.status == TraceStatus.RUNNING
        )

    # ------------------------------------------------------
    # Part 4.3
    # Finished
    # ------------------------------------------------------

    @property
    def finished(self) -> bool:
        """
        Whether the trace has completed successfully.
        """

        return (
            self.status == TraceStatus.COMPLETED
        )

    # ------------------------------------------------------
    # Part 4.4
    # Failed
    # ------------------------------------------------------

    @property
    def failed(self) -> bool:
        """
        Whether the trace has failed.
        """

        return (
            self.status == TraceStatus.FAILED
        )

    # ------------------------------------------------------
    # Part 4.5
    # Span Count
    # ------------------------------------------------------

    @property
    def span_count(self) -> int:
        """
        Number of spans in this trace.
        """

        return len(self.spans)

    # ------------------------------------------------------
    # Part 4.6
    # Event Count
    # ------------------------------------------------------

    @property
    def event_count(self) -> int:
        """
        Number of events associated with this trace.
        """

        return len(self.events)
# ==========================================================
# Part 5
# Operations
#
# Provides
#     • start()
#     • finish()
#     • fail()
#     • cancel()
#     • reset()
#
# Notes
# -----
# Runtime lifecycle operations for TraceSchema.
# State transitions are centralized through TraceStatus.
# ==========================================================

    # ------------------------------------------------------
    # Part 5.1
    # Start
    # ------------------------------------------------------

    def start(self) -> "TraceSchema":
        """
        Start the trace.

        Returns
        -------
        TraceSchema
            Self.
        """

        now = timestamp()

        self.status = TraceStatus.RUNNING

        self.started_at = now

        self.finished_at = None

        self.completed = False

        self.exported = False

        self.updated_at = now

        return self

    # ------------------------------------------------------
    # Part 5.2
    # Finish
    # ------------------------------------------------------

    def finish(self) -> "TraceSchema":
        """
        Complete the trace successfully.
        """

        now = timestamp()

        if self.started_at is None:
            self.started_at = now

        self.finished_at = now

        self.status = TraceStatus.COMPLETED

        self.completed = True

        self.updated_at = now

        return self

    # ------------------------------------------------------
    # Part 5.3
    # Fail
    # ------------------------------------------------------

    def fail(
        self,
        reason: str | None = None,
    ) -> "TraceSchema":
        """
        Mark the trace as failed.

        Parameters
        ----------
        reason
            Optional failure reason.
        """

        now = timestamp()

        if self.started_at is None:
            self.started_at = now

        self.finished_at = now

        self.status = TraceStatus.FAILED

        self.completed = False

        self.updated_at = now

        if reason is not None:

            self.diagnostics[
                "failure_reason"
            ] = reason

        return self

    # ------------------------------------------------------
    # Part 5.4
    # Cancel
    # ------------------------------------------------------

    def cancel(
        self,
        reason: str | None = None,
    ) -> "TraceSchema":
        """
        Cancel the trace.
        """

        now = timestamp()

        if self.started_at is None:
            self.started_at = now

        self.finished_at = now

        self.status = (
            TraceStatus.CANCELLED
        )

        self.completed = False

        self.updated_at = now

        if reason is not None:

            self.diagnostics[
                "cancel_reason"
            ] = reason

        return self

    # ------------------------------------------------------
    # Part 5.5
    # Reset
    # ------------------------------------------------------

    def reset(self) -> "TraceSchema":
        """
        Reset the trace to its initial state.

        Runtime collections and diagnostics are cleared,
        while identity, context and metadata are preserved.
        """

        now = timestamp()

        self.status = TraceStatus.CREATED

        self.started_at = None

        self.finished_at = None

        self.completed = False

        self.exported = False

        self.spans.clear()

        self.events.clear()

        self.links.clear()

        self.tags.clear()

        self.attributes.clear()

        self.metrics.clear()

        self.diagnostics.clear()

        self.payload.clear()

        self.extras.clear()

        self.updated_at = now

        return self
# ==========================================================
# Part 6
# Span Management
#
# Provides
#     • add_span()
#     • remove_span()
#     • get_span()
#     • has_span()
#     • clear_spans()
#
# Notes
# -----
# TraceSchema owns the collection of spans that belong to
# the trace. Spans are identified by their "id" (preferred)
# or "span_id" attribute/key.
#
# SpanSchema is intentionally treated generically here to
# avoid circular dependencies with span_schema.py.
# ==========================================================

    # ------------------------------------------------------
    # Part 6.1
    # Internal Helpers
    # ------------------------------------------------------

    @staticmethod
    def _span_identifier(
        span: Any,
    ) -> Optional[str]:
        """
        Return the identifier of a span.

        Supported representations

            • SpanSchema.id
            • SpanSchema.span_id
            • dict["id"]
            • dict["span_id"]
        """

        if span is None:

            return None

        if isinstance(span, Mapping):

            return (

                span.get("id")

                or

                span.get("span_id")

            )

        return (

            getattr(span, "id", None)

            or

            getattr(span, "span_id", None)

        )

    # ------------------------------------------------------
    # Part 6.2
    # Add Span
    # ------------------------------------------------------

    def add_span(
        self,
        span: Any,
    ) -> Any:
        """
        Add a span to the trace.

        Duplicate span identifiers are ignored.

        Returns
        -------
        Added span.
        """

        span_id = self._span_identifier(
            span
        )

        if (

            span_id is not None

            and

            self.has_span(span_id)

        ):

            return span

        self.spans.append(span)

        self.updated_at = timestamp()

        return span

    # ------------------------------------------------------
    # Part 6.3
    # Remove Span
    # ------------------------------------------------------

    def remove_span(
        self,
        span: str | Any,
    ) -> Optional[Any]:
        """
        Remove a span by object or identifier.

        Returns
        -------
        Removed span or None.
        """

        target = (

            span

            if isinstance(span, str)

            else self._span_identifier(span)

        )

        for index, item in enumerate(self.spans):

            if (

                self._span_identifier(item)

                ==

                target

            ):

                removed = self.spans.pop(
                    index
                )

                self.updated_at = timestamp()

                return removed

        return None

    # ------------------------------------------------------
    # Part 6.4
    # Get Span
    # ------------------------------------------------------

    def get_span(
        self,
        span_id: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve a span by identifier.
        """

        for span in self.spans:

            if (

                self._span_identifier(span)

                ==

                span_id

            ):

                return span

        return default

    # ------------------------------------------------------
    # Part 6.5
    # Has Span
    # ------------------------------------------------------

    def has_span(
        self,
        span: str | Any,
    ) -> bool:
        """
        Check whether a span exists.
        """

        target = (

            span

            if isinstance(span, str)

            else self._span_identifier(span)

        )

        return any(

            self._span_identifier(item)

            ==

            target

            for item in self.spans

        )

    # ------------------------------------------------------
    # Part 6.6
    # Clear Spans
    # ------------------------------------------------------

    def clear_spans(
        self,
    ) -> int:
        """
        Remove every span from the trace.

        Returns
        -------
        Number of removed spans.
        """

        count = len(self.spans)

        self.spans.clear()

        self.updated_at = timestamp()

        return count
# ==========================================================
# Part 7
# Event Management
#
# Provides
#     • add_event()
#     • remove_event()
#     • get_event()
#     • clear_events()
#
# Notes
# -----
# TraceSchema owns the collection of runtime events.
# Events are identified by "id" (preferred) or "event_id".
#
# EventSchema is intentionally treated generically to
# avoid circular dependencies with event_schema.py.
# ==========================================================

    # ------------------------------------------------------
    # Part 7.1
    # Internal Helper
    # ------------------------------------------------------

    @staticmethod
    def _event_identifier(
        event: Any,
    ) -> Optional[str]:
        """
        Return the identifier of an event.

        Supported representations

            • EventSchema.id
            • EventSchema.event_id
            • dict["id"]
            • dict["event_id"]
        """

        if event is None:

            return None

        if isinstance(event, Mapping):

            return (

                event.get("id")

                or

                event.get("event_id")

            )

        return (

            getattr(event, "id", None)

            or

            getattr(event, "event_id", None)

        )

    # ------------------------------------------------------
    # Part 7.2
    # Add Event
    # ------------------------------------------------------

    def add_event(
        self,
        event: Any,
    ) -> Any:
        """
        Add an event to the trace.

        Duplicate event identifiers are ignored.

        Returns
        -------
        Added event.
        """

        event_id = self._event_identifier(
            event
        )

        if (

            event_id is not None

            and

            self.get_event(event_id) is not None

        ):

            return event

        self.events.append(event)

        self.updated_at = timestamp()

        return event

    # ------------------------------------------------------
    # Part 7.3
    # Remove Event
    # ------------------------------------------------------

    def remove_event(
        self,
        event: str | Any,
    ) -> Optional[Any]:
        """
        Remove an event by identifier or object.

        Returns
        -------
        Removed event or None.
        """

        target = (

            event

            if isinstance(event, str)

            else self._event_identifier(event)

        )

        for index, item in enumerate(self.events):

            if (

                self._event_identifier(item)

                ==

                target

            ):

                removed = self.events.pop(
                    index
                )

                self.updated_at = timestamp()

                return removed

        return None

    # ------------------------------------------------------
    # Part 7.4
    # Get Event
    # ------------------------------------------------------

    def get_event(
        self,
        event_id: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve an event by identifier.
        """

        for event in self.events:

            if (

                self._event_identifier(event)

                ==

                event_id

            ):

                return event

        return default

    # ------------------------------------------------------
    # Part 7.5
    # Clear Events
    # ------------------------------------------------------

    def clear_events(
        self,
    ) -> int:
        """
        Remove all events from the trace.

        Returns
        -------
        int
            Number of removed events.
        """

        count = len(self.events)

        self.events.clear()

        self.updated_at = timestamp()

        return count
# ==========================================================
# Part 8
# Tag & Metadata
#
# Provides
#     • set_tag()
#     • get_tag()
#     • remove_tag()
#     • update_metadata()
#
# Notes
# -----
# Tags are lightweight key/value annotations attached to
# the trace.
#
# Metadata updates are applied directly to the
# TraceMetadata dataclass while preserving unknown fields.
# ==========================================================

    # ------------------------------------------------------
    # Part 8.1
    # Tag Management
    # ------------------------------------------------------

    def set_tag(
        self,
        key: str,
        value: Any,
    ) -> "TraceSchema":
        """
        Set or update a trace tag.

        Parameters
        ----------
        key
            Tag name.

        value
            Tag value.

        Returns
        -------
        TraceSchema
            Self.
        """

        key = str(key).strip()

        if not key:

            raise ValueError(
                "Tag key cannot be empty."
            )

        self.tags[key] = value

        #
        # Keep metadata tags synchronized.
        #

        self.metadata.tags[key] = value

        self.updated_at = timestamp()

        return self

    # ------------------------------------------------------
    # Part 8.2
    # Get Tag
    # ------------------------------------------------------

    def get_tag(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve a tag value.
        """

        return self.tags.get(
            key,
            default,
        )

    # ------------------------------------------------------
    # Part 8.3
    # Remove Tag
    # ------------------------------------------------------

    def remove_tag(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Remove a tag.

        Returns
        -------
        Removed value or default.
        """

        value = self.tags.pop(
            key,
            default,
        )

        self.metadata.tags.pop(
            key,
            None,
        )

        self.updated_at = timestamp()

        return value

    # ------------------------------------------------------
    # Part 8.4
    # Metadata Update
    # ------------------------------------------------------

    def update_metadata(
        self,
        **metadata: Any,
    ) -> "TraceSchema":
        """
        Update TraceMetadata.

        Existing fields are updated directly.

        Unknown fields are stored inside
        metadata.extras.
        """

        for key, value in metadata.items():

            if hasattr(
                self.metadata,
                key,
            ):

                setattr(

                    self.metadata,

                    key,

                    value,

                )

            else:

                self.metadata.extras[
                    key
                ] = value

        #
        # Keep timestamps synchronized.
        #

        self.updated_at = timestamp()

        return self
# ==========================================================
# Part 9
# Serialization
#
# Provides
#     • to_dict()
#     • to_json()
#     • from_dict()
#     • from_json()
#
# Notes
# -----
# Serialization converts TraceSchema into portable formats.
# Nested dataclasses (TraceContext, TraceMetadata) are
# serialized recursively.
# ==========================================================

    # ------------------------------------------------------
    # Part 9.1
    # Dictionary Serialization
    # ------------------------------------------------------

    def to_dict(
        self,
    ) -> TraceDict:
        """
        Convert the trace into a dictionary.

        Returns
        -------
        TraceDict
        """

        return {

            # Identity

            "id": self.id,

            "name": self.name,

            "kind": self.kind.value,

            "status": self.status.value,

            # Core

            "context":

                dataclass_to_dict(
                    self.context
                ),

            "metadata":

                dataclass_to_dict(
                    self.metadata
                ),

            # Timing

            "started_at":

                self.started_at,

            "finished_at":

                self.finished_at,

            "created_at":

                self.created_at,

            "updated_at":

                self.updated_at,

            # Collections

            "spans":

                list(self.spans),

            "events":

                list(self.events),

            "links":

                list(self.links),

            # Attributes

            "tags":

                dict(self.tags),

            "attributes":

                dict(self.attributes),

            "metrics":

                dict(self.metrics),

            "diagnostics":

                dict(self.diagnostics),

            # Runtime

            "sampled":

                self.sampled,

            "exported":

                self.exported,

            "completed":

                self.completed,

            # Payload

            "payload":

                dict(self.payload),

            "extras":

                dict(self.extras),

        }

    # ------------------------------------------------------
    # Part 9.2
    # JSON Serialization
    # ------------------------------------------------------

    def to_json(
        self,
        *,
        indent: int = 4,
        ensure_ascii: bool = False,
    ) -> str:
        """
        Serialize the trace into JSON.
        """

        return json.dumps(

            self.to_dict(),

            indent=indent,

            ensure_ascii=ensure_ascii,

            default=str,

        )

    # ------------------------------------------------------
    # Part 9.3
    # Dictionary Deserialization
    # ------------------------------------------------------

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "TraceSchema":
        """
        Create TraceSchema from a dictionary.
        """

        data = dict(data)

        #
        # Restore nested dataclasses.
        #

        context = TraceContext(

            **data.pop(
                "context",
                {},
            )

        )

        metadata = TraceMetadata(

            **data.pop(
                "metadata",
                {},
            )

        )

        #
        # Restore enums.
        #

        if "status" in data:

            data["status"] = TraceStatus(
                data["status"]
            )

        if "kind" in data:

            data["kind"] = TraceKind(
                data["kind"]
            )

        return cls(

            context=context,

            metadata=metadata,

            **data,

        )

    # ------------------------------------------------------
    # Part 9.4
    # JSON Deserialization
    # ------------------------------------------------------

    @classmethod
    def from_json(
        cls,
        text: str,
    ) -> "TraceSchema":
        """
        Create TraceSchema from JSON.
        """

        return cls.from_dict(

            json.loads(text)

        )
# ==========================================================
# Part 10
# Snapshot
#
# Provides
#     • snapshot()
#     • restore()
#     • clone()
#     • copy()
#
# Notes
# -----
# Snapshot APIs provide lightweight state persistence for
# TraceSchema. A snapshot is represented as a serializable
# dictionary compatible with to_dict()/from_dict().
# ==========================================================

    # ------------------------------------------------------
    # Part 10.1
    # Snapshot
    # ------------------------------------------------------

    def snapshot(
        self,
    ) -> TraceDict:
        """
        Create a snapshot of the current trace.

        Returns
        -------
        TraceDict
            Serializable snapshot.
        """

        return self.to_dict()

    # ------------------------------------------------------
    # Part 10.2
    # Restore
    # ------------------------------------------------------

    def restore(
        self,
        snapshot: Mapping[str, Any],
    ) -> "TraceSchema":
        """
        Restore the trace from a snapshot.

        Parameters
        ----------
        snapshot
            Snapshot previously produced by snapshot()
            or to_dict().

        Returns
        -------
        TraceSchema
            Self.
        """

        restored = self.__class__.from_dict(snapshot)

        #
        # Replace current state.
        #

        self.__dict__.clear()

        self.__dict__.update(

            restored.__dict__

        )

        self.updated_at = timestamp()

        return self

    # ------------------------------------------------------
    # Part 10.3
    # Clone
    # ------------------------------------------------------

    def clone(
        self,
    ) -> "TraceSchema":
        """
        Create a deep clone of the trace.

        Returns
        -------
        TraceSchema
        """

        return self.__class__.from_dict(

            self.to_dict()

        )

    # ------------------------------------------------------
    # Part 10.4
    # Copy
    # ------------------------------------------------------

    def copy(
        self,
        *,
        deep: bool = True,
    ) -> "TraceSchema":
        """
        Create a copy of the trace.

        Parameters
        ----------
        deep
            If True, returns a deep copy using clone().
            Otherwise returns a shallow copy.

        Returns
        -------
        TraceSchema
        """

        if deep:

            return self.clone()

        import copy as _copy

        return _copy.copy(self)
# ==========================================================
# Part 11
# Validation
#
# Provides
#     • validate()
#     • validate_context()
#     • validate_spans()
#     • validate_events()
#
# Notes
# -----
# Public validation APIs used by Runtime, Dashboard,
# Exporters and CLI.
#
# Validation is intentionally lightweight and raises
# descriptive exceptions when invalid state is detected.
# ==========================================================

    # ------------------------------------------------------
    # Part 11.1
    # Validate Trace
    # ------------------------------------------------------

    def validate(
        self,
    ) -> bool:
        """
        Validate the complete trace.

        Returns
        -------
        bool
            True if the trace is valid.
        """

        self.validate_context()

        self.validate_spans()

        self.validate_events()

        #
        # Basic identity
        #

        if not self.id:

            raise ValueError(
                "Trace id cannot be empty."
            )

        if not self.name:

            raise ValueError(
                "Trace name cannot be empty."
            )

        if not isinstance(
            self.status,
            TraceStatus,
        ):

            raise TypeError(
                "Invalid TraceStatus."
            )

        if not isinstance(
            self.kind,
            TraceKind,
        ):

            raise TypeError(
                "Invalid TraceKind."
            )

        return True

    # ------------------------------------------------------
    # Part 11.2
    # Validate Context
    # ------------------------------------------------------

    def validate_context(
        self,
    ) -> bool:
        """
        Validate TraceContext.
        """

        if not isinstance(
            self.context,
            TraceContext,
        ):

            raise TypeError(
                "context must be TraceContext."
            )

        if not self.context.trace_id:

            raise ValueError(
                "Context trace_id is missing."
            )

        if not self.context.service_name:

            raise ValueError(
                "Service name is required."
            )

        if not isinstance(
            self.context.trace_kind,
            TraceKind,
        ):

            raise TypeError(
                "Invalid TraceKind."
            )

        return True

    # ------------------------------------------------------
    # Part 11.3
    # Validate Spans
    # ------------------------------------------------------

    def validate_spans(
        self,
    ) -> bool:
        """
        Validate span collection.
        """

        if not isinstance(
            self.spans,
            list,
        ):

            raise TypeError(
                "spans must be a list."
            )

        identifiers = set()

        for span in self.spans:

            span_id = self._span_identifier(
                span
            )

            if not span_id:

                raise ValueError(
                    "Span identifier is missing."
                )

            if span_id in identifiers:

                raise ValueError(

                    f"Duplicate span id: {span_id}"

                )

            identifiers.add(
                span_id
            )

        return True

    # ------------------------------------------------------
    # Part 11.4
    # Validate Events
    # ------------------------------------------------------

    def validate_events(
        self,
    ) -> bool:
        """
        Validate event collection.
        """

        if not isinstance(
            self.events,
            list,
        ):

            raise TypeError(
                "events must be a list."
            )

        identifiers = set()

        for event in self.events:

            event_id = self._event_identifier(
                event
            )

            if not event_id:

                raise ValueError(
                    "Event identifier is missing."
                )

            if event_id in identifiers:

                raise ValueError(

                    f"Duplicate event id: {event_id}"

                )

            identifiers.add(
                event_id
            )

        return True
# ==========================================================
# Part 12
# Statistics
#
# Provides
#     • statistics()
#     • diagnostics()
#     • summary()
#
# Notes
# -----
# Statistics APIs provide runtime information for
# monitoring, dashboard visualization, exporters and CLI.
# ==========================================================

    # ------------------------------------------------------
    # Part 12.1
    # Statistics
    # ------------------------------------------------------

    def statistics(
        self,
    ) -> TraceDict:
        """
        Return runtime statistics.

        Returns
        -------
        TraceDict
        """

        return {

            # Identity

            "id":

                self.id,

            "name":

                self.name,

            "status":

                self.status.value,

            "kind":

                self.kind.value,

            # Timing

            "duration":

                self.duration,

            "started_at":

                self.started_at,

            "finished_at":

                self.finished_at,

            # Collections

            "span_count":

                self.span_count,

            "event_count":

                self.event_count,

            "link_count":

                len(self.links),

            # Runtime

            "sampled":

                self.sampled,

            "exported":

                self.exported,

            "running":

                self.running,

            "finished":

                self.finished,

            "failed":

                self.failed,

        }

    # ------------------------------------------------------
    # Part 12.2
    # Diagnostics
    # ------------------------------------------------------

    def diagnostics(
        self,
    ) -> TraceDict:
        """
        Return runtime diagnostics.

        Returns
        -------
        TraceDict
        """

        return {

            "identity": {

                "id":

                    self.id,

                "name":

                    self.name,

            },

            "validation": {

                "valid":

                    self.validate(),

                "context":

                    self.validate_context(),

                "spans":

                    self.validate_spans(),

                "events":

                    self.validate_events(),

            },

            "statistics":

                self.statistics(),

            "context":

                dataclass_to_dict(

                    self.context

                ),

            "metadata":

                dataclass_to_dict(

                    self.metadata

                ),

            "diagnostics":

                dict(self.diagnostics),

        }

    # ------------------------------------------------------
    # Part 12.3
    # Summary
    # ------------------------------------------------------

    def summary(
        self,
    ) -> TraceDict:
        """
        Return a compact trace summary.

        Returns
        -------
        TraceDict
        """

        return {

            "trace_id":

                self.id,

            "name":

                self.name,

            "status":

                self.status.value,

            "duration":

                round(

                    self.duration,

                    6,

                ),

            "spans":

                self.span_count,

            "events":

                self.event_count,

            "sampled":

                self.sampled,

            "exported":

                self.exported,

        }
# ==========================================================
# Part 13
# Python Protocols
#
# Provides
#     • __repr__()
#     • __str__()
#     • __len__()
#     • __iter__()
#     • __contains__()
#     • __getitem__()
#     • __setitem__()
#     • __copy__()
#     • __deepcopy__()
#
# Notes
# -----
# Python protocol implementations for TraceSchema.
# These methods provide an intuitive Pythonic interface
# while remaining compatible with dataclasses(slots=True).
# ==========================================================

    # ------------------------------------------------------
    # Part 13.1
    # Representation
    # ------------------------------------------------------

    def __repr__(self) -> str:
        """
        Developer representation.
        """

        return (

            f"{self.__class__.__name__}("

            f"id={self.id!r}, "

            f"name={self.name!r}, "

            f"status={self.status.value!r}, "

            f"spans={self.span_count}, "

            f"events={self.event_count}"

            f")"

        )

    # ------------------------------------------------------
    # Part 13.2
    # String
    # ------------------------------------------------------

    def __str__(self) -> str:
        """
        Human-readable representation.
        """

        return (

            f"{self.name} "

            f"[{self.status.value}] "

            f"({self.span_count} spans, "

            f"{self.event_count} events)"

        )

    # ------------------------------------------------------
    # Part 13.3
    # Length
    # ------------------------------------------------------

    def __len__(self) -> int:
        """
        Total number of runtime objects.

        Returns
        -------
        int
            span_count + event_count
        """

        return (

            self.span_count

            +

            self.event_count

        )

    # ------------------------------------------------------
    # Part 13.4
    # Iterator
    # ------------------------------------------------------

    def __iter__(
        self,
    ) -> Iterator[Any]:
        """
        Iterate over spans.
        """

        return iter(

            self.spans

        )

    # ------------------------------------------------------
    # Part 13.5
    # Membership
    # ------------------------------------------------------

    def __contains__(
        self,
        item: Any,
    ) -> bool:
        """
        Membership test.

        Supports

            • span object
            • span id
            • event object
            • event id
        """

        if self.has_span(item):

            return True

        if isinstance(item, str):

            return (

                self.get_event(item)

                is not None

            )

        return (

            item

            in

            self.events

        )

    # ------------------------------------------------------
    # Part 13.6
    # Dictionary-style Access
    # ------------------------------------------------------

    def __getitem__(
        self,
        key: str,
    ) -> Any:
        """
        Dictionary-style access.

        Lookup order

            1. attributes
            2. tags
            3. dataclass field
        """

        if key in self.attributes:

            return self.attributes[key]

        if key in self.tags:

            return self.tags[key]

        if hasattr(self, key):

            return getattr(

                self,

                key,

            )

        raise KeyError(key)

    # ------------------------------------------------------
    # Part 13.7
    # Dictionary-style Assignment
    # ------------------------------------------------------

    def __setitem__(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Dictionary-style assignment.

        Existing dataclass fields are updated directly.
        Unknown keys are stored as attributes.
        """

        if hasattr(

            self,

            key,

        ):

            setattr(

                self,

                key,

                value,

            )

        else:

            self.attributes[key] = value

        self.updated_at = timestamp()

    # ------------------------------------------------------
    # Part 13.8
    # Shallow Copy
    # ------------------------------------------------------

    def __copy__(
        self,
    ) -> "TraceSchema":
        """
        Return a shallow copy.
        """

        import copy

        return copy.copy(

            self.clone()

        )

    # ------------------------------------------------------
    # Part 13.9
    # Deep Copy
    # ------------------------------------------------------

    def __deepcopy__(
        self,
        memo: dict,
    ) -> "TraceSchema":
        """
        Return a deep copy.
        """

        import copy

        if id(self) in memo:

            return memo[id(self)]

        cloned = self.clone()

        memo[id(self)] = cloned

        return copy.deepcopy(

            cloned,

            memo,

        )                                                                                        
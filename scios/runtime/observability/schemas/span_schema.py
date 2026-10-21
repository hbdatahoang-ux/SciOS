"""
SciOS-NG Runtime Observability

Span Schema

span_schema.py

Part 1
Foundation

Provides

    • imports
    • constants
    • enums
    • type aliases
    • utilities

This module defines the foundation for the runtime
Span schema used throughout the SciOS observability
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

    "SpanStatus",
    "SpanKind",

    "SpanDict",
    "SpanList",
    "SpanTags",
    "SpanAttributes",

    "SPAN_VERSION",

    "generate_span_id",
    "generate_event_id",

    "utc_now",
    "timestamp",

    "ensure_path",
    "pretty_json",

    "enum_value",
    "dataclass_to_dict",

    "runtime_info",
]

__version__ = "0.1.0"

__author__ = "SciOS-NG"

__description__ = (
    "Runtime Span Schema"
)

# ==========================================================
# Constants
# ==========================================================

SPAN_VERSION = "1.0"

SPAN_ID_LENGTH = 16

TRACE_ID_LENGTH = 32

EVENT_ID_LENGTH = 16

DEFAULT_SPAN_NAME = "span"

DEFAULT_SERVICE_NAME = "SciOS"

DEFAULT_NAMESPACE = "runtime"

DEFAULT_SPAN_KIND = "internal"

DEFAULT_ENCODING = "utf-8"

DEFAULT_TIMEOUT = 30.0

# ==========================================================
# Enums
# ==========================================================


class SpanStatus(str, Enum):
    """
    Runtime span status.
    """

    CREATED = "created"

    RUNNING = "running"

    COMPLETED = "completed"

    FAILED = "failed"

    CANCELLED = "cancelled"


class SpanKind(str, Enum):
    """
    Span classification.
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

SpanID: TypeAlias = str

TraceID: TypeAlias = str

EventID: TypeAlias = str

SpanDict: TypeAlias = Dict[str, Any]

SpanList: TypeAlias = List[SpanDict]

SpanTags: TypeAlias = Dict[str, Any]

SpanAttributes: TypeAlias = Dict[str, Any]

SpanFilter: TypeAlias = Callable[
    [SpanDict],
    bool,
]

# ==========================================================
# Utilities
# ==========================================================


def generate_span_id() -> SpanID:
    """
    Generate a span identifier.
    """

    return uuid.uuid4().hex[:SPAN_ID_LENGTH]


def generate_event_id() -> EventID:
    """
    Generate an event identifier.
    """

    return uuid.uuid4().hex[:EVENT_ID_LENGTH]


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
    Normalize a filesystem path.
    """

    return Path(
        path
    ).expanduser().resolve()


def pretty_json(
    obj: Any,
) -> str:
    """
    Serialize an object into pretty JSON.
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
    Convert an Enum into its primitive value.
    """

    if isinstance(value, Enum):

        return value.value

    return value


def dataclass_to_dict(
    obj: Any,
) -> Dict[str, Any]:
    """
    Convert a dataclass into a dictionary.

    Falls back to __dict__ when appropriate.
    """

    try:

        return asdict(obj)

    except Exception:

        if hasattr(obj, "__dict__"):

            return dict(obj.__dict__)

        return {
            "value": obj,
        }


def runtime_info() -> SpanDict:
    """
    Return runtime information for the
    Span schema module.
    """

    return {

        "module":

            __name__,

        "version":

            __version__,

        "description":

            __description__,

        "span_version":

            SPAN_VERSION,

        "default_service":

            DEFAULT_SERVICE_NAME,

        "default_namespace":

            DEFAULT_NAMESPACE,

        "supported_status":

            [
                status.value
                for status
                in SpanStatus
            ],

        "supported_kinds":

            [
                kind.value
                for kind
                in SpanKind
            ],

    }
# ==========================================================
# Part 2
# Dataclasses
#
# Provides
#     • SpanSchema
#     • SpanContext
#     • SpanMetadata
#
# Notes
# -----
# These dataclasses define the canonical runtime span model
# used throughout the SciOS observability subsystem.
#
# SpanSchema represents one execution unit within a Trace.
# ==========================================================

from dataclasses import dataclass, field


# ==========================================================
# Part 2.1
# Span Context
# ==========================================================

@dataclass(slots=True)
class SpanContext:
    """
    Runtime span context.

    Carries correlation information used to relate this
    span to its trace and parent spans.
    """

    span_id: SpanID = field(
        default_factory=generate_span_id
    )

    trace_id: Optional[TraceID] = None

    parent_span_id: Optional[SpanID] = None

    root_span_id: Optional[SpanID] = None

    service_name: str = DEFAULT_SERVICE_NAME

    namespace: str = DEFAULT_NAMESPACE

    span_kind: SpanKind = SpanKind.INTERNAL

    baggage: Dict[str, Any] = field(
        default_factory=dict
    )


# ==========================================================
# Part 2.2
# Span Metadata
# ==========================================================

@dataclass(slots=True)
class SpanMetadata:
    """
    Runtime metadata describing a span.
    """

    name: str = DEFAULT_SPAN_NAME

    description: str = ""

    version: str = SPAN_VERSION

    source: str = "runtime"

    environment: str = "production"

    host: Optional[str] = None

    process_id: Optional[int] = None

    thread_id: Optional[int] = None

    runtime: str = "SciOS"

    runtime_version: str = __version__

    language: str = "Python"

    tags: SpanTags = field(
        default_factory=dict
    )

    attributes: SpanAttributes = field(
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
# Span Schema
# ==========================================================

@dataclass(slots=True)
class SpanSchema:
    """
    Canonical runtime span schema.

    A Span represents a single unit of execution within
    a Trace.

    Shared by

        • Runtime
        • Dashboard
        • CLI
        • Exporters
        • OpenTelemetry
        • Jaeger
        • Zipkin
    """

    # ------------------------------------------------------
    # Identity
    # ------------------------------------------------------

    id: SpanID = field(
        default_factory=generate_span_id
    )

    name: str = DEFAULT_SPAN_NAME

    kind: SpanKind = SpanKind.INTERNAL

    status: SpanStatus = SpanStatus.CREATED

    # ------------------------------------------------------
    # Core Models
    # ------------------------------------------------------

    context: SpanContext = field(
        default_factory=SpanContext
    )

    metadata: SpanMetadata = field(
        default_factory=SpanMetadata
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

    events: List[Any] = field(
        default_factory=list
    )

    links: List[Any] = field(
        default_factory=list
    )

    # ------------------------------------------------------
    # Runtime Attributes
    # ------------------------------------------------------

    tags: SpanTags = field(
        default_factory=dict
    )

    attributes: SpanAttributes = field(
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
# Responsible for validating and normalizing a SpanSchema
# immediately after construction.
# ==========================================================

    # ------------------------------------------------------
    # Part 3.1
    # Dataclass Initialization
    # ------------------------------------------------------

    def __post_init__(self) -> None:
        """
        Finalize SpanSchema initialization.
        """

        self._normalize()

        self._validate()

        self.updated_at = timestamp()

    # ------------------------------------------------------
    # Part 3.2
    # Validation
    # ------------------------------------------------------

    def _validate(self) -> None:
        """
        Validate the internal state of the span.

        Raises
        ------
        TypeError
            Invalid object type.

        ValueError
            Invalid value.
        """

        #
        # Identity
        #

        if not isinstance(self.id, str):

            raise TypeError(
                "Span id must be a string."
            )

        self.id = self.id.strip()

        if not self.id:

            raise ValueError(
                "Span id cannot be empty."
            )

        if not isinstance(self.name, str):

            raise TypeError(
                "Span name must be a string."
            )

        self.name = self.name.strip()

        if not self.name:

            raise ValueError(
                "Span name cannot be empty."
            )

        #
        # Enums
        #

        if not isinstance(
            self.kind,
            SpanKind,
        ):

            raise TypeError(
                "kind must be SpanKind."
            )

        if not isinstance(
            self.status,
            SpanStatus,
        ):

            raise TypeError(
                "status must be SpanStatus."
            )

        #
        # Context
        #

        if not isinstance(
            self.context,
            SpanContext,
        ):

            raise TypeError(
                "context must be SpanContext."
            )

        #
        # Metadata
        #

        if not isinstance(
            self.metadata,
            SpanMetadata,
        ):

            raise TypeError(
                "metadata must be SpanMetadata."
            )

        #
        # Collections
        #

        for name in (

            "events",
            "links",

        ):

            value = getattr(
                self,
                name,
            )

            if not isinstance(
                value,
                list,
            ):

                raise TypeError(
                    f"{name} must be a list."
                )

        #
        # Dictionaries
        #

        for name in (

            "tags",
            "attributes",
            "metrics",
            "diagnostics",
            "payload",
            "extras",

        ):

            value = getattr(
                self,
                name,
            )

            if not isinstance(
                value,
                dict,
            ):

                raise TypeError(
                    f"{name} must be a dictionary."
                )

        #
        # Timing
        #

        if (

            self.started_at is not None

            and

            self.finished_at is not None

            and

            self.finished_at < self.started_at

        ):

            raise ValueError(
                "finished_at cannot be earlier than started_at."
            )

    # ------------------------------------------------------
    # Part 3.3
    # Normalization
    # ------------------------------------------------------

    def _normalize(self) -> None:
        """
        Normalize runtime values.
        """

        #
        # Identity
        #

        self.id = str(
            self.id
        ).strip()

        self.name = (
            str(self.name).strip()
            or DEFAULT_SPAN_NAME
        )

        #
        # Synchronize Context
        #

        self.context.span_id = self.id

        #
        # Synchronize Metadata
        #

        self.metadata.name = self.name

        #
        # Merge tags/attributes
        #

        if self.metadata.tags:

            self.tags.update(
                self.metadata.tags
            )

        self.metadata.tags = self.tags

        if self.metadata.attributes:

            self.attributes.update(
                self.metadata.attributes
            )

        self.metadata.attributes = (
            self.attributes
        )

        #
        # Runtime timestamps
        #

        if self.created_at <= 0:

            self.created_at = timestamp()

        if self.updated_at <= 0:

            self.updated_at = self.created_at
# ==========================================================
# Part 4
# Properties
#
# Provides
#     • duration
#     • running
#     • finished
#     • failed
#     • event_count
#     • attribute_count
#
# Notes
# -----
# Read-only runtime properties computed dynamically from
# the current state of the SpanSchema.
# ==========================================================

    # ------------------------------------------------------
    # Part 4.1
    # Duration
    # ------------------------------------------------------

    @property
    def duration(self) -> float:
        """
        Span execution duration in seconds.

        Returns
        -------
        float
            Current duration if running, otherwise the
            completed duration.
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
        True if the span is currently running.
        """

        return (

            self.status

            is

            SpanStatus.RUNNING

        )

    # ------------------------------------------------------
    # Part 4.3
    # Finished
    # ------------------------------------------------------

    @property
    def finished(self) -> bool:
        """
        True if the span completed successfully.
        """

        return (

            self.status

            is

            SpanStatus.COMPLETED

        )

    # ------------------------------------------------------
    # Part 4.4
    # Failed
    # ------------------------------------------------------

    @property
    def failed(self) -> bool:
        """
        True if the span failed.
        """

        return (

            self.status

            is

            SpanStatus.FAILED

        )

    # ------------------------------------------------------
    # Part 4.5
    # Event Count
    # ------------------------------------------------------

    @property
    def event_count(self) -> int:
        """
        Number of events attached to this span.
        """

        return len(

            self.events

        )

    # ------------------------------------------------------
    # Part 4.6
    # Attribute Count
    # ------------------------------------------------------

    @property
    def attribute_count(self) -> int:
        """
        Number of span attributes.
        """

        return len(

            self.attributes

        )
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
# Runtime lifecycle operations for SpanSchema.
# The span state is managed exclusively through SpanStatus.
# ==========================================================

    # ------------------------------------------------------
    # Part 5.1
    # Start
    # ------------------------------------------------------

    def start(self) -> "SpanSchema":
        """
        Start the span.

        Returns
        -------
        SpanSchema
            Self.
        """

        now = timestamp()

        self.status = SpanStatus.RUNNING

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

    def finish(self) -> "SpanSchema":
        """
        Finish the span successfully.

        Returns
        -------
        SpanSchema
            Self.
        """

        now = timestamp()

        if self.started_at is None:

            self.started_at = now

        self.finished_at = now

        self.status = SpanStatus.COMPLETED

        self.completed = True

        self.updated_at = now

        return self

    # ------------------------------------------------------
    # Part 5.3
    # Fail
    # ------------------------------------------------------

    def fail(
        self,
        reason: Optional[str] = None,
    ) -> "SpanSchema":
        """
        Mark the span as failed.

        Parameters
        ----------
        reason
            Optional failure reason.

        Returns
        -------
        SpanSchema
            Self.
        """

        now = timestamp()

        if self.started_at is None:

            self.started_at = now

        self.finished_at = now

        self.status = SpanStatus.FAILED

        self.completed = False

        if reason:

            self.diagnostics[
                "failure_reason"
            ] = reason

        self.updated_at = now

        return self

    # ------------------------------------------------------
    # Part 5.4
    # Cancel
    # ------------------------------------------------------

    def cancel(
        self,
        reason: Optional[str] = None,
    ) -> "SpanSchema":
        """
        Cancel the span.

        Parameters
        ----------
        reason
            Optional cancellation reason.

        Returns
        -------
        SpanSchema
            Self.
        """

        now = timestamp()

        if self.started_at is None:

            self.started_at = now

        self.finished_at = now

        self.status = SpanStatus.CANCELLED

        self.completed = False

        if reason:

            self.diagnostics[
                "cancel_reason"
            ] = reason

        self.updated_at = now

        return self

    # ------------------------------------------------------
    # Part 5.5
    # Reset
    # ------------------------------------------------------

    def reset(self) -> "SpanSchema":
        """
        Reset the span to its initial state.

        Runtime collections are cleared while the
        span identity, context and metadata are preserved.

        Returns
        -------
        SpanSchema
            Self.
        """

        now = timestamp()

        self.status = SpanStatus.CREATED

        self.started_at = None

        self.finished_at = None

        self.completed = False

        self.exported = False

        self.events.clear()

        self.links.clear()

        self.tags.clear()

        self.attributes.clear()

        self.metrics.clear()

        self.diagnostics.clear()

        self.payload.clear()

        self.extras.clear()

        #
        # Keep metadata synchronized.
        #

        self.metadata.tags.clear()

        self.metadata.attributes.clear()

        self.metadata.extras.clear()

        self.updated_at = now

        return self
# ==========================================================
# Part 6
# Event Management
#
# Provides
#     • add_event()
#     • remove_event()
#     • get_event()
#     • has_event()
#     • clear_events()
#
# Notes
# -----
# SpanSchema owns the collection of runtime events that
# occur during span execution.
#
# Events may be represented by EventSchema objects or
# dictionaries containing an "id" or "event_id".
# ==========================================================

    # ------------------------------------------------------
    # Part 6.1
    # Internal Helper
    # ------------------------------------------------------

    @staticmethod
    def _event_identifier(
        event: Any,
    ) -> Optional[str]:
        """
        Return the identifier of an event.

        Supported formats

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
    # Part 6.2
    # Add Event
    # ------------------------------------------------------

    def add_event(
        self,
        event: Any,
    ) -> Any:
        """
        Add an event to the span.

        Duplicate event identifiers are ignored.

        Returns
        -------
        Any
            Added event.
        """

        event_id = self._event_identifier(
            event
        )

        if (

            event_id is not None

            and

            self.has_event(event_id)

        ):

            return event

        self.events.append(
            event
        )

        self.updated_at = timestamp()

        return event

    # ------------------------------------------------------
    # Part 6.3
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
        Optional[Any]
            Removed event if found.
        """

        target = (

            event

            if isinstance(event, str)

            else self._event_identifier(
                event
            )

        )

        for index, item in enumerate(
            self.events
        ):

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
    # Part 6.4
    # Get Event
    # ------------------------------------------------------

    def get_event(
        self,
        event_id: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve an event by identifier.

        Returns
        -------
        Any
            Matching event or default.
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
    # Part 6.5
    # Has Event
    # ------------------------------------------------------

    def has_event(
        self,
        event: str | Any,
    ) -> bool:
        """
        Determine whether an event exists.
        """

        target = (

            event

            if isinstance(event, str)

            else self._event_identifier(
                event
            )

        )

        return any(

            self._event_identifier(item)

            ==

            target

            for item in self.events

        )

    # ------------------------------------------------------
    # Part 6.6
    # Clear Events
    # ------------------------------------------------------

    def clear_events(
        self,
    ) -> int:
        """
        Remove every event from the span.

        Returns
        -------
        int
            Number of removed events.
        """

        count = len(
            self.events
        )

        self.events.clear()

        self.updated_at = timestamp()

        return count
# ==========================================================
# Part 7
# Link Management
#
# Provides
#     • add_link()
#     • remove_link()
#     • get_link()
#     • clear_links()
#
# Notes
# -----
# Span links represent relationships between spans.
#
# A link may be:
#
#   • SpanSchema
#   • SpanContext
#   • dict
#
# Every link is identified by one of:
#
#   • id
#   • span_id
# ==========================================================

    # ------------------------------------------------------
    # Part 7.1
    # Internal Helper
    # ------------------------------------------------------

    @staticmethod
    def _link_identifier(
        link: Any,
    ) -> Optional[str]:
        """
        Return the identifier of a span link.
        """

        if link is None:

            return None

        if isinstance(link, Mapping):

            return (

                link.get("id")

                or

                link.get("span_id")

            )

        return (

            getattr(link, "id", None)

            or

            getattr(link, "span_id", None)

        )

    # ------------------------------------------------------
    # Part 7.2
    # Add Link
    # ------------------------------------------------------

    def add_link(
        self,
        link: Any,
    ) -> Any:
        """
        Add a span link.

        Duplicate links are ignored.
        """

        identifier = self._link_identifier(
            link
        )

        if (

            identifier is not None

            and

            self.get_link(identifier)

            is not None

        ):

            return link

        self.links.append(link)

        self.updated_at = timestamp()

        return link

    # ------------------------------------------------------
    # Part 7.3
    # Remove Link
    # ------------------------------------------------------

    def remove_link(
        self,
        link: str | Any,
    ) -> Optional[Any]:
        """
        Remove a link by identifier or object.

        Returns
        -------
        Removed link or None.
        """

        identifier = (

            link

            if isinstance(link, str)

            else self._link_identifier(
                link
            )

        )

        for index, item in enumerate(
            self.links
        ):

            if (

                self._link_identifier(item)

                ==

                identifier

            ):

                removed = self.links.pop(
                    index
                )

                self.updated_at = timestamp()

                return removed

        return None

    # ------------------------------------------------------
    # Part 7.4
    # Get Link
    # ------------------------------------------------------

    def get_link(
        self,
        link_id: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve a link by identifier.
        """

        for link in self.links:

            if (

                self._link_identifier(link)

                ==

                link_id

            ):

                return link

        return default

    # ------------------------------------------------------
    # Part 7.5
    # Clear Links
    # ------------------------------------------------------

    def clear_links(
        self,
    ) -> int:
        """
        Remove all span links.

        Returns
        -------
        int
            Number of removed links.
        """

        count = len(
            self.links
        )

        self.links.clear()

        self.updated_at = timestamp()

        return count
# ==========================================================
# Part 8
# Attributes & Metadata
#
# Provides
#     • set_attribute()
#     • get_attribute()
#     • remove_attribute()
#     • update_metadata()
#
# Notes
# -----
# Span attributes are lightweight key/value pairs describing
# the execution of a span.
#
# Metadata contains descriptive information about the span
# itself (host, runtime, labels, version, etc.).
# ==========================================================

    # ------------------------------------------------------
    # Part 8.1
    # Set Attribute
    # ------------------------------------------------------

    def set_attribute(
        self,
        key: str,
        value: Any,
    ) -> "SpanSchema":
        """
        Set or update a span attribute.

        Parameters
        ----------
        key
            Attribute name.

        value
            Attribute value.

        Returns
        -------
        SpanSchema
            Self.
        """

        key = str(key).strip()

        if not key:

            raise ValueError(
                "Attribute key cannot be empty."
            )

        self.attributes[key] = value

        #
        # Keep metadata synchronized.
        #

        self.metadata.attributes[key] = value

        self.updated_at = timestamp()

        return self

    # ------------------------------------------------------
    # Part 8.2
    # Get Attribute
    # ------------------------------------------------------

    def get_attribute(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve an attribute value.
        """

        return self.attributes.get(
            key,
            default,
        )

    # ------------------------------------------------------
    # Part 8.3
    # Remove Attribute
    # ------------------------------------------------------

    def remove_attribute(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Remove an attribute.

        Returns
        -------
        Removed value or default.
        """

        value = self.attributes.pop(
            key,
            default,
        )

        self.metadata.attributes.pop(
            key,
            None,
        )

        self.updated_at = timestamp()

        return value

    # ------------------------------------------------------
    # Part 8.4
    # Update Metadata
    # ------------------------------------------------------

    def update_metadata(
        self,
        **metadata: Any,
    ) -> "SpanSchema":
        """
        Update SpanMetadata.

        Existing fields are updated directly.
        Unknown fields are stored inside
        metadata.extras.

        Returns
        -------
        SpanSchema
            Self.
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
        # Synchronize commonly-used dictionaries.
        #

        if hasattr(
            self.metadata,
            "attributes",
        ):

            self.attributes.update(
                self.metadata.attributes
            )

        if hasattr(
            self.metadata,
            "tags",
        ):

            self.tags.update(
                self.metadata.tags
            )

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
# Serialization converts SpanSchema into portable formats.
# Nested dataclasses (SpanContext, SpanMetadata) are
# serialized recursively.
#
# This implementation is fully symmetric:
#
#     SpanSchema
#        ↓
#     to_dict()
#        ↓
#     from_dict()
#        ↓
#     SpanSchema
# ==========================================================

    # ------------------------------------------------------
    # Part 9.1
    # Dictionary Serialization
    # ------------------------------------------------------

    def to_dict(self) -> SpanDict:
        """
        Serialize the span into a dictionary.

        Returns
        -------
        SpanDict
        """

        return {

            # --------------------------------------------------
            # Identity
            # --------------------------------------------------

            "id": self.id,

            "name": self.name,

            "kind": self.kind.value,

            "status": self.status.value,

            # --------------------------------------------------
            # Nested Dataclasses
            # --------------------------------------------------

            "context":

                dataclass_to_dict(
                    self.context
                ),

            "metadata":

                dataclass_to_dict(
                    self.metadata
                ),

            # --------------------------------------------------
            # Runtime Timing
            # --------------------------------------------------

            "started_at":

                self.started_at,

            "finished_at":

                self.finished_at,

            "created_at":

                self.created_at,

            "updated_at":

                self.updated_at,

            # --------------------------------------------------
            # Collections
            # --------------------------------------------------

            "events":

                list(self.events),

            "links":

                list(self.links),

            # --------------------------------------------------
            # Dictionaries
            # --------------------------------------------------

            "tags":

                dict(self.tags),

            "attributes":

                dict(self.attributes),

            "metrics":

                dict(self.metrics),

            "diagnostics":

                dict(self.diagnostics),

            # --------------------------------------------------
            # Runtime Flags
            # --------------------------------------------------

            "sampled":

                self.sampled,

            "exported":

                self.exported,

            "completed":

                self.completed,

            # --------------------------------------------------
            # User Data
            # --------------------------------------------------

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
        Serialize the span into JSON.
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
    ) -> "SpanSchema":
        """
        Construct a SpanSchema from a dictionary.
        """

        data = dict(data)

        #
        # Restore nested dataclasses.
        #

        context = SpanContext(

            **data.pop(
                "context",
                {},
            )

        )

        metadata = SpanMetadata(

            **data.pop(
                "metadata",
                {},
            )

        )

        #
        # Restore enums.
        #

        if "kind" in data:

            data["kind"] = SpanKind(
                data["kind"]
            )

        if "status" in data:

            data["status"] = SpanStatus(
                data["status"]
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
    ) -> "SpanSchema":
        """
        Construct a SpanSchema from JSON.
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
# Snapshot APIs provide lightweight persistence for
# SpanSchema. A snapshot is represented as a serializable
# dictionary fully compatible with to_dict()/from_dict().
#
# Designed to work correctly with dataclasses(slots=True).
# ==========================================================

    # ------------------------------------------------------
    # Part 10.1
    # Snapshot
    # ------------------------------------------------------

    def snapshot(
        self,
    ) -> SpanDict:
        """
        Create a serializable snapshot of this span.

        Returns
        -------
        SpanDict
        """

        return self.to_dict()

    # ------------------------------------------------------
    # Part 10.2
    # Restore
    # ------------------------------------------------------

    def restore(
        self,
        snapshot: Mapping[str, Any],
    ) -> "SpanSchema":
        """
        Restore this span from a snapshot.

        Parameters
        ----------
        snapshot
            Snapshot produced by snapshot() or to_dict().

        Returns
        -------
        SpanSchema
            Self.
        """

        restored = self.__class__.from_dict(
            snapshot
        )

        #
        # Compatible with dataclasses(slots=True)
        #

        for field_name in self.__dataclass_fields__:

            setattr(

                self,

                field_name,

                getattr(
                    restored,
                    field_name,
                ),

            )

        self.updated_at = timestamp()

        return self

    # ------------------------------------------------------
    # Part 10.3
    # Clone
    # ------------------------------------------------------

    def clone(
        self,
    ) -> "SpanSchema":
        """
        Create a deep clone of this span.

        Returns
        -------
        SpanSchema
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
    ) -> "SpanSchema":
        """
        Create a copy of this span.

        Parameters
        ----------
        deep
            True  -> deep copy (default)
            False -> shallow copy

        Returns
        -------
        SpanSchema
        """

        import copy as _copy

        if deep:

            return self.clone()

        return _copy.copy(self)
# ==========================================================
# Part 11
# Validation
#
# Provides
#     • validate()
#     • validate_context()
#     • validate_events()
#     • validate_links()
#
# Notes
# -----
# Public validation APIs for SpanSchema.
#
# Validation is intentionally lightweight and raises
# descriptive exceptions whenever invalid state is
# detected.
# ==========================================================

    # ------------------------------------------------------
    # Part 11.1
    # Validate Span
    # ------------------------------------------------------

    def validate(
        self,
    ) -> bool:
        """
        Validate the entire span.

        Returns
        -------
        bool
            True if the span is valid.
        """

        self.validate_context()

        self.validate_events()

        self.validate_links()

        #
        # Identity
        #

        if not self.id:

            raise ValueError(
                "Span id cannot be empty."
            )

        if not self.name:

            raise ValueError(
                "Span name cannot be empty."
            )

        #
        # Enums
        #

        if not isinstance(
            self.kind,
            SpanKind,
        ):

            raise TypeError(
                "Invalid SpanKind."
            )

        if not isinstance(
            self.status,
            SpanStatus,
        ):

            raise TypeError(
                "Invalid SpanStatus."
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
        Validate SpanContext.
        """

        if not isinstance(
            self.context,
            SpanContext,
        ):

            raise TypeError(
                "context must be SpanContext."
            )

        if not self.context.span_id:

            raise ValueError(
                "Context span_id is missing."
            )

        if not self.context.service_name:

            raise ValueError(
                "Service name is required."
            )

        if not isinstance(
            self.context.span_kind,
            SpanKind,
        ):

            raise TypeError(
                "Invalid SpanKind."
            )

        return True

    # ------------------------------------------------------
    # Part 11.3
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

        identifiers: set[str] = set()

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

    # ------------------------------------------------------
    # Part 11.4
    # Validate Links
    # ------------------------------------------------------

    def validate_links(
        self,
    ) -> bool:
        """
        Validate span links.
        """

        if not isinstance(
            self.links,
            list,
        ):

            raise TypeError(
                "links must be a list."
            )

        identifiers: set[str] = set()

        for link in self.links:

            link_id = self._link_identifier(
                link
            )

            if not link_id:

                raise ValueError(
                    "Link identifier is missing."
                )

            if link_id in identifiers:

                raise ValueError(

                    f"Duplicate link id: {link_id}"

                )

            identifiers.add(
                link_id
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
# Runtime statistical APIs for SpanSchema.
#
# These methods are intended for:
#
#     • Dashboard
#     • CLI
#     • Runtime Inspector
#     • Exporters
#     • Monitoring
#
# They are read-only and never modify the Span.
# ==========================================================

    # ------------------------------------------------------
    # Part 12.1
    # Statistics
    # ------------------------------------------------------

    def statistics(self) -> Dict[str, Any]:
        """
        Return runtime statistics for this span.

        Returns
        -------
        Dict[str, Any]
        """

        return {

            # Identity

            "id":
                self.id,

            "name":
                self.name,

            "kind":
                self.kind.value,

            "status":
                self.status.value,

            # Timing

            "duration":
                self.duration,

            "started_at":
                self.started_at,

            "finished_at":
                self.finished_at,

            # Collections

            "events":
                self.event_count,

            "links":
                len(self.links),

            "attributes":
                self.attribute_count,

            "tags":
                len(self.tags),

            "metrics":
                len(self.metrics),

            # Runtime Flags

            "sampled":
                self.sampled,

            "exported":
                self.exported,

            "completed":
                self.completed,

        }

    # ------------------------------------------------------
    # Part 12.2
    # Diagnostics
    # ------------------------------------------------------

    def diagnostics(self) -> Dict[str, Any]:
        """
        Return runtime diagnostics.

        Returns
        -------
        Dict[str, Any]
        """

        validation_error = None

        try:

            self.validate()

            valid = True

        except Exception as exc:

            valid = False

            validation_error = str(exc)

        return {

            "valid":
                valid,

            "validation_error":
                validation_error,

            "running":
                self.running,

            "finished":
                self.finished,

            "failed":
                self.failed,

            "duration":
                self.duration,

            "event_count":
                self.event_count,

            "link_count":
                len(self.links),

            "attribute_count":
                self.attribute_count,

            "status":
                self.status.value,

            "kind":
                self.kind.value,

            "updated_at":
                self.updated_at,

        }

    # ------------------------------------------------------
    # Part 12.3
    # Summary
    # ------------------------------------------------------

    def summary(self) -> Dict[str, Any]:
        """
        Return a compact summary.

        Suitable for dashboards, CLI output,
        logging and exporters.

        Returns
        -------
        Dict[str, Any]
        """

        return {

            "id":
                self.id,

            "name":
                self.name,

            "status":
                self.status.value,

            "kind":
                self.kind.value,

            "duration":
                round(
                    self.duration,
                    6,
                ),

            "events":
                self.event_count,

            "links":
                len(self.links),

            "attributes":
                self.attribute_count,

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
# Python protocol implementations for SpanSchema.
# These provide a natural Python interface while remaining
# compatible with dataclasses(slots=True).
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

            f"kind={self.kind.value!r}, "

            f"status={self.status.value!r}, "

            f"events={self.event_count}, "

            f"links={len(self.links)}"

            f")"

        )

    # ------------------------------------------------------
    # Part 13.2
    # Human-readable String
    # ------------------------------------------------------

    def __str__(self) -> str:
        """
        Human-readable representation.
        """

        return (

            f"{self.name} "

            f"[{self.status.value}] "

            f"{self.duration:.6f}s"

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
            event_count + link_count
        """

        return (

            self.event_count

            +

            len(self.links)

        )

    # ------------------------------------------------------
    # Part 13.4
    # Iterator
    # ------------------------------------------------------

    def __iter__(
        self,
    ) -> Iterator[Any]:
        """
        Iterate over span events.
        """

        return iter(

            self.events

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

            • attribute key
            • tag key
            • event id
            • link id
        """

        if isinstance(item, str):

            if item in self.attributes:

                return True

            if item in self.tags:

                return True

            if self.has_event(item):

                return True

            if self.get_link(item) is not None:

                return True

        return False

    # ------------------------------------------------------
    # Part 13.6
    # Dictionary-style Access
    # ------------------------------------------------------

    def __getitem__(
        self,
        key: str,
    ) -> Any:
        """
        Dictionary-style lookup.

        Search order

            1. attributes
            2. tags
            3. dataclass fields
        """

        if key in self.attributes:

            return self.attributes[key]

        if key in self.tags:

            return self.tags[key]

        if hasattr(

            self,

            key,

        ):

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
        Unknown keys become attributes.
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

            self.set_attribute(

                key,

                value,

            )

        self.updated_at = timestamp()

    # ------------------------------------------------------
    # Part 13.8
    # Shallow Copy
    # ------------------------------------------------------

    def __copy__(
        self,
    ) -> "SpanSchema":
        """
        Return a shallow copy.
        """

        return self.clone()

    # ------------------------------------------------------
    # Part 13.9
    # Deep Copy
    # ------------------------------------------------------

    def __deepcopy__(
        self,
        memo: dict,
    ) -> "SpanSchema":
        """
        Return a deep copy.
        """

        if id(self) in memo:

            return memo[id(self)]

        cloned = self.clone()

        memo[id(self)] = cloned

        return cloned                                                                                            
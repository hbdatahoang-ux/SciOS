# scios/runtime/observability/schemas/event_schema.py

from __future__ import annotations

import copy
import json
import os
import socket
import threading
import uuid

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import (
    Any,
    Dict,
    List,
    Mapping,
    Optional,
    TypeAlias,
    TypeVar,
)


# ============================================================
# Constants
# ============================================================

DEFAULT_EVENT_NAME: str = "SciOS.Event"

DEFAULT_EVENT_MESSAGE: str = ""

DEFAULT_EVENT_SOURCE: str = "runtime"

DEFAULT_EVENT_LEVEL: str = "INFO"

DEFAULT_EVENT_TYPE: str = "SYSTEM"

DEFAULT_EVENT_STATUS: str = "CREATED"

DEFAULT_VERSION: str = "1.0"

DEFAULT_ENCODING: str = "utf-8"

DEFAULT_MAX_TAGS: int = 128

DEFAULT_MAX_ATTRIBUTES: int = 512

DEFAULT_MAX_PAYLOAD_SIZE: int = 1024 * 1024

UNKNOWN_VALUE: str = "unknown"

HOSTNAME: str = socket.gethostname()

PROCESS_ID: int = os.getpid()

EMPTY_PAYLOAD: Dict[str, Any] = {}

EMPTY_TAGS: Dict[str, str] = {}

EMPTY_ATTRIBUTES: Dict[str, Any] = {}

DEFAULT_TIMEZONE = timezone.utc



# ============================================================
# Enums
# ============================================================

class EventType(str, Enum):
    """
    Type/category of runtime event.
    """

    SYSTEM = "SYSTEM"

    RUNTIME = "RUNTIME"

    LIFECYCLE = "LIFECYCLE"

    EXECUTION = "EXECUTION"

    PIPELINE = "PIPELINE"

    STAGE = "STAGE"

    ERROR = "ERROR"

    WARNING = "WARNING"

    METRIC = "METRIC"

    TRACE = "TRACE"

    CUSTOM = "CUSTOM"



class EventLevel(str, Enum):
    """
    Severity level of event.
    """

    DEBUG = "DEBUG"

    INFO = "INFO"

    WARNING = "WARNING"

    ERROR = "ERROR"

    CRITICAL = "CRITICAL"



class EventStatus(str, Enum):
    """
    Lifecycle state of event.
    """

    CREATED = "CREATED"

    ACTIVE = "ACTIVE"

    COMPLETED = "COMPLETED"

    FAILED = "FAILED"

    CANCELLED = "CANCELLED"

    ARCHIVED = "ARCHIVED"



class EventSource(str, Enum):
    """
    Source component generating the event.
    """

    KERNEL = "KERNEL"

    RUNTIME = "RUNTIME"

    ENGINE = "ENGINE"

    PIPELINE = "PIPELINE"

    STAGE = "STAGE"

    OBSERVABILITY = "OBSERVABILITY"

    API = "API"

    CLI = "CLI"

    USER = "USER"

    SYSTEM = "SYSTEM"

    CUSTOM = "CUSTOM"



# ============================================================
# Type Aliases
# ============================================================

T = TypeVar("T")


JSONValue: TypeAlias = (
    str
    | int
    | float
    | bool
    | None
    | Dict[str, Any]
    | List[Any]
)


EventPayload: TypeAlias = Dict[str, Any]

TagMap: TypeAlias = Dict[str, str]

AttributeMap: TypeAlias = Dict[str, Any]

MetadataMap: TypeAlias = Dict[str, Any]

Snapshot: TypeAlias = Dict[str, Any]

Serializable: TypeAlias = Mapping[str, Any]



# ============================================================
# Utilities
# ============================================================

def utc_now() -> datetime:
    """
    Return timezone-aware UTC timestamp.
    """
    return datetime.now(DEFAULT_TIMEZONE)



def generate_event_id() -> str:
    """
    Generate unique event identifier.
    """
    return uuid.uuid4().hex



def deep_copy(value: T) -> T:
    """
    Safe deep copy.
    """
    return copy.deepcopy(value)



def json_dumps(data: Any) -> str:
    """
    Stable JSON serialization.
    """
    return json.dumps(
        data,
        ensure_ascii=False,
        sort_keys=True,
        default=str,
    )



def json_loads(data: str) -> Dict[str, Any]:
    """
    Parse JSON string.
    """
    return json.loads(data)



def normalize_event_type(
    event_type: str | EventType,
) -> EventType:
    """
    Normalize event type.
    """
    if isinstance(event_type, EventType):
        return event_type

    return EventType(
        str(event_type).upper()
    )



def normalize_event_level(
    level: str | EventLevel,
) -> EventLevel:
    """
    Normalize event level.
    """
    if isinstance(level, EventLevel):
        return level

    return EventLevel(
        str(level).upper()
    )



def normalize_event_status(
    status: str | EventStatus,
) -> EventStatus:
    """
    Normalize event status.
    """
    if isinstance(status, EventStatus):
        return status

    return EventStatus(
        str(status).upper()
    )



def normalize_message(
    message: str,
) -> str:
    """
    Normalize event message.
    """
    return str(message).strip()



def current_thread_id() -> int:
    """
    Return current thread identifier.
    """
    return threading.get_ident()
# ============================================================
# Part 2. Dataclasses
# ============================================================


@dataclass(slots=True)
class EventContext:
    """
    Runtime execution context associated with an event.
    """

    trace_id: str = ""

    span_id: str = ""

    parent_span_id: str = ""


    runtime_id: str = ""

    component: str = ""

    service: str = DEFAULT_EVENT_SOURCE


    thread_id: int = field(
        default_factory=current_thread_id
    )

    process_id: int = PROCESS_ID


    hostname: str = HOSTNAME

    environment: str = "production"


    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize EventContext into dictionary.
        """
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,

            "runtime_id": self.runtime_id,
            "component": self.component,
            "service": self.service,

            "thread_id": self.thread_id,
            "process_id": self.process_id,

            "hostname": self.hostname,
            "environment": self.environment,
        }


    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "EventContext":
        """
        Restore EventContext from dictionary.
        """
        return cls(
            trace_id=data.get(
                "trace_id",
                "",
            ),

            span_id=data.get(
                "span_id",
                "",
            ),

            parent_span_id=data.get(
                "parent_span_id",
                "",
            ),


            runtime_id=data.get(
                "runtime_id",
                "",
            ),

            component=data.get(
                "component",
                "",
            ),

            service=data.get(
                "service",
                DEFAULT_EVENT_SOURCE,
            ),


            thread_id=data.get(
                "thread_id",
                current_thread_id(),
            ),

            process_id=data.get(
                "process_id",
                PROCESS_ID,
            ),


            hostname=data.get(
                "hostname",
                HOSTNAME,
            ),

            environment=data.get(
                "environment",
                "production",
            ),
        )


    def copy(self) -> "EventContext":
        """
        Return deep copy of context.
        """
        return deep_copy(self)



@dataclass(slots=True)
class EventMetadata:
    """
    Metadata attached to an event.
    """

    created_at: datetime = field(
        default_factory=utc_now
    )

    updated_at: datetime = field(
        default_factory=utc_now
    )


    version: str = DEFAULT_VERSION


    source: EventSource = EventSource.RUNTIME


    attributes: AttributeMap = field(
        default_factory=dict
    )

    labels: TagMap = field(
        default_factory=dict
    )

    extra: MetadataMap = field(
        default_factory=dict
    )


    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize EventMetadata into dictionary.
        """
        return {
            "created_at": self.created_at.isoformat(),

            "updated_at": self.updated_at.isoformat(),

            "version": self.version,

            "source": self.source.value
            if isinstance(
                self.source,
                EventSource,
            )
            else self.source,

            "attributes": deep_copy(
                self.attributes
            ),

            "labels": deep_copy(
                self.labels
            ),

            "extra": deep_copy(
                self.extra
            ),
        }


    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "EventMetadata":
        """
        Restore EventMetadata from dictionary.
        """
        return cls(

            created_at=datetime.fromisoformat(
                data.get(
                    "created_at",
                    utc_now().isoformat(),
                )
            ),

            updated_at=datetime.fromisoformat(
                data.get(
                    "updated_at",
                    utc_now().isoformat(),
                )
            ),


            version=data.get(
                "version",
                DEFAULT_VERSION,
            ),


            source=EventSource(
                data.get(
                    "source",
                    EventSource.RUNTIME.value,
                )
            ),


            attributes=dict(
                data.get(
                    "attributes",
                    {},
                )
            ),

            labels=dict(
                data.get(
                    "labels",
                    {},
                )
            ),

            extra=dict(
                data.get(
                    "extra",
                    {},
                )
            ),
        )


    def merge(
        self,
        other: "EventMetadata",
    ) -> None:
        """
        Merge another metadata object.
        """
        if not isinstance(
            other,
            EventMetadata,
        ):
            raise TypeError(
                "other must be EventMetadata"
            )


        self.attributes.update(
            other.attributes
        )

        self.labels.update(
            other.labels
        )

        self.extra.update(
            other.extra
        )

        self.updated_at = utc_now()



    def copy(self) -> "EventMetadata":
        """
        Return deep copy of metadata.
        """
        return deep_copy(self)



@dataclass(slots=True)
class EventSchema:
    """
    Universal runtime event schema for SciOS-NG.
    """

    id: str = field(
        default_factory=generate_event_id
    )


    timestamp: datetime = field(
        default_factory=utc_now
    )


    type: EventType = EventType.SYSTEM


    level: EventLevel = EventLevel.INFO


    name: str = DEFAULT_EVENT_NAME


    message: str = DEFAULT_EVENT_MESSAGE


    source: EventSource = EventSource.RUNTIME


    context: EventContext = field(
        default_factory=EventContext
    )


    metadata: EventMetadata = field(
        default_factory=EventMetadata
    )


    payload: EventPayload = field(
        default_factory=dict
    )


    tags: TagMap = field(
        default_factory=dict
    )


    attributes: AttributeMap = field(
        default_factory=dict
    )


    status: EventStatus = EventStatus.CREATED
# ============================================================
# Part 3. Constructor
# ============================================================

    def __post_init__(self) -> None:
        """
        Initialize and normalize EventSchema after construction.
        """
        self._initialize_defaults()

        self._validate_types()

        self._normalize_fields()

        self._generate_identifier()

        self._update_timestamp()



    def _initialize_defaults(self) -> None:
        """
        Initialize missing default values.
        """

        if self.name is None:
            self.name = DEFAULT_EVENT_NAME


        if self.message is None:
            self.message = DEFAULT_EVENT_MESSAGE


        if self.source is None:
            self.source = EventSource.RUNTIME


        if self.context is None:
            self.context = EventContext()


        if self.metadata is None:
            self.metadata = EventMetadata()


        if self.payload is None:
            self.payload = {}


        if self.tags is None:
            self.tags = {}


        if self.attributes is None:
            self.attributes = {}



    def _validate_types(self) -> None:
        """
        Validate EventSchema field types.
        """

        if not isinstance(
            self.type,
            EventType,
        ):
            self.type = normalize_event_type(
                self.type
            )


        if not isinstance(
            self.level,
            EventLevel,
        ):
            self.level = normalize_event_level(
                self.level
            )


        if not isinstance(
            self.status,
            EventStatus,
        ):
            self.status = normalize_event_status(
                self.status
            )


        if not isinstance(
            self.source,
            EventSource,
        ):
            self.source = EventSource(
                str(self.source).upper()
            )


        if not isinstance(
            self.context,
            EventContext,
        ):
            raise TypeError(
                "context must be EventContext"
            )


        if not isinstance(
            self.metadata,
            EventMetadata,
        ):
            raise TypeError(
                "metadata must be EventMetadata"
            )


        if not isinstance(
            self.payload,
            dict,
        ):
            raise TypeError(
                "payload must be dictionary"
            )


        if not isinstance(
            self.tags,
            dict,
        ):
            raise TypeError(
                "tags must be dictionary"
            )


        if not isinstance(
            self.attributes,
            dict,
        ):
            raise TypeError(
                "attributes must be dictionary"
            )



    def _normalize_fields(self) -> None:
        """
        Normalize EventSchema fields.
        """

        self.name = (
            str(self.name)
            .strip()
        )


        self.message = normalize_message(
            self.message
        )


        self.type = normalize_event_type(
            self.type
        )


        self.level = normalize_event_level(
            self.level
        )


        self.status = normalize_event_status(
            self.status
        )



    def _generate_identifier(self) -> None:
        """
        Generate event identifier.
        """

        if not self.id:
            self.id = generate_event_id()



    def _update_timestamp(self) -> None:
        """
        Update event timestamps.
        """

        now = utc_now()


        if self.timestamp is None:
            self.timestamp = now


        self.metadata.updated_at = now
# ============================================================
# Part 4. Properties
# ============================================================

    @property
    def id(self) -> str:
        """
        Return event identifier.
        """
        return self._id


    @id.setter
    def id(self, value: str) -> None:
        """
        Set event identifier.
        """
        self._id = str(value)



    @property
    def timestamp(self) -> datetime:
        """
        Return event timestamp.
        """
        return self._timestamp


    @timestamp.setter
    def timestamp(self, value: datetime) -> None:
        """
        Set event timestamp.
        """
        if isinstance(
            value,
            datetime,
        ):
            self._timestamp = value
        else:
            self._timestamp = utc_now()



    @property
    def type(self) -> EventType:
        """
        Return event type.
        """
        return self._type


    @type.setter
    def type(
        self,
        value: EventType | str,
    ) -> None:
        """
        Set event type.
        """
        self._type = normalize_event_type(
            value
        )



    @property
    def level(self) -> EventLevel:
        """
        Return event severity level.
        """
        return self._level


    @level.setter
    def level(
        self,
        value: EventLevel | str,
    ) -> None:
        """
        Set event severity level.
        """
        self._level = normalize_event_level(
            value
        )



    @property
    def name(self) -> str:
        """
        Return event name.
        """
        return self._name


    @name.setter
    def name(
        self,
        value: str,
    ) -> None:
        """
        Set event name.
        """
        self._name = str(value).strip()



    @property
    def message(self) -> str:
        """
        Return event message.
        """
        return self._message


    @message.setter
    def message(
        self,
        value: str,
    ) -> None:
        """
        Set event message.
        """
        self._message = normalize_message(
            value
        )



    @property
    def source(self) -> EventSource:
        """
        Return event source.
        """
        return self._source


    @source.setter
    def source(
        self,
        value: EventSource | str,
    ) -> None:
        """
        Set event source.
        """
        if isinstance(
            value,
            EventSource,
        ):
            self._source = value
        else:
            self._source = EventSource(
                str(value).upper()
            )



    @property
    def tag_count(self) -> int:
        """
        Return number of event tags.
        """
        return len(self.tags)



    @property
    def attribute_count(self) -> int:
        """
        Return number of event attributes.
        """
        return len(self.attributes)



    @property
    def payload_size(self) -> int:
        """
        Estimate payload size in bytes.
        """
        return len(
            json_dumps(
                self.payload
            ).encode(
                DEFAULT_ENCODING
            )
        )



    @property
    def is_runtime_event(self) -> bool:
        """
        Check whether event belongs to runtime layer.
        """
        return (
            self.source
            in {
                EventSource.RUNTIME,
                EventSource.ENGINE,
                EventSource.PIPELINE,
                EventSource.STAGE,
            }
        )



    @property
    def status(self) -> EventStatus:
        """
        Return event lifecycle status.
        """
        return self._status


    @status.setter
    def status(
        self,
        value: EventStatus | str,
    ) -> None:
        """
        Set event lifecycle status.
        """
        self._status = normalize_event_status(
            value
        )
# ============================================================
# Part 5. Event Operations
# ============================================================

    def emit(
        self,
        message: Optional[str] = None,
        level: Optional[EventLevel | str] = None,
    ) -> "EventSchema":
        """
        Activate and emit an event.
        
        This method prepares the event for EventBus,
        Runtime dispatcher, or observability pipeline.
        """

        if message is not None:
            self.message = message

        if level is not None:
            self.level = level

        self.status = EventStatus.ACTIVE

        self.touch()

        return self



    def dispatch(
        self,
        dispatcher: Any = None,
    ) -> "EventSchema":
        """
        Dispatch event to an external dispatcher.

        Compatible with:
        - EventBus
        - Runtime Dispatcher
        - Pipeline Dispatcher
        """

        if dispatcher is not None:

            if hasattr(
                dispatcher,
                "dispatch",
            ):
                dispatcher.dispatch(
                    self
                )

            elif callable(dispatcher):
                dispatcher(
                    self
                )

            else:
                raise TypeError(
                    "dispatcher must be callable or provide dispatch()"
                )


        self.touch()

        return self



    def update(
        self,
        **kwargs: Any,
    ) -> "EventSchema":
        """
        Update event fields dynamically.
        """

        for key, value in kwargs.items():

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


        self.touch()

        return self



    def reset(self) -> "EventSchema":
        """
        Reset event to initial state.
        """

        self.id = generate_event_id()

        self.timestamp = utc_now()

        self.type = EventType.SYSTEM

        self.level = EventLevel.INFO

        self.name = DEFAULT_EVENT_NAME

        self.message = DEFAULT_EVENT_MESSAGE

        self.source = EventSource.RUNTIME


        self.context = EventContext()

        self.metadata = EventMetadata()


        self.payload.clear()

        self.tags.clear()

        self.attributes.clear()


        self.status = EventStatus.CREATED


        return self



    def touch(self) -> "EventSchema":
        """
        Update event timestamps.
        """

        now = utc_now()

        self.timestamp = now

        self.metadata.updated_at = now

        return self



    def merge(
        self,
        other: "EventSchema",
    ) -> "EventSchema":
        """
        Merge another event into current event.
        """

        if not isinstance(
            other,
            EventSchema,
        ):
            raise TypeError(
                "other must be EventSchema"
            )


        if other.name:
            self.name = other.name


        if other.message:
            self.message = other.message


        self.type = other.type

        self.level = other.level

        self.source = other.source


        self.payload.update(
            other.payload
        )


        self.tags.update(
            other.tags
        )


        self.attributes.update(
            other.attributes
        )


        self.metadata.merge(
            other.metadata
        )


        self.touch()

        return self



    def clone(self) -> "EventSchema":
        """
        Create a new independent event clone.
        """

        cloned = deep_copy(
            self
        )


        cloned.id = generate_event_id()

        cloned.timestamp = utc_now()

        cloned.status = EventStatus.CREATED


        return cloned
# ============================================================
# Part 6. Event Payload
# ============================================================

    def set_payload(
        self,
        key: str,
        value: Any,
    ) -> "EventSchema":
        """
        Set a single payload value.
        """

        if not isinstance(
            key,
            str,
        ):
            raise TypeError(
                "payload key must be string"
            )


        key = key.strip()


        if not key:
            raise ValueError(
                "payload key cannot be empty"
            )


        self.payload[key] = value


        self.touch()


        return self



    def get_payload(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve payload value.
        """

        return self.payload.get(
            key,
            default,
        )



    def remove_payload(
        self,
        key: str,
    ) -> bool:
        """
        Remove a payload field.
        """

        if key in self.payload:

            del self.payload[key]

            self.touch()

            return True


        return False



    def clear_payload(self) -> "EventSchema":
        """
        Remove all payload data.
        """

        self.payload.clear()


        self.touch()


        return self



    def update_payload(
        self,
        data: Mapping[str, Any],
    ) -> "EventSchema":
        """
        Update multiple payload values.
        """

        if not isinstance(
            data,
            Mapping,
        ):
            raise TypeError(
                "payload update must be a mapping"
            )


        if (
            self.payload_size
            > DEFAULT_MAX_PAYLOAD_SIZE
        ):
            raise ValueError(
                "payload size limit exceeded"
            )


        self.payload.update(
            dict(data)
        )


        self.touch()


        return self
# ============================================================
# Part 7. Tags & Attributes
# ============================================================

    def set_tag(
        self,
        key: str,
        value: str,
    ) -> "EventSchema":
        """
        Add or update an event tag.
        """

        if not isinstance(
            key,
            str,
        ):
            raise TypeError(
                "tag key must be string"
            )


        key = key.strip()


        if not key:
            raise ValueError(
                "tag key cannot be empty"
            )


        if (
            len(self.tags) >= DEFAULT_MAX_TAGS
            and key not in self.tags
        ):
            raise ValueError(
                "maximum tag limit exceeded"
            )


        self.tags[key] = str(value)


        self.touch()


        return self



    def get_tag(
        self,
        key: str,
        default: Optional[str] = None,
    ) -> Optional[str]:
        """
        Retrieve event tag value.
        """

        return self.tags.get(
            key,
            default,
        )



    def remove_tag(
        self,
        key: str,
    ) -> bool:
        """
        Remove event tag.
        """

        if key in self.tags:

            del self.tags[key]

            self.touch()

            return True


        return False



    def clear_tags(self) -> "EventSchema":
        """
        Clear all event tags.
        """

        self.tags.clear()


        self.touch()


        return self



    def set_attribute(
        self,
        key: str,
        value: Any,
    ) -> "EventSchema":
        """
        Add or update event attribute.
        """

        if not isinstance(
            key,
            str,
        ):
            raise TypeError(
                "attribute key must be string"
            )


        key = key.strip()


        if not key:
            raise ValueError(
                "attribute key cannot be empty"
            )


        if (
            len(self.attributes)
            >= DEFAULT_MAX_ATTRIBUTES
            and key not in self.attributes
        ):
            raise ValueError(
                "maximum attribute limit exceeded"
            )


        self.attributes[key] = value


        self.touch()


        return self



    def get_attribute(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve event attribute value.
        """

        return self.attributes.get(
            key,
            default,
        )



    def remove_attribute(
        self,
        key: str,
    ) -> bool:
        """
        Remove event attribute.
        """

        if key in self.attributes:

            del self.attributes[key]

            self.touch()

            return True


        return False



    def clear_attributes(self) -> "EventSchema":
        """
        Clear all event attributes.
        """

        self.attributes.clear()


        self.touch()


        return self
# ============================================================
# Part 8. Lifecycle
# ============================================================

    def activate(self) -> "EventSchema":
        """
        Activate event execution lifecycle.

        CREATED -> ACTIVE
        """

        self.status = EventStatus.ACTIVE

        self.touch()

        return self



    def deactivate(self) -> "EventSchema":
        """
        Deactivate an active event.

        ACTIVE -> CREATED
        """

        self.status = EventStatus.CREATED

        self.touch()

        return self



    def complete(self) -> "EventSchema":
        """
        Mark event as successfully completed.

        ACTIVE -> COMPLETED
        """

        self.status = EventStatus.COMPLETED

        self.touch()

        return self



    def fail(
        self,
        message: Optional[str] = None,
    ) -> "EventSchema":
        """
        Mark event as failed.

        ACTIVE -> FAILED
        """

        if message is not None:
            self.message = message


        self.level = EventLevel.ERROR

        self.status = EventStatus.FAILED

        self.touch()

        return self



    def cancel(
        self,
        message: Optional[str] = None,
    ) -> "EventSchema":
        """
        Cancel event execution.

        ACTIVE -> CANCELLED
        """

        if message is not None:
            self.message = message


        self.status = EventStatus.CANCELLED

        self.touch()

        return self



    def archive(self) -> "EventSchema":
        """
        Archive completed or failed event.

        COMPLETED / FAILED / CANCELLED
            -> ARCHIVED
        """

        self.status = EventStatus.ARCHIVED

        self.touch()

        return self
# ============================================================
# Part 9. Serialization
# ============================================================

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize EventSchema into dictionary format.
        """

        return {
            "id": self.id,

            "timestamp": self.timestamp.isoformat(),

            "type": self.type.value,

            "level": self.level.value,

            "name": self.name,

            "message": self.message,

            "source": self.source.value,


            "context": self.context.to_dict(),


            "metadata": self.metadata.to_dict(),


            "payload": deep_copy(
                self.payload
            ),


            "tags": deep_copy(
                self.tags
            ),


            "attributes": deep_copy(
                self.attributes
            ),


            "status": self.status.value,
        }



    def to_json(self) -> str:
        """
        Serialize EventSchema into JSON string.
        """

        return json_dumps(
            self.to_dict()
        )



    def to_yaml(self) -> str:
        """
        Serialize EventSchema into YAML string.
        """

        try:

            import yaml


            return yaml.safe_dump(
                self.to_dict(),
                allow_unicode=True,
                sort_keys=False,
            )


        except ImportError:

            raise ImportError(
                "PyYAML is required for YAML serialization."
            )



    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "EventSchema":
        """
        Restore EventSchema from dictionary.
        """

        if not isinstance(
            data,
            Mapping,
        ):
            raise TypeError(
                "data must be a mapping"
            )


        return cls(

            id=data.get(
                "id",
                generate_event_id(),
            ),


            timestamp=datetime.fromisoformat(
                data.get(
                    "timestamp",
                    utc_now().isoformat(),
                )
            ),


            type=normalize_event_type(
                data.get(
                    "type",
                    EventType.SYSTEM.value,
                )
            ),


            level=normalize_event_level(
                data.get(
                    "level",
                    EventLevel.INFO.value,
                )
            ),


            name=data.get(
                "name",
                DEFAULT_EVENT_NAME,
            ),


            message=data.get(
                "message",
                DEFAULT_EVENT_MESSAGE,
            ),


            source=EventSource(
                data.get(
                    "source",
                    EventSource.RUNTIME.value,
                )
            ),


            context=EventContext.from_dict(
                data.get(
                    "context",
                    {},
                )
            ),


            metadata=EventMetadata.from_dict(
                data.get(
                    "metadata",
                    {},
                )
            ),


            payload=dict(
                data.get(
                    "payload",
                    {},
                )
            ),


            tags=dict(
                data.get(
                    "tags",
                    {},
                )
            ),


            attributes=dict(
                data.get(
                    "attributes",
                    {},
                )
            ),


            status=normalize_event_status(
                data.get(
                    "status",
                    EventStatus.CREATED.value,
                )
            ),
        )



    @classmethod
    def from_json(
        cls,
        data: str,
    ) -> "EventSchema":
        """
        Restore EventSchema from JSON string.
        """

        return cls.from_dict(
            json_loads(data)
        )



    @classmethod
    def from_yaml(
        cls,
        data: str,
    ) -> "EventSchema":
        """
        Restore EventSchema from YAML string.
        """

        try:

            import yaml


            return cls.from_dict(
                yaml.safe_load(data)
            )


        except ImportError:

            raise ImportError(
                "PyYAML is required for YAML deserialization."
            )
# ============================================================
# Part 10. Snapshot
# ============================================================

    def snapshot(self) -> Snapshot:
        """
        Create a complete snapshot of current event state.
        """

        snapshot_data = self.to_dict()


        snapshot_data["_snapshot"] = {
            "created_at": utc_now().isoformat(),

            "schema_version": DEFAULT_VERSION,

            "event_id": self.id,

            "status": self.status.value,
        }


        return deep_copy(
            snapshot_data
        )



    def restore(
        self,
        snapshot: Snapshot,
    ) -> "EventSchema":
        """
        Restore EventSchema from snapshot.
        """

        if not isinstance(
            snapshot,
            Mapping,
        ):
            raise TypeError(
                "snapshot must be a mapping"
            )


        restored = EventSchema.from_dict(
            snapshot
        )


        self.id = restored.id

        self.timestamp = restored.timestamp


        self.type = restored.type

        self.level = restored.level


        self.name = restored.name

        self.message = restored.message


        self.source = restored.source


        self.context = restored.context

        self.metadata = restored.metadata


        self.payload = restored.payload


        self.tags = restored.tags

        self.attributes = restored.attributes


        self.status = EventStatus.ACTIVE


        self.touch()


        return self



    def clone(self) -> "EventSchema":
        """
        Create a new independent event clone.
        """

        cloned = deep_copy(
            self
        )


        cloned.id = generate_event_id()


        cloned.timestamp = utc_now()


        cloned.status = EventStatus.CREATED


        return cloned



    def copy(self) -> "EventSchema":
        """
        Create exact deep copy preserving identity.
        """

        return deep_copy(
            self
        )



    def freeze(self) -> "EventSchema":
        """
        Freeze event state for export/archive.

        Frozen events should not be modified
        during persistence.
        """

        self.status = EventStatus.ARCHIVED


        self.metadata.extra[
            "frozen"
        ] = True


        self.metadata.extra[
            "frozen_at"
        ] = utc_now().isoformat()


        return self



    def thaw(self) -> "EventSchema":
        """
        Restore event into mutable state.
        """

        self.metadata.extra.pop(
            "frozen",
            None,
        )


        self.metadata.extra.pop(
            "frozen_at",
            None,
        )


        if self.status == EventStatus.ARCHIVED:

            self.status = EventStatus.ACTIVE


        self.touch()


        return self
# ============================================================
# Part 11. Validation
# ============================================================

    def validate(self) -> bool:
        """
        Validate complete EventSchema.
        """

        return all(
            [
                self.validate_context(),

                self.validate_payload(),

                self.validate_tags(),

                self.validate_attributes(),

                self.validate_name(),

                self.validate_type(),

                self.validate_source(),
            ]
        )



    def validate_context(self) -> bool:
        """
        Validate event runtime context.
        """

        if not isinstance(
            self.context,
            EventContext,
        ):
            return False


        required_fields = [
            "hostname",
            "service",
            "environment",
        ]


        for field_name in required_fields:

            value = getattr(
                self.context,
                field_name,
                None,
            )


            if not value:
                return False


        return True



    def validate_payload(self) -> bool:
        """
        Validate event payload.
        """

        if not isinstance(
            self.payload,
            dict,
        ):
            return False


        if (
            self.payload_size
            > DEFAULT_MAX_PAYLOAD_SIZE
        ):
            return False


        return True



    def validate_tags(self) -> bool:
        """
        Validate event tags.
        """

        if not isinstance(
            self.tags,
            dict,
        ):
            return False


        if (
            len(self.tags)
            > DEFAULT_MAX_TAGS
        ):
            return False


        for key, value in self.tags.items():

            if not isinstance(
                key,
                str,
            ):
                return False


            if not isinstance(
                value,
                str,
            ):
                return False


            if not key.strip():
                return False


        return True



    def validate_attributes(self) -> bool:
        """
        Validate event attributes.
        """

        if not isinstance(
            self.attributes,
            dict,
        ):
            return False


        if (
            len(self.attributes)
            > DEFAULT_MAX_ATTRIBUTES
        ):
            return False


        for key in self.attributes.keys():

            if not isinstance(
                key,
                str,
            ):
                return False


            if not key.strip():
                return False


        return True



    def validate_name(self) -> bool:
        """
        Validate event name.
        """

        if not isinstance(
            self.name,
            str,
        ):
            return False


        if not self.name.strip():
            return False


        return True



    def validate_type(self) -> bool:
        """
        Validate event type.
        """

        return isinstance(
            self.type,
            EventType,
        )



    def validate_source(self) -> bool:
        """
        Validate event source.
        """

        return isinstance(
            self.source,
            EventSource,
        )
# ============================================================
# Part 12. Statistics
# ============================================================

    def diagnostics(self) -> Dict[str, Any]:
        """
        Return detailed diagnostic information
        about current event state.
        """

        return {
            "id": self.id,

            "type": self.type.value,

            "level": self.level.value,

            "status": self.status.value,

            "source": self.source.value,


            "name": self.name,

            "message_length": len(
                self.message
            ),


            "timestamp": self.timestamp.isoformat(),


            "payload_size": self.payload_size,


            "tag_count": self.tag_count,

            "attribute_count": self.attribute_count,


            "is_runtime_event": self.is_runtime_event,


            "valid": self.validate(),


            "context": {
                "trace_id": self.context.trace_id,

                "span_id": self.context.span_id,

                "runtime_id": self.context.runtime_id,

                "component": self.context.component,

                "service": self.context.service,
            },


            "metadata": {
                "version": self.metadata.version,

                "source": (
                    self.metadata.source.value
                    if isinstance(
                        self.metadata.source,
                        EventSource,
                    )
                    else self.metadata.source
                ),

                "created_at":
                    self.metadata.created_at.isoformat(),

                "updated_at":
                    self.metadata.updated_at.isoformat(),
            },
        }



    def summary(self) -> Dict[str, Any]:
        """
        Return compact event summary.
        """

        return {
            "id": self.id,

            "name": self.name,

            "type": self.type.value,

            "level": self.level.value,

            "status": self.status.value,

            "source": self.source.value,

            "message": self.message,

            "timestamp":
                self.timestamp.isoformat(),
        }



    def runtime_statistics(self) -> Dict[str, Any]:
        """
        Return runtime execution statistics.
        """

        return {
            "runtime_id":
                self.context.runtime_id,

            "component":
                self.context.component,

            "service":
                self.context.service,


            "thread_id":
                self.context.thread_id,

            "process_id":
                self.context.process_id,


            "hostname":
                self.context.hostname,


            "environment":
                self.context.environment,


            "is_runtime_event":
                self.is_runtime_event,


            "status":
                self.status.value,
        }



    def memory_usage(self) -> Dict[str, int]:
        """
        Estimate memory usage of event components.
        """

        payload_bytes = len(
            json_dumps(
                self.payload
            ).encode(
                DEFAULT_ENCODING
            )
        )


        tags_bytes = len(
            json_dumps(
                self.tags
            ).encode(
                DEFAULT_ENCODING
            )
        )


        attributes_bytes = len(
            json_dumps(
                self.attributes
            ).encode(
                DEFAULT_ENCODING
            )
        )


        message_bytes = len(
            self.message.encode(
                DEFAULT_ENCODING
            )
        )


        return {
            "payload_bytes": payload_bytes,

            "tags_bytes": tags_bytes,

            "attributes_bytes": attributes_bytes,

            "message_bytes": message_bytes,


            "total_bytes":
                payload_bytes
                + tags_bytes
                + attributes_bytes
                + message_bytes,
        }



    def field_statistics(self) -> Dict[str, Any]:
        """
        Return statistics for event fields.
        """

        return {
            "fields": {

                "payload":
                    len(self.payload),

                "tags":
                    len(self.tags),

                "attributes":
                    len(self.attributes),

            },


            "objects": {

                "context":
                    len(
                        self.context.to_dict()
                    ),

                "metadata":
                    len(
                        self.metadata.to_dict()
                    ),
            },


            "total_fields":
                (
                    len(self.payload)
                    +
                    len(self.tags)
                    +
                    len(self.attributes)
                ),
        }



    def is_valid(self) -> bool:
        """
        Shortcut method for validation status.
        """

        return self.validate()
# ============================================================
# Part 13. Python Protocols
# ============================================================

    def __repr__(self) -> str:
        """
        Developer-friendly representation.
        """

        return (
            f"EventSchema("
            f"id={self.id!r}, "
            f"type={self.type.value!r}, "
            f"level={self.level.value!r}, "
            f"name={self.name!r}, "
            f"status={self.status.value!r}"
            f")"
        )



    def __str__(self) -> str:
        """
        Human-readable event representation.
        """

        return (
            f"[{self.level.value}] "
            f"{self.name}: "
            f"{self.message}"
        )



    def __len__(self) -> int:
        """
        Return number of event data fields.
        """

        return (
            len(self.payload)
            +
            len(self.tags)
            +
            len(self.attributes)
        )



    def __iter__(self) -> Iterator[str]:
        """
        Iterate through event keys.
        """

        yield from self.to_dict().keys()



    def __contains__(
        self,
        key: str,
    ) -> bool:
        """
        Check whether event contains field.
        """

        return (
            key in self.payload
            or key in self.tags
            or key in self.attributes
            or key in self.to_dict()
        )



    def __getitem__(
        self,
        key: str,
    ) -> Any:
        """
        Dictionary-style event access.
        """

        if key in self.payload:
            return self.payload[key]


        if key in self.tags:
            return self.tags[key]


        if key in self.attributes:
            return self.attributes[key]


        data = self.to_dict()


        if key in data:
            return data[key]


        raise KeyError(
            key
        )



    def __setitem__(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Dictionary-style event mutation.
        """

        if key in self.tags:

            self.tags[key] = str(value)


        elif key in self.attributes:

            self.attributes[key] = value


        else:

            self.payload[key] = value


        self.touch()



    def __copy__(self) -> "EventSchema":
        """
        Shallow copy protocol.
        """

        return copy.copy(
            self
        )



    def __deepcopy__(
        self,
        memo: Optional[Dict[int, Any]] = None,
    ) -> "EventSchema":
        """
        Deep copy protocol.
        """

        if memo is None:
            memo = {}


        cloned = EventSchema(
            id=self.id,

            timestamp=self.timestamp,

            type=self.type,

            level=self.level,

            name=self.name,

            message=self.message,

            source=self.source,

            context=self.context.copy(),

            metadata=self.metadata.copy(),

            payload=deep_copy(
                self.payload
            ),

            tags=deep_copy(
                self.tags
            ),

            attributes=deep_copy(
                self.attributes
            ),

            status=self.status,
        )


        memo[id(self)] = cloned


        return cloned



    def __hash__(self) -> int:
        """
        Hash event using immutable identity.
        """

        return hash(
            self.id
        )



    def __eq__(
        self,
        other: object,
    ) -> bool:
        """
        Compare two events.
        """

        if not isinstance(
            other,
            EventSchema,
        ):
            return False


        return (
            self.id == other.id
            and
            self.type == other.type
            and
            self.level == other.level
            and
            self.name == other.name
            and
            self.message == other.message
            and
            self.status == other.status
        )                                                                                            
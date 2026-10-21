from __future__ import annotations

import copy
import json
import socket
import threading
import uuid

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import (
    Any,
    Dict,
    Iterable,
    Iterator,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    Type,
    TypeAlias,
    TypeVar,
)

DEFAULT_LOGGER_NAME: str = "SciOS"
DEFAULT_MODULE_NAME: str = "runtime"
DEFAULT_LOG_MESSAGE: str = ""
DEFAULT_LOG_FORMAT: str = "text"
DEFAULT_ENCODING: str = "utf-8"
DEFAULT_TIMEZONE = timezone.utc
DEFAULT_MAX_MESSAGE_LENGTH: int = 8192
DEFAULT_MAX_TAGS: int = 128
DEFAULT_MAX_ATTRIBUTES: int = 512
DEFAULT_VERSION: str = "1.0"
UNKNOWN_VALUE: str = "unknown"

HOSTNAME: str = socket.gethostname()

EMPTY_TAGS: Dict[str, str] = {}
EMPTY_ATTRIBUTES: Dict[str, Any] = {}


class LogLevel(str, Enum):
    """
    Standard logging levels.
    """

    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    FATAL = "FATAL"
    NOTSET = "NOTSET"


class LogStatus(str, Enum):
    """
    Runtime state of a log record.
    """

    CREATED = "CREATED"
    UPDATED = "UPDATED"
    VALIDATED = "VALIDATED"
    SERIALIZED = "SERIALIZED"
    SNAPSHOTTED = "SNAPSHOTTED"
    RESTORED = "RESTORED"
    ARCHIVED = "ARCHIVED"
    DELETED = "DELETED"


class LogFormat(str, Enum):
    """
    Supported serialization formats.
    """

    TEXT = "text"
    JSON = "json"
    YAML = "yaml"
    XML = "xml"
    BINARY = "binary"


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

TagMap: TypeAlias = Dict[str, str]
AttributeMap: TypeAlias = Dict[str, Any]
MetadataMap: TypeAlias = Dict[str, Any]
Snapshot: TypeAlias = Dict[str, Any]
Serializable: TypeAlias = Mapping[str, Any]


def utc_now() -> datetime:
    """
    Return timezone-aware UTC timestamp.
    """
    return datetime.now(timezone.utc)


def generate_log_id() -> str:
    """
    Generate a unique log identifier.
    """
    return uuid.uuid4().hex


def deep_copy(value: T) -> T:
    """
    Safely perform a deep copy.
    """
    return copy.deepcopy(value)


def json_dumps(data: Any) -> str:
    """
    Serialize an object into a stable JSON string.
    """
    return json.dumps(
        data,
        ensure_ascii=False,
        sort_keys=True,
        default=str,
    )


def json_loads(data: str) -> Dict[str, Any]:
    """
    Deserialize a JSON string.
    """
    return json.loads(data)


def normalize_level(level: str | LogLevel) -> LogLevel:
    """
    Normalize a log level to LogLevel.
    """
    if isinstance(level, LogLevel):
        return level
    return LogLevel(level.upper())


def normalize_message(message: str) -> str:
    """
    Normalize a log message.
    """
    return message.strip()


def current_thread_id() -> int:
    """
    Return the current thread identifier.
    """
    return threading.get_ident()
@dataclass(slots=True)
class LogContext:
    """
    Runtime execution context associated with a log record.
    """

    trace_id: str = ""
    span_id: str = ""
    parent_span_id: str = ""

    correlation_id: str = ""
    request_id: str = ""
    session_id: str = ""

    thread_id: int = field(default_factory=current_thread_id)
    process_id: int = 0

    hostname: str = HOSTNAME
    service: str = DEFAULT_LOGGER_NAME
    environment: str = "production"

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the context into a dictionary.
        """
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "correlation_id": self.correlation_id,
            "request_id": self.request_id,
            "session_id": self.session_id,
            "thread_id": self.thread_id,
            "process_id": self.process_id,
            "hostname": self.hostname,
            "service": self.service,
            "environment": self.environment,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "LogContext":
        """
        Construct a LogContext from a dictionary.
        """
        return cls(
            trace_id=data.get("trace_id", ""),
            span_id=data.get("span_id", ""),
            parent_span_id=data.get("parent_span_id", ""),
            correlation_id=data.get("correlation_id", ""),
            request_id=data.get("request_id", ""),
            session_id=data.get("session_id", ""),
            thread_id=data.get("thread_id", current_thread_id()),
            process_id=data.get("process_id", 0),
            hostname=data.get("hostname", HOSTNAME),
            service=data.get("service", DEFAULT_LOGGER_NAME),
            environment=data.get("environment", "production"),
        )

    def copy(self) -> "LogContext":
        """
        Return a deep copy of this context.
        """
        return deep_copy(self)


@dataclass(slots=True)
class LogMetadata:
    """
    Metadata associated with a log record.
    """

    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    source: str = DEFAULT_MODULE_NAME
    version: str = DEFAULT_VERSION

    attributes: AttributeMap = field(default_factory=dict)
    labels: TagMap = field(default_factory=dict)
    extra: MetadataMap = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize metadata into a dictionary.
        """
        return {
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "source": self.source,
            "version": self.version,
            "attributes": deep_copy(self.attributes),
            "labels": deep_copy(self.labels),
            "extra": deep_copy(self.extra),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "LogMetadata":
        """
        Construct LogMetadata from a dictionary.
        """
        return cls(
            created_at=datetime.fromisoformat(
                data.get("created_at", utc_now().isoformat())
            ),
            updated_at=datetime.fromisoformat(
                data.get("updated_at", utc_now().isoformat())
            ),
            source=data.get("source", DEFAULT_MODULE_NAME),
            version=data.get("version", DEFAULT_VERSION),
            attributes=dict(data.get("attributes", {})),
            labels=dict(data.get("labels", {})),
            extra=dict(data.get("extra", {})),
        )

    def merge(self, other: "LogMetadata") -> None:
        """
        Merge another metadata object into this one.
        """
        self.updated_at = utc_now()

        self.attributes.update(other.attributes)
        self.labels.update(other.labels)
        self.extra.update(other.extra)

    def copy(self) -> "LogMetadata":
        """
        Return a deep copy of this metadata.
        """
        return deep_copy(self)


@dataclass(slots=True)
class LogSchema:
    """
    Canonical log schema for the SciOS-NG observability subsystem.
    """

    id: str = field(default_factory=generate_log_id)
    timestamp: datetime = field(default_factory=utc_now)

    level: LogLevel = LogLevel.INFO
    message: str = DEFAULT_LOG_MESSAGE

    logger: str = DEFAULT_LOGGER_NAME
    module: str = DEFAULT_MODULE_NAME
    function: str = ""
    line: int = 0

    context: LogContext = field(default_factory=LogContext)
    metadata: LogMetadata = field(default_factory=LogMetadata)

    tags: TagMap = field(default_factory=dict)
    attributes: AttributeMap = field(default_factory=dict)

    exception: Optional[BaseException] = None

    status: LogStatus = LogStatus.CREATED
    # ------------------------------------------------------------------
    # Part 3. Constructor
    # ------------------------------------------------------------------

    def __post_init__(self) -> None:
        """
        Initialize and normalize the log schema after construction.
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
        if self.logger is None:
            self.logger = DEFAULT_LOGGER_NAME

        if self.module is None:
            self.module = DEFAULT_MODULE_NAME

        if self.message is None:
            self.message = DEFAULT_LOG_MESSAGE

        if self.tags is None:
            self.tags = {}

        if self.attributes is None:
            self.attributes = {}

        if self.context is None:
            self.context = LogContext()

        if self.metadata is None:
            self.metadata = LogMetadata()

    def _validate_types(self) -> None:
        """
        Validate core field types.
        """
        if not isinstance(self.level, LogLevel):
            self.level = normalize_level(self.level)

        if not isinstance(self.message, str):
            self.message = str(self.message)

        if not isinstance(self.logger, str):
            raise TypeError("logger must be a string.")

        if not isinstance(self.module, str):
            raise TypeError("module must be a string.")

        if not isinstance(self.line, int):
            raise TypeError("line must be an integer.")

        if not isinstance(self.context, LogContext):
            raise TypeError("context must be a LogContext.")

        if not isinstance(self.metadata, LogMetadata):
            raise TypeError("metadata must be a LogMetadata.")

        if not isinstance(self.tags, dict):
            raise TypeError("tags must be a dictionary.")

        if not isinstance(self.attributes, dict):
            raise TypeError("attributes must be a dictionary.")

    def _normalize_fields(self) -> None:
        """
        Normalize log fields.
        """
        self.message = normalize_message(self.message)

        self.logger = self.logger.strip()

        self.module = self.module.strip()

        self.function = self.function.strip()

        self.level = normalize_level(self.level)

    def _generate_identifier(self) -> None:
        """
        Generate a unique identifier if one does not exist.
        """
        if not self.id:
            self.id = generate_log_id()

    def _update_timestamp(self) -> None:
        """
        Update timestamps.
        """
        now = utc_now()

        if self.timestamp is None:
            self.timestamp = now

        self.metadata.updated_at = now
    # ------------------------------------------------------------------
    # Part 4. Properties
    # ------------------------------------------------------------------

    @property
    def message(self) -> str:
        """
        Return the log message.
        """
        return self._message

    @message.setter
    def message(self, value: str) -> None:
        """
        Set the log message.
        """
        self._message = normalize_message(str(value))

    @property
    def level(self) -> LogLevel:
        """
        Return the log level.
        """
        return self._level

    @level.setter
    def level(self, value: str | LogLevel) -> None:
        """
        Set the log level.
        """
        self._level = normalize_level(value)

    @property
    def logger(self) -> str:
        """
        Return the logger name.
        """
        return self._logger

    @logger.setter
    def logger(self, value: str) -> None:
        """
        Set the logger name.
        """
        self._logger = str(value).strip()

    @property
    def module(self) -> str:
        """
        Return the module name.
        """
        return self._module

    @module.setter
    def module(self, value: str) -> None:
        """
        Set the module name.
        """
        self._module = str(value).strip()

    @property
    def function(self) -> str:
        """
        Return the function name.
        """
        return self._function

    @function.setter
    def function(self, value: str) -> None:
        """
        Set the function name.
        """
        self._function = str(value).strip()

    @property
    def line(self) -> int:
        """
        Return the source code line number.
        """
        return self._line

    @line.setter
    def line(self, value: int) -> None:
        """
        Set the source code line number.
        """
        self._line = int(value)

    @property
    def tag_count(self) -> int:
        """
        Return the number of tags.
        """
        return len(self.tags)

    @property
    def attribute_count(self) -> int:
        """
        Return the number of attributes.
        """
        return len(self.attributes)

    @property
    def has_exception(self) -> bool:
        """
        Return True if an exception is attached.
        """
        return self.exception is not None

    @property
    def timestamp(self) -> datetime:
        """
        Return the log timestamp.
        """
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value: datetime) -> None:
        """
        Set the log timestamp.
        """
        self._timestamp = value if isinstance(value, datetime) else utc_now()

    @property
    def status(self) -> LogStatus:
        """
        Return the current log status.
        """
        return self._status

    @status.setter
    def status(self, value: LogStatus | str) -> None:
        """
        Set the current log status.
        """
        if isinstance(value, LogStatus):
            self._status = value
        else:
            self._status = LogStatus(str(value).upper())
    # ------------------------------------------------------------------
    # Part 5. Log Operations
    # ------------------------------------------------------------------

    def info(self, message: str) -> "LogSchema":
        """
        Update the log as an INFO record.
        """
        self.level = LogLevel.INFO
        self.message = message
        self.touch()
        return self

    def debug(self, message: str) -> "LogSchema":
        """
        Update the log as a DEBUG record.
        """
        self.level = LogLevel.DEBUG
        self.message = message
        self.touch()
        return self

    def warning(self, message: str) -> "LogSchema":
        """
        Update the log as a WARNING record.
        """
        self.level = LogLevel.WARNING
        self.message = message
        self.touch()
        return self

    def error(self, message: str) -> "LogSchema":
        """
        Update the log as an ERROR record.
        """
        self.level = LogLevel.ERROR
        self.message = message
        self.touch()
        return self

    def critical(self, message: str) -> "LogSchema":
        """
        Update the log as a CRITICAL record.
        """
        self.level = LogLevel.CRITICAL
        self.message = message
        self.touch()
        return self

    def reset(self) -> None:
        """
        Reset the log record to its default state.
        """
        self.timestamp = utc_now()
        self.level = LogLevel.INFO
        self.message = DEFAULT_LOG_MESSAGE

        self.logger = DEFAULT_LOGGER_NAME
        self.module = DEFAULT_MODULE_NAME
        self.function = ""
        self.line = 0

        self.context = LogContext()
        self.metadata = LogMetadata()

        self.tags.clear()
        self.attributes.clear()

        self.exception = None
        self.status = LogStatus.CREATED

    def touch(self) -> None:
        """
        Refresh timestamps and mark the log as updated.
        """
        now = utc_now()

        self.timestamp = now
        self.metadata.updated_at = now
        self.status = LogStatus.UPDATED

    def update(self, **kwargs: Any) -> "LogSchema":
        """
        Update one or more log fields.
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

        self.touch()
        return self

    def merge(self, other: "LogSchema") -> "LogSchema":
        """
        Merge another LogSchema into this one.
        """
        if not isinstance(other, LogSchema):
            raise TypeError("other must be a LogSchema instance.")

        if other.message:
            self.message = other.message

        self.level = other.level
        self.logger = other.logger
        self.module = other.module
        self.function = other.function
        self.line = other.line

        self.tags.update(other.tags)
        self.attributes.update(other.attributes)

        self.metadata.merge(other.metadata)

        if other.exception is not None:
            self.exception = other.exception

        self.touch()
        return self
    # ------------------------------------------------------------------
    # Part 6. Exception Management
    # ------------------------------------------------------------------

    def attach_exception(self, exception: BaseException) -> "LogSchema":
        """
        Attach an exception to this log record.
        """
        if not isinstance(exception, BaseException):
            raise TypeError("exception must be an instance of BaseException.")

        self.exception = exception
        self.level = LogLevel.ERROR
        self.touch()
        return self

    def clear_exception(self) -> "LogSchema":
        """
        Remove the attached exception.
        """
        self.exception = None
        self.touch()
        return self

    def has_exception(self) -> bool:
        """
        Return True if an exception is attached.
        """
        return self.exception is not None

    def exception_summary(self) -> str:
        """
        Return a short summary of the attached exception.
        """
        if self.exception is None:
            return ""

        return (
            f"{type(self.exception).__name__}: "
            f"{self.exception}"
        )

    def exception_type(self) -> str:
        """
        Return the exception class name.
        """
        if self.exception is None:
            return ""

        return type(self.exception).__name__

    def exception_message(self) -> str:
        """
        Return the exception message.
        """
        if self.exception is None:
            return ""

        return str(self.exception)

    def stack_trace(self) -> str:
        """
        Return the formatted stack trace of the attached exception.
        """
        if self.exception is None:
            return ""

        import traceback

        return "".join(
            traceback.format_exception(
                type(self.exception),
                self.exception,
                self.exception.__traceback__,
            )
        )
    # ------------------------------------------------------------------
    # Part 7. Tags & Metadata
    # ------------------------------------------------------------------

    def set_tag(
        self,
        key: str,
        value: str,
    ) -> "LogSchema":
        """
        Add or update a tag.
        """
        if not isinstance(key, str):
            raise TypeError("tag key must be a string.")

        if not isinstance(value, str):
            value = str(value)

        key = key.strip()

        if not key:
            raise ValueError("tag key cannot be empty.")

        if len(self.tags) >= DEFAULT_MAX_TAGS and key not in self.tags:
            raise ValueError("maximum tag limit exceeded.")

        self.tags[key] = value

        self.touch()

        return self


    def get_tag(
        self,
        key: str,
        default: Optional[str] = None,
    ) -> Optional[str]:
        """
        Retrieve a tag value.
        """
        return self.tags.get(key, default)


    def remove_tag(
        self,
        key: str,
    ) -> bool:
        """
        Remove a tag.
        """
        if key in self.tags:
            del self.tags[key]
            self.touch()
            return true

        return False


    def clear_tags(self) -> "LogSchema":
        """
        Remove all tags.
        """
        self.tags.clear()

        self.touch()

        return self


    def update_metadata(
        self,
        metadata: Mapping[str, Any],
    ) -> "LogSchema":
        """
        Update log metadata.
        """
        if not isinstance(metadata, Mapping):
            raise TypeError(
                "metadata must be a mapping."
            )

        self.metadata.extra.update(
            dict(metadata)
        )

        self.metadata.updated_at = utc_now()

        self.touch()

        return self


    def set_attribute(
        self,
        key: str,
        value: Any,
    ) -> "LogSchema":
        """
        Add or update an attribute.
        """
        if not isinstance(key, str):
            raise TypeError(
                "attribute key must be a string."
            )

        key = key.strip()

        if not key:
            raise ValueError(
                "attribute key cannot be empty."
            )

        if (
            len(self.attributes) >= DEFAULT_MAX_ATTRIBUTES
            and key not in self.attributes
        ):
            raise ValueError(
                "maximum attribute limit exceeded."
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
        Retrieve an attribute value.
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
        Remove an attribute.
        """
        if key in self.attributes:
            del self.attributes[key]

            self.touch()

            return True

        return False


    def clear_attributes(self) -> "LogSchema":
        """
        Remove all attributes.
        """
        self.attributes.clear()

        self.touch()

        return self
    # ------------------------------------------------------------------
    # Part 8. Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize LogSchema into dictionary format.
        """
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),

            "level": self.level.value,
            "message": self.message,

            "logger": self.logger,
            "module": self.module,
            "function": self.function,
            "line": self.line,

            "context": self.context.to_dict(),

            "metadata": self.metadata.to_dict(),

            "tags": deep_copy(self.tags),

            "attributes": deep_copy(self.attributes),

            "exception": {
                "type": self.exception_type(),
                "message": self.exception_message(),
                "stack_trace": self.stack_trace(),
            }
            if self.has_exception()
            else None,

            "status": self.status.value,
        }


    def to_json(self) -> str:
        """
        Serialize LogSchema into JSON format.
        """
        return json_dumps(
            self.to_dict()
        )


    def to_yaml(self) -> str:
        """
        Serialize LogSchema into YAML format.
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
    ) -> "LogSchema":
        """
        Restore LogSchema from dictionary.
        """

        exception_data = data.get(
            "exception"
        )

        obj = cls(
            id=data.get(
                "id",
                generate_log_id(),
            ),

            timestamp=datetime.fromisoformat(
                data.get(
                    "timestamp",
                    utc_now().isoformat(),
                )
            ),

            level=normalize_level(
                data.get(
                    "level",
                    LogLevel.INFO.value,
                )
            ),

            message=data.get(
                "message",
                DEFAULT_LOG_MESSAGE,
            ),

            logger=data.get(
                "logger",
                DEFAULT_LOGGER_NAME,
            ),

            module=data.get(
                "module",
                DEFAULT_MODULE_NAME,
            ),

            function=data.get(
                "function",
                "",
            ),

            line=data.get(
                "line",
                0,
            ),

            context=LogContext.from_dict(
                data.get(
                    "context",
                    {},
                )
            ),

            metadata=LogMetadata.from_dict(
                data.get(
                    "metadata",
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

            status=LogStatus(
                data.get(
                    "status",
                    LogStatus.CREATED.value,
                )
            ),
        )

        if exception_data:
            obj.metadata.extra["exception"] = exception_data

        return obj


    @classmethod
    def from_json(
        cls,
        data: str,
    ) -> "LogSchema":
        """
        Restore LogSchema from JSON string.
        """
        return cls.from_dict(
            json_loads(data)
        )


    @classmethod
    def from_yaml(
        cls,
        data: str,
    ) -> "LogSchema":
        """
        Restore LogSchema from YAML string.
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
    # ------------------------------------------------------------------
    # Part 9. Snapshot
    # ------------------------------------------------------------------

    def snapshot(self) -> Snapshot:
        """
        Create an immutable snapshot of the current log state.
        """
        snapshot_data = self.to_dict()

        snapshot_data["_snapshot"] = {
            "created_at": utc_now().isoformat(),
            "schema_version": DEFAULT_VERSION,
            "object_id": self.id,
        }

        self.status = LogStatus.SNAPSHOTTED

        return deep_copy(snapshot_data)


    def restore(
        self,
        snapshot: Snapshot,
    ) -> "LogSchema":
        """
        Restore log state from a snapshot.
        """
        if not isinstance(snapshot, Mapping):
            raise TypeError(
                "snapshot must be a mapping."
            )

        restored = LogSchema.from_dict(
            snapshot
        )

        self.id = restored.id
        self.timestamp = restored.timestamp

        self.level = restored.level
        self.message = restored.message

        self.logger = restored.logger
        self.module = restored.module
        self.function = restored.function
        self.line = restored.line

        self.context = restored.context
        self.metadata = restored.metadata

        self.tags = restored.tags
        self.attributes = restored.attributes

        self.exception = restored.exception

        self.status = LogStatus.RESTORED

        self.touch()

        return self


    def clone(self) -> "LogSchema":
        """
        Create a deep independent clone.
        """
        cloned = deep_copy(self)

        cloned.id = generate_log_id()

        cloned.status = LogStatus.CREATED

        cloned.timestamp = utc_now()

        return cloned


    def copy(self) -> "LogSchema":
        """
        Create a copy preserving identity.
        """
        return deep_copy(self)


    def freeze(self) -> "LogSchema":
        """
        Freeze the current log record.

        A frozen log should not be modified
        during export or archival.
        """
        self.status = LogStatus.SERIALIZED

        return self


    def thaw(self) -> "LogSchema":
        """
        Re-enable modifications after freezing.
        """
        self.status = LogStatus.UPDATED

        self.touch()

        return self
    # ------------------------------------------------------------------
    # Part 10. Validation
    # ------------------------------------------------------------------

    def validate(self) -> bool:
        """
        Validate the complete LogSchema object.
        """
        return all(
            [
                self.validate_context(),
                self.validate_tags(),
                self.validate_attributes(),
                self.validate_message(),
                self.validate_level(),
                self.validate_logger(),
            ]
        )


    def validate_context(self) -> bool:
        """
        Validate log execution context.
        """
        if not isinstance(
            self.context,
            LogContext,
        ):
            return False

        required_fields = [
            "hostname",
            "service",
            "environment",
        ]

        for field_name in required_fields:
            if not getattr(
                self.context,
                field_name,
                None,
            ):
                return False

        return True


    def validate_tags(self) -> bool:
        """
        Validate log tags.
        """
        if not isinstance(
            self.tags,
            dict,
        ):
            return False

        if len(self.tags) > DEFAULT_MAX_TAGS:
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
        Validate log attributes.
        """
        if not isinstance(
            self.attributes,
            dict,
        ):
            return False

        if len(self.attributes) > DEFAULT_MAX_ATTRIBUTES:
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


    def validate_message(self) -> bool:
        """
        Validate log message.
        """
        if not isinstance(
            self.message,
            str,
        ):
            return False

        if len(self.message) > DEFAULT_MAX_MESSAGE_LENGTH:
            return False

        return True


    def validate_level(self) -> bool:
        """
        Validate log level.
        """
        return isinstance(
            self.level,
            LogLevel,
        )


    def validate_logger(self) -> bool:
        """
        Validate logger information.
        """
        if not isinstance(
            self.logger,
            str,
        ):
            return False

        if not self.logger.strip():
            return False

        return True
    # ------------------------------------------------------------------
    # Part 11. Statistics
    # ------------------------------------------------------------------

    def diagnostics(self) -> Dict[str, Any]:
        """
        Return detailed diagnostics information.
        """
        return {
            "id": self.id,
            "status": self.status.value,

            "level": self.level.value,
            "message_length": len(self.message),

            "logger": self.logger,
            "module": self.module,
            "function": self.function,
            "line": self.line,

            "timestamp": self.timestamp.isoformat(),

            "has_exception": self.has_exception(),

            "tag_count": self.tag_count,
            "attribute_count": self.attribute_count,

            "context": {
                "trace_id": self.context.trace_id,
                "span_id": self.context.span_id,
                "service": self.context.service,
                "environment": self.context.environment,
            },

            "validation": {
                "is_valid": self.is_valid(),
            },
        }


    def summary(self) -> Dict[str, Any]:
        """
        Return compact summary information.
        """
        return {
            "id": self.id,

            "level": self.level.value,

            "message": self.message,

            "logger": self.logger,

            "timestamp": self.timestamp.isoformat(),

            "status": self.status.value,

            "tags": self.tag_count,

            "attributes": self.attribute_count,

            "exception": self.has_exception(),
        }


    def runtime_statistics(self) -> Dict[str, Any]:
        """
        Return runtime-related statistics.
        """
        return {
            "created_at": self.metadata.created_at.isoformat(),

            "updated_at": self.metadata.updated_at.isoformat(),

            "age_seconds": (
                utc_now() - self.timestamp
            ).total_seconds(),

            "status": self.status.value,

            "thread_id": self.context.thread_id,

            "process_id": self.context.process_id,

            "hostname": self.context.hostname,

            "service": self.context.service,

            "environment": self.context.environment,
        }


    def memory_usage(self) -> Dict[str, int]:
        """
        Estimate memory usage of the log object.
        """
        import sys

        return {
            "object_bytes": sys.getsizeof(self),

            "message_bytes": sys.getsizeof(
                self.message
            ),

            "tags_bytes": sys.getsizeof(
                self.tags
            ),

            "attributes_bytes": sys.getsizeof(
                self.attributes
            ),

            "context_bytes": sys.getsizeof(
                self.context
            ),

            "metadata_bytes": sys.getsizeof(
                self.metadata
            ),
        }


    def field_statistics(self) -> Dict[str, Any]:
        """
        Return statistics for schema fields.
        """
        return {
            "fields": {
                "id": bool(self.id),

                "timestamp": self.timestamp is not None,

                "message": {
                    "length": len(self.message),
                    "empty": not bool(self.message),
                },

                "tags": {
                    "count": self.tag_count,
                    "limit": DEFAULT_MAX_TAGS,
                },

                "attributes": {
                    "count": self.attribute_count,
                    "limit": DEFAULT_MAX_ATTRIBUTES,
                },

                "exception": {
                    "attached": self.has_exception(),
                    "type": self.exception_type(),
                },
            }
        }


    def is_valid(self) -> bool:
        """
        Check whether this log record is valid.
        """
        try:
            return self.validate()

        except Exception:
            return False
    # ------------------------------------------------------------------
    # Part 12. Python Protocols
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        """
        Developer representation of LogSchema.
        """
        return (
            f"LogSchema("
            f"id='{self.id}', "
            f"level='{self.level.value}', "
            f"message='{self.message[:50]}', "
            f"logger='{self.logger}', "
            f"status='{self.status.value}'"
            f")"
        )


    def __str__(self) -> str:
        """
        Human-readable representation.
        """
        return (
            f"[{self.level.value}] "
            f"{self.logger}: "
            f"{self.message}"
        )


    def __len__(self) -> int:
        """
        Return total number of dynamic fields.
        """
        return (
            len(self.tags)
            + len(self.attributes)
            + len(self.metadata.extra)
        )


    def __iter__(self) -> Iterator[str]:
        """
        Iterate over serialized fields.
        """
        return iter(
            self.to_dict()
        )


    def __contains__(self, key: str) -> bool:
        """
        Check whether a field exists.
        """
        return key in self.to_dict()


    def __getitem__(self, key: str) -> Any:
        """
        Dictionary-style field access.
        """
        data = self.to_dict()

        if key not in data:
            raise KeyError(key)

        return data[key]


    def __setitem__(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Dictionary-style field update.
        """
        if key == "message":
            self.message = value

        elif key == "level":
            self.level = value

        elif key == "logger":
            self.logger = value

        elif key == "module":
            self.module = value

        elif key == "tags":
            self.tags = value

        elif key == "attributes":
            self.attributes = value

        elif key == "status":
            self.status = value

        else:
            self.metadata.extra[key] = value

        self.touch()


    def __copy__(self) -> "LogSchema":
        """
        Shallow copy protocol.
        """
        return copy.copy(self)


    def __deepcopy__(
        self,
        memo: Optional[Dict[int, Any]] = None,
    ) -> "LogSchema":
        """
        Deep copy protocol.
        """
        if memo is None:
            memo = {}

        cloned = type(self)(
            id=self.id,
            timestamp=self.timestamp,

            level=self.level,
            message=self.message,

            logger=self.logger,
            module=self.module,
            function=self.function,
            line=self.line,

            context=deep_copy(
                self.context
            ),

            metadata=deep_copy(
                self.metadata
            ),

            tags=deep_copy(
                self.tags
            ),

            attributes=deep_copy(
                self.attributes
            ),

            exception=self.exception,

            status=self.status,
        )

        memo[id(self)] = cloned

        return cloned


    def __hash__(self) -> int:
        """
        Hash protocol based on immutable identity.
        """
        return hash(
            self.id
        )


    def __eq__(
        self,
        other: object,
    ) -> bool:
        """
        Equality comparison protocol.
        """
        if not isinstance(
            other,
            LogSchema,
        ):
            return False

        return (
            self.id == other.id
            and self.timestamp == other.timestamp
            and self.level == other.level
            and self.message == other.message
            and self.logger == other.logger
            and self.module == other.module
            and self.tags == other.tags
            and self.attributes == other.attributes
        )
                                                                                                    
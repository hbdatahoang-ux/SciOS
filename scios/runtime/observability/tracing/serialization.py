# ==============================================================================
# SciOS Runtime Observability
# Trace Serialization
# ==============================================================================


# ==============================================================================
# Part 1. Module Header
# ==============================================================================

"""
SciOS Runtime Observability
===========================

Trace serialization layer.

Provides stable serialization primitives for traces, spans, contexts,
and tracing-related runtime payloads.

Python 3.11+
"""


# ==============================================================================
# Part 2. Imports
# ==============================================================================

from __future__ import annotations

import json

from dataclasses import (
    InitVar,
    asdict,
    dataclass,
    field,
    is_dataclass,
)

from enum import Enum

from typing import (
    Any,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    TypeAlias,
    TypeVar,
)


# ==============================================================================
# Part 3. Type Aliases
# ==============================================================================

T = TypeVar("T")


SerializableValue: TypeAlias = (
    None
    | bool
    | int
    | float
    | str
    | list[Any]
    | dict[str, Any]
)

SerializableMapping: TypeAlias = Mapping[str, Any]

MutableSerializableMapping: TypeAlias = MutableMapping[str, Any]

SerializableSequence: TypeAlias = Sequence[Any]

SerializedData: TypeAlias = dict[str, Any]

SerializedValue: TypeAlias = Any


# ==============================================================================
# Part 4. Constants
# ==============================================================================


# ==============================================================================
# Serialization identity
# ==============================================================================

SERIALIZATION_NAME = "trace-serialization"

SERIALIZATION_VERSION = "1.0"

SERIALIZATION_API_VERSION = SERIALIZATION_VERSION


# ==============================================================================
# Serialization formats
# ==============================================================================

SERIALIZATION_FORMAT_DICT = "dict"

SERIALIZATION_FORMAT_JSON = "json"

SUPPORTED_SERIALIZATION_FORMATS = (
    SERIALIZATION_FORMAT_DICT,
    SERIALIZATION_FORMAT_JSON,
)


# ==============================================================================
# Serialization object types
# ==============================================================================

TRACE_KEY = "trace"
SPAN_KEY = "span"
CONTEXT_KEY = "context"
MIDDLEWARE_KEY = "middleware"


# ==============================================================================
# Payload keys
# ==============================================================================

METADATA_KEY = "metadata"
ATTRIBUTES_KEY = "attributes"
EVENTS_KEY = "events"
LINKS_KEY = "links"
ERROR_KEY = "error"


# ==============================================================================
# Serialization envelope keys
# ==============================================================================

SERIALIZATION_VERSION_KEY = "version"
SERIALIZATION_TYPE_KEY = "type"
SERIALIZATION_FORMAT_KEY = "format"
SERIALIZATION_STATUS_KEY = "status"
SERIALIZATION_DIRECTION_KEY = "direction"
SERIALIZATION_MODE_KEY = "mode"
SERIALIZATION_DATA_KEY = "data"

DATA_KEY = SERIALIZATION_DATA_KEY


# ==============================================================================
# Compatibility metadata keys
# ==============================================================================

SERIALIZATION_METADATA_VERSION_KEY = "serialization_version"
SERIALIZATION_METADATA_TYPE_KEY = "serialization_type"


# ==============================================================================
# Semantic defaults
# ==============================================================================

SERIALIZATION_TYPE = TRACE_KEY
SERIALIZATION_STATUS = "created"
SERIALIZATION_DIRECTION = "encode"
SERIALIZATION_MODE = "strict"


# ==============================================================================
# Serialization defaults
# ==============================================================================

DEFAULT_SERIALIZATION_VERSION = SERIALIZATION_VERSION
DEFAULT_SERIALIZATION_FORMAT = SERIALIZATION_FORMAT_DICT
DEFAULT_SERIALIZATION_STATUS = SERIALIZATION_STATUS
DEFAULT_SERIALIZATION_DIRECTION = SERIALIZATION_DIRECTION
DEFAULT_SERIALIZATION_MODE = SERIALIZATION_MODE


# ==============================================================================
# JSON defaults
# ==============================================================================

DEFAULT_ENSURE_ASCII = False
DEFAULT_SORT_KEYS = True
DEFAULT_INDENT = None
DEFAULT_ALLOW_NON_FINITE = False


# ==============================================================================
# Object key aliases
# ==============================================================================

DEFAULT_TRACE_KEY = TRACE_KEY
DEFAULT_SPAN_KEY = SPAN_KEY
DEFAULT_CONTEXT_KEY = CONTEXT_KEY
DEFAULT_MIDDLEWARE_KEY = MIDDLEWARE_KEY


# ==============================================================================
# Part 5. Exceptions
# ==============================================================================


class SerializationError(Exception):
    """
    Base exception for tracing serialization failures.
    """


class SerializationTypeError(
    SerializationError,
    TypeError,
):
    """
    Raised when an unsupported or invalid value type is encountered.
    """


class SerializationValueError(
    SerializationError,
    ValueError,
):
    """
    Raised when serialized data contains an invalid value.
    """


class SerializationFormatError(
    SerializationError,
    ValueError,
):
    """
    Raised when an unsupported serialization format is requested.
    """


class SerializationDecodeError(
    SerializationError,
    ValueError,
):
    """
    Raised when serialized data cannot be decoded.
    """


class SerializationEncodeError(
    SerializationError,
    ValueError,
):
    """
    Raised when an object cannot be encoded.
    """


class SerializationValidationError(
    SerializationError,
    ValueError,
):
    """
    Raised when serialized payload validation fails.
    """


# ==============================================================================
# Part 6. Serialization Enums
# ==============================================================================


class SerializationFormat(str, Enum):
    """
    Supported serialization formats.
    """

    DICT = SERIALIZATION_FORMAT_DICT
    JSON = SERIALIZATION_FORMAT_JSON


class SerializationType(str, Enum):
    """
    Supported tracing serialization object types.
    """

    TRACE = TRACE_KEY
    SPAN = SPAN_KEY
    CONTEXT = CONTEXT_KEY
    MIDDLEWARE = MIDDLEWARE_KEY


class SerializationStatus(str, Enum):
    """
    Serialization operation status.
    """

    CREATED = "created"
    ENCODED = "encoded"
    DECODED = "decoded"
    VALIDATED = "validated"
    FAILED = "failed"


class SerializationDirection(str, Enum):
    """
    Direction of a serialization operation.
    """

    ENCODE = "encode"
    DECODE = "decode"


class SerializationMode(str, Enum):
    """
    Serialization operation mode.
    """

    STRICT = "strict"
    PERMISSIVE = "permissive"


# ------------------------------------------------------------------------------
# Public enum defaults
# ------------------------------------------------------------------------------

DEFAULT_FORMAT: SerializationFormat = (
    SerializationFormat.DICT
)

DEFAULT_STATUS: SerializationStatus = (
    SerializationStatus.CREATED
)

DEFAULT_DIRECTION: SerializationDirection = (
    SerializationDirection.ENCODE
)

DEFAULT_MODE: SerializationMode = (
    SerializationMode.STRICT
)


# ==============================================================================
# Part 7. Serialization Dataclasses
# ==============================================================================


@dataclass
class SerializationMetadata:
    """Metadata describing a serialization operation."""

    serialization_version: str = SERIALIZATION_VERSION
    serialization_type: SerializationType = SerializationType.TRACE
    serialization_format: SerializationFormat = DEFAULT_FORMAT
    status: SerializationStatus = DEFAULT_STATUS
    direction: SerializationDirection = DEFAULT_DIRECTION
    mode: SerializationMode = DEFAULT_MODE


@dataclass
class SerializationResult:
    """Result produced by a serialization operation."""

    data: SerializedData = field(
        default_factory=dict,
    )

    metadata: SerializationMetadata = field(
        default_factory=SerializationMetadata,
    )

    @property
    def value(self) -> SerializedData:
        """Return a defensive copy of serialized data."""

        return _deep_copy_mapping(
            self.data,
        )


@dataclass
class TracePayload:
    """
    Generic trace serialization payload.

    The public ``payload`` field is stored as a normal dataclass field so
    ``dataclasses.asdict()`` preserves the public schema.

    Every read of ``payload`` returns a defensive deep copy, preventing
    external mutation of the internal payload.
    """

    serialization_version: str = SERIALIZATION_VERSION

    serialization_type: SerializationType = (
        SerializationType.TRACE
    )

    payload: SerializedData = field(
        default_factory=dict,
    )

    def __post_init__(self) -> None:
        # ------------------------------------------------------------------
        # serialization_version
        # ------------------------------------------------------------------

        if not isinstance(
            self.serialization_version,
            str,
        ):
            raise SerializationTypeError(
                "serialization_version must be a string",
            )

        # ------------------------------------------------------------------
        # serialization_type
        # ------------------------------------------------------------------

        try:
            object.__setattr__(
                self,
                "serialization_type",
                SerializationType(
                    self.serialization_type,
                ),
            )
        except (
            ValueError,
            TypeError,
        ) as exc:
            raise SerializationTypeError(
                "invalid serialization_type",
            ) from exc

        # ------------------------------------------------------------------
        # payload
        # ------------------------------------------------------------------

        if not isinstance(
            self.payload,
            Mapping,
        ):
            raise SerializationTypeError(
                "payload must be a mapping",
            )

        # ``self.payload`` here is already a defensive copy because
        # __getattribute__() handles public payload access.
        #
        # Store an independent canonical copy explicitly.
        object.__setattr__(
            self,
            "payload",
            _deep_copy_mapping(
                object.__getattribute__(
                    self,
                    "payload",
                ),
            ),
        )

    def __getattribute__(
        self,
        name: str,
    ) -> Any:
        """
        Return a defensive copy whenever ``payload`` is accessed.

        This is intentionally implemented at attribute-access level so
        dataclasses.asdict() still sees ``payload`` as a real dataclass
        field while callers never receive the internal dictionary.
        """

        if name == "payload":
            raw_payload = object.__getattribute__(
                self,
                "__dict__",
            ).get(
                "payload",
            )

            if raw_payload is None:
                return None

            return _deep_copy_mapping(
                raw_payload,
            )

        return object.__getattribute__(
            self,
            name,
        )

    def __setattr__(
        self,
        name: str,
        value: Any,
    ) -> None:
        """
        Defensively copy payload assignments.
        """

        if name == "payload":
            if not isinstance(
                value,
                Mapping,
            ):
                raise SerializationTypeError(
                    "payload must be a mapping",
                )

            object.__setattr__(
                self,
                name,
                _deep_copy_mapping(
                    value,
                ),
            )

            return

        object.__setattr__(
            self,
            name,
            value,
        )

    def to_dict(self) -> SerializedData:
        """
        Return the canonical serialized representation.
        """

        raw_payload = object.__getattribute__(
            self,
            "__dict__",
        ).get(
            "payload",
        )

        return {
            SERIALIZATION_VERSION_KEY: (
                self.serialization_version
            ),
            SERIALIZATION_TYPE_KEY: (
                self.serialization_type.value
            ),
            "payload": _deep_copy_mapping(
                raw_payload,
            ),
        }

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "TracePayload":
        """
        Create a TracePayload from serialized data.
        """

        if not isinstance(
            data,
            Mapping,
        ):
            raise SerializationTypeError(
                "payload must be a mapping",
            )

        # ------------------------------------------------------------------
        # Version
        # ------------------------------------------------------------------

        version = data.get(
            SERIALIZATION_VERSION_KEY,
            SERIALIZATION_VERSION,
        )

        # ------------------------------------------------------------------
        # Type
        # ------------------------------------------------------------------

        serialization_type = data.get(
            SERIALIZATION_TYPE_KEY,
            data.get(
                SERIALIZATION_METADATA_TYPE_KEY,
                SerializationType.TRACE.value,
            ),
        )

        # ------------------------------------------------------------------
        # Canonical payload
        # ------------------------------------------------------------------

        payload = data.get(
            "payload",
        )

        # ------------------------------------------------------------------
        # Compatibility data field
        # ------------------------------------------------------------------

        if payload is None:
            payload = data.get(
                SERIALIZATION_DATA_KEY,
            )

        # ------------------------------------------------------------------
        # Legacy flat representation
        # ------------------------------------------------------------------

        if payload is None:
            payload = {
                key: value
                for key, value in data.items()
                if key not in {
                    SERIALIZATION_VERSION_KEY,
                    SERIALIZATION_TYPE_KEY,
                    SERIALIZATION_METADATA_VERSION_KEY,
                    SERIALIZATION_METADATA_TYPE_KEY,
                    SERIALIZATION_FORMAT_KEY,
                    SERIALIZATION_STATUS_KEY,
                    SERIALIZATION_DIRECTION_KEY,
                    SERIALIZATION_MODE_KEY,
                }
            }

        if not isinstance(
            payload,
            Mapping,
        ):
            raise SerializationTypeError(
                "serialized payload data must be a mapping",
            )

        return cls(
            serialization_version=version,
            serialization_type=serialization_type,
            payload=payload,
        )

    def copy(self) -> "TracePayload":
        """
        Return an independent deep copy.
        """

        raw_payload = object.__getattribute__(
            self,
            "__dict__",
        ).get(
            "payload",
        )

        return TracePayload(
            serialization_version=(
                self.serialization_version
            ),
            serialization_type=(
                self.serialization_type
            ),
            payload=_deep_copy_mapping(
                raw_payload,
            ),
        )

    def to_json(
        self,
        *,
        ensure_ascii: bool = DEFAULT_ENSURE_ASCII,
        sort_keys: bool = DEFAULT_SORT_KEYS,
        indent: Optional[int] = DEFAULT_INDENT,
    ) -> str:
        """
        Serialize the payload to JSON.
        """

        return serialize_json(
            self.to_dict(),
            ensure_ascii=ensure_ascii,
            sort_keys=sort_keys,
            indent=indent,
        )

# ==============================================================================
# Part 8. Base Serialization Helpers
# ==============================================================================


def _serialize_value(
    value: Any,
) -> Any:
    """
    Convert a Python value into a serialization-safe representation.

    Supported values include:

    - None
    - bool
    - int
    - float
    - str
    - Enum
    - Mapping
    - list / tuple / set / frozenset
    - dataclass
    - objects exposing ``to_dict()``
    - ordinary objects exposing ``__dict__``
    """

    # ------------------------------------------------------------------
    # Primitive values
    # ------------------------------------------------------------------

    if value is None:
        return None

    if isinstance(
        value,
        (str, int, float, bool),
    ):
        return value

    # ------------------------------------------------------------------
    # Enum
    # ------------------------------------------------------------------

    if isinstance(
        value,
        Enum,
    ):
        return _serialize_value(
            value.value,
        )

    # ------------------------------------------------------------------
    # Mapping
    # ------------------------------------------------------------------

    if isinstance(
        value,
        Mapping,
    ):
        return {
            str(key): _serialize_value(item)
            for key, item in value.items()
        }

    # ------------------------------------------------------------------
    # Sequence / set
    # ------------------------------------------------------------------

    if isinstance(
        value,
        (list, tuple, set, frozenset),
    ):
        return [
            _serialize_value(item)
            for item in value
        ]

    # ------------------------------------------------------------------
    # Dataclass
    # ------------------------------------------------------------------

    if is_dataclass(value):
        try:
            return _serialize_value(
                asdict(value),
            )
        except Exception as exc:
            raise SerializationEncodeError(
                "failed to serialize "
                f"{type(value).__name__}",
            ) from exc

    # ------------------------------------------------------------------
    # Explicit object serializer
    # ------------------------------------------------------------------

    if hasattr(
        value,
        "to_dict",
    ):
        try:
            result = value.to_dict()
        except Exception as exc:
            raise SerializationEncodeError(
                "failed to serialize "
                f"{type(value).__name__}",
            ) from exc

        if not isinstance(
            result,
            Mapping,
        ):
            raise SerializationEncodeError(
                f"{type(value).__name__}.to_dict() "
                "must return a mapping",
            )

        return {
            str(key): _serialize_value(item)
            for key, item in result.items()
        }

    # ------------------------------------------------------------------
    # Generic Python object
    # ------------------------------------------------------------------

    if hasattr(
        value,
        "__dict__",
    ):
        return {
            str(key): _serialize_value(item)
            for key, item in vars(value).items()
            if not str(key).startswith("_")
        }

    # ------------------------------------------------------------------
    # Unsupported
    # ------------------------------------------------------------------

    raise SerializationTypeError(
        "unsupported value type: "
        f"{type(value).__name__}",
    )


def _deep_copy_mapping(
    data: Mapping[str, Any],
) -> SerializedData:
    """
    Create a recursive serialization-safe defensive copy.
    """

    if not isinstance(
        data,
        Mapping,
    ):
        raise SerializationTypeError(
            "data must be a mapping",
        )

    result = _serialize_value(
        data,
    )

    if not isinstance(
        result,
        dict,
    ):
        raise SerializationTypeError(
            "serialized mapping must produce a dict",
        )

    return result


def _serialize_object(
    value: Any,
    *,
    object_type: SerializationType,
) -> SerializedData:
    """
    Serialize an object using the tracing serialization envelope.

    Both canonical envelope fields and compatibility
    ``serialization_*`` aliases are emitted.
    """

    data = _serialize_value(
        value,
    )

    if not isinstance(
        data,
        Mapping,
    ):
        raise SerializationEncodeError(
            f"{object_type.value} must serialize "
            "to a mapping",
        )

    result: SerializedData = {
        # Canonical envelope.
        SERIALIZATION_VERSION_KEY: (
            SERIALIZATION_VERSION
        ),
        SERIALIZATION_TYPE_KEY: (
            object_type.value
        ),

        # Compatibility envelope.
        SERIALIZATION_METADATA_VERSION_KEY: (
            SERIALIZATION_VERSION
        ),
        SERIALIZATION_METADATA_TYPE_KEY: (
            object_type.value
        ),
    }

    for key, item in data.items():
        key = str(key)

        # Prevent user data from overwriting envelope metadata.
        if key in {
            SERIALIZATION_VERSION_KEY,
            SERIALIZATION_TYPE_KEY,
            SERIALIZATION_METADATA_VERSION_KEY,
            SERIALIZATION_METADATA_TYPE_KEY,
        }:
            continue

        result[key] = item

    return result


def _strip_serialization_metadata(
    data: Mapping[str, Any],
) -> SerializedData:
    """
    Remove serialization envelope fields before returning payload data.
    """

    metadata_keys = {
        SERIALIZATION_VERSION_KEY,
        SERIALIZATION_TYPE_KEY,
        SERIALIZATION_METADATA_VERSION_KEY,
        SERIALIZATION_METADATA_TYPE_KEY,
        SERIALIZATION_FORMAT_KEY,
        SERIALIZATION_STATUS_KEY,
        SERIALIZATION_DIRECTION_KEY,
        SERIALIZATION_MODE_KEY,
    }

    return {
        str(key): _serialize_value(value)
        for key, value in data.items()
        if str(key) not in metadata_keys
    }


def _deserialize_mapping(
    data: Mapping[str, Any] | str,
    object_type: SerializationType,
) -> SerializedData:
    """
    Validate and decode serialized mapping data.

    JSON strings are accepted here as a convenience so that:

        deserialize_trace(json_string)

    works without explicitly passing ``format=JSON``.
    """

    # ------------------------------------------------------------------
    # JSON input
    # ------------------------------------------------------------------

    if isinstance(
        data,
        str,
    ):
        data = deserialize_json(
            data,
        )

    # ------------------------------------------------------------------
    # Mapping validation
    # ------------------------------------------------------------------

    if not isinstance(
        data,
        Mapping,
    ):
        raise SerializationDecodeError(
            f"{object_type.value} data must be a mapping",
        )

    # ------------------------------------------------------------------
    # Serialization validation
    # ------------------------------------------------------------------

    validate_serialized_data(
        data,
        expected_type=object_type,
    )

    # ------------------------------------------------------------------
    # Remove envelope
    # ------------------------------------------------------------------

    return _strip_serialization_metadata(
        data,
    )


# ==============================================================================
# Part 9. TraceSerializer
# ==============================================================================


class TraceSerializer:
    """Serialize trace objects."""

    serialization_type = SerializationType.TRACE

    def serialize(
        self,
        trace: Any,
        *,
        format: SerializationFormat = DEFAULT_FORMAT,
    ) -> SerializedData | str:
        if trace is None:
            raise SerializationValueError(
                "trace cannot be None",
            )

        data = _serialize_object(
            trace,
            object_type=self.serialization_type,
        )

        if SerializationFormat(format) is SerializationFormat.JSON:
            return serialize_json(data)

        if SerializationFormat(format) is not SerializationFormat.DICT:
            raise SerializationFormatError(
                f"unsupported serialization format: {format!r}",
            )

        return data

    def deserialize(
        self,
        data: Mapping[str, Any] | str,
        *,
        format: SerializationFormat = DEFAULT_FORMAT,
    ) -> SerializedData:
        """
        Deserialize trace/span/context/middleware data.

        JSON input is automatically decoded when ``data`` is a string.
        """

        if isinstance(data, str):
            format = SerializationFormat.JSON

        if SerializationFormat(format) is SerializationFormat.JSON:
            data = deserialize_json(data)

        elif SerializationFormat(format) is not SerializationFormat.DICT:
            raise SerializationFormatError(
                f"unsupported serialization format: {format!r}",
            )

        return _deserialize_mapping(
            data,
            self.serialization_type,
        )

    def to_dict(
        self,
        trace: Any,
    ) -> SerializedData:
        return self.serialize(
            trace,
            format=SerializationFormat.DICT,
        )

    def from_dict(
        self,
        data: Mapping[str, Any],
    ) -> SerializedData:
        return self.deserialize(
            data,
            format=SerializationFormat.DICT,
        )

    def to_json(
        self,
        trace: Any,
        *,
        ensure_ascii: bool = DEFAULT_ENSURE_ASCII,
        sort_keys: bool = DEFAULT_SORT_KEYS,
        indent: Optional[int] = DEFAULT_INDENT,
    ) -> str:
        return serialize_json(
            self.to_dict(trace),
            ensure_ascii=ensure_ascii,
            sort_keys=sort_keys,
            indent=indent,
        )

    def from_json(
        self,
        data: str,
    ) -> SerializedData:
        return self.deserialize(
            data,
            format=SerializationFormat.JSON,
        )


# ==============================================================================
# Part 10. SpanSerializer
# ==============================================================================


class SpanSerializer(TraceSerializer):
    """Serialize span objects."""

    serialization_type = SerializationType.SPAN


# ==============================================================================
# Part 11. ContextSerializer
# ==============================================================================


class ContextSerializer(TraceSerializer):
    """Serialize trace context objects."""

    serialization_type = SerializationType.CONTEXT


# ==============================================================================
# Part 12. MiddlewareSerializer
# ==============================================================================


class MiddlewareSerializer(TraceSerializer):
    """Serialize tracing middleware state."""

    serialization_type = SerializationType.MIDDLEWARE


# ==============================================================================
# Part 13. Module-Level Object Serialization API
# ==============================================================================


def serialize_trace(
    trace: Any,
    *,
    format: SerializationFormat = DEFAULT_FORMAT,
) -> SerializedData | str:
    """Serialize a trace object."""

    return DEFAULT_TRACE_SERIALIZER.serialize(
        trace,
        format=format,
    )


def deserialize_trace(
    data: Mapping[str, Any] | str,
    *,
    format: SerializationFormat = DEFAULT_FORMAT,
) -> SerializedData:
    """Deserialize trace data."""

    return DEFAULT_TRACE_SERIALIZER.deserialize(
        data,
        format=format,
    )


def serialize_span(
    span: Any,
    *,
    format: SerializationFormat = DEFAULT_FORMAT,
) -> SerializedData | str:
    """Serialize a span object."""

    return DEFAULT_SPAN_SERIALIZER.serialize(
        span,
        format=format,
    )


def deserialize_span(
    data: Mapping[str, Any] | str,
    *,
    format: SerializationFormat = DEFAULT_FORMAT,
) -> SerializedData:
    """Deserialize span data."""

    return DEFAULT_SPAN_SERIALIZER.deserialize(
        data,
        format=format,
    )


def serialize_context(
    context: Any,
    *,
    format: SerializationFormat = DEFAULT_FORMAT,
) -> SerializedData | str:
    """Serialize a trace context."""

    return DEFAULT_CONTEXT_SERIALIZER.serialize(
        context,
        format=format,
    )


def deserialize_context(
    data: Mapping[str, Any] | str,
    *,
    format: SerializationFormat = DEFAULT_FORMAT,
) -> SerializedData:
    """Deserialize trace context data."""

    return DEFAULT_CONTEXT_SERIALIZER.deserialize(
        data,
        format=format,
    )


def serialize_middleware(
    middleware: Any,
    *,
    format: SerializationFormat = DEFAULT_FORMAT,
) -> SerializedData | str:
    """Serialize tracing middleware."""

    return DEFAULT_MIDDLEWARE_SERIALIZER.serialize(
        middleware,
        format=format,
    )


def deserialize_middleware(
    data: Mapping[str, Any] | str,
    *,
    format: SerializationFormat = DEFAULT_FORMAT,
) -> SerializedData:
    """Deserialize middleware data."""

    return DEFAULT_MIDDLEWARE_SERIALIZER.deserialize(
        data,
        format=format,
    )


# ==============================================================================
# Part 14. TracePayload Helper
# ==============================================================================


def serialize_trace_payload(
    *,
    trace: Any = None,
    span: Any = None,
    context: Any = None,
    middleware: Any = None,
    metadata: Optional[Mapping[str, Any]] = None,
    attributes: Optional[Mapping[str, Any]] = None,
) -> TracePayload:
    """Create a TracePayload from tracing objects."""

    payload: SerializedData = {}

    if trace is not None:
        payload[TRACE_KEY] = serialize_trace(trace)

    if span is not None:
        payload[SPAN_KEY] = serialize_span(span)

    if context is not None:
        payload[CONTEXT_KEY] = serialize_context(context)

    if middleware is not None:
        payload[MIDDLEWARE_KEY] = serialize_middleware(
            middleware,
        )

    if metadata is not None:
        payload[METADATA_KEY] = _deep_copy_mapping(
            metadata,
        )

    if attributes is not None:
        payload[ATTRIBUTES_KEY] = _deep_copy_mapping(
            attributes,
        )

    return TracePayload(
        serialization_version=SERIALIZATION_VERSION,
        serialization_type=SerializationType.TRACE,
        payload=payload,
    )


# ==============================================================================
# Part 15. JSON Helpers
# ==============================================================================


def serialize_json(
    data: Mapping[str, Any],
    *,
    ensure_ascii: bool = DEFAULT_ENSURE_ASCII,
    sort_keys: bool = DEFAULT_SORT_KEYS,
    indent: Optional[int] = DEFAULT_INDENT,
) -> str:
    """Serialize mapping data to JSON."""

    if not isinstance(data, Mapping):
        raise SerializationTypeError(
            "data must be a mapping",
        )

    normalized = _deep_copy_mapping(data)

    try:
        return json.dumps(
            normalized,
            ensure_ascii=ensure_ascii,
            sort_keys=sort_keys,
            indent=indent,
            allow_nan=DEFAULT_ALLOW_NON_FINITE,
        )
    except (
        TypeError,
        ValueError,
    ) as exc:
        raise SerializationEncodeError(
            "failed to encode JSON",
        ) from exc


def deserialize_json(
    data: str,
) -> SerializedData:
    """Deserialize JSON into a mapping."""

    if not isinstance(data, str):
        raise SerializationTypeError(
            "JSON data must be a string",
        )

    try:
        result = json.loads(data)
    except json.JSONDecodeError as exc:
        raise SerializationDecodeError(
            "invalid JSON data",
        ) from exc

    if not isinstance(result, Mapping):
        raise SerializationDecodeError(
            "JSON root must be a mapping",
        )

    return _deep_copy_mapping(result)


def to_json(
    data: Mapping[str, Any],
    *,
    ensure_ascii: bool = DEFAULT_ENSURE_ASCII,
    sort_keys: bool = DEFAULT_SORT_KEYS,
    indent: Optional[int] = DEFAULT_INDENT,
) -> str:
    """Compatibility alias for ``serialize_json``."""

    return serialize_json(
        data,
        ensure_ascii=ensure_ascii,
        sort_keys=sort_keys,
        indent=indent,
    )


def from_json(
    data: str,
) -> SerializedData:
    """Compatibility alias for ``deserialize_json``."""

    return deserialize_json(data)


# ==============================================================================
# Part 16. Validation
# ==============================================================================


def validate_serialized_data(
    data: Mapping[str, Any],
    *,
    expected_type: Optional[SerializationType] = None,
) -> bool:
    """Validate serialized mapping data."""

    if not isinstance(data, Mapping):
        raise SerializationValidationError(
            "serialized data must be a mapping",
        )

    version = data.get(
        SERIALIZATION_VERSION_KEY,
        data.get("serialization_version"),
    )

    if version is not None and not isinstance(
        version,
        str,
    ):
        raise SerializationValidationError(
            "serialization version must be a string",
        )

    declared_type = data.get(
        SERIALIZATION_TYPE_KEY,
        data.get("serialization_type"),
    )

    if declared_type is not None:
        try:
            declared_type = SerializationType(
                declared_type,
            )
        except (
            ValueError,
            TypeError,
        ) as exc:
            raise SerializationValidationError(
                f"unknown serialization type: {declared_type!r}",
            ) from exc

    if expected_type is not None:
        if declared_type != expected_type:
            raise SerializationValidationError(
                "serialization type mismatch: "
                f"expected {expected_type.value!r}, "
                f"got {getattr(declared_type, 'value', declared_type)!r}",
            )

    return True


def copy_serialized_data(
    data: Mapping[str, Any],
) -> SerializedData:
    """Create a defensive copy."""

    return _deep_copy_mapping(data)


def get_serialization_type(
    data: Mapping[str, Any],
) -> Optional[SerializationType]:
    """Return the declared serialization type."""

    if not isinstance(data, Mapping):
        raise SerializationTypeError(
            "data must be a mapping",
        )

    value = data.get(
        SERIALIZATION_TYPE_KEY,
        data.get("serialization_type"),
    )

    if value is None:
        return None

    try:
        return SerializationType(value)
    except (
        ValueError,
        TypeError,
    ) as exc:
        raise SerializationValueError(
            f"unknown serialization type: {value!r}",
        ) from exc


# ==============================================================================
# Part 17. Default Serializers
# ==============================================================================


DEFAULT_TRACE_SERIALIZER = TraceSerializer()

DEFAULT_SPAN_SERIALIZER = SpanSerializer()

DEFAULT_CONTEXT_SERIALIZER = ContextSerializer()

DEFAULT_MIDDLEWARE_SERIALIZER = MiddlewareSerializer()


# ==============================================================================
# Part 18. Public API
# ==============================================================================


__all__ = [
    # Type aliases
    "T",
    "SerializableValue",
    "SerializableMapping",
    "MutableSerializableMapping",
    "SerializableSequence",
    "SerializedData",
    "SerializedValue",

    # Dataclasses
    "SerializationMetadata",
    "SerializationResult",
    "TracePayload",

    # Serializers
    "TraceSerializer",
    "SpanSerializer",
    "ContextSerializer",
    "MiddlewareSerializer",

    # Public functions
    "serialize_trace",
    "deserialize_trace",
    "serialize_span",
    "deserialize_span",
    "serialize_context",
    "deserialize_context",
    "serialize_middleware",
    "deserialize_middleware",
    "serialize_trace_payload",

    # JSON
    "serialize_json",
    "deserialize_json",
    "to_json",
    "from_json",

    # Validation/helpers
    "validate_serialized_data",
    "copy_serialized_data",
    "get_serialization_type",

    # Default serializers
    "DEFAULT_TRACE_SERIALIZER",
    "DEFAULT_SPAN_SERIALIZER",
    "DEFAULT_CONTEXT_SERIALIZER",
    "DEFAULT_MIDDLEWARE_SERIALIZER",

    # Exceptions
    "SerializationError",
    "SerializationTypeError",
    "SerializationValueError",
    "SerializationFormatError",
    "SerializationDecodeError",
    "SerializationEncodeError",
    "SerializationValidationError",

    # Enums
    "SerializationFormat",
    "SerializationType",
    "SerializationStatus",
    "SerializationDirection",
    "SerializationMode",

    # Identity
    "SERIALIZATION_NAME",
    "SERIALIZATION_VERSION",
    "SERIALIZATION_API_VERSION",

    # Formats
    "SERIALIZATION_FORMAT_DICT",
    "SERIALIZATION_FORMAT_JSON",
    "SUPPORTED_SERIALIZATION_FORMATS",

    # Types
    "SERIALIZATION_TYPE",
    "TRACE_KEY",
    "SPAN_KEY",
    "CONTEXT_KEY",
    "MIDDLEWARE_KEY",

    # Payload keys
    "METADATA_KEY",
    "ATTRIBUTES_KEY",
    "EVENTS_KEY",
    "LINKS_KEY",
    "ERROR_KEY",

    # Envelope
    "SERIALIZATION_VERSION_KEY",
    "SERIALIZATION_TYPE_KEY",
    "SERIALIZATION_FORMAT_KEY",
    "SERIALIZATION_STATUS_KEY",
    "SERIALIZATION_DIRECTION_KEY",
    "SERIALIZATION_MODE_KEY",
    "SERIALIZATION_DATA_KEY",
    "DATA_KEY",

    # Compatibility metadata
    "SERIALIZATION_METADATA_VERSION_KEY",
    "SERIALIZATION_METADATA_TYPE_KEY",

    # Defaults
    "SERIALIZATION_STATUS",
    "SERIALIZATION_DIRECTION",
    "SERIALIZATION_MODE",
    "DEFAULT_SERIALIZATION_VERSION",
    "DEFAULT_SERIALIZATION_FORMAT",
    "DEFAULT_SERIALIZATION_STATUS",
    "DEFAULT_SERIALIZATION_DIRECTION",
    "DEFAULT_SERIALIZATION_MODE",

    # JSON defaults
    "DEFAULT_ENSURE_ASCII",
    "DEFAULT_SORT_KEYS",
    "DEFAULT_INDENT",
    "DEFAULT_ALLOW_NON_FINITE",

    # Key aliases
    "DEFAULT_TRACE_KEY",
    "DEFAULT_SPAN_KEY",
    "DEFAULT_CONTEXT_KEY",
    "DEFAULT_MIDDLEWARE_KEY",

    # Enum defaults
    "DEFAULT_FORMAT",
    "DEFAULT_STATUS",
    "DEFAULT_DIRECTION",
    "DEFAULT_MODE",
]

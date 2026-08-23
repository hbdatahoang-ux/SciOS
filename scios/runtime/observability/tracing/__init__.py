# ==============================================================================
# SciOS Runtime Observability
# Tracing Package
# ==============================================================================

"""
SciOS Runtime Observability
===========================

Tracing package public API.

Python 3.11+
"""

from .serialization import (
    # Dataclasses
    SerializationMetadata,
    SerializationResult,
    TracePayload,

    # Serializers
    TraceSerializer,
    SpanSerializer,
    ContextSerializer,
    MiddlewareSerializer,

    # Serialization functions
    serialize_trace,
    deserialize_trace,
    serialize_span,
    deserialize_span,
    serialize_context,
    deserialize_context,
    serialize_middleware,
    deserialize_middleware,
    serialize_trace_payload,

    # JSON
    serialize_json,
    deserialize_json,
    to_json,
    from_json,

    # Validation / helpers
    validate_serialized_data,
    copy_serialized_data,
    get_serialization_type,

    # Default serializers
    DEFAULT_TRACE_SERIALIZER,
    DEFAULT_SPAN_SERIALIZER,
    DEFAULT_CONTEXT_SERIALIZER,
    DEFAULT_MIDDLEWARE_SERIALIZER,

    # Exceptions
    SerializationError,
    SerializationTypeError,
    SerializationValueError,
    SerializationFormatError,
    SerializationDecodeError,
    SerializationEncodeError,
    SerializationValidationError,

    # Enums
    SerializationFormat,
    SerializationType,
    SerializationStatus,
    SerializationDirection,
    SerializationMode,
)


__all__ = [
    # Dataclasses
    "SerializationMetadata",
    "SerializationResult",
    "TracePayload",

    # Serializers
    "TraceSerializer",
    "SpanSerializer",
    "ContextSerializer",
    "MiddlewareSerializer",

    # Serialization functions
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

    # Validation / helpers
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
]

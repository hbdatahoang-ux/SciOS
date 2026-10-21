# ==============================================================================
# test_serialization.py
# ==============================================================================

"""
Tests for tracing serialization.

Python 3.11+
"""

from __future__ import annotations

# ==============================================================================
# Part 1. Imports
# ==============================================================================

import json
from dataclasses import asdict, is_dataclass
from typing import Any

import pytest

from scios.runtime.observability.tracing.serialization import (
    DEFAULT_SERIALIZATION_VERSION,
    SERIALIZATION_VERSION,
    SerializationError,
    SerializationFormat,
    SerializationType,
    SerializationValidationError,
    TraceSerializer,
    SpanSerializer,
    ContextSerializer,
    MiddlewareSerializer,
    TracePayload,
    serialize_trace,
    serialize_span,
    serialize_context,
    serialize_middleware,
    deserialize_trace,
    deserialize_span,
    deserialize_context,
    deserialize_middleware,
)


try:
    from scios.runtime.observability.tracing.trace import Trace
except ImportError:
    Trace = Any

try:
    from scios.runtime.observability.tracing.span import Span
except ImportError:
    Span = Any

try:
    from scios.runtime.observability.tracing.context import TraceContext
except ImportError:
    TraceContext = Any

try:
    from scios.runtime.observability.tracing.middleware import (
        TraceMiddleware,
        MiddlewareConfig,
    )
except ImportError:
    TraceMiddleware = Any
    MiddlewareConfig = Any


# ==============================================================================
# Part 2. Fixtures
# ==============================================================================


@pytest.fixture
def trace_payload() -> TracePayload:
    return TracePayload(
        serialization_version=SERIALIZATION_VERSION,
        serialization_type=SerializationType.TRACE,
        payload={
            "name": "test-trace",
            "trace_id": "trace-123",
            "service_name": "scios",
        },
    )


@pytest.fixture
def trace_serializer() -> TraceSerializer:
    return TraceSerializer()


@pytest.fixture
def span_serializer() -> SpanSerializer:
    return SpanSerializer()


@pytest.fixture
def context_serializer() -> ContextSerializer:
    return ContextSerializer()


@pytest.fixture
def middleware_serializer() -> MiddlewareSerializer:
    return MiddlewareSerializer()


@pytest.fixture
def sample_trace() -> Any:
    try:
        return Trace(
            name="test-trace",
            trace_id="trace-123",
            service_name="scios",
        )
    except Exception:
        return {
            "name": "test-trace",
            "trace_id": "trace-123",
            "service_name": "scios",
        }


@pytest.fixture
def sample_span() -> Any:
    try:
        return Span(
            name="test-span",
            span_id="span-123",
            trace_id="trace-123",
        )
    except Exception:
        return {
            "name": "test-span",
            "span_id": "span-123",
            "trace_id": "trace-123",
        }


@pytest.fixture
def sample_context() -> Any:
    try:
        return TraceContext(
            trace_id="trace-123",
            span_id="span-123",
        )
    except Exception:
        return {
            "trace_id": "trace-123",
            "span_id": "span-123",
        }


@pytest.fixture
def sample_middleware() -> Any:
    try:
        return TraceMiddleware()
    except Exception:
        return {
            "name": "tracing",
            "enabled": True,
        }


# ==============================================================================
# Part 3. Constants Tests
# ==============================================================================


def test_serialization_version_exists() -> None:
    assert SERIALIZATION_VERSION
    assert isinstance(SERIALIZATION_VERSION, str)


def test_default_serialization_version() -> None:
    assert DEFAULT_SERIALIZATION_VERSION
    assert isinstance(DEFAULT_SERIALIZATION_VERSION, str)


def test_serialization_versions_are_consistent() -> None:
    assert SERIALIZATION_VERSION == DEFAULT_SERIALIZATION_VERSION


# ==============================================================================
# Part 4. Enum Tests
# ==============================================================================


def test_serialization_format_members() -> None:
    assert SerializationFormat.JSON.value == "json"


def test_serialization_type_members() -> None:
    assert SerializationType.TRACE.value == "trace"
    assert SerializationType.SPAN.value == "span"
    assert SerializationType.CONTEXT.value == "context"
    assert SerializationType.MIDDLEWARE.value == "middleware"


def test_serialization_format_is_string_enum() -> None:
    assert isinstance(SerializationFormat.JSON, str)


def test_serialization_type_is_string_enum() -> None:
    assert isinstance(SerializationType.TRACE, str)


# ==============================================================================
# Part 5. Dataclass Tests
# ==============================================================================


def test_trace_payload_is_dataclass(
    trace_payload: TracePayload,
) -> None:
    assert is_dataclass(trace_payload)


def test_trace_payload_fields(
    trace_payload: TracePayload,
) -> None:
    assert trace_payload.serialization_version == SERIALIZATION_VERSION
    assert trace_payload.serialization_type == SerializationType.TRACE
    assert trace_payload.payload["name"] == "test-trace"


def test_trace_payload_to_dict(
    trace_payload: TracePayload,
) -> None:
    result = asdict(trace_payload)

    assert isinstance(result, dict)
    assert "serialization_version" in result
    assert "serialization_type" in result
    assert "payload" in result


def test_trace_payload_payload_is_defensive(
    trace_payload: TracePayload,
) -> None:
    payload = trace_payload.payload

    payload["new"] = "value"

    assert "new" not in trace_payload.payload


# ==============================================================================
# Part 6. TraceSerializer Tests
# ==============================================================================


def test_trace_serializer_creation(
    trace_serializer: TraceSerializer,
) -> None:
    assert isinstance(trace_serializer, TraceSerializer)


def test_trace_serializer_serializes_mapping(
    trace_serializer: TraceSerializer,
) -> None:
    source = {
        "name": "test-trace",
        "trace_id": "trace-123",
    }

    result = trace_serializer.serialize(source)

    assert isinstance(result, dict)
    assert result["name"] == "test-trace"
    assert result["trace_id"] == "trace-123"


def test_trace_serializer_adds_type(
    trace_serializer: TraceSerializer,
) -> None:
    result = trace_serializer.serialize(
        {
            "name": "test-trace",
        },
    )

    assert result["serialization_type"] == SerializationType.TRACE.value


def test_trace_serializer_round_trip(
    trace_serializer: TraceSerializer,
) -> None:
    source = {
        "name": "test-trace",
        "trace_id": "trace-123",
    }

    encoded = trace_serializer.serialize(source)
    decoded = trace_serializer.deserialize(encoded)

    assert decoded["name"] == source["name"]
    assert decoded["trace_id"] == source["trace_id"]


# ==============================================================================
# Part 7. SpanSerializer Tests
# ==============================================================================


def test_span_serializer_creation(
    span_serializer: SpanSerializer,
) -> None:
    assert isinstance(span_serializer, SpanSerializer)


def test_span_serializer_serializes_mapping(
    span_serializer: SpanSerializer,
) -> None:
    source = {
        "name": "test-span",
        "span_id": "span-123",
        "trace_id": "trace-123",
    }

    result = span_serializer.serialize(source)

    assert result["name"] == "test-span"
    assert result["span_id"] == "span-123"
    assert result["trace_id"] == "trace-123"


def test_span_serializer_adds_type(
    span_serializer: SpanSerializer,
) -> None:
    result = span_serializer.serialize(
        {
            "name": "test-span",
        },
    )

    assert result["serialization_type"] == SerializationType.SPAN.value


def test_span_serializer_round_trip(
    span_serializer: SpanSerializer,
) -> None:
    source = {
        "name": "test-span",
        "span_id": "span-123",
        "trace_id": "trace-123",
    }

    encoded = span_serializer.serialize(source)
    decoded = span_serializer.deserialize(encoded)

    assert decoded["name"] == source["name"]
    assert decoded["span_id"] == source["span_id"]


# ==============================================================================
# Part 8. ContextSerializer Tests
# ==============================================================================


def test_context_serializer_creation(
    context_serializer: ContextSerializer,
) -> None:
    assert isinstance(context_serializer, ContextSerializer)


def test_context_serializer_serializes_mapping(
    context_serializer: ContextSerializer,
) -> None:
    source = {
        "trace_id": "trace-123",
        "span_id": "span-123",
    }

    result = context_serializer.serialize(source)

    assert result["trace_id"] == "trace-123"
    assert result["span_id"] == "span-123"


def test_context_serializer_adds_type(
    context_serializer: ContextSerializer,
) -> None:
    result = context_serializer.serialize(
        {
            "trace_id": "trace-123",
        },
    )

    assert result["serialization_type"] == SerializationType.CONTEXT.value


def test_context_serializer_round_trip(
    context_serializer: ContextSerializer,
) -> None:
    source = {
        "trace_id": "trace-123",
        "span_id": "span-123",
    }

    encoded = context_serializer.serialize(source)
    decoded = context_serializer.deserialize(encoded)

    assert decoded == source


# ==============================================================================
# Part 9. MiddlewareSerializer Tests
# ==============================================================================


def test_middleware_serializer_creation(
    middleware_serializer: MiddlewareSerializer,
) -> None:
    assert isinstance(
        middleware_serializer,
        MiddlewareSerializer,
    )


def test_middleware_serializer_serializes_mapping(
    middleware_serializer: MiddlewareSerializer,
) -> None:
    source = {
        "name": "tracing",
        "enabled": True,
    }

    result = middleware_serializer.serialize(source)

    assert result["name"] == "tracing"
    assert result["enabled"] is True


def test_middleware_serializer_adds_type(
    middleware_serializer: MiddlewareSerializer,
) -> None:
    result = middleware_serializer.serialize(
        {
            "name": "tracing",
        },
    )

    assert (
        result["serialization_type"]
        == SerializationType.MIDDLEWARE.value
    )


def test_middleware_serializer_round_trip(
    middleware_serializer: MiddlewareSerializer,
) -> None:
    source = {
        "name": "tracing",
        "enabled": True,
    }

    encoded = middleware_serializer.serialize(source)
    decoded = middleware_serializer.deserialize(encoded)

    assert decoded == source


# ==============================================================================
# Part 10. TracePayload Tests
# ==============================================================================


def test_trace_payload_defaults() -> None:
    payload = TracePayload(
        payload={
            "name": "trace",
        },
    )

    assert payload.payload["name"] == "trace"


def test_trace_payload_copy() -> None:
    payload = TracePayload(
        payload={
            "name": "trace",
            "nested": {
                "value": 1,
            },
        },
    )

    copied = payload.copy()

    assert copied is not payload
    assert copied.payload == payload.payload


def test_trace_payload_json(
    trace_payload: TracePayload,
) -> None:
    result = trace_payload.to_json()

    assert isinstance(result, str)

    decoded = json.loads(result)

    assert decoded["payload"]["name"] == "test-trace"


# ==============================================================================
# Part 11. Round-trip Tests
# ==============================================================================


def test_trace_round_trip() -> None:
    source = {
        "name": "trace",
        "trace_id": "trace-123",
        "metadata": {
            "environment": "test",
        },
    }

    encoded = serialize_trace(source)
    decoded = deserialize_trace(encoded)

    assert decoded == source


def test_span_round_trip() -> None:
    source = {
        "name": "span",
        "span_id": "span-123",
        "trace_id": "trace-123",
    }

    encoded = serialize_span(source)
    decoded = deserialize_span(encoded)

    assert decoded == source


def test_context_round_trip() -> None:
    source = {
        "trace_id": "trace-123",
        "span_id": "span-123",
        "sampled": True,
    }

    encoded = serialize_context(source)
    decoded = deserialize_context(encoded)

    assert decoded == source


def test_middleware_round_trip() -> None:
    source = {
        "name": "tracing",
        "enabled": True,
        "metadata": {
            "environment": "test",
        },
    }

    encoded = serialize_middleware(source)
    decoded = deserialize_middleware(encoded)

    assert decoded == source


def test_nested_payload_round_trip() -> None:
    source = {
        "name": "trace",
        "attributes": {
            "request": {
                "id": "123",
                "values": [
                    1,
                    2,
                    3,
                ],
            },
        },
    }

    encoded = serialize_trace(source)
    decoded = deserialize_trace(encoded)

    assert decoded == source


# ==============================================================================
# Part 12. Defensive Copy Tests
# ==============================================================================


def test_trace_serializer_defensive_copy() -> None:
    source = {
        "name": "trace",
        "metadata": {
            "key": "value",
        },
    }

    result = serialize_trace(source)

    source["metadata"]["key"] = "changed"

    assert result["metadata"]["key"] == "value"


def test_span_serializer_defensive_copy() -> None:
    source = {
        "name": "span",
        "attributes": {
            "key": "value",
        },
    }

    result = serialize_span(source)

    source["attributes"]["key"] = "changed"

    assert result["attributes"]["key"] == "value"


def test_context_serializer_defensive_copy() -> None:
    source = {
        "trace_id": "trace-123",
        "metadata": {
            "key": "value",
        },
    }

    result = serialize_context(source)

    source["metadata"]["key"] = "changed"

    assert result["metadata"]["key"] == "value"


def test_middleware_serializer_defensive_copy() -> None:
    source = {
        "name": "middleware",
        "metadata": {
            "key": "value",
        },
    }

    result = serialize_middleware(source)

    source["metadata"]["key"] = "changed"

    assert result["metadata"]["key"] == "value"


# ==============================================================================
# Part 13. Invalid Input Tests
# ==============================================================================


@pytest.mark.parametrize(
    "serializer",
    [
        TraceSerializer(),
        SpanSerializer(),
        ContextSerializer(),
        MiddlewareSerializer(),
    ],
)
def test_serializer_rejects_none(
    serializer: Any,
) -> None:
    with pytest.raises(
        (TypeError, SerializationError, SerializationValidationError),
    ):
        serializer.serialize(None)


@pytest.mark.parametrize(
    "serializer",
    [
        TraceSerializer(),
        SpanSerializer(),
        ContextSerializer(),
        MiddlewareSerializer(),
    ],
)
def test_serializer_rejects_invalid_scalar(
    serializer: Any,
) -> None:
    with pytest.raises(
        (TypeError, SerializationError, SerializationValidationError),
    ):
        serializer.serialize("invalid")


@pytest.mark.parametrize(
    "serializer",
    [
        TraceSerializer(),
        SpanSerializer(),
        ContextSerializer(),
        MiddlewareSerializer(),
    ],
)
def test_deserializer_rejects_none(
    serializer: Any,
) -> None:
    with pytest.raises(
        (TypeError, SerializationError, SerializationValidationError),
    ):
        serializer.deserialize(None)


def test_trace_deserializer_rejects_wrong_type() -> None:
    with pytest.raises(
        (TypeError, SerializationError, SerializationValidationError),
    ):
        deserialize_trace(
            {
                "serialization_type": "span",
            },
        )


def test_span_deserializer_rejects_wrong_type() -> None:
    with pytest.raises(
        (TypeError, SerializationError, SerializationValidationError),
    ):
        deserialize_span(
            {
                "serialization_type": "trace",
            },
        )


# ==============================================================================
# Part 14. JSON Serialization Tests
# ==============================================================================


def test_trace_json_serialization() -> None:
    source = {
        "name": "trace",
        "trace_id": "trace-123",
        "value": 42,
    }

    encoded = serialize_trace(
        source,
        format=SerializationFormat.JSON,
    )

    assert isinstance(encoded, str)

    decoded = json.loads(encoded)

    assert decoded["name"] == "trace"
    assert decoded["trace_id"] == "trace-123"


def test_span_json_serialization() -> None:
    source = {
        "name": "span",
        "span_id": "span-123",
    }

    encoded = serialize_span(
        source,
        format=SerializationFormat.JSON,
    )

    assert isinstance(encoded, str)

    decoded = json.loads(encoded)

    assert decoded["name"] == "span"


def test_context_json_serialization() -> None:
    source = {
        "trace_id": "trace-123",
        "span_id": "span-123",
    }

    encoded = serialize_context(
        source,
        format=SerializationFormat.JSON,
    )

    assert isinstance(encoded, str)

    decoded = json.loads(encoded)

    assert decoded["trace_id"] == "trace-123"


def test_middleware_json_serialization() -> None:
    source = {
        "name": "middleware",
        "enabled": True,
    }

    encoded = serialize_middleware(
        source,
        format=SerializationFormat.JSON,
    )

    assert isinstance(encoded, str)

    decoded = json.loads(encoded)

    assert decoded["name"] == "middleware"
    assert decoded["enabled"] is True


def test_json_round_trip() -> None:
    source = {
        "name": "trace",
        "trace_id": "trace-123",
        "metadata": {
            "environment": "test",
            "nested": {
                "enabled": True,
            },
        },
    }

    encoded = serialize_trace(
        source,
        format=SerializationFormat.JSON,
    )

    decoded = deserialize_trace(encoded)

    assert decoded == source


# ==============================================================================
# Part 15. Public API Tests
# ==============================================================================


def test_trace_serializer_public_api() -> None:
    assert TraceSerializer is not None


def test_span_serializer_public_api() -> None:
    assert SpanSerializer is not None


def test_context_serializer_public_api() -> None:
    assert ContextSerializer is not None


def test_middleware_serializer_public_api() -> None:
    assert MiddlewareSerializer is not None


def test_trace_payload_public_api() -> None:
    assert TracePayload is not None


def test_public_helper_functions() -> None:
    assert callable(serialize_trace)
    assert callable(serialize_span)
    assert callable(serialize_context)
    assert callable(serialize_middleware)

    assert callable(deserialize_trace)
    assert callable(deserialize_span)
    assert callable(deserialize_context)
    assert callable(deserialize_middleware)


def test_public_serialization_enums() -> None:
    assert SerializationFormat.JSON.value == "json"
    assert SerializationType.TRACE.value == "trace"
    assert SerializationType.SPAN.value == "span"
    assert SerializationType.CONTEXT.value == "context"
    assert SerializationType.MIDDLEWARE.value == "middleware"


def test_public_exceptions() -> None:
    assert issubclass(
        SerializationError,
        Exception,
    )

    assert issubclass(
        SerializationValidationError,
        SerializationError,
    )

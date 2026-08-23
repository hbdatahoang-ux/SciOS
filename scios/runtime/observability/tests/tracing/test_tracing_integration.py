# ==============================================================================
# SciOS Runtime Observability
# Tracing Integration Tests
# ==============================================================================

"""
Integration tests for the SciOS tracing subsystem.

Python 3.11+
"""

from __future__ import annotations

import json

import pytest

from scios.runtime.observability.tracing import (
    SerializationFormat,
    SerializationType,
    TracePayload,
    TraceSerializer,
    deserialize_trace,
    serialize_trace,
)


# ==============================================================================
# Helpers
# ==============================================================================


def create_trace() -> dict:
    """Create a representative trace payload."""

    return {
        "name": "integration-trace",
        "trace_id": "trace-integration-123",
        "service_name": "scios",
        "metadata": {
            "environment": "test",
            "component": "tracing",
        },
        "attributes": {
            "version": 1,
            "enabled": True,
        },
    }


# ==============================================================================
# Serialization Integration
# ==============================================================================


def test_trace_serialization_dict_round_trip() -> None:
    """Trace dictionary serialization must round-trip."""

    source = create_trace()

    encoded = serialize_trace(
        source,
        format=SerializationFormat.DICT,
    )

    assert isinstance(encoded, dict)

    assert encoded["version"] == "1.0"
    assert encoded["type"] == SerializationType.TRACE.value
    assert encoded["name"] == source["name"]
    assert encoded["trace_id"] == source["trace_id"]

    decoded = deserialize_trace(
        encoded,
        format=SerializationFormat.DICT,
    )

    assert decoded["name"] == source["name"]
    assert decoded["trace_id"] == source["trace_id"]
    assert decoded["service_name"] == source["service_name"]


def test_trace_serialization_json_round_trip() -> None:
    """Trace JSON serialization must round-trip."""

    source = create_trace()

    encoded = serialize_trace(
        source,
        format=SerializationFormat.JSON,
    )

    assert isinstance(encoded, str)

    decoded_json = json.loads(encoded)

    assert decoded_json["version"] == "1.0"
    assert decoded_json["type"] == "trace"

    decoded = deserialize_trace(
        encoded,
    )

    assert decoded["name"] == source["name"]
    assert decoded["trace_id"] == source["trace_id"]


def test_trace_serializer_class_matches_module_api() -> None:
    """Class API and module-level API must produce equivalent data."""

    source = create_trace()

    serializer = TraceSerializer()

    class_result = serializer.to_dict(source)

    module_result = serialize_trace(
        source,
        format=SerializationFormat.DICT,
    )

    assert class_result == module_result


# ==============================================================================
# TracePayload Integration
# ==============================================================================


def test_trace_payload_integration() -> None:
    """TracePayload must integrate with serialization API."""

    source = create_trace()

    payload = TracePayload(
        payload=source,
    )

    encoded = payload.to_dict()

    assert encoded["version"] == "1.0"
    assert encoded["type"] == "trace"
    assert encoded["payload"]["trace_id"] == (
        "trace-integration-123"
    )

    restored = TracePayload.from_dict(
        encoded,
    )

    assert restored.serialization_version == "1.0"
    assert restored.serialization_type == (
        SerializationType.TRACE
    )

    assert restored.payload == source


def test_trace_payload_json_round_trip() -> None:
    """TracePayload JSON representation must be reversible."""

    payload = TracePayload(
        payload=create_trace(),
    )

    encoded = payload.to_json()

    assert isinstance(encoded, str)

    decoded = json.loads(encoded)

    assert decoded["version"] == "1.0"
    assert decoded["type"] == "trace"
    assert decoded["payload"]["trace_id"] == (
        "trace-integration-123"
    )

    restored = TracePayload.from_dict(
        decoded,
    )

    assert restored.payload == payload.payload


# ==============================================================================
# Defensive Copy Integration
# ==============================================================================


def test_trace_payload_defensive_copy() -> None:
    """Payload mutation must not affect internal tracing state."""

    source = create_trace()

    payload = TracePayload(
        payload=source,
    )

    exposed = payload.payload

    exposed["name"] = "mutated"
    exposed["metadata"]["environment"] = "mutated"

    assert payload.payload["name"] == (
        "integration-trace"
    )

    assert payload.payload["metadata"]["environment"] == (
        "test"
    )


# ==============================================================================
# Serializer Independence
# ==============================================================================


def test_serialized_result_is_independent() -> None:
    """Serialized output must not alias source state."""

    source = create_trace()

    encoded = serialize_trace(source)

    encoded["metadata"]["environment"] = "mutated"

    assert source["metadata"]["environment"] == "test"


# ==============================================================================
# Validation Integration
# ==============================================================================


def test_trace_serialization_type_is_preserved() -> None:
    """Trace serialization must expose the expected type."""

    encoded = serialize_trace(
        create_trace(),
    )

    assert encoded["type"] == "trace"
    assert encoded["serialization_type"] == "trace"


def test_trace_serialization_version_is_preserved() -> None:
    """Trace serialization version must remain stable."""

    encoded = serialize_trace(
        create_trace(),
    )

    assert encoded["version"] == "1.0"
    assert encoded["serialization_version"] == "1.0"


# ==============================================================================
# Error Integration
# ==============================================================================


def test_trace_serializer_rejects_none() -> None:
    """TraceSerializer must reject None."""

    serializer = TraceSerializer()

    with pytest.raises(Exception):
        serializer.serialize(None)


def test_trace_json_output_is_valid_json() -> None:
    """JSON output must always be valid JSON."""

    encoded = serialize_trace(
        create_trace(),
        format=SerializationFormat.JSON,
    )

    decoded = json.loads(encoded)

    assert isinstance(decoded, dict)
    assert decoded["type"] == "trace"
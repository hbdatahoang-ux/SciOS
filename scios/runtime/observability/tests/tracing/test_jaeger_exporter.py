# ==============================================================================
# SciOS Runtime Observability
# Jaeger Exporter Tests
# ==============================================================================

from __future__ import annotations

import json

import pytest

from scios.runtime.observability.tracing.jaeger import (
    JaegerExportError,
    JaegerExporter,
)


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def exporter() -> JaegerExporter:
    return JaegerExporter()


@pytest.fixture
def span() -> dict[str, object]:
    return {
        "trace_id": "trace-001",
        "span_id": "span-001",
        "operation_name": "planner",
        "start_time": 1.0,
        "duration": 0.25,
    }


# ==============================================================================
# Part 1. Construction
# ==============================================================================


def test_default_construction():
    exporter = JaegerExporter()

    assert exporter.name == "jaeger"
    assert exporter.endpoint == "http://localhost:14268/api/traces"
    assert exporter.service_name == "scios"
    assert exporter.encoding == "utf-8"
    assert exporter.enabled is True
    assert exporter.state == "created"


def test_custom_name():
    exporter = JaegerExporter(
        name="test-jaeger",
    )

    assert exporter.name == "test-jaeger"


def test_custom_endpoint():
    exporter = JaegerExporter(
        endpoint="http://jaeger:14268/api/traces",
    )

    assert exporter.endpoint == "http://jaeger:14268/api/traces"


def test_custom_service_name():
    exporter = JaegerExporter(
        service_name="my-service",
    )

    assert exporter.service_name == "my-service"


def test_custom_encoding():
    exporter = JaegerExporter(
        encoding="utf-16",
    )

    assert exporter.encoding == "utf-16"


def test_disabled_exporter():
    exporter = JaegerExporter(
        enabled=False,
    )

    assert exporter.enabled is False


def test_custom_options():
    options = {
        "timeout": 5,
        "batch_size": 10,
    }

    exporter = JaegerExporter(
        options=options,
    )

    assert exporter.options == options


# ==============================================================================
# Part 2. Configuration
# ==============================================================================


def test_name(exporter):
    assert exporter.name == "jaeger"


def test_endpoint(exporter):
    assert exporter.endpoint == (
        "http://localhost:14268/api/traces"
    )


def test_service_name(exporter):
    assert exporter.service_name == "scios"


def test_encoding(exporter):
    assert exporter.encoding == "utf-8"


def test_enabled(exporter):
    assert exporter.enabled is True

    exporter.enabled = False

    assert exporter.enabled is False

    exporter.enabled = True

    assert exporter.enabled is True


def test_options(exporter):
    assert isinstance(
        exporter.options,
        dict,
    )

    exporter.options["timeout"] = 10

    assert exporter.options["timeout"] == 10


# ==============================================================================
# Part 3. Serialization
# ==============================================================================


def test_serialize_mapping(exporter):
    payload = {
        "trace_id": "trace-001",
        "span_id": "span-001",
    }

    result = exporter.serialize(
        payload,
    )

    assert isinstance(
        result,
        str,
    )

    assert json.loads(
        result,
    ) == payload


def test_serialize_span(
    exporter,
    span,
):
    result = exporter.serialize_span(
        span,
    )

    assert isinstance(
        result,
        str,
    )

    assert json.loads(
        result,
    ) == span


def test_serialize_list(exporter):
    payload = [
        {"id": 1},
        {"id": 2},
        {"id": 3},
    ]

    result = exporter.serialize(
        payload,
    )

    assert isinstance(
        result,
        str,
    )

    assert json.loads(
        result,
    ) == payload


def test_serialize_string(exporter):
    result = exporter.serialize(
        "hello",
    )

    assert isinstance(
        result,
        str,
    )

    assert json.loads(
        result,
    ) == "hello"


def test_serialize_bytes(exporter):
    result = exporter.serialize(
        b"hello",
    )

    assert isinstance(
        result,
        str,
    )

    assert json.loads(
        result,
    ) == "hello"


def test_serialize_none(exporter):
    result = exporter.serialize(
        None,
    )

    assert result == "null"


# ==============================================================================
# Part 4. Export
# ==============================================================================


def test_export_mapping(exporter):
    payload = {
        "trace_id": "trace-001",
        "span_id": "span-001",
    }

    result = exporter.export(
        payload,
    )

    assert result.success is True
    assert isinstance(
        result.payload,
        str,
    )


def test_export_span(
    exporter,
    span,
):
    result = exporter.export(
        span,
    )

    assert result.success is True
    assert isinstance(
        result.payload,
        str,
    )

    assert json.loads(
        result.payload,
    ) == span


def test_export_result(exporter):
    result = exporter.export(
        {
            "operation": "planner",
        },
    )

    assert result.success is True
    assert result.format.value == "json"
    assert result.bytes_exported > 0
    assert result.error is None

    assert result.metadata["endpoint"] == exporter.endpoint
    assert result.metadata["service_name"] == (
        exporter.service_name
    )


def test_export_bytes(exporter):
    result = exporter.export(
        b"jaeger-data",
    )

    assert result.success is True
    assert isinstance(
        result.payload,
        str,
    )

    assert json.loads(
        result.payload,
    ) == "jaeger-data"


def test_export_many(exporter):
    payloads = [
        {"id": 1},
        {"id": 2},
        {"id": 3},
    ]

    results = exporter.export_many(
        payloads,
    )

    assert isinstance(
        results,
        list,
    )

    assert len(results) == 3

    assert all(
        result.success
        for result in results
    )

    assert exporter.export_count == 3


# ==============================================================================
# Part 5. Validation
# ==============================================================================


def test_valid_payload(exporter):
    assert exporter.validate_payload(
        {"id": 1},
    ) is True

    assert exporter.validate_payload(
        [{"id": 1}],
    ) is True

    assert exporter.validate_payload(
        "hello",
    ) is True

    assert exporter.validate_payload(
        b"hello",
    ) is True

    assert exporter.validate_payload(
        None,
    ) is True


def test_invalid_payload(exporter):
    class Unsupported:
        pass

    assert exporter.validate_payload(
        Unsupported(),
    ) is False


def test_valid_endpoint(exporter):
    assert exporter.validate_endpoint(
        "http://localhost:14268/api/traces",
    ) is True

    assert exporter.validate_endpoint(
        "https://jaeger.example.com/api/traces",
    ) is True


def test_invalid_endpoint(exporter):
    assert exporter.validate_endpoint(
        "",
    ) is False

    assert exporter.validate_endpoint(
        "not-a-url",
    ) is False

    assert exporter.validate_endpoint(
        None,
    ) is False


def test_invalid_options(exporter):
    assert exporter.validate_options(
        {
            "timeout": 5,
        },
    ) is True

    assert exporter.validate_options(
        {
            1: "invalid",
        },
    ) is False

    assert exporter.validate_options(
        [],
    ) is False


# ==============================================================================
# Part 6. Lifecycle
# ==============================================================================


def test_start(exporter):
    result = exporter.start()

    assert result is exporter
    assert exporter.state == "running"


def test_stop(exporter):
    exporter.start()

    result = exporter.stop()

    assert result is exporter
    assert exporter.state == "stopped"


def test_reset(exporter):
    exporter.export(
        {
            "id": 1,
        },
    )

    assert exporter.export_count == 1

    result = exporter.reset()

    assert result is exporter
    assert exporter.state == "created"
    assert exporter.export_count == 0
    assert exporter.success_count == 0
    assert exporter.error_count == 0
    assert exporter.bytes_exported == 0


def test_close(exporter):
    result = exporter.close()

    assert result is exporter
    assert exporter.state == "closed"


def test_export_after_close(exporter):
    exporter.close()

    with pytest.raises(
        JaegerExportError,
    ):
        exporter.export(
            {
                "id": 1,
            },
        )


# ==============================================================================
# Part 7. Error Handling
# ==============================================================================


def test_invalid_endpoint():
    with pytest.raises(
        (ValueError, JaegerExportError),
    ):
        JaegerExporter(
            endpoint="not-a-url",
        )


def test_invalid_payload(exporter):
    class Unsupported:
        pass

    assert exporter.validate_payload(
        Unsupported(),
    ) is False

    with pytest.raises(
        JaegerExportError,
    ):
        exporter.export(
            Unsupported(),
        )


def test_serialization_error(exporter):
    class Unsupported:
        pass

    # Force serializer to reject the payload.
    with pytest.raises(
        JaegerExportError,
    ):
        exporter.serialize(
            Unsupported(),
        )

    assert exporter.error_count >= 1


def test_export_error(exporter):
    exporter.close()

    with pytest.raises(
        JaegerExportError,
    ):
        exporter.export(
            {
                "id": 1,
            },
        )

    assert exporter.error_count == 1


def test_error_count(exporter):
    exporter.close()

    with pytest.raises(
        JaegerExportError,
    ):
        exporter.export(
            {
                "id": 1,
            },
        )

    with pytest.raises(
        JaegerExportError,
    ):
        exporter.export(
            {
                "id": 2,
            },
        )

    assert exporter.error_count == 2


# ==============================================================================
# Part 8. Statistics
# ==============================================================================


def test_export_count(exporter):
    assert exporter.export_count == 0

    exporter.export(
        {
            "id": 1,
        },
    )

    exporter.export(
        {
            "id": 2,
        },
    )

    assert exporter.export_count == 2


def test_success_count(exporter):
    assert exporter.success_count == 0

    exporter.export(
        {
            "id": 1,
        },
    )

    exporter.export(
        {
            "id": 2,
        },
    )

    assert exporter.success_count == 2


def test_error_count_statistics(exporter):
    exporter.close()

    with pytest.raises(
        JaegerExportError,
    ):
        exporter.export(
            {
                "id": 1,
            },
        )

    assert exporter.error_count == 1


def test_bytes_exported(exporter):
    assert exporter.bytes_exported == 0

    result = exporter.export(
        {
            "message": "hello",
        },
    )

    assert exporter.bytes_exported == (
        result.bytes_exported
    )

    assert exporter.bytes_exported > 0


# ==============================================================================
# Part 9. Diagnostics
# ==============================================================================


def test_health(exporter):
    assert exporter.health() is True

    exporter.enabled = False

    assert exporter.health() is False


def test_health_after_close(exporter):
    exporter.close()

    assert exporter.health() is False


def test_diagnostics(exporter):
    exporter.export(
        {
            "id": 1,
        },
    )

    diagnostics = exporter.diagnostics()

    assert isinstance(
        diagnostics,
        dict,
    )

    assert diagnostics["name"] == exporter.name
    assert diagnostics["endpoint"] == exporter.endpoint
    assert diagnostics["service_name"] == (
        exporter.service_name
    )
    assert diagnostics["encoding"] == exporter.encoding
    assert diagnostics["enabled"] is True
    assert diagnostics["state"] == exporter.state
    assert diagnostics["healthy"] is True

    assert diagnostics["export_count"] == (
        exporter.export_count
    )

    assert diagnostics["success_count"] == (
        exporter.success_count
    )

    assert diagnostics["error_count"] == (
        exporter.error_count
    )

    assert diagnostics["bytes_exported"] == (
        exporter.bytes_exported
    )


def test_summary(exporter):
    summary = exporter.summary()

    assert isinstance(
        summary,
        dict,
    )

    assert summary["name"] == exporter.name
    assert summary["endpoint"] == exporter.endpoint
    assert summary["service_name"] == (
        exporter.service_name
    )
    assert summary["state"] == exporter.state
    assert summary["enabled"] == exporter.enabled
    assert summary["healthy"] == exporter.health()

    assert summary["export_count"] == (
        exporter.export_count
    )

    assert summary["success_count"] == (
        exporter.success_count
    )

    assert summary["error_count"] == (
        exporter.error_count
    )

    assert summary["bytes_exported"] == (
        exporter.bytes_exported
    )


# ==============================================================================
# Part 10. Representation
# ==============================================================================


def test_repr(exporter):
    result = repr(
        exporter,
    )

    assert isinstance(
        result,
        str,
    )

    assert "JaegerExporter" in result
    assert exporter.name in result
    assert exporter.endpoint in result


def test_str(exporter):
    result = str(
        exporter,
    )

    assert isinstance(
        result,
        str,
    )

    assert exporter.name in result
    assert exporter.endpoint in result


# ==============================================================================
# Part 11. End
# ==============================================================================
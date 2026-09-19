# ==============================================================================
# SciOS Runtime Observability
# Zipkin Exporter Tests
# ==============================================================================

from __future__ import annotations

# ==============================================================================
# Part 1. Imports
# ==============================================================================

import json

import pytest

from scios.runtime.observability.tracing.zipkin import (
    ZipkinExporter,
    ZipkinExportError,
)


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def exporter():
    return ZipkinExporter()


@pytest.fixture
def span():
    return {
        "trace_id": "trace-001",
        "span_id": "span-001",
        "operation_name": "planner",
        "start_time": 1.0,
        "duration": 0.5,
        "tags": {
            "component": "runtime",
        },
    }


# ==============================================================================
# Part 1. Construction
# ==============================================================================


def test_default_construction():
    exporter = ZipkinExporter()

    assert exporter.name == "zipkin"
    assert exporter.endpoint == "http://localhost:9411/api/v2/spans"
    assert exporter.service_name == "scios"
    assert exporter.encoding == "utf-8"
    assert exporter.enabled is True


def test_custom_name():
    exporter = ZipkinExporter(
        name="custom-zipkin",
    )

    assert exporter.name == "custom-zipkin"


def test_custom_endpoint():
    endpoint = "http://zipkin:9411/api/v2/spans"

    exporter = ZipkinExporter(
        endpoint=endpoint,
    )

    assert exporter.endpoint == endpoint


def test_custom_service_name():
    exporter = ZipkinExporter(
        service_name="my-service",
    )

    assert exporter.service_name == "my-service"


def test_custom_encoding():
    exporter = ZipkinExporter(
        encoding="utf-16",
    )

    assert exporter.encoding == "utf-16"


def test_disabled_exporter():
    exporter = ZipkinExporter(
        enabled=False,
    )

    assert exporter.enabled is False


def test_custom_options():
    options = {
        "timeout": 5,
        "batch_size": 10,
    }

    exporter = ZipkinExporter(
        options=options,
    )

    assert exporter.options == options


# ==============================================================================
# Part 2. Configuration
# ==============================================================================


def test_name(exporter):
    assert exporter.name == "zipkin"


def test_endpoint(exporter):
    assert exporter.endpoint == "http://localhost:9411/api/v2/spans"


def test_service_name(exporter):
    assert exporter.service_name == "scios"


def test_encoding(exporter):
    assert exporter.encoding == "utf-8"


def test_enabled(exporter):
    assert exporter.enabled is True


def test_options(exporter):
    assert exporter.options == {}


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
    result = exporter.serialize(
        [1, 2, 3],
    )

    assert result == "[1, 2, 3]"


def test_serialize_string(exporter):
    result = exporter.serialize(
        "hello",
    )

    assert result == '"hello"'


def test_serialize_bytes(exporter):
    result = exporter.serialize(
        b"hello",
    )

    assert isinstance(
        result,
        str,
    )

    assert result == '"hello"'


def test_serialize_none(exporter):
    result = exporter.serialize(
        None,
    )

    assert result == "null"


# ==============================================================================
# Part 4. Export
# ==============================================================================


def test_export_mapping(exporter):
    result = exporter.export(
        {
            "id": 1,
        },
    )

    assert result.success is True
    assert json.loads(
        result.payload,
    ) == {
        "id": 1,
    }


def test_export_span(
    exporter,
    span,
):
    result = exporter.export(
        span,
    )

    assert result.success is True
    assert json.loads(
        result.payload,
    ) == span


def test_export_result(exporter):
    result = exporter.export(
        {
            "message": "hello",
        },
    )

    assert result.success is True
    assert isinstance(
        result.payload,
        str,
    )
    assert result.bytes_exported > 0


def test_export_bytes(exporter):
    result = exporter.export(
        b"zipkin-data",
    )

    assert result.success is True
    assert isinstance(
        result.payload,
        str,
    )
    assert result.payload == '"zipkin-data"'


def test_export_many(exporter):
    results = exporter.export_many(
        [
            {"id": 1},
            {"id": 2},
            {"id": 3},
        ],
    )

    assert len(results) == 3

    assert all(
        result.success
        for result in results
    )


# ==============================================================================
# Part 5. Validation
# ==============================================================================


def test_valid_payload(exporter):
    assert exporter.validate_payload(
        {"id": 1},
    ) is True

    assert exporter.validate_payload(
        [1, 2, 3],
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
        "http://localhost:9411/api/v2/spans",
    ) is True

    assert exporter.validate_endpoint(
        "https://zipkin.example.com/api/v2/spans",
    ) is True


def test_invalid_endpoint():
    with pytest.raises(
        (ValueError, ZipkinExportError),
    ):
        ZipkinExporter(
            endpoint="invalid-endpoint",
        )


def test_invalid_options(exporter):
    assert exporter.validate_options(
        {
            "timeout": 5,
        },
    ) is True

    assert exporter.validate_options(
        {
            123: "invalid",
        },
    ) is False

    assert exporter.validate_options(
        "invalid",
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
    assert exporter.success_count == 1
    assert exporter.bytes_exported > 0

    result = exporter.reset()

    assert result is exporter
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
        ZipkinExportError,
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
        (ValueError, ZipkinExportError),
    ):
        ZipkinExporter(
            endpoint="invalid-endpoint",
        )


def test_invalid_payload(exporter):
    class Unsupported:
        pass

    with pytest.raises(
        ZipkinExportError,
    ):
        exporter.serialize(
            Unsupported(),
        )

    assert exporter.error_count >= 1


def test_serialization_error(exporter):
    class Unsupported:
        pass

    with pytest.raises(
        ZipkinExportError,
    ):
        exporter.serialize(
            Unsupported(),
        )

    assert exporter.error_count >= 1


def test_export_error(exporter):
    class Unsupported:
        pass

    with pytest.raises(
        ZipkinExportError,
    ):
        exporter.export(
            Unsupported(),
        )

    assert exporter.error_count >= 1


def test_error_count(exporter):
    assert exporter.error_count == 0

    class Unsupported:
        pass

    with pytest.raises(
        ZipkinExportError,
    ):
        exporter.serialize(
            Unsupported(),
        )

    assert exporter.error_count >= 1


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

    assert exporter.export_count == 1


def test_success_count(exporter):
    assert exporter.success_count == 0

    exporter.export(
        {
            "id": 1,
        },
    )

    assert exporter.success_count == 1


def test_error_count_after_failed_export(exporter):
    assert exporter.error_count == 0

    class Unsupported:
        pass

    with pytest.raises(
        ZipkinExportError,
    ):
        exporter.export(
            Unsupported(),
        )

    assert exporter.error_count >= 1


def test_bytes_exported(exporter):
    assert exporter.bytes_exported == 0

    result = exporter.export(
        {
            "message": "hello",
        },
    )

    assert exporter.bytes_exported == result.bytes_exported
    assert exporter.bytes_exported > 0


# ==============================================================================
# Part 9. Diagnostics
# ==============================================================================


def test_health(exporter):
    health = exporter.health()

    assert isinstance(
        health,
        dict,
    )

    assert "healthy" in health
    assert "state" in health
    assert "enabled" in health


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

    assert diagnostics["name"] == "zipkin"
    assert diagnostics["endpoint"] == (
        "http://localhost:9411/api/v2/spans"
    )
    assert diagnostics["service_name"] == "scios"

    assert diagnostics["export_count"] == 1
    assert diagnostics["success_count"] == 1
    assert diagnostics["bytes_exported"] > 0


def test_summary(exporter):
    summary = exporter.summary()

    assert isinstance(
        summary,
        dict,
    )

    assert summary["name"] == "zipkin"
    assert summary["state"] == "created"
    assert summary["export_count"] == 0
    assert summary["success_count"] == 0
    assert summary["error_count"] == 0
    assert summary["bytes_exported"] == 0


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

    assert "ZipkinExporter" in result
    assert "zipkin" in result
    assert exporter.endpoint in result


def test_str(exporter):
    result = str(
        exporter,
    )

    assert isinstance(
        result,
        str,
    )

    assert "ZipkinExporter" in result
    assert "zipkin" in result


# ==============================================================================
# Part 11. End
# ==============================================================================


__all__ = [
    "test_invalid_endpoint",
    "test_invalid_payload",
    "test_serialization_error",
    "test_export_error",
    "test_error_count",
    "test_export_count",
    "test_success_count",
    "test_error_count_after_failed_export",
    "test_bytes_exported",
    "test_health",
    "test_diagnostics",
    "test_summary",
    "test_repr",
    "test_str",
]        
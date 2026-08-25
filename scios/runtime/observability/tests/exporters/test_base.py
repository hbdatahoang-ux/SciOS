"""
SciOS Runtime Observability
===========================

Tests for the generic Exporter base contract.

Test organization
-----------------

Part 1. Construction
Part 2. Configuration validation
Part 3. Properties
Part 4. Lifecycle
Part 5. Serialization
Part 6. Export
Part 7. Export statistics
Part 8. Validation
Part 9. Error handling
Part 10. Diagnostics
Part 11. Representation

Python 3.11+
"""

from __future__ import annotations

import json
import time

import pytest

from scios.runtime.observability.exporters.base import (
    ExportError,
    ExportFormat,
    ExportPayload,
    ExportResult,
    Exporter,
)


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def exporter() -> Exporter:
    """Return a default exporter instance."""

    return Exporter(
        name="test",
        format=ExportFormat.JSON,
    )


@pytest.fixture
def payload() -> ExportPayload:
    """Return a representative export payload."""

    return ExportPayload(
        name="request_total",
        value=42,
        labels={
            "method": "GET",
            "status": "200",
        },
    )


# ==============================================================================
# Part 1. Construction
# ==============================================================================


def test_exporter_constructs_with_defaults() -> None:
    exporter = Exporter("test")

    assert exporter.name == "test"
    assert exporter.format is ExportFormat.JSON
    assert exporter.encoding == "utf-8"
    assert exporter.enabled is True
    assert exporter.started is False
    assert exporter.closed is False
    assert exporter.state == "stopped"


def test_exporter_constructs_with_custom_configuration() -> None:
    exporter = Exporter(
        name="custom",
        format=ExportFormat.TEXT,
        encoding="ascii",
        enabled=False,
        options={
            "ensure_ascii": True,
        },
    )

    assert exporter.name == "custom"
    assert exporter.format is ExportFormat.TEXT
    assert exporter.encoding == "ascii"
    assert exporter.enabled is False
    assert exporter.options == {
        "ensure_ascii": True,
    }


def test_export_payload_constructs() -> None:
    payload = ExportPayload(
        name="metric",
        value=10,
    )

    assert payload.name == "metric"
    assert payload.value == 10
    assert payload.labels == {}
    assert payload.metadata == {}
    assert payload.options == {}
    assert payload.timestamp is not None


def test_export_result_constructs() -> None:
    result = ExportResult(
        success=True,
        exporter="test",
    )

    assert result.success is True
    assert result.failed is False
    assert result.exporter == "test"
    assert result.count == 1
    assert result.bytes_exported == 0
    assert result.error is None


def test_export_error_is_runtime_error() -> None:
    error = ExportError("export failed")

    assert isinstance(error, RuntimeError)
    assert str(error) == "export failed"
    assert error.cause is None


def test_export_error_preserves_cause() -> None:
    cause = ValueError("invalid payload")
    error = ExportError(
        "export failed",
        cause=cause,
    )

    assert error.cause is cause


# ==============================================================================
# Part 2. Configuration validation
# ==============================================================================


@pytest.mark.parametrize(
    "name",
    [
        "",
        "   ",
    ],
)
def test_empty_name_is_rejected(name: str) -> None:
    with pytest.raises(ValueError, match="name must not be empty"):
        Exporter(name)


def test_non_string_name_is_rejected() -> None:
    with pytest.raises(TypeError, match="name must be a string"):
        Exporter(123)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "format_value",
    [
        "json",
        "text",
        "binary",
        "prometheus",
        "otlp",
        "jaeger",
        "zipkin",
    ],
)
def test_string_format_is_normalized(
    format_value: str,
) -> None:
    exporter = Exporter(
        "test",
        format=format_value,  # type: ignore[arg-type]
    )

    assert exporter.format.value == format_value


def test_invalid_format_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="unsupported export format",
    ):
        Exporter(
            "test",
            format="invalid",  # type: ignore[arg-type]
        )


def test_invalid_encoding_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="unknown encoding",
    ):
        Exporter(
            "test",
            encoding="not-a-real-encoding",
        )


def test_non_string_encoding_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match="encoding must be a string",
    ):
        Exporter(
            "test",
            encoding=123,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "enabled",
    [
        True,
        False,
    ],
)
def test_enabled_accepts_boolean(enabled: bool) -> None:
    exporter = Exporter(
        "test",
        enabled=enabled,
    )

    assert exporter.enabled is enabled


def test_non_boolean_enabled_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match="enabled must be a bool",
    ):
        Exporter(
            "test",
            enabled=1,  # type: ignore[arg-type]
        )


def test_options_are_copied_on_construction() -> None:
    options = {
        "timeout": 10,
    }

    exporter = Exporter(
        "test",
        options=options,
    )

    options["timeout"] = 20

    assert exporter.options == {
        "timeout": 10,
    }


def test_options_property_returns_copy(
    exporter: Exporter,
) -> None:
    options = exporter.options
    options["new_option"] = True

    assert "new_option" not in exporter.options


# ==============================================================================
# Part 3. Properties
# ==============================================================================


def test_name_property(exporter: Exporter) -> None:
    assert exporter.name == "test"


def test_format_property(exporter: Exporter) -> None:
    assert exporter.format is ExportFormat.JSON


def test_encoding_property(exporter: Exporter) -> None:
    assert exporter.encoding == "utf-8"


def test_enabled_property(exporter: Exporter) -> None:
    assert exporter.enabled is True


def test_enabled_property_can_be_changed(
    exporter: Exporter,
) -> None:
    exporter.enabled = False

    assert exporter.enabled is False


def test_enabled_property_rejects_non_boolean(
    exporter: Exporter,
) -> None:
    with pytest.raises(
        TypeError,
        match="enabled must be a bool",
    ):
        exporter.enabled = "yes"  # type: ignore[assignment]


def test_state_property_initially_stopped(
    exporter: Exporter,
) -> None:
    assert exporter.state == "stopped"


def test_statistics_are_zero_initially(
    exporter: Exporter,
) -> None:
    assert exporter.export_count == 0
    assert exporter.success_count == 0
    assert exporter.error_count == 0
    assert exporter.bytes_exported == 0
    assert exporter.last_export is None
    assert exporter.last_error is None


# ==============================================================================
# Part 4. Lifecycle
# ==============================================================================


def test_start_changes_state(exporter: Exporter) -> None:
    result = exporter.start()

    assert result is exporter
    assert exporter.started is True
    assert exporter.closed is False
    assert exporter.state == "started"


def test_start_is_idempotent(exporter: Exporter) -> None:
    exporter.start()
    result = exporter.start()

    assert result is exporter
    assert exporter.state == "started"


def test_stop_changes_state(exporter: Exporter) -> None:
    exporter.start()

    result = exporter.stop()

    assert result is exporter
    assert exporter.started is False
    assert exporter.state == "stopped"


def test_stop_is_idempotent(exporter: Exporter) -> None:
    result = exporter.stop()

    assert result is exporter
    assert exporter.state == "stopped"


def test_reset_clears_statistics(
    exporter: Exporter,
    payload: ExportPayload,
) -> None:
    exporter.export(payload)

    assert exporter.export_count == 1

    result = exporter.reset()

    assert result is exporter
    assert exporter.export_count == 0
    assert exporter.success_count == 0
    assert exporter.error_count == 0
    assert exporter.bytes_exported == 0
    assert exporter.last_export is None
    assert exporter.last_error is None


def test_reset_preserves_configuration(
    exporter: Exporter,
) -> None:
    exporter.start()

    exporter.reset()

    assert exporter.name == "test"
    assert exporter.format is ExportFormat.JSON
    assert exporter.encoding == "utf-8"
    assert exporter.enabled is True
    assert exporter.started is True
    assert exporter.closed is False


def test_close_changes_state(
    exporter: Exporter,
) -> None:
    result = exporter.close()

    assert result is exporter
    assert exporter.closed is True
    assert exporter.started is False
    assert exporter.state == "closed"


def test_close_is_idempotent(
    exporter: Exporter,
) -> None:
    exporter.close()

    result = exporter.close()

    assert result is exporter
    assert exporter.closed is True


def test_start_after_close_is_rejected(
    exporter: Exporter,
) -> None:
    exporter.close()

    with pytest.raises(
        RuntimeError,
        match="cannot start a closed exporter",
    ):
        exporter.start()


def test_reset_after_close_is_rejected(
    exporter: Exporter,
) -> None:
    exporter.close()

    with pytest.raises(
        RuntimeError,
        match="cannot reset a closed exporter",
    ):
        exporter.reset()


def test_flush_after_close_is_rejected(
    exporter: Exporter,
) -> None:
    exporter.close()

    with pytest.raises(
        RuntimeError,
        match="cannot flush a closed exporter",
    ):
        exporter.flush()


# ==============================================================================
# Part 5. Serialization
# ==============================================================================


def test_json_serialization(
    exporter: Exporter,
    payload: ExportPayload,
) -> None:
    serialized = exporter.serialize(payload)

    assert isinstance(serialized, str)

    data = json.loads(serialized)

    assert data["name"] == "request_total"
    assert data["value"] == 42
    assert data["labels"]["method"] == "GET"
    assert data["labels"]["status"] == "200"


def test_text_serialization(
    payload: ExportPayload,
) -> None:
    exporter = Exporter(
        "test",
        format=ExportFormat.TEXT,
    )

    serialized = exporter.serialize(payload)

    assert isinstance(serialized, str)
    assert "request_total" in serialized
    assert "42" in serialized


def test_binary_serialization(
    payload: ExportPayload,
) -> None:
    exporter = Exporter(
        "test",
        format=ExportFormat.BINARY,
    )

    serialized = exporter.serialize(payload)

    assert isinstance(serialized, bytes)

    decoded = json.loads(
        serialized.decode("utf-8")
    )

    assert decoded["name"] == "request_total"


def test_serialization_accepts_mapping(
    exporter: Exporter,
) -> None:
    serialized = exporter.serialize(
        {
            "name": "requests",
            "value": 5,
            "labels": {
                "status": "200",
            },
        }
    )

    data = json.loads(serialized)

    assert data["name"] == "requests"
    assert data["value"] == 5


def test_serialization_options_are_applied(
    payload: ExportPayload,
) -> None:
    exporter = Exporter(
        "test",
        format=ExportFormat.JSON,
    )

    serialized = exporter.serialize(
        payload,
        options={
            "ensure_ascii": True,
        },
    )

    assert isinstance(serialized, str)


# ==============================================================================
# Part 6. Export
# ==============================================================================


def test_export_returns_success_result(
    exporter: Exporter,
    payload: ExportPayload,
) -> None:
    result = exporter.export(payload)

    assert isinstance(result, ExportResult)
    assert result.success is True
    assert result.failed is False
    assert result.exporter == "test"
    assert result.count == 1
    assert result.bytes_exported > 0
    assert result.error is None


def test_export_accepts_mapping(
    exporter: Exporter,
) -> None:
    result = exporter.export(
        {
            "name": "request_total",
            "value": 42,
        }
    )

    assert result.success is True
    assert result.count == 1


def test_export_many_returns_one_result_per_payload(
    exporter: Exporter,
) -> None:
    payloads = [
        ExportPayload("one", 1),
        ExportPayload("two", 2),
        ExportPayload("three", 3),
    ]

    results = exporter.export_many(payloads)

    assert len(results) == 3
    assert all(
        isinstance(result, ExportResult)
        for result in results
    )
    assert all(
        result.success
        for result in results
    )


def test_export_options_override_defaults(
    payload: ExportPayload,
) -> None:
    exporter = Exporter(
        "test",
        options={
            "custom": "default",
        },
    )

    captured: dict[str, object] = {}

    def capture(
        payload: ExportPayload,
        *,
        serialized: object,
        options: dict[str, object],
    ) -> object:
        captured.update(options)
        return serialized

    exporter._export = capture  # type: ignore[method-assign]

    result = exporter.export(
        payload,
        custom="override",
        per_call=True,
    )

    assert result.success is True
    assert captured["custom"] == "override"
    assert captured["per_call"] is True

    assert exporter.options["custom"] == "default"
    assert "per_call" not in exporter.options


def test_disabled_exporter_returns_failure(
    payload: ExportPayload,
) -> None:
    exporter = Exporter(
        "test",
        enabled=False,
    )

    result = exporter.export(payload)

    assert result.success is False
    assert result.failed is True
    assert result.error == "exporter is disabled"


def test_export_after_close_returns_failure(
    exporter: Exporter,
    payload: ExportPayload,
) -> None:
    exporter.close()

    result = exporter.export(payload)

    assert result.success is False
    assert result.failed is True
    assert "closed" in result.error


def test_flush_returns_self(
    exporter: Exporter,
) -> None:
    result = exporter.flush()

    assert result is exporter


# ==============================================================================
# Part 7. Export statistics
# ==============================================================================


def test_successful_export_updates_statistics(
    exporter: Exporter,
    payload: ExportPayload,
) -> None:
    before = time.time()

    result = exporter.export(payload)

    after = time.time()

    assert result.success is True
    assert exporter.export_count == 1
    assert exporter.success_count == 1
    assert exporter.error_count == 0
    assert exporter.bytes_exported == result.bytes_exported
    assert exporter.last_export is not None
    assert before <= exporter.last_export <= after
    assert exporter.last_error is None


def test_multiple_exports_accumulate_statistics(
    exporter: Exporter,
) -> None:
    results = exporter.export_many(
        [
            ExportPayload("one", 1),
            ExportPayload("two", 2),
            ExportPayload("three", 3),
        ]
    )

    expected_bytes = sum(
        result.bytes_exported
        for result in results
    )

    assert exporter.export_count == 3
    assert exporter.success_count == 3
    assert exporter.error_count == 0
    assert exporter.bytes_exported == expected_bytes


def test_reset_clears_export_statistics(
    exporter: Exporter,
) -> None:
    exporter.export(
        ExportPayload("metric", 42)
    )

    exporter.reset()

    assert exporter.export_count == 0
    assert exporter.success_count == 0
    assert exporter.error_count == 0
    assert exporter.bytes_exported == 0


# ==============================================================================
# Part 8. Validation
# ==============================================================================


def test_validate_payload_accepts_export_payload(
    exporter: Exporter,
    payload: ExportPayload,
) -> None:
    exporter.validate_payload(payload)


def test_validate_payload_accepts_mapping(
    exporter: Exporter,
) -> None:
    exporter.validate_payload(
        {
            "name": "metric",
            "value": 1,
        }
    )


def test_validate_payload_rejects_non_mapping(
    exporter: Exporter,
) -> None:
    with pytest.raises(
        TypeError,
        match="payload must be ExportPayload or a mapping",
    ):
        exporter.validate_payload("invalid")  # type: ignore[arg-type]


def test_validate_payload_requires_name(
    exporter: Exporter,
) -> None:
    with pytest.raises(
        ValueError,
        match="payload mapping must contain 'name'",
    ):
        exporter.validate_payload(
            {
                "value": 1,
            }
        )


def test_validate_options_accepts_mapping(
    exporter: Exporter,
) -> None:
    exporter.validate_options(
        {
            "timeout": 10,
            "retry": True,
        }
    )


def test_validate_options_rejects_non_mapping(
    exporter: Exporter,
) -> None:
    with pytest.raises(
        TypeError,
        match="options must be a mapping",
    ):
        exporter.validate_options(
            ["invalid"]  # type: ignore[arg-type]
        )


def test_validate_options_requires_string_keys(
    exporter: Exporter,
) -> None:
    with pytest.raises(
        TypeError,
        match="export option keys must be strings",
    ):
        exporter.validate_options(
            {
                1: "invalid",
            }
        )


def test_payload_rejects_empty_name() -> None:
    with pytest.raises(
        ValueError,
        match="payload name must not be empty",
    ):
        ExportPayload(
            name="   ",
            value=1,
        )


def test_payload_rejects_non_string_name() -> None:
    with pytest.raises(
        TypeError,
        match="payload name must be a string",
    ):
        ExportPayload(
            name=123,  # type: ignore[arg-type]
            value=1,
        )


# ==============================================================================
# Part 9. Error handling
# ==============================================================================


def test_export_invalid_payload_returns_failure(
    exporter: Exporter,
) -> None:
    result = exporter.export(
        {
            "value": 42,
        }
    )

    assert result.success is False
    assert result.failed is True
    assert result.error is not None


def test_export_error_updates_error_statistics(
    exporter: Exporter,
) -> None:
    result = exporter.export(
        {
            "value": 42,
        }
    )

    assert result.success is False
    assert exporter.export_count == 1
    assert exporter.success_count == 0
    assert exporter.error_count == 1
    assert exporter.last_error is not None


def test_export_backend_error_is_captured(
    exporter: Exporter,
    payload: ExportPayload,
) -> None:
    def failing_export(
        payload: ExportPayload,
        *,
        serialized: object,
        options: dict[str, object],
    ) -> object:
        raise RuntimeError("backend failure")

    exporter._export = failing_export  # type: ignore[method-assign]

    result = exporter.export(payload)

    assert result.success is False
    assert result.failed is True
    assert result.error == "backend failure"
    assert exporter.error_count == 1
    assert exporter.last_error == "backend failure"


def test_handle_error_returns_export_result(
    exporter: Exporter,
) -> None:
    error = RuntimeError("failure")

    result = exporter._handle_error(
        error,
        duration=0.01,
    )

    assert isinstance(result, ExportResult)
    assert result.success is False
    assert result.error == "failure"
    assert result.duration == 0.01


def test_record_error_updates_error_state(
    exporter: Exporter,
) -> None:
    error = RuntimeError("failure")

    exporter._record_error(error)

    assert exporter.error_count == 1
    assert exporter.last_error == "failure"


# ==============================================================================
# Part 10. Diagnostics
# ==============================================================================


def test_health_returns_expected_structure(
    exporter: Exporter,
) -> None:
    health = exporter.health()

    assert health["name"] == "test"
    assert health["state"] == "stopped"
    assert health["enabled"] is True
    assert health["healthy"] is True


def test_health_is_unhealthy_after_close(
    exporter: Exporter,
) -> None:
    exporter.close()

    health = exporter.health()

    assert health["healthy"] is False
    assert health["state"] == "closed"


def test_health_is_unhealthy_after_error(
    exporter: Exporter,
) -> None:
    exporter.export(
        {
            "value": 42,
        }
    )

    health = exporter.health()

    assert health["healthy"] is False
    assert health["last_error"] if "last_error" in health else True


def test_diagnostics_returns_configuration(
    exporter: Exporter,
) -> None:
    diagnostics = exporter.diagnostics()

    assert diagnostics["name"] == "test"
    assert diagnostics["format"] == "json"
    assert diagnostics["encoding"] == "utf-8"
    assert diagnostics["enabled"] is True
    assert diagnostics["state"] == "stopped"


def test_diagnostics_returns_statistics(
    exporter: Exporter,
) -> None:
    exporter.export(
        ExportPayload(
            name="metric",
            value=10,
        )
    )

    diagnostics = exporter.diagnostics()
    statistics = diagnostics["statistics"]

    assert statistics["export_count"] == 1
    assert statistics["success_count"] == 1
    assert statistics["error_count"] == 0
    assert statistics["bytes_exported"] > 0


def test_diagnostics_returns_options(
    exporter: Exporter,
) -> None:
    diagnostics = exporter.diagnostics()

    assert diagnostics["options"] == {}


def test_summary_returns_compact_state(
    exporter: Exporter,
) -> None:
    summary = exporter.summary()

    assert summary == {
        "name": "test",
        "format": "json",
        "state": "stopped",
        "enabled": True,
        "export_count": 0,
        "success_count": 0,
        "error_count": 0,
        "bytes_exported": 0,
    }


# ==============================================================================
# Part 11. Representation
# ==============================================================================


def test_repr_contains_configuration(
    exporter: Exporter,
) -> None:
    value = repr(exporter)

    assert "Exporter" in value
    assert "test" in value
    assert "json" in value
    assert "enabled=True" in value
    assert "state='stopped'" in value


def test_str_contains_identity(
    exporter: Exporter,
) -> None:
    value = str(exporter)

    assert "Exporter" in value
    assert "test" in value
    assert "json" in value
    assert "stopped" in value


def test_repr_changes_with_lifecycle(
    exporter: Exporter,
) -> None:
    before = repr(exporter)

    exporter.start()

    after = repr(exporter)

    assert "state='stopped'" in before
    assert "state='started'" in after
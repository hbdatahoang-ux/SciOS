# ==============================================================================
# SciOS Runtime Exporter Tests
# ==============================================================================

from __future__ import annotations

from typing import Any

import pytest

from scios.runtime.observability.tracing.exporter import (
    ExportError,
    ExportFormat,
    Exporter,
)


# ==============================================================================
# Part 1. Fixtures
# ==============================================================================


@pytest.fixture
def exporter() -> Exporter:
    """Create a JSON exporter for tests."""
    return Exporter(
        name="test",
        format=ExportFormat.JSON,
    )


@pytest.fixture
def payload() -> dict[str, Any]:
    """Return a valid export payload."""
    return {
        "name": "request_total",
        "value": 42,
        "labels": {
            "method": "GET",
            "status": "200",
        },
    }


@pytest.fixture
def invalid_payload() -> object:
    """Return an object that cannot represent a valid payload."""
    return object()

# ==============================================================================
# Part 2. Construction
# ==============================================================================


def test_default_constructor():

    instance = Exporter()

    assert instance.name == "exporter"
    assert instance.format is ExportFormat.JSON
    assert instance.encoding == "utf-8"
    assert instance.enabled is True
    assert isinstance(instance.options, dict)
    assert instance.state == "created"


def test_custom_constructor():

    instance = Exporter(
        name="metrics",
        format=ExportFormat.JSON,
        encoding="utf-8",
        enabled=False,
        options={
            "indent": 2,
        },
    )

    assert instance.name == "metrics"
    assert instance.format is ExportFormat.JSON
    assert instance.encoding == "utf-8"
    assert instance.enabled is False
    assert instance.options["indent"] == 2
    assert instance.state == "created"


def test_invalid_configuration():

    with pytest.raises(
        (TypeError, ValueError),
    ):
        Exporter(
            name="",
        )

    with pytest.raises(
        (TypeError, ValueError),
    ):
        Exporter(
            encoding="invalid-encoding",
        )


# ==============================================================================
# Part 3. Properties
# ==============================================================================


def test_name(exporter):

    assert exporter.name == "test"


def test_format(exporter):

    assert exporter.format is ExportFormat.JSON


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

    exporter.options["indent"] = 2

    assert exporter.options["indent"] == 2


def test_state(exporter):

    assert exporter.state == "created"


# ==============================================================================
# Part 4. Lifecycle
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

    exporter.start()

    result = exporter.reset()

    assert result is exporter
    assert exporter.state == "created"
    assert exporter.export_count == 0
    assert exporter.success_count == 0
    assert exporter.error_count == 0
    assert exporter.bytes_exported == 0
    assert exporter.last_export is None


def test_close(exporter):

    exporter.start()

    result = exporter.close()

    assert result is exporter
    assert exporter.state == "closed"


# ==============================================================================
# Part 5. Export
# ==============================================================================


def test_export(
    exporter,
    payload,
):

    exporter.start()

    result = exporter.export(
        payload,
    )

    assert result is not None
    assert exporter.export_count == 1
    assert exporter.success_count == 1
    assert exporter.error_count == 0
    assert exporter.bytes_exported > 0
    assert exporter.last_export is not None


def test_export_many(
    exporter,
    payload,
):

    exporter.start()

    payloads = [
        payload,
        {
            "name": "request_errors",
            "value": 3,
        },
        {
            "name": "latency",
            "value": 12.5,
        },
    ]

    result = exporter.export_many(
        payloads,
    )

    assert result is not None
    assert len(result) == len(payloads)

    assert exporter.export_count == 3
    assert exporter.success_count == 3
    assert exporter.error_count == 0
    assert exporter.bytes_exported > 0
    assert exporter.last_export is not None


def test_serialize(
    exporter,
    payload,
):

    result = exporter.serialize(
        payload,
    )

    assert result is not None

    if isinstance(
        result,
        bytes,
    ):
        assert result

    else:
        assert isinstance(
            result,
            str,
        )
        assert result


def test_flush(
    exporter,
    payload,
):

    exporter.start()

    exporter.export(
        payload,
    )

    result = exporter.flush()

    assert result is not None

# ==============================================================================
# Part 6. Validation
# ==============================================================================


def test_validate(exporter):

    result = exporter.validate()

    assert result is True


def test_validate_payload(
    exporter,
    payload,
    invalid_payload,
):

    assert exporter.validate_payload(
        payload,
    ) is True

    assert exporter.validate_payload(
        invalid_payload,
    ) is False


def test_validate_options(exporter):

    assert exporter.validate_options() is True

    exporter.options["indent"] = 2

    assert exporter.validate_options() is True


# ==============================================================================
# Part 7. Errors
# ==============================================================================


def test_export_error(
    exporter,
    invalid_payload,
):

    exporter.start()

    with pytest.raises(
        (ExportError, TypeError, ValueError),
    ):
        exporter.export(
            invalid_payload,
        )


def test_invalid_payload(
    exporter,
    invalid_payload,
):

    assert exporter.validate_payload(
        invalid_payload,
    ) is False


def test_error_count(
    exporter,
    invalid_payload,
):

    exporter.start()

    initial = exporter.error_count

    with pytest.raises(
        (ExportError, TypeError, ValueError),
    ):
        exporter.export(
            invalid_payload,
        )

    assert exporter.error_count == initial + 1


# ==============================================================================
# Part 8. Statistics
# ==============================================================================


def test_export_count(
    exporter,
    payload,
):

    exporter.start()

    assert exporter.export_count == 0

    exporter.export(
        payload,
    )

    assert exporter.export_count == 1

    exporter.export(
        payload,
    )

    assert exporter.export_count == 2


def test_success_count(
    exporter,
    payload,
):

    exporter.start()

    assert exporter.success_count == 0

    exporter.export(
        payload,
    )

    assert exporter.success_count == 1


def test_error_count(
    exporter,
    invalid_payload,
):

    exporter.start()

    assert exporter.error_count == 0

    with pytest.raises(
        (ExportError, TypeError, ValueError),
    ):
        exporter.export(
            invalid_payload,
        )

    assert exporter.error_count == 1


def test_bytes_exported(
    exporter,
    payload,
):

    exporter.start()

    assert exporter.bytes_exported == 0

    exporter.export(
        payload,
    )

    assert exporter.bytes_exported > 0


def test_last_export(
    exporter,
    payload,
):

    exporter.start()

    assert exporter.last_export is None

    exporter.export(
        payload,
    )

    assert exporter.last_export is not None


# ==============================================================================
# Part 9. Diagnostics
# ==============================================================================


def test_health(exporter):

    assert exporter.health() is True

    exporter.close()

    assert exporter.health() is False


def test_diagnostics(exporter):

    diagnostics = exporter.diagnostics()

    assert isinstance(
        diagnostics,
        dict,
    )

    assert "name" in diagnostics
    assert "format" in diagnostics
    assert "encoding" in diagnostics
    assert "enabled" in diagnostics
    assert "state" in diagnostics
    assert "export_count" in diagnostics
    assert "success_count" in diagnostics
    assert "error_count" in diagnostics
    assert "bytes_exported" in diagnostics
    assert "last_export" in diagnostics


def test_summary(exporter):

    summary = exporter.summary()

    assert isinstance(
        summary,
        dict,
    )

    assert summary["name"] == exporter.name
    assert summary["state"] == exporter.state
    assert summary["export_count"] == exporter.export_count
    assert summary["success_count"] == exporter.success_count
    assert summary["error_count"] == exporter.error_count


# ==============================================================================
# Part 10. Representation
# ==============================================================================


def test_repr(exporter):

    value = repr(
        exporter,
    )

    assert isinstance(
        value,
        str,
    )

    assert "Exporter" in value
    assert exporter.name in value


def test_str(exporter):

    value = str(
        exporter,
    )

    assert isinstance(
        value,
        str,
    )

    assert exporter.name in value

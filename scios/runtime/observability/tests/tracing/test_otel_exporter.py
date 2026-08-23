# ==============================================================================
# SciOS Runtime Observability
# OpenTelemetry Exporter Tests
# ==============================================================================

from __future__ import annotations

import pytest

from scios.runtime.observability.tracing.otel import (
    OTELExportError,
    OTELExporter,
)
from scios.runtime.observability.tracing.exporter import (
    ExportFormat,
)


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def exporter() -> OTELExporter:
    return OTELExporter()


@pytest.fixture
def payload() -> dict[str, object]:
    return {
        "service": "scios",
        "trace_id": "abc123",
        "value": 42,
    }


# ==============================================================================
# Part 1. Construction
# ==============================================================================


def test_default_construction():

    exporter = OTELExporter()

    assert exporter.name == "otel"
    assert exporter.endpoint == "http://localhost:4318"
    assert exporter.encoding == "utf-8"
    assert exporter.enabled is True
    assert exporter.state == "created"
    assert exporter.format is ExportFormat.JSON


def test_custom_name():

    exporter = OTELExporter(
        name="test-otel",
    )

    assert exporter.name == "test-otel"


def test_custom_endpoint():

    exporter = OTELExporter(
        endpoint="http://otel.example:4318",
    )

    assert exporter.endpoint == (
        "http://otel.example:4318"
    )


def test_custom_encoding():

    exporter = OTELExporter(
        encoding="utf-16",
    )

    assert exporter.encoding == "utf-16"


def test_disabled_exporter():

    exporter = OTELExporter(
        enabled=False,
    )

    assert exporter.enabled is False


def test_custom_options():

    exporter = OTELExporter(
        options={
            "indent": 2,
            "ensure_ascii": True,
            "sort_keys": True,
        },
    )

    assert exporter.options["indent"] == 2
    assert exporter.options["ensure_ascii"] is True
    assert exporter.options["sort_keys"] is True


# ==============================================================================
# Part 2. Configuration
# ==============================================================================


def test_name(exporter):

    assert exporter.name == "otel"


def test_endpoint(exporter):

    assert exporter.endpoint == (
        "http://localhost:4318"
    )


def test_encoding(exporter):

    assert exporter.encoding == "utf-8"


def test_enabled(exporter):

    assert exporter.enabled is True

    exporter.enabled = False

    assert exporter.enabled is False


def test_options(exporter):

    assert isinstance(
        exporter.options,
        dict,
    )


# ==============================================================================
# Part 3. Export
# ==============================================================================


def test_export_mapping(
    exporter,
):

    result = exporter.export(
        {
            "id": 1,
            "name": "test",
        },
    )

    assert result.success is True
    assert result.format is ExportFormat.JSON
    assert result.payload is not None


def test_export_payload(
    exporter,
    payload,
):

    result = exporter.export(
        payload,
    )

    assert result.success is True
    assert isinstance(
        result.payload,
        str,
    )


def test_export_result(
    exporter,
):

    result = exporter.export(
        {"value": 42},
    )

    assert result.success is True
    assert result.error is None
    assert result.bytes_exported > 0


def test_export_bytes(
    exporter,
):

    result = exporter.export(
        b"otel-data",
    )

    assert result.success is True
    assert isinstance(
        result.payload,
        str,
    )
    assert result.bytes_exported > 0


def test_export_many(
    exporter,
):

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

    assert exporter.export_count == 3
    assert exporter.success_count == 3


# ==============================================================================
# Part 4. Serialization
# ==============================================================================


def test_serialize_mapping(
    exporter,
):

    result = exporter.serialize(
        {
            "id": 1,
            "value": "hello",
        },
    )

    assert isinstance(
        result,
        str,
    )

    assert '"id"' in result
    assert '"value"' in result


def test_serialize_list(
    exporter,
):

    result = exporter.serialize(
        [1, 2, 3],
    )

    assert result == "[1, 2, 3]"


def test_serialize_string(
    exporter,
):

    result = exporter.serialize(
        "hello",
    )

    assert result == '"hello"'


def test_serialize_bytes(
    exporter,
):

    result = exporter.serialize(
        b"hello",
    )

    assert isinstance(
        result,
        str,
    )

    assert "hello" in result


def test_serialize_none(
    exporter,
):

    result = exporter.serialize(
        None,
    )

    assert result == "null"


# ==============================================================================
# Part 5. Validation
# ==============================================================================


def test_valid_payload(
    exporter,
):

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
        None,
    ) is True


def test_invalid_payload(
    exporter,
):

    invalid = object()

    assert exporter.validate_payload(
        invalid,
    ) is False


def test_invalid_options(
    exporter,
):

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


def test_start(
    exporter,
):

    result = exporter.start()

    assert result is exporter
    assert exporter.state == "running"


def test_stop(
    exporter,
):

    exporter.start()

    result = exporter.stop()

    assert result is exporter
    assert exporter.state == "stopped"


def test_reset(
    exporter,
):

    exporter.export(
        {"id": 1},
    )

    assert exporter.export_count == 1

    result = exporter.reset()

    assert result is exporter
    assert exporter.state == "created"
    assert exporter.export_count == 0
    assert exporter.success_count == 0
    assert exporter.error_count == 0
    assert exporter.bytes_exported == 0


def test_close(
    exporter,
):

    result = exporter.close()

    assert result is exporter
    assert exporter.state == "closed"


def test_export_after_close(
    exporter,
):

    exporter.close()

    with pytest.raises(
        OTELExportError,
    ):
        exporter.export(
            {"id": 1},
        )

# ==============================================================================
# Part 7. Error Handling
# ==============================================================================


    def _handle_error(
        self,
        error: OTELExportError,
    ) -> ExportResult:
        """
        Record an OTEL export error and return a failed result.
        """

        self._record_error(
            error,
        )

        return ExportResult(
            success=False,
            payload=None,
            format=self._format,
            bytes_exported=0,
            error=error,
        )


    def _record_error(
        self,
        error: OTELExportError,
    ) -> None:
        """
        Record exporter error state.
        """

        self._error_count += 1
        self._last_error = error


    def _validate_endpoint(
        self,
        endpoint: str,
    ) -> bool:
        """
        Validate OTEL endpoint.

        Endpoint must be a non-empty string.
        """

        if not isinstance(
            endpoint,
            str,
        ):
            return False

        endpoint = endpoint.strip()

        if not endpoint:
            return False

        if "://" not in endpoint:
            return False

        return True


# ==============================================================================
# Part 8. Statistics
# ==============================================================================


    @property
    def export_count(
        self,
    ) -> int:
        """
        Return total export attempts.
        """

        return self._export_count


    @property
    def success_count(
        self,
    ) -> int:
        """
        Return successful export count.
        """

        return self._success_count


    @property
    def error_count(
        self,
    ) -> int:
        """
        Return failed export count.
        """

        return self._error_count


    @property
    def bytes_exported(
        self,
    ) -> int:
        """
        Return total number of successfully exported bytes.
        """

        return self._bytes_exported


# ==============================================================================
# Part 9. Diagnostics
# ==============================================================================


    def health(
        self,
    ) -> bool:
        """
        Return OTEL exporter health status.
        """

        return (
            self._state != "closed"
            and self._state != "failed"
            and self._enabled
            and self._validate_endpoint(
                self._endpoint,
            )
        )


    def diagnostics(
        self,
    ) -> dict[str, Any]:
        """
        Return detailed OTEL exporter diagnostics.
        """

        return {
            "name": self._name,
            "endpoint": self._endpoint,
            "encoding": self._encoding,
            "enabled": self._enabled,
            "state": self._state,
            "healthy": self.health(),
            "export_count": self._export_count,
            "success_count": self._success_count,
            "error_count": self._error_count,
            "bytes_exported": self._bytes_exported,
            "last_export": self._last_export,
            "last_error": (
                str(self._last_error)
                if self._last_error is not None
                else None
            ),
        }


    def summary(
        self,
    ) -> dict[str, Any]:
        """
        Return a compact OTEL exporter summary.
        """

        return {
            "name": self._name,
            "endpoint": self._endpoint,
            "state": self._state,
            "enabled": self._enabled,
            "healthy": self.health(),
            "export_count": self._export_count,
            "success_count": self._success_count,
            "error_count": self._error_count,
            "bytes_exported": self._bytes_exported,
        }


# ==============================================================================
# Part 10. Representation
# ==============================================================================


    def __repr__(
        self,
    ) -> str:
        """
        Return an unambiguous representation.
        """

        return (
            f"{type(self).__name__}("
            f"name={self._name!r}, "
            f"endpoint={self._endpoint!r}, "
            f"encoding={self._encoding!r}, "
            f"enabled={self._enabled!r}, "
            f"state={self._state!r}"
            f")"
        )


    def __str__(
        self,
    ) -> str:
        """
        Return a human-readable representation.
        """

        return (
            f"{self._name}("
            f"endpoint={self._endpoint}, "
            f"state={self._state}, "
            f"enabled={self._enabled}"
            f")"
        )


# ==============================================================================
# Part 11. End
# ==============================================================================


__all__ = [
    "OTELExporter",
    "OTELExportError",
]

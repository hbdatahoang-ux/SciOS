# ==============================================================================
# SciOS Runtime Observability
# JSON Exporter Tests
# ==============================================================================

from __future__ import annotations

import io
import json

import pytest

from scios.runtime.observability.exporters.base import (
    ExportFormat,
    ExportPayload,
    ExportResult,
)
from scios.runtime.observability.exporters.json import (
    JSONExportOptions,
    JSONExporter,
    JSON_EXPORTER_VERSION,
)


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def exporter() -> JSONExporter:
    return JSONExporter()


@pytest.fixture
def payload() -> ExportPayload:
    return ExportPayload(
        name="request_total",
        value=42,
        labels={
            "method": "GET",
            "status": "200",
        },
    )


@pytest.fixture
def stream() -> io.StringIO:
    return io.StringIO()


# ==============================================================================
# Part 1. Construction
# ==============================================================================


def test_default_name() -> None:
    exporter = JSONExporter()

    assert exporter.name == "json"


def test_custom_name() -> None:
    exporter = JSONExporter(name="custom")

    assert exporter.name == "custom"


def test_export_format(
    exporter: JSONExporter,
) -> None:
    assert exporter.format == ExportFormat.JSON


def test_encoding(
    exporter: JSONExporter,
) -> None:
    assert exporter.encoding == "utf-8"


def test_version(
    exporter: JSONExporter,
) -> None:
    assert exporter.version == JSON_EXPORTER_VERSION


def test_default_options(
    exporter: JSONExporter,
) -> None:
    assert exporter.ensure_ascii is False
    assert exporter.indent is None
    assert exporter.sort_keys is False


def test_custom_options() -> None:
    options = JSONExportOptions(
        ensure_ascii=True,
        indent=2,
        sort_keys=True,
    )

    exporter = JSONExporter(
        name="custom",
        options=options,
    )

    assert exporter.ensure_ascii is True
    assert exporter.indent == 2
    assert exporter.sort_keys is True


def test_options_are_exposed_through_base_property(
    exporter: JSONExporter,
) -> None:
    options = exporter.options

    assert options["ensure_ascii"] is False
    assert options["indent"] is None
    assert options["sort_keys"] is False


# ==============================================================================
# Part 2. Serialization
# ==============================================================================


def test_serialize_string(
    exporter: JSONExporter,
) -> None:
    result = exporter.serialize("hello")

    assert result == '"hello"'


def test_serialize_integer(
    exporter: JSONExporter,
) -> None:
    assert exporter.serialize(42) == "42"


def test_serialize_float(
    exporter: JSONExporter,
) -> None:
    assert exporter.serialize(3.14) == "3.14"


def test_serialize_boolean(
    exporter: JSONExporter,
) -> None:
    assert exporter.serialize(True) == "true"


def test_serialize_none(
    exporter: JSONExporter,
) -> None:
    assert exporter.serialize(None) == "null"


def test_serialize_mapping(
    exporter: JSONExporter,
) -> None:
    result = exporter.serialize(
        {
            "name": "test",
            "value": 42,
        }
    )

    assert json.loads(result) == {
        "name": "test",
        "value": 42,
    }


def test_serialize_list(
    exporter: JSONExporter,
) -> None:
    result = exporter.serialize([1, 2, 3])

    assert json.loads(result) == [1, 2, 3]


def test_serialize_unicode(
    exporter: JSONExporter,
) -> None:
    result = exporter.serialize("Xin chào Việt Nam")

    assert result == '"Xin chào Việt Nam"'


def test_deserialize_mapping(
    exporter: JSONExporter,
) -> None:
    result = exporter.deserialize(
        '{"name": "test", "value": 42}'
    )

    assert result == {
        "name": "test",
        "value": 42,
    }


def test_deserialize_list(
    exporter: JSONExporter,
) -> None:
    assert exporter.deserialize("[1, 2, 3]") == [1, 2, 3]


def test_deserialize_string(
    exporter: JSONExporter,
) -> None:
    assert exporter.deserialize('"hello"') == "hello"


def test_deserialize_none(
    exporter: JSONExporter,
) -> None:
    assert exporter.deserialize("null") is None


def test_deserialize_rejects_non_string(
    exporter: JSONExporter,
) -> None:
    with pytest.raises(TypeError):
        exporter.deserialize(123)  # type: ignore[arg-type]


def test_deserialize_invalid_json(
    exporter: JSONExporter,
) -> None:
    with pytest.raises(ValueError):
        exporter.deserialize("{invalid json}")


# ==============================================================================
# Part 3. Encode / Decode
# ==============================================================================


def test_encode_matches_serialize(
    exporter: JSONExporter,
) -> None:
    value = {
        "name": "test",
        "value": 42,
    }

    assert exporter.encode(value) == exporter.serialize(value)


def test_decode_matches_deserialize(
    exporter: JSONExporter,
) -> None:
    text = '{"name": "test", "value": 42}'

    assert exporter.decode(text) == exporter.deserialize(text)


def test_decode_rejects_non_string(
    exporter: JSONExporter,
) -> None:
    with pytest.raises(TypeError):
        exporter.decode(123)  # type: ignore[arg-type]


# ==============================================================================
# Part 4. JSON Configuration
# ==============================================================================


def test_ensure_ascii() -> None:
    exporter = JSONExporter(
        options=JSONExportOptions(
            ensure_ascii=True,
        )
    )

    result = exporter.serialize("Xin chào")

    assert "\\u" in result


def test_disable_ensure_ascii() -> None:
    exporter = JSONExporter(
        options=JSONExportOptions(
            ensure_ascii=False,
        )
    )

    result = exporter.serialize("Xin chào")

    assert "Xin chào" in result


def test_indent() -> None:
    exporter = JSONExporter(
        options=JSONExportOptions(
            indent=2,
        )
    )

    result = exporter.serialize(
        {
            "name": "test",
            "value": 42,
        }
    )

    assert "\n" in result
    assert "  " in result


def test_sort_keys() -> None:
    exporter = JSONExporter(
        options=JSONExportOptions(
            sort_keys=True,
        )
    )

    result = exporter.serialize(
        {
            "z": 1,
            "a": 2,
        }
    )

    assert result.index('"a"') < result.index('"z"')


# ==============================================================================
# Part 5. Validation
# ==============================================================================


def test_validate_output_accepts_json(
    exporter: JSONExporter,
) -> None:
    assert exporter.validate_output('{"value": 42}')


def test_validate_output_rejects_invalid_json(
    exporter: JSONExporter,
) -> None:
    assert exporter.validate_output("{invalid}") is False


def test_validate_output_rejects_non_string(
    exporter: JSONExporter,
) -> None:
    assert exporter.validate_output(123) is False


def test_validate_output_raise_error(
    exporter: JSONExporter,
) -> None:
    with pytest.raises((TypeError, ValueError)):
        exporter.validate_output(
            123,
            raise_error=True,
        )


def test_validate_payload(
    exporter: JSONExporter,
    payload: ExportPayload,
) -> None:
    assert exporter.validate_payload(payload)


def test_validate_mapping_payload(
    exporter: JSONExporter,
) -> None:
    assert exporter.validate_payload(
        {
            "name": "test",
            "value": 42,
        }
    )


# ==============================================================================
# Part 6. Export
# ==============================================================================


def test_export_returns_export_result(
    exporter: JSONExporter,
    payload: ExportPayload,
) -> None:
    result = exporter.export(payload)

    assert isinstance(result, ExportResult)
    assert result.success is True


def test_export_payload(
    exporter: JSONExporter,
    payload: ExportPayload,
) -> None:
    result = exporter.export_payload(payload)

    assert isinstance(result, ExportResult)
    assert result.success is True


def test_export_mapping(
    exporter: JSONExporter,
) -> None:
    result = exporter.export(
        {
            "name": "request_total",
            "value": 42,
        }
    )

    assert result.success is True


def test_export_contains_payload_name(
    exporter: JSONExporter,
    payload: ExportPayload,
) -> None:
    result = exporter.export(payload)

    assert result.success
    assert result.data is not None
    assert "request_total" in result.data


def test_export_output_is_valid_json(
    exporter: JSONExporter,
    payload: ExportPayload,
) -> None:
    result = exporter.export(payload)

    assert result.success
    assert result.data is not None

    decoded = json.loads(result.data)

    assert isinstance(decoded, dict)
    assert decoded["name"] == "request_total"
    assert decoded["value"] == 42


def test_export_updates_statistics(
    exporter: JSONExporter,
    payload: ExportPayload,
) -> None:
    result = exporter.export(payload)

    assert result.success
    assert exporter.export_count == 1
    assert exporter.success_count == 1
    assert exporter.failure_count == 0


def test_export_many(
    exporter: JSONExporter,
) -> None:
    payloads = [
        ExportPayload(name="one", value=1),
        ExportPayload(name="two", value=2),
        ExportPayload(name="three", value=3),
    ]

    results = exporter.export_many(payloads)

    assert len(results) == 3
    assert all(result.success for result in results)


def test_export_many_preserves_order(
    exporter: JSONExporter,
) -> None:
    payloads = [
        ExportPayload(name="first", value=1),
        ExportPayload(name="second", value=2),
        ExportPayload(name="third", value=3),
    ]

    results = exporter.export_many(payloads)

    names = [
        json.loads(result.data)["name"]
        for result in results
        if result.data is not None
    ]

    assert names == [
        "first",
        "second",
        "third",
    ]


# ==============================================================================
# Part 7. Convenience API
# ==============================================================================


def test_export_object(
    exporter: JSONExporter,
) -> None:
    result = exporter.export_object(
        {
            "value": 42,
        }
    )

    assert result.success


def test_export_dict(
    exporter: JSONExporter,
) -> None:
    result = exporter.export_dict(
        {
            "value": 42,
        }
    )

    assert result.success


def test_export_list(
    exporter: JSONExporter,
) -> None:
    result = exporter.export_list(
        [1, 2, 3]
    )

    assert result.success


def test_call_exports_object(
    exporter: JSONExporter,
) -> None:
    result = exporter(
        {
            "value": 42,
        }
    )

    assert isinstance(result, ExportResult)
    assert result.success


# ==============================================================================
# Part 8. Snapshot / State
# ==============================================================================


def test_snapshot_contains_json_state(
    exporter: JSONExporter,
    payload: ExportPayload,
) -> None:
    exporter.export(payload)

    snapshot = exporter.snapshot()

    assert snapshot["format"] == "json"
    assert snapshot["version"] == JSON_EXPORTER_VERSION
    assert "json" in snapshot

    state = snapshot["json"]

    assert state["objects_exported"] > 0
    assert state["bytes_written"] > 0


def test_len(
    exporter: JSONExporter,
    payload: ExportPayload,
) -> None:
    assert len(exporter) == 0

    exporter.export(payload)

    assert len(exporter) == 1


# ==============================================================================
# Part 9. JSON Round Trip
# ==============================================================================


def test_round_trip_mapping(
    exporter: JSONExporter,
) -> None:
    value = {
        "name": "request_total",
        "value": 42,
        "labels": {
            "method": "GET",
            "status": "200",
        },
    }

    encoded = exporter.encode(value)
    decoded = exporter.decode(encoded)

    assert decoded == value


def test_round_trip_unicode(
    exporter: JSONExporter,
) -> None:
    value = {
        "message": "Xin chào Việt Nam",
        "scientist": "Ω",
    }

    encoded = exporter.encode(value)
    decoded = exporter.decode(encoded)

    assert decoded == value


def test_round_trip_nested_structure(
    exporter: JSONExporter,
) -> None:
    value = {
        "trace": {
            "id": "abc",
            "spans": [
                {
                    "name": "root",
                    "duration": 1.25,
                },
                {
                    "name": "child",
                    "duration": 0.42,
                },
            ],
        }
    }

    assert exporter.decode(
        exporter.encode(value)
    ) == value


# ==============================================================================
# Part 10. Representation
# ==============================================================================


def test_repr(
    exporter: JSONExporter,
) -> None:
    text = repr(exporter)

    assert "JSONExporter" in text
    assert "json" in text.lower()
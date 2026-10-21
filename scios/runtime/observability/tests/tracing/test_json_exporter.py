# ==============================================================================
# SciOS Runtime Observability
# JSON Exporter Tests
# ==============================================================================

from __future__ import annotations

import json

import pytest

from scios.runtime.observability.tracing.exporter import (
    ExportError,
    ExportFormat,
    ExportResult,
)

from scios.runtime.observability.tracing.json_exporter import (
    JSONExporter,
)


# ==============================================================================
# Part 1. Construction
# ==============================================================================


def test_default_construction():

    exporter = JSONExporter()

    assert isinstance(
        exporter,
        JSONExporter,
    )

    assert exporter.name == "json"
    assert exporter.format is ExportFormat.JSON
    assert exporter.encoding == "utf-8"
    assert exporter.ensure_ascii is False
    assert exporter.indent == 2
    assert exporter.sort_keys is False
    assert exporter.enabled is True
    assert exporter.state == "created"


def test_custom_name():

    exporter = JSONExporter(
        name="test-json",
    )

    assert exporter.name == "test-json"


def test_custom_encoding():

    exporter = JSONExporter(
        encoding="utf-16",
    )

    assert exporter.encoding == "utf-16"


def test_custom_indent():

    exporter = JSONExporter(
        indent=4,
    )

    assert exporter.indent == 4


def test_custom_ensure_ascii():

    exporter = JSONExporter(
        ensure_ascii=True,
    )

    assert exporter.ensure_ascii is True


def test_custom_sort_keys():

    exporter = JSONExporter(
        sort_keys=True,
    )

    assert exporter.sort_keys is True


# ==============================================================================
# Part 2. Configuration
# ==============================================================================


def test_name():

    exporter = JSONExporter(
        name="memory-json",
    )

    assert exporter.name == "memory-json"


def test_encoding():

    exporter = JSONExporter(
        encoding="utf-16",
    )

    assert exporter.encoding == "utf-16"


def test_ensure_ascii():

    exporter = JSONExporter(
        ensure_ascii=True,
    )

    assert exporter.ensure_ascii is True


def test_indent():

    exporter = JSONExporter(
        indent=4,
    )

    assert exporter.indent == 4


def test_sort_keys():

    exporter = JSONExporter(
        sort_keys=True,
    )

    assert exporter.sort_keys is True


def test_invalid_ensure_ascii():

    with pytest.raises(
        TypeError,
    ):
        JSONExporter(
            ensure_ascii="yes",
        )


def test_invalid_indent():

    with pytest.raises(
        (TypeError, ValueError),
    ):
        JSONExporter(
            indent=-1,
        )


def test_invalid_sort_keys():

    with pytest.raises(
        TypeError,
    ):
        JSONExporter(
            sort_keys="yes",
        )


# ==============================================================================
# Part 3. JSON Serialization
# ==============================================================================


def test_serialize_mapping():

    exporter = JSONExporter()

    result = exporter.serialize_mapping(
        {
            "id": 1,
            "value": "hello",
        },
    )

    assert isinstance(
        result,
        str,
    )

    assert json.loads(
        result,
    ) == {
        "id": 1,
        "value": "hello",
    }


def test_serialize_list():

    exporter = JSONExporter()

    result = exporter.serialize(
        [
            1,
            2,
            3,
        ],
    )

    assert json.loads(
        result,
    ) == [
        1,
        2,
        3,
    ]


def test_serialize_tuple():

    exporter = JSONExporter()

    result = exporter.serialize(
        (
            1,
            2,
            3,
        ),
    )

    assert json.loads(
        result,
    ) == [
        1,
        2,
        3,
    ]


def test_serialize_string():

    exporter = JSONExporter()

    result = exporter.serialize(
        "hello",
    )

    assert json.loads(
        result,
    ) == "hello"


def test_serialize_numbers():

    exporter = JSONExporter()

    assert json.loads(
        exporter.serialize(
            42,
        ),
    ) == 42

    assert json.loads(
        exporter.serialize(
            3.14,
        ),
    ) == pytest.approx(
        3.14,
    )


def test_serialize_boolean():

    exporter = JSONExporter()

    assert json.loads(
        exporter.serialize(
            True,
        ),
    ) is True


def test_serialize_none():

    exporter = JSONExporter()

    assert json.loads(
        exporter.serialize(
            None,
        ),
    ) is None


def test_unicode():

    exporter = JSONExporter(
        ensure_ascii=False,
    )

    result = exporter.serialize(
        {
            "message": "Xin chÃ o Viá»‡t Nam",
        },
    )

    assert "Xin chÃ o Viá»‡t Nam" in result


def test_ensure_ascii():

    exporter = JSONExporter(
        ensure_ascii=True,
    )

    result = exporter.serialize(
        {
            "message": "Xin chÃ o",
        },
    )

    assert "Xin chÃ o" not in result

    assert "\\u" in result


def test_indent():

    exporter = JSONExporter(
        indent=4,
    )

    result = exporter.serialize(
        {
            "id": 1,
            "value": "hello",
        },
    )

    assert "\n" in result
    assert "    " in result


def test_sort_keys():

    exporter = JSONExporter(
        sort_keys=True,
        indent=None,
    )

    result = exporter.serialize(
        {
            "z": 1,
            "a": 2,
            "m": 3,
        },
    )

    assert result.index(
        '"a"',
    ) < result.index(
        '"m"',
    )

    assert result.index(
        '"m"',
    ) < result.index(
        '"z"',
    )


def test_serialize_many():

    exporter = JSONExporter()

    results = exporter.serialize_many(
        [
            {"id": 1},
            {"id": 2},
            {"id": 3},
        ],
    )

    assert len(
        results,
    ) == 3

    assert [
        json.loads(
            item,
        )
        for item in results
    ] == [
        {"id": 1},
        {"id": 2},
        {"id": 3},
    ]


# ==============================================================================
# Part 4. Export
# ==============================================================================


def test_export_success():

    exporter = JSONExporter()

    result = exporter.export(
        {
            "id": 1,
            "value": "hello",
        },
    )

    assert result.success is True
    assert isinstance(
        result,
        ExportResult,
    )


def test_export_result():

    exporter = JSONExporter()

    result = exporter.export(
        {
            "id": 1,
        },
    )

    assert result.success is True
    assert result.format is ExportFormat.JSON
    assert isinstance(
        result.payload,
        str,
    )

    assert json.loads(
        result.payload,
    ) == {
        "id": 1,
    }

    assert result.bytes_exported > 0


def test_export_bytes():

    exporter = JSONExporter(
        encoding="utf-8",
    )

    result = exporter.export(
        {
            "message": "Xin chÃ o",
        },
    )

    assert result.bytes_exported == len(
        result.payload.encode(
            "utf-8",
        ),
    )


def test_export_count():

    exporter = JSONExporter()

    assert exporter.export_count == 0

    exporter.export(
        {"id": 1},
    )

    exporter.export(
        {"id": 2},
    )

    assert exporter.export_count == 2
    assert exporter.success_count == 2
    assert exporter.error_count == 0


def test_export_many():

    exporter = JSONExporter()

    results = exporter.export_many(
        [
            {"id": 1},
            {"id": 2},
            {"id": 3},
        ],
    )

    assert len(
        results,
    ) == 3

    assert all(
        result.success
        for result in results
    )

    assert exporter.export_count == 3
    assert exporter.success_count == 3


# ==============================================================================
# Part 5. Validation
# ==============================================================================


def test_valid_payload():

    exporter = JSONExporter()

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


def test_invalid_payload():

    exporter = JSONExporter()

    invalid_payload = object()

    assert exporter.validate_payload(
        invalid_payload,
    ) is False

    with pytest.raises(
        ExportError,
    ):
        exporter.serialize(
            invalid_payload,
        )


def test_invalid_options():

    exporter = JSONExporter()

    assert exporter.validate_options(
        {
            "ensure_ascii": True,
            "indent": 4,
            "sort_keys": True,
        },
    ) is True

    assert exporter.validate_options(
        {
            "ensure_ascii": "yes",
        },
    ) is False

    assert exporter.validate_options(
        {
            "indent": -1,
        },
    ) is False

    assert exporter.validate_options(
        {
            "sort_keys": "yes",
        },
    ) is False


# ==============================================================================
# Part 6. Lifecycle
# ==============================================================================


def test_start():

    exporter = JSONExporter()

    assert exporter.state == "created"

    result = exporter.start()

    assert result is exporter
    assert exporter.state == "running"


def test_stop():

    exporter = JSONExporter()

    exporter.start()

    result = exporter.stop()

    assert result is exporter
    assert exporter.state == "stopped"


def test_reset():

    exporter = JSONExporter()

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


def test_close():

    exporter = JSONExporter()

    result = exporter.close()

    assert result is exporter
    assert exporter.state == "closed"


def test_export_after_close():

    exporter = JSONExporter()

    exporter.close()

    with pytest.raises(
        ExportError,
    ):
        exporter.export(
            {"id": 1},
        )

# ==============================================================================
# Part 7. Error Handling
# ==============================================================================


def test_serialization_error():

    exporter = JSONExporter()

    invalid_payload = object()

    with pytest.raises(
        ExportError,
    ):
        exporter.serialize(
            invalid_payload,
        )


def test_export_error():

    exporter = JSONExporter()

    invalid_payload = object()

    with pytest.raises(
        ExportError,
    ):
        exporter.export(
            invalid_payload,
        )

    assert exporter.error_count == 1


def test_error_count():

    exporter = JSONExporter()

    assert exporter.error_count == 0

    with pytest.raises(
        ExportError,
    ):
        exporter.export(
            object(),
        )

    assert exporter.error_count == 1

    with pytest.raises(
        ExportError,
    ):
        exporter.export(
            object(),
        )

    assert exporter.error_count == 2


# ==============================================================================
# Part 8. Statistics
# ==============================================================================


def test_export_count_statistics():

    exporter = JSONExporter()

    assert exporter.export_count == 0

    exporter.export(
        {"id": 1},
    )

    exporter.export(
        {"id": 2},
    )

    assert exporter.export_count == 2


def test_success_count_statistics():

    exporter = JSONExporter()

    assert exporter.success_count == 0

    exporter.export(
        {"id": 1},
    )

    exporter.export(
        {"id": 2},
    )

    assert exporter.success_count == 2


def test_error_count_statistics():

    exporter = JSONExporter()

    assert exporter.error_count == 0

    with pytest.raises(
        ExportError,
    ):
        exporter.export(
            object(),
        )

    assert exporter.error_count == 1


def test_bytes_exported_statistics():

    exporter = JSONExporter()

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


def test_diagnostics():

    exporter = JSONExporter(
        name="test-json",
        encoding="utf-8",
        ensure_ascii=False,
        indent=4,
        sort_keys=True,
    )

    exporter.export(
        {"id": 1},
    )

    diagnostics = exporter.diagnostics()

    assert isinstance(
        diagnostics,
        dict,
    )

    assert diagnostics["name"] == "test-json"
    assert diagnostics["state"] == exporter.state
    assert diagnostics["enabled"] is True
    assert diagnostics["healthy"] is True

    assert diagnostics["export_count"] == exporter.export_count
    assert diagnostics["success_count"] == exporter.success_count
    assert diagnostics["error_count"] == exporter.error_count
    assert diagnostics["bytes_exported"] == exporter.bytes_exported

    assert diagnostics["exporter_type"] == "JSONExporter"
    assert diagnostics["ensure_ascii"] is False
    assert diagnostics["indent"] == 4
    assert diagnostics["sort_keys"] is True


def test_summary():

    exporter = JSONExporter(
        name="test-json",
        indent=2,
        sort_keys=True,
    )

    summary = exporter.summary()

    assert isinstance(
        summary,
        dict,
    )

    assert summary["name"] == exporter.name
    assert summary["state"] == exporter.state
    assert summary["enabled"] == exporter.enabled
    assert summary["healthy"] is True

    assert summary["export_count"] == exporter.export_count
    assert summary["success_count"] == exporter.success_count
    assert summary["error_count"] == exporter.error_count
    assert summary["bytes_exported"] == exporter.bytes_exported

    assert summary["exporter_type"] == "JSONExporter"
    assert summary["ensure_ascii"] is False
    assert summary["indent"] == 2
    assert summary["sort_keys"] is True


# ==============================================================================
# Part 10. Representation
# ==============================================================================


def test_repr():

    exporter = JSONExporter(
        name="test-json",
        encoding="utf-8",
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    )

    result = repr(
        exporter,
    )

    assert isinstance(
        result,
        str,
    )

    assert "JSONExporter" in result
    assert "test-json" in result
    assert "utf-8" in result
    assert "ensure_ascii=False" in result
    assert "indent=2" in result
    assert "sort_keys=True" in result


def test_str():

    exporter = JSONExporter(
        name="test-json",
    )

    result = str(
        exporter,
    )

    assert isinstance(
        result,
        str,
    )

    assert "test-json" in result
    assert "format=json" in result
    assert "state=created" in result
    assert "enabled=True" in result


# ==============================================================================
# Part 11. End
# ==============================================================================


# End of test_json_exporter.py

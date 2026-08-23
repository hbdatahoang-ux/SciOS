# ==============================================================================
# SciOS Runtime Observability
# Tests - MemoryExporter
# ==============================================================================

from __future__ import annotations

import pytest

from scios.runtime.observability.tracing.memory import (
    MemoryExporter,
)
from scios.runtime.observability.tracing.exporter import (
    ExportError,
    ExportFormat,
)


# ==============================================================================
# Part 1. Construction
# ==============================================================================


def test_default_construction():

    exporter = MemoryExporter()

    assert isinstance(
        exporter,
        MemoryExporter,
    )

    assert exporter.name == "memory"

    assert exporter.format is ExportFormat.JSON

    assert exporter.encoding == "utf-8"

    assert exporter.enabled is True

    assert exporter.state == "created"

    assert exporter.size == 0


def test_custom_construction():

    exporter = MemoryExporter(
        name="test-memory",
        max_items=10,
        enabled=False,
    )

    assert exporter.name == "test-memory"

    assert exporter.max_items == 10

    assert exporter.enabled is False

    assert exporter.size == 0


def test_invalid_name():

    with pytest.raises(
        (TypeError, ValueError),
    ):
        MemoryExporter(
            name="",
        )


def test_invalid_max_items():

    with pytest.raises(
        (TypeError, ValueError),
    ):
        MemoryExporter(
            max_items=0,
        )

    with pytest.raises(
        (TypeError, ValueError),
    ):
        MemoryExporter(
            max_items=-1,
        )


# ==============================================================================
# Part 2. Configuration
# ==============================================================================


def test_name():

    exporter = MemoryExporter(
        name="test",
    )

    assert exporter.name == "test"


def test_enabled():

    exporter = MemoryExporter()

    assert exporter.enabled is True

    exporter.enabled = False

    assert exporter.enabled is False

    exporter.enabled = True

    assert exporter.enabled is True


def test_invalid_enabled():

    exporter = MemoryExporter()

    with pytest.raises(TypeError):
        exporter.enabled = "yes"


def test_format():

    exporter = MemoryExporter()

    assert exporter.format is ExportFormat.JSON


def test_encoding():

    exporter = MemoryExporter()

    assert exporter.encoding == "utf-8"


def test_options():

    exporter = MemoryExporter()

    assert isinstance(
        exporter.options,
        dict,
    )


def test_initial_state():

    exporter = MemoryExporter()

    assert exporter.state == "created"


# ==============================================================================
# Part 3. Export
# ==============================================================================


def test_export_mapping():

    exporter = MemoryExporter()

    result = exporter.export(
        {
            "message": "hello",
            "value": 42,
        },
    )

    assert result.success is True

    assert exporter.size == 1

    assert exporter.export_count == 1

    assert exporter.success_count == 1

    assert exporter.error_count == 0


def test_export_multiple():

    exporter = MemoryExporter()

    exporter.export(
        {"id": 1},
    )

    exporter.export(
        {"id": 2},
    )

    exporter.export(
        {"id": 3},
    )

    assert exporter.size == 3

    assert exporter.export_count == 3

    assert exporter.success_count == 3

    assert exporter.error_count == 0


def test_export_string():

    exporter = MemoryExporter()

    result = exporter.export(
        "hello",
    )

    assert result.success is True

    assert exporter.size == 1


def test_export_bytes():

    exporter = MemoryExporter()

    result = exporter.export(
        b"hello",
    )

    assert result.success is True

    assert exporter.size == 1


def test_invalid_payload():

    exporter = MemoryExporter()

    invalid_payload = object()

    with pytest.raises(
        (ExportError, TypeError, ValueError),
    ):
        exporter.export(
            invalid_payload,
        )

    assert exporter.error_count == 1


def test_export_after_start():

    exporter = MemoryExporter()

    exporter.start()

    result = exporter.export(
        {
            "event": "test",
        },
    )

    assert result.success is True

    assert exporter.state == "running"


def test_export_after_close():

    exporter = MemoryExporter()

    exporter.close()

    with pytest.raises(
        ExportError,
    ):
        exporter.export(
            {"event": "test"},
        )


# ==============================================================================
# Part 4. Storage
# ==============================================================================


def test_items_initially_empty():

    exporter = MemoryExporter()

    assert exporter.items == []


def test_items_after_export():

    exporter = MemoryExporter()

    exporter.export(
        {"id": 1},
    )

    assert len(exporter.items) == 1


def test_get_existing_item():

    exporter = MemoryExporter()

    exporter.export(
        {
            "id": 1,
            "value": "hello",
        },
    )

    item = exporter.get(
        0,
    )

    assert item == {
        "id": 1,
        "value": "hello",
    }


def test_get_missing_item():

    exporter = MemoryExporter()

    assert exporter.get(
        999,
    ) is None


def test_get_with_default():

    exporter = MemoryExporter()

    marker = object()

    assert exporter.get(
        999,
        marker,
    ) is marker


def test_snapshot():

    exporter = MemoryExporter()

    exporter.export(
        {"id": 1},
    )

    exporter.export(
        {"id": 2},
    )

    snapshot = exporter.snapshot()

    assert isinstance(
        snapshot,
        dict,
    )

    assert snapshot["size"] == 2

    assert len(
        snapshot["items"],
    ) == 2


def test_clear():

    exporter = MemoryExporter()

    exporter.export(
        {"id": 1},
    )

    exporter.export(
        {"id": 2},
    )

    assert exporter.size == 2

    exporter.clear()

    assert exporter.size == 0

    assert exporter.items == []


# ==============================================================================
# Part 5. max_items
# ==============================================================================


def test_max_items():

    exporter = MemoryExporter(
        max_items=2,
    )

    assert exporter.max_items == 2


def test_max_items_limits_storage():

    exporter = MemoryExporter(
        max_items=2,
    )

    exporter.export(
        {"id": 1},
    )

    exporter.export(
        {"id": 2},
    )

    exporter.export(
        {"id": 3},
    )

    assert exporter.size == 2


def test_max_items_keeps_latest_items():

    exporter = MemoryExporter(
        max_items=2,
    )

    exporter.export(
        {"id": 1},
    )

    exporter.export(
        {"id": 2},
    )

    exporter.export(
        {"id": 3},
    )

    items = exporter.items

    assert items[-1]["id"] == 3

    assert items[-2]["id"] == 2


def test_max_items_one():

    exporter = MemoryExporter(
        max_items=1,
    )

    exporter.export(
        {"id": 1},
    )

    exporter.export(
        {"id": 2},
    )

    assert exporter.size == 1

    assert exporter.items[0]["id"] == 2

# ==============================================================================
# Part 6. Lifecycle
# ==============================================================================


def test_start():

    exporter = MemoryExporter()

    assert exporter.state == "created"

    result = exporter.start()

    assert result is exporter
    assert exporter.state == "running"


def test_stop():

    exporter = MemoryExporter()

    exporter.start()

    result = exporter.stop()

    assert result is exporter
    assert exporter.state == "stopped"


def test_start_after_stop():

    exporter = MemoryExporter()

    exporter.start()
    exporter.stop()
    exporter.start()

    assert exporter.state == "running"


def test_close():

    exporter = MemoryExporter()

    result = exporter.close()

    assert result is exporter
    assert exporter.state == "closed"


def test_close_is_idempotent():

    exporter = MemoryExporter()

    exporter.close()

    result = exporter.close()

    assert result is exporter
    assert exporter.state == "closed"


def test_export_after_close():

    exporter = MemoryExporter()

    exporter.close()

    with pytest.raises(
        ExportError,
    ):
        exporter.export(
            {"id": 1},
        )


# ==============================================================================
# Part 7. Reset / Clear
# ==============================================================================


def test_clear_does_not_close_exporter():

    exporter = MemoryExporter()

    exporter.export(
        {"id": 1},
    )

    exporter.clear()

    assert exporter.size == 0
    assert exporter.state == "running"


def test_reset():

    exporter = MemoryExporter()

    exporter.export(
        {"id": 1},
    )

    exporter.export(
        {"id": 2},
    )

    assert exporter.size == 2
    assert exporter.export_count == 2

    result = exporter.reset()

    assert result is exporter
    assert exporter.size == 0
    assert exporter.export_count == 0
    assert exporter.success_count == 0
    assert exporter.error_count == 0
    assert exporter.bytes_exported == 0
    assert exporter.last_export is None
    assert exporter.state == "created"


def test_reset_after_close():

    exporter = MemoryExporter()

    exporter.close()

    with pytest.raises(
        ExportError,
    ):
        exporter.reset()


def test_clear_empty_storage():

    exporter = MemoryExporter()

    exporter.clear()

    assert exporter.size == 0


# ==============================================================================
# Part 8. Error Handling
# ==============================================================================


def test_error_count_increments():

    exporter = MemoryExporter()

    invalid_payload = object()

    with pytest.raises(
        (ExportError, TypeError, ValueError),
    ):
        exporter.export(
            invalid_payload,
        )

    assert exporter.error_count == 1


def test_last_error():

    exporter = MemoryExporter()

    invalid_payload = object()

    with pytest.raises(
        (ExportError, TypeError, ValueError),
    ):
        exporter.export(
            invalid_payload,
        )

    assert exporter.last_error is not None


def test_success_does_not_increment_error_count():

    exporter = MemoryExporter()

    exporter.export(
        {"id": 1},
    )

    assert exporter.error_count == 0
    assert exporter.last_error is None


def test_disabled_exporter():

    exporter = MemoryExporter(
        enabled=False,
    )

    with pytest.raises(
        ExportError,
    ):
        exporter.export(
            {"id": 1},
        )

    assert exporter.error_count == 1


# ==============================================================================
# Part 9. Statistics
# ==============================================================================


def test_initial_statistics():

    exporter = MemoryExporter()

    assert exporter.export_count == 0
    assert exporter.success_count == 0
    assert exporter.error_count == 0
    assert exporter.bytes_exported == 0
    assert exporter.last_export is None


def test_statistics_after_successful_export():

    exporter = MemoryExporter()

    result = exporter.export(
        {"message": "hello"},
    )

    assert result.success is True

    assert exporter.export_count == 1
    assert exporter.success_count == 1
    assert exporter.error_count == 0
    assert exporter.bytes_exported > 0
    assert exporter.last_export is not None


def test_statistics_after_multiple_exports():

    exporter = MemoryExporter()

    exporter.export(
        {"id": 1},
    )

    exporter.export(
        {"id": 2},
    )

    exporter.export(
        {"id": 3},
    )

    assert exporter.export_count == 3
    assert exporter.success_count == 3
    assert exporter.error_count == 0
    assert exporter.bytes_exported > 0


def test_statistics_after_error():

    exporter = MemoryExporter()

    with pytest.raises(
        (ExportError, TypeError, ValueError),
    ):
        exporter.export(
            object(),
        )

    assert exporter.export_count == 1
    assert exporter.success_count == 0
    assert exporter.error_count == 1


# ==============================================================================
# Part 10. Diagnostics
# ==============================================================================


def test_health():

    exporter = MemoryExporter()

    assert exporter.health() is True

    exporter.enabled = False

    assert exporter.health() is False


def test_health_after_close():

    exporter = MemoryExporter()

    exporter.close()

    assert exporter.health() is False


def test_diagnostics():

    exporter = MemoryExporter(
        name="test-memory",
        max_items=10,
    )

    exporter.export(
        {"id": 1},
    )

    diagnostics = exporter.diagnostics()

    assert isinstance(
        diagnostics,
        dict,
    )

    assert diagnostics["name"] == "test-memory"
    assert diagnostics["state"] == exporter.state
    assert diagnostics["enabled"] is True
    assert diagnostics["healthy"] is True
    assert diagnostics["items"] == exporter.size
    assert diagnostics["max_items"] == 10
    assert diagnostics["export_count"] == exporter.export_count
    assert diagnostics["success_count"] == exporter.success_count
    assert diagnostics["error_count"] == exporter.error_count
    assert diagnostics["bytes_exported"] == exporter.bytes_exported


def test_summary():

    exporter = MemoryExporter(
        name="test-memory",
        max_items=5,
    )

    summary = exporter.summary()

    assert isinstance(
        summary,
        dict,
    )

    assert summary["name"] == exporter.name
    assert summary["state"] == exporter.state
    assert summary["enabled"] == exporter.enabled
    assert summary["items"] == exporter.size
    assert summary["max_items"] == exporter.max_items
    assert summary["export_count"] == exporter.export_count
    assert summary["success_count"] == exporter.success_count
    assert summary["error_count"] == exporter.error_count


# ==============================================================================
# Part 11. Representation
# ==============================================================================


def test_repr():

    exporter = MemoryExporter(
        name="test-memory",
        max_items=10,
    )

    value = repr(exporter)

    assert isinstance(
        value,
        str,
    )

    assert "MemoryExporter" in value
    assert "test-memory" in value
    assert "max_items=10" in value


def test_str():

    exporter = MemoryExporter(
        name="test-memory",
        max_items=10,
    )

    value = str(exporter)

    assert isinstance(
        value,
        str,
    )

    assert "test-memory" in value
    assert "items=" in value
    assert "max_items=" in value
    assert "state=" in value

"""
Tests for MemoryExporter.

Part 1. Construction
Part 2. Configuration
Part 3. Storage access
Part 4. Export
Part 5. Export many
Part 6. Capacity management
Part 7. Storage management
Part 8. Lifecycle
Part 9. Validation and errors
Part 10. Representation

Python 3.11+
"""

from __future__ import annotations

import pytest

from scios.runtime.observability.exporters.base import (
    ExportFormat,
    ExportPayload,
)
from scios.runtime.observability.exporters.memory import (
    MemoryExporter,
)


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def exporter() -> MemoryExporter:
    return MemoryExporter()


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
def payloads() -> list[ExportPayload]:
    return [
        ExportPayload("one", 1),
        ExportPayload("two", 2),
        ExportPayload("three", 3),
    ]


# ==============================================================================
# Part 1. Construction
# ==============================================================================


def test_default_construction() -> None:
    exporter = MemoryExporter()

    assert exporter.name == "memory"
    assert exporter.enabled is True
    assert exporter.max_items is None
    assert exporter.count == 0
    assert exporter.items == ()
    assert exporter.latest is None


def test_custom_name() -> None:
    exporter = MemoryExporter("custom")

    assert exporter.name == "custom"


def test_custom_format() -> None:
    exporter = MemoryExporter(
        format=ExportFormat.JSON,
    )

    assert exporter.format == ExportFormat.JSON


def test_custom_encoding() -> None:
    exporter = MemoryExporter(
        encoding="ascii",
    )

    assert exporter.encoding == "ascii"


def test_custom_options() -> None:
    exporter = MemoryExporter(
        options={"source": "test"},
    )

    assert exporter.options["source"] == "test"


def test_custom_max_items() -> None:
    exporter = MemoryExporter(
        max_items=10,
    )

    assert exporter.max_items == 10


def test_negative_max_items_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="max_items must be >= 0",
    ):
        MemoryExporter(max_items=-1)


def test_boolean_max_items_rejected() -> None:
    with pytest.raises(
        TypeError,
        match="max_items must be an integer or None",
    ):
        MemoryExporter(max_items=True)  # type: ignore[arg-type]


def test_invalid_max_items_rejected() -> None:
    with pytest.raises(
        TypeError,
        match="max_items must be an integer or None",
    ):
        MemoryExporter(max_items="10")  # type: ignore[arg-type]


# ==============================================================================
# Part 2. Configuration
# ==============================================================================


def test_max_items_can_be_changed(
    exporter: MemoryExporter,
) -> None:
    exporter.max_items = 5

    assert exporter.max_items == 5


def test_max_items_can_be_unlimited(
    exporter: MemoryExporter,
) -> None:
    exporter.max_items = 5
    exporter.max_items = None

    assert exporter.max_items is None


def test_setting_negative_max_items_rejected(
    exporter: MemoryExporter,
) -> None:
    with pytest.raises(
        ValueError,
        match="max_items must be >= 0",
    ):
        exporter.max_items = -1


# ==============================================================================
# Part 3. Storage access
# ==============================================================================


def test_items_is_empty_initially(
    exporter: MemoryExporter,
) -> None:
    assert exporter.items == ()


def test_count_is_zero_initially(
    exporter: MemoryExporter,
) -> None:
    assert exporter.count == 0


def test_latest_is_none_initially(
    exporter: MemoryExporter,
) -> None:
    assert exporter.latest is None


def test_items_returns_snapshot(
    exporter: MemoryExporter,
    payload: ExportPayload,
) -> None:
    exporter.export(payload)

    items = exporter.items

    assert isinstance(items, tuple)
    assert items == (payload,)


def test_snapshot_returns_immutable_view(
    exporter: MemoryExporter,
    payload: ExportPayload,
) -> None:
    exporter.export(payload)

    snapshot = exporter.snapshot()

    assert snapshot == (payload,)


# ==============================================================================
# Part 4. Export
# ==============================================================================


def test_export_stores_payload(
    exporter: MemoryExporter,
    payload: ExportPayload,
) -> None:
    result = exporter.export(payload)

    assert result.success is True
    assert exporter.count == 1
    assert exporter.latest is payload


def test_export_preserves_payload_identity(
    exporter: MemoryExporter,
    payload: ExportPayload,
) -> None:
    exporter.export(payload)

    assert exporter.items[0] is payload


def test_export_updates_statistics(
    exporter: MemoryExporter,
    payload: ExportPayload,
) -> None:
    result = exporter.export(payload)

    assert result.success is True
    assert exporter.export_count == 1
    assert exporter.success_count == 1
    assert exporter.error_count == 0


def test_multiple_exports_preserve_order(
    exporter: MemoryExporter,
    payloads: list[ExportPayload],
) -> None:
    exporter.export_many(payloads)

    assert exporter.items == tuple(payloads)


def test_latest_returns_newest_payload(
    exporter: MemoryExporter,
    payloads: list[ExportPayload],
) -> None:
    exporter.export_many(payloads)

    assert exporter.latest is payloads[-1]


def test_export_mapping_payload(
    exporter: MemoryExporter,
) -> None:
    payload = {
        "name": "request_total",
        "value": 42,
    }

    result = exporter.export(payload)

    assert result.success is True
    assert exporter.latest is payload


# ==============================================================================
# Part 5. Export many
# ==============================================================================


def test_export_many_returns_one_result_per_payload(
    exporter: MemoryExporter,
    payloads: list[ExportPayload],
) -> None:
    results = exporter.export_many(payloads)

    assert len(results) == len(payloads)
    assert all(result.success for result in results)


def test_export_many_stores_all_payloads(
    exporter: MemoryExporter,
    payloads: list[ExportPayload],
) -> None:
    exporter.export_many(payloads)

    assert exporter.items == tuple(payloads)
    assert exporter.count == 3


def test_export_many_updates_statistics(
    exporter: MemoryExporter,
    payloads: list[ExportPayload],
) -> None:
    exporter.export_many(payloads)

    assert exporter.export_count == 3
    assert exporter.success_count == 3
    assert exporter.error_count == 0


# ==============================================================================
# Part 6. Capacity management
# ==============================================================================


def test_max_items_limits_storage(
    payloads: list[ExportPayload],
) -> None:
    exporter = MemoryExporter(max_items=2)

    exporter.export_many(payloads)

    assert exporter.count == 2
    assert exporter.items == (
        payloads[1],
        payloads[2],
    )


def test_max_items_uses_fifo_eviction(
    payloads: list[ExportPayload],
) -> None:
    exporter = MemoryExporter(max_items=2)

    exporter.export(payloads[0])
    exporter.export(payloads[1])
    exporter.export(payloads[2])

    assert exporter.items == (
        payloads[1],
        payloads[2],
    )


def test_zero_capacity_stores_nothing(
    payload: ExportPayload,
) -> None:
    exporter = MemoryExporter(max_items=0)

    result = exporter.export(payload)

    assert result.success is True
    assert exporter.count == 0
    assert exporter.latest is None


def test_changing_capacity_trims_existing_items(
    payloads: list[ExportPayload],
) -> None:
    exporter = MemoryExporter()

    exporter.export_many(payloads)
    exporter.max_items = 2

    assert exporter.items == (
        payloads[1],
        payloads[2],
    )


def test_increasing_capacity_does_not_modify_items(
    payloads: list[ExportPayload],
) -> None:
    exporter = MemoryExporter(max_items=2)

    exporter.export_many(payloads)

    before = exporter.items

    exporter.max_items = 10

    assert exporter.items == before


# ==============================================================================
# Part 7. Storage management
# ==============================================================================


def test_clear_removes_items(
    exporter: MemoryExporter,
    payloads: list[ExportPayload],
) -> None:
    exporter.export_many(payloads)

    exporter.clear()

    assert exporter.count == 0
    assert exporter.items == ()
    assert exporter.latest is None


def test_clear_does_not_reset_statistics(
    exporter: MemoryExporter,
    payload: ExportPayload,
) -> None:
    exporter.export(payload)

    exporter.clear()

    assert exporter.count == 0
    assert exporter.export_count == 1
    assert exporter.success_count == 1


def test_pop_removes_oldest(
    exporter: MemoryExporter,
    payloads: list[ExportPayload],
) -> None:
    exporter.export_many(payloads)

    result = exporter.pop()

    assert result is payloads[0]
    assert exporter.items == (
        payloads[1],
        payloads[2],
    )


def test_pop_latest_removes_newest(
    exporter: MemoryExporter,
    payloads: list[ExportPayload],
) -> None:
    exporter.export_many(payloads)

    result = exporter.pop_latest()

    assert result is payloads[-1]
    assert exporter.items == (
        payloads[0],
        payloads[1],
    )


def test_pop_empty_raises(
    exporter: MemoryExporter,
) -> None:
    with pytest.raises(IndexError):
        exporter.pop()


def test_pop_latest_empty_raises(
    exporter: MemoryExporter,
) -> None:
    with pytest.raises(IndexError):
        exporter.pop_latest()


# ==============================================================================
# Part 8. Lifecycle
# ==============================================================================


def test_reset_clears_storage(
    exporter: MemoryExporter,
    payload: ExportPayload,
) -> None:
    exporter.export(payload)

    exporter.reset()

    assert exporter.count == 0
    assert exporter.items == ()


def test_reset_clears_statistics(
    exporter: MemoryExporter,
    payload: ExportPayload,
) -> None:
    exporter.export(payload)

    exporter.reset()

    assert exporter.export_count == 0
    assert exporter.success_count == 0
    assert exporter.error_count == 0


def test_reset_preserves_configuration(
    exporter: MemoryExporter,
) -> None:
    exporter.max_items = 10

    exporter.reset()

    assert exporter.max_items == 10


def test_start_preserves_storage(
    exporter: MemoryExporter,
    payload: ExportPayload,
) -> None:
    exporter.export(payload)

    exporter.start()

    assert exporter.latest is payload


def test_stop_preserves_storage(
    exporter: MemoryExporter,
    payload: ExportPayload,
) -> None:
    exporter.export(payload)

    exporter.start()
    exporter.stop()

    assert exporter.latest is payload


# ==============================================================================
# Part 9. Validation and errors
# ==============================================================================


def test_disabled_export_does_not_store(
    exporter: MemoryExporter,
    payload: ExportPayload,
) -> None:
    exporter.enabled = False

    result = exporter.export(payload)

    assert result.success is False
    assert exporter.count == 0


def test_disabled_export_records_attempt(
    exporter: MemoryExporter,
    payload: ExportPayload,
) -> None:
    exporter.enabled = False

    exporter.export(payload)

    assert exporter.export_count == 1


def test_invalid_payload_is_rejected(
    exporter: MemoryExporter,
) -> None:
    with pytest.raises(
        (TypeError, ValueError),
    ):
        exporter.export(None)  # type: ignore[arg-type]


def test_invalid_option_is_rejected(
    exporter: MemoryExporter,
    payload: ExportPayload,
) -> None:
    with pytest.raises(
        (TypeError, ValueError),
    ):
        exporter.export(
            payload,
            invalid=True,
        )


# ==============================================================================
# Part 10. Representation
# ==============================================================================


def test_repr(
    exporter: MemoryExporter,
) -> None:
    value = repr(exporter)

    assert "MemoryExporter" in value
    assert "count=0" in value
    assert "max_items=None" in value


def test_str(
    exporter: MemoryExporter,
) -> None:
    value = str(exporter)

    assert "MemoryExporter" in value
    assert "count=0" in value
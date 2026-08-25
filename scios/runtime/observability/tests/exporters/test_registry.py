"""
SciOS Runtime Observability
===========================

Tests for ExporterRegistry.

Test organization
-----------------

Part 1. Construction
Part 2. Registration
Part 3. Lookup
Part 4. Properties
Part 5. Enable / disable
Part 6. Lifecycle
Part 7. Export
Part 8. Statistics
Part 9. Diagnostics
Part 10. Error handling
Part 11. Collection protocol
Part 12. Representation

Python 3.11+
"""

from __future__ import annotations

import pytest

from scios.runtime.observability.exporters.base import (
    ExportFormat,
    ExportPayload,
    Exporter,
)
from scios.runtime.observability.exporters.registry import (
    ExporterAlreadyRegisteredError,
    ExporterNotFoundError,
    ExporterRegistry,
    ExporterRegistryError,
)


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def exporter() -> Exporter:
    return Exporter(
        name="test",
        format=ExportFormat.JSON,
    )


@pytest.fixture
def second_exporter() -> Exporter:
    return Exporter(
        name="second",
        format=ExportFormat.JSON,
    )


@pytest.fixture
def third_exporter() -> Exporter:
    return Exporter(
        name="third",
        format=ExportFormat.TEXT,
    )


@pytest.fixture
def registry(
    exporter: Exporter,
) -> ExporterRegistry:
    return ExporterRegistry([exporter])


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


# ==============================================================================
# Part 1. Construction
# ==============================================================================


def test_empty_registry_constructs() -> None:
    registry = ExporterRegistry()

    assert registry.count == 0
    assert registry.empty is True
    assert registry.names == ()
    assert registry.exporters == {}


def test_registry_accepts_initial_exporters(
    exporter: Exporter,
    second_exporter: Exporter,
) -> None:
    registry = ExporterRegistry(
        [
            exporter,
            second_exporter,
        ]
    )

    assert registry.count == 2
    assert registry.names == (
        "test",
        "second",
    )


def test_registry_rejects_invalid_initial_exporter() -> None:
    with pytest.raises(
        TypeError,
        match="exporter must be an Exporter instance",
    ):
        ExporterRegistry(
            ["invalid"]  # type: ignore[list-item]
        )


def test_registry_error_hierarchy() -> None:
    assert issubclass(
        ExporterRegistryError,
        RuntimeError,
    )

    assert issubclass(
        ExporterAlreadyRegisteredError,
        ExporterRegistryError,
    )

    assert issubclass(
        ExporterNotFoundError,
        ExporterRegistryError,
    )


# ==============================================================================
# Part 2. Registration
# ==============================================================================


def test_register_adds_exporter(
    exporter: Exporter,
) -> None:
    registry = ExporterRegistry()

    result = registry.register(exporter)

    assert result is exporter
    assert registry.count == 1
    assert registry.get("test") is exporter


def test_register_rejects_non_exporter() -> None:
    registry = ExporterRegistry()

    with pytest.raises(
        TypeError,
        match="exporter must be an Exporter instance",
    ):
        registry.register(
            "invalid"  # type: ignore[arg-type]
        )


def test_register_rejects_duplicate_name(
    registry: ExporterRegistry,
) -> None:
    duplicate = Exporter("test")

    with pytest.raises(
        ExporterAlreadyRegisteredError,
        match="exporter already registered",
    ):
        registry.register(duplicate)


def test_register_replace_replaces_existing_exporter(
    registry: ExporterRegistry,
) -> None:
    replacement = Exporter("test")

    result = registry.register(
        replacement,
        replace=True,
    )

    assert result is replacement
    assert registry.get("test") is replacement
    assert registry.count == 1


def test_register_preserves_insertion_order(
    exporter: Exporter,
    second_exporter: Exporter,
    third_exporter: Exporter,
) -> None:
    registry = ExporterRegistry()

    registry.register(exporter)
    registry.register(second_exporter)
    registry.register(third_exporter)

    assert registry.names == (
        "test",
        "second",
        "third",
    )


def test_unregister_returns_exporter(
    registry: ExporterRegistry,
    exporter: Exporter,
) -> None:
    result = registry.unregister("test")

    assert result is exporter
    assert registry.count == 0
    assert registry.empty is True


def test_unregister_can_close_exporter(
    registry: ExporterRegistry,
    exporter: Exporter,
) -> None:
    registry.unregister(
        "test",
        close=True,
    )

    assert exporter.closed is True
    assert registry.empty is True


def test_unregister_missing_exporter_raises(
    registry: ExporterRegistry,
) -> None:
    with pytest.raises(
        ExporterNotFoundError,
        match="exporter not found",
    ):
        registry.unregister("missing")


def test_clear_removes_all_exporters(
    exporter: Exporter,
    second_exporter: Exporter,
) -> None:
    registry = ExporterRegistry(
        [
            exporter,
            second_exporter,
        ]
    )

    registry.clear()

    assert registry.count == 0
    assert registry.names == ()


def test_clear_can_close_all_exporters(
    exporter: Exporter,
    second_exporter: Exporter,
) -> None:
    registry = ExporterRegistry(
        [
            exporter,
            second_exporter,
        ]
    )

    registry.clear(close=True)

    assert exporter.closed is True
    assert second_exporter.closed is True
    assert registry.empty is True


# ==============================================================================
# Part 3. Lookup
# ==============================================================================


def test_get_returns_exporter(
    registry: ExporterRegistry,
    exporter: Exporter,
) -> None:
    assert registry.get("test") is exporter


def test_get_missing_raises(
    registry: ExporterRegistry,
) -> None:
    with pytest.raises(
        ExporterNotFoundError,
        match="exporter not found",
    ):
        registry.get("missing")


def test_find_returns_exporter(
    registry: ExporterRegistry,
    exporter: Exporter,
) -> None:
    assert registry.find("test") is exporter


def test_find_missing_returns_none(
    registry: ExporterRegistry,
) -> None:
    assert registry.find("missing") is None


def test_contains_returns_true(
    registry: ExporterRegistry,
) -> None:
    assert registry.contains("test") is True


def test_contains_returns_false(
    registry: ExporterRegistry,
) -> None:
    assert registry.contains("missing") is False


# ==============================================================================
# Part 4. Properties
# ==============================================================================


def test_exporters_returns_copy(
    registry: ExporterRegistry,
    exporter: Exporter,
) -> None:
    exporters = registry.exporters

    exporters.clear()

    assert registry.count == 1
    assert registry.get("test") is exporter


def test_names_returns_tuple(
    registry: ExporterRegistry,
) -> None:
    assert isinstance(registry.names, tuple)
    assert registry.names == ("test",)


def test_count(
    registry: ExporterRegistry,
) -> None:
    assert registry.count == 1


def test_empty(
    registry: ExporterRegistry,
) -> None:
    assert registry.empty is False


# ==============================================================================
# Part 5. Enable / disable
# ==============================================================================


def test_disable(
    registry: ExporterRegistry,
    exporter: Exporter,
) -> None:
    result = registry.disable("test")

    assert result is exporter
    assert exporter.enabled is False


def test_enable(
    registry: ExporterRegistry,
    exporter: Exporter,
) -> None:
    exporter.enabled = False

    result = registry.enable("test")

    assert result is exporter
    assert exporter.enabled is True


def test_disable_missing_raises(
    registry: ExporterRegistry,
) -> None:
    with pytest.raises(ExporterNotFoundError):
        registry.disable("missing")


def test_enable_missing_raises(
    registry: ExporterRegistry,
) -> None:
    with pytest.raises(ExporterNotFoundError):
        registry.enable("missing")


# ==============================================================================
# Part 6. Lifecycle
# ==============================================================================


def test_start_starts_all_exporters(
    exporter: Exporter,
    second_exporter: Exporter,
) -> None:
    registry = ExporterRegistry(
        [
            exporter,
            second_exporter,
        ]
    )

    result = registry.start()

    assert result is registry
    assert exporter.started is True
    assert second_exporter.started is True


def test_stop_stops_all_exporters(
    exporter: Exporter,
    second_exporter: Exporter,
) -> None:
    registry = ExporterRegistry(
        [
            exporter,
            second_exporter,
        ]
    )

    registry.start()
    result = registry.stop()

    assert result is registry
    assert exporter.started is False
    assert second_exporter.started is False


def test_reset_resets_all_exporters(
    exporter: Exporter,
    second_exporter: Exporter,
) -> None:
    registry = ExporterRegistry(
        [
            exporter,
            second_exporter,
        ]
    )

    exporter.export(
        ExportPayload("one", 1)
    )
    second_exporter.export(
        ExportPayload("two", 2)
    )

    result = registry.reset()

    assert result is registry
    assert exporter.export_count == 0
    assert second_exporter.export_count == 0


def test_flush_flushes_all_exporters(
    registry: ExporterRegistry,
) -> None:
    result = registry.flush()

    assert result is registry


def test_close_closes_all_exporters(
    exporter: Exporter,
    second_exporter: Exporter,
) -> None:
    registry = ExporterRegistry(
        [
            exporter,
            second_exporter,
        ]
    )

    result = registry.close()

    assert result is registry
    assert exporter.closed is True
    assert second_exporter.closed is True


def test_close_empty_registry_is_safe() -> None:
    registry = ExporterRegistry()

    result = registry.close()

    assert result is registry
    assert registry.empty is True


# ==============================================================================
# Part 7. Export
# ==============================================================================


def test_export_uses_all_exporters(
    exporter: Exporter,
    second_exporter: Exporter,
    payload: ExportPayload,
) -> None:
    registry = ExporterRegistry(
        [
            exporter,
            second_exporter,
        ]
    )

    results = registry.export(payload)

    assert set(results) == {
        "test",
        "second",
    }

    assert results["test"].success is True
    assert results["second"].success is True


def test_export_can_select_exporters(
    exporter: Exporter,
    second_exporter: Exporter,
    payload: ExportPayload,
) -> None:
    registry = ExporterRegistry(
        [
            exporter,
            second_exporter,
        ]
    )

    results = registry.export(
        payload,
        exporters=["second"],
    )

    assert set(results.keys()) == {"second"}
    assert results["second"].success is True
    assert "test" not in results


def test_export_unknown_exporter_raises(
    registry: ExporterRegistry,
    payload: ExportPayload,
) -> None:
    with pytest.raises(ExporterNotFoundError):
        registry.export(
            payload,
            exporters=["missing"],
        )


def test_export_many_uses_all_exporters(
    exporter: Exporter,
    second_exporter: Exporter,
) -> None:
    registry = ExporterRegistry(
        [
            exporter,
            second_exporter,
        ]
    )

    payloads = [
        ExportPayload("one", 1),
        ExportPayload("two", 2),
        ExportPayload("three", 3),
    ]

    results = registry.export_many(payloads)

    assert set(results) == {
        "test",
        "second",
    }

    assert len(results["test"]) == 3
    assert len(results["second"]) == 3

    assert all(
        result.success
        for result in results["test"]
    )


def test_export_can_forward_options(
    registry: ExporterRegistry,
    payload: ExportPayload,
) -> None:
    result = registry.export(
        payload,
        custom_option=True,
    )

    assert result["test"].success is True


def test_export_disabled_exporter_returns_failure(
    registry: ExporterRegistry,
    exporter: Exporter,
    payload: ExportPayload,
) -> None:
    exporter.enabled = False

    results = registry.export(payload)

    assert results["test"].success is False
    assert results["test"].failed is True


# ==============================================================================
# Part 8. Statistics
# ==============================================================================


def test_statistics_are_zero_initially(
    registry: ExporterRegistry,
) -> None:
    assert registry.export_count == 0
    assert registry.success_count == 0
    assert registry.error_count == 0
    assert registry.bytes_exported == 0


def test_statistics_are_aggregated(
    exporter: Exporter,
    second_exporter: Exporter,
) -> None:
    registry = ExporterRegistry(
        [
            exporter,
            second_exporter,
        ]
    )

    registry.export(
        ExportPayload("one", 1)
    )

    assert registry.export_count == 2
    assert registry.success_count == 2
    assert registry.error_count == 0
    assert registry.bytes_exported > 0


def test_statistics_include_failed_exports(
    registry: ExporterRegistry,
    payload: ExportPayload,
) -> None:
    exporter = registry.get("test")
    exporter.enabled = False

    registry.export(payload)

    assert registry.export_count == 1
    assert registry.success_count == 0
    assert registry.error_count == 0


# ==============================================================================
# Part 9. Diagnostics
# ==============================================================================


def test_health_empty_registry() -> None:
    registry = ExporterRegistry()

    health = registry.health()

    assert health["healthy"] is True
    assert health["count"] == 0
    assert health["exporters"] == {}


def test_health_contains_exporters(
    registry: ExporterRegistry,
) -> None:
    health = registry.health()

    assert health["healthy"] is True
    assert health["count"] == 1
    assert "test" in health["exporters"]


def test_health_reflects_closed_exporter(
    registry: ExporterRegistry,
) -> None:
    registry.close()

    health = registry.health()

    assert health["healthy"] is False
    assert health["count"] == 1
    assert health["exporters"]["test"]["healthy"] is False


def test_diagnostics_contains_configuration(
    registry: ExporterRegistry,
) -> None:
    diagnostics = registry.diagnostics()

    assert diagnostics["count"] == 1
    assert diagnostics["names"] == ("test",)
    assert "test" in diagnostics["exporters"]


def test_diagnostics_contains_statistics(
    registry: ExporterRegistry,
    payload: ExportPayload,
) -> None:
    registry.export(payload)

    statistics = registry.diagnostics()["statistics"]

    assert statistics["export_count"] == 1
    assert statistics["success_count"] == 1
    assert statistics["error_count"] == 0
    assert statistics["bytes_exported"] > 0


def test_summary_is_compact(
    registry: ExporterRegistry,
) -> None:
    summary = registry.summary()

    assert summary == {
        "count": 1,
        "names": ("test",),
        "export_count": 0,
        "success_count": 0,
        "error_count": 0,
        "bytes_exported": 0,
    }


# ==============================================================================
# Part 10. Error handling
# ==============================================================================


def test_registry_does_not_swallow_missing_exporter(
    registry: ExporterRegistry,
) -> None:
    with pytest.raises(
        ExporterNotFoundError,
    ):
        registry.get("missing")


def test_registry_duplicate_error_contains_name(
    registry: ExporterRegistry,
) -> None:
    with pytest.raises(
        ExporterAlreadyRegisteredError,
        match="'test'",
    ):
        registry.register(
            Exporter("test")
        )


def test_registry_lookup_error_contains_name(
    registry: ExporterRegistry,
) -> None:
    with pytest.raises(
        ExporterNotFoundError,
        match="'missing'",
    ):
        registry.get("missing")


# ==============================================================================
# Part 11. Collection protocol
# ==============================================================================


def test_len_returns_count(
    registry: ExporterRegistry,
) -> None:
    assert len(registry) == 1


def test_contains_protocol(
    registry: ExporterRegistry,
) -> None:
    assert "test" in registry
    assert "missing" not in registry


def test_iteration_returns_exporters(
    exporter: Exporter,
    second_exporter: Exporter,
) -> None:
    registry = ExporterRegistry(
        [
            exporter,
            second_exporter,
        ]
    )

    result = list(registry)

    assert result == [
        exporter,
        second_exporter,
    ]


# ==============================================================================
# Part 12. Representation
# ==============================================================================


def test_repr(
    registry: ExporterRegistry,
) -> None:
    value = repr(registry)

    assert "ExporterRegistry" in value
    assert "count=1" in value
    assert "test" in value


def test_str(
    registry: ExporterRegistry,
) -> None:
    value = str(registry)

    assert "ExporterRegistry" in value
    assert "count=1" in value
    assert "test" in value


def test_repr_empty_registry() -> None:
    registry = ExporterRegistry()

    assert repr(registry) == (
        "ExporterRegistry(count=0, names=())"
    )
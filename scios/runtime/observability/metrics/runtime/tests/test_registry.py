"""
Tests for runtime.registry
"""

from __future__ import annotations

import json

import pytest

from scios.runtime.observability.metrics.runtime.registry import (
    DEFAULT_ENABLED,
    DEFAULT_LOCKED,
    DEFAULT_NAME,
    RuntimeRegistry,
)


# ==============================================================================
# Helpers
# ==============================================================================


def create_registry() -> RuntimeRegistry:

    registry = RuntimeRegistry()

    registry.register_recorder("r1", object())
    registry.register_collector("c1", object())
    registry.register_plugin("p1", object())

    return registry


# ==============================================================================
# Constructor
# ==============================================================================


def test_default_constructor():

    registry = RuntimeRegistry()

    assert registry.name == DEFAULT_NAME
    assert registry.enabled is DEFAULT_ENABLED
    assert registry.locked is DEFAULT_LOCKED
    assert registry.size == 0


def test_custom_constructor():

    registry = RuntimeRegistry(
        name="metrics",
        enabled=False,
        locked=True,
    )

    assert registry.name == "metrics"
    assert registry.enabled is False
    assert registry.locked is True


# ==============================================================================
# Slots / Properties
# ==============================================================================


def test_slots():

    assert hasattr(RuntimeRegistry, "__slots__")


def test_properties():

    registry = RuntimeRegistry()

    assert isinstance(registry.recorders, dict)
    assert isinstance(registry.collectors, dict)
    assert isinstance(registry.plugins, dict)


# ==============================================================================
# Recorder API
# ==============================================================================


def test_register_recorder():

    registry = RuntimeRegistry()

    registry.register_recorder("cpu", 1)

    assert registry.has_recorder("cpu")
    assert registry.get_recorder("cpu") == 1


def test_unregister_recorder():

    registry = RuntimeRegistry()

    registry.register_recorder("cpu", 1)

    registry.unregister_recorder("cpu")

    assert not registry.has_recorder("cpu")


def test_clear_recorders():

    registry = RuntimeRegistry()

    registry.register_recorder("a", 1)

    registry.clear_recorders()

    assert registry.recorders == {}


# ==============================================================================
# Collector API
# ==============================================================================


def test_register_collector():

    registry = RuntimeRegistry()

    registry.register_collector("mem", 2)

    assert registry.has_collector("mem")


def test_unregister_collector():

    registry = RuntimeRegistry()

    registry.register_collector("mem", 2)

    registry.unregister_collector("mem")

    assert not registry.has_collector("mem")


def test_clear_collectors():

    registry = RuntimeRegistry()

    registry.register_collector("x", 1)

    registry.clear_collectors()

    assert registry.collectors == {}


# ==============================================================================
# Plugin API
# ==============================================================================


def test_register_plugin():

    registry = RuntimeRegistry()

    registry.register_plugin("otel", object())

    assert registry.has_plugin("otel")


def test_unregister_plugin():

    registry = RuntimeRegistry()

    registry.register_plugin("otel", object())

    registry.unregister_plugin("otel")

    assert not registry.has_plugin("otel")


def test_clear_plugins():

    registry = RuntimeRegistry()

    registry.register_plugin("x", object())

    registry.clear_plugins()

    assert registry.plugins == {}


# ==============================================================================
# Registry Operations
# ==============================================================================


def test_clear():

    registry = create_registry()

    registry.clear()

    assert registry.size == 0


def test_reset():

    registry = create_registry()

    registry.reset()

    assert registry.size == 0
    assert registry.enabled is DEFAULT_ENABLED
    assert registry.locked is DEFAULT_LOCKED


def test_clone():

    registry = create_registry()

    clone = registry.clone()

    assert clone == registry
    assert clone is not registry


def test_copy():

    registry = create_registry()

    clone = registry.copy()

    assert clone == registry


def test_snapshot_restore():

    registry = create_registry()

    snap = registry.snapshot()

    registry.clear()

    registry.restore(snap)

    assert registry.size == 3


# ==============================================================================
# Validation
# ==============================================================================


def test_validate():

    registry = RuntimeRegistry()

    assert registry.validate()


def test_normalize():

    registry = RuntimeRegistry(name="  runtime ")

    registry.normalize()

    assert registry.name == "runtime"


# ==============================================================================
# Serialization
# ==============================================================================


def test_to_from_dict():

    registry = create_registry()

    data = registry.to_dict()

    restored = RuntimeRegistry.from_dict(data)

    assert restored == registry


def test_to_from_tuple():

    registry = create_registry()

    restored = RuntimeRegistry.from_tuple(
        registry.to_tuple()
    )

    assert restored == registry


def test_to_from_json():

    registry = create_registry()

    restored = RuntimeRegistry.from_json(
        registry.to_json()
    )

    assert restored == registry

    json.loads(registry.to_json())


# ==============================================================================
# Diagnostics
# ==============================================================================


def test_summary():

    registry = RuntimeRegistry()

    assert "size" in registry.summary()


def test_diagnostics():

    registry = RuntimeRegistry()

    assert registry.diagnostics()["valid"]


def test_report():

    registry = RuntimeRegistry()

    assert isinstance(
        registry.report(),
        dict,
    )


def test_status():

    registry = RuntimeRegistry()

    assert registry.status() == "ready"


# ==============================================================================
# Protocols
# ==============================================================================


def test_len():

    registry = create_registry()

    assert len(registry) == 3


def test_contains():

    registry = RuntimeRegistry()

    registry.register_recorder("cpu", 1)

    assert "cpu" in registry


def test_iter():

    registry = create_registry()

    assert len(list(registry)) == 3


def test_hash():

    registry = RuntimeRegistry()

    assert isinstance(hash(registry), int)


def test_eq():

    assert RuntimeRegistry() == RuntimeRegistry()


def test_repr():

    assert "RuntimeRegistry" in repr(RuntimeRegistry())


def test_str():

    assert "runtime" in str(RuntimeRegistry())


def test_bool():

    assert not RuntimeRegistry()

    registry = RuntimeRegistry()

    registry.register_recorder("cpu", 1)

    assert registry
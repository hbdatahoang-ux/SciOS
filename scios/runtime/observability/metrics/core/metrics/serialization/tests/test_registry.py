"""
Tests for registry.py

Python 3.11+
"""

from __future__ import annotations

import copy
import inspect
import pickle

import pytest

from scios.runtime.observability.metrics.core.metrics.serialization.registry import (
    Registry,
    DEFAULT_REGISTRY_NAME,
    DEFAULT_STRICT,
    DEFAULT_CASE_SENSITIVE,
    __all__,
)


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def registry() -> Registry:
    return Registry()


@pytest.fixture
def populated_registry() -> Registry:
    registry = Registry()

    registry.register("encoder", {"type": "encoder"})
    registry.register("decoder", {"type": "decoder"})
    registry.register("serializer", {"type": "serializer"})

    return registry


# ==============================================================================
# Part 1. Constructor
# ==============================================================================


def test_default_constructor():
    r = Registry()

    assert r.name == DEFAULT_REGISTRY_NAME
    assert r.strict is DEFAULT_STRICT
    assert r.case_sensitive is DEFAULT_CASE_SENSITIVE
    assert r.size == 0


def test_custom_constructor():
    items = {
        "a": 1,
        "b": 2,
    }

    r = Registry(
        name="custom",
        strict=False,
        case_sensitive=False,
        items=items,
    )

    assert r.name == "custom"
    assert r.strict is False
    assert r.case_sensitive is False
    assert r.size == 2


def test_slots():
    assert hasattr(Registry, "__slots__")

    expected = {
        "_name",
        "_strict",
        "_case_sensitive",
        "_items",
    }

    assert set(Registry.__slots__) == expected


def test_annotations():
    annotations = Registry.__annotations__

    assert "_name" in annotations
    assert "_strict" in annotations
    assert "_case_sensitive" in annotations
    assert "_items" in annotations


def test_signature():
    signature = inspect.signature(Registry)

    assert "name" in signature.parameters
    assert "strict" in signature.parameters
    assert "case_sensitive" in signature.parameters
    assert "items" in signature.parameters


# ==============================================================================
# Part 2. Properties
# ==============================================================================


def test_name_property(registry):
    assert registry.name == DEFAULT_REGISTRY_NAME


def test_strict_property(registry):
    assert registry.strict is DEFAULT_STRICT


def test_case_sensitive_property(registry):
    assert registry.case_sensitive is DEFAULT_CASE_SENSITIVE


def test_size_property(registry):
    assert registry.size == 0

    registry.register("a", 1)

    assert registry.size == 1


def test_items_property(registry):
    registry.register("a", 123)

    mapping = registry.mapping

    assert isinstance(mapping, dict)
    assert mapping["a"] == 123


# ==============================================================================
# Part 3. Registration
# ==============================================================================


def test_register(registry):
    value = object()

    returned = registry.register("encoder", value)

    assert returned is value
    assert registry.size == 1
    assert registry.get("encoder") is value


def test_unregister(registry):
    registry.register("encoder", 10)

    value = registry.unregister("encoder")

    assert value == 10
    assert registry.size == 0


def test_replace(registry):
    registry.register("x", 1)

    registry.replace("x", 2)

    assert registry.get("x") == 2


def test_update(registry):
    registry.update(
        {
            "a": 1,
            "b": 2,
        }
    )

    assert registry.size == 2
    assert registry.get("a") == 1
    assert registry.get("b") == 2


def test_clear(populated_registry):
    populated_registry.clear()

    assert populated_registry.size == 0


# ==============================================================================
# Part 4. Lookup
# ==============================================================================


def test_get(populated_registry):
    value = populated_registry.get("encoder")

    assert value is not None


def test_require(populated_registry):
    value = populated_registry.require("decoder")

    assert value is populated_registry.get("decoder")


def test_contains(populated_registry):
    assert populated_registry.contains("encoder")
    assert not populated_registry.contains("unknown")


def test_exists(populated_registry):
    assert populated_registry.exists("serializer")
    assert not populated_registry.exists("abc")


def test_resolve(populated_registry):
    value = populated_registry.resolve("encoder")

    assert value is populated_registry.get("encoder")

    obj = object()

    assert populated_registry.resolve(obj) is obj


# ==============================================================================
# Part 5. Collection
# ==============================================================================


def test_keys(populated_registry):
    keys = populated_registry.keys()

    assert set(keys) == {
        "encoder",
        "decoder",
        "serializer",
    }


def test_values(populated_registry):
    values = list(populated_registry.values())

    assert len(values) == 3


def test_items(populated_registry):
    items = list(populated_registry.items())

    assert len(items) == 3

    assert all(len(item) == 2 for item in items)


def test_names(populated_registry):
    names = populated_registry.names()

    assert sorted(names) == [
        "decoder",
        "encoder",
        "serializer",
    ]


def test_list(populated_registry):
    values = populated_registry.list()

    assert isinstance(values, list)
    assert len(values) == 3


# ==============================================================================
# Part 6. Snapshot
# ==============================================================================


def test_snapshot(populated_registry):
    snapshot = populated_registry.snapshot()

    assert snapshot["name"] == populated_registry.name
    assert snapshot["items"]


def test_restore(populated_registry):
    snapshot = populated_registry.snapshot()

    populated_registry.clear()

    assert populated_registry.size == 0

    populated_registry.restore(snapshot)

    assert populated_registry.size == 3


def test_copy(populated_registry):
    copied = populated_registry.copy()

    assert copied == populated_registry
    assert copied is not populated_registry


def test_deepcopy(populated_registry):
    copied = populated_registry.deepcopy()

    assert copied == populated_registry
    assert copied is not populated_registry


def test_clone(populated_registry):
    cloned = populated_registry.clone()

    assert cloned == populated_registry
    assert cloned is not populated_registry

# ==============================================================================
# Part 7. Validation
# ==============================================================================

def test_validate_name(registry):
    assert registry.validate_name("encoder") is True
    assert registry.validate_name("") is False
    assert registry.validate_name(None) is False


def test_validate_item(registry):
    item = object()

    assert registry.validate_item(item) is True
    assert registry.validate_item(None) is False


def test_validate(registry):
    registry.register("item", object())

    assert registry.validate() is True


def test_is_registered(registry):
    registry.register("item", object())

    assert registry.is_registered("item") is True
    assert registry.is_registered("missing") is False


def test_is_empty(registry):
    assert registry.is_empty() is True

    registry.register("item", object())

    assert registry.is_empty() is False


# ==============================================================================
# Part 8. Protocols
# ==============================================================================

def test_contains_protocol(registry):
    registry.register("item", 123)

    assert "item" in registry
    assert "missing" not in registry


def test_getitem(registry):
    registry.register("item", 123)

    assert registry["item"] == 123


def test_setitem(registry):
    registry["item"] = 456

    assert registry["item"] == 456


def test_delitem(registry):
    registry["item"] = 1

    del registry["item"]

    assert "item" not in registry


def test_iter(registry):
    registry.register("a", 1)
    registry.register("b", 2)

    assert list(iter(registry)) == ["a", "b"]


def test_len(registry):
    assert len(registry) == 0

    registry.register("a", 1)

    assert len(registry) == 1


def test_bool(registry):
    assert bool(registry) is False

    registry.register("a", 1)

    assert bool(registry) is True


def test_repr(registry):
    text = repr(registry)

    assert "Registry" in text


def test_str(registry):
    text = str(registry)

    assert "Registry" in text


def test_eq():
    a = Registry()
    b = Registry()

    assert a == b

    a.register("x", 1)

    assert a != b


def test_hash():
    registry = Registry()

    assert isinstance(hash(registry), int)


def test_pickle(registry):
    restored = pickle.loads(
        pickle.dumps(registry)
    )

    assert restored == registry


# ==============================================================================
# Part 9. Diagnostics
# ==============================================================================

def test_summary(registry):
    summary = registry.summary()

    assert summary["type"] == "Registry"
    assert summary["name"] == registry.name
    assert summary["size"] == registry.size


def test_diagnostics(registry):
    diagnostics = registry.diagnostics()

    assert diagnostics["type"] == "Registry"
    assert "summary" in diagnostics
    assert "hash" in diagnostics


def test_registry_report(registry):
    report = registry.registry_report()

    assert report["status"] == "ready"
    assert "registry" in report


def test_overall_status(registry):
    assert registry.overall_status() == "ready"


# ==============================================================================
# Part 10. Public API
# ==============================================================================

def test_public_api():
    expected = {
        "Registry",
        "DEFAULT_REGISTRY_NAME",
        "DEFAULT_STRICT",
        "DEFAULT_CASE_SENSITIVE",
    }

    assert expected.issubset(set(__all__))    
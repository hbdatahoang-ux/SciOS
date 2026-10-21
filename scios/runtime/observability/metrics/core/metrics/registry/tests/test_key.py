# ==============================================================================
# Part 1. Constructor
# ==============================================================================

from __future__ import annotations

import inspect

import scios.runtime.observability.metrics.core.metrics.registry.key as key_module

from scios.runtime.observability.metrics.core.metrics.registry.key import (
    MetricKey,
)


def test_default_constructor():

    metric_key = MetricKey()

    assert metric_key.name == ""
    assert metric_key.namespace == ""
    assert metric_key.labels == {}


def test_custom_constructor():

    metric_key = MetricKey(
        name="cpu_usage",
        namespace="system",
        labels={"host": "node1"},
    )

    assert metric_key.name == "cpu_usage"
    assert metric_key.namespace == "system"
    assert metric_key.labels == {
        "host": "node1",
    }


def test_slots():

    assert hasattr(MetricKey, "__slots__")


def test_annotations():

    annotations = MetricKey.__annotations__

    assert "name" in annotations
    assert "namespace" in annotations
    assert "labels" in annotations


def test_signature():

    signature = inspect.signature(MetricKey)

    assert "name" in signature.parameters
    assert "namespace" in signature.parameters
    assert "labels" in signature.parameters


# ==============================================================================
# Part 2. Properties
# ==============================================================================

def test_name_property():

    key = MetricKey(name="requests")

    assert key.name == "requests"


def test_namespace_property():

    key = MetricKey(namespace="runtime")

    assert key.namespace == "runtime"


def test_labels_property():

    labels = {"host": "a", "region": "us"}

    key = MetricKey(labels=labels)

    assert key.labels == labels


def test_fullname_property():

    key = MetricKey(
        name="requests",
        namespace="runtime",
    )

    assert key.fullname == "runtime.requests"


def test_state_property():

    key = MetricKey(
        "cpu",
        "system",
        {"host": "node1"},
    )

    state = key.state

    assert isinstance(state, dict)
    assert state["name"] == "cpu"
    assert state["namespace"] == "system"


# ==============================================================================
# Part 3. Comparison
# ==============================================================================

def test_equals():

    a = MetricKey("cpu", "system", {"host": "a"})
    b = MetricKey("cpu", "system", {"host": "a"})

    assert a.equals(b)
    assert a == b


def test_ordering():

    a = MetricKey("cpu")
    b = MetricKey("memory")

    assert a < b


def test_matching():

    a = MetricKey("cpu", "system", {"host": "a"})
    b = MetricKey("cpu", "system", {"host": "a"})

    assert a.matching(b)


def test_compatibility():

    a = MetricKey("cpu", "system")
    b = MetricKey("cpu", "system")

    assert a.compatibility(b)


# ==============================================================================
# Part 4. Serialization
# ==============================================================================

def test_to_dict():

    key = MetricKey(
        "cpu",
        "system",
        {"host": "a"},
    )

    data = key.to_dict()

    assert data["name"] == "cpu"
    assert data["namespace"] == "system"
    assert data["labels"] == {"host": "a"}


def test_from_dict():

    data = {
        "name": "memory",
        "namespace": "runtime",
        "labels": {"service": "api"},
    }

    key = MetricKey.from_dict(data)

    assert key.name == "memory"
    assert key.namespace == "runtime"
    assert key.labels == {"service": "api"}


def test_to_tuple():

    key = MetricKey(
        "cpu",
        "system",
        {"host": "a"},
    )

    value = key.to_tuple()

    assert isinstance(value, tuple)
    assert value[0] == "cpu"


def test_from_tuple():

    value = (
        "cpu",
        "system",
        {"host": "a"},
    )

    key = MetricKey.from_tuple(value)

    assert key.name == "cpu"
    assert key.namespace == "system"
    assert key.labels == {"host": "a"}


def test_snapshot():

    key = MetricKey(
        "cpu",
        "system",
        {"host": "a"},
    )

    snap = key.snapshot()

    assert isinstance(snap, dict)
    assert snap["name"] == "cpu"


def test_restore():

    key = MetricKey()

    key.restore(
        {
            "name": "memory",
            "namespace": "runtime",
            "labels": {"host": "node1"},
        }
    )

    assert key.name == "memory"
    assert key.namespace == "runtime"
    assert key.labels == {"host": "node1"}


# ==============================================================================
# Part 5. Validation
# ==============================================================================

def test_validate_name():

    assert MetricKey.validate_name("cpu")
    assert not MetricKey.validate_name("")


def test_validate_namespace():

    assert MetricKey.validate_namespace("system")
    assert not MetricKey.validate_namespace(None)


def test_validate_labels():

    assert MetricKey.validate_labels({"a": "b"})
    assert not MetricKey.validate_labels([])


def test_validate_key():

    key = MetricKey("cpu", "system")

    assert key.validate_key()


def test_validate():

    key = MetricKey(
        "cpu",
        "system",
        {"host": "a"},
    )

    assert key.validate()

# ==============================================================================
# Part 6. Utilities
# ==============================================================================

def test_clone():

    key = MetricKey(
        "cpu",
        "system",
        {"host": "node1"},
    )

    cloned = key.clone()

    assert cloned == key
    assert cloned is not key


def test_copy():

    key = MetricKey(
        "cpu",
        "system",
        {"host": "node1"},
    )

    copied = key.copy()

    assert copied == key
    assert copied is not key


def test_merge():

    key = MetricKey(
        "cpu",
        "system",
        {"host": "node1"},
    )

    merged = key.merge(
        labels={"region": "us"},
    )

    assert merged.labels["host"] == "node1"
    assert merged.labels["region"] == "us"


def test_update():

    key = MetricKey(
        "cpu",
        "system",
        {"host": "node1"},
    )

    key.update(
        name="memory",
        namespace="runtime",
        labels={"service": "api"},
    )

    assert key.name == "memory"
    assert key.namespace == "runtime"
    assert key.labels == {"service": "api"}


def test_clear():

    key = MetricKey(
        "cpu",
        "system",
        {"host": "node1"},
    )

    key.clear()

    assert key.name == ""
    assert key.namespace == ""
    assert key.labels == {}


def test_normalize():

    key = MetricKey(
        " CPU ",
        " System ",
        {" Host ": " Node1 "},
    )

    key.normalize()

    assert key.name == "cpu"
    assert key.namespace == "system"
    assert key.labels == {"host": "Node1"}


# ==============================================================================
# Part 7. Protocols
# ==============================================================================

def test_hash():

    key = MetricKey("cpu")

    assert isinstance(hash(key), int)


def test_eq():

    left = MetricKey("cpu", "system")
    right = MetricKey("cpu", "system")

    assert left == right


def test_lt():

    left = MetricKey("cpu")
    right = MetricKey("memory")

    assert left < right


def test_repr():

    key = MetricKey("cpu")

    text = repr(key)

    assert "MetricKey" in text


def test_str():

    key = MetricKey("cpu", "system")

    text = str(key)

    assert isinstance(text, str)
    assert "cpu" in text


def test_bool():

    assert bool(MetricKey("cpu"))
    assert not bool(MetricKey())


# ==============================================================================
# Part 8. Diagnostics
# ==============================================================================

def test_summary():

    key = MetricKey(
        "cpu",
        "system",
    )

    result = key.summary()

    assert isinstance(result, dict)
    assert result["name"] == "cpu"


def test_diagnostics():

    key = MetricKey(
        "cpu",
        "system",
    )

    result = key.diagnostics()

    assert isinstance(result, dict)
    assert "valid" in result


def test_key_report():

    key = MetricKey(
        "cpu",
        "system",
    )

    report = key.key_report()

    assert isinstance(report, dict)


def test_overall_status():

    key = MetricKey(
        "cpu",
        "system",
    )

    assert isinstance(key.overall_status(), bool)


# ==============================================================================
# Part 9. Public API
# ==============================================================================

def test_public_api():

    assert hasattr(key_module, "__all__")

    expected = {
        "MetricKey",
    }

    assert expected.issubset(set(key_module.__all__))
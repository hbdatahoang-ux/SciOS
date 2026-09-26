# ==============================================================================
# Part 1. Constructor
# ==============================================================================

from __future__ import annotations

import inspect

import scios.runtime.observability.metrics.core.metrics.registry.namespace as namespace

assert "MetricNamespace" in namespace.__all__

from scios.runtime.observability.metrics.core.metrics.registry.namespace import (
    MetricNamespace,
)


def test_default_constructor():

    ns = MetricNamespace()

    assert ns.name == ""
    assert ns.parent == ""
    assert isinstance(ns.state, dict)


def test_custom_constructor():

    ns = MetricNamespace(
        name="system",
        parent="runtime",
    )

    assert ns.name == "system"
    assert ns.parent == "runtime"


def test_slots():

    assert hasattr(MetricNamespace, "__slots__")


def test_annotations():

    annotations = MetricNamespace.__annotations__

    assert "name" in annotations
    assert "parent" in annotations
    assert "state" in annotations


def test_signature():

    sig = inspect.signature(MetricNamespace)

    assert "name" in sig.parameters
    assert "parent" in sig.parameters
    assert "state" in sig.parameters


# ==============================================================================
# Part 2. Properties
# ==============================================================================


def test_name_property():

    ns = MetricNamespace(name="system")

    assert ns.name == "system"


def test_parent_property():

    ns = MetricNamespace(parent="runtime")

    assert ns.parent == "runtime"


def test_fullname_property():

    ns = MetricNamespace(
        name="system",
        parent="runtime",
    )

    assert ns.fullname == "runtime.system"


def test_depth_property():

    ns = MetricNamespace(
        name="cpu",
        parent="runtime.system",
    )

    assert ns.depth == 3


def test_state_property():

    ns = MetricNamespace(
        name="cpu",
        parent="system",
    )

    assert isinstance(ns.state, dict)


# ==============================================================================
# Part 3. Operations
# ==============================================================================


def test_rename():

    ns = MetricNamespace(name="cpu")

    ns.rename("memory")

    assert ns.name == "memory"


def test_reparent():

    ns = MetricNamespace(
        name="cpu",
        parent="system",
    )

    ns.reparent("runtime")

    assert ns.parent == "runtime"


def test_clear():

    ns = MetricNamespace(
        name="cpu",
        parent="system",
    )

    ns.clear()

    assert ns.name == ""
    assert ns.parent in ("", None)


def test_normalize():

    ns = MetricNamespace(
        name=" CPU ",
        parent=" SYSTEM ",
    )

    ns.normalize()

    assert ns.name == "cpu"
    assert ns.parent == "system"


# ==============================================================================
# Part 4. Serialization
# ==============================================================================


def test_to_dict():

    ns = MetricNamespace(
        name="cpu",
        parent="system",
    )

    data = ns.to_dict()

    assert data["name"] == "cpu"
    assert data["parent"] == "system"


def test_from_dict():

    ns = MetricNamespace.from_dict(
        {
            "name": "memory",
            "parent": "runtime",
        }
    )

    assert ns.name == "memory"
    assert ns.parent == "runtime"


def test_to_tuple():

    ns = MetricNamespace(
        name="cpu",
        parent="system",
    )

    value = ns.to_tuple()

    assert value[0] == "cpu"
    assert value[1] == "system"


def test_from_tuple():

    ns = MetricNamespace.from_tuple(
        (
            "memory",
            "runtime",
        )
    )

    assert ns.name == "memory"
    assert ns.parent == "runtime"


def test_snapshot():

    ns = MetricNamespace(
        name="cpu",
        parent="system",
    )

    snap = ns.snapshot()

    assert snap["name"] == "cpu"
    assert snap["parent"] == "system"


def test_restore():

    ns = MetricNamespace()

    ns.restore(
        {
            "name": "memory",
            "parent": "runtime",
        }
    )

    assert ns.name == "memory"
    assert ns.parent == "runtime"


# ==============================================================================
# Part 5. Validation
# ==============================================================================


def test_validate_name():

    assert MetricNamespace.validate_name("system")

    assert not MetricNamespace.validate_name(123)


def test_validate_parent():

    assert MetricNamespace.validate_parent("runtime")

    assert MetricNamespace.validate_parent(None)

    assert not MetricNamespace.validate_parent(123)


def test_validate_namespace():

    ns = MetricNamespace(
        name="cpu",
        parent="system",
    )

    assert MetricNamespace.validate_namespace(ns)


def test_validate():

    ns = MetricNamespace(
        name="cpu",
        parent="system",
    )

    assert ns.validate()

# ==============================================================================
# Part 6. Utilities
# ==============================================================================


def test_clone():

    ns = MetricNamespace(
        name="cpu",
        parent="system",
    )

    cloned = ns.clone()

    assert cloned == ns
    assert cloned is not ns


def test_copy():

    ns = MetricNamespace(
        name="cpu",
        parent="system",
    )

    copied = ns.copy()

    assert copied == ns
    assert copied is not ns


def test_merge():

    ns = MetricNamespace(
        name="cpu",
        parent="system",
    )

    merged = ns.merge(
        name="memory",
    )

    assert merged.name == "memory"
    assert merged.parent == "system"

    merged = ns.merge(
        parent="runtime",
    )

    assert merged.name == "cpu"
    assert merged.parent == "runtime"


def test_update():

    ns = MetricNamespace(
        name="cpu",
        parent="system",
    )

    ns.update(
        name="memory",
        parent="runtime",
    )

    assert ns.name == "memory"
    assert ns.parent == "runtime"


def test_clear():

    ns = MetricNamespace(
        name="cpu",
        parent="system",
    )

    ns.clear()

    assert ns.name == ""
    assert ns.parent in ("", None)


# ==============================================================================
# Part 7. Protocols
# ==============================================================================


def test_hash():

    ns = MetricNamespace(
        name="cpu",
        parent="system",
    )

    assert isinstance(hash(ns), int)


def test_eq():

    a = MetricNamespace(
        name="cpu",
        parent="system",
    )

    b = MetricNamespace(
        name="cpu",
        parent="system",
    )

    c = MetricNamespace(
        name="memory",
        parent="system",
    )

    assert a == b
    assert a != c


def test_lt():

    a = MetricNamespace(
        name="a",
        parent="system",
    )

    b = MetricNamespace(
        name="b",
        parent="system",
    )

    assert a < b


def test_repr():

    ns = MetricNamespace(
        name="cpu",
        parent="system",
    )

    text = repr(ns)

    assert "MetricNamespace" in text
    assert "cpu" in text


def test_str():

    ns = MetricNamespace(
        name="cpu",
        parent="system",
    )

    assert str(ns) == "system.cpu"


def test_bool():

    assert bool(MetricNamespace("cpu"))

    assert not bool(MetricNamespace())


# ==============================================================================
# Part 8. Diagnostics
# ==============================================================================


def test_summary():

    ns = MetricNamespace(
        name="cpu",
        parent="system",
    )

    summary = ns.summary()

    assert isinstance(summary, dict)
    assert summary["name"] == "cpu"
    assert summary["parent"] == "system"
    assert summary["fullname"] == "system.cpu"


def test_diagnostics():

    ns = MetricNamespace(
        name="cpu",
        parent="system",
    )

    diagnostics = ns.diagnostics()

    assert isinstance(diagnostics, dict)
    assert diagnostics["valid"] is True
    assert diagnostics["fullname"] == "system.cpu"


def test_namespace_report():

    ns = MetricNamespace(
        name="cpu",
        parent="system",
    )

    report = ns.namespace_report()

    assert isinstance(report, dict)
    assert "summary" in report
    assert "diagnostics" in report


def test_overall_status():

    ns = MetricNamespace(
        name="cpu",
        parent="system",
    )

    assert ns.overall_status()


# ==============================================================================
# Part 9. Public API
# ==============================================================================


def test_public_api():

    expected = {
        "MetricNamespace",
    }

    for symbol in expected:
        assert symbol in namespace.__all__    
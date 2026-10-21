"""
Tests for MetricSnapshot.
"""

from __future__ import annotations

import inspect

from scios.runtime.observability.metrics.core.metrics.metric import (
    Metric,
)
from scios.runtime.observability.metrics.core.metrics.core.metadata import (
    MetricMetadata,
)
from scios.runtime.observability.metrics.core.metrics.registry.snapshot import (
    MetricSnapshot,
)

__all__: list[str] = []


# ==============================================================================
# Helpers
# ==============================================================================


def make_metric(name: str = "cpu") -> Metric:
    """
    Create a Metric using the current Metric API.
    """

    return Metric(
        metadata=MetricMetadata(
            name=name,
        ),
    )


# ==============================================================================
# Part 1. Constructor
# ==============================================================================


def test_default_constructor():

    snapshot = MetricSnapshot()

    assert snapshot.name == ""
    assert snapshot.size == 0
    assert isinstance(snapshot.metrics, dict)
    assert isinstance(snapshot.state, dict)


def test_custom_constructor():

    snapshot = MetricSnapshot("runtime")

    assert snapshot.name == "runtime"


def test_slots():

    assert hasattr(
        MetricSnapshot,
        "__slots__",
    )


def test_annotations():

    annotations = MetricSnapshot.__annotations__

    assert "name" in annotations
    assert "timestamp" in annotations
    assert "metrics" in annotations
    assert "state" in annotations


def test_signature():

    sig = inspect.signature(
        MetricSnapshot
    )

    assert "name" in sig.parameters


# ==============================================================================
# Part 2. Properties
# ==============================================================================


def test_name_property():

    snapshot = MetricSnapshot("cpu")

    assert snapshot.name == "cpu"


def test_timestamp_property():

    snapshot = MetricSnapshot()

    assert isinstance(
        snapshot.timestamp,
        str,
    )


def test_metrics_property():

    snapshot = MetricSnapshot()

    assert isinstance(
        snapshot.metrics,
        dict,
    )


def test_size_property():

    snapshot = MetricSnapshot()

    assert snapshot.size == 0


def test_state_property():

    snapshot = MetricSnapshot()

    assert isinstance(
        snapshot.state,
        dict,
    )


# ==============================================================================
# Part 3. Operations
# ==============================================================================


def test_add():

    snapshot = MetricSnapshot()

    metric = make_metric("cpu")

    snapshot.add(metric)

    assert snapshot.size == 1


def test_remove():

    snapshot = MetricSnapshot()

    metric = make_metric("cpu")

    snapshot.add(metric)
    snapshot.remove(metric)

    assert snapshot.size == 0


def test_get():

    snapshot = MetricSnapshot()

    metric = make_metric("cpu")

    snapshot.add(metric)

    assert snapshot.get("cpu") == metric


def test_contains():

    snapshot = MetricSnapshot()

    metric = make_metric("cpu")

    snapshot.add(metric)

    assert snapshot.contains(metric)


def test_clear():

    snapshot = MetricSnapshot()

    snapshot.add(
        make_metric("cpu")
    )

    snapshot.clear()

    assert snapshot.size == 0


def test_normalize():

    snapshot = MetricSnapshot(
        " CPU "
    )

    snapshot.normalize()

    assert snapshot.name == "cpu"


# ==============================================================================
# Part 4. Serialization
# ==============================================================================


def test_to_dict():

    snapshot = MetricSnapshot(
        "cpu"
    )

    data = snapshot.to_dict()

    assert data["name"] == "cpu"


def test_from_dict():

    snapshot = MetricSnapshot.from_dict(
        {
            "name": "cpu",
            "timestamp": "",
            "metrics": {},
            "state": {},
        }
    )

    assert snapshot.name == "cpu"


def test_to_tuple():

    snapshot = MetricSnapshot(
        "cpu"
    )

    value = snapshot.to_tuple()

    assert isinstance(
        value,
        tuple,
    )


def test_from_tuple():

    snapshot = MetricSnapshot(
        "cpu"
    )

    restored = MetricSnapshot.from_tuple(
        snapshot.to_tuple()
    )

    assert restored == snapshot


def test_snapshot():

    snapshot = MetricSnapshot(
        "cpu"
    )

    snap = snapshot.snapshot()

    assert isinstance(
        snap,
        dict,
    )


def test_restore():

    snapshot = MetricSnapshot()

    snapshot.restore(
        {
            "name": "runtime",
            "timestamp": "",
            "metrics": {},
            "state": {},
        }
    )

    assert snapshot.name == "runtime"


# ==============================================================================
# Part 5. Validation
# ==============================================================================


def test_validate_name():

    assert MetricSnapshot.validate_name(
        "cpu"
    )


def test_validate_metrics():

    assert MetricSnapshot.validate_metrics(
        {}
    )


def test_validate_snapshot():

    snapshot = MetricSnapshot()

    assert MetricSnapshot.validate_snapshot(
        snapshot
    )


def test_validate():

    snapshot = MetricSnapshot()

    assert snapshot.validate()


# ==============================================================================
# Part 6. Utilities
# ==============================================================================


def test_clone():

    snapshot = MetricSnapshot(
        "cpu"
    )

    cloned = snapshot.clone()

    assert cloned == snapshot
    assert cloned is not snapshot


def test_copy():

    snapshot = MetricSnapshot(
        "cpu"
    )

    copied = snapshot.copy()

    assert copied == snapshot
    assert copied is not snapshot


def test_merge():

    a = MetricSnapshot()

    b = MetricSnapshot()

    b.add(
        make_metric("cpu")
    )

    a.merge(b)

    assert a.size == 1
    assert a.contains(
        make_metric("cpu")
    ) or a.get("cpu") is not None


def test_update():

    a = MetricSnapshot()

    b = MetricSnapshot()

    b.add(
        make_metric("cpu")
    )

    a.update(b)

    assert a.size == 1
    assert a.get("cpu") is not None


def test_reset():

    snapshot = MetricSnapshot()

    snapshot.add(
        make_metric("cpu")
    )

    snapshot.reset()

    assert snapshot.size == 0


# ==============================================================================
# Part 7. Protocols
# ==============================================================================


def test_hash():

    snapshot = MetricSnapshot()

    assert isinstance(
        hash(snapshot),
        int,
    )


def test_eq():

    a = MetricSnapshot()

    b = MetricSnapshot()

    assert a == b


def test_repr():

    snapshot = MetricSnapshot()

    assert "MetricSnapshot" in repr(snapshot)


def test_str():

    snapshot = MetricSnapshot()

    assert isinstance(
        str(snapshot),
        str,
    )


def test_bool():

    snapshot = MetricSnapshot()

    assert not snapshot

    snapshot.add(
        make_metric("cpu")
    )

    assert snapshot


# ==============================================================================
# Part 8. Diagnostics
# ==============================================================================


def test_summary():

    snapshot = MetricSnapshot()

    result = snapshot.summary()

    assert isinstance(
        result,
        dict,
    )


def test_diagnostics():

    snapshot = MetricSnapshot()

    result = snapshot.diagnostics()

    assert isinstance(
        result,
        dict,
    )

    assert result["valid"]


def test_snapshot_report():

    snapshot = MetricSnapshot()

    report = snapshot.snapshot_report()

    assert isinstance(
        report,
        dict,
    )

    assert "summary" in report


def test_overall_status():

    snapshot = MetricSnapshot()

    assert (
        snapshot.overall_status()
        == "healthy"
    )


# ==============================================================================
# Part 9. Public API
# ==============================================================================


def test_public_api():

    from scios.runtime.observability.metrics.core.metrics.registry.snapshot import (
        __all__,
    )

    assert "MetricSnapshot" in __all__
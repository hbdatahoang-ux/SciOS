# ==============================================================================
# Part 1. Constructor
# ==============================================================================

from __future__ import annotations

import inspect

import scios.runtime.observability.metrics.core.metrics.registry.filter as filter_module

assert "MetricFilter" in filter_module.__all__

from scios.runtime.observability.metrics.core.metrics.registry.entry import MetricEntry
from scios.runtime.observability.metrics.core.metrics.registry.filter import MetricFilter
from scios.runtime.observability.metrics.core.metrics.registry.key import MetricKey


def test_default_constructor():

    f = MetricFilter()

    assert f.name == ""
    assert f.namespace == ""
    assert f.labels == {}
    assert f.metric is None
    assert f.predicate is None
    assert isinstance(f.state, dict)


def test_custom_constructor():

    f = MetricFilter(
        name="cpu",
        namespace="system",
        labels={"host": "node1"},
        metric="counter",
    )

    assert f.name == "cpu"
    assert f.namespace == "system"
    assert f.labels == {"host": "node1"}
    assert f.metric == "counter"


def test_slots():

    assert hasattr(MetricFilter, "__slots__")


def test_annotations():

    annotations = MetricFilter.__annotations__

    assert "name" in annotations
    assert "namespace" in annotations
    assert "labels" in annotations
    assert "metric" in annotations
    assert "predicate" in annotations
    assert "state" in annotations


def test_signature():

    sig = inspect.signature(MetricFilter)

    assert "name" in sig.parameters
    assert "namespace" in sig.parameters
    assert "labels" in sig.parameters
    assert "metric" in sig.parameters
    assert "predicate" in sig.parameters
    assert "state" in sig.parameters


# ==============================================================================
# Part 2. Properties
# ==============================================================================


def test_name_property():

    f = MetricFilter(name="cpu")

    assert f.name == "cpu"


def test_namespace_property():

    f = MetricFilter(namespace="system")

    assert f.namespace == "system"


def test_labels_property():

    f = MetricFilter(labels={"host": "node1"})

    assert f.labels == {"host": "node1"}


def test_metric_property():

    f = MetricFilter(metric="counter")

    assert f.metric == "counter"


def test_predicate_property():

    fn = lambda e: True

    f = MetricFilter(predicate=fn)

    assert f.predicate is fn


def test_state_property():

    f = MetricFilter()

    assert isinstance(f.state, dict)


# ==============================================================================
# Part 3. Matching
# ==============================================================================


def test_match_name():

    f = MetricFilter(name="cpu")

    key = MetricKey("cpu")

    assert f.match_name(key)


def test_match_namespace():

    f = MetricFilter(namespace="system")

    key = MetricKey("cpu", "system")

    assert f.match_namespace(key)


def test_match_labels():

    f = MetricFilter(labels={"host": "node1"})

    key = MetricKey(
        "cpu",
        "system",
        {"host": "node1"},
    )

    assert f.match_labels(key)


def test_match_metric():

    f = MetricFilter(metric="counter")

    entry = MetricEntry(
        key=MetricKey("cpu"),
        metric="counter",
    )

    assert f.match_metric(entry)


def test_match():

    entry = MetricEntry(
        key=MetricKey(
            "cpu",
            "system",
            {"host": "node1"},
        ),
        metric="counter",
    )

    f = MetricFilter(
        name="cpu",
        namespace="system",
        labels={"host": "node1"},
        metric="counter",
    )

    assert f.match(entry)


def test_filter():

    entries = [
        MetricEntry(
            key=MetricKey("cpu"),
            metric="counter",
        ),
        MetricEntry(
            key=MetricKey("memory"),
            metric="gauge",
        ),
    ]

    result = MetricFilter(
        name="cpu",
    ).filter(entries)

    assert len(result) == 1
    assert result[0].key.name == "cpu"


# ==============================================================================
# Part 4. Serialization
# ==============================================================================


def test_to_dict():

    f = MetricFilter(
        name="cpu",
        namespace="system",
        labels={"host": "node1"},
        metric="counter",
    )

    data = f.to_dict()

    assert data["name"] == "cpu"
    assert data["namespace"] == "system"
    assert data["labels"] == {"host": "node1"}
    assert data["metric"] == "counter"


def test_from_dict():

    f = MetricFilter.from_dict(
        {
            "name": "cpu",
            "namespace": "system",
            "labels": {"host": "node1"},
            "metric": "counter",
        }
    )

    assert f.name == "cpu"
    assert f.namespace == "system"
    assert f.metric == "counter"


def test_to_tuple():

    f = MetricFilter(
        name="cpu",
        namespace="system",
        metric="counter",
    )

    value = f.to_tuple()

    assert isinstance(value, tuple)
    assert value[0] == "cpu"


def test_from_tuple():

    f = MetricFilter.from_tuple(
        (
            "cpu",
            "system",
            (("host", "node1"),),
            "counter",
        )
    )

    assert f.name == "cpu"
    assert f.namespace == "system"
    assert f.labels == {"host": "node1"}
    assert f.metric == "counter"


def test_snapshot():

    f = MetricFilter(name="cpu")

    snap = f.snapshot()

    assert isinstance(snap, dict)
    assert snap["name"] == "cpu"


def test_restore():

    f = MetricFilter()

    f.restore(
        {
            "name": "cpu",
            "namespace": "system",
            "labels": {},
            "metric": "counter",
        }
    )

    assert f.name == "cpu"
    assert f.namespace == "system"
    assert f.metric == "counter"


# ==============================================================================
# Part 5. Validation
# ==============================================================================


def test_validate_name():

    assert MetricFilter.validate_name("cpu")
    assert not MetricFilter.validate_name(1)


def test_validate_namespace():

    assert MetricFilter.validate_namespace("system")
    assert not MetricFilter.validate_namespace(1)


def test_validate_labels():

    assert MetricFilter.validate_labels({})
    assert not MetricFilter.validate_labels([])


def test_validate_metric():

    assert MetricFilter.validate_metric("counter")
    assert MetricFilter.validate_metric(None)
    assert not MetricFilter.validate_metric(123)


def test_validate_filter():

    assert MetricFilter.validate_filter(MetricFilter())


def test_validate():

    assert MetricFilter().validate()

# ==============================================================================
# Part 6. Utilities
# ==============================================================================


def test_clone():

    f = MetricFilter(
        name="cpu",
        namespace="system",
        labels={"host": "node1"},
        metric="counter",
    )

    cloned = f.clone()

    assert cloned == f
    assert cloned is not f
    assert cloned.labels is not f.labels


def test_copy():

    f = MetricFilter(name="cpu")

    copied = f.copy()

    assert copied == f
    assert copied is not f


def test_merge():

    f = MetricFilter(
        name="cpu",
        namespace="system",
    )

    merged = f.merge(
        namespace="runtime",
        labels={"host": "node1"},
        metric="gauge",
    )

    assert merged.name == "cpu"
    assert merged.namespace == "runtime"
    assert merged.labels == {"host": "node1"}
    assert merged.metric == "gauge"


def test_update():

    f = MetricFilter()

    f.update(
        name="memory",
        namespace="runtime",
        labels={"host": "node2"},
        metric="counter",
    )

    assert f.name == "memory"
    assert f.namespace == "runtime"
    assert f.labels == {"host": "node2"}
    assert f.metric == "counter"


def test_clear():

    f = MetricFilter(
        name="cpu",
        namespace="system",
        labels={"host": "node1"},
        metric="counter",
    )

    f.clear()

    assert f.name == ""
    assert f.namespace == ""
    assert f.labels == {}
    assert f.metric is None


def test_normalize():

    f = MetricFilter(
        name=" CPU ",
        namespace=" SYSTEM ",
        labels={" Host ": " Node1 "},
        metric=" Counter ",
    )

    f.normalize()

    assert f.name == "cpu"
    assert f.namespace == "system"
    assert f.labels == {"Host": "Node1"}
    assert f.metric == "counter"


# ==============================================================================
# Part 7. Protocols
# ==============================================================================


def test_hash():

    assert isinstance(hash(MetricFilter(name="cpu")), int)


def test_eq():

    a = MetricFilter(name="cpu")

    b = MetricFilter(name="cpu")

    assert a == b


def test_lt():

    a = MetricFilter(name="a")

    b = MetricFilter(name="b")

    assert a < b


def test_repr():

    value = repr(MetricFilter(name="cpu"))

    assert "MetricFilter" in value


def test_str():

    f = MetricFilter(
        name="cpu",
        namespace="system",
    )

    assert str(f) == "system.cpu"


def test_bool():

    assert bool(MetricFilter(name="cpu"))

    assert not bool(MetricFilter())


# ==============================================================================
# Part 8. Diagnostics
# ==============================================================================


def test_summary():

    f = MetricFilter(
        name="cpu",
        namespace="system",
        metric="counter",
    )

    summary = f.summary()

    assert isinstance(summary, dict)
    assert summary["name"] == "cpu"
    assert summary["namespace"] == "system"
    assert summary["metric"] == "counter"


def test_diagnostics():

    diag = MetricFilter(name="cpu").diagnostics()

    assert isinstance(diag, dict)
    assert diag["valid"]


def test_filter_report():

    report = MetricFilter(name="cpu").filter_report()

    assert isinstance(report, dict)
    assert "summary" in report
    assert "diagnostics" in report


def test_overall_status():

    assert MetricFilter().overall_status()


# ==============================================================================
# Part 9. Public API
# ==============================================================================


def test_public_api():

    expected = {
        "DEFAULT_METRIC",
        "DEFAULT_PREDICATE",
        "MetricPredicate",
        "MetricSnapshot",
        "MetricFilter",
    }

    assert expected.issubset(set(filter_module.__all__))    
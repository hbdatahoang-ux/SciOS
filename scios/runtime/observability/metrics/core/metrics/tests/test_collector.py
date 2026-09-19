# ==========================================================
# Part 1. Imports
# ==========================================================

from __future__ import annotations

import copy
import inspect
import pickle
from typing import get_type_hints

import pytest

from scios.runtime.observability.metrics.core.metrics.core.collector import (
    MetricCollector,
)
from scios.runtime.observability.metrics.core.metrics.core.metric import (
    Metric,
)
from scios.runtime.observability.metrics.core.metrics.core.registry import (
    MetricRegistry,
)
from scios.runtime.observability.metrics.core.metrics.core.metric_hooks import (
    MetricHooks,
)

# ==========================================================
# Test Callbacks
# ==========================================================


def before_collect() -> None:
    return None


def after_collect() -> None:
    return None


# ==========================================================
# Part 2. Fixtures
# ==========================================================


@pytest.fixture
def empty_collector() -> MetricCollector:
    return MetricCollector()


@pytest.fixture
def custom_collector() -> MetricCollector:
    registry = MetricRegistry()
    registry.register(
        Metric(
            name="cpu",
            value=10.0,
        )
    )

    hooks = MetricHooks()
    hooks.before_collect.append(before_collect)
    hooks.after_collect.append(after_collect)

    return MetricCollector(
        registry=registry,
        hooks=hooks,
        enabled=False,
    )


@pytest.fixture
def full_collector() -> MetricCollector:
    registry = MetricRegistry()

    registry.register(Metric(name="cpu", value=10.0))
    registry.register(Metric(name="memory", value=20.0))
    registry.register(Metric(name="disk", value=30.0))

    hooks = MetricHooks()
    hooks.before_collect.append(before_collect)
    hooks.after_collect.append(after_collect)

    collector = MetricCollector(
        registry=registry,
        hooks=hooks,
        enabled=True,
    )

    return collector


# ==========================================================
# Part 3. Construction
# ==========================================================


class TestConstruction:
    def test_create_default(self):
        collector = MetricCollector()

        assert isinstance(collector, MetricCollector)
        assert isinstance(collector.registry, MetricRegistry)
        assert isinstance(collector.hooks, MetricHooks)
        assert collector.enabled is True

    def test_create_custom(
        self,
        custom_collector: MetricCollector,
    ):
        assert custom_collector.registry is not None
        assert custom_collector.hooks is not None
        assert custom_collector.enabled is False

    def test_create_empty(
        self,
        empty_collector: MetricCollector,
    ):
        assert len(empty_collector.registry) == 0
        assert len(empty_collector.hooks.before_collect) == 0
        assert empty_collector.enabled is True

    def test_create_full(
        self,
        full_collector: MetricCollector,
    ):
        assert len(full_collector.registry) == 3
        assert len(full_collector.hooks.before_collect) == 1
        assert len(full_collector.hooks.after_collect) == 1
        assert full_collector.enabled is True

# ==========================================================
# Part 4. Identity
# ==========================================================


class TestIdentity:
    def test_registry(
        self,
        full_collector: MetricCollector,
    ):
        assert isinstance(full_collector.registry, MetricRegistry)

    def test_hooks(
        self,
        full_collector: MetricCollector,
    ):
        assert isinstance(full_collector.hooks, MetricHooks)

    def test_buffer(
        self,
        full_collector: MetricCollector,
    ):
        assert isinstance(full_collector.buffer, list)

    def test_enabled(
        self,
        full_collector: MetricCollector,
    ):
        assert full_collector.enabled is True

    def test_length(
        self,
        full_collector: MetricCollector,
    ):
        assert len(full_collector) == len(full_collector.registry)


# ==========================================================
# Part 5. Defaults
# ==========================================================


class TestDefaults:
    def test_default_empty(self):
        collector = MetricCollector()

        assert len(collector.registry) == 0
        assert collector.buffer == []

    def test_default_mutable_independent(self):
        c1 = MetricCollector()
        c2 = MetricCollector()

        c1.buffer.append("x")

        assert c1.buffer != c2.buffer
        assert c2.buffer == []

    def test_default_enabled(self):
        collector = MetricCollector()

        assert collector.enabled is True


# ==========================================================
# Part 6. Collection
# ==========================================================


class TestCollection:
    def test_collect(
        self,
        full_collector: MetricCollector,
    ):
        metrics = full_collector.collect()

        assert len(metrics) == 3
        assert len(full_collector.buffer) == 3

    def test_collect_single(self):
        collector = MetricCollector()

        metric = Metric(
            name="cpu",
            value=10.0,
        )

        collector.registry.register(metric)

        metrics = collector.collect()

        assert len(metrics) == 1
        assert metrics[0] == metric

    def test_collect_multiple(
        self,
        full_collector: MetricCollector,
    ):
        metrics = full_collector.collect()

        assert len(metrics) == 3

        names = {m.name for m in metrics}

        assert names == {"cpu", "memory", "disk"}

    def test_collect_duplicate(self):
        collector = MetricCollector()

        metric = Metric(
            name="cpu",
            value=10.0,
        )

        collector.registry.register(metric)
        collector.collect()
        collector.collect()

        assert len(collector.buffer) == 2

    def test_clear(
        self,
        full_collector: MetricCollector,
    ):
        full_collector.collect()

        assert len(full_collector.buffer) == 3

        full_collector.clear()

        assert full_collector.buffer == [] 

# ==========================================================
# Part 7. Lookup
# ==========================================================


class TestLookup:
    def test_get(
        self,
        full_collector: MetricCollector,
    ):
        metric = full_collector.get("cpu")

        assert metric is not None
        assert metric.name == "cpu"

    def test_contains(
        self,
        full_collector: MetricCollector,
    ):
        assert "cpu" in full_collector
        assert "memory" in full_collector
        assert "disk" in full_collector
        assert "gpu" not in full_collector

    def test_metrics(
        self,
        full_collector: MetricCollector,
    ):
        metrics = full_collector.metrics()

        assert len(metrics) == 3
        assert all(isinstance(m, Metric) for m in metrics)

    def test_values(
        self,
        full_collector: MetricCollector,
    ):
        values = full_collector.values()

        assert len(values) == 3
        assert all(isinstance(v, Metric) for v in values)

    def test_items(
        self,
        full_collector: MetricCollector,
    ):
        items = full_collector.items()

        assert len(items) == 3

        for name, metric in items:
            assert isinstance(name, str)
            assert isinstance(metric, Metric)


# ==========================================================
# Part 8. Serialization
# ==========================================================


class TestSerialization:
    def test_to_dict(
        self,
        full_collector: MetricCollector,
    ):
        data = full_collector.to_dict()

        assert isinstance(data, dict)
        assert "registry" in data
        assert "hooks" in data
        assert "buffer" in data
        assert "enabled" in data

    def test_from_dict(
        self,
        full_collector: MetricCollector,
    ):
        restored = MetricCollector.from_dict(
            full_collector.to_dict(),
        )

        assert restored == full_collector

    def test_to_json(
        self,
        full_collector: MetricCollector,
    ):
        text = full_collector.to_json()

        assert isinstance(text, str)

    def test_from_json(
        self,
        full_collector: MetricCollector,
    ):
        restored = MetricCollector.from_json(
            full_collector.to_json(),
        )

        assert restored == full_collector

    def test_roundtrip_dict(
        self,
        full_collector: MetricCollector,
    ):
        restored = MetricCollector.from_dict(
            full_collector.to_dict(),
        )

        assert restored.to_dict() == full_collector.to_dict()

    def test_roundtrip_json(
        self,
        full_collector: MetricCollector,
    ):
        restored = MetricCollector.from_json(
            full_collector.to_json(),
        )

        assert restored.to_json() == full_collector.to_json()


# ==========================================================
# Part 9. Validation
# ==========================================================


class TestValidation:
    def test_validate(
        self,
        full_collector: MetricCollector,
    ):
        assert full_collector.validate() is True

    def test_validate_invalid_registry(self):
        collector = MetricCollector()

        collector.registry = None

        with pytest.raises((TypeError, ValueError)):
            collector.validate()

    def test_validate_invalid_metric(self):
        collector = MetricCollector()

        # Bypass public API to simulate corrupted internal state.
        collector.registry.metrics["cpu"] = object()

        with pytest.raises(TypeError):
            collector.validate()

    def test_is_valid(
        self,
        full_collector: MetricCollector,
    ):
        assert full_collector.is_valid() is True

# ==========================================================
# Part 10. Comparison
# ==========================================================


class TestComparison:
    def test_equals(
        self,
        full_collector: MetricCollector,
    ):
        copied = full_collector.copy()

        assert copied == full_collector

    def test_not_equals(
        self,
        full_collector: MetricCollector,
    ):
        copied = full_collector.copy()

        copied.enabled = False

        assert copied != full_collector

    def test_hash(
        self,
        full_collector: MetricCollector,
    ):
        assert isinstance(hash(full_collector), int)

    def test_copy_equality(
        self,
        full_collector: MetricCollector,
    ):
        copied = full_collector.copy()

        assert copied == full_collector
        assert copied is not full_collector


# ==========================================================
# Part 11. Snapshot
# ==========================================================


class TestSnapshot:
    def test_copy(
        self,
        full_collector: MetricCollector,
    ):
        copied = full_collector.copy()

        assert copied == full_collector
        assert copied is not full_collector

    def test_deepcopy(
        self,
        full_collector: MetricCollector,
    ):
        copied = copy.deepcopy(full_collector)

        assert copied == full_collector
        assert copied is not full_collector

    def test_clone(
        self,
        full_collector: MetricCollector,
    ):
        cloned = full_collector.clone()

        assert cloned == full_collector
        assert cloned is not full_collector

    def test_replace(
        self,
        full_collector: MetricCollector,
    ):
        replaced = full_collector.replace(
            enabled=False,
        )

        assert replaced.enabled is False
        assert full_collector.enabled is True

# ==========================================================
# Part 12. Python Protocols
# ==========================================================


class TestPythonProtocols:
    def test_repr(
        self,
        full_collector: MetricCollector,
    ):
        assert "MetricCollector" in repr(full_collector)

    def test_str(
        self,
        full_collector: MetricCollector,
    ):
        assert isinstance(str(full_collector), str)

    def test_bool(
        self,
        empty_collector: MetricCollector,
        full_collector: MetricCollector,
    ):
        assert bool(empty_collector) is False
        assert bool(full_collector) is True

    def test_len(
        self,
        full_collector: MetricCollector,
    ):
        assert len(full_collector) == len(full_collector.registry)

    def test_iter(
        self,
        full_collector: MetricCollector,
    ):
        assert list(iter(full_collector)) == full_collector.registry.names()

    def test_contains(
        self,
        full_collector: MetricCollector,
    ):
        assert "cpu" in full_collector
        assert "gpu" not in full_collector

    def test_getitem(
        self,
        full_collector: MetricCollector,
    ):
        metric = full_collector["cpu"]

        assert metric.name == "cpu"

    def test_setitem(
        self,
        empty_collector: MetricCollector,
    ):
        metric = Metric(
            name="gpu",
            value=99.0,
        )

        empty_collector["gpu"] = metric

        assert empty_collector["gpu"] == metric

    def test_delitem(
        self,
        full_collector: MetricCollector,
    ):
        del full_collector["cpu"]

        assert "cpu" not in full_collector

    def test_hash_protocol(
        self,
        full_collector: MetricCollector,
    ):
        assert isinstance(hash(full_collector), int)


# ==========================================================
# Part 13. API Freeze
# ==========================================================


class TestAPIFreeze:
    def test_public_api(self):
        expected = {
            "validate",
            "is_valid",
            "collect",
            "clear",
            "register",
            "unregister",
            "replace",
            "get",
            "items",
            "keys",
            "values",
            "metrics",
            "to_dict",
            "from_dict",
            "to_json",
            "from_json",
            "copy",
            "clone",
            "deepcopy",
        }

        members = set(dir(MetricCollector))

        assert expected <= members

    def test_annotations(self):
        hints = get_type_hints(MetricCollector)

        assert "registry" in hints
        assert "hooks" in hints
        assert "buffer" in hints
        assert "enabled" in hints

    def test_slots(self):
        assert hasattr(MetricCollector, "__slots__")

    def test_signature(self):
        sig = inspect.signature(MetricCollector)

        assert "registry" in sig.parameters
        assert "hooks" in sig.parameters

    def test_pickle(
        self,
        full_collector: MetricCollector,
    ):
        restored = pickle.loads(
            pickle.dumps(full_collector),
        )

        assert restored == full_collector                               
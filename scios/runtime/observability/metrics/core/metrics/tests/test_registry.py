# ==========================================================
# Part 1. Imports
# ==========================================================

from __future__ import annotations

import copy
import inspect
import pickle
from typing import get_type_hints

import pytest

from scios.runtime.observability.metrics.core.metrics.core.metric import Metric
from scios.runtime.observability.metrics.core.metrics.core.registry import (
    MetricRegistry,
)


# ==========================================================
# Test Metrics
# ==========================================================

metric_cpu = Metric(
    name="cpu",
    value=10.0,
)

metric_memory = Metric(
    name="memory",
    value=20.0,
)

metric_disk = Metric(
    name="disk",
    value=30.0,
)


# ==========================================================
# Part 2. Fixtures
# ==========================================================

@pytest.fixture
def empty_registry() -> MetricRegistry:
    return MetricRegistry()


@pytest.fixture
def custom_registry() -> MetricRegistry:
    registry = MetricRegistry()

    registry.register(metric_cpu)

    return registry


@pytest.fixture
def full_registry() -> MetricRegistry:
    registry = MetricRegistry()

    registry.register(metric_cpu)
    registry.register(metric_memory)
    registry.register(metric_disk)

    return registry


# ==========================================================
# Part 3. Construction
# ==========================================================

class TestConstruction:

    def test_create_default(self):
        registry = MetricRegistry()

        assert isinstance(registry, MetricRegistry)

    def test_create_custom(
        self,
        custom_registry: MetricRegistry,
    ):
        assert len(custom_registry) == 1

    def test_create_empty(
        self,
        empty_registry: MetricRegistry,
    ):
        assert len(empty_registry) == 0

    def test_create_full(
        self,
        full_registry: MetricRegistry,
    ):
        assert len(full_registry) == 3

# ==========================================================
# Part 4. Identity
# ==========================================================

class TestIdentity:

    def test_metrics(
        self,
        full_registry: MetricRegistry,
    ):
        assert isinstance(full_registry.metrics, dict)

    def test_names(
        self,
        full_registry: MetricRegistry,
    ):
        assert set(full_registry.names()) == {
            "cpu",
            "memory",
            "disk",
        }

    def test_size(
        self,
        full_registry: MetricRegistry,
    ):
        assert full_registry.size == 3

    def test_version(
        self,
        full_registry: MetricRegistry,
    ):
        assert isinstance(full_registry.version, str)

    def test_length(
        self,
        full_registry: MetricRegistry,
    ):
        assert len(full_registry) == 3


# ==========================================================
# Part 5. Defaults
# ==========================================================

class TestDefaults:

    def test_default_empty(
        self,
        empty_registry: MetricRegistry,
    ):
        assert empty_registry.metrics == {}

    def test_default_mutable_independent(self):
        r1 = MetricRegistry()
        r2 = MetricRegistry()

        r1.register(metric_cpu)

        assert len(r1) == 1
        assert len(r2) == 0

    def test_default_version(
        self,
        empty_registry: MetricRegistry,
    ):
        assert isinstance(empty_registry.version, str)


# ==========================================================
# Part 6. Registration
# ==========================================================

class TestRegistration:

    def test_register(self):
        registry = MetricRegistry()

        registry.register(metric_cpu)

        assert "cpu" in registry
        assert len(registry) == 1

    def test_unregister(
        self,
        full_registry: MetricRegistry,
    ):
        full_registry.unregister("cpu")

        assert "cpu" not in full_registry
        assert len(full_registry) == 2

    def test_replace(
        self,
        custom_registry: MetricRegistry,
    ):
        replacement = Metric(
            name="cpu",
            value=999.0,
        )

        custom_registry.register(replacement)

        assert custom_registry["cpu"].value == 999.0
        assert len(custom_registry) == 1

    def test_clear(
        self,
        full_registry: MetricRegistry,
    ):
        full_registry.clear()

        assert len(full_registry) == 0
        assert full_registry.metrics == {}

# ==========================================================
# Part 7. Lookup
# ==========================================================

class TestLookup:

    def test_get(
        self,
        full_registry: MetricRegistry,
    ):
        metric = full_registry.get("cpu")

        assert isinstance(metric, Metric)
        assert metric.name == "cpu"

    def test_contains(
        self,
        full_registry: MetricRegistry,
    ):
        assert "cpu" in full_registry
        assert "unknown" not in full_registry

    def test_names_list(
        self,
        full_registry: MetricRegistry,
    ):
        names = full_registry.names()

        assert isinstance(names, list)
        assert set(names) == {"cpu", "memory", "disk"}

    def test_values_list(
        self,
        full_registry: MetricRegistry,
    ):
        values = full_registry.values()

        assert isinstance(values, list)
        assert len(values) == 3
        assert all(isinstance(v, Metric) for v in values)

    def test_items_list(
        self,
        full_registry: MetricRegistry,
    ):
        items = full_registry.items()

        assert isinstance(items, list)
        assert len(items) == 3
        assert all(isinstance(k, str) for k, _ in items)
        assert all(isinstance(v, Metric) for _, v in items)


# ==========================================================
# Part 8. Serialization
# ==========================================================

class TestSerialization:

    def test_to_dict(
        self,
        full_registry: MetricRegistry,
    ):
        data = full_registry.to_dict()

        assert isinstance(data, dict)

    def test_from_dict(
        self,
        full_registry: MetricRegistry,
    ):
        restored = MetricRegistry.from_dict(
            full_registry.to_dict()
        )

        assert restored == full_registry

    def test_to_json(
        self,
        full_registry: MetricRegistry,
    ):
        payload = full_registry.to_json()

        assert isinstance(payload, str)

    def test_from_json(
        self,
        full_registry: MetricRegistry,
    ):
        restored = MetricRegistry.from_json(
            full_registry.to_json()
        )

        assert restored == full_registry

    def test_roundtrip_dict(
        self,
        full_registry: MetricRegistry,
    ):
        restored = MetricRegistry.from_dict(
            full_registry.to_dict()
        )

        assert restored.to_dict() == full_registry.to_dict()

    def test_roundtrip_json(
        self,
        full_registry: MetricRegistry,
    ):
        restored = MetricRegistry.from_json(
            full_registry.to_json()
        )

        assert restored.to_json() == full_registry.to_json()


# ==========================================================
# Part 9. Validation
# ==========================================================

class TestValidation:

    def test_validate(
        self,
        full_registry: MetricRegistry,
    ):
        full_registry.validate()

    def test_validate_invalid_name(self):
        registry = MetricRegistry()

        registry.metrics[123] = metric_cpu  # type: ignore[index]

        with pytest.raises(TypeError):
            registry.validate()

    def test_validate_invalid_metric(self):
        registry = MetricRegistry()

        registry.metrics["cpu"] = "invalid"  # type: ignore[assignment]

        with pytest.raises(TypeError):
            registry.validate()

    def test_is_valid(
        self,
        full_registry: MetricRegistry,
    ):
        assert full_registry.is_valid() is True

# ==========================================================
# Part 10. Comparison
# ==========================================================

class TestComparison:

    def test_equals(
        self,
        full_registry: MetricRegistry,
    ):
        other = full_registry.copy()

        assert other == full_registry

    def test_not_equals(
        self,
        full_registry: MetricRegistry,
    ):
        other = MetricRegistry()

        assert other != full_registry

    def test_hash(
        self,
        full_registry: MetricRegistry,
    ):
        assert isinstance(hash(full_registry), int)

    def test_copy_equality(
        self,
        full_registry: MetricRegistry,
    ):
        copied = full_registry.copy()

        assert copied == full_registry
        assert copied is not full_registry


# ==========================================================
# Part 11. Snapshot
# ==========================================================

class TestSnapshot:

    def test_copy(
        self,
        full_registry: MetricRegistry,
    ):
        copied = full_registry.copy()

        assert copied == full_registry
        assert copied is not full_registry

    def test_deepcopy(
        self,
        full_registry: MetricRegistry,
    ):
        copied = copy.deepcopy(full_registry)

        assert copied == full_registry
        assert copied is not full_registry

    def test_clone(
        self,
        full_registry: MetricRegistry,
    ):
        cloned = full_registry.clone()

        assert cloned == full_registry
        assert cloned is not full_registry

    def test_replace(
        self,
        full_registry: MetricRegistry,
    ):
        replaced = full_registry.replace(
            version="2.0",
        )

        assert replaced.version == "2.0"
        assert len(replaced) == len(full_registry)
        assert replaced is not full_registry

# ==========================================================
# Part 12. Python Protocols
# ==========================================================

class TestPythonProtocols:

    def test_repr(
        self,
        full_registry: MetricRegistry,
    ):
        assert "MetricRegistry" in repr(full_registry)

    def test_str(
        self,
        full_registry: MetricRegistry,
    ):
        assert isinstance(str(full_registry), str)

    def test_bool(
        self,
        empty_registry: MetricRegistry,
        full_registry: MetricRegistry,
    ):
        assert bool(empty_registry) is False
        assert bool(full_registry) is True

    def test_len(
        self,
        full_registry: MetricRegistry,
    ):
        assert len(full_registry) == 3

    def test_iter(
        self,
        full_registry: MetricRegistry,
    ):
        assert list(iter(full_registry)) == full_registry.names()

    def test_contains(
        self,
        full_registry: MetricRegistry,
    ):
        assert "cpu" in full_registry
        assert "unknown" not in full_registry

    def test_getitem(
        self,
        full_registry: MetricRegistry,
    ):
        metric = full_registry["cpu"]

        assert isinstance(metric, Metric)
        assert metric.name == "cpu"

    def test_setitem(
        self,
        empty_registry: MetricRegistry,
    ):
        metric = Metric(
            name="gpu",
            value=99.0,
        )

        empty_registry["gpu"] = metric

        assert empty_registry["gpu"] == metric

    def test_delitem(
        self,
        full_registry: MetricRegistry,
    ):
        del full_registry["cpu"]

        assert "cpu" not in full_registry
        assert len(full_registry) == 2

    def test_hash_protocol(
        self,
        full_registry: MetricRegistry,
    ):
        assert isinstance(hash(full_registry), int)


# ==========================================================
# Part 13. API Freeze
# ==========================================================

class TestAPIFreeze:

    def test_public_api(self):
        expected = {
            "register",
            "unregister",
            "clear",
            "replace",
            "get",
            "items",
            "keys",
            "values",
            "names",
            "to_dict",
            "from_dict",
            "to_json",
            "from_json",
            "validate",
            "is_valid",
            "copy",
            "clone",
            "deepcopy",
        }

        public = {
            name
            for name in dir(MetricRegistry)
            if not name.startswith("_")
        }

        assert expected <= public

    def test_annotations(self):
        hints = get_type_hints(MetricRegistry)

        assert isinstance(hints, dict)

    def test_slots(self):
        assert hasattr(MetricRegistry, "__slots__")

    def test_signature(self):
        signature = inspect.signature(MetricRegistry)

        assert signature is not None

    def test_pickle(
        self,
        full_registry: MetricRegistry,
    ):
        restored = pickle.loads(
            pickle.dumps(full_registry),
        )

        assert restored == full_registry                                
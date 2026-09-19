"""
Tests for MetricDescriptor.
"""

from __future__ import annotations

# ==========================================================
# Part 1. Imports
# ==========================================================


import copy
import dataclasses
import inspect
import pickle

from typing import Any

import pytest

from scios.runtime.observability.metrics.core.metrics.core.descriptor import (
    MetricDescriptor,
)
from scios.runtime.observability.metrics.core.metrics.core.metadata import (
    MetricMetadata,
)

# ==========================================================
# Part 2. Fixtures
# ==========================================================

@pytest.fixture
def default_metadata() -> MetricMetadata:
    return MetricMetadata(
        name="cpu_usage",
    )


@pytest.fixture
def custom_metadata() -> MetricMetadata:
    return MetricMetadata(
        name="cpu_usage",
        description="CPU utilization",
        unit="percent",
        namespace="system",
        category="performance",
        owner="runtime",
        version="1.0",
        tags=("cpu", "system"),
        extras={"source": "pytest"},
    )


@pytest.fixture
def default_descriptor(
    default_metadata: MetricMetadata,
) -> MetricDescriptor:
    return MetricDescriptor(
        metadata=default_metadata,
    )


@pytest.fixture
def custom_descriptor(
    custom_metadata: MetricMetadata,
) -> MetricDescriptor:
    return MetricDescriptor(
        metadata=custom_metadata,
        metric_type="gauge",
        value_type=float,
        aggregation="last_value",
        temporality="cumulative",
        monotonic=False,
    )


# ==========================================================
# Part 3. Construction
# ==========================================================

class TestConstruction:

    def test_create_default(
        self,
        default_descriptor: MetricDescriptor,
    ):
        assert isinstance(default_descriptor, MetricDescriptor)

    def test_create_custom(
        self,
        custom_descriptor: MetricDescriptor,
    ):
        assert custom_descriptor.metadata.name == "cpu_usage"

    def test_create_minimal(self):
        descriptor = MetricDescriptor(
            metadata=MetricMetadata(
                name="memory_usage",
            ),
        )

        assert descriptor.metadata.name == "memory_usage"

    def test_create_full(self):
        descriptor = MetricDescriptor(
            metadata=MetricMetadata(
                name="disk_usage",
                description="Disk usage",
                unit="percent",
                namespace="system",
                category="storage",
                owner="runtime",
                version="2.0",
                tags=("disk",),
                extras={"device": "sda"},
            ),
            metric_type="gauge",
            value_type=float,
            aggregation="last_value",
            temporality="delta",
            monotonic=False,
        )

        assert descriptor.metadata.name == "disk_usage"
        assert descriptor.metric_type == "gauge"
# ==========================================================
# Part 4. Identity
# ==========================================================

class TestIdentity:

    def test_metadata(
        self,
        custom_descriptor: MetricDescriptor,
    ):
        assert custom_descriptor.metadata.name == "cpu_usage"

    def test_metric_type(
        self,
        custom_descriptor: MetricDescriptor,
    ):
        assert custom_descriptor.metric_type == "gauge"

    def test_value_type(
        self,
        custom_descriptor: MetricDescriptor,
    ):
        assert custom_descriptor.value_type is float

    def test_aggregation(
        self,
        custom_descriptor: MetricDescriptor,
    ):
        assert custom_descriptor.aggregation == "last_value"

    def test_temporality(
        self,
        custom_descriptor: MetricDescriptor,
    ):
        assert custom_descriptor.temporality == "cumulative"

    def test_monotonic(
        self,
        custom_descriptor: MetricDescriptor,
    ):
        assert custom_descriptor.monotonic is False


# ==========================================================
# Part 5. Defaults
# ==========================================================

class TestDefaults:

    def test_default_metric_type(
        self,
        default_descriptor: MetricDescriptor,
    ):
        assert default_descriptor.metric_type == "gauge"

    def test_default_value_type(
        self,
        default_descriptor: MetricDescriptor,
    ):
        assert default_descriptor.value_type is float

    def test_default_aggregation(
        self,
        default_descriptor: MetricDescriptor,
    ):
        assert default_descriptor.aggregation == "last_value"

    def test_default_temporality(
        self,
        default_descriptor: MetricDescriptor,
    ):
        assert default_descriptor.temporality == "cumulative"

    def test_default_monotonic(
        self,
        default_descriptor: MetricDescriptor,
    ):
        assert default_descriptor.monotonic is False


# ==========================================================
# Part 6. Mutation
# ==========================================================

class TestMutation:

    def test_replace_metadata(
        self,
        custom_descriptor: MetricDescriptor,
    ):
        replaced = custom_descriptor.replace(
            metadata=MetricMetadata(name="memory_usage"),
        )

        assert replaced.metadata.name == "memory_usage"
        assert custom_descriptor.metadata.name == "cpu_usage"

    def test_replace_metric_type(
        self,
        custom_descriptor: MetricDescriptor,
    ):
        replaced = custom_descriptor.replace(
            metric_type="counter",
        )

        assert replaced.metric_type == "counter"
        assert custom_descriptor.metric_type == "gauge"

    def test_replace_value_type(
        self,
        custom_descriptor: MetricDescriptor,
    ):
        replaced = custom_descriptor.replace(
            value_type=int,
        )

        assert replaced.value_type is int
        assert custom_descriptor.value_type is float

    def test_replace_aggregation(
        self,
        custom_descriptor: MetricDescriptor,
    ):
        replaced = custom_descriptor.replace(
            aggregation="sum",
        )

        assert replaced.aggregation == "sum"
        assert custom_descriptor.aggregation == "last_value"
# ==========================================================
# Part 7. Serialization
# ==========================================================

class TestSerialization:

    def test_to_dict(
        self,
        custom_descriptor: MetricDescriptor,
    ):
        data = custom_descriptor.to_dict()

        assert data["metric_type"] == "gauge"
        assert data["metadata"]["name"] == "cpu_usage"

    def test_from_dict(
        self,
        custom_descriptor: MetricDescriptor,
    ):
        restored = MetricDescriptor.from_dict(
            custom_descriptor.to_dict(),
        )

        assert restored == custom_descriptor

    def test_to_json(
        self,
        custom_descriptor: MetricDescriptor,
    ):
        text = custom_descriptor.to_json()

        assert isinstance(text, str)

    def test_from_json(
        self,
        custom_descriptor: MetricDescriptor,
    ):
        restored = MetricDescriptor.from_json(
            custom_descriptor.to_json(),
        )

        assert restored == custom_descriptor

    def test_roundtrip_dict(
        self,
        custom_descriptor: MetricDescriptor,
    ):
        restored = MetricDescriptor.from_dict(
            custom_descriptor.to_dict(),
        )

        assert restored.to_dict() == custom_descriptor.to_dict()

    def test_roundtrip_json(
        self,
        custom_descriptor: MetricDescriptor,
    ):
        restored = MetricDescriptor.from_json(
            custom_descriptor.to_json(),
        )

        assert restored.to_dict() == custom_descriptor.to_dict()


# ==========================================================
# Part 8. Validation
# ==========================================================

class TestValidation:

    def test_validate(
        self,
        custom_descriptor: MetricDescriptor,
    ):
        custom_descriptor.validate()

    def test_validate_invalid_metric_type(self):

        descriptor = MetricDescriptor(
            metadata=MetricMetadata(name="cpu"),
            metric_type="invalid",
        )

        with pytest.raises(Exception):
            descriptor.validate()

    def test_validate_invalid_value_type(self):

        descriptor = MetricDescriptor(
            metadata=MetricMetadata(name="cpu"),
            value_type="float",
        )

        with pytest.raises(Exception):
            descriptor.validate()

    def test_is_valid(
        self,
        custom_descriptor: MetricDescriptor,
    ):
        assert custom_descriptor.is_valid() is True


# ==========================================================
# Part 9. Comparison
# ==========================================================

class TestComparison:

    def test_equals(
        self,
        custom_descriptor: MetricDescriptor,
    ):
        copied = custom_descriptor.copy()

        assert custom_descriptor.equals(copied)

    def test_not_equals(
        self,
        custom_descriptor: MetricDescriptor,
    ):
        other = custom_descriptor.replace(
            metric_type="counter",
        )

        assert not custom_descriptor.equals(other)

    def test_hash(
        self,
        custom_descriptor: MetricDescriptor,
    ):
        assert hash(custom_descriptor) == hash(
            custom_descriptor.copy()
        )

    def test_copy_equality(
        self,
        custom_descriptor: MetricDescriptor,
    ):
        copied = custom_descriptor.copy()

        assert copied == custom_descriptor
        assert copied is not custom_descriptor
# ==========================================================
# Part 10. Snapshot
# ==========================================================



class TestSnapshot:

    def test_copy(
        self,
        custom_descriptor: MetricDescriptor,
    ):
        copied = custom_descriptor.copy()

        assert copied == custom_descriptor
        assert copied is not custom_descriptor

    def test_deepcopy(
        self,
        custom_descriptor: MetricDescriptor,
    ):
        cloned = copy.deepcopy(custom_descriptor)

        assert cloned == custom_descriptor
        assert cloned is not custom_descriptor

    def test_clone(
        self,
        custom_descriptor: MetricDescriptor,
    ):
        cloned = custom_descriptor.clone()

        assert cloned == custom_descriptor
        assert cloned is not custom_descriptor

    def test_replace(
        self,
        custom_descriptor: MetricDescriptor,
    ):
        replaced = custom_descriptor.replace(
            metric_type="counter",
        )

        assert replaced.metric_type == "counter"
        assert custom_descriptor.metric_type == "gauge"


# ==========================================================
# Part 11. Python Protocols
# ==========================================================

class TestPythonProtocols:

    def test_repr(
        self,
        custom_descriptor: MetricDescriptor,
    ):
        assert "MetricDescriptor" in repr(custom_descriptor)

    def test_str(
        self,
        custom_descriptor: MetricDescriptor,
    ):
        assert isinstance(str(custom_descriptor), str)

    def test_bool(
        self,
        custom_descriptor: MetricDescriptor,
    ):
        assert bool(custom_descriptor)

    def test_eq(
        self,
        custom_descriptor: MetricDescriptor,
    ):
        assert custom_descriptor == custom_descriptor.copy()

    def test_hash_protocol(
        self,
        custom_descriptor: MetricDescriptor,
    ):
        assert isinstance(hash(custom_descriptor), int)

    def test_dataclass_fields(self):
        fields = dataclasses.fields(MetricDescriptor)

        assert len(fields) > 0


# ==========================================================
# Part 12. API Freeze
# ==========================================================

class TestAPIFreeze:

    def test_public_api(self):

        assert hasattr(MetricDescriptor, "to_dict")
        assert hasattr(MetricDescriptor, "from_dict")
        assert hasattr(MetricDescriptor, "validate")
        assert hasattr(MetricDescriptor, "copy")
        assert hasattr(MetricDescriptor, "clone")

    def test_annotations(self):

        assert MetricDescriptor.__annotations__

    def test_slots(self):

        assert hasattr(MetricDescriptor, "__slots__")

    def test_signature(self):

        sig = inspect.signature(MetricDescriptor)

        assert "metadata" in sig.parameters

    def test_pickle(
        self,
        custom_descriptor: MetricDescriptor,
    ):
        restored = pickle.loads(
            pickle.dumps(custom_descriptor),
        )

        assert restored == custom_descriptor                        
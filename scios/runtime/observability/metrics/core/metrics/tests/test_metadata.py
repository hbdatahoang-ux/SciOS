"""
Tests for MetricMetadata

SciOS Runtime Metrics
"""

from __future__ import annotations

# ==========================================================
# Part 1. Imports
# ==========================================================

import pytest

from scios.runtime.observability.metrics.core.metrics.core.metadata import (
    MetricMetadata,
)


# ==========================================================
# Part 2. Fixtures
# ==========================================================

@pytest.fixture
def default_metadata() -> MetricMetadata:
    """
    Default metadata fixture.
    """
    return MetricMetadata(
        name="cpu_usage",
    )


@pytest.fixture
def custom_metadata() -> MetricMetadata:
    """
    Fully populated metadata fixture.
    """
    return MetricMetadata(
        name="cpu_usage",
        description="CPU utilization",
        unit="percent",
        namespace="system",
        category="performance",
        owner="runtime",
        version="1.0.0",
        tags=("cpu", "system"),
    )


# ==========================================================
# Part 3. Construction
# ==========================================================

class TestConstruction:
    """
    MetricMetadata construction tests.
    """

    def test_create_default(
        self,
        default_metadata: MetricMetadata,
    ):

        assert isinstance(default_metadata, MetricMetadata)

        assert default_metadata.name == "cpu_usage"

    def test_create_custom(
        self,
        custom_metadata: MetricMetadata,
    ):

        assert isinstance(custom_metadata, MetricMetadata)

        assert custom_metadata.name == "cpu_usage"

        assert custom_metadata.description == "CPU utilization"

        assert custom_metadata.unit == "percent"

        assert custom_metadata.namespace == "system"

        assert custom_metadata.category == "performance"

        assert custom_metadata.owner == "runtime"

        assert custom_metadata.version == "1.0.0"

        assert custom_metadata.tags == (
            "cpu",
            "system",
        )

    def test_create_minimal(self):

        metadata = MetricMetadata(
            name="memory_usage",
        )

        assert metadata.name == "memory_usage"

    def test_create_full(self):

        metadata = MetricMetadata(
            name="disk_usage",
            description="Disk utilization",
            unit="percent",
            namespace="storage",
            category="performance",
            owner="runtime",
            version="2.0.0",
            tags=(
                "disk",
                "storage",
            ),
        )

        assert metadata.name == "disk_usage"

        assert metadata.description == "Disk utilization"

        assert metadata.unit == "percent"

        assert metadata.namespace == "storage"

        assert metadata.category == "performance"

        assert metadata.owner == "runtime"

        assert metadata.version == "2.0.0"

        assert metadata.tags == (
            "disk",
            "storage",
        )
# ==========================================================
# Part 4. Identity
# ==========================================================

class TestIdentity:

    def test_name(
        self,
        custom_metadata: MetricMetadata,
    ):

        assert custom_metadata.name == "cpu_usage"

    def test_description(
        self,
        custom_metadata: MetricMetadata,
    ):

        assert custom_metadata.description == "CPU utilization"

    def test_unit(
        self,
        custom_metadata: MetricMetadata,
    ):

        assert custom_metadata.unit == "percent"

    def test_namespace(
        self,
        custom_metadata: MetricMetadata,
    ):

        assert custom_metadata.namespace == "system"

    def test_category(
        self,
        custom_metadata: MetricMetadata,
    ):

        assert custom_metadata.category == "performance"

    def test_owner(
        self,
        custom_metadata: MetricMetadata,
    ):

        assert custom_metadata.owner == "runtime"

    def test_version(
        self,
        custom_metadata: MetricMetadata,
    ):

        assert custom_metadata.version == "1.0.0"

    def test_tags(
        self,
        custom_metadata: MetricMetadata,
    ):

        assert custom_metadata.tags == (
            "cpu",
            "system",
        )


# ==========================================================
# Part 5. Defaults
# ==========================================================

class TestDefaults:

    def test_default_description(
        self,
        default_metadata: MetricMetadata,
    ):

        assert default_metadata.description == ""

    def test_default_unit(
        self,
        default_metadata: MetricMetadata,
    ):

        assert default_metadata.unit == ""

    def test_default_namespace(
        self,
        default_metadata: MetricMetadata,
    ):

        assert default_metadata.namespace == ""

    def test_default_category(
        self,
        default_metadata: MetricMetadata,
    ):

        assert default_metadata.category == ""

    def test_default_owner(
        self,
        default_metadata: MetricMetadata,
    ):

        assert default_metadata.owner == ""

    def test_default_version(
        self,
        default_metadata: MetricMetadata,
    ):

        assert default_metadata.version == ""

    def test_default_tags(
        self,
        default_metadata: MetricMetadata,
    ):

        assert default_metadata.tags == ()
# ==========================================================
# Part 6. Mutation
# ==========================================================

class TestMutation:

    def test_replace_name(
        self,
        custom_metadata: MetricMetadata,
    ):

        custom_metadata.name = "memory_usage"

        assert custom_metadata.name == "memory_usage"

    def test_replace_description(
        self,
        custom_metadata: MetricMetadata,
    ):

        custom_metadata.description = "Memory utilization"

        assert custom_metadata.description == "Memory utilization"

    def test_replace_unit(
        self,
        custom_metadata: MetricMetadata,
    ):

        custom_metadata.unit = "bytes"

        assert custom_metadata.unit == "bytes"

    def test_replace_tags(
        self,
        custom_metadata: MetricMetadata,
    ):

        custom_metadata.tags = (
            "memory",
            "runtime",
        )

        assert custom_metadata.tags == (
            "memory",
            "runtime",
        )

    def test_replace_namespace(
        self,
        custom_metadata: MetricMetadata,
    ):

        custom_metadata.namespace = "runtime"

        assert custom_metadata.namespace == "runtime"


# ==========================================================
# Part 7. Serialization
# ==========================================================

class TestSerialization:

    def test_to_dict(
        self,
        custom_metadata: MetricMetadata,
    ):

        data = custom_metadata.to_dict()

        assert isinstance(data, dict)

    def test_from_dict(
        self,
        custom_metadata: MetricMetadata,
    ):

        data = custom_metadata.to_dict()

        restored = MetricMetadata.from_dict(data)

        assert isinstance(restored, MetricMetadata)

    def test_to_json(
        self,
        custom_metadata: MetricMetadata,
    ):

        text = custom_metadata.to_json()

        assert isinstance(text, str)

    def test_from_json(
        self,
        custom_metadata: MetricMetadata,
    ):

        text = custom_metadata.to_json()

        restored = MetricMetadata.from_json(text)

        assert isinstance(restored, MetricMetadata)

    def test_roundtrip_dict(
        self,
        custom_metadata: MetricMetadata,
    ):

        restored = MetricMetadata.from_dict(
            custom_metadata.to_dict(),
        )

        assert restored == custom_metadata

    def test_roundtrip_json(
        self,
        custom_metadata: MetricMetadata,
    ):

        restored = MetricMetadata.from_json(
            custom_metadata.to_json(),
        )

        assert restored == custom_metadata
# ==========================================================
# Part 8. Validation
# ==========================================================

class TestValidation:

    def test_validate(
        self,
        custom_metadata: MetricMetadata,
    ):

        assert custom_metadata.validate() is None

    def test_validate_invalid_name(self):

        metadata = MetricMetadata(
            name="",
        )

        with pytest.raises(Exception):
            metadata.validate()

    def test_validate_invalid_tags(self):

        with pytest.raises(Exception):

            MetricMetadata(
                name="cpu",
                tags=("cpu", 123),
            )

    def test_is_valid(
        self,
        custom_metadata: MetricMetadata,
    ):

        assert custom_metadata.is_valid() is True


# ==========================================================
# Part 9. Comparison
# ==========================================================

class TestComparison:

    def test_equals(
        self,
        custom_metadata: MetricMetadata,
    ):

        other = MetricMetadata.from_dict(
            custom_metadata.to_dict(),
        )

        assert custom_metadata.equals(other)

    def test_not_equals(
        self,
        custom_metadata: MetricMetadata,
    ):

        other = MetricMetadata(
            name="memory_usage",
        )

        assert not custom_metadata.equals(other)

    def test_hash(
        self,
        custom_metadata: MetricMetadata,
    ):

        assert isinstance(
            hash(custom_metadata),
            int,
        )

    def test_copy_equality(
        self,
        custom_metadata: MetricMetadata,
    ):

        copied = custom_metadata.copy()

        assert copied == custom_metadata

        assert copied is not custom_metadata


# ==========================================================
# Part 10. Snapshot
# ==========================================================

class TestSnapshot:

    def test_copy(
        self,
        custom_metadata: MetricMetadata,
    ):

        copied = custom_metadata.copy()

        assert copied == custom_metadata

        assert copied is not custom_metadata

    def test_deepcopy(
        self,
        custom_metadata: MetricMetadata,
    ):

        import copy

        cloned = copy.deepcopy(custom_metadata)

        assert cloned == custom_metadata

        assert cloned is not custom_metadata

    def test_clone(
        self,
        custom_metadata: MetricMetadata,
    ):

        cloned = custom_metadata.clone()

        assert cloned == custom_metadata

        assert cloned is not custom_metadata

    def test_replace(
        self,
        custom_metadata: MetricMetadata,
    ):

        replaced = custom_metadata.replace(
            name="memory_usage",
        )

        assert replaced.name == "memory_usage"

        assert custom_metadata.name == "cpu_usage"
# ==========================================================
# Part 11. Python Protocols
# ==========================================================

class TestPythonProtocols:

    def test_repr(
        self,
        custom_metadata: MetricMetadata,
    ):

        assert isinstance(
            repr(custom_metadata),
            str,
        )

    def test_str(
        self,
        custom_metadata: MetricMetadata,
    ):

        assert isinstance(
            str(custom_metadata),
            str,
        )

    def test_bool(
        self,
        custom_metadata: MetricMetadata,
    ):

        assert bool(custom_metadata) is True

    def test_eq(
        self,
        custom_metadata: MetricMetadata,
    ):

        other = custom_metadata.copy()

        assert custom_metadata == other

    def test_hash_protocol(
        self,
        custom_metadata: MetricMetadata,
    ):

        assert isinstance(
            hash(custom_metadata),
            int,
        )

    def test_dataclass_fields(self):

        from dataclasses import fields

        assert len(fields(MetricMetadata)) > 0


# ==========================================================
# Part 12. API Freeze
# ==========================================================

class TestAPIFreeze:

    def test_public_api(self):

        assert MetricMetadata.__name__ == "MetricMetadata"

    def test_annotations(self):

        assert isinstance(
            MetricMetadata.__annotations__,
            dict,
        )

    def test_slots(self):

        assert hasattr(
            MetricMetadata,
            "__slots__",
        )

    def test_signature(self):

        import inspect

        signature = inspect.signature(
            MetricMetadata,
        )

        assert "name" in signature.parameters

    def test_pickle(
        self,
        custom_metadata: MetricMetadata,
    ):

        import pickle

        restored = pickle.loads(
            pickle.dumps(custom_metadata),
        )

        assert restored == custom_metadata                                
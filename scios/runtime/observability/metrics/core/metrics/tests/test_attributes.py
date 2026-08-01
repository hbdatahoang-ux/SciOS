"""
Tests for MetricAttributes.

SciOS Runtime Metrics Core
"""

# ==========================================================
# Part 1. Imports
# ==========================================================

from __future__ import annotations

import copy
import inspect
import pickle
from typing import get_type_hints

import pytest

from scios.runtime.observability.metrics.core.metrics.core.attributes import (
    MetricAttributes,
)


# ==========================================================
# Part 2. Fixtures
# ==========================================================


@pytest.fixture
def empty_attributes() -> MetricAttributes:
    return MetricAttributes()


@pytest.fixture
def custom_attributes() -> MetricAttributes:
    return MetricAttributes(
        {
            "host": "localhost",
            "service": "runtime",
            "env": "test",
        }
    )


@pytest.fixture
def full_attributes() -> MetricAttributes:
    return MetricAttributes(
        {
            "host": "localhost",
            "service": "runtime",
            "env": "test",
            "version": "1.0.0",
            "region": "asia",
            "instance": "001",
        }
    )


# ==========================================================
# Part 3. Construction
# ==========================================================


class TestConstruction:

    def test_create_default(self):
        attributes = MetricAttributes()

        assert isinstance(attributes, MetricAttributes)
        assert len(attributes) == 0

    def test_create_custom(self):
        attributes = MetricAttributes(
            {
                "host": "localhost",
                "service": "runtime",
            }
        )

        assert attributes["host"] == "localhost"
        assert attributes["service"] == "runtime"

    def test_create_empty(self):
        attributes = MetricAttributes({})

        assert len(attributes) == 0
        assert bool(attributes) is False

    def test_create_full(
        self,
        full_attributes: MetricAttributes,
    ):
        assert len(full_attributes) == 6

        assert full_attributes["host"] == "localhost"
        assert full_attributes["service"] == "runtime"
        assert full_attributes["env"] == "test"
        assert full_attributes["version"] == "1.0.0"
        assert full_attributes["region"] == "asia"
        assert full_attributes["instance"] == "001"


# ==========================================================
# Part 4. Identity
# ==========================================================


class TestIdentity:

    def test_items(
        self,
        custom_attributes: MetricAttributes,
    ):
        assert ("host", "localhost") in custom_attributes.items()
        assert ("service", "runtime") in custom_attributes.items()
        assert ("env", "test") in custom_attributes.items()

    def test_keys(
        self,
        custom_attributes: MetricAttributes,
    ):
        keys = custom_attributes.keys()

        assert "host" in keys
        assert "service" in keys
        assert "env" in keys

    def test_values(
        self,
        custom_attributes: MetricAttributes,
    ):
        values = custom_attributes.values()

        assert "localhost" in values
        assert "runtime" in values
        assert "test" in values

    def test_length(
        self,
        custom_attributes: MetricAttributes,
    ):
        assert len(custom_attributes) == 3

    def test_contains(
        self,
        custom_attributes: MetricAttributes,
    ):
        assert "host" in custom_attributes
        assert "service" in custom_attributes
        assert "env" in custom_attributes
        assert "missing" not in custom_attributes
# ==========================================================
# Part 5. Defaults
# ==========================================================


class TestDefaults:

    def test_default_empty(self):
        attributes = MetricAttributes()

        assert len(attributes) == 0
        assert attributes.to_dict() == {}

    def test_default_mutable_independent(self):
        a = MetricAttributes()
        b = MetricAttributes()

        a["host"] = "localhost"

        assert "host" in a
        assert "host" not in b


# ==========================================================
# Part 6. Mutation
# ==========================================================


class TestMutation:

    def test_set_item(
        self,
        empty_attributes: MetricAttributes,
    ):
        empty_attributes["host"] = "localhost"

        assert empty_attributes["host"] == "localhost"

    def test_update(
        self,
        empty_attributes: MetricAttributes,
    ):
        empty_attributes.update(
            {
                "host": "localhost",
                "service": "runtime",
            }
        )

        assert empty_attributes["host"] == "localhost"
        assert empty_attributes["service"] == "runtime"

    def test_remove(
        self,
        custom_attributes: MetricAttributes,
    ):
        custom_attributes.remove("host")

        assert "host" not in custom_attributes

    def test_clear(
        self,
        custom_attributes: MetricAttributes,
    ):
        custom_attributes.clear()

        assert len(custom_attributes) == 0
        assert custom_attributes.to_dict() == {}


# ==========================================================
# Part 7. Serialization
# ==========================================================


class TestSerialization:

    def test_to_dict(
        self,
        custom_attributes: MetricAttributes,
    ):
        data = custom_attributes.to_dict()

        assert isinstance(data, dict)
        assert data["host"] == "localhost"
        assert data["service"] == "runtime"

    def test_from_dict(
        self,
        custom_attributes: MetricAttributes,
    ):
        restored = MetricAttributes.from_dict(
            custom_attributes.to_dict(),
        )

        assert restored == custom_attributes

    def test_to_json(
        self,
        custom_attributes: MetricAttributes,
    ):
        text = custom_attributes.to_json()

        assert isinstance(text, str)
        assert "host" in text

    def test_from_json(
        self,
        custom_attributes: MetricAttributes,
    ):
        restored = MetricAttributes.from_json(
            custom_attributes.to_json(),
        )

        assert restored == custom_attributes

    def test_roundtrip_dict(
        self,
        full_attributes: MetricAttributes,
    ):
        restored = MetricAttributes.from_dict(
            full_attributes.to_dict(),
        )

        assert restored == full_attributes

    def test_roundtrip_json(
        self,
        full_attributes: MetricAttributes,
    ):
        restored = MetricAttributes.from_json(
            full_attributes.to_json(),
        )

        assert restored == full_attributes


# ==========================================================
# Part 8. Validation
# ==========================================================


class TestValidation:

    def test_validate(
        self,
        custom_attributes: MetricAttributes,
    ):
        custom_attributes.validate()

    def test_validate_invalid_key(self):
        attributes = MetricAttributes(
            {
                123: "value",
            }
        )

        with pytest.raises(Exception):
            attributes.validate()

    def test_validate_invalid_value(self):
        attributes = MetricAttributes(
            {
                "host": object(),
            }
        )

        with pytest.raises(Exception):
            attributes.validate()

    def test_is_valid(
        self,
        custom_attributes: MetricAttributes,
    ):
        assert custom_attributes.is_valid() is True


# ==========================================================
# Part 9. Comparison
# ==========================================================


class TestComparison:

    def test_equals(
        self,
        custom_attributes: MetricAttributes,
    ):
        other = MetricAttributes(
            custom_attributes.to_dict(),
        )

        assert custom_attributes == other

    def test_not_equals(
        self,
        custom_attributes: MetricAttributes,
    ):
        other = MetricAttributes(
            {
                "host": "remote",
            }
        )

        assert custom_attributes != other

    def test_hash(
        self,
        custom_attributes: MetricAttributes,
    ):
        assert isinstance(
            hash(custom_attributes),
            int,
        )

    def test_copy_equality(
        self,
        custom_attributes: MetricAttributes,
    ):
        copied = custom_attributes.copy()

        assert copied == custom_attributes
        assert copied is not custom_attributes
# ==========================================================
# Part 10. Snapshot
# ==========================================================


class TestSnapshot:

    def test_copy(
        self,
        custom_attributes: MetricAttributes,
    ):
        copied = custom_attributes.copy()

        assert copied == custom_attributes
        assert copied is not custom_attributes

    def test_deepcopy(
        self,
        custom_attributes: MetricAttributes,
    ):
        copied = copy.deepcopy(
            custom_attributes,
        )

        assert copied == custom_attributes
        assert copied is not custom_attributes

    def test_clone(
        self,
        custom_attributes: MetricAttributes,
    ):
        cloned = custom_attributes.clone()

        assert cloned == custom_attributes
        assert cloned is not custom_attributes

    def test_replace(
        self,
        custom_attributes: MetricAttributes,
    ):
        replaced = custom_attributes.replace(
            host="127.0.0.1",
        )

        assert replaced["host"] == "127.0.0.1"
        assert custom_attributes["host"] == "localhost"


# ==========================================================
# Part 11. Python Protocols
# ==========================================================


class TestPythonProtocols:

    def test_repr(
        self,
        custom_attributes: MetricAttributes,
    ):
        assert "MetricAttributes" in repr(
            custom_attributes,
        )

    def test_str(
        self,
        custom_attributes: MetricAttributes,
    ):
        assert isinstance(
            str(custom_attributes),
            str,
        )

    def test_bool(
        self,
        custom_attributes: MetricAttributes,
    ):
        assert bool(custom_attributes)

        assert not MetricAttributes()

    def test_len(
        self,
        custom_attributes: MetricAttributes,
    ):
        assert len(custom_attributes) == 3

    def test_iter(
        self,
        custom_attributes: MetricAttributes,
    ):
        keys = list(iter(custom_attributes))

        assert "host" in keys
        assert "service" in keys

    def test_contains(
        self,
        custom_attributes: MetricAttributes,
    ):
        assert "host" in custom_attributes
        assert "missing" not in custom_attributes

    def test_getitem(
        self,
        custom_attributes: MetricAttributes,
    ):
        assert (
            custom_attributes["host"]
            == "localhost"
        )

    def test_setitem(
        self,
        empty_attributes: MetricAttributes,
    ):
        empty_attributes["host"] = "localhost"

        assert (
            empty_attributes["host"]
            == "localhost"
        )

    def test_delitem(
        self,
        custom_attributes: MetricAttributes,
    ):
        del custom_attributes["host"]

        assert "host" not in custom_attributes

    def test_hash_protocol(
        self,
        custom_attributes: MetricAttributes,
    ):
        assert isinstance(
            hash(custom_attributes),
            int,
        )


# ==========================================================
# Part 12. API Freeze
# ==========================================================


class TestAPIFreeze:

    def test_public_api(self):
        expected = {
            "copy",
            "clone",
            "deepcopy",
            "replace",
            "validate",
            "is_valid",
            "to_dict",
            "from_dict",
            "to_json",
            "from_json",
            "items",
            "keys",
            "values",
            "get",
            "update",
            "clear",
            "pop",
        }

        members = set(dir(MetricAttributes))

        assert expected.issubset(members)

    def test_annotations(self):
        hints = get_type_hints(
            MetricAttributes,
        )

        assert isinstance(
            hints,
            dict,
        )

    def test_slots(self):
        assert hasattr(
            MetricAttributes,
            "__slots__",
        )

    def test_signature(self):
        signature = inspect.signature(
            MetricAttributes,
        )

        assert "attributes" in signature.parameters

    def test_pickle(
        self,
        custom_attributes: MetricAttributes,
    ):
        restored = pickle.loads(
            pickle.dumps(
                custom_attributes,
            )
        )

        assert restored == custom_attributes                
"""
SciOS-NG Observability
Tracing Test - Attributes

Tests:

- Attribute creation
- Set/Get operations
- Update operations
- Remove operations
- Clear operations
- Type support
- Serialization
- Snapshot
- Clone
- Validation
- Python protocols

"""

from __future__ import annotations


import copy
import json


import pytest


from scios.runtime.observability.tracing.attributes import (
    Attributes,
)



# ============================================================
# Fixtures
# ============================================================


@pytest.fixture
def attributes() -> Attributes:
    """
    Empty attributes container.
    """

    return Attributes()



@pytest.fixture
def populated_attributes() -> Attributes:
    """
    Attributes with values.
    """

    attrs = Attributes()


    attrs.set(
        "service",
        "scios",
    )


    attrs.set(
        "version",
        "0.3",
    )


    attrs.set(
        "enabled",
        True,
    )


    return attrs



# ============================================================
# Creation
# ============================================================


def test_attributes_creation(attributes):

    assert attributes is not None



def test_default_empty(attributes):

    assert len(
        attributes
    ) == 0



# ============================================================
# Set / Get
# ============================================================


def test_set_attribute(attributes):

    attributes.set(
        "name",
        "runtime",
    )


    assert (
        attributes.get("name")
        ==
        "runtime"
    )



def test_get_missing_attribute(attributes):

    assert (
        attributes.get(
            "missing"
        )
        is None
    )



def test_get_default_value(attributes):

    assert (
        attributes.get(
            "missing",
            "default",
        )
        ==
        "default"
    )



def test_overwrite_attribute(attributes):

    attributes.set(
        "key",
        "old",
    )


    attributes.set(
        "key",
        "new",
    )


    assert (
        attributes.get("key")
        ==
        "new"
    )



# ============================================================
# Multiple Attributes
# ============================================================


def test_multiple_attributes(
    populated_attributes,
):

    assert (
        populated_attributes.get(
            "service"
        )
        ==
        "scios"
    )


    assert (
        populated_attributes.get(
            "version"
        )
        ==
        "0.3"
    )



def test_attribute_count(
    populated_attributes,
):

    assert (
        populated_attributes.count()
        ==
        3
    )



# ============================================================
# Update
# ============================================================


def test_update_attributes(attributes):

    attributes.update(
        {
            "a": 1,
            "b": 2,
        }
    )


    assert (
        attributes.get("a")
        ==
        1
    )


    assert (
        attributes.get("b")
        ==
        2
    )



def test_merge_attributes(attributes):

    attributes.set(
        "existing",
        True,
    )

    attributes.merge(
        {
            "new": "value",
        }
    )

    assert (
        attributes.get(
            "existing"
        )
        is True
    )

    assert (
        attributes.get(
            "new"
        )
        ==
        "value"
    )



# ============================================================
# Remove / Clear
# ============================================================


def test_remove_attribute(attributes):

    attributes.set(
        "temp",
        123,
    )


    attributes.remove(
        "temp"
    )


    assert (
        attributes.get("temp")
        is None
    )



def test_clear_attributes(
    populated_attributes,
):

    populated_attributes.clear()


    assert (
        len(populated_attributes)
        ==
        0
    )



# ============================================================
# Type Handling
# ============================================================


def test_string_attribute(attributes):

    attributes.set(
        "name",
        "SciOS",
    )


    assert isinstance(
        attributes.get("name"),
        str,
    )



def test_integer_attribute(attributes):

    attributes.set(
        "count",
        100,
    )


    assert isinstance(
        attributes.get("count"),
        int,
    )



def test_float_attribute(attributes):

    attributes.set(
        "latency",
        0.25,
    )


    assert isinstance(
        attributes.get("latency"),
        float,
    )



def test_boolean_attribute(attributes):

    attributes.set(
        "active",
        True,
    )


    assert (
        attributes.get("active")
        is True
    )



def test_dict_attribute(attributes):

    attributes.set(
        "metadata",
        {
            "env": "test"
        },
    )


    assert (
        attributes.get(
            "metadata"
        )["env"]
        ==
        "test"
    )



# ============================================================
# Validation
# ============================================================


def test_invalid_key(attributes):

    with pytest.raises(
        Exception
    ):

        attributes.set(
            "",
            "value",
        )



def test_invalid_none_key(attributes):

    with pytest.raises(
        Exception
    ):

        attributes.set(
            None,
            "value",
        )



def test_validate(
    populated_attributes,
):

    assert (
        populated_attributes
        .validate()
        is True
    )



# ============================================================
# Serialization
# ============================================================


def test_to_dict(
    populated_attributes,
):

    data = (
        populated_attributes
        .to_dict()
    )


    assert isinstance(
        data,
        dict,
    )


    assert (
        data["service"]
        ==
        "scios"
    )



def test_to_json(
    populated_attributes,
):

    value = (
        populated_attributes
        .to_json()
    )


    assert isinstance(
        value,
        str,
    )


    data = json.loads(
        value
    )


    assert (
        data["version"]
        ==
        "0.3"
    )



def test_from_dict(
    populated_attributes,
):

    data = (
        populated_attributes
        .to_dict()
    )


    restored = (
        Attributes
        .from_dict(data)
    )


    assert (
        restored.get(
            "service"
        )
        ==
        "scios"
    )



def test_from_json(
    populated_attributes,
):

    data = (
        populated_attributes
        .to_json()
    )


    restored = (
        Attributes
        .from_json(data)
    )


    assert (
        restored.get(
            "version"
        )
        ==
        "0.3"
    )



# ============================================================
# Snapshot
# ============================================================


def test_snapshot(
    populated_attributes,
):

    snapshot = (
        populated_attributes
        .snapshot()
    )


    assert isinstance(
        snapshot,
        dict,
    )


    assert (
        snapshot["service"]
        ==
        "scios"
    )



def test_restore(
    populated_attributes,
):

    snapshot = (
        populated_attributes
        .snapshot()
    )


    restored = (
        Attributes
        .restore(snapshot)
    )


    assert (
        restored.get(
            "service"
        )
        ==
        "scios"
    )



# ============================================================
# Clone / Copy
# ============================================================


def test_clone(
    populated_attributes,
):

    clone = (
        populated_attributes
        .clone()
    )


    assert (
        clone.get(
            "service"
        )
        ==
        "scios"
    )



def test_copy(
    populated_attributes,
):

    copied = (
        populated_attributes
        .copy()
    )


    assert (
        copied.get(
            "version"
        )
        ==
        "0.3"
    )



def test_python_copy(
    populated_attributes,
):

    copied = copy.copy(
        populated_attributes
    )


    assert (
        copied.get(
            "service"
        )
        ==
        "scios"
    )



def test_python_deepcopy(
    populated_attributes,
):

    copied = copy.deepcopy(
        populated_attributes
    )


    assert (
        copied.get(
            "enabled"
        )
        is True
    )



# ============================================================
# Diagnostics
# ============================================================


def test_diagnostics(
    populated_attributes,
):

    result = (
        populated_attributes
        .diagnostics()
    )


    assert isinstance(
        result,
        dict,
    )



def test_summary(
    populated_attributes,
):

    result = (
        populated_attributes
        .summary()
    )


    assert isinstance(
        result,
        dict,
    )



# ============================================================
# Python Protocols
# ============================================================


def test_repr(attributes):

    result = repr(
        attributes
    )


    assert (
        "Attributes"
        in result
    )



def test_str(attributes):

    result = str(
        attributes
    )


    assert isinstance(
        result,
        str,
    )



def test_len(
    populated_attributes,
):

    assert (
        len(populated_attributes)
        ==
        3
    )



def test_contains(
    populated_attributes,
):

    assert (
        "service"
        in populated_attributes
    )



def test_getitem(
    populated_attributes,
):

    assert (
        populated_attributes["service"]
        ==
        "scios"
    )



def test_setitem(attributes):

    attributes["runtime"] = (
        "engine"
    )


    assert (
        attributes["runtime"]
        ==
        "engine"
    )



def test_iter(
    populated_attributes,
):

    keys = list(
        iter(
            populated_attributes
        )
    )


    assert (
        "service"
        in keys
    )



# ============================================================
# Equality / Hash
# ============================================================


def test_equality():

    first = Attributes()


    first.set(
        "a",
        1,
    )


    second = Attributes()


    second.set(
        "a",
        1,
    )


    assert (
        first
        ==
        second
    )



def test_hash(attributes):

    value = hash(
        attributes
    )


    assert isinstance(
        value,
        int,
    )
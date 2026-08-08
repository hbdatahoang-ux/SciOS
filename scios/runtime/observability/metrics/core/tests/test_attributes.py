# ==============================================================================
# MetricAttributes Tests
# ==============================================================================


# ==============================================================================
# Part 1. Imports
# ==============================================================================

import pytest


from scios.runtime.observability.metrics.core.attributes import (
    MetricAttributes,
    ATTRIBUTES_VERSION,
)



# ==============================================================================
# Part 2. Construction
# ==============================================================================


def test_default_attributes():

    attrs = MetricAttributes()

    assert isinstance(
        attrs,
        MetricAttributes,
    )

    assert attrs.attributes == {}



def test_custom_attributes():

    attrs = MetricAttributes(
        {
            "service": "api",
            "version": "1.0",
        }
    )

    assert attrs.attributes == {
        "service": "api",
        "version": "1.0",
    }



# ==============================================================================
# Part 3. Defaults
# ==============================================================================


def test_empty_attributes():

    attrs = MetricAttributes()

    assert len(attrs) == 0

    assert attrs.attributes == {}



# ==============================================================================
# Part 4. Validation
# ==============================================================================


def test_invalid_attributes():

    with pytest.raises(TypeError):

        MetricAttributes(
            [
                "invalid"
            ]
        )



def test_invalid_key():

    attrs = MetricAttributes()

    with pytest.raises(TypeError):

        attrs.add(
            123,
            "value",
        )



def test_invalid_value():

    with pytest.raises(TypeError):

        MetricAttributes(
            {
                "key": None,
            }
        )



# ==============================================================================
# Part 5. Properties
# ==============================================================================


def test_attributes():

    attrs = MetricAttributes(
        {
            "runtime": "python",
        }
    )

    assert attrs.attributes == {
        "runtime": "python",
    }



# ==============================================================================
# Part 6. Operations
# ==============================================================================


def test_add():

    attrs = MetricAttributes()

    attrs.add(
        "runtime",
        "python",
    )

    assert attrs["runtime"] == "python"



def test_update():

    attrs = MetricAttributes()

    attrs.update(
        {
            "a": 1,
            "b": 2,
        }
    )

    assert attrs.attributes == {
        "a": 1,
        "b": 2,
    }



def test_remove():

    attrs = MetricAttributes(
        {
            "runtime": "python",
        }
    )

    attrs.remove(
        "runtime"
    )

    assert "runtime" not in attrs



def test_pop():

    attrs = MetricAttributes(
        {
            "runtime": "python",
        }
    )

    value = attrs.pop(
        "runtime"
    )

    assert value == "python"

    assert len(attrs) == 0



def test_clear():

    attrs = MetricAttributes(
        {
            "a": 1,
            "b": 2,
        }
    )

    attrs.clear()

    assert attrs.attributes == {}



def test_has():

    attrs = MetricAttributes(
        {
            "runtime": "python",
        }
    )

    assert attrs.has(
        "runtime"
    )

    assert not attrs.has(
        "missing"
    )



def test_get():

    attrs = MetricAttributes(
        {
            "runtime": "python",
        }
    )

    assert attrs.get(
        "runtime"
    ) == "python"


    assert attrs.get(
        "missing"
    ) is None

# ==============================================================================
# Part 7. Mapping Protocol
# ==============================================================================


def test_getitem():

    attrs = MetricAttributes(
        {
            "runtime": "python",
        }
    )

    assert attrs["runtime"] == "python"



def test_setitem():

    attrs = MetricAttributes()

    attrs["runtime"] = "python"

    assert attrs["runtime"] == "python"



def test_delitem():

    attrs = MetricAttributes(
        {
            "runtime": "python",
        }
    )

    del attrs["runtime"]

    assert "runtime" not in attrs



def test_contains():

    attrs = MetricAttributes(
        {
            "runtime": "python",
        }
    )

    assert "runtime" in attrs

    assert "missing" not in attrs



def test_iter():

    attrs = MetricAttributes(
        {
            "a": 1,
            "b": 2,
        }
    )

    assert list(iter(attrs)) == [
        "a",
        "b",
    ]



def test_len():

    attrs = MetricAttributes(
        {
            "a": 1,
            "b": 2,
        }
    )

    assert len(attrs) == 2



# ==============================================================================
# Part 8. Serialization
# ==============================================================================


def test_to_dict():

    attrs = MetricAttributes(
        {
            "service": "api",
        }
    )

    data = attrs.to_dict()

    assert data == {
        "service": "api",
    }



def test_from_dict():

    attrs = MetricAttributes.from_dict(
        {
            "service": "api",
        }
    )

    assert attrs.attributes == {
        "service": "api",
    }



def test_to_json():

    attrs = MetricAttributes(
        {
            "service": "api",
        }
    )

    data = attrs.to_json()

    assert isinstance(
        data,
        str,
    )

    assert "service" in data



def test_from_json():

    attrs = MetricAttributes.from_json(
        '{"service": "api"}'
    )

    assert attrs.attributes == {
        "service": "api",
    }



# ==============================================================================
# Part 9. Copy
# ==============================================================================


def test_copy():

    attrs = MetricAttributes(
        {
            "a": 1,
        }
    )

    copied = attrs.copy()

    assert copied == attrs

    assert copied is not attrs



def test_clone():

    attrs = MetricAttributes(
        {
            "a": {
                "nested": True,
            }
        }
    )

    cloned = attrs.clone()

    assert cloned == attrs

    assert cloned is not attrs



# ==============================================================================
# Part 10. Equality
# ==============================================================================


def test_eq():

    a = MetricAttributes(
        {
            "x": 1,
        }
    )

    b = MetricAttributes(
        {
            "x": 1,
        }
    )

    assert a == b



def test_hash():

    attrs = MetricAttributes(
        {
            "x": 1,
        }
    )

    assert isinstance(
        hash(attrs),
        int,
    )



# ==============================================================================
# Part 11. Representation
# ==============================================================================


def test_repr():

    attrs = MetricAttributes(
        {
            "x": 1,
        }
    )

    value = repr(attrs)

    assert "MetricAttributes" in value



def test_str():

    attrs = MetricAttributes(
        {
            "x": 1,
        }
    )

    value = str(attrs)

    assert "x" in value



# ==============================================================================
# Part 12. Public API
# ==============================================================================


def test_all():

    from scios.runtime.observability.metrics.core import attributes

    assert hasattr(
        attributes,
        "__all__",
    )

    assert "MetricAttributes" in attributes.__all__



def test_version():

    from scios.runtime.observability.metrics.core.attributes import (
        __version__,
    )

    assert __version__ == ATTRIBUTES_VERSION



# ==============================================================================
# Part 13. Regression
# ==============================================================================


def test_attributes_are_copied():

    source = {
        "runtime": "python",
    }

    attrs = MetricAttributes(
        source
    )

    source["runtime"] = "changed"

    assert attrs["runtime"] == "python"



def test_json_roundtrip():

    attrs = MetricAttributes(
        {
            "service": "api",
            "version": 1,
        }
    )

    restored = MetricAttributes.from_json(
        attrs.to_json()
    )

    assert restored == attrs



def test_dict_roundtrip():

    attrs = MetricAttributes(
        {
            "service": "api",
            "version": 1,
        }
    )

    restored = MetricAttributes.from_dict(
        attrs.to_dict()
    )

    assert restored == attrs



def test_order_is_preserved():

    attrs = MetricAttributes(
        {
            "first": 1,
            "second": 2,
            "third": 3,
        }
    )

    assert list(attrs.keys()) == [
        "first",
        "second",
        "third",
    ]    
"""
Tests for SciOS shared JSON type contracts.
"""

from pathlib import Path

from scios.shared.json_types import (
    JSONArray,
    JSONObject,
    JSONPrimitive,
    JSONValue,
    is_json_primitive,
    is_json_value,
)


# ============================================================================
# Public API
# ============================================================================


def test_public_api():
    expected = {
        "JSONPrimitive",
        "JSONValue",
        "JSONObject",
        "JSONArray",
        "is_json_primitive",
        "is_json_value",
    }

    assert set(__import__(
        "scios.shared.json_types",
        fromlist=["__all__"],
    ).__all__) == expected


# ============================================================================
# Primitive validation
# ============================================================================


def test_json_primitive_accepts_string():
    assert is_json_primitive("hello")


def test_json_primitive_accepts_integer():
    assert is_json_primitive(42)


def test_json_primitive_accepts_float():
    assert is_json_primitive(3.14)


def test_json_primitive_accepts_boolean():
    assert is_json_primitive(True)
    assert is_json_primitive(False)


def test_json_primitive_accepts_none():
    assert is_json_primitive(None)


def test_json_primitive_rejects_non_primitive():
    assert not is_json_primitive([])
    assert not is_json_primitive({})
    assert not is_json_primitive((1, 2))
    assert not is_json_primitive({1, 2})
    assert not is_json_primitive(Path("data"))


# ============================================================================
# JSON value validation
# ============================================================================


def test_json_value_accepts_primitives():
    assert is_json_value("text")
    assert is_json_value(1)
    assert is_json_value(1.5)
    assert is_json_value(True)
    assert is_json_value(False)
    assert is_json_value(None)


def test_json_value_accepts_empty_list():
    assert is_json_value([])


def test_json_value_accepts_empty_dict():
    assert is_json_value({})


def test_json_value_accepts_flat_list():
    assert is_json_value([1, 2, 3, "text", True, None])


def test_json_value_accepts_flat_dict():
    assert is_json_value({
        "name": "SciOS",
        "version": 1,
        "enabled": True,
        "value": None,
    })


def test_json_value_accepts_nested_list():
    value = [
        [1, 2],
        ["a", "b"],
        [True, None],
    ]

    assert is_json_value(value)


def test_json_value_accepts_nested_dict():
    value = {
        "system": {
            "name": "SciOS",
            "enabled": True,
        },
        "runtime": {
            "workers": 4,
        },
    }

    assert is_json_value(value)


def test_json_value_accepts_mixed_recursive_structure():
    value = {
        "name": "SciOS",
        "items": [
            {"id": 1, "valid": True},
            {"id": 2, "valid": False},
            None,
        ],
    }

    assert is_json_value(value)


# ============================================================================
# Invalid structures
# ============================================================================


def test_json_value_rejects_tuple():
    assert not is_json_value((1, 2, 3))


def test_json_value_rejects_set():
    assert not is_json_value({1, 2, 3})


def test_json_value_rejects_path():
    assert not is_json_value(Path("data"))


def test_json_value_rejects_object():
    class Example:
        pass

    assert not is_json_value(Example())


def test_json_value_rejects_non_string_dict_key():
    assert not is_json_value({
        1: "value",
    })


def test_json_value_rejects_nested_non_string_key():
    assert not is_json_value({
        "data": {
            1: "invalid",
        },
    })


def test_json_value_rejects_nested_invalid_value():
    assert not is_json_value({
        "data": [
            1,
            2,
            Path("invalid"),
        ],
    })


def test_json_value_rejects_mixed_invalid_list():
    assert not is_json_value([
        "valid",
        42,
        {"ok": True},
        {1, 2},
    ])


# ============================================================================
# Type aliases
# ============================================================================


def test_json_type_aliases_exist():
    assert JSONPrimitive is not None
    assert JSONValue is not None
    assert JSONObject is not None
    assert JSONArray is not None

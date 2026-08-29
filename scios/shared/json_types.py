"""
SciOS JSON Types
================

Canonical JSON-compatible type definitions shared across the
Scientific Cognitive Operating System (SciOS).

Design Goals
------------
- Python 3.11+
- Recursive JSON type definitions
- Zero runtime dependencies
- Explicit structural validation
- Stable public API
- Reusable across all SciOS subsystems

The runtime helpers validate the SciOS JSON type model only.
They do not perform actual JSON serialization.
"""

from __future__ import annotations

from typing import Any
from typing import TypeAlias
from typing import Union


# ============================================================================
# Public API
# ============================================================================

__all__ = [
    "JSONPrimitive",
    "JSONValue",
    "JSONObject",
    "JSONArray",
    "is_json_primitive",
    "is_json_value",
]


# ============================================================================
# JSON Primitive Types
# ============================================================================

JSONPrimitive: TypeAlias = Union[
    str,
    int,
    float,
    bool,
    None,
]


# ============================================================================
# Recursive JSON Types
# ============================================================================

JSONValue: TypeAlias = Union[
    JSONPrimitive,
    "JSONObject",
    "JSONArray",
]

JSONObject: TypeAlias = dict[str, JSONValue]

JSONArray: TypeAlias = list[JSONValue]


# ============================================================================
# Runtime Validation
# ============================================================================

_JSON_PRIMITIVE_TYPES: tuple[type[Any], ...] = (
    str,
    int,
    float,
    bool,
    type(None),
)


def is_json_primitive(value: Any) -> bool:
    """
    Return True when *value* is a supported JSON primitive.

    Supported primitive values are:

    - str
    - int
    - float
    - bool
    - None

    Python's bool is intentionally accepted as a JSON primitive.
    """

    return isinstance(value, _JSON_PRIMITIVE_TYPES)


def is_json_value(value: Any) -> bool:
    """
    Recursively validate a value against the SciOS JSON type model.

    Valid structures consist exclusively of:

    - JSON primitives
    - lists containing JSON values
    - dictionaries with string keys and JSON values

    This function validates structure only. It does not call
    json.dumps() and does not perform serialization.
    """

    if is_json_primitive(value):
        return True

    if isinstance(value, list):
        return all(
            is_json_value(item)
            for item in value
        )

    if isinstance(value, dict):
        return all(
            isinstance(key, str)
            and is_json_value(item)
            for key, item in value.items()
        )

    return False

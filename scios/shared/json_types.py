"""
SciOS JSON Types
================

Canonical JSON type definitions shared across the Scientific
Cognitive Operating System (SciOS).

Design Goals
------------
- Python 3.11+
- Recursive JSON definitions
- Zero runtime dependencies
- Reusable across all SciOS subsystems
"""

from __future__ import annotations

from typing import Any
from typing import TypeAlias
from typing import Union

__all__ = [
    "JSONPrimitive",
    "JSONValue",
    "JSONObject",
    "JSONArray",
    "is_json_primitive",
    "is_json_value",
]

# ==========================================================
# JSON Primitive Types
# ==========================================================

JSONPrimitive: TypeAlias = Union[
    str,
    int,
    float,
    bool,
    None,
]

# ==========================================================
# Recursive JSON Types
# ==========================================================

JSONValue: TypeAlias = Union[
    JSONPrimitive,
    "JSONObject",
    "JSONArray",
]

JSONObject: TypeAlias = dict[str, JSONValue]

JSONArray: TypeAlias = list[JSONValue]

# ==========================================================
# Runtime Helpers
# ==========================================================

_JSON_PRIMITIVE_TYPES = (
    str,
    int,
    float,
    bool,
    type(None),
)


def is_json_primitive(value: Any) -> bool:
    """
    Return True if *value* is a valid JSON primitive.
    """

    return isinstance(value, _JSON_PRIMITIVE_TYPES)


def is_json_value(value: Any) -> bool:
    """
    Recursively validate whether *value* is JSON serializable
    according to the SciOS JSON type model.

    This function validates structure only.
    It does not attempt serialization.
    """

    if is_json_primitive(value):
        return True

    if isinstance(value, list):
        return all(is_json_value(v) for v in value)

    if isinstance(value, dict):
        return all(
            isinstance(k, str)
            and is_json_value(v)
            for k, v in value.items()
        )

    return False
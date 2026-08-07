"""
SciOS Metrics Serialization Utilities
=====================================

Shared helpers for serialization backends.

Python 3.11+
"""

from __future__ import annotations

# ==============================================================================
# Part 1. Imports & Constants
# ==============================================================================

import json
import pickle
import zlib

from typing import Any
from typing import Mapping
from typing import TypeAlias

__all__ = [

    # ------------------------------------------------------------------
    # Constants
    # ------------------------------------------------------------------

    "DEFAULT_ENCODING",
    "DEFAULT_PROTOCOL",
    "DEFAULT_COMPRESS_LEVEL",

    # ------------------------------------------------------------------
    # Type Aliases
    # ------------------------------------------------------------------

    "BytesLike",
    "JsonType",

    # ------------------------------------------------------------------
    # Encoding
    # ------------------------------------------------------------------

    "ensure_bytes",
    "ensure_str",
    "encode_text",
    "decode_text",
    "normalize_encoding",
    "detect_encoding",

    # ------------------------------------------------------------------
    # JSON
    # ------------------------------------------------------------------

    "json_dumps",
    "json_loads",
    "json_snapshot",
    "json_restore",
    "is_json",
    "validate_json",

    # ------------------------------------------------------------------
    # Pickle
    # ------------------------------------------------------------------

    "pickle_dumps",
    "pickle_loads",
    "pickle_snapshot",
    "pickle_restore",
    "is_pickle",
    "validate_pickle",

    # ------------------------------------------------------------------
    # Compression
    # ------------------------------------------------------------------

    "compress",
    "decompress",
    "compress_if_needed",
    "decompress_if_needed",
    "compression_ratio",
    "validate_compression",
]

DEFAULT_ENCODING = "utf-8"
DEFAULT_PROTOCOL = pickle.HIGHEST_PROTOCOL
DEFAULT_COMPRESS_LEVEL = 6

BytesLike: TypeAlias = bytes | bytearray | memoryview
JsonType: TypeAlias = Mapping[str, Any] | list[Any]


# ==============================================================================
# Part 2. Encoding Helpers
# ==============================================================================


def ensure_bytes(
    value: Any,
    encoding: str = DEFAULT_ENCODING,
) -> bytes:
    """
    Convert value to bytes.
    """

    if isinstance(value, bytes):
        return value

    if isinstance(value, bytearray):
        return bytes(value)

    if isinstance(value, memoryview):
        return value.tobytes()

    if isinstance(value, str):
        return value.encode(encoding)

    return str(value).encode(encoding)


def ensure_str(
    value: Any,
    encoding: str = DEFAULT_ENCODING,
) -> str:
    """
    Convert value to string.
    """

    if isinstance(value, str):
        return value

    if isinstance(value, (bytes, bytearray, memoryview)):
        return bytes(value).decode(encoding)

    return str(value)


def encode_text(
    text: str,
    encoding: str = DEFAULT_ENCODING,
) -> bytes:
    return text.encode(encoding)


def decode_text(
    data: BytesLike,
    encoding: str = DEFAULT_ENCODING,
) -> str:
    return bytes(data).decode(encoding)


def normalize_encoding(
    encoding: str | None,
) -> str:
    return (encoding or DEFAULT_ENCODING).lower()


def detect_encoding(
    data: BytesLike,
) -> str:
    """
    Simple encoding detector.
    """

    try:
        bytes(data).decode("utf-8")
        return "utf-8"
    except UnicodeDecodeError:
        return "latin-1"


# ==============================================================================
# Part 3. JSON Helpers
# ==============================================================================


def json_dumps(
    obj: Any,
    *,
    indent: int | None = None,
    sort_keys: bool = False,
    ensure_ascii: bool = False,
) -> str:
    return json.dumps(
        obj,
        indent=indent,
        sort_keys=sort_keys,
        ensure_ascii=ensure_ascii,
        default=lambda o: getattr(o, "__dict__", str(o)),
    )


def json_loads(
    value: str | BytesLike,
) -> Any:
    if isinstance(value, (bytes, bytearray, memoryview)):
        value = decode_text(value)

    return json.loads(value)


def json_snapshot(
    obj: Any,
) -> str:
    return json_dumps(obj)


def json_restore(
    snapshot: str | BytesLike,
) -> Any:
    return json_loads(snapshot)


def is_json(
    value: str | BytesLike,
) -> bool:
    try:
        json_loads(value)
        return True
    except Exception:
        return False


def validate_json(
    value: str | BytesLike,
) -> bool:
    return is_json(value)


# ==============================================================================
# Part 4. Pickle Helpers
# ==============================================================================


def pickle_dumps(
    obj: Any,
    protocol: int = DEFAULT_PROTOCOL,
) -> bytes:
    return pickle.dumps(
        obj,
        protocol=protocol,
    )


def pickle_loads(
    data: BytesLike,
) -> Any:
    return pickle.loads(
        bytes(data),
    )


def pickle_snapshot(
    obj: Any,
) -> bytes:
    return pickle_dumps(obj)


def pickle_restore(
    snapshot: BytesLike,
) -> Any:
    return pickle_loads(snapshot)


def is_pickle(
    value: BytesLike,
) -> bool:
    try:
        pickle_loads(value)
        return True
    except Exception:
        return False


def validate_pickle(
    value: BytesLike,
) -> bool:
    return is_pickle(value)


# ==============================================================================
# Part 5. Compression Helpers
# ==============================================================================


def compress(
    data: BytesLike,
    level: int = DEFAULT_COMPRESS_LEVEL,
) -> bytes:
    return zlib.compress(
        bytes(data),
        level,
    )


def decompress(
    data: BytesLike,
) -> bytes:
    return zlib.decompress(
        bytes(data),
    )


def compress_if_needed(
    data: BytesLike,
    *,
    enabled: bool = True,
    level: int = DEFAULT_COMPRESS_LEVEL,
) -> bytes:
    if not enabled:
        return bytes(data)

    return compress(
        data,
        level,
    )


def decompress_if_needed(
    data: BytesLike,
    *,
    compressed: bool = True,
) -> bytes:
    if not compressed:
        return bytes(data)

    return decompress(data)


def compression_ratio(
    original: BytesLike,
    compressed: BytesLike,
) -> float:
    original_size = len(bytes(original))

    if original_size == 0:
        return 1.0

    return len(bytes(compressed)) / original_size


def validate_compression(
    original: BytesLike,
    compressed: BytesLike,
) -> bool:
    try:
        return decompress(compressed) == bytes(original)
    except Exception:
        return False

# ==============================================================================
# Part 6. Mapping Helpers
# ==============================================================================

from copy import deepcopy as _deepcopy


def deep_merge(
    left: Mapping[str, Any],
    right: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Recursively merge two mappings.
    """

    result: dict[str, Any] = dict(left)

    for key, value in right.items():

        if (
            key in result
            and isinstance(result[key], Mapping)
            and isinstance(value, Mapping)
        ):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = _deepcopy(value)

    return result


def deep_copy(
    mapping: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Deep copy a mapping.
    """

    return _deepcopy(dict(mapping))


def flatten_mapping(
    mapping: Mapping[str, Any],
    parent_key: str = "",
    separator: str = ".",
) -> dict[str, Any]:
    """
    Flatten nested mapping.
    """

    items: dict[str, Any] = {}

    for key, value in mapping.items():

        new_key = (
            f"{parent_key}{separator}{key}"
            if parent_key
            else key
        )

        if isinstance(value, Mapping):
            items.update(
                flatten_mapping(
                    value,
                    new_key,
                    separator,
                )
            )
        else:
            items[new_key] = value

    return items


def unflatten_mapping(
    mapping: Mapping[str, Any],
    separator: str = ".",
) -> dict[str, Any]:
    """
    Restore flattened mapping.
    """

    result: dict[str, Any] = {}

    for key, value in mapping.items():

        current = result

        parts = key.split(separator)

        for part in parts[:-1]:
            current = current.setdefault(part, {})

        current[parts[-1]] = value

    return result


def filter_mapping(
    mapping: Mapping[str, Any],
    *,
    include_none: bool = False,
) -> dict[str, Any]:
    """
    Remove None values.
    """

    if include_none:
        return dict(mapping)

    return {
        key: value
        for key, value in mapping.items()
        if value is not None
    }


def validate_mapping(
    value: Any,
) -> bool:
    """
    Validate mapping object.
    """

    return isinstance(value, Mapping)


# ==============================================================================
# Part 7. Validation
# ==============================================================================


def validate_bytes(
    value: Any,
) -> bool:
    return isinstance(
        value,
        (bytes, bytearray, memoryview),
    )


def validate_string(
    value: Any,
) -> bool:
    return isinstance(value, str)


def validate_encoding(
    encoding: str,
) -> bool:
    try:
        "".encode(encoding)
        return True
    except LookupError:
        return False


def validate_protocol(
    protocol: int,
) -> bool:
    return (
        isinstance(protocol, int)
        and 0 <= protocol <= pickle.HIGHEST_PROTOCOL
    )


def validate_options(
    options: Any,
) -> bool:
    return (
        options is None
        or isinstance(options, Mapping)
    )


def validate(
    value: Any,
) -> bool:
    """
    Generic validation.
    """

    return value is not None


# ==============================================================================
# Part 8. Diagnostics
# ==============================================================================


def summary() -> dict[str, Any]:
    """
    Utility summary.
    """

    return {
        "encoding": DEFAULT_ENCODING,
        "pickle_protocol": DEFAULT_PROTOCOL,
        "compression_level": DEFAULT_COMPRESS_LEVEL,
    }


def diagnostics() -> dict[str, Any]:
    """
    Diagnostics information.
    """

    return {
        "summary": summary(),
        "json": True,
        "pickle": True,
        "compression": True,
    }


def utility_report() -> dict[str, Any]:
    """
    Utility report.
    """

    return {
        "status": "ok",
        "diagnostics": diagnostics(),
    }


def overall_status() -> str:
    """
    Overall utility status.
    """

    return "healthy"


# ==============================================================================
# Part 9. Public API
# ==============================================================================

__all__.extend(

    [

        # ------------------------------------------------------------------
        # Mapping
        # ------------------------------------------------------------------

        "deep_merge",
        "deep_copy",
        "flatten_mapping",
        "unflatten_mapping",
        "filter_mapping",
        "validate_mapping",

        # ------------------------------------------------------------------
        # Validation
        # ------------------------------------------------------------------

        "validate_bytes",
        "validate_string",
        "validate_encoding",
        "validate_protocol",
        "validate_options",
        "validate",

        # ------------------------------------------------------------------
        # Diagnostics
        # ------------------------------------------------------------------

        "summary",
        "diagnostics",
        "utility_report",
        "overall_status",

    ]

)        
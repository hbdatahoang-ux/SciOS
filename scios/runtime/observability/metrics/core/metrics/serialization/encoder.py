"""
SciOS Metrics Serialization Encoder
===================================

Part 1–4
"""

from __future__ import annotations

# ==========================================================
# Part 1. Imports & Constants
# ==========================================================

import threading
import base64
from copy import deepcopy
from typing import Any, TypeAlias

__all__ = [
    "Serializable",
    "EncodedValue",
    "EncoderOptions",
    "MetadataType",
    "MetricEncoder",
]

DEFAULT_INDENT: int = 2
DEFAULT_SORT_KEYS: bool = True
DEFAULT_ASCII: bool = False
DEFAULT_ENCODING: str = "utf-8"
DEFAULT_COMPACT: bool = False


# ==========================================================
# Part 2. Type Aliases
# ==========================================================

Serializable: TypeAlias = (
    dict[str, Any]
    | list[Any]
    | tuple[Any, ...]
    | str
    | int
    | float
    | bool
    | None
)

EncodedValue: TypeAlias = Any

EncoderOptions: TypeAlias = dict[str, Any]

MetadataType: TypeAlias = dict[str, Any]


# ==========================================================
# Part 3. Constructor
# ==========================================================


class MetricEncoder:
    """
    Generic serialization encoder.
    """

    __slots__ = (
        "_indent",
        "_sort_keys",
        "_ensure_ascii",
        "_encoding",
        "_compact",
        "_lock",
    )

    _indent: int
    _sort_keys: bool
    _ensure_ascii: bool
    _encoding: str
    _compact: bool
    _lock: Any

    def __init__(
        self,
        *,
        indent: int = DEFAULT_INDENT,
        sort_keys: bool = DEFAULT_SORT_KEYS,
        ensure_ascii: bool = DEFAULT_ASCII,
        encoding: str = DEFAULT_ENCODING,
        compact: bool = DEFAULT_COMPACT,
    ) -> None:

        self._indent = int(indent)
        self._sort_keys = bool(sort_keys)
        self._ensure_ascii = bool(ensure_ascii)
        self._encoding = str(encoding)
        self._compact = bool(compact)

        self._lock = threading.RLock()


# ==========================================================
# Part 4. Properties
# ==========================================================

    @property
    def indent(self) -> int:
        return self._indent

    @indent.setter
    def indent(self, value: int) -> None:
        self._indent = int(value)

    @property
    def sort_keys(self) -> bool:
        return self._sort_keys

    @sort_keys.setter
    def sort_keys(self, value: bool) -> None:
        self._sort_keys = bool(value)

    @property
    def ensure_ascii(self) -> bool:
        return self._ensure_ascii

    @ensure_ascii.setter
    def ensure_ascii(self, value: bool) -> None:
        self._ensure_ascii = bool(value)

    @property
    def encoding(self) -> str:
        return self._encoding

    @encoding.setter
    def encoding(self, value: str) -> None:
        self._encoding = str(value)

    @property
    def compact(self) -> bool:
        return self._compact

    @compact.setter
    def compact(self, value: bool) -> None:
        self._compact = bool(value)

# ==========================================================
# Part 5. Primitive Encoding
# ==========================================================

    def encode_none(self, value: None = None) -> None:
        return None

    def encode_bool(self, value: bool) -> bool:
        return bool(value)

    def encode_int(self, value: int) -> int:
        return int(value)

    def encode_float(self, value: float) -> float:
        return float(value)

    def encode_str(self, value: str) -> str:
        return str(value)

    def encode_bytes(self, value: bytes) -> str:
        return base64.b64encode(value).decode("ascii")


# ==========================================================
# Part 6. Container Encoding
# ==========================================================

    def encode_list(self, value: list[Any]) -> list[Any]:
        return [self.encode(v) for v in value]

    def encode_tuple(self, value: tuple[Any, ...]) -> list[Any]:
        return [self.encode(v) for v in value]

    def encode_set(self, value: set[Any]) -> list[Any]:
        return [self.encode(v) for v in sorted(value, key=repr)]

    def encode_dict(self, value: dict[Any, Any]) -> dict[str, Any]:
        return {
            str(k): self.encode(v)
            for k, v in value.items()
        }

    def encode_mapping(self, value: Any) -> dict[str, Any]:
        return {
            str(k): self.encode(v)
            for k, v in dict(value).items()
        }


# ==========================================================
# Part 7. Object Encoding
# ==========================================================

    def encode_dataclass(self, obj: Any) -> dict[str, Any]:
        from dataclasses import asdict

        return self.encode(asdict(obj))

    def encode_enum(self, obj: Any) -> Any:
        return obj.value

    def encode_datetime(self, obj: Any) -> str:
        return obj.isoformat()

    def encode_path(self, obj: Any) -> str:
        return str(obj)

    def encode_object(self, obj: Any) -> Any:

        from dataclasses import is_dataclass
        from datetime import datetime
        from enum import Enum
        from pathlib import Path
        from collections.abc import Mapping

        if is_dataclass(obj):
            return self.encode_dataclass(obj)

        if isinstance(obj, Enum):
            return self.encode_enum(obj)

        if isinstance(obj, datetime):
            return self.encode_datetime(obj)

        if isinstance(obj, Path):
            return self.encode_path(obj)

        if isinstance(obj, dict):
            return self.encode_dict(obj)

        if isinstance(obj, Mapping):
            return self.encode_mapping(obj)

        if isinstance(obj, list):
            return self.encode_list(obj)

        if isinstance(obj, tuple):
            return self.encode_tuple(obj)

        if isinstance(obj, set):
            return self.encode_set(obj)

        if hasattr(obj, "to_dict"):
            return self.encode(obj.to_dict())

        if hasattr(obj, "__dict__"):
            return self.encode_dict(vars(obj))

        return repr(obj)


# ==========================================================
# Part 8. Generic API
# ==========================================================

    def encode(self, value: Any) -> EncodedValue:

        from dataclasses import is_dataclass
        from datetime import datetime
        from enum import Enum
        from pathlib import Path
        from collections.abc import Mapping

        if value is None:
            return self.encode_none(value)

        if isinstance(value, bool):
            return self.encode_bool(value)

        if isinstance(value, int) and not isinstance(value, bool):
            return self.encode_int(value)

        if isinstance(value, float):
            return self.encode_float(value)

        if isinstance(value, str):
            return self.encode_str(value)

        if isinstance(value, bytes):
            return self.encode_bytes(value)

        if isinstance(value, list):
            return self.encode_list(value)

        if isinstance(value, tuple):
            return self.encode_tuple(value)

        if isinstance(value, set):
            return self.encode_set(value)

        if isinstance(value, dict):
            return self.encode_dict(value)

        if isinstance(value, Mapping):
            return self.encode_mapping(value)

        if is_dataclass(value):
            return self.encode_dataclass(value)

        if isinstance(value, Enum):
            return self.encode_enum(value)

        if isinstance(value, datetime):
            return self.encode_datetime(value)

        if isinstance(value, Path):
            return self.encode_path(value)

        return self.encode_object(value)

    def dumps(self, value: Any) -> str:
        import json

        return json.dumps(
            self.encode(value),
            indent=None if self._compact else self._indent,
            ensure_ascii=self._ensure_ascii,
            sort_keys=self._sort_keys,
        )

    def dump(self, value: Any, fp: Any) -> None:
        fp.write(self.dumps(value))

    def encode_many(self, values: list[Any]) -> list[Any]:
        return [self.encode(v) for v in values]

    def encode_metadata(self, metadata: MetadataType) -> dict[str, Any]:
        return self.encode_dict(metadata)


# ==========================================================
# Part 9. Validation
# ==========================================================

    def validate(self, value: Any) -> bool:
        try:
            self.encode(value)
            return True
        except Exception:
            return False

    def is_serializable(self, value: Any) -> bool:
        return self.validate(value)


# ==========================================================
# Part 10. Clone API
# ==========================================================

    def copy(self) -> "MetricEncoder":
        return MetricEncoder(
            indent=self._indent,
            sort_keys=self._sort_keys,
            ensure_ascii=self._ensure_ascii,
            encoding=self._encoding,
            compact=self._compact,
        )

    def deepcopy(self) -> "MetricEncoder":
        return deepcopy(self)

    def clone(self) -> "MetricEncoder":
        return self.deepcopy()


# ==========================================================
# Part 11. Python Protocols
# ==========================================================

    def __call__(self, value: Any) -> EncodedValue:
        return self.encode(value)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"indent={self._indent}, "
            f"sort_keys={self._sort_keys}, "
            f"ensure_ascii={self._ensure_ascii}, "
            f"encoding={self._encoding!r}, "
            f"compact={self._compact})"
        )

    def __str__(self) -> str:
        return self.__repr__()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MetricEncoder):
            return NotImplemented

        return (
            self._indent == other._indent
            and self._sort_keys == other._sort_keys
            and self._ensure_ascii == other._ensure_ascii
            and self._encoding == other._encoding
            and self._compact == other._compact
        )

    def __hash__(self) -> int:
        return hash(
            (
                self._indent,
                self._sort_keys,
                self._ensure_ascii,
                self._encoding,
                self._compact,
            )
        )

    def __getstate__(self) -> dict[str, Any]:
        return {
            "indent": self._indent,
            "sort_keys": self._sort_keys,
            "ensure_ascii": self._ensure_ascii,
            "encoding": self._encoding,
            "compact": self._compact,
        }

    def __setstate__(self, state: dict[str, Any]) -> None:
        self.__init__(
            indent=state["indent"],
            sort_keys=state["sort_keys"],
            ensure_ascii=state["ensure_ascii"],
            encoding=state["encoding"],
            compact=state["compact"],
        )


# ==========================================================
# Part 12. Diagnostics
# ==========================================================

    def summary(self) -> dict[str, Any]:
        return {
            "indent": self._indent,
            "sort_keys": self._sort_keys,
            "ensure_ascii": self._ensure_ascii,
            "encoding": self._encoding,
            "compact": self._compact,
        }

    def diagnostics(self) -> dict[str, Any]:
        return {
            "class": self.__class__.__name__,
            "configuration": self.summary(),
            "serializable": True,
        }

    def encoder_report(self) -> dict[str, Any]:
        return {
            "encoder": self.__class__.__name__,
            "settings": self.summary(),
            "diagnostics": self.diagnostics(),
        }

    def overall_status(self) -> str:
        return "healthy"

# ==============================================================================
# Backward / Public API Alias
# ==============================================================================

Encoder = MetricEncoder

# ==========================================================
# Part 13. Public API
# ==========================================================

__all__ = [
    "DEFAULT_INDENT",
    "DEFAULT_SORT_KEYS",
    "DEFAULT_ASCII",
    "DEFAULT_ENCODING",
    "DEFAULT_COMPACT",
    "Serializable",
    "EncodedValue",
    "EncoderOptions",
    "MetadataType",
    "Encoder",
    "MetricEncoder",   # alias tương thích ngược
]               
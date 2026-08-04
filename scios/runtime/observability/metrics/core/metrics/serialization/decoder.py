"""
SciOS Metrics Serialization Decoder
===================================

Generic decoder for metrics serialization.

Python 3.11+
"""

from __future__ import annotations

# ==============================================================================
# Part 1. Imports & Constants
# ==============================================================================

import copy
import json

from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any, TypeAlias

__all__ = [
    "DEFAULT_ENCODING",
    "DEFAULT_STRICT",
    "DEFAULT_OBJECT_HOOK",
    "DEFAULT_PARSE_FLOAT",
    "DEFAULT_PARSE_INT",
    "DecodedValue",
    "DecoderOptions",
    "ObjectHook",
    "MetadataType",
    "Decoder",
]

DEFAULT_ENCODING: str = "utf-8"
DEFAULT_STRICT: bool = True
DEFAULT_OBJECT_HOOK = None
DEFAULT_PARSE_FLOAT = float
DEFAULT_PARSE_INT = int


# ==============================================================================
# Part 2. Type Aliases
# ==============================================================================

DecodedValue: TypeAlias = (
    None
    | bool
    | int
    | float
    | str
    | bytes
    | list[Any]
    | tuple[Any, ...]
    | set[Any]
    | dict[str, Any]
    | Path
    | Any
)

ObjectHook: TypeAlias = Callable[[dict[str, Any]], Any] | None

DecoderOptions: TypeAlias = dict[str, Any]

MetadataType: TypeAlias = Mapping[str, Any]


# ==============================================================================
# Part 3. Constructor
# ==============================================================================


class Decoder:
    """
    Generic serialization decoder.
    """

    __slots__ = (
        "_encoding",
        "_strict",
        "_object_hook",
        "_parse_float",
        "_parse_int",
    )

    __annotations__ = {
        "_encoding": str,
        "_strict": bool,
        "_object_hook": ObjectHook,
        "_parse_float": Callable[[str], Any],
        "_parse_int": Callable[[str], Any],
    }

    def __init__(
        self,
        *,
        encoding: str = DEFAULT_ENCODING,
        strict: bool = DEFAULT_STRICT,
        object_hook: ObjectHook = DEFAULT_OBJECT_HOOK,
        parse_float: Callable[[str], Any] = DEFAULT_PARSE_FLOAT,
        parse_int: Callable[[str], Any] = DEFAULT_PARSE_INT,
    ) -> None:
        self._encoding = str(encoding)
        self._strict = bool(strict)
        self._object_hook = object_hook
        self._parse_float = parse_float
        self._parse_int = parse_int

    # ==========================================================================
    # Part 4. Properties
    # ==========================================================================

    @property
    def encoding(self) -> str:
        """Text encoding."""
        return self._encoding

    @encoding.setter
    def encoding(self, value: str) -> None:
        self._encoding = str(value)

    @property
    def strict(self) -> bool:
        """Strict decoding mode."""
        return self._strict

    @strict.setter
    def strict(self, value: bool) -> None:
        self._strict = bool(value)

    @property
    def object_hook(self) -> ObjectHook:
        """JSON object hook."""
        return self._object_hook

    @object_hook.setter
    def object_hook(self, value: ObjectHook) -> None:
        self._object_hook = value

    @property
    def parse_float(self) -> Callable[[str], Any]:
        """Float parser."""
        return self._parse_float

    @parse_float.setter
    def parse_float(self, value: Callable[[str], Any]) -> None:
        self._parse_float = value

    @property
    def parse_int(self) -> Callable[[str], Any]:
        """Integer parser."""
        return self._parse_int

    @parse_int.setter
    def parse_int(self, value: Callable[[str], Any]) -> None:
        self._parse_int = value

    # ==========================================================================
    # Part 5. Primitive Decoding
    # ==========================================================================

    def decode_none(self, value: Any) -> None:
        """Decode None."""
        if value is not None and self._strict:
            raise TypeError("Expected None.")
        return None

    def decode_bool(self, value: Any) -> bool:
        """Decode bool."""
        if isinstance(value, bool):
            return value
        if self._strict:
            raise TypeError("Expected bool.")
        return bool(value)

    def decode_int(self, value: Any) -> int:
        """Decode int."""
        if isinstance(value, bool):
            if self._strict:
                raise TypeError("bool is not int.")
        try:
            return self._parse_int(value)
        except Exception as exc:
            raise ValueError(f"Cannot decode int: {value!r}") from exc

    def decode_float(self, value: Any) -> float:
        """Decode float."""
        try:
            return self._parse_float(value)
        except Exception as exc:
            raise ValueError(f"Cannot decode float: {value!r}") from exc

    def decode_str(self, value: Any) -> str:
        """Decode string."""
        if isinstance(value, str):
            return value
        if isinstance(value, bytes):
            return value.decode(self._encoding)
        if self._strict:
            raise TypeError("Expected str.")
        return str(value)

    def decode_bytes(self, value: Any) -> bytes:
        """Decode bytes."""
        if isinstance(value, bytes):
            return value
        if isinstance(value, str):
            return value.encode(self._encoding)
        if self._strict:
            raise TypeError("Expected bytes.")
        return bytes(value)

    # ==========================================================================
    # Part 6. Container Decoding
    # ==========================================================================

    def decode_list(self, value: Any) -> list[Any]:
        """Decode list."""
        if not isinstance(value, list):
            if self._strict:
                raise TypeError("Expected list.")
            value = list(value)
        return [self.decode(v) for v in value]

    def decode_tuple(self, value: Any) -> tuple[Any, ...]:
        """Decode tuple."""
        if isinstance(value, tuple):
            return tuple(self.decode(v) for v in value)
        if isinstance(value, list):
            return tuple(self.decode(v) for v in value)
        if self._strict:
            raise TypeError("Expected tuple/list.")
        return tuple(value)

    def decode_set(self, value: Any) -> set[Any]:
        """Decode set."""
        if isinstance(value, (set, list, tuple)):
            return {self.decode(v) for v in value}
        if self._strict:
            raise TypeError("Expected iterable.")
        return set(value)

    def decode_dict(self, value: Any) -> dict[str, Any]:
        """Decode dictionary."""
        if not isinstance(value, dict):
            if self._strict:
                raise TypeError("Expected dict.")
            value = dict(value)

        result: dict[str, Any] = {}
        for k, v in value.items():
            result[str(k)] = self.decode(v)

        if self._object_hook is not None:
            return self._object_hook(result)

        return result

    def decode_mapping(self, value: Mapping[str, Any]) -> dict[str, Any]:
        """Decode generic mapping."""
        return self.decode_dict(dict(value))

    # ==========================================================================
    # Part 7. Object Decoding
    # ==========================================================================

    def decode_dataclass(self, cls: type, value: Mapping[str, Any]) -> Any:
        """Decode dataclass."""
        return cls(**self.decode_dict(dict(value)))

    def decode_enum(self, cls: type, value: Any) -> Any:
        """Decode enum."""
        return cls(value)

    def decode_datetime(self, value: str):
        """Decode datetime."""
        from datetime import datetime

        return datetime.fromisoformat(value)

    def decode_path(self, value: str) -> Path:
        """Decode pathlib.Path."""
        return Path(value)

    def decode_object(self, value: Any) -> Any:
        """Decode arbitrary object."""
        if isinstance(value, dict):
            return self.decode_dict(value)
        if isinstance(value, list):
            return self.decode_list(value)
        return value

    # ==========================================================================
    # Part 8. Generic API
    # ==========================================================================

    def decode(self, value: Any) -> Any:
        """Generic decoder."""
        if value is None:
            return self.decode_none(value)
        if isinstance(value, bool):
            return self.decode_bool(value)
        if isinstance(value, int) and not isinstance(value, bool):
            return self.decode_int(value)
        if isinstance(value, float):
            return self.decode_float(value)
        if isinstance(value, str):
            return self.decode_str(value)
        if isinstance(value, bytes):
            return self.decode_bytes(value)
        if isinstance(value, list):
            return self.decode_list(value)
        if isinstance(value, tuple):
            return self.decode_tuple(value)
        if isinstance(value, set):
            return self.decode_set(value)
        if isinstance(value, Mapping):
            return self.decode_mapping(value)
        return self.decode_object(value)

    def loads(self, text: str) -> Any:
        """Decode JSON string."""
        obj = json.loads(
            text,
            object_hook=self._object_hook,
            parse_float=self._parse_float,
            parse_int=self._parse_int,
        )
        return self.decode(obj)

    def load(self, fp) -> Any:
        """Decode JSON file."""
        return self.loads(fp.read())

    def decode_many(self, values) -> list[Any]:
        """Decode many values."""
        return [self.decode(v) for v in values]

    def decode_metadata(self, metadata: MetadataType) -> dict[str, Any]:
        """Decode metadata mapping."""
        return self.decode_mapping(metadata)

    # ==========================================================================
    # Part 9. Validation
    # ==========================================================================

    def validate(self, value: Any) -> bool:
        """Validate decodable value."""
        try:
            self.decode(value)
            return True
        except Exception:
            return False

    def is_decodable(self, value: Any) -> bool:
        """Return True if value can be decoded."""
        return self.validate(value)

    # ==========================================================================
    # Part 10. Clone API
    # ==========================================================================

    def copy(self):
        """Shallow copy."""
        return copy.copy(self)

    def deepcopy(self):
        """Deep copy."""
        return copy.deepcopy(self)

    def clone(self):
        """Alias of deepcopy."""
        return self.deepcopy()

    # ==========================================================================
    # Part 11. Python Protocols
    # ==========================================================================

    def __call__(self, value: Any) -> Any:
        return self.decode(value)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"encoding={self._encoding!r}, "
            f"strict={self._strict!r})"
        )

    def __str__(self) -> str:
        return self.__repr__()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Decoder):
            return NotImplemented
        return (
            self.encoding == other.encoding
            and self.strict == other.strict
            and self.object_hook == other.object_hook
            and self.parse_float == other.parse_float
            and self.parse_int == other.parse_int
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.encoding,
                self.strict,
                self.object_hook,
                self.parse_float,
                self.parse_int,
            )
        )

    def __getstate__(self) -> dict[str, Any]:
        return {
            "encoding": self.encoding,
            "strict": self.strict,
            "object_hook": self.object_hook,
            "parse_float": self.parse_float,
            "parse_int": self.parse_int,
        }

    def __setstate__(self, state: dict[str, Any]) -> None:
        self.__init__(**state)

    # ==========================================================================
    # Part 12. Diagnostics
    # ==========================================================================

    def summary(self) -> dict[str, Any]:
        return {
            "encoding": self.encoding,
            "strict": self.strict,
        }

    def diagnostics(self) -> dict[str, Any]:
        return {
            "type": self.__class__.__name__,
            "summary": self.summary(),
            "hash": hash(self),
        }

    def decoder_report(self) -> dict[str, Any]:
        return {
            "decoder": self.summary(),
            "status": "ready",
        }

    def overall_status(self) -> str:
        return "ready"

# ==============================================================================
# Part 13. Public API
# ==============================================================================

__all__ = tuple(__all__)        
"""
JSON Codec
==========

Runtime JSON serialization codec.

Python 3.11+
"""

from __future__ import annotations

# ==============================================================================
# Part 1. Imports & Constants
# ==============================================================================

import copy
import json

from typing import Any
from typing import Mapping
from typing import Iterator


DEFAULT_ENCODING: str = "utf-8"
DEFAULT_INDENT: int | None = None
DEFAULT_SORT_KEYS: bool = False
DEFAULT_ENSURE_ASCII: bool = False


__all__ = [
    "DEFAULT_ENCODING",
    "DEFAULT_INDENT",
    "DEFAULT_SORT_KEYS",
    "DEFAULT_ENSURE_ASCII",
    "JsonCodec",
]


# ==============================================================================
# Part 2. Constructor
# ==============================================================================


class JsonCodec:
    """
    JSON serialization codec.
    """

    __slots__ = (
        "_encoding",
        "_indent",
        "_sort_keys",
        "_ensure_ascii",
        "_options",
    )

    __annotations__ = {
        "_encoding": str,
        "_indent": int | None,
        "_sort_keys": bool,
        "_ensure_ascii": bool,
        "_options": dict[str, Any],
    }

    def __init__(
        self,
        *,
        encoding: str = DEFAULT_ENCODING,
        indent: int | None = DEFAULT_INDENT,
        sort_keys: bool = DEFAULT_SORT_KEYS,
        ensure_ascii: bool = DEFAULT_ENSURE_ASCII,
        options: Mapping[str, Any] | None = None,
    ) -> None:

        self._encoding = encoding
        self._indent = indent
        self._sort_keys = sort_keys
        self._ensure_ascii = ensure_ascii
        self._options = dict(options or {})

    def configuration(self) -> dict[str, Any]:
        return {
            "encoding": self._encoding,
            "indent": self._indent,
            "sort_keys": self._sort_keys,
            "ensure_ascii": self._ensure_ascii,
            "options": dict(self._options),
        }

    def reset(self) -> None:
        self._encoding = DEFAULT_ENCODING
        self._indent = DEFAULT_INDENT
        self._sort_keys = DEFAULT_SORT_KEYS
        self._ensure_ascii = DEFAULT_ENSURE_ASCII
        self._options.clear()


# ==============================================================================
# Part 3. Properties
# ==============================================================================

    @property
    def encoding(self) -> str:
        return self._encoding

    @property
    def indent(self) -> int | None:
        return self._indent

    @property
    def sort_keys(self) -> bool:
        return self._sort_keys

    @property
    def ensure_ascii(self) -> bool:
        return self._ensure_ascii

    @property
    def options(self) -> dict[str, Any]:
        return self._options

    @property
    def config(self) -> dict[str, Any]:
        return self.configuration()

    @property
    def state(self) -> dict[str, Any]:
        return self.configuration()


# ==============================================================================
# Part 4. Encode
# ==============================================================================

    def encode(
        self,
        obj: Any,
    ) -> str:
        return self.dumps(obj)

    def encode_dict(
        self,
        mapping: Mapping[str, Any],
    ) -> str:
        return self.dumps(dict(mapping))

    def encode_object(
        self,
        obj: Any,
    ) -> str:

        if hasattr(obj, "__dict__"):
            obj = vars(obj)

        return self.dumps(obj)

    def encode_bytes(
        self,
        obj: Any,
    ) -> bytes:
        return self.dumps(obj).encode(self._encoding)

    def dumps(
        self,
        obj: Any,
    ) -> str:
        return json.dumps(
            obj,
            indent=self._indent,
            sort_keys=self._sort_keys,
            ensure_ascii=self._ensure_ascii,
            **self._options,
        )

    def snapshot(
        self,
    ) -> dict[str, Any]:

        return {
            "encoding": self._encoding,
            "indent": self._indent,
            "sort_keys": self._sort_keys,
            "ensure_ascii": self._ensure_ascii,
            "options": copy.deepcopy(self._options),
        }


# ==============================================================================
# Part 5. Decode
# ==============================================================================

    def decode(
        self,
        data: str,
    ) -> Any:
        return self.loads(data)

    def decode_dict(
        self,
        data: str,
    ) -> dict[str, Any]:
        return dict(self.loads(data))

    def decode_object(
        self,
        data: str,
    ) -> Any:
        return self.loads(data)

    def decode_bytes(
        self,
        data: bytes,
    ) -> Any:
        return self.loads(data.decode(self._encoding))

    def loads(
        self,
        data: str,
    ) -> Any:
        return json.loads(data)

    def restore(
        self,
        snapshot: Mapping[str, Any],
    ) -> "JsonCodec":

        self._encoding = snapshot["encoding"]
        self._indent = snapshot["indent"]
        self._sort_keys = snapshot["sort_keys"]
        self._ensure_ascii = snapshot["ensure_ascii"]
        self._options = copy.deepcopy(
            snapshot["options"]
        )

        return self

# ==============================================================================
# Part 6. Validation
# ==============================================================================

    @staticmethod
    def validate_json(data: str) -> str:
        if not isinstance(data, str):
            raise TypeError("JSON data must be a string.")

        json.loads(data)
        return data

    @staticmethod
    def validate_bytes(data: bytes) -> bytes:
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError("Data must be bytes.")
        return bytes(data)

    @staticmethod
    def validate_mapping(
        mapping: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        if not isinstance(mapping, Mapping):
            raise TypeError("Object must be a mapping.")
        return mapping

    @staticmethod
    def validate_encoding(
        encoding: str,
    ) -> str:
        if not isinstance(encoding, str):
            raise TypeError("Encoding must be a string.")

        if not encoding:
            raise ValueError("Encoding cannot be empty.")

        return encoding

    @staticmethod
    def validate_options(
        options: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        if not isinstance(options, Mapping):
            raise TypeError("Options must be a mapping.")
        return options

    def validate(self) -> bool:
        self.validate_encoding(self._encoding)
        self.validate_options(self._options)

        if self._indent is not None and not isinstance(self._indent, int):
            raise TypeError("Indent must be int or None.")

        if not isinstance(self._sort_keys, bool):
            raise TypeError("sort_keys must be bool.")

        if not isinstance(self._ensure_ascii, bool):
            raise TypeError("ensure_ascii must be bool.")

        return True


# ==============================================================================
# Part 7. Utilities
# ==============================================================================

    def copy(self) -> "JsonCodec":
        return type(self)(
            encoding=self._encoding,
            indent=self._indent,
            sort_keys=self._sort_keys,
            ensure_ascii=self._ensure_ascii,
            options=self._options.copy(),
        )

    def deepcopy(self) -> "JsonCodec":
        return copy.deepcopy(self)

    def clone(self) -> "JsonCodec":
        return self.deepcopy()

    def clear(self) -> None:
        self._options.clear()

    def update(
        self,
        options: Mapping[str, Any],
    ) -> None:
        self._options.update(options)

    def merge(
        self,
        other: Mapping[str, Any],
    ) -> "JsonCodec":

        for key, value in other.items():
            self._options[key] = copy.deepcopy(value)

        return self


# ==============================================================================
# Part 8. Protocols
# ==============================================================================

    def __contains__(self, key: str) -> bool:
        return key in self._options

    def __getitem__(self, key: str) -> Any:
        return self._options[key]

    def __setitem__(
        self,
        key: str,
        value: Any,
    ) -> None:
        self._options[key] = value

    def __delitem__(
        self,
        key: str,
    ) -> None:
        del self._options[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._options)

    def __len__(self) -> int:
        return len(self._options)

    def __bool__(self) -> bool:
        return bool(self._options)

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"encoding={self._encoding!r}, "
            f"indent={self._indent!r}, "
            f"sort_keys={self._sort_keys!r}, "
            f"ensure_ascii={self._ensure_ascii!r}, "
            f"options={len(self._options)})"
        )

    __str__ = __repr__

    def __eq__(
        self,
        other: object,
    ) -> bool:
        if not isinstance(other, JsonCodec):
            return NotImplemented

        return self.configuration() == other.configuration()

    def __hash__(self) -> int:
        return hash(
            (
                self._encoding,
                self._indent,
                self._sort_keys,
                self._ensure_ascii,
                tuple(sorted(self._options.items())),
            )
        )

    def __getstate__(self) -> dict[str, Any]:
        return self.configuration()

    def __setstate__(
        self,
        state: Mapping[str, Any],
    ) -> None:
        self.__init__(
            encoding=state["encoding"],
            indent=state["indent"],
            sort_keys=state["sort_keys"],
            ensure_ascii=state["ensure_ascii"],
            options=state["options"],
        )


# ==============================================================================
# Part 9. Diagnostics
# ==============================================================================

    def summary(self) -> dict[str, Any]:
        return {
            "encoding": self._encoding,
            "indent": self._indent,
            "sort_keys": self._sort_keys,
            "ensure_ascii": self._ensure_ascii,
            "options": len(self),
        }

    def diagnostics(self) -> dict[str, Any]:
        return {
            "status": self.overall_status(),
            "valid": self.validate(),
            "size": len(self),
            "summary": self.summary(),
        }

    def codec_report(self) -> dict[str, Any]:
        return {
            "codec": self.summary(),
            "options": list(self._options),
            "status": self.overall_status(),
        }

    def overall_status(self) -> str:
        return "ready"


# ==============================================================================
# Part 10. Public API
# ==============================================================================

__all__ = [
    "DEFAULT_ENCODING",
    "DEFAULT_INDENT",
    "DEFAULT_SORT_KEYS",
    "DEFAULT_ENSURE_ASCII",
    "JsonCodec",
]        
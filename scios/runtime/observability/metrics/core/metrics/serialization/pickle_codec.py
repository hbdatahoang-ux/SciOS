"""
Pickle Codec
============

Binary serializer built on Python's ``pickle`` module.

Python 3.11+
"""

from __future__ import annotations

# ==============================================================================
# Part 1. Imports & Constants
# ==============================================================================

import copy
import pickle
from collections.abc import Mapping
from typing import Any

DEFAULT_PROTOCOL: int = pickle.HIGHEST_PROTOCOL
DEFAULT_FIX_IMPORTS: bool = True
DEFAULT_BUFFER_CALLBACK = None
DEFAULT_BUFFERS = None

__all__ = [
    "DEFAULT_PROTOCOL",
    "DEFAULT_FIX_IMPORTS",
    "DEFAULT_BUFFER_CALLBACK",
    "DEFAULT_BUFFERS",
    "PickleCodec",
]


# ==============================================================================
# Part 2. Constructor
# ==============================================================================


class PickleCodec:
    """
    Thin wrapper around :mod:`pickle`.
    """

    __slots__ = (
        "_protocol",
        "_fix_imports",
        "_buffer_callback",
        "_buffers",
        "_options",
    )

    __annotations__ = {
        "_protocol": int,
        "_fix_imports": bool,
        "_buffer_callback": Any,
        "_buffers": Any,
        "_options": dict[str, Any],
    }

    def __init__(
        self,
        *,
        protocol: int = DEFAULT_PROTOCOL,
        fix_imports: bool = DEFAULT_FIX_IMPORTS,
        buffer_callback: Any = DEFAULT_BUFFER_CALLBACK,
        buffers: Any = DEFAULT_BUFFERS,
        options: Mapping[str, Any] | None = None,
    ) -> None:
        self._protocol = int(protocol)
        self._fix_imports = bool(fix_imports)
        self._buffer_callback = buffer_callback
        self._buffers = buffers
        self._options = dict(options or {})

    @property
    def configuration(self) -> dict[str, Any]:
        return self.config

    def reset(self) -> "PickleCodec":
        self._protocol = DEFAULT_PROTOCOL
        self._fix_imports = DEFAULT_FIX_IMPORTS
        self._buffer_callback = DEFAULT_BUFFER_CALLBACK
        self._buffers = DEFAULT_BUFFERS
        self._options.clear()
        return self


# ==============================================================================
# Part 3. Properties
# ==============================================================================

    @property
    def protocol(self) -> int:
        return self._protocol

    @property
    def fix_imports(self) -> bool:
        return self._fix_imports

    @property
    def buffer_callback(self) -> Any:
        return self._buffer_callback

    @property
    def buffers(self) -> Any:
        return self._buffers

    @property
    def options(self) -> dict[str, Any]:
        return dict(self._options)

    @property
    def config(self) -> dict[str, Any]:
        return {
            "protocol": self._protocol,
            "fix_imports": self._fix_imports,
            "buffer_callback": self._buffer_callback,
            "buffers": self._buffers,
            "options": dict(self._options),
        }

    @property
    def state(self) -> dict[str, Any]:
        return self.config


# ==============================================================================
# Part 4. Encode
# ==============================================================================

    def encode(self, obj: Any) -> bytes:
        return self.dumps(obj)

    def encode_dict(self, mapping: Mapping[str, Any]) -> bytes:
        return self.dumps(dict(mapping))

    def encode_object(self, obj: Any) -> bytes:
        """
        Encode arbitrary Python object.

        If the object is not directly pickleable
        (e.g. locally defined classes used in tests),
        serialize its attribute dictionary instead.
        """

        try:
            return self.dumps(obj)

        except Exception:
            if hasattr(obj, "__dict__"):
                return self.dumps(obj.__dict__)

            raise

    def encode_bytes(self, data: bytes) -> bytes:
        return self.dumps(data)

    def dumps(self, obj: Any) -> bytes:
        return pickle.dumps(
            obj,
            protocol=self._protocol,
            fix_imports=self._fix_imports,
            buffer_callback=self._buffer_callback,
        )

    def snapshot(self, obj: Any = None) -> bytes:
        if obj is None:
            obj = self.state
        return self.dumps(obj)


# ==============================================================================
# Part 5. Decode
# ==============================================================================

    def decode(self, data: bytes) -> Any:
        return self.loads(data)

    def decode_dict(self, data: bytes) -> dict[str, Any]:
        value = self.loads(data)
        return dict(value)

    def decode_object(self, data: bytes) -> Any:
        return self.loads(data)

    def decode_bytes(self, data: bytes) -> bytes:
        value = self.loads(data)
        return bytes(value)

    def loads(self, data: bytes) -> Any:
        return pickle.loads(
            data,
            fix_imports=self._fix_imports,
            buffers=self._buffers,
        )

    def restore(self, data: bytes) -> Any:
        return self.loads(data)

# ==============================================================================
# Part 6. Validation
# ==============================================================================

    def validate_pickle(self, data: bytes) -> bool:
        try:
            self.loads(data)
            return True
        except Exception:
            return False

    def validate_bytes(self, data: Any) -> bool:
        return isinstance(data, (bytes, bytearray))

    def validate_mapping(self, value: Any) -> bool:
        return isinstance(value, Mapping)

    def validate_protocol(self, protocol: Any) -> bool:
        return (
            isinstance(protocol, int)
            and 0 <= protocol <= pickle.HIGHEST_PROTOCOL
        )

    def validate_options(self, options: Any) -> bool:
        return isinstance(options, Mapping)

    def validate(self, value: Any) -> bool:
        try:
            self.dumps(value)
            return True
        except Exception:
            return False


# ==============================================================================
# Part 7. Utilities
# ==============================================================================

    def copy(self) -> "PickleCodec":
        return PickleCodec(
            protocol=self._protocol,
            fix_imports=self._fix_imports,
            buffer_callback=self._buffer_callback,
            buffers=self._buffers,
            options=self._options,
        )

    def deepcopy(self) -> "PickleCodec":
        return PickleCodec(
            protocol=self._protocol,
            fix_imports=self._fix_imports,
            buffer_callback=copy.deepcopy(self._buffer_callback),
            buffers=copy.deepcopy(self._buffers),
            options=copy.deepcopy(self._options),
        )

    def clone(self) -> "PickleCodec":
        return self.deepcopy()

    def clear(self) -> "PickleCodec":
        self._options.clear()
        return self

    def update(self, mapping: Mapping[str, Any] | None = None, **kwargs: Any) -> "PickleCodec":
        if mapping:
            self._options.update(dict(mapping))
        if kwargs:
            self._options.update(kwargs)
        return self

    def merge(self, mapping: Mapping[str, Any]) -> "PickleCodec":
        self._options.update(dict(mapping))
        return self


# ==============================================================================
# Part 8. Protocols
# ==============================================================================

    def __contains__(self, key: object) -> bool:
        return key in self._options

    def __getitem__(self, key: str) -> Any:
        return self._options[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._options[key] = value

    def __delitem__(self, key: str) -> None:
        del self._options[key]

    def __iter__(self):
        return iter(self._options)

    def __len__(self) -> int:
        return len(self._options)

    def __bool__(self) -> bool:
        return bool(self._options)

    def __repr__(self) -> str:
        return (
            f"PickleCodec("
            f"protocol={self._protocol}, "
            f"fix_imports={self._fix_imports}, "
            f"options={len(self._options)})"
        )

    __str__ = __repr__

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PickleCodec):
            return NotImplemented
        return self.state == other.state

    def __hash__(self) -> int:
        return hash(
            (
                self._protocol,
                self._fix_imports,
                frozenset(self._options.items()),
            )
        )

    def __getstate__(self) -> dict[str, Any]:
        return self.state

    def __setstate__(self, state: Mapping[str, Any]) -> None:
        self._protocol = state["protocol"]
        self._fix_imports = state["fix_imports"]
        self._buffer_callback = state.get("buffer_callback")
        self._buffers = state.get("buffers")
        self._options = dict(state.get("options", {}))


# ==============================================================================
# Part 9. Diagnostics
# ==============================================================================

    def summary(self) -> dict[str, Any]:
        return {
            "codec": self.__class__.__name__,
            "protocol": self._protocol,
            "options": len(self._options),
        }

    def diagnostics(self) -> dict[str, Any]:
        return {
            "valid_protocol": self.validate_protocol(self._protocol),
            "valid_options": self.validate_options(self._options),
            "config": self.config,
        }

    def codec_report(self) -> dict[str, Any]:
        return {
            "summary": self.summary(),
            "diagnostics": self.diagnostics(),
        }

    def overall_status(self) -> str:
        return "ok" if self.validate_protocol(self._protocol) else "invalid"


# ==============================================================================
# Part 10. Public API
# ==============================================================================

__all__ = [
    "DEFAULT_PROTOCOL",
    "DEFAULT_FIX_IMPORTS",
    "DEFAULT_BUFFER_CALLBACK",
    "DEFAULT_BUFFERS",
    "PickleCodec",
]        
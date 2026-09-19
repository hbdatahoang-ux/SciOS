"""
Snapshot serialization codec.

Python 3.11+
"""

from __future__ import annotations

import copy
import pickle
from typing import Any, Mapping

# ==============================================================================
# Part 1. Imports & Constants
# ==============================================================================

DEFAULT_ENCODING = "utf-8"

DEFAULT_PROTOCOL = pickle.HIGHEST_PROTOCOL

DEFAULT_COMPRESS = False


__all__ = [
    "SnapshotCodec",
    "DEFAULT_ENCODING",
    "DEFAULT_PROTOCOL",
    "DEFAULT_COMPRESS",
]


# ==============================================================================
# Part 2. Constructor
# ==============================================================================


class SnapshotCodec:
    """
    Generic snapshot codec.

    Encodes and decodes arbitrary runtime snapshots.
    """

    __slots__ = (
        "_encoding",
        "_protocol",
        "_compress",
        "_options",
    )

    __annotations__ = {
        "_encoding": str,
        "_protocol": int,
        "_compress": bool,
        "_options": dict[str, Any],
    }

    def __init__(
        self,
        *,
        encoding: str = DEFAULT_ENCODING,
        protocol: int = DEFAULT_PROTOCOL,
        compress: bool = DEFAULT_COMPRESS,
        options: Mapping[str, Any] | None = None,
    ) -> None:

        self._encoding = encoding
        self._protocol = protocol
        self._compress = compress

        self._options = dict(options or {})

    def configuration(self) -> dict[str, Any]:
        return {
            "encoding": self._encoding,
            "protocol": self._protocol,
            "compress": self._compress,
            "options": copy.deepcopy(self._options),
        }

    def reset(self) -> None:
        self._encoding = DEFAULT_ENCODING
        self._protocol = DEFAULT_PROTOCOL
        self._compress = DEFAULT_COMPRESS
        self._options.clear()

# ==============================================================================
# Part 3. Properties
# ==============================================================================

    @property
    def encoding(self) -> str:
        return self._encoding

    @property
    def protocol(self) -> int:
        return self._protocol

    @property
    def compress(self) -> bool:
        return self._compress

    @property
    def options(self) -> dict[str, Any]:
        return dict(self._options)

    @property
    def config(self) -> dict[str, Any]:
        return self.configuration()

    @property
    def state(self) -> dict[str, Any]:
        return self.snapshot()

# ==============================================================================
# Part 4. Encode
# ==============================================================================

    def encode(
        self,
        obj: Any,
    ) -> bytes:
        return pickle.dumps(
            obj,
            protocol=self._protocol,
        )

    def encode_dict(
        self,
        data: Mapping[str, Any],
    ) -> bytes:
        return self.encode(dict(data))

    def encode_object(
        self,
        obj: Any,
    ) -> bytes:
        return self.encode(obj)

    def encode_bytes(
        self,
        data: bytes,
    ) -> bytes:
        if not isinstance(data, bytes):
            raise TypeError("Expected bytes.")
        return data

    def dumps(
        self,
        obj: Any,
    ) -> bytes:
        return self.encode(obj)

    def snapshot(self):

        return {
            "encoding": self._encoding,
            "protocol": self._protocol,
            "compress": self._compress,
            "options": copy.deepcopy(self._options),
        }

# ==============================================================================
# Part 5. Decode
# ==============================================================================

    def decode(
        self,
        payload: bytes,
    ) -> Any:
        return pickle.loads(payload)

    def decode_dict(
        self,
        payload: bytes,
    ) -> dict[str, Any]:
        value = self.decode(payload)
        if not isinstance(value, dict):
            raise TypeError("Decoded object is not a dict.")
        return value

    def decode_object(
        self,
        payload: bytes,
    ) -> Any:
        return self.decode(payload)

    def decode_bytes(
        self,
        payload: bytes,
    ) -> bytes:
        if not isinstance(payload, bytes):
            raise TypeError("Expected bytes.")
        return payload

    def loads(
        self,
        payload: bytes,
    ) -> Any:
        return self.decode(payload)

    def restore(self, state):

        self._encoding = state["encoding"]
        self._protocol = state["protocol"]
        self._compress = state["compress"]

        self._options = copy.deepcopy(
            state["options"]
        )

# ==============================================================================
# Part 6. Validation
# ==============================================================================

    @staticmethod
    def validate_snapshot(snapshot: Mapping[str, Any]) -> Mapping[str, Any]:
        if not isinstance(snapshot, Mapping):
            raise TypeError("Snapshot must be a mapping.")
        return snapshot

    @staticmethod
    def validate_bytes(data: bytes | bytearray) -> bytes | bytearray:
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError("Data must be bytes.")
        return data

    @staticmethod
    def validate_mapping(mapping: Mapping[str, Any]) -> Mapping[str, Any]:
        if not isinstance(mapping, Mapping):
            raise TypeError("Mapping expected.")
        return mapping

    @staticmethod
    def validate_encoding(encoding: str) -> str:
        if not isinstance(encoding, str):
            raise TypeError("Encoding must be a string.")
        if not encoding:
            raise ValueError("Encoding cannot be empty.")
        return encoding

    @staticmethod
    def validate_protocol(protocol: int) -> int:
        if not isinstance(protocol, int):
            raise TypeError("Protocol must be an integer.")
        if protocol < 0:
            raise ValueError("Protocol must be >= 0.")
        return protocol

    def validate(self) -> bool:
        self.validate_encoding(self._encoding)
        self.validate_protocol(self._protocol)
        return True


# ==============================================================================
# Part 7. Utilities
# ==============================================================================

    def copy(self) -> "SnapshotCodec":
        return SnapshotCodec(
            encoding=self._encoding,
            protocol=self._protocol,
            compress=self._compress,
            options=self._options.copy(),
        )

    def deepcopy(self) -> "SnapshotCodec":
        return SnapshotCodec(
            encoding=self._encoding,
            protocol=self._protocol,
            compress=self._compress,
            options=copy.deepcopy(self._options),
        )

    def clone(self) -> "SnapshotCodec":
        return self.deepcopy()

    def clear(self) -> None:
        self._options.clear()

    def update(self, mapping: Mapping[str, Any]) -> None:
        self.validate_mapping(mapping)
        self._options.update(mapping)

    def merge(self, mapping: Mapping[str, Any]) -> "SnapshotCodec":
        self.update(mapping)
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
            f"{self.__class__.__name__}("
            f"encoding={self._encoding!r}, "
            f"protocol={self._protocol!r}, "
            f"compress={self._compress!r}, "
            f"options={len(self._options)!r})"
        )

    __str__ = __repr__

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SnapshotCodec):
            return NotImplemented

        return (
            self._encoding,
            self._protocol,
            self._compress,
            self._options,
        ) == (
            other._encoding,
            other._protocol,
            other._compress,
            other._options,
        )

    def __hash__(self) -> int:
        return hash(
            (
                self._encoding,
                self._protocol,
                self._compress,
            )
        )

    def __getstate__(self) -> dict[str, Any]:
        return self.snapshot()

    def __setstate__(self, state: Mapping[str, Any]) -> None:
        self.__init__(
            encoding=state["encoding"],
            protocol=state["protocol"],
            compress=state["compress"],
            options=state["options"],
        )


# ==============================================================================
# Part 9. Diagnostics
# ==============================================================================

    def summary(self) -> dict[str, Any]:
        return {
            "encoding": self._encoding,
            "protocol": self._protocol,
            "compress": self._compress,
            "options": len(self._options),
        }

    def diagnostics(self) -> dict[str, Any]:
        return {
            "valid": self.validate(),
            "summary": self.summary(),
            "status": self.overall_status(),
        }

    def codec_report(self) -> dict[str, Any]:
        return {
            "codec": self.summary(),
            "options": copy.deepcopy(self._options),
            "status": self.overall_status(),
        }

    def overall_status(self) -> str:
        return "ready" if self.validate() else "invalid"


# ==============================================================================
# Part 10. Public API
# ==============================================================================

__all__ = [
    "SnapshotCodec",
    "DEFAULT_ENCODING",
    "DEFAULT_PROTOCOL",
    "DEFAULT_COMPRESS",
]        
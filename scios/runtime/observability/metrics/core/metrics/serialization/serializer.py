"""
SciOS Metrics Serialization Serializer
======================================

High-level serializer built on Encoder + Decoder.

Python 3.11+
"""

from __future__ import annotations

# ==============================================================================
# Part 1. Imports & Constants
# ==============================================================================

from __future__ import annotations

import copy

from collections.abc import Mapping
from pathlib import Path
from typing import Any, BinaryIO, TextIO, TypeAlias

from .decoder import (
    DEFAULT_ENCODING,
    Decoder,
)
from .encoder import (
    DEFAULT_ASCII,
    DEFAULT_COMPACT,
    DEFAULT_INDENT,
    DEFAULT_SORT_KEYS,
    Encoder,
)

# ------------------------------------------------------------------------------
# Defaults
# ------------------------------------------------------------------------------

DEFAULT_STRICT: bool = True

# ------------------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------------------

__all__ = [
    # --------------------------------------------------------------------------
    # Defaults
    # --------------------------------------------------------------------------
    "DEFAULT_ENCODING",
    "DEFAULT_INDENT",
    "DEFAULT_SORT_KEYS",
    "DEFAULT_ASCII",
    "DEFAULT_COMPACT",
    "DEFAULT_STRICT",

    # --------------------------------------------------------------------------
    # Type Aliases
    # --------------------------------------------------------------------------
    "Serializable",
    "SerializedValue",
    "SerializerOptions",
    "MetadataType",

    # --------------------------------------------------------------------------
    # Main API
    # --------------------------------------------------------------------------
    "Serializer",
]

# ==============================================================================
# Part 2. Type Aliases
# ==============================================================================

Serializable: TypeAlias = Any

SerializedValue: TypeAlias = Any

SerializerOptions: TypeAlias = dict[str, Any]

MetadataType: TypeAlias = Mapping[str, Any]

# ==============================================================================
# Part 3. Constructor
# ==============================================================================


class Serializer:
    """
    High-level serialization façade.

    Combines Encoder + Decoder into one object.
    """

    __slots__ = (
        "_encoder",
        "_decoder",
        "_encoding",
        "_compact",
        "_strict",
    )

    __annotations__ = {
        "_encoder": Encoder,
        "_decoder": Decoder,
        "_encoding": str,
        "_compact": bool,
        "_strict": bool,
    }

    def __init__(
        self,
        *,
        encoding: str = DEFAULT_ENCODING,
        indent: int = DEFAULT_INDENT,
        sort_keys: bool = DEFAULT_SORT_KEYS,
        ensure_ascii: bool = DEFAULT_ASCII,
        compact: bool = DEFAULT_COMPACT,
        strict: bool = DEFAULT_STRICT,
    ) -> None:

        self._encoder = Encoder(
            indent=indent,
            sort_keys=sort_keys,
            ensure_ascii=ensure_ascii,
            encoding=encoding,
            compact=compact,
        )

        self._decoder = Decoder(
            encoding=encoding,
            strict=strict,
        )

        self._encoding = encoding
        self._compact = compact
        self._strict = strict

    # ==========================================================================
    # Part 4. Properties
    # ==========================================================================

    @property
    def encoder(self) -> Encoder:
        """Underlying encoder."""
        return self._encoder

    @property
    def decoder(self) -> Decoder:
        """Underlying decoder."""
        return self._decoder

    @property
    def encoding(self) -> str:
        """Current encoding."""
        return self._encoding

    @encoding.setter
    def encoding(self, value: str) -> None:
        value = str(value)

        self._encoding = value
        self._encoder.encoding = value
        self._decoder.encoding = value

    @property
    def compact(self) -> bool:
        """Compact encoding mode."""
        return self._compact

    @compact.setter
    def compact(self, value: bool) -> None:
        value = bool(value)

        self._compact = value
        self._encoder.compact = value

    @property
    def strict(self) -> bool:
        """Strict decoding mode."""
        return self._strict

    @strict.setter
    def strict(self, value: bool) -> None:
        value = bool(value)

        self._strict = value
        self._decoder.strict = value

    # ==========================================================================
    # Part 5. Encode API
    # ==========================================================================

    def encode(
        self,
        value: Serializable,
    ) -> SerializedValue:
        """Encode Python object."""
        return self._encoder.encode(value)

    def dumps(
        self,
        value: Serializable,
    ) -> str:
        """Serialize to JSON string."""
        return self._encoder.dumps(value)

    def dump(
        self,
        value: Serializable,
        fp: TextIO | BinaryIO,
    ) -> None:
        """Serialize to file object."""
        self._encoder.dump(value, fp)

    def encode_many(
        self,
        values: list[Serializable],
    ) -> list[SerializedValue]:
        """Encode multiple objects."""
        return self._encoder.encode_many(values)

    def encode_metadata(
        self,
        metadata: MetadataType,
    ) -> dict[str, Any]:
        """Encode metadata."""
        return self._encoder.encode_metadata(metadata)
    
    # ==========================================================================
    # Part 6. Decode API
    # ==========================================================================

    def decode(
        self,
        value: SerializedValue,
    ) -> Serializable:
        """Decode object."""
        return self._decoder.decode(value)

    def loads(
        self,
        text: str,
    ) -> Serializable:
        """Deserialize JSON string."""
        return self._decoder.loads(text)

    def load(
        self,
        fp: TextIO | BinaryIO,
    ) -> Serializable:
        """Deserialize from file object."""
        return self._decoder.load(fp)

    def decode_many(
        self,
        values: list[SerializedValue],
    ) -> list[Serializable]:
        """Decode multiple objects."""
        return self._decoder.decode_many(values)

    def decode_metadata(
        self,
        metadata: MetadataType,
    ) -> dict[str, Any]:
        """Decode metadata."""
        return self._decoder.decode_metadata(metadata)


    # ==========================================================================
    # Part 7. Roundtrip API
    # ==========================================================================

    def serialize(
        self,
        value: Serializable,
    ) -> str:
        """Serialize object."""
        return self.dumps(value)

    def deserialize(
        self,
        text: str,
    ) -> Serializable:
        """Deserialize object."""
        return self.loads(text)

    def roundtrip(
        self,
        value: Serializable,
    ) -> Serializable:
        """Serialize then deserialize."""
        return self.deserialize(self.serialize(value))

    def serialize_object(
        self,
        value: Serializable,
    ) -> str:
        """Serialize object alias."""
        return self.serialize(value)

    def deserialize_object(
        self,
        text: str,
    ) -> Serializable:
        """Deserialize object alias."""
        return self.deserialize(text)


    # ==========================================================================
    # Part 8. Generic API
    # ==========================================================================

    def save(
        self,
        value: Serializable,
        path: str | Path,
    ) -> Path:
        """Save JSON to file."""
        path = Path(path)

        with path.open("w", encoding=self.encoding) as fp:
            self.dump(value, fp)

        return path

    def restore(
        self,
        path: str | Path,
    ) -> Serializable:
        """Restore JSON from file."""
        path = Path(path)

        with path.open("r", encoding=self.encoding) as fp:
            return self.load(fp)

    def to_json(
        self,
        value: Serializable,
    ) -> str:
        """Convert object to JSON."""
        return self.dumps(value)

    def from_json(
        self,
        text: str,
    ) -> Serializable:
        """Convert JSON to object."""
        return self.loads(text)

    def convert(
        self,
        value: Any,
    ) -> Any:
        """
        Generic conversion.

        JSON string -> object
        Python object -> roundtrip object
        """
        if isinstance(value, str):
            return self.loads(value)

        return self.roundtrip(value)


    # ==========================================================================
    # Part 9. Validation
    # ==========================================================================

    def validate(
        self,
        value: Any,
    ) -> bool:
        """Validate serialization pipeline."""
        try:
            encoded = self.encode(value)
            self.decode(encoded)
            return True
        except Exception:
            return False

    def is_serializable(
        self,
        value: Any,
    ) -> bool:
        """Return True if object can be encoded."""
        try:
            self.encode(value)
            return True
        except Exception:
            return False

    def is_deserializable(
        self,
        value: Any,
    ) -> bool:
        """Return True if object can be decoded."""
        try:
            self.decode(value)
            return True
        except Exception:
            return False


    # ==========================================================================
    # Part 10. Clone API
    # ==========================================================================

    def copy(self) -> "Serializer":
        """Return shallow copy."""
        return Serializer(
            encoding=self.encoding,
            compact=self.compact,
            strict=self.strict,
        )

    def deepcopy(self) -> "Serializer":
        """Return deep copy."""
        return copy.deepcopy(self)

    def clone(self) -> "Serializer":
        """Clone serializer."""
        return self.copy()


    # ==========================================================================
    # Part 11. Python Protocols
    # ==========================================================================

    def __call__(
        self,
        value: Serializable,
    ) -> SerializedValue:
        return self.encode(value)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"encoding={self.encoding!r}, "
            f"compact={self.compact!r}, "
            f"strict={self.strict!r})"
        )

    def __str__(self) -> str:
        return self.__repr__()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Serializer):
            return False

        return (
            self.encoding,
            self.compact,
            self.strict,
        ) == (
            other.encoding,
            other.compact,
            other.strict,
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.encoding,
                self.compact,
                self.strict,
            )
        )

    def __getstate__(self) -> dict[str, Any]:
        return {
            "encoding": self.encoding,
            "compact": self.compact,
            "strict": self.strict,
        }

    def __setstate__(
        self,
        state: dict[str, Any],
    ) -> None:
        self.__init__(**state)


    # ==========================================================================
    # Part 12. Diagnostics
    # ==========================================================================

    def summary(self) -> dict[str, Any]:
        return {
            "type": self.__class__.__name__,
            "encoding": self.encoding,
            "compact": self.compact,
            "strict": self.strict,
        }

    def diagnostics(self) -> dict[str, Any]:
        """
        Return diagnostic information.
        """
        return {
            "type": self.__class__.__name__,
            "summary": self.summary(),
            "encoder": self.encoder.summary(),
            "decoder": self.decoder.summary(),
            "status": self.overall_status(),
            "hash": hash(self),
        }

    def serializer_report(self) -> dict[str, Any]:
        return {
            "serializer": self.summary(),
            "encoder": self.encoder.summary(),
            "decoder": self.decoder.summary(),
            "status": self.overall_status(),
        }

    def overall_status(self) -> str:
        return "ready" if self.validate({"status": "ok"}) else "error"


    # ==============================================================================
    # Part 13. Public API
    # ==============================================================================

    __all__ = tuple(__all__)
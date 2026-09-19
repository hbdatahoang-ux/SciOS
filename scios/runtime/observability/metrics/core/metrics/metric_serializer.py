"""
SciOS Observability
==================

Metric Serializer.

Serialization utilities for the SciOS Observability Metrics
subsystem.

Responsibilities
----------------
- Serialize runtime metrics
- Deserialize metrics
- Snapshot conversion
- Dictionary conversion
- JSON conversion
- Format normalization

This module contains no persistence logic.

Persistence belongs to storage/export layers.
"""

from __future__ import annotations

# ==========================================================
# Part 2 — Imports
# ==========================================================

import json

from collections.abc import Mapping
from typing import Any
from typing import Final
from typing import TypeAlias

from .metric import Metric
from .metric_snapshot import MetricSnapshot

# ==========================================================
# Part 3 — Public API
# ==========================================================

__all__ = [
    "SERIALIZER_VERSION",
    "DEFAULT_ENCODING",
    "DEFAULT_INDENT",
    "DEFAULT_SORT_KEYS",
    "DEFAULT_COMPACT",
    "SerializedObject",
    "SerializedDict",
    "SerializedJSON",
]

# ==========================================================
# Part 4 — Version / Constants / Type Aliases
# ==========================================================

SERIALIZER_VERSION: Final[str] = "1.0.0"

DEFAULT_ENCODING: Final[str] = "utf-8"

DEFAULT_INDENT: Final[int] = 2

DEFAULT_SORT_KEYS: Final[bool] = False

DEFAULT_COMPACT: Final[bool] = False

SerializedObject: TypeAlias = Metric | MetricSnapshot

SerializedDict: TypeAlias = dict[str, Any]

SerializedJSON: TypeAlias = str
# ==========================================================
# Part 5 — Runtime Enums
# ==========================================================

from enum import Enum
from enum import auto


class SerializerFormat(Enum):
    """
    Supported serialization formats.
    """

    DICT = auto()
    JSON = auto()


class SerializerMode(Enum):
    """
    Serialization strategy.
    """

    COMPACT = auto()
    PRETTY = auto()
    STRICT = auto()


# ==========================================================
# Part 6 — MetricSerializer
# ==========================================================

class MetricSerializer:
    """
    Runtime metric serializer.
    """

    # ------------------------------------------------------
    # Constructor
    # ------------------------------------------------------

    def __init__(
        self,
        *,
        fmt: SerializerFormat = SerializerFormat.DICT,
        mode: SerializerMode = SerializerMode.PRETTY,
        encoding: str = DEFAULT_ENCODING,
        indent: int = DEFAULT_INDENT,
        sort_keys: bool = DEFAULT_SORT_KEYS,
    ) -> None:

        self._format = fmt
        self._mode = mode
        self._encoding = encoding
        self._indent = indent
        self._sort_keys = sort_keys

        self._serialize_count = 0
        self._deserialize_count = 0

    # ------------------------------------------------------
    # Properties
    # ------------------------------------------------------

    @property
    def format(self) -> SerializerFormat:
        return self._format

    @property
    def mode(self) -> SerializerMode:
        return self._mode

    @property
    def encoding(self) -> str:
        return self._encoding

    @property
    def indent(self) -> int:
        return self._indent

    @property
    def sort_keys(self) -> bool:
        return self._sort_keys

    @property
    def serialize_count(self) -> int:
        return self._serialize_count

    @property
    def deserialize_count(self) -> int:
        return self._deserialize_count


# ==========================================================
# Part 7 — Serialization API
# ==========================================================

    def serialize(
        self,
        obj: SerializedObject,
    ) -> SerializedDict | SerializedJSON:
        """
        Serialize an object using the configured format.
        """

        self._serialize_count += 1

        if self._format is SerializerFormat.JSON:
            return self.to_json(obj)

        return self.to_dict(obj)

    def deserialize(
        self,
        data: SerializedDict | SerializedJSON,
    ) -> SerializedDict:
        """
        Deserialize serialized data.
        """

        self._deserialize_count += 1

        if isinstance(data, str):
            return self.from_json(data)

        return self.from_dict(data)

    def dumps(
        self,
        obj: SerializedObject,
    ) -> str:
        """
        Serialize to JSON string.
        """

        self._serialize_count += 1

        return json.dumps(
            self.to_dict(obj),
            indent=None if self._mode is SerializerMode.COMPACT else self._indent,
            sort_keys=self._sort_keys,
            ensure_ascii=False,
        )

    def loads(
        self,
        text: str,
    ) -> SerializedDict:
        """
        Deserialize JSON string.
        """

        self._deserialize_count += 1

        return json.loads(text)
# ==========================================================
# Part 8 — Dictionary API
# ==========================================================

    def to_dict(
        self,
        obj: SerializedObject,
    ) -> SerializedDict:
        """
        Convert a metric or snapshot into a normalized dictionary.
        """

        if hasattr(obj, "to_dict"):
            return self.normalize(obj.to_dict())

        if isinstance(obj, Mapping):
            return self.normalize(dict(obj))

        raise TypeError(
            f"Unsupported object type: {type(obj).__name__}"
        )

    def from_dict(
        self,
        data: Mapping[str, Any],
    ) -> SerializedDict:
        """
        Normalize an input mapping.
        """

        return self.normalize(dict(data))

    def normalize(
        self,
        data: Mapping[str, Any],
    ) -> SerializedDict:
        """
        Normalize nested structures into JSON-safe objects.
        """

        def _normalize(value: Any) -> Any:

            if isinstance(value, Mapping):
                return {
                    str(k): _normalize(v)
                    for k, v in value.items()
                }

            if isinstance(value, (list, tuple, set)):
                return [
                    _normalize(v)
                    for v in value
                ]

            if hasattr(value, "isoformat"):
                try:
                    return value.isoformat()
                except Exception:
                    pass

            if hasattr(value, "name"):
                try:
                    return value.name
                except Exception:
                    pass

            return value

        return {
            str(k): _normalize(v)
            for k, v in data.items()
        }


# ==========================================================
# Part 9 — JSON API
# ==========================================================

    def to_json(
        self,
        obj: SerializedObject,
    ) -> SerializedJSON:
        """
        Serialize to JSON.
        """

        return json.dumps(
            self.to_dict(obj),
            ensure_ascii=False,
            sort_keys=self._sort_keys,
            indent=(
                None
                if self._mode is SerializerMode.COMPACT
                else self._indent
            ),
        )

    def from_json(
        self,
        text: SerializedJSON,
    ) -> SerializedDict:
        """
        Deserialize JSON.
        """

        return self.normalize(
            json.loads(text)
        )


# ==========================================================
# Part 10 — Snapshot API
# ==========================================================

    def snapshot(self) -> SerializedDict:
        """
        Serializer runtime snapshot.
        """

        return {
            "format": self._format.name,
            "mode": self._mode.name,
            "encoding": self._encoding,
            "indent": self._indent,
            "sort_keys": self._sort_keys,
            "serialize_count": self._serialize_count,
            "deserialize_count": self._deserialize_count,
        }

    def restore(
        self,
        snapshot: Mapping[str, Any],
    ) -> None:
        """
        Restore serializer runtime state.
        """

        self._format = SerializerFormat[
            snapshot["format"]
        ]

        self._mode = SerializerMode[
            snapshot["mode"]
        ]

        self._encoding = snapshot["encoding"]

        self._indent = snapshot["indent"]

        self._sort_keys = snapshot["sort_keys"]

        self._serialize_count = snapshot[
            "serialize_count"
        ]

        self._deserialize_count = snapshot[
            "deserialize_count"
        ]
# ==========================================================
# Part 11 — Statistics
# ==========================================================

    def serialize_count(self) -> int:
        """
        Total serialization operations.
        """
        return self._serialize_count

    def deserialize_count(self) -> int:
        """
        Total deserialization operations.
        """
        return self._deserialize_count

    def summary(self) -> SerializedDict:
        """
        Serializer summary.
        """
        return {
            "format": self._format.name,
            "mode": self._mode.name,
            "encoding": self._encoding,
            "serialize_count": self._serialize_count,
            "deserialize_count": self._deserialize_count,
        }

    def diagnostics(self) -> SerializedDict:
        """
        Detailed runtime diagnostics.
        """
        return {
            **self.summary(),
            "indent": self._indent,
            "sort_keys": self._sort_keys,
            "version": SERIALIZER_VERSION,
        }


# ==========================================================
# Part 12 — Validation
# ==========================================================

    def validate(self) -> None:
        """
        Validate serializer configuration.
        """

        if not isinstance(
            self._format,
            SerializerFormat,
        ):
            raise TypeError(
                "Invalid serializer format."
            )

        if not isinstance(
            self._mode,
            SerializerMode,
        ):
            raise TypeError(
                "Invalid serializer mode."
            )

        if not isinstance(
            self._encoding,
            str,
        ):
            raise TypeError(
                "Encoding must be a string."
            )

        if not isinstance(
            self._indent,
            int,
        ):
            raise TypeError(
                "Indent must be an integer."
            )

        if self._indent < 0:
            raise ValueError(
                "Indent cannot be negative."
            )

        if not isinstance(
            self._sort_keys,
            bool,
        ):
            raise TypeError(
                "sort_keys must be bool."
            )

        if self._serialize_count < 0:
            raise ValueError(
                "serialize_count cannot be negative."
            )

        if self._deserialize_count < 0:
            raise ValueError(
                "deserialize_count cannot be negative."
            )

    def is_valid(self) -> bool:
        """
        Safe validation.
        """

        try:
            self.validate()
            return True
        except Exception:
            return False
# ==========================================================
# Part 13 — Python Protocols
# ==========================================================

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"format={self._format.name!r}, "
            f"mode={self._mode.name!r}, "
            f"encoding={self._encoding!r}, "
            f"serialize_count={self._serialize_count}, "
            f"deserialize_count={self._deserialize_count})"
        )

    def __str__(self) -> str:

        return (
            f"{self._format.name.lower()} "
            f"serializer "
            f"({self._mode.name.lower()})"
        )


# ==========================================================
# Part 14 — Final cleanup
# ==========================================================

__all__ = [
    "SERIALIZER_VERSION",
    "DEFAULT_ENCODING",
    "DEFAULT_INDENT",
    "DEFAULT_SORT_KEYS",
    "DEFAULT_COMPACT",
    "SerializedObject",
    "SerializedDict",
    "SerializedJSON",
    "SerializerFormat",
    "SerializerMode",
    "MetricSerializer",
]

# ==========================================================
# End of File
# ==========================================================                            
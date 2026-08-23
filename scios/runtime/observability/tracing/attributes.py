"""
SciOS Runtime Observability
===========================

Structured attribute container used throughout the tracing subsystem.

Python 3.11+
"""

from __future__ import annotations

import json

from copy import deepcopy
from typing import Any, TypeAlias


# ==============================================================================
# Constants & Type Aliases
# ==============================================================================

DEFAULT_ATTRIBUTES: dict[str, Any] = {}

ATTRIBUTES_VERSION = "1.0.0"

ATTRIBUTES_API_VERSION = "1"

AttributeMap: TypeAlias = dict[str, Any]

AttributeJSON: TypeAlias = dict[str, Any]


# ==============================================================================
# Exceptions
# ==============================================================================


class AttributesError(Exception):
    """Base exception for Attributes operations."""


class AttributeValidationError(AttributesError):
    """Raised when attribute validation fails."""


class AttributeSerializationError(AttributesError):
    """Raised when attribute serialization fails."""


# ==============================================================================
# Attributes
# ==============================================================================


class Attributes:
    """
    Canonical structured attribute container.

    Used by tracing entities such as Trace, Span, Event and Link.
    """

    __slots__ = ("_data",)

    def __init__(
        self,
        initial: AttributeMap | None = None,
    ) -> None:
        self._data: AttributeMap = {}

        if initial is not None:
            if not isinstance(initial, dict):
                raise TypeError(
                    "initial must be a dictionary."
                )

            self._validate_mapping(initial)

            self._data.update(
                deepcopy(initial)
            )

    # ==========================================================================
    # Properties
    # ==========================================================================

    @property
    def data(self) -> AttributeMap:
        """Return a deep copy of the attributes."""
        return deepcopy(self._data)

    @property
    def empty(self) -> bool:
        """Return True when no attributes exist."""
        return not self._data

    @property
    def size(self) -> int:
        """Return the number of attributes."""
        return len(self._data)

    def count(self) -> int:
        """Return the number of attributes."""
        return len(self._data)

    def keys(self):
        """Return attribute keys."""
        return self._data.keys()

    def values(self):
        """Return attribute values."""
        return self._data.values()

    def items(self):
        """Return attribute items."""
        return self._data.items()

    # ==========================================================================
    # Mutation
    # ==========================================================================

    def set(
        self,
        key: str,
        value: Any,
    ) -> Attributes:
        """Set or replace an attribute."""
        key = self._validate_key(key)

        self._data[key] = value

        return self

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """Return an attribute or a default value."""
        key = self._validate_key(key)

        return self._data.get(
            key,
            default,
        )

    def get_or_set(
        self,
        key: str,
        default: Any,
    ) -> Any:
        """Return an existing value or create the default."""
        key = self._validate_key(key)

        return self._data.setdefault(
            key,
            default,
        )

    def exists(
        self,
        key: str,
    ) -> bool:
        """Return True when an attribute exists."""
        key = self._validate_key(key)

        return key in self._data

    def remove(
        self,
        key: str,
    ) -> Any:
        """Remove and return an attribute."""
        key = self._validate_key(key)

        return self._data.pop(key)

    def pop(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """Remove and return an attribute or default."""
        key = self._validate_key(key)

        return self._data.pop(
            key,
            default,
        )

    def clear(self) -> Attributes:
        """Remove all attributes."""
        self._data.clear()

        return self

    def update(
        self,
        other: AttributeMap | Attributes,
    ) -> Attributes:
        """Update attributes from another Attributes or dict."""
        mapping = self._coerce_mapping(other)

        self._validate_mapping(mapping)

        for key, value in mapping.items():
            self._data[key] = deepcopy(value)

        return self

    def merge(
        self,
        other: AttributeMap | Attributes,
        *,
        overwrite: bool = False,
    ) -> Attributes:
        """
        Merge attributes.

        By default existing values are preserved.
        """

        mapping = self._coerce_mapping(other)

        self._validate_mapping(mapping)

        for key, value in mapping.items():
            if overwrite or key not in self._data:
                self._data[key] = deepcopy(value)

        return self

    # ==========================================================================
    # Validation
    # ==========================================================================

    @staticmethod
    def _validate_key(key: Any) -> str:
        """Validate and normalize an attribute key."""

        if not isinstance(key, str):
            raise AttributeValidationError(
                "Attribute key must be string."
            )

        key = key.strip()

        if not key:
            raise AttributeValidationError(
                "Attribute key cannot be empty."
            )

        return key

    @classmethod
    def _validate_mapping(
        cls,
        mapping: AttributeMap,
    ) -> None:
        """Validate an attribute mapping."""

        if not isinstance(mapping, dict):
            raise AttributeValidationError(
                "Attributes must be dictionary."
            )

        for key in mapping:
            cls._validate_key(key)

    @staticmethod
    def _coerce_mapping(
        other: AttributeMap | Attributes,
    ) -> AttributeMap:
        """Convert a supported input into a mapping."""

        if isinstance(other, Attributes):
            return other._data

        if isinstance(other, dict):
            return other

        raise TypeError(
            "Expected dict or Attributes."
        )

    def validate(self) -> bool:
        """Validate the current container state."""

        self._validate_mapping(
            self._data
        )

        return True

    # ==========================================================================
    # Serialization
    # ==========================================================================

    def to_dict(self) -> AttributeMap:
        """Return a deep dictionary representation."""
        return deepcopy(self._data)

    @classmethod
    def from_dict(
        cls,
        data: AttributeMap,
    ) -> Attributes:
        """Create an Attributes instance from a dictionary."""

        cls._validate_mapping(data)

        return cls(
            deepcopy(data)
        )

    def to_json(
        self,
        *,
        indent: int | None = 4,
        sort_keys: bool = True,
        ensure_ascii: bool = False,
    ) -> str:
        """Serialize attributes to JSON."""

        try:
            return json.dumps(
                self._data,
                indent=indent,
                sort_keys=sort_keys,
                ensure_ascii=ensure_ascii,
                default=str,
            )

        except Exception as exc:
            raise AttributeSerializationError(
                "Failed to serialize Attributes."
            ) from exc

    @classmethod
    def from_json(
        cls,
        value: str,
    ) -> Attributes:
        """Create Attributes from JSON."""

        if not isinstance(value, str):
            raise AttributeSerializationError(
                "JSON value must be a string."
            )

        try:
            data = json.loads(value)

        except Exception as exc:
            raise AttributeSerializationError(
                "Invalid JSON."
            ) from exc

        if not isinstance(data, dict):
            raise AttributeSerializationError(
                "JSON must decode to dictionary."
            )

        return cls.from_dict(data)

    # ==========================================================================
    # Snapshot / Restore
    # ==========================================================================

    def snapshot(self) -> AttributeJSON:
        """Return an independent snapshot."""
        return deepcopy(self._data)

    @classmethod
    def restore(
        cls,
        snapshot: AttributeJSON,
    ) -> Attributes:
        """Restore Attributes from a snapshot."""

        cls._validate_mapping(snapshot)

        return cls(
            deepcopy(snapshot)
        )

    # ==========================================================================
    # Copy / Clone
    # ==========================================================================

    def copy(self) -> Attributes:
        """Return an independent copy."""
        return self.__class__.restore(
            self.snapshot()
        )

    def clone(self) -> Attributes:
        """Return an independent clone."""
        return self.copy()

    def __copy__(self) -> Attributes:
        """Support copy.copy()."""
        return self.copy()

    def __deepcopy__(
        self,
        memo: dict[int, Any],
    ) -> Attributes:
        """Support copy.deepcopy()."""

        if id(self) in memo:
            return memo[id(self)]

        result = self.__class__()

        memo[id(self)] = result

        result._data = deepcopy(
            self._data,
            memo,
        )

        return result

    # ==========================================================================
    # Diagnostics
    # ==========================================================================

    def diagnostics(self) -> dict[str, Any]:
        """Return detailed diagnostic information."""

        return {
            "valid": self.validate(),
            "version": ATTRIBUTES_VERSION,
            "api_version": ATTRIBUTES_API_VERSION,
            "count": self.count(),
            "size": self.size,
            "empty": self.empty,
            "keys": list(self._data.keys()),
            "types": {
                key: type(value).__name__
                for key, value in self._data.items()
            },
        }

    def summary(self) -> dict[str, Any]:
        """Return compact diagnostic information."""

        return {
            "valid": self.validate(),
            "count": self.count(),
            "size": self.size,
            "empty": self.empty,
            "keys": list(self._data.keys()),
        }

    # ==========================================================================
    # Python Protocols
    # ==========================================================================

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"({self._data!r})"
        )

    def __str__(self) -> str:
        return (
            f"Attributes("
            f"count={self.count()}, "
            f"empty={self.empty}, "
            f"valid={self.validate()}"
            f")"
        )

    def __len__(self) -> int:
        return self.count()

    def __iter__(self):
        return iter(self._data)

    def __contains__(
        self,
        key: object,
    ) -> bool:
        return key in self._data

    def __getitem__(
        self,
        key: str,
    ) -> Any:
        key = self._validate_key(key)

        return self._data[key]

    def __setitem__(
        self,
        key: str,
        value: Any,
    ) -> None:
        self.set(
            key,
            value,
        )

    def __delitem__(
        self,
        key: str,
    ) -> None:
        self.remove(key)

    def __bool__(self) -> bool:
        return not self.empty

    def __eq__(
        self,
        other: object,
    ) -> bool:
        if not isinstance(
            other,
            Attributes,
        ):
            return NotImplemented

        return self._data == other._data

    def __hash__(self) -> int:
        return hash(
            json.dumps(
                self._data,
                default=str,
                sort_keys=True,
                ensure_ascii=False,
            )
        )


# ==============================================================================
# Public API
# ==============================================================================

__all__ = [
    "DEFAULT_ATTRIBUTES",
    "ATTRIBUTES_VERSION",
    "ATTRIBUTES_API_VERSION",
    "AttributeMap",
    "AttributeJSON",
    "AttributesError",
    "AttributeValidationError",
    "AttributeSerializationError",
    "Attributes",
]

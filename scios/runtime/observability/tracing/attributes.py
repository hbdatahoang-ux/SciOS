"""
SciOS Observability - Trace Attributes
======================================

Structured attribute container used by Trace, Span and Event.

Responsibilities
----------------
- Store structured attributes
- Type-safe validation
- Bulk operations
- Serialization
- Snapshot / Restore
- Diagnostics
- Python container protocol
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from collections.abc import Iterator
from copy import deepcopy
from typing import Any

__all__ = [
    "Attributes",
]


class Attributes:
    """
    Structured attribute container.

    This class is the canonical attribute storage used throughout the
    SciOS Observability subsystem.

    Used by
    -------
    - Trace
    - Span
    - Event

    Notes
    -----
    Keys must always be non-empty strings.

    Values may be any JSON-serializable Python object, although arbitrary
    Python objects are also accepted internally.
    """

    # ==========================================================
    # Constructor
    # ==========================================================

    def __init__(
        self,
        initial: dict[str, Any] | None = None,
    ) -> None:
        """
        Create a new attribute container.

        Parameters
        ----------
        initial:
            Optional initial mapping.
        """

        self._data: dict[str, Any] = {}

        if initial is not None:
            self.update(initial)

    # ==========================================================
    # Internal State
    # ==========================================================

    @property
    def data(self) -> dict[str, Any]:
        """
        Return a deep copy of internal storage.
        """

        return deepcopy(self._data)

    @property
    def empty(self) -> bool:
        """
        True if no attributes exist.
        """

        return len(self._data) == 0

    @property
    def size(self) -> int:
        """
        Number of stored attributes.
        """

        return len(self._data)

    # ==========================================================
    # Validation Helpers
    # ==========================================================

    @staticmethod
    def _validate_key(
        key: Any,
    ) -> str:
        """
        Validate an attribute key.

        Returns
        -------
        str
            Validated key.

        Raises
        ------
        TypeError
            If key is not a string.

        ValueError
            If key is empty.
        """

        if key is None:
            raise ValueError(
                "Attribute key cannot be None."
            )

        if not isinstance(
            key,
            str,
        ):
            raise TypeError(
                "Attribute key must be a string."
            )

        key = key.strip()

        if not key:
            raise ValueError(
                "Attribute key cannot be empty."
            )

        return key

    @staticmethod
    def _validate_mapping(
        mapping: dict[str, Any],
    ) -> None:
        """
        Validate an attribute mapping.
        """

        if not isinstance(
            mapping,
            dict,
        ):
            raise TypeError(
                "Expected a dictionary."
            )

        for key in mapping:
            Attributes._validate_key(key)

    @staticmethod
    def _deep_copy(
        value: Any,
    ) -> Any:
        """
        Safely deep-copy an object.
        """

        return deepcopy(value)

    @staticmethod
    def _json_default(
        value: Any,
    ) -> Any:
        """
        JSON serializer fallback.

        Non-serializable objects are converted using ``str()``.
        """

        try:
            json.dumps(value)
            return value
        except TypeError:
            return str(value)
    # ==========================================================
    # Part 2 - Basic Operations
    # ==========================================================

    def set(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Set or replace an attribute.

        Parameters
        ----------
        key:
            Attribute name.

        value:
            Attribute value.

        Raises
        ------
        TypeError
            If the key is not a string.

        ValueError
            If the key is empty or None.
        """

        key = self._validate_key(key)

        self._data[key] = value

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve an attribute.

        Parameters
        ----------
        key:
            Attribute name.

        default:
            Value returned when the key does not exist.

        Returns
        -------
        Any
            Stored value or default.
        """

        key = self._validate_key(key)

        return self._data.get(
            key,
            default,
        )

    def remove(
        self,
        key: str,
    ) -> Any:
        """
        Remove an attribute.

        Parameters
        ----------
        key:
            Attribute name.

        Returns
        -------
        Any
            Removed value.

        Raises
        ------
        KeyError
            If the key does not exist.
        """

        key = self._validate_key(key)

        return self._data.pop(key)

    def clear(
        self,
    ) -> None:
        """
        Remove every attribute.
        """

        self._data.clear()

    def count(
        self,
    ) -> int:
        """
        Return the number of stored attributes.

        Returns
        -------
        int
            Attribute count.
        """

        return len(self._data)

    def validate(
        self,
    ) -> bool:
        """
        Validate the current attribute container.

        Validation Rules
        ----------------
        - every key is a non-empty string
        - internal storage is a dictionary

        Returns
        -------
        bool
            True if valid.

        Raises
        ------
        TypeError
            If internal storage is corrupted.
        """

        if not isinstance(
            self._data,
            dict,
        ):
            raise TypeError(
                "Internal attribute storage must be a dictionary."
            )

        for key in self._data.keys():
            self._validate_key(key)

        return True
    # ==========================================================
    # Part 3 - Bulk Operations
    # ==========================================================

    def update(
        self,
        other: dict[str, Any] | "Attributes",
    ) -> "Attributes":
        """
        Update attributes from another mapping or Attributes object.

        Existing keys are overwritten.

        Parameters
        ----------
        other:
            Source attributes.

        Returns
        -------
        Attributes
            Self (for method chaining).

        Raises
        ------
        TypeError
            If the input type is unsupported.
        """

        if isinstance(other, Attributes):
            mapping = other._data

        elif isinstance(other, dict):
            mapping = other

        else:
            raise TypeError(
                "update() expects a dict or Attributes instance."
            )

        self._validate_mapping(mapping)

        for key, value in mapping.items():
            self._data[key] = deepcopy(value)

        return self

    def merge(
        self,
        other: dict[str, Any] | "Attributes",
        *,
        overwrite: bool = False,
    ) -> "Attributes":
        """
        Merge another mapping into this container.

        Unlike update(), merge() preserves existing values by default.

        Parameters
        ----------
        other:
            Source mapping.

        overwrite:
            Replace existing keys if True.

        Returns
        -------
        Attributes
            Self.
        """

        if isinstance(other, Attributes):
            mapping = other._data

        elif isinstance(other, dict):
            mapping = other

        else:
            raise TypeError(
                "merge() expects a dict or Attributes instance."
            )

        self._validate_mapping(mapping)

        for key, value in mapping.items():

            if overwrite or key not in self._data:
                self._data[key] = deepcopy(value)

        return self

    def copy(
        self,
    ) -> "Attributes":
        """
        Create a deep copy.

        Returns
        -------
        Attributes
            Independent copy.
        """

        return Attributes(
            deepcopy(self._data)
        )

    def clone(
        self,
    ) -> "Attributes":
        """
        Clone this attribute container.

        Alias of copy().

        Returns
        -------
        Attributes
            Independent clone.
        """

        return self.copy()
    # ==========================================================
    # Part 4 - Serialization
    # ==========================================================

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Export attributes as a deep-copied dictionary.

        Returns
        -------
        dict[str, Any]
            Independent dictionary representation.
        """

        return deepcopy(self._data)

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "Attributes":
        """
        Create an Attributes instance from a dictionary.

        Parameters
        ----------
        data:
            Source dictionary.

        Returns
        -------
        Attributes
            New attribute container.
        """

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
        """
        Serialize attributes to JSON.

        Parameters
        ----------
        indent:
            JSON indentation.

        sort_keys:
            Sort keys alphabetically.

        ensure_ascii:
            Escape non-ASCII characters.

        Returns
        -------
        str
            JSON string.
        """

        return json.dumps(
            self._data,
            default=self._json_default,
            indent=indent,
            sort_keys=sort_keys,
            ensure_ascii=ensure_ascii,
        )

    @classmethod
    def from_json(
        cls,
        value: str,
    ) -> "Attributes":
        """
        Construct an Attributes object from JSON.

        Parameters
        ----------
        value:
            JSON string.

        Returns
        -------
        Attributes
            New attribute container.

        Raises
        ------
        TypeError
            If the decoded JSON is not a dictionary.
        """

        data = json.loads(value)

        if not isinstance(
            data,
            dict,
        ):
            raise TypeError(
                "JSON must decode to a dictionary."
            )

        return cls.from_dict(data)

    def snapshot(
        self,
    ) -> dict[str, Any]:
        """
        Create a snapshot of the current attributes.

        Returns
        -------
        dict[str, Any]
            Deep-copied snapshot.
        """

        return deepcopy(self._data)

    @classmethod
    def restore(
        cls,
        snapshot: dict[str, Any],
    ) -> "Attributes":
        """
        Restore an Attributes instance from a snapshot.

        Parameters
        ----------
        snapshot:
            Snapshot previously returned by ``snapshot()``.

        Returns
        -------
        Attributes
            Restored attribute container.
        """

        cls._validate_mapping(snapshot)

        return cls(
            deepcopy(snapshot)
        )
    # ==========================================================
    # Part 5 - Diagnostics
    # ==========================================================

    def diagnostics(
        self,
    ) -> dict[str, Any]:
        """
        Return diagnostic information for this attribute container.

        The returned information is intended for debugging,
        monitoring and observability.

        Returns
        -------
        dict[str, Any]
            Diagnostic information.
        """

        value_types: dict[str, str] = {
            key: type(value).__name__
            for key, value in self._data.items()
        }

        return {
            "valid": self.validate(),
            "count": self.count(),
            "empty": self.empty,
            "size": self.size,
            "keys": list(self._data.keys()),
            "types": value_types,
        }

    def summary(
        self,
    ) -> dict[str, Any]:
        """
        Return a concise summary of the attribute container.

        Returns
        -------
        dict[str, Any]
            Summary information.
        """

        return {
            "count": self.count(),
            "empty": self.empty,
            "valid": self.validate(),
            "size": self.size,
            "keys": list(self._data.keys()),
        }
    # ==========================================================
    # Part 6 - Python Protocols
    # ==========================================================

    def __repr__(
        self,
    ) -> str:
        """
        Official string representation.
        """

        return (
            f"{self.__class__.__name__}"
            f"({self._data!r})"
        )

    def __str__(
        self,
    ) -> str:
        """
        Human-readable representation.
        """

        return (
            f"Attributes("
            f"count={self.count()}, "
            f"empty={self.empty}, "
            f"valid={self.validate()}"
            f")"
        )

    def __len__(
        self,
    ) -> int:
        """
        Return the number of stored attributes.
        """

        return self.count()

    def __iter__(
        self,
    ) -> Iterator[str]:
        """
        Iterate over attribute keys.
        """

        return iter(self._data)

    def __contains__(
        self,
        key: object,
    ) -> bool:
        """
        Return True if the key exists.
        """

        return key in self._data

    def __getitem__(
        self,
        key: str,
    ) -> Any:
        """
        Dictionary-style lookup.
        """

        key = self._validate_key(key)

        return self._data[key]

    def __setitem__(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Dictionary-style assignment.
        """

        self.set(
            key,
            value,
        )

    def __delitem__(
        self,
        key: str,
    ) -> None:
        """
        Dictionary-style deletion.
        """

        self.remove(key)

    def __bool__(
        self,
    ) -> bool:
        """
        Truthiness.

        Empty container -> False.
        """

        return not self.empty

    def __eq__(
        self,
        other: object,
    ) -> bool:
        """
        Equality comparison.
        """

        if not isinstance(
            other,
            Attributes,
        ):
            return NotImplemented

        return self._data == other._data

    def __hash__(
        self,
    ) -> int:
        """
        Hash value.

        Uses a deterministic JSON representation.
        """

        return hash(
            json.dumps(
                self._data,
                default=self._json_default,
                sort_keys=True,
                ensure_ascii=False,
            )
        )

    def __copy__(
        self,
    ) -> "Attributes":
        """
        Support copy.copy().
        """

        return self.copy()

    def __deepcopy__(
        self,
        memo: dict[int, Any],
    ) -> "Attributes":
        """
        Support copy.deepcopy().
        """

        obj = self.__class__()

        memo[id(self)] = obj

        obj._data = deepcopy(
            self._data,
            memo,
        )

        return obj
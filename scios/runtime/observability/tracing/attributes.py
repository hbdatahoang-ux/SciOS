"""
SciOS Runtime Observability
===========================

Structured attribute container used throughout the tracing subsystem.

Responsibilities
----------------
- Store structured key-value attributes.
- Provide validation and safe mutation.
- Support bulk operations.
- Support serialization.
- Support snapshot/restore.
- Provide diagnostics and Python container protocols.

Python 3.11+
"""

from __future__ import annotations


import json

from collections.abc import Iterator
from copy import deepcopy
from typing import Any, TypeAlias


__all__: list[str] = []


# ==============================================================================
# Part 2. Constants & Type Aliases
# ==============================================================================


DEFAULT_ATTRIBUTES: dict[str, Any] = {}

ATTRIBUTES_VERSION = "1.0.0"

ATTRIBUTES_API_VERSION = "1"


AttributeMap: TypeAlias = dict[str, Any]

AttributeJSON: TypeAlias = dict[str, Any]



# ==============================================================================
# Part 3. Exceptions
# ==============================================================================


class AttributesError(Exception):
    """
    Base exception for Attributes operations.
    """



class AttributeValidationError(
    AttributesError
):
    """
    Raised when attribute validation fails.
    """



class AttributeSerializationError(
    AttributesError
):
    """
    Raised when serialization fails.
    """



# ==============================================================================
# Part 4. Core Class
# ==============================================================================


class Attributes:
    """
    Canonical structured attribute container.

    Used by
    -----
    - Trace
    - Span
    - Event
    - Link
    """



    # ==========================================================================
    # Part 4. Constructor
    # ==========================================================================


    def __init__(
        self,
        initial: AttributeMap | None = None,
    ) -> None:
        """
        Initialize Attributes container.
        """

        self._data: AttributeMap = {}


        if initial is not None:

            if not isinstance(
                initial,
                dict,
            ):
                raise TypeError(
                    "initial must be a dictionary."
                )


            self._validate_mapping(
                initial
            )


            self._data.update(
                deepcopy(initial)
            )



    # ==========================================================================
    # Part 5. Constructor & Properties
    # ==========================================================================


    @property
    def data(
        self,
    ) -> AttributeMap:
        """
        Return deep copy of internal data.
        """

        return deepcopy(
            self._data
        )



    @property
    def empty(
        self,
    ) -> bool:
        """
        Return True if empty.
        """

        return len(
            self._data
        ) == 0



    @property
    def size(
        self,
    ) -> int:
        """
        Number of attributes.
        """

        return len(
            self._data
        )



    def count(
        self,
    ) -> int:
        """
        Return number of attributes.
        """

        return len(
            self._data
        )



    def keys(
        self,
    ):
        """
        Return attribute keys.
        """

        return self._data.keys()



    def values(
        self,
    ):
        """
        Return attribute values.
        """

        return self._data.values()



    def items(
        self,
    ):
        """
        Return attribute items.
        """

        return self._data.items()



    # ==========================================================================
    # Part 6. Core API
    # ==========================================================================


    def set(
        self,
        key: str,
        value: Any,
    ) -> "Attributes":
        """
        Set attribute.
        """

        key = self._validate_key(
            key
        )


        self._data[key] = value


        return self



    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Get attribute.
        """

        key = self._validate_key(
            key
        )


        return self._data.get(
            key,
            default,
        )



    def get_or_set(
        self,
        key: str,
        default: Any,
    ) -> Any:
        """
        Return existing value or create.
        """

        key = self._validate_key(
            key
        )


        return self._data.setdefault(
            key,
            default,
        )



    def exists(
        self,
        key: str,
    ) -> bool:
        """
        Check attribute existence.
        """

        key = self._validate_key(
            key
        )


        return key in self._data



    def remove(
        self,
        key: str,
    ) -> Any:
        """
        Remove attribute.
        """

        key = self._validate_key(
            key
        )


        return self._data.pop(
            key
        )



    def pop(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Pop attribute.
        """

        key = self._validate_key(
            key
        )


        return self._data.pop(
            key,
            default,
        )



    def clear(
        self,
    ) -> "Attributes":
        """
        Clear all attributes.
        """

        self._data.clear()


        return self



    def update(
        self,
        other: AttributeMap | "Attributes",
    ) -> "Attributes":
        """
        Update attributes.
        """

        if isinstance(
            other,
            Attributes,
        ):
            mapping = other._data


        elif isinstance(
            other,
            dict,
        ):
            mapping = other


        else:
            raise TypeError(
                "Expected dict or Attributes."
            )


        self._validate_mapping(
            mapping
        )


        for key, value in mapping.items():

            self._data[key] = deepcopy(
                value
            )


        return self



    def merge(
        self,
        other: AttributeMap | "Attributes",
        *,
        overwrite: bool = False,
    ) -> "Attributes":
        """
        Merge attributes.
        """

        if isinstance(
            other,
            Attributes,
        ):
            mapping = other._data


        elif isinstance(
            other,
            dict,
        ):
            mapping = other


        else:
            raise TypeError(
                "Expected dict or Attributes."
            )


        self._validate_mapping(
            mapping
        )


        for key, value in mapping.items():

            if overwrite or key not in self._data:

                self._data[key] = deepcopy(
                    value
                )


        return self



    # ==========================================================================
    # Part 7. Validation
    # ==========================================================================


    @staticmethod
    def _validate_key(
        key: Any,
    ) -> str:
        """
        Validate attribute key.
        """

        if not isinstance(
            key,
            str,
        ):
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
        """
        Validate mapping.
        """

        if not isinstance(
            mapping,
            dict,
        ):
            raise AttributeValidationError(
                "Attributes must be dictionary."
            )


        for key in mapping:

            cls._validate_key(
                key
            )



    def validate(
        self,
    ) -> bool:
        """
        Validate current state.
        """

        self._validate_mapping(
            self._data
        )


        return True



    # ==========================================================================
    # Part 8. Serialization
    # ==========================================================================


    def to_dict(
        self,
    ) -> AttributeMap:
        """
        Convert to dictionary.
        """

        return deepcopy(
            self._data
        )



    @classmethod
    def from_dict(
        cls,
        data: AttributeMap,
    ) -> "Attributes":
        """
        Restore from dictionary.
        """

        cls._validate_mapping(
            data
        )


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
        Serialize to JSON.
        """

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
    ) -> "Attributes":
        """
        Restore from JSON.
        """

        try:

            data = json.loads(
                value
            )


        except Exception as exc:

            raise AttributeSerializationError(
                "Invalid JSON."
            ) from exc


        if not isinstance(
            data,
            dict,
        ):
            raise AttributeSerializationError(
                "JSON must decode to dictionary."
            )


        return cls.from_dict(
            data
        )
# ==============================================================================
# Part B. Snapshot / Clone
# ==============================================================================

    def snapshot(
        self,
    ) -> AttributeJSON:
        """
        Create a deep snapshot of current attributes.

        Returns
        -------
        AttributeJSON
            Independent snapshot data.
        """

        return deepcopy(
            self._data
        )


    @classmethod
    def restore(
        cls,
        snapshot: AttributeJSON,
    ) -> "Attributes":
        """
        Restore Attributes from snapshot.

        Parameters
        ----------
        snapshot:
            Snapshot generated by ``snapshot()``.

        Returns
        -------
        Attributes
            Restored attribute container.
        """

        cls._validate_mapping(
            snapshot
        )

        return cls(
            deepcopy(snapshot)
        )


    def copy(
        self,
    ) -> "Attributes":
        """
        Create a deep copy of Attributes.

        Returns
        -------
        Attributes
            Independent copy.
        """

        return self.__class__.restore(
            self.snapshot()
        )


    def clone(
        self,
    ) -> "Attributes":
        """
        Create a clone of Attributes.

        Alias of copy().
        """

        return self.copy()


    def __copy__(
        self,
    ) -> "Attributes":
        """
        Support Python copy.copy().
        """

        return self.copy()


    def __deepcopy__(
        self,
        memo: dict[int, Any],
    ) -> "Attributes":
        """
        Support Python copy.deepcopy().
        """

        if id(self) in memo:
            return memo[id(self)]

        result = self.__class__()

        memo[id(self)] = result

        result._data = deepcopy(
            self._data,
            memo,
        )

        return result


# ==============================================================================
# Part 10. Diagnostics
# ==============================================================================

    def diagnostics(
        self,
    ) -> dict[str, Any]:
        """
        Return detailed diagnostic information.
        """

        return {
            "valid": self.validate(),
            "version": ATTRIBUTES_VERSION,
            "api_version": ATTRIBUTES_API_VERSION,
            "count": self.count(),
            "size": self.size,
            "empty": self.empty,
            "keys": list(
                self._data.keys()
            ),
            "types": {
                key: type(value).__name__
                for key, value in self._data.items()
            },
        }


    def summary(
        self,
    ) -> dict[str, Any]:
        """
        Return compact summary.
        """

        return {
            "valid": self.validate(),
            "count": self.count(),
            "size": self.size,
            "empty": self.empty,
            "keys": list(
                self._data.keys()
            ),
        }


# ==============================================================================
# Part 11. Python Protocols
# ==============================================================================

    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """

        return (
            f"{self.__class__.__name__}"
            f"({self._data!r})"
        )


    def __str__(
        self,
    ) -> str:
        """
        Human readable representation.
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
        Return attribute count.
        """

        return self.count()


    def __iter__(
        self,
    ):
        """
        Iterate over keys.
        """

        return iter(
            self._data
        )


    def __contains__(
        self,
        key: object,
    ) -> bool:
        """
        Check key existence.
        """

        return key in self._data


    def __getitem__(
        self,
        key: str,
    ) -> Any:
        """
        Dictionary-style access.
        """

        key = self._validate_key(
            key
        )

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

        self.remove(
            key
        )


    def __bool__(
        self,
    ) -> bool:
        """
        Return True when attributes exist.
        """

        return not self.empty


    def __eq__(
        self,
        other: object,
    ) -> bool:
        """
        Compare Attributes objects.
        """

        if not isinstance(
            other,
            Attributes,
        ):
            return NotImplemented

        return (
            self._data
            ==
            other._data
        )


    def __hash__(
        self,
    ) -> int:
        """
        Deterministic hash value.
        """

        return hash(
            json.dumps(
                self._data,
                default=str,
                sort_keys=True,
                ensure_ascii=False,
            )
        )


# ==============================================================================
# Part 12. Public API
# ==============================================================================

__all__ = [

    # ------------------------------------------------------------------
    # Constants
    # ------------------------------------------------------------------

    "DEFAULT_ATTRIBUTES",
    "ATTRIBUTES_VERSION",
    "ATTRIBUTES_API_VERSION",

    # ------------------------------------------------------------------
    # Types
    # ------------------------------------------------------------------

    "AttributeMap",
    "AttributeJSON",

    # ------------------------------------------------------------------
    # Exceptions
    # ------------------------------------------------------------------

    "AttributesError",
    "AttributeValidationError",
    "AttributeSerializationError",

    # ------------------------------------------------------------------
    # Core
    # ------------------------------------------------------------------

    "Attributes",
]        
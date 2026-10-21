# ==============================================================================
# MetricAttributes
# ==============================================================================


# ==============================================================================
# Part 1. Imports
# ==============================================================================

from __future__ import annotations

import copy
import json

from copy import deepcopy

from collections.abc import (
    Iterator,
    Mapping,
    MutableMapping,
)

from typing import (
    Any,
    TypeAlias,
)


# ==============================================================================
# Part 2. Constants
# ==============================================================================

ATTRIBUTES_VERSION = "1.0.0"

DEFAULT_ATTRIBUTES: dict[str, Any] = {}



# ==============================================================================
# Part 3. Exceptions
# ==============================================================================


class MetricAttributesError(Exception):
    """
    Base exception for metric attributes.
    """



class MetricAttributesValidationError(
    MetricAttributesError
):
    """
    Raised when attributes validation fails.
    """



# ==============================================================================
# Part 4. Type Aliases
# ==============================================================================


AttributeKey: TypeAlias = str

AttributeValue: TypeAlias = Any

AttributeMapping: TypeAlias = dict[
    AttributeKey,
    AttributeValue,
]



# ==============================================================================
# Part 5. Class
# ==============================================================================


class MetricAttributes(
    MutableMapping[str, Any]
):
    """
    Mutable mapping container for metric attributes.

    Attributes represent dynamic metadata attached
    to a metric instance.

    Example
    -------

    >>> attrs = MetricAttributes(
    ...     {
    ...         "service": "api",
    ...         "version": "1.0",
    ...     }
    ... )

    >>> attrs["service"]
    'api'
    """

    __version__ = ATTRIBUTES_VERSION


    # --------------------------------------------------------------------------
    # Constructor
    # --------------------------------------------------------------------------

    def __init__(
        self,
        attributes: Mapping[str, Any] | None = None,
    ) -> None:
        """
        Create MetricAttributes.
        """

        if attributes is None:
            attributes = {}

        self._attributes: dict[str, Any] = {}

        self._initialize(attributes)

# ==============================================================================
# Part 6. Constructor Validation
# ==============================================================================

    def __init__(
        self,
        attributes: AttributeMapping | None = None,
    ) -> None:
        """
        Initialize MetricAttributes.
        """

        if attributes is None:
            self._attributes: dict[str, AttributeValue] = {}

        else:

            if not isinstance(attributes, Mapping):
                raise TypeError(
                    "attributes must be a mapping."
                )

            self._attributes = {}

            for key, value in attributes.items():
                self._validate_key(key)
                self._validate_value(value)

                self._attributes[str(key)] = value



# ==============================================================================
# Part 7. Properties
# ==============================================================================

    @property
    def attributes(self) -> dict[str, AttributeValue]:
        """
        Return copy of attributes.
        """

        return dict(self._attributes)



    @property
    def size(self) -> int:
        """
        Number of attributes.
        """

        return len(self._attributes)



# ==============================================================================
# Part 8. Attribute Operations
# ==============================================================================


    def add(
        self,
        key: str,
        value: AttributeValue,
    ) -> None:
        """
        Add or replace attribute.
        """

        self._validate_key(key)
        self._validate_value(value)

        self._attributes[str(key)] = value



    def update(
        self,
        attributes: AttributeMapping,
    ) -> None:
        """
        Update attributes.
        """

        if not isinstance(attributes, Mapping):
            raise TypeError(
                "attributes must be a mapping."
            )


        for key, value in attributes.items():

            self._validate_key(key)
            self._validate_value(value)

            self._attributes[str(key)] = value



    def remove(
        self,
        key: str,
    ) -> None:
        """
        Remove attribute.
        """

        self._attributes.pop(
            str(key),
            None,
        )



    def pop(
        self,
        key: str,
        default: Any = None,
    ) -> AttributeValue | Any:
        """
        Pop attribute.
        """

        return self._attributes.pop(
            str(key),
            default,
        )



    def clear(self) -> None:
        """
        Remove all attributes.
        """

        self._attributes.clear()



    def has(
        self,
        key: str,
    ) -> bool:
        """
        Check attribute existence.
        """

        return str(key) in self._attributes



    def get(
        self,
        key: str,
        default: Any = None,
    ) -> AttributeValue | Any:
        """
        Get attribute.
        """

        return self._attributes.get(
            str(key),
            default,
        )



    def keys(self):
        """
        Return keys view.
        """

        return self._attributes.keys()



    def values(self):
        """
        Return values view.
        """

        return self._attributes.values()



    def items(self):
        """
        Return items view.
        """

        return self._attributes.items()



# ==============================================================================
# Part 9. Mapping Protocol
# ==============================================================================


    def __getitem__(
        self,
        key: str,
    ) -> AttributeValue:
        return self._attributes[str(key)]



    def __setitem__(
        self,
        key: str,
        value: AttributeValue,
    ) -> None:

        self.add(
            key,
            value,
        )



    def __delitem__(
        self,
        key: str,
    ) -> None:

        del self._attributes[str(key)]



    def __contains__(
        self,
        key: object,
    ) -> bool:

        return str(key) in self._attributes



    def __iter__(self):

        return iter(
            self._attributes
        )



    def __len__(self) -> int:

        return len(
            self._attributes
        )



# ==============================================================================
# Part 10. Validation
# ==============================================================================


    @staticmethod
    def _validate_key(
        key: Any,
    ) -> None:
        """
        Validate attribute key.
        """

        if not isinstance(key, str):

            raise TypeError(
                "attribute key must be string."
            )


        if not key.strip():

            raise ValueError(
                "attribute key cannot be empty."
            )



    @staticmethod
    def _validate_value(
        value: Any,
    ) -> None:
        """
        Validate attribute value.
        """

        if value is None:

            raise TypeError(
                "attribute value cannot be None."
            )


# ==============================================================================
# Part 11. Serialization
# ==============================================================================


    def to_dict(self) -> dict[str, Any]:
        """
        Serialize attributes to dictionary.
        """

        return dict(
            self._attributes
        )



    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "MetricAttributes":
        """
        Create MetricAttributes from dictionary.
        """

        if not isinstance(data, Mapping):
            raise TypeError(
                "data must be a mapping."
            )

        return cls(
            dict(data)
        )



    def to_json(self) -> str:
        """
        Serialize attributes to JSON.
        """

        return json.dumps(
            self.to_dict(),
            sort_keys=True,
        )



    @classmethod
    def from_json(
        cls,
        data: str,
    ) -> "MetricAttributes":
        """
        Create MetricAttributes from JSON.
        """

        if not isinstance(data, str):
            raise TypeError(
                "data must be a string."
            )

        payload = json.loads(data)

        return cls.from_dict(
            payload
        )



# ==============================================================================
# Part 12. Copy
# ==============================================================================


    def copy(self) -> "MetricAttributes":
        """
        Return shallow copy.
        """

        return MetricAttributes(
            self._attributes.copy()
        )



    def clone(self) -> "MetricAttributes":
        """
        Return deep clone.
        """

        return MetricAttributes(
            deepcopy(
                self._attributes
            )
        )



# ==============================================================================
# Part 13. Equality
# ==============================================================================


    def __eq__(
        self,
        other: object,
    ) -> bool:
        """
        Compare attributes.
        """

        if not isinstance(
            other,
            MetricAttributes,
        ):
            return NotImplemented


        return (
            self._attributes
            ==
            other._attributes
        )



    def __hash__(self) -> int:
        """
        Hash attributes.
        """

        return hash(
            tuple(
                sorted(
                    self._attributes.items()
                )
            )
        )



# ==============================================================================
# Part 14. Representation
# ==============================================================================


    def __repr__(self) -> str:
        """
        Developer representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"{self._attributes!r}"
            ")"
        )



    def __str__(self) -> str:
        """
        String representation.
        """

        return str(
            self._attributes
        )



# ==============================================================================
# Part 15. Public API
# ==============================================================================


__all__ = [

    # Constants
    "ATTRIBUTES_VERSION",
    "DEFAULT_ATTRIBUTES",

    # Exceptions
    "MetricAttributesError",
    "MetricAttributesValidationError",

    # Types
    "AttributeKey",
    "AttributeValue",
    "AttributeMapping",

    # Class
    "MetricAttributes",
]


__version__ = ATTRIBUTES_VERSION
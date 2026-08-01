"""
SciOS-NG Metrics Core - Attributes
==================================

Attribute container for Metric objects.

Design goals
------------
- Ordered
- Type-safe
- Validation-aware
- Snapshot-friendly
- Mapping compatible
"""

# ==========================================================
# Part 1. Imports
# ==========================================================

from __future__ import annotations

import copy
import json

from dataclasses import dataclass, field
from typing import Any, TypeAlias
from collections.abc import Iterator, Mapping

from .validation import MetricValidator


# ==========================================================
# Part 2. Constants & Type Aliases
# ==========================================================

AttributeKey: TypeAlias = str
AttributeValue: TypeAlias = Any
AttributeDict: TypeAlias = dict[AttributeKey, AttributeValue]

DEFAULT_ATTRIBUTES: AttributeDict = {}


# ==========================================================
# Part 3. Dataclass / Core Container
# ==========================================================


@dataclass(slots=True)
class MetricAttributes:
    """
    Mutable metric attribute container.

    Behaves similarly to a standard mapping while providing
    validation, serialization and snapshot capabilities.
    """

    attributes: AttributeDict = field(
        default_factory=dict,
    )
# ==========================================================
# Part 4. Validation
# ==========================================================

    def __post_init__(self) -> None:
        """
        Normalize and validate attributes.
        """

        if self.attributes is None:
            self.attributes = {}

        if not isinstance(self.attributes, dict):
            self.attributes = dict(self.attributes)

    def validate(self) -> None:
        """
        Validate attributes.
        """

        if not isinstance(self.attributes, dict):
            raise TypeError(
                "attributes must be dict."
            )

        for key, value in self.attributes.items():

            if not isinstance(key, str):
                raise TypeError(
                    "attribute key must be str."
                )

            if not key.strip():
                raise ValueError(
                    "attribute key cannot be empty."
                )

            if not isinstance(
                value,
                (
                    str,
                    int,
                    float,
                    bool,
                    type(None),
                ),
            ):
                raise TypeError(
                    f"Invalid attribute value for '{key}': {type(value).__name__}"
                )

    def is_valid(self) -> bool:
        """
        Return True if attributes are valid.
        """

        try:
            self.validate()
            return True
        except Exception:
            return False


# ==========================================================
# Part 5. Serialization
# ==========================================================

    def to_dict(self) -> AttributeDict:
        """
        Serialize to dictionary.
        """

        return dict(self.attributes)

    @classmethod
    def from_dict(
        cls,
        data: AttributeDict,
    ) -> "MetricAttributes":
        """
        Construct from dictionary.
        """

        return cls(
            attributes=dict(data),
        )

    def to_json(
        self,
        *,
        indent: int | None = 2,
    ) -> str:
        """
        Serialize to JSON.
        """

        return json.dumps(
            self.to_dict(),
            indent=indent,
            ensure_ascii=False,
        )

    @classmethod
    def from_json(
        cls,
        text: str,
    ) -> "MetricAttributes":
        """
        Construct from JSON.
        """

        return cls.from_dict(
            json.loads(text),
        )


# ==========================================================
# Part 6. Copy API
# ==========================================================

    def copy(self) -> "MetricAttributes":
        """
        Return shallow copy.
        """

        return self.__class__.from_dict(
            self.to_dict(),
        )

    def clone(self) -> "MetricAttributes":
        """
        Return deep clone.
        """

        return copy.deepcopy(self)

    def deepcopy(self) -> "MetricAttributes":
        """
        Explicit deep copy.
        """

        return copy.deepcopy(self)

    def replace(
        self,
        **updates: Any,
    ) -> "MetricAttributes":
        """
        Return copied instance with updated fields.
        """

        data = self.to_dict()

        if "attributes" in updates:
            data = dict(updates["attributes"])
        else:
            data.update(updates)

        return self.__class__.from_dict(data)
# ==========================================================
# Part 7. Comparison
# ==========================================================

    def __eq__(
        self,
        other: object,
    ) -> bool:
        """
        Equality comparison.
        """

        if isinstance(other, MetricAttributes):
            return self.attributes == other.attributes

        if isinstance(other, Mapping):
            return self.attributes == dict(other)

        return NotImplemented


    def __hash__(self) -> int:
        """
        Hash support.
        """

        return hash(
            tuple(sorted(self.attributes.items()))
        )
# ==========================================================
# Part 8. Python Protocols
# ==========================================================

    def items(self):

        return self.attributes.items()


    def keys(self):

        return self.attributes.keys()


    def values(self):

        return self.attributes.values()


    def get(
        self,
        key: str,
        default: Any = None,
    ):

        return self.attributes.get(
            key,
            default,
        )


    def update(
        self,
        other: Mapping[str, Any],
    ) -> None:
        """
        Update attributes.
        """

        if not isinstance(other, Mapping):
            raise TypeError(
                "attributes must be a mapping."
            )

        self.attributes.update(other)


    def remove(
        self,
        key: str,
    ) -> None:
        """
        Remove attribute.
        """

        self.attributes.pop(
            key,
            None,
        )


    def clear(self) -> None:
        """
        Clear all attributes.
        """

        self.attributes.clear()


    def pop(
        self,
        key: str,
        default: Any = None,
    ):

        return self.attributes.pop(
            key,
            default,
        )


    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}"
            f"({self.attributes!r})"
        )


    def __str__(self) -> str:

        return str(self.attributes)


    def __bool__(self) -> bool:

        return bool(self.attributes)


    def __len__(self) -> int:

        return len(self.attributes)


    def __iter__(self) -> Iterator[str]:

        return iter(self.attributes)


    def __contains__(
        self,
        key: object,
    ) -> bool:

        return key in self.attributes


    def __getitem__(
        self,
        key: str,
    ) -> Any:

        return self.attributes[key]


    def __setitem__(
        self,
        key: str,
        value: Any,
    ) -> None:

        self.attributes[key] = value


    def __delitem__(
        self,
        key: str,
    ) -> None:

        del self.attributes[key]
# ==========================================================
# Part 9. Public API
# ==========================================================

__all__ = [
    "MetricAttributes",
]                    
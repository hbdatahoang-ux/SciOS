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

from __future__ import annotations

from collections.abc import Iterator, Mapping
from typing import Any

from .validation import MetricValidator

__all__ = [
    "MetricAttributes",
]


class MetricAttributes:
    """
    Mutable attribute container.
    """

    __slots__ = ("_attributes",)

    def __init__(
        self,
        attributes: Mapping[str, Any] | None = None,
    ) -> None:

        self._attributes: dict[str, Any] = {}

        if attributes:
            self.update(attributes)

    # ---------------------------------------------------------
    # Basic API
    # ---------------------------------------------------------

    def add(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Add or replace an attribute.
        """
        key, value = MetricValidator.validate_attribute(key, value)
        self._attributes[key] = value

    def update(
        self,
        attributes: Mapping[str, Any],
    ) -> None:
        """
        Update multiple attributes.
        """
        attributes = MetricValidator.validate_attributes(attributes)

        self._attributes.update(attributes)

    def remove(
        self,
        key: str,
    ) -> None:
        """
        Remove an attribute.
        """
        self._attributes.pop(key, None)

    def clear(self) -> None:
        """
        Remove all attributes.
        """
        self._attributes.clear()

    # ---------------------------------------------------------
    # Query
    # ---------------------------------------------------------

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:

        return self._attributes.get(key, default)

    def contains(
        self,
        key: str,
    ) -> bool:

        return key in self._attributes

    # ---------------------------------------------------------
    # Views
    # ---------------------------------------------------------

    def keys(self):

        return self._attributes.keys()

    def values(self):

        return self._attributes.values()

    def items(self):

        return self._attributes.items()

    # ---------------------------------------------------------
    # Copy
    # ---------------------------------------------------------

    def copy(self) -> "MetricAttributes":
        """
        Shallow copy.
        """
        return MetricAttributes(self._attributes)

    def to_dict(self) -> dict[str, Any]:
        """
        Export as dict.
        """
        return dict(self._attributes)

    # ---------------------------------------------------------
    # Rich API
    # ---------------------------------------------------------

    def __getitem__(
        self,
        key: str,
    ) -> Any:

        return self._attributes[key]

    def __setitem__(
        self,
        key: str,
        value: Any,
    ) -> None:

        self.add(key, value)

    def __delitem__(
        self,
        key: str,
    ) -> None:

        self.remove(key)

    def __contains__(
        self,
        key: object,
    ) -> bool:

        return key in self._attributes

    def __iter__(self) -> Iterator[str]:

        return iter(self._attributes)

    def __len__(self) -> int:

        return len(self._attributes)

    def __bool__(self) -> bool:

        return bool(self._attributes)

    def __repr__(self) -> str:

        return f"MetricAttributes({self._attributes!r})"

    def __str__(self) -> str:

        return str(self._attributes)

    def __eq__(
        self,
        other: object,
    ) -> bool:

        if isinstance(other, MetricAttributes):
            return self._attributes == other._attributes

        if isinstance(other, Mapping):
            return self._attributes == dict(other)

        return False
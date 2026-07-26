"""
SciOS Observability - Trace Baggage
==================================

Distributed trace baggage.

Responsibilities
----------------
- Carry contextual metadata
- Propagate across spans
- Merge baggage
- Serialize baggage
"""

from __future__ import annotations

from collections.abc import Iterator
from copy import deepcopy
from typing import Any

__all__ = [
    "Baggage",
]


class Baggage:
    """
    Distributed tracing baggage.

    Baggage is propagated across the entire trace.

    Typical examples:

        request_id
        user_id
        tenant
        session
        workflow
        runtime
    """

    def __init__(
        self,
        initial: dict[str, Any] | None = None,
    ) -> None:

        self._items: dict[str, Any] = {}

        if initial:
            self.update(initial)

    # =====================================================
    # Basic Operations
    # =====================================================

    def set(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Set baggage item.
        """

        self._items[key] = value

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Get baggage item.
        """

        return self._items.get(key, default)

    def remove(
        self,
        key: str,
    ) -> None:
        """
        Remove baggage item.
        """

        self._items.pop(key, None)

    def clear(self) -> None:
        """
        Remove all baggage.
        """

        self._items.clear()

    # =====================================================
    # Merge
    # =====================================================

    def update(
        self,
        values: dict[str, Any],
    ) -> None:
        """
        Merge dictionary.
        """

        self._items.update(values)

    def merge(
        self,
        other: "Baggage",
    ) -> None:
        """
        Merge another baggage.
        """

        self._items.update(
            other._items
        )

    # =====================================================
    # Clone
    # =====================================================

    def copy(self) -> "Baggage":
        """
        Deep copy.
        """

        return Baggage(
            deepcopy(self._items)
        )

    # =====================================================
    # Serialization
    # =====================================================

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Convert to dictionary.
        """

        return deepcopy(
            self._items
        )

    @classmethod
    def from_dict(
        cls,
        values: dict[str, Any],
    ) -> "Baggage":

        return cls(values)

    # =====================================================
    # Query
    # =====================================================

    def keys(self):

        return self._items.keys()

    def values(self):

        return self._items.values()

    def items(self):

        return self._items.items()

    # =====================================================
    # Container API
    # =====================================================

    def __contains__(
        self,
        key: str,
    ) -> bool:

        return key in self._items

    def __getitem__(
        self,
        key: str,
    ) -> Any:

        return self._items[key]

    def __setitem__(
        self,
        key: str,
        value: Any,
    ) -> None:

        self._items[key] = value

    def __delitem__(
        self,
        key: str,
    ) -> None:

        del self._items[key]

    def __iter__(
        self,
    ) -> Iterator[str]:

        return iter(self._items)

    def __len__(
        self,
    ) -> int:

        return len(self._items)

    def __bool__(
        self,
    ) -> bool:

        return bool(self._items)

    # =====================================================
    # Representation
    # =====================================================

    def __repr__(
        self,
    ) -> str:

        return (
            f"{self.__class__.__name__}"
            f"(size={len(self)})"
        )
"""
SciOS-NG Metrics Core - Labels
==============================

Immutable-like label container with validation.

Design goals
------------
- Ordered
- Type-safe
- Validation-aware
- Snapshot-friendly
- Mapping compatible
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping
from typing import Any

from .validation import MetricValidator

__all__ = [
    "MetricLabels",
]


class MetricLabels:
    """
    Metric label container.
    """

    __slots__ = ("_labels",)

    def __init__(
        self,
        labels: Mapping[str, str] | None = None,
    ) -> None:

        self._labels: dict[str, str] = {}

        if labels:
            self.update(labels)

    # ---------------------------------------------------------
    # Basic API
    # ---------------------------------------------------------

    def add(self, key: str, value: str) -> None:
        """
        Add or replace one label.
        """
        key, value = MetricValidator.validate_label(key, value)

        self._labels[key] = value

    def update(
        self,
        labels: Mapping[str, str],
    ) -> None:
        """
        Update labels.
        """
        labels = MetricValidator.validate_labels(labels)

        self._labels.update(labels)

    def remove(
        self,
        key: str,
    ) -> None:
        """
        Remove a label.
        """
        self._labels.pop(key, None)

    def clear(self) -> None:
        """
        Remove all labels.
        """
        self._labels.clear()

    # ---------------------------------------------------------
    # Query
    # ---------------------------------------------------------

    def get(
        self,
        key: str,
        default: str | None = None,
    ) -> str | None:

        return self._labels.get(key, default)

    def contains(
        self,
        key: str,
    ) -> bool:

        return key in self._labels

    # ---------------------------------------------------------
    # Views
    # ---------------------------------------------------------

    def keys(self):

        return self._labels.keys()

    def values(self):

        return self._labels.values()

    def items(self):

        return self._labels.items()

    # ---------------------------------------------------------
    # Copy
    # ---------------------------------------------------------

    def copy(self) -> "MetricLabels":

        return MetricLabels(self._labels)

    def to_dict(self) -> dict[str, str]:

        return dict(self._labels)

    # ---------------------------------------------------------
    # Rich API
    # ---------------------------------------------------------

    def __getitem__(self, key: str) -> str:

        return self._labels[key]

    def __setitem__(
        self,
        key: str,
        value: str,
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

        return key in self._labels

    def __iter__(self) -> Iterator[str]:

        return iter(self._labels)

    def __len__(self) -> int:

        return len(self._labels)

    def __bool__(self) -> bool:

        return bool(self._labels)

    def __repr__(self) -> str:

        return f"MetricLabels({self._labels!r})"

    def __str__(self) -> str:

        return str(self._labels)

    def __eq__(
        self,
        other: object,
    ) -> bool:

        if isinstance(other, MetricLabels):
            return self._labels == other._labels

        if isinstance(other, Mapping):
            return self._labels == dict(other)

        return False
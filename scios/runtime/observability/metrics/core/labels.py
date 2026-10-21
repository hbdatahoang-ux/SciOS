# ==============================================================================
# Part 1. Imports
# ==============================================================================

from __future__ import annotations

import json

from copy import deepcopy

from collections.abc import Iterator, MutableMapping

from typing import Any, TypeAlias



# ==============================================================================
# Part 2. Constants
# ==============================================================================

LABEL_KEY_MAX_LENGTH: int = 256

LABEL_VALUE_MAX_LENGTH: int = 1024

__version__ = "0.1.0"



# ==============================================================================
# Part 3. Exceptions
# ==============================================================================

class MetricLabelsError(Exception):
    """
    Base exception for MetricLabels.
    """


class LabelValidationError(MetricLabelsError):
    """
    Raised when a label is invalid.
    """


class LabelNotFoundError(MetricLabelsError):
    """
    Raised when a label does not exist.
    """


# ==============================================================================
# Part 4. Type Aliases
# ==============================================================================

LabelKey: TypeAlias = str

LabelValue: TypeAlias = str

LabelDict: TypeAlias = dict[LabelKey, LabelValue]



# ==============================================================================
# Part 5. Class
# ==============================================================================

class MetricLabels(MutableMapping[str, str]):
    """
    Mutable mapping storing metric labels.

    Labels are normalized to strings and preserve insertion order.
    """

    __slots__ = ("_labels",)

# ==============================================================================
# Part 6. Constructor Validation
# ==============================================================================

    def __init__(
        self,
        labels: LabelDict | None = None,
    ) -> None:
        self._labels: LabelDict = {}

        if labels is None:
            return

        if not isinstance(labels, MutableMapping):
            raise TypeError(
                "labels must be a mapping."
            )

        for key, value in labels.items():
            self.add(key, value)



# ==============================================================================
# Part 7. Properties
# ==============================================================================

    @property
    def labels(self) -> LabelDict:
        """
        Return a copy of labels.
        """
        return dict(self._labels)

    @property
    def size(self) -> int:
        """
        Number of labels.
        """
        return len(self._labels)

    @property
    def is_empty(self) -> bool:
        """
        True if no labels exist.
        """
        return not self._labels



# ==============================================================================
# Part 8. Label Operations
# ==============================================================================

    def add(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Add or replace a label.
        """
        self._validate_key(key)
        self._validate_value(value)

        self._labels[str(key)] = str(value)

    def update(
        self,
        labels: MutableMapping[str, Any],
    ) -> None:
        """
        Update multiple labels.
        """
        if not isinstance(labels, MutableMapping):
            raise TypeError(
                "labels must be a mapping."
            )

        for key, value in labels.items():
            self.add(key, value)

    def remove(
        self,
        key: str,
    ) -> None:
        """
        Remove a label.
        """
        if key not in self._labels:
            raise LabelNotFoundError(key)

        del self._labels[key]

    def pop(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Pop a label.
        """
        return self._labels.pop(key, default)

    def clear(self) -> None:
        """
        Remove all labels.
        """
        self._labels.clear()

    def has(
        self,
        key: str,
    ) -> bool:
        """
        Whether a label exists.
        """
        return key in self._labels

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Get a label.
        """
        return self._labels.get(key, default)

    def keys(self):
        return self._labels.keys()

    def values(self):
        return self._labels.values()

    def items(self):
        return self._labels.items()



# ==============================================================================
# Part 9. Mapping Protocol
# ==============================================================================

    def __getitem__(
        self,
        key: str,
    ) -> str:
        return self._labels[key]

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
        return key in self._labels

    def __iter__(
        self,
    ) -> Iterator[str]:
        return iter(self._labels)

    def __len__(
        self,
    ) -> int:
        return len(self._labels)



# ==============================================================================
# Part 10. Validation
# ==============================================================================

    @staticmethod
    def _validate_key(
        key: Any,
    ) -> None:
        if not isinstance(key, str):
            raise LabelValidationError(
                "label key must be a string."
            )

        key = key.strip()

        if not key:
            raise LabelValidationError(
                "label key cannot be empty."
            )

        if len(key) > LABEL_KEY_MAX_LENGTH:
            raise LabelValidationError(
                "label key exceeds maximum length."
            )

    @staticmethod
    def _validate_value(
        value: Any,
    ) -> None:
        value = str(value)

        if len(value) > LABEL_VALUE_MAX_LENGTH:
            raise LabelValidationError(
                "label value exceeds maximum length."
            )

# ==============================================================================
# Part 11. Serialization
# ==============================================================================

    def to_dict(self) -> LabelDict:
        """
        Serialize to dictionary.
        """
        return dict(self._labels)

    @classmethod
    def from_dict(
        cls,
        data: MutableMapping[str, Any],
    ) -> "MetricLabels":
        """
        Construct from dictionary.
        """
        if not isinstance(data, MutableMapping):
            raise TypeError(
                "data must be a mapping."
            )

        return cls(data)

    def to_json(
        self,
        *,
        indent: int | None = None,
        sort_keys: bool = False,
    ) -> str:
        """
        Serialize to JSON.
        """
        return json.dumps(
            self.to_dict(),
            indent=indent,
            sort_keys=sort_keys,
            ensure_ascii=False,
        )

    @classmethod
    def from_json(
        cls,
        data: str,
    ) -> "MetricLabels":
        """
        Construct from JSON.
        """
        obj = json.loads(data)
        return cls.from_dict(obj)


# ==============================================================================
# Part 12. Copy
# ==============================================================================

    def copy(self) -> "MetricLabels":
        """
        Return a shallow copy.
        """
        return MetricLabels(self._labels)

    def clone(self) -> "MetricLabels":
        """
        Return a deep copy.
        """
        return deepcopy(self)


# ==============================================================================
# Part 13. Equality
# ==============================================================================

    def __eq__(
        self,
        other: object,
    ) -> bool:
        if not isinstance(other, MetricLabels):
            return NotImplemented

        return self._labels == other._labels

    def __hash__(self) -> int:
        return hash(
            tuple(self._labels.items())
        )


# ==============================================================================
# Part 14. Representation
# ==============================================================================

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"({self._labels!r})"
        )

    def __str__(self) -> str:
        return str(self._labels)


# ==============================================================================
# Part 15. Public API
# ==============================================================================

__all__ = [
    "LABEL_KEY_MAX_LENGTH",
    "LABEL_VALUE_MAX_LENGTH",
    "LabelKey",
    "LabelValue",
    "LabelDict",
    "MetricLabels",
    "MetricLabelsError",
    "LabelValidationError",
    "LabelNotFoundError",
]                
# ==========================================================
# Part 1. Imports
# ==========================================================

from __future__ import annotations

import copy
import json

from collections.abc import Iterator, Mapping
from dataclasses import dataclass, field
from typing import Any, TypeAlias

__all__ = [
    "LabelKey",
    "LabelValue",
    "LabelMap",
    "DEFAULT_LABELS",
    "MetricLabels",
]


# ==========================================================
# Part 2. Constants & Type Aliases
# ==========================================================

LabelKey: TypeAlias = str
LabelValue: TypeAlias = str
LabelMap: TypeAlias = dict[LabelKey, LabelValue]

DEFAULT_LABELS: LabelMap = {}


# ==========================================================
# Part 3. Dataclass / Core Container
# ==========================================================

@dataclass(slots=True)
class MetricLabels:
    """
    Metric label container.

    Labels are mutable mappings of string keys to string values.
    """

    labels: LabelMap = field(default_factory=dict)
# ==========================================================
# Part 4. Validation
# ==========================================================

    
    def __post_init__(self) -> None:
        """
        Normalize container only.
        """

        self.labels = dict(self.labels)

    def validate(self) -> None:
        """
        Validate labels.
        """

        if not isinstance(self.labels, dict):
            raise TypeError(
                "labels must be a dictionary."
            )

        for key, value in self.labels.items():

            if not isinstance(key, str):
                raise TypeError(
                    "label key must be str."
                )

            if not key.strip():
                raise ValueError(
                    "label key cannot be empty."
                )

            if not isinstance(value, str):
                raise TypeError(
                    "label value must be str."
                )

    def is_valid(self) -> bool:
        """
        Return True if labels are valid.
        """

        try:
            self.validate()
            return True
        except Exception:
            return False


# ==========================================================
# Part 5. Serialization
# ==========================================================

    def to_dict(self) -> LabelMap:
        """
        Serialize labels.
        """

        return dict(self.labels)

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, str],
    ) -> "MetricLabels":
        """
        Construct from dictionary.
        """

        return cls(
            labels=dict(data),
        )

    def to_json(
        self,
        *,
        indent: int |None = 2,
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
    ) -> "MetricLabels":
        """
        Construct from JSON.
        """

        return cls.from_dict(
            json.loads(text),
        )


# ==========================================================
# Part 6. Copy API
# ==========================================================

    def copy(self) -> "MetricLabels":
        """
        Return shallow copy.
        """

        return self.__class__.from_dict(
            self.to_dict(),
        )

    def clone(self) -> "MetricLabels":
        """
        Return deep clone.
        """

        return copy.deepcopy(self)

    def deepcopy(self) -> "MetricLabels":
        """
        Explicit deep copy.
        """

        return copy.deepcopy(self)

    def replace(
        self,
        **updates: str,
    ) -> "MetricLabels":
        """
        Return copied labels with updates.
        """

        data = self.to_dict()
        data.update(updates)

        return self.__class__.from_dict(data)
# ==========================================================
# Part 7. Comparison
# ==========================================================

    def __eq__(
        self,
        other: object,
    ) -> bool:

        if isinstance(other, MetricLabels):
            return self.labels == other.labels

        if isinstance(other, Mapping):
            return self.labels == dict(other)

        return False

    def __hash__(self) -> int:

        return hash(
            tuple(
                sorted(self.labels.items()),
            )
        )


# ==========================================================
# Part 8. Python Protocols
# ==========================================================

    def items(self):

        return self.labels.items()

    def keys(self):

        return self.labels.keys()

    def values(self):

        return self.labels.values()

    def get(
        self,
        key: str,
        default: Any = None,
    ):

        return self.labels.get(
            key,
            default,
        )

    def update(
        self,
        other: Mapping[str, str],
    ) -> None:

        self.labels.update(
            {
                str(k): str(v)
                for k, v in other.items()
            }
        )

    def clear(self) -> None:

        self.labels.clear()

    def pop(
        self,
        key: str,
        default: Any = None,
    ):

        return self.labels.pop(
            key,
            default,
        )

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}"
            f"({self.labels!r})"
        )

    def __str__(self) -> str:

        return str(self.labels)

    def __bool__(self) -> bool:

        return bool(self.labels)

    def __len__(self) -> int:

        return len(self.labels)

    def __iter__(self) -> Iterator[str]:

        return iter(self.labels)

    def __contains__(
        self,
        key: object,
    ) -> bool:

        return key in self.labels

    def __getitem__(
        self,
        key: str,
    ) -> str:

        return self.labels[key]

    def __setitem__(
        self,
        key: str,
        value: str,
    ) -> None:

        self.labels[str(key)] = str(value)

    def __delitem__(
        self,
        key: str,
    ) -> None:

        del self.labels[key]

# ==========================================================
# Part 9. Public API
# ==========================================================

__all__ = [
    "LabelKey",
    "LabelValue",
    "LabelMap",
    "DEFAULT_LABELS",
    "MetricLabels",
]            
"""
SciOS Runtime Metrics Labels
============================

Metric label model.

Responsibilities
-----------------
- Store metric dimensions.
- Validate label keys.
- Normalize values.
- Provide immutable-like label operations.
- Support exporters.

Examples
--------

labels = MetricLabels(
    service="runtime",
    component="scheduler",
)

Python 3.11+
"""

from __future__ import annotations


from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Iterator


__all__ = [
    "MetricLabels",
]



# ==========================================================
# Validation
# ==========================================================


def _normalize_key(
    key: str,
) -> str:
    """
    Normalize label key.
    """

    key = str(key).strip()


    if not key:

        raise ValueError(
            "label key cannot be empty"
        )


    return key



def _normalize_value(
    value: Any,
) -> str:
    """
    Normalize label value.

    Prometheus/OpenTelemetry
    labels are string based.
    """

    return str(value)



# ==========================================================
# Labels
# ==========================================================


@dataclass(slots=True)
class MetricLabels:
    """
    Metric label container.

    Example
    -------

    labels = MetricLabels(
        service="runtime",
        module="scheduler",
    )

    """


    values: dict[str, str] = field(
        default_factory=dict
    )



    # ======================================================
    # Initialization
    # ======================================================


    def __init__(
        self,
        **labels: Any,
    ):
        """
        Create labels.
        """

        self.values = {}


        for key, value in labels.items():

            self.set(
                key,
                value,
            )



    # ======================================================
    # Mutation
    # ======================================================


    def set(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Set label.
        """


        key = _normalize_key(
            key
        )


        self.values[key] = (
            _normalize_value(value)
        )



    def remove(
        self,
        key: str,
    ) -> None:
        """
        Remove label.
        """

        self.values.pop(
            key,
            None,
        )



    def clear(self) -> None:
        """
        Remove all labels.
        """

        self.values.clear()



    # ======================================================
    # Access
    # ======================================================


    def get(
        self,
        key: str,
        default: str | None = None,
    ) -> str | None:
        """
        Get label value.
        """

        return self.values.get(
            key,
            default,
        )



    def contains(
        self,
        key: str,
    ) -> bool:
        """
        Check label existence.
        """

        return key in self.values



    # ======================================================
    # Merge
    # ======================================================


    def merge(
        self,
        other: "MetricLabels",
    ) -> "MetricLabels":
        """
        Create merged labels.

        Existing labels are overwritten.
        """


        result = self.copy()


        result.values.update(
            other.values
        )


        return result



    # ======================================================
    # Serialization
    # ======================================================


    def to_dict(
        self,
    ) -> dict[str, str]:
        """
        Convert to dictionary.
        """

        return dict(
            self.values
        )



    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "MetricLabels":
        """
        Restore labels.
        """

        return cls(
            **data
        )



    # ======================================================
    # Copy
    # ======================================================


    def copy(
        self,
    ) -> "MetricLabels":
        """
        Deep copy.
        """

        result = MetricLabels()

        result.values = deepcopy(
            self.values
        )

        return result



    # ======================================================
    # Protocols
    # ======================================================


    def __getitem__(
        self,
        key: str,
    ) -> str:
        return self.values[key]



    def __setitem__(
        self,
        key: str,
        value: Any,
    ) -> None:

        self.set(
            key,
            value,
        )



    def __contains__(
        self,
        key: str,
    ) -> bool:

        return key in self.values



    def __iter__(
        self,
    ) -> Iterator[str]:

        return iter(
            self.values
        )



    def __len__(
        self,
    ) -> int:

        return len(
            self.values
        )



    def __repr__(
        self,
    ) -> str:

        return (
            "MetricLabels("
            f"{self.values!r}"
            ")"
        )
# ==========================================================
# Part 1. Imports
# ==========================================================

from __future__ import annotations

import copy
import json

from dataclasses import dataclass
from dataclasses import field

from typing import Any
from typing import Final
from typing import TypeAlias

from .metadata import MetricMetadata
from .validation import MetricValidator

# ==========================================================
# Part 2. Constants & Type Aliases
# ==========================================================

__all__ = [
    "MetricDescriptor",
]

# ----------------------------------------------------------
# Default constants
# ----------------------------------------------------------

DEFAULT_METRIC_TYPE: Final[str] = "gauge"

DEFAULT_VALUE_TYPE: Final[type] = float

DEFAULT_AGGREGATION: Final[str] = "last_value"

DEFAULT_TEMPORALITY: Final[str] = "cumulative"

DEFAULT_MONOTONIC: Final[bool] = False


# ----------------------------------------------------------
# Type aliases
# ----------------------------------------------------------

MetricType: TypeAlias = str

MetricValueType: TypeAlias = type

MetricAggregation: TypeAlias = str

MetricTemporality: TypeAlias = str

MetricMonotonic: TypeAlias = bool
# ==========================================================
# Part 3. Dataclass
# ==========================================================

@dataclass(slots=True)
class MetricDescriptor:
    """
    Immutable descriptor describing a metric.
    """

    # ------------------------------------------------------
    # Metadata
    # ------------------------------------------------------

    metadata: MetricMetadata

    # ------------------------------------------------------
    # Metric type
    # ------------------------------------------------------

    metric_type: MetricType = DEFAULT_METRIC_TYPE

    # ------------------------------------------------------
    # Runtime value type
    # ------------------------------------------------------

    value_type: MetricValueType = DEFAULT_VALUE_TYPE

    # ------------------------------------------------------
    # Aggregation
    # ------------------------------------------------------

    aggregation: MetricAggregation = DEFAULT_AGGREGATION

    # ------------------------------------------------------
    # Temporality
    # ------------------------------------------------------

    temporality: MetricTemporality = DEFAULT_TEMPORALITY

    # ------------------------------------------------------
    # Monotonic
    # ------------------------------------------------------

    monotonic: MetricMonotonic = DEFAULT_MONOTONIC

# ==========================================================
# Part 4. Validation
# ==========================================================

    def __post_init__(self) -> None:
        """
        Normalize descriptor.
        """

        if not isinstance(self.metadata, MetricMetadata):
            raise TypeError(
                "metadata must be a MetricMetadata instance."
            )

        self.metric_type = str(
            self.metric_type,
        ).strip()

        self.aggregation = str(
            self.aggregation,
        ).strip()

        self.temporality = str(
            self.temporality,
        ).strip()

        if isinstance(
            self.value_type,
            str,
        ):
            self.value_type = self.value_type.strip()

    def validate(self) -> None:
        """
        Validate descriptor.
        """

        self.metadata.validate()

        if self.metric_type not in {
            "counter",
            "gauge",
            "histogram",
            "summary",
        }:
            raise ValueError(
                f"Invalid metric_type: {self.metric_type}"
            )

        if not isinstance(
            self.value_type,
            type,
        ):
            raise TypeError(
                "value_type must be type."
            )

        if self.aggregation not in {
            "sum",
            "last_value",
            "min",
            "max",
            "average",
            "count",
        }:
            raise ValueError(
                f"Invalid aggregation: {self.aggregation}"
            )

        if self.temporality not in {
            "delta",
            "cumulative",
        }:
            raise ValueError(
                f"Invalid temporality: {self.temporality}"
            )

        if not isinstance(
            self.monotonic,
            bool,
        ):
            raise TypeError(
                "monotonic must be bool."
            )

    def is_valid(self) -> bool:
        """
        Return True if descriptor is valid.
        """

        try:
            self.validate()
        except Exception:
            return False

        return True
# ==========================================================
# Part 5. Serialization
# ==========================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize descriptor to dictionary.
        """

        return {
            "metadata": self.metadata.to_dict(),
            "metric_type": self.metric_type,
            "value_type": self.value_type.__name__,
            "aggregation": self.aggregation,
            "temporality": self.temporality,
            "monotonic": self.monotonic,
        }


    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "MetricDescriptor":
        """
        Construct descriptor from dictionary.
        """

        value = data.get(
            "value_type",
            DEFAULT_VALUE_TYPE,
        )

        if isinstance(value, type):
            value_type = value
        else:
            value_type = getattr(
                __builtins__,
                str(value),
                DEFAULT_VALUE_TYPE,
            )

        return cls(
            metadata=MetricMetadata.from_dict(
                data["metadata"],
            ),
            metric_type=data.get(
                "metric_type",
                DEFAULT_METRIC_TYPE,
            ),
            value_type=value_type,
            aggregation=data.get(
                "aggregation",
                DEFAULT_AGGREGATION,
            ),
            temporality=data.get(
                "temporality",
                DEFAULT_TEMPORALITY,
            ),
            monotonic=data.get(
                "monotonic",
                DEFAULT_MONOTONIC,
            ),
        )


    def to_json(
        self,
        *,
        indent: int | None = 2,
    ) -> str:
        """
        Serialize descriptor to JSON.
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
    ) -> "MetricDescriptor":
        """
        Construct descriptor from JSON.
        """

        return cls.from_dict(
            json.loads(text),
        )


    # ==========================================================
    # Part 6. Copy API
    # ==========================================================

    def copy(self) -> "MetricDescriptor":
        """
        Return shallow copy.
        """

        return self.__class__.from_dict(
            self.to_dict(),
        )


    def clone(self) -> "MetricDescriptor":
        """
        Return deep clone.
        """

        return copy.deepcopy(self)


    def deepcopy(self) -> "MetricDescriptor":
        """
        Explicit deep copy.
        """

        return copy.deepcopy(self)


    def replace(
        self,
        **updates: Any,
    ) -> "MetricDescriptor":
        """
        Return copied descriptor with updated fields.
        """

        data = self.to_dict()

        data.update(updates)

        if isinstance(
            data.get("metadata"),
            MetricMetadata,
        ):
            data["metadata"] = data["metadata"].to_dict()

        return self.__class__.from_dict(data)

# ==========================================================
# Part 7. Comparison
# ==========================================================

    def equals(
        self,
        other: object,
    ) -> bool:
        """
        Compare two descriptors.
        """

        if not isinstance(
            other,
            MetricDescriptor,
        ):
            return False

        return self.to_dict() == other.to_dict()

    def __eq__(
        self,
        other: object,
    ) -> bool:
        """
        Equality operator.
        """

        return self.equals(other)

    def __hash__(self) -> int:
        """
        Hash value.
        """

        return hash(
            (
                self.metadata,
                self.metric_type,
                self.value_type,
                self.aggregation,
                self.temporality,
                self.monotonic,
            )
        )
# ==========================================================
# Part 8. Python Protocols
# ==========================================================

    def __repr__(self) -> str:
        """
        Developer representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"metadata={self.metadata!r}, "
            f"metric_type={self.metric_type!r}, "
            f"value_type={self.value_type.__name__!r})"
        )

    def __str__(self) -> str:
        """
        Human-readable representation.
        """

        return self.metadata.name

    def __bool__(self) -> bool:
        """
        Truth value.
        """

        return bool(self.metadata.name)
# ==========================================================
# Part 9. Public API
# ==========================================================

__all__ = [
    "MetricDescriptor",
    "DEFAULT_METRIC_TYPE",
    "DEFAULT_VALUE_TYPE",
    "DEFAULT_AGGREGATION",
    "DEFAULT_TEMPORALITY",
    "DEFAULT_MONOTONIC",
    "MetricType",
    "MetricValueType",
    "MetricAggregation",
    "MetricTemporality",
]                            
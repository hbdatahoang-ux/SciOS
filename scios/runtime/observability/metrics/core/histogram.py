"""
SciOS Runtime Histogram
=======================

A Histogram represents a metric that records observations and aggregates
them into configurable value buckets.

Python 3.11+
"""

from __future__ import annotations

# ==============================================================================

# Part 1. Imports

# ==============================================================================

from typing import Any, Final, TypeAlias

from copy import deepcopy
import json
from typing import Any

from .metric_state import MetricState

# ==============================================================================

# Part 2. Constants

# ==============================================================================

DEFAULT_VALUE: Final[float] = 0.0

DEFAULT_NAME: Final[str | None] = None

DEFAULT_DESCRIPTION: Final[str | None] = None

DEFAULT_UNIT: Final[str | None] = None

DEFAULT_BUCKETS: Final[tuple[float, ...]] = ()

DEFAULT_METADATA: Final[dict[str, Any]] = {}

DEFAULT_ANNOTATIONS: Final[dict[str, Any]] = {}

DEFAULT_TAGS: Final[dict[str, Any]] = {}

# ==============================================================================

# Part 3. Type Aliases

# ==============================================================================

NumericValue: TypeAlias = int | float

BucketValue: TypeAlias = int | float

BucketCollection: TypeAlias = tuple[BucketValue, ...]

Metadata: TypeAlias = dict[str, Any]

Annotation: TypeAlias = dict[str, Any]

Tag: TypeAlias = dict[str, Any]

# ==============================================================================

# Part 4. Exceptions

# ==============================================================================

class HistogramValidationError(ValueError):
    """
    Raised when a Histogram contains invalid configuration or state.
    """

    pass

# ==============================================================================
# Part 5. Histogram class
# ==============================================================================

# ------------------------------------------------------------------------------
# Internal sentinel
# ------------------------------------------------------------------------------

_DEFAULT_STATE = object()


class Histogram:
    """
    SciOS Runtime Histogram.

    A Histogram records numeric observations and provides aggregate
    statistics over those observations.
    """

    # ==========================================================================
    # Constructor
    # ==========================================================================

    def __init__(
        self,
        value: NumericValue = DEFAULT_VALUE,
        *,
        name: str | None = DEFAULT_NAME,
        description: str | None = DEFAULT_DESCRIPTION,
        unit: str | None = DEFAULT_UNIT,
        buckets: BucketCollection = DEFAULT_BUCKETS,
        metadata: Metadata | None = None,
        annotations: Annotation | None = None,
        tags: Tag | None = None,
        state: MetricState | None | object = _DEFAULT_STATE,
    ) -> None:
        self._name = name
        self._value = value
        self._description = description
        self._unit = unit

        # Do not validate ordering/duplicates during construction.
        # The validation contract is exposed through validate().
        self._buckets = tuple(buckets)

        self._metadata = deepcopy(
            DEFAULT_METADATA if metadata is None else metadata
        )

        self._annotations = deepcopy(
            DEFAULT_ANNOTATIONS if annotations is None else annotations
        )

        self._tags = deepcopy(
            DEFAULT_TAGS if tags is None else tags
        )

        # Distinguish omitted state from explicit state=None.
        self._state = (
            MetricState()
            if state is _DEFAULT_STATE
            else state
        )

        self._observations: list[float] = []

        # Validate basic configuration while allowing the explicit
        # None-state contract and deferred bucket validation.
        self._validate_basic_configuration()

    # ==========================================================================
    # Properties
    # ==========================================================================

    @property
    def name(self) -> str | None:
        return self._name

    @name.setter
    def name(self, value: str | None) -> None:
        if value is not None and not isinstance(value, str):
            raise TypeError("name must be str or None.")
        self._name = value

    @property
    def value(self) -> NumericValue:
        return self._value

    @value.setter
    def value(self, value: NumericValue) -> None:
        self._validate_numeric(value, "value")
        self._value = value

    @property
    def description(self) -> str | None:
        return self._description

    @description.setter
    def description(self, value: str | None) -> None:
        if value is not None and not isinstance(value, str):
            raise TypeError("description must be str or None.")
        self._description = value

    @property
    def unit(self) -> str | None:
        return self._unit

    @unit.setter
    def unit(self, value: str | None) -> None:
        if value is not None and not isinstance(value, str):
            raise TypeError("unit must be str or None.")
        self._unit = value

    @property
    def buckets(self) -> BucketCollection:
        return tuple(self._buckets)

    @buckets.setter
    def buckets(self, value: BucketCollection) -> None:
        self._buckets = tuple(value)

    @property
    def metadata(self) -> Metadata:
        return self._metadata

    @metadata.setter
    def metadata(self, value: Metadata) -> None:
        if not isinstance(value, dict):
            raise TypeError("metadata must be dict.")
        self._metadata = deepcopy(value)

    @property
    def annotations(self) -> Annotation:
        return self._annotations

    @annotations.setter
    def annotations(self, value: Annotation) -> None:
        if value is None:
            raise TypeError("annotations must not be None.")
        if not isinstance(value, dict):
            raise TypeError("annotations must be dict.")
        self._annotations = deepcopy(value)

    @property
    def tags(self) -> Tag:
        return self._tags

    @tags.setter
    def tags(self, value: Tag) -> None:
        if value is None:
            raise TypeError("tags must not be None.")
        if not isinstance(value, dict):
            raise TypeError("tags must be dict.")
        self._tags = deepcopy(value)

    @property
    def state(self) -> MetricState | None:
        return self._state

    @state.setter
    def state(self, value: MetricState | None) -> None:
        if value is not None and not isinstance(value, MetricState):
            raise TypeError("state must be MetricState or None.")
        self._state = value

    # ==========================================================================
    # Value operations
    # ==========================================================================

    def set_value(self, value: NumericValue) -> "Histogram":
        self._validate_numeric(value, "value")
        self._value = value
        return self

    def reset(self) -> "Histogram":
        self._value = DEFAULT_VALUE
        self._observations.clear()
        self._apply_state_reset()
        return self

    def add_value(
        self,
        amount: NumericValue = 1,
    ) -> "Histogram":
        self._validate_numeric(amount, "amount")
        self._value += amount
        return self

    def subtract_value(
        self,
        amount: NumericValue = 1,
    ) -> "Histogram":
        self._validate_numeric(amount, "amount")
        self._value -= amount
        return self

    def increment(
        self,
        amount: NumericValue = 1,
    ) -> "Histogram":
        return self.add_value(amount)

    def decrement(
        self,
        amount: NumericValue = 1,
    ) -> "Histogram":
        return self.subtract_value(amount)

    # ==========================================================================
    # Histogram operations
    # ==========================================================================

    def observe(self, value: NumericValue) -> "Histogram":
        self._validate_numeric(value, "observation")
        self._observations.append(float(value))
        return self

    def record(self, value: NumericValue) -> "Histogram":
        return self.observe(value)

    def count(self) -> int:
        return len(self._observations)

    def sum(self) -> float:
        return float(sum(self._observations))

    def min(self) -> float | None:
        if not self._observations:
            return None
        return min(self._observations)

    def max(self) -> float | None:
        if not self._observations:
            return None
        return max(self._observations)

    def mean(self) -> float | None:
        if not self._observations:
            return None
        return self.sum() / self.count()

    def percentile(
        self,
        percentile: float,
    ) -> float | None:
        if (
            isinstance(percentile, bool)
            or not isinstance(percentile, (int, float))
        ):
            raise TypeError(
                "percentile must be int or float."
            )

        if not 0 <= percentile <= 100:
            raise ValueError(
                "percentile must be between 0 and 100."
            )

        if not self._observations:
            return None

        values = sorted(self._observations)

        if len(values) == 1:
            return values[0]

        position = (
            (len(values) - 1)
            * (percentile / 100.0)
        )

        lower = int(position)
        upper = min(
            lower + 1,
            len(values) - 1,
        )

        if lower == upper:
            return values[lower]

        fraction = position - lower

        return (
            values[lower]
            + (
                values[upper] - values[lower]
            ) * fraction
        )

    def bucket_counts(self) -> dict[float, int]:
        counts = {
            bucket: 0
            for bucket in self._buckets
        }

        for observation in self._observations:
            for bucket in self._buckets:
                if observation <= bucket:
                    counts[bucket] += 1

        return counts

    def clear_observations(self) -> "Histogram":
        self._observations.clear()
        return self

    # ==========================================================================
    # Lifecycle operations
    # ==========================================================================

    def enable(self) -> "Histogram":
        if self._state is not None:
            method = getattr(
                self._state,
                "enable",
                None,
            )
            if callable(method):
                method()
        return self

    def disable(self) -> "Histogram":
        if self._state is not None:
            method = getattr(
                self._state,
                "disable",
                None,
            )
            if callable(method):
                method()
        return self

    def activate(self) -> "Histogram":
        if self._state is not None:
            method = getattr(
                self._state,
                "activate",
                None,
            )
            if callable(method):
                method()
        return self

    def deactivate(self) -> "Histogram":
        if self._state is not None:
            method = getattr(
                self._state,
                "deactivate",
                None,
            )
            if callable(method):
                method()
        return self

    # ==========================================================================
    # Metadata operations
    # ==========================================================================

    def set_metadata(
        self,
        key: str,
        value: Any,
    ) -> "Histogram":
        self._metadata[key] = value
        return self

    def get_metadata(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        return self._metadata.get(
            key,
            default,
        )

    def remove_metadata(
        self,
        key: str,
    ) -> "Histogram":
        self._metadata.pop(key, None)
        return self

    def clear_metadata(self) -> "Histogram":
        self._metadata.clear()
        return self

    # ==========================================================================
    # Annotation operations
    # ==========================================================================

    def set_annotation(
        self,
        key: str,
        value: Any,
    ) -> "Histogram":
        self._annotations[key] = value
        return self

    def get_annotation(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        return self._annotations.get(
            key,
            default,
        )

    def remove_annotation(
        self,
        key: str,
    ) -> "Histogram":
        self._annotations.pop(key, None)
        return self

    def clear_annotations(self) -> "Histogram":
        self._annotations.clear()
        return self

    # ==========================================================================
    # Tag operations
    # ==========================================================================

    def set_tag(
        self,
        key: str,
        value: Any,
    ) -> "Histogram":
        self._tags[key] = value
        return self

    def get_tag(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        return self._tags.get(
            key,
            default,
        )

    def remove_tag(
        self,
        key: str,
    ) -> "Histogram":
        self._tags.pop(key, None)
        return self

    def clear_tags(self) -> "Histogram":
        self._tags.clear()
        return self

    # ==========================================================================
    # Serialization
    # ==========================================================================

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self._name,
            "value": self._value,
            "description": self._description,
            "unit": self._unit,
            "buckets": tuple(self._buckets),
            "observations": list(
                self._observations
            ),
            "metadata": deepcopy(
                self._metadata
            ),
            "annotations": deepcopy(
                self._annotations
            ),
            "tags": deepcopy(
                self._tags
            ),
            "state": deepcopy(
                self._state
            ),
        }

    def to_json(
        self,
        **kwargs: Any,
    ) -> str:
        return json.dumps(
            self.to_dict(),
            default=str,
            **kwargs,
        )

    # ==========================================================================
    # Snapshot / restore
    # ==========================================================================

    def snapshot(self) -> dict[str, Any]:
        return deepcopy(
            self.to_dict()
        )

    def restore(
        self,
        snapshot: dict[str, Any],
    ) -> "Histogram":
        if not isinstance(snapshot, dict):
            raise TypeError(
                "snapshot must be dict."
            )

        self._name = snapshot.get(
            "name",
            DEFAULT_NAME,
        )

        self._value = snapshot.get(
            "value",
            DEFAULT_VALUE,
        )

        self._description = snapshot.get(
            "description",
            DEFAULT_DESCRIPTION,
        )

        self._unit = snapshot.get(
            "unit",
            DEFAULT_UNIT,
        )

        self._buckets = tuple(
            snapshot.get(
                "buckets",
                DEFAULT_BUCKETS,
            )
        )

        self._observations = list(
            snapshot.get(
                "observations",
                [],
            )
        )

        self._metadata = deepcopy(
            snapshot.get(
                "metadata",
                DEFAULT_METADATA,
            )
        )

        self._annotations = deepcopy(
            snapshot.get(
                "annotations",
                DEFAULT_ANNOTATIONS,
            )
        )

        self._tags = deepcopy(
            snapshot.get(
                "tags",
                DEFAULT_TAGS,
            )
        )

        # Missing state means "leave current state unchanged".
        if "state" in snapshot:
            self._state = deepcopy(
                snapshot["state"]
            )

        self.validate()

        return self

    # ==========================================================================
    # Copy / clone
    # ==========================================================================

    def copy(self) -> "Histogram":
        return deepcopy(self)

    def clone(self) -> "Histogram":
        return self.copy()

    # ==========================================================================
    # Validation
    # ==========================================================================

    def validate(self) -> bool:
        self._validate_basic_configuration()

        if not isinstance(
            self._buckets,
            tuple,
        ):
            raise TypeError(
                "buckets must be tuple."
            )

        for bucket in self._buckets:
            self._validate_numeric(
                bucket,
                "bucket",
            )

        if (
            tuple(sorted(self._buckets))
            != self._buckets
        ):
            raise HistogramValidationError(
                "buckets must be sorted "
                "in ascending order."
            )

        if (
            len(set(self._buckets))
            != len(self._buckets)
        ):
            raise HistogramValidationError(
                "buckets must not contain "
                "duplicates."
            )

        if not isinstance(
            self._metadata,
            dict,
        ):
            raise TypeError(
                "metadata must be dict."
            )

        if not isinstance(
            self._annotations,
            dict,
        ):
            raise TypeError(
                "annotations must be dict."
            )

        if not isinstance(
            self._tags,
            dict,
        ):
            raise TypeError(
                "tags must be dict."
            )

        if not isinstance(
            self._observations,
            list,
        ):
            raise TypeError(
                "observations must be list."
            )

        for observation in self._observations:
            self._validate_numeric(
                observation,
                "observation",
            )

        if (
            self._state is not None
            and not isinstance(
                self._state,
                MetricState,
            )
        ):
            raise TypeError(
                "state must be MetricState or None."
            )

        return True

    # ==========================================================================
    # Equality / hashing
    # ==========================================================================

    def __eq__(
        self,
        other: object,
    ) -> bool:
        if not isinstance(
            other,
            Histogram,
        ):
            return NotImplemented

        return (
            self._name == other._name
            and self._value == other._value
            and self._description
            == other._description
            and self._unit == other._unit
            and self._buckets
            == other._buckets
            and self._observations
            == other._observations
            and self._metadata
            == other._metadata
            and self._annotations
            == other._annotations
            and self._tags
            == other._tags
            and self._state
            == other._state
        )

    def __hash__(self) -> int:
        return hash(
            (
                self._name,
                self._value,
                self._description,
                self._unit,
                self._buckets,
                tuple(self._observations),
                json.dumps(
                    self._metadata,
                    sort_keys=True,
                    default=str,
                ),
                json.dumps(
                    self._annotations,
                    sort_keys=True,
                    default=str,
                ),
                json.dumps(
                    self._tags,
                    sort_keys=True,
                    default=str,
                ),
            )
        )

    # ==========================================================================
    # Representation
    # ==========================================================================

    def __repr__(self) -> str:
        return (
            "Histogram("
            f"name={self._name!r}, "
            f"value={self._value!r}, "
            f"description={self._description!r}, "
            f"unit={self._unit!r}, "
            f"buckets={self._buckets!r}"
            ")"
        )

    def __str__(self) -> str:
        return str(self._value)

    # ==========================================================================
    # Internal helpers
    # ==========================================================================

    def _validate_basic_configuration(
        self,
    ) -> None:
        if (
            self._name is not None
            and not isinstance(
                self._name,
                str,
            )
        ):
            raise TypeError(
                "name must be str or None."
            )

        self._validate_numeric(
            self._value,
            "value",
        )

        if (
            self._description is not None
            and not isinstance(
                self._description,
                str,
            )
        ):
            raise TypeError(
                "description must be str or None."
            )

        if (
            self._unit is not None
            and not isinstance(
                self._unit,
                str,
            )
        ):
            raise TypeError(
                "unit must be str or None."
            )

    @staticmethod
    def _validate_numeric(
        value: Any,
        field: str,
    ) -> None:
        if (
            isinstance(value, bool)
            or not isinstance(
                value,
                (int, float),
            )
        ):
            raise HistogramValidationError(
                f"{field} must be int or float."
            )

    def _apply_state_reset(self) -> None:
        if self._state is not None:
            method = getattr(
                self._state,
                "reset",
                None,
            )

            if callable(method):
                method()


# ==============================================================================
# Part N. Public API
# ==============================================================================

__all__ = [
    "DEFAULT_VALUE",
    "DEFAULT_NAME",
    "DEFAULT_DESCRIPTION",
    "DEFAULT_UNIT",
    "DEFAULT_BUCKETS",
    "DEFAULT_METADATA",
    "DEFAULT_ANNOTATIONS",
    "DEFAULT_TAGS",
    "NumericValue",
    "BucketValue",
    "BucketCollection",
    "Metadata",
    "Annotation",
    "Tag",
    "HistogramValidationError",
    "Histogram",
]
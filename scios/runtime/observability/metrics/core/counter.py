# ==============================================================================
# Counter
# ==============================================================================

from __future__ import annotations


# ==============================================================================
# Part 1. Imports
# ==============================================================================

import copy
import json
from dataclasses import dataclass
from typing import Any, TypeAlias

from .metric import (
    Metric,
    MetricType,
    MetricUnit,
    MetricValidationError,
)



# ==============================================================================
# Part 2. Constants
# ==============================================================================

DEFAULT_COUNTER_VALUE: int = 0

DEFAULT_COUNTER_TYPE: MetricType = MetricType.COUNTER

DEFAULT_COUNTER_UNIT: MetricUnit = MetricUnit.NONE


# ==============================================================================
# Part 3. Type Aliases
# ==============================================================================

CounterValue: TypeAlias = int


# ==============================================================================
# Part 4. Exceptions
# ==============================================================================

class CounterValidationError(MetricValidationError):
    """
    Raised when a Counter violates counter-specific validation rules.
    """

    pass



# ==============================================================================
# Part 5. Dataclass
# ==============================================================================

@dataclass(
    slots=True,
    eq=False,
    repr=False,
)
class Counter(Metric):
    """Runtime counter metric."""

    value: CounterValue = DEFAULT_COUNTER_VALUE
    metric_type: MetricType = DEFAULT_COUNTER_TYPE
    unit: MetricUnit = DEFAULT_COUNTER_UNIT

    # ==========================================================================
    # Part 6. Constructor Validation
    # ==========================================================================

    def __post_init__(self) -> None:
        # IMPORTANT:
        # Do not use zero-argument super() here because @dataclass(slots=True)
        # recreates the class and breaks the __class__ closure used by super().
        Metric.__post_init__(self)

        if self.metric_type is not MetricType.COUNTER:
            raise CounterValidationError(
                "Counter metric_type must be MetricType.COUNTER."
            )

        if isinstance(self.value, bool) or not isinstance(
            self.value,
            int,
        ):
            raise CounterValidationError(
                "Counter value must be an integer."
            )

        if self.value < 0:
            raise CounterValidationError(
                "Counter value cannot be negative."
            )

    # ==========================================================================
    # Part 7. Properties
    # ==========================================================================

    @property
    def is_counter(self) -> bool:
        return self.metric_type is MetricType.COUNTER

    # ==========================================================================
    # Part 8. Counter Operations
    # ==========================================================================

    def increment(self, amount: int = 1) -> int:
        if isinstance(amount, bool) or not isinstance(amount, int):
            raise CounterValidationError(
                "Increment amount must be an integer."
            )

        if amount < 0:
            raise CounterValidationError(
                "Increment amount cannot be negative."
            )

        self.value += amount
        return self.value


    def decrement(self, amount: int = 1) -> int:
        if isinstance(amount, bool) or not isinstance(amount, int):
            raise CounterValidationError(
                "Decrement amount must be an integer."
            )

        if amount < 0:
            raise CounterValidationError(
                "Decrement amount cannot be negative."
            )

        if self.value - amount < 0:
            raise CounterValidationError(
                "Counter value cannot be negative."
            )

        self.value -= amount
        return self.value


    def reset(self) -> int:
        self.value = DEFAULT_COUNTER_VALUE
        return self.value

    # ==========================================================================
    # Part 9. State / Lifecycle
    # ==========================================================================

    def enable(self) -> Counter:
        result = Metric.enable(self)
        return result if result is not None else self

    def disable(self) -> Counter:
        result = Metric.disable(self)
        return result if result is not None else self

    def activate(self) -> Counter:
        result = Metric.activate(self)
        return result if result is not None else self

    def deactivate(self) -> Counter:
        result = Metric.deactivate(self)
        return result if result is not None else self

    def archive(self) -> Counter:
        result = Metric.archive(self)
        return result if result is not None else self

    # ==========================================================================
    # Part 10. Metadata API
    # ==========================================================================

    @property
    def labels(self) -> Any:
        return getattr(self, "_labels", {})

    @property
    def attributes(self) -> Any:
        return getattr(self, "_attributes", {})


    @property
    def hooks(self) -> Any:
        return getattr(self, "_hooks", {})


    # ==========================================================================
    # Part 11. Serialization
    # ==========================================================================

    def to_dict(self) -> dict[str, Any]:
        payload = Metric.to_dict(self)

        payload["value"] = self.value
        payload["metric_type"] = self.metric_type.value
        payload["unit"] = self.unit.value

        return payload


    @classmethod
    def from_dict(
        cls,
        payload: dict[str, Any],
    ) -> Counter:
        if not isinstance(payload, dict):
            raise CounterValidationError(
                "Counter payload must be a dictionary."
            )

        data = copy.deepcopy(payload)

        metric_type = data.pop(
            "metric_type",
            DEFAULT_COUNTER_TYPE,
        )

        if isinstance(metric_type, str):
            metric_type = MetricType(metric_type)

        if metric_type is not MetricType.COUNTER:
            raise CounterValidationError(
                "Counter metric_type must be 'counter'."
            )

        unit = data.pop(
            "unit",
            DEFAULT_COUNTER_UNIT,
        )

        if isinstance(unit, str):
            unit = MetricUnit(unit)

        constructor_fields = {
            "name",
            "value",
            "metric_type",
            "unit",
        }

        data = {
            key: value
            for key, value in data.items()
            if key in constructor_fields
        }

        data["metric_type"] = metric_type
        data["unit"] = unit

        counter = cls(**data)

        # ------------------------------------------------------------------
        # Restore Metric metadata after construction.
        # ------------------------------------------------------------------

        metadata = copy.deepcopy(payload)

        if "labels" in metadata:
            counter.labels.clear()

            for key, value in metadata["labels"].items():
                counter.labels.add(
                    key,
                    value,
                )

        if "attributes" in metadata:
            counter.attributes.clear()

            for key, value in metadata["attributes"].items():
                counter.attributes.add(
                    key,
                    value,
                )

        if "annotations" in metadata:
            counter.annotations.clear()

            for key, value in metadata["annotations"].items():
                counter.annotations.add(
                    key,
                    value,
                )

        if "tags" in metadata:
            counter.tags.clear()

            for tag in metadata["tags"]:
                counter.tags.add(tag)

        return counter


    def to_json(self) -> str:
        return json.dumps(
            self.to_dict(),
            sort_keys=True,
        )


    @classmethod
    def from_json(
        cls,
        payload: str,
    ) -> Counter:
        if not isinstance(payload, str):
            raise CounterValidationError(
                "Counter JSON payload must be a string."
            )

        try:
            data = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise CounterValidationError(
                "Invalid Counter JSON payload."
            ) from exc

        if not isinstance(data, dict):
            raise CounterValidationError(
                "Counter JSON payload must decode to a dictionary."
            )

        return cls.from_dict(data)



    # ==========================================================================
    # Part 12. Copy / Clone
    # ==========================================================================

    def copy(self) -> Counter:
        return copy.copy(self)

    def clone(self) -> Counter:
        return copy.deepcopy(self)

    # ==========================================================================
    # Part 13. Snapshot
    # ==========================================================================

    def snapshot(self) -> dict[str, Any]:
        return copy.deepcopy(self.to_dict())

    # ==========================================================================
    # Part 14. Restore
    # ==========================================================================

    def restore(self, snapshot: dict[str, Any]) -> Counter:
        restored = type(self).from_dict(snapshot)

        for field in (
            "name",
            "value",
            "metric_type",
            "unit",
        ):
            if hasattr(restored, field):
                setattr(self, field, getattr(restored, field))

        for field in (
            "_labels",
            "_attributes",
            "_annotations",
            "_tags",
            "_hooks",
        ):
            if hasattr(restored, field):
                setattr(
                    self,
                    field,
                    copy.deepcopy(getattr(restored, field)),
                )

        return self

    # ==========================================================================
    # Part 15. Representation
    # ==========================================================================

    def __repr__(self) -> str:
        return (
            f"Counter("
            f"name={self.name!r}, "
            f"value={self.value!r}, "
            f"type={self.metric_type.value!r}, "
            f"unit={self.unit.value!r}"
            f")"
        )

    def __str__(self) -> str:
        return (
            f"Counter("
            f"name={self.name}, "
            f"value={self.value}, "
            f"type={self.metric_type.value}, "
            f"unit={self.unit.value}"
            f")"
        )


# ==============================================================================
# Part 16. Public API
# ==============================================================================

__all__ = [
    "DEFAULT_COUNTER_VALUE",
    "DEFAULT_COUNTER_TYPE",
    "DEFAULT_COUNTER_UNIT",
    "CounterValue",
    "CounterValidationError",
    "Counter",
]

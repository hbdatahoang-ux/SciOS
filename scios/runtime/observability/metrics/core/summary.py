# ==============================================================================

# Summary

# ==============================================================================

"""
A Summary represents a metric that aggregates observations into a statistical
summary.

Python 3.11+
"""

from __future__ import annotations

# ==============================================================================

# Part 1. Imports

# ==============================================================================

from copy import deepcopy
import json
from typing import Any, Final, TypeAlias

from .metric_state import MetricState



# ==============================================================================
# Part 2. Constants
# ==============================================================================

DEFAULT_VALUE: Final[float] = 0.0

DEFAULT_NAME: Final[str | None] = None

DEFAULT_DESCRIPTION: Final[str | None] = None

DEFAULT_UNIT: Final[str | None] = None

DEFAULT_METADATA: Final[dict[str, Any]] = {}

DEFAULT_ANNOTATIONS: Final[dict[str, Any]] = {}

DEFAULT_TAGS: Final[dict[str, Any]] = {}


# ==============================================================================
# Part 3. Type Aliases
# ==============================================================================

SummaryValue: TypeAlias = int | float

SummaryMetadata: TypeAlias = dict[str, Any]

SummaryAnnotations: TypeAlias = dict[str, Any]

SummaryTags: TypeAlias = dict[str, Any]


# ==============================================================================
# Part 4. Exceptions
# ==============================================================================

class SummaryValidationError(ValueError):
    """
    Raised when a Summary contains invalid internal state.
    """

    pass


# ==============================================================================
# Part 5. Summary class
# ==============================================================================

class Summary:
    """
    SciOS Runtime Summary.

    Represents a metric value together with descriptive metadata,
    annotations, tags, and runtime state.
    """

    # ==========================================================================
    # Constructor
    # ==========================================================================

    def __init__(
        self,
        value: SummaryValue = DEFAULT_VALUE,
        *,
        name: str | None = DEFAULT_NAME,
        description: str | None = DEFAULT_DESCRIPTION,
        unit: str | None = DEFAULT_UNIT,
        metadata: SummaryMetadata | None = None,
        annotations: SummaryAnnotations | None = None,
        tags: SummaryTags | None = None,
        state: Any = None,
    ) -> None:
        self._name = name
        self._value = value
        self._description = description
        self._unit = unit

        self._metadata = (
            {} if metadata is None else dict(metadata)
        )

        self._annotations = (
            {} if annotations is None else dict(annotations)
        )

        self._tags = (
            {} if tags is None else dict(tags)
        )

        self._state = state

    # ==========================================================================
    # Properties
    # ==========================================================================

    @property
    def name(self) -> str | None:
        return self._name

    @name.setter
    def name(self, value: str | None) -> None:
        self._name = value

    @property
    def value(self) -> SummaryValue:
        return self._value

    @value.setter
    def value(self, value: SummaryValue) -> None:
        self._value = value

    @property
    def description(self) -> str | None:
        return self._description

    @description.setter
    def description(self, value: str | None) -> None:
        self._description = value

    @property
    def unit(self) -> str | None:
        return self._unit

    @unit.setter
    def unit(self, value: str | None) -> None:
        self._unit = value

    @property
    def metadata(self) -> SummaryMetadata:
        return self._metadata

    @property
    def annotations(self) -> SummaryAnnotations:
        return self._annotations

    @property
    def tags(self) -> SummaryTags:
        return self._tags

    @property
    def state(self) -> Any:
        return self._state

    @state.setter
    def state(self, value: Any) -> None:
        self._state = value

    # ==========================================================================
    # Value operations
    # ==========================================================================

    def set(self, value: SummaryValue) -> Summary:
        self._value = value
        return self

    def reset(self) -> Summary:
        self._value = DEFAULT_VALUE
        return self

    def add(self, amount: SummaryValue) -> Summary:
        self._value += amount
        return self

    def subtract(self, amount: SummaryValue) -> Summary:
        self._value -= amount
        return self

    def increment(self, amount: SummaryValue = 1) -> Summary:
        return self.add(amount)

    def decrement(self, amount: SummaryValue = 1) -> Summary:
        return self.subtract(amount)

    # ==========================================================================
    # Lifecycle operations
    # ==========================================================================

    def enable(self) -> Summary:
        if self._state is not None and hasattr(self._state, "enable"):
            self._state.enable()
        return self

    def disable(self) -> Summary:
        if self._state is not None and hasattr(self._state, "disable"):
            self._state.disable()
        return self

    def activate(self) -> Summary:
        if self._state is not None and hasattr(self._state, "activate"):
            self._state.activate()
        return self

    def deactivate(self) -> Summary:
        if self._state is not None and hasattr(self._state, "deactivate"):
            self._state.deactivate()
        return self

    # ==========================================================================
    # Metadata / annotation / tag operations
    # ==========================================================================

    def set_metadata(self, key: str, value: Any) -> Summary:
        self._metadata[key] = value
        return self

    def get_metadata(self, key: str, default: Any = None) -> Any:
        return self._metadata.get(key, default)

    def remove_metadata(self, key: str) -> Summary:
        self._metadata.pop(key, None)
        return self

    def clear_metadata(self) -> Summary:
        self._metadata.clear()
        return self

    def set_annotation(self, key: str, value: Any) -> Summary:
        self._annotations[key] = value
        return self

    def get_annotation(self, key: str, default: Any = None) -> Any:
        return self._annotations.get(key, default)

    def remove_annotation(self, key: str) -> Summary:
        self._annotations.pop(key, None)
        return self

    def clear_annotations(self) -> Summary:
        self._annotations.clear()
        return self

    def set_tag(self, key: str, value: Any) -> Summary:
        self._tags[key] = value
        return self

    def get_tag(self, key: str, default: Any = None) -> Any:
        return self._tags.get(key, default)

    def remove_tag(self, key: str) -> Summary:
        self._tags.pop(key, None)
        return self

    def clear_tags(self) -> Summary:
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
            "metadata": dict(self._metadata),
            "annotations": dict(self._annotations),
            "tags": dict(self._tags),
            "state": (
                self._state.to_dict()
                if self._state is not None
                and hasattr(self._state, "to_dict")
                else self._state
            ),
        }

    def to_json(self, **kwargs: Any) -> str:
        return json.dumps(self.to_dict(), **kwargs)

    # ==========================================================================
    # Snapshot / restore
    # ==========================================================================

    def snapshot(self) -> dict[str, Any]:
        return deepcopy(self.to_dict())

    def restore(self, snapshot: dict[str, Any]) -> Summary:
        self._name = snapshot.get("name")
        self._value = snapshot.get("value", DEFAULT_VALUE)
        self._description = snapshot.get("description")
        self._unit = snapshot.get("unit")

        self._metadata = dict(snapshot.get("metadata", {}))
        self._annotations = dict(snapshot.get("annotations", {}))
        self._tags = dict(snapshot.get("tags", {}))

        return self

    # ==========================================================================
    # Copy / clone
    # ==========================================================================

    def copy(self) -> Summary:
        return deepcopy(self)

    def clone(self) -> Summary:
        return self.copy()

    # ==========================================================================
    # Validation
    # ==========================================================================

    def validate(self) -> bool:
        if self._name is not None and not isinstance(
            self._name,
            str,
        ):
            raise SummaryValidationError(
                "name must be str or None."
            )

        if not isinstance(
            self._value,
            (int, float),
        ) or isinstance(
            self._value,
            bool,
        ):
            raise SummaryValidationError(
                "value must be int or float."
            )

        if self._description is not None and not isinstance(
            self._description,
            str,
        ):
            raise SummaryValidationError(
                "description must be str or None."
            )

        if self._unit is not None and not isinstance(
            self._unit,
            str,
        ):
            raise SummaryValidationError(
                "unit must be str or None."
            )

        if not isinstance(self._metadata, dict):
            raise SummaryValidationError(
                "metadata must be dict."
            )

        if self._annotations is None:
            raise SummaryValidationError(
                "annotations must not be None."
            )

        if self._tags is None:
            raise SummaryValidationError(
                "tags must not be None."
            )

        return True

    # ==========================================================================
    # Equality / hashing
    # ==========================================================================

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Summary):
            return NotImplemented

        return self.to_dict() == other.to_dict()

    def __hash__(self) -> int:
        return hash(
            (
                self._name,
                self._value,
                self._description,
                self._unit,
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
            f"Summary("
            f"name={self._name!r}, "
            f"value={self._value!r}, "
            f"description={self._description!r}, "
            f"unit={self._unit!r}"
            f")"
        )

    def __str__(self) -> str:
        return str(self._value)


# ==============================================================================
# Part N. Public API
# ==============================================================================

__all__ = [
    # ------------------------------------------------------------------
    # Constants
    # ------------------------------------------------------------------

    "DEFAULT_VALUE",
    "DEFAULT_NAME",
    "DEFAULT_DESCRIPTION",
    "DEFAULT_UNIT",
    "DEFAULT_METADATA",
    "DEFAULT_ANNOTATIONS",
    "DEFAULT_TAGS",

    # ------------------------------------------------------------------
    # Type Aliases
    # ------------------------------------------------------------------

    "SummaryValue",
    "SummaryMetadata",
    "SummaryAnnotations",
    "SummaryTags",

    # ------------------------------------------------------------------
    # Exceptions
    # ------------------------------------------------------------------

    "SummaryValidationError",

    # ------------------------------------------------------------------
    # Main class
    # ------------------------------------------------------------------

    "Summary",
]

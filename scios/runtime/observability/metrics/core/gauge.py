# ==============================================================================
# Gauge
# ==============================================================================

"""
A Gauge represents a metric whose value may increase or decrease freely.

Python 3.11+
"""

from __future__ import annotations

# ==============================================================================
# Part 1. Imports
# ==============================================================================

import json
from collections.abc import Iterator
from copy import deepcopy
from typing import Any, Final, TypeAlias

from .metric_state import MetricState

# ==============================================================================
# Part 2. Constants
# ==============================================================================

__version__: Final[str] = "0.1.0"

DEFAULT_VALUE: Final[float] = 0.0


# ==============================================================================
# Part 3. Type Aliases
# ==============================================================================

Number: TypeAlias = int | float

Metadata: TypeAlias = dict[str, Any]


# ==============================================================================
# Part 4. Exceptions
# ==============================================================================

class GaugeError(RuntimeError):
    """
    Base exception for Gauge errors.
    """


class GaugeValidationError(
    GaugeError,
    ValueError,
):
    """
    Raised when Gauge configuration or value is invalid.
    """


# ==============================================================================
# Part 4B. Annotation / Tag Containers
# ==============================================================================


class _AnnotationStore:
    """
    Mutable key-value annotation store.
    """

    def __init__(
        self,
        initial: dict[str, Any] | None = None,
    ) -> None:
        self._data: dict[str, Any] = (
            deepcopy(initial)
            if initial is not None
            else {}
        )

    def add(
        self,
        key: str,
        value: Any,
    ) -> None:
        self._data[key] = value

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        return self._data.get(key, default)

    def remove(
        self,
        key: str,
    ) -> Any:
        return self._data.pop(key)

    def clear(self) -> None:
        self._data.clear()

    def update(
        self,
        values: dict[str, Any],
    ) -> None:
        self._data.update(values)

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __setitem__(
        self,
        key: str,
        value: Any,
    ) -> None:
        self._data[key] = value

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def to_dict(self) -> dict[str, Any]:
        return deepcopy(self._data)


class _TagStore:
    """
    Mutable tag store.

    Supports both set-like ``add()`` and
    mapping-style item assignment.
    """

    def __init__(
        self,
        initial: dict[str, Any] | None = None,
    ) -> None:
        self._data: dict[str, Any] = (
            deepcopy(initial)
            if initial is not None
            else {}
        )

    def add(
        self,
        value: str,
    ) -> None:
        self._data[value] = value

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        return self._data.get(key, default)

    def remove(
        self,
        key: str,
    ) -> Any:
        return self._data.pop(key)

    def clear(self) -> None:
        self._data.clear()

    def update(
        self,
        values: dict[str, Any],
    ) -> None:
        self._data.update(values)

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __setitem__(
        self,
        key: str,
        value: Any,
    ) -> None:
        self._data[key] = value

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def to_dict(self) -> dict[str, Any]:
        return deepcopy(self._data)

# ==============================================================================
# Part 5. Constructor
# ==============================================================================

class Gauge:
    """
    Runtime Gauge metric.

    A Gauge stores a value that can move freely in either direction.

    Parameters
    ----------
    name:
        Optional metric name.

    value:
        Initial numeric value.

    description:
        Optional human-readable description.

    unit:
        Optional measurement unit.

    metadata:
        Optional metadata dictionary.
    """

    def __init__(
        self,
        name: str | None = None,
        value: Number = DEFAULT_VALUE,
        *,
        description: str | None = None,
        unit: str | None = None,
        metadata: Metadata | None = None,
    ) -> None:

        if name is not None and not isinstance(
            name,
            str,
        ):
            raise TypeError(
                "name must be str or None."
            )

        if not isinstance(
            value,
            (int, float),
        ) or isinstance(value, bool):
            raise TypeError(
                "value must be int or float."
            )

        if description is not None and not isinstance(
            description,
            str,
        ):
            raise TypeError(
                "description must be str or None."
            )

        if unit is not None and not isinstance(
            unit,
            str,
        ):
            raise TypeError(
                "unit must be str or None."
            )

        if metadata is not None and not isinstance(
            metadata,
            dict,
        ):
            raise TypeError(
                "metadata must be dict or None."
            )

        self._name: str | None = name

        self._value: Number = value

        self._description: str | None = description

        self._unit: str | None = unit

        self._metadata: Metadata = (
            dict(metadata)
            if metadata is not None
            else {}
        )

        self._annotations = _AnnotationStore()

        self._tags = _TagStore()


        self._state = MetricState()

    @property
    def annotations(self) -> _AnnotationStore:
        """
        Return mutable metric annotations.
        """
        return self._annotations

    @property
    def tags(self) -> _TagStore:
        """
        Return mutable metric tags.
        """
        return self._tags
# ==============================================================================
# Part 6. Properties
# ==============================================================================

    @property
    def name(self) -> str | None:
        """
        Return the metric name.
        """
        return self._name

    @property
    def value(self) -> Number:
        """
        Return the current gauge value.
        """
        return self._value

    @property
    def description(self) -> str | None:
        """
        Return the metric description.
        """
        return self._description

    @property
    def unit(self) -> str | None:
        """
        Return the metric unit.
        """
        return self._unit

    @property
    def metadata(self) -> Metadata:
        """
        Return a copy of metric metadata.
        """
        return dict(self._metadata)

    @property
    def state(self) -> MetricState:
        """
        Return the metric runtime state.
        """
        return self._state

# ==============================================================================
# Part 7. Value Operations
# ==============================================================================

    def set(self, value: Number) -> Number:
        """
        Set the gauge value.
        """
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise TypeError("value must be int or float.")

        self._value = value
        return self._value

    def increment(self, amount: Number = 1) -> Number:
        """
        Increase the gauge value.
        """
        if not isinstance(amount, (int, float)) or isinstance(amount, bool):
            raise TypeError("amount must be int or float.")

        self._value += amount
        return self._value

    def decrement(self, amount: Number = 1) -> Number:
        """
        Decrease the gauge value.
        """
        if not isinstance(amount, (int, float)) or isinstance(amount, bool):
            raise TypeError("amount must be int or float.")

        self._value -= amount
        return self._value

    def add(self, amount: Number) -> Number:
        """
        Add a numeric amount to the gauge value.
        """
        return self.increment(amount)

    def subtract(self, amount: Number) -> Number:
        """
        Subtract a numeric amount from the gauge value.
        """
        return self.decrement(amount)


# ==============================================================================
# Part 8. State
# ==============================================================================

    def enable(self) -> None:
        """
        Enable the gauge.
        """
        self._state.enable()

    def disable(self) -> None:
        """
        Disable the gauge.
        """
        self._state.disable()

    def activate(self) -> None:
        """
        Activate the gauge.
        """
        self._state.activate()

    def deactivate(self) -> None:
        """
        Deactivate the gauge.
        """
        self._state.deactivate()

    def is_enabled(self) -> bool:
        """
        Return whether the gauge is enabled.
        """
        return self._state.is_enabled()

    def is_active(self) -> bool:
        """
        Return whether the gauge is active.
        """
        return self._state.is_active()

    def is_healthy(self) -> bool:
        """
        Return whether the gauge is healthy.
        """
        return self._state.is_healthy()

    def is_warning(self) -> bool:
        """
        Return whether the gauge is in warning state.
        """
        return self._state.is_warning()

    def is_error(self) -> bool:
        """
        Return whether the gauge is in error state.
        """
        return self._state.is_error()

    def is_stale(self) -> bool:
        """
        Return whether the gauge is stale.
        """
        return self._state.is_stale()


# ==============================================================================
# Part 9. Lifecycle
# ==============================================================================

    def reset(self) -> None:
        """
        Reset the gauge value and runtime state.
        """
        self._value = DEFAULT_VALUE
        self._state.reset()

    def archive(self) -> None:
        """
        Archive the gauge.
        """
        self._state.archive()

    def restore(self) -> None:
        """
        Restore the gauge to active state.
        """
        self._state.restore()


# ==============================================================================
# Part 10. Annotations & Tags
# ==============================================================================

    def set_description(
        self,
        description: str | None,
    ) -> None:
        """
        Set the metric description.
        """
        if description is not None and not isinstance(
            description,
            str,
        ):
            raise TypeError(
                "description must be str or None."
            )

        self._description = description

    def set_unit(
        self,
        unit: str | None,
    ) -> None:
        """
        Set the metric unit.
        """
        if unit is not None and not isinstance(unit, str):
            raise TypeError("unit must be str or None.")

        self._unit = unit

    def set_metadata(
        self,
        metadata: Metadata | None,
    ) -> None:
        """
        Replace metric metadata.
        """
        if metadata is not None and not isinstance(metadata, dict):
            raise TypeError("metadata must be dict or None.")

        self._metadata = (
            dict(metadata)
            if metadata is not None
            else {}
        )

    def update_metadata(
        self,
        **values: Any,
    ) -> None:
        """
        Update metric metadata.
        """
        self._metadata.update(values)


# ==============================================================================
# Part 11. Snapshot
# ==============================================================================

    def snapshot(self) -> dict[str, Any]:
        """
        Return an independent Gauge snapshot.
        """
        return {
            "name": self._name,
            "value": self._value,
            "description": self._description,
            "unit": self._unit,
            "metadata": deepcopy(self._metadata),
            "annotations": self._annotations.to_dict(),
            "tags": self._tags.to_dict(),
            "state": (
                self._state.to_dict()
                if hasattr(self._state, "to_dict")
                else deepcopy(self._state)
            ),
        }
# ==============================================================================
# Part 12. Serialization
# ==============================================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize Gauge to a dictionary.
        """
        return {
            "name": self._name,
            "value": self._value,
            "description": self._description,
            "unit": self._unit,
            "metadata": deepcopy(self._metadata),
            "annotations": self._annotations.to_dict(),
            "tags": self._tags.to_dict(),
            "state": (
                self._state.to_dict()
                if hasattr(self._state, "to_dict")
                else deepcopy(self._state)
            ),
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "Gauge":
        """
        Restore Gauge from a dictionary.
        """
        gauge = cls(
            name=data.get("name"),
            value=data.get(
                "value",
                DEFAULT_VALUE,
            ),
            description=data.get("description"),
            unit=data.get("unit"),
            metadata=deepcopy(
                data.get("metadata", {})
            ),
        )

        gauge._annotations = _AnnotationStore(
            data.get("annotations", {})
        )

        gauge._tags = _TagStore(
            data.get("tags", {})
        )

        state_data = data.get("state")

        if state_data is not None:
            if hasattr(
                MetricState,
                "from_dict",
            ):
                gauge._state = MetricState.from_dict(
                    state_data
                )
            elif hasattr(
                gauge._state,
                "restore",
            ):
                gauge._state.restore(state_data)

        return gauge

    def to_json(self) -> str:
        """
        Serialize Gauge to JSON.
        """
        return json.dumps(
            self.to_dict(),
            sort_keys=True,
        )

    @classmethod
    def from_json(
        cls,
        data: str,
    ) -> "Gauge":
        """
        Restore Gauge from JSON.
        """
        return cls.from_dict(
            json.loads(data)
        )



# ==============================================================================
# Part 13. Copy
# ==============================================================================

    def copy(self) -> "Gauge":
        """
        Return an independent copy.
        """
        return self.from_dict(
            self.to_dict()
        )

    def clone(self) -> "Gauge":
        """
        Return an independent clone.
        """
        return self.copy()


# ==============================================================================
# Part 14. Validation
# ==============================================================================

    def validate(self) -> bool:
        """
        Validate the current Gauge.

        Returns
        -------
        bool
            True when the Gauge is valid.

        Raises
        ------
        ValueError
            If a Gauge value or lifecycle state is invalid.
        TypeError
            If an internal field has an invalid type.
        """

        # ------------------------------------------------------------------
        # Name
        # ------------------------------------------------------------------

        if self._name is not None and not isinstance(
            self._name,
            str,
        ):
            raise TypeError(
                "name must be str or None."
            )

        # ------------------------------------------------------------------
        # Value
        # ------------------------------------------------------------------

        if not isinstance(
            self._value,
            (int, float),
        ) or isinstance(
            self._value,
            bool,
        ):
            raise TypeError(
                "value must be int or float."
            )

        # ------------------------------------------------------------------
        # Description
        # ------------------------------------------------------------------

        if self._description is not None and not isinstance(
            self._description,
            str,
        ):
            raise TypeError(
                "description must be str or None."
            )

        # ------------------------------------------------------------------
        # Unit
        # ------------------------------------------------------------------

        if self._unit is not None and not isinstance(
            self._unit,
            str,
        ):
            raise TypeError(
                "unit must be str or None."
            )

        # ------------------------------------------------------------------
        # Metadata
        # ------------------------------------------------------------------

        if not isinstance(
            self._metadata,
            dict,
        ):
            raise TypeError(
                "metadata must be dict."
            )

        # ------------------------------------------------------------------
        # Annotations
        #
        # Do NOT require dict here.
        # The annotation container has its own API.
        # ------------------------------------------------------------------

        if self._annotations is None:
            raise TypeError(
                "annotations must not be None."
            )

        # ------------------------------------------------------------------
        # Tags
        #
        # Do NOT require dict here.
        # The tag container has its own API.
        # ------------------------------------------------------------------

        if self._tags is None:
            raise TypeError(
                "tags must not be None."
            )

        # ------------------------------------------------------------------
        # Runtime State
        # ------------------------------------------------------------------

        if self._state is None:
            raise ValueError(
                "state must not be None."
            )

        # ------------------------------------------------------------------
        # State type
        # ------------------------------------------------------------------

        if not isinstance(
            self._state,
            MetricState,
        ):
            raise TypeError(
                "state must be MetricState."
            )

        # ------------------------------------------------------------------
        # State validation
        # ------------------------------------------------------------------

        try:
            state_valid = self._state.validate()
        except (ValueError, TypeError):
            raise
        except Exception as exc:
            raise ValueError(
                "invalid Gauge lifecycle state."
            ) from exc

        if state_valid is False:
            raise ValueError(
                "invalid Gauge lifecycle state."
            )

        return True


# ==============================================================================
# Part 15. Equality
# ==============================================================================

    def __eq__(
        self,
        other: object,
    ) -> bool:
        """
        Compare two gauges by value and configuration.
        """
        if not isinstance(other, Gauge):
            return NotImplemented

        return self.to_dict() == other.to_dict()


# ==============================================================================
# Part 16. Representation
# ==============================================================================

    def __repr__(self) -> str:
        """
        Return an unambiguous Gauge representation.
        """
        return (
            "Gauge("
            f"name={self._name!r}, "
            f"value={self._value!r}, "
            f"description={self._description!r}, "
            f"unit={self._unit!r}, "
            f"state={self._state!r}"
            ")"
        )

    def __str__(self) -> str:
        """
        Return the human-readable representation.
        """
        if self._name is not None:
            return (
                f"{self._name}="
                f"{self._value}"
            )

        return str(self._value)


# ==============================================================================
# Part 17. Public API
# ==============================================================================

__all__ = [
    "__version__",
    "DEFAULT_VALUE",
    "Number",
    "Metadata",
    "GaugeError",
    "GaugeValidationError",
    "Gauge",
]                
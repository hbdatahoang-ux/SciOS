"""
Runtime metric timer for measuring elapsed execution time.

Python 3.11+
"""

# ==============================================================================

# Part 1. Imports

# ==============================================================================

from __future__ import annotations

import copy
import json
import time

from typing import Any, TypeAlias

from .metric_state import MetricState



# ==============================================================================
# Part 2. Constants
# ==============================================================================

DEFAULT_VALUE: float = 0.0

DEFAULT_NAME: str | None = None

DEFAULT_DESCRIPTION: str | None = None

DEFAULT_UNIT: str | None = None

DEFAULT_METADATA: dict[str, Any] = {}

DEFAULT_ANNOTATIONS: dict[str, Any] = {}

DEFAULT_TAGS: dict[str, Any] = {}


# ==============================================================================
# Part 3. Type Aliases
# ==============================================================================

NumericValue: TypeAlias = int | float

Metadata: TypeAlias = dict[str, Any]

Annotation: TypeAlias = dict[str, Any]

Tag: TypeAlias = dict[str, Any]


# ==============================================================================
# Part 4. Exceptions
# ==============================================================================


class TimerValidationError(ValueError):
    """
    Raised when a Timer contains invalid configuration or state.
    """

    pass


# ==============================================================================
# State Sentinel
# ==============================================================================

_STATE_UNSET = object()


# ==============================================================================
# Part 5. Timer class
# ==============================================================================


# ------------------------------------------------------------------------------
# Constructor sentinel
#
# Distinguishes:
#
#     Timer()
#         -> create default MetricState
#
#     Timer(state=None)
#         -> explicitly store None
#
#     Timer(state=some_state)
#         -> preserve exact object identity
# ------------------------------------------------------------------------------

_STATE_UNSET = object()


class Timer:
    """
    SciOS Runtime Timer.

    Runtime metric timer for measuring elapsed execution time.
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
        metadata: Metadata | None = None,
        annotations: Annotation | None = None,
        tags: Tag | None = None,
        state: MetricState | None | object = _STATE_UNSET,
    ) -> None:
        self._name = name
        self._value = value
        self._description = description
        self._unit = unit

        self._metadata = copy.deepcopy(
            DEFAULT_METADATA
            if metadata is None
            else metadata
        )

        self._annotations = copy.deepcopy(
            DEFAULT_ANNOTATIONS
            if annotations is None
            else annotations
        )

        self._tags = copy.deepcopy(
            DEFAULT_TAGS
            if tags is None
            else tags
        )

        # ------------------------------------------------------------------
        # State semantics
        #
        # Timer()            -> default MetricState
        # Timer(state=None)  -> explicit None
        # Timer(state=obj)   -> exact object identity
        # ------------------------------------------------------------------

        if state is _STATE_UNSET:
            self._state = MetricState()
        else:
            self._state = state

        # ------------------------------------------------------------------
        # Timer internals
        # ------------------------------------------------------------------

        self._elapsed = 0.0
        self._start_time: float | None = None
        self._pause_time: float | None = None
        self._paused_elapsed = 0.0

        self.validate()

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

    # --------------------------------------------------------------------------

    @property
    def value(self) -> NumericValue:
        return self._value

    @value.setter
    def value(self, value: NumericValue) -> None:
        self._validate_numeric(value, "value")
        self._value = value

    # --------------------------------------------------------------------------

    @property
    def description(self) -> str | None:
        return self._description

    @description.setter
    def description(self, value: str | None) -> None:
        if value is not None and not isinstance(value, str):
            raise TypeError(
                "description must be str or None."
            )

        self._description = value

    # --------------------------------------------------------------------------

    @property
    def unit(self) -> str | None:
        return self._unit

    @unit.setter
    def unit(self, value: str | None) -> None:
        if value is not None and not isinstance(value, str):
            raise TypeError("unit must be str or None.")

        self._unit = value

    # --------------------------------------------------------------------------

    @property
    def metadata(self) -> Metadata:
        return self._metadata

    @metadata.setter
    def metadata(self, value: Metadata) -> None:
        if not isinstance(value, dict):
            raise TypeError("metadata must be dict.")

        self._metadata = copy.deepcopy(value)

    # --------------------------------------------------------------------------

    @property
    def annotations(self) -> Annotation:
        return self._annotations

    @annotations.setter
    def annotations(self, value: Annotation) -> None:
        if value is None:
            raise TypeError(
                "annotations must not be None."
            )

        if not isinstance(value, dict):
            raise TypeError(
                "annotations must be dict."
            )

        self._annotations = copy.deepcopy(value)

    # --------------------------------------------------------------------------

    @property
    def tags(self) -> Tag:
        return self._tags

    @tags.setter
    def tags(self, value: Tag) -> None:
        if value is None:
            raise TypeError(
                "tags must not be None."
            )

        if not isinstance(value, dict):
            raise TypeError(
                "tags must be dict."
            )

        self._tags = copy.deepcopy(value)

    # --------------------------------------------------------------------------

    @property
    def state(self) -> MetricState | None:
        return self._state

    @state.setter
    def state(
        self,
        value: MetricState | None,
    ) -> None:
        if value is not None and not isinstance(
            value,
            MetricState,
        ):
            raise TypeError(
                "state must be MetricState or None."
            )

        # Preserve exact object identity.
        self._state = value

    # ==========================================================================
    # Value operations
    # ==========================================================================

    def set_value(
        self,
        value: NumericValue,
    ) -> "Timer":
        self._validate_numeric(value, "value")
        self._value = value
        return self

    # --------------------------------------------------------------------------

    def add_value(
        self,
        amount: NumericValue = 1,
    ) -> "Timer":
        self._validate_numeric(amount, "amount")
        self._value += amount
        return self

    # --------------------------------------------------------------------------

    def subtract_value(
        self,
        amount: NumericValue = 1,
    ) -> "Timer":
        self._validate_numeric(amount, "amount")
        self._value -= amount
        return self

    # --------------------------------------------------------------------------

    def increment(
        self,
        amount: NumericValue = 1,
    ) -> "Timer":
        return self.add_value(amount)

    # --------------------------------------------------------------------------

    def decrement(
        self,
        amount: NumericValue = 1,
    ) -> "Timer":
        return self.subtract_value(amount)

    # --------------------------------------------------------------------------

    def reset(self) -> "Timer":
        self._value = DEFAULT_VALUE

        self._elapsed = 0.0
        self._start_time = None
        self._pause_time = None
        self._paused_elapsed = 0.0

        self._apply_state_reset()

        return self

    # ==========================================================================
    # Metadata operations
    # ==========================================================================

    def set_metadata(
        self,
        key: str,
        value: Any,
    ) -> "Timer":
        if not isinstance(key, str):
            raise TypeError(
                "metadata key must be str."
            )

        self._metadata[key] = value
        return self

    # --------------------------------------------------------------------------

    def get_metadata(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        return self._metadata.get(
            key,
            default,
        )

    # --------------------------------------------------------------------------

    def remove_metadata(
        self,
        key: str,
    ) -> "Timer":
        self._metadata.pop(
            key,
            None,
        )

        return self

    # --------------------------------------------------------------------------

    def clear_metadata(self) -> "Timer":
        self._metadata.clear()
        return self

    # ==========================================================================
    # Annotation operations
    # ==========================================================================

    def set_annotation(
        self,
        key: str,
        value: Any,
    ) -> "Timer":
        if not isinstance(key, str):
            raise TypeError(
                "annotation key must be str."
            )

        self._annotations[key] = value
        return self

    # --------------------------------------------------------------------------

    def get_annotation(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        return self._annotations.get(
            key,
            default,
        )

    # --------------------------------------------------------------------------

    def remove_annotation(
        self,
        key: str,
    ) -> "Timer":
        self._annotations.pop(
            key,
            None,
        )

        return self

    # --------------------------------------------------------------------------

    def clear_annotations(self) -> "Timer":
        self._annotations.clear()
        return self

    # ==========================================================================
    # Tag operations
    # ==========================================================================

    def set_tag(
        self,
        key: str,
        value: Any,
    ) -> "Timer":
        if not isinstance(key, str):
            raise TypeError(
                "tag key must be str."
            )

        self._tags[key] = value
        return self

    # --------------------------------------------------------------------------

    def get_tag(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        return self._tags.get(
            key,
            default,
        )

    # --------------------------------------------------------------------------

    def remove_tag(
        self,
        key: str,
    ) -> "Timer":
        self._tags.pop(
            key,
            None,
        )

        return self

    # --------------------------------------------------------------------------

    def clear_tags(self) -> "Timer":
        self._tags.clear()
        return self

    # ==========================================================================
    # Timer operations
    # ==========================================================================

    def start(self) -> "Timer":
        if self.is_running():
            return self

        if self.is_paused():
            return self

        self._start_time = self._now()
        self._pause_time = None

        return self

    # --------------------------------------------------------------------------

    def stop(self) -> "Timer":
        if self._start_time is None:
            return self

        now = self._now()

        if self.is_paused():
            self._elapsed += (
                self._pause_time
                - self._start_time
            )
        else:
            self._elapsed += (
                now
                - self._start_time
            )

        self._start_time = None
        self._pause_time = None
        self._paused_elapsed = 0.0

        self._value = self._elapsed

        return self

    # --------------------------------------------------------------------------

    def pause(self) -> "Timer":
        if self._start_time is None:
            return self

        if self.is_paused():
            return self

        self._pause_time = self._now()

        return self

    # --------------------------------------------------------------------------

    def resume(self) -> "Timer":
        if self._start_time is None:
            return self

        if not self.is_paused():
            return self

        now = self._now()

        self._paused_elapsed = (
            self._pause_time
            - self._start_time
        )

        self._elapsed += self._paused_elapsed

        self._start_time = now
        self._pause_time = None
        self._paused_elapsed = 0.0

        return self

    # --------------------------------------------------------------------------

    def elapsed(self) -> float:
        if self._start_time is None:
            return float(self._elapsed)

        if self.is_paused():
            return float(
                self._elapsed
                + (
                    self._pause_time
                    - self._start_time
                )
            )

        return float(
            self._elapsed
            + (
                self._now()
                - self._start_time
            )
        )

    # --------------------------------------------------------------------------

    def duration(self) -> float:
        return self.elapsed()

    # --------------------------------------------------------------------------

    def is_running(self) -> bool:
        return (
            self._start_time is not None
            and self._pause_time is None
        )

    # --------------------------------------------------------------------------

    def is_paused(self) -> bool:
        return (
            self._start_time is not None
            and self._pause_time is not None
        )

    # --------------------------------------------------------------------------

    def clear(self) -> "Timer":
        self._elapsed = 0.0
        self._start_time = None
        self._pause_time = None
        self._paused_elapsed = 0.0
        self._value = DEFAULT_VALUE

        return self

    # ==========================================================================
    # Lifecycle operations
    # ==========================================================================

    def enable(self) -> "Timer":
        if (
            self._state is not None
            and hasattr(self._state, "enable")
        ):
            self._state.enable()

        return self

    # --------------------------------------------------------------------------

    def disable(self) -> "Timer":
        if (
            self._state is not None
            and hasattr(self._state, "disable")
        ):
            self._state.disable()

        return self

    # --------------------------------------------------------------------------

    def activate(self) -> "Timer":
        if (
            self._state is not None
            and hasattr(self._state, "activate")
        ):
            self._state.activate()

        return self

    # --------------------------------------------------------------------------

    def deactivate(self) -> "Timer":
        if (
            self._state is not None
            and hasattr(self._state, "deactivate")
        ):
            self._state.deactivate()

        return self

    # ==========================================================================
    # Snapshot
    # ==========================================================================

    def snapshot(self) -> dict[str, Any]:
        return {
            "value": self._value,
            "name": self._name,
            "description": self._description,
            "unit": self._unit,
            "metadata": copy.deepcopy(
                self._metadata
            ),
            "annotations": copy.deepcopy(
                self._annotations
            ),
            "tags": copy.deepcopy(
                self._tags
            ),
            "state": copy.deepcopy(
                self._state
            ),
            "elapsed": self._elapsed,
            "start_time": self._start_time,
            "pause_time": self._pause_time,
            "paused_elapsed": self._paused_elapsed,
        }

    # ==========================================================================
    # Restore
    # ==========================================================================

    def restore(
        self,
        snapshot: dict[str, Any],
    ) -> "Timer":
        if not isinstance(snapshot, dict):
            raise TypeError(
                "snapshot must be dict."
            )

        # ------------------------------------------------------------------
        # Every field is restored from the snapshot.
        #
        # Missing optional fields intentionally reset to their defaults.
        # This is important for:
        #
        #     timer.restore({"value": 10})
        #
        # which must not retain previous name/description/unit/metadata/etc.
        # ------------------------------------------------------------------

        self._value = snapshot.get(
            "value",
            DEFAULT_VALUE,
        )

        self._name = snapshot.get(
            "name",
            DEFAULT_NAME,
        )

        self._description = snapshot.get(
            "description",
            DEFAULT_DESCRIPTION,
        )

        self._unit = snapshot.get(
            "unit",
            DEFAULT_UNIT,
        )

        self._metadata = copy.deepcopy(
            snapshot.get(
                "metadata",
                DEFAULT_METADATA,
            )
        )

        self._annotations = copy.deepcopy(
            snapshot.get(
                "annotations",
                DEFAULT_ANNOTATIONS,
            )
        )

        self._tags = copy.deepcopy(
            snapshot.get(
                "tags",
                DEFAULT_TAGS,
            )
        )

        # Missing state is explicitly None.
        #
        # Do NOT deepcopy here: restore preserves the exact state
        # object supplied by the snapshot.
        self._state = snapshot.get(
            "state",
            None,
        )

        self._elapsed = snapshot.get(
            "elapsed",
            0.0,
        )

        self._start_time = snapshot.get(
            "start_time",
            None,
        )

        self._pause_time = snapshot.get(
            "pause_time",
            None,
        )

        self._paused_elapsed = snapshot.get(
            "paused_elapsed",
            0.0,
        )

        self.validate()

        return self

    # ==========================================================================
    # Copy / Clone
    # ==========================================================================

    def copy(self) -> "Timer":
        return copy.deepcopy(self)

    # --------------------------------------------------------------------------

    def clone(self) -> "Timer":
        return copy.deepcopy(self)

    # ==========================================================================
    # Serialization
    # ==========================================================================

    def to_dict(self) -> dict[str, Any]:
        return copy.deepcopy(
            self.snapshot()
        )

    # --------------------------------------------------------------------------

    def to_json(self) -> str:
        return json.dumps(
            self.to_dict(),
            sort_keys=True,
            default=str,
        )

    # ==========================================================================
    # Comparison / Representation
    # ==========================================================================

    def __eq__(
        self,
        other: object,
    ) -> bool:
        if not isinstance(other, Timer):
            return NotImplemented

        return (
            self.to_dict()
            == other.to_dict()
        )

    # --------------------------------------------------------------------------

    def __hash__(self) -> int:
        return hash(
            (
                self._value,
                self._name,
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
                json.dumps(
                    self._state,
                    sort_keys=True,
                    default=str,
                ),
            )
        )

    # --------------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            "Timer("
            f"value={self._value!r}, "
            f"name={self._name!r}, "
            f"description={self._description!r}, "
            f"unit={self._unit!r}"
            ")"
        )

    # --------------------------------------------------------------------------

    def __str__(self) -> str:
        return str(self._value)

    # ==========================================================================
    # Internal helpers
    # ==========================================================================

    def _apply_state_reset(self) -> None:
        if (
            self._state is not None
            and hasattr(self._state, "reset")
        ):
            self._state.reset()

    # --------------------------------------------------------------------------

    def _validate_numeric(
        self,
        value: NumericValue,
        field: str,
    ) -> None:
        if isinstance(value, bool):
            raise TimerValidationError(
                f"{field} must be int or float."
            )

        if not isinstance(
            value,
            (int, float),
        ):
            raise TimerValidationError(
                f"{field} must be int or float."
            )

    # --------------------------------------------------------------------------

    def _now(self) -> float:
        return time.perf_counter()

    # ==========================================================================
    # Validation
    # ==========================================================================

    def validate(self) -> bool:
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

        # ------------------------------------------------------------------
        # None is part of the Timer validation contract.
        # ------------------------------------------------------------------

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

        self._validate_numeric(
            self._elapsed,
            "elapsed",
        )

        self._validate_numeric(
            self._paused_elapsed,
            "paused_elapsed",
        )

        if self._start_time is not None:
            self._validate_numeric(
                self._start_time,
                "start_time",
            )

        if self._pause_time is not None:
            self._validate_numeric(
                self._pause_time,
                "pause_time",
            )

        return True


# ==============================================================================
# Part N. Public API
# ==============================================================================

__all__ = [
    "DEFAULT_VALUE",
    "DEFAULT_NAME",
    "DEFAULT_DESCRIPTION",
    "DEFAULT_UNIT",
    "DEFAULT_METADATA",
    "DEFAULT_ANNOTATIONS",
    "DEFAULT_TAGS",
    "NumericValue",
    "Metadata",
    "Annotation",
    "Tag",
    "TimerValidationError",
    "Timer",
]

# ==============================================================================
# Part 1. Imports
# ==============================================================================

from __future__ import annotations

import json

from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, TypeAlias


# ==============================================================================
# Part 2. Constants
# ==============================================================================

HOOKS_VERSION: str = "0.1.0"

DEFAULT_STAGE: str = "before_collect"


# ==============================================================================
# Part 3. Exceptions
# ==============================================================================

class MetricHookError(Exception):
    """Base exception for metric hooks."""


class HookRegistrationError(MetricHookError):
    """Raised when hook registration fails."""


class HookExecutionError(MetricHookError):
    """Raised when hook execution fails."""


class HookValidationError(MetricHookError):
    """Raised when hook validation fails."""


# ==============================================================================
# Part 4. Type Aliases
# ==============================================================================

HookCallback: TypeAlias = Callable[..., Any]

HookMap: TypeAlias = dict["HookStage", list[HookCallback]]


# ==============================================================================
# Part 5. HookStage Enum
# ==============================================================================

class HookStage(str, Enum):
    """Supported hook stages."""

    BEFORE_COLLECT = "before_collect"
    AFTER_COLLECT = "after_collect"

    BEFORE_EXPORT = "before_export"
    AFTER_EXPORT = "after_export"

    ON_ERROR = "on_error"
    ON_RESET = "on_reset"

    def __str__(self) -> str:
        return self.value


# ==============================================================================
# Part 6. Dataclass
# ==============================================================================

@dataclass(slots=True)
class MetricHooks:
    """
    Container for metric lifecycle hooks.
    """

    hooks: HookMap = field(default_factory=dict)

# ==============================================================================
# Part 7. Constructor Validation
# ==============================================================================

    def __post_init__(self) -> None:
        if self.hooks is None:
            self.hooks = {}

        if not isinstance(self.hooks, dict):
            raise TypeError("hooks must be a dictionary.")

        normalized: HookMap = {}

        for stage, callbacks in self.hooks.items():

            if isinstance(stage, str):
                stage = HookStage(stage)

            if not isinstance(stage, HookStage):
                raise TypeError("invalid hook stage.")

            if callbacks is None:
                callbacks = []

            if not isinstance(callbacks, (list, tuple)):
                raise TypeError("callbacks must be a sequence.")

            validated: list[HookCallback] = []

            for callback in callbacks:
                if not callable(callback):
                    raise TypeError("hook callback must be callable.")
                validated.append(callback)

            normalized[stage] = validated

        self.hooks = normalized


# ==============================================================================
# Part 8. Properties
# ==============================================================================

    @property
    def mapping(self) -> HookMap:
        return self.hooks

    @property
    def size(self) -> int:
        return self.count()

    @property
    def empty(self) -> bool:
        return self.count() == 0


# ==============================================================================
# Part 9. Hook Registration
# ==============================================================================

    def register(
        self,
        stage: HookStage | str,
        callback: HookCallback,
    ) -> None:
        if isinstance(stage, str):
            stage = HookStage(stage)

        if not callable(callback):
            raise TypeError("callback must be callable.")

        self.hooks.setdefault(stage, [])

        if callback not in self.hooks[stage]:
            self.hooks[stage].append(callback)

    def unregister(
        self,
        stage: HookStage | str,
        callback: HookCallback,
    ) -> None:
        if isinstance(stage, str):
            stage = HookStage(stage)

        if stage not in self.hooks:
            return

        try:
            self.hooks[stage].remove(callback)
        except ValueError:
            return

        if not self.hooks[stage]:
            del self.hooks[stage]

    def clear(
        self,
        stage: HookStage | str | None = None,
    ) -> None:
        if stage is None:
            self.hooks.clear()
            return

        if isinstance(stage, str):
            stage = HookStage(stage)

        self.hooks.pop(stage, None)

    def has(
        self,
        stage: HookStage | str,
    ) -> bool:
        if isinstance(stage, str):
            stage = HookStage(stage)

        return stage in self.hooks and bool(self.hooks[stage])

    def count(self) -> int:
        return sum(len(v) for v in self.hooks.values())

    def stages(self) -> tuple[HookStage, ...]:
        return tuple(self.hooks.keys())


# ==============================================================================
# Part 10. Hook Execution
# ==============================================================================

    @staticmethod
    def _placeholder_hook(*args: Any, **kwargs: Any) -> None:
        """
        Placeholder callback restored from serialized metadata.

        Since Python callables cannot be serialized safely,
        deserialization recreates lightweight placeholder callbacks
        so hook counts and execution semantics remain consistent.
        """
        return None


    def run(
        self,
        stage: HookStage | str,
        *args: Any,
        **kwargs: Any,
    ) -> list[Any]:
        """
        Execute every callback registered for a stage.
        """

        if isinstance(stage, str):
            stage = HookStage(stage)

        results: list[Any] = []

        for callback in self.hooks.get(stage, ()):
            results.append(callback(*args, **kwargs))

        return results


    def run_before_collect(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> list[Any]:
        return self.run(
            HookStage.BEFORE_COLLECT,
            *args,
            **kwargs,
        )


    def run_after_collect(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> list[Any]:
        return self.run(
            HookStage.AFTER_COLLECT,
            *args,
            **kwargs,
        )


    def run_before_export(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> list[Any]:
        return self.run(
            HookStage.BEFORE_EXPORT,
            *args,
            **kwargs,
        )


    def run_after_export(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> list[Any]:
        return self.run(
            HookStage.AFTER_EXPORT,
            *args,
            **kwargs,
        )


    def run_on_error(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> list[Any]:
        return self.run(
            HookStage.ON_ERROR,
            *args,
            **kwargs,
        )


    def run_on_reset(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> list[Any]:
        return self.run(
            HookStage.ON_RESET,
            *args,
            **kwargs,
        )


# ==============================================================================
# Part 11. Validation
# ==============================================================================

    def validate(self) -> bool:
        """
        Validate internal hook registry.
        """

        for stage, callbacks in self.hooks.items():

            if not isinstance(stage, HookStage):
                return False

            if not isinstance(callbacks, list):
                return False

            if not all(callable(cb) for cb in callbacks):
                return False

        return True


# ==============================================================================
# Part 12. Serialization
# ==============================================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize hook metadata.

        Note:
            Callback objects themselves are intentionally omitted.
            Only stage names and callback counts are preserved.
        """

        return {
            "hooks": {
                stage.value: len(callbacks)
                for stage, callbacks in self.hooks.items()
            }
        }


    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "MetricHooks":
        """
        Restore hook metadata.

        Placeholder callbacks are recreated so callback counts
        remain identical after deserialization.
        """

        mapping: HookMap = {}

        hooks = data.get("hooks", {})

        for stage_name, count in hooks.items():

            stage = HookStage(stage_name)

            count = max(0, int(count))

            if count == 0:
                continue

            mapping[stage] = [
                cls._placeholder_hook
                for _ in range(count)
            ]

        return cls(mapping)


    def to_json(self) -> str:
        """
        Serialize to JSON.
        """

        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            sort_keys=True,
        )


    @classmethod
    def from_json(
        cls,
        payload: str,
    ) -> "MetricHooks":
        """
        Restore from JSON.
        """

        return cls.from_dict(
            json.loads(payload),
        )


# ==============================================================================
# Part 13. Copy
# ==============================================================================

    def copy(self) -> "MetricHooks":
        copied: HookMap = {
            stage: callbacks.copy()
            for stage, callbacks in self.hooks.items()
        }
        return MetricHooks(copied)

    def clone(self) -> "MetricHooks":
        return deepcopy(self)


# ==============================================================================
# Part 14. Equality
# ==============================================================================

    def __eq__(
        self,
        other: object,
    ) -> bool:
        if not isinstance(other, MetricHooks):
            return NotImplemented

        return self.to_dict() == other.to_dict()

    def __hash__(self) -> int:
        return hash(
            tuple(
                sorted(
                    (stage.value, len(callbacks))
                    for stage, callbacks in self.hooks.items()
                )
            )
        )


# ==============================================================================
# Part 15. Representation
# ==============================================================================

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(hooks={self.to_dict()['hooks']!r})"
        )

    def __str__(self) -> str:
        return repr(self)


# ==============================================================================
# Part 16. Public API
# ==============================================================================

__all__ = [
    "HOOKS_VERSION",
    "DEFAULT_STAGE",
    "HookCallback",
    "HookMap",
    "HookStage",
    "MetricHookError",
    "HookRegistrationError",
    "HookExecutionError",
    "HookValidationError",
    "MetricHooks",
]

__version__ = HOOKS_VERSION            
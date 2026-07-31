"""
SciOS Observability
==================

Metric Hooks

Hook system for the SciOS Metrics runtime.

Responsibilities
----------------
- Metric lifecycle hooks
- Collection hooks
- Update hooks
- Export hooks
- Runtime callback registration
- Event dispatching

This module provides the infrastructure used by the
Metrics subsystem to execute user-defined callbacks
around metric operations.
"""

from __future__ import annotations


# ==========================================================
# Part 2 — Imports
# ==========================================================

from collections.abc import Callable
from collections.abc import Iterable

from typing import Any
from typing import Final
from typing import TypeAlias
from threading import RLock

# ==========================================================
# Part 3 — Public API
# ==========================================================

__all__ = [
    "HOOKS_VERSION",
    "DEFAULT_PRIORITY",
    "DEFAULT_ENABLED",
    "HookCallback",
    "HookName",
    "HookPriority",
]
# ==========================================================
# Part 4 — Version / Constants / Type Aliases
# ==========================================================

HOOKS_VERSION: Final[str] = "1.0.0"

DEFAULT_PRIORITY: Final[int] = 100

DEFAULT_ENABLED: Final[bool] = True

DEFAULT_MAX_CALLBACKS: Final[int] = 1024

DEFAULT_HOOK_NAMESPACE: Final[str] = "metrics"


# ----------------------------------------------------------
# Type aliases
# ----------------------------------------------------------

HookName: TypeAlias = str

HookPriority: TypeAlias = int

HookResult: TypeAlias = Any

HookCallback: TypeAlias = Callable[..., Any]

HookIterable: TypeAlias = Iterable[HookCallback]
# ==========================================================
# Part 5 — HookEvent Enum
# ==========================================================

from enum import Enum
from enum import auto


class HookEvent(Enum):
    """
    Supported metric hook events.
    """

    BEFORE_REGISTER = auto()
    AFTER_REGISTER = auto()

    BEFORE_UNREGISTER = auto()
    AFTER_UNREGISTER = auto()

    BEFORE_UPDATE = auto()
    AFTER_UPDATE = auto()

    BEFORE_RESET = auto()
    AFTER_RESET = auto()

    BEFORE_SNAPSHOT = auto()
    AFTER_SNAPSHOT = auto()

    BEFORE_RESTORE = auto()
    AFTER_RESTORE = auto()

    BEFORE_EXPORT = auto()
    AFTER_EXPORT = auto()

    ERROR = auto()


# ==========================================================
# Part 6 — MetricHooks
# ==========================================================


class MetricHooks:
    """
    Thread-safe hook registry.

    Stores callbacks grouped by HookEvent.
    """

    def __init__(self) -> None:

        self._hooks: dict[
            HookEvent,
            list[HookCallback],
        ] = {
            event: []
            for event in HookEvent
        }

        self._enabled: bool = True

        self._lock = RLock()

    # ------------------------------------------------------
    # Properties
    # ------------------------------------------------------

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def events(self) -> tuple[HookEvent, ...]:
        return tuple(self._hooks.keys())

    @property
    def hook_count(self) -> int:
        return sum(
            len(callbacks)
            for callbacks in self._hooks.values()
        )

    @property
    def empty(self) -> bool:
        return self.hook_count == 0


# ==========================================================
# Part 7 — Registration API
# ==========================================================

    def register(
        self,
        event: HookEvent,
        callback: HookCallback,
    ) -> HookCallback:
        """
        Register a callback.
        """

        if not callable(callback):
            raise TypeError(
                "callback must be callable."
            )

        with self._lock:

            callbacks = self._hooks[event]

            if callback not in callbacks:
                callbacks.append(callback)

        return callback

    def unregister(
        self,
        event: HookEvent,
        callback: HookCallback,
    ) -> bool:
        """
        Remove callback.
        """

        with self._lock:

            callbacks = self._hooks[event]

            if callback in callbacks:
                callbacks.remove(callback)
                return True

        return False

    def clear(
        self,
        event: HookEvent | None = None,
    ) -> None:
        """
        Clear callbacks.
        """

        with self._lock:

            if event is None:

                for callbacks in self._hooks.values():
                    callbacks.clear()

            else:
                self._hooks[event].clear()
    # ======================================================
    # Part 8 — Execution API
    # ======================================================

    def emit(
        self,
        event: HookEvent,
        *args: Any,
        **kwargs: Any,
    ) -> list[HookResult]:
        """
        Execute all callbacks for an event.

        Exceptions raised by callbacks are suppressed and
        returned as results so that one failing callback does
        not interrupt the remaining callbacks.
        """

        if not self._enabled:
            return []

        callbacks = tuple(self._hooks[event])

        results: list[HookResult] = []

        for callback in callbacks:

            try:
                results.append(
                    callback(
                        *args,
                        **kwargs,
                    )
                )

            except Exception as exc:
                results.append(exc)

        return results

    def before_collect(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> list[HookResult]:

        return self.emit(
            HookEvent.BEFORE_SNAPSHOT,
            *args,
            **kwargs,
        )

    def after_collect(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> list[HookResult]:

        return self.emit(
            HookEvent.AFTER_SNAPSHOT,
            *args,
            **kwargs,
        )

    def before_update(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> list[HookResult]:

        return self.emit(
            HookEvent.BEFORE_UPDATE,
            *args,
            **kwargs,
        )

    def after_update(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> list[HookResult]:

        return self.emit(
            HookEvent.AFTER_UPDATE,
            *args,
            **kwargs,
        )


    # ======================================================
    # Part 9 — Statistics
    # ======================================================

    def size(
        self,
    ) -> int:
        """
        Total registered callbacks.
        """

        return self.hook_count

    def summary(
        self,
    ) -> dict[str, Any]:
        """
        Runtime summary.
        """

        return {
            "version": HOOKS_VERSION,
            "enabled": self._enabled,
            "events": len(self._hooks),
            "callbacks": self.hook_count,
            "distribution": {
                event.name: len(callbacks)
                for event, callbacks in self._hooks.items()
            },
        }


    # ======================================================
    # Part 10 — Validation
    # ======================================================

    def validate(
        self,
    ) -> None:
        """
        Validate internal state.
        """

        for event, callbacks in self._hooks.items():

            if not isinstance(
                event,
                HookEvent,
            ):
                raise TypeError(
                    "Invalid hook event."
                )

            if len(callbacks) > DEFAULT_MAX_CALLBACKS:
                raise RuntimeError(
                    f"{event.name} exceeds callback limit."
                )

            for callback in callbacks:

                if not callable(callback):
                    raise TypeError(
                        "Hook callback must be callable."
                    )

    def is_valid(
        self,
    ) -> bool:
        """
        Safe validation.
        """

        try:
            self.validate()
            return True

        except Exception:
            return False
    # ======================================================
    # Part 11 — Python Protocols
    # ======================================================

    def __len__(
        self,
    ) -> int:
        """
        Return total registered callbacks.
        """

        return self.hook_count

    def __iter__(
        self,
    ):
        """
        Iterate over (event, callbacks).
        """

        return iter(
            self._hooks.items()
        )

    def __repr__(
        self,
    ) -> str:

        return (
            f"{self.__class__.__name__}("
            f"enabled={self._enabled}, "
            f"events={len(self._hooks)}, "
            f"callbacks={self.hook_count})"
        )

    def __str__(
        self,
    ) -> str:

        return (
            f"MetricHooks("
            f"{self.hook_count} callbacks)"
        )


# ==========================================================
# Part 12 — Final Cleanup
# ==========================================================

__all__ = [
    "HOOKS_VERSION",
    "DEFAULT_PRIORITY",
    "DEFAULT_ENABLED",
    "DEFAULT_MAX_CALLBACKS",
    "DEFAULT_HOOK_NAMESPACE",
    "HookName",
    "HookPriority",
    "HookResult",
    "HookCallback",
    "HookIterable",
    "HookEvent",
    "MetricHooks",
]                            
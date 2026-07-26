"""
SciOS-NG Metrics Core - Hooks
=============================

Hook manager for MetricState lifecycle events.

Design goals
------------
- Thread-safe
- Lightweight
- Extensible
- Event-driven
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from threading import RLock
from typing import Any

__all__ = [
    "MetricHooks",
]

Hook = Callable[..., None]


class MetricHooks:
    """
    Manage lifecycle hooks for MetricState.
    """

    __slots__ = (
        "_hooks",
        "_lock",
    )

    def __init__(self) -> None:

        self._hooks: dict[str, list[Hook]] = defaultdict(list)

        self._lock = RLock()

    # ---------------------------------------------------------
    # Registration
    # ---------------------------------------------------------

    def register(
        self,
        event: str,
        callback: Hook,
    ) -> None:
        """
        Register a callback for an event.
        """

        if not callable(callback):
            raise TypeError("callback must be callable")

        with self._lock:
            self._hooks[event].append(callback)

    def unregister(
        self,
        event: str,
        callback: Hook,
    ) -> None:
        """
        Remove a callback.
        """

        with self._lock:

            if event not in self._hooks:
                return

            try:
                self._hooks[event].remove(callback)
            except ValueError:
                pass

    def clear(
        self,
        event: str | None = None,
    ) -> None:
        """
        Remove hooks.
        """

        with self._lock:

            if event is None:
                self._hooks.clear()
            else:
                self._hooks.pop(event, None)

    # ---------------------------------------------------------
    # Dispatch
    # ---------------------------------------------------------

    def dispatch(
        self,
        event: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Dispatch an event.
        """

        callbacks = tuple(self._hooks.get(event, ()))

        for callback in callbacks:
            callback(*args, **kwargs)

    # ---------------------------------------------------------
    # Query
    # ---------------------------------------------------------

    def has_hooks(
        self,
        event: str,
    ) -> bool:

        return bool(self._hooks.get(event))

    def events(self) -> tuple[str, ...]:

        return tuple(self._hooks.keys())

    def callbacks(
        self,
        event: str,
    ) -> tuple[Hook, ...]:

        return tuple(self._hooks.get(event, ()))

    # ---------------------------------------------------------
    # Rich API
    # ---------------------------------------------------------

    def __contains__(
        self,
        event: object,
    ) -> bool:

        return event in self._hooks

    def __len__(self) -> int:

        return sum(len(v) for v in self._hooks.values())

    def __bool__(self) -> bool:

        return len(self) > 0

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}"
            f"(events={len(self._hooks)}, "
            f"callbacks={len(self)})"
        )
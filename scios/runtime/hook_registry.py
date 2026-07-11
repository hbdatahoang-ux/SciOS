"""
SciOS Runtime Hook Registry
===========================

Central hook registry for the SciOS Runtime.

Responsibilities
----------------
- Register runtime hooks.
- Unregister hooks.
- Emit hooks.
- Isolate hook failures.
- Preserve deterministic execution order.

Design Goals
------------
- Python 3.11+
- Lightweight
- Deterministic
- Thread-safe friendly
- Plugin-ready
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from typing import Any

__all__ = [
    "HookRegistry",
]

HookHandler = Callable[..., None]


class HookRegistry:
    """
    Runtime hook registry.

    Example
    -------

        hooks = HookRegistry()

        hooks.register(
            "before_execute",
            callback,
        )

        hooks.emit(
            "before_execute",
            context,
        )
    """

    def __init__(self) -> None:

        self._hooks: dict[
            str,
            list[HookHandler],
        ] = defaultdict(list)

    # ==========================================================
    # Registration
    # ==========================================================

    def register(
        self,
        name: str,
        handler: HookHandler,
    ) -> None:
        """
        Register a hook handler.

        Parameters
        ----------
        name:
            Hook name.

        handler:
            Callable hook.
        """

        if not callable(handler):
            raise TypeError(
                "Hook handler must be callable."
            )

        handlers = self._hooks[name]

        if handler not in handlers:
            handlers.append(handler)

    def unregister(
        self,
        name: str,
        handler: HookHandler,
    ) -> None:
        """
        Remove a hook handler.
        """

        handlers = self._hooks.get(name)

        if not handlers:
            return

        if handler in handlers:
            handlers.remove(handler)

        if not handlers:
            self._hooks.pop(name, None)

    # ==========================================================
    # Execution
    # ==========================================================

    def emit(
        self,
        name: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Execute every handler registered
        under one hook name.

        Hook failures never interrupt
        Runtime execution.
        """

        handlers = tuple(
            self._hooks.get(name, ())
        )

        for handler in handlers:

            try:
                handler(
                    *args,
                    **kwargs,
                )

            except Exception:
                #
                # Hook failures are isolated.
                #
                pass

    # ==========================================================
    # Queries
    # ==========================================================

    def handlers(
        self,
        name: str,
    ) -> tuple[HookHandler, ...]:
        """
        Return handlers of one hook.
        """

        return tuple(
            self._hooks.get(name, ())
        )

    def registered(
        self,
        name: str,
    ) -> bool:
        """
        Whether a hook exists.
        """

        return (
            name in self._hooks
            and len(self._hooks[name]) > 0
        )

    def count(
        self,
        name: str,
    ) -> int:
        """
        Number of handlers.
        """

        return len(
            self._hooks.get(name, ())
        )

    # ==========================================================
    # Maintenance
    # ==========================================================

    def clear(
        self,
    ) -> None:
        """
        Remove all hooks.
        """

        self._hooks.clear()

    # ==========================================================
    # Serialization
    # ==========================================================

    def status(
        self,
    ) -> dict[str, int]:
        """
        Runtime snapshot.
        """

        return {

            name: len(handlers)

            for name, handlers

            in self._hooks.items()
        }

    # ==========================================================
    # Python Protocols
    # ==========================================================

    def __contains__(
        self,
        name: str,
    ) -> bool:

        return self.registered(name)

    def __len__(
        self,
    ) -> int:
        """
        Total registered handlers.
        """

        return sum(
            len(v)
            for v in self._hooks.values()
        )

    def __bool__(
        self,
    ) -> bool:

        return bool(self._hooks)

    def __repr__(
        self,
    ) -> str:

        return (
            f"{self.__class__.__name__}("
            f"hooks={len(self._hooks)}, "
            f"handlers={len(self)})"
        )
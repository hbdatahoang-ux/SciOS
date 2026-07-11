"""
SciOS Runtime Hook Registry
===========================

Central hook registry for the SciOS Runtime.

Responsibilities
----------------
- Register runtime hooks.
- Manage Hook lifecycle.
- Return HookHandle.
- Support priority ordering.
- Support once hooks.
- Isolate hook failures.
- Preserve deterministic execution.

Design Goals
------------
- Python 3.11+
- Lightweight
- Deterministic
- Plugin-ready
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from typing import Any

from .hook import (
    Hook,
    HookHandle,
)

__all__ = [
    "HookRegistry",
]


class HookRegistry:
    """
    Runtime Hook Registry.

    Example
    -------

    registry = HookRegistry()

    handle = registry.register(
        "runtime.after_execute",
        callback,
        priority=10,
    )

    registry.emit(
        "runtime.after_execute",
        context,
    )

    handle.disable()
    """

    def __init__(self) -> None:

        self._hooks: dict[
            str,
            list[Hook],
        ] = defaultdict(list)


    # ==========================================================
    # Registration
    # ==========================================================

    def register(
        self,
        name: str,
        handler: Callable[..., None],
        *,
        priority: int = 100,
        once: bool = False,
    ) -> HookHandle:
        """
        Register a hook.

        Returns
        -------
        HookHandle
            Lifecycle controller.
        """

        if not callable(handler):
            raise TypeError(
                "Hook handler must be callable."
            )

        hook = Hook(
            name=name,
            handler=handler,
            priority=priority,
            once=once,
        )

        self._hooks[name].append(
            hook
        )

        return HookHandle(
            registry=self,
            hook=hook,
        )


    def unregister(
        self,
        name: str,
        handler: Callable[..., None],
    ) -> None:
        """
        Remove hook handler.
        """

        hooks = self._hooks.get(name)

        if not hooks:
            return


        self._hooks[name] = [
            hook
            for hook in hooks
            if hook.handler != handler
        ]


        if not self._hooks[name]:

            self._hooks.pop(
                name,
                None,
            )


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
        Execute hooks by priority.

        Lower priority number runs first.
        """

        hooks = sorted(
            self._hooks.get(name, ()),
            key=lambda h: h.priority,
        )


        for hook in tuple(hooks):

            if not hook.enabled:
                continue


            try:

                hook(
                    *args,
                    **kwargs,
                )


                if hook.once:

                    self.unregister(
                        hook.name,
                        hook.handler,
                    )


            except Exception:
                #
                # Hook failures never
                # break Runtime.
                #
                pass


    # ==========================================================
    # Queries
    # ==========================================================

    def handlers(
        self,
        name: str,
    ) -> tuple[Callable[..., None], ...]:
        """
        Return raw handlers.
        """

        return tuple(
            hook.handler
            for hook in self._hooks.get(
                name,
                (),
            )
        )


    def hooks(
        self,
        name: str,
    ) -> tuple[Hook, ...]:
        """
        Return Hook objects.
        """

        return tuple(
            self._hooks.get(
                name,
                (),
            )
        )


    def registered(
        self,
        name: str,
    ) -> bool:

        return bool(
            self._hooks.get(name)
        )


    def count(
        self,
        name: str | None = None,
    ) -> int:
        """
        Count hooks.

        count()
            total hooks

        count(name)
            hooks under name
        """

        if name is None:

            return sum(
                len(v)
                for v in self._hooks.values()
            )

        return len(
            self._hooks.get(
                name,
                (),
            )
        )


    # ==========================================================
    # Maintenance
    # ==========================================================

    def clear(self) -> None:
        """
        Remove all hooks.
        """

        self._hooks.clear()


    # ==========================================================
    # Status
    # ==========================================================

    def status(self) -> dict[str, int]:

        return {

            name: len(hooks)

            for name, hooks
            in self._hooks.items()
        }


    # ==========================================================
    # Protocols
    # ==========================================================

    def __contains__(
        self,
        name: str,
    ) -> bool:

        return self.registered(name)


    def __len__(
        self,
    ) -> int:

        return self.count()


    def __bool__(
        self,
    ) -> bool:

        return bool(
            self._hooks
        )


    def __repr__(
        self,
    ) -> str:

        return (
            f"{self.__class__.__name__}("
            f"hooks={len(self._hooks)}, "
            f"handlers={self.count()})"
        )
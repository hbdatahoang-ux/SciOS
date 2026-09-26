"""
SciOS Runtime Hook Registry
===========================

Central hook registry for SciOS Runtime.

Responsibilities
----------------
- Register runtime hooks.
- Manage hook lifecycle.
- Provide HookHandle.
- Support priority ordering.
- Support once hooks.
- Isolate hook failures.
- Preserve deterministic execution.

Python 3.11+
"""

from __future__ import annotations


from collections import defaultdict
from collections.abc import Callable
from threading import RLock
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

    Features
    --------
    - Duplicate-safe registration.
    - Priority execution.
    - Once hooks.
    - Thread-safe access.
    - Runtime diagnostics.
    """



    def __init__(self) -> None:

        self._hooks: dict[
            str,
            list[Hook],
        ] = defaultdict(list)


        self._lock = RLock()



    # ======================================================
    # Registration
    # ======================================================

    def register(
        self,
        name: str,
        handler: Callable[..., None],
        *,
        priority: int = 100,
        once: bool = False,
    ) -> HookHandle:
        """
        Register hook.

        Duplicate handler under same hook
        name will be ignored.
        """

        if not isinstance(
            name,
            str,
        ):
            raise TypeError(
                "Hook name must be string."
            )


        if not callable(handler):

            raise TypeError(
                "Hook handler must be callable."
            )


        with self._lock:

            existing = self._hooks.get(
                name,
                [],
            )


            for hook in existing:

                if hook.handler is handler:

                    return HookHandle(
                        registry=self,
                        hook=hook,
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


            self._hooks[name].sort(
                key=lambda item: item.priority
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

        with self._lock:

            hooks = self._hooks.get(
                name
            )


            if not hooks:
                return


            self._hooks[name] = [

                hook

                for hook in hooks

                if hook.handler is not handler

            ]


            if not self._hooks[name]:

                self._hooks.pop(
                    name,
                    None,
                )



    # ======================================================
    # Execution
    # ======================================================

    def emit(
        self,
        name: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Execute hooks.

        Hook failures never break runtime.
        """

        with self._lock:

            hooks = tuple(
                self._hooks.get(
                    name,
                    (),
                )
            )



        for hook in hooks:


            if not hook.enabled:

                continue



            try:

                hook(
                    *args,
                    **kwargs,
                )


            except Exception:

                # Runtime isolation.
                continue



            finally:

                if hook.once:

                    self.unregister(
                        hook.name,
                        hook.handler,
                    )



    # ======================================================
    # Queries
    # ======================================================

    def handlers(
        self,
        name: str,
    ) -> tuple[
        Callable[..., None],
        ...
    ]:
        """
        Return registered handlers.
        """

        with self._lock:

            return tuple(

                hook.handler

                for hook
                in self._hooks.get(
                    name,
                    (),
                )

            )



    def hooks(
        self,
        name: str,
    ) -> tuple[
        Hook,
        ...
    ]:
        """
        Return Hook objects.
        """

        with self._lock:

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
        """
        Check hook existence.
        """

        with self._lock:

            return bool(
                self._hooks.get(
                    name
                )
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

        with self._lock:


            if name is None:

                return sum(
                    len(items)
                    for items in self._hooks.values()
                )


            return len(
                self._hooks.get(
                    name,
                    (),
                )
            )



    # ======================================================
    # Maintenance
    # ======================================================

    def clear(
        self,
    ) -> None:
        """
        Remove all hooks.
        """

        with self._lock:

            self._hooks.clear()



    # ======================================================
    # Diagnostics
    # ======================================================

    def status(
        self,
    ) -> dict[str, int]:
        """
        Return hook statistics.

        Compatibility API.

        Example
        -------
        {
            "runtime.start": 2,
            "runtime.stop": 1,
        }
        """

        with self._lock:

            return {

                name: len(hooks)

                for name, hooks

                in self._hooks.items()

            }



    def diagnostics(
        self,
    ) -> dict[str, Any]:
        """
        Extended registry diagnostics.

        Example
        -------
        {
            "hook_types": 2,
            "total_hooks": 3,
            "hooks": {
                "runtime.start": 1
            }
        }
        """

        return {

            "hook_types":
                len(self._hooks),

            "total_hooks":
                self.count(),

            "hooks":
                self.status(),

        }



    # ======================================================
    # Protocols
    # ======================================================

    def __contains__(
        self,
        name: str,
    ) -> bool:

        return self.registered(
            name
        )



    def __len__(
        self,
    ) -> int:

        return self.count()



    def __bool__(
        self,
    ) -> bool:

        return len(self) > 0



    def __repr__(
        self,
    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"hooks={len(self._hooks)}, "

            f"handlers={self.count()}"

            ")"

        )
"""
SciOS Kernel Lifecycle Manager
==============================

Kernel lifecycle orchestration.

Responsibilities
----------------
- Manage kernel lifecycle states.
- Initialize runtime components.
- Start/stop kernel services.
- Coordinate lifecycle hooks.
- Preserve deterministic transitions.

Python 3.11+
"""

from __future__ import annotations


from collections.abc import Iterable
from threading import RLock
from typing import Any


from .state import KernelState


__all__ = [
    "LifecycleManager",
]



class LifecycleManager:
    """
    SciOS Kernel Lifecycle Coordinator.

    State machine:

        created
           |
        initialize()
           |
        booting
           |
        start()
           |
        running
           |
        shutdown()
           |
        stopped
    """



    def __init__(self) -> None:

        self._state: KernelState = "created"

        self._hooks: list[Any] = []

        self._lock = RLock()



    # ======================================================
    # Properties
    # ======================================================

    @property
    def state(self) -> KernelState:
        """
        Current lifecycle state.
        """

        return self._state



    # ======================================================
    # Hook Management
    # ======================================================

    def add_hook(
        self,
        hook: Any,
    ) -> None:
        """
        Register lifecycle hook.
        """

        with self._lock:

            if hook not in self._hooks:

                self._hooks.append(
                    hook
                )



    def add_hooks(
        self,
        hooks: Iterable[Any],
    ) -> None:
        """
        Register multiple hooks.
        """

        for hook in hooks:

            self.add_hook(
                hook
            )



    def remove_hook(
        self,
        hook: Any,
    ) -> None:
        """
        Remove lifecycle hook.
        """

        with self._lock:

            if hook in self._hooks:

                self._hooks.remove(
                    hook
                )



    def clear_hooks(self) -> None:
        """
        Remove all hooks.
        """

        with self._lock:

            self._hooks.clear()



    # ======================================================
    # Lifecycle
    # ======================================================

    def initialize(self) -> None:
        """
        Initialize registered components.

        Transition:

            created -> booting
        """

        with self._lock:

            self._state = "booting"


            hooks = tuple(
                self._hooks
            )



        for hook in hooks:

            initialize = getattr(
                hook,
                "initialize",
                None,
            )

            if callable(initialize):

                try:

                    initialize()

                except Exception:
                    #
                    # Kernel lifecycle isolation.
                    #
                    continue



    def start(self) -> None:
        """
        Start runtime.

        Transition:

            booting -> running
        """

        with self._lock:

            hooks = tuple(
                self._hooks
            )


        for hook in hooks:

            start = getattr(
                hook,
                "start",
                None,
            )

            if callable(start):

                try:

                    start()

                except Exception:

                    continue



        with self._lock:

            self._state = "running"



    def shutdown(self) -> None:
        """
        Shutdown runtime.

        Transition:

            running -> stopped
        """

        with self._lock:

            self._state = "stopping"

            hooks = tuple(
                reversed(
                    self._hooks
                )
            )


        for hook in hooks:

            shutdown = getattr(
                hook,
                "shutdown",
                None,
            )

            if callable(shutdown):

                try:

                    shutdown()

                except Exception:

                    continue



        with self._lock:

            self._state = "stopped"



    def restart(self) -> None:
        """
        Restart lifecycle.

        stopped -> booting -> running
        """

        self.shutdown()

        self.initialize()

        self.start()



    # ======================================================
    # Status
    # ======================================================

    def status(
        self,
    ) -> dict[str, Any]:
        """
        Lifecycle status snapshot.
        """

        return {

            "state": self._state,

            "hooks": len(
                self._hooks
            ),

        }



    # ======================================================
    # Helpers
    # ======================================================

    def is_running(
        self,
    ) -> bool:

        return self._state == "running"



    def is_stopped(
        self,
    ) -> bool:

        return self._state == "stopped"



    def hook_count(
        self,
    ) -> int:

        return len(
            self._hooks
        )



    # ======================================================
    # Protocols
    # ======================================================

    def __len__(
        self,
    ) -> int:

        return len(
            self._hooks
        )



    def __contains__(
        self,
        hook: Any,
    ) -> bool:

        return hook in self._hooks



    def __repr__(
        self,
    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"state={self._state!r}, "

            f"hooks={len(self._hooks)}"

            ")"

        )
"""
SciOS Runtime Plugin
====================

Canonical plugin interface for the SciOS Runtime.

Responsibilities
----------------
- Install runtime hooks.
- Manage plugin lifecycle.
- Provide plugin metadata.
- Support Runtime extension without modifying Engine.

Design Goals
------------
- Python 3.11+
- Lightweight
- Plugin-oriented
- Deterministic
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from .engine import ExecutionEngine
from .hook import HookHandle

__all__ = [
    "RuntimePlugin",
]


class RuntimePlugin(ABC):
    """
    Base class for every Runtime plugin.

    Lifecycle

        construct
            │
            ▼
         install()
            │
            ▼
          start()
            │
            ▼
           stop()
            │
            ▼
        uninstall()
    """

    name: str = "plugin"

    version: str = "0.1.0"

    description: str = ""

    def __init__(
        self,
        engine: ExecutionEngine,
    ) -> None:

        self._engine = engine

        self._handles: list[HookHandle] = []

        self._installed = False

        self._running = False

    # ==========================================================
    # Properties
    # ==========================================================

    @property
    def engine(self) -> ExecutionEngine:
        return self._engine

    @property
    def installed(self) -> bool:
        return self._installed

    @property
    def running(self) -> bool:
        return self._running

    @property
    def handles(self) -> tuple[HookHandle, ...]:
        return tuple(self._handles)

    # ==========================================================
    # Lifecycle
    # ==========================================================

    @abstractmethod
    def install(self) -> None:
        """
        Register hooks.

        Derived plugins should call

            self.add_handle(...)
        """

    def start(self) -> None:

        self._running = True

    def stop(self) -> None:

        self._running = False

    def uninstall(self) -> None:
        """
        Remove every registered hook.
        """

        for handle in tuple(self._handles):
            handle.unregister()

        self._handles.clear()

        self._installed = False

        self._running = False

    # ==========================================================
    # Helpers
    # ==========================================================

    def add_handle(
        self,
        handle: HookHandle,
    ) -> HookHandle:

        self._handles.append(handle)

        self._installed = True

        return handle

    def clear_handles(self) -> None:

        self._handles.clear()

    # ==========================================================
    # Metadata
    # ==========================================================

    def status(self) -> dict[str, Any]:

        return {

            "name": self.name,

            "version": self.version,

            "installed": self._installed,

            "running": self._running,

            "hooks": len(self._handles),
        }

    # ==========================================================
    # Protocols
    # ==========================================================

    def __len__(self) -> int:

        return len(self._handles)

    def __bool__(self) -> bool:

        return self._running

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"installed={self._installed}, "
            f"running={self._running}, "
            f"hooks={len(self._handles)})"
        )
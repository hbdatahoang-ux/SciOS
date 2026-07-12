"""
SciOS Kernel Plugin Manager
===========================

Plugin management subsystem for SciOS.

Responsibilities
----------------
- Register plugins.
- Enable/disable plugins.
- Initialize/shutdown plugins.
- Discover installed plugins.
- Maintain plugin lifecycle.

Design Goals
------------
- Thread-safe
- Lifecycle aware
- Runtime independent
- Extensible
"""

from __future__ import annotations

from threading import RLock
from typing import Any


class PluginManager:
    """
    Kernel plugin manager.
    """

    def __init__(self) -> None:
        self._plugins: dict[str, Any] = {}
        self._enabled: set[str] = set()
        self._lock = RLock()

    # ==========================================================
    # Registration
    # ==========================================================

    def register(
        self,
        name: str,
        plugin: Any,
        *,
        enable: bool = True,
        overwrite: bool = False,
    ) -> None:
        """
        Register a plugin.
        """

        with self._lock:

            if name in self._plugins and not overwrite:
                raise ValueError(
                    f"Plugin '{name}' already exists."
                )

            self._plugins[name] = plugin

            if enable:
                self._enabled.add(name)

    def unregister(
        self,
        name: str,
    ) -> Any:
        """
        Remove a plugin.
        """

        with self._lock:

            if name not in self._plugins:
                raise KeyError(
                    f"Unknown plugin '{name}'."
                )

            self._enabled.discard(name)

            return self._plugins.pop(name)

    # ==========================================================
    # Lookup
    # ==========================================================

    def get(
        self,
        name: str,
        default: Any = None,
    ) -> Any:
        with self._lock:
            return self._plugins.get(name, default)

    def require(
        self,
        name: str,
    ) -> Any:

        plugin = self.get(name)

        if plugin is None:
            raise KeyError(
                f"Unknown plugin '{name}'."
            )

        return plugin

    # ==========================================================
    # Enable / Disable
    # ==========================================================

    def enable(
        self,
        name: str,
    ) -> None:

        self.require(name)

        with self._lock:
            self._enabled.add(name)

    def disable(
        self,
        name: str,
    ) -> None:

        self.require(name)

        with self._lock:
            self._enabled.discard(name)

    def enabled(
        self,
        name: str,
    ) -> bool:

        with self._lock:
            return name in self._enabled

    # ==========================================================
    # Lifecycle
    # ==========================================================

    def initialize_all(self) -> None:
        """
        Initialize enabled plugins.
        """

        for name in self.names():

            if not self.enabled(name):
                continue

            plugin = self.require(name)

            initialize = getattr(
                plugin,
                "initialize",
                None,
            )

            if callable(initialize):
                initialize()

    def shutdown_all(self) -> None:
        """
        Shutdown enabled plugins.
        """

        for name in reversed(self.names()):

            if not self.enabled(name):
                continue

            plugin = self.require(name)

            shutdown = getattr(
                plugin,
                "shutdown",
                None,
            )

            if callable(shutdown):
                shutdown()

    # ==========================================================
    # Query
    # ==========================================================

    def names(self) -> list[str]:
        with self._lock:
            return sorted(self._plugins)

    def enabled_plugins(self) -> list[str]:
        with self._lock:
            return sorted(self._enabled)

    def disabled_plugins(self) -> list[str]:
        with self._lock:
            return sorted(
                set(self._plugins) - self._enabled
            )

    def count(self) -> int:
        return len(self)

    def clear(self) -> None:
        with self._lock:
            self._plugins.clear()
            self._enabled.clear()

    # ==========================================================
    # Status
    # ==========================================================

    def status(self) -> dict[str, Any]:

        return {
            "plugins": len(self),
            "enabled": len(self._enabled),
            "disabled": len(self) - len(self._enabled),
            "names": self.names(),
        }

    # ==========================================================
    # Magic Methods
    # ==========================================================

    def __contains__(
        self,
        name: object,
    ) -> bool:
        return (
            isinstance(name, str)
            and name in self._plugins
        )

    def __len__(self) -> int:
        return len(self._plugins)

    def __iter__(self):
        return iter(self.names())

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"plugins={len(self)}, "
            f"enabled={len(self._enabled)})"
        )
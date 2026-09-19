"""
SciOS Plugin Manager
====================

Responsibilities
----------------
- Register/unregister plugins.
- Enable/disable plugins.
- Initialize/shutdown plugins.
- Inspect plugin registry.

Does NOT:
- Import modules dynamically.
- Install packages.
- Manage dependencies.
- Execute plugin logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Protocol, Dict, Optional
import threading


class Plugin(Protocol):
    """Plugin interface contract."""

    name: str
    version: str

    def initialize(self, kernel: Any) -> None: ...
    def shutdown(self) -> None: ...


class PluginState(Enum):
    REGISTERED = auto()
    ENABLED = auto()
    DISABLED = auto()


@dataclass(slots=True)
class PluginInfo:
    name: str
    version: str
    state: PluginState = PluginState.REGISTERED
    instance: Optional[Plugin] = None

    def __repr__(self) -> str:
        return f"PluginInfo(name={self.name}, version={self.version}, state={self.state.name})"


class PluginManager:
    """
    Thread-safe plugin manager for SciOS Kernel.
    """

    def __init__(self) -> None:
        self._plugins: Dict[str, PluginInfo] = {}
        self._lock = threading.RLock()

    # ==========================================================
    # Registration
    # ==========================================================

    def register(self, plugin: Plugin) -> None:
        """Register a plugin."""
        with self._lock:
            if plugin.name in self._plugins:
                raise RuntimeError(f"Plugin '{plugin.name}' already registered.")
            self._plugins[plugin.name] = PluginInfo(
                name=plugin.name,
                version=plugin.version,
                state=PluginState.REGISTERED,
                instance=plugin,
            )

    def unregister(self, name: str) -> None:
        """Remove a plugin from registry."""
        with self._lock:
            if name not in self._plugins:
                raise KeyError(f"Plugin '{name}' not found.")
            del self._plugins[name]

    # ==========================================================
    # Lookup
    # ==========================================================

    def get(self, name: str) -> PluginInfo:
        """Retrieve plugin info."""
        with self._lock:
            if name not in self._plugins:
                raise KeyError(f"Plugin '{name}' not found.")
            return self._plugins[name]

    def contains(self, name: str) -> bool:
        """Return True if plugin exists."""
        with self._lock:
            return name in self._plugins

    # ==========================================================
    # Lifecycle
    # ==========================================================

    def enable(self, name: str) -> None:
        """Enable a plugin."""
        with self._lock:
            info = self.get(name)
            info.state = PluginState.ENABLED

    def disable(self, name: str) -> None:
        """Disable a plugin."""
        with self._lock:
            info = self.get(name)
            info.state = PluginState.DISABLED

    def initialize_all(self, kernel: Any) -> None:
        """Initialize all registered/enabled plugins."""
        with self._lock:
            for info in self._plugins.values():
                if info.state in (PluginState.REGISTERED, PluginState.ENABLED):
                    if info.instance:
                        info.instance.initialize(kernel)
                    info.state = PluginState.ENABLED

    def shutdown_all(self) -> None:
        """Shutdown all plugins."""
        with self._lock:
            for info in self._plugins.values():
                if info.instance:
                    try:
                        info.instance.shutdown()
                    except Exception:
                        pass
                info.state = PluginState.DISABLED

    def clear(self) -> None:
        """Clear all plugins."""
        with self._lock:
            self._plugins.clear()

    # ==========================================================
    # Inspection
    # ==========================================================

    def names(self) -> list[str]:
        """Return plugin names."""
        with self._lock:
            return sorted(self._plugins.keys())

    def count(self) -> int:
        """Number of registered plugins."""
        with self._lock:
            return len(self._plugins)

    # ==========================================================
    # Pythonic helpers
    # ==========================================================

    def __contains__(self, name: object) -> bool:
        return isinstance(name, str) and self.contains(name)

    def __len__(self) -> int:
        return self.count()

    def __iter__(self):
        with self._lock:
            return iter(tuple(sorted(self._plugins.keys())))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(plugins={len(self)})"

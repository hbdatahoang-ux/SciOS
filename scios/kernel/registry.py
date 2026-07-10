# scios/kernel/registry.py
"""
SciOS Service Registry

A lightweight thread-safe service registry used by the SciOS Kernel.

Responsibilities
----------------
- Register shared services.
- Lookup services.
- Replace/remove services.
- Enumerate registered services.

The registry intentionally does NOT create services.
Object creation belongs to bootstrap.py (Composition Root).
"""

from __future__ import annotations

from typing import Any
import threading
from types import MappingProxyType


class ServiceAlreadyRegisteredError(RuntimeError):
    """Raised when attempting to register an existing service."""


class ServiceNotFoundError(KeyError):
    """Raised when a requested service does not exist."""


class ServiceRegistry:
    """
    Thread-safe registry for Kernel services.

    Example
    -------
    >>> registry = ServiceRegistry()
    >>> registry.register("events", EventBus())
    >>> bus = registry.get("events")
    """

    def __init__(self) -> None:
        self._services: dict[str, Any] = {}
        self._lock = threading.RLock()

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(
        self,
        name: str,
        service: Any,
        *,
        overwrite: bool = False,
    ) -> None:
        """
        Register a service.

        Parameters
        ----------
        name : str
            Unique service name.
        service : Any
            Service instance.
        overwrite : bool
            Replace an existing service.
        """
        with self._lock:
            if not overwrite and name in self._services:
                raise ServiceAlreadyRegisteredError(
                    f"Service '{name}' already registered."
                )
            self._services[name] = service

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def get(self, name: str) -> Any:
        """Retrieve a registered service."""
        with self._lock:
            try:
                return self._services[name]
            except KeyError as exc:
                raise ServiceNotFoundError(
                    f"Service '{name}' not found."
                ) from exc

    def try_get(self, name: str, default: Any = None) -> Any:
        """Retrieve a service or return a default value."""
        with self._lock:
            return self._services.get(name, default)

    # ------------------------------------------------------------------
    # Removal
    # ------------------------------------------------------------------

    def unregister(self, name: str) -> None:
        """Remove a service."""
        with self._lock:
            if name not in self._services:
                raise ServiceNotFoundError(name)
            del self._services[name]

    def clear(self) -> None:
        """Remove every registered service."""
        with self._lock:
            self._services.clear()

    # ------------------------------------------------------------------
    # Inspection
    # ------------------------------------------------------------------

    def contains(self, name: str) -> bool:
        """Return True if a service exists."""
        with self._lock:
            return name in self._services

    def names(self) -> list[str]:
        """Return registered service names."""
        with self._lock:
            return sorted(self._services.keys())

    def services(self) -> MappingProxyType[str, Any]:
        """Return an immutable view of the registry."""
        with self._lock:
            return MappingProxyType(dict(self._services))

    def count(self) -> int:
        """Number of registered services."""
        with self._lock:
            return len(self._services)

    # ------------------------------------------------------------------
    # Pythonic helpers
    # ------------------------------------------------------------------

    def __contains__(self, name: object) -> bool:
        return isinstance(name, str) and self.contains(name)

    def __len__(self) -> int:
        return self.count()

    def __iter__(self):
        with self._lock:
            return iter(tuple(sorted(self._services.keys())))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(services={len(self)})"

"""
SciOS Kernel Service Registry
=============================

Central service registry for the SciOS Kernel.

Responsibilities
----------------
- Register services.
- Lookup services.
- Remove services.
- Support dependency injection.
- Provide service discovery.

Design Goals
------------
- O(1) lookup
- Thread-safe
- Type-safe API
- Bootstrap friendly
"""

from __future__ import annotations

from threading import RLock
from typing import Any


class ServiceRegistry:
    """
    Central registry for kernel services.
    """

    def __init__(self) -> None:
        self._services: dict[str, Any] = {}
        self._lock = RLock()

    # ==========================================================
    # Registration
    # ==========================================================

    def register(
        self,
        name: str,
        service: Any,
        *,
        overwrite: bool = False,
    ) -> None:
        """
        Register a service.

        Raises
        ------
        ValueError
            If the service already exists and overwrite=False.
        """

        with self._lock:

            if not overwrite and name in self._services:
                raise ValueError(
                    f"Service '{name}' is already registered."
                )

            self._services[name] = service

    # ==========================================================
    # Lookup
    # ==========================================================

    def get(
        self,
        name: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve a service.

        Returns
        -------
        Any
            Registered service or default.
        """

        with self._lock:
            return self._services.get(name, default)

    def require(
        self,
        name: str,
    ) -> Any:
        """
        Retrieve a required service.

        Raises
        ------
        KeyError
            If the service is not registered.
        """

        with self._lock:

            if name not in self._services:
                raise KeyError(
                    f"Unknown service '{name}'."
                )

            return self._services[name]

    # ==========================================================
    # Removal
    # ==========================================================

    def unregister(
        self,
        name: str,
    ) -> Any:
        """
        Remove a service.

        Returns
        -------
        Removed service.

        Raises
        ------
        KeyError
            If service does not exist.
        """

        with self._lock:

            if name not in self._services:
                raise KeyError(
                    f"Unknown service '{name}'."
                )

            return self._services.pop(name)

    def clear(self) -> None:
        """
        Remove all services.
        """

        with self._lock:
            self._services.clear()

    # ==========================================================
    # Query
    # ==========================================================

    def contains(
        self,
        name: str,
    ) -> bool:
        """
        Check if service exists.
        """

        with self._lock:
            return name in self._services

    def names(self) -> list[str]:
        """
        Return sorted service names.
        """

        with self._lock:
            return sorted(self._services.keys())

    def values(self) -> list[Any]:
        """
        Return registered services.
        """

        with self._lock:
            return list(self._services.values())

    def items(self) -> list[tuple[str, Any]]:
        """
        Return registry items.
        """

        with self._lock:
            return list(self._services.items())

    def count(self) -> int:
        """
        Number of registered services.
        """

        with self._lock:
            return len(self._services)

    # ==========================================================
    # Export
    # ==========================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Export registry.
        """

        with self._lock:
            return dict(self._services)

    # ==========================================================
    # Status
    # ==========================================================

    def status(self) -> dict[str, Any]:
        """
        Registry status.
        """

        return {
            "services": self.count(),
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
            and self.contains(name)
        )

    def __getitem__(
        self,
        name: str,
    ) -> Any:
        return self.require(name)

    def __setitem__(
        self,
        name: str,
        service: Any,
    ) -> None:
        self.register(
            name,
            service,
            overwrite=True,
        )

    def __delitem__(
        self,
        name: str,
    ) -> None:
        self.unregister(name)

    def __iter__(self):
        return iter(self.names())

    def __len__(self) -> int:
        return self.count()

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"services={self.count()})"
        )
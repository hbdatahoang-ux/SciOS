"""
SciOS Dependency Injection Container
====================================

Dependency Injection (DI) container for the Scientific
Cognitive Operating System (SciOS).

Responsibilities
----------------
- Register services
- Resolve dependencies
- Lazy service creation
- Singleton management
- Factory registration
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from scios.shared.exceptions import ConfigurationError

__all__ = [
    "DependencyContainer",
]


class DependencyContainer:
    """
    Dependency Injection container.

    Examples
    --------
    >>> container = DependencyContainer()

    >>> container.register_instance(
    ...     "config",
    ...     Config(),
    ... )

    >>> container.register_factory(
    ...     "runtime",
    ...     lambda c: Runtime(
    ...         registry=c.resolve("registry")
    ...     ),
    ... )

    >>> runtime = container.resolve("runtime")
    """

    def __init__(self) -> None:

        self._instances: dict[str, Any] = {}

        self._factories: dict[
            str,
            Callable[[DependencyContainer], Any],
        ] = {}

    # =====================================================
    # Instance Registration
    # =====================================================

    def register_instance(
        self,
        name: str,
        instance: Any,
        *,
        overwrite: bool = False,
    ) -> None:

        if not overwrite and name in self._instances:
            raise ConfigurationError(
                f"Dependency '{name}' already exists."
            )

        self._instances[name] = instance

    # =====================================================
    # Factory Registration
    # =====================================================

    def register_factory(
        self,
        name: str,
        factory: Callable[
            ["DependencyContainer"],
            Any,
        ],
        *,
        overwrite: bool = False,
    ) -> None:

        if not overwrite and name in self._factories:
            raise ConfigurationError(
                f"Factory '{name}' already exists."
            )

        self._factories[name] = factory

    # =====================================================
    # Resolution
    # =====================================================

    def resolve(
        self,
        name: str,
    ) -> Any:
        """
        Resolve a dependency.

        Lazy factories are executed only once.
        """

        if name in self._instances:
            return self._instances[name]

        if name in self._factories:

            instance = self._factories[name](self)

            self._instances[name] = instance

            return instance

        raise ConfigurationError(
            f"Dependency '{name}' not found."
        )

    # =====================================================
    # Queries
    # =====================================================

    def contains(
        self,
        name: str,
    ) -> bool:

        return (
            name in self._instances
            or name in self._factories
        )

    def unregister(
        self,
        name: str,
    ) -> None:

        self._instances.pop(name, None)

        self._factories.pop(name, None)

    def clear(self) -> None:

        self._instances.clear()

        self._factories.clear()

    # =====================================================
    # Metadata
    # =====================================================

    def names(self) -> list[str]:

        return sorted(
            set(self._instances)
            | set(self._factories)
        )

    def status(self) -> dict[str, Any]:

        return {
            "instances": len(self._instances),
            "factories": len(self._factories),
            "registered": self.names(),
        }

    # =====================================================
    # Python Protocols
    # =====================================================

    def __contains__(
        self,
        name: str,
    ) -> bool:

        return self.contains(name)

    def __getitem__(
        self,
        name: str,
    ) -> Any:

        return self.resolve(name)

    def __len__(self) -> int:

        return (
            len(self._instances)
            + len(self._factories)
        )

    def __repr__(self) -> str:

        return (
            "DependencyContainer("
            f"instances={len(self._instances)}, "
            f"factories={len(self._factories)})"
        )

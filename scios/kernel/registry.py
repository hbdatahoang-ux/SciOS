"""
SciOS Component Registry
========================

Global component registry for the Scientific Cognitive
Operating System (SciOS).

Responsibilities
----------------
- Register system components
- Resolve components by name
- Remove components
- Prevent duplicate registrations
- Provide registry inspection
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from scios.shared.exceptions import ConfigurationError

__all__ = [
    "Registry",
    "ComponentRegistry",
]


class Registry:
    """
    Global component registry.

    Examples
    --------
    >>> registry = Registry()

    >>> registry.register("runtime", runtime)

    >>> runtime = registry.get("runtime")
    """

    def __init__(self) -> None:
        self._components: dict[str, Any] = {}

    # ======================================================
    # Registration
    # ======================================================

    def register(
        self,
        name: str,
        component: Any,
        *,
        overwrite: bool = False,
    ) -> None:
        """
        Register a component.

        Parameters
        ----------
        name
            Component name.

        component
            Component instance.

        overwrite
            Replace existing component.
        """

        if not overwrite and name in self._components:
            raise ConfigurationError(
                f"Component '{name}' is already registered."
            )

        self._components[name] = component

    # ======================================================
    # Lookup
    # ======================================================

    def get(
        self,
        name: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve a component.
        """

        return self._components.get(
            name,
            default,
        )

    def require(
        self,
        name: str,
    ) -> Any:
        """
        Retrieve a required component.

        Raises
        ------
        ConfigurationError
        """

        if name not in self._components:
            raise ConfigurationError(
                f"Component '{name}' is not registered."
            )

        return self._components[name]

    # ======================================================
    # Removal
    # ======================================================

    def unregister(
        self,
        name: str,
    ) -> None:
        """
        Remove a component.
        """

        self._components.pop(name, None)

    def clear(self) -> None:
        """
        Remove all registered components.
        """

        self._components.clear()

    # ======================================================
    # Queries
    # ======================================================

    def contains(
        self,
        name: str,
    ) -> bool:
        """
        Check whether a component exists.
        """

        return name in self._components

    def names(self) -> list[str]:
        """
        Registered component names.
        """

        return sorted(self._components.keys())

    def values(self) -> list[Any]:
        """
        Registered component instances.
        """

        return list(self._components.values())

    def items(self) -> list[tuple[str, Any]]:
        """
        Registered component pairs.
        """

        return list(self._components.items())

    def size(self) -> int:
        """
        Number of registered components.
        """

        return len(self._components)

    def is_empty(self) -> bool:
        """
        Whether registry is empty.
        """

        return not self._components

    # ======================================================
    # Export
    # ======================================================

    def to_dict(self) -> dict[str, str]:
        """
        Export registry metadata.
        """

        return {
            name: type(component).__name__
            for name, component in self._components.items()
        }

    def status(self) -> dict[str, Any]:
        """
        Registry status.
        """

        return {
            "components": self.size(),
            "registered": self.names(),
        }

    # ======================================================
    # Python Protocols
    # ======================================================

    def __contains__(
        self,
        name: str,
    ) -> bool:
        return self.contains(name)

    def __getitem__(
        self,
        name: str,
    ) -> Any:
        return self.require(name)

    def __iter__(self) -> Iterator[str]:
        return iter(self._components)

    def __len__(self) -> int:
        return self.size()

    def __repr__(self) -> str:
        return (
            f"Registry("
            f"components={self.size()})"
        )
# ======================================================
# Backward Compatibility
# ======================================================

class ComponentRegistry(Registry):
    """
    Backward-compatible alias.

    Existing kernel modules may still import
    ComponentRegistry while Registry is the
    canonical implementation.
    """

    pass        
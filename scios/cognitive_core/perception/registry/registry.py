"""Registry for SciOS Cognitive Core Perception perceptors."""

from __future__ import annotations

from collections.abc import Iterator

from ..core.base import BasePerceptor


class PerceptorRegistry:
    """Registry of named perception implementations."""

    def __init__(self) -> None:
        """Initialize an empty registry."""

        self._perceptors: dict[str, BasePerceptor] = {}

    def register(self, perceptor: BasePerceptor) -> BasePerceptor:
        """Register a perceptor by its unique name."""

        if not isinstance(perceptor, BasePerceptor):
            raise TypeError("perceptor must be a BasePerceptor")

        if perceptor.name in self._perceptors:
            raise ValueError(
                f"perceptor already registered: {perceptor.name}"
            )

        self._perceptors[perceptor.name] = perceptor
        return perceptor

    def unregister(self, name: str) -> BasePerceptor:
        """Remove and return a registered perceptor."""

        try:
            return self._perceptors.pop(name)
        except KeyError as exc:
            raise KeyError(f"perceptor not registered: {name}") from exc

    def get(self, name: str) -> BasePerceptor:
        """Return a registered perceptor by name."""

        try:
            return self._perceptors[name]
        except KeyError as exc:
            raise KeyError(f"perceptor not registered: {name}") from exc

    def has(self, name: str) -> bool:
        """Return whether a perceptor is registered."""

        return name in self._perceptors

    def list(self) -> list[str]:
        """Return registered perceptor names in insertion order."""

        return list(self._perceptors)

    def clear(self) -> None:
        """Remove all registered perceptors."""

        self._perceptors.clear()

    def __len__(self) -> int:
        """Return the number of registered perceptors."""

        return len(self._perceptors)

    def __contains__(self, name: object) -> bool:
        """Return whether a name is registered."""

        return name in self._perceptors

    def __iter__(self) -> Iterator[str]:
        """Iterate over registered perceptor names."""

        return iter(self._perceptors)


__all__ = ["PerceptorRegistry"]

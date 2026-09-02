"""Factory for SciOS Cognitive Core Perception perceptors."""

from __future__ import annotations

from ..core.base import BasePerceptor
from ..registry.registry import PerceptorRegistry


class PerceptorFactory:
    """Create or retrieve perceptors from a registry."""

    def __init__(self, registry: PerceptorRegistry) -> None:
        """Initialize the factory with a perceptor registry."""

        if not isinstance(registry, PerceptorRegistry):
            raise TypeError("registry must be a PerceptorRegistry")

        self.registry = registry

    def create(self, name: str) -> BasePerceptor:
        """Return the registered perceptor identified by name."""

        return self.registry.get(name)


__all__ = ["PerceptorFactory"]

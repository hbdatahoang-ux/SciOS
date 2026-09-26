"""Abstract base contracts for the Knowledge subsystem."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar


T = TypeVar("T")


class KnowledgeComponent(ABC, Generic[T]):
    """Base contract for reusable Knowledge components."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the component name."""

    @abstractmethod
    def validate(self, value: T) -> bool:
        """Validate a value against the component contract."""


__all__ = [
    "KnowledgeComponent",
]

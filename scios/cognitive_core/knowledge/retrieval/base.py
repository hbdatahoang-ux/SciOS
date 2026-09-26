"""Abstract retrieval contracts for the Knowledge subsystem."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, Iterable, TypeVar


T = TypeVar("T")
Q = TypeVar("Q")


class RetrievalStrategy(ABC, Generic[T, Q]):
    """Base contract for Knowledge retrieval strategies."""

    def __init__(self, name: str) -> None:
        if not isinstance(name, str) or not name.strip():
            raise ValueError("name must be a non-empty string.")

        self._name = name

    @property
    def name(self) -> str:
        """Return the strategy name."""
        return self._name

    @abstractmethod
    def retrieve(
        self,
        items: Iterable[T],
        query: Q,
    ) -> list[T]:
        """Retrieve matching items from an iterable source."""


__all__ = ["RetrievalStrategy"]

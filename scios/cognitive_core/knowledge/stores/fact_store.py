"""Fact store for the Knowledge subsystem."""

from __future__ import annotations

from scios.cognitive_core.knowledge.core.errors import FactError
from scios.cognitive_core.knowledge.core.fact import Fact


class FactStore:
    """In-memory store for semantic facts."""

    def __init__(self) -> None:
        self._facts: dict[str, Fact] = {}

    def add(self, fact: Fact) -> Fact:
        """Add a fact to the store."""
        if not isinstance(fact, Fact):
            raise TypeError("fact must be a Fact.")

        if fact.id in self._facts:
            raise FactError(f"Fact already exists: {fact.id}")

        self._facts[fact.id] = fact
        return fact

    def get(self, fact_id: str) -> Fact | None:
        """Return a fact by ID."""
        return self._facts.get(fact_id)

    def remove(self, fact_id: str) -> Fact | None:
        """Remove and return a fact by ID."""
        return self._facts.pop(fact_id, None)

    def all(self) -> list[Fact]:
        """Return all stored facts as a snapshot."""
        return list(self._facts.values())

    def count(self) -> int:
        """Return the number of stored facts."""
        return len(self._facts)

    def clear(self) -> None:
        """Remove all facts."""
        self._facts.clear()


__all__ = ["FactStore"]

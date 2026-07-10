from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List
from uuid import UUID, uuid4


@dataclass
class KnowledgeBase:
    """
    KnowledgeBase = Foundational store for knowledge facts and concepts.
    """

    kb_id: UUID = field(default_factory=uuid4)
    store: Dict[str, Any] = field(default_factory=dict)
    categories: Dict[str, List[str]] = field(default_factory=dict)

    # =========================================================
    # Core API
    # =========================================================

    def add_entry(self, key: str, value: Any, category: str | None = None) -> None:
        """
        Add a knowledge entry with optional category.
        """
        self.store[key] = value
        if category:
            self.categories.setdefault(category, []).append(key)

    def get_entry(self, key: str) -> Any:
        """
        Retrieve a knowledge entry by key.
        """
        return self.store.get(key)

    def remove_entry(self, key: str) -> None:
        """
        Remove a knowledge entry.
        """
        if key in self.store:
            del self.store[key]
        for cat, keys in self.categories.items():
            if key in keys:
                keys.remove(key)

    def list_entries(self) -> Dict[str, Any]:
        """
        Return all knowledge entries.
        """
        return dict(self.store)

    # =========================================================
    # Utility
    # =========================================================

    def search_by_category(self, category: str) -> Dict[str, Any]:
        """
        Search entries by category.
        """
        results = {}
        for key in self.categories.get(category, []):
            results[key] = self.store.get(key)
        return results

    def clear(self) -> None:
        """
        Clear all knowledge entries.
        """
        self.store.clear()
        self.categories.clear()

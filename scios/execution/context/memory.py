from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(frozen=True)
class MemoryStore:
    """
    MemoryStore = Cognitive memory layer for ExecutionContext.
    Supports short-term (ephemeral) and long-term (persistent) memory.
    Immutable, copy-on-write.
    """

    short_term: dict[str, Any] = field(default_factory=dict)
    long_term: dict[str, Any] = field(default_factory=dict)
    parent: Optional["MemoryStore"] = None

    # =========================================================
    # Copy-on-Write mutation API
    # =========================================================

    def fork(self, short_term: Optional[dict[str, Any]] = None,
             long_term: Optional[dict[str, Any]] = None) -> "MemoryStore":
        """
        Create new immutable memory snapshot.
        """
        st = self.short_term.copy()
        lt = self.long_term.copy()
        if short_term:
            st.update(short_term)
        if long_term:
            lt.update(long_term)
        return MemoryStore(short_term=st, long_term=lt, parent=self.parent)

    def extend(self, short_term: dict[str, Any] = None,
               long_term: dict[str, Any] = None) -> "MemoryStore":
        """
        Create child memory scope with new entries.
        """
        return MemoryStore(short_term=short_term or {},
                           long_term=long_term or {},
                           parent=self)

    # =========================================================
    # Lookup API
    # =========================================================

    def resolve(self, key: str, default=None) -> Any:
        """
        Hierarchical lookup: short-term → long-term → parent chain.
        """
        if key in self.short_term:
            return self.short_term[key]
        if key in self.long_term:
            return self.long_term[key]
        if self.parent:
            return self.parent.resolve(key, default)
        return default

    def contains(self, key: str) -> bool:
        """
        Check if memory contains key in chain.
        """
        if key in self.short_term or key in self.long_term:
            return True
        if self.parent:
            return self.parent.contains(key)
        return False

    # =========================================================
    # Serialization
    # =========================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Flatten memory chain into dict.
        """
        result = {}
        if self.parent:
            result.update(self.parent.to_dict())
        result.update(self.long_term)
        result.update(self.short_term)
        return result

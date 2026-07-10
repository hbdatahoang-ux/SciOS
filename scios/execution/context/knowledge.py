from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(frozen=True)
class KnowledgeBase:
    """
    KnowledgeBase = Cognitive knowledge layer for ExecutionContext.
    Stores facts, entities, and relations in a hierarchical chain.
    Immutable, copy-on-write.
    """

    facts: dict[str, Any] = field(default_factory=dict)
    entities: dict[str, dict[str, Any]] = field(default_factory=dict)
    relations: list[tuple[str, str, str]] = field(default_factory=list)
    parent: Optional["KnowledgeBase"] = None

    # =========================================================
    # Copy-on-Write mutation API
    # =========================================================

    def fork(self,
             facts: Optional[dict[str, Any]] = None,
             entities: Optional[dict[str, dict[str, Any]]] = None,
             relations: Optional[list[tuple[str, str, str]]] = None) -> "KnowledgeBase":
        """
        Create new immutable knowledge snapshot.
        """
        f = self.facts.copy()
        e = {k: v.copy() for k, v in self.entities.items()}
        r = self.relations.copy()

        if facts:
            f.update(facts)
        if entities:
            e.update(entities)
        if relations:
            r.extend(relations)

        return KnowledgeBase(facts=f, entities=e, relations=r, parent=self.parent)

    def extend(self,
               facts: dict[str, Any] = None,
               entities: dict[str, dict[str, Any]] = None,
               relations: list[tuple[str, str, str]] = None) -> "KnowledgeBase":
        """
        Create child knowledge scope with new entries.
        """
        return KnowledgeBase(facts=facts or {},
                             entities=entities or {},
                             relations=relations or [],
                             parent=self)

    # =========================================================
    # Lookup API
    # =========================================================

    def resolve_fact(self, key: str, default=None) -> Any:
        """
        Lookup fact by key in chain.
        """
        if key in self.facts:
            return self.facts[key]
        if self.parent:
            return self.parent.resolve_fact(key, default)
        return default

    def resolve_entity(self, name: str) -> Optional[dict[str, Any]]:
        """
        Lookup entity by name in chain.
        """
        if name in self.entities:
            return self.entities[name]
        if self.parent:
            return self.parent.resolve_entity(name)
        return None

    def resolve_relations(self, subject: str) -> list[tuple[str, str, str]]:
        """
        Get all relations for a subject in chain.
        """
        rels = [r for r in self.relations if r[0] == subject]
        if self.parent:
            rels.extend(self.parent.resolve_relations(subject))
        return rels

    # =========================================================
    # Serialization
    # =========================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Flatten knowledge chain into dict.
        """
        result = {}
        if self.parent:
            result.update(self.parent.to_dict())
        result.update(self.facts)
        return result

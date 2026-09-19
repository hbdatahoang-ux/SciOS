"""Knowledge manager facade."""

from __future__ import annotations

from scios.cognitive_core.knowledge.core.entity import Entity
from scios.cognitive_core.knowledge.core.fact import Fact
from scios.cognitive_core.knowledge.core.graph import KnowledgeGraph
from scios.cognitive_core.knowledge.core.relation import Relation
from scios.cognitive_core.knowledge.retrieval.entity import EntityRetrieval
from scios.cognitive_core.knowledge.retrieval.fact import FactRetrieval
from scios.cognitive_core.knowledge.retrieval.relation import RelationRetrieval
from scios.cognitive_core.knowledge.stores.entity_store import EntityStore
from scios.cognitive_core.knowledge.stores.fact_store import FactStore
from scios.cognitive_core.knowledge.stores.relation_store import RelationStore


class KnowledgeManager:
    """Facade coordinating Knowledge stores, graph, and retrieval."""

    def __init__(self) -> None:
        self.entity_store = EntityStore()
        self.relation_store = RelationStore()
        self.fact_store = FactStore()

        self.graph = KnowledgeGraph()

        self.entity_retrieval = EntityRetrieval()
        self.relation_retrieval = RelationRetrieval()
        self.fact_retrieval = FactRetrieval()

    def add_entity(self, entity: Entity) -> Entity:
        """Add an entity to the store and graph."""
        self.entity_store.add(entity)
        try:
            self.graph.add_entity(entity)
        except Exception:
            self.entity_store.remove(entity.id)
            raise
        return entity

    def get_entity(self, entity_id: str) -> Entity | None:
        """Return an entity by ID."""
        return self.entity_store.get(entity_id)

    def remove_entity(self, entity_id: str) -> Entity | None:
        """Remove an entity and all dependent relations and facts."""
        entity = self.entity_store.get(entity_id)

        if entity is None:
            return None

        relation_ids = [
            relation.id
            for relation in self.relation_store.all()
            if (
                relation.source.id == entity_id
                or relation.target.id == entity_id
            )
        ]

        fact_ids = [
            fact.id
            for fact in self.fact_store.all()
            if fact.relation.id in relation_ids
        ]

        for fact_id in fact_ids:
            self.fact_store.remove(fact_id)

        for relation_id in relation_ids:
            self.relation_store.remove(relation_id)

        self.graph.remove_entity(entity_id)
        self.entity_store.remove(entity_id)

        return entity
    def add_relation(self, relation: Relation) -> Relation:
        """Add a relation to the store and graph."""
        self.relation_store.add(relation)
        try:
            self.graph.add_relation(relation)
        except Exception:
            self.relation_store.remove(relation.id)
            raise
        return relation

    def get_relation(self, relation_id: str) -> Relation | None:
        """Return a relation by ID."""
        return self.relation_store.get(relation_id)

    def remove_relation(self, relation_id: str) -> Relation | None:
        """Remove a relation and its graph facts."""
        relation = self.relation_store.remove(relation_id)

        if relation is None:
            return None

        self.graph.remove_relation(relation_id)

        fact_ids = [
            fact.id
            for fact in self.fact_store.all()
            if fact.relation.id == relation_id
        ]

        for fact_id in fact_ids:
            self.fact_store.remove(fact_id)

        return relation

    def add_fact(self, fact: Fact) -> Fact:
        """Add a fact to the store and graph."""
        self.fact_store.add(fact)
        try:
            self.graph.add_fact(fact)
        except Exception:
            self.fact_store.remove(fact.id)
            raise
        return fact

    def get_fact(self, fact_id: str) -> Fact | None:
        """Return a fact by ID."""
        return self.fact_store.get(fact_id)

    def remove_fact(self, fact_id: str) -> Fact | None:
        """Remove a fact from the store and graph."""
        fact = self.fact_store.remove(fact_id)

        if fact is None:
            return None

        self.graph.remove_fact(fact_id)

        return fact

    def find_entities(self, query: str) -> list[Entity]:
        """Retrieve entities using the entity retrieval strategy."""
        return self.entity_retrieval.retrieve(
            self.entity_store.all(),
            query,
        )

    def find_relations(self, query: str) -> list[Relation]:
        """Retrieve relations using the relation retrieval strategy."""
        return self.relation_retrieval.retrieve(
            self.relation_store.all(),
            query,
        )

    def find_facts(self, query: str) -> list[Fact]:
        """Retrieve facts using the fact retrieval strategy."""
        return self.fact_retrieval.retrieve(
            self.fact_store.all(),
            query,
        )

    def clear(self) -> None:
        """Clear all Knowledge state."""
        self.entity_store.clear()
        self.relation_store.clear()
        self.fact_store.clear()
        self.graph.clear()

    @property
    def entity_count(self) -> int:
        """Return the number of stored entities."""
        return self.entity_store.count()

    @property
    def relation_count(self) -> int:
        """Return the number of stored relations."""
        return self.relation_store.count()

    @property
    def fact_count(self) -> int:
        """Return the number of stored facts."""
        return self.fact_store.count()


__all__ = ["KnowledgeManager"]


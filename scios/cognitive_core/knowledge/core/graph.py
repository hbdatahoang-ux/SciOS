"""Knowledge graph model."""

from __future__ import annotations

from dataclasses import dataclass, field

from .entity import Entity
from .errors import GraphError
from .fact import Fact
from .relation import Relation


@dataclass(slots=True)
class KnowledgeGraph:
    """Directed graph containing entities, relations, and facts."""

    entities: dict[str, Entity] = field(default_factory=dict)
    relations: dict[str, Relation] = field(default_factory=dict)
    facts: dict[str, Fact] = field(default_factory=dict)

    def add_entity(self, entity: Entity) -> Entity:
        if not isinstance(entity, Entity):
            raise TypeError("entity must be an Entity.")

        if entity.id in self.entities:
            raise GraphError(f"Entity already exists: {entity.id}")

        self.entities[entity.id] = entity
        return entity

    def get_entity(self, entity_id: str) -> Entity | None:
        return self.entities.get(entity_id)

    def remove_entity(self, entity_id: str) -> Entity | None:
        entity = self.entities.pop(entity_id, None)

        if entity is None:
            return None

        relation_ids = [
            relation_id
            for relation_id, relation in self.relations.items()
            if relation.source.id == entity_id or relation.target.id == entity_id
        ]

        for relation_id in relation_ids:
            self.remove_relation(relation_id)

        return entity

    def add_relation(self, relation: Relation) -> Relation:
        if not isinstance(relation, Relation):
            raise TypeError("relation must be a Relation.")

        if relation.id in self.relations:
            raise GraphError(f"Relation already exists: {relation.id}")

        if relation.source.id not in self.entities:
            raise GraphError(f"Source entity does not exist: {relation.source.id}")

        if relation.target.id not in self.entities:
            raise GraphError(f"Target entity does not exist: {relation.target.id}")

        self.relations[relation.id] = relation
        return relation

    def get_relation(self, relation_id: str) -> Relation | None:
        return self.relations.get(relation_id)

    def remove_relation(self, relation_id: str) -> Relation | None:
        relation = self.relations.pop(relation_id, None)

        if relation is None:
            return None

        fact_ids = [
            fact_id
            for fact_id, fact in self.facts.items()
            if fact.relation.id == relation_id
        ]

        for fact_id in fact_ids:
            self.facts.pop(fact_id, None)

        return relation

    def add_fact(self, fact: Fact) -> Fact:
        if not isinstance(fact, Fact):
            raise TypeError("fact must be a Fact.")

        if fact.id in self.facts:
            raise GraphError(f"Fact already exists: {fact.id}")

        if fact.relation.id not in self.relations:
            raise GraphError(
                f"Relation does not exist: {fact.relation.id}"
            )

        self.facts[fact.id] = fact
        return fact

    def get_fact(self, fact_id: str) -> Fact | None:
        return self.facts.get(fact_id)

    def remove_fact(self, fact_id: str) -> Fact | None:
        return self.facts.pop(fact_id, None)

    def neighbors(self, entity_id: str) -> list[Entity]:
        if entity_id not in self.entities:
            return []

        result: list[Entity] = []

        for relation in self.relations.values():
            if relation.source.id == entity_id:
                result.append(relation.target)

        return result

    def clear(self) -> None:
        self.entities.clear()
        self.relations.clear()
        self.facts.clear()

    def entity_count(self) -> int:
        return len(self.entities)

    def relation_count(self) -> int:
        return len(self.relations)

    def fact_count(self) -> int:
        return len(self.facts)


__all__ = ["KnowledgeGraph"]

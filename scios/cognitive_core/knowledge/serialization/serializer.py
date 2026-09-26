"""Serialization utilities for the Knowledge subsystem."""

from __future__ import annotations

from typing import Any

from scios.cognitive_core.knowledge.core.entity import Entity
from scios.cognitive_core.knowledge.core.fact import Fact
from scios.cognitive_core.knowledge.core.graph import KnowledgeGraph
from scios.cognitive_core.knowledge.core.relation import Relation
from scios.cognitive_core.knowledge.core.types import (
    EntityType,
    FactType,
    RelationType,
)


class KnowledgeSerializer:
    """Stateless serializer for Knowledge core objects."""

    @staticmethod
    def serialize_entity(entity: Entity) -> dict[str, Any]:
        """Serialize an Entity to a dictionary."""
        if not isinstance(entity, Entity):
            raise TypeError("entity must be an Entity.")

        return {
            "id": entity.id,
            "label": entity.label,
            "entity_type": entity.entity_type.value,
            "metadata": dict(entity.metadata),
        }

    @staticmethod
    def deserialize_entity(data: dict[str, Any]) -> Entity:
        """Deserialize an Entity from a dictionary."""
        if not isinstance(data, dict):
            raise TypeError("data must be a dictionary.")

        return Entity(
            id=data["id"],
            label=data["label"],
            entity_type=EntityType(data["entity_type"]),
            metadata=dict(data.get("metadata", {})),
        )

    @staticmethod
    def serialize_relation(relation: Relation) -> dict[str, Any]:
        """Serialize a Relation to a dictionary."""
        if not isinstance(relation, Relation):
            raise TypeError("relation must be a Relation.")

        return {
            "id": relation.id,
            "source_id": relation.source.id,
            "target_id": relation.target.id,
            "relation_type": relation.relation_type.value,
            "metadata": dict(relation.metadata),
        }

    @staticmethod
    def deserialize_relation(
        data: dict[str, Any],
        entities: dict[str, Entity],
    ) -> Relation:
        """Deserialize a Relation using an entity lookup."""
        if not isinstance(data, dict):
            raise TypeError("data must be a dictionary.")

        if not isinstance(entities, dict):
            raise TypeError("entities must be a dictionary.")

        return Relation(
            id=data["id"],
            source=entities[data["source_id"]],
            target=entities[data["target_id"]],
            relation_type=RelationType(data["relation_type"]),
            metadata=dict(data.get("metadata", {})),
        )

    @staticmethod
    def serialize_fact(fact: Fact) -> dict[str, Any]:
        """Serialize a Fact to a dictionary."""
        if not isinstance(fact, Fact):
            raise TypeError("fact must be a Fact.")

        return {
            "id": fact.id,
            "relation_id": fact.relation.id,
            "fact_type": fact.fact_type.value,
            "metadata": dict(fact.metadata),
        }

    @staticmethod
    def deserialize_fact(
        data: dict[str, Any],
        relations: dict[str, Relation],
    ) -> Fact:
        """Deserialize a Fact using a relation lookup."""
        if not isinstance(data, dict):
            raise TypeError("data must be a dictionary.")

        if not isinstance(relations, dict):
            raise TypeError("relations must be a dictionary.")

        return Fact(
            id=data["id"],
            relation=relations[data["relation_id"]],
            fact_type=FactType(data["fact_type"]),
            metadata=dict(data.get("metadata", {})),
        )

    @classmethod
    def serialize_graph(
        cls,
        graph: KnowledgeGraph,
    ) -> dict[str, Any]:
        """Serialize a KnowledgeGraph to a dictionary."""
        if not isinstance(graph, KnowledgeGraph):
            raise TypeError("graph must be a KnowledgeGraph.")

        return {
            "entities": [
                cls.serialize_entity(entity)
                for entity in graph.entities.values()
            ],
            "relations": [
                cls.serialize_relation(relation)
                for relation in graph.relations.values()
            ],
            "facts": [
                cls.serialize_fact(fact)
                for fact in graph.facts.values()
            ],
        }

    @classmethod
    def deserialize_graph(
        cls,
        data: dict[str, Any],
    ) -> KnowledgeGraph:
        """Deserialize a KnowledgeGraph from a dictionary."""
        if not isinstance(data, dict):
            raise TypeError("data must be a dictionary.")

        graph = KnowledgeGraph()

        entities_data = data.get("entities", [])
        relations_data = data.get("relations", [])
        facts_data = data.get("facts", [])

        if not isinstance(entities_data, list):
            raise TypeError("entities must be a list.")

        if not isinstance(relations_data, list):
            raise TypeError("relations must be a list.")

        if not isinstance(facts_data, list):
            raise TypeError("facts must be a list.")

        entities: dict[str, Entity] = {}

        for entity_data in entities_data:
            entity = cls.deserialize_entity(entity_data)
            graph.add_entity(entity)
            entities[entity.id] = entity

        relations: dict[str, Relation] = {}

        for relation_data in relations_data:
            relation = cls.deserialize_relation(
                relation_data,
                entities,
            )
            graph.add_relation(relation)
            relations[relation.id] = relation

        for fact_data in facts_data:
            fact = cls.deserialize_fact(
                fact_data,
                relations,
            )
            graph.add_fact(fact)

        return graph


__all__ = ["KnowledgeSerializer"]

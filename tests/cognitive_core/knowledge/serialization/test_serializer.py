"""Tests for Knowledge serialization."""

import pytest

from scios.cognitive_core.knowledge.core.entity import Entity
from scios.cognitive_core.knowledge.core.fact import Fact
from scios.cognitive_core.knowledge.core.graph import KnowledgeGraph
from scios.cognitive_core.knowledge.core.relation import Relation
from scios.cognitive_core.knowledge.core.types import (
    EntityType,
    FactType,
    RelationType,
)
from scios.cognitive_core.knowledge.serialization.serializer import (
    KnowledgeSerializer,
)


@pytest.fixture
def entities():
    return [
        Entity(
            "e1",
            "Python",
            EntityType.CONCEPT,
            {"language": "programming"},
        ),
        Entity(
            "e2",
            "Machine Learning",
            EntityType.CONCEPT,
            {"field": "AI"},
        ),
        Entity(
            "e3",
            "Research Lab",
            EntityType.ORGANIZATION,
            {"country": "Vietnam"},
        ),
    ]


@pytest.fixture
def relation(entities):
    return Relation(
        "r1",
        entities[0],
        entities[1],
        RelationType.ASSOCIATED_WITH,
        {"confidence": 0.95},
    )


@pytest.fixture
def fact(relation):
    return Fact(
        "f1",
        relation,
        FactType.ASSERTION,
        {"source": "test"},
    )


@pytest.fixture
def graph(entities, relation, fact):
    graph = KnowledgeGraph()

    for entity in entities:
        graph.add_entity(entity)

    graph.add_relation(relation)
    graph.add_fact(fact)

    return graph


def test_serialize_entity_returns_dict(entities):
    data = KnowledgeSerializer.serialize_entity(entities[0])

    assert isinstance(data, dict)
    assert data == {
        "id": "e1",
        "label": "Python",
        "entity_type": "concept",
        "metadata": {"language": "programming"},
    }


def test_serialize_entity_copies_metadata(entities):
    data = KnowledgeSerializer.serialize_entity(entities[0])

    assert data["metadata"] is not entities[0].metadata
    assert data["metadata"] == entities[0].metadata


def test_serialize_entity_rejects_invalid_input():
    with pytest.raises(TypeError):
        KnowledgeSerializer.serialize_entity("invalid")


def test_deserialize_entity_restores_entity(entities):
    data = KnowledgeSerializer.serialize_entity(entities[0])

    result = KnowledgeSerializer.deserialize_entity(data)

    assert isinstance(result, Entity)
    assert result.id == entities[0].id
    assert result.label == entities[0].label
    assert result.entity_type is entities[0].entity_type
    assert result.metadata == entities[0].metadata


def test_deserialize_entity_rejects_non_dict():
    with pytest.raises(TypeError):
        KnowledgeSerializer.deserialize_entity([])


def test_deserialize_entity_defaults_missing_metadata():
    data = {
        "id": "e1",
        "label": "Python",
        "entity_type": "concept",
    }

    result = KnowledgeSerializer.deserialize_entity(data)

    assert result.metadata == {}


def test_serialize_relation_uses_entity_ids(relation):
    data = KnowledgeSerializer.serialize_relation(relation)

    assert isinstance(data, dict)
    assert data == {
        "id": "r1",
        "source_id": "e1",
        "target_id": "e2",
        "relation_type": "associated_with",
        "metadata": {"confidence": 0.95},
    }


def test_serialize_relation_does_not_embed_entities(relation):
    data = KnowledgeSerializer.serialize_relation(relation)

    assert "source" not in data
    assert "target" not in data
    assert data["source_id"] == relation.source.id
    assert data["target_id"] == relation.target.id


def test_serialize_relation_rejects_invalid_input():
    with pytest.raises(TypeError):
        KnowledgeSerializer.serialize_relation("invalid")


def test_deserialize_relation_restores_entity_references(
    entities,
    relation,
):
    data = KnowledgeSerializer.serialize_relation(relation)

    entity_map = {
        entity.id: entity
        for entity in entities
    }

    result = KnowledgeSerializer.deserialize_relation(
        data,
        entity_map,
    )

    assert isinstance(result, Relation)
    assert result.id == relation.id
    assert result.source is entities[0]
    assert result.target is entities[1]
    assert result.relation_type is relation.relation_type
    assert result.metadata == relation.metadata


def test_deserialize_relation_rejects_non_dict(entities):
    with pytest.raises(TypeError):
        KnowledgeSerializer.deserialize_relation(
            [],
            {"e1": entities[0]},
        )


def test_deserialize_relation_rejects_non_dict_entities(relation):
    data = KnowledgeSerializer.serialize_relation(relation)

    with pytest.raises(TypeError):
        KnowledgeSerializer.deserialize_relation(data, [])


def test_deserialize_relation_missing_entity_raises(entities, relation):
    data = KnowledgeSerializer.serialize_relation(relation)

    with pytest.raises(KeyError):
        KnowledgeSerializer.deserialize_relation(
            data,
            {"e1": entities[0]},
        )


def test_serialize_fact_uses_relation_id(fact):
    data = KnowledgeSerializer.serialize_fact(fact)

    assert isinstance(data, dict)
    assert data == {
        "id": "f1",
        "relation_id": "r1",
        "fact_type": "assertion",
        "metadata": {"source": "test"},
    }


def test_serialize_fact_does_not_embed_relation(fact):
    data = KnowledgeSerializer.serialize_fact(fact)

    assert "relation" not in data
    assert data["relation_id"] == fact.relation.id


def test_serialize_fact_rejects_invalid_input():
    with pytest.raises(TypeError):
        KnowledgeSerializer.serialize_fact("invalid")


def test_deserialize_fact_restores_relation_reference(
    relation,
    fact,
):
    data = KnowledgeSerializer.serialize_fact(fact)

    relation_map = {
        relation.id: relation,
    }

    result = KnowledgeSerializer.deserialize_fact(
        data,
        relation_map,
    )

    assert isinstance(result, Fact)
    assert result.id == fact.id
    assert result.relation is relation
    assert result.fact_type is fact.fact_type
    assert result.metadata == fact.metadata


def test_deserialize_fact_rejects_non_dict(relation):
    with pytest.raises(TypeError):
        KnowledgeSerializer.deserialize_fact(
            [],
            {"r1": relation},
        )


def test_deserialize_fact_rejects_non_dict_relations(fact):
    data = KnowledgeSerializer.serialize_fact(fact)

    with pytest.raises(TypeError):
        KnowledgeSerializer.deserialize_fact(data, [])


def test_deserialize_fact_missing_relation_raises(fact):
    data = KnowledgeSerializer.serialize_fact(fact)

    with pytest.raises(KeyError):
        KnowledgeSerializer.deserialize_fact(data, {})


def test_serialize_graph_returns_expected_sections(graph):
    data = KnowledgeSerializer.serialize_graph(graph)

    assert set(data) == {
        "entities",
        "relations",
        "facts",
    }

    assert len(data["entities"]) == 3
    assert len(data["relations"]) == 1
    assert len(data["facts"]) == 1


def test_serialize_graph_preserves_order(graph, entities):
    data = KnowledgeSerializer.serialize_graph(graph)

    assert [item["id"] for item in data["entities"]] == [
        entity.id for entity in entities
    ]

    assert [item["id"] for item in data["relations"]] == ["r1"]
    assert [item["id"] for item in data["facts"]] == ["f1"]


def test_serialize_graph_rejects_invalid_input():
    with pytest.raises(TypeError):
        KnowledgeSerializer.serialize_graph("invalid")


def test_serialize_graph_does_not_mutate_graph(graph):
    before = (
        list(graph.entities.keys()),
        list(graph.relations.keys()),
        list(graph.facts.keys()),
    )

    KnowledgeSerializer.serialize_graph(graph)

    after = (
        list(graph.entities.keys()),
        list(graph.relations.keys()),
        list(graph.facts.keys()),
    )

    assert after == before


def test_deserialize_graph_restores_structure(graph):
    data = KnowledgeSerializer.serialize_graph(graph)

    result = KnowledgeSerializer.deserialize_graph(data)

    assert isinstance(result, KnowledgeGraph)

    assert result.entity_count() == 3
    assert result.relation_count() == 1
    assert result.fact_count() == 1


def test_deserialize_graph_restores_entity_values(graph):
    data = KnowledgeSerializer.serialize_graph(graph)

    result = KnowledgeSerializer.deserialize_graph(data)

    entity = result.get_entity("e1")

    assert entity is not None
    assert entity.label == "Python"
    assert entity.entity_type is EntityType.CONCEPT
    assert entity.metadata == {"language": "programming"}


def test_deserialize_graph_restores_relation_references(graph):
    data = KnowledgeSerializer.serialize_graph(graph)

    result = KnowledgeSerializer.deserialize_graph(data)

    relation = result.get_relation("r1")

    assert relation is not None
    assert relation.source is result.get_entity("e1")
    assert relation.target is result.get_entity("e2")
    assert relation.relation_type is RelationType.ASSOCIATED_WITH


def test_deserialize_graph_restores_fact_reference(graph):
    data = KnowledgeSerializer.serialize_graph(graph)

    result = KnowledgeSerializer.deserialize_graph(data)

    fact = result.get_fact("f1")

    assert fact is not None
    assert fact.relation is result.get_relation("r1")
    assert fact.fact_type is FactType.ASSERTION


def test_deserialize_graph_preserves_metadata(graph):
    data = KnowledgeSerializer.serialize_graph(graph)

    result = KnowledgeSerializer.deserialize_graph(data)

    assert result.get_entity("e3").metadata == {
        "country": "Vietnam",
    }
    assert result.get_relation("r1").metadata == {
        "confidence": 0.95,
    }
    assert result.get_fact("f1").metadata == {
        "source": "test",
    }


def test_graph_round_trip_preserves_ids(graph):
    data = KnowledgeSerializer.serialize_graph(graph)

    result = KnowledgeSerializer.deserialize_graph(data)

    assert set(result.entities) == set(graph.entities)
    assert set(result.relations) == set(graph.relations)
    assert set(result.facts) == set(graph.facts)


def test_graph_round_trip_preserves_semantics(graph):
    data = KnowledgeSerializer.serialize_graph(graph)

    result = KnowledgeSerializer.deserialize_graph(data)

    original_relation = graph.get_relation("r1")
    restored_relation = result.get_relation("r1")

    original_fact = graph.get_fact("f1")
    restored_fact = result.get_fact("f1")

    assert restored_relation.source.id == original_relation.source.id
    assert restored_relation.target.id == original_relation.target.id
    assert restored_relation.relation_type == original_relation.relation_type

    assert restored_fact.relation.id == original_fact.relation.id
    assert restored_fact.fact_type == original_fact.fact_type


def test_deserialize_graph_empty_data():
    result = KnowledgeSerializer.deserialize_graph({})

    assert isinstance(result, KnowledgeGraph)
    assert result.entity_count() == 0
    assert result.relation_count() == 0
    assert result.fact_count() == 0


def test_deserialize_graph_rejects_non_dict():
    with pytest.raises(TypeError):
        KnowledgeSerializer.deserialize_graph([])


def test_deserialize_graph_rejects_non_list_entities():
    with pytest.raises(TypeError):
        KnowledgeSerializer.deserialize_graph(
            {"entities": {}},
        )


def test_deserialize_graph_rejects_non_list_relations():
    with pytest.raises(TypeError):
        KnowledgeSerializer.deserialize_graph(
            {"relations": {}},
        )


def test_deserialize_graph_rejects_non_list_facts():
    with pytest.raises(TypeError):
        KnowledgeSerializer.deserialize_graph(
            {"facts": {}},
        )


def test_deserialize_graph_missing_entity_reference_raises(
    entities,
):
    data = {
        "entities": [
            KnowledgeSerializer.serialize_entity(entities[0]),
        ],
        "relations": [
            {
                "id": "r1",
                "source_id": "e1",
                "target_id": "missing",
                "relation_type": "associated_with",
                "metadata": {},
            },
        ],
        "facts": [],
    }

    with pytest.raises(KeyError):
        KnowledgeSerializer.deserialize_graph(data)


def test_deserialize_graph_missing_relation_reference_raises(
    entities,
):
    data = {
        "entities": [
            KnowledgeSerializer.serialize_entity(entities[0]),
            KnowledgeSerializer.serialize_entity(entities[1]),
        ],
        "relations": [],
        "facts": [
            {
                "id": "f1",
                "relation_id": "missing",
                "fact_type": "assertion",
                "metadata": {},
            },
        ],
    }

    with pytest.raises(KeyError):
        KnowledgeSerializer.deserialize_graph(data)


def test_serialize_graph_is_round_trip_safe(graph):
    first = KnowledgeSerializer.serialize_graph(graph)
    restored = KnowledgeSerializer.deserialize_graph(first)
    second = KnowledgeSerializer.serialize_graph(restored)

    assert second == first


def test_serializer_is_stateless():
    serializer = KnowledgeSerializer()

    assert serializer.serialize_entity(
        Entity("e1", "Python")
    ) == {
        "id": "e1",
        "label": "Python",
        "entity_type": "concept",
        "metadata": {},
    }


def test_serializer_public_export():
    from scios.cognitive_core.knowledge.serialization import serializer

    assert serializer.__all__ == ["KnowledgeSerializer"]

def test_package_public_export():
    from scios.cognitive_core.knowledge.serialization import (
        KnowledgeSerializer,
    )

    assert KnowledgeSerializer is not None


def test_package_all():
    import scios.cognitive_core.knowledge.serialization as serialization

    assert serialization.__all__ == ["KnowledgeSerializer"]

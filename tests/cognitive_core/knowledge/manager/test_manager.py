"""Tests for Knowledge manager."""

import pytest

from scios.cognitive_core.knowledge.core.entity import Entity
from scios.cognitive_core.knowledge.core.fact import Fact
from scios.cognitive_core.knowledge.core.graph import KnowledgeGraph
from scios.cognitive_core.knowledge.core.relation import Relation
from scios.cognitive_core.knowledge.core.types import FactType, RelationType
from scios.cognitive_core.knowledge.manager.manager import KnowledgeManager
from scios.cognitive_core.knowledge.retrieval.entity import EntityRetrieval
from scios.cognitive_core.knowledge.retrieval.fact import FactRetrieval
from scios.cognitive_core.knowledge.retrieval.relation import RelationRetrieval
from scios.cognitive_core.knowledge.stores.entity_store import EntityStore
from scios.cognitive_core.knowledge.stores.fact_store import FactStore
from scios.cognitive_core.knowledge.stores.relation_store import RelationStore


@pytest.fixture
def manager():
    return KnowledgeManager()


@pytest.fixture
def entities():
    return [
        Entity("e1", "Python"),
        Entity("e2", "Machine Learning"),
        Entity("e3", "PyTorch"),
        Entity("e4", "Research Lab"),
    ]


@pytest.fixture
def relation(entities):
    return Relation(
        "r1",
        entities[0],
        entities[1],
        RelationType.ASSOCIATED_WITH,
    )


@pytest.fixture
def fact(relation):
    return Fact(
        "f1",
        relation,
        FactType.ASSERTION,
    )


def test_manager_initializes_stores(manager):
    assert isinstance(manager.entity_store, EntityStore)
    assert isinstance(manager.relation_store, RelationStore)
    assert isinstance(manager.fact_store, FactStore)


def test_manager_initializes_graph(manager):
    assert isinstance(manager.graph, KnowledgeGraph)


def test_manager_initializes_retrieval_strategies(manager):
    assert isinstance(manager.entity_retrieval, EntityRetrieval)
    assert isinstance(manager.relation_retrieval, RelationRetrieval)
    assert isinstance(manager.fact_retrieval, FactRetrieval)


def test_initial_counts_are_zero(manager):
    assert manager.entity_count == 0
    assert manager.relation_count == 0
    assert manager.fact_count == 0


def test_add_entity_updates_store_and_graph(manager, entities):
    entity = manager.add_entity(entities[0])

    assert entity is entities[0]
    assert manager.get_entity("e1") is entity
    assert manager.graph.get_entity("e1") is entity
    assert manager.entity_count == 1


def test_get_missing_entity_returns_none(manager):
    assert manager.get_entity("missing") is None


def test_remove_entity_updates_store_and_graph(manager, entities):
    manager.add_entity(entities[0])

    result = manager.remove_entity("e1")

    assert result is entities[0]
    assert manager.get_entity("e1") is None
    assert manager.graph.get_entity("e1") is None
    assert manager.entity_count == 0


def test_remove_missing_entity_returns_none(manager):
    assert manager.remove_entity("missing") is None


def test_add_relation_updates_store_and_graph(
    manager,
    entities,
    relation,
):
    manager.add_entity(entities[0])
    manager.add_entity(entities[1])

    result = manager.add_relation(relation)

    assert result is relation
    assert manager.get_relation("r1") is relation
    assert manager.graph.get_relation("r1") is relation
    assert manager.relation_count == 1


def test_add_relation_requires_entities(manager, relation):
    with pytest.raises(Exception):
        manager.add_relation(relation)

    assert manager.relation_count == 0
    assert manager.graph.relation_count() == 0


def test_get_missing_relation_returns_none(manager):
    assert manager.get_relation("missing") is None


def test_remove_relation_updates_store_and_graph(
    manager,
    entities,
    relation,
):
    manager.add_entity(entities[0])
    manager.add_entity(entities[1])
    manager.add_relation(relation)

    result = manager.remove_relation("r1")

    assert result is relation
    assert manager.get_relation("r1") is None
    assert manager.graph.get_relation("r1") is None
    assert manager.relation_count == 0


def test_remove_missing_relation_returns_none(manager):
    assert manager.remove_relation("missing") is None


def test_add_fact_updates_store_and_graph(
    manager,
    entities,
    relation,
    fact,
):
    manager.add_entity(entities[0])
    manager.add_entity(entities[1])
    manager.add_relation(relation)

    result = manager.add_fact(fact)

    assert result is fact
    assert manager.get_fact("f1") is fact
    assert manager.graph.get_fact("f1") is fact
    assert manager.fact_count == 1


def test_add_fact_requires_relation(
    manager,
    fact,
):
    with pytest.raises(Exception):
        manager.add_fact(fact)

    assert manager.fact_count == 0
    assert manager.graph.fact_count() == 0


def test_get_missing_fact_returns_none(manager):
    assert manager.get_fact("missing") is None


def test_remove_fact_updates_store_and_graph(
    manager,
    entities,
    relation,
    fact,
):
    manager.add_entity(entities[0])
    manager.add_entity(entities[1])
    manager.add_relation(relation)
    manager.add_fact(fact)

    result = manager.remove_fact("f1")

    assert result is fact
    assert manager.get_fact("f1") is None
    assert manager.graph.get_fact("f1") is None
    assert manager.fact_count == 0


def test_remove_missing_fact_returns_none(manager):
    assert manager.remove_fact("missing") is None


def test_remove_relation_removes_related_facts(
    manager,
    entities,
    relation,
    fact,
):
    manager.add_entity(entities[0])
    manager.add_entity(entities[1])
    manager.add_relation(relation)
    manager.add_fact(fact)

    manager.remove_relation("r1")

    assert manager.get_relation("r1") is None
    assert manager.get_fact("f1") is None
    assert manager.graph.get_relation("r1") is None
    assert manager.graph.get_fact("f1") is None
    assert manager.relation_count == 0
    assert manager.fact_count == 0


def test_remove_entity_cascades_all_stores_and_graph(
    manager,
    entities,
    relation,
    fact,
):
    manager.add_entity(entities[0])
    manager.add_entity(entities[1])
    manager.add_relation(relation)
    manager.add_fact(fact)

    result = manager.remove_entity("e1")

    assert result is entities[0]

    # Entity state
    assert manager.get_entity("e1") is None
    assert manager.graph.get_entity("e1") is None

    # Relation state
    assert manager.get_relation("r1") is None
    assert manager.graph.get_relation("r1") is None

    # Fact state
    assert manager.get_fact("f1") is None
    assert manager.graph.get_fact("f1") is None

    # Store ? Graph invariant
    assert manager.entity_count == manager.graph.entity_count()
    assert manager.relation_count == manager.graph.relation_count()
    assert manager.fact_count == manager.graph.fact_count()


def test_remove_target_entity_cascades_all_dependencies(
    manager,
    entities,
):
    relation = Relation(
        "r1",
        entities[0],
        entities[1],
        RelationType.ASSOCIATED_WITH,
    )

    fact = Fact(
        "f1",
        relation,
        FactType.ASSERTION,
    )

    manager.add_entity(entities[0])
    manager.add_entity(entities[1])
    manager.add_relation(relation)
    manager.add_fact(fact)

    manager.remove_entity("e2")

    assert manager.get_entity("e2") is None
    assert manager.get_relation("r1") is None
    assert manager.get_fact("f1") is None

    assert manager.graph.get_entity("e2") is None
    assert manager.graph.get_relation("r1") is None
    assert manager.graph.get_fact("f1") is None

    assert manager.entity_count == 1
    assert manager.relation_count == 0
    assert manager.fact_count == 0

    assert manager.entity_count == manager.graph.entity_count()
    assert manager.relation_count == manager.graph.relation_count()
    assert manager.fact_count == manager.graph.fact_count()


def test_remove_entity_without_dependencies_preserves_other_entities(
    manager,
    entities,
):
    manager.add_entity(entities[0])
    manager.add_entity(entities[1])

    result = manager.remove_entity("e1")

    assert result is entities[0]

    assert manager.get_entity("e1") is None
    assert manager.get_entity("e2") is entities[1]

    assert manager.graph.get_entity("e1") is None
    assert manager.graph.get_entity("e2") is entities[1]

    assert manager.entity_count == 1
    assert manager.relation_count == 0
    assert manager.fact_count == 0

    assert manager.entity_count == manager.graph.entity_count()
    assert manager.relation_count == manager.graph.relation_count()
    assert manager.fact_count == manager.graph.fact_count()

def test_find_entities_delegates_retrieval(manager, entities):
    for entity in entities:
        manager.add_entity(entity)

    result = manager.find_entities("Python")

    assert result == [entities[0]]


def test_find_relations_delegates_retrieval(
    manager,
    entities,
    relation,
):
    manager.add_entity(entities[0])
    manager.add_entity(entities[1])
    manager.add_relation(relation)

    result = manager.find_relations("Python")

    assert result == [relation]


def test_find_facts_delegates_retrieval(
    manager,
    entities,
    relation,
    fact,
):
    manager.add_entity(entities[0])
    manager.add_entity(entities[1])
    manager.add_relation(relation)
    manager.add_fact(fact)

    result = manager.find_facts("assertion")

    assert result == [fact]


def test_find_entities_empty_query_returns_empty(manager):
    assert manager.find_entities("") == []


def test_find_relations_empty_query_raises(manager):
    with pytest.raises(ValueError):
        manager.find_relations("")


def test_find_facts_empty_query_raises(manager):
    with pytest.raises(ValueError):
        manager.find_facts("")


def test_clear_removes_all_state(
    manager,
    entities,
    relation,
    fact,
):
    manager.add_entity(entities[0])
    manager.add_entity(entities[1])
    manager.add_relation(relation)
    manager.add_fact(fact)

    manager.clear()

    assert manager.entity_count == 0
    assert manager.relation_count == 0
    assert manager.fact_count == 0

    assert manager.graph.entity_count() == 0
    assert manager.graph.relation_count() == 0
    assert manager.graph.fact_count() == 0


def test_clear_is_idempotent(manager):
    manager.clear()
    manager.clear()

    assert manager.entity_count == 0
    assert manager.relation_count == 0
    assert manager.fact_count == 0


def test_public_export():
    from scios.cognitive_core.knowledge.manager import manager as manager_module

    assert manager_module.__all__ == ["KnowledgeManager"]




def test_package_public_export():
    from scios.cognitive_core.knowledge.manager import KnowledgeManager

    assert KnowledgeManager is not None


def test_package_all():
    import scios.cognitive_core.knowledge.manager as manager_package

    assert manager_package.__all__ == ["KnowledgeManager"]

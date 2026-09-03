"""Tests for the Knowledge graph model."""

import pytest

from scios.cognitive_core.knowledge.core.entity import Entity
from scios.cognitive_core.knowledge.core.errors import GraphError
from scios.cognitive_core.knowledge.core.fact import Fact
from scios.cognitive_core.knowledge.core.graph import KnowledgeGraph
from scios.cognitive_core.knowledge.core.relation import Relation
from scios.cognitive_core.knowledge.core.types import (
    FactType,
    RelationType,
)


@pytest.fixture
def graph():
    return KnowledgeGraph()


@pytest.fixture
def source():
    return Entity("e1", "Python")


@pytest.fixture
def target():
    return Entity("e2", "Programming")


@pytest.fixture
def relation(source, target):
    return Relation(
        "r1",
        source,
        target,
        RelationType.ASSOCIATED_WITH,
    )


@pytest.fixture
def fact(relation):
    return Fact("f1", relation, FactType.ASSERTION)


def test_empty_graph(graph):
    assert graph.entities == {}
    assert graph.relations == {}
    assert graph.facts == {}


def test_add_entity(graph, source):
    result = graph.add_entity(source)

    assert result is source
    assert graph.get_entity("e1") is source
    assert graph.entity_count() == 1


def test_duplicate_entity_is_rejected(graph, source):
    graph.add_entity(source)

    with pytest.raises(GraphError, match="Entity already exists"):
        graph.add_entity(source)


def test_invalid_entity_is_rejected(graph):
    with pytest.raises(TypeError, match="entity"):
        graph.add_entity("entity")


def test_get_missing_entity_returns_none(graph):
    assert graph.get_entity("missing") is None


def test_remove_entity(graph, source):
    graph.add_entity(source)

    result = graph.remove_entity("e1")

    assert result is source
    assert graph.get_entity("e1") is None
    assert graph.entity_count() == 0


def test_remove_missing_entity_returns_none(graph):
    assert graph.remove_entity("missing") is None


def test_add_relation(graph, source, target, relation):
    graph.add_entity(source)
    graph.add_entity(target)

    result = graph.add_relation(relation)

    assert result is relation
    assert graph.get_relation("r1") is relation
    assert graph.relation_count() == 1


def test_relation_requires_source_entity(graph, target, relation):
    graph.add_entity(target)

    with pytest.raises(GraphError, match="Source entity does not exist"):
        graph.add_relation(relation)


def test_relation_requires_target_entity(graph, source, relation):
    graph.add_entity(source)

    with pytest.raises(GraphError, match="Target entity does not exist"):
        graph.add_relation(relation)


def test_duplicate_relation_is_rejected(graph, source, target, relation):
    graph.add_entity(source)
    graph.add_entity(target)
    graph.add_relation(relation)

    with pytest.raises(GraphError, match="Relation already exists"):
        graph.add_relation(relation)


def test_invalid_relation_is_rejected(graph):
    with pytest.raises(TypeError, match="relation"):
        graph.add_relation("relation")


def test_get_missing_relation_returns_none(graph):
    assert graph.get_relation("missing") is None


def test_remove_relation(graph, source, target, relation):
    graph.add_entity(source)
    graph.add_entity(target)
    graph.add_relation(relation)

    result = graph.remove_relation("r1")

    assert result is relation
    assert graph.get_relation("r1") is None
    assert graph.relation_count() == 0


def test_remove_missing_relation_returns_none(graph):
    assert graph.remove_relation("missing") is None


def test_add_fact(graph, source, target, relation, fact):
    graph.add_entity(source)
    graph.add_entity(target)
    graph.add_relation(relation)

    result = graph.add_fact(fact)

    assert result is fact
    assert graph.get_fact("f1") is fact
    assert graph.fact_count() == 1


def test_fact_requires_existing_relation(graph, source, target, fact):
    graph.add_entity(source)
    graph.add_entity(target)

    with pytest.raises(GraphError, match="Relation does not exist"):
        graph.add_fact(fact)


def test_duplicate_fact_is_rejected(graph, source, target, relation, fact):
    graph.add_entity(source)
    graph.add_entity(target)
    graph.add_relation(relation)
    graph.add_fact(fact)

    with pytest.raises(GraphError, match="Fact already exists"):
        graph.add_fact(fact)


def test_invalid_fact_is_rejected(graph):
    with pytest.raises(TypeError, match="fact"):
        graph.add_fact("fact")


def test_get_missing_fact_returns_none(graph):
    assert graph.get_fact("missing") is None


def test_remove_fact(graph, source, target, relation, fact):
    graph.add_entity(source)
    graph.add_entity(target)
    graph.add_relation(relation)
    graph.add_fact(fact)

    result = graph.remove_fact("f1")

    assert result is fact
    assert graph.get_fact("f1") is None
    assert graph.fact_count() == 0


def test_remove_missing_fact_returns_none(graph):
    assert graph.remove_fact("missing") is None


def test_neighbors_returns_outgoing_targets(graph, source, target, relation):
    graph.add_entity(source)
    graph.add_entity(target)
    graph.add_relation(relation)

    assert graph.neighbors("e1") == [target]


def test_neighbors_only_returns_outgoing_edges(graph, source, target):
    graph.add_entity(source)
    graph.add_entity(target)

    relation = Relation("r1", target, source)
    graph.add_relation(relation)

    assert graph.neighbors("e1") == []


def test_neighbors_for_missing_entity_returns_empty_list(graph):
    assert graph.neighbors("missing") == []


def test_remove_entity_removes_connected_relations(
    graph,
    source,
    target,
    relation,
):
    graph.add_entity(source)
    graph.add_entity(target)
    graph.add_relation(relation)

    graph.remove_entity("e1")

    assert graph.relation_count() == 0
    assert graph.get_relation("r1") is None


def test_remove_relation_removes_connected_facts(
    graph,
    source,
    target,
    relation,
    fact,
):
    graph.add_entity(source)
    graph.add_entity(target)
    graph.add_relation(relation)
    graph.add_fact(fact)

    graph.remove_relation("r1")

    assert graph.fact_count() == 0
    assert graph.get_fact("f1") is None


def test_clear(graph, source, target, relation, fact):
    graph.add_entity(source)
    graph.add_entity(target)
    graph.add_relation(relation)
    graph.add_fact(fact)

    graph.clear()

    assert graph.entity_count() == 0
    assert graph.relation_count() == 0
    assert graph.fact_count() == 0


def test_graph_uses_slots():
    graph = KnowledgeGraph()

    assert not hasattr(graph, "__dict__")


def test_public_exports():
    from scios.cognitive_core.knowledge.core import graph

    assert graph.__all__ == ["KnowledgeGraph"]

"""Tests for Relation retrieval."""

import pytest

from scios.cognitive_core.knowledge.core.entity import Entity
from scios.cognitive_core.knowledge.core.relation import Relation
from scios.cognitive_core.knowledge.core.types import RelationType
from scios.cognitive_core.knowledge.retrieval.base import RetrievalStrategy
from scios.cognitive_core.knowledge.retrieval.relation import RelationRetrieval


@pytest.fixture
def strategy():
    return RelationRetrieval()


@pytest.fixture
def entities():
    return [
        Entity("e1", "Python"),
        Entity("e2", "Machine Learning"),
        Entity("e3", "PyTorch"),
        Entity("e4", "Research Lab"),
    ]


@pytest.fixture
def relations(entities):
    return [
        Relation(
            "r1",
            entities[0],
            entities[1],
            RelationType.ASSOCIATED_WITH,
        ),
        Relation(
            "r2",
            entities[0],
            entities[2],
            RelationType.DEPENDS_ON,
        ),
        Relation(
            "r3",
            entities[1],
            entities[3],
            RelationType.LOCATED_IN,
        ),
        Relation(
            "r4",
            entities[2],
            entities[3],
            RelationType.PART_OF,
        ),
    ]


def test_default_name(strategy):
    assert strategy.name == "relation"


def test_custom_name():
    strategy = RelationRetrieval("custom")

    assert strategy.name == "custom"


def test_is_retrieval_strategy(strategy):
    assert isinstance(strategy, RetrievalStrategy)


def test_retrieve_by_source_id(strategy, relations):
    result = strategy.retrieve(relations, "e1")

    assert result == [relations[0], relations[1]]


def test_retrieve_by_source_label(strategy, relations):
    result = strategy.retrieve(relations, "Python")

    assert result == [relations[0], relations[1]]


def test_retrieve_by_source_label_is_case_insensitive(
    strategy,
    relations,
):
    result = strategy.retrieve(relations, "PYTHON")

    assert result == [relations[0], relations[1]]


def test_retrieve_by_partial_source_label(strategy, relations):
    result = strategy.retrieve(relations, "machine")

    assert result == [relations[0], relations[2]]


def test_retrieve_by_target_id(strategy, relations):
    result = strategy.retrieve(relations, "e4")

    assert result == [relations[2], relations[3]]


def test_retrieve_by_target_label(strategy, relations):
    result = strategy.retrieve(relations, "Research Lab")

    assert result == [relations[2], relations[3]]


def test_retrieve_by_target_label_is_case_insensitive(
    strategy,
    relations,
):
    result = strategy.retrieve(relations, "RESEARCH LAB")

    assert result == [relations[2], relations[3]]


def test_retrieve_by_partial_target_label(strategy, relations):
    result = strategy.retrieve(relations, "learning")

    assert result == [relations[0], relations[2]]


def test_retrieve_by_relation_type(strategy, relations):
    result = strategy.retrieve(relations, "depends_on")

    assert result == [relations[1]]


def test_relation_type_is_case_insensitive(strategy, relations):
    result = strategy.retrieve(relations, "DEPENDS_ON")

    assert result == [relations[1]]


def test_relation_type_requires_exact_match(strategy, relations):
    result = strategy.retrieve(relations, "depends")

    assert result == []


def test_retrieve_no_match(strategy, relations):
    assert strategy.retrieve(relations, "Java") == []


def test_empty_items(strategy):
    assert strategy.retrieve([], "Python") == []


def test_generator_input(strategy, relations):
    items = (relation for relation in relations)

    result = strategy.retrieve(items, "depends_on")

    assert result == [relations[1]]


def test_result_preserves_input_order(strategy, relations):
    items = [
        relations[2],
        relations[1],
        relations[3],
        relations[0],
    ]

    result = strategy.retrieve(items, "e1")

    assert result == [relations[1], relations[0]]


def test_result_preserves_relation_identity(strategy, relations):
    result = strategy.retrieve(relations, "Python")

    assert result[0] is relations[0]
    assert result[1] is relations[1]


def test_result_is_new_list(strategy, relations):
    result = strategy.retrieve(relations, "Python")

    assert result is not relations


def test_query_must_be_string(strategy, relations):
    with pytest.raises(TypeError, match="query must be a string"):
        strategy.retrieve(relations, None)


def test_query_empty_string_is_rejected(strategy, relations):
    with pytest.raises(
        ValueError,
        match="query must be a non-empty string",
    ):
        strategy.retrieve(relations, "")


def test_query_whitespace_is_rejected(strategy, relations):
    with pytest.raises(
        ValueError,
        match="query must be a non-empty string",
    ):
        strategy.retrieve(relations, "   ")


def test_query_whitespace_is_trimmed(strategy, relations):
    result = strategy.retrieve(relations, "  Python  ")

    assert result == [relations[0], relations[1]]


def test_relations_are_not_mutated(strategy, relations):
    original = [
        (
            relation.id,
            relation.source,
            relation.target,
            relation.relation_type,
            relation.metadata.copy(),
        )
        for relation in relations
    ]

    strategy.retrieve(relations, "python")

    current = [
        (
            relation.id,
            relation.source,
            relation.target,
            relation.relation_type,
            relation.metadata.copy(),
        )
        for relation in relations
    ]

    assert current == original


def test_public_export():
    from scios.cognitive_core.knowledge.retrieval import relation

    assert relation.__all__ == ["RelationRetrieval"]


"""Tests for Entity retrieval."""

import pytest

from scios.cognitive_core.knowledge.core.entity import Entity
from scios.cognitive_core.knowledge.retrieval.entity import EntityRetrieval


@pytest.fixture
def strategy():
    return EntityRetrieval()


@pytest.fixture
def entities():
    return [
        Entity("e1", "Python"),
        Entity("e2", "Python Programming"),
        Entity("e3", "Rust"),
        Entity("E4", "PyTorch"),
    ]


def test_default_name(strategy):
    assert strategy.name == "entity"


def test_custom_name():
    strategy = EntityRetrieval("custom")

    assert strategy.name == "custom"


def test_retrieve_by_exact_id(strategy, entities):
    result = strategy.retrieve(entities, "e1")

    assert result == [entities[0]]


def test_retrieve_id_is_case_insensitive(strategy, entities):
    result = strategy.retrieve(entities, "E4")

    assert result == [entities[3]]


def test_retrieve_by_exact_label(strategy, entities):
    result = strategy.retrieve(entities, "Python")

    assert result == [entities[0], entities[1]]


def test_retrieve_by_partial_label(strategy, entities):
    result = strategy.retrieve(entities, "program")

    assert result == [entities[1]]


def test_retrieve_label_is_case_insensitive(strategy, entities):
    result = strategy.retrieve(entities, "PYTHON")

    assert result == [entities[0], entities[1]]


def test_retrieve_no_match(strategy, entities):
    assert strategy.retrieve(entities, "Java") == []


def test_empty_items(strategy):
    assert strategy.retrieve([], "Python") == []


def test_generator_input(strategy):
    items = (
        entity
        for entity in [
            Entity("e1", "Python"),
            Entity("e2", "Rust"),
        ]
    )

    result = strategy.retrieve(items, "python")

    assert result[0].id == "e1"


def test_result_preserves_input_order(strategy, entities):
    result = strategy.retrieve(entities, "p")

    assert result == [entities[0], entities[1], entities[3]]


def test_result_preserves_entity_identity(strategy, entities):
    result = strategy.retrieve(entities, "e1")

    assert result[0] is entities[0]


def test_query_must_be_string(strategy, entities):
    with pytest.raises(TypeError, match="query"):
        strategy.retrieve(entities, None)


def test_entities_are_not_mutated(strategy, entities):
    original = [
        (
            entity.id,
            entity.label,
            entity.entity_type,
            entity.metadata.copy(),
        )
        for entity in entities
    ]

    strategy.retrieve(entities, "python")

    current = [
        (
            entity.id,
            entity.label,
            entity.entity_type,
            entity.metadata.copy(),
        )
        for entity in entities
    ]

    assert current == original


def test_is_subclass_of_retrieval_strategy(strategy):
    from scios.cognitive_core.knowledge.retrieval.base import RetrievalStrategy

    assert isinstance(strategy, RetrievalStrategy)


def test_public_export():
    from scios.cognitive_core.knowledge.retrieval import entity

    assert entity.__all__ == ["EntityRetrieval"]

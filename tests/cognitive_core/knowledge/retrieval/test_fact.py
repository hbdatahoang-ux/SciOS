"""Tests for Fact retrieval."""

import pytest

from scios.cognitive_core.knowledge.core.entity import Entity
from scios.cognitive_core.knowledge.core.fact import Fact
from scios.cognitive_core.knowledge.core.relation import Relation
from scios.cognitive_core.knowledge.core.types import FactType, RelationType
from scios.cognitive_core.knowledge.retrieval.base import RetrievalStrategy
from scios.cognitive_core.knowledge.retrieval.fact import FactRetrieval


@pytest.fixture
def strategy():
    return FactRetrieval()


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


@pytest.fixture
def facts(relations):
    return [
        Fact(
            "f1",
            relations[0],
            FactType.ASSERTION,
        ),
        Fact(
            "f2",
            relations[1],
            FactType.OBSERVATION,
        ),
        Fact(
            "f3",
            relations[2],
            FactType.RULE,
        ),
        Fact(
            "f4",
            relations[3],
            FactType.ASSERTION,
        ),
    ]


def test_default_name(strategy):
    assert strategy.name == "fact"


def test_custom_name():
    strategy = FactRetrieval("custom")

    assert strategy.name == "custom"


def test_is_retrieval_strategy(strategy):
    assert isinstance(strategy, RetrievalStrategy)


def test_retrieve_by_source_id(strategy, facts):
    result = strategy.retrieve(facts, "e1")

    assert result == [facts[0], facts[1]]


def test_retrieve_by_source_label(strategy, facts):
    result = strategy.retrieve(facts, "Python")

    assert result == [facts[0], facts[1]]


def test_retrieve_by_source_label_is_case_insensitive(
    strategy,
    facts,
):
    result = strategy.retrieve(facts, "PYTHON")

    assert result == [facts[0], facts[1]]


def test_retrieve_by_partial_source_label(strategy, facts):
    result = strategy.retrieve(facts, "machine")

    assert result == [facts[0], facts[2]]


def test_retrieve_by_target_id(strategy, facts):
    result = strategy.retrieve(facts, "e4")

    assert result == [facts[2], facts[3]]


def test_retrieve_by_target_label(strategy, facts):
    result = strategy.retrieve(facts, "Research Lab")

    assert result == [facts[2], facts[3]]


def test_retrieve_by_target_label_is_case_insensitive(
    strategy,
    facts,
):
    result = strategy.retrieve(facts, "RESEARCH LAB")

    assert result == [facts[2], facts[3]]


def test_retrieve_by_partial_target_label(strategy, facts):
    result = strategy.retrieve(facts, "learning")

    assert result == [facts[0], facts[2]]


def test_retrieve_by_relation_type(strategy, facts):
    result = strategy.retrieve(facts, "depends_on")

    assert result == [facts[1]]


def test_relation_type_is_case_insensitive(strategy, facts):
    result = strategy.retrieve(facts, "DEPENDS_ON")

    assert result == [facts[1]]


def test_relation_type_requires_exact_match(strategy, facts):
    result = strategy.retrieve(facts, "depends")

    assert result == []


def test_retrieve_by_fact_type(strategy, facts):
    result = strategy.retrieve(facts, "assertion")

    assert result == [facts[0], facts[3]]


def test_fact_type_is_case_insensitive(strategy, facts):
    result = strategy.retrieve(facts, "ASSERTION")

    assert result == [facts[0], facts[3]]


def test_fact_type_requires_exact_match(strategy, facts):
    result = strategy.retrieve(facts, "assert")

    assert result == []


def test_retrieve_no_match(strategy, facts):
    assert strategy.retrieve(facts, "Java") == []


def test_empty_items(strategy):
    assert strategy.retrieve([], "Python") == []


def test_generator_input(strategy, facts):
    items = (fact for fact in facts)

    result = strategy.retrieve(items, "observation")

    assert result == [facts[1]]


def test_result_preserves_input_order(strategy, facts):
    items = [
        facts[2],
        facts[1],
        facts[3],
        facts[0],
    ]

    result = strategy.retrieve(items, "e1")

    assert result == [facts[1], facts[0]]


def test_result_preserves_fact_identity(strategy, facts):
    result = strategy.retrieve(facts, "Python")

    assert result[0] is facts[0]
    assert result[1] is facts[1]


def test_result_is_new_list(strategy, facts):
    result = strategy.retrieve(facts, "Python")

    assert result is not facts


def test_query_must_be_string(strategy, facts):
    with pytest.raises(TypeError, match="query must be a string"):
        strategy.retrieve(facts, None)


def test_query_empty_string_is_rejected(strategy, facts):
    with pytest.raises(
        ValueError,
        match="query must be a non-empty string",
    ):
        strategy.retrieve(facts, "")


def test_query_whitespace_is_rejected(strategy, facts):
    with pytest.raises(
        ValueError,
        match="query must be a non-empty string",
    ):
        strategy.retrieve(facts, "   ")


def test_query_whitespace_is_trimmed(strategy, facts):
    result = strategy.retrieve(facts, "  Python  ")

    assert result == [facts[0], facts[1]]


def test_facts_are_not_mutated(strategy, facts):
    original = [
        (
            fact.id,
            fact.relation,
            fact.fact_type,
            fact.metadata.copy(),
        )
        for fact in facts
    ]

    strategy.retrieve(facts, "python")

    current = [
        (
            fact.id,
            fact.relation,
            fact.fact_type,
            fact.metadata.copy(),
        )
        for fact in facts
    ]

    assert current == original


def test_public_export():
    from scios.cognitive_core.knowledge.retrieval import fact

    assert fact.__all__ == ["FactRetrieval"]

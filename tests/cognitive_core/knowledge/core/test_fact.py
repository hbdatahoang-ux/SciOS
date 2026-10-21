"""Tests for the Knowledge Fact model."""

import pytest

from scios.cognitive_core.knowledge.core.entity import Entity
from scios.cognitive_core.knowledge.core.fact import Fact
from scios.cognitive_core.knowledge.core.relation import Relation
from scios.cognitive_core.knowledge.core.types import (
    EntityType,
    FactType,
    RelationType,
)


@pytest.fixture
def source():
    return Entity("e1", "Python", EntityType.CONCEPT)


@pytest.fixture
def target():
    return Entity("e2", "Programming", EntityType.CONCEPT)


@pytest.fixture
def relation(source, target):
    return Relation(
        "r1",
        source,
        target,
        RelationType.ASSOCIATED_WITH,
    )


def test_fact_creation(relation):
    fact = Fact("f1", relation)

    assert fact.id == "f1"
    assert fact.relation is relation
    assert fact.fact_type is FactType.ASSERTION
    assert fact.metadata == {}


def test_fact_creation_with_type(relation):
    fact = Fact(
        "f1",
        relation,
        FactType.OBSERVATION,
    )

    assert fact.fact_type is FactType.OBSERVATION


def test_fact_creation_with_metadata(relation):
    metadata = {"confidence": 0.95, "source": "test"}

    fact = Fact(
        "f1",
        relation,
        metadata=metadata,
    )

    assert fact.metadata == metadata
    assert fact.metadata is metadata


def test_fact_uses_slots(relation):
    fact = Fact("f1", relation)

    assert not hasattr(fact, "__dict__")


def test_fact_source_property(relation, source):
    fact = Fact("f1", relation)

    assert fact.source is source


def test_fact_target_property(relation, target):
    fact = Fact("f1", relation)

    assert fact.target is target


def test_fact_relation_type_property(relation):
    fact = Fact("f1", relation)

    assert fact.relation_type is RelationType.ASSOCIATED_WITH


def test_fact_equality_uses_id(relation, source, target):
    other_relation = Relation("r2", target, source)

    first = Fact("f1", relation)
    second = Fact("f1", other_relation)

    assert first == second


def test_facts_with_different_ids_are_not_equal(relation):
    first = Fact("f1", relation)
    second = Fact("f2", relation)

    assert first != second


def test_fact_is_hashable_by_id(relation):
    first = Fact("f1", relation)
    second = Fact("f1", relation)

    assert hash(first) == hash(second)


def test_fact_can_be_used_in_set(relation):
    first = Fact("f1", relation)
    second = Fact("f1", relation)

    facts = {first, second}

    assert len(facts) == 1


def test_empty_id_is_rejected(relation):
    with pytest.raises(ValueError, match="Fact id"):
        Fact("", relation)


def test_whitespace_id_is_rejected(relation):
    with pytest.raises(ValueError, match="Fact id"):
        Fact("   ", relation)


def test_invalid_relation_is_rejected():
    with pytest.raises(TypeError, match="relation"):
        Fact("f1", "r1")


def test_invalid_fact_type_is_rejected(relation):
    with pytest.raises(TypeError, match="fact_type"):
        Fact("f1", relation, "assertion")


def test_invalid_metadata_is_rejected(relation):
    with pytest.raises(TypeError, match="metadata"):
        Fact("f1", relation, metadata=[])


def test_public_exports():
    from scios.cognitive_core.knowledge.core import fact

    assert fact.__all__ == ["Fact"]

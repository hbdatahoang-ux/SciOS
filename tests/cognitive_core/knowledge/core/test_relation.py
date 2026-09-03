"""Tests for the Knowledge Relation model."""

import pytest

from scios.cognitive_core.knowledge.core.entity import Entity
from scios.cognitive_core.knowledge.core.relation import Relation
from scios.cognitive_core.knowledge.core.types import (
    EntityType,
    RelationType,
)


@pytest.fixture
def source():
    return Entity("e1", "Python", EntityType.CONCEPT)


@pytest.fixture
def target():
    return Entity("e2", "Programming", EntityType.CONCEPT)


def test_relation_creation(source, target):
    relation = Relation("r1", source, target)

    assert relation.id == "r1"
    assert relation.source is source
    assert relation.target is target
    assert relation.relation_type is RelationType.ASSOCIATED_WITH
    assert relation.metadata == {}


def test_relation_creation_with_type(source, target):
    relation = Relation(
        "r1",
        source,
        target,
        RelationType.PART_OF,
    )

    assert relation.relation_type is RelationType.PART_OF


def test_relation_creation_with_metadata(source, target):
    metadata = {"confidence": 0.95, "source": "test"}

    relation = Relation(
        "r1",
        source,
        target,
        metadata=metadata,
    )

    assert relation.metadata == metadata
    assert relation.metadata is metadata


def test_relation_uses_slots(source, target):
    relation = Relation("r1", source, target)

    assert not hasattr(relation, "__dict__")


def test_relation_equality_uses_id(source, target):
    first = Relation("r1", source, target)
    second = Relation("r1", target, source)

    assert first == second


def test_relations_with_different_ids_are_not_equal(source, target):
    first = Relation("r1", source, target)
    second = Relation("r2", source, target)

    assert first != second


def test_relation_is_hashable_by_id(source, target):
    first = Relation("r1", source, target)
    second = Relation("r1", target, source)

    assert hash(first) == hash(second)


def test_relation_can_be_used_in_set(source, target):
    first = Relation("r1", source, target)
    second = Relation("r1", target, source)

    relations = {first, second}

    assert len(relations) == 1


def test_empty_id_is_rejected(source, target):
    with pytest.raises(ValueError, match="Relation id"):
        Relation("", source, target)


def test_whitespace_id_is_rejected(source, target):
    with pytest.raises(ValueError, match="Relation id"):
        Relation("   ", source, target)


def test_invalid_source_is_rejected(target):
    with pytest.raises(TypeError, match="source"):
        Relation("r1", "e1", target)


def test_invalid_target_is_rejected(source):
    with pytest.raises(TypeError, match="target"):
        Relation("r1", source, "e2")


def test_invalid_relation_type_is_rejected(source, target):
    with pytest.raises(TypeError, match="relation_type"):
        Relation("r1", source, target, "part_of")


def test_invalid_metadata_is_rejected(source, target):
    with pytest.raises(TypeError, match="metadata"):
        Relation("r1", source, target, metadata=[])


def test_public_exports():
    from scios.cognitive_core.knowledge.core import relation

    assert relation.__all__ == ["Relation"]

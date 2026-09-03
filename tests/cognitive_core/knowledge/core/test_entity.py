"""Tests for the Knowledge Entity model."""

import pytest

from scios.cognitive_core.knowledge.core.entity import Entity
from scios.cognitive_core.knowledge.core.types import EntityType


def test_entity_creation():
    entity = Entity("e1", "Python")

    assert entity.id == "e1"
    assert entity.label == "Python"
    assert entity.entity_type is EntityType.CONCEPT
    assert entity.metadata == {}


def test_entity_creation_with_type():
    entity = Entity(
        "e2",
        "Python",
        EntityType.OBJECT,
    )

    assert entity.entity_type is EntityType.OBJECT


def test_entity_creation_with_metadata():
    metadata = {"source": "test", "confidence": 0.95}

    entity = Entity(
        "e1",
        "Python",
        metadata=metadata,
    )

    assert entity.metadata == metadata
    assert entity.metadata is metadata


def test_entity_uses_slots():
    entity = Entity("e1", "Python")

    assert not hasattr(entity, "__dict__")


def test_entity_equality_uses_id():
    first = Entity("e1", "Python")
    second = Entity("e1", "Python language")

    assert first == second


def test_entities_with_different_ids_are_not_equal():
    first = Entity("e1", "Python")
    second = Entity("e2", "Python")

    assert first != second


def test_entity_is_hashable_by_id():
    first = Entity("e1", "Python")
    second = Entity("e1", "Python language")

    assert hash(first) == hash(second)


def test_entity_can_be_used_in_set():
    first = Entity("e1", "Python")
    second = Entity("e1", "Python language")

    entities = {first, second}

    assert len(entities) == 1


def test_empty_id_is_rejected():
    with pytest.raises(ValueError, match="Entity id"):
        Entity("", "Python")


def test_whitespace_id_is_rejected():
    with pytest.raises(ValueError, match="Entity id"):
        Entity("   ", "Python")


def test_empty_label_is_rejected():
    with pytest.raises(ValueError, match="Entity label"):
        Entity("e1", "")


def test_whitespace_label_is_rejected():
    with pytest.raises(ValueError, match="Entity label"):
        Entity("e1", "   ")


def test_invalid_entity_type_is_rejected():
    with pytest.raises(TypeError, match="entity_type"):
        Entity("e1", "Python", "concept")


def test_invalid_metadata_is_rejected():
    with pytest.raises(TypeError, match="metadata"):
        Entity("e1", "Python", metadata=[])


def test_public_exports():
    from scios.cognitive_core.knowledge.core import entity

    assert entity.__all__ == ["Entity"]

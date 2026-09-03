"""Tests for the Knowledge entity store."""

import pytest

from scios.cognitive_core.knowledge.core.entity import Entity
from scios.cognitive_core.knowledge.core.errors import EntityError
from scios.cognitive_core.knowledge.stores.entity_store import EntityStore


@pytest.fixture
def store():
    return EntityStore()


@pytest.fixture
def entity():
    return Entity("e1", "Python")


def test_empty_store(store):
    assert store.count() == 0
    assert store.all() == []


def test_add_entity(store, entity):
    result = store.add(entity)

    assert result is entity
    assert store.get("e1") is entity
    assert store.count() == 1


def test_add_duplicate_entity_raises_entity_error(store, entity):
    store.add(entity)

    with pytest.raises(EntityError):
        store.add(entity)


def test_add_non_entity_raises_type_error(store):
    with pytest.raises(TypeError):
        store.add("entity")


def test_get_existing_entity(store, entity):
    store.add(entity)

    assert store.get("e1") is entity


def test_get_missing_entity_returns_none(store):
    assert store.get("missing") is None


def test_remove_existing_entity(store, entity):
    store.add(entity)

    result = store.remove("e1")

    assert result is entity
    assert store.get("e1") is None
    assert store.count() == 0


def test_remove_missing_entity_returns_none(store):
    assert store.remove("missing") is None


def test_all_returns_entities(store):
    first = Entity("e1", "Python")
    second = Entity("e2", "Rust")

    store.add(first)
    store.add(second)

    result = store.all()

    assert result == [first, second]


def test_all_returns_snapshot(store, entity):
    store.add(entity)

    result = store.all()
    result.clear()

    assert store.count() == 1
    assert store.get("e1") is entity


def test_count_tracks_entities(store):
    assert store.count() == 0

    store.add(Entity("e1", "Python"))
    assert store.count() == 1

    store.add(Entity("e2", "Rust"))
    assert store.count() == 2

    store.remove("e1")
    assert store.count() == 1


def test_clear(store):
    store.add(Entity("e1", "Python"))
    store.add(Entity("e2", "Rust"))

    store.clear()

    assert store.count() == 0
    assert store.all() == []
    assert store.get("e1") is None
    assert store.get("e2") is None


def test_clear_empty_store_is_safe(store):
    store.clear()

    assert store.count() == 0
    assert store.all() == []


def test_store_preserves_entity_identity(store, entity):
    store.add(entity)

    retrieved = store.get("e1")

    assert retrieved is entity


def test_entity_id_is_store_key(store):
    first = Entity("e1", "Python")
    second = Entity("e2", "Python")

    store.add(first)
    store.add(second)

    assert store.get("e1") is first
    assert store.get("e2") is second


def test_store_does_not_mutate_entity(store, entity):
    original_id = entity.id
    original_label = entity.label
    original_metadata = entity.metadata.copy()

    store.add(entity)

    assert entity.id == original_id
    assert entity.label == original_label
    assert entity.metadata == original_metadata


def test_public_export():
    from scios.cognitive_core.knowledge.stores import entity_store

    assert entity_store.__all__ == ["EntityStore"]


def test_entity_store_is_instantiable():
    store = EntityStore()

    assert isinstance(store, EntityStore)

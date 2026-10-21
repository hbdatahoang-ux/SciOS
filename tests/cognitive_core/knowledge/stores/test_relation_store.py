"""Tests for the Knowledge relation store."""

import pytest

from scios.cognitive_core.knowledge.core.entity import Entity
from scios.cognitive_core.knowledge.core.errors import RelationError
from scios.cognitive_core.knowledge.core.relation import Relation
from scios.cognitive_core.knowledge.core.types import RelationType
from scios.cognitive_core.knowledge.stores.relation_store import RelationStore


@pytest.fixture
def store():
    return RelationStore()


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


def test_empty_store(store):
    assert store.count() == 0
    assert store.all() == []


def test_add_relation(store, relation):
    result = store.add(relation)

    assert result is relation
    assert store.get("r1") is relation
    assert store.count() == 1


def test_add_duplicate_relation_raises_relation_error(store, relation):
    store.add(relation)

    with pytest.raises(RelationError):
        store.add(relation)


def test_add_non_relation_raises_type_error(store):
    with pytest.raises(TypeError):
        store.add("relation")


def test_get_existing_relation(store, relation):
    store.add(relation)

    assert store.get("r1") is relation


def test_get_missing_relation_returns_none(store):
    assert store.get("missing") is None


def test_remove_existing_relation(store, relation):
    store.add(relation)

    result = store.remove("r1")

    assert result is relation
    assert store.get("r1") is None
    assert store.count() == 0


def test_remove_missing_relation_returns_none(store):
    assert store.remove("missing") is None


def test_all_returns_relations(store, source, target):
    first = Relation("r1", source, target)
    second = Relation("r2", target, source)

    store.add(first)
    store.add(second)

    assert store.all() == [first, second]


def test_all_returns_snapshot(store, relation):
    store.add(relation)

    result = store.all()
    result.clear()

    assert store.count() == 1
    assert store.get("r1") is relation


def test_count_tracks_relations(store, source, target):
    first = Relation("r1", source, target)
    second = Relation("r2", target, source)

    assert store.count() == 0

    store.add(first)
    assert store.count() == 1

    store.add(second)
    assert store.count() == 2

    store.remove("r1")
    assert store.count() == 1


def test_clear(store, source, target):
    first = Relation("r1", source, target)
    second = Relation("r2", target, source)

    store.add(first)
    store.add(second)

    store.clear()

    assert store.count() == 0
    assert store.all() == []
    assert store.get("r1") is None
    assert store.get("r2") is None


def test_clear_empty_store_is_safe(store):
    store.clear()

    assert store.count() == 0
    assert store.all() == []


def test_store_preserves_relation_identity(store, relation):
    store.add(relation)

    assert store.get("r1") is relation


def test_relation_id_is_store_key(store, source, target):
    first = Relation("r1", source, target)
    second = Relation("r2", source, target)

    store.add(first)
    store.add(second)

    assert store.get("r1") is first
    assert store.get("r2") is second


def test_store_preserves_directionality(store, source, target):
    forward = Relation("r1", source, target)
    reverse = Relation("r2", target, source)

    store.add(forward)
    store.add(reverse)

    assert store.get("r1").source is source
    assert store.get("r1").target is target
    assert store.get("r2").source is target
    assert store.get("r2").target is source


def test_store_does_not_mutate_relation(store, relation):
    original_id = relation.id
    original_source = relation.source
    original_target = relation.target
    original_metadata = relation.metadata.copy()

    store.add(relation)

    assert relation.id == original_id
    assert relation.source is original_source
    assert relation.target is original_target
    assert relation.metadata == original_metadata


def test_public_export():
    from scios.cognitive_core.knowledge.stores import relation_store

    assert relation_store.__all__ == ["RelationStore"]


def test_relation_store_is_instantiable():
    store = RelationStore()

    assert isinstance(store, RelationStore)

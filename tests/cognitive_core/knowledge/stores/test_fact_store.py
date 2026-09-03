"""Tests for the Knowledge fact store."""

import pytest

from scios.cognitive_core.knowledge.core.entity import Entity
from scios.cognitive_core.knowledge.core.errors import FactError
from scios.cognitive_core.knowledge.core.fact import Fact
from scios.cognitive_core.knowledge.core.relation import Relation
from scios.cognitive_core.knowledge.core.types import FactType, RelationType
from scios.cognitive_core.knowledge.stores.fact_store import FactStore


@pytest.fixture
def store():
    return FactStore()


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


def test_empty_store(store):
    assert store.count() == 0
    assert store.all() == []


def test_add_fact(store, fact):
    result = store.add(fact)

    assert result is fact
    assert store.get("f1") is fact
    assert store.count() == 1


def test_add_duplicate_fact_raises_fact_error(store, fact):
    store.add(fact)

    with pytest.raises(FactError):
        store.add(fact)


def test_add_non_fact_raises_type_error(store):
    with pytest.raises(TypeError):
        store.add("fact")


def test_get_existing_fact(store, fact):
    store.add(fact)

    assert store.get("f1") is fact


def test_get_missing_fact_returns_none(store):
    assert store.get("missing") is None


def test_remove_existing_fact(store, fact):
    store.add(fact)

    result = store.remove("f1")

    assert result is fact
    assert store.get("f1") is None
    assert store.count() == 0


def test_remove_missing_fact_returns_none(store):
    assert store.remove("missing") is None


def test_all_returns_facts(store, relation):
    first = Fact("f1", relation)
    second = Fact("f2", relation, FactType.OBSERVATION)

    store.add(first)
    store.add(second)

    assert store.all() == [first, second]


def test_all_returns_snapshot(store, fact):
    store.add(fact)

    result = store.all()
    result.clear()

    assert store.count() == 1
    assert store.get("f1") is fact


def test_count_tracks_facts(store, relation):
    first = Fact("f1", relation)
    second = Fact("f2", relation)

    assert store.count() == 0

    store.add(first)
    assert store.count() == 1

    store.add(second)
    assert store.count() == 2

    store.remove("f1")
    assert store.count() == 1


def test_clear(store, relation):
    first = Fact("f1", relation)
    second = Fact("f2", relation)

    store.add(first)
    store.add(second)

    store.clear()

    assert store.count() == 0
    assert store.all() == []
    assert store.get("f1") is None
    assert store.get("f2") is None


def test_clear_empty_store_is_safe(store):
    store.clear()

    assert store.count() == 0
    assert store.all() == []


def test_store_preserves_fact_identity(store, fact):
    store.add(fact)

    assert store.get("f1") is fact


def test_fact_id_is_store_key(store, relation):
    first = Fact("f1", relation)
    second = Fact("f2", relation)

    store.add(first)
    store.add(second)

    assert store.get("f1") is first
    assert store.get("f2") is second


def test_store_preserves_fact_type(store, relation):
    assertion = Fact("f1", relation, FactType.ASSERTION)
    observation = Fact("f2", relation, FactType.OBSERVATION)
    rule = Fact("f3", relation, FactType.RULE)

    store.add(assertion)
    store.add(observation)
    store.add(rule)

    assert store.get("f1").fact_type is FactType.ASSERTION
    assert store.get("f2").fact_type is FactType.OBSERVATION
    assert store.get("f3").fact_type is FactType.RULE


def test_store_preserves_relation(store, fact, relation):
    store.add(fact)

    assert store.get("f1").relation is relation


def test_store_does_not_mutate_fact(store, fact):
    original_id = fact.id
    original_relation = fact.relation
    original_type = fact.fact_type
    original_metadata = fact.metadata.copy()

    store.add(fact)

    assert fact.id == original_id
    assert fact.relation is original_relation
    assert fact.fact_type is original_type
    assert fact.metadata == original_metadata


def test_public_export():
    from scios.cognitive_core.knowledge.stores import fact_store

    assert fact_store.__all__ == ["FactStore"]


def test_fact_store_is_instantiable():
    store = FactStore()

    assert isinstance(store, FactStore)

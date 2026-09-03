from inspect import isabstract

import pytest

from scios.cognitive_core.memory.core import (
    MemoryCapacityError,
    MemoryKind,
    MemoryRecord,
    MemoryStore,
)
from scios.cognitive_core.memory.stores.working import WorkingMemory


def test_working_memory_inherits_memory_store() -> None:
    assert issubclass(WorkingMemory, MemoryStore)


def test_working_memory_is_concrete() -> None:
    assert not isabstract(WorkingMemory)


def test_default_name() -> None:
    store = WorkingMemory()

    assert store.name == "WorkingMemory"


def test_default_capacity() -> None:
    store = WorkingMemory()

    assert store.capacity == 10


@pytest.mark.parametrize("capacity", [0, -1, -10])
def test_capacity_must_be_positive(capacity: int) -> None:
    with pytest.raises(ValueError, match="capacity"):
        WorkingMemory(capacity=capacity)


@pytest.mark.parametrize("capacity", [None, "10", 10.5, object()])
def test_capacity_must_be_integer(capacity: object) -> None:
    with pytest.raises(ValueError, match="capacity"):
        WorkingMemory(capacity=capacity)  # type: ignore[arg-type]


def test_custom_name_and_capacity() -> None:
    store = WorkingMemory(name="SessionMemory", capacity=3)

    assert store.name == "SessionMemory"
    assert store.capacity == 3


def test_empty_store() -> None:
    store = WorkingMemory()

    assert store.count() == 0
    assert store.all() == ()


def test_store_returns_record() -> None:
    store = WorkingMemory()
    record = MemoryRecord(content="hello")

    stored = store.store(record)

    assert stored is record


def test_store_and_get() -> None:
    store = WorkingMemory()
    record = MemoryRecord(content="hello")

    store.store(record)

    assert store.get(record.id) is record


def test_get_missing_returns_none() -> None:
    store = WorkingMemory()

    assert store.get("missing") is None


def test_count_after_store() -> None:
    store = WorkingMemory()

    store.store(MemoryRecord(content="one"))
    store.store(MemoryRecord(content="two"))

    assert store.count() == 2


def test_all_returns_tuple() -> None:
    store = WorkingMemory()
    first = MemoryRecord(content="one")
    second = MemoryRecord(content="two")

    store.store(first)
    store.store(second)

    assert isinstance(store.all(), tuple)
    assert store.all() == (first, second)


def test_all_preserves_insertion_order() -> None:
    store = WorkingMemory()
    records = [
        MemoryRecord(content="one"),
        MemoryRecord(content="two"),
        MemoryRecord(content="three"),
    ]

    for record in records:
        store.store(record)

    assert store.all() == tuple(records)



def test_delete_existing_record() -> None:
    store = WorkingMemory()
    record = MemoryRecord(content="hello")

    store.store(record)

    assert store.delete(record.id) is True
    assert store.get(record.id) is None
    assert store.count() == 0


def test_delete_missing_record() -> None:
    store = WorkingMemory()

    assert store.delete("missing") is False


def test_clear_removes_all_records() -> None:
    store = WorkingMemory()

    store.store(MemoryRecord(content="one"))
    store.store(MemoryRecord(content="two"))

    store.clear()

    assert store.count() == 0
    assert store.all() == ()


def test_capacity_is_enforced() -> None:
    store = WorkingMemory(capacity=2)

    store.store(MemoryRecord(content="one"))
    store.store(MemoryRecord(content="two"))

    with pytest.raises(MemoryCapacityError):
        store.store(MemoryRecord(content="three"))


def test_count_never_exceeds_capacity() -> None:
    store = WorkingMemory(capacity=2)

    store.store(MemoryRecord(content="one"))
    store.store(MemoryRecord(content="two"))

    assert store.count() == 2


def test_capacity_reusable_after_delete() -> None:
    store = WorkingMemory(capacity=2)
    first = MemoryRecord(content="one")
    second = MemoryRecord(content="two")
    third = MemoryRecord(content="three")

    store.store(first)
    store.store(second)

    assert store.delete(first.id) is True

    store.store(third)

    assert store.count() == 2
    assert store.all() == (second, third)


def test_duplicate_id_replaces_existing_record() -> None:
    store = WorkingMemory()

    first = MemoryRecord(content="first", id="same-id")
    second = MemoryRecord(content="second", id="same-id")

    store.store(first)
    stored = store.store(second)

    assert stored is second
    assert store.count() == 1
    assert store.get("same-id") is second


def test_duplicate_id_does_not_consume_capacity() -> None:
    store = WorkingMemory(capacity=1)

    first = MemoryRecord(content="first", id="same-id")
    second = MemoryRecord(content="second", id="same-id")

    store.store(first)
    store.store(second)

    assert store.count() == 1
    assert store.get("same-id") is second


def test_store_requires_memory_record() -> None:
    store = WorkingMemory()

    with pytest.raises(TypeError):
        store.store("invalid")  # type: ignore[arg-type]


def test_get_requires_string_id() -> None:
    store = WorkingMemory()

    with pytest.raises(TypeError):
        store.get(None)  # type: ignore[arg-type]


def test_delete_requires_string_id() -> None:
    store = WorkingMemory()

    with pytest.raises(TypeError):
        store.delete(None)  # type: ignore[arg-type]


def test_all_returns_snapshot() -> None:
    store = WorkingMemory()
    record = MemoryRecord(content="hello")

    store.store(record)
    snapshot = store.all()

    store.delete(record.id)

    assert snapshot == (record,)
    assert store.all() == ()


def test_clear_is_idempotent() -> None:
    store = WorkingMemory()

    store.clear()
    store.clear()

    assert store.count() == 0
    assert store.all() == ()
from inspect import isabstract

import pytest

from scios.cognitive_core.memory.core.base import MemoryStore
from scios.cognitive_core.memory.core.record import MemoryRecord


EXPECTED_ABSTRACT_METHODS = {
    "store",
    "get",
    "delete",
    "clear",
    "count",
    "all",
}


def test_memory_store_is_abstract() -> None:
    assert isabstract(MemoryStore)


def test_memory_store_abstract_methods() -> None:
    assert set(MemoryStore.__abstractmethods__) == EXPECTED_ABSTRACT_METHODS


def test_memory_store_cannot_be_instantiated_directly() -> None:
    with pytest.raises(TypeError):
        MemoryStore(name="memory")  # type: ignore[abstract]


@pytest.mark.parametrize("name", ["", " ", "\t", "\n", None, 123])
def test_name_must_be_non_empty_string(name: object) -> None:
    class ConcreteMemoryStore(MemoryStore):
        def store(self, record: MemoryRecord) -> MemoryRecord:
            return record

        def get(self, record_id: str) -> MemoryRecord | None:
            return None

        def delete(self, record_id: str) -> bool:
            return False

        def clear(self) -> None:
            pass

        def count(self) -> int:
            return 0

        def all(self) -> tuple[MemoryRecord, ...]:
            return ()

    with pytest.raises(ValueError, match="name must be a non-empty string"):
        ConcreteMemoryStore(name=name)  # type: ignore[arg-type]


def test_name_is_stored() -> None:
    class ConcreteMemoryStore(MemoryStore):
        def store(self, record: MemoryRecord) -> MemoryRecord:
            return record

        def get(self, record_id: str) -> MemoryRecord | None:
            return None

        def delete(self, record_id: str) -> bool:
            return False

        def clear(self) -> None:
            pass

        def count(self) -> int:
            return 0

        def all(self) -> tuple[MemoryRecord, ...]:
            return ()

    store = ConcreteMemoryStore(name="TestStore")

    assert store.name == "TestStore"


def test_concrete_store_is_instantiable_when_contract_is_complete() -> None:
    class ConcreteMemoryStore(MemoryStore):
        def store(self, record: MemoryRecord) -> MemoryRecord:
            return record

        def get(self, record_id: str) -> MemoryRecord | None:
            return None

        def delete(self, record_id: str) -> bool:
            return False

        def clear(self) -> None:
            pass

        def count(self) -> int:
            return 0

        def all(self) -> tuple[MemoryRecord, ...]:
            return ()

    store = ConcreteMemoryStore(name="TestStore")

    assert isinstance(store, MemoryStore)
    assert not isabstract(store.__class__)


def test_concrete_store_must_implement_all_abstract_methods() -> None:
    class IncompleteMemoryStore(MemoryStore):
        def store(self, record: MemoryRecord) -> MemoryRecord:
            return record

    assert isabstract(IncompleteMemoryStore)

    with pytest.raises(TypeError):
        IncompleteMemoryStore(name="Incomplete")  # type: ignore[abstract]


def test_contract_methods_exist() -> None:
    for method_name in EXPECTED_ABSTRACT_METHODS:
        method = getattr(MemoryStore, method_name)

        assert callable(method)


def test_concrete_store_contract_behavior() -> None:
    record = MemoryRecord(content="hello")

    class ConcreteMemoryStore(MemoryStore):
        def store(self, record: MemoryRecord) -> MemoryRecord:
            return record

        def get(self, record_id: str) -> MemoryRecord | None:
            return record if record_id == record.id else None

        def delete(self, record_id: str) -> bool:
            return record_id == record.id

        def clear(self) -> None:
            return None

        def count(self) -> int:
            return 1

        def all(self) -> tuple[MemoryRecord, ...]:
            return (record,)

    store = ConcreteMemoryStore(name="TestStore")

    assert store.store(record) is record
    assert store.get(record.id) is record
    assert store.get("missing") is None
    assert store.delete(record.id) is True
    assert store.delete("missing") is False
    assert store.count() == 1
    assert store.all() == (record,)
    assert store.clear() is None